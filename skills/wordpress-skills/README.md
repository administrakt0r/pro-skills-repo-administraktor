# WordPress skills

Four agent-ready skills for WordPress development, covering the full platform:
the umbrella workflow, themes, plugins, and WooCommerce stores. They target
WordPress 7.0 "Armstrong" (released May 20, 2026) and its developer surface —
the AI Client, Abilities API, PHP-only block registration, DataViews, navigation
overlays, and the breadcrumbs block.

| Skill | Use it for | Location |
| --- | --- | --- |
| `wordpress` | The end-to-end workflow: setup, themes, plugins, WooCommerce, performance, security, deployment, and the WordPress 7.0 feature set. Start here. | [`wordpress`](wordpress/) |
| `wordpress-theme-development` | Themes: `theme.json` v3, template hierarchy, block patterns, template parts, navigation overlays, breadcrumbs, block styles, child themes. | [`wordpress-theme-development`](wordpress-theme-development/) |
| `wordpress-plugin-development` | Plugins: hooks, admin UI, custom tables, REST endpoints, Abilities API, AI Client integration, PHP-only blocks, security, tests. | [`wordpress-plugin-development`](wordpress-plugin-development/) |
| `wordpress-woocommerce-development` | Stores: product setup, payment gateways, shipping, checkout, custom product types, order automation, store performance. | [`wordpress-woocommerce-development`](wordpress-woocommerce-development/) |

## Provenance and review

