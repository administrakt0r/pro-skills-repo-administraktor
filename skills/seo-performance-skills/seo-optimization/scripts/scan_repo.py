#!/usr/bin/env python3
"""Read-only repository scanner that surfaces SEO *leads* for an auditor to verify.

It never modifies files and never touches the network. Its output is a set of signals
found in source files, NOT confirmed defects: templates often build titles, canonicals
and structured data at render time, so every signal must be checked against the actual
rendered output (build, local preview, or live fetch) before it becomes a finding.

Usage:  python scan_repo.py [--root PATH] [--out report.json] [--max-examples 25]
Standard library only.
"""
import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "dist", "build", ".next", ".nuxt", ".svelte-kit", ".astro", ".output",
             "vendor", "coverage", "__pycache__", ".venv", "venv", ".cache", "public/build", "seo-optimization-work",
             "target", "_site", ".turbo", ".vercel", ".netlify"}
TEMPLATE_EXT = {".html", ".htm", ".liquid", ".njk", ".hbs", ".ejs", ".php", ".twig", ".erb", ".jinja", ".jinja2",
                ".blade.php"}
COMPONENT_EXT = {".js", ".mjs", ".ts", ".jsx", ".tsx", ".vue", ".svelte", ".astro"}
INSTRUCTION_FILES = ["AGENTS.md", "CLAUDE.md", "GEMINI.md", "CONTRIBUTING.md", ".cursorrules", ".windsurfrules",
                     ".github/copilot-instructions.md", "docs/CONTRIBUTING.md"]
AI_BOTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "PerplexityBot", "Perplexity-User", "Bingbot", "Googlebot",
           "Google-Extended", "ClaudeBot", "Claude-SearchBot", "Claude-User", "CCBot", "Applebot-Extended"]
TEMPLATE_TOKENS = ("{{", "{%", "<?", "${", "<%", "{@", "{#")
MAX_BYTES = 400_000


def is_templated(s):
    return any(t in s for t in TEMPLATE_TOKENS)


def walk(root):
    """Prune dependencies before traversal; never follow repository symlinks."""
    for directory, dirs, names in os.walk(root, followlinks=False):
        base = Path(directory)
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS
                         and not (base / d).is_symlink()
                         and not (d.lower().startswith(("seo-audit", "seo_audit", "seo-work", "seo-optimization"))
                                  and any((base / d / marker).is_file()
                                          for marker in ("AUDIT.md", "TASKS.md", "WORKLOG.md"))))
        for name in sorted(names):
            p = base / name
            if not p.is_symlink() and p.is_file():
                yield p, p.relative_to(root)


def read(p):
    try:
        if p.stat().st_size > MAX_BYTES:
            return None
        return p.read_text(encoding="utf-8", errors="ignore")
    except (OSError, UnicodeError):
        return None


