---
name: wordpress-woocommerce-development
description: >-
  Use when building or customizing WooCommerce stores: product configuration, payment gateways, shipping, checkout flow, custom product types, order automation via the Abilities API, or store performance. Do not use for general theme or plugin work; use wordpress-theme-development or wordpress-plugin-development.
---

# WordPress WooCommerce Development Workflow

## Overview

Specialized workflow for building WooCommerce stores including setup, payment gateway integration, shipping configuration, custom product types, store optimization, and WordPress 7.0 enhancements.

## WordPress 7.0 + WooCommerce Features

1. **AI Integration**
   - Auto-generate product descriptions
   - AI-powered customer service responses
   - Product summary generation
   - Marketing copy assistance

2. **DataViews for Orders**
   - Modern order management interfaces
   - Enhanced filtering and sorting
   - Activity layout for order history

3. **Real-Time Collaboration**
   - Did NOT ship in WordPress 7.0 (removed May 8, 2026); collaborative order
     editing is not available in core
   - When the feature plugin lands, team notes and live inventory updates become
     feasible — keep order data REST-exposed until then

4. **Admin Refresh**
   - Consistent WooCommerce admin styling
   - View transitions between screens

5. **Abilities API**
   - AI-powered order processing
   - Automated inventory management
   - Smart shipping recommendations

## When to Use This Workflow

Use this workflow when:
- Setting up WooCommerce stores
- Integrating payment gateways
- Configuring shipping methods
- Creating custom product types
- Building subscription products
- Implementing AI-powered features (WP 7.0)

## Workflow Phases

### Phase 1: Store Setup

#### Actions
1. Install WooCommerce
2. Run setup wizard
3. Configure store settings
4. Set up tax rules
5. Configure currency
6. Test with WordPress 7.0 admin

#### WordPress 7.0 + WooCommerce Setup
```php
// Minimum requirements for WP 7.0 + WooCommerce: PHP 7.4 (8.3+ recommended).
// Real-Time Collaboration did not ship in 7.0 - there is no core collaboration
// constant to define in wp-config.php.

// AI features are enabled by installing a provider plugin
// Install OpenAI, Anthropic, or Gemini connector from WordPress.org
// Then configure via Settings > Connectors in admin panel
```

### Phase 2: Product Configuration

#### Actions
1. Create product categories
2. Add product attributes
3. Configure product types
4. Set up variable products
5. Add product images

#### AI-Powered Product Descriptions (WP 7.0)
```php
// Auto-generate product descriptions with AI.
// Note: the callback name in add_action must match the function name exactly.
add_action('woocommerce_new_product', 'generate_ai_product_description', 10, 2);

function generate_ai_product_description($product_id, $product) {
    if ($product->get_description()) {
        return; // Skip if description exists
    }
    
    // Check if AI client is available
    if (!function_exists('wp_ai_client_prompt')) {
        return;
    }
    
    $title = $product->get_name();
    $short_description = $product->get_short_description();
    
    $prompt = sprintf(
        'Write a compelling WooCommerce product description for "%s" that highlights key features and benefits. Make it SEO-friendly and persuasive.',
        $title
    );
    
    if ($short_description) {
        $prompt .= "\n\nShort description: " . $short_description;
    }
    
    // The AI client returns a fluent builder; chain configuration and generation.
    // Errors surface from generate_text() as WP_Error.
    $description = wp_ai_client_prompt($prompt)
        ->using_temperature(0.3)
        ->generate_text();
    
    if ($description && !is_wp_error($description)) {
        $product->set_description(sanitize_textarea_field($description));
        $product->save();
    }
}
```

**Privacy note:** product data you send to `wp_ai_client_prompt()` leaves your server
for a third-party AI provider. Never include customer PII (names, emails, addresses,
order history) in prompts without a documented legal basis and disclosure. Review the
provider's data-retention terms under Settings > Connectors before enabling this in
production.

### Phase 3: Payment Integration

#### Actions
1. Choose payment gateways
2. Configure Stripe
3. Set up PayPal
4. Add offline payments
5. Test payment flows

#### WordPress 7.0 AI for Payments
**Do not ship AI-based fraud checks that send customer PII to a third-party model by
default.** Shipping addresses and billing emails are personal data; forwarding them to
an AI provider is a disclosure that needs a documented legal basis, a DPA with the
provider, and usually customer consent. Real fraud detection uses deterministic signals
first — order velocity, AVS/CVV results, address mismatch, proxy/ASN reputation,
billing-vs-shipping distance — and only consults an AI on redacted, non-PII features if
at all.

