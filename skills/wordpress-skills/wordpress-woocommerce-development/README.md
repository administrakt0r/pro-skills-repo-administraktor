# wordpress-woocommerce-development

Focused workflow for WooCommerce stores: product configuration, payment
gateways, shipping, checkout, custom product types, extensions via the Abilities
API, optimization, and testing — with WordPress 7.0 features where they apply.

## Prerequisites

- PHP 7.4+ (8.3+ recommended), a local WordPress install with WooCommerce.
- Payment sandbox accounts (Stripe, PayPal) for the payment phase.
- An AI provider plugin only if you exercise the AI Client examples.

## Install

```bash
cp -R skills/wordpress-skills/wordpress-woocommerce-development ~/.config/opencode/skills/wordpress-woocommerce-development
```

## What it covers

- Eight phases: store setup, products, payments, shipping, customization,
  extensions, optimization, testing
- Deterministic-first design for fraud signals and shipping notices — model
  output is advisory only and PII never leaves the server without a legal basis
- Abilities API order/inventory automation with strict permission callbacks
- Rate limiting on public AI endpoints

See the [bundle README](../README.md) for provenance and review notes.
