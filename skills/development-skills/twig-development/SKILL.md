---
name: twig-development
description: Use when authoring, refactoring, debugging, or optimizing Twig templates across any PHP framework or CMS (Symfony, Drupal, Craft CMS, Prestashop, FOSSBilling, Timber/WordPress, Grav). Covers Twig 3.x syntax, defensive strict-variables handling, template inheritance and block architecture, macros, filters, components, auto-escaping, sandboxing, and performance optimization. Excludes framework-specific PHP controller routing or backend database queries.
---

# Modern Twig Templating & Template Engineering Guide

Twig is a modern, fast, and secure template engine for PHP, compiling templates down to optimized, raw PHP bytecode. It is the primary template engine across Symfony, Drupal, Craft CMS, Grav, FOSSBilling, Timber (WordPress), and many enterprise PHP ecosystems.

This skill provides patterns, defensive coding rules, component architectures, and debugging protocols for engineering reliable, high-performance Twig 3.x templates.

---

## 1. Engine Fundamentals & Architecture

### Delimiters & Core Constructs
- `{{ ... }}`: **Say (Expression Output)**. Evaluates an expression, applies auto-escaping according to context, and prints to the output buffer.
- `{% ... %}`: **Do (Control Flow & Tags)**. Executes logic, loops, conditionals, template inheritance, variable assignments, and block definitions.
- `{# ... #}`: **Comment**. Stripped completely during compilation; never emitted to the client HTML.

### Whitespace Trimming Control
Twig provides hyphens (`-`) on any delimiter tag to strip surrounding whitespace (spaces, tabs, newlines):
```twig
{# Strips leading and trailing whitespace around output #}
{{- value -}}

{# Strips whitespace inside conditionals #}
{%- if condition -%}
    <span>Clean Output</span>
{%- endif -%}
```

### Compilation & Caching Pipeline
1. **Parsing & Tokenizing**: Twig parses the template into an Abstract Syntax Tree (AST).
2. **Compiling**: The AST compiles into a pure PHP class cached on the filesystem.
3. **Execution**: Subsequent requests execute the cached PHP class directly with zero template parsing overhead.
4. **Configuration Invariants**:
   - `cache`: Always set to a writable directory in production (`/path/to/var/cache/twig`).
   - `auto_reload`: Set to `false` in production for maximum performance; `true` in development to reload templates on modification.
   - `strict_variables`: When `true`, accessing non-existent variables, attributes, or array keys triggers a fatal `Twig\Error\RuntimeError`.

---

## 2. Defensive Templating: Strict Mode & Null Coalescing (`??`) vs `|default`

In production environments, Twig frequently runs with `'strict_variables' => true`. When strict variables are enforced, referencing an undefined key or missing property without a guard halts template rendering with a fatal `Twig\Error\RuntimeError: Key "..." does not exist`.

### Direct Access vs Null Coalescing (`??`) vs `|default`
A common misconception is that `??` fails in strict mode. In reality, Twig's `NullCoalesceExpression` explicitly checks whether the variable/attribute is defined and not null before resolving. Both `??` and `|default` safely guard against undefined keys, but they have critically different semantics regarding falsy values (`false`, `""`, `0`):

| Construct | Handles Undefined Keys? | Preserves `false`? | Preserves `""`? | Preserves `0`? | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Direct Access (`item.key`)** | ❌ Fatal `RuntimeError` | N/A | N/A | N/A | Guaranteed properties only |
| **Null Coalescing (`item.key ?? fallback`)** | ✅ Safe | ✅ Yes (`false`) | ✅ Yes (`""`) | ✅ Yes (`0`) | Booleans, optional overrides, flags |
| **Default Filter (`item.key\|default(fallback)`)** | ✅ Safe | ❌ Replaced with fallback | ❌ Replaced with fallback | ✅ Kept (if numeric) | Display text, empty strings, missing arrays |

### Preserving Valid Falsy Values
Using `|default` on a boolean or empty-string value silently mutates business logic because `default` checks for `empty()`:

