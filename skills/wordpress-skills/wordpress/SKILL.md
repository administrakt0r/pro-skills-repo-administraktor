---
name: wordpress
description: >-
  Use when building, extending, auditing, or modernizing WordPress sites end to end: themes, plugins, WooCommerce, performance, security hardening, or WordPress 7.0 features (AI Client, Abilities API, PHP-only blocks, DataViews). Use as the entry point that routes to the three focused WordPress skills. Do not use for non-WordPress PHP, or front-end work with no WordPress involvement.
---

# WordPress Development Workflow Bundle

## Overview

Comprehensive WordPress development workflow covering theme development, plugin creation, WooCommerce integration, performance optimization, and security. This bundle orchestrates skills for building production-ready WordPress sites and applications.

## WordPress 7.0 Features (Backward Compatible)

WordPress 7.0 "Armstrong" shipped May 20, 2026 (the originally planned April 9 date slipped during RC). Minimum PHP is now 7.4; PHP 8.3+ is recommended.

### Real-Time Collaboration (RTC) — did NOT ship in 7.0
- Planned as the 7.0 headline feature (Yjs CRDT, simultaneous editing); removed from the release on May 8, 2026 over race conditions, server load, memory efficiency, and fuzz-test bugs
- Do not write code against RTC APIs as if they exist in core. Expect a feature-plugin phase before any future core merge; no target version announced
- **Forward-compatible practice**: register post meta with `show_in_rest => true` and avoid legacy meta boxes so your data is RTC-ready whenever it lands
- Ignore any guidance referencing a `WP_COLLABORATION_MAX_USERS` constant or a `sync.providers` filter in core — those are not shipped core APIs

### AI Client / Connectors API
- Provider-agnostic AI interface in core (`wp_ai_client_prompt()`)
- Settings > Connectors for centralized API credential management
- Official providers: OpenAI, Anthropic Claude, Google Gemini (plus community providers)
- **Backward Compatibility**: Works with WordPress 6.9+ via plugin

### Abilities API (introduced in 6.9, stable in 7.0)
- Standardized capability declaration system
- REST API endpoints: `/wp-json/abilities/v1/manifest`
- Official MCP Adapter (`wordpress/mcp-adapter`) exposes Abilities as MCP tools for AI agents
- **Backward Compatibility**: Can be used as Composer package in 6.x

### DataViews & DataForm
- Replaces WP_List_Table on Posts, Pages, Media screens
- New layouts: table, grid, list, activity
- Client-side validation (pattern, minLength, maxLength, min, max)
- **Backward Compatibility**: Plugins using old hooks still work

### PHP-Only Block Registration
- Register blocks entirely via PHP without JavaScript
- Auto-generated Inspector controls
- **Backward Compatibility**: Existing JS blocks continue to work

### Interactivity API Updates
- `watch()` replaces `effect` from @preact/signals
- State navigation changes
- **Backward Compatibility**: Old syntax deprecated but functional

### Admin Refresh
- New default color scheme
- View transitions between admin screens
- **Backward Compatibility**: CSS-level changes, no breaking changes

### Pattern Editing
- ContentOnly mode defaults for unsynced patterns
- `disableContentOnlyForUnsyncedPatterns` setting
- **Backward Compatibility**: Existing patterns work

## When to Use This Workflow

Use this workflow when:
- Building new WordPress websites
- Creating custom themes
- Developing WordPress plugins
- Setting up WooCommerce stores
- Optimizing WordPress performance
- Hardening WordPress security
- Implementing WordPress 7.0 features (AI Client, Abilities API, DataViews)

## Workflow Phases

### Phase 1: WordPress Setup

#### Actions
1. Set up local development environment (LocalWP, Docker, or Valet)
2. Install WordPress (recommend 7.0+ for new projects)
3. Configure development database
4. Set up version control
5. Configure wp-config.php for development

#### WordPress 7.0 Configuration
```php
// wp-config.php - AI Client and collaboration settings
// Real-Time Collaboration did not ship in 7.0; there is no core collaboration
// constant to define. When the feature plugin lands, configure it there.
// AI Connector is enabled by installing a provider plugin
// (e.g., OpenAI, Anthropic Claude, or Google Gemini connector)
// No constant needed - configure via Settings > Connectors in admin
```

### Phase 2: Theme Development

#### Actions
1. Design theme architecture
2. Create theme files (style.css, functions.php, index.php)
3. Implement template hierarchy
4. Create custom page templates
5. Add custom post types and taxonomies
6. Implement theme customization options
7. Add responsive design
8. Test with WordPress 7.0 admin refresh

