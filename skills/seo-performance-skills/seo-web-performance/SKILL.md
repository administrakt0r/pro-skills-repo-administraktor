---
name: seo-web-performance
description: >-
  Audits, fixes, and optimizes modern web applications for search engine optimization
  (SEO) and Core Web Vitals performance. Use when implementing meta tags, Open Graph,
  structured data (JSON-LD), XML sitemaps, robots.txt, asset delivery optimization
  (images, fonts, critical CSS, code splitting, compression), Lighthouse audits, or
  diagnosing and resolving LCP, INP, and CLS bottlenecks.
---

# SEO & Web Performance

Search Engine Optimization (SEO) and web performance are deeply interconnected: search crawlers prioritize fast, responsive, and semantically structured web pages. This skill provides an end-to-end playbook for implementing technical SEO foundations, optimizing the critical rendering path, delivering modern media formats, embedding rich structured data, and meeting Google's Core Web Vitals thresholds.

## When to Use

- Configuring or auditing search metadata (canonical tags, meta robots, Open Graph, Twitter cards).
- Structuring content with JSON-LD (Articles, Products, FAQs, Breadcrumbs).
- Generating XML sitemaps, sitemap indexes, or configuring `robots.txt`.
- Resolving Core Web Vitals regressions: Largest Contentful Paint (LCP), Interaction to Next Paint (INP), and Cumulative Layout Shift (CLS).
- Optimizing media assets (AVIF, WebP, responsive `srcset`, priority hints).
- Tuning web typography (WOFF2 self-hosting, `font-display: swap`, font preloading).
- Implementing critical CSS, script deferral, code splitting, and HTTP compression.
- Improving heading hierarchy, mobile-first indexing compliance, internal linking, and semantic HTML accessibility overlap.

## Prerequisites

- Node.js ($\ge 18$) or equivalent backend runtime.
- Lighthouse CLI installed globally or executed via `npx lighthouse`.
- Modern web build tooling (Vite, Webpack, Next.js, Astro, or standard HTML5/CSS/ESM pipeline).
- Access to server response headers or web server configuration (Nginx, Caddy, Apache, or CDN edge rules).

---

## Steps

### 1. Audit Performance and Indexing Baseline

Establish baseline metrics before modifying assets or code.

```bash
# Run Lighthouse audit in headless Chrome (Mobile preset)
npx lighthouse https://example.com \
  --output=json,html \
  --output-path=./reports/lighthouse-mobile \
  --form-factor=mobile \
  --screenEmulation.mobile \
  --throttling-method=simulate \
  --only-categories=performance,seo,accessibility,best-practices

# Inspect response headers and TTFB using curl
curl -Iv https://example.com
```

Key Lighthouse score thresholds to target:
- **Performance**: $\ge 90$
- **SEO**: 100
- **Accessibility**: $\ge 95$
- **Best Practices**: 100

---

### 2. Configure Technical Crawling (`robots.txt` & XML Sitemaps)

Ensure crawlers index only canonical public content and discover new pages efficiently.

#### `robots.txt` Configuration
Place in public root (`/public/robots.txt`):

```txt
User-agent: *
Allow: /
Disallow: /api/
Disallow: /admin/
Disallow: /private/
Disallow: /*?*sort=
Disallow: /*?*filter=

# Crawl delay (optional, for rate-limited servers)
# Crawl-delay: 2

# Direct link to Sitemap index
Sitemap: https://example.com/sitemap-index.xml
```

#### Sitemap Index and XML Sitemaps
Split large sites ($> 50,000$ URLs or $> 50\text{MB}$) into a sitemap index pointing to sub-sitemaps:

```xml
<!-- /public/sitemap-index.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://example.com/sitemaps/pages.xml</loc>
    <lastmod>2026-10-01T00:00:00Z</lastmod>
  </sitemap>
  <sitemap>
    <loc>https://example.com/sitemaps/posts.xml</loc>
    <lastmod>2026-10-05T12:00:00Z</lastmod>
  </sitemap>
</sitemapindex>
```

```xml
<!-- /public/sitemaps/pages.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/</loc>
    <lastmod>2026-10-05T00:00:00Z</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://example.com/pricing</loc>
    <lastmod>2026-10-01T00:00:00Z</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
```

---

### 3. Implement Meta Tags, Canonicalization, and Social Media Previews

Add essential document metadata into `<head>`:

```html
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  
  <!-- Primary Meta Tags -->
  <title>High Performance Web Architectures | Domain Insights</title>
  <meta name="title" content="High Performance Web Architectures | Domain Insights" />
  <meta name="description" content="Explore actionable patterns for sub-second page loads, Core Web Vitals optimization, and enterprise technical SEO." />
  <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1" />
  
  <!-- Canonical URL (strictly self-referencing on canonical pages) -->
  <link rel="canonical" href="https://example.com/articles/performance-guide" />

  <!-- Open Graph / Facebook -->
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://example.com/articles/performance-guide" />
  <meta property="og:title" content="High Performance Web Architectures | Domain Insights" />
  <meta property="og:description" content="Explore actionable patterns for sub-second page loads, Core Web Vitals optimization, and enterprise technical SEO." />
  <meta property="og:image" content="https://example.com/og/performance-guide-1200x630.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="Performance optimization benchmark chart" />
  <meta property="og:site_name" content="Domain Insights" />

  <!-- Twitter Cards -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:url" content="https://example.com/articles/performance-guide" />
  <meta name="twitter:title" content="High Performance Web Architectures | Domain Insights" />
  <meta name="twitter:description" content="Explore actionable patterns for sub-second page loads, Core Web Vitals optimization, and enterprise technical SEO." />
  <meta name="twitter:image" content="https://example.com/og/performance-guide-1200x630.png" />
</head>
```

---

### 4. Inject Structured Data (JSON-LD)

Structured data enables Google rich results. Inject via valid `<script type="application/ld+json">`.

#### Combined BreadcrumbList + Article / FAQ / Product Schema:
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "Home",
          "item": "https://example.com"
        },
        {
          "@type": "ListItem",
          "position": 2,
          "name": "Guides",
          "item": "https://example.com/guides"
        },
        {
          "@type": "ListItem",
          "position": 3,
          "name": "Performance",
          "item": "https://example.com/guides/performance"
        }
      ]
    },
    {
      "@type": "Article",
      "headline": "High Performance Web Architectures",
      "description": "Actionable patterns for sub-second page loads and technical SEO.",
      "image": ["https://example.com/og/performance-guide-1200x630.png"],
      "datePublished": "2026-10-01T08:00:00+00:00",
      "dateModified": "2026-10-05T14:30:00+00:00",
      "author": {
        "@type": "Person",
        "name": "Lead Engineer"
      },
      "publisher": {
        "@type": "Organization",
        "name": "Domain Insights",
        "logo": {
          "@type": "ImageObject",
          "url": "https://example.com/logo.png"
        }
      },
      "mainEntityOfPage": "https://example.com/guides/performance"
    },
    {
      "@type": "FAQPage",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "What is the recommended threshold for LCP?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "The recommended threshold for Largest Contentful Paint (LCP) is 2.5 seconds or less for at least 75 percent of page visits."
          }
        }
      ]
    }
  ]
}
</script>
```

---

### 5. Structure Semantic HTML, Heading Hierarchy, and Accessibility

Search crawlers build document outline trees from semantic elements and headings.

#### Semantic Outline Checklist
- One single `<h1>` per page reflecting the page's primary subject.
- Sequential headings (`<h2>` $\rightarrow$ `<h3>` $\rightarrow$ `<h4>`). Never skip levels (e.g., do not jump from `<h2>` to `<h4>`).
- Landmark tags: `<header>`, `<nav>`, `<main>`, `<article>`, `<aside>`, `<footer>`.
- Meaningful `alt` attributes on informative images; empty `alt=""` and `aria-hidden="true"` on decorative icons.
- Descriptive link anchor text: Avoid generic terms like "click here" or "read more". Use context-rich phrases: "View the comprehensive Core Web Vitals guide".

```html
<body>
  <header>
    <a href="#main-content" class="skip-link">Skip to main content</a>
    <nav aria-label="Main Navigation">
      <ul>
        <li><a href="/">Overview</a></li>
        <li><a href="/guides">Technical Guides</a></li>
      </ul>
    </nav>
  </header>

  <main id="main-content">
    <article>
      <header>
        <h1>Modern Web Performance Optimization Guide</h1>
        <p class="byline">Published on <time datetime="2026-10-01">October 1, 2026</time></p>
      </header>

      <section>
        <h2>Optimizing Largest Contentful Paint</h2>
        <p>LCP measures perceived load speed...</p>

        <h3>Eliminating Render-Blocking Resources</h3>
        <p>Stylesheets and scripts in the head...</p>
      </section>
    </article>
  </main>

  <footer>
    <p>&copy; 2026 Domain Insights. All rights reserved.</p>
  </footer>
