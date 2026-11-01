# skillcheck log

Source of truth for the incremental skill updater in
[`skillcheck.md`](skillcheck.md). Each run of that prompt picks exactly one
skill — prefer `unaudited`/`needs-work`, else fewest runs, oldest
`last_checked` first — audits it, and appends an entry under "Log entries".
Keep the index sorted by skill name.

## Index of skills

| skill | path | runs | last_checked | status | notes |
|-------|------|------|--------------|--------|-------|
| coding-guidelines-generator | skills/development-skills/coding-guidelines-generator/ | 1 | 2026-10-18 | updated | Rebuilt as modular skill; addressed Codex review feedback (26 fixtures, byte-for-byte upsert) |
| context-optimization | skills/AI-agent-skills/context-optimization/ | 1 | 2026-09-28 | updated | Cache/compaction provider mechanics added; Codex install path corrected |
| linux-speed-optimizer | skills/system-administration-skills/linux-speed-optimizer/ | 1 | 2026-11-01 | updated | Staleness fixes: kernel-bore→kernel-cachyos/scx for Fedora/openSUSE; XanMod MOK guidance clarified; systemd-boot regeneration step added; earlyoom dual-threshold note added |
| pullrequests-review-merge | skills/git-skills/pullrequests-review-merge/ | 1 | 2026-11-02 | updated | Description fixed to start with "Use when"; `gh pr merge --admin` ban made explicit; merge queue + `uv.lock` added to stack-discovery |
| readme-generator | skills/writing-skills/readme-writing-skill/ | 0 | — | unaudited | Directory name is `readme-writing-skill`, frontmatter name is `readme-generator` |
| speckit-init | skills/development-skills/speckit-init/ | 0 | — | unaudited | Pins commands to github/spec-kit — check upstream rewrites before trusting commands |
| tui-design | skills/UI-UX-skills/TUI-skills/ | 0 | — | unaudited | Imported before this log existed; no audit run recorded |
| wordpress | skills/wordpress-skills/wordpress/ | 2 | 2026-11-01 | updated | Safety: `__return_true` REST example annotated with scope/warning; Staleness: FID replaced with INP (retired March 2024) |
| wordpress-plugin-development | skills/wordpress-skills/wordpress-plugin-development/ | 2 | 2026-11-01 | updated | 7.1 update: DataViews fix (undefined handleViewChange→useState, missing paginationInfo/defaultLayouts); iframe enforced; SVG Icon API added; __next40pxDefaultSize no-op noted |
| wordpress-theme-development | skills/wordpress-skills/wordpress-theme-development/ | 2 | 2026-11-01 | updated | 7.1 update: viewport/responsive styling in theme.json, Tabs+Playlist blocks, iframed editor enforced, SVG Icon API, client-side media notes, schema URL updated |
| wordpress-woocommerce-development | skills/wordpress-skills/wordpress-woocommerce-development/ | 1 | 2026-09-27 | updated | Import audit: callback-name bug fixed, PII/AI examples rewritten deterministic-first, rate limiting added |