#### WordPress 7.0 Theme Considerations
- Block API v3 now reference model
- Pseudo-element support in theme.json
- Global Styles custom CSS honors block-defined selectors
- View transitions for admin navigation

#### Theme Structure
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
├── template-parts/
├── inc/
├── assets/
│   ├── css/
│   ├── js/
│   └── images/
└── languages/
```

### Phase 3: Plugin Development

#### Actions
1. Design plugin architecture
2. Create plugin boilerplate
3. Implement hooks (actions and filters)
4. Create admin interfaces
5. Add custom database tables
6. Implement REST API endpoints
7. Add settings and options pages

#### WordPress 7.0 Plugin Considerations
- **REST-Ready Meta**: Register post meta with `show_in_rest => true` (keeps data editable via REST and ready for future collaboration features)
- **AI Integration**: Use `wp_ai_client_prompt()` for AI features
- **DataViews**: Consider new admin UI patterns
- **Meta Boxes**: Migrate to block-based UIs for collaboration support

#### REST-Ready Post Meta Registration
```php
register_post_meta('post', 'custom_field', [
    'type' => 'string',
    'single' => true,
    'show_in_rest' => true,  // Expose via REST API
    'sanitize_callback' => 'sanitize_text_field',
]);
```

#### AI Connector Example
```php
// Using WordPress 7.0 AI Connector
// Note: Requires an AI provider plugin (OpenAI, Claude, or Gemini) to be installed and configured

// Basic text generation
$response = wp_ai_client_prompt('Summarize this content.')
    ->generate_text();

// With temperature for deterministic output
$response = wp_ai_client_prompt('Summarize this content.')
    ->using_temperature(0.2)
    ->generate_text();

// With model preference (tries first available in list)
$response = wp_ai_client_prompt('Summarize this content.')
    ->using_model_preference('gpt-4', 'claude-3-opus', 'gemini-2-pro')
    ->generate_text();

// For JSON structured output
$schema = [
    'type' => 'object',
    'properties' => [
        'summary' => ['type' => 'string'],
        'keywords' => ['type' => 'array', 'items' => ['type' => 'string']]
    ],
    'required' => ['summary']
];
$response = wp_ai_client_prompt('Analyze this content and return JSON.')
    ->using_system_instruction('You are a content analyzer.')
    ->as_json_response($schema)
    ->generate_text();
```

#### Plugin Structure
```
plugin-name/
├── plugin-name.php
├── includes/
│   ├── class-plugin-activator.php
│   ├── class-plugin-deactivator.php
│   ├── class-plugin-loader.php
│   └── class-plugin.php
├── admin/
│   ├── class-plugin-admin.php
│   ├── css/
│   └── js/
├── public/
│   ├── class-plugin-public.php
│   ├── css/
│   └── js/
└── languages/
```

### Phase 4: WooCommerce Integration

#### Actions
1. Install and configure WooCommerce
2. Create custom product types
3. Customize checkout flow
4. Integrate payment gateways
5. Set up shipping methods
6. Create custom order statuses
7. Implement subscription products
8. Add custom email templates

#### WordPress 7.0 + WooCommerce Considerations
- Test checkout with new admin interfaces
- AI connectors for product descriptions
- DataViews for order management screens
- Shared editing flows when collaboration features land

### Phase 5: Performance Optimization

#### Actions
1. Implement caching (object, page, browser)
2. Optimize images (lazy loading, WebP)
3. Minify and combine assets
4. Enable CDN
5. Optimize database queries
6. Implement lazy loading
7. Configure OPcache
8. Set up Redis/Memcached

#### WordPress 7.0 Performance
- Client-side media processing
- Font Library enabled for all themes
- Responsive grid block optimizations
- View transitions reduce perceived load time

#### Performance Checklist
- [ ] Page load time < 3 seconds
- [ ] Time to First Byte < 200ms
- [ ] Largest Contentful Paint < 2.5s
- [ ] Cumulative Layout Shift < 0.1
- [ ] First Input Delay < 100ms

### Phase 6: Security Hardening

#### Actions
1. Update WordPress core, themes, plugins
2. Implement security headers
3. Configure file permissions
4. Set up firewall rules
5. Enable two-factor authentication
6. Implement rate limiting
7. Configure security logging
8. Set up malware scanning

#### WordPress 7.0 Security Considerations
- PHP 7.4 minimum (drops 7.2/7.3 support)
- Test Abilities API permission boundaries
- Verify collaboration data isolation
- AI connector credential security

#### Security Checklist
- [ ] WordPress core updated (7.0+ recommended)
- [ ] All plugins/themes updated
- [ ] Strong passwords enforced
- [ ] Two-factor authentication enabled
- [ ] Security headers configured
- [ ] XML-RPC disabled or protected
- [ ] File editing disabled
- [ ] Database prefix changed
- [ ] Regular backups configured

### Phase 7: Testing

#### Actions
1. Write unit tests for custom code
2. Create integration tests
3. Set up E2E tests
4. Test cross-browser compatibility
5. Test responsive design
6. Performance testing
7. Security testing

#### WordPress 7.0 Testing Priorities
- Test with iframed post editor
- Verify DataViews integration
- Test collaboration workflows when the feature plugin is active
- Validate AI connector functionality
- Test Interactivity API with watch()

### Phase 8: Deployment

#### Actions
1. Set up staging environment
2. Configure deployment pipeline
3. Set up database migrations
4. Configure environment variables
5. Enable maintenance mode during deployment
6. Deploy to production
7. Verify deployment
8. Monitor post-deployment

## WordPress-Specific Workflows

### Custom Post Type Development (REST-Ready)
```php
register_post_type('book', [
    'labels' => [...],
    'public' => true,
    'has_archive' => true,
    'supports' => ['title', 'editor', 'thumbnail', 'excerpt'],
    'menu_icon' => 'dashicons-book',
    'show_in_rest' => true,  // Expose via REST API
]);

