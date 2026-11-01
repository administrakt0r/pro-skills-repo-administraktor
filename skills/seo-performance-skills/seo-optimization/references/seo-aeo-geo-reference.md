# SEO, AEO, and GEO: an evidence-based practical reference

**Research date:** 23 October 2026  
**Purpose:** Source material for an AI agent skill that audits and improves real websites.  
**Maintenance note (2026-10-23):** This inherited research document is background, not a set of freshly verified instructions. Follow SKILL.md for authorization, workflow and evidence rules. Detailed report fields, dated rollout claims and study results require direct-source verification before use; see platform-evidence.md for verification limits.

**Use note:** Search features, crawler policies and tools change. Recheck primary documentation before acting on a live site.

## Platforms covered by available evidence

This document makes platform-specific claims only where public first-party evidence was available on the research date.

| Platform | Evidence available |
|---|---|
| Google Search, including AI Overviews and AI Mode | Search Central documents crawling, indexing, SEO fundamentals and generative Search. Search Console now documents a generative AI performance report for AI Overviews and AI Mode. |
| Bing Search, Microsoft Copilot, Bing AI summaries and selected partner integrations | Bing Webmaster Guidelines describe crawling, indexing, ranking, grounding and citations. Bing Webmaster Tools documents an AI Performance report. |
| ChatGPT Search | OpenAI documents OAI-SearchBot, robots controls and publisher guidance. It does not publish a complete source-selection formula. |
| Perplexity | Perplexity documents PerplexityBot and robots.txt behavior. Its public documentation does not establish a universal ranking recipe or guarantee citations. |
| GEO research | Includes the 2024 ACM SIGKDD study and newer empirical work, with limits stated below. |
| Other products, including standalone assistants without relevant public documentation | No platform-specific conclusions are generalized to them. Evidence for one product does not establish behavior for all AI systems. |

Recommendation labels indicate evidence strength, never a ranking guarantee:

- **Established** — documented by a platform, standard, or mature web practice.
- **Supported but context-dependent** — evidence exists, but outcomes vary by query, site, audience, or implementation.
- **Emerging** — new reports, platform features, or limited studies; recheck over time.
- **Speculative** — plausible claim without reliable causal evidence or platform documentation. Do not present it as a ranking factor.

## Table of contents