Provenance note: the four `wordpress*` skills were imported from
[`administrakt0r/AI-Agents-Safe-Coding-Skills`](https://github.com/administrakt0r/AI-Agents-Safe-Coding-Skills)
and audited during import (prompt-injection scan: clean). That import audit is
recorded below as run #1 for each.

## Log entries

### 2026-11-02 — pullrequests-review-merge (run #1)

Verdict: updated

Scope: `skills/git-skills/pullrequests-review-merge/SKILL.md` and
`skills/git-skills/pullrequests-review-merge/references/stack-discovery.md`.
Prompt-injection scan: **clean** — no agent-directed instructions, hidden Unicode,
encoded payloads, or remote-exec references found. Hard rule #1 already explicitly
addresses injection via PR content (treating it as data, not instructions).

Skill selection rationale: alphabetically first among four skills with `unaudited`
status (pullrequests-review-merge < readme-generator < speckit-init < tui-design).

Changes:

- **STRUCTURE (E) — description fixed to start with "Use when"**: The frontmatter
  `description` began with "Autonomous, safety-first…", violating the README's
  checklist requirement (item 5: "starts with a trigger phrase such as 'Use when'").
  Reworded to open with "Use when the user mentions…" while preserving the full
  trigger list and adding an explicit exclusion clause ("Excludes PR creation,
  branch naming, or release workflows.").

- **SECURITY (A) — `gh pr merge --admin` explicitly banned in hard rules**: Hard
  rule #2 already prohibited admin overrides generically, but the GitHub CLI's
  `--admin` flag (which bypasses branch protection, required status checks, and
  CODEOWNERS) was not named. Security research confirms this is a specific, named
  risk for unattended AI agents. Added: "This includes `gh pr merge --admin` and
  equivalent API calls that bypass required checks — do not use them even if the
  token has the privilege."

- **STALENESS (B) — merge queue guidance added to `stack-discovery.md`**: GitHub's
  merge queue feature (GA 2023, widely adopted 2024–2025 for org repos) requires
  CI workflows to trigger on the `merge_group` event in addition to `pull_request`.
  Without this guidance an agent reviewing CI config would miss a common setup gap.
  Added a "Merge queues" paragraph to the Merge method hints section covering: how
  to detect merge queue use, the `merge_group` CI trigger requirement, how to
  observe a PR's queue status via `gh pr view`, and the no-admin-bypass rule
  reinforced at point-of-use.

- **STALENESS (B) — `uv.lock` added to Python stack manifest list**: `uv` is now
  a primary Python package manager (2024+) and `uv.lock` is its lockfile. Added
  alongside `pyproject.toml` and other Python manifests in the stack discovery
  table.

Sources:
- https://cli.github.com/manual/gh_pr_merge (GitHub CLI reference; verified 2026-11)
- https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-into-your-project/merging-a-pull-request-with-a-merge-queue (GitHub Merge Queue docs; 2023–2024)
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue (merge_group trigger; 2024)
- https://owasp.org/www-project-top-10-for-large-language-model-applications/ (OWASP LLM Top 10: indirect prompt injection; 2024)
- https://github.blog/ (AI PR review risks, gh pr merge --admin bypass risks; 2024–2025)
- https://docs.astral.sh/uv/concepts/projects/layout/#the-lockfile (uv.lock lockfile; 2024)

Follow-ups:
- `readme-generator` (skills/writing-skills/readme-writing-skill/): 0 runs, unaudited.
  Next in the queue alphabetically.
- `speckit-init`: 0 runs, pins commands to `github/spec-kit` — verify commands still
  match current upstream before next run.
- `tui-design`: 0 runs, imported before log existed — full first audit needed.

### 2026-09-27 — wordpress, wordpress-theme-development, wordpress-plugin-development, wordpress-woocommerce-development (run #1, import audit)

Verdict: updated

Scope: all four skills (import-time audit, before incremental cadence started).
Prompt-injection scan: clean — no agent-directed instructions, hidden Unicode,
encoded payloads, or remote-exec references.

Changes (applied to all or specific skills):
- Release date corrected: WordPress 7.0 "Armstrong" shipped 2026-05-20, not
  2026-04-09 (original target; slipped during RC).
- Real-Time Collaboration: marked as did-not-ship (pulled from 7.0 on
  2026-05-08). Removed invented `WP_COLLABORATION_MAX_USERS` constant and
  core `sync.providers` claims; kept forward-compatible advice only.
- `wordpress-theme-development`: breadcrumb filters corrected to
  `block_core_breadcrumbs_items` / `block_core_breadcrumbs_post_type_settings`;
  navigation overlays rewritten to `parts/` + `navigation-overlay` area +
  `core/navigation-overlay-close`; block patterns corrected to block markup
  (removed `{{placeholder}}` JSON tree); removed invented CSS custom properties.
- `wordpress-woocommerce-development`: fixed `add_action` callback-name bug
  (registered `generate_ai_description`, defined
  `generate_ai_product_description`); rewrote PII-to-AI fraud/validation
  examples as deterministic-first with redaction; added rate limiting to the
  public AI Q&A endpoint; demoted model output to advisory.
- All skills: AI Client examples fixed to chain the fluent builder
  (`->using_temperature()->generate_text()`), external skill references removed
  (repo checklist rule), frontmatter converted to repo convention
  ("Use when…" descriptions with exclusions).
- Added WordPress MCP guidance: official MCP Adapter (`wordpress/mcp-adapter`),
  STDIO/HTTP connection configs, `meta.mcp.public`, least-privilege rules;
  explicitly flags deprecated `Automattic/wordpress-mcp`.

Sources:
- https://wordpress.org/news/2026/05/armstrong/ (2026-05-20)
- https://make.wordpress.org/core/2026/05/14/wordpress-7-0-field-guide/ (2026-05-14)
- https://make.wordpress.org/core/2026/03/04/breadcrumb-block-filters/ (2026-03-04)
- https://make.wordpress.org/core/2026/03/04/customisable-navigation-overlays-in-wordpress-7-0/ (2026-03-04)
- https://developer.wordpress.org/news/2026/02/from-abilities-to-ai-agents-introducing-the-wordpress-mcp-adapter/ (2026-02-04)
- https://make.wordpress.org/core/2026/03/24/introducing-the-ai-client-in-wordpress-7-0/ (2026-03-24)

Follow-ups:
- Re-verify against the WordPress 7.1 release notes when published; several
  notes say "full enforcement in 7.1".
- Real-Time Collaboration: watch for the announced feature-plugin phase; when
  it lands, revisit the forward-compat guidance in all four skills.
- The MCP Adapter API (`create_server()` signature, default tool names) should
  be re-checked at the next run — it is versioned independently of core.

### 2026-09-28 — context-optimization (run #1)

Verdict: updated

Scope: `skills/AI-agent-skills/context-optimization/` only. Chosen because five
skills were tied at 0 runs and `unaudited`, and alphabetical tie-break puts
`context-optimization` first. Prompt-injection scan: clean — no agent-directed
instructions, hidden Unicode (scanned for zero-width and bidi-override
characters), encoded payloads, remote-exec references, or secret-handling
advice. Examples carry no security-relevant defaults. Frontmatter parses, `name`
matches the directory, description starts with "Use when" and states its
exclusion, and every referenced file exists.

Changes:
- `SKILL.md` cache section: added the provider-side caveats that were missing —
  minimum cacheable prefix (commonly ~1,024 tokens, higher for some models),
  byte-exact prefix matching, short idle TTLs refreshed on use (~5 minutes, up
  to an hour on some providers), writes costing more than uncached input while
  reads are discounted, and measuring real hit rate from provider usage fields.
- `SKILL.md` compaction section: noted compaction is lossy by design, runtimes
  keep a configurable slice of recent turns beside the summary, and
  server-side context management (clearing old tool results before token
  counting and cache lookup) is preferable to hand-rolled trimming when the
  platform offers it.
- `SKILL.md` trigger paragraph: added that quality decays before the window
  fills (recall and instruction-following weaken as the window grows) — the
  current framing only triggered on utilization or visible quality drop.
- `references/optimization-techniques.md`: new section 8, "Provider cache and
  compaction mechanics" (verified table for OpenAI and Anthropic caching,
  byte-exact-prefix and rate-limit caveats, server-side context management on
  Anthropic/OpenAI/OpenCode, with source links and a re-verify warning).
- `SKILL.md` reference-file paragraph updated to list the reference's actual
  contents (also covers the previously unlisted failure-mode table).
- `README.md`: install locations corrected — Codex reads user skills from
  `~/.agents/skills` (repo: `.agents/skills`) per the official docs, not
  `~/.codex/skills`; OpenCode global `~/.config/opencode/skills` confirmed and
  its `~/.claude/skills` / `~/.agents/skills` compatibility paths added.

Sources (consulted 2026-09-28):
- https://developers.openai.com/api/docs/guides/prompt-caching (OpenAI prompt
  caching; 1,024-token minimum for GPT-5.6+, 0.1x read rate, 5–10 min TTL)
