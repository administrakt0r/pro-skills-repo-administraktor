---
name: coding-guidelines-generator
description: >-
  Use when the user asks to generate, create, set up, bootstrap, or apply
  coding guidelines, coding rules, project standards, or stack-specific
  conventions for a repository. Also trigger on requests to add an
  AGENTS-GUIDELINES file, enforce coding standards, standardize a project's
  rules, or "set up rules for this repo". Auto-detects the project's tech
  stack(s), generates tailored AGENTS-GUIDELINES-{STACK}.md files next to
  AGENTS.md, merges with any existing guideline files (preserving user
  customizations), and injects a mandatory read-and-obey directive at the top
  of AGENTS.md. Creates AGENTS.md if absent. Do not use for general code
  review, linting configuration, or CI setup — this skill produces the
  written guidance documents only.
---

# Coding Guidelines Generator

## Purpose

Generate stack-specific coding guideline files rooted in a proven portable
baseline, tailored to the actual project configuration, and wired into the
repository's AGENTS.md so every AI agent that touches the repo is required to
read and follow them.

## Portable Baseline (Foundation)

Every generated guideline file opens with (or assumes) these cross-stack
defaults. Do NOT duplicate them into every stack file — reference them once in
the AGENTS.md directive. They are embedded here so the skill is self-contained.

<baseline>
Inspect relevant code, callers, and applicable instructions before editing.
Preserve existing user changes. Make the smallest complete change; avoid
unrelated cleanup, speculative features, and unnecessary abstractions. Follow
repository conventions and reuse existing implementations and dependencies.
Preserve public and persisted contracts unless changes are authorized; update
consumers and migration guidance when needed. Validate external input, enforce
server-side authorization, and protect secrets and personal data. Verify
changed behavior with proportionate project checks and regression coverage
where practical; never weaken valid checks to get green. Wait for check results
and distinguish passed, failed, pending, and unavailable verification. Report
actual outcomes and remaining limitations without claiming unverified success.
Commit, push, publish, deploy, or perform destructive actions only within user
authorization. For version-sensitive library, framework, SDK, API, CLI, or
cloud-service work, consult Context7 when available, matching the installed
version; use official documentation or installed source when coverage is
insufficient. Preserve these rules alongside project-specific instructions and
resolve material conflicts explicitly.
</baseline>

---

## Execution Procedure

Follow every step in order. Do not skip steps.

### Step 1 — Pre-flight Checks

1. Identify the repository root. If you cannot determine it, ask the user.
2. Check Git status and diff — do not overwrite uncommitted user changes to
   AGENTS.md or any AGENTS-GUIDELINES-*.md files without confirmation.

### Step 2 — Stack Detection

Auto-detect tech stacks by scanning the repo root and common subdirectories
for signature files. Use this detection table:

| Stack | Signature files |
|-------|----------------|
| JavaScript/TypeScript | `package.json`, `tsconfig.json`, `tsconfig*.json`, `.eslintrc*`, `eslint.config.*`, `.prettierrc*`, `vite.config.*`, `webpack.config.*`, `next.config.*`, `nuxt.config.*`, `angular.json`, `svelte.config.*`, `bun.lockb`, `deno.json` |
| Python | `pyproject.toml`, `setup.py`, `setup.cfg`, `requirements*.txt`, `Pipfile`, `poetry.lock`, `tox.ini`, `.flake8`, `mypy.ini`, `.python-version`, `ruff.toml` |
| Go | `go.mod`, `go.sum` |
| Rust | `Cargo.toml`, `Cargo.lock`, `rust-toolchain.toml`, `clippy.toml` |
| PHP | `composer.json`, `composer.lock`, `artisan`, `wp-config.php`, `symfony.lock`, `.php-cs-fixer*` |
| Java/Kotlin | `build.gradle`, `build.gradle.kts`, `pom.xml`, `settings.gradle*`, `gradlew`, `AndroidManifest.xml` |
| Shell/Bash | `*.sh` in root, `Makefile`, `.shellcheckrc`, `shellcheck.yml` |
| HTML/CSS | `index.html` in root, `*.html` in root, `tailwind.config.*`, `postcss.config.*`, `.stylelintrc*` |