```twig
{# Scenario: product.stock_control is explicitly set to boolean false #}

{# ❌ BUG: |default treats false as empty and replaces it with true! #}
{% set stock_enabled = product.stock_control|default(true) %}
{# stock_enabled is now TRUE instead of the intended FALSE #}

{# ✅ CORRECT: ?? only replaces null or undefined, preserving false #}
{% set stock_enabled = product.stock_control ?? true %}
{# stock_enabled is properly FALSE #}

{# Scenario: user.custom_title is an empty string ("") indicating an intentional blank title #}
{{ user.custom_title ?? 'Default Title' }}   {# Renders "" (preserves intentional blank) #}
{{ user.custom_title|default('Default Title') }} {# Renders "Default Title" (replaces empty string) #}
```

### Essential Defensive Rules:
1. **Never use unshielded direct property access on optional/heterogeneous mappings**:
   Direct access (`{{ item.description }}`) is what causes fatal strict-mode crashes when rendering polymorphic cart items or dynamic API responses.
2. **Choose `??` when preserving `false`, `0`, or `""` matters**:
   - Boolean toggles: `product.stock_control ?? false`, `settings.show_sidebar ?? true`.
   - Counts and offsets: `cart.discount_amount ?? 0`.
3. **Choose `|default` when any empty value should trigger fallback**:
   - Display labels: `item.description|default('No description provided')`.
   - Fallback collections: `items|default([])`.
4. **Chain Defaults for Deep Navigation**:
   Both `??` and `|default` short-circuit gracefully across nested paths:
   ```twig
   {{ order.customer.billing_address.city ?? 'N/A' }}
   {{ order.customer.billing_address.city|default('N/A') }}
   ```
5. **Guard Against Empty Traversables**:
   Use Twig's native `{% for ... else %}` syntax rather than checking count:
   ```twig
   {% for item in cart.items ?? [] %}
       <div class="cart-row">{{ item.title|default('Product') }}</div>
   {% else %}
       <p class="text-muted">{{ 'Your cart is empty.'|trans }}</p>
   {% endfor %}
   ```
6. **Native Twig Tests Reference**:
   - `var is defined`: Checks if variable/key exists in context.
   - `var is empty`: True if `null`, `false`, `''`, `[]`, or empty `Countable`.
   - `var is null`: Strict null comparison.
   - `var is iterable`: Checks if variable can be looped over with `{% for %}`.
   - `var is same as(value)`: Strict identity (`===`).

---

## 3. Template Inheritance & Block Architecture

Template inheritance is Twig's core architectural pattern. It solves the boilerplate duplication problem by defining an extensible base skeleton.

### Base Layout Contract
Base layouts must declare extension points. Never omit critical asset or script blocks:

```twig
{# templates/layouts/base.html.twig #}
<!DOCTYPE html>
<html lang="{{ app.locale|default('en') }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}{{ company.name|default('Portal') }}{% endblock %}</title>

    {% block stylesheets %}
        <link rel="stylesheet" href="{{ asset('css/main.css') }}">
    {% endblock %}

    {% block head %}{% endblock %}
</head>
<body class="{% block body_class %}{% endblock %}">
    {% block header %}
        {% include 'partials/header.html.twig' %}
    {% endblock %}

    <main id="main-content">
        {% block content %}{% endblock %}
    </main>

    {% block footer %}
        {% include 'partials/footer.html.twig' %}
    {% endblock %}

    {% block javascripts %}
        <script src="{{ asset('js/app.js') }}"></script>
    {% endblock %}

    {# Essential for child template modal/form scripts #}
    {% block js %}{% endblock %}
</body>
</html>
```

### The `parent()` Function
Child templates can append or prepend to inherited blocks using `{{ parent() }}`:

