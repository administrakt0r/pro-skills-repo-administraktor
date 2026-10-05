# Tailwind CSS Development Skill

A universal AI agent skill for developing modern, accessible, and performant web interfaces with Tailwind CSS (v3 and v4).

## Overview

This skill equips AI coding agents to author idiomatic Tailwind CSS code, configure design tokens, manage dark mode strategies, structure robust components using class merging utilities (`cn`), implement micro-interactions and transitions, and navigate architectural upgrades from Tailwind CSS v3 to v4.

## Files

- [`SKILL.md`](SKILL.md): Core skill definition, workflow guidelines, step-by-step instructions, best practices, pitfalls, and verification procedures.
- [`references/utility-patterns.md`](references/utility-patterns.md): Concrete copy-paste patterns for application layouts, form controls, card and button systems, fluid typography, ambient shadows, and animation keyframes.

## Covered Topics

- Utility-first workflow and mindset
- Mobile-first responsive design (`sm`, `md`, `lg`, `xl`, `2xl`)
- Container queries (`@container`)
- Dark mode configuration (`media` vs `class` / `selector` strategies)
- Tailwind v3 configuration (`tailwind.config.ts`) vs v4 CSS-first configuration (`@theme`, `@utility`, `@variant`)
- Design token extensions (colors, spacing, typography)
- Arbitrary values (`w-[120px]`) and properties (`[mask-type:alpha]`)
- Component extraction vs `@apply`
- Transitions, hover/active/focus states, and keyframe animations
- Integration with React/Next.js and class composition (`cn()` with `clsx` and `tailwind-merge`)
- Official plugins (`@tailwindcss/typography`, `@tailwindcss/forms`)
- Automated and manual migration from v3 to v4
