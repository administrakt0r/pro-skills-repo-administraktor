---
name: github-actions-templates
description: >
  Use when setting up, auditing, or modernizing GitHub Actions CI/CD workflows:
  automated testing, Docker image builds, Kubernetes deployments, security
  scanning, matrix builds, reusable workflows, and approval-gated production
  releases. Covers workflow architecture, secret handling, caching, permissions,
  and environment protection rules. Excludes GitLab CI, CircleCI, Jenkins, or
  other non-GitHub CI systems (see `gitlab-ci-patterns` for GitLab).
license: MIT
metadata:
  author: Seth Hobson (wshobson)
  upstream_repo: https://github.com/wshobson/agents
  upstream_path: plugins/cicd-automation/skills/github-actions-templates/SKILL.md
  commit: 156b7a5e7a8b
  imported: "2026-11-01"
---

# GitHub Actions Templates

Production-ready GitHub Actions workflow patterns for automated testing, Docker
builds, Kubernetes deployments, security scanning, and approval-gated releases.

## When to Use This Skill

- Wire up CI/CD for a new repository with automated tests and builds
- Build and publish Docker images to GHCR or Docker Hub on every push / tag
- Deploy to Kubernetes (EKS, GKE, AKS) from a GitHub Actions pipeline
- Run vulnerability scans (Trivy, Snyk, CodeQL) as PR checks
- Create matrix builds to validate multiple OS / language-version combinations
- Implement reusable workflows to share CI logic across repositories
- Add environment protection rules and approval gates for production deploys
- Configure secrets management and least-privilege job permissions

## Action Version Reference (November 2026)

Always pin to a major version tag (e.g. `@v7`), never `@latest`.

| Action | Current major | Notes |
|---|---|---|
| `actions/checkout` | **@v7** | Runs on Node 24 runtime |
| `actions/setup-node` | **@v7** | Use `node-version: '22'` or `'24'` for current LTS |
| `actions/setup-python` | **@v5** | |
| `docker/login-action` | **@v3** | |
| `docker/metadata-action` | **@v6** | |
| `docker/build-push-action` | **@v7** | v5 is deprecated (Node 20 EOL) |
| `aws-actions/configure-aws-credentials` | **@v4** | Prefer OIDC over long-lived keys |
| `aquasecurity/trivy-action` | **@v0.36.0+** | v0.28–v0.34.2 had a security compromise in early 2026; use ≥ v0.35.0 |
| `github/codeql-action/upload-sarif` | **@v4** | Requires `security-events: write` permission |
| `codecov/codecov-action` | **@v5** | Use `token: ${{ secrets.CODECOV_TOKEN }}` |
| `snyk/actions/node` | **@master** | Or use `snyk/actions/setup` for CLI-only install |
| `slackapi/slack-github-action` | **@v4** | API changed in v2+; use `method: chat.postMessage` |

## Common Workflow Patterns

### Pattern 1: Test Workflow (Node.js)

```yaml
name: Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [22, 24]   # Current Active LTS and Current

    steps:
      - uses: actions/checkout@v7

      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v7
        with:
          node-version: ${{ matrix.node-version }}
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint

      - name: Run tests
        run: npm test

      - name: Upload coverage
        uses: codecov/codecov-action@v5
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          files: ./coverage/lcov.info
          fail_ci_if_error: true
```

### Pattern 2: Build and Push Docker Image

```yaml
name: Build and Push

on:
  push:
    branches: [main]
    tags: ["v*"]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v7

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v6
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}

      - name: Build and push
        uses: docker/build-push-action@v7
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### Pattern 3: Deploy to Kubernetes (OIDC — no long-lived keys)

```yaml
name: Deploy to Kubernetes

on:
  push:
    branches: [main]

permissions:
  id-token: write   # Required for OIDC token exchange
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v7

      - name: Configure AWS credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: us-west-2

      - name: Update kubeconfig
        run: |
          aws eks update-kubeconfig --name production-cluster --region us-west-2

      - name: Deploy to Kubernetes
        run: |
          kubectl apply -f k8s/
          kubectl rollout status deployment/my-app -n production

      - name: Verify deployment
        run: |
          kubectl get pods -n production
          kubectl describe deployment my-app -n production
