# Platform scope and evidence snapshot

Snapshot reviewed **2026-10-23**. Verification depth differs by source (see below). Search features, crawler policies and tools change:
**re-verify the primary source before relying on any row**, and record the date you checked it.

Use this file to decide which platforms are in scope and what can honestly be said about each. Never carry a conclusion from
one platform to another.

## Contents
1. How to choose platforms in scope
2. Evidence table
3. Verification notes and discrepancies
4. Research evidence (what it can and cannot show)
5. Things this snapshot could not verify

## 1. Choosing platforms in scope

Infer from repository evidence (target markets, existing `robots.txt` rules, analytics/webmaster verification tags,
`hreflang`, existing bot rules, docs that name platforms). Default scope when nothing says otherwise:
**Google Search (incl. AI Overviews / AI Mode) and Bing Search**, because they have first-party guidance and measurement tools.
Add ChatGPT Search and Perplexity for *crawler-access and measurement-readiness* checks only, because their public documentation
covers crawlers, not ranking or citation selection. Record the scope as an assumption if the repo does not state it.

## 2. Evidence table

| Platform | What first-party documentation establishes | What it does NOT establish | Primary sources |
|---|---|---|---|
| **Google Search, AI Overviews, AI Mode** | Normal SEO fundamentals apply; no additional requirements or special markup for AI features. To appear as a supporting link a page must be indexed and eligible for a snippet. Preview controls (`nosnippet`, `data-nosnippet`, `max-snippet`, `noindex`) can limit appearance. AI traffic is counted in Search Console totals. | Any selection formula; guaranteed inclusion or citation; value of `llms.txt` or "chunking". | [AI features and your website](https://developers.google.com/search/docs/appearance/ai-features) (living doc; one cached copy showed *last updated 2025-08-22*, so record your access date) |
| **Search Console generative AI reports** | Google Search Central announced dedicated Search Generative AI performance reports on **2026-06-03**: impressions inside generative AI features on Search (AI Overviews, AI Mode) and in Discover. | Clicks, rank, citations or causality. Availability per property may vary (rolled out in stages). | [Announcement](https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports); reference file cites [help page](https://support.google.com/webmasters/answer/16984139) |
| **Bing Search, Copilot, Bing AI summaries** | Bing Webmaster Guidelines describe crawl/index/ranking foundations that also support grounding and citations. Bing Webmaster Tools has an **AI Performance** report (public preview announced Feb 2026 per trade coverage) showing citations across Copilot, Bing AI summaries and selected partners. | Clicks, ranking, importance or causal effect of content changes. Preview status may have changed. | [Webmaster Guidelines](https://www.bing.com/webmasters/help/webmaster-guidelines-30fba23a), [AI Performance report](https://www.bing.com/webmasters/help/ai-performance-9f8e7d6c) (first-party pages listed in the reference; not re-fetched in this snapshot) |
| **ChatGPT Search (OpenAI)** | `OAI-SearchBot` surfaces sites in ChatGPT search; sites opted out are not shown in answers but may still appear as navigational links. `GPTBot` is a separate (training) crawler. `ChatGPT-User` is for user-initiated actions and robots.txt rules may not apply. robots.txt changes can take ~24 h to take effect. Published IP lists exist for verification. | Source selection or ranking formula; citation guarantee. | [OpenAI crawler overview](https://developers.openai.com/api/docs/bots), [GPTBot page](https://developers.openai.com/docs/gptbot) |
| **Perplexity** | `PerplexityBot` surfaces and links sites in results and honors robots.txt; Perplexity recommends allowing it plus its published IP ranges. `Perplexity-User` fetches on a user's request and generally ignores robots.txt. | Ranking recipe; citation guarantee. | [Perplexity crawlers](https://docs.perplexity.ai/docs/resources/perplexity-crawlers) |
| **Other assistants** (Claude, Gemini app, others) | Not covered. | Do not generalize. If one is in scope, find that vendor's first-party crawler/search documentation first and state when none exists. | n/a |

User-agent version numbers change (OpenAI pages showed 1.3 and 1.4). Match on the product token (`OAI-SearchBot`), not the version.

## 3. Verification notes and discrepancies

Maintenance recheck (2026-10-23): fetched Google AI-features guidance, the Google report announcement, OpenAI crawler overview, Perplexity crawler documentation, and the Bing help URL. Google AI guidance explicitly confirms no additional requirements or special schema; OpenAI documents independent search/training settings; Perplexity distinguishes bot and user retrieval. The Google announcement title resolves, but this recheck did not establish every report field. Bing returned a JavaScript application shell/localization bundle, not a readable report article: HTTP 200 is **not** confirmation of its claimed help content, report URL or limits. Treat the detailed report claims below as inherited background until the actual article/account is inspected. No account-level availability was checked.


- **Search Console generative AI report timing.** The reference file says the report is global "as of 31 Aug 2026". Google's own
  announcement is dated 2026-06-03 and trade coverage describes an initial rollout to a subset of sites. Treat availability as
  *check per property*; never assume the user can see it.
- **Google AI opt-out control.** Several secondary sources describe a new Search Console setting to opt out of AI Overviews / AI Mode / AI
  features in Discover without affecting classic Search. This was **not confirmed against a Google first-party page** in this
  snapshot. Label **Emerging**; read Google's documentation before ever recommending or describing it, and treat any use as a
  high-risk, user-approved change.
- **Bing AI Performance report.** Dates and "public preview" status come from trade coverage; the report's explicit limits (citations
  are not clicks; observational trends are not causation) come from the reference. Re-check Bing's page.
- **OpenAI/Perplexity** statements were read from first-party pages on the snapshot date. Secondary blogs add commentary (traffic
  shares, "block X to opt out of training") that is *not* used here.

## 4. Research evidence

| Source | Use it as | Do not use it as |
|---|---|---|
| Aggarwal et al., "GEO: Generative Engine Optimization", ACM SIGKDD 2024, [doi:10.1145/3637528.3671900](https://doi.org/10.1145/3637528.3671900) | Peer-reviewed benchmark in which some content strategies (e.g. adding statistics, citations, quotations) improved visibility on the tested generative engines and prompts. Label: **Emerging**. | Proof of a stable, cross-platform ranking or citation factor. |
| 2026 preprints listed in the reference (arXiv 2610.15033, 2604.25707, 2604.27790) | Observational or framework evidence that behavior varies by system and query. **Emerging**. | Causal proof or platform disclosure. **Not independently re-fetched in this snapshot**; open them before citing specifics. |

## 5. What this snapshot could not verify

- Bing report article content could not be verified from its JavaScript shell. The three 2026 arXiv preprints were not re-fetched.
- No first-party crawler documentation was checked for Anthropic, Google-Extended, Apple, or other vendors.
- Live availability of any report or setting for the user's own accounts.
