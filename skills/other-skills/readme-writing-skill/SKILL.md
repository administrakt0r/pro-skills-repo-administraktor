---
name: readme-generator
description: Use whenever the user wants to create, rewrite, or improve a README.md for a GitHub/GitLab repo, project, library, CLI tool, app, or package. Trigger on "write me a README", "make a README for this repo", "improve my project's README", "make my repo/GitHub page look professional", or requests for repo docs, project landing content, or quickstart docs. Also trigger when the user pastes project details, a package.json/pyproject.toml, or a repo link and asks for docs. Interviews the user with targeted questions, offers 4 distinct visual/structural README designs to pick from, researches any related or inspirational projects named, and produces a polished, SEO-optimized, beginner-friendly README.md with a full table of contents, working anchor links, badges, and a real quickstart. Not for generic blog posts or non-repo documentation.
---

# README Generator

A skill for producing genuinely great, visually striking `README.md` files for code repositories — the kind that make a project look alive, trustworthy, and easy to try in under 60 seconds.

This is a **conversational, interview-driven** skill. Do not skip straight to generating a generic README. The interview is what makes the output good — it's the difference between a template and a README that actually sells the project.

## Why the interview matters

A README has about 8 seconds to convince a visitor to keep reading, and about 2 minutes to get them from "landed on this page" to "it's running on my machine." Nearly every mediocre README fails because it was written by someone who already knows the project inside out and forgot what a stranger needs. Your job is to extract that context before writing a single line.

---

## Workflow

### Step 1 — Quick project scan (do this silently, before asking anything)

Before asking the user anything, check what's already available so you don't ask questions you can answer yourself:

