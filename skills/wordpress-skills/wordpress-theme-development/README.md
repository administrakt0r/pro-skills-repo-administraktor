# wordpress-theme-development

Focused workflow for WordPress themes: `theme.json` v3, the template hierarchy,
block patterns, template parts, navigation overlays, the breadcrumbs block,
block styles, child themes, and the WordPress 7.0 theme feature set.

## Prerequisites

- PHP 7.4+ (8.3+ recommended) and a local WordPress install.
- A working knowledge of block markup and `theme.json` structure.

## Install

```bash
cp -R skills/wordpress-skills/wordpress-theme-development ~/.config/opencode/skills/wordpress-theme-development
```

## What it covers

- Eight phases: setup, templates, theme functions, custom post types, block
  editor support, styling, 7.0 features, testing
- Correct 7.0 APIs: `navigation-overlay` template part area with
  `core/navigation-overlay-close`; `block_core_breadcrumbs_items` and
  `block_core_breadcrumbs_post_type_settings` filters; pattern files as block
  markup in `patterns/`; pseudo-elements in `theme.json`
- Theme structure and a 7.0 compatibility checklist

See the [bundle README](../README.md) for provenance and review notes.
