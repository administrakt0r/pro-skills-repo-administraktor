# Next.js Guidelines

> Verified: 2026-10-18, Next.js Official Docs, applies to Next.js 14+ / 15+
> Note: Extends React and JavaScript/TypeScript guidelines. Also read AGENTS-GUIDELINES-REACT.md and AGENTS-GUIDELINES-JS.md.

## Component Boundaries & Routing
- **Server Components by Default**: In the App Router (`app/`), all components are React Server Components (RSC) by default. Add `'use client'` only at leaf components that require browser APIs, event listeners (`onClick`, `onChange`), or React client state hooks (`useState`, `useEffect`).
- **Data Fetching**: Fetch data directly in Server Components using async/await. Keep database credentials and secrets on the server.

## Security & Server Actions
- **Server Action Authorization**: Treat Server Actions (`'use server'`) as public HTTP endpoints. Always re-authenticate the user, verify session validity, and authorize the specific resource ID inside the action before mutating data. Never trust caller-provided user IDs.
- **Environment Variables**: Only prefix variables with `NEXT_PUBLIC_` if they are safe to expose to the public client bundle. Keep API secrets, database connection strings, and private keys un-prefixed.

## Caching & Route Handlers
- **Caching Semantics**: Next.js 15 defaults `fetch` requests and route handlers to uncached (`cache: 'no-store'`). When caching is desirable, use explicit `revalidateTag()` or `revalidatePath()` rather than blanket cache configurations.

## Verification
- Build & check: `next build` (or `{pm} run build`).
- Type and lint check: `{pm} run lint` (note: Next.js 16+ deprecates/removes `next lint` in favor of project ESLint/Biome scripts).
