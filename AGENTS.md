# Repository guidance

This is a collection of agent skills, primarily Markdown with optional helper scripts. Keep each change within the requested skill and its callers. Read the skill, references, tests, and applicable instructions before editing. Preserve user work and existing conventions; make the smallest complete change, reuse dependencies, and avoid unrelated cleanup or speculative abstractions. Preserve public and persisted contracts unless a change is authorized, updating consumers and migration guidance when necessary. Validate external input, enforce authorization where relevant, and protect secrets and personal data.

Verify changed behavior with proportionate checks and regression coverage where practical. Never weaken valid checks to get green. Wait for results and distinguish passed, failed, pending, and unavailable verification. Report actual outcomes and limitations. Commit, push, publish, deploy, or perform destructive actions only within user authorization. For version-sensitive library, framework, SDK, API, CLI, or cloud-service work, consult Context7 when available against the installed or targeted version; use official documentation or installed source when coverage is insufficient. Preserve these safeguards alongside skill-specific instructions and surface material conflicts.

## Skill-specific checks

- Coding guidelines: `PYTHONDONTWRITEBYTECODE=1 python3 skills/development-skills/coding-guidelines-generator/tests/run_tests.py`. Helpers use Python's standard library; no dependency installation is required.
- Keep YAML frontmatter names consistent with directories and relative references resolvable. Follow the root README's skill checklist when adding or renaming skills.
- Test filesystem mutations in temporary fixtures. Preserve unmanaged bytes and detect collisions; do not run a guideline installer against this repository as a test.
