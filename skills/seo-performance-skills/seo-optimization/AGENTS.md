# Repository guidance

This folder contains the `seo-optimization` agent skill, Markdown references and Python 3 standard-library helpers. No package installation or build is required. Keep the skill portable across host agents and distinguish source evidence from rendered and live behavior.

Inspect relevant code, callers and applicable instructions before editing. Preserve user changes. Make the smallest complete change, reuse existing dependencies and conventions, and avoid unrelated cleanup or speculative abstractions. Preserve public and persisted contracts unless authorized; update consumers when necessary. Validate external input, enforce authorization at the relevant boundary, and protect secrets and personal data. Consult Context7 for version-sensitive work when available; otherwise use official documentation or installed source.

Verify changed behavior with proportionate checks and practical regression coverage. Never weaken valid checks. Wait for results and report passed, failed, pending and unavailable checks accurately. Do not claim unverified completion. Commit, push, publish, deploy or perform destructive actions only within user authorization.

Run helper regression tests from this directory with `python3 -m unittest discover -s tests -v`. Helpers must remain usable when the current directory differs from `--root`; audit writes must preserve existing records and stay inside the chosen project. Scanner results are leads, never automatic defects. Validate skill frontmatter with the host's skill validator when available; behavioral review is still required.
