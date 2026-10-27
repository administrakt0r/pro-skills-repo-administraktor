---
name: codebase-todoist
description: Use when invoked on any codebase to perform a thorough scan of its structure, completion state, features, and gaps, then produce a ranked TODOIST.md of actionable work items with context, rationale, and competitive insight.
---

# Codebase TODOIST Generator

## Overview

Scan the codebase end-to-end, understand what it is and what it does, assess its completion state, compare it against proven patterns from comparable public projects, then write a **TODOIST.md** file at the repo root. Every item in that file is ranked, scoped, explained with a "why", and estimated — ready to execute without additional context.

> **Privacy guarantee:** This skill never reads, logs, or outputs secrets, credentials, `.env` files, personal data, or anything outside the current repository's tracked files.

---

## When to Use

- Invoked explicitly (`/codebase-todoist`, `use codebase-todoist skill`, or `generate TODOIST.md`)
- Starting work on an unfamiliar codebase and needing a prioritized action plan
- Before a sprint, milestone, or release to find gaps and feature opportunities
- After a large refactor, to re-assess outstanding work
- When a project feels "stuck" and you want structured next steps

**Do NOT use when:**
- The project has no committed source files (nothing to scan)
- The user only wants a generic checklist unrelated to this codebase

---

## Phase 1 — Codebase Discovery

Run these steps in order. Collect evidence; do not write TODOIST.md yet.

### 1.1 Identity & Stack

```
Read: README.md, package.json / pyproject.toml / go.mod / Cargo.toml / pom.xml
      composer.json, Gemfile, .nvmrc, .ruby-version, Dockerfile, docker-compose.yml
      wrangler.toml / wrangler.json, vercel.json, netlify.toml, fly.toml
```

Extract:
- **Project name** and one-sentence purpose
- **Language(s)** and primary framework(s)
- **Runtime target** (browser SPA, SSR, API, CLI, mobile, library, worker, …)
- **Package manager** (npm/pnpm/yarn/bun, pip/uv, cargo, go, …)
- **Deployment target** (Cloudflare Workers, Vercel, Railway, Docker, bare VPS, …)

### 1.2 Architecture Scan

```
Read: src/, app/, lib/, server/, worker/, api/, pages/, routes/, components/
      (recurse up to 3 levels; do not read node_modules, .git, dist, build, .next, .cache)
```

Identify:
- Entry points and main modules
- Data-flow pattern (MVC, feature-sliced, domain-driven, flat, monorepo, …)
- Database / persistence layer and migration state
- Auth surface (none, JWT, session, OAuth, API keys)
- External service integrations (APIs, queues, storage, …)
- Test surface: presence and coverage of unit / integration / e2e tests
- CI/CD config: `.github/workflows/`, `.circleci/`, `Makefile` targets

### 1.3 Completion State Assessment

For each major module or surface area assign one of:

| State | Meaning |
|-------|---------|
| ✅ Done | Functional, tested, production-ready |
| 🔧 Partial | Core logic exists but incomplete, untested, or broken |
| ❌ Missing | Clearly implied by the stack/spec but absent |
| 💡 Opportunity | Not present, but proven valuable in comparable projects |

Scan for hard signals:
- `TODO`, `FIXME`, `HACK`, `XXX` comments in source
- Placeholder routes returning 501/stub responses
- Empty or near-empty files
- Commented-out blocks of significant size
- Schema migrations with no corresponding business logic
- Test files that import non-existent modules

### 1.4 Existing TODO Inventory

```bash
grep -rn "TODO\|FIXME\|HACK\|XXX\|PLACEHOLDER\|STUB\|WIP" \
  --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" \
  --include="*.py" --include="*.go" --include="*.rs" --include="*.php" \
  --include="*.rb" --include="*.java" --include="*.kt" \
  src/ app/ lib/ server/ worker/ api/ pages/ routes/ 2>/dev/null \
  | grep -v node_modules | grep -v ".git"
```

Record file + line + content for each hit; deduplicate by theme.

---

## Phase 2 — Competitive & Ecosystem Research

**Goal:** surface features that are proven to work in comparable products, so recommendations are grounded in market evidence, not speculation.

### 2.1 Identify Comparable Projects

Using the project identity established in Phase 1, search for:

```
"[project type] open source [primary language]" GitHub stars > 500
"[project type] SaaS features" site:github.com
"[project type] alternatives" site:reddit.com OR site:hn.algolia.com
```

Examples by project type:

| Project type | Reference projects to look up |
|---|---|
| REST/GraphQL API | fastify, hono, nestjs ecosystem starter repos |
| React SPA | bulletproof-react, t3-stack, refine |
| CLI tool | cobra-based CLIs, oclif starters |
| E-commerce | medusa, woocommerce, solidus |
| CMS / blog | ghost, keystatic, payload |
| Auth service | better-auth, lucia, clerk OSS |
| Data pipeline | dagster, prefect OSS starters |
| Mobile (RN) | expo-router starters, react-native-template-obytes |

Search for **feature lists, changelogs, and roadmaps** of the 2–3 closest analogues. Extract features tagged as "highly requested", "v2", "shipped in X.Y", or starred in their own TODOs.