- https://platform.claude.com/docs/en/build-with-claude/prompt-caching
  (Anthropic prompt caching; breakpoints, 5 min TTL refreshed on use, 1 h TTL,
  1.25x/2x write, 0.1x read)
- https://platform.claude.com/docs/en/build-with-claude/context-editing
  (Anthropic context editing: server-side tool-result and thinking clearing,
  placeholders, memory-tool pairing)
- https://developers.openai.com/api/reference/resources/responses/methods/compact
  (OpenAI Responses compaction operation)
- https://opencode.ai/v2/docs/compaction/ (OpenCode V2 compaction;
  `compaction.keep.tokens` 15,000 default, `buffer` 10%, native provider
  compaction)
- https://opencode.ai/v2/docs/skills/ (OpenCode V2 skill discovery locations)
- https://developers.openai.com/codex/skills (Codex "Build skills"; USER scope
  `$HOME/.agents/skills`, REPO `.agents/skills`, ADMIN `/etc/codex/skills`)
- https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  (published 2025-09; compaction and sub-agent framing matches the skill)
- https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools
  (Claude Cookbook, published 2026-03-20; memory vs compaction vs tool clearing)

Sources disagreed on Anthropic's minimum cacheable prefix (1,024 tokens for some
models, 4,096 or 512 for others depending on channel and model generation), so
the skill states "1,024 tokens for many models, higher for some" and points at
the per-model docs rather than a single number. Third-party installers also
still use `~/.codex/skills` via `CODEX_HOME`; the skill follows the official
OpenAI location table.

