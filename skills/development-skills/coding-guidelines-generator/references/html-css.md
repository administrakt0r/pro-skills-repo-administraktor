# HTML & CSS Guidelines

> Verified: 2026-10-18, W3C HTML5 & WCAG 2.2 AA Standards

## Semantic HTML
- **Semantic Structure**: Use native semantic HTML elements (`<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<footer>`) instead of generic `<div>` wrappers.
- **Interactive Controls**: Always use native `<button>` for actions and `<a href="...">` for navigation. Do not attach click handlers to static elements (`<div>`, `<span>`).

## Accessibility & Contrast
- **WCAG AA Compliance**: Ensure text contrast meets minimum WCAG AA ratios (4.5:1 for normal text, 3:1 for large text). Never rely on color alone to convey meaning or state.
- **Form Controls**: Every form input must have a corresponding `<label for="...">` or explicit `aria-label`.

## CSS Conventions
- **No Inline Styles**: Never write inline `style="..."` attributes in HTML templates.
- **Responsive Design**: Design mobile-first using responsive layout units (`rem`, `ch`, CSS Grid, Flexbox) and `@media` queries.