### 2.2 Filter for Relevance

Only carry forward competitive features that:
1. Make sense given **this project's stack and purpose**
2. Are implementable without replacing the existing architecture
3. Provide clear user or developer value

Label these **"Competitive Opportunity"** in the output.

---

## Phase 3 — Ranking Matrix

Score every candidate work item on three dimensions (1–3 each):

| Dimension | 1 (Low) | 2 (Medium) | 3 (High) |
|-----------|---------|------------|----------|
| **Impact** | Nice-to-have | Meaningfully improves UX/DX/reliability | Unblocks core value or prevents data loss |
| **Effort** | > 2 weeks solo | 2–5 days | < 1 day |
| **Risk** | Breaks existing contracts / requires migration | Isolated change with rollback path | Additive, zero regression risk |

**Priority score = Impact × 2 + Effort + Risk** (range 4–15; higher = do first)

Items scoring ≥ 12 are **P0 – Critical**.
Items scoring 9–11 are **P1 – High**.
Items scoring 6–8 are **P2 – Medium**.
Items scoring ≤ 5 are **P3 – Low / Backlog**.

---

## Phase 4 — Write TODOIST.md

Create (or overwrite) `TODOIST.md` at the **repository root**.

### Required Structure

```markdown
# TODOIST — [Project Name]

> Generated: [ISO date]  
> Stack: [languages & frameworks]  
> Completion snapshot: [X% of surfaces assessed as ✅ Done]

---

## 🔴 P0 — Critical (do these first)

### [SHORT IMPERATIVE TITLE]
- **Why:** [one sentence — user or business consequence of not doing this]
- **What:** [concrete description of the deliverable]
- **How:** [key steps or approach; link to relevant file(s)]
- **Effort:** [rough estimate]
- **Source:** [InCode TODO | Architecture Gap | Competitive Opportunity | Spec]
- **Files:** [`path/to/file.ts`](path/to/file.ts) (if applicable)

[repeat for each P0 item]

---

## 🟠 P1 — High

[same template]

---

## 🟡 P2 — Medium

[same template]

---

## 🔵 P3 — Low / Backlog

[same template — can be collapsed to a simple bulleted list if > 8 items]

---

## 📊 Completion Snapshot

| Area | State | Notes |
|------|-------|-------|
| [module/surface] | ✅ / 🔧 / ❌ / 💡 | [short note] |

---

## 🌐 Competitive Insights Used

| Feature | Seen In | Why Recommended |
|---------|---------|-----------------|
| [feature] | [project] | [reason] |

---

_TODOIST.md is a living document. Re-run this skill after major milestones to refresh priorities._
```

### Content Rules

- **No secrets, credentials, or personal data** — never copy `.env` values, API keys, tokens, internal hostnames, or personal names into TODOIST.md
- **File paths are repo-relative** — use `src/routes/auth.ts`, never absolute paths like `/home/user/...`
- **Every item has a "Why"** — items without business or technical justification are cut
- **Use the project's own language** — if the codebase calls something "handlers", use that word, not "controllers"
- **Competitive items are clearly labelled** — never present a speculative feature as an existing gap
- **Avoid vague verbs** — "Improve X" is invalid. Use "Add rate-limiting middleware to `/api/auth` routes", "Extract `UserService` from `routes/user.ts`", etc.
- **Keep it scannable** — P0/P1 items get full template; P3 items may be brief bullets

---

## Phase 5 — Self-Check Before Delivering

Before writing the final file, verify:

- [ ] No absolute local paths (no `/home/`, `/Users/`, `/root/`)
- [ ] No secrets, tokens, passwords, or `.env` values
- [ ] No references to the local machine's username, hostname, or directory structure
- [ ] All file references are repo-relative and exist in the tracked codebase
- [ ] At least one item per non-empty priority tier
- [ ] Every P0 and P1 item has Impact ≥ 2 confirmed
- [ ] Competitive items are labelled and sourced
- [ ] TODOIST.md is written to the repo root (not a subdirectory, not an artifact directory)

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Listing generic "add tests" without scope | Scope to specific module: "Add unit tests for `AuthService.verifyToken()`" |
| Marking everything P0 | Apply the scoring matrix; 3–5 P0s is normal for most projects |
| Including placeholder text from templates | Scan for `[PROJECT NAME]`, `TODO: fill`, and remove before writing |
| Missing the completion snapshot | Always include the table — it's the fastest way to orient a new contributor |
| Copying raw grep output as-is | Synthesize and deduplicate; 40 TODOs may collapse to 6 themes |
| Exposing local file paths | All paths must be repo-relative |

---

## Quick Reference

```
Phase 1 → Discover (stack, architecture, completion state, inline TODOs)
Phase 2 → Research (comparable projects, proven features)
Phase 3 → Score (Impact × 2 + Effort + Risk → P0/P1/P2/P3)
Phase 4 → Write TODOIST.md (ranked, scoped, with why + how)
Phase 5 → Self-check (no secrets, no absolute paths, no vague items)
```

Deliver TODOIST.md. Tell the user what was found and how many items landed in each priority tier.