</body>
```

---

### 6. Optimize Media Assets & Typography

Media assets represent over $60\%$ of total page weight on average.

#### Modern Responsive Image Pattern
Use modern formats (AVIF then WebP), responsive `srcset`, explicit dimensions to prevent CLS, and appropriate loading priorities:

```html
<!-- Above-the-fold Hero / LCP Image -->
<picture>
  <source
    type="image/avif"
    srcset="/assets/hero-480.avif 480w, /assets/hero-800.avif 800w, /assets/hero-1200.avif 1200w"
    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 80vw, 1200px"
  />
  <source
    type="image/webp"
    srcset="/assets/hero-480.webp 480w, /assets/hero-800.webp 800w, /assets/hero-1200.webp 1200w"
    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 80vw, 1200px"
  />
  <img
    src="/assets/hero-800.jpg"
    alt="Server rack telemetry dashboard showing sub-second response times"
    width="1200"
    height="675"
    fetchpriority="high"
    decoding="async"
  />
</picture>

<!-- Below-the-fold Image (Lazy loaded) -->
<img
  src="/assets/diagram.webp"
  alt="Architecture diagram of edge CDN distribution"
  width="800"
  height="450"
  loading="lazy"
  decoding="async"
/>
```

#### Self-Hosted Font Optimization
- Convert fonts to `.woff2` format (superior compression).
- Preload the primary above-the-fold font file.
- Use `font-display: swap` (or `font-display: optional` for zero CLS).

```html
<head>
  <!-- Preload primary font file -->
  <link
    rel="preload"
    href="/fonts/inter-latin-var.woff2"
    as="font"
    type="font/woff2"
    crossorigin
  />
  
  <style>
    @font-face {
      font-family: 'Inter';
      src: url('/fonts/inter-latin-var.woff2') format('woff2');
      font-weight: 100 900;
      font-style: normal;
      font-display: swap;
      unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC;
    }

    body {
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
  </style>
</head>
```

---

### 7. Optimize Critical Rendering Path, Code Splitting & Compression

Ensure the browser renders content with minimal blocking roundtrips.

#### Inlining Critical CSS and Deferring Non-Critical CSS
Extract above-the-fold styles and inline them directly in `<head>`. Load other styles asynchronously:

```html
<head>
  <!-- Critical CSS Inlined -->
  <style>
    :root { --font-sans: 'Inter', system-ui, sans-serif; }
    *, *::before, *::after { box-sizing: border-box; margin: 0; }
    body { font-family: var(--font-sans); line-height: 1.5; color: #111827; }
    .hero { min-height: 50vh; display: flex; flex-direction: column; justify-content: center; padding: 2rem; }
  </style>

  <!-- Non-critical Stylesheets Asynchronously Loaded -->
  <link rel="preload" href="/css/site-deferred.css" as="style" onload="this.onload=null;this.rel='stylesheet'" />
  <noscript><link rel="stylesheet" href="/css/site-deferred.css" /></noscript>

  <!-- Modern Module Scripts are automatically deferred -->
  <script type="module" src="/js/main.js"></script>
</head>
```

#### Web Server Compression & Caching Headers (Nginx Example)
```nginx
# Enable Brotli and Gzip compression
brotli on;
brotli_comp_level 6;
brotli_types text/plain text/css application/json application/javascript application/xml+rss image/svg+xml;

gzip on;
gzip_comp_level 6;
gzip_types text/plain text/css application/json application/javascript application/xml+rss image/svg+xml;

# Immutable long-term caching for hashed static assets
location ~* \.(?:css|js|woff2|avif|webp|png|jpe?g|svg)$ {
    expires 1y;
    add_header Cache-Control "public, max-age=31536000, immutable";
    access_log off;
}

# Short/revalidating cache for HTML entry points
location / {
    add_header Cache-Control "public, max-age=0, must-revalidate";
}
```

---

### 8. Implement Internal Linking and Mobile-First Indexing

Google crawls and evaluates pages primarily via its mobile smartphone crawler.

1. **Mobile Viewport Parity**: Ensure identical content, metadata, structured data, and navigation links exist on both mobile and desktop viewports. Do not hide primary text or links on mobile.
2. **Touch Targets**: Minimum $48\times 48\text{px}$ tap targets for buttons and interactive controls with at least $8\text{px}$ separation.
3. **Crawl Depth & Breadcrumbs**: Keep any important page reachable within 3 clicks of the homepage.
4. **Contextual Internal Links**: Use keyword-relevant descriptive anchors connecting related subtopics:
   ```html
   <!-- GOOD: Semantic, keyword-rich anchor text -->
   <p>To diagnose frame drops and input delay, refer to our <a href="/guides/inp-tuning">Interaction to Next Paint tuning guide</a>.</p>

   <!-- BAD: Generic link -->
   <p>To diagnose frame drops and input delay, click <a href="/guides/inp-tuning">here</a>.</p>
   ```

---

### 9. Remediate Core Web Vitals (LCP, INP, CLS)

Meet Google's 75th-percentile real-user thresholds:

- **LCP ($\le 2.5\text{s}$)**: Preload hero images with `fetchpriority="high"`, eliminate server TTFB delays, inline critical CSS, and avoid lazy loading above the fold.
- **INP ($\le 200\text{ms}$)**: Break JavaScript tasks exceeding $50\text{ms}$ using `scheduler.yield()` or microtask slicing, offload heavy data parsing to Web Workers, and debounce event listeners.
- **CLS ($\le 0.10$)**: Add explicit `width` and `height` or `aspect-ratio` to all images/videos/embeds, reserve slots for dynamic banners/ads, and use compositor-only CSS transforms (`transform`, `opacity`).

For comprehensive diagnostic scripts, attribution hooks, and step-by-step remediation patterns, refer to [Core Web Vitals Reference](references/core-web-vitals.md).

---

## Best Practices

- **Self-reference canonical URLs**: Every indexed page must provide a `<link rel="canonical">` to avoid duplicate-content penalties from query parameters or protocol variations.
- **Always provide dimensions for media**: Pre-allocate visual space with HTML attributes (`width`, `height`) or CSS `aspect-ratio` to guarantee zero layout shifts.
- **Serve next-generation image formats**: Use AVIF with WebP fallbacks; AVIF provides $20\text{--}50\%$ smaller file sizes compared to standard WebP/JPEG at equivalent visual fidelity.
- **Avoid hydration blocking**: In SSR/SSG frameworks, defer client-side hydration or use selective hydration (islands architecture) to prevent main-thread freezing.
- **Preserve semantic tag structure**: Use `<button>` for actions and `<a href="...">` for navigation; never use `<div onclick="...">`.

## Common Pitfalls

- **Setting `loading="lazy"` on LCP images**: Delays the start of the hero image download until after layout computation, severely degrading LCP.
- **Skipping heading levels**: Jumping from `<h1>` to `<h3>` breaks document hierarchy for screen readers and search crawlers.
- **Blocking Googlebot in `robots.txt`**: Unintentionally adding `Disallow: /assets/` or `Disallow: /*.js` prevents crawlers from rendering the page accurately.
- **Injecting layout-shifting ads or banners**: Inserting dynamic notification bars above the main header pushes content down after page load, directly ruining CLS.
- **Over-relying on client-side rendering (CSR) without SSR or pre-rendering**: Pure CSR requires crawlers to run a secondary JavaScript rendering pass, delaying indexing and often failing metadata extraction.

---

## Verification

Confirm implementation using automated and manual verification steps:

```bash
# 1. Verify robots.txt syntax and access
curl -sSL https://example.com/robots.txt | grep -E "User-agent|Disallow|Sitemap"

# 2. Verify XML sitemap status and schema validity
curl -Is https://example.com/sitemap-index.xml | head -n 1

# 3. Verify HTML metadata and JSON-LD schema
curl -sSL https://example.com | grep -E "<title|<meta name=\"description|<meta property=\"og:|<script type=\"application/ld\+json"

# 4. Check asset compression (Brotli 'br' or Gzip 'gzip')
curl -sSL -H "Accept-Encoding: br, gzip" -I https://example.com/assets/app.js | grep -i "content-encoding"

# 5. Execute headless Lighthouse audit for CWV metrics
npx lighthouse https://example.com \
  --output=json \
  --output-path=./reports/audit.json \
  --chrome-flags="--headless" \
  --quiet

# Inspect CWV metrics from report
node -e '
  const r = require("./reports/audit.json");
  const a = r.audits;
  console.log("LCP:", a["largest-contentful-paint"].displayValue);
  console.log("CLS:", a["cumulative-layout-shift"].displayValue);
  console.log("TBT/INP Proxy:", a["total-blocking-time"].displayValue);
  console.log("SEO Score:", r.categories.seo.score * 100);
  console.log("Perf Score:", r.categories.performance.score * 100);
'
```
