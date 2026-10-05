# Tailwind CSS Utility Patterns Reference

Comprehensive production-ready utility patterns, component blueprints, and version migration guidance for Tailwind CSS.

---

## 1. Common Layout Patterns

### Holy Grail Application Layout
Responsive 3-column layout with header, collapsible sidebar, fluid main content area, secondary panel, and sticky footer.

```html
<div class="flex min-h-screen flex-col bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
  <!-- Top Navigation Header -->
  <header class="sticky top-0 z-40 flex h-16 w-full items-center justify-between border-b border-slate-200 bg-white/80 px-4 backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/80 sm:px-6">
    <div class="flex items-center gap-4">
      <span class="text-lg font-bold tracking-tight">AppLogo</span>
    </div>
    <div class="flex items-center gap-3">
      <div class="h-8 w-8 rounded-full bg-slate-200 dark:bg-slate-700"></div>
    </div>
  </header>

  <div class="flex flex-1">
    <!-- Left Sidebar (Desktop persistent, hidden on mobile) -->
    <aside class="hidden w-64 flex-col border-r border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900 md:flex">
      <nav class="flex flex-1 flex-col gap-1 text-sm font-medium">
        <a href="#" class="flex items-center gap-3 rounded-lg bg-indigo-50 px-3 py-2 text-indigo-600 dark:bg-indigo-950/60 dark:text-indigo-400">Dashboard</a>
        <a href="#" class="flex items-center gap-3 rounded-lg px-3 py-2 text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800">Projects</a>
        <a href="#" class="flex items-center gap-3 rounded-lg px-3 py-2 text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800">Settings</a>
      </nav>
    </aside>

    <!-- Main Content Area -->
    <main class="flex-1 p-4 sm:p-6 lg:p-8">
      <div class="mx-auto max-w-7xl space-y-6">
        <h1 class="text-2xl font-bold tracking-tight sm:text-3xl">Dashboard</h1>
        <div class="h-96 rounded-xl border border-dashed border-slate-300 dark:border-slate-700"></div>
      </div>
    </main>

    <!-- Right Contextual Rail (Desktop extra-wide screens only) -->
    <aside class="hidden w-80 border-l border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900 xl:block">
      <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Activity</h2>
      <div class="mt-4 space-y-3">
        <div class="h-16 rounded-lg bg-slate-100 dark:bg-slate-800"></div>
        <div class="h-16 rounded-lg bg-slate-100 dark:bg-slate-800"></div>
      </div>
    </aside>
  </div>

  <!-- Footer -->
  <footer class="border-t border-slate-200 bg-white py-4 text-center text-xs text-slate-500 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-400">
    &copy; 2026 Modern Application. All rights reserved.
  </footer>
</div>
```

---

### Responsive Auto-Fit & Auto-Fill Grid
Automatically adjusts column count without explicit breakpoint declarations.

```html
<!-- Grid with automatic column sizing (minimum 280px per column) -->
<div class="grid grid-cols-[repeat(auto-fit,minmax(280px,1fr))] gap-6">
  <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">Card 1</div>
  <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">Card 2</div>
  <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">Card 3</div>
</div>
```

---

### Centered Hero Section with Dual Call-To-Action
Optimized for high-impact landing pages with fluid typography and balanced layout.

```html
<section class="relative overflow-hidden bg-slate-900 py-24 sm:py-32">
  <div class="mx-auto max-w-5xl px-6 text-center lg:px-8">
    <div class="inline-flex items-center gap-2 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-xs font-medium text-indigo-400">
      <span>What's new</span>
      <span class="h-1 w-1 rounded-full bg-indigo-400"></span>
      <span class="text-slate-300">Version 2.0 Released</span>
    </div>
    
    <h1 class="mt-6 text-4xl font-extrabold tracking-tight text-white sm:text-6xl sm:leading-tight">
      Build modern apps with <span class="bg-gradient-to-r from-indigo-400 via-sky-300 to-emerald-400 bg-clip-text text-transparent">effortless velocity</span>
    </h1>
    
    <p class="mx-auto mt-6 max-w-2xl text-lg text-slate-300 sm:text-xl sm:leading-8">
      A composable, production-ready utility design system built for speed, accessibility, and frictionless developer ergonomics.
    </p>
    
    <div class="mt-10 flex flex-wrap items-center justify-center gap-4">
      <a href="#" class="rounded-lg bg-indigo-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-600/30 hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500">
        Get Started Free
      </a>
      <a href="#" class="rounded-lg border border-slate-700 bg-slate-800/80 px-5 py-3 text-sm font-semibold text-slate-200 hover:bg-slate-800 hover:text-white">
        View Documentation &rarr;
      </a>
    </div>
  </div>
</section>
```

