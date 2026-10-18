# React Guidelines

> Verified: 2026-10-18, React Official Docs (react.dev), applies to React 18+ / React 19
> Note: Extends JavaScript/TypeScript guidelines. Also observe `references/javascript.md` and `references/typescript.md`.

## Hooks & Component State
- **Rules of Hooks**: Only call hooks at the top level of function components or custom hooks. Never call hooks inside loops, conditions, or nested functions.
- **Minimal Effects**: Do not use `useEffect` for data transformation or computing values from existing props/state. Calculate derived state during rendering. Use effects only to synchronize with external non-React systems (timers, browser APIs, network sockets).
- **Stable Keys**: Always provide unique, stable identifiers for list `key` props. Never use array indices as keys if items can be reordered, filtered, or deleted.

## Accessibility (A11y)
- **Semantic Elements**: Use native interactive elements (`<button>`, `<a>`, `<input>`) instead of `<div onClick=...>` with ARIA attributes.
- **Labels & Forms**: Ensure all form inputs have associated `<label>` elements or accessible names (`aria-label`, `aria-labelledby`).
- **Keyboard Navigation**: Ensure custom modal dialogs, popovers, and menus manage focus correctly and trap focus when active.

## Verification & Testing
- **Testing by Behavior**: Write component tests that query the DOM by user-facing roles and text (e.g. `getByRole('button', { name: /save/i })`), not implementation details like CSS class names or internal state.
