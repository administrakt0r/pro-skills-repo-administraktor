# JavaScript Guidelines

> Verified: 2026-10-18, Node.js & TC39 Official Docs, applies to Node.js 18+ / ES2022+

## Module Consistency & Imports
- **Module System**: Follow the repository's module system consistently. If `"type": "module"` is configured in `package.json`, use standard ESM (`import`/`export`). Do not mix `require()` and `import` within the same package unless explicitly interoperating.
- **Node Built-ins**: Prefix Node.js core modules with `node:` (e.g., `import fs from 'node:fs/promises';`).

## Async & Error Flow
- **No Floating Promises**: Every promise returned by an async function must be `await`ed or chained with `.catch()`. Unhandled rejections cause process exits in modern runtimes.
- **Error Handling**: Throw real `Error` instances (or custom subclasses), never raw strings, numbers, or plain objects.
- **Top-Level Await**: Use top-level await only in entry-point CLI scripts or module initialization files where execution order is deterministic.

## Verification & Never-Dos
- **Verification Commands**: Follow scripts defined in `package.json`:
  - Lint: `{pm} run lint`
  - Test: `{pm} test`
- **Never-Do**:
  - Never suppress unhandled errors with empty `catch {}` blocks without explanatory comment.
  - Never mutate `Array.prototype` or global prototypes.
  - Never use `eval()` or `new Function()` for dynamic execution.
