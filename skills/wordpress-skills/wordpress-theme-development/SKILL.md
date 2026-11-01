---
name: wordpress-theme-development
description: >-
  Use when creating or converting WordPress themes: theme.json v3, template hierarchy, block patterns, template parts, navigation overlays, breadcrumbs, block styles, child themes, or WordPress 7.0/7.1 theme features. Do not use for plugin back-end logic or store setup; use wordpress-plugin-development or wordpress-woocommerce-development.
---

# WordPress Theme Development Workflow

## Overview

Specialized workflow for creating custom WordPress themes from scratch, including modern block editor (Gutenberg) support, template hierarchy, responsive design, and WordPress 7.0 and 7.1 enhancements.

> **Current WordPress release:** 7.1.4 "Mary Lou" (August 19, 2026). Minimum PHP 7.4; PHP 8.2+ recommended for new projects.

## WordPress 7.0 + 7.1 Theme Features

1. **Admin Refresh** _(7.0)_
   - New default color scheme
   - View transitions between admin screens
   - Modern typography and spacing

2. **Pattern Editing** _(7.0)_
   - ContentOnly mode defaults for unsynced patterns
   - `disableContentOnlyForUnsyncedPatterns` setting
   - Per-block instance custom CSS

3. **Navigation Overlays** _(7.0)_
   - Customizable navigation overlays
   - Improved mobile navigation

4. **New Blocks** _(7.0)_
   - `core/icon` — Icon block with default library
   - `core/breadcrumbs` — Breadcrumbs block with filters
   - `core/responsive-grid` — Responsive grid block

5. **New Blocks** _(7.1)_
   - `core/tabs` — Native tabbed content; parent/child structure (`core/tab-list` → `core/tab-panels` → `core/tab-panel`)
   - `core/playlist` — Audio Playlist block for podcasting and media themes

6. **Theme.json Enhancements** _(7.0)_
   - Pseudo-element support (`:hover`, `:focus`, `:focus-visible`, `:active`) in block styles
   - Block-defined feature selectors honored
   - Enhanced custom CSS

7. **Per-Device Responsive Styling** _(7.1)_
   - Native `settings.viewport` in `theme.json` defines custom `mobile`/`tablet` breakpoints
   - `@mobile` / `@tablet` keys nest inside `styles.blocks` for per-breakpoint overrides
   - Editor device-preview width snaps to these breakpoints automatically
   - No `@desktop` key — desktop/base styles are the default fallback

8. **Client-Side Media Processing** _(7.1)_
   - HEIC, AVIF, WebP, Ultra HDR processed in-browser (WebAssembly / `wasm-vips`) before upload
   - HEIC originals preserved as companion files in attachment metadata (`$metadata['original']`)
   - Older browsers and Firefox fall back to server-side PHP automatically
   - Use `wp_get_attachment_image()` for markup — it handles `srcset`/`sizes` correctly for all formats
   - Audit `add_image_size()` calls: 7.1 deduplicates sizes that match core defaults

9. **Enforced Iframed Post Editor** _(7.1)_
   - The post editor iframe is now **unconditional** (Block API v3 enforcement)
   - Was opt-in in 7.0; now always active — theme editor styles must be enqueued via `editor_style` to load inside the iframe sandbox
   - `vw`/`vh` units inside block editor styles resolve against the iframe canvas width, not the browser window

10. **SVG Icon API** _(7.1)_
    - Themes can register custom icon collections via `wp_register_icon_collection()` / `wp_register_icon()`
    - Icons appear in the `core/icon` block picker; use patterns or `wp_register_icon()` (not custom JS) for theme-provided icons

## When to Use This Workflow

Use this workflow when:
- Creating custom WordPress themes
- Converting designs to WordPress themes
- Adding block editor support
- Implementing custom post types
- Building child themes
- Implementing WordPress 7.0 or 7.1 design features

## Workflow Phases

### Phase 1: Theme Setup

#### Actions
1. Create theme directory structure
2. Set up style.css with theme header
3. Create functions.php
4. Configure theme support
5. Set up enqueue scripts/styles

#### WordPress 7.1 Theme Header
```css
/*
Theme Name: My Custom Theme
Theme URI: https://example.com
Author: Developer Name
Author URI: https://example.com
Description: A WordPress 7.1 compatible theme with modern design
Version: 1.0.0
Requires at least: 6.0
Requires PHP: 7.4
License: GNU General Public License v2
License URI: https://www.gnu.org/licenses/gpl-2.0.html
Text Domain: my-custom-theme
Tags: block-patterns, block-styles, editor-style, wide-blocks, responsive-layout
*/
```

### Phase 2: Template Hierarchy

#### Actions
1. Create index.php (fallback template)
2. Implement header.php and footer.php
3. Create single.php for posts
4. Create page.php for pages
5. Add archive.php for archives
6. Implement search.php and 404.php

#### WordPress 7.1 Template Considerations
- **Iframed editor is now unconditional**: enqueue editor styles via `editor_style` in `block.json` or `add_theme_support('editor-styles')` — they will not load inside the iframe otherwise
- `vw`/`vh` CSS units inside block styles resolve against the iframe canvas, not the browser window; prefer `cqw`/`cqh` container-query units where possible
- Verify view transitions work
- Check admin color scheme compatibility

### Phase 3: Theme Functions

#### Actions
1. Register navigation menus
2. Add theme support (thumbnails, RSS, etc.)
3. Register widget areas
4. Create custom template tags
5. Implement helper functions

#### WordPress 7.1 theme.json Configuration
```json
{
  "$schema": "https://schemas.wp.org/wp/7.1/theme.json",
  "version": 3,
  "settings": {
    "appearanceTools": true,
    "layout": {
      "contentSize": "1200px",
      "wideSize": "1400px"
    },
    "background": {
      "backgroundImage": true
    },
    "typography": {
      "fontFamilies": true,
      "fontSizes": true
    },
    "spacing": {
      "margin": true,
      "padding": true
    },
    "viewport": {
      "mobile": "480px",
      "tablet": "782px"
    },
    "blocks": {
      "core/heading": {
        "typography": {
          "fontSizes": ["24px", "32px", "48px"]
        }
      }
    }
  },
  "styles": {
    "color": {
      "background": "#ffffff",
      "text": "#1a1a1a"
    },
    "elements": {
      "link": {
        "color": {
          "text": "#0066cc"
        }
      }
    },
    "blocks": {
      "core/group": {
        "spacing": {
          "padding": { "top": "3rem", "bottom": "3rem" }
        },
        "@mobile": {
          "spacing": {
            "padding": { "top": "1rem", "bottom": "1rem" }
          }
        }
      }
    }
  },
  "customTemplates": [
    {
      "name": "page-home",
      "title": "Homepage",
      "postTypes": ["page"]
    }
  ],
  "templateParts": [
    {
      "name": "header",
      "title": "Header",
      "area": "header"
    }
  ]
}
```

> **`settings.viewport` rules (7.1):**
> - `mobile` compiles to `@media (width <= VALUE)`; `tablet` to `@media (MOBILE < width <= TABLET)`
> - No `@desktop` key — base styles are the desktop fallback
> - Nest `@mobile` / `@tablet` inside `styles.blocks` for per-breakpoint overrides (see `core/group` example above)
> - `settings.viewport` is top-level only — not configurable per block
> - Invalid values (percentages, unitless numbers, CSS functions) fall back to core defaults (480px / 782px)

### Phase 4: Custom Post Types

#### Actions
1. Register custom post types
2. Create custom taxonomies
3. Add custom meta boxes
4. Implement custom fields
5. Create archive templates

#### REST-Ready CPT Registration
```php
register_post_type('portfolio', [
    'labels' => [
        'name' => __('Portfolio', 'my-theme'),
        'singular_name' => __('Portfolio Item', 'my-theme')
    ],
    'public' => true,
    'has_archive' => true,
    'show_in_rest' => true,  // Expose via REST API
    'supports' => ['title', 'editor', 'thumbnail', 'excerpt', 'custom-fields'],
    'menu_icon' => 'dashicons-portfolio',
]);

// Register meta for collaboration
register_post_meta('portfolio', 'client_name', [
    'type' => 'string',
    'single' => true,
    'show_in_rest' => true,
    'sanitize_callback' => 'sanitize_text_field',
]);
```

### Phase 5: Block Editor Support

#### Actions
1. Enable block editor support
2. Register custom blocks
3. Create block styles
4. Add block patterns
5. Configure block templates

#### WordPress 7.0 + 7.1 Block Features
- Block API v3 is reference model
- PHP-only block registration
- Per-instance custom CSS
- Block visibility controls (viewport-based, respects `settings.viewport` breakpoints)
- **7.1:** `core/tabs` and `core/playlist` are now available in patterns and templates

#### New Block Patterns — Tabs (7.1)
Use `core/tabs` in patterns for tabbed-content layouts without third-party plugins.
The block requires its full child hierarchy:

`patterns/product-tabs.php`:
```php
<?php
/**
 * Title: Product Tabs Section
 * Slug: my-theme/product-tabs
 * Categories: text, featured
 * Block Types: [core/tabs]
 */
?>
<!-- wp:tabs -->
<div class="wp-block-tabs">
  <!-- wp:tab-list -->
  <div role="tablist" class="wp-block-tab-list">
    <button type="button" role="tab">Description</button>
    <button type="button" role="tab">Details</button>
  </div>
  <!-- /wp:tab-list -->
  <!-- wp:tab-panels -->
  <div class="wp-block-tab-panels">
    <!-- wp:tab-panel {"label":"Description"} -->
    <section role="tabpanel" tabindex="0" class="wp-block-tab-panel">
      <!-- wp:paragraph -->
      <p>Add your description here.</p>
      <!-- /wp:paragraph -->
    </section>
    <!-- /wp:tab-panel -->
    <!-- wp:tab-panel {"label":"Details"} -->
    <section role="tabpanel" tabindex="0" class="wp-block-tab-panel">
      <!-- wp:paragraph -->
      <p>Add your details here.</p>
      <!-- /wp:paragraph -->
    </section>
    <!-- /wp:tab-panel -->
  </div>
  <!-- /wp:tab-panels -->
</div>
<!-- /wp:tabs -->
```

#### Block Pattern with ContentOnly (WP 7.0)
Patterns live as PHP files in the theme's `patterns/` directory (auto-registered) or
are registered via `register_block_pattern()`. The `content` is block markup — not a
JSON block tree. In 7.0, unsynced patterns default to ContentOnly editing.

`patterns/hero-section.php`:
```php
<?php
/**
 * Title: Hero Section
 * Slug: my-theme/hero-section
 * Categories: featured
 * Inserter: yes
 */
?>
<!-- wp:cover {"dimRatio":50,"overlayColor":"black"} -->
<div class="wp-block-cover">
    <!-- wp:heading {"level":1,"textAlign":"center"} -->
    <h1 class="wp-block-heading has-text-align-center"><?php echo esc_html__('Hero Title', 'my-theme'); ?></h1>
    <!-- /wp:heading -->
    <!-- wp:paragraph {"align":"center"} -->
    <p class="has-text-align-center"><?php echo esc_html__('Hero description goes here.', 'my-theme'); ?></p>
    <!-- /wp:paragraph -->
</div>
<!-- /wp:cover -->
```

Note: `{{placeholder}}` tokens are not a core pattern templating syntax. Use real
default content, or block bindings / the Pattern block for dynamic values.

#### Navigation Overlay Template Part (WP 7.0)
Navigation overlays are template parts in your theme's `parts/` directory, registered
under the `navigation-overlay` area in `theme.json`. Build them with blocks, not PHP.

`theme.json` (the `area` must be exactly `navigation-overlay`):
```json
{
  "version": 3,
  "templateParts": [
    {
      "area": "navigation-overlay",
      "name": "primary-overlay",
      "title": "Primary Mobile Overlay"
    }
  ]
}
```

`parts/primary-overlay.html` (include `core/navigation-overlay-close` so you control
its styling; otherwise WordPress injects a default close button):
```html
<!-- wp:group {"layout":{"type":"flex","orientation":"vertical","justifyContent":"center"}} -->
<div class="wp-block-group">
  <!-- wp:navigation {"overlayMenu":"never"} /-->
  <!-- wp:navigation-overlay-close /-->
</div>
<!-- /wp:group -->
```

Wire it up in your header template part. The `overlay` attribute takes the template
part slug only — no theme prefix (`"primary-overlay"`, not `"my-theme//primary-overlay"`):
```html
<!-- wp:navigation {"overlayMenu":"always","overlay":"primary-overlay"} /-->
```

To scope a pattern to overlay editing only, set `blockTypes` to
`core/template-part/navigation-overlay` in `register_block_pattern()`. Overlays are
full-screen in 7.0; a slide-in drawer is your own CSS on top.

### Phase 6: Styling and Design

#### Actions
1. Implement responsive design
2. Add CSS framework or custom styles
3. Create design system
4. Implement theme customizer
5. Add accessibility features

#### WordPress 7.0 Admin Refresh Considerations
The 7.0 admin refresh (new default color scheme, view transitions between admin
screens) is an admin-side change. Front-end themes do not need to opt in, and there
is no `--admin-color` CSS variable to set — users pick an admin color scheme in
their profile. If your plugin or theme enqueues admin CSS, test against the new
default scheme and avoid hard-coding colors that clash with it.

#### Styling 7.0 Features
Use theme.json for design tokens rather than inventing CSS custom properties.
Pseudo-elements (`:hover`, `:focus`, `:focus-visible`, `:active`) can be styled
declaratively in `theme.json` — no custom CSS required:
```json
{
  "styles": {
    "blocks": {
      "core/button": {
        ":hover": {
          "color": { "background": "#0055aa" }
        },
        ":focus-visible": {
          "outline": { "color": "#0066cc", "width": "2px" }
        }
      }
    }
  }
}
```
Navigation overlay colors are controlled by the blocks and global styles inside the
overlay template part, not by dedicated CSS variables.

### Phase 7: WordPress 7.0 Features Integration

#### Breadcrumbs Block Support
The `core/breadcrumbs` block (API v3, dynamic) reflects the site hierarchy
automatically. Two filters control its trail:

```php
// Modify, add, or remove items just before rendering. Each item is an array with
// 'label' (string) and optional 'url' (string) and 'allow_html' (bool).
add_filter('block_core_breadcrumbs_items', function ($items) {
    array_unshift($items, [
        'label' => __('Shop', 'my-theme'),
        'url'   => home_url('/shop/'),
    ]);
    return $items;
});

// Choose which taxonomy/term feeds the trail for posts, products, and other
// non-hierarchical post types (or hierarchical types using "Prefer taxonomy terms").
add_filter('block_core_breadcrumbs_post_type_settings', function ($settings, $post_type, $post_id) {
    if ($post_type === 'post') {
        $settings['taxonomy'] = 'category';
    }
    if ($post_type === 'portfolio') {
        $settings['taxonomy'] = 'portfolio_tag';
    }
    return $settings;
}, 10, 3);
```

When `allow_html` is true the label is sanitized with `wp_kses_post()`; otherwise it
is escaped with `esc_html()`. Prefer escaping unless you control the label markup.

#### Icon Block Support (updated in 7.1)
In 7.0, themes extended `core/icon` through block patterns only. In 7.1, a native
SVG Icon API allows themes (and plugins) to register custom icon collections that
appear directly in the block picker:

```php
add_action('init', function () {
    // Register a custom collection (7.1+)
    wp_register_icon_collection('my-theme-icons', [
        'label'       => __('Theme Icons', 'my-theme'),
        'description' => __('Custom brand icons', 'my-theme'),
    ]);

    // Register an individual icon. Use fill="currentColor" so the icon inherits
    // block/text color. SVG is sanitized through wp_kses (basic elements only).
    wp_register_icon('my-theme-icons/arrow-right', [
        'label'   => __('Arrow Right', 'my-theme'),
        'content' => '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M10 17l5-5-5-5v10z"/></svg>',
    ]);
});
```

For pre-7.1 environments, continue composing patterns that include `core/icon` blocks:

```php
add_action('init', function () {
    register_block_pattern_category('my-theme/icons', [
        'label'       => __('Theme Icons', 'my-theme'),
        'description' => __('Patterns that use the Icon block', 'my-theme'),
    ]);

    register_block_pattern('my-theme/contact-icons', [
        'title'      => __('Contact Icon Row', 'my-theme'),
        'categories' => ['my-theme/icons'],
        'content'    => '<!-- wp:group {"layout":{"type":"flex"}} --><div class="wp-block-group"><!-- wp:icon {"name":"wordpress"} /--></div><!-- /wp:group -->',
    ]);
});
```

### Phase 8: Testing

#### Actions
1. Test across browsers
2. Verify responsive breakpoints
3. Test block editor
4. Check accessibility
5. Performance testing

#### WordPress 7.1 Testing Checklist
- [ ] **Iframed editor (now unconditional):** editor styles load inside the iframe (via `editor_style` / `add_theme_support('editor-styles')`)
- [ ] `vw`/`vh` in block CSS reviewed — they resolve against the iframe canvas, not browser window
- [ ] Verify view transitions (admin-to-admin navigation)
- [ ] Check admin color scheme
- [ ] Test navigation overlays
- [ ] Verify contentOnly patterns
- [ ] Test breadcrumbs on CPT archives
- [ ] Test `core/tabs` and `core/playlist` blocks in patterns/templates (7.1)
- [ ] Per-device responsive styles: toggle Mobile/Tablet in editor and verify `@mobile`/`@tablet` overrides in `theme.json`
- [ ] Upload HEIC/AVIF images and verify `wp_get_attachment_image()` outputs correct `srcset`

## Theme Structure

```
theme-name/
├── style.css
├── functions.php
├── index.php
├── header.php
├── footer.php
├── sidebar.php
├── single.php
├── page.php
├── archive.php
├── search.php
├── 404.php
├── comments.php
├── template-parts/
│   ├── header/
│   ├── footer/
│   ├── navigation/
│   └── content/
├── patterns/           # Block patterns (WP 7.0)
├── templates/          # Site editor templates
├── inc/
│   ├── class-theme.php
│   └── supports.php
├── assets/
│   ├── css/
│   ├── js/
│   └── images/
└── languages/
```

## WordPress 7.0 + 7.1 Theme Checklist

- [ ] PHP 7.4+ requirement documented (PHP 8.2+ recommended for new projects)
- [ ] `theme.json` v3 schema used (`https://schemas.wp.org/wp/7.1/theme.json`)
- [ ] `settings.viewport` defined for custom breakpoints (7.1); `@mobile`/`@tablet` used in `styles.blocks` as needed
- [ ] Block patterns tested
- [ ] ContentOnly editing supported
- [ ] Navigation overlays implemented
- [ ] Breadcrumb filters added for CPT (`block_core_breadcrumbs_items`, `block_core_breadcrumbs_post_type_settings`)
- [ ] View transitions working
- [ ] Admin refresh compatible
- [ ] CPT meta `show_in_rest` set
- [ ] **Iframed editor (7.1 — now unconditional):** editor styles enqueued via `editor_style` in `block.json` or `add_theme_support('editor-styles')`; `vw`/`vh` units reviewed
- [ ] `core/tabs` and `core/playlist` blocks tested in patterns if used (7.1)
- [ ] `wp_register_icon_collection()` used for any theme-provided custom icons (7.1)
- [ ] `wp_get_attachment_image()` used for image output (HEIC/AVIF srcset handled automatically)
- [ ] Custom `add_image_size()` sizes audited — remove any that duplicate core defaults (7.1 deduplicates)

## Quality Gates

- [ ] All templates working
- [ ] Block editor supported
- [ ] Responsive design verified (including `@mobile`/`@tablet` overrides)
- [ ] Accessibility checked
- [ ] Performance optimized
- [ ] Cross-browser tested
- [ ] WordPress 7.1 compatibility verified

## MCP note

Theme work is mostly file-based, so MCP matters less here than in the plugin skill.
If a WordPress MCP connection is available, `core/get-environment-info` and
`core/get-site-info` (via the MCP Adapter) are still the fastest way to confirm the
target site's PHP version, active theme, and settings before editing — see the
`wordpress` skill for setup and security rules.

## Related skills

- `wordpress` - Full WordPress development workflow
- `wordpress-plugin-development` - Plugin development workflow
- `wordpress-woocommerce-development` - WooCommerce development workflow
