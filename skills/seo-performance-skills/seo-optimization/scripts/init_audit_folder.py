#!/usr/bin/env python3
"""Create or reuse the durable SEO audit folder in a repository. Never overwrites.

Subcommands
  init     Find or create the audit folder and scaffold any MISSING files.
  log      Append a chronological entry to WORKLOG.md (append-only).
  next-id  Print the next unused finding ID(s), e.g. SEO-004.

Examples
  python init_audit_folder.py init
  python init_audit_folder.py next-id --count 3
  python init_audit_folder.py log --title "Audit complete" \
      --done "Wrote AUDIT.md and TASKS.md" --remaining "Awaiting task choice" --blockers none

Exit codes: 0 ok, 2 ambiguous existing folders (decide, then re-run with --folder), 3 error.
Standard library only.
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_NAME = "seo-optimization-work"
CANDIDATE_GLOBS = [
    DEFAULT_NAME, "seo-optimization", "seo-audit*", "seo-work*", "seo_audit*",
    "docs/seo-optimization-work", "docs/seo-audit*",
]
MARKERS = ("AUDIT.md", "TASKS.md", "WORKLOG.md")
SKIP = {".git", "node_modules"}


def now_iso(tz=None):
    """ISO 8601 with a UTC offset. Uses the machine's local zone unless tz is an IANA name."""
    if tz:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo(tz)).isoformat(timespec="seconds")
    return datetime.now().astimezone().isoformat(timespec="seconds")


def repo_root(explicit=None):
    if explicit:
        root = Path(explicit).resolve()
        if not root.is_dir():
            raise ValueError(f"Not a project directory: {root}")
        return root
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                             text=True, check=True).stdout.strip()
        return Path(out)
    except Exception:
        return Path.cwd()


def find_existing(root):
    """Folders that are clearly SEO audit work: the default name, or any candidate holding marker files."""
    found = []
    for pattern in CANDIDATE_GLOBS:
        for p in sorted(root.glob(pattern)):
            if p.is_dir() and not (set(p.relative_to(root).parts) & SKIP):
                if p.name == DEFAULT_NAME or any((p / m).exists() for m in MARKERS):
                    if p not in found:
                        found.append(p)
    return found


SKELETONS = {
    "README.md": """# SEO optimization work

Durable context for AI agents and humans continuing SEO / AEO / GEO work in this repository.

- **Project:** <name and type, inferred from repository evidence>
- **Audit folder path:** `{rel}`
- **Last audit:** <ISO 8601 timestamp with timezone>
- **Platforms in scope:** <e.g. Google Search, Bing; others only with evidence>

## Files
| File | Purpose |
|---|---|
| `AUDIT.md` | Latest full audit: findings, assumptions, methods, sources, status |
| `TASKS.md` | Prioritized backlog of unresolved work (stable IDs `SEO-001`...) |
| `WORKLOG.md` | Append-only chronological record. Never rewrite past entries |
| `evidence/` | Concise evidence notes. No secrets, credentials, personal data or huge raw crawls |

## How to continue (for another agent)
1. Read repository instruction files first (`AGENTS.md`, etc.), then this folder: `AUDIT.md`, `TASKS.md`, newest `WORKLOG.md` entries.
2. Re-check anything marked `likely`, `hypothesis` or `blocked` before acting; the code may have changed.
3. Continue the task(s) the user authorized, including safe fixes under an improvement request. Update the finding status, `TASKS.md`, and append to `WORKLOG.md`.
4. Do not mark anything fixed until the changed output has been verified.
""",
    "AUDIT.md": """# SEO audit

> Status: scaffold created {ts}. No audit has been written yet.

## Executive summary and context
## Platforms covered and evidence available
## Scope, date, tools and limitations
## Findings
## What is working well
## Assumptions and open questions
## Recommended next actions and risks
## Sources
""",
    "TASKS.md": """# SEO task backlog

Unresolved work only, highest priority first. IDs are stable; never reuse or renumber.

| ID | Priority | Status | Label | Title | Review required |
|---|---|---|---|---|---|
""",
    "WORKLOG.md": """# SEO work log

Append-only. One entry per session or meaningful step: what was done, what remains, blockers.
""",
}


def write_if_missing(path, text):
    if path.exists():
        return False
    try:
        with path.open("x", encoding="utf-8") as output:
            output.write(text)
        return True
    except FileExistsError:
        return False


