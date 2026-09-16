# TOC Anchors, Badges & SEO Mechanics

Read this before writing any README's Table of Contents or badge row — these are mechanical rules, not style choices, and getting them wrong silently breaks the links.

## 1. GitHub heading → anchor slug rules

GitHub auto-generates an anchor id for every Markdown heading. To link to it from a TOC, you must derive the *exact* slug:

1. Take the heading text.
2. Lowercase it.
3. Strip anything that isn't a letter, number, space, hyphen, or underscore (drop `.`, `,`, `!`, `?`, `:`, `(`, `)`, `` ` ``, `'`, `/`, `&`, emoji, etc.).
4. Replace each space with a single hyphen `-`.
5. If the resulting slug is already used by an earlier heading on the page, GitHub appends `-1`, `-2`, `-3`... for the 2nd, 3rd, 4th occurrence. **Avoid this entirely by making every heading unique** — don't rely on the numbered-suffix behavior, since it's easy to miscount and it looks unprofessional if it desyncs.

### Worked examples

| Heading | Anchor |
|---|---|
| `## Quickstart` | `#quickstart` |
| `## How It Compares` | `#how-it-compares` |
| `## FAQ` | `#faq` |
| `## Why MyProject?` | `#why-myproject` (the `?` is dropped, not replaced with a hyphen) |
| `## Related Projects` | `#related-projects` |
| `## Configuration & Options` | `#configuration--options` (the `&` is dropped, leaving a double space collapsed... in practice GitHub renders this as `#configuration--options` — when a heading contains punctuation like `&`, prefer to just avoid it and write `## Configuration and Options` → `#configuration-and-options`, which is unambiguous) |
| `## API Reference` | `#api-reference` |

**Rule of thumb: prefer plain alphanumeric headings with spaces only.** Avoid `&`, `/`, `:`, parentheses, and emoji *inside heading text* if you plan to link to it — emoji in particular render fine visually but complicate the slug (GitHub strips them, but the exact stripping can vary with emoji shortcode vs. unicode input, so it's the single most common source of a broken TOC link). If you want an emoji for visual flavor, it's safest to skip decorating linked headers.

## 2. Table of Contents construction

- Place the TOC after the hero/header block, before the first content section.
- One bullet per top-level section; nest with 2-space indents for subsections only if the README is long enough to need it (Classic Technical Docs design; skip nesting for Minimal design).
- Every TOC entry must be a real link: `- [Display Text](#anchor-slug)`. Display text can have different casing/wording than you'd want, but the anchor must match the actual heading using the rules above.
- Double check every anchor after the README is fully drafted — headings sometimes change during writing and the TOC is the thing most likely to go stale.
- For very short READMEs (roughly under ~5 sections), a TOC is still worth including for the Classic and Startup designs (readers expect it), but is optional for Minimal design if the whole doc fits in one screen.

## 3. Badges (shields.io)

Base pattern: `https://img.shields.io/{provider}/{metric}/{owner}/{repo}` or `https://img.shields.io/{provider}/{metric}/{package}` for registries. Always wrap in a link to somewhere useful (the CI run, the package page, etc.) — a badge that doesn't link anywhere is a missed opportunity and looks broken to users who click it.

Common ones:

- **License**: `https://img.shields.io/github/license/{owner}/{repo}` → link to `LICENSE`
- **CI/build status**: `https://img.shields.io/github/actions/workflow/status/{owner}/{repo}/{workflow-file}.yml` → link to the Actions tab
- **npm version**: `https://img.shields.io/npm/v/{package}` → link to the npm page
- **PyPI version**: `https://img.shields.io/pypi/v/{package}` → link to the PyPI page
- **Downloads (npm)**: `https://img.shields.io/npm/dm/{package}` (monthly) or `/dt/` (total)
- **GitHub stars**: `https://img.shields.io/github/stars/{owner}/{repo}?style=social` → link to repo
- **Latest release**: `https://img.shields.io/github/v/release/{owner}/{repo}`
- **Contributors**: `https://img.shields.io/github/contributors/{owner}/{repo}`
- **Custom static badge**: `https://img.shields.io/badge/{label}-{message}-{color}` (e.g. `docs-latest-blue`) — use for anything without a live data source; keep the label/message accurate, don't imply a live status that isn't wired up.

**Never fabricate status.** Don't add a "build: passing" badge if there's no CI configured — either wire it to real Actions/CI, or leave it out. Static badges are fine for things that are genuinely static (license, docs-available), not for things implying live monitoring.

## 4. SEO mechanics specific to README/GitHub

READMEs get discovered two ways: GitHub's own search/topics, and Google indexing the raw README page. Optimize for both:

- **First ~160 characters matter most** — put the project name and its core keyword/category in the H1 + the sentence directly under it, since this is what search snippets and GitHub's repo search weigh most heavily. Don't bury the "what is this" sentence below a big logo with no text.
- **Use the words a searcher would actually type**, once, naturally, in the opening description — e.g. if it's a "lightweight React state management library," say that phrase plainly rather than only cutesy branding language.
- **GitHub repo Topics** (the tags set in repo settings, not in the README itself) matter as much as README content for GitHub's internal search — remind the user to set these if they haven't (you can't set them from the README file itself, but it's worth a one-line mention).
- **Descriptive link text and alt text**, never "click here" — `![Screenshot of the dashboard showing real-time metrics](...)` beats `![screenshot](...)`, and both are read by crawlers and screen readers.
- **Heading hierarchy matters**: one H1 (the title), H2 for main sections, H3 for subsections. Don't skip levels (H1 straight to H3) — it confuses both readers and any doc-generation tooling.
- **Keep code blocks tagged with a language** (`` ```bash ``, `` ```python ``, etc.) — this isn't SEO exactly, but it's the single most common beginner-friendliness miss, since untagged blocks don't get syntax highlighting.
- **Internal consistency**: the project name, install command, and any package name must all agree with each other and with the actual repo — a mismatch here is the #1 thing that makes a generated README look fake.