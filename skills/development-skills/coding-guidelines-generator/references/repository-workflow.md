# Repository evidence and implementation contract

Read this during every setup or refresh. Inspect enough representative behavior to
write rules an agent can actually apply; a manifest alone cannot reveal architecture.

## Evidence to gather

1. **Authority and scope:** applicable instructions, Git status/diff, package boundaries,
   human guidance, generated/vendor directories, public and persisted contracts.
2. **Compatibility:** manifests, lockfiles, runtime/toolchain files, CI matrices,
   Gradle catalogs and wrappers where applicable. A dependency range is not an exact
   installed version. Workspace inheritance and multiple versions need explicit scope.
3. **Existing implementation:** entry points and representative callers, business
   logic, I/O boundaries, validation and resource authorization, state/error handling,
   migrations, tests and fixtures. Link to stable relevant paths rather than line numbers.
4. **Checks:** documented scripts and their bodies, CI invocation and working directory,
   configuration and prerequisites. Never execute setup.py, Gradle, package lifecycle
   hooks, or arbitrary Make targets just to detect a stack. Read before running any check.
5. **Observed risks:** document important invariants supported by code or user policy.
   Do not elevate an incidental bad pattern into a required convention. Surface an
   actual conflict or security defect separately rather than silently endorsing it.

Prefer current executable configuration and CI over stale README commands when they
disagree, but report material conflicts. Do not install a tool or run a deployment,
network integration, migration, or destructive test as a discovery shortcut.

## Contract for each generated guideline file

Use this shape, adapting headings and size to the repository:

- **Scope and compatibility:** affected paths, exclusions, supported runtime/framework
  constraints, evidence paths, and lower-layer guideline links.
- **Implementation rules:** concrete directions tied to local modules and boundaries.
  State what to reuse, where validation belongs, how errors/cancellation propagate,
  and which public/persisted behavior must remain compatible. Include only relevant
  security, data lifecycle, concurrency, performance, or accessibility constraints.
- **Verification:** exact command, working directory, prerequisites and whether it was
  discovered, passed, failed, or unavailable. Unknown check runners remain unknown.
  Include appropriate behavior/regression tests and user workflow checks when practical.
- **Unresolved facts:** only unknowns that affect implementation, with the next source
  to inspect. Avoid generic TODOs and invented commands to fill a template.

For example, in a Python repository that actually has `src/api/routes.py`,
`src/api/auth.py`, and a CI `uv run pytest tests/api` step, a useful instruction is:
"Reuse the authorization dependency in `src/api/auth.py` for routes in
`src/api/routes.py`; test allowed and denied access with the API fixtures. Run
`uv run pytest tests/api` from the repository root (discovered in CI, not run)."
Use the target repository's real paths and commands, not these example paths.

## How the generated rules guide later implementation

Keep a concise version of this workflow in the root baseline, merging equivalents:

1. Before editing, load the root instructions and applicable scoped guideline links;
   inspect relevant source, callers, tests, and Git changes. Identify acceptance criteria
   and material compatibility, authorization, data, and UI risks.
2. Make the smallest complete change using existing project conventions. Keep public
   contracts and user changes intact. Consult version-matched documentation for
   version-sensitive choices; do not upgrade as a side effect.
3. Reproduce defects when practical and cover meaningful regression/failure boundaries.
   Run focused checks first and broader repository checks as warranted. Verify the
   affected user interaction when practical. Never weaken valid checks to get green.
4. Review the final diff and report actual results and limitations. Commit, push,
   publish, deploy, or perform destructive operations only within user authorization.

These instructions should improve work on a later task without initiating a codebase
refactor, adding CI, or pretending that prose can enforce compliance mechanically.