def detect_project(root, files):
    sig, names = {}, {rel.as_posix() for _, rel in files}
    pkg = root / "package.json"
    deps = {}
    if pkg.exists():
        try:
            j = json.loads(pkg.read_text(encoding="utf-8"))
            deps = {**j.get("dependencies", {}), **j.get("devDependencies", {})}
            sig["package_scripts"] = sorted((j.get("scripts") or {}).keys())
        except Exception:
            sig["package_json_unparsable"] = True
    fw = [name for dep, name in [("next", "Next.js"), ("nuxt", "Nuxt"), ("astro", "Astro"), ("gatsby", "Gatsby"),
                                 ("@remix-run/react", "Remix"), ("@sveltejs/kit", "SvelteKit"),
                                 ("@angular/core", "Angular"), ("vite", "Vite"), ("react", "React"), ("vue", "Vue"),
                                 ("svelte", "Svelte"), ("@11ty/eleventy", "Eleventy"), ("vitepress", "VitePress"),
                                 ("docusaurus", "Docusaurus"), ("@docusaurus/core", "Docusaurus")] if dep in deps]
    if any(n.startswith("wp-content/") or n == "functions.php" or n == "style.css" for n in names) and \
            ("functions.php" in names or any(n.startswith("wp-content/") for n in names)):
        fw.append("WordPress (theme/plugin)")
    if "layout/theme.liquid" in names:
        fw.append("Shopify theme")
    if any(n in names for n in ("hugo.toml", "hugo.yaml", "config.toml")) and any(n.startswith("content/") for n in names):
        fw.append("Hugo (likely)")
    if "_config.yml" in names and ("Gemfile" in names):
        fw.append("Jekyll (likely)")
    if "manage.py" in names:
        fw.append("Django (likely)")
    if "composer.json" in names:
        fw.append("PHP/Composer project")
    if "Gemfile" in names and "config/routes.rb" in names:
        fw.append("Rails (likely)")
    if not fw and any(n.endswith(".html") for n in names):
        fw.append("Static HTML (likely)")
    sig["frameworks"] = fw
    sig["next_router"] = [d for d in ("app", "pages", "src/app", "src/pages") if (root / d).is_dir()] if "Next.js" in fw else []
    sig["rendering_hints"] = []
    for _, rel in files:
        n = rel.as_posix()
        if re.search(r"(^|/)(next|nuxt|astro|svelte)\.config\.(js|ts|mjs)$", n):
            txt = read(root / rel) or ""
            for hint, pat in [("static export", r"output\s*:\s*['\"]export['\"]"), ("ssr: false", r"ssr\s*:\s*false"),
                              ("output: static", r"output\s*:\s*['\"]static['\"]"),
                              ("output: server", r"output\s*:\s*['\"]server['\"]"),
                              ("trailingSlash", r"trailingSlash"), ("redirects()", r"redirects\s*\(")]:
                if re.search(pat, txt):
                    sig["rendering_hints"].append(f"{n}: {hint}")
    return sig


def parse_robots(text):
    groups, cur = defaultdict(list), []
    sitemaps = re.findall(r"(?im)^\s*sitemap\s*:\s*(\S+)", text)
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        k, v = [x.strip() for x in line.split(":", 1)]
        k = k.lower()
        if k == "user-agent":
            if cur and groups.get("_last_had_rule"):
                cur = []
                groups["_last_had_rule"] = False
            cur.append(v)
        elif k in ("allow", "disallow"):
            groups["_last_had_rule"] = True
            for ua in cur:
                groups[ua].append((k, v))
    groups.pop("_last_had_rule", None)
    return dict(groups), sitemaps


