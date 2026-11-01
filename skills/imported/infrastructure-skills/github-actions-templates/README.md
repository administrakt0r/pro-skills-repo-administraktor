# github-actions-templates

Production-ready GitHub Actions CI/CD workflow patterns: automated testing,
Docker builds, Kubernetes deployments, security scanning, matrix builds,
reusable workflows, and approval-gated production releases.

## Overview

This skill gives an AI coding agent step-by-step, copy-paste-ready GitHub
Actions YAML patterns for the most common CI/CD scenarios. It covers workflow
architecture decisions, secret handling, caching strategy, job-level
permissions, and environment protection rules.

## When to Use

- Setting up CI for a new repository (test, lint, coverage)
- Building and publishing Docker images to GHCR or Docker Hub
- Deploying to Kubernetes (EKS, GKE, AKS) via GitHub Actions
- Integrating vulnerability scanners (Trivy, Snyk, CodeQL) as PR checks
- Cross-platform matrix builds (Linux, macOS, Windows; multiple runtime versions)
- Sharing CI logic across repositories via reusable workflows (`workflow_call`)
- Implementing approval-gated production deploys with environment protection
- Hardening existing workflows (OIDC instead of long-lived secrets, pinned
  action versions, least-privilege permissions)

**Not for:** GitLab CI, CircleCI, Jenkins, or other CI systems.

## Prerequisites

- A GitHub repository with Actions enabled
- Appropriate GitHub Secrets configured (tokens, cloud credentials)
- For Kubernetes deploys: a cluster and `kubeconfig` or OIDC role

## Directory Structure

```text
github-actions-templates/
├── SKILL.md      Main skill instructions and workflow patterns
├── README.md     This file — overview, prerequisites, usage, provenance
└── LICENSE       MIT License (upstream: wshobson/agents)
```

## Example Prompts

```text
Set up a GitHub Actions workflow to run my Node.js 22 tests on every PR and
push to main, with npm caching and Codecov coverage upload.
```

```text
Create a workflow that builds and pushes a Docker image to GHCR on every push
to main or version tag, using the docker/metadata-action for tagging.
```

```text
Add a Trivy security-scan job that fails on HIGH and CRITICAL CVEs and uploads
results to GitHub Security's Code Scanning dashboard.
```

```text
Harden my existing GitHub Actions workflows: pin action versions, add
least-privilege permissions, replace long-lived AWS keys with OIDC.
```

```text
Create a reusable workflow for running tests so my three microservice repos can
share the same CI logic without copy-pasting YAML.
```

## Action Version Reference (November 2026)

| Action | Current major |
|---|---|
| `actions/checkout` | `@v7` |
| `actions/setup-node` | `@v7` |
| `actions/setup-python` | `@v5` |
| `docker/login-action` | `@v3` |
| `docker/metadata-action` | `@v6` |
| `docker/build-push-action` | `@v7` |
| `aws-actions/configure-aws-credentials` | `@v4` |
| `aquasecurity/trivy-action` | `@v0.36.0+` ⚠️ see note |
| `github/codeql-action/upload-sarif` | `@v4` |
| `codecov/codecov-action` | `@v5` |
| `slackapi/slack-github-action` | `@v4` |

> **⚠️ Trivy:** Versions `v0.28.0`–`v0.34.2` of `aquasecurity/trivy-action`
> were compromised in early 2026. Pin to **`v0.35.0` or later**.

## Upstream Provenance

| Field | Value |
|---|---|
| **Original author** | Seth Hobson ([@wshobson](https://github.com/wshobson)) |
| **Upstream repository** | [wshobson/agents](https://github.com/wshobson/agents) |
| **Upstream path** | `plugins/cicd-automation/skills/github-actions-templates/SKILL.md` |
| **Commit** | `156b7a5e7a8b` (2026-09-29) |
| **License** | MIT — see `LICENSE` in this directory |
| **Import date** | 2026-11-01 |

## Enhancements Applied on Import

The following changes were made before import into this repository:

1. **Action versions updated to current majors** — all `actions/checkout`,
   `actions/setup-node`, `docker/build-push-action`, `docker/metadata-action`,
   `codecov/codecov-action`, `github/codeql-action/upload-sarif`, and
   `slackapi/slack-github-action` references updated from stale v4/v5 to their
   current major versions (v7, v6, v4, etc.).
2. **Security notice added for Trivy** — flagged that `aquasecurity/trivy-action`
   `v0.28.0`–`v0.34.2` were compromised in early 2026; SKILL.md and README now
   recommend `≥ v0.35.0`.
3. **Trivy scan hardened** — added `exit-code: "1"` and
   `severity: "HIGH,CRITICAL"` so the job actually fails on findings; upstream
   had these missing.
4. **OIDC Kubernetes pattern** — replaced long-lived
   `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` with OIDC
   (`role-to-assume: ${{ secrets.AWS_ROLE_ARN }}`). Added note explaining
   why OIDC is preferred.
5. **Slack notification updated to v4 API** — the `slackapi/slack-github-action@v4`
   changed its interface; updated payload structure to `method: chat.postMessage`
   and `token:` parameter.
6. **Node.js versions in matrix** — updated from `[18.x, 20.x]` to `[22, 24]`
   to reflect current Active LTS (22) and Current (24) releases.
7. **Python 3.9 removed from matrix** — Python 3.9 reached end-of-life October
   2025; matrix updated to `["3.10", "3.11", "3.12"]`.
8. **`if: always()`** added to SARIF upload step — ensures results are uploaded
   even when the Trivy scan step fails (e.g. high-severity findings detected).
9. **Failure Slack notification** added to production deploy pattern — the
   upstream only notified on success; added a parallel `if: failure()` step.
10. **Permissions block** added to security-scan job — `security-events: write`
    is required for `upload-sarif` but was absent in the upstream.
11. **`README.md` created** — upstream skill had no README; this file was written
    from scratch.
12. **Frontmatter enhanced** — trigger phrase prefixed to `description`;
    `license` and `metadata` keys added per the Agent Skills schema.