---

### Centered Modal Dialog with Backdrop Blur
Accessible overlay structure with responsive width and smooth layering.

```html
<div class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6" role="dialog" aria-modal="true">
  <!-- Backdrop -->
  <div class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm transition-opacity" aria-hidden="true"></div>

  <!-- Dialog Card -->
  <div class="relative w-full max-w-lg overflow-hidden rounded-2xl border border-slate-200 bg-white p-6 shadow-2xl dark:border-slate-800 dark:bg-slate-900">
    <div class="flex items-start justify-between gap-4">
      <div>
        <h3 class="text-lg font-semibold text-slate-900 dark:text-slate-100">Confirm Deletion</h3>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Are you sure you want to delete this resource? This action cannot be undone.
        </p>
      </div>
      <button type="button" class="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-200" aria-label="Close dialog">
        <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" /></svg>
      </button>
    </div>
    
    <div class="mt-6 flex justify-end gap-3">
      <button type="button" class="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800">
        Cancel
      </button>
      <button type="button" class="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600">
        Delete
      </button>
    </div>
  </div>
</div>
```

---

## 2. Form Styling Patterns

### Complete Accessible Form Group
Includes floating/standard label, input adornment icon, validation error state, and helper text.

```html
<div class="space-y-4 max-w-md">
  <!-- Text Input with Leading Icon -->
  <div class="space-y-1.5">
    <label for="email" class="block text-sm font-medium text-slate-700 dark:text-slate-300">
      Email Address
    </label>
    <div class="relative rounded-lg shadow-sm">
      <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
        <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
          <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
        </svg>
      </div>
      <input
        type="email"
        id="email"
        name="email"
        placeholder="you@domain.com"
        class="block w-full rounded-lg border border-slate-300 bg-white py-2.5 pl-10 pr-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-400 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:placeholder:text-slate-500 dark:focus:border-indigo-400 dark:focus:ring-indigo-400/20"
      />
    </div>
    <p class="text-xs text-slate-500 dark:text-slate-400">We'll never share your email with third parties.</p>
  </div>

  <!-- Error State Input -->
  <div class="space-y-1.5">
    <div class="flex justify-between">
      <label for="username" class="block text-sm font-medium text-slate-700 dark:text-slate-300">Username</label>
      <span class="text-xs text-rose-500">Required</span>
    </div>
    <input
      type="text"
      id="username"
      name="username"
      value="bad_handle!"
      aria-invalid="true"
      aria-describedby="username-error"
      class="block w-full rounded-lg border border-rose-500 bg-rose-50/30 py-2.5 px-3 text-sm text-rose-900 placeholder:text-rose-300 focus:border-rose-500 focus:outline-none focus:ring-2 focus:ring-rose-500/20 dark:border-rose-500 dark:bg-rose-950/20 dark:text-rose-200"
    />
    <p id="username-error" class="text-xs text-rose-600 dark:text-rose-400">Username can only contain alphanumeric characters.</p>
  </div>

  <!-- Custom Checkbox -->
  <div class="flex items-start gap-3">
    <div class="flex h-6 items-center">
      <input
        id="terms"
        name="terms"
        type="checkbox"
        class="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-2 focus:ring-indigo-500/20 dark:border-slate-700 dark:bg-slate-900 dark:ring-offset-slate-900"
      />
    </div>
    <div class="text-sm">
      <label for="terms" class="font-medium text-slate-700 dark:text-slate-300">Accept terms and conditions</label>
      <p class="text-xs text-slate-500 dark:text-slate-400">You agree to our privacy policy and terms of service.</p>
    </div>
  </div>

  <!-- Custom Toggle Switch (Pure Tailwind + Peer) -->
  <div class="flex items-center justify-between">
    <span class="text-sm font-medium text-slate-700 dark:text-slate-300">Enable email notifications</span>
    <label class="relative inline-flex cursor-pointer items-center">
      <input type="checkbox" class="peer sr-only" />
      <div class="h-6 w-11 rounded-full bg-slate-200 transition-colors after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:bg-white after:shadow-sm after:transition-all after:content-[''] peer-checked:bg-indigo-600 peer-checked:after:translate-x-full peer-focus-visible:ring-2 peer-focus-visible:ring-indigo-500/40 dark:bg-slate-700 dark:peer-checked:bg-indigo-500"></div>
    </label>
  </div>
</div>
```