Follow-ups:
- Re-verify the provider table in section 8 at the next run or before any
  release; TTLs, minimums, and read discounts are all in flux.
- Root `README.md` repo index is stale: the Skills table and the "Nine skills in
  five categories" line do not include `pullrequests-review-merge`
  (skills/git-skills/, added in commit 6417ad4), which also breaks the repo's
  own `#adding-a-skill` checklist items 2 and 3. Out of scope for this run —
  fix on the next run, or when that skill is audited.
- `tui-design`, `linux-speed-optimizer`, `readme-generator`, `speckit-init`, and
  `pullrequests-review-merge` remain 0-run `unaudited`; next run picks by the
  standard tie-break (currently `linux-speed-optimizer`).

### 2026-10-18 — coding-guidelines-generator (run #1)

Verdict: updated

Scope: `skills/development-skills/coding-guidelines-generator/` only. Prompt-injection scan: clean — no agent-directed instructions, hidden Unicode, encoded payloads, or remote-exec scripts.

Changes:
- Rebuilt skill into modular architecture: router-only `SKILL.md` (<150 lines), stdlib-only detector `scripts/detect_stack.py`, marker-based upsert script `scripts/upsert_section.py`, modular `references/` guides, and asset templates.
- Addressed all automated Codex PR review feedback:
  - Added all advertised detector branches in `detect_stack.py`: Java backend (`pom.xml`, non-Android Gradle), Shell (`*.sh`, `.shellcheckrc`), static HTML/CSS (`index.html`), and Generic fallback (`references/generic.md`).
  - Scoped Android detection to target directory to eliminate duplicate module detections between root and `app/`.
  - Added dynamic declared Python version extraction (`pyproject.toml`, `.python-version`, `setup.cfg`) and added Python 3.8/3.9 compatibility guidance in `references/python.md`.
  - Fixed monorepo traversal truncation past `MAX_FILES_SCANNED` cap by decoupling file collection limits from directory enumeration.
  - Constructed dynamic AGENTS.md links matching only detected stacks; converted `assets/agents-md-section.md` into a `{stack_links}` template.
  - Rewrote relative cross-guideline notes in `references/nextjs.md`, `references/react.md`, and `references/wordpress.md` to reference generated `./AGENTS-GUIDELINES-*.md` files instead of unresolvable internal paths.
  - Updated Next.js verification to use `{pm} run lint` and noted Next.js 16+ `next lint` deprecation.
  - Added `--substitute KEY=VAL` (`-s`) to `upsert_section.py` for template substitution (e.g. `{pm}` -> `pnpm`).
  - Refactored `apply_upsert` in `upsert_section.py` to ensure 100% byte-for-byte fidelity of existing user content outside markers.
  - Expanded test suite `tests/run_tests.py` to 26 fixture test cases plus upsert lifecycle, substitution, and byte-preservation tests.

Sources:
- Official Next.js Documentation (2026-10-18): App Router, Server Actions, Next.js 15/16 caching and CLI updates
- Official React Documentation (react.dev, 2026-10-18): Hooks rules, React 19 compiler & Server Components
- Official WordPress Handbook (2026-10-18): Theme.json v3, Nonces, Capabilities, REST APIs
- PEP 585 & PEP 604 (2026-10-18): Type hinting generics and union syntax compatibility

Follow-ups:
- Re-verify Python 3.14 features when shipped.


### 2026-11-01 — linux-speed-optimizer (run #1)

Verdict: updated

Scope: `skills/system-administration-skills/linux-speed-optimizer/` only.
Prompt-injection scan: **clean** — no agent-directed instructions, hidden
Unicode, encoded payloads, or remote-exec references found.

Changes:

- **§4.7 (Custom kernel) — openSUSE**: Removed stale `kernel-bore` entry.
  `kernel-bore` is not available in official openSUSE repos. Modern openSUSE
  Tumbleweed (kernel ≥ 6.12) ships `sched_ext` natively; the correct
  recommendation is `sudo zypper install scx`. No custom kernel needed.
- **§4.7 (Custom kernel) — Fedora**: Clarified from vague "kernel-bore or
  XanMod COPR" to `kernel-cachyos` via CachyOS COPR
  (`bieszczaders/kernel-cachyos`; BORE scheduler), with XanMod COPR as an
  alternative. This matches the actual active community kernel project.
- **§4.7 (Custom kernel) — XanMod Secure Boot**: Tightened wording from
  "Setup Mode or MOK enrollment" to explicitly state XanMod kernels are unsigned
  by default and require `mokutil --import` self-signing workflow; noted that
  `bootctl status` is an alternative check when `mokutil` is unavailable.
- **§4.7 (Custom kernel) — Arch**: Clarified that `linux-zen` is in the
  official `extra` repo (not AUR) and does not require unofficial repositories.
- **§8 (Distribution matrix) — Custom kernel row**: Updated openSUSE from
  `kernel-bore` to `scx (sched_ext, kernel ≥ 6.12)`; updated Fedora from
  `kernel-bore` to `kernel-cachyos (BORE)`.
- **§8 (systemd-boot footnote)**: Expanded from a single-line mention of
  `/etc/kernel/cmdline` to include the mandatory regeneration step
  (`sudo kernel-install add-all` for UKI layouts, or editing the BLS entry
  file directly), and added a post-reboot verification via `cat /proc/cmdline`.
  Without this step, edits to `/etc/kernel/cmdline` have no effect.
- **§4.3 (earlyoom)**: Added a note documenting the `-m PERCENT[,KILL_PERCENT]`
  dual-threshold syntax available since earlyoom v1.8+, with a version-check
  reminder. The existing `-m 5 -s 5` example was preserved (correct syntax);
  only the explanatory prose was extended.

Sources:
- https://github.com/systemd/zram-generator (zram-generator config reference;
  current as of 2026-11)
- https://fedoraproject.org/wiki/Changes/EnableSystemdOomd (systemd-oomd Fedora
  default since F34; confirmed still the default 2026)
- https://copr.fedorainfracloud.org/coprs/bieszczaders/kernel-cachyos/
  (CachyOS COPR for Fedora; includes BORE scheduler; verified 2026-11)
- https://xanmod.org (XanMod APT repo, key path, package names; verified 2026-11)
- https://linuxcapable.com/install-xanmod-kernel-on-ubuntu/ (XanMod Secure Boot
  unsigned status, MOK workflow; 2025/2026)
- https://wiki.archlinux.org/title/Unified_kernel_image (kernel-install / UKI /
  `/etc/kernel/cmdline`; Arch wiki, 2026)
- https://fedoraproject.org/wiki/Changes/systemd_boot (Fedora systemd-boot /
  UKI; kernel-install add-all; 2026)
- https://opensuse.org / OBS search for `scx` (openSUSE Tumbleweed sched_ext
  package; verified 2026-11)
- https://github.com/rfjakob/earlyoom (earlyoom README; v1.8+ `-m PERCENT[,KILL]`
  syntax; 2025/2026)
- https://kernel.org/doc/html/latest/admin-guide/sysctl/vm.html
  (`vm.page-cluster` still present in kernel 6.x; verified 2026-11)

Follow-ups:
- The `linux-speed-optimizer` skill is **not listed** in the repo root
  `README.md` skills table. The table currently shows 35 skills but omits this
  one. Fix when the README is next updated or on a dedicated README-refresh run.
- Re-verify `sched_ext` / `scx` package name stability on openSUSE Tumbleweed
  at next run (the `scx` package was relatively new as of 2026-11).
- earlyoom default thresholds (currently `-m 5`) are quite aggressive (triggers
  at 5% free memory); consider annotating with a recommended range (10–15%) in
  a future pass without changing the example syntax.
- `pullrequests-review-merge`, `readme-generator`, `speckit-init`, and
  `tui-design` remain 0-run `unaudited`; next run picks by tie-break
  (alphabetically: `pullrequests-review-merge`).

### 2026-11-01 — wordpress (run #2)

Verdict: updated

Scope: `skills/wordpress-skills/wordpress/SKILL.md` only (the entry/router skill).
Prompt-injection scan: **clean** — no agent-directed instructions, hidden Unicode,
encoded payloads, or remote-exec references found.

Skill selection rationale: user requested WordPress skill enhancement; all four
WordPress skills are tied at run #1 / 2026-09-27. Alphabetically, `wordpress`
(the router skill) comes first among the four.

Changes:

- **§ Custom REST API Endpoint — safety annotation**: The example used
  `'permission_callback' => '__return_true'` with no comment or context. The
  skill's own MCP security section explicitly prohibits `__return_true` on
  state-changing abilities, but gave no guidance in the REST endpoint example (a
  common place developers copy from). Added four inline comment lines explaining
  when `__return_true` is acceptable (public read-only data only), what to use
  instead (a `current_user_can()` check), and that it must never appear on
  POST/PUT/DELETE routes or routes returning private data. No functionality changed;
  the GET example itself is valid for a public book list.

- **§ Performance Checklist — FID retired → INP**: The checklist item
  `- [ ] First Input Delay < 100ms` is stale. Google officially retired FID as a
  Core Web Vital on March 12, 2024 and replaced it with **Interaction to Next
  Paint (INP)** — threshold ≤ 200ms, measuring all interactions throughout the
  visit (not just the first). Replaced the FID item with the INP equivalent and
  added a parenthetical noting FID's retirement date so readers understand why.

Sources:
- https://web.dev/articles/inp (Google web.dev, INP overview; FID retirement
  confirmed March 12, 2024; verified 2026-11)
- https://corewebvitals.io/core-web-vitals/inp-vs-fid (INP vs FID comparison;
  thresholds; 2024/2026)
- https://developer.wordpress.org/rest-api/extending-the-rest-api/adding-custom-endpoints/
  (WordPress developer docs, REST endpoint registration; verified 2026-11)
- https://wordpress.org (WordPress 7.0 "Armstrong" release notes; May 20, 2026)

Follow-ups:
- **`wordpress-plugin-development`**: The `DataViews` example (Phase 4) references
  undefined `handleViewChange` — should be a `useState`-driven setter. Makes the
  example non-functional. Fix on the next run targeting that skill.
- **`wordpress-plugin-development`**: `gemini-2-pro` used as a model name string
  in `using_model_preference()` — should be annotated as illustrative.
- **`wordpress-woocommerce-development` §8 Testing**: "Verify collaboration features"
  remains in Phase 8 testing checklist even though RTC is noted as not shipped.
  Minor inconsistency; flag for next pass.
- Four 0-run unaudited skills remain: `pullrequests-review-merge`,
  `readme-generator`, `speckit-init`, `tui-design`. Alphabetically next:
  `pullrequests-review-merge`.

### 2026-11-01 — wordpress-plugin-development (run #2)

Verdict: updated