```

> **Security note:** Prefer OIDC (`role-to-assume`) over long-lived
> `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` secrets. OIDC tokens expire
> automatically and leave no persistent credentials in GitHub.

### Pattern 4: Matrix Build (Python)

```yaml
name: Matrix Build

on: [push, pull_request]

jobs:
  build:
    runs-on: ${{ matrix.os }}

    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v7

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: "pip"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: pytest
```

## Workflow Best Practices

1. **Pin to major version tags** — use `@v7`, not `@latest`. Floating `@latest`
   can silently break workflows on major releases.
2. **Cache dependencies** — `cache: "npm"` / `cache: "pip"` shaves minutes off
   every run.
3. **Use GitHub Secrets** for tokens, keys, and webhook URLs — never hardcode.
4. **Enforce branch protection** — require status checks from CI jobs before
   merging PRs.
5. **Matrix builds** — validate across the OS / runtime versions you actively
   support.
6. **Least-privilege permissions** — set `permissions:` at the job level;
   default `contents: read` prevents accidental write access.
7. **Reusable workflows** — share common CI logic via `workflow_call` instead of
   copy-pasting YAML across repositories.
8. **Approval gates** — protect production environments in repository Settings →
   Environments; require one or more reviewers before the deploy job runs.
9. **Failure notifications** — add a Slack or email step with `if: failure()`
   so on-call engineers are paged immediately.
10. **Self-hosted runners** — use for workloads that access private VPC resources
    or require specialized hardware; avoid for public open-source repositories
    (supply-chain risk from fork PRs).

## Reusable Workflows

```yaml
# .github/workflows/reusable-test.yml
name: Reusable Test Workflow

on:
  workflow_call:
    inputs:
      node-version:
        required: true
        type: string
    secrets:
      NPM_TOKEN:
        required: true

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-node@v7
        with:
          node-version: ${{ inputs.node-version }}
          cache: "npm"
      - run: npm ci
      - run: npm test
```

**Invoke the reusable workflow from another workflow:**

```yaml
jobs:
  call-test:
    uses: ./.github/workflows/reusable-test.yml
    with:
      node-version: "22"
    secrets:
      NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## Security Scanning

```yaml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read
  security-events: write   # Required for uploading SARIF results

jobs:
  security:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v7

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@v0.36.0
        with:
          scan-type: "fs"
          scan-ref: "."
          format: "sarif"
          output: "trivy-results.sarif"
          exit-code: "1"          # Fail the job on HIGH/CRITICAL findings
          severity: "HIGH,CRITICAL"

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v4
        if: always()              # Upload even when trivy-action fails
        with:
          sarif_file: "trivy-results.sarif"

      - name: Run Snyk Security Scan
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

> **⚠️ Trivy security note:** Versions `v0.28.0`–`v0.34.2` of
> `aquasecurity/trivy-action` were compromised in early 2026. Use
> **`v0.35.0` or later**.

## Deployment with Approval Gates

```yaml
name: Deploy to Production

on:
  push:
    tags: ["v*"]

permissions:
  contents: read
  id-token: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://app.example.com   # Shown in the deployment UI

    steps:
      - uses: actions/checkout@v7

      - name: Deploy application
        run: |
          echo "Deploying ${{ github.ref_name }} to production..."
          # Insert your deploy command here

      - name: Notify Slack on success
        if: success()
        uses: slackapi/slack-github-action@v4
        with:
          method: chat.postMessage
          token: ${{ secrets.SLACK_BOT_TOKEN }}
          payload: |
            {
              "channel": "${{ secrets.SLACK_DEPLOY_CHANNEL }}",
              "text": "✅ Deployment of ${{ github.ref_name }} to production completed successfully!"
            }

      - name: Notify Slack on failure
        if: failure()
        uses: slackapi/slack-github-action@v4
        with:
          method: chat.postMessage
          token: ${{ secrets.SLACK_BOT_TOKEN }}
          payload: |
            {
              "channel": "${{ secrets.SLACK_DEPLOY_CHANNEL }}",
              "text": "🚨 Deployment of ${{ github.ref_name }} to production FAILED. Check the run: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
            }
```

> Configure the `production` environment in **Settings → Environments** to
> require one or more designated reviewers before this job runs.

## Related Skills

- `deployment-pipeline-design` — Pipeline architecture and stage design
- `secrets-management` — Secrets rotation, OIDC, and vault integration
- `gitlab-ci-patterns` — For GitLab CI/CD equivalents
