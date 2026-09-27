---
name: wordpress-plugin-development
description: >-
  Use when creating WordPress plugins: hooks, admin interfaces, custom tables, REST endpoints, Abilities API, AI Client integration, PHP-only blocks, security hardening, or plugin test setup. Do not use for theme templates or storefront setup; use wordpress-theme-development or wordpress-woocommerce-development.
---

# WordPress Plugin Development Workflow

## Overview

Specialized workflow for creating WordPress plugins with proper architecture, hooks system, admin interfaces, REST API endpoints, and security practices. Now includes WordPress 7.0 features for modern plugin development.

## WordPress 7.0 Plugin Development

### Key Features for Plugin Developers

1. **Real-Time Collaboration (RTC) — did not ship in 7.0**
   - Planned as Yjs-based CRDT simultaneous editing; removed from the 7.0 release on May 8, 2026 (race conditions, server load, fuzz-test bugs)
   - Do not build against RTC APIs in core. Expect a feature-plugin phase first
   - **Forward-compatible practice**: register post meta with `show_in_rest => true` so your data is RTC-ready when the feature lands

2. **AI Client / Connector Integration**
   - Provider-agnostic AI via `wp_ai_client_prompt()`
   - Settings > Connectors admin screen
   - Works with OpenAI, Claude, Gemini, Ollama (via provider plugins)

3. **Abilities API**
   - Declare plugin capabilities for AI agents
   - REST API: `/wp-json/abilities/v1/manifest`
   - Official MCP Adapter (`wordpress/mcp-adapter`) exposes Abilities as MCP tools

4. **DataViews & DataForm**
   - Modern admin interfaces
   - Replaces WP_List_Table patterns
   - Built-in validation

5. **PHP-Only Blocks**
   - Register blocks without JavaScript
   - Auto-generated Inspector controls

## When to Use This Workflow

Use this workflow when:
- Creating custom WordPress plugins
- Extending WordPress functionality
- Building admin interfaces
- Adding REST API endpoints
- Integrating third-party services
- Implementing WordPress 7.0 AI/Collaboration features

## Workflow Phases

### Phase 1: Plugin Setup

#### Actions
1. Create plugin directory structure
2. Set up main plugin file with header
3. Implement activation/deactivation hooks
4. Set up autoloading
5. Configure text domain

#### WordPress 7.0 Plugin Header
```php
/*
Plugin Name: My Plugin
Plugin URI: https://example.com/my-plugin
Description: A WordPress 7.0 compatible plugin with AI and MCP support
Version: 1.0.0
Requires at least: 6.0
Requires PHP: 7.4
Author: Developer Name
License: GPL2+
*/
```

### Phase 2: Plugin Architecture

#### Actions
1. Design plugin class structure
2. Implement singleton pattern
3. Create loader class
4. Set up dependency injection
5. Configure plugin lifecycle

#### WordPress 7.0 Architecture Considerations
- Prepare for iframed editor compatibility
- Design for collaboration-aware data flows
- Consider Abilities API for AI integration

### Phase 3: Hooks Implementation

#### Actions
1. Register action hooks
2. Create filter hooks
3. Implement callback functions
4. Set up hook priorities
5. Add conditional hooks

### Phase 4: Admin Interface

#### Actions
1. Create admin menu
2. Build settings pages
3. Implement options registration
4. Add settings sections/fields
5. Create admin notices

#### WordPress 7.0 Admin Considerations
- Test with new admin color scheme
- Consider DataViews for data displays
- Implement view transitions
- Use new validation patterns

#### DataViews Example
```javascript
import { DataViews } from '@wordpress/dataviews';

const MyPluginDataView = () => {
    const data = [/* records */];
    const fields = [
        { id: 'title', label: 'Title', sortable: true },
        { id: 'status', label: 'Status', filterBy: true }
    ];
    const view = {
        type: 'table',
        perPage: 10,
        sort: { field: 'title', direction: 'asc' }
    };

    return (
        <DataViews
            data={data}
            fields={fields}
            view={view}
            onChangeView={handleViewChange}
        />
    );
};
```

### Phase 5: Database Operations

#### Actions
1. Create custom tables
2. Implement CRUD operations
3. Add data validation
4. Set up data sanitization
5. Create data upgrade routines

#### REST-Ready Post Meta
```php
// Register meta exposed via the REST API
register_post_meta('post', 'my_custom_field', [
    'type' => 'string',
    'single' => true,
    'show_in_rest' => true,  // Expose via REST; keeps data RTC-ready
    'sanitize_callback' => 'sanitize_text_field',
]);

// For WP 7.0, also consider:
register_term_meta('category', 'my_term_field', [
    'type' => 'string',
    'show_in_rest' => true,
]);
```

### Phase 6: REST API

#### Actions
1. Register REST routes
2. Create endpoint callbacks
3. Implement permission callbacks
4. Add request validation
5. Document API endpoints

#### WordPress 7.0 REST API Enhancements
- Abilities API integration
- AI Connector endpoints
- Enhanced validation

### Phase 7: Security

#### Actions
1. Implement nonce verification
2. Add capability checks
3. Sanitize all inputs
4. Escape all outputs
5. Secure database queries

#### WordPress 7.0 Security Considerations
- Test Abilities API permission boundaries
- Validate AI connector credential handling
- Review collaboration data isolation
- PHP 7.4+ requirement compliance

### Phase 8: WordPress 7.0 Features

#### AI Connector Implementation
```php
// Using WordPress 7.0 AI Connector
add_action('save_post', 'my_plugin_generate_ai_summary', 10, 2);

function my_plugin_generate_ai_summary($post_id, $post) {
    if (wp_is_post_autosave($post_id) || wp_is_post_revision($post_id)) {
        return;
    }
    
    // Check if AI client is available
    if (!function_exists('wp_ai_client_prompt')) {
        return;
    }
    
    $content = strip_tags($post->post_content);
    if (empty($content)) {
        return;
    }
    
    // Build prompt - direct string concatenation for input
    // The AI client returns a fluent builder; chain configuration and generation.
    // Errors surface from generate_text() as WP_Error.
    $summary = wp_ai_client_prompt(
        'Create a compelling 2-sentence summary for social media: ' . substr($content, 0, 1000)
    )
        ->using_temperature(0.3) // Set temperature for consistent output
        ->generate_text();
    
    if ($summary && !is_wp_error($summary)) {
        update_post_meta($post_id, '_ai_summary', sanitize_textarea_field($summary));
    }
}
```

#### Abilities API Registration
```php
// Register ability categories on their own hook
add_action('wp_abilities_api_categories_init', function() {
    wp_register_ability_category('content-creation', [
        'label' => __('Content Creation', 'my-plugin'),
        'description' => __('Abilities for generating and managing content', 'my-plugin'),
    ]);
});

// Register abilities on their own hook
add_action('wp_abilities_api_init', function() {
    wp_register_ability('my-plugin/generate-summary', [
        'label' => __('Generate Summary', 'my-plugin'),
        'description' => __('Creates an AI-powered summary of content', 'my-plugin'),
        'category' => 'content-creation',
        'input_schema' => [
            'type' => 'object',
            'properties' => [
                'content' => ['type' => 'string'],
                'length' => ['type' => 'integer', 'default' => 2]
            ],
            'required' => ['content']
        ],
        'output_schema' => [
            'type' => 'object',
            'properties' => [
                'summary' => ['type' => 'string']
            ]
        ],
        'execute_callback' => 'my_plugin_generate_summary_cb',
        'permission_callback' => function() {
            return current_user_can('edit_posts');
        }
    ]);
});

// Handler callback
function my_plugin_generate_summary_cb($input) {
    $content = isset($input['content']) ? $input['content'] : '';
    $length = isset($input['length']) ? absint($input['length']) : 2;
    
    if (empty($content)) {
        return new WP_Error('empty_content', 'No content provided');
    }
    
    if (!function_exists('wp_ai_client_prompt')) {
        return new WP_Error('ai_unavailable', 'AI not available');
    }
    
    $prompt = sprintf('Create a %d-sentence summary of: %s', $length, substr($content, 0, 2000));
    
    $result = wp_ai_client_prompt($prompt)
        ->using_temperature(0.3)
        ->generate_text();
    
    if (is_wp_error($result)) {
        return $result;
    }
    
    return ['summary' => sanitize_textarea_field($result)];
}
```