// Register meta with REST API for collaboration
register_post_meta('book', 'isbn', [
    'type' => 'string',
    'single' => true,
    'show_in_rest' => true,
    'sanitize_callback' => 'sanitize_text_field',
]);
```

### Custom REST API Endpoint
```php
add_action('rest_api_init', function() {
    register_rest_route('myplugin/v1', '/books', [
        'methods' => 'GET',
        'callback' => 'get_books',
        'permission_callback' => '__return_true',
    ]);
});
```

### WordPress 7.0 AI Connector Usage
```php
// Auto-generate post excerpt with AI
add_action('save_post', function($post_id, $post) {
    if (wp_is_post_autosave($post_id) || wp_is_post_revision($post_id)) {
        return;
    }
    
    // Skip if excerpt already exists
    if (!empty($post->post_excerpt)) {
        return;
    }
    
    $content = strip_tags($post->post_content);
    if (empty($content)) {
        return;
    }
    
    // Check if AI client is available
    if (!function_exists('wp_ai_client_prompt')) {
        return;
    }
    
    // Build prompt with input
    // The AI client returns a fluent builder; chain configuration and generation.
    // Errors surface from generate_text() as WP_Error.
    $summary = wp_ai_client_prompt(
        'Create a brief 2-sentence summary of this content: ' . substr($content, 0, 1000)
    )
        ->using_temperature(0.3) // Use temperature for consistent output
        ->generate_text();
    
    if ($summary && !is_wp_error($summary)) {
        wp_update_post([
            'ID' => $post_id,
            'post_excerpt' => sanitize_textarea_field($summary)
        ]);
    }
}, 10, 2);
```

### PHP-Only Block Registration (WordPress 7.0)
```php
// Register block entirely in PHP
register_block_type('my-plugin/hello-world', [
    'render_callback' => function($attributes, $content) {
        return '<p class="hello-world">Hello, World!</p>';
    },
    'attributes' => [
        'message' => ['type' => 'string', 'default' => 'Hello!']
    ],
]);
```

### Abilities API Registration
```php
// Register ability category on correct hook
add_action('wp_abilities_api_categories_init', function() {
    wp_register_ability_category('content-creation', [
        'label' => __('Content Creation', 'my-plugin'),
        'description' => __('Abilities for generating and managing content', 'my-plugin'),
    ]);
});

// Register abilities on correct hook
add_action('wp_abilities_api_init', function() {
    wp_register_ability('my-plugin/generate-summary', [
        'label' => __('Generate Post Summary', 'my-plugin'),
        'description' => __('Creates an AI-powered summary of a post', 'my-plugin'),
        'category' => 'content-creation',
        'input_schema' => [
            'type' => 'object',
            'properties' => [
                'post_id' => ['type' => 'integer', 'description' => 'The post ID to summarize']
            ],
            'required' => ['post_id']
        ],
        'output_schema' => [
            'type' => 'object',
            'properties' => [
                'summary' => ['type' => 'string', 'description' => 'The generated summary']
            ]
        ],
        'execute_callback' => 'my_plugin_generate_summary_handler',
        'permission_callback' => function() {
            return current_user_can('edit_posts');
        }
    ]);
});

