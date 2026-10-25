# Verification playbook

Use this alongside the checklist. These are observable checks, not a requirement to install tools or crawl the whole site.

## Build an evidence matrix

Record one row per sampled route: page type, environment, expected indexability, response status/final URL, raw HTML, rendered DOM (if available), canonical/robots, title/main content/links, schema, result and limitation. Include each affected template, important locale, pagination/filter behavior and one nonexistent route. For shared fixes, include an unchanged control route and all materially different consumers. Never invent URLs from file names without checking routing.

Example: a title exists only after hydration. Record what the raw response and DOM actually contain. This is a platform-dependent rendering risk, not proof that Google cannot index it. `use client` alone does not establish client-only rendering.

## Response and indexability

For a few authorized URLs, inspect GET response status, headers and body with a deadline and bounded download. HEAD alone is insufficient because servers can handle it differently. Inspect redirects one hop at a time, within scope, with a small hop limit. Record `X-Robots-Tag`, HTML robots (including bot-specific directives), canonical, content type, and actual page content. Inspect browser DOM separately where available. Conflicting directives and environment-dependent responses require investigation; do not assume the most permissive directive wins.

Confirm production versus staging intent before treating noindex/disallow as defects. Robots exclusion is not access control and cannot reliably remove an already indexed URL. A blocked crawler may not see noindex. A robots allow rule is only one layer: CDN/WAF, authentication, response and rendered content still matter.

## Metadata and URLs

Check computed values on real routes, not just strings in components. Confirm canonical targets use the approved host/base path, resolve successfully and fit the intended duplicate policy. Check inherited metadata and plugin ownership before adding tags. Canonicals are signals, not guaranteed directives. Do not force self-canonicals onto intentionally duplicated pages or translate every variant to the default language.

No fixed character count is a universal title/description limit. Assess accuracy, uniqueness, intent and display truncation risk. Missing meta keywords is not a defect. A description can affect presentation; engines may generate another snippet.

Sitemap checks: XML parsing, correct origin/base path, only intended canonical indexable URLs, real status checks on samples, truthful lastmod. For large sitemaps inspect indexes, shard limits and the generator. A valid sitemap does not prove discovery or indexing. Do not demand one for every small site as a critical fix.

## Structured data

Parse rendered JSON-LD (including arrays and @graph), then inspect vocabulary, required/recommended properties and visible-content consistency. Static regex failures can be template syntax. Serialize dynamic JSON safely for the HTML script context; use the framework/project's existing safe mechanism. Do not concatenate untrusted product or author strings into markup. Test quotes and an HTML-closing sequence in input when changing serialization.

Schema.org validity, current search-feature eligibility, and actual rich-result display are three different results. Verify current feature documentation; do not add FAQ/HowTo/QAPage or review markup indiscriminately. No fabricated ratings, authors or product facts. Keep verified stable entity identifiers consistent with existing site identity; do not invent external profiles.

## Content, AEO and GEO

Use actual user questions/intents evidenced by page purpose or available query data. Improve direct answers, definitions, comparison criteria, steps, source attribution, dates and relevant caveats when they help readers. Keep claims consistent across metadata, visible content and schema. Do not invent query demand, enforce arbitrary word counts, keyword density or snippet lengths, or rewrite every page into FAQs. Preserve intent, voice, localization and conversion paths.

For legitimate local businesses, check consistent public business details, location/service accuracy and relevant LocalBusiness subtypes. Do not expose private addresses or create fabricated city pages. For ecommerce check variants, availability, currency/prices and policy consistency. For documentation check versioned URLs and obsolete-page handling. Only audit applicable cases.

For AI access distinguish search crawlers, training crawlers and user-initiated retrieval; controls do not necessarily transfer between them. Google-Extended is not Googlebot and is not a control for inclusion in Google Search. Recheck first-party documentation before policy advice. Do not recommend opening all bots as a universal improvement.

## Performance and user experience

Field Core Web Vitals reflect real users, typically assessed at the 75th percentile; a lab run is diagnostic, not a field pass. Record tool/version, route, device/network settings and sample limitations. Standard good thresholds: LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1. Lighthouse's blocking-time metric is not a measured INP substitute. Do not infer a penalty or ranking gain from a score.

Inspect the actual mobile interaction, accessible navigation, informative/decorative image alternatives and page stability. Preserve accessibility and consent/privacy behavior while optimizing performance. Avoid blanket lazy-loading of probable LCP images or blindly preloading every asset.

## Measurements and stopping

Use authorized existing Search Console, Bing and analytics evidence when available. Record date range, timezone, filters, release date and affected URL cohort. Account for seasonality, demand shifts, lag and concurrent changes; compare to a suitable control where feasible. A reproducible AI prompt study records prompt, platform/model, date, locale, session conditions, repeated samples and cited URL. Manual observations do not establish universal citation share.

Stop expanding the audit once relevant categories have an honest coverage status and the authorized scope is addressed. If blocked, preserve evidence, mark unresolved checks explicitly, and complete independent safe work. Do not add speculative tasks to make the report appear thorough.