- If a repo/folder is attached or accessible, look for `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `setup.py`, `composer.json`, existing `README*`, `LICENSE`, `.github/workflows/*`, and a rough file tree. Use `view` / `bash_tool` if you have filesystem access.
- Pull out: project name, language(s), existing description/keywords, dependencies, entry points, existing license, existing CI badges.
- If the user gave a GitHub URL instead of files, use `web_fetch` on it to pull the same information (description, topics, languages, license, latest release tag, stars — stars/forks can be nice to know but never fabricate a number; only cite what you actually fetched).

Never make the user re-type information you can already see. Only ask about what's genuinely missing or ambiguous.

### Step 2 — Ask the interview questions

Ask concise, grouped questions — not twenty separate messages. If you have a tool for presenting selectable options to the user (a multiple-choice / button UI), use it for the design pick and any other clearly single-select question; otherwise ask them as a short numbered list in one message. Skip any question you already answered in Step 1. Keep this to as few turns as possible — batch related questions together.

**A. The essentials**
1. Project name + a one-sentence description of what it does and who it's for (if not already obvious from the scan).
2. What kind of project is this? (library/package, CLI tool, web app, API/backend service, ML model or dataset, VS Code/browser extension, mobile app, game, other)
3. Who's the primary audience? (total beginners, experienced devs in this language/ecosystem, both)

**B. The design pick — always show these 4 options (see `references/design-styles.md` for full specs)**

Present these as a genuine choice, briefly described:

1. **Minimal & Badge-Driven** — clean, text-forward, dense badge row, favored by mature libraries and CLI tools that want to look serious and low-fuss (think: minimalist OSS infra project).
2. **Visual Hero / Landing Page** — centered logo/banner, big tagline, screenshot or GIF near the top, feature grid with emoji or icons; favored by apps, tools with a UI, and anything that benefits from being *seen* before being *read*.
3. **Classic Technical Docs** — traditional, thorough, TOC-heavy, closer to a manual; favored by libraries/APIs with a lot of configuration options or that will be read by engineers evaluating it for production use.
4. **Startup / Product Landing** — punchy marketing tone, social proof section, "why we built this," comparison table vs. alternatives; favored by projects trying to build a community or attract contributors/users fast.

If the user is unsure, recommend one based on project type from step A (e.g., a CLI tool → Minimal; a UI app → Visual Hero) and say why, but let them override.

**C. Content that makes the README actually useful**
4. Key features — a short list (3–7 bullet points) of what it does. If the user doesn't have this ready, offer to draft it from the code/package files you scanned and let them correct it.
5. Tech stack / languages / frameworks used.
6. How is it installed and how is it run? (package manager command, Docker, binary download, etc.) Get the *exact* commands — never invent install commands you're not sure of.
7. A minimal working quickstart example (a few lines of code or CLI usage) showing the smallest possible "it works" moment. This is the single highest-leverage section in the whole README — press for a real example rather than a placeholder.
8. License (or "not sure yet" — in which case ask if they want a recommendation, and note MIT is the common permissive default, without deciding for them).

**D. Research & promotion — always ask this explicitly**
9. "Are there any related projects, inspirations, alternatives, or your own other repos/sites you'd like me to research and reference or link to in this README (e.g. in an Acknowledgments, Related Projects, or 'Built with' section)?" Take any names or URLs given.

**E. Nice-to-haves (ask briefly, single message, skip what doesn't apply)**
10. Do you have a logo, screenshot, or demo GIF to reference or placeholder for?
11. Do you want a Contributing section, Code of Conduct, roadmap/FAQ, or "Star History" section?
12. Any badges you specifically want (build status, version, downloads, Discord/community link, sponsor link) beyond the defaults for your chosen design?
13. Any social/contact links (Twitter/X, Discord, docs site, demo/live URL)?

Don't block on every single nice-to-have — reasonable defaults are fine (e.g. include a Contributing section by default unless told not to; skip Code of Conduct unless requested).

### Step 3 — Research phase

For every project, URL, or name given in question 9 (and for the project's own category in general, if useful):

- `web_search` and/or `web_fetch` each one. Get: what it is, what it's for, and its actual relationship to this project (inspiration, alternative, dependency, prior work by the same author, etc.).
- Never quote their descriptions verbatim — write a short original sentence or two per project, per the copyright rules (paraphrase, one detail at a time, no reproduced marketing copy).
- Slot these in naturally: a comparison table (Startup/Product Landing design), a "Related Projects" or "Built With" section, or inline acknowledgment — whichever fits the chosen design and reads as genuine credit rather than a spam link.
- If a "why choose this over X" comparison is wanted, keep it factual and fair — don't disparage alternatives; contrast on features/tradeoffs only.

### Step 4 — Draft the README

Read `references/design-styles.md` for the full template of whichever design was picked, and `references/seo-and-structure.md` for the TOC/anchor/SEO rules — both are required reading before writing, every time, since they contain the exact mechanics (anchor slug rules, badge syntax, heading hierarchy) that make the output actually work on GitHub rather than just look right in the response.

Universal requirements for every design:

- **H1 title** with the project name, ideally with the core keyword/category naturally in the tagline right under it (e.g. "A fast, zero-dependency **Markdown parser** for Node.js") — this is what search engines and GitHub's own search index primarily weigh.
- **Table of Contents** near the top, using real anchor links generated with the exact slug rules in `references/seo-and-structure.md` (do not guess — GitHub's slugify rules are specific and this skill gets them wrong constantly if you don't check).
- **Quickstart / Installation** within the first screen-and-a-half of content — a beginner should never have to scroll past marketing copy to find the install command.
- Badges (via shields.io — see reference file for exact URL patterns) relevant to the design chosen; never fabricate a badge that implies false status (e.g. a "build passing" badge with no real CI).
- Beginner-friendly language: define any jargon on first use, keep the quickstart copy-pasteable with no unstated assumptions (state the required Node/Python/etc. version).
- Alt text on every image (`![Descriptive alt text](url)`) — required for accessibility and it's also read by search engines.
- A closing section with License, and Contributing if applicable, and a way to star/watch/follow.
- Section headers that are unique (GitHub anchor slugs collide and get `-1`, `-2` suffixes on duplicates — avoid this by keeping headers distinct, per the reference file).

### Step 5 — Deliver

Create the actual `README.md` file (this is a real file deliverable — always create it, don't just paste it in chat) and present it to the user. Briefly summarize what design was used and what's still a placeholder (e.g. "add your actual demo GIF here," "swap in your real repo URL," "confirm the license") so nothing fake ends up shipped by accident.

If the user wants to iterate ("make it punchier," "add a roadmap," "swap to the other design"), just edit the file directly rather than re-running the whole interview.

---

## Reference files

- `references/design-styles.md` — full template + section order + tone notes for all 4 designs. Read the one the user picked (or all 4 if helping them decide).
- `references/seo-and-structure.md` — GitHub anchor-link slug rules, TOC construction, badge (shields.io) syntax, and SEO mechanics specific to README files on GitHub/Google.