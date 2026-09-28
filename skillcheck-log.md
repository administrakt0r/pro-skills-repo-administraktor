# skillcheck log

Source of truth for the incremental skill updater in
[`skillcheck.md`](skillcheck.md). Each run of that prompt picks exactly one
skill — prefer `unaudited`/`needs-work`, else fewest runs, oldest
`last_checked` first — audits it, and appends an entry under "Log entries".
Keep the index sorted by skill name.

## Index of skills

| skill | path | runs | last_checked | status | notes |
|-------|------|------|--------------|--------|-------|
| context-optimization | skills/AI-agent-skills/context-optimization/ | 1 | 2026-09-28 | updated | Cache/compaction provider mechanics added; Codex install path corrected |
| linux-speed-optimizer | skills/system-administration-skills/linux-speed-optimizer/ | 0 | — | unaudited | Contains version-sensitive tuning commands; re-verify against current kernel/systemd docs |
| pullrequests-review-merge | skills/git-skills/pullrequests-review-merge/ | 0 | — | unaudited | Not in this log until 2026-09-28 (added in commit 6417ad4 after the last run); frontmatter name is `pr-review-merge` |
| readme-generator | skills/other-skills/readme-writing-skill/ | 0 | — | unaudited | Directory name is `readme-writing-skill`, frontmatter name is `readme-generator` |
| speckit-init | skills/development-skills/speckit-init/ | 0 | — | unaudited | Pins commands to github/spec-kit — check upstream rewrites before trusting commands |
| tui-design | skills/UI-UX-skills/TUI-skills/ | 0 | — | unaudited | Imported before this log existed; no audit run recorded |
| wordpress | skills/wordpress-skills/wordpress/ | 1 | 2026-09-27 | updated | Import audit: RTC claims corrected, AI Client usage fixed, MCP section added |
| wordpress-plugin-development | skills/wordpress-skills/wordpress-plugin-development/ | 1 | 2026-09-27 | updated | Import audit: RTC claims corrected, fluent-builder misuse fixed, MCP exposure guidance added |
| wordpress-theme-development | skills/wordpress-skills/wordpress-theme-development/ | 1 | 2026-09-27 | updated | Import audit: breadcrumb filters, navigation-overlay APIs, pattern format corrected |
| wordpress-woocommerce-development | skills/wordpress-skills/wordpress-woocommerce-development/ | 1 | 2026-09-27 | updated | Import audit: callback-name bug fixed, PII/AI examples rewritten deterministic-first, rate limiting added |

Provenance note: the four `wordpress*` skills were imported from
[`administrakt0r/AI-Agents-Safe-Coding-Skills`](https://github.com/administrakt0r/AI-Agents-Safe-Coding-Skills)
and audited during import (prompt-injection scan: clean). That import audit is
recorded below as run #1 for each.

## Log entries

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
