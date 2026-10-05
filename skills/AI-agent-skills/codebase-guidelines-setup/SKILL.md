---
name: codebase-guidelines-setup
description: >-
  Establish authoritative codebase guidelines, boundaries, and project goals for AI coding agents.
  Use when onboarding AI agents to an existing or new repository, conducting an interactive
  diagnostic interview with the developer, and generating standardized instruction files
  (AGENTS.md, CLAUDE.md, .cursorrules / .mdc, and project goals).
---

# Codebase Guidelines & Agent Goals Setup

A universal operational skill for analyzing any repository, interviewing the developer to extract core goals and technical constraints, and establishing a single source of truth for all AI coding agents working in the codebase.

## Official Documentation & Upstream References

Reference these standards and upstream specifications when generating rule files:
- **Universal Agent Instructions Specification**:
  - `AGENTS.md` specification and multi-agent standards.
- **Cursor Project Rules**:
  - Context7 ID: `/patrickjs/awesome-cursorrules` (`npx ctx7@latest docs /patrickjs/awesome-cursorrules "rules format"`)
  - Modern `.cursor/rules/*.mdc` format with frontmatter (`globs`, `alwaysApply`).
- **Claude Code Architecture Guidelines**:
  - `CLAUDE.md` repository guidelines specification.
- **GitHub Copilot Repository Instructions**:
  - `.github/copilot-instructions.md` configuration guide.
- **llms.txt Codebase Context Standard**:
  - Context7 ID: `/firecrawl/llmstxt-generator` (`/llmstxt/`)

---

## When to Use

Activate this skill when:
- Setting up a new or existing repository for AI-assisted development.
- The developer asks to establish coding standards, rules of engagement, or goal tracking for AI agents.
- Agents are making repetitive mistakes, modifying forbidden files, hallucinating build commands, or violating codebase conventions.
- Standardizing agent guidelines across multiple team members and diverse AI tools (Claude Code, Cursor, Codex, Gemini CLI, etc.).

---

## The 4-Phase Workflow

```
[Phase 1: Automated Discovery]
   ├── Detect package manifests & runtimes
   ├── Scan directory tree & identify key layers
   └── Check existing configs, CI workflows & linters
                 │
                 ▼
[Phase 2: Interactive Developer Interview]
   ├── Ask targeted questions (Goals, Boundaries, Conventions)
   └── Clarify ambiguous patterns & forbidden operations
                 │
                 ▼
[Phase 3: Guideline Synthesis]
   ├── Compile authoritative AGENTS.md (Single Source of Truth)
   ├── Create tool bridges (CLAUDE.md, .cursor/rules, etc.)
   └── Create/update PROJECT_GOALS.md for active roadmap
                 │
                 ▼
[Phase 4: Verification & Agent Test]
   └── Dry-run test instructions against linters and build checks
```

---

## Phase 1: Automated Codebase Discovery

Before asking questions, the agent **MUST** run automated discovery to avoid asking trivial questions that can be answered from the filesystem.

### 1. Detect Stack & Manifests
Run file checks for common manifests:
- **Node/TS/JS**: `package.json`, `pnpm-workspace.yaml`, `tsconfig.json`
- **PHP**: `composer.json`
- **Python**: `pyproject.toml`, `requirements.txt`, `Pipfile`
- **Go**: `go.mod`
- **Rust**: `Cargo.toml`
- **Ruby**: `Gemfile`
- **Java/Kotlin**: `pom.xml`, `build.gradle`, `build.gradle.kts`
- **Infrastructure**: `Dockerfile`, `docker-compose.yml`, `wrangler.jsonc`, `vercel.json`

### 2. Identify Test & Lint Toolchains
Inspect `scripts` in `package.json`, `Makefile`, `.github/workflows/`, or config files:
- Linter configs: `.eslintrc*`, `biome.json`, `ruff.toml`, `phpstan.neon`, `golangci.yml`
- Test configs: `vitest.config.*`, `jest.config.*`, `phpunit.xml`, `pytest.ini`

### 3. Check for Existing AI Rules
Look for existing rules files that should be unified or migrated:
- `AGENTS.md` / `GEMINI.md` / `CLAUDE.md`
- `.cursorrules` or `.cursor/rules/*.mdc`
- `.github/copilot-instructions.md`
- `.agents/rules/` or `.windsurfrules`

---

## Phase 2: Interactive Developer Interview

Once automated discovery is complete, the agent **MUST present the developer with a focused questionnaire**. Group the questions into 4 core sections and tailor them to the detected stack.

### Question 1: Project Identity & Active Goals
- **Primary Objective**: What is the core purpose of this project, and what is the primary goal for this development cycle?
- **Audience & Context**: Is this a public library, an internal microservice, a high-traffic production application, or a prototype?

### Question 2: Architecture & Layering Rules
- **Layer Boundaries**: How should code be organized? (e.g., Domain-Driven, Feature-sliced, classic MVC, Clean Architecture).
- **Component / Module Conventions**: Are there strict patterns for creating new features (e.g., must every service have an interface, or every component have a co-located test)?

