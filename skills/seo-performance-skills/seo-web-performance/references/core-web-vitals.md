# Core Web Vitals Diagnostic & Remediation Guide

This reference provides in-depth diagnostic techniques, metric breakdowns, and production-tested code patterns for optimizing Google's Core Web Vitals (CWV): **Largest Contentful Paint (LCP)**, **Interaction to Next Paint (INP)**, and **Cumulative Layout Shift (CLS)**.

---

## 1. Metric Overview & Thresholds

Core Web Vitals are evaluated at the 75th percentile of page visits across mobile and desktop devices:

| Metric | Good (Green) | Needs Improvement (Amber) | Poor (Red) | Measurement Focus |
|---|---|---|---|---|
| **LCP** (Largest Contentful Paint) | $\le$ 2.5 s | 2.5 s – 4.0 s | > 4.0 s | Perceived loading speed (main content visible) |
| **INP** (Interaction to Next Paint) | $\le$ 200 ms | 200 ms – 500 ms | > 500 ms | Responsiveness to user input across session lifespan |
| **CLS** (Cumulative Layout Shift) | $\le$ 0.10 | 0.10 – 0.25 | > 0.25 | Visual stability (unexpected layout shifts) |

---

## 2. Largest Contentful Paint (LCP)

LCP marks the render time of the largest image, video poster, or text block visible within the viewport.

### 2.1 The 4 Sub-Part Breakdown

Total LCP time breaks down into four sequential phases:

```
[============================= Total LCP =============================]
[-- TTFB (≤ 40%) --][-- Load Delay (≤ 10%) --][-- Load Duration (≤ 40%) --][-- Render Delay (≤ 10%) --]
```

1. **Time to First Byte (TTFB)**: Time from navigation start until the browser receives the first byte of HTML. Target: $< 800\text{ ms}$.
2. **Resource Load Delay**: Time between TTFB and when the browser starts requesting the LCP resource. Target: as close to $0\text{ ms}$ as possible ($< 10\%$ of LCP).
3. **Resource Load Duration**: Time taken to fetch the LCP asset over the network. Target: $< 40\%$ of LCP budget.
4. **Element Render Delay**: Time between resource download completion and the element being painted on screen. Target: $< 100\text{ ms}$.

### 2.2 Diagnostics

#### In-Browser PerformanceObserver
Run this script in the browser console or bundle it in development to identify the LCP element and timing:

```javascript
const observer = new PerformanceObserver((entryList) => {
  const entries = entryList.getEntries();
  const lastEntry = entries[entries.length - 1];
  console.group('LCP Candidate Detected');
  console.log('LCP Time (ms):', Math.round(lastEntry.startTime));
  console.log('Element:', lastEntry.element);
  console.log('URL:', lastEntry.url);
  console.log('Size (px):', lastEntry.size);
  console.log('Entry Details:', lastEntry);
  console.groupEnd();
});
observer.observe({ type: 'largest-contentful-paint', buffered: true });
```

#### Chrome DevTools Analysis
1. Open **Performance** panel $\rightarrow$ check **Screenshots** and **Web Vitals**.
2. Run a CPU (4x slowdown) and Network (Fast 3G / Slow 4G) throttled recording.
3. Locate the `LCP` flag on the Timings track.
4. Check the **Summary** tab to see which phase consumed the most time (TTFB vs Resource Duration vs Render Delay).

### 2.3 Common Root Causes & Concrete Fixes

#### Issue A: High Resource Load Delay (Browser Discovers LCP Late)
- **Cause**: LCP image is defined inside external CSS (`background-image`), rendered dynamically by client-side JavaScript, or buried deep in the DOM.
- **Fix**: Preload the LCP resource in `<head>` with `fetchpriority="high"`.

```html
<!-- For a static single image -->
<link
  rel="preload"
  as="image"
  href="/images/hero-banner.avif"
  type="image/avif"
  fetchpriority="high"
/>

<!-- For responsive images matching viewport sizes -->
<link
  rel="preload"
  as="image"
  imagesrcset="/images/hero-480w.avif 480w, /images/hero-960w.avif 960w, /images/hero-1440w.avif 1440w"
  imagesizes="(max-width: 600px) 100vw, 1200px"
  fetchpriority="high"
/>
```

#### Issue B: Slow Resource Load Duration (Asset Too Large)
- **Cause**: Uncompressed PNG/JPEG, unoptimized dimensions, missing CDN edge caching.
- **Fix**: Serve next-gen formats (AVIF/WebP) with responsive `srcset` and proper compression:

```html
<picture>
  <source
    type="image/avif"
    srcset="/images/hero-400.avif 400w, /images/hero-800.avif 800w, /images/hero-1200.avif 1200w"
    sizes="(max-width: 768px) 100vw, 1200px"
  />
  <source
    type="image/webp"
    srcset="/images/hero-400.webp 400w, /images/hero-800.webp 800w, /images/hero-1200.webp 1200w"
    sizes="(max-width: 768px) 100vw, 1200px"
  />
  <img
    src="/images/hero-800.jpg"
    alt="Primary feature showcase banner"
    width="1200"
    height="675"
    fetchpriority="high"
    decoding="async"
  />
</picture>
```
*Never set `loading="lazy"` on an above-the-fold or LCP image.*

#### Issue C: High Element Render Delay (Render-Blocking Resources)
- **Cause**: Synchronous CSS stylesheets or scripts delaying HTML parsing and first paint.
- **Fix**: Inline critical CSS, defer non-critical CSS, and load JavaScript with `defer` or `type="module"`.

```html
<head>
  <!-- Inline critical above-the-fold layout styles -->
  <style>
    .hero-container { min-height: 400px; display: flex; align-items: center; }
    .hero-title { font-size: 2.5rem; line-height: 1.2; font-family: system-ui, sans-serif; }
  </style>

  <!-- Non-critical styles loaded asynchronously -->
  <link rel="preload" href="/css/non-critical.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
  <noscript><link rel="stylesheet" href="/css/non-critical.css"></noscript>

  <!-- Defer JavaScript execution -->
  <script src="/js/app.js" defer></script>
</head>
```

#### Issue D: High TTFB
- **Cause**: Uncached dynamic backend rendering, database query bottlenecks, geographic latency.
- **Fix**:
  - Implement edge caching via CDN (Cloudflare, Fastly, AWS CloudFront) with `Cache-Control: public, max-age=0, s-maxage=3600, stale-while-revalidate=86400`.
  - Use streaming server-side rendering (SSR) so the `<head>` flushes immediately while dynamic data streams down.

---

## 3. Interaction to Next Paint (INP)

INP measures responsiveness by observing the latency of all user clicks, taps, and keyboard presses throughout a visit. The page's score represents the longest interaction duration (with rare outlier filtering on high-interaction sessions).

### 3.1 The 3 Sub-Part Breakdown

```
[============================ Single Interaction ============================]
[-- Input Delay (Waiting) --][-- Processing Duration (Callbacks) --][-- Presentation Delay (Paint) --]
```

1. **Input Delay**: Background tasks blocking the main thread before the event listener starts executing.
2. **Processing Duration**: Time spent executing event handlers (`click`, `keydown`, `pointerdown`, etc.).
3. **Presentation Delay**: Time needed by the browser to recalculate styles, layout the page, composite layers, and paint the updated pixels.

### 3.2 Diagnostics

#### In-Browser PerformanceObserver for Interactions
```javascript
const inpObserver = new PerformanceObserver((entryList) => {
  for (const entry of entryList.getEntries()) {
    // Only look at event timing entries with duration
    if (entry.interactionId) {
      console.group(`Interaction Detected [ID: ${entry.interactionId}]`);
      console.log(`Interaction Type: ${entry.name}`);
      console.log(`Total Duration: ${Math.round(entry.duration)}ms`);
      console.log(`Input Delay: ${Math.round(entry.processingStart - entry.startTime)}ms`);
      console.log(`Processing Time: ${Math.round(entry.processingEnd - entry.processingStart)}ms`);
      console.log(`Presentation Delay: ${Math.round(entry.startTime + entry.duration - entry.processingEnd)}ms`);
      console.log('Target Element:', entry.target);
      console.groupEnd();
    }
  }
});
inpObserver.observe({ type: 'event', durationThreshold: 16, buffered: true });
```

### 3.3 Common Root Causes & Concrete Fixes

#### Issue A: Long Tasks Blocking Main Thread (High Input Delay)
- **Cause**: Third-party scripts, hydration bundles, or heavy computations holding the main thread for $> 50\text{ ms}$.
- **Fix**: Break monolithic tasks into smaller slices by yielding to the main thread.

```javascript
// Universal yielding helper: uses scheduler.yield() where available, falls back to setTimeout
function yieldToMain() {
  if ('scheduler' in window && 'yield' in window.scheduler) {
    return window.scheduler.yield();
  }
  return new Promise((resolve) => setTimeout(resolve, 0));
}

// Processing large dataset without freezing interaction response
async function processItemsInChunks(items, batchSize = 50) {
  for (let i = 0; i < items.length; i += batchSize) {
    const chunk = items.slice(i, i + batchSize);
    renderChunk(chunk);

    // Yield control back to browser to process pending user input & paint
    await yieldToMain();
  }
}
```

