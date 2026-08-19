# Spec Kit — Reusable SDD Workflow Catalog

> **Reusable public SDD workflow catalog** · Framework-, language-, runtime-, package-manager-, hosting-, database-, and AI-agent-agnostic
>
> **Rule:** Always inspect the target repository first. Never copy stack-specific paths, scripts, architecture, or deployment assumptions from this document.
>
> `/speckit.*` below is **logical Spec Kit command notation**. The installed agent integration determines the exact invocation surface.

## How to use this catalog

This is a reusable reference, not a project template. When creating a
project's `SPECKITINIT.md`, retain the core operating model and curate only
the command reference, pipelines, verification, and maintenance material that
the repository actually needs. Replace generic placeholders with verified
repository evidence; omit inapplicable sections rather than marking every
possibility as required.

Before executing a CLI command, use the installed CLI's `--help` and status
output to confirm its spelling, flags, and support. Examples in the CLI and
maintenance sections describe the intended operation, not a compatibility
guarantee for every Spec Kit version.

The catalog does not grant permission to mutate a repository, production
system, credentials, data, infrastructure, or external issue tracker. Keep
those actions behind the target project's normal approval process.

---

## 📚 Table of Contents

1. [Constitution — General Copy-Paste Prompt](#1-constitution--general-copy-paste-prompt)  
2. [Core SDD Workflow — The Golden Path](#2-core-sdd-workflow--the-golden-path)  
3. [Core Commands Reference](#3-core-commands-reference)  
4. [Pipeline 1 — Feature / Product Development](#4-pipeline-1--feature--product-development)  
5. [Pipeline 2 — Bug Fix & Regression Prevention](#5-pipeline-2--bug-fix--regression-prevention)  
6. [Pipeline 3 — Performance Optimization](#6-pipeline-3--performance-optimization)  
7. [Pipeline 4 — UI / UX Design Polishing](#7-pipeline-4--ui--ux-design-polishing)  
8. [Pipeline 5 — Security Hardening](#8-pipeline-5--security-hardening)  
9. [Pipeline 6 — SEO / AEO / GEO Discoverability](#9-pipeline-6--seo--aeo--geo-discoverability)  
10. [Pipeline 7 — Accessibility & Responsive Behavior](#10-pipeline-7--accessibility--responsive-behavior)  
11. [Pipeline 8 — Cleanup, De-slop & Dead Code](#11-pipeline-8--cleanup-de-slop--dead-code)  
12. [Pipeline 9 — Database / Persistence Changes](#12-pipeline-9--database--persistence-changes)  
13. [Pipeline 10 — Testing & Quality Gates](#13-pipeline-10--testing--quality-gates)  
14. [Pipeline 11 — Deployment & Release Safety](#14-pipeline-11--deployment--release-safety)  
15. [Pipeline 12 — Observability, Logging & Privacy](#15-pipeline-12--observability-logging--privacy)  
16. [Pipeline 13 — Architecture Modernization & Refactoring](#16-pipeline-13--architecture-modernization--refactoring)  
17. [Pipeline 14 — Dependency & Runtime Upgrades](#17-pipeline-14--dependency--runtime-upgrades)  
18. [CLI Workflow Automation](#18-cli-workflow-automation)  
19. [Quick-Reference Cheat Sheet](#19-quick-reference-cheat-sheet)  
20. [Update & Self-Maintenance](#20-update--self-maintenance)  
21. [Verification Matrix](#21-verification-matrix)  
22. [Safety & Operating Rules](#22-safety--operating-rules)

---

# 1. Constitution — General Copy-Paste Prompt

> 🏛️ **Use this once when establishing governance, then amend it deliberately as the project evolves.**

```text
/speckit.constitution

Create or update the project constitution using ONLY verified evidence from this repository.

First inspect repository guidance, architecture documentation, language/framework/runtime configuration, package manager, build system, test/lint/typecheck setup, database or persistence contracts, authentication/authorization, security/privacy rules, deployment/CI configuration, accessibility requirements, and existing design-system rules.

Create durable project principles for:

1. Architecture & Boundaries
   Define the actual module/package/service/route/component boundaries discovered in the repository. Preserve dependency direction and runtime boundaries.

2. Security & Privacy
   Require appropriate authentication/authorization, least privilege, safe input/output handling, secure secret management, and privacy-preserving logging.

3. Data & Persistence
   Identify the repository's real source of truth for schema and persistence changes. Require compatibility analysis, safe migrations, and recovery planning.

4. Quality & Verification
   Define the repository's actual lint, type/static analysis, test, build, and release gates. Do not invent commands.

5. Dependency & Runtime Discipline
   Require evidence-backed dependency/runtime changes, official compatibility checks, and focused upgrade scope.

6. Accessibility & User Experience
   Preserve applicable accessibility, semantic HTML, responsive behavior, interaction quality, and established design-system conventions.

7. Maintainability & Operations
   Require measurable acceptance criteria, reviewable changes, durable documentation for architectural decisions, and safe operational practices.

Use MUST / MUST NOT / SHOULD language.
Use semantic versioning for constitution revisions.
Include the ISO ratification date.
Define an amendment process with documented rationale and a version bump.

Do NOT implement application code.
Do NOT invent technologies, paths, commands, or project rules.
Do NOT turn temporary implementation details into constitutional principles.
```

> ✅ **Important:** This prompt is intentionally stack-neutral. The agent must derive the actual rules from the repository instead of guessing them.

---

# 2. Core SDD Workflow — The Golden Path

> 🎯 **Default flow for features, fixes, refactors, optimizations, audits, and modernization work.**

```text
/speckit.constitution   → governance
/speckit.specify        → WHAT + WHY
/speckit.clarify        → resolve meaningful ambiguity (optional)
/speckit.plan           → HOW
/speckit.checklist      → quality/compliance gates (optional)
/speckit.tasks          → ordered implementation tasks
/speckit.analyze        → cross-artifact consistency (recommended for complex work)
/speckit.implement      → implementation
/speckit.converge       → gap/remaining-work assessment
VERIFY PROJECT GATES    → repository-specific validation
/speckit.taskstoissues   → external issue export (optional)
```

> 🧭 **Agent note:** `/speckit.*` is logical notation. Use the syntax exposed by the installed integration.

---

# 3. Core Commands Reference

| Command | Purpose | Input |
|---|---|---|
| `/speckit.constitution` | Governance | Verified durable project rules |
| `/speckit.specify` | Requirements | Goal, scope, behavior, acceptance criteria |
| `/speckit.clarify` | Ambiguity | Existing specification |
| `/speckit.plan` | Technical design | Specification + repository evidence |
| `/speckit.checklist` | Quality gates | Focused risk/compliance criteria |
| `/speckit.tasks` | Task breakdown | Approved plan |
| `/speckit.analyze` | Consistency | Constitution + spec + plan + tasks |
| `/speckit.implement` | Coding | Approved tasks |
| `/speckit.converge` | Gap analysis | Artifacts + implementation |
| `/speckit.taskstoissues` | Issue export | Tasks |

### 📌 Copy-paste command pattern

```text
/speckit.specify <describe the desired outcome, scope, constraints, and acceptance criteria>
/speckit.clarify
/speckit.plan <describe any verified repository constraints that matter>
/speckit.checklist <list the focused quality/security/release gates>
/speckit.tasks
/speckit.analyze
/speckit.implement
/speckit.converge
```

> ⚠️ Never paste project-specific commands, file paths, framework names, database names, or deployment commands from an example unless they exist in the target repository.

---

# 4. Pipeline 1 — Feature / Product Development

> 🚀 **Goal:** Build a new feature with explicit requirements, technical planning, dependency-ordered implementation, and verification.

### Copy-paste command sequence

```text
/speckit.constitution Review the repository and update the constitution only if durable project governance is missing or materially outdated. Derive rules from actual evidence and do not implement application code.
```

```text
/speckit.specify Build <feature-name>; define the user problem, desired behavior, scope, non-goals, constraints, acceptance criteria, affected capabilities, and required verification. Inspect the repository first and do not assume any framework, path, command, or service.
```

```text
/speckit.clarify Review the specification and resolve only materially ambiguous requirements, edge cases, compatibility decisions, or acceptance criteria that cannot be established from repository evidence.
```

```text
/speckit.plan Create the implementation plan for <feature-name> using the repository's actual architecture, runtime, dependencies, data boundaries, interfaces, and quality gates. Identify exact files/modules only after inspecting them.
```

```text
/speckit.checklist Create a focused verification checklist for <feature-name> covering functional behavior, regression risk, security, accessibility, performance, compatibility, and repository-specific quality gates that actually apply.
```

```text
/speckit.tasks Break the approved <feature-name> plan into dependency-ordered implementation tasks with clear completion criteria and verification steps. Keep unrelated refactors out of scope.
```

```text
/speckit.analyze Analyze the constitution, specification, plan, checklist, and tasks for contradictions, unsupported assumptions, architectural conflicts, missing requirements, and missing verification.
```

```text
/speckit.implement Implement the approved tasks for <feature-name> in dependency order. Preserve repository conventions, verify meaningful changes, and do not introduce unrelated changes.
```

```text
/speckit.converge Compare the implementation against the specification, plan, checklist, and tasks. Verify acceptance criteria, identify incomplete or risky work, and append only justified remaining work.
```

> ⛔ **Stop when:** requirements remain materially ambiguous, the plan contradicts repository guidance, required credentials/dependencies are unavailable, or implementation would require an unapproved destructive operation.
# 5. Pipeline 2 — Bug Fix & Regression Prevention

> 🛠️ **Goal:** Reproduce, specify, fix, and prevent a defect without unnecessarily changing unrelated behavior.

### Copy-paste command sequence

```text
/speckit.specify Fix <bug-description>; define expected behavior, observed incorrect behavior, reproduction evidence, root-cause boundaries, scope, non-goals, compatibility constraints, and regression criteria. Inspect the repository before making assumptions.
```

```text
/speckit.clarify Resolve only remaining ambiguity around reproduction, expected behavior, edge cases, failure handling, compatibility, or regression expectations for <bug-description>.
```

```text
/speckit.plan Create a minimal root-cause-driven fix plan for <bug-description>. Identify the narrowest safe change, required regression coverage, and actual project verification commands. Avoid unrelated refactoring.
```

```text
/speckit.tasks Break the bug-fix plan into small dependency-ordered tasks covering reproduction, fix, regression test or alternate verification, and final quality gates.
```

```text
/speckit.implement Implement the approved bug fix and regression coverage. Validate the original reproduction before and after the change, preserve unrelated behavior, and run the repository's applicable quality gates.
```

```text
/speckit.converge Verify that <bug-description> is fixed, the regression is prevented, acceptance criteria are satisfied, and no unjustified scope was introduced. Record residual risk.
```

> ✅ Prefer a regression test or another concrete repeatable verification mechanism; document why it is omitted when infeasible.
# 6. Pipeline 3 — Performance Optimization

> ⚡ **Goal:** Improve measurable performance without trading away correctness, maintainability, accessibility, or security.

### Copy-paste command sequence

```text
/speckit.specify Optimize performance for <target>; inspect the actual runtime, build system, deployment environment, performance tooling, critical paths, and existing benchmarks. Establish a reproducible baseline, define a justified measurable target, identify non-goals, and require before/after evidence. Do not assume a framework or platform.
```

```text
/speckit.plan Create a performance optimization plan for <target> based on measured evidence. Identify dominant bottlenecks, optimization hypotheses, affected components/modules, measurement tools, trade-offs, and rollback strategy. Prefer small changes that can prove the hypothesis.
```

```text
/speckit.checklist Create a performance verification checklist covering baseline capture, before/after measurements, correctness, regression detection, memory/CPU impact, user-facing latency where applicable, and repository-specific quality gates.
```

```text
/speckit.tasks Break the performance plan into measurement, implementation, and verification tasks. Every optimization task must state how success will be measured.
```

```text
/speckit.analyze Check that every proposed optimization is supported by the baseline, does not invent targets, respects architecture/correctness constraints, and has measurable verification.
```

```text
/speckit.implement Implement the approved performance changes only. Capture before/after measurements with the repository's actual tooling and revert changes that fail their justified performance target.
```

```text
/speckit.converge Compare measured results with the acceptance criteria. Confirm real improvement, identify regressions or trade-offs, and append only evidence-backed remaining work.
```
# 7. Pipeline 4 — UI / UX Design Polishing

> 🎨 **Goal:** Improve usability, visual hierarchy, interaction quality, responsive behavior, and design consistency without assuming a frontend framework.

### Copy-paste command sequence

```text
/speckit.specify Improve the UI/UX for <scope>; inspect the actual UI technology, design system, component architecture, responsive strategy, supported browsers/devices, and accessibility expectations. Define user goals, information hierarchy, interaction states, visual consistency, responsive behavior, and non-goals.
```

```text
/speckit.clarify Resolve only meaningful ambiguity around <scope>, including target users, responsive behavior, design-system constraints, interaction states, browser support, and accessibility expectations.
```

```text
/speckit.plan Create the UI/UX implementation plan using the repository's actual component architecture, styling system, routes/layouts, assets, and test tooling. Reuse existing design primitives before introducing new ones.
```

```text
/speckit.checklist Create a UI/UX quality checklist covering responsive states, keyboard/focus behavior, loading/empty/error states, semantic structure, accessibility, visual consistency, and visual regression/manual review.
```

```text
/speckit.tasks Break the UI/UX plan into focused implementation and verification tasks. Keep unrelated visual or architectural changes out of scope.
```

```text
/speckit.implement Implement the approved UI/UX changes for <scope>. Preserve established product identity and design-system conventions, support responsive states, and verify keyboard/accessibility behavior while editing.
```

```text
/speckit.converge Review the completed UI/UX work against the specification and checklist. Verify user flows, responsive layouts, interaction states, accessibility, and visual consistency; record remaining issues and known limitations.
```
# 8. Pipeline 5 — Security Hardening

> 🛡️ **Goal:** Reduce realistic security risk while preserving intended product behavior.

### Copy-paste command sequence

```text
/speckit.specify Harden security for <scope>; inspect authentication, authorization, trust boundaries, secrets handling, input/output flows, storage, network boundaries, dependencies, logging, and deployment context. Define threats, protected assets, abuse cases, security requirements, non-goals, and regression criteria.
```

```text
/speckit.clarify Resolve only material security ambiguity for <scope>, including trust boundaries, authorization rules, threat assumptions, failure behavior, migration impact, or privacy requirements.
```

```text
/speckit.plan Create a security hardening plan grounded in repository evidence and applicable official security guidance. Identify attack surfaces, controls, affected components, tests, rollout considerations, and residual risks. Do not invent controls.
```

```text
/speckit.checklist Create a security verification checklist covering authentication, authorization, input validation, output handling, secrets, dependency risk, logging/privacy, least privilege, abuse resistance, regression tests, and relevant deployment configuration.
```

```text
/speckit.tasks Break the security plan into dependency-ordered audit, implementation, regression-test, and verification tasks. Separate low-risk fixes from changes requiring explicit review or migration.
```

```text
/speckit.analyze Analyze the security artifacts for missing threat coverage, contradictory controls, unsupported assumptions, excessive scope, and unverified claims.
```

```text
/speckit.implement Implement only the approved security changes. Preserve compatibility, avoid exposing secrets in logs/output, and run the repository's applicable security and quality checks.
```

```text
/speckit.converge Verify controls against the defined threats and acceptance criteria. Record residual risks and any assumptions that could not be verified.
```

> ⚠️ Never claim absolute security.
# 9. Pipeline 6 — SEO / AEO / GEO Discoverability

> 🔎 **Goal:** Improve observable technical discoverability and content structure without promising rankings or AI citation outcomes.

### Copy-paste command sequence

```text
/speckit.specify Improve technical SEO, answer-engine discoverability, and generative-search readability for <scope>; inspect routing, rendering, content architecture, metadata, canonical controls, robots directives, sitemap generation, structured data, internal linking, semantic HTML, and indexability. Require only observable, testable improvements.
```

```text
/speckit.plan Create a discoverability implementation plan using the repository's actual rendering model, URL structure, content system, metadata implementation, structured-data implementation, and deployment constraints. Identify effects on canonical URLs, crawlability, internal links, and visible content.
```

```text
/speckit.checklist Create an SEO/AEO/GEO verification checklist covering canonical correctness, noindex/index behavior, metadata accuracy, sitemap/robots behavior, structured data matching visible content, internal-link integrity, semantic HTML, accessibility, and duplicate-content risks.
```

```text
/speckit.tasks Break the discoverability plan into small implementation and verification tasks. Each task must identify the user-visible or machine-observable outcome it improves.
```

```text
/speckit.implement Implement the approved discoverability changes. Preserve content semantics, ensure structured data matches visible content, and verify generated metadata, robots, sitemaps, canonicals, and links using repository-supported tooling.
```

```text
/speckit.converge Verify that the final implementation satisfies the discoverability specification without unsupported SEO promises. Check canonical/noindex behavior, visible answer-first copy, schema consistency, internal links, crawlability, and residual indexing risks.
```

> 🚫 Never promise rankings, indexing, AI citation, traffic, featured snippets, or crawler behavior.
# 10. Pipeline 7 — Accessibility & Responsive Behavior

> ♿ **Goal:** Improve accessibility and reliable behavior across supported devices, browsers, input methods, and assistive technologies.

### Copy-paste command sequence

```text
/speckit.specify Improve accessibility and responsive behavior for <scope>; inspect the actual UI stack, semantic structure, accessibility rules, supported devices/browsers, and current responsive strategy. Define user and assistive-technology outcomes plus acceptance criteria.
```

```text
/speckit.plan Create an accessibility/responsive implementation plan using the repository's actual UI architecture, styling system, components, forms, overlays, and test tooling. Apply relevant WCAG and platform guidance.
```

```text
/speckit.checklist Create an accessibility checklist covering semantic structure, accessible names, keyboard navigation, focus order/visibility, forms, dialogs, contrast, reduced motion, zoom/reflow, touch usability, responsive layouts, and screen-reader behavior where applicable.
```

```text
/speckit.tasks Break the plan into focused implementation and verification tasks. Include automated checks where available and manual checks where automation cannot establish the requirement.
```

```text
/speckit.implement Implement the approved accessibility and responsive changes. Preserve existing behavior, avoid decorative ARIA, and validate interaction states under supported keyboard and viewport/device conditions.
```

```text
/speckit.converge Compare the implementation against the accessibility specification and checklist. Confirm responsive and keyboard behavior, record evidence, and identify residual accessibility issues.
```
# 11. Pipeline 8 — Cleanup, De-slop & Dead Code

> 🧹 **Goal:** Remove obsolete or redundant code safely without turning static guesses into destructive deletions.

### Copy-paste command sequence

```text
/speckit.specify Clean up <scope> conservatively; identify dead code, unused exports/files, stale dependencies, duplicated abstractions, redundant wrappers, stale configuration, generated junk, misleading comments, placeholder implementations, and AI-generated boilerplate that adds no behavior. Define deletion criteria and non-goals.
```

```text
/speckit.plan Create a cleanup plan based on repository evidence. Before deletion, inspect static references, dynamic loading, reflection/code generation, build inputs, framework conventions, tests, public APIs, and runtime behavior. Prefer small reversible batches.
```

```text
/speckit.checklist Create a cleanup safety checklist covering reference analysis, public API preservation, build/runtime verification, tests, dependency consistency, generated-file handling, and rollback/review points.
```

```text
/speckit.tasks Break the cleanup plan into small reviewable batches. Every deletion task must state the evidence supporting removal and the verification proving nothing required was lost.
```

```text
/speckit.analyze Check the cleanup artifacts for unjustified deletions, hidden runtime references, unnecessary refactors, public API breaks, and unrelated scope expansion.
```

```text
/speckit.implement Apply the approved cleanup in small batches. Verify each batch using the repository's actual static checks, tests, build, and runtime checks before continuing.
```

```text
/speckit.converge Confirm that cleanup reduced unnecessary complexity without behavior regressions, broken imports, missing runtime assets, or accidental API removal.
```
# 12. Pipeline 9 — Database / Persistence Changes

> 🗄️ **Goal:** Safely evolve schemas, queries, models, storage contracts, or persistence behavior.

### Copy-paste command sequence

```text
/speckit.specify Change persistence for <goal>; inspect the actual storage engine, schema source of truth, ORM/query layer, migration mechanism, transactions, compatibility constraints, backup/recovery, test database process, and deployment sequencing. Define data-model changes, migration behavior, rollback, and acceptance criteria.
```

```text
/speckit.clarify Resolve ambiguity around data ownership, compatibility, defaults/nullability, backfills, migration ordering, rollback/recovery, concurrent access, or production rollout for <goal>.
```

```text
/speckit.plan Create the persistence implementation plan using actual repository migration/schema conventions. Identify schema/query/model changes, data transformations, compatibility windows, verification tests/queries, and production sequencing.
```

```text
/speckit.checklist Create a database-change checklist covering schema correctness, migration safety, data integrity, permissions, performance, backward compatibility, test coverage, rollback/recovery, and production safeguards.
```

```text
/speckit.tasks Break the persistence plan into dependency-ordered schema, migration, data, application, test, and verification tasks. Separate destructive operations and production steps clearly.
```

```text
/speckit.analyze Analyze the artifacts for migration-order issues, incompatible application/schema states, data-loss risks, missing rollback/recovery, and absent verification.
```

```text
/speckit.implement Implement the approved persistence changes and migrations according to repository policy. Do not rewrite applied migrations unless explicitly permitted and do not execute destructive production operations automatically.
```

```text
/speckit.converge Verify schema, data behavior, application compatibility, migrations, tests, and recovery assumptions. Record unverified production-only conditions before completion.
```
# 13. Pipeline 10 — Testing & Quality Gates

> 🧪 **Goal:** Establish reliable verification using the repository's real test and quality tooling.

### Copy-paste command sequence

```text
/speckit.specify Improve testing and quality gates for <scope>; inspect actual unit/integration/e2e tests, fixtures, mocks, static analysis, formatting, linting, type checking, build, CI, release checks, and coverage gaps. Define behavior to protect and measurable verification criteria.
```

```text
/speckit.plan Create the testing/quality plan using only tools and commands that actually exist in the repository. Map changed behavior to the appropriate test layer and identify CI/release gates that need adjustment.
```

```text
/speckit.checklist Create a quality-gates checklist covering regression tests, static analysis, formatting, build validity, integration boundaries, end-to-end flows, and CI/release requirements that actually apply.
```

```text
/speckit.tasks Break the quality plan into implementation, test, fixture, tooling, and verification tasks. Every new gate must map to an executable repository command or documented manual check.
```

```text
/speckit.implement Implement the approved tests and quality-gate changes. Keep tests deterministic, preserve existing conventions, and avoid adding tooling without a demonstrated need.
```

```text
/speckit.converge Verify that changed behavior is covered, quality gates execute successfully, and no gate falsely reports success while excluding relevant code. Record skipped or unavailable checks.
```

> 🧭 Prefer the repository's own CI ordering over a universal order; do not invent commands such as `npm test`.
# 14. Pipeline 11 — Deployment & Release Safety

> 🚢 **Goal:** Make releases predictable, reversible, and appropriately gated.

### Copy-paste command sequence

```text
/speckit.specify Improve release safety for <target-environment>; inspect actual CI/CD configuration, hosting, deployment tooling, environment variables, secrets management, health checks, migration dependencies, rollout strategy, smoke tests, approvals, and rollback mechanisms. Separate local, preview/staging, and production behavior.
```

```text
/speckit.clarify Resolve only material deployment ambiguity, including approval points, migration ordering, environment differences, rollback limits, health checks, or post-deployment responsibilities for <target-environment>.
```

```text
/speckit.plan Create a release-safety plan using the repository's real deployment architecture and commands. Define preflight checks, artifact validation, rollout sequence, smoke tests, monitoring, rollback/recovery, and explicit production side effects.
```

```text
/speckit.checklist Create a deployment checklist covering configuration, secrets, migrations, build artifacts, health checks, smoke tests, observability, approvals, rollback readiness, and post-deploy verification.
```

```text
/speckit.tasks Break the release-safety plan into local validation, preview/staging, production, post-deploy, and rollback tasks. Mark every external or production-affecting step clearly.
```

```text
/speckit.implement Implement only the approved deployment-safety changes. Do not deploy production, mutate infrastructure, or execute production migrations unless explicitly authorized by repository workflow and the current task.
```

```text
/speckit.converge Verify release readiness against actual configuration and quality gates. Confirm rollback/recovery and post-deployment checks are feasible, and record environment-specific unknowns.
```
# 15. Pipeline 12 — Observability, Logging & Privacy

> 📡 **Goal:** Improve diagnostics while reducing sensitive-data leakage and noisy telemetry.

### Copy-paste command sequence

```text
/speckit.specify Improve observability and privacy for <scope>; inspect actual logs, traces, metrics, error reporting, telemetry providers, retention, environment configuration, sensitive data flows, and privacy requirements. Define useful diagnostics while minimizing exposure of secrets and personal data.
```

```text
/speckit.plan Create an observability plan using the existing logging/telemetry architecture. Identify diagnostic context, severity levels, redaction rules, correlation/trace behavior, environment-specific verbosity, retention considerations, and verification methods.
```

```text
/speckit.checklist Create a telemetry/privacy checklist covering secret/token/password redaction, PII minimization, structured context, error visibility, environment configuration, retention, and tests for sensitive-data leakage.
```

```text
/speckit.tasks Break the observability plan into focused logging, telemetry, redaction, testing, and verification tasks. Do not introduce a new telemetry provider unless the approved specification requires it.
```

```text
/speckit.implement Implement the approved observability changes. Preserve useful diagnostics, remove sensitive data from emitted logs, and validate redaction and environment-specific behavior.
```

```text
/speckit.converge Verify diagnostics remain useful while sensitive data is protected, and confirm logging/telemetry behavior matches repository policy across relevant environments.
```
# 16. Pipeline 13 — Architecture Modernization & Refactoring

> 🏗️ **Goal:** Improve structure without turning refactoring into an uncontrolled rewrite.

### Copy-paste command sequence

```text
/speckit.specify Modernize or refactor <architectural-scope>; map the current architecture from repository evidence, including modules/packages/services/routes/components, dependency direction, runtime boundaries, data ownership, public interfaces, integration points, and test boundaries. Define invariants, outcomes, and non-goals.
```

```text
/speckit.clarify Resolve ambiguity around architectural boundaries, compatibility, migration sequencing, public APIs, runtime constraints, and acceptable temporary states for <architectural-scope>.
```

```text
/speckit.plan Create an incremental refactoring plan. Prefer reversible migration steps, preserve behavior unless explicitly changed, define dependency direction, identify compatibility seams, and specify how each step will be verified.
```

```text
/speckit.checklist Create an architecture-refactoring checklist covering behavior preservation, dependency direction, API compatibility, runtime boundaries, data ownership, tests, build integrity, rollback points, and documentation updates.
```

```text
/speckit.tasks Break the refactor into small dependency-ordered migration steps. Avoid a big-bang rewrite and identify temporary compatibility layers that can later be removed.
```

```text
/speckit.analyze Analyze the proposed architecture against the current repository for circular dependencies, hidden coupling, incompatible interfaces, missing migration steps, and scope that would become an uncontrolled rewrite.
```

```text
/speckit.implement Implement the refactor incrementally. Preserve externally observable behavior unless changed by specification, run targeted verification after each migration step, and avoid unrelated cleanup.
```

```text
/speckit.converge Verify the final architecture against defined invariants, behavior, dependency direction, compatibility requirements, and the removal plan for temporary migration structures.
```
# 17. Pipeline 14 — Dependency & Runtime Upgrades

> ⬆️ **Goal:** Upgrade runtimes, frameworks, libraries, package managers, or build tooling with evidence-backed compatibility checks.

### Copy-paste command sequence

```text
/speckit.specify Upgrade <dependency-or-runtime>; determine the current version from repository configuration and lockfiles, define the target version, scope, reason, compatibility requirements, non-goals, and acceptance criteria. Do not upgrade unrelated dependencies merely because they are outdated.
```

```text
/speckit.clarify Resolve only material ambiguity around target versions, supported runtimes, breaking changes, peer constraints, deployment compatibility, lockfile policy, and rollback strategy for <dependency-or-runtime>.
```

```text
/speckit.plan Create an upgrade plan using official release notes/migration guidance and repository evidence. Identify breaking changes, deprecated APIs, peer/runtime constraints, lockfile effects, CI compatibility, deployment compatibility, test impact, and rollback steps.
```

```text
/speckit.checklist Create an upgrade checklist covering compatibility, deprecated APIs, tests, static analysis, build, CI, deployment, lockfile integrity, security advisories, and rollback readiness.
```

```text
/speckit.tasks Break the upgrade into dependency, code migration, test, verification, and documentation tasks. Keep unrelated upgrades out of scope unless required for compatibility.
```

```text
/speckit.analyze Analyze the upgrade plan for unverified breaking changes, dependency conflicts, unsupported runtime assumptions, missing migration steps, and unnecessary scope expansion.
```

```text
/speckit.implement Implement the approved upgrade and only the required compatibility changes. Run focused verification frequently and preserve lockfile integrity and repository dependency policy.
```

```text
/speckit.converge Verify runtime/dependency versions, migrated APIs, tests, static checks, build, CI compatibility, and deployment assumptions. Record residual compatibility risk before completion.
```
# 18. CLI Workflow Automation

Current Spec Kit supports installable, resumable workflow pipelines in addition
to individual `/speckit.*` commands. Workflows can chain commands, shell steps,
prompts, conditions, loops, fan-out/fan-in, and human approval gates. [Spec Kit Workflows reference](https://github.com/github/spec-kit/blob/main/docs/reference/workflows.md)

## Discover workflows

```bash
specify workflow search
specify workflow info <workflow-id>
```

## Install a workflow

```bash
specify workflow add <source>
```

Examples may use a catalog ID, URL, or local directory/file according to the
installed workflow system. Review workflow source before installation.

## Run a workflow

```bash
specify workflow run <workflow-source>
```

With inputs:

```bash
specify workflow run <workflow-source> \
  --input key=value
```

Multiple inputs:

```bash
specify workflow run <workflow-source> \
  --input key=value \
  --input another=value
```

Machine-readable result:

```bash
specify workflow run <workflow-source> --json
```

## Check workflow status

```bash
specify workflow status
specify workflow status <run-id>
specify workflow status <run-id> --json
```

## Resume a paused/failed workflow

```bash
specify workflow resume <run-id>
```

Optional updated input:

```bash
specify workflow resume <run-id> --input key=value
```

## Update workflows

```bash
specify workflow update
specify workflow update <workflow-id>
```

## Enable / disable / remove

```bash
specify workflow enable <workflow-id>
specify workflow disable <workflow-id>
specify workflow remove <workflow-id>
```

## Workflow safety

A workflow `shell` step runs with the user's local privileges. Spec Kit's
workflow `requires` metadata is not a security sandbox. Review downloaded or
community workflow source and require human gates before sensitive/destructive
operations. [Spec Kit Workflows reference](https://github.com/github/spec-kit/blob/main/docs/reference/workflows.md)

---

# 19. Quick-Reference Cheat Sheet

## First-time initialization

```bash
uv tool install specify-cli
specify version
specify integration list
specify init --here --integration <integration-key>
specify integration status
```

## Daily health

```bash
specify version
specify self check
specify integration status
```

## Standard SDD cycle

```text
/speckit.specify
/speckit.clarify       # when needed
/speckit.plan
/speckit.checklist     # when needed
/speckit.tasks
/speckit.analyze       # when useful
/speckit.implement
/speckit.converge
```

## Upgrade the CLI

```bash
specify self check
specify self upgrade --dry-run
specify self upgrade
```

## Upgrade installed project integrations

```bash
specify integration status
specify integration upgrade <integration-key>
specify extension update
```

The manifest-aware path is preferred because it detects modified managed files
and protects user changes unless forced. [Spec Kit Upgrade Guide](https://github.com/github/spec-kit/blob/main/docs/upgrade.md) and [Spec Kit Integrations reference](https://github.com/github/spec-kit/blob/main/docs/reference/integrations.md)

## Switch active integration

```bash
specify integration list
specify integration use <integration-key>
```

Use `switch` only when appropriate to the installed CLI semantics. Current Spec
Kit distinguishes `use`/`switch` from `upgrade`; `use` changes the default and
refreshes integration-layer artifacts according to the active configuration.
[Spec Kit Integrations reference](https://github.com/github/spec-kit/blob/main/docs/reference/integrations.md)

---

# 20. Update & Self-Maintenance

## CLI freshness

```bash
specify self check
```

This is read-only.

## Preview the CLI upgrade

```bash
specify self upgrade --dry-run
```

## Apply the CLI upgrade

```bash
specify self upgrade
```

## Refresh project integration

```bash
specify integration status
specify integration upgrade <integration-key>
```

If locally modified managed files are detected, inspect the diff before using
`--force`.

## Refresh extensions

```bash
specify extension update
```

## Update workflows

```bash
specify workflow update
```

## Safe maintenance order

```text
1. Check CLI freshness
2. Review repository status
3. Upgrade CLI if desired
4. Inspect integration status
5. Upgrade installed integrations
6. Update extensions
7. Update installed workflows where appropriate
8. Review generated diff
9. Run repository quality gates
10. Confirm agent/IDE reload requirements
```

Spec Kit keeps CLI upgrades separate from project-file integration upgrades and
extension updates. [Spec Kit Upgrade Guide](https://github.com/github/spec-kit/blob/main/docs/upgrade.md)

---

# 21. Verification Matrix

| Area | What to verify | Exact command / evidence | Status |
|---|---|---|---|
| CLI | Installed version | `specify version` | ☐ |
| CLI health | Tool is operational | `specify self check` | ☐ |
| Integrations | Installed/default state | `specify integration status` | ☐ |
| Integration artifacts | Correct generated commands/skills | Filesystem + integration status | ☐ |
| Constitution | Project-derived principles | `.specify/memory/constitution.md` + diff | ☐ |
| Feature artifacts | Spec/plan/tasks consistency | `/speckit.analyze` | ☐ |
| Implementation | Tasks executed | `/speckit.implement` output + diff | ☐ |
| Convergence | Remaining work assessed | `/speckit.converge` | ☐ |
| Tests | Actual repository test gates | Detected project command(s) | ☐ |
| Static quality | Lint/type/static checks | Detected project command(s) | ☐ |
| Build | Production/build artifact validity | Detected project command | ☐ |
| Deployment | Release readiness | Detected project command/checks | ☐ |
| Documentation | Commands/paths remain accurate | Manual review | ☐ |
| Update automation | Advisory/non-blocking behavior | Safe checker invocation | ☐ |
| Workflow automation | Correct run state/gates | `specify workflow status` | ☐ |

Do not replace the final column with a checkmark until evidence exists.

Recommended status values:

```text
VERIFIED
VERIFIED WITH WARNING
NOT VERIFIED
SKIPPED
BLOCKED
NOT APPLICABLE
```

---

# 22. Safety & Operating Rules

## Never blindly overwrite Spec Kit files

For existing projects:

```bash
git status
specify integration status
```

Inspect modified managed files before using `--force`.

## Never silently mutate production

Do not automatically:

```text
run destructive database migrations
deploy production
rotate secrets
delete user data
remove infrastructure
create external issues
push commits
change production configuration
```

## Never invent repository commands

The repository determines:

```text
install command
build command
test command
lint command
typecheck command
format command
migration command
deploy command
```

## Never turn absence of evidence into permission

If something is unknown:

```text
UNKNOWN
```

not:

```text
assume safe
```

## Keep scope narrow

A performance task should not silently become a UI redesign.

A security task should not silently become an architecture rewrite.

A cleanup task should not silently remove public APIs.

A database task should not silently modify deployment behavior.

## Prefer reversible changes

Use:

```text
small commits
small migration steps
feature flags where appropriate
backups/recovery points
review checkpoints
before/after measurements
```

## Final completion standard

Never claim:

```text
perfect
flawless
completely secure
fully optimized
guaranteed SEO
guaranteed AI visibility
```

Instead report concrete evidence:

```text
implemented
verified
skipped
blocked
warning
residual risk
```

---

# Appendix A — Recommended Minimal Universal Pipeline

When the change is small but still benefits from SDD:

```text
/speckit.specify
/speckit.plan
/speckit.tasks
/speckit.implement
/speckit.converge
```

Use the longer path when ambiguity, quality risk, architectural impact, or
cross-system complexity justifies it.

---

# Appendix B — Recommended Full Pipeline

For high-risk or cross-cutting work:

```text
/speckit.constitution
/speckit.specify
/speckit.clarify
/speckit.plan
/speckit.checklist
/speckit.tasks
/speckit.analyze
/speckit.implement
/speckit.converge
/speckit.taskstoissues
```

`taskstoissues` is optional and should only be included when external issue
tracking is explicitly part of the workflow.

---

# Appendix C — Framework-Independence Contract

This document is considered framework-independent only if all of the following
remain true:

- no pipeline requires a particular programming language;
- no pipeline requires a particular frontend/backend framework;
- no pipeline assumes a specific package manager;
- no pipeline assumes a particular hosting provider;
- no pipeline assumes a specific database;
- repository-specific paths are discovered rather than guessed;
- project-specific quality gates are discovered before being documented;
- AI-agent command syntax is derived from the installed integration;
- Spec Kit CLI commands are validated against the installed CLI/docs;
- destructive actions remain explicit and reviewable;
- repeated execution converges rather than producing duplicate configuration;
- uncertain facts are recorded as unknown rather than invented.

---

*Master workflow catalog. Keep project-specific observations in the project's
own `SPECKITINIT.md`; keep this document reusable and framework/agent agnostic.*