Deterministic risk scoring (preferred):
```php
// Rule-based risk signals; no data leaves the server.
add_filter('woocommerce_checkout_order_processed', 'my_store_risk_score', 10, 3);

function my_store_risk_score($order_id, $data, $order) {
    $score = 0;

    if (strtolower($order->get_billing_country()) !== strtolower($order->get_shipping_country())) {
        $score += 2; // Cross-border shipping
    }
    if ($order->get_payment_method() === 'cod' && $order->get_total() > 200) {
        $score += 2; // High-value cash on delivery
    }
    if (my_store_order_velocity($order->get_billing_email()) > 3) {
        $score += 3; // Repeat attempts in a short window
    }

    $order->update_meta_data('_risk_score', $score);
    $order->save();

    if ($score >= 5) {
        $order->update_status('on-hold', __('Held for manual fraud review.', 'my-store'));
    }
}
```

If you deliberately opt into an AI check, keep it advisory only (never auto-cancel on
model output), redact all PII from the prompt, and record the legal basis:
```php
// Advisory only. Redact PII; never gate checkout on model output alone.
function my_store_ai_advisory_risk(array $signals) {
    if (!function_exists('wp_ai_client_prompt')) {
        return null;
    }

    $prompt = sprintf(
        'Classify order risk from these non-PII signals only (return "low", "medium", or "high"): '
        . 'total=%s, currency=%s, items=%d, cross_border=%s, payment_method=%s.',
        $signals['total'],
        $signals['currency'],
        $signals['items'],
        $signals['cross_border'] ? 'yes' : 'no',
        $signals['payment_method']
    );

    $analysis = wp_ai_client_prompt($prompt)
        ->using_temperature(0.1)
        ->generate_text();

    return is_wp_error($analysis) ? null : $analysis;
}
```

### Phase 4: Shipping Configuration

#### Actions
1. Set up shipping zones
2. Configure shipping methods
3. Add flat rate shipping
4. Set up free shipping
5. Integrate carriers

#### Shipping Recommendations (WP 7.0)
Choosing between fixed shipping options is arithmetic, not inference — do it
deterministically. Do not call an AI model during checkout for this: it adds latency,
cost, and nondeterminism to the payment path for no benefit.

```php
// Deterministic upsell notice: no model call, no external dependency.
add_action('woocommerce_after_checkout_form', 'my_store_shipping_recommendation');

function my_store_shipping_recommendation($checkout) {
    $cart = WC()->cart;
    if (!$cart || $cart->is_empty()) {
        return;
    }

    $total   = (float) $cart->get_subtotal();
    $country = WC()->customer ? WC()->customer->get_shipping_country() : '';

    if ($total < 100) {
        wc_add_notice(
            esc_html__('Spend more than $100 for free shipping.', 'my-store'),
            'info'
        );
    } elseif ($country !== 'US' && $country !== '') {
        wc_add_notice(
            esc_html__('Express shipping is available for faster international delivery.', 'my-store'),
            'info'
        );
    }
}
```

If the choice is genuinely open-ended (e.g. carrier selection by natural-language
constraints), gate the model call behind a transient cache and keep it advisory:

```php
$cached = get_transient('my_store_carrier_advice_' . md5($cart_key));
if (false === $cached && function_exists('wp_ai_client_prompt')) {
    $cached = wp_ai_client_prompt($redacted_prompt)
        ->using_temperature(0.1)
        ->generate_text();
    if (!is_wp_error($cached)) {
        set_transient('my_store_carrier_advice_' . md5($cart_key), $cached, HOUR_IN_SECONDS);
    }
}
// $cached is advice shown to the customer, never an automatic charge or rate change.
```

### Phase 5: Store Customization

#### Actions
1. Customize product pages
2. Modify cart page
3. Style checkout flow
4. Create custom templates
5. Add custom fields

