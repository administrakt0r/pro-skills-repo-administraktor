# Production AGENTS.md & PROJECT_GOALS.md Templates

Use these templates when synthesizing guidelines after completing the developer interview.

---

## 1. Universal `AGENTS.md` Master Template

```markdown
# Repository Guidelines for AI Coding Agents

## 1. Project Overview & Mission
- **Project Purpose**: [Brief description of the application/service/library]
- **Target Runtime / Environment**: [e.g., Node.js 20 LTS, PHP 8.3, Go 1.22]
- **Deployment Platform**: [e.g., Vercel, Cloudflare Pages, Docker, AWS ECS]

---

## 2. Toolchain & Essential Commands

All AI agents MUST use the following commands. Do not substitute package managers or flags.

| Task | Command | Notes |
| :--- | :--- | :--- |
| **Install** | `<install_cmd>` | [e.g., `pnpm install --frozen-lockfile`] |
| **Dev Server** | `<dev_cmd>` | [e.g., `pnpm dev`] |
| **Build** | `<build_cmd>` | [e.g., `pnpm build`] |
| **Test** | `<test_cmd>` | [e.g., `pnpm test -- --run`] |
| **Lint** | `<lint_cmd>` | [e.g., `pnpm lint`] |
| **Format** | `<format_cmd>` | [e.g., `pnpm format:check`] |
| **Type Check** | `<typecheck_cmd>` | [e.g., `pnpm tsc --noEmit`] |

### Golden Verification Pipeline
Before declaring any task complete or committing changes, you MUST run and achieve a zero exit code on:
```bash
<verification_pipeline_command>
```

---

## 3. Directory Layout & Architecture Boundaries

```text
/src
  ├── /core         # Pure business logic and domain entities (zero external framework dependencies)
  ├── /features     # Feature-sliced modules (UI, hooks, and local logic)
  ├── /components   # Shared universal UI components
  └── /lib          # Shared technical utilities (HTTP client, database, formatting)
```

### Architectural Invariants:
1. Modules inside `/core` MUST NOT import from `/features` or `/components`.
2. Shared components must remain stateless or manage only localized UI state.
3. Database queries must be encapsulated within repository or service layers—never executed directly inside route handlers.

---

## 4. Rules of Engagement & Guardrails

### MUST DO (Mandatory):
- Follow strict typing: No `any` or untyped casts unless strictly required with an explicit comment justification.
- Co-locate unit tests alongside implementation files (e.g., `user-service.ts` -> `user-service.test.ts`).
- Check that all imports resolve cleanly and adhere to path aliases (e.g., `@/components/*`).
- Handle errors explicitly using structured error classes or standard result types.
- Follow the project commit standard: Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`, `chore:`).

### MUST NOT DO (Strictly Forbidden):
- **NEVER modify locked paths**:
  - `migrations/` (Do not edit existing migrations; create new ones)
  - `.env*` (Never edit or expose production secrets)
  - `*-lock.yaml` / `package-lock.json` (Do not hand-edit lockfiles)
- **NEVER install unapproved dependencies**: You must request explicit confirmation before modifying `dependencies` in `package.json` / `composer.json`.
- **NEVER suppress lint or type errors**: Do not use `@ts-ignore`, `eslint-disable`, or `@phpstan-ignore` without explicit permission.
- **NEVER delete existing tests** to make a test suite pass.

---

## 5. Security & Data Protection Standards
- Always parameterize SQL/database queries.
- Sanitize and validate external user input at boundary entrypoints (using Zod / Pydantic / validator).
- Never log sensitive user data, PII, authentication tokens, or authorization headers.
```

---

## 2. Dedicated `PROJECT_GOALS.md` Template

```markdown
# Active Project Goals & AI Roadmap

This document defines the high-level roadmap and concrete active objectives for AI agents and developers working in this codebase.

## How Agents Use This Document:
1. Check the **Active Sprint / Milestone** before beginning multi-step refactors or features.
2. Align proposed tasks with listed acceptance criteria.
3. When a goal is accomplished and verified, update the checkbox and note the relevant commit or PR.

---

## Active Milestone: [Milestone Name]

### Objective 1: [Goal Title]
- **Status**: [In Progress / Planned / Blocked]
- **Target Files**: `src/features/auth/*`
- **Description**: [Detailed description of the requirement]
- **Acceptance Criteria**:
  - [ ] Criteria 1 (e.g., Unit tests cover at least 90% of edge cases)
  - [ ] Criteria 2 (e.g., All endpoints return RFC 7807 problem details on failure)
  - [ ] Criteria 3 (e.g., Build and typecheck pass cleanly)

### Objective 2: [Goal Title]
- **Status**: [Planned]
- **Target Files**: `src/api/*`
- **Description**: [Detailed description]
- **Acceptance Criteria**:
  - [ ] Criteria 1
  - [ ] Criteria 2

---

## Backlog & Future Goals
- [ ] Goal: Performance audit and LCP reduction below 1.5s
- [ ] Goal: Database indexing and slow query optimization

---

## Completed Goals Archive
- [x] Initial repository setup and baseline CI pipeline (Commit: `abc1234`)
```