// Handler function for the ability
function my_plugin_generate_summary_handler($input) {
    $post_id = isset($input['post_id']) ? absint($input['post_id']) : 0;
    $post = get_post($post_id);
    
    if (!$post) {
        return new WP_Error('invalid_post', 'Post not found');
    }
    
    $content = strip_tags($post->post_content);
    if (empty($content)) {
        return ['summary' => ''];
    }
    
    if (!function_exists('wp_ai_client_prompt')) {
        return new WP_Error('ai_unavailable', 'AI client not available');
    }
    
    $result = wp_ai_client_prompt('Summarize in 2 sentences: ' . substr($content, 0, 1000))
        ->using_temperature(0.3)
        ->generate_text();
    
    if (is_wp_error($result)) {
        return $result;
    }
    
    return ['summary' => sanitize_textarea_field($result)];
}
```

### WooCommerce Custom Product Type
```php
add_action('init', function() {
    class WC_Product_Custom extends WC_Product {
        // Custom product implementation
    }
});
```

## WordPress MCP Integration

WordPress has first-class MCP support through the official MCP Adapter. When a
WordPress site is connected to the agent via MCP, prefer its tools over guessing at
WP-CLI incantations or REST calls: read site state through MCP first, then edit code.

### Components (all official unless noted)

| Piece | What it is | Status |
| --- | --- | --- |
| Abilities API | Register typed, permission-checked capabilities via `wp_register_ability()` | Introduced 6.9, stable in 7.0 |
| MCP Adapter (`wordpress/mcp-adapter`) | Turns registered Abilities into MCP tools, resources, prompts | Official, "AI Building Blocks for WordPress" |
| `@automattic/mcp-wordpress-remote` | HTTP remote proxy for publicly reachable sites | Official (note: the older `Automattic/wordpress-mcp` plugin is deprecated — do not use it) |
| WordPress.org MCP server | Helps prepare, validate, and submit plugins to the plugin directory | Official (developer.wordpress.org/plugins/wordpress-org/using-the-mcp-server/) |
| `@wp-playground/mcp` | MCP server for WordPress Playground environments | Official |

### Connecting an agent to a site

Local site (STDIO via WP-CLI — needs WP-CLI installed):
```json
{
  "mcpServers": {
    "wordpress": {
      "command": "wp",
      "args": [
        "--path=/path/to/wordpress",
        "mcp-adapter", "serve",
        "--server=mcp-adapter-default-server",
        "--user=admin"
      ]
    }
  }
}
```

Remote site (HTTP via the official proxy + application password):
```json
{
  "mcpServers": {
    "wordpress": {
      "command": "npx",
      "args": ["-y", "@automattic/mcp-wordpress-remote@latest"],
      "env": {
        "WP_API_URL": "https://yoursite.example/wp-json/mcp/mcp-adapter-default-server",
        "WP_API_USERNAME": "admin",
        "WP_API_PASSWORD": "xxxx xxxx xxxx xxxx xxxx xxxx"
      }
    }
  }
}
```

The default server exposes three tools: `mcp-adapter-discover-abilities`,
`mcp-adapter-get-ability-info`, `mcp-adapter-execute-ability`. WordPress 6.9+ ships
`core/get-site-info`, `core/get-user-info`, and `core/get-environment-info` — ask the
agent to run these before assuming environment details.

### Security rules when using WordPress MCP

- An MCP client acts as a logged-in WordPress user. Use a dedicated, least-privilege
  user for agent access — never an administrator by default.
- Only abilities registered with `'meta' => ['mcp' => ['public' => true]]` are exposed
  on the default server. Mark read-only abilities public; keep destructive ones off
  the default server or behind explicit capability checks.
- Never use `__return_true` as a `permission_callback` for state-changing abilities.
- Prefer read-only abilities on any internet-exposed HTTP transport; use application
  passwords or OAuth, and log/monitor all MCP-driven changes.
- Model output is untrusted input: validate and sanitize anything an AI tool passes to
  `execute_callback`, exactly as you would for REST requests.

## Quality Gates

Before moving to next phase, verify:
- [ ] All custom code tested
- [ ] Security scan passed
- [ ] Performance targets met
- [ ] Cross-browser tested
- [ ] Mobile responsive verified
- [ ] Accessibility checked (WCAG 2.1)
- [ ] WordPress 7.0 compatibility verified (for new projects)

## Related skills

- `wordpress-theme-development` - Theme development workflow
- `wordpress-plugin-development` - Plugin development workflow
- `wordpress-woocommerce-development` - WooCommerce development workflow
