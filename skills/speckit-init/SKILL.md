---
name: speckit-init
description: >
  Use when the user asks to install, initialize, integrate, upgrade, or
  document GitHub Spec Kit. Covers SPECKITINIT.md creation, constitution
  setup, OpenCode /speckit.* workflows, and update-check automation.
  Do NOT use for implementing application features — that is speckit.implement.
---

# Spec Kit Initialization and Workflow Authoring

Create a truthful, codebase-specific Spec Kit setup — never a generic template.
This skill is framework-agnostic but framework-aware: detect the repository's
actual stack first, then adapt every command, path, gate, and deployment
instruction to it.

**Boundary:** This skill owns installation, configuration, constitution, and
guide authoring. Application implementation (running tasks, writing code from
specs) belongs to `speckit.implement` or the equivalent agent command.

## 1. Discovery

Before editing anything, gather these facts:

### 1a. Repository context

Read (do not skim) the repo's guidance files:

- `AGENTS.md`, `CONTRIBUTING.md`, `README.md`
- Architecture, auth, database, deployment docs as relevant

Identify: language, framework, runtime, package manager, build system,
test commands, source layout, persistence, auth, security contracts,
CI checks, deployment target, supported platforms.

### 1b. Existing Spec Kit state

Inspect `.specify/`, `.opencode/`, `specs/`, `SPECKITINIT.md`, and any
update scripts. Never overwrite user changes without understanding them.

### 1c. CLI health

```bash
specify --version
specify self check
specify integration list
specify integration status
specify integration status --json   # machine-readable when available
```

If `specify` is absent, install via the official method:

```bash
uv tool install specify-cli
```

Record the observed version — do not treat it as a permanent pin.

**Failure paths:**
- If `uv` is missing, tell the user and offer alternative install methods from the official repo.
- If `specify self check` fails (network, corrupt install), report the error and stop — do not proceed with a broken CLI.
- If the repo has no `.specify/` and the user hasn't asked for one, ask before creating it.

## 2. Agent integration detection

Use the CLI's own output as the source of truth:

```bash
specify integration list
specify integration status
specify integration status --json
```

Enumerate the **actual generated** commands/skills from the manifest and
status report. Do not use a hard-coded command list — command sets evolve
between Spec Kit versions.

For OpenCode: inspect `.opencode/commands/`, `.opencode/skills/`,
`.opencode/plugins/` as applicable.

For other integrations (Claude, Codex, Cline, Kilo, Copilot, etc.): use
that integration's documented directory and invocation format.

Document both the Spec Kit concept name and the detected agent-specific
invocation syntax (e.g., `/speckit.plan` for OpenCode, `/speckit-plan`
for Claude). Never present one agent's syntax as universal.

## 3. Constitution

Create a copy-paste first-run prompt in `SPECKITINIT.md`. It must encode
only verified project rules:

- Runtime boundaries and architecture
- Data and auth contracts
- Security and privacy prohibitions
- Test and build gates
- Deployment constraints
- Design and accessibility standards

It must **not** authorize constitution work to implement application code.

If `.specify/memory/constitution.md` is still the stock placeholder,
replace it with a concrete constitution derived from repository docs.
Use ISO dates, semantic versioning, declarative MUST/SHOULD language,
and an amendment rule. The constitution is governance — it may be amended
but should be established before the first implementation workflow.

## 4. SPECKITINIT.md structure

Write a detailed, skimmable operator guide. The file MUST read like a
project operator manual, not a short installation note.

### Required sections

| # | Section | What it covers |
|---|---------|----------------|
| 1 | **Title & metadata** | Observed Spec Kit CLI version, detected integration, date. Label version as observed, not pinned. |
| 2 | **Table of contents** | Links to all major sections. |
| 3 | **Repository profile** | Detected stack, runtime, build system, source layout, persistence, auth, security, tests, deployment, platforms. Separate verified facts from agent-neutral Spec Kit behavior. |
| 4 | **Installation & status** | Ownership table for CLI, `.specify/`, agent artifacts, constitution, guide, update checker. |
| 5 | **Command inventory** | Enumerate from manifest/status — never hard-coded. Include each path and purpose. |
| 6 | **Golden workflow** | The correct ordering (see below). Explain when optional steps are appropriate. |
| 7 | **Command reference** | One entry per detected command: purpose, prerequisites, bounded copy-paste prompt (using detected syntax), expected artifacts, verification, stop/approval conditions. |
| 8 | **Cross-cutting pipelines** | Performance, UI/UX, security, SEO, accessibility, testing, cleanup, database, deployment, observability, architecture. Add stack-specific pipelines as needed. |
| 9 | **First-run constitution prompt** | Copy-pasteable, derived from verified rules only, explicitly forbids implementation during constitution. |
| 10 | **Quick-reference** | First setup, normal feature, audit-only, resume interrupted, constitution amendment, CLI maintenance. |
| 11 | **Maintenance** | Three channels: CLI (`self check`/`self upgrade`), project integration (manifest-aware update), extensions/presets (own lifecycle). Include restart requirements. |
| 12 | **File ownership** | Managed, user-authored, generated-but-customizable, unknown. Include actual feature-artifact layout. |
| 13 | **Safe operating rules** | Backups, secrets, user data, permissions, migrations, deps, destructive commands, production data, rollback, approval points, files to inspect before editing. |
| 14 | **Verification matrix** | Map each workflow to exact checks, expected evidence, known limitations. Classify auto-safe vs. mutating commands. |

