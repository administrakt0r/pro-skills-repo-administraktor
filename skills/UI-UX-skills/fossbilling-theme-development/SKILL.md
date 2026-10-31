---
name: fossbilling-theme-development
description: Use when creating, modifying, debugging, or verifying FOSSBilling themes, Twig templates, cart & checkout workflows, ticket and invoice systems, API forms, or strict-mode Twig runtime behavior. Excludes core FOSSBilling PHP backend development or server infrastructure management.
---

# FOSSBilling Theme Development & Twig Engineering Guide

This guide establishes architecture, design rules, Twig conventions, API integration patterns, and verification protocols for engineering production-ready themes in [FOSSBilling](https://fossbilling.org/).

---

## 1. Architecture & Core Concepts

FOSSBilling themes operate on a multi-tier rendering architecture:
- **Template Engine**: Twig 3.x with strict variables (`strict_variables => true` in production).
- **HTTP Routing (`Box_App` / Slim)**: Routes are registered on separate roles:
  - `admin` (`/admin/...`)
  - `client` (`/login`, `/support`, `/order`, etc.)
  - `guest` (`/`, `/order`, `/support/contact-us`, `/kb`, etc.)
  - `api` (`/api/guest/...`, `/api/client/...`, `/api/admin/...`)
- **Theme Precedence & Overrides**:
  - Active theme templates reside in `themes/<theme_name>/html/`.
  - If a template is absent from the active theme, FOSSBilling falls back to `modules/<Module>/templates/client/` or `themes/huraga/html/`.
  - Extension assets reside in `themes/<theme_name>/assets/`.

---

## 2. Master Layouts & Block Contracts

### The Golden Rule: Never Omit Layout Blocks
Base layouts (`layout_default.html.twig`, `layout_public.html.twig`, `layout_blank.html.twig`) establish the structural contract for all module templates. If a layout fails to declare a block, Twig silently drops content that child templates place inside that block—**without raising a compile-time or runtime error**.

### Required Layout Blocks
Every master layout template must provide:

```twig
<!DOCTYPE html>
<html lang="{{ guest.system_locale|default('en')|replace({'_': '-'}) }}">
<head>
    <meta charset="utf-8">
    <title>{% block meta_title %}{% endblock %} - {{ company.name|default('Client Portal') }}</title>

    {# Essential for OpenGraph and social cards #}
    {% block opengraph %}{% endblock %}

    {# Essential for page-specific CSS or WYSIWYG assets #}
    {% block head %}{% endblock %}
</head>
<body class="{% block body_class %}{% endblock %}">
    {# Main view content #}
    {% block content_before %}{% endblock %}
    {% block content %}{% endblock %}
    {% block content_after %}{% endblock %}

    {# Global scripts #}
    {{ 'js/fossbilling.js'|public_asset_url|script_tag }}
    <script src="{{ 'assets/js/theme.js'|asset_url }}"></script>

    {# MANDATORY: Never omit this block. Child templates inject forms, modals, and API logic here. #}
    {% block js %}{% endblock %}

    {# Hook for FOSSBilling extension widgets #}
    {{ render_widgets('client.theme.body.end') }}
</body>
</html>
```

> [!CAUTION]
> **The Silent Script Drop Failure**: If `layout_default.html.twig` omits `{% block js %}{% endblock %}`, templates like `mod_support_tickets`, `mod_order_manage`, and `mod_support_ticket` have their form submit handlers silently discarded. This leads to native form submissions that result in fatal 404s.

---

## 3. Strict Variables Mode & Twig Defensive Templating

FOSSBilling can execute with `strict_variables => true`. In this mode, accessing a missing key or attribute halts rendering immediately:
```text
Key "X" for sequence/mapping does not exist in "<template>.html.twig" at line Y.
```

### Critical Twig Rules:
1. **Never use unshielded property access on optional/heterogeneous data**:
   - Cart items represent different product families (domains, cPanel hosting, VPS, addons, licenses).
   - Domain products have `register_sld`, `register_tld`, `period`, but **do not** have `description`.
   - Hosting products have `config` and `pricing`, but may lack `stock_control`.
2. **Always shield optional keys with `|default`**:
   ```twig
   {# BAD - crashes if description is missing in strict mode #}
   <p>{{ item.description }}</p>

   {# GOOD #}
   <p>{{ item.description|default('') }}</p>
   ```
3. **Distinguish `??` (Null Coalescing) from `|default`**:
   - Both `??` and `|default` safely guard against undefined keys in Twig strict mode without fatal errors.
   - **Use `??` when preserving valid `false` booleans or `0` matters** (e.g., `product.stock_control ?? false`, `settings.show_sidebar ?? true`). Because `|default` checks `empty()`, `false|default(true)` mistakenly evaluates to `true`!
   - **Use `|default` when empty strings or missing collections should trigger fallback** (e.g., `item.description|default('')`, `items|default([])`).
   - The fatal strict-mode crash (`Key "..." does not exist`) occurs when keys are accessed **directly without either `??` or `|default`** (e.g., `{{ item.description }}` or `{% if product.stock_control %}`).

### Common FOSSBilling Variables Cheat Sheet:
| Variable | Safe Twig Usage | Notes |
| :--- | :--- | :--- |
| Cart item description | `item.description\|default('')` | Absent on domain items; replaces empty strings |
| Product stock control | `product.stock_control ?? false` | Preserves valid `false` boolean; `\|default(true)` would invert `false` |
| Product addons | `product.addons ?? []` | Absent if addons disabled |
| Currency format | `item.total\|currency(item.currency ?? guest.cart_get_currency.code)` | Preserves defined currency code |
| Request parameters | `request.param_name\|default('')` | Guards absent request parameters |
| Client logged check | `client ? true : false` | Check `client` object before `client.email` |

---

## 4. Forms, API Integration & Routing Safety

FOSSBilling controllers strictly separate HTTP methods:
- Controller web routes (e.g. `modules/Support/Controller/Client.php`) only register `$app->get(...)`.
- State-changing actions are handled via the JSON-RPC / API router (`/api/client/...`, `/api/guest/...`).

### The Native POST 404 Pitfall
If a form is written as:
```html
<!-- FATAL FLAW -->
<form id="ticket-submit" method="post">
```
When JavaScript fails to intercept the submit (due to an error, missing block, or network glitch), the browser falls back to native submission:
`POST /support`
Because FOSSBilling has no `post('/support')` route, it halts with:
`404 Page /support not found`

### Proper Form Implementation Pattern
Always define an explicit API endpoint in `action`:

```twig
<form id="ticket-submit" method="post" action="{{ 'support/ticket_create'|api_url }}">
    <input type="hidden" name="CSRFToken" value="{{ CSRFToken }}">
    <!-- Form fields -->
    <button type="submit" class="theme-btn theme-btn-primary" id="ticket-submit-btn">
        {{ 'Submit Ticket'|trans }}
    </button>
</form>

{% block js %}
<script>
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById('ticket-submit');
    const submitBtn = document.getElementById('ticket-submit-btn') || form?.querySelector('button[type="submit"]');

    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span><span>{{ "Submitting..."|trans }}</span>';
            }

            FOSSBilling.api.client.post(
                'support/ticket_create',
                FOSSBilling.tools.serializeFormDataToObject(new FormData(form)),
                function (res) {
                    window.location = "{{ 'support/ticket'|url }}/" + res;
                },
                function (err) {
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.textContent = `{{ 'Submit Ticket'|trans }}`;
                    }
                    FOSSBilling.message(err.message, 'error');
                }
            );
        });
    }
});
</script>
{% endblock %}
```

### Guest Form Anti-Spam Honeypot
FOSSBilling includes an automated anti-spam honeypot on guest forms (such as `mod_support_contact_us`):
- Twig macro `{{ mf.recaptcha }}` renders a hidden `#anti-spam` field.
- In JavaScript, `document.getElementById('anti-spam')?.remove()` must be executed on DOM load. If bot-protection JS is stripped, submissions fail validation.

---

## 5. State Persistence & Flash Notification Bridge

When saving profile changes, updating orders, or closing tickets, user actions cause page reloads or redirects. Themes must persist and display these state transitions.

### Standard Flash Message Pattern (`theme.js`)
Ensure `assets/js/theme.js` implements `globalThis.flashMessage`:

```javascript
// Flash message handler for cross-page notifications
globalThis.flashMessage = function (options) {
  options = options || {};
  var message = options.message || '';
  var reload = options.reload || false;
  var type = options.type || 'info';
  var key = 'flash-message';

  if (!message) {
    try {
      var stored = sessionStorage.getItem(key);
      if (stored) {
        if (window.FOSSBilling && typeof window.FOSSBilling.message === 'function') {
          window.FOSSBilling.message(stored, type);
        }
        sessionStorage.removeItem(key);
      }
    } catch (e) {}
    return;
  }

  try {
    sessionStorage.setItem(key, message);
  } catch (e) {}

  if (reload === true) {
    window.location.reload();
  } else if (typeof reload === 'string' && reload) {
    window.location.assign(reload);
  }
};

// Always trigger on page load to consume any queued flash message
try {
  globalThis.flashMessage({});
} catch (e) {}
```

---

## 6. Verification & Quality Protocols

Never declare a template fix complete based solely on `curl` or static analysis.

### Standard Verification Checklist:
1. **Static Validation**:
   - Run `python3 AGENTARDS/scripts/validate_theme.py` (or local validator).
   - Confirm all JSON configuration files, Twig tags, and scripts parse without syntax errors.
2. **Interactive Form Life-Cycle**:
   - Test form submission with actual credentials or guest session.
   - Confirm server responses: HTTP 200 OK or proper JSON `{ result: ..., error: null }`.
   - Confirm redirect destination loads without 404 or Twig strict variable errors.
3. **Cross-Device Visual Evidence**:
   - Inspect desktop (1280x800) and mobile (375x812) viewports.
   - Verify modal dialogs render properly, scroll on mobile, and dismiss cleanly.
   - Verify toast alerts appear with adequate contrast and visible feedback.
