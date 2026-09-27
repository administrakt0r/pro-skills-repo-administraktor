# wordpress

The umbrella WordPress workflow: local setup, theme development, plugin
development, WooCommerce integration, performance optimization, security
hardening, testing, and deployment — plus the WordPress 7.0 developer surface
(AI Client, Abilities API, PHP-only blocks, DataViews) and how to expose site
functionality to AI agents over MCP.

Start here, then move to the focused skill for your task:
[`wordpress-theme-development`](../wordpress-theme-development/),
[`wordpress-plugin-development`](../wordpress-plugin-development/), or
[`wordpress-woocommerce-development`](../wordpress-woocommerce-development/).

## Prerequisites

- PHP 7.4+ (8.3+ recommended), a local WordPress install (LocalWP, Docker,
  wp-env, or WordPress Playground), and version control.
- Optional: WP-CLI; an AI provider plugin under Settings > Connectors to
  exercise the AI Client examples.

## Install

```bash
cp -R skills/wordpress-skills/wordpress ~/.config/opencode/skills/wordpress
```

## What it covers

- Eight workflow phases from setup to deployment
- WordPress 7.0 feature reference, including that Real-Time Collaboration did
  not ship in 7.0
- REST-ready post meta, AI Client usage, Abilities API registration
- WordPress MCP integration: the official MCP Adapter, connection configs for
  local (STDIO) and remote (HTTP) sites, and security rules

See the [bundle README](../README.md) for provenance, review notes, and MCP
setup detail.