#### PHP-Only Block Registration
```php
// Register block entirely in PHP (WordPress 7.0)
// Note: For full PHP-only blocks, use block.json with PHP render_callback

// First, create a block.json file in build/ or includes/blocks/
// Then register in PHP:

// Simple PHP-only block registration (WordPress 7.0+)
if (function_exists('register_block_type')) {
    register_block_type('my-plugin/featured-post', [
        'render_callback' => function($attributes, $content, $block) {
            $post_id = isset($attributes['postId']) ? absint($attributes['postId']) : 0;
            
            if (!$post_id) {
                $post_id = get_the_ID();
            }
            
            $post = get_post($post_id);
            
            if (!$post) {
                return '';
            }
            
            $title = esc_html($post->post_title);
            $excerpt = esc_html(get_the_excerpt($post));
            
            return sprintf(
                '<div class="featured-post"><h2>%s</h2><p>%s</p></div>',
                $title,
                $excerpt
            );
        },
        'attributes' => [
            'postId' => ['type' => 'integer', 'default' => 0],
            'showExcerpt' => ['type' => 'boolean', 'default' => true]
        ],
    ]);
}
```

#### Collaboration (when the feature plugin is active)
```javascript
// Only if you have the collaboration feature plugin active and must opt a
// post type out. There is no core sync.providers filter in WordPress 7.0.
import { addFilter } from '@wordpress/hooks';

addFilter(
    'sync.providers',
    'my-plugin/disable-collab',
    () => []
);
```

### Phase 9: Testing

#### Actions
1. Set up PHPUnit
2. Create unit tests
3. Write integration tests
4. Test with WordPress test suite
5. Configure CI

#### WordPress 7.0 Testing Priorities
- Test with the collaboration feature plugin active if you support it
- Verify AI connector functionality
- Validate DataViews integration
- Test Interactivity API with watch()

## Exposing Plugin Functionality via MCP

If your plugin registers Abilities, the official MCP Adapter can expose them to AI
agents (Claude Code, Cursor, VS Code, Claude Desktop) as MCP tools. This is the
supported path — do not build a bespoke MCP server.

- Mark an ability public for the default MCP server at registration time:
```php
wp_register_ability('my-plugin/generate-summary', [
    // ...label, schemas, callbacks...
    'meta' => [
        'mcp' => [
            'public' => true, // Required for default-server MCP access
        ],
    ],
]);
```

- Core abilities can be opted in via the `wp_register_ability_args` filter.
- For full control, require `wordpress/mcp-adapter` via Composer, initialize
  `WP\MCP\Core\McpAdapter::instance()`, and create a custom server on the
  `mcp_adapter_init` action with `create_server()` (explicitly listing the abilities
  to expose). Use `Jetpack Autoloader` if multiple plugins may bundle the adapter.
- Client-side wiring (STDIO via `wp mcp-adapter serve`, or HTTP via
  `@automattic/mcp-wordpress-remote`) is documented in the `wordpress` skill.
- Treat MCP tool calls as authenticated user requests: enforce a real
  `permission_callback`, validate/sanitize all input, and log executions. Start with
  read-only abilities before enabling anything that mutates state.

## Plugin Structure

```
plugin-name/
├── plugin-name.php
├── includes/
│   ├── class-plugin.php
│   ├── class-loader.php
│   ├── class-activator.php
│   └── class-deactivator.php
├── admin/
│   ├── class-plugin-admin.php
│   ├── css/
│   └── js/
├── public/
│   ├── class-plugin-public.php
│   ├── css/
│   └── js/
├── blocks/           # PHP-only blocks (WP 7.0)
├── abilities/        # Abilities API
├── ai/               # AI Connector integration
├── languages/
└── vendor/
```

## WordPress 7.0 Compatibility Checklist

- [ ] PHP 7.4+ requirement documented
- [ ] Post meta registered with `show_in_rest => true`
- [ ] Meta boxes migrated to block-based UIs
- [ ] AI Connector integration tested
- [ ] Abilities API registered (if applicable)
- [ ] DataViews integration tested (if applicable)
- [ ] Interactivity API uses `watch()` not `effect`
- [ ] Tested with iframed editor
- [ ] Legacy meta boxes avoided where block-based UIs are feasible

## Quality Gates

- [ ] Plugin activates without errors
- [ ] All hooks working
- [ ] Admin interface functional
- [ ] Security measures implemented
- [ ] Tests passing
- [ ] Documentation complete
- [ ] WordPress 7.0 compatibility verified

## Related skills

- `wordpress` - Full WordPress development workflow
- `wordpress-theme-development` - Theme development workflow
- `wordpress-woocommerce-development` - WooCommerce development workflow
