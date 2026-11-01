# Codebase-first audit checklist

Work through the items that apply. For each, record: what you inspected (paths, commands), what you saw, and what you could not
check. Run only relevant checks; "not applicable" and "could not test" are valid outcomes. Evidence gaps are **not** defects.

## Contents
- 0. Orientation
- 1. Crawl access and indexability
- 2. Rendering and JavaScript
- 3. Metadata, headings, snippets
- 4. URLs, canonicals, redirects, status handling
- 5. Navigation, internal links, pagination, facets
- 6. Structured data
- 7. Images, mobile, accessibility
- 8. Performance (code evidence only)
- 9. International
- 10. Content quality and trust
- 11. Links and reputation
- 12. AEO: answer usability
- 13. GEO: crawler access and measurement readiness
- 14. Framework notes (verify against current docs)

Read `verification-playbook.md` for sampling and observable acceptance checks. Track checked / not applicable / not checked for each relevant area.

## 0. Orientation

1. Read every applicable instruction file first: `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `.cursor/rules`,
   `.github/copilot-instructions.md`, the README, and any global coding rules the environment provides.
2. Run `python3 "/absolute/skill/path/scripts/scan_repo.py" --root "/absolute/project/web-package"` (if Python is available) for a quick map and leads. Otherwise use `ls`, `find`,
   `git ls-files`, and `grep`/`rg`.
3. Infer project type, purpose, user journeys, templates and target platforms from evidence (routes, page copy, product
   models, locales, existing analytics/webmaster tags). Write unknowns as assumptions/open questions.
4. Identify the build/test/lint commands from `package.json` scripts, `Makefile`, CI config. Only run what is safe and local.

## 1. Crawl access and indexability
- `robots.txt` (static file or generated route): blanket `Disallow: /`, blocked CSS/JS/asset paths, missing `Sitemap:` line, per-bot groups.
- Remember: robots.txt blocks crawling, not indexing; a blocked page cannot show its `noindex`. It is not a privacy control.
- `noindex` via `<meta name="robots">`, `X-Robots-Tag` (check server/CDN config), framework metadata (`robots: { index: false }`).
- Staging-only directives leaking into production configuration (environment-conditional logic).
- Auth walls, cookie/consent walls, geo-blocking, bot-challenge or WAF rules that may deny crawlers (config only; note live behavior is untested).
- Sitemaps: generated or static; includes only canonical, indexable, 200 URLs; `lastmod` not auto-bumped on every build.

## 2. Rendering and JavaScript
- Rendering strategy per route type (SSR / SSG / CSR / hybrid): config flags, `use client` boundaries, `ssr: false`, `getServerSideProps`, `generateStaticParams`.
- Is the title, canonical, robots, main text, primary image and ordinary links in the server HTML, or injected after hydration?
- Content that needs clicks, scrolling, login, a consent gesture or a private API to appear.
- Client-side routers exposing real `href`s; SPA catch-all fallbacks that return a 200 shell for unknown paths (soft-404 risk).
- Duplicate structured data or metadata introduced by hydration.
- If a build/preview is possible, compare raw HTML (`curl` the local server) with rendered DOM.

## 3. Metadata, headings, snippets
- Title and description present and distinct per indexable template; not boilerplate repeated site-wide; not stale placeholders ("Untitled", "Home").
- One clear `<h1>`-level heading per page purpose and logical hierarchy. There is no evidence of a universal "exactly one H1" ranking rule: judge clarity and accessibility.
- `nosnippet` / `data-nosnippet` / `max-snippet` used only with a reason.
- Open Graph and social tags present and consistent with visible content (presentation, not a ranking factor).

## 4. URLs, canonicals, redirects, status handling
- Canonical: absolute, self-referencing where appropriate, matches internal links and sitemap, not pointing to errors/noindex targets, not all pointing to the home page.
- Redirect rules (`_redirects`, `vercel.json`, `next.config`, `.htaccess`, server config): permanent vs temporary, chains, loops, unrelated-to-home redirects.
- Trailing-slash and host/protocol conventions are consistent; HTTP-to-HTTPS handling.
- 404 handling returns a real 404/410 status, not a 200 "not found" page.
- Query parameters: tracking variants canonicalized; filters/sorts have an explicit strategy.

## 5. Navigation, internal links, pagination, facets
- Primary navigation and key pages reachable through ordinary `<a href>` links in rendered HTML; no `div onClick`, `href="#"`, or JS-only destinations for navigation.
- Descriptive anchor text; breadcrumbs where they help.
- Orphaned important pages (in routes/CMS but not linked from anywhere).
- Pagination exposes crawlable links; later pages not all canonicalized to page one.
- Faceted/filter URLs: control for crawl traps; blocked-by-robots pages cannot convey canonical/noindex.

## 6. Structured data
- Inventory types in use (JSON-LD, microdata) and where they are generated.
- Type matches page purpose; every marked-up value (price, rating, author, FAQ) is visible to users and accurate.
- Syntax valid (the scanner checks static JSON-LD only; templated blocks need rendered output).
- Eligibility checked against the platform's *current* feature gallery. Remember: FAQ rich results are restricted for most sites (Google, Aug 2023) and HowTo was curtailed; QAPage is for user-submitted answers.
- Markup never promises a rich result, ranking gain or citation.

## 7. Images, mobile, accessibility
- Meaningful `alt` for informative images; `alt=""` for decorative; no keyword stuffing.
- Width/height or aspect-ratio set; responsive variants; modern formats; main above-the-fold image not lazy-loaded.
- Mobile parity: the same primary content, metadata, structured data, links and alt text as desktop (Google indexes the mobile version first).
- Viewport meta; tap targets; keyboard operation; focus order; contrast; accessible names. WCAG 2.2 is the W3C standard.

## 8. Performance (code evidence only)
- Oversized hero images, render-blocking scripts/styles, heavy third-party tags, layout-shifting embeds, long main-thread work.
- Do **not** infer field Core Web Vitals from source. State "field data not checked". Thresholds (75th percentile): LCP <= 2.5 s, INP <= 200 ms, CLS <= 0.1.

## 9. International
- URL structure per language/region; reciprocal `hreflang` including self-reference; valid codes; `x-default` where useful; localized canonicals; no forced geo-redirects that hide alternatives.
- Machine-translated near-duplicates published without review.

## 10. Content quality and trust
- Each indexable page has a clear purpose and completes the task (product pages: what it is, fit, specs, price/availability, policies).
- Original information, first-hand experience, sources and dates for non-obvious claims; truthful author/reviewer info; review triggers for time-sensitive facts.
- Thin, duplicated or scaled template pages (location/city swaps, programmatic pages) and AI-generated content practices.
- Sensitive topics (health, legal, financial, safety): flag for qualified human review; do not rewrite claims.

## 11. Links and reputation
- Look for paid links without `rel="sponsored"`/`nofollow`, link-exchange pages, hidden links, keyword-stuffed footers, auto-generated guest-post anchors. Flag as policy-risky.
- Recommend only earned approaches (useful tools, original data, documentation, expert commentary).

## 12. AEO: answer usability
- For question-led pages: direct answer near the heading, caveats kept with the answer, descriptive question headings, tables/steps where they help.
- FAQ content serves readers; no rich-result promise. No universal ideal word count or "chunk size" is documented.
- Feature eligibility named per platform; markup validity and feature display treated separately.

## 13. GEO: crawler access and measurement readiness
- For each in-scope platform, check documented crawler tokens against robots.txt and any WAF/CDN rules: `Googlebot`, `Bingbot`, `OAI-SearchBot` (and distinct `GPTBot`, `ChatGPT-User`), `PerplexityBot` (and `Perplexity-User`). A rule for one token does not govern the others.
- Training-versus-search choices are the owner's decision; surface them as questions, never change them silently.
- Measurement readiness: Search Console and Bing Webmaster Tools verification tags present? Analytics able to segment AI referrers? Is there a documented prompt set? Mark absent items as **evidence gaps**.
- Keep impression, citation, mention and referral/conversion separate. No "AI rank" or "AI score".
- Unsupported special tactics (`llms.txt`, special "GEO schema", forced mentions) must not be presented as proven factors. Evidence-backed answer clarity, original information and entity consistency remain useful content practices, with platform/outcome limits stated.

## 14. Framework notes (verify against the current docs before recommending)
- **Next.js:** `metadata` / `generateMetadata`, `app/robots.ts`, `app/sitemap.ts`, `alternates.canonical`, `redirects()` in config, `use client` boundaries, `notFound()` status handling.
- **Nuxt:** `useSeoMeta` / `useHead`, `routeRules` (prerender, redirects, robots), `@nuxtjs/sitemap`-style modules.
- **Astro / Eleventy / Hugo / Jekyll:** layout `<head>` partials, front-matter title/description, generated sitemaps, permalink config.
- **SvelteKit / Remix / Angular:** per-route head APIs, prerender settings, SSR vs SPA mode.
- **WordPress:** theme `header.php` / `wp_head`, SEO plugin ownership of titles/canonicals/sitemaps (avoid duplicating what a plugin already does), permalink settings.
- **Shopify:** `theme.liquid`, `canonical_url`, collection/product URL duplicates, structured data generated by theme or apps.
- Confirm the framework's current documentation (version in lockfile) before stating how an API behaves.