---

## 3. Card, Button, and Badge Component Patterns

### Interactive Card with Hover Elevation and Accent Border
```html
<article class="group relative flex flex-col justify-between overflow-hidden rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-slate-300 hover:shadow-xl hover:shadow-slate-200/50 dark:border-slate-800 dark:bg-slate-900 dark:hover:border-slate-700 dark:hover:shadow-indigo-950/20">
  <div class="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-indigo-500 to-sky-500 opacity-0 transition-opacity duration-300 group-hover:opacity-100"></div>
  <div>
    <div class="flex items-center justify-between">
      <span class="inline-flex items-center gap-1.5 rounded-full bg-indigo-50 px-2.5 py-1 text-xs font-medium text-indigo-700 dark:bg-indigo-950/80 dark:text-indigo-300">
        <span class="h-1.5 w-1.5 rounded-full bg-indigo-500"></span>
        Infrastructure
      </span>
      <time class="text-xs text-slate-400">Oct 2026</time>
    </div>
    <h3 class="mt-4 text-lg font-semibold tracking-tight text-slate-900 group-hover:text-indigo-600 dark:text-slate-100 dark:group-hover:text-indigo-400">
      Zero-Config Continuous Deployments
    </h3>
    <p class="mt-2 text-sm leading-relaxed text-slate-600 dark:text-slate-400">
      Automate canary rollouts and instant rollbacks with distributed edge nodes worldwide.
    </p>
  </div>
  <div class="mt-6 flex items-center gap-2 text-sm font-semibold text-indigo-600 dark:text-indigo-400">
    <span>Read report</span>
    <span class="transition-transform duration-200 group-hover:translate-x-1">&rarr;</span>
  </div>
</article>
```

---

### Production Button Variant Suite
Consistent sizing, active compression, focus rings, and disabled behavior.

```html
<div class="flex flex-wrap items-center gap-3">
  <!-- Primary Solid -->
  <button type="button" class="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-indigo-500 active:scale-[0.98] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:pointer-events-none disabled:opacity-50">
    Primary
  </button>

  <!-- Secondary Neutral -->
  <button type="button" class="inline-flex items-center justify-center rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 active:scale-[0.98] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400 disabled:pointer-events-none disabled:opacity-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700/80">
    Secondary
  </button>

  <!-- Ghost Subtle -->
  <button type="button" class="inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-900 active:scale-[0.98] dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-100">
    Ghost
  </button>

  <!-- Destructive Danger -->
  <button type="button" class="inline-flex items-center justify-center rounded-lg bg-rose-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-rose-500 active:scale-[0.98] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-rose-600">
    Delete Resource
  </button>

  <!-- Loading State with SVG Spinner -->
  <button type="button" disabled class="inline-flex cursor-not-allowed items-center justify-center gap-2 rounded-lg bg-indigo-600/70 px-4 py-2 text-sm font-medium text-white">
    <svg class="h-4 w-4 animate-spin text-white" viewBox="0 0 24 24" fill="none">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    <span>Processing...</span>
  </button>
</div>
```

---

