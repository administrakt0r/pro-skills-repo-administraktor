# twig-development

Production guide and reference for writing defensive, high-performance, and secure Twig 3.x templates across any PHP framework (Symfony, Drupal, Craft CMS, FOSSBilling, Timber/WordPress, Grav).

## Prerequisites

- PHP 8.1+ with Twig 3.x installed via Composer (`twig/twig`).
- Familiarity with HTML5 semantics and basic template inheritance concepts.

## Install

```bash
cp -R skills/development-skills/twig-development ~/.config/opencode/skills/twig-development
```

## What it covers

- **Defensive Templating & Strict Mode**: Safe property access under `strict_variables => true`, distinguishing `??` (preserves valid `false`, `0`, and empty strings) from `|default` (replaces empty values), and guarding against unshielded direct access.
- **Template Inheritance & Block Architecture**: Base layout contracts, calling `parent()`, and dynamic inheritance patterns.
- **Component Composition**: Using `{% include %}` with isolated scope (`only`), `{% embed %}` for complex widget layouts, and `{% use %}` for horizontal block traits.
- **Macros**: Authoring and consuming reusable markup components and attribute builders.
- **Filters & Collections**: Transforming datasets using `|filter`, `|map`, `|reduce`, `|batch`, and `|merge`.
- **Security & Auto-Escaping**: Context-aware escaping (`html`, `js`, `html_attr`), proper usage of `|raw`, and Twig Sandbox policy enforcement.