```twig
{# templates/pages/dashboard.html.twig #}
{% extends 'layouts/base.html.twig' %}

{% block title %}Dashboard | {{ parent() }}{% endblock %}

{% block stylesheets %}
    {{ parent() }}
    <link rel="stylesheet" href="{{ asset('css/dashboard.css') }}">
{% endblock %}

{% block content %}
    <h1>User Dashboard</h1>
{% endblock %}

{% block js %}
    <script src="{{ asset('js/chart-widgets.js') }}"></script>
{% endblock %}
```

### Inheritance Invariants:
- A template that declares `{% extends %}` **cannot have any HTML tags or text outside of `{% block %}` definitions**. Anything outside a block is discarded or raises a syntax error.
- Dynamic inheritance allows conditional rendering:
  ```twig
  {% extends request.ajax ? 'layouts/blank.html.twig' : 'layouts/base.html.twig' %}
  ```

---

## 4. Component Composition: Include, Embed, and Use

| Construct | Syntax | Primary Use Case | Scope Isolation |
| :--- | :--- | :--- | :--- |
| **`include`** | `{% include 't.html.twig' %}` | Small, static template snippets (header, footer, badges). | Shares context by default. Use `with {...} only` to isolate. |
| **`embed`** | `{% embed 'modal.html.twig' %}...{% endembed %}` | Complex widgets with internal overridable blocks (dialogs, cards). | Creates a mini-inheritance scope while including. |
| **`use`** | `{% use 'blocks/forms.html.twig' %}` | Horizontal block reuse (traits); imports blocks without full inheritance. | Imports blocks into current template. |

### Component Pattern with `{% embed %}`
The `embed` tag combines the properties of `include` and `extends`:

```twig
{# templates/components/modal.html.twig #}
<div class="modal fade" id="{{ modal_id|default('app-modal') }}" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">{% block modal_title %}Modal Title{% endblock %}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                {% block modal_body %}{% endblock %}
            </div>
            <div class="modal-footer">
                {% block modal_footer %}
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                {% endblock %}
            </div>
        </div>
    </div>
</div>

{# Consuming the component in another template #}
{% embed 'components/modal.html.twig' with { modal_id: 'confirm-delete' } %}
    {% block modal_title %}{{ 'Confirm Deletion'|trans }}{% endblock %}
    {% block modal_body %}
        <p>{{ 'Are you sure you want to permanently delete this resource?'|trans }}</p>
    {% endblock %}
    {% block modal_footer %}
        {{ parent() }}
        <button type="button" class="btn btn-danger" id="delete-btn">{{ 'Delete'|trans }}</button>
    {% endblock %}
{% endembed %}
```

---

## 5. Macros & Reusable UI Functions

Macros are the Twig equivalent of functions in PHP or components in React. They encapsulate markup generation and keep templates DRY.

### Defining and Importing Macros:
```twig
{# templates/macros/ui.html.twig #}
{% macro badge(text, type='info', icon=null) %}
    <span class="badge badge-{{ type|default('info') }}">
        {% if icon %}<i class="icon-{{ icon }}"></i> {% endif %}
        {{ text }}
    </span>
{% endmacro %}

{% macro button(label, url='#', variant='primary', size='md', type='button', attrs={}) %}
    <a href="{{ url }}" class="btn btn-{{ variant }} btn-{{ size }}" role="{{ type }}"
       {% for k, v in attrs|default({}) %}{{ k }}="{{ v|e('html_attr') }}" {% endfor %}>
        {{ label }}
    </a>
{% endmacro %}
```

```twig
{# Consuming template #}
{% import 'macros/ui.html.twig' as ui %}

{{ ui.badge('Active', 'success', 'check') }}
{{ ui.button('Edit Profile', path('user_edit'), 'outline-primary', 'sm') }}
```

### Macro Best Practices:
- Always define default values for optional parameters in the signature.
- Macros cannot access template variables unless explicitly passed in, or unless `_context` is passed: `{{ ui.render_nav(_context) }}`.

---

## 6. Filters & Collection Transformations

Twig includes powerful functional filters for transforming strings, numbers, dates, and arrays.