#### WordPress 7.0 Template Customization
```php
// Custom product template with WP 7.0 blocks
add_action('woocommerce_after_main_content', 'add_product_ai_chat');

function add_product_ai_chat() {
    if (!is_product()) return;
    
    global $product;
    ?>
    <div class="product-ai-assistant">
        <h3>AI Shopping Assistant</h3>
        <button id="ai-chat-toggle" type="button">Ask about this product</button>
        <div id="ai-chat-panel" style="display:none;">
            <div id="ai-chat-messages"></div>
            <input type="text" id="ai-chat-input" placeholder="Ask about sizing, materials, etc.">
        </div>
    </div>
    <script>
    document.getElementById('ai-chat-toggle').addEventListener('click', function() {
        const panel = document.getElementById('ai-chat-panel');
        panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    });
    </script>
    <?php
}

// AI-powered product Q&A
add_action('wp_ajax_ai_product_question', 'handle_ai_product_question');
add_action('wp_ajax_nopriv_ai_product_question', 'handle_ai_product_question');

function handle_ai_product_question() {
    // Verify nonce for security
    if (!check_ajax_referer('ai_product_question_nonce', 'nonce', false)) {
        wp_send_json_error(['message' => 'Security check failed']);
    }
    
    $question = isset($_POST['question']) ? sanitize_text_field(wp_unslash($_POST['question'])) : '';
    $product_id = isset($_POST['product_id']) ? absint($_POST['product_id']) : 0;
    
    if (empty($question) || empty($product_id)) {
        wp_send_json_error(['message' => 'Missing required fields']);
    }
    
    // Rate-limit per IP: this endpoint is public and each call costs real AI credits.
    // Without this, anyone can script requests and run up your provider bill.
    $ip        = isset($_SERVER['REMOTE_ADDR']) ? sanitize_text_field(wp_unslash($_SERVER['REMOTE_ADDR'])) : '';
    $rate_key  = 'ai_qa_' . md5($ip);
    $hits      = (int) get_transient($rate_key);
    if ($hits >= 5) {
        wp_send_json_error(['message' => 'Too many requests. Try again later.']);
    }
    set_transient($rate_key, $hits + 1, 5 * MINUTE_IN_SECONDS);
    
    $product = wc_get_product($product_id);
    if (!$product) {
        wp_send_json_error(['message' => 'Product not found']);
    }
    
    // Check if AI client is available
    if (!function_exists('wp_ai_client_prompt')) {
        wp_send_json_error(['message' => 'AI service unavailable']);
    }
    
    // Only include fields safe to disclose publicly. Do NOT include cost price,
    // supplier data, or anything not already visible on the product page.
    $prompt = sprintf(
        'Customer question about "%s": %s\n\nProduct details:
- Price: $%s
- Stock status: %s

Answer helpfully, accurately, and concisely. If the answer is not in the product
details, say you do not know.',
        $product->get_name(),
        $question,
        $product->get_price(),
        $product->get_stock_status()
    );
    
    // Chain the fluent builder; errors surface from generate_text().
    $answer = wp_ai_client_prompt($prompt)
        ->using_temperature(0.4) // Slightly higher for more varied responses
        ->generate_text();
    
    if (is_wp_error($answer)) {
        wp_send_json_error(['message' => 'Failed to generate response']);
    }
    
    wp_send_json_success(['answer' => esc_html($answer)]);
}
```

### Phase 6: Extensions

#### Actions
1. Install required extensions
2. Configure subscriptions
3. Set up bookings
4. Add memberships
5. Integrate marketplace

#### Abilities API for WooCommerce (WP 7.0)
Store operations registered as Abilities can be surfaced to AI agents as MCP tools via
the official MCP Adapter (see the `wordpress` skill for connection setup and security
rules). Keep `permission_callback` strict — `manage_woocommerce` at minimum — and mark
an ability `'meta' => ['mcp' => ['public' => true]]` only when a store agent should
reach it on the default server.
```php
// Register ability categories first
add_action('wp_abilities_api_categories_init', function() {
    wp_register_ability_category('ecommerce', [
        'label' => __('E-Commerce', 'woocommerce'),
        'description' => __('WooCommerce store management and operations', 'woocommerce'),
    ]);
});

// Register abilities
add_action('wp_abilities_api_init', function() {
    // Register ability to update inventory
    wp_register_ability('woocommerce/update-inventory', [
        'label' => __('Update Inventory', 'woocommerce'),
        'description' => __('Update product stock quantity', 'woocommerce'),
        'category' => 'ecommerce',
        'input_schema' => [
            'type' => 'object',
            'properties' => [
                'product_id' => ['type' => 'integer', 'description' => 'Product ID to update'],
                'quantity' => ['type' => 'integer', 'description' => 'New stock quantity']
            ],
            'required' => ['product_id', 'quantity']
        ],
        'output_schema' => [
            'type' => 'object',
            'properties' => [
                'success' => ['type' => 'boolean'],
                'new_quantity' => ['type' => 'integer']
            ]
        ],
        'execute_callback' => 'woocommerce_update_inventory_handler',
        'permission_callback' => function() {
            return current_user_can('manage_woocommerce');
        }
    ]);
    
    // Register ability to process orders
    wp_register_ability('woocommerce/process-order', [
        'label' => __('Process Order', 'woocommerce'),
        'description' => __('Mark order as processing and trigger fulfillment', 'woocommerce'),
        'category' => 'ecommerce',
        'input_schema' => [
            'type' => 'object',
            'properties' => [
                'order_id' => ['type' => 'integer', 'description' => 'Order ID to process']
            ],
            'required' => ['order_id']
        ],
        'output_schema' => [
            'type' => 'object',
            'properties' => [
                'success' => ['type' => 'boolean'],
                'status' => ['type' => 'string']
            ]
        ],
        'execute_callback' => 'woocommerce_process_order_handler',
        'permission_callback' => function() {
            return current_user_can('manage_woocommerce');
        }
    ]);
});

// Handler for inventory update
function woocommerce_update_inventory_handler($input) {
    $product_id = isset($input['product_id']) ? absint($input['product_id']) : 0;
    $quantity = isset($input['quantity']) ? absint($input['quantity']) : 0;
    
    $product = wc_get_product($product_id);
    if (!$product) {
        return new WP_Error('invalid_product', 'Product not found');
    }
    
    // Update stock
    wc_update_product_stock($product, $quantity);
    
    return [
        'success' => true,
        'new_quantity' => $product->get_stock_quantity()
    ];
}

// Handler for order processing
function woocommerce_process_order_handler($input) {
    $order_id = isset($input['order_id']) ? absint($input['order_id']) : 0;
    
    $order = wc_get_order($order_id);
    if (!$order) {
        return new WP_Error('invalid_order', 'Order not found');
    }
    
    $order->update_status('processing');
    
    return [
        'success' => true,
        'status' => 'processing'
    ];
}
```