def cmd_init(a):
    root = repo_root(a.root)
    if a.folder:
        folder = Path(a.folder)
        folder = folder if folder.is_absolute() else root / folder
    else:
        found = find_existing(root)
        if len(found) > 1:
            print(json.dumps({"status": "ambiguous",
                              "candidates": [str(p.relative_to(root)) for p in found],
                              "hint": "Pick the folder that is the same work, then re-run with --folder."},
                             indent=2))
            return 2
        folder = found[0] if found else root / DEFAULT_NAME
    if folder.exists() and not folder.is_dir():
        print(json.dumps({"status": "error", "error": f"{folder} exists and is not a directory"}))
        return 3
    folder = safe_folder(root, folder)
    for name in (*SKELETONS, "evidence"):
        if (folder / name).is_symlink():
            raise ValueError(f"Refusing symlink destination: {folder / name}")
    ts = now_iso(a.tz)
    existed = folder.exists()
    folder.mkdir(parents=True, exist_ok=True)
    try:
        rel = str(folder.relative_to(root))
    except ValueError:
        rel = str(folder)
    ts = now_iso(a.tz)
    created, kept = [], []
    for name, text in SKELETONS.items():
        target = folder / name
        (created if write_if_missing(target, text.format(rel=rel, ts=ts)) else kept).append(name)
    ev = folder / "evidence"
    if not ev.exists():
        ev.mkdir()
        (ev / ".gitkeep").write_text("", encoding="utf-8")
        created.append("evidence/")
    if "WORKLOG.md" in created:
        with open(folder / "WORKLOG.md", "a", encoding="utf-8") as fh:
            fh.write(f"\n## {ts} - Audit folder created\n- Done: scaffolded {', '.join(created)}\n"
                     f"- Remaining: run the audit and write AUDIT.md / TASKS.md\n- Blockers: none\n")
    ignored = False
    try:
        ignored = subprocess.run(["git", "-C", str(root), "check-ignore", "-q", str(folder)],
                                 capture_output=True).returncode == 0
    except Exception:
        pass
    print(json.dumps({"status": "reused" if existed else "created", "repo_root": str(root), "folder": rel,
                      "created": created, "preserved": kept, "timestamp": ts,
                      "gitignored": ignored}, indent=2))
    return 0


def safe_folder(root, folder):
    root = root.resolve()
    candidate = folder if folder.is_absolute() else root / folder
    # Reject symlinks even when their targets happen to remain in the repository.
    if any(part.is_symlink() for part in (candidate, *candidate.parents) if part != root and root in part.parents):
        raise ValueError("Audit folder must not traverse symlinks")
    candidate = candidate.resolve()
    if candidate == root or root not in candidate.parents:
        raise ValueError("Audit folder must be inside the project root")
    return candidate


def resolve_folder(a):
    root = repo_root(a.root)
    if a.folder:
        return safe_folder(root, Path(a.folder))
    found = find_existing(root)
    if len(found) > 1:
        raise ValueError("Multiple audit folders; pass --folder. IDs were not allocated.")
    return safe_folder(root, found[0]) if found else None


def cmd_log(a):
    folder = resolve_folder(a)
    if folder is None:
        print("Cannot determine a single audit folder; pass --folder.", file=sys.stderr)
        return 3
    log = folder / "WORKLOG.md"
    if log.is_symlink():
        raise ValueError("Refusing symlink WORKLOG.md")
    if not log.exists():
        log.write_text(SKELETONS["WORKLOG.md"], encoding="utf-8")
    lines = [f"\n## {now_iso(a.tz)} - {a.title}", f"- Done: {a.done}", f"- Remaining: {a.remaining}",
             f"- Blockers: {a.blockers}"]
    if a.findings:
        lines.append(f"- Findings: {a.findings}")
    if a.files:
        lines.append(f"- Files changed: {a.files}")
    if a.checks:
        lines.append(f"- Checks run: {a.checks}")
    with open(log, "a", encoding="utf-8") as fh:  # append only; history is never rewritten
        fh.write("\n".join(lines) + "\n")
    print(f"Appended entry to {log}")
    return 0


def cmd_next_id(a):
    root = repo_root(a.root)
    folder = resolve_folder(a) or (root / DEFAULT_NAME)
    if a.count < 1:
        raise ValueError("--count must be positive")
    top = 0
    for p in sorted(folder.rglob("*.md")) if folder.is_dir() else []:
        if p.is_symlink() or any(parent.is_symlink() for parent in p.parents):
            continue
        if p.is_file():
            for m in re.finditer(r"SEO-(\d{3,})", p.read_text(encoding="utf-8", errors="ignore")):
                top = max(top, int(m.group(1)))
    print("\n".join(f"SEO-{top + i + 1:03d}" for i in range(a.count)))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", help="Repository root (default: git toplevel or cwd)")
    ap.add_argument("--tz", help="IANA timezone for timestamps (default: machine local zone)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init")
    p.add_argument("--folder")
    p.set_defaults(fn=cmd_init)
    p = sub.add_parser("next-id")
    p.add_argument("--folder")
    p.add_argument("--count", type=int, default=1)
    p.set_defaults(fn=cmd_next_id)
    p = sub.add_parser("log")
    p.add_argument("--folder")
    for f in ("title", "done", "remaining", "blockers"):
        p.add_argument(f"--{f}", required=True)
    for f in ("findings", "files", "checks"):
        p.add_argument(f"--{f}")
    p.set_defaults(fn=cmd_log)
    a = ap.parse_args()
    try:
        result = a.fn(a)
    except (OSError, ValueError, KeyError) as error:
        print(f"Error: {error}", file=sys.stderr)
        result = 3
    sys.exit(result)


if __name__ == "__main__":
    main()