### Status Badges and Removable Chips
```html
<div class="flex flex-wrap items-center gap-2">
  <!-- Success Badge -->
  <span class="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-medium text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300">
    <span class="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
    Active
  </span>

  <!-- Warning Badge -->
  <span class="inline-flex items-center gap-1.5 rounded-full bg-amber-50 px-2.5 py-0.5 text-xs font-medium text-amber-700 dark:bg-amber-950/60 dark:text-amber-300">
    <span class="h-1.5 w-1.5 rounded-full bg-amber-500"></span>
    Pending
  </span>

  <!-- Error Badge -->
  <span class="inline-flex items-center gap-1.5 rounded-full bg-rose-50 px-2.5 py-0.5 text-xs font-medium text-rose-700 dark:bg-rose-950/60 dark:text-rose-300">
    <span class="h-1.5 w-1.5 rounded-full bg-rose-500"></span>
    Failed
  </span>

  <!-- Removable Chip -->
  <span class="inline-flex items-center gap-1 rounded-md border border-slate-200 bg-slate-50 py-1 pl-2.5 pr-1.5 text-xs font-medium text-slate-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300">
    <span>TypeScript</span>
    <button type="button" class="rounded p-0.5 text-slate-400 hover:bg-slate-200 hover:text-slate-600 dark:hover:bg-slate-700 dark:hover:text-slate-200" aria-label="Remove tag">
      <svg class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" /></svg>
    </button>
  </span>
</div>
```

---

## 4. Typography Patterns

### Multi-Line Truncation (Line Clamp)
```html
<p class="line-clamp-2 text-sm leading-relaxed text-slate-600 dark:text-slate-400">
  This is a long paragraph of text that will automatically be truncated with an ellipsis after exactly two lines across all browsers, preventing layout shifts or overflow bugs inside constrained card containers.
</p>
```

### Editorial Prose Article with Inversion
Requires `@tailwindcss/typography` plugin in v3, or native styling in v4.

```html
<article class="prose prose-slate max-w-none dark:prose-invert prose-headings:font-semibold prose-headings:tracking-tight prose-a:text-indigo-600 hover:prose-a:text-indigo-500 prose-img:rounded-xl">
  <h2>Architectural Overview</h2>
  <p>
    When structuring large-scale web applications, separating view primitives from dynamic business domains ensures long-term testability and code maintainability.
  </p>
  <blockquote>
    Good software architecture makes systems easy to understand, easy to develop, and easy to maintain.
  </blockquote>
  <ul>
    <li>Atomic design token consistency</li>
    <li>Zero runtime CSS style computation overhead</li>
    <li>Automated dead-code pruning during build steps</li>
  </ul>
</article>
```

### Metric Block / Stat Display
```html
<div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
  <dt class="truncate text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">
    Total Monthly Volume
  </dt>
  <dd class="mt-2 flex items-baseline gap-2">
    <span class="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-slate-100">$2,482,900</span>
    <span class="inline-flex items-baseline text-xs font-semibold text-emerald-600 dark:text-emerald-400">
      &uarr; 14.2%
    </span>
  </dd>
</div>
```

---

## 5. Gradient and Shadow Patterns

### Text and Background Gradients
```html
<!-- Text Gradient -->
<span class="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent font-black text-4xl">
  Hypercharged Velocity
</span>

<!-- Subtle Border Gradient Wrapper -->
<div class="rounded-2xl p-[1px] bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500">
  <div class="rounded-[15px] bg-slate-900 p-6 text-white">
    Content surrounded by an exact 1px gradient border.
  </div>
</div>
```

### Modern Elevation and Ambient Glow Shadows
```html
<!-- Soft Layered Shadow -->
<div class="rounded-xl bg-white p-6 shadow-[0_4px_20px_-4px_rgba(0,0,0,0.1),0_2px_4px_-2px_rgba(0,0,0,0.06)] dark:bg-slate-900">
  Elevated card with customized multi-layer ambient shadow.
</div>

<!-- Colored Glow Shadow on Hover -->
<button class="rounded-lg bg-indigo-600 px-5 py-2.5 font-medium text-white shadow-lg shadow-indigo-500/25 transition-all duration-200 hover:shadow-xl hover:shadow-indigo-500/40 hover:-translate-y-0.5">
  Glowing Button
</button>
```

---

## 6. Animation Keyframe Patterns

### Shimmer / Skeleton Loader
```html
<div class="relative overflow-hidden rounded-xl border border-slate-200 bg-slate-100 p-6 dark:border-slate-800 dark:bg-slate-800/50">
  <!-- Moving Shimmer Beam -->
  <div class="absolute inset-0 -translate-x-full animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-white/40 to-transparent dark:via-white/10"></div>
  
  <div class="space-y-3">
    <div class="h-4 w-2/5 rounded bg-slate-200 dark:bg-slate-700"></div>
    <div class="h-3 w-4/5 rounded bg-slate-200 dark:bg-slate-700"></div>
    <div class="h-3 w-3/5 rounded bg-slate-200 dark:bg-slate-700"></div>
  </div>
</div>
```