### Phase 7: Optimization

#### Actions
1. Optimize product images
2. Enable caching
3. Optimize database
4. Configure CDN
5. Set up lazy loading

#### WordPress 7.0 Performance
- Client-side media processing
- Font Library enabled
- Responsive grid block
- View transitions for perceived performance

#### Query Performance & Coding Standards (`wc_get_products`)
- When passing `'exclude'` to `wc_get_products()`, annotate the array key to prevent false positives from VIPCS (`WordPressVIPMinimum.Performance.WPQueryParams.PostNotIn_exclude`):
```php
$products = wc_get_products([
    'limit'   => 50,
    'status'  => 'publish',
    'exclude' => array_map('intval', $excluded_ids), // phpcs:ignore WordPressVIPMinimum.Performance.WPQueryParams.PostNotIn_exclude -- WooCommerce wc_get_products argument.
]);
```
- For custom database tables (e.g. price histories, audit logs), use `%i` identifier placeholders in `$wpdb->prepare()` and annotate direct queries as outlined in the `wordpress-plugin-development` workflow.

### Phase 8: Testing

#### Actions
1. Test checkout flow
2. Verify payment processing
3. Test email notifications
4. Check mobile experience
5. Performance testing

#### WordPress 7.0 Testing
- Test with new admin interface
- Verify AI features work
- Test DataViews for orders
- Verify collaboration features

#### AI-Powered Store Testing
Test AI features as you would any integration: stub the AI client in tests, assert on
the deterministic fallbacks, and never gate a real checkout on live model output. Do not
ship checkout validators that send customer email, phone, or address to an AI provider
(see the privacy note in Phase 3) — the sample below validates that AI failures degrade
safely instead.

```php
// Integration test example: AI failure must never block checkout.
// Run inside your PHPUnit suite with the WooCommerce test framework.
public function test_ai_unavailable_does_not_block_checkout() {
    // Simulate an environment without the AI client.
    // The shipping-recommendation hook must no-op, not error.
    do_action('woocommerce_after_checkout_form', WC()->checkout());

    $notices = wc_get_notices('notice');
    foreach ($notices as $notice) {
        $this->assertStringNotContainsString('AI Recommendation', $notice['notice']);
    }
}

// When the AI client IS available, assert only on redacted prompts and advisory
// output. Keep the same low-temperature chained call style:
// $result = wp_ai_client_prompt($redacted_prompt)->using_temperature(0.1)->generate_text();
// and treat any WP_Error as "skip", never as "reject".
```

Manual QA checklist for AI features:
- [ ] Disable the AI provider plugin; store must work unchanged
- [ ] No PII appears in prompts sent to `wp_ai_client_prompt()`
- [ ] Model errors/timeouts degrade to the deterministic path
- [ ] No checkout, payment, or order status is decided by model output alone

## WooCommerce + WordPress 7.0 AI Use Cases

1. **Product Descriptions**
   - Auto-generate from product attributes
   - Translate descriptions
   - SEO optimization

2. **Customer Service**
   - AI chatbot for common questions
   - Order status lookup
   - Return processing

3. **Inventory Management**
   - Demand forecasting
   - Low stock alerts
   - Reorder recommendations

4. **Marketing**
   - Personalized emails
   - Product recommendations
   - Abandoned cart recovery

5. **Order Processing**
   - Fraud detection
   - Shipping optimization
   - Invoice generation

## Quality Gates

- [ ] Products displaying correctly
- [ ] Checkout flow working
- [ ] Payments processing
- [ ] Shipping calculating
- [ ] Emails sending
- [ ] Mobile responsive
- [ ] Coding standards verified (no unescaped DB parameters or unannotated query false positives)
- [ ] AI features tested (WP 7.0)
- [ ] DataViews working (WP 7.0)

## Related skills

- `wordpress` - Full WordPress development workflow
- `wordpress-theme-development` - Theme development workflow
- `wordpress-plugin-development` - Plugin development workflow
