# Final report template

Use this exact order. Keep it concise. Be explicit about what was and wasn't verified.

## 1. Environment and method
- Stack(s) detected and what the repo ships
- Commands used for build / lint / test (and where they came from: CI file, manifest)
- Baseline result on the untouched default branch (including pre-existing failures)
- Merge method used
- What verification was possible and what was not

## 2. PR table

| # | Title | Classification | Action taken | One-line reason |
|---|---|---|---|---|
| 123 | ... | CLEAN / FIXABLE / BLOCKED | merged / fixed and merged / left open / skipped | ... |

## 3. Fixes made
For each FIXABLE PR: what was wrong, what you changed, and the commit.

## 4. BLOCKED and skipped PRs
For each: why it was blocked or skipped, and exactly what a human needs to decide or do to unblock it.

## 5. Post-merge verification
- Method (tests, build, CLI smoke test, health check, emulator)
- Result, compared to baseline
- Anything that could not be run (state that runtime behavior is unverified)

## 6. Risks and follow-ups
Tech debt, flaky tests, pre-existing failures, anything worth a human's attention.

## 7. Confidence
What you are sure works, and what you are not sure about.
