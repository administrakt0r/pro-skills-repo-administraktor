# Templates

Copy and fill in. Keep entries short and factual. If a destination file already exists, read it first and merge: never overwrite history.
Timestamps: ISO 8601 with the user's local UTC offset, e.g. `2026-10-23T22:05:22+02:00`.

## Contents
1. Finding block (used in AUDIT.md)
2. AUDIT.md
3. TASKS.md
4. WORKLOG.md entry
5. Folder README.md
6. Closing chat message and task menu

---

## 1. Finding block

```markdown
### SEO-003 - Product pages share one static <title>
- **Status:** confirmed | likely | hypothesis | blocked | fixed | deferred
- **Priority:** high - affects every product template; titles are the main presentation text in results
- **Evidence label:** Established | Supported but context-dependent | Emerging | Speculative
- **Evidence:** `templates/product.html:4` hard-codes `<title>Shop</title>`; same literal on 3 other templates (`scan_repo.py`, checked 2026-10-23T22:05+02:00). Source: [Google title links](https://developers.google.com/search/docs/appearance/title-link) (accessed 2026-10-23).
- **Recommendation:** Render `{{ product.name }} - {{ site.name }}` in the template; keep the visible H1 aligned.
- **Expected outcome:** Clearer, distinct results presentation; watch impressions and CTR for product URLs. No ranking or traffic is guaranteed. Engines may rewrite titles.
- **Risk:** Low. Possible short-term CTR change; no URL changes.
- **Validation:** Build; fetch raw HTML for 3 product URLs and confirm distinct `<title>`; check H1 match; confirm no duplicate `<title>` after hydration.
- **Confirmation level:** code-confirmed defect | observed response/rendered defect | likely risk | hypothesis | needs access
- **Review required:** no | yes - <why>
```

Priority guide: **critical** = important pages cannot be crawled/indexed or are broken for users; **high** = affects many/valuable pages with
strong evidence; **medium** = real but narrower, or evidence is partial; **low** = polish or small scope. Give a short reason every time.

## 2. AUDIT.md

```markdown
# SEO audit - <project name>
**Audit date:** <ISO 8601>   **Agent/tool environment:** <name if known>   **Repo ref:** <branch + short commit>

## Executive summary and context
<3-6 sentences: project type, inferred purpose and main journeys, headline results, biggest risks.>

## Platforms covered and evidence available
| Platform | In scope because | Evidence available this run | Not checked |
|---|---|---|---|

## Scope, date, tools and limitations
- Inspected: <paths, templates, routes>   Commands run: <list>   Tools used: <list>
- **Not performed:** <live site, Search Console, Bing Webmaster Tools, analytics, logs, field Core Web Vitals, etc., and why>

## Findings
<Finding blocks, ordered by priority. Group by: Code-confirmed defects / Likely risks / Hypotheses / Needs live-site access.>

## Coverage
| Area / template | Sample URLs / paths | checked / not applicable / not checked | Evidence / reason / next check |
|---|---|---|---|

## What is working well
<Specific, evidenced positives.>

## Assumptions and open questions
| # | Assumption or question | Why it matters | Who can answer |
|---|---|---|---|

## Recommended next actions and risks
<Ordered list referencing finding IDs; flag which need review (see risk-and-review.md).>

## Sources
| Source | Type (documented guidance / research / industry opinion / inference) | Date (published/updated or accessed) |
|---|---|---|
```

## 3. TASKS.md

```markdown
# SEO task backlog
Unresolved work only, highest priority first. IDs are stable; never reuse or renumber. Fixed items move to AUDIT.md status and WORKLOG.md.

| ID | Priority | Status | Label | Title | Review required |
|---|---|---|---|---|---|
| SEO-001 | critical | confirmed | Established | robots.txt disallows all crawlers in production config | yes (robots policy) |
```

## 4. WORKLOG.md entry (append only)

```markdown
## 2026-10-23T22:05:22+02:00 - <short title>
- Done: <what was inspected / changed / validated / deferred>
- Remaining: <what still needs attention>
- Blockers: <none | specific blocker>
- Findings: SEO-001, SEO-003
- Files changed: <paths, or none>
- Checks run: <exact commands/tools and results, or "not run: reason">
```
Helper: `python3 "/absolute/skill/path/scripts/init_audit_folder.py" --root "/absolute/project" log --folder "seo-optimization-work" --title ... --done ... --remaining ... --blockers ...`.

## 5. Folder README.md

Use the scaffold written by `init_audit_folder.py`, then fill in: project, audit folder path, audit date, platforms in scope, and the "how to continue" steps.

## 6. Closing chat message and task menu

Keep it short. Do not paste the whole audit. This menu is for audit-only requests. For authorized implementation, instead report changes, verification and unresolved decisions; do not ask the user to select already-authorized work again.

```markdown
**Audit saved to `seo-optimization-work/`** (AUDIT.md, TASKS.md, WORKLOG.md, README.md). Not checked: live site, Search Console, analytics.

**Summary:** <2-4 sentences: project type, platforms in scope, N findings (x critical, y high), biggest risk.>

**Which job should I tackle?**
1. SEO-001 - <title> (critical, Established) - <one-line outcome>; <needs your review | safe local fix>
2. SEO-004 - <title> (high, Supported but context-dependent) - ...
3. SEO-002 - <title> (high, Established) - ...
4. Other task - tell me what you'd like.

<If any assumptions block progress, list at most 2 open questions here.>
```
List at most 5 numbered tasks plus "Other task". Use finding IDs. Say plainly which options need your review before any change.