### Question 3: AI Agent Guardrails & No-Touch Zones
- **Forbidden Files / Folders**: What files must an AI agent NEVER modify directly? (e.g., production database migrations, `.env*`, generated schemas, lockfiles).
- **Dependency Policy**: Can the agent autonomously add new external packages, or must it explicitly request approval before installing anything?
- **Breaking Changes & Refactoring**: Are destructive rewrites allowed, or must changes be strictly incremental and backwards-compatible?

### Question 4: Commands & Operational Runbook
- **Golden Verification Path**: What exact sequence of commands must pass before any task is considered complete? (e.g., `npm run lint && npm test && npm run build`).
- **Target File Outputs**: Which agent instruction files should be generated?
  - `AGENTS.md` (Universal standard)
  - `CLAUDE.md` (Direct bridge for Claude Code)
  - `.cursor/rules/` (Modular `.mdc` files for Cursor)
  - `.github/copilot-instructions.md` (GitHub Copilot)
  - `PROJECT_GOALS.md` (Dedicated roadmap and goal-tracking document)

> Refer to [interview-framework.md](./references/interview-framework.md) for full branch logic and adaptive follow-up questions.

---

## Phase 3: Guideline Synthesis & File Generation

Synthesize the discovered data and the user's answers into high-leverage instruction documents.

### 1. The Universal Single Source of Truth (`AGENTS.md`)
Create `AGENTS.md` in the repository root. Ensure it includes:
1. **Repository Overview & Mission**: High-level description.
2. **Tech Stack & Toolchain**: Exact languages, runtimes, package managers, and versions.
3. **Commands Cheatsheet**: Copy-pasteable commands for Dev, Build, Test, Lint, and Format.
4. **Code Architecture & Directory Map**: What each top-level directory contains.
5. **Rules of Engagement (Crucial)**:
   - What the agent **MUST ALWAYS DO** (e.g., run `pnpm test` before concluding, keep functions small).
   - What the agent **MUST NEVER DO** (e.g., never commit unmasked API keys, never edit `dist/`).
6. **Error Handling & Security Standards**: Input sanitization, error wrapping, types.

### 2. Multi-Tool Bridge Strategy
To ensure all AI coding tools read the same guidelines without duplication:

- **For Claude Code (`CLAUDE.md`)**:
  Create `CLAUDE.md` referencing or mirroring `AGENTS.md`:
  ```markdown
  # Repository Guidelines for Claude Code

  > This project maintains its primary rules in [AGENTS.md](./AGENTS.md).
  > Follow all rules, commands, and constraints specified in AGENTS.md.

  ## Quick Reference Commands
  - Build: `<build_cmd>`
  - Test: `<test_cmd>`
  - Lint: `<lint_cmd>`
  ```

- **For Cursor (`.cursor/rules/main-guidelines.mdc`)**:
  ```markdown
  ---
  description: Core repository architecture and agent rules
  globs: **/*
  alwaysApply: true
  ---
  # Project Guidelines

  Refer to the primary rules defined in `AGENTS.md`.
  - Build: `<build_cmd>`
  - Test: `<test_cmd>`
  - Strictly observe all boundaries and no-touch zones.
  ```

### 3. Project Goals File (`PROJECT_GOALS.md`)
Create a dedicated `PROJECT_GOALS.md` tracking active milestones:
```markdown
# Project Goals & Agent Roadmap

## Current Milestone: [Milestone Name]
- [ ] Goal 1: Description and acceptance criteria
- [ ] Goal 2: Description and acceptance criteria

## Completed Milestones
- [x] Initial setup and architecture baseline

## Guidelines for AI Agents Working on Goals:
1. Always update the checkbox upon completing a goal.
2. Verify all acceptance criteria before marking a goal complete.
```

---

## Phase 4: Verification & Agent Testing

Confirm the guidelines are operational:
1. **Lint & Command Verification**: Run the verification command chain recorded in `AGENTS.md` to ensure all listed commands actually exist and exit cleanly.
2. **Path Verification**: Confirm that all paths, file references, and script names listed in `AGENTS.md` correspond to real paths in the repository.
3. **Review with Developer**: Present the generated `AGENTS.md` and `PROJECT_GOALS.md` to the developer for final sign-off.

---

## Best Practices

- **Be Concise and Actionable**: AI agent instruction files must not be filled with generic fluff. Every bullet point should constrain or direct model behavior.
- **State Negative Constraints Explicitly**: Models respond best to clear negative constraints (e.g., *"DO NOT use `any` in TypeScript"*, *"DO NOT touch database migration files once pushed"*).
- **Keep Verification Commands Deterministic**: Always provide exact, non-interactive commands (e.g., `npm test -- --run` instead of an interactive watch mode).
- **Version Control the Rules**: Check `AGENTS.md` into Git so the entire team shares the same agent guidelines.
