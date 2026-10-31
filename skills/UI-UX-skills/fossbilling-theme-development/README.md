# fossbilling-theme-development

Production-grade engineering workflow for creating, customizing, debugging, and verifying FOSSBilling client themes and Twig templates.

## Prerequisites

- FOSSBilling v0.8.x or v0.9.x running locally (Docker or LEMP/LAMP stack).
- PHP 8.2+ with Twig 3.x and `strict_variables => true`.
- Familiarity with FOSSBilling's API roles (`guest`, `client`, `admin`) and JSON-RPC endpoints.

## Install

```bash
cp -R skills/UI-UX-skills/fossbilling-theme-development ~/.config/opencode/skills/fossbilling-theme-development
```

## What it covers

- **Master Layout Block Contracts**: Declaring standard extension blocks (`{% block head %}`, `{% block js %}`) so child template scripts are never silently dropped.
- **Twig Strict Variables Guardrails**: Safe attribute and mapping access with `|default` filters; avoiding unshielded `??` operators on missing keys.
- **Form Action & Routing Fallbacks**: Specifying explicit API endpoint actions on every `<form>` to prevent browser fallbacks to fatal native `POST /<page>` 404s.
- **State Persistence & Flash Message Bridge**: Implementing `globalThis.flashMessage` with `sessionStorage` and `FOSSBilling.message` toasts.
- **Cart & Heterogeneous Checkout**: Robust rendering for diverse product families (domain registrations, transfers, hosting packages, addons).
- **Verification Protocols**: Static linting with `validate_theme.py`, interactive lifecycle testing, and cross-device visual verification via headless Chrome CDP.
