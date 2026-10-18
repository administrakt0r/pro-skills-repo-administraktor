# WordPress Guidelines

> Verified: 2026-10-18, WordPress Developer Handbook, applies to WordPress 6.5+ / 6.7 / 7.0
> Note: Extends PHP guidelines. Also read AGENTS-GUIDELINES-PHP.md.

## Data Sanitization & Escaping
- **Sanitize Input**: Sanitize all incoming input early using WordPress functions (`sanitize_text_field()`, `sanitize_key()`, `absint()`).
- **Late Escaping**: Escape all output at the point of rendering (`esc_html()`, `esc_attr()`, `esc_url()`, `wp_kses_post()`). Never echo raw variables.
- **SQL Queries**: Use `$wpdb->prepare()` for all custom queries with placeholders (`%s`, `%d`, `%f`). Never interpolate variables into SQL strings.

## Nonces, Capabilities & REST
- **Nonces & Permissions**: Check nonces with `check_admin_referer()` or `wp_verify_nonce()` AND check user capabilities with `current_user_can()`. Nonces verify intent; capabilities verify authorization. Both are required.
- **REST API Endpoints**: Always provide a `permission_callback` in `register_rest_route()`. Never use `__return_true` for routes that modify state, expose private data, or run admin actions.

## Architecture & Lifecycles
- **Prefixing**: Prefix all functions, classes, constants, and global variables with the project's unique vendor prefix to avoid namespace collisions.
- **Enqueuing**: Enqueue scripts and styles only via `wp_enqueue_scripts`, `admin_enqueue_scripts`, or `enqueue_block_assets`. Never echo `<script>` or `<link>` tags directly into template heads.
- **Theme Development**: For block themes, configure styles and layout in `theme.json` (v3). Never edit WordPress core files.
- **Plugin Lifecycle**: Clean up options and custom tables in `uninstall.php`, not in deactivation hooks.

## Verification
- Code style: `./vendor/bin/phpcs --standard=WordPress`