### Golden workflow ordering

```text
constitution → specify → [clarify] → plan → [checklist] → tasks → [analyze] → implement → converge → [taskstoissues]
```

Brackets `[...]` = optional. Explain when each is appropriate.

### Recipe format

Each pipeline/recipe MUST include:
- **Goal** — what success looks like
- **Scope** — what it touches and what it does NOT touch
- **Prerequisites** — what must be true before starting
- **Commands** — exact, ordered, copy-pasteable, using only verified flags
- **Expected artifacts** — files, outputs, side effects
- **Verification** — commands or manual checks to confirm success
- **Stop conditions** — when to halt and ask for human input
- **Rollback** — how to undo if something goes wrong

Use placeholders like `<feature-name>` only when the user must supply a
value, and explain each placeholder immediately.

## 5. Proven standards

Assert only what you can verify. The hierarchy:

1. **Repo's own docs and tests** — highest authority for this project.
2. **Official vendor docs** — MDN, framework maintainers, cloud-provider
   docs, package-manager docs, OWASP, W3C/WCAG, IETF.
3. **Version-sensitive claims** — check current docs/release notes. Record
   the date or version when it materially affects behavior.

**Never recommend:** deprecated APIs, abandoned tools, cargo-cult benchmarks,
fabricated flags, invented hooks, or patterns that sound modern but lack
evidence.

**If evidence is unavailable** or sources disagree: label as assumption or
open question. Do not make it a mandatory gate.

### Cross-cutting verification checklist

| Area | What to verify |
|------|----------------|
| Performance | Baseline exists, measurement tool identified, target justified by product, before/after comparison possible |
| Security | Threat scope defined, least privilege, input/output handling, dependency audit (`npm audit` / `pip-audit` / `cargo audit`), logging privacy, regression tests |
| UI/UX | User goals defined, responsive/keyboard behavior tested, accessibility evidence (axe, Lighthouse, manual), visual regression or manual review |
| SEO | Accurate metadata, crawlability, structured data matches visible content, accessible HTML, useful content |
| Database | Migration path exists, rollback tested, no untested schema changes in production |

## 6. Ownership and idempotency

Classify every file before editing:

| Ownership | Handling |
|-----------|----------|
| **Managed** | Created by Spec Kit/CLI. Safely replaceable. Update through CLI, verify status after. |
| **User-authored** | Never overwrite automatically. Preserve and request intentional edit. |
| **Generated-but-customizable** | Keep local overrides. Update the source layer, not the customized output. |
| **Unknown** | Stop. Inspect provenance before changing. |

Record ownership in `SPECKITINIT.md`. Use the integration manifest, status
report, ignore files, and git history as evidence.

**Idempotency rule:** Running this skill twice MUST converge to the same
result — no duplicate commands, hooks, scripts, docs, or unnecessary
formatting changes. Re-run status and inspect the diff after every update.

## 7. Update check automation

Provide a project-native task or standalone script (e.g.,
`scripts/speckit-update-check.sh`) with:

- `specify self check` (read-only) with configurable throttle
- Clear upgrade instruction (`specify self upgrade`, `--dry-run` preview)
- Graceful behavior when `specify` is missing or offline
- No secrets, prompts, or tokens in logs
- A native task entry (package script, Make/Just task, Cargo alias, etc.)

The updater MUST be advisory by default: report newer releases but never
silently rewrite project files, upgrade deps, run migrations, or deploy.

For OpenCode, an optional auto-discovered plugin at
`.opencode/plugins/speckit-update.ts` MAY run the checker on session
creation. Make failures non-blocking. Provide an opt-out env var
(`SPECKIT_AUTO_UPDATE_CHECK=0`).

## 8. Quality gate

Before reporting completion, validate:

- [ ] Command count, names, frontmatter, and artifact paths match the
      installed integration and manifest — not a hard-coded list.
- [ ] Every shell command verified with `--help` or a safe dry-run.
- [ ] Shell/plugin syntax passes the repo's lint/typecheck/tests.
- [ ] All framework-specific paths verified against actual filesystem.
- [ ] Links, headings, code fences, placeholders, and command order correct.
- [ ] Final diff inspected, including generated and ignored files.
- [ ] Explicit `unknown`, `unverified`, or `not supported` labels wherever
      the repo, CLI, agent, or docs cannot confirm a claim.

Never state that Spec Kit was installed, upgraded, or integrated unless
filesystem and CLI checks support that claim. Never call a workflow
flawless — report warnings, skipped checks, and residual risk.
