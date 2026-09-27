# skillcheck log

Source of truth for the incremental skill updater in
[`skillcheck.md`](skillcheck.md). Each run of that prompt picks exactly one
skill — prefer `unaudited`/`needs-work`, else fewest runs, oldest
`last_checked` first — audits it, and appends an entry under "Log entries".
Keep the index sorted by skill name.

## Index of skills

| skill | path | runs | last_checked | status | notes |
|-------|------|------|--------------|--------|-------|
| context-optimization | skills/AI-agent-skills/context-optimization/ | 0 | — | unaudited | Imported before this log existed; no audit run recorded |
| linux-speed-optimizer | skills/system-administration-skills/linux-speed-optimizer/ | 0 | — | unaudited | Contains version-sensitive tuning commands; re-verify against current kernel/systemd docs |
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
