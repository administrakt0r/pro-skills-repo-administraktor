# TypeScript Guidelines

> Verified: 2026-10-18, TypeScript Official Handbook, applies to TypeScript 5.0+
> Note: Extends JavaScript guidelines. Also observe `references/javascript.md`.

## Type Safety & Strictness
- **Strict Mode**: Preserve `"strict": true` in `tsconfig.json`. Never loosen `noImplicitAny`, `strictNullChecks`, or `noUncheckedIndexedAccess` to make a build pass. Fix the underlying type mismatch.
- **Avoid Any**: Never declare variables or function parameters as `any`. Use `unknown` for data of unknown structure, then narrow using type guards, assertion functions, or schema parsers.
- **Narrowing & Casts**: Minimize type assertions (`as Type`). Do not use non-null assertions (`!`) unless immediately preceded by a verified runtime guard. Avoid `@ts-ignore` or `@ts-expect-error` without an adjacent comment detailing the upstream compiler issue.

## Boundary Validation
- **External Data**: Never trust external input (HTTP request bodies, URL search params, filesystem reads, localStorage) to match TypeScript interface shapes at runtime. Validate boundaries using schema libraries (such as Zod, Valibot, or ArkType) before consumption.
- **Exports & Interfaces**: Prefer `interface` for public APIs and extensible object shapes; prefer `type` for unions, intersections, and mapped primitives.

## Verification
- **Type Checking**: Run `tsc --noEmit` before committing code to verify compiler health without generating build artifacts.