Scope: `skills/wordpress-skills/wordpress-plugin-development/SKILL.md` only.
Prompt-injection scan: **clean** — no agent-directed instructions, hidden Unicode,
encoded payloads, or remote-exec references found.

Skill selection rationale: user requested sequential WordPress skill enhancement;
alphabetically next after `wordpress` among the four. User confirmed latest
WordPress is 7.1.4 ("Mary Lou", released August 19, 2026).

Changes:

- **Overview banner**: Added release callout — WordPress 7.1.4 "Mary Lou",
  August 19, 2026; PHP 8.2+ recommended for new projects (was silent on version).

- **RTC note extended**: "did not ship in 7.0" → "did not ship in 7.0 or 7.1"
  (RTC was deferred again from the 7.1 cycle).

- **DataViews example — code bug fixed (critical)**: The example called
  `onChangeView={handleViewChange}` where `handleViewChange` was never defined —
  an uncaught ReferenceError at runtime. Rewrote the example as a proper
  controlled component using `useState(setView)` from `@wordpress/element`,
  with a `useMemo`-based pagination slice, and all required props populated:
  `paginationInfo`, `defaultLayouts`. Added inline comments explaining
  the controlled-component requirement.

- **DataViews 7.1 breaking changes documented**:
  - `__next40pxDefaultSize` is now a deprecated no-op (40px is the unconditional
    default for all form controls); removed from checklist as an opt-in step.
  - `css` prop on layout components no longer works (Emotion → SCSS Modules
    migration); must use `className` or `style`.
  - Server-side view-config injection via REST filters now available.

- **Iframed editor 7.1 enforcement**: In 7.0 the iframe was opt-in; in 7.1 it is
  unconditional. Added detailed guidance: avoid `document.querySelector()` inside
  block JS (use `element.ownerDocument` or `element.getRootNode()`); `vw`/`vh`
  units resolve against the iframe canvas; styles must be enqueued via
  `editor_style` in `block.json`. Added to features list, testing priorities,
  and compatibility checklist.

- **SVG Icon API (new in 7.1)**: Added a full PHP example for
  `wp_register_icon_collection()` / `wp_register_icon()` / `wp_get_icon()` /
  `wp_unregister_icon()`, with notes on `fill="currentColor"` for theme-color
  inheritance and the conservative `wp_kses` sanitizer constraint.
  Added to features list and compatibility checklist.

- **Interactivity API import path clarified**: Testing priority updated to
  explicitly say `import { watch } from '@wordpress/interactivity'` (not the
  old internal `@wordpress/signals` path that was removed).

- **Abilities API 7.1 expansion noted**: brief mention that 7.1 expanded the
  API for richer external-application permission discovery.

- **Compatibility checklist updated**: Added `block.json` `"apiVersion": 3`
  requirement; tightened DataViews entry; added iframed-editor and SVG icon items.

Sources:
- https://wordpress.org/news/2026/08/mary-lou/ (WordPress 7.1 "Mary Lou" release
  announcement; August 19, 2026)
- https://make.wordpress.org/core/ (WordPress 7.1 dev notes — iframed editor
  enforcement, DataViews Emotion→SCSS, 40px controls; 2026-08)
- https://developer.wordpress.org/block-editor/reference-guides/packages/packages-dataviews/
  (DataViews component reference; verified 2026-11)
- https://developer.wordpress.org/block-editor/how-to-guides/iframed-editor/
  (iframed editor compatibility guide; verified 2026-11)
- https://make.wordpress.org/core/2026/ (SVG Icon API: wp_register_icon_collection,
  wp_register_icon, wp_get_icon; REST endpoints; kses sanitizer notes; 2026-08)

Follow-ups:
- `wordpress-theme-development`: also mentions iframed editor as opt-in (7.0
  framing); needs same enforcement update, plus 7.1 new blocks (Tabs, Audio
  Playlist), per-device responsive controls, and client-side media processing notes.
- `wordpress-woocommerce-development`: RTC "Verify collaboration features" in Phase
  8 testing checklist still present; also needs 7.1.4 version banner.
- After all four WordPress skills are updated, consider a cross-skill consistency
  pass to ensure version references are unified.