These skills were imported from
[`administrakt0r/AI-Agents-Safe-Coding-Skills`](https://github.com/administrakt0r/AI-Agents-Safe-Coding-Skills)
and reviewed on 2026-09-27 before inclusion. The review found no prompt injection
or obfuscated content, and corrected the factual drift listed below. Re-verify
against the WordPress release notes before relying on version-specific details.

Corrections applied during review:

- **Release date.** The source said WordPress 7.0 shipped April 9, 2026. That was
  the original target; the release slipped and shipped May 20, 2026 as
  "Armstrong".
- **Real-Time Collaboration did not ship.** The source described RTC (Yjs CRDT,
  `sync.providers`, a `WP_COLLABORATION_MAX_USERS` constant) as core 7.0
  features. RTC was pulled from the release on May 8, 2026 over race conditions,
  server load, and fuzz-test failures. The constant is not a real API. Guidance
  now marks RTC as not shipped and keeps only forward-compatible advice
  (`show_in_rest` meta registration).
- **Breadcrumb hooks.** The source used `wp_breadcrumb_args` and
  `breadcrumb_items`. The real filters are `block_core_breadcrumbs_items` and
  `block_core_breadcrumbs_post_type_settings`.
- **Navigation overlays.** The source showed hand-rolled PHP with `wp_nav_menu()`.
  7.0 overlays are template parts in `parts/`, registered with the
  `navigation-overlay` area and the `core/navigation-overlay-close` block.
- **Block patterns.** The source showed a JSON block tree with `{{placeholders}}`
  and a `contentOnly` key. Patterns are block markup (PHP files in `patterns/`
  or `register_block_pattern()`); placeholder tokens are not a core syntax.
- **Broken code.** A WooCommerce example registered
  `generate_ai_description` but defined `generate_ai_product_description`.
- **API misuse.** Several examples treated the AI client's fluent builder as
  error-first. `wp_ai_client_prompt()` returns a builder; chain
  `->using_temperature()->generate_text()` and handle `WP_Error` from the result.
- **Privacy and abuse.** Examples sent customer PII to third-party AI providers
  and exposed an unauthenticated AI endpoint. Rewritten: deterministic scoring
  first, PII redaction, rate limiting, and advisory-only model output.
- **Cross-references.** References to skills not present in this repository were
  removed, per this repository's [skill checklist](../../README.md#adding-a-skill).
- **WordPress.org Plugin Check (PCP) & coding standards.** Added requirements for
  automated WordPress.org plugin directory audits: avoiding discouraged
  `load_plugin_textdomain()` calls (WordPress 4.6+ loads JIT), using `%i`
  identifier placeholders in `$wpdb->prepare()`, annotating custom table direct
  queries and caching, handling dynamic parameter escaping, and preventing false
  positives on `WordPressVIPMinimum.Performance.WPQueryParams.PostNotIn_exclude`.

## Prerequisites

- PHP 7.4 minimum (8.3+ recommended) — WordPress 7.0 raises the floor to 7.4.
- A local WordPress install for testing (LocalWP, Docker, wp-env, or
  WordPress Playground).
- Optional but recommended: WP-CLI, and an AI provider plugin (OpenAI, Anthropic
  Claude, or Google Gemini connector) configured under Settings > Connectors if
  you are exercising the AI Client examples.

## Install

From this repository's root:

```bash
mkdir -p ~/.config/opencode/skills
cp -R skills/wordpress-skills/wordpress ~/.config/opencode/skills/wordpress
cp -R skills/wordpress-skills/wordpress-theme-development ~/.config/opencode/skills/wordpress-theme-development
cp -R skills/wordpress-skills/wordpress-plugin-development ~/.config/opencode/skills/wordpress-plugin-development
cp -R skills/wordpress-skills/wordpress-woocommerce-development ~/.config/opencode/skills/wordpress-woocommerce-development
```

Swap the destination for your agent: `~/.claude/skills/` (Claude Code) or
`~/.codex/skills/` (Codex). See the root README's skill-location table.

To have an AI agent do the install (with prompt-injection verification and
optional MCP wiring), point it at [`init.md`](init.md) in this folder.

## MCP integration

These skills prefer real WordPress data over guesswork when the site is reachable
over MCP. The supported stack is the official **MCP Adapter**
(`wordpress/mcp-adapter`), which turns Abilities API registrations into MCP tools.
Do not use the deprecated `Automattic/wordpress-mcp` plugin.

Two connection styles (config goes in your agent's MCP settings):

```jsonc
// Local site: STDIO via WP-CLI (requires WP-CLI)
{
  "mcpServers": {
    "wordpress": {
      "command": "wp",
      "args": ["--path=/path/to/wordpress", "mcp-adapter", "serve",
               "--server=mcp-adapter-default-server", "--user=agent"]
    }
  }
}
```

```jsonc
// Remote site: HTTP via the official proxy (requires Node.js + application password)
{
  "mcpServers": {
    "wordpress": {
      "command": "npx",
      "args": ["-y", "@automattic/mcp-wordpress-remote@latest"],
      "env": {
        "WP_API_URL": "https://yoursite.example/wp-json/mcp/mcp-adapter-default-server",
        "WP_API_USERNAME": "agent",
        "WP_API_PASSWORD": "xxxx xxxx xxxx xxxx xxxx xxxx"
      }
    }
  }
}
```

The default server exposes `mcp-adapter-discover-abilities`,
`mcp-adapter-get-ability-info`, and `mcp-adapter-execute-ability`. Abilities must
opt in with `'meta' => ['mcp' => ['public' => true]]`.

Security rules the skills enforce:

- Use a dedicated, least-privilege WordPress user for agent access — never an
  administrator by default.
- Keep destructive abilities off the default MCP server, or behind strict
  `permission_callback` capability checks. Never `__return_true` for writes.
- Prefer read-only abilities on internet-exposed HTTP transports; log and monitor
  everything an MCP client does.
- Treat model output as untrusted input; sanitize whatever AI tools pass into
  `execute_callback` exactly as you would REST request data.

## Related resources

- [WordPress 7.0 release notes](https://developer.wordpress.org/news/2026/05/wordpress-7-0-armstrong/)
- [Abilities API and MCP Adapter](https://developer.wordpress.org/news/2026/02/from-abilities-to-ai-agents-introducing-the-wordpress-mcp-adapter/)
- [WordPress.org MCP server for plugin submission](https://developer.wordpress.org/plugins/wordpress-org/using-the-mcp-server/)