### Radar Ping Indicator
```html
<span class="relative flex h-3 w-3">
  <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
  <span class="relative inline-flex h-3 w-3 rounded-full bg-emerald-500"></span>
</span>
```

### Accordion Grid Collapse Pattern (Zero-JS Smooth CSS Height)
Using CSS grid `grid-template-rows: 0fr` to `1fr` to smoothly animate dynamic-height content without hardcoded max-heights.

```html
<div class="rounded-lg border border-slate-200 dark:border-slate-800">
  <label for="acc-toggle" class="flex cursor-pointer items-center justify-between p-4 font-medium">
    <span>Can I customize every utility token?</span>
    <span class="text-slate-400">+</span>
  </label>
  <input type="checkbox" id="acc-toggle" class="peer sr-only" />
  <div class="grid grid-rows-[0fr] transition-[grid-template-rows] duration-300 ease-out peer-checked:grid-rows-[1fr]">
    <div class="overflow-hidden">
      <div class="p-4 pt-0 text-sm text-slate-600 dark:text-slate-400">
        Yes! In both v3 and v4, tokens can be extended or completely replaced via the configuration layer.
      </div>
    </div>
  </div>
</div>
```

---

## 7. Tailwind CSS v3 vs v4 Migration Guide

### Architectural Differences

| Feature | Tailwind CSS v3 | Tailwind CSS v4 |
| :--- | :--- | :--- |
| **Config File** | `tailwind.config.js` or `tailwind.config.ts` | CSS-First: configured directly in CSS via `@theme` |
| **CSS Entry Point** | `@tailwind base; @tailwind components; @tailwind utilities;` | `@import "tailwindcss";` |
| **Compiler Engine** | JavaScript / PostCSS runtime | Rust-powered Oxide engine (lightning fast, standalone) |
| **Content Detection** | Manual glob array: `content: ['./src/**/*.{js,ts,jsx,tsx}']` | Automatic scanning of project workspace files |
| **Custom Utilities** | `plugin(({ addUtilities }) => ...)` in JS | Native `@utility utility-name { ... }` directive in CSS |
| **Custom Variants** | `plugin(({ addVariant }) => ...)` in JS | Native `@variant variant-name (&:hover, ...)` directive |
| **Color Space** | Standard sRGB (hex / rgb) | Modern OKLCH color space by default (wide gamut P3) |
| **Container Queries** | Requires `@tailwindcss/container-queries` plugin | Native `@container` and `@sm:`, `@md:` utilities included |

---

### Configuration Transformation Example

#### Tailwind v3 (`tailwind.config.ts`)
```typescript
import type { Config } from 'tailwindcss';

export default {
  content: ['./src/**/*.{ts,tsx,html}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef2ff',
          500: '#6366f1',
          900: '#312e81',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
} satisfies Config;
```

#### Tailwind v4 (`app/globals.css` / `src/index.css`)
```css
@import "tailwindcss";

@theme {
  --color-brand-50: oklch(0.97 0.02 260);
  --color-brand-500: oklch(0.60 0.22 260);
  --color-brand-900: oklch(0.35 0.18 260);
  --font-sans: "Inter", sans-serif;
}

/* Custom utility in v4 */
@utility text-balance {
  text-wrap: balance;
}

/* Custom variant in v4 */
@custom-variant pointer-fine (@media (pointer: fine));
```

---

### Step-by-Step Automated Migration

1. Run the official migration CLI:
   ```bash
   npx @tailwindcss/upgrade
   ```
2. The tool analyzes your project:
   - Migrates `tailwind.config.js` options into your main stylesheet.
   - Updates CSS imports from `@tailwind` to `@import "tailwindcss";`.
   - Renames deprecated utility names (e.g. `shadow-sm` token adjustments or obsolete opacity rules).
   - Updates build tool dependencies (e.g., swapping `tailwindcss` PostCSS plugin for `@tailwindcss/postcss` or `@tailwindcss/vite`).
3. Run test builds and verify visual output across key breakpoints.