### 2026-11-01 — wordpress-theme-development (run #2)

Verdict: updated

Scope: `skills/wordpress-skills/wordpress-theme-development/SKILL.md` only.
Prompt-injection scan: **clean** — no agent-directed instructions, hidden Unicode,
encoded payloads, or remote-exec references found.

Skill selection rationale: third WordPress skill in alphabetical sequence; user
confirmed sequential update pass. WordPress 7.1.4 "Mary Lou" is latest.

Changes:

- **Overview + version banner**: Added release callout (7.1.4 "Mary Lou",
  August 19, 2026; PHP 8.2+ recommended). Description frontmatter updated to
  mention 7.0/7.1.

- **Features section restructured**: Split 7.0 vs 7.1 features explicitly.
  Added seven new 7.1 entries: new blocks (Tabs, Playlist), per-device
  responsive styling, client-side media processing, enforced iframed editor,
  SVG Icon API, and the viewport schema key.

- **theme.json schema URL corrected**: Was `schemas.wp.org/trunk/theme.json`
  (tracks unstable HEAD). Updated to version-pinned
  `schemas.wp.org/wp/7.1/theme.json`. Using `trunk` in production is incorrect
  as schema shape changes without notice.

- **`settings.viewport` + responsive block styling added to theme.json example**:
  Added `"viewport": {"mobile":"480px","tablet":"782px"}` to `settings`, and
  a `"@mobile"` override under `styles.blocks.core/group` as a concrete example.
  Added a callout box explaining compilation rules, the no-`@desktop` convention,
  and validation/collision behaviour.

- **Template Considerations updated (7.1 iframe enforcement)**: Replaced
  "Test with iframed editor" with actionable guidance: enqueue editor styles via
  `editor_style` / `add_theme_support('editor-styles')`; avoid `vw`/`vh` in block
  CSS or prefer `cqw`/`cqh`; added to testing checklist.

- **New Tabs block pattern example added**: Full `patterns/product-tabs.php` with
  the correct `core/tabs → core/tab-list → core/tab-panels → core/tab-panel`
  hierarchy. Without the full child chain the block will not render.

- **Icon Block section updated (7.1 SVG API)**: Replaced the old "patterns only"
  note with the new `wp_register_icon_collection()` / `wp_register_icon()` API,
  including `fill="currentColor"` guidance. Kept the pattern fallback for
  pre-7.1 environments.

- **Client-side media processing guidance added**: Use `wp_get_attachment_image()`
  for `srcset`/`sizes` correctness; audit `add_image_size()` for duplicates
  (7.1 deduplication); HEIC original preserved in `$metadata['original']`.

- **Testing Checklist expanded**: Added iframed editor, responsive breakpoint
  toggle, new Tabs/Playlist block test, HEIC/AVIF upload test.

- **Theme Checklist updated**: Added viewport/breakpoints, `editor_style`
  requirement, new blocks, SVG Icon API, image output function, image size audit.

Sources:
- https://wordpress.org/news/2026/08/mary-lou/ (WP 7.1 "Mary Lou" release; 2026-08-19)
- https://make.wordpress.org/core/2026/ (dev notes: responsive editing, viewport
  schema, iframed editor enforcement, client-side media; 2026-08)
- https://schemas.wp.org/wp/7.1/theme.json (official theme.json v3 schema; 2026)
- https://developer.wordpress.org/themes/global-settings-and-styles/ (theme.json
  settings.viewport reference; verified 2026-11)
- https://wordpress.org/documentation/article/core-blocks/ (core/tabs, core/playlist
  block structure; verified 2026-11)
- https://make.wordpress.org/core/2026/ (client-side media: wasm-vips, HEIC/AVIF,
  wp_generate_attachment_metadata 'update' context; 2026-08)

Follow-ups:
- `wordpress-woocommerce-development`: last remaining WordPress skill at run #1
  (2026-09-27). Needs 7.1.4 banner; "Verify collaboration features" in Phase 8
  testing checklist should be removed or qualified; DataViews 7.1 changes relevant
  to order management screens (40px controls, css prop deprecated); client-side
  media relevant to product images.