1. [Executive summary](#1-executive-summary)
2. [Foundations](#2-foundations)
3. [Technical SEO for modern web applications](#3-technical-seo-for-modern-web-applications)
4. [AEO: answer-focused search](#4-aeo-answer-focused-search)
5. [GEO: visibility in generative search](#5-geo-visibility-in-generative-search-and-answer-systems)
6. [Content and authority](#6-content-and-authority)
7. [Measurement and diagnosis](#7-measurement-and-diagnosis)
8. [Practical optimization workflow](#8-practical-optimization-workflow)
9. [Glossary](#9-glossary)
10. [Concise checklists](#10-concise-checklists)
11. [Annotated bibliography](#11-annotated-bibliography)
12. [Implications for an SEO optimization skill](#implications-for-an-seo-optimization-skill)

## 1. Executive summary

### Definitions and overlap

**SEO (search engine optimization)** improves the likelihood that a site can be discovered, crawled, understood, indexed, selected and presented usefully in search. It includes technical access, information architecture, content, reputation and measurement.

**AEO (answer engine optimization)** is an industry term for making useful answers easier to find and present in answer-focused experiences: featured snippets, voice responses, knowledge panels, AI Overviews and conversational search. There is no single formal AEO standard. Its defensible practices are conventional SEO plus clear answers and correct eligibility for specific features.

**GEO (generative engine optimization)** describes attempts to improve a source’s visibility, mention or citation in answers synthesized by generative systems. It has an academic definition, including the 2024 KDD paper, but no cross-platform standard. Systems can use live retrieval, indexes, cached or learned information, proprietary sources, or user-provided content in different combinations. Their selection processes are partly opaque.

The durable shared base is useful, accurate, distinctive information; technical accessibility; stable URLs and internal links; clear page purpose and entity facts; evidence for claims; maintenance; and measurement. Google says normal SEO best practices apply to AI Overviews and AI Mode and identifies no special GEO hacks. Bing says the same crawl/index/ranking foundations support grounding and citations.

### High-impact actions for a typical site

Priorities depend on business goals and site condition, but a useful starting order is:

1. **Define the audience, important actions, markets and target platforms.** Otherwise an agent can optimize the wrong traffic. **Established.**
2. **Fix access and indexability:** working responses, no accidental blocking/noindex, crawlable links, renderable main content, correct canonicals and a clean sitemap. **Established.**
3. **Make key pages satisfy real intent** with complete, accurate information and useful next steps. **Established.**
4. **Clarify information architecture** using coherent categories, descriptive titles/headings and internal links. **Established.**
5. **Improve search presentation** with distinct and accurate titles and descriptions, while recognizing search engines can rewrite them. **Established.**
6. **Use structured data only when it matches visible content and a currently supported feature.** It may enable eligibility; it does not guarantee a rich result, citation or ranking boost. **Established.**
7. **Check mobile, accessibility and real-user performance.** Fix barriers to users and content; Core Web Vitals are part of page experience, not a ranking shortcut. **Established / context-dependent.**
8. **For generative search, verify documented crawler controls and measure visibility per platform.** Crawl permission alone does not prove a page will be retrieved or cited. **Established for access controls; emerging for citation measurement.**

## 2. Foundations

### 2.1 Crawling, rendering, indexing, ranking and presentation

A useful diagnostic model:

1. **Discovery:** a crawler learns a URL from links, sitemaps, feeds or submissions.
2. **Crawling:** it requests the URL and resources subject to access rules, capacity and system priorities.
3. **Rendering and processing:** it parses HTML and may execute JavaScript, then extracts text, links, metadata, images and structured data.
4. **Canonicalization and indexing:** systems determine eligibility, topic, duplication and whether to retain a page.
5. **Retrieval and ranking:** for a query, a system selects and orders candidates using many signals. These vary by query and are proprietary.
6. **Presentation:** it may show a title, snippet, image, rich result or synthesized answer. Display text is not fully controlled by the site.

Google describes crawling, indexing and serving as distinct stages and says it does not guarantee that a page will be crawled, indexed or served. Its JavaScript documentation describes crawl and render queues. See [How Search works](https://developers.google.com/search/docs/fundamentals/how-search-works) and [JavaScript SEO basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics). **Established.**

**Example:** a URL returning 200 may still be absent because it is blocked, marked noindex, duplicate, rendered without useful content, or not selected for indexing. “It loads in my browser” proves only part of the pipeline.

### 2.2 Search intent and page purpose

Map a page to the visitor’s task: learn, compare, choose, buy, locate, troubleshoot or complete an action. Use customer questions, Search Console queries, internal site search, support requests and current result patterns. Avoid thin pages for wording variants that share one intent.

**Recommendation — established:** give each indexable page a clear purpose and enough information to complete the task. A product page should state what the product is, fit/compatibility, specifications, price/availability and relevant policies. Repeated generic copy does not answer product-specific questions.

Search intent is inferred, not proved by a keyword tool. Results can have mixed intent and vary by market, device and time. **Supported but context-dependent:** inspect the actual result types and user evidence before choosing a guide, category, product page or tool.

### 2.3 Helpful and reliable content

Google’s people-first guidance asks whether content provides original information, first-hand knowledge, completeness, clear sourcing and a satisfying result. Bing warns against scraped material without added value and auto-generated pages at scale without oversight. These are quality/policy guides, not deterministic ranking formulas.

**Strong example:** a repair guide identifies a model/version, explains a tested procedure, lists tools and safety constraints, cites the current manual and explains failure cases.

**Weak example:** a page paraphrases competitor articles, gives broad claims without sources, repeats target phrases and ends with a generic contact prompt.

**Common mistake:** treating “helpful” as “long.” Length follows the task. A simple fact may need two sentences; a safety procedure may require qualifications, steps and sources.

### 2.4 Information architecture and internal links

Organize content around stable topics and tasks. Important pages should be reachable through normal HTML links with descriptive anchor text. Connect hubs to useful detail and detail pages to relevant next steps. Internal links help people navigate and crawlers discover/contextualize pages; exact-match keyword anchors are unnecessary.

~~~html
<nav aria-label="Breadcrumb">
  <a href="/guides/">Guides</a> ›
  <a href="/guides/lighting/">Lighting</a> ›
  <span aria-current="page">Choosing a grow light</span>
</nav>
~~~

**Established:** use ordinary links with href destinations. A click handler on a div, href="#" or JavaScript-only destination may not expose a crawlable URL.

**Supported but context-dependent:** topic hubs help when they make coherent collections easier to use and add context. They are not a reason to create thin “SEO silo” pages.

### 2.5 URLs, canonicals, duplicate content and redirects

Keep URLs stable and readable. Choose a preferred HTTPS/host/slash convention; link internally to it. Duplicates commonly arise from tracking parameters, sorting, session IDs, host variants and alternate routes.

Use rel=canonical as a consolidation hint for substantially equivalent pages. Make it absolute and consistent with internal links and sitemap entries. Search engines can choose another canonical. Use a permanent redirect when a URL has actually moved. Do not redirect unrelated old pages to the home page.

~~~html
<link rel="canonical" href="https://example.com/guides/lighting/">
~~~

**Mistakes:** canonicalizing distinct language/product variants together; pointing every page to the home page; canonical targets that error or noindex; conflicting sitemap, internal-link and hreflang signals; using robots.txt to remove duplicates.

See [Google canonicalization guidance](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls). **Established.**

### 2.6 Metadata, headings and snippets

- **Title:** write concise, specific text that describes the page. Google may use the title, visible heading, prominent text, links and other sources to generate its title link. **Established.**
- **Meta description:** write a distinct, useful summary. Google may use it, but often builds a query-specific snippet from the page. There is no fixed universal character limit; display is truncated contextually. **Established.**
- **Headings:** use a clear main heading and logical subheadings. Hierarchy helps readers and assistive technology; there is no evidence that a rigid H1 count is a universal ranking lever. **Established for clarity/accessibility; context-dependent for SEO effect.**
- **Snippet controls:** nosnippet, max-snippet and data-nosnippet affect what Google can display. Use only with a clear reason.

~~~html
<title>How to choose a desk lamp for close-up work</title>
<meta name="description" content="Compare light output, color quality, arm reach, and glare control before choosing a lamp for detailed work.">
<h1>How to choose a desk lamp for close-up work</h1>
~~~

Keep title, visible page purpose and content aligned. See [title link guidance](https://developers.google.com/search/docs/appearance/title-link) and [snippet guidance](https://developers.google.com/search/docs/appearance/snippet).

### 2.7 Images and accessibility

Use relevant, high-quality images at suitable sizes and stable URLs. Compress and serve responsive variants. Add meaningful alt text for informative images; use empty alt text for decorative images. Describe function/content, not keyword lists. Put essential product/instructional facts in text too.

~~~html
<img src="/images/filter-installation.webp"
     alt="Carbon filter attached to the fan with the airflow arrow pointing toward the duct"
     width="960" height="640" loading="lazy">
~~~

Do not lazy-load the main above-the-fold image if that delays main content. Essential content should not require clicking or swiping to appear. Google says mobile-first indexing uses the mobile version. WCAG 2.2 is a W3C Recommendation, first published 5 October 2023 and revised 12 December 2024. See [WCAG 2.2](https://www.w3.org/TR/WCAG22/) and [Google image guidance](https://developers.google.com/search/docs/appearance/google-images). Accessibility benefits users beyond SEO. **Established.**

### 2.8 Structured data

Structured data is machine-readable markup, often JSON-LD using Schema.org vocabulary, that describes entities and page content. Search engines may use it to understand a page and, for supported types, make it eligible for a rich result. It does **not** guarantee indexing, rich display, citation or ranking improvement. Markup must match visible content and platform rules.

Select a type based on the page and the target platform’s current feature gallery. A real product page may use Product and Offer; editorial content may use Article; an organization page may use Organization. Do not mark a standard article as QAPage or invent ratings, prices, authors or FAQs that visitors cannot see.

~~~html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Example desk lamp",
  "image": ["https://example.com/lamp.webp"],
  "sku": "LAMP-01",
  "offers": {
    "@type": "Offer",
    "url": "https://example.com/products/lamp/",
    "priceCurrency": "EUR",
    "price": "49.90",
    "availability": "https://schema.org/InStock"
  }
}
</script>
~~~

Example only: values must match visible product facts and current policy. Use Google’s [supported data gallery](https://developers.google.com/search/docs/appearance/structured-data/search-gallery), [general policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies), [Rich Results Test](https://search.google.com/test/rich-results), and Search Console enhancement reports. The [Schema.org Validator](https://validator.schema.org/) checks vocabulary/graph structure, not Google eligibility. **Established.**

**FAQ markup caveat:** in August 2023 Google limited FAQ rich results to well-known authoritative government and health sites. FAQs can help people, but most sites should not expect Google FAQ rich results. HowTo results were also curtailed. See [Google’s announcement](https://developers.google.com/search/blog/2023/08/howto-faq-changes). Eligibility differs across engines. **Established, platform-specific.**

## 3. Technical SEO for modern web applications

### 3.1 Rendering models

| Model | How it works | Good fit | Main risk/control |
|---|---|---|---|
| Server-side rendering (SSR) | Server returns HTML per request. | Dynamic pages and frequently updated content. | Slow/failing origin or metadata only after hydration; test response before and after hydration. |
| Static generation (SSG) | HTML generated at build/publish time. | Marketing, docs, editorial and stable catalog pages. | Stale output if rebuilds fail; verify regeneration and sitemap updates. |
| Client-side rendering (CSR) | Browser JavaScript builds most content. | App-like or private experiences; can work for public pages if robust. | Delayed rendering, blocked scripts/APIs, blank HTML or incompatible crawlers. |
| Hybrid/incremental | Routes or portions use SSR, SSG, streaming or revalidation. | Common mixed-content sites. | Cache, hydration and route inconsistencies; test each representative route type. |

No rendering model automatically ranks better. The requirement is reliable, timely, crawler-accessible public content. Google can render JavaScript, but rendering is queued and resources must be accessible. Other crawlers may have different execution capability. **Established for Google; context-dependent for others.**

Portable pattern: render page title, canonical, robots, main text, primary image and ordinary links in server HTML; hydrate interactions afterward. If that is infeasible, test the actual crawler view and remove dependencies on login, clicks, consent gestures or fragile third-party APIs.

### 3.2 Routing, links and status codes

- Use stable, unique URLs for content that deserves search entry. SPA transitions should expose ordinary href links.
- Return 200 for real pages; 301/308 for permanent moves; 302/307 for temporary moves; 404/410 when content is gone.
- Avoid soft 404s: 200 responses that show “not found” or empty content.
- Redirect directly to the closest relevant replacement; avoid chains and loops.
- Keep query parameters purposeful. Canonicalize tracking variants; make an explicit strategy for filters/sorts.
- Avoid a SPA fallback returning the same 200 shell for every unknown path without page-specific content.

**Example:** if /products/old-model/ is replaced by /products/new-model/, serve a permanent redirect and ensure the destination is relevant, indexable and self-canonical. Do not return a generic homepage with 200 for the old path.

### 3.3 Robots, sitemaps and platform crawlers

robots.txt controls crawler access; it is not privacy protection or a reliable removal mechanism. A crawler blocked from a URL cannot read its noindex tag. To keep a page out of an index, allow crawling so noindex can be read, or require authentication for private content. Never rely on robots to protect sensitive public data.

~~~txt
User-agent: *
Disallow: /cart/
Disallow: /account/
Sitemap: https://example.com/sitemap.xml
~~~

This example needs site-specific review; blanket rules can block important assets/pages. A sitemap should contain canonical, indexable URLs that return successfully. It is a discovery hint, not a guarantee. Update lastmod only for material changes. Split large sitemaps within protocol limits and monitor errors.

Check controls per platform. OpenAI documents OAI-SearchBot for ChatGPT Search, distinct from GPTBot (training crawl) and ChatGPT-User (user-triggered). Perplexity documents PerplexityBot for search discovery and robots control. Bing uses Bingbot and describes its search/AI grounding foundation. Allowing any crawler does not guarantee indexing or citation. **Established for documented access controls.**

### 3.4 Pagination, facets and crawl traps

For paginated lists, provide crawlable next/previous links and distinct URLs where useful. Google does not rely on rel=next/prev as an indexing signal; crawlable links remain useful. Do not canonicalize every page to page one if later pages contain distinct items.

Faceted filters can create huge URL spaces. Index combinations only when they satisfy distinct demand with useful landing-page content. Control links and apply a coherent canonical/noindex/robots strategy to low-value permutations. Blocking crawling prevents engines from seeing noindex/canonical instructions. See [Google faceted navigation guidance](https://developers.google.com/search/docs/crawling-indexing/crawling-managing-faceted-navigation). **Established for crawl management; context-dependent for which facets to index.**

### 3.5 Lazy loading, hydration and interactive content

Lazy loading is useful for below-the-fold media when URLs remain discoverable. Do not require scrolling, clicking or typing to reveal essential text or links. Provide text equivalents for canvas/visual interfaces. Ensure hydration does not replace or contradict server output; avoid duplicate structured data before and after hydration.

If central value exists only behind authentication, a user action or private API, crawlers generally cannot index that private experience. Publish a public summary or landing page if suitable, while protecting personal data.

### 3.6 Mobile, performance and Core Web Vitals

Google primarily indexes the mobile version. Keep primary content, metadata, structured data, robots directives, alt text and links equivalent across mobile and desktop.

Current Core Web Vitals are LCP (loading), INP (responsiveness) and CLS (visual stability). Good field thresholds at the 75th percentile: LCP ≤2.5 seconds, INP ≤200 ms, CLS ≤0.1. Field data and lab tools answer different questions. Google says Core Web Vitals are used in ranking systems, but good scores alone do not ensure top rankings. See [web.dev thresholds](https://web.dev/articles/defining-core-web-vitals-thresholds) and [Google page experience](https://developers.google.com/search/docs/appearance/page-experience). **Established; ranking impact context-dependent.**

Fix actual bottlenecks: oversized hero image, render-blocking assets, slow backend, long main-thread tasks, unstable dimensions and excessive third-party code. Accessibility and performance both affect user experience but are not interchangeable.

### 3.7 Internationalization and hreflang

Use clear URLs for language/region versions, serve the intended language and add reciprocal hreflang references among equivalent pages, including self-reference. Use valid codes and self-canonicalize localized pages where appropriate. Do not redirect users/crawlers away from alternatives. Google says it detects language algorithmically; hreflang associates alternatives but does not guarantee ranking. See [localized versions guidance](https://developers.google.com/search/docs/specialty/international/localized-versions). **Established.**

~~~html
<link rel="alternate" hreflang="en-GB" href="https://example.com/en-gb/item/">
<link rel="alternate" hreflang="hr-HR" href="https://example.com/hr/item/">
<link rel="alternate" hreflang="x-default" href="https://example.com/item/">
~~~

Localize only where content, currency, availability, law or service fits the audience. Machine-translated near-duplicates without review can damage usefulness and trust.

### 3.8 Launch and troubleshooting tools

| Tool | Useful for | Cannot prove |
|---|---|---|
| curl/HTTP client and server logs | Status, redirects, headers, latency and requests. | Indexing or ranking. Spoofing a user-agent does not authenticate a bot. |
| Search Console URL Inspection/live test | Google indexed state and live fetch/render clues. | Guaranteed indexing/ranking or other platforms’ behavior. |
| Search Console indexing/sitemap reports | Aggregate exclusions and sitemap processing. | Exact cause for every URL or immediate updates. |
| Rich Results Test | Google-supported rich-result parsing and eligibility errors. | Display, ranking or other engines’ schema behavior. |
| Schema.org Validator | Vocabulary and graph inspection. | Google feature eligibility. |
| Bing Webmaster Tools | Bing crawl/index clues and AI Performance citations. | Google status, causal uplift or clicks from citations. |
| PageSpeed Insights/Lighthouse | Lab diagnostics and available CrUX field data. | Every visitor’s experience, crawlability or rank. |
| Devtools/rendered HTML | Hydration, layout, console and network failures. | How every crawler rendered the page. |
| Logs/site crawler | Bot requests, statuses, links, canonical/metadata patterns. | Whether a page was indexed or selected for a query. |
| Manual search/prompt set | Observed results/answers at a point in time. | Stable universal visibility; results vary by location, account, query and time. |

**Launch checklist**

1. Test each page template with raw HTTP and browser rendering.
2. Confirm status, redirects, HTTPS, and no soft 404s or loops.
3. Compare raw/rendered HTML: content, title, description, canonical, robots and links.
4. Test representative URLs in Search Console; distinguish live fetch from indexed state.
5. Check crawler access for Googlebot, Bingbot, OAI-SearchBot and PerplexityBot if in scope.
6. Validate sitemap URLs against canonicals and statuses; submit to relevant tools.
7. Validate structured data against visible content and target feature rules.
8. Check mobile layout, keyboard operation, image alternatives and field performance.
9. Test hreflang reciprocity and canonical behavior when relevant.
10. Monitor logs, coverage, queries, conversions and AI citation reports; submission is not proof of indexing.

## 4. AEO: answer-focused search

### 4.1 Answer structure

For question-focused pages, state the useful answer near the relevant heading, then add qualifications, explanation, steps, evidence and next action. This helps people scan. No public evidence establishes a universal ideal word count or chunk size for AI selection.

**Example**

> **How often should a reusable HVAC filter be checked?** Check monthly during the first season, then adjust for dust, pets, runtime and manufacturer instructions. Clean or replace it when visibly loaded or when pressure/airflow guidance says to; a calendar interval is only a starting point.

Why useful: the question is explicit, the first sentence answers directly, and the qualification prevents an unsafe universal rule. Use this format only when the page truly addresses that question.

### 4.2 Useful answer formats

- **Definition:** concise definition, boundaries and example.
- **How-to:** prerequisites, numbered steps, expected outcome, failure cases and safety notes.
- **Comparison:** criteria, like-for-like comparison, tradeoffs and dated conditions.
- **Product/service question:** exact model, compatibility, current price/availability and policies.
- **FAQ:** questions users actually ask; answers should add value beyond nearby text.

Use descriptive headings (“Can this adapter power a 4K monitor?”), keep answer and qualification together, and avoid burying a critical caveat elsewhere.

### 4.3 Features and eligibility

Answer interfaces may show snippets, featured answers, knowledge panels, local, product, image/video or generative results. Eligibility is platform- and content-specific. Structured data may support eligible features when correct; crawlability, visible content and quality remain important. Markup is not a request to show a particular answer.

Google’s FAQ rich-result restriction matters: most ordinary commercial/editorial sites should not expect FAQ rich results. QAPage is for a page where users can submit answers to one question, not a publisher-authored FAQ. Check the [supported feature gallery](https://developers.google.com/search/docs/appearance/structured-data/search-gallery). **Established, feature-specific.**

Google says AI Overview/AI Mode inclusion has no extra technical requirements or special markup beyond being indexed and eligible for a snippet. Its AI guide recommends effective SEO over artificial “chunking,” unnecessary llms.txt or inauthentic mentions. **Established for Google only.**

## 5. GEO: visibility in generative search and answer systems

### 5.1 What is known

GEO means efforts to improve a source’s chance of retrieval, selection, mention or citation in a generated answer. These outcomes differ. A model can mention a brand from learned knowledge without visiting its site; a system can fetch a page but not cite it; a citation may receive no click.

Public documentation establishes limited platform facts:

- Google says its AI Search features use core Search systems and indexed content; pages must meet normal technical requirements and be eligible for snippets. No special AI schema or additional SEO requirement is documented. Its Aug 2026 Search Console report measures impressions for AI Overviews and AI Mode.
- Bing says ordinary crawl/index/ranking foundations support grounding and citations. Its AI Performance report covers visible citations across Copilot, Bing AI summaries and selected partners. It explicitly says citations are not clicks and observational trends do not prove causation.
- OpenAI documents OAI-SearchBot for ChatGPT Search and says opting out excludes pages from Search answers, although navigational links may still appear. It does not publish the complete source ranking formula.
- Perplexity documents PerplexityBot for surfacing and linking websites. Crawler access is not a citation guarantee.

Aggarwal et al.’s 2024 KDD study tested content changes on benchmark generative engines and found some strategies, including statistics, citations and quotations, improved visibility in that setup. It is evidence from a particular benchmark, not a stable cross-platform factor. Newer research reports meaningful system/query variability. **Emerging.**

### 5.2 Tactic evidence table

| Proposed tactic | Evidence label | Practical use and boundary |
|---|---|---|
| Make pages crawlable/indexable for target platforms | **Established** | Check documented crawler access and search index. Access is eligibility, not citation. |
| Write clear, complete, accurate explanations | **Established / context-dependent** | Consistent with user needs and platform quality guidance. A fixed paragraph length is not a documented universal factor. |
| Cite reliable sources for non-obvious facts | **Supported but context-dependent** | Helps verification and trust. Citation count is not a documented universal boost. |
| Publish original data, tests, tools or firsthand experience | **Supported but context-dependent** | Differentiates a page and gives others a reason to cite it. Measure actual impact. |
| Keep brand/product/entity facts consistent | **Supported but context-dependent** | Reduces ambiguity for people and systems. Avoid fake entity pages or keyword boilerplate. |
| Use precise titles, headings, tables and definitions | **Supported but context-dependent** | Helps human scanning and structural clarity; no guaranteed citation result. |
| Earn credible third-party mentions | **Supported but context-dependent** | Can aid reputation, referral discovery and conventional link signals when editorially earned. Do not manufacture mentions. |
| Add llms.txt, special GEO schema or “AI-readable” feeds | **Speculative / platform-specific** | Google says unnecessary AI text files and special hacks are not required for Google AI Search. Use only with documented benefit or a controlled test. |
| Prompt-injection text, “according to experts” repetition, forced brand mentions | **Speculative / potentially harmful** | No robust evidence; can degrade usefulness or violate policy. Bing warns against AI manipulation and keyword stuffing. |

### 5.3 Retrieval, selection, citation and summary

A cautious conceptual model is: query interpretation → retrieval/grounding → candidate selection → synthesis → citation presentation. This is not a universal implementation diagram. Retrieval sources, ranking, personalization, cache timing and citation rules differ. Google describes RAG grounded in Search; Bing discusses grounding; OpenAI and Perplexity document crawlers but not full pipelines.

A page can fail at several points: no crawl, no index, poor query fit, a stronger competing source, summary without citation, or an answer based elsewhere. Site owners control access, quality and owned facts, not platform use or citation.

### 5.4 Measurement and testing

Separate four outcomes:

1. **Impression:** platform counted an eligible result/feature as shown. It does not prove a user read or clicked it.
2. **Attributed citation:** visible URL/source link. Record product, prompt/query, date, market, context, exact answer and link.
3. **Mention:** brand/source named without an attributed link. It may reflect learned facts, retrieval or inference; attribution is unknown.
4. **Referral/conversion:** analytics recorded a visit or action. Referrers can be lost through privacy settings, redirects, copy/paste or cross-device use.

Google Search Console reports AI Overview/AI Mode impressions, not a complete citation/click ledger. Bing AI Performance reports visible citation activity and says it does not measure clicks, rank, importance or causal effect. For ChatGPT and Perplexity, use available referral analytics and reproducible manual/API sampling; do not infer total visibility from a small tracker.

**Testing approach — emerging:** define representative prompts by intent (brand, non-brand problem, comparison, local/product), locale and target product. Repeat over time, record platform/version/context, save answers/citations and compare to baseline. Change one meaningful variable at a time when feasible; use matched pages or staggered rollout for stronger inference. Respect platform terms. Report sample size and uncertainty, not an invented “AI rank.”

## 6. Content and authority

### 6.1 Research and intent mapping

Combine Search Console, analytics conversions, customer interviews, support tickets, site search, product data and SERP inspection. Group by underlying task. Decide whether the need belongs on an existing page or warrants a distinct one. Prefer user evidence to keyword volume alone.

Before drafting, state audience, need, page type, evidence, differentiating contribution, next action and accuracy constraints. A keyword list alone is not a content plan.

### 6.2 Expertise, authorship and sources

Show the work behind claims: author/reviewer where useful, relevant qualifications or experience, methodology, source dates, scope, limitations and correction process. Cite primary references for regulations, safety, research, technical behavior and specifications. Do not fabricate bios, tests, reviews, customer quotes or credentials.

For health, legal, financial and safety subjects, require qualified human review, relevant jurisdiction/context, current primary sources and careful language. An agent can identify gaps and draft recommendations; it should not silently make consequential expert judgments.

### 6.3 Maintenance and AI-assisted content

Review pages when facts, products, laws, software versions, prices or service terms change. Update visible content and dateModified only after meaningful edits. Do not refresh dates as decoration. Before removal/consolidation, check traffic, links, conversions, legal retention and the best replacement.

AI can assist research, outlining, editing and translation. The publisher remains responsible for accuracy, originality, rights, privacy and usefulness. Google says AI use is not categorically disallowed; scaled unoriginal pages created primarily to manipulate results may violate its scaled-content-abuse policy. Human review is not a shield if the outcome remains misleading or valueless. **Established.**

**Strong workflow:** draft from verified sources; an expert adds real examples and checks facts; an editor checks originality, voice and usefulness; monitor after release.

**Weak workflow:** generate hundreds of near-identical location pages, swap city names, fabricate local knowledge and auto-publish with FAQ schema. This risks harm and violates stated quality policies.

### 6.4 Links, reputation and digital PR

Earn attention with useful tools, original data, reporting, expert commentary and documentation. Editorial links can help discovery and are part of how search systems understand the web. PR should earn coverage, not require followed links as payment.

Avoid buying links for ranking, automated networks, excessive reciprocal schemes, paid advertorial links passing ranking credit and mass guest posts with keyword-rich anchors. Google identifies these as link spam; qualify paid placements with sponsored or nofollow as appropriate. **Established.**

Third-party mentions may help reputation/entity understanding, but their effect on a specific AI answer is opaque. Treat citation-focused PR as an experiment, not a guaranteed GEO factor. **Emerging.**

## 7. Measurement and diagnosis

### 7.1 Match tools to questions

- **Search Console:** Google impressions, clicks, CTR, average position, query/page/device/country, indexing, URL inspection, sitemaps, enhancements, Core Web Vitals and AI report where available. Data is aggregated; it does not capture every search behavior.
- **Bing Webmaster Tools:** crawl/index diagnosis, sitemap and URL submission, site explorer and AI Performance.
- **Analytics:** sessions, landing pages, engagement and conversions; attribution is incomplete.
- **Server/CDN logs:** actual requests, status, latency and bot patterns. Verify bot identity using published IP/DNS methods where available; user-agent strings can be spoofed.
- **Site crawlers:** broken links, redirects, metadata, canonicals, hreflang and duplicate patterns. Rendering capability affects results.
- **Lighthouse/PageSpeed/CrUX:** lab diagnosis and available field performance data; neither alone proves crawler behavior.
- **Structured-data testing:** Rich Results Test for Google eligibility, Search Console after deployment, Schema.org Validator for vocabulary.
- **Manual queries/prompts:** qualitative evidence; save context and repeat.

### 7.2 Metrics and limits

| Metric | Tells you | Does not tell you |
|---|---|---|
| Impressions | A platform counted a result/feature as shown. | Attention, ranking quality or a click. Definitions vary. |
| Clicks | Recorded search clicks. | All search-influenced visits or conversions. |
| CTR | Clicks / impressions for a selected segment. | A stable page-quality score; affected by position, brand, snippets and SERP features. |
| Average position | Aggregated position for impressions. | One fixed rank for all users/queries or directly comparable query mixes. |
| Indexed pages | Pages reported/observed in an index. | Quality, future serving or whether all pages should be indexed. |
| Organic conversions | Actions attributed to organic sessions under analytics rules. | Incrementality or perfect attribution. |
| Referral visits | Visits attributed to a source. | All AI influence; referrers can be lost. |
| AI citations | Visible source attribution or platform report count. | Clicks, importance, stable rank or causal content impact. |
| AI mentions | Brand/page named in an answer. | Whether the site was retrieved or facts are correct. |

See [Search Console performance report help](https://support.google.com/webmasters/answer/7576553) for metric definitions. Do not compare incompatible properties, periods or query filters.

### 7.3 Diagnostic workflows

**Page not indexed**

1. Confirm intended canonical and whether an alternate URL is indexed.
2. Fetch status, redirects, robots, noindex, authentication and WAF/CDN behavior.
3. Compare raw/rendered content and crawlable links.
4. Check canonical consistency, duplicates, sitemap, internal links and user value.
5. Inspect in Google/Bing tools; distinguish live test from indexed state.
6. Fix the cause, submit/request recrawl if useful, and wait. Requests do not guarantee inclusion.

**Traffic decline**

1. Verify analytics/Search Console filters, time zone, tracking, consent and outages.
2. Compare equivalent periods; segment by type, country, device, query and landing page.
3. Separate impression decline (visibility/demand), CTR decline (presentation/competition) and conversion decline (landing/offer/tracking).
4. Check platform status, manual actions/security, releases, redirects, robots, canonicals, rendering and logs.
5. Compare demand and result features; inspect affected pages and credible competitors.
6. Change only after evidence identifies a likely cause; record uncertainty. See [Google traffic-drop diagnosis](https://developers.google.com/search/docs/monitor-debug/debugging-search-traffic-drops).

**Wrong title/snippet:** compare title, H1, prominent text, internal anchor text, meta description and external links. Align them, remove stale boilerplate, then allow recrawl; the engine may still choose alternate text.

**Wrong duplicate URL:** compare content, canonical, redirects, internal links, sitemap and hreflang. Choose intended canonical; redirect pages that truly moved; keep distinct pages distinct; remove conflicting signals.

**JavaScript content missing:** compare response with rendered DOM; inspect console/network; ensure scripts/APIs are not blocked and content does not require user action/session; consider SSR/SSG for essential public content; retest with URL Inspection and browser tools.

## 8. Practical optimization workflow

### Step 1 — Scope and goals
Establish business goal, audience, target action, countries/languages, target platforms, page types, constraints, available access and whether the agent may edit or only recommend. Do not assume Google is the only target.

### Step 2 — Inspect without changing
Inventory templates, URL patterns, navigation, important pages, robots/sitemaps, statuses, rendering, canonicals/hreflang/metadata, structured data, links, mobile and performance. Inspect representative routes and crawl samples. Note evidence gaps.

### Step 3 — Baseline
Record source and period for Google/Bing impressions, clicks, CTR, position, indexed URLs, organic sessions/conversions, CWV, logs and available AI citation/impression data. Keep cohorts consistent.

### Step 4 — Diagnose affected URLs
For each issue record evidence, URL/template, expected user/business impact, confidence, likely cause and evidence that would disprove it. Separate confirmed defects from hypotheses.

### Step 5 — Prioritize
Rank by expected impact, effort, confidence and risk. Fix access failures and broken high-value pages before speculative citation tactics.

### Step 6 — Recommend concretely
Every recommendation must state:

| Field | Required detail |
|---|---|
| Evidence | Source/tool, observation, date/range, URL examples. |
| Change | Specific implementation/copy recommendation. |
| Expected outcome | Metric or task expected to improve; no guarantee. |
| Label | Established, supported but context-dependent, emerging or speculative. |
| Risk | Traffic, conversion, legal, privacy, accessibility and content risk. |
| Validation | Checks and monitoring method. |
| Scope | Affected URLs/templates and exclusions. |

### Step 7 — Implement or prepare for review
Usually reversible: fix typos, add accurate alt text, repair broken links, improve a title/description while preserving intent, correct invalid schema values, or make visible content render reliably. Keep a diff and validate.

Human review required before URL migrations, broad canonical/noindex/robots changes, mass removal/consolidation, redirect maps, regulated claims, pricing/availability/legal terms, mass AI publishing or changes to sensitive content. Prepare impact analysis and concrete proposed edits first; do not silently make high-risk site-wide changes.

### Step 8 — Validate
Check status, raw/rendered HTML, mobile, crawl directives, canonical, links, schema-policy match, accessibility and performance. Test affected templates. For migrations, test full URL map, chains, canonicals, sitemap, internal links, analytics and rollback plan.

### Step 9 — Monitor
Record release date, cohort, baseline, expected lag, monitoring window and owner. Use tools matching the goal. Compare with a control where possible. Do not claim causation from coincident movement. Keep a changelog.

## 9. Glossary

| Term | Meaning |
|---|---|
| AEO | Answer engine optimization: a loose term for improving usefulness/eligibility in answer-focused search. |
| AI Overview / AI Mode | Google generative Search features that synthesize responses and may link supporting sources. |
| Canonical URL | Preferred representative URL for equivalent/duplicate content. |
| Citation | Visible source attribution/link; distinct from mention, impression or visit. |
| Crawl budget | Practical crawl rate/capacity allocated to a site; most small sites need no special crawl-budget work. |
| Crawler | Software requesting pages/resources to discover or process web content. |
| CTR | Click-through rate, clicks divided by impressions in a defined report. |
| GEO | Generative engine optimization: attempts to improve visibility in generative answers; no universal standard or guarantee. |
| Hreflang | Annotation of localized equivalent pages. |
| Indexing | Search engine storage/processing of pages; inclusion does not guarantee display. |
| INP | Interaction to Next Paint, Core Web Vital for responsiveness. |
| LCP | Largest Contentful Paint, Core Web Vital for loading. |
| Mention | Name appearing in an answer without necessarily linking a source. |
| Noindex | Directive asking a compliant engine not to index a page; crawler must be able to read it. |
| Rendering | Processing HTML/CSS/JavaScript/resources into interpretable page content. |
| Robots.txt | Crawler-access convention; not privacy or guaranteed de-indexing. |
| SEO | Search engine optimization: improving discovery, understanding, eligibility, presentation and outcomes. |
| SERP | Search engine results page. |
| Soft 404 | A missing/empty page that returns success status, often 200. |
| Structured data | Machine-readable description of entities/content, often Schema.org JSON-LD. |
| CLS | Cumulative Layout Shift, Core Web Vital for visual stability. |

## 10. Concise checklists

### Content
- [ ] Audience and page purpose are clear.
- [ ] Content adds useful evidence/experience beyond paraphrase.
- [ ] Important claims have sources, dates, scope and limits.
- [ ] Authors/reviewers and qualifications are truthful.
- [ ] The answer and its caveats are easy to find.
- [ ] Title, visible heading, content and markup agree.
- [ ] No fabricated evidence, keyword stuffing or scaled near-duplicates.
- [ ] Time-sensitive facts have a review trigger.

### Technical SEO
- [ ] Important URLs return intended status over HTTPS.
- [ ] Main content and links render without user interaction.
- [ ] No unintended robots block, noindex, auth wall or WAF denial.
- [ ] Canonicals, redirects, links, sitemap and hreflang agree.
- [ ] Facets/parameters do not create uncontrolled duplicate space.
- [ ] Mobile includes primary content and metadata.
- [ ] Images have proper alternatives, stable URLs and dimensions.
- [ ] Field CWV and accessibility issues are measured and addressed.

### AEO
- [ ] Real questions appear in descriptive headings where useful.
- [ ] Answers are clear and include needed context/caveats.
- [ ] FAQs serve readers; no rich-result promise is made.
- [ ] Schema matches visible content and an eligible feature.
- [ ] Markup validity and feature display are treated separately.

### GEO experiments
- [ ] Exact platform and feature are named.
- [ ] Crawler access and indexability are verified.
- [ ] Prompt set, locale, date and repetitions are recorded.
- [ ] Citation, mention, impression, referral and conversion are separate.
- [ ] Baseline/comparison exist and uncertainty is reported.
- [ ] No untested tactic is called causal.
- [ ] No prompt injection or manufactured mentions are used.

### Launch
- [ ] Raw/rendered response, status, headers, links, metadata and schema checked.
- [ ] Search platform URL inspection and reports checked on representative routes.
- [ ] Sitemap/robots correct for target crawlers.
- [ ] Mobile, keyboard, accessibility and performance reviewed.
- [ ] Migration maps, redirects, canonicals and hreflang reviewed.
- [ ] Analytics/conversion tracking works.
- [ ] Monitoring owner, baseline and follow-up date set.

## 11. Annotated bibliography

### Search fundamentals and technical guidance

1. [Google: How Search works](https://developers.google.com/search/docs/fundamentals/how-search-works) — Primary description of discovery, crawling, indexing and serving; states Google does not guarantee crawl, index or display. Living docs, accessed 23 Oct 2026.
2. [Google: Search Essentials](https://developers.google.com/search/docs/essentials) — Baseline technical requirements and spam policies.
3. [Google: JavaScript SEO basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics) and [troubleshooting](https://developers.google.com/search/docs/crawling-indexing/javascript/fix-search-javascript) — Rendering and JavaScript diagnostics.
4. [Google: Canonicals](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls), [robots.txt](https://developers.google.com/search/docs/crawling-indexing/robots/intro) and [sitemaps](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap) — Duplicate consolidation, crawler access and sitemap limits.
5. [Google: Helpful content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) — People-first content self-assessment, not a ranking formula.
6. [Google: Title links](https://developers.google.com/search/docs/appearance/title-link) and [snippets](https://developers.google.com/search/docs/appearance/snippet) — How titles/snippets are generated and may be rewritten.
7. [Google: Structured-data policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies) and [feature gallery](https://developers.google.com/search/docs/appearance/structured-data/search-gallery) — Feature-specific rules and eligibility.
8. [Google: Traffic-drop diagnosis](https://developers.google.com/search/docs/monitor-debug/debugging-search-traffic-drops) — Segmented troubleshooting guidance.
9. [Google: Page experience](https://developers.google.com/search/docs/appearance/page-experience) and [web.dev CWV thresholds](https://web.dev/articles/defining-core-web-vitals-thresholds) — Metrics and ranking caveats.
10. [W3C: WCAG 2.2](https://www.w3.org/TR/WCAG22/) — Accessibility standard; Recommendation dated 5 Oct 2023 and revised 12 Dec 2024.

### Bing and AI search documentation

11. [Bing Webmaster Guidelines](https://www.bing.com/webmasters/help/webmaster-guidelines-30fba23a) — Current guidance on discovery, indexing, ranking, grounding, citations and abuse.
12. [Bing AI Performance report](https://www.bing.com/webmasters/help/ai-performance-9f8e7d6c) — Citation measures and explicit measurement limits.
13. [Bing URL submission / IndexNow](https://www.bing.com/webmasters/help/URL-Submission-62f2860b) — Current submission options; submissions do not guarantee indexing.
14. [Google: AI features](https://developers.google.com/search/docs/appearance/ai-features) and [generative AI guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) — Normal SEO foundations apply; special requirements/hacks are not documented.
15. [Search Console generative AI report](https://support.google.com/webmasters/answer/16984139) — As of 31 Aug 2026, global report for AI Overview and AI Mode impressions; limited to documented surfaces and definitions.
16. [OpenAI: crawler overview](https://developers.openai.com/api/docs/bots) and [publisher FAQ](https://help.openai.com/en/articles/12627856-publishers-and-developers-faq) — Distinguishes OAI-SearchBot, GPTBot and ChatGPT-User; no full source-selection formula.
17. [Perplexity: crawler docs](https://docs.perplexity.ai/docs/resources/perplexity-crawlers) and [robots help](https://www.perplexity.ai/help-center/en/articles/10354969-how-does-perplexity-follow-robots-txt) — First-party crawler and access statements; recheck current policy.

### GEO research

18. Aggarwal et al., [“GEO: Generative Engine Optimization”](https://doi.org/10.1145/3637528.3671900), ACM SIGKDD 2024, pp. 5–16 — Peer-reviewed benchmark introducing GEO; results apply to its tested systems/prompts, not all current engines.
19. [“What Drives AI Citations? Content, Retrieval and Model Knowledge in GEO”](https://arxiv.org/abs/2610.15033), 2026 preprint — Large observational answer/citation collections; useful but not causal proof or platform disclosure.
20. [“From Citation Selection to Citation Absorption…”](https://arxiv.org/abs/2604.25707), 2026 preprint — Separates source selection from how cited material is reflected in answers; emerging framework.
21. [“How Generative AI Disrupts Search…”](https://arxiv.org/abs/2604.27790), 2026 preprint — Reports source and answer variation across Google Search, AI Overviews and Gemini in its benchmark; cautions against generalization.

## 12. Implications for an SEO optimization skill

The skill should behave as an evidence-driven auditor and implementation assistant, not a “rank me” copy generator.

### Principles
- Name target search engines and AI answer products before platform-specific conclusions.
- Treat SEO as shared technical/content foundations; AEO as answer usability and feature eligibility; GEO as platform-specific visibility with uncertainty.
- Label every recommendation with the four evidence levels and cite primary sources. Mark inference explicitly.
- Never promise rankings, indexing, rich results, citations, traffic or conversions.

### Workflow requirements
1. Establish business goals, users, locales and platform scope.
2. Inventory templates, URLs, technical access and key content.
3. Capture baseline data and date range.
4. Diagnose specific URLs with evidence.
5. Prioritize by impact, effort, confidence and risk.
6. For each recommendation show evidence, affected URLs, change, expected outcome, label, risk and validation.
7. Implement only authorized low-risk changes; prepare high-risk changes for human review.
8. Validate rendered output, platform tools, structured data, accessibility, performance and analytics.
9. Monitor and distinguish correlation from causation.

### Guardrails
- Human review for migrations, broad robots/canonical/noindex changes, mass removals, large-scale publishing and regulated/sensitive content.
- Never fabricate expertise, reviews, citations, product facts or legal/medical/financial claims.
- Do not recommend link buying, hidden text, keyword stuffing, prompt injection, fake mentions or scaled pages without added value.
- Explain that crawler access can affect retrieval eligibility but cannot guarantee citation.
- Prefer tests with baselines, cohorts and repeated observations over one-off screenshots or opaque “AI scores.”

### Validation criteria
Report completion only after verifying changed output, affected URLs, relevant tool checks and a monitoring plan. Separate implementation success from outcome success: a valid canonical is an implementation result; increased qualified conversions or citations is a later measured outcome.