#### Issue B: Expensive Event Handlers (High Processing Duration)
- **Cause**: Heavy synchronous calculation, data formatting, or recursive filtering directly inside a `click` or `input` event listener.
- **Fix**: Move CPU-intensive work to a Web Worker, debounce rapid inputs, and update visual state immediately.

```javascript
// 1. Offload heavy computation to Web Worker
const searchWorker = new Worker(new URL('./search.worker.js', import.meta.url), { type: 'module' });

// 2. Debounced handler with immediate visual feedback
function debounce(fn, delayMs = 150) {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delayMs);
  };
}

const inputEl = document.querySelector('#filter-input');
const spinnerEl = document.querySelector('#filter-spinner');

inputEl.addEventListener('input', (event) => {
  // Immediate visual feedback (low input/processing delay)
  spinnerEl.classList.remove('hidden');

  // Deferred heavy processing
  debouncedSearch(event.target.value);
});

const debouncedSearch = debounce((query) => {
  searchWorker.postMessage({ query });
});

searchWorker.onmessage = (event) => {
  spinnerEl.classList.add('hidden');
  renderResults(event.data.results);
};
```

#### Issue C: Large DOM Mutating & Layout Thrashing (High Presentation Delay)
- **Cause**: Reading layout geometries (`offsetHeight`, `getBoundingClientRect()`) followed immediately by style mutations in a loop, or rendering thousands of nodes at once.
- **Fix**:
  - Virtualize long lists so only visible items are rendered.
  - Batch DOM reads before DOM writes.
  - Use `requestAnimationFrame` for animations.

```javascript
// Anti-pattern (causes Forced Synchronous Layout / Layout Thrashing):
// elements.forEach(el => {
//   const width = el.offsetWidth; // READ
//   el.style.width = (width * 1.5) + 'px'; // WRITE
// });

// Correct Pattern: Batch Reads, then Batch Writes
function resizeElementsSafely(elements) {
  // Step 1: Batch all reads
  const widths = elements.map((el) => el.offsetWidth);

  // Step 2: Batch all writes inside requestAnimationFrame
  requestAnimationFrame(() => {
    elements.forEach((el, index) => {
      el.style.width = `${widths[index] * 1.5}px`;
    });
  });
}
```

---

## 4. Cumulative Layout Shift (CLS)

CLS measures the sum total of all unexpected layout shift scores that occur during the entire lifespan of the page.

### 4.1 Layout Shift Score Formula
$$\text{Layout Shift Score} = \text{Impact Fraction} \times \text{Distance Fraction}$$
- **Impact Fraction**: Proportion of the viewport area affected by the unstable elements.
- **Distance Fraction**: Greatest distance the unstable element moved relative to viewport height or width.
- Layout shifts within $500\text{ ms}$ of user input have the `hadRecentInput` flag set to true and are excluded from CLS.

### 4.2 Diagnostics

#### In-Browser PerformanceObserver for Shifts
```javascript
let clsScore = 0;
const clsObserver = new PerformanceObserver((entryList) => {
  for (const entry of entryList.getEntries()) {
    // Only count shifts that were NOT triggered by user interaction
    if (!entry.hadRecentInput) {
      clsScore += entry.value;
      console.group(`Layout Shift (+${entry.value.toFixed(4)}) | Running Total: ${clsScore.toFixed(4)}`);
      for (const source of entry.sources) {
        console.log('Shifted Element:', source.node);
        console.log('Previous Rect:', source.previousRect);
        console.log('Current Rect:', source.currentRect);
      }
      console.groupEnd();
    }
  }
});
clsObserver.observe({ type: 'layout-shift', buffered: true });
```

### 4.3 Common Root Causes & Concrete Fixes

#### Issue A: Images & Media Without Defined Dimensions
- **Cause**: Browser reserves 0 height until the image downloads and decodes, violently pushing subsequent content down.
- **Fix**: Always specify `width` and `height` attributes on HTML `<img>`, `<video>`, and `<iframe>` tags or define CSS `aspect-ratio`.

```html
<!-- Native HTML attributes allow the browser to compute aspect-ratio before image downloads -->
<img
  src="/images/product.webp"
  alt="Wireless noise-canceling headphones"
  width="800"
  height="600"
  style="width: 100%; height: auto;"
/>

<!-- Or in CSS -->
<style>
  .responsive-banner {
    width: 100%;
    aspect-ratio: 16 / 9;
    object-fit: cover;
  }
</style>
```

#### Issue B: Dynamically Injected Content (Ads, Banners, Embeds)
- **Cause**: Cookie notices, marketing alert banners, or ads injected into the page without reserved slots.
- **Fix**: Reserve minimum dimensions using CSS `min-height` or skeleton placeholders.