def scan(root, max_ex):
    if max_ex < 1:
        raise ValueError("max-examples must be positive")
    files = list(walk(root))
    report = {"root": str(root), "note": "Signals are leads, not confirmed defects. Verify against rendered output.",
              "project": detect_project(root, files), "package_manifests": [rel.as_posix() for _, rel in files if rel.name == "package.json"], "instruction_files": [], "robots": [], "sitemaps": [],
              "redirect_or_routing_files": [], "routing_config_lines": [], "i18n": {}, "counts": {}, "signals": []}
    for f in INSTRUCTION_FILES:
        if (root / f).exists():
            report["instruction_files"].append(f)
    for p, rel in files:
        if p.name in ("copilot-instructions.md",) or (rel.parts and rel.parts[0] in (".cursor",) and p.suffix in (".md", ".mdc")):
            if rel.as_posix() not in report["instruction_files"]:
                report["instruction_files"].append(rel.as_posix())

    sig = report["signals"]

    def add(kind, file, detail, hint):
        sig.append({"kind": kind, "file": file, "detail": detail, "priority_hint": hint})

    titles, pages = defaultdict(list), 0
    counters = Counter()
    for p, rel in files:
        name, rels = p.name.lower(), rel.as_posix()
        if name in ("robots.txt", "robots.ts", "robots.js"):
            txt = read(p) or ""
            entry = {"file": rels, "dynamic": p.suffix in (".ts", ".js")}
            if not entry["dynamic"]:
                groups, sm = parse_robots(txt)
                entry.update({"sitemap_directives": sm, "bots_mentioned": [b for b in AI_BOTS if b in groups]})
                if ("Disallow", "/") in [(k.title(), v) for k, v in groups.get("*", [])]:
                    add("robots-disallow-all", rels, "User-agent * has 'Disallow: /'.", "check: may be intentional (staging)")
                if not sm:
                    add("robots-no-sitemap-directive", rels, "No Sitemap: line.", "low")
                for ua, rules in groups.items():
                    for k, v in rules:
                        if k == "disallow" and re.search(r"\.(css|js)\b|/assets|/static|/_next|/wp-includes", v):
                            add("robots-may-block-assets", rels, f"{ua}: Disallow: {v}", "check")
                if txt and "noindex" in txt.lower():
                    add("robots-txt-noindex-line", rels, "noindex in robots.txt is not a supported way to deindex.", "check")
            report["robots"].append(entry)
        elif re.match(r"(sitemap.*\.(xml|ts|js)|.*sitemap.*\.xml)$", name):
            report["sitemaps"].append(rels)
        elif name in ("hugo.toml", "hugo.yaml", "hugo.yml", "config.toml", "config.yaml", "_config.yml", "astro.config.mjs",
                      "astro.config.ts") and (txt_cfg := read(p)) is not None:
            after = 0
            for ln, line in enumerate(txt_cfg.splitlines(), 1):
                hit = re.search(r"permalink|baseurl|trailingslash|uglyurls|canonifyurls|\bsite\s*:", line, re.I)
                if re.match(r"\s*\[+permalinks", line, re.I):
                    after = 6  # capture the rules listed under a [permalinks] table
                elif after and line.strip().startswith("[") :
                    after = 0
                if hit or (after and line.strip()):
                    report["routing_config_lines"].append(f"{rels}:{ln}: {line.strip()[:120]}")
                if after and not re.match(r"\s*\[+permalinks", line, re.I):
                    after -= 1
            if name.startswith(("hugo", "config", "_config")):
                report["redirect_or_routing_files"].append(rels)
        elif name in ("_redirects", "redirects.json", "vercel.json", "netlify.toml", ".htaccess", "nginx.conf",
                      "redirects.yaml", "redirects.yml") or re.match(r"(next|nuxt|astro)\.config", name):
            report["redirect_or_routing_files"].append(rels)

        ext = p.suffix.lower()
        is_tpl = ext in TEMPLATE_EXT or name.endswith(".blade.php")
        is_cmp = ext in COMPONENT_EXT
        if not (is_tpl or is_cmp):
            continue
        txt = read(p)
        if txt is None:
            continue
        counters["template_files" if is_tpl else "component_files"] += 1

        # JSON-LD
        for m in re.finditer(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', txt, re.S | re.I):
            counters["jsonld_blocks"] += 1
            body = m.group(1).strip()
            if is_templated(body):
                continue
            try:
                j = json.loads(body)
                if isinstance(j, dict) and "@context" not in j and "@graph" not in j:
                    add("jsonld-missing-context", rels, "JSON-LD parses but has no @context.", "medium")
            except Exception as e:
                add("jsonld-syntax-error", rels, f"JSON-LD does not parse: {str(e)[:80]}", "medium")

        # images without alt (HTML <img> and JSX <img>/<Image>)
        for m in re.finditer(r"<(img|Image)\b(?![^>]*\balt\s*=)[^>]*>", txt, re.S):
            if "{...props}" in m.group(0) or "{...rest}" in m.group(0):
                continue
            counters["img_without_alt"] += 1
            add("img-missing-alt", rels, m.group(0)[:100].replace("\n", " "), "check: decorative images need alt=\"\"")

        # non-crawlable links
        for m in re.finditer(r'<a\b[^>]*\bhref=["\'](#|javascript:[^"\']*)["\'][^>]*>', txt, re.I):
            add("non-crawlable-link", rels, m.group(0)[:100], "check: fine for in-page widgets, bad for navigation")

        if is_tpl:
            if re.search(r"<html\b", txt, re.I) or re.search(r"<head\b", txt, re.I):
                pages += 1
                tm = re.search(r"<title[^>]*>(.*?)</title>", txt, re.S | re.I)
                if not tm:
                    add("missing-title", rels, "No <title> in this document template (may come from a layout/partial).", "check")
                else:
                    t = tm.group(1).strip()
                    if not t:
                        add("empty-title", rels, "<title> is empty.", "high")
                    elif not is_templated(t):
                        titles[t].append(rels)
                if not re.search(r'<meta[^>]+name=["\']description["\']', txt, re.I):
                    add("missing-meta-description", rels, "No meta description in this template.", "check")
                if not re.search(r'<link[^>]+rel=["\']canonical["\']', txt, re.I):
                    add("missing-canonical", rels, "No rel=canonical in this template.", "check: self-canonical is common practice")
                else:
                    cm = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', txt, re.I)
                    if cm and cm.group(1).startswith("http://"):
                        add("canonical-http", rels, f"Canonical uses http: {cm.group(1)[:80]}", "medium")
                if re.search(r'<meta[^>]+name=["\']robots["\'][^>]*content=["\'][^"\']*noindex', txt, re.I):
                    add("noindex-meta", rels, "meta robots contains noindex.", "check: confirm intent")
                if not re.search(r'<meta[^>]+name=["\']viewport["\']', txt, re.I):
                    add("missing-viewport", rels, "No viewport meta tag.", "medium")
                if re.search(r"<html\b", txt, re.I) and not re.search(r"<html[^>]+\blang=", txt, re.I):
                    add("missing-html-lang", rels, "<html> has no lang attribute.", "low")
                if re.search(r'hreflang=', txt, re.I):
                    report["i18n"].setdefault("hreflang_files", []).append(rels)
                if not re.search(r'property=["\']og:', txt, re.I):
                    counters["no_open_graph"] += 1

        if is_cmp:
            if re.search(r"export\s+(const\s+metadata|async\s+function\s+generateMetadata|function\s+generateMetadata)", txt):
                counters["next_metadata_exports"] += 1
            if re.search(r"useSeoMeta|useHead\(", txt):
                counters["nuxt_seo_composables"] += 1
            if re.search(r"hreflang|alternates\s*:\s*\{[^}]*languages", txt):
                report["i18n"].setdefault("hreflang_files", []).append(rels)
            if re.search(r"noindex|robots\s*:\s*\{[^}]*index\s*:\s*false", txt):
                add("noindex-in-component", rels, "noindex / index:false configured.", "check: confirm intent")

    robots_mentions_sitemap = False
    for entry in report["robots"]:
        if entry.get("sitemap_directives"):
            robots_mentions_sitemap = True
        elif entry.get("dynamic") and re.search(r"sitemap", read(root / entry["file"]) or "", re.I):
            robots_mentions_sitemap = True
    if robots_mentions_sitemap and not report["sitemaps"]:
        add("sitemap-referenced-no-source-found", ", ".join(e["file"] for e in report["robots"]),
            "robots references a sitemap but no sitemap file or route was found in the repo "
            "(may be generated by a plugin, CDN or deploy step).", "check: confirm the URL resolves on the live site")

    for t, where in titles.items():
        if len(where) > 1:
            add("duplicate-static-title", ", ".join(where[:4]), f"Same literal title on {len(where)} files: {t[:70]}", "medium")

    report["counts"] = dict(counters, document_templates=pages)
    # cap examples per kind, but keep totals
    grouped, totals = defaultdict(list), Counter()
    for s in sig:
        totals[s["kind"]] += 1
        if len(grouped[s["kind"]]) < max_ex:
            grouped[s["kind"]].append(s)
    report["signals"] = [s for v in grouped.values() for s in v]
    report["signal_totals"] = dict(totals)
    report["limits"] = ["Symlinks and existing audit folders are excluded; nested package manifests are leads for separate package scans.",
                        "Static source scan only: no rendering, no network, no live-site, analytics or Search Console data.",
                        f"Files over {MAX_BYTES} bytes are skipped.",
                        "Dynamic metadata (frameworks, CMS plugins) is invisible to regex checks; confirm with a build or rendered output."]
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".")
    ap.add_argument("--out")
    ap.add_argument("--max-examples", type=int, default=25)
    a = ap.parse_args()
    root = Path(a.root).resolve()
    if not root.is_dir():
        sys.exit(f"Not a directory: {root}")
    if a.max_examples < 1:
        ap.error("--max-examples must be positive")
    r = scan(root, a.max_examples)
    out = json.dumps(r, indent=2)
    if a.out:
        with Path(a.out).open("x", encoding="utf-8") as output:
            output.write(out)
        print(f"Wrote {a.out}")
    else:
        print(out)


if __name__ == "__main__":
    main()