### Collection Operations
```twig
{# Filtering items #}
{% set active_orders = orders|filter(o => o.status == 'active') %}

{# Mapping fields #}
{% set user_names = users|map(u => "#{u.first_name} #{u.last_name}") %}

{# Merging arrays/dictionaries #}
{% set final_config = default_config|merge(user_config|default({})) %}

{# Slicing arrays #}
{% for item in items|slice(0, 5) %}
    <li>{{ item.name }}</li>
{% endfor %}

{# Batching arrays into columns #}
{% for row in products|batch(3, 'No Product') %}
    <div class="row">
        {% for col in row %}
            <div class="col-4">{{ col.name|default(col) }}</div>
        {% endfor %}
    </div>
{% endfor %}
```

### String & Formatting Filters
- `|e('html')` / `|e('js')` / `|e('css')` / `|e('url')` / `|e('html_attr')`: Context-aware escaping.
- `|trim`: Strips leading/trailing whitespace.
- `|replace({'old': 'new'})`: Replaces substrings.
- `|striptags('<p><a>')`: Removes HTML tags, optionally keeping allowed ones.
- `|date('Y-m-d H:i:s', timezone='UTC')`: Formats date strings, timestamps, or `DateTimeInterface` objects.
- `|number_format(decimals=2, decimal_sep='.', thousands_sep=',')`: Formats floating-point numbers.

---

## 7. Security, Escaping & Sandboxing

### The Golden Rule of `|raw`
By default, Twig automatically HTML-escapes all expression outputs (`{{ ... }}`).
- **NEVER** use `|raw` on untrusted user input (form input, query params, unescaped database fields).
- Only use `|raw` on sanitized HTML produced by trusted markdown parsers or backend WYSIWYG sanitizers (e.g. HTMLPurifier).

### Escaping by Context
When interpolating variables into JavaScript or HTML attributes, specify the context:
```twig
{# Injecting into a JavaScript string #}
<script>
    const userRole = "{{ user.role|e('js') }}";
</script>

{# Injecting into an HTML attribute #}
<div data-tooltip="{{ tooltip_text|e('html_attr') }}"></div>
```

### Twig Sandbox Mode
When allowing untrusted end-users to edit templates (e.g., email templates, CMS custom pages), enforce the Twig Sandbox:
```php
use Twig\Extension\SandboxExtension;
use Twig\Sandbox\SecurityPolicy;

$tags = ['if', 'for'];
$filters = ['upper', 'date', 'default', 'escape'];
$methods = ['Article' => ['getTitle', 'getBody']];
$properties = ['Article' => ['title', 'body']];
$functions = ['range'];

$policy = new SecurityPolicy($tags, $filters, $methods, $properties, $functions);
$twig->addExtension(new SandboxExtension($policy, true)); // true = sandbox all templates
```

---

## 8. Quality & Debugging Checklist

Before finalizing any Twig template changes:

- [ ] **Strict Variables Audit**: Run with `strict_variables => true`. Verify all optional properties are guarded by either `??` (to preserve `false`/empty values) or `|default` (to replace empty values), preventing unshielded direct access.
- [ ] **All Fallbacks Guarded**: Every dynamic variable has an appropriate `|default` filter.
- [ ] **Master Layout Block Verification**: Verify all child templates extend base layouts that declare `{% block head %}` and `{% block js %}`.
- [ ] **XSS Audit**: Confirm `|raw` is only applied to pre-sanitized strings; verify proper escaping context (`js`, `html_attr`) where applicable.
- [ ] **Empty State Handling**: Ensure `{% for ... else %}` handles empty sets gracefully.
- [ ] **No Business Logic in Views**: Complex data mutations, SQL queries, or heavy sorting operations are resolved in backend PHP controllers, not Twig templates.
- [ ] **Syntax Compilation Check**: Run the CLI syntax validator (e.g., `php bin/console lint:twig templates/` in Symfony or custom AST parser).