```html
<style>
  .ad-slot-container {
    min-height: 250px;
    background-color: #f3f4f6;
    display: flex;
    align-items: center;
    justify-content: center;
    contain: layout style;
  }
  .ad-slot-container::before {
    content: "Advertisement";
    font-size: 0.75rem;
    color: #9ca3af;
  }
</style>

<div class="ad-slot-container" id="leaderboard-ad">
  <!-- Ad script mounts into pre-reserved container -->
</div>
```

#### Issue C: Web Fonts Causing FOIT / FOUT
- **Cause**: Fallback font renders with different glyph metrics than custom web font. When the web font loads, line wraps and element heights shift.
- **Fix**: Use `font-display: optional` or align metrics using `@font-face` overrides (`size-adjust`, `ascent-override`, `descent-override`).

```css
@font-face {
  font-family: 'CustomSans';
  src: url('/fonts/custom-sans.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}

/* Fallback font tuned to match CustomSans dimensions */
@font-face {
  font-family: 'CustomSans-Fallback';
  src: local('Arial');
  ascent-override: 95%;
  descent-override: 25%;
  line-gap-override: 0%;
  size-adjust: 100.5%;
}

body {
  font-family: 'CustomSans', 'CustomSans-Fallback', sans-serif;
}
```

#### Issue D: Animations Triggering Layout Recalculation
- **Cause**: Animating CSS properties like `top`, `bottom`, `left`, `right`, `margin`, `padding`, or `height`.
- **Fix**: Use compositor-only properties (`transform` and `opacity`).

```css
/* BAD: Causes layout recalculation on every frame */
.drawer-bad {
  transition: height 0.3s ease;
  height: 0;
}
.drawer-bad.open {
  height: 300px;
}

/* GOOD: GPU-accelerated transform, zero layout shift */
.drawer-good {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform: translateY(-100%);
  will-change: transform;
}
.drawer-good.open {
  transform: translateY(0);
}
```

---

## 5. Production Real User Monitoring (RUM) Implementation

Integrate the official `web-vitals` library (v4) with metric attribution for real-time diagnostics:

```javascript
import { onCLS, onINP, onLCP, onFCP, onTTFB } from 'web-vitals/attribution';

const ANALYTICS_ENDPOINT = '/api/telemetry/vitals';

function sendToAnalytics({ name, value, rating, id, attribution }) {
  const payload = {
    metric: name,
    value: Math.round(name === 'CLS' ? value * 1000 : value) / (name === 'CLS' ? 1000 : 1),
    rating, // 'good' | 'needs-improvement' | 'poor'
    id,     // unique metric instance ID
    path: window.location.pathname,
    connection: navigator.connection ? navigator.connection.effectiveType : 'unknown',
    deviceMemory: navigator.deviceMemory || 'unknown',
    timestamp: Date.now(),
    attributionDetails: {}
  };

  // Extract actionable attribution context based on metric
  if (name === 'LCP' && attribution) {
    payload.attributionDetails = {
      element: attribution.element,
      url: attribution.url,
      timeToFirstByte: Math.round(attribution.timeToFirstByte),
      resourceLoadDelay: Math.round(attribution.resourceLoadDelay),
      resourceLoadDuration: Math.round(attribution.resourceLoadDuration),
      elementRenderDelay: Math.round(attribution.elementRenderDelay)
    };
  } else if (name === 'INP' && attribution) {
    payload.attributionDetails = {
      interactionTarget: attribution.interactionTarget,
      interactionType: attribution.interactionType,
      inputDelay: Math.round(attribution.inputDelay),
      processingDuration: Math.round(attribution.processingDuration),
      presentationDelay: Math.round(attribution.presentationDelay)
    };
  } else if (name === 'CLS' && attribution) {
    payload.attributionDetails = {
      largestShiftTarget: attribution.largestShiftTarget,
      largestShiftTime: attribution.largestShiftTime,
      largestShiftValue: attribution.largestShiftValue
    };
  }

  const blob = new Blob([JSON.stringify(payload)], { type: 'application/json' });
  if (navigator.sendBeacon) {
    navigator.sendBeacon(ANALYTICS_ENDPOINT, blob);
  } else {
    fetch(ANALYTICS_ENDPOINT, { method: 'POST', body: blob, keepalive: true });
  }
}

// Subscribe to all Web Vitals
onCLS(sendToAnalytics);
onINP(sendToAnalytics);
onLCP(sendToAnalytics);
onFCP(sendToAnalytics);
onTTFB(sendToAnalytics);
```
