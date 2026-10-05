# Developer Interview Framework for AI Codebase Onboarding

An adaptive questioning tree designed for AI coding agents to systematically extract architectural boundaries, operational commands, and guardrails from developers across different stacks.

---

## 1. Interview Execution Protocol

When conducting the interview, the AI agent must follow these rules:

1. **Pre-populate from File Scans**: Never ask what can be directly inspected (e.g., "What language is this?" if `package.json` with TypeScript is in root). Instead, say: *"I noticed this is a TypeScript/Next.js repo using pnpm. Is that correct?"*
2. **Present Concise Choices**: Provide concrete options alongside open-ended questions to minimize developer typing.
3. **Adaptive Branching**: Only ask stack-relevant questions (e.g., skip database migration questions on a pure static frontend UI kit).

---

## 2. Core Question Bank (Universal)

### Section A: Project Goals & Scope
1. **Primary Purpose**:
   - *"In 1-2 sentences, what does this repository build or provide?"*
   - Options:
     - [ ] Production SaaS / Web App
     - [ ] Open Source Library / SDK
     - [ ] Internal Microservice / API
     - [ ] CLI Tool / Developer Utility
     - [ ] Content Site / Documentation
2. **Current Sprint / Cycle Focus**:
   - *"What is the main goal or milestone for upcoming AI agent tasks?"*
   - (e.g., building feature X, refactoring legacy module Y, improving test coverage to Z%).

---

### Section B: Architecture & Code Conventions
1. **Code Organization Style**:
   - *"How should code be structured when adding new features?"*
   - Options:
     - [ ] **Feature-Sliced**: Co-locate components, hooks, tests, and API calls per feature (`/features/auth/`).
     - [ ] **Layered / MVC**: Strict layer directories (`/controllers`, `/models`, `/views`, `/services`).
     - [ ] **Hexagonal / Clean Architecture**: Core domain isolated from adapters and infrastructure.
     - [ ] **Flat / Minimal**: Lightweight files without deep folder hierarchies.
2. **Typing & Strictness**:
   - *"What is your stance on type safety and lint strictness?"*
   - (e.g., strict TypeScript with `noImplicitAny`, zero warnings tolerated, strict return types).
3. **State & Data Management**:
   - *"What is the preferred pattern for managing state or database access?"*
   - (e.g., server components with server actions, Redux/Zustand, ORM vs raw SQL).

---

### Section C: Guardrails & "No-Touch" Zones (Crucial for AI Safety)
1. **Protected Files & Directories**:
   - *"Are there files or directories that an AI agent should NEVER touch or overwrite without explicit user permission?"*
   - Common choices to suggest:
     - [ ] Production database migrations (`/migrations`)
     - [ ] Lockfiles (`pnpm-lock.yaml`, `package-lock.json`, `composer.lock`)
     - [ ] Core authentication / billing modules
     - [ ] Generated files / schemas / type definitions (`/generated`, `*.d.ts`)
     - [ ] Environment files (`.env*`)
2. **Dependency & Package Policy**:
   - *"Can AI agents install new packages, or must they strictly ask before adding dependencies?"*
   - [ ] Autonomous: Can install reputable, well-known packages as needed.
   - [ ] Gated: Must ask and justify before adding any new package to `dependencies` or `devDependencies`.
   - [ ] Zero-deps: Never add new dependencies; use standard library or existing dependencies only.
3. **Refactoring Boundaries**:
   - *"When fixing a bug or adding a feature, should agents keep modifications strictly localized, or are broader refactorings welcomed?"*
   - [ ] Localized only (minimal diffs, zero side effects).
   - [ ] Proactive refactoring allowed if it improves code quality.

---

### Section D: Verification & Operational Commands
1. **Verification Command Chain**:
   - *"What exact commands must run cleanly before any AI task is marked complete?"*
   - Example presets to confirm:
     - `pnpm lint && pnpm test && pnpm build`
     - `composer test && ./vendor/bin/phpstan`
     - `go test ./... && golangci-lint run`
     - `pytest && ruff check .`
2. **Git & Commit Standards**:
   - *"Do you use Conventional Commits (`feat:`, `fix:`, `refactor:`) or a custom commit message format?"*

---

## 3. Stack-Specific Question Branches

### Branch: Frontend / UI (React, Next.js, Vue, Svelte)
- *"What component library or styling system is used? (Tailwind CSS, shadcn/ui, CSS Modules, Styled Components)?"*
- *"Are Server Components preferred over Client Components by default?"*
- *"Should components be written with named exports or default exports?"*

### Branch: Backend / API (Node, PHP, Go, Python)
- *"What API architecture is followed? (REST with JSON, GraphQL, gRPC)?"*
- *"How should validation errors and operational errors be formatted? (RFC 7807 Problem Details, custom JSON)?"*
- *"How should database transactions and connection pools be handled?"*

### Branch: CLI / Utilities (Go, Rust, Python, Bash)
- *"Is backwards compatibility with existing CLI arguments strictly required?"*
- *"Are stdout and stderr separated according to POSIX conventions (data to stdout, errors/logs to stderr)?"*

---

## 4. Synthesis Output Checklist

Once the developer responds to the questionnaire, the agent compiles:
- [ ] `AGENTS.md`: Authoritative guide containing all answers consolidated into enforceable markdown sections.
- [ ] `CLAUDE.md`: Lightweight pointer or mirror for Claude Code.
- [ ] `.cursor/rules/`: Tailored `.mdc` files for Cursor.
- [ ] `PROJECT_GOALS.md`: Active goals list with acceptance criteria.