**Multi-stack handling**: If multiple stacks are detected, generate a separate
`AGENTS-GUIDELINES-{STACK}.md` file for each detected stack.

**Unknown stack**: If no signatures match, prompt the user to specify the
stack. If the specified stack has no preset, generate generic but useful
guidelines covering the 10 categories below with stack-agnostic best practices.

### Step 3 — Inspect Project Configuration

For each detected stack, inspect the repo for actual tooling configuration.
This produces tailored guidelines, not generic boilerplate. Look for:

- **Formatter/Linter config**: ESLint rules, Prettier settings, Black/Ruff
  config, gofmt, rustfmt, Clippy, PHP-CS-Fixer, Checkstyle, ShellCheck, Stylelint
- **Type checking**: tsconfig strictness, mypy/pyright settings, Java generics
  usage, Rust edition
- **Test framework**: Jest, Vitest, Mocha, pytest, Go testing, Rust test,
  PHPUnit, JUnit, BATS
- **Build tool**: Webpack, Vite, esbuild, setuptools, Poetry, Cargo, Gradle,
  Maven, Make
- **Package manager**: npm/yarn/pnpm/bun, pip/poetry/uv, cargo, composer,
  gradle/maven
- **CI config**: `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`,
  `bitbucket-pipelines.yml` — extract test/lint/build commands
- **Framework**: Next.js, React, Vue, Angular, Svelte, Django, Flask, FastAPI,
  Laravel, Symfony, WordPress, Spring Boot, Actix, Rocket, Gin, Echo

Record what you find. The guidelines must reference the actual tools, not
hypothetical ones.

### Step 4 — Generate AGENTS-GUIDELINES-{STACK}.md

For each detected stack, generate (or merge into) a file named
`AGENTS-GUIDELINES-{STACK}.md` in the same directory as AGENTS.md, using the
uppercase short stack name:

- `AGENTS-GUIDELINES-JS.md` (JavaScript/TypeScript)
- `AGENTS-GUIDELINES-PYTHON.md`
- `AGENTS-GUIDELINES-GO.md`
- `AGENTS-GUIDELINES-RUST.md`
- `AGENTS-GUIDELINES-PHP.md`
- `AGENTS-GUIDELINES-JAVA.md` (Java/Kotlin)
- `AGENTS-GUIDELINES-SHELL.md`
- `AGENTS-GUIDELINES-HTML-CSS.md`
- `AGENTS-GUIDELINES-GENERIC.md` (unknown stacks)

#### File Structure

Each generated file MUST follow this structure:

```markdown
# {Stack Name} Coding Guidelines

> These guidelines are **mandatory** for all AI agents working in this
> repository. They supplement the portable baseline referenced in AGENTS.md.
> When a guideline here conflicts with the baseline, this file takes
> precedence for {stack}-specific concerns.

## 1. Package Manager & Lockfile

{Tailored rules based on detected package manager. Specify exact commands.
E.g., "Use `pnpm` exclusively. Never run `npm install`. Commit `pnpm-lock.yaml`."}

## 2. Linting & Formatting

{Reference the actual linter/formatter config found. Specify commands to run.
E.g., "Run `pnpm lint` before committing. Do not disable ESLint rules with
inline comments unless you explain why in a code comment."}

## 3. Type Safety & Nullability

{Stack-specific type conventions. E.g., for TS: "Strict mode is enabled.
Never use `any` — use `unknown` and narrow. No `@ts-ignore` without adjacent
explanation comment."}

## 4. Testing Conventions

{Test runner, file naming, coverage expectations. E.g., "Tests live in
`__tests__/` next to source. Run `pnpm test`. Name test files `*.test.ts`.
Bug fixes require a regression test."}

## 5. Error Handling

{Stack-idiomatic patterns. E.g., for Go: "Return errors; do not panic in
library code. Wrap errors with `fmt.Errorf('...': %w, err)`. Check every
returned error." For Rust: "Use `Result<T, E>`. Reserve `unwrap()`/`expect()`
for provably safe cases with a comment. Propagate with `?`."}

## 6. Security Patterns

{Stack-specific security. E.g., for PHP/Laravel: "Always use Eloquent or
query builder parameterized queries. Never concatenate user input into SQL.
Validate all request input with Form Requests. Use `{!! !!}` only when
explicitly safe."}

## 7. Build & Compilation

{Exact build commands, flags, output expectations. E.g., "Run `cargo build
--release` for production. Treat all warnings as errors (`-D warnings` in CI)."}

## 8. Dependency Management

{Version pinning strategy, audit commands, update policy. E.g., "Pin exact
versions in `package.json`. Run `pnpm audit` before adding new deps. Do not
add dependencies without a concrete justification."}

## 9. Logging & Observability

{Stack-appropriate patterns. E.g., "Use `structlog` for structured logging.
Log at INFO for business events, ERROR for failures. Never log secrets,
tokens, passwords, or PII."}

## 10. API Design

{If applicable. REST conventions, error response format, versioning.
E.g., "REST endpoints use kebab-case. Return `{ error: string, code: string }`
for errors. Version via URL prefix `/api/v1/`."}
```

#### Content Quality Rules

- **Be specific**: Reference actual project tools, paths, and commands.
  "Run `pytest -x --tb=short`" not "run your tests".
- **Be actionable**: Every rule must tell the agent what to do or not do.
  No vague advice like "follow best practices".
- **Be concise**: Aim for 200-400 words per file. Agents need to read this
  on every task; bloat wastes context window.
- **No duplication**: Do not repeat the portable baseline. These files are
  stack-specific supplements.
- **Detect, don't assume**: If a section's tooling isn't present in the repo,
  write a brief generic best-practice rule and note that no specific config
  was detected.

### Step 5 — Merge with Existing Files

If an `AGENTS-GUIDELINES-{STACK}.md` file already exists:

1. Read the existing file section by section.
2. For each of the 10 sections, compare existing content with generated content.
3. **Preserve** all existing user-written rules and customizations.
4. **Add** only sections or rules that are missing from the existing file.
5. **Do not** remove, rewrite, or reorder existing content.
6. Report what was added in the completion summary.

### Step 6 — Inject Directive into AGENTS.md

#### If AGENTS.md exists:

1. Check if a directive block pointing to `AGENTS-GUIDELINES-*.md` already
   exists (search for the marker `<!-- CODING-GUIDELINES-DIRECTIVE -->`).
2. If the marker exists, update the file list inside the directive block to
   include any newly generated files. Do not duplicate existing entries.
3. If the marker does NOT exist, prepend the following block at the very top
   of AGENTS.md (before all existing content):

```markdown
<!-- CODING-GUIDELINES-DIRECTIVE -->
> [!IMPORTANT]
> **Mandatory Coding Guidelines**
>
> Before starting ANY work in this repository, you MUST read and obey the
> following stack-specific coding guideline files. These are non-negotiable
> and supplement the portable baseline rules in this document.
>
> {List each generated file as a bullet with relative path, e.g.:}
> - [`AGENTS-GUIDELINES-JS.md`](./AGENTS-GUIDELINES-JS.md) — JavaScript/TypeScript rules
> - [`AGENTS-GUIDELINES-PYTHON.md`](./AGENTS-GUIDELINES-PYTHON.md) — Python rules
>
> Violations of these guidelines must be corrected before completing any task.
<!-- /CODING-GUIDELINES-DIRECTIVE -->

```

4. Do NOT modify any other content in AGENTS.md.

