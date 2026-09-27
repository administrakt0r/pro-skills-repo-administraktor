# wordpress-plugin-development

Focused workflow for WordPress plugins: hooks, admin interfaces, database
operations, REST endpoints, security, testing, and the WordPress 7.0 plugin
surface — Abilities API, AI Client integration, PHP-only blocks, DataViews, and
exposing plugin capabilities to AI agents over MCP.

## Prerequisites

- PHP 7.4+ (8.3+ recommended) and a local WordPress install.
- Composer for the optional `wordpress/mcp-adapter` integration.
- PHPUnit (or the WooCommerce test framework) for the testing phase.

## Install

```bash
cp -R skills/wordpress-skills/wordpress-plugin-development ~/.config/opencode/skills/wordpress-plugin-development
```

## What it covers

- Nine phases: setup, architecture, hooks, admin UI, database, REST API,
  security, 7.0 features, testing
- Abilities API registration with `meta.mcp.public` for MCP exposure, and
  custom MCP servers via `mcp_adapter_init`
- Correct AI Client usage (chained fluent builder) and REST-ready post meta
- Security checklist: nonces, capabilities, sanitization, escaping, prepared SQL
- Database best practices: `%i` identifier placeholders, custom table caching
  annotations, and dynamic query parameter safety
- WordPress.org Plugin Check (PCP) compliance and automated review readiness

See the [bundle README](../README.md) for provenance, review notes, and MCP
setup detail.
