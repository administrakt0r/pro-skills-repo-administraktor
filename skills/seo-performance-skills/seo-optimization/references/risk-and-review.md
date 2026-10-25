# Risk boundaries and review proposals

## Safe to implement within an authorized improvement request
Local, reversible, claim-preserving fixes, when repository rules permit:
- correct a broken internal link; fix an obvious metadata typo; add accurate alt text for an image whose content is clear from context;
- repair a structured-data **syntax** error without changing the claims it makes;
- improve a title/description while preserving intent and factual claims.
Keep the diff small, run the repo's relevant checks, and log the result.

Existing explicit authorization remains valid. Inspect shared consumers before classifying a change as local. Rendering architecture changes require assessment of runtime, caching and data exposure.

## Requires a concrete proposal and any missing owner authorization
- URL migrations, domain/host/protocol changes, large redirect maps, broad permalink changes.
- Site-wide `robots.txt`, `noindex`, canonical, hreflang or sitemap **policy** changes (including AI-crawler allow/block decisions).
- Large-scale removal, consolidation or rewriting of content; mass publishing or automated page generation.
- Legal, medical, financial, safety, pricing, product-availability or other sensitive claims.
- Anything that could materially affect conversions, indexing, access, privacy or user rights.

Do not ask for approval until the proposal below is complete and inspectable. After approval, still implement in small, reviewable steps.

## Proposal template (`evidence/proposal-SEO-NNN.md` or inside the finding)
```
# Proposal SEO-NNN: <title>
Date: <ISO 8601 with timezone>   Status: proposed / approved / rejected / implemented
Label: Established | Supported but context-dependent | Emerging | Speculative

## Problem and evidence
<files, URLs, observed behavior, tool output, sources with dates>

## Proposed change
<exact edits or rules; before/after examples>

## Scope
Affected URLs/templates: <list or pattern, with counts>   Exclusions: <list>

## Expected outcome and metric
<what could improve and which metric would show it; no guarantee; expected lag>

## Risk analysis
Traffic / indexing:   Conversion:   Accessibility:   Privacy / legal:   Content:
Likelihood and impact of each, and what would indicate trouble early.

## Validation plan
<exact checks: status codes, raw vs rendered HTML, canonical/robots, redirect map test, sitemap vs canonicals, analytics, tools to run>

## Rollback
<how to revert: commit(s), config flag, redirect removal, timing window>

## Monitoring
Owner:   Baseline (source, period):   Window:   Follow-up date:

## Open questions for the reviewer
```
For migrations also include: the full old-to-new URL map (or the rule generating it), chain/loop test results, canonical and hreflang
updates, internal-link updates, sitemap update, analytics continuity, and a launch/rollback runbook.
