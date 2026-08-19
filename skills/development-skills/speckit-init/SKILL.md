---
name: speckit-init
description: >
  Use when the user asks to install, initialize, integrate, upgrade, or
  document GitHub Spec Kit. Creates a repository-specific constitution and
  SPECKITINIT.md using the public workflow catalog. Do NOT use to implement
  application features; use the installed Spec Kit implementation command.
---

# Spec Kit Initialization and Workflow Authoring

Create a truthful, codebase-specific Spec Kit setup. This skill owns
installation, integration, constitution work, and guide authoring; it does not
implement application features from specs.

## 1. Discover before changing anything

Read the repository's guidance and relevant architecture, security, data,
deployment, and CI documentation. Establish the actual language, runtime,
package manager, source layout, test/build gates, persistence, auth, and
deployment constraints.

Inspect existing `.specify/`, agent integration directories, `specs/`,
`SPECKITINIT.md`, and update scripts. Classify files as managed,
user-authored, generated-but-customizable, or unknown before editing them.
Never overwrite unknown or user-authored content without an intentional
decision.

## 2. Verify the CLI and integration

Start with `specify --help` and `specify integration --help`. Use only the
commands and flags the installed CLI exposes; `--version`, `self check`,
integration listing, and integration status are common but version-dependent.

If the CLI is absent and installation is in scope, use the official install
method after confirming its current documentation. If health checks fail,
report that result and do not claim installation, upgrade, or integration
succeeded.

Use the CLI manifest/status and generated files as the source of truth for the
available commands and their agent-specific invocation syntax. Do not present
one integration's `/speckit.*` syntax as universal.

## 3. Use the public workflow catalog selectively

Read the [reusable Spec Kit workflow catalog](https://github.com/administrakt0r/pro-skills-repo-administraktor/blob/main/speckit-skills-guides-workflows/SPECKIT-workflows.md)
before authoring or materially revising `SPECKITINIT.md`.

Treat it as a reference library, not a document to copy. Preserve its logical
command ordering and safety model, then curate it for the target repository:

- include the detected command inventory and agent syntax;
- include only pipelines relevant to the repository or requested use cases;
- replace all generic commands, paths, checks, and ownership claims with
  verified local evidence;
- mark unverified facts as unknown and omit unsupported operations;
- retain explicit stop, approval, verification, and rollback conditions for
  consequential workflows.

The resulting `SPECKITINIT.md` should be a skimmable operator guide with a
repository profile, command inventory, curated workflow recipes, constitution
prompt, maintenance notes, ownership table, operating rules, and a verification
matrix. Do not duplicate the entire public catalog unless the repository has a
demonstrated need for every section.

## 4. Constitution and maintenance

Derive constitution rules only from verified repository evidence. A first-run
prompt must cover actual architectural boundaries, data/auth contracts,
security and privacy rules, quality gates, deployment constraints, and
applicable design/accessibility standards. Constitution work must not authorize
application implementation.

If ongoing maintenance is requested and the repository has an appropriate
task/script location, add an advisory update check. It may report available
updates but must not silently upgrade the CLI, rewrite project files, change
dependencies, run migrations, deploy, or expose secrets. For a
documentation-only request, document the manual check instead.

## 5. Completion standard

Before reporting completion, confirm that generated commands, paths, and
frontmatter match the installed integration; validate shell commands using help
or a safe dry run; check local links and placeholders; and inspect the final
diff. Report skipped checks, unknowns, warnings, and residual risk. Never claim
that Spec Kit is installed, upgraded, or integrated without filesystem and CLI
evidence.
