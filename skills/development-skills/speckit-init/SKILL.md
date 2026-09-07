---
name: speckit-init
description: >
  Use when the user asks to install, initialize, integrate, upgrade, or
  document GitHub Spec Kit. Creates a repository-specific constitution and
  SPECKITINIT.md with complete copy-paste workflows using the public workflow
  catalog. Do NOT use to implement application features; use the installed
  Spec Kit implementation command.
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

## 4. Require complete copy-paste command packs

Whenever creating or materially revising `SPECKITINIT.md`, include all four
command packs below unless the user explicitly asks to omit one:

1. governance or constitution creation/amendment;
2. general optimization covering measured performance, reliability,
   maintainability, and relevant UX improvements;
3. SEO, GEO, and AEO discoverability; and
4. bug or problem diagnosis, root-cause repair, and regression prevention.

Use the invocation syntax verified from the installed integration. For every
implementation workflow, provide the full ordered sequence exposed by that
integration corresponding to specify, optional-but-present clarify, plan,
checklist, tasks, analyze, implement, and converge. Put every invocation in its
own copyable code block with a complete repository-specific prompt, then add a
separate terminal block containing the repository's verified completion gates.
Tell the operator to paste one block at a time and wait for completion because
later commands consume artifacts produced by earlier commands.

Make the optimization pack ready to paste without a target placeholder: it
must inspect evidence, establish a reproducible baseline, select a bounded
coherent batch, define measurable success and rollback signals, and reject
unsupported optimization claims or unrelated rewrites. Make the SEO/GEO/AEO
pack ready to paste and cover only discoverability surfaces supported by the
repository; require observable outcomes, truthful visible-content/schema
alignment, accessibility, and no promises of rankings, indexing, traffic,
snippets, or AI citations. The bug pack may contain one clearly identified
problem-report placeholder because the operator must supply the incident; it
must require reproduction evidence, a root-cause-driven minimal fix, focused
regression coverage, and preservation of unrelated behavior.

The governance pack is a complete constitution command plus safe inspection
and validation commands, not an implementation pipeline. Derive its durable
rules from verified architecture, data/auth, security/privacy, quality,
deployment, and accessibility evidence. State that it should run only when
governance is missing or materially changed.

Keep prompts specific enough to run without inventing missing inputs. Include
scope, non-goals, constraints, acceptance evidence, rollback or stopping
conditions, authorization boundaries, and honest handling of unknowns. Avoid
generic `<scope>` or `<target>` placeholders except the single bug-report input
or another input that is genuinely impossible to infer. Do not copy framework,
path, service, or shell-command assumptions from the public catalog; substitute
only verified local facts. Preserve direct user instructions when they request
a different set or shape of workflows.

## 5. Constitution and maintenance

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

## 6. Completion standard

Before reporting completion, confirm that generated commands, paths, and
frontmatter match the installed integration; validate shell commands using help
or a safe dry run; check local links, balanced code fences, workflow command
order, and placeholder counts; and inspect the final diff. Confirm that all
four required command packs and their repository-specific verification blocks
are present. Report skipped checks, unknowns, warnings, and residual risk.
Never claim that Spec Kit is installed, upgraded, or integrated without
filesystem and CLI evidence.
