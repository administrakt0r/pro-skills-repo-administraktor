# new-skill-import log

Source of truth for skills imported into `skills/imported/`. Maintained by
[`new-skill-import.md`](new-skill-import.md). Each run documents provenance,
security audit results, enhancements, and target paths.

## Index of imported skills

| skill | category | upstream_repo | license | date | status | path | notes |
|-------|----------|---------------|---------|------|--------|------|-------|
| seo-optimization | seo-performance-skills | /home/q/Desktop/seo-optim-skill (local) | (author's original license) | 2026-10-25 | imported | skills/seo-performance-skills/seo-optimization/ | Enhanced with Common mistakes section; strengthened description; all 9 tests pass |
| github-actions-templates | infrastructure-skills | https://github.com/wshobson/agents | MIT | 2026-11-01 | imported | skills/imported/infrastructure-skills/github-actions-templates/ | Action versions modernized (checkout@v7, build-push@v7, metadata@v6, slack@v4, codeql@v4, codecov@v5); Trivy security compromise flagged; OIDC deploy pattern; Python 3.9 EOL removed; README and LICENSE added |

## Import log entries

<!-- Log entries will be appended below by new-skill-import.md runs -->

### seo-optimization — 2026-10-25

**Source:** Local skill folder `/home/q/Desktop/seo-optim-skill/`  
**Category:** seo-performance-skills  
**Target path:** `skills/seo-performance-skills/seo-optimization/`  
**License:** (author's original, no explicit license file found)

**Security audit:** Content reviewed — no prompt injection, no hidden instructions, no unauthorized external calls. Scripts are standard-library Python 3 with bounded I/O. No secrets or credentials.

**Enhancements applied:**
- Strengthened `description` frontmatter with additional trigger keywords (GEO, AEO, Core Web Vitals, hreflang, crawl budget, canonicals, structured data, schema.org)
- Added `## Common mistakes` section documenting six common failure modes with clear guidance
- All 9 helper regression tests verified passing before and after enhancement

**Verification:** `python3 -m unittest discover -s tests -v` → 9/9 passed (OK)

**Follow-ups:** None required.

---

### github-actions-templates — 2026-11-01

**Upstream:** https://github.com/wshobson/agents (commit: `156b7a5e7a8b`, 2026-09-29)
**Upstream path:** `plugins/cicd-automation/skills/github-actions-templates/SKILL.md`
**License:** MIT — Copyright (c) 2024 Seth Hobson
**Category:** infrastructure-skills
**Path:** `skills/imported/infrastructure-skills/github-actions-templates/`

**Security Audit:**
- Prompt injection scan: **CLEAN** — no "ignore previous instructions", "system override", "DAN mode", or agent-hijacking language found
- Hidden payloads / Unicode scan: **CLEAN** — no zero-width characters (U+200B, U+200C, U+200D, U+FEFF, U+202E), no bidirectional override bytes, no hidden HTML comments
- Obfuscation scan: **CLEAN** — no base64-encoded commands, `eval()`, `Function()`, hex-escape sequences, or packed scripts
- Malicious execution scan: **CLEAN** — no `curl | sh`, `wget | bash`, or unverified binary downloads; all shell commands in examples are standard `kubectl`, `aws`, `npm`, `pytest`
- Secret exfiltration scan: **CLEAN** — no instructions to read `~/.ssh`, `~/.aws`, or `.env`; all credential references use `${{ secrets.X }}` GitHub Secrets idiom (legitimate CI pattern)
- Permission/safety scan: **CLEAN** — no `chmod 777`, no TLS verification disable, no privileged containers, no auth bypass advice

**Enhancements Applied:**
1. Action versions modernized — `actions/checkout` → `@v7`, `actions/setup-node` → `@v7`, `docker/build-push-action` → `@v7`, `docker/metadata-action` → `@v6`, `github/codeql-action/upload-sarif` → `@v4`, `codecov/codecov-action` → `@v5`, `slackapi/slack-github-action` → `@v4`
2. **Critical security notice added** — `aquasecurity/trivy-action@v0.28.0`–`v0.34.2` suffered a supply-chain compromise in early 2026; SKILL.md and README warn to use `≥ v0.35.0`
3. Trivy scan hardened — added `exit-code: "1"` and `severity: "HIGH,CRITICAL"` so job actually blocks PRs on serious findings (upstream omitted these)
4. OIDC Kubernetes pattern — replaced long-lived `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` with `role-to-assume` OIDC pattern; added explanation note
5. Slack notification updated to v4 API — upstream used v1 payload format; updated to `method: chat.postMessage` + `token:` which is the v4 API
6. Node.js matrix versions updated — `[18.x, 20.x]` → `[22, 24]` (22 = Active LTS, 24 = Current as of Nov 2026)
7. Python 3.9 removed from matrix — reached EOL October 2025; matrix now `["3.10","3.11","3.12"]`
8. `if: always()` added to SARIF upload step — ensures results are uploaded even when Trivy step exits non-zero
9. Failure Slack notification added — upstream deploy pattern only had `if: success()`; added `if: failure()` step with run URL
10. `permissions:` block added to security-scan job — `security-events: write` required for `upload-sarif` but absent upstream
11. `README.md` created from scratch — upstream skill had no README
12. `LICENSE` file copied from upstream repository
13. YAML frontmatter enhanced — trigger phrase added to `description`; `license` field and `metadata:` mapping added per Agent Skills schema

**Staleness Verification:** All action versions and Python/Node ranges verified against official GitHub Marketplace releases and GitHub blog posts (November 2026). Trivy compromise confirmed via StepSecurity disclosure.

**Follow-ups:**
- Monitor `aquasecurity/trivy-action` for releases beyond `v0.36.0`
- Add a `references/` folder with GitHub's official workflow syntax reference when expanding this skill