#### If AGENTS.md does NOT exist:

Create a new AGENTS.md with:

```markdown
<!-- CODING-GUIDELINES-DIRECTIVE -->
> [!IMPORTANT]
> **Mandatory Coding Guidelines**
>
> Before starting ANY work in this repository, you MUST read and obey the
> following stack-specific coding guideline files. These are non-negotiable.
>
> {List each generated file as a bullet with relative path}
>
> Violations of these guidelines must be corrected before completing any task.
<!-- /CODING-GUIDELINES-DIRECTIVE -->

# Project Instructions

<!-- Add project-specific instructions below this line. -->
<!-- Describe your project's architecture, conventions, and workflows here. -->
```

### Step 7 — Completion Report

After all files are generated/merged and AGENTS.md is updated, produce a
summary report with:

| Item | Detail |
|------|--------|
| **Stacks detected** | List each detected stack and the signature file(s) that triggered detection |
| **Files created** | List each new AGENTS-GUIDELINES-{STACK}.md file created |
| **Files merged** | List each existing file that was merged (with count of sections added) |
| **Files skipped** | List any files that were fully up-to-date |
| **AGENTS.md status** | Created / Updated / Already had directive (no changes) |
| **Undetected stacks** | Any stacks the user should manually specify |
| **Project tools found** | Summary of linters, formatters, test runners, build tools detected |

---

## Stack Preset Details

Below are the guideline templates for each supported stack. The skill MUST
tailor these based on actual project configuration found in Step 3.

### JavaScript / TypeScript

Key areas: strict TypeScript (`noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`
if configured), ESM vs CJS, framework-specific patterns (React hooks rules,
Next.js App Router conventions, Vue Composition API), `node:` prefix for
built-in imports, proper async/await error handling, no floating promises.

### Python

Key areas: type hints on all public functions, `ruff` or `black` formatting,
`mypy --strict` or `pyright` if configured, virtual environment conventions,
`__all__` exports, dataclasses/Pydantic over raw dicts, context managers for
resources, no bare `except:`.

### Go

Key areas: `gofmt`/`goimports` (non-negotiable), error wrapping with `%w`,
table-driven tests, no `init()` unless essential, context propagation,
`golangci-lint` configuration, interface segregation, no stuttered names.

### Rust

Key areas: Clippy lints at `warn` or `deny`, `cargo fmt`, `Result`/`Option`
over panics, `#[must_use]` on fallible functions, edition-specific features,
`unsafe` blocks require safety comments, `cargo audit`.

### PHP

Key areas: PSR-12/PER coding style, Composer autoloading, prepared statements
(never string concatenation for SQL), Laravel/Symfony conventions if detected,
`declare(strict_types=1)`, PHP-CS-Fixer or Pint config.

### Java / Kotlin

Key areas: Gradle/Maven conventions, null-safety (Kotlin `?` vs `!!`, Java
`@Nullable`/`@NonNull`), JUnit 5 patterns, Checkstyle/ktlint if configured,
no raw types, resource management with try-with-resources/`use`.

### Shell / Bash

Key areas: `set -euo pipefail` in all scripts, ShellCheck compliance,
quoting all variables, no `eval`, prefer `[[` over `[`, functions for
reusable logic, trap for cleanup.

### HTML / CSS

Key areas: semantic HTML elements, accessibility (ARIA only when native
semantics insufficient), responsive design conventions, Tailwind/PostCSS
config if detected, no inline styles in production, CSS custom properties
over preprocessor variables where supported.

---

## Guardrails

- **Never overwrite** existing user content in AGENTS.md or guideline files.
- **Never invent** tools, packages, or configurations not found in the repo.
- **Always be idempotent** — running the skill twice produces the same result.
- **Keep files concise** — agents read these on every task. 200-400 words per
  guideline file. The directive block should be under 15 lines.
- **Preserve Git cleanliness** — do not stage or commit; leave that to the user.
