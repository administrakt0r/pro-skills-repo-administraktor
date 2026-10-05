---
name: tailwind-css-development
description: >-
  Build, style, and maintain modern responsive web interfaces using Tailwind CSS across versions 3 and 4.
  Use when designing responsive layouts, configuring design tokens, implementing dark mode, structuring reusable
  components with clsx and tailwind-merge, creating animations, or managing v3 and v4 configurations in frontend applications.
---

# Tailwind CSS Development

Tailwind CSS is a utility-first CSS framework that composes atomic utility classes directly within markup. Rather than writing ad-hoc CSS stylesheets and inventing arbitrary class names, developers assemble UIs using structured design constraints for spacing, color, typography, elevation, and layout. This eliminates stylesheet bloat, prevents CSS regression cascades across features, and dramatically speeds up UI iteration.

For detailed UI component recipes, responsive layout templates, and syntax migration tables, consult [utility-patterns.md](references/utility-patterns.md).

## When to Use

- Building or restyling user interfaces using atomic utility classes.
- Structuring responsive layouts with mobile-first breakpoints (`sm`, `md`, `lg`, `xl`, `2xl`) or container queries (`@container`).
- Implementing theme toggling (system-preference media queries vs manual class/attribute-based dark mode).
- Managing design tokens (custom color palettes, font stacks, spacing scales, and custom shadows) in Tailwind v3 (`tailwind.config.ts`) or v4 (`@theme`).
- Creating resilient, reusable component primitives in React, Next.js, Vue, or Svelte with class merging (`cn()`, `clsx`, `tailwind-merge`).
- Deciding between template component extraction and `@apply` CSS abstractions.
- Adding micro-interactions, CSS transitions, and keyframe animations.
- Upgrading codebases between Tailwind CSS v3 and Tailwind CSS v4.

## Prerequisites

- **Runtime & Package Manager**: Node.js (v18.0.0 or higher) with `npm`, `pnpm`, `yarn`, or `bun`.
- **Build Tool / Framework**: Vite, Next.js, Astro, PostCSS, or Tailwind CLI.
- **Core Dependencies**:
  - Tailwind v4: `tailwindcss` (v4.x) and `@tailwindcss/vite` (or `@tailwindcss/postcss`).
  - Tailwind v3: `tailwindcss` (v3.x), `postcss`, and `autoprefixer`.
  - Component Utilities: `clsx` and `tailwind-merge` for robust conditional class composition.

---

## Steps

### 1. Detect Tailwind Version and Architecture

Determine whether the project is on Tailwind CSS v3 (JavaScript-first) or v4 (CSS-first Oxide engine):

1. Check `package.json` dependencies for `tailwindcss`:
   - `^3.x.x`: Uses `tailwind.config.js` or `tailwind.config.ts`, PostCSS, and `@tailwind` directives.
   - `^4.x.x`: Uses CSS-first configuration (`@import "tailwindcss";`), `@theme`, and build tool plugins like `@tailwindcss/vite`.
2. Inspect CSS entry points (`src/index.css`, `app/globals.css`, or `styles/main.css`):
   - v3 Entry:
     ```css
     @tailwind base;
     @tailwind components;
     @tailwind utilities;
     ```
   - v4 Entry:
     ```css
     @import "tailwindcss";
     ```

To install Tailwind in a new project:

```bash
# For Tailwind CSS v4 (Modern Default)
npm install tailwindcss @tailwindcss/postcss postcss
# Or in a Vite project:
npm install tailwindcss @tailwindcss/vite

# For Tailwind CSS v3 (Legacy/LTS)
npm install -D tailwindcss@^3 postcss autoprefixer
npx tailwindcss init -p # Generates tailwind.config.js and postcss.config.js
```

---

### 2. Configure Design Tokens (Theme, Colors, Fonts, Spacing)

Design tokens define the constraint system for the application. Always extend rather than overwrite default tokens unless an intentional reset is required.

#### Tailwind CSS v3 Configuration (`tailwind.config.ts`)

```typescript
import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class', // 'media' for system default, 'class' for manual toggle
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0fdf4',
          500: '#22c55e',
          900: '#14532d',
        },
        surface: {
          light: '#ffffff',
          dark: '#0f172a',
        },
      },
      fontFamily: {
        sans: ['var(--font-sans)', 'system-ui', 'sans-serif'],
        display: ['var(--font-heading)', 'serif'],
      },
      spacing: {
        '128': '32rem',
        '144': '36rem',
      },
      borderRadius: {
        '4xl': '2rem',
      },
    },
  },
  plugins: [],
};

export default config;
```

#### Tailwind CSS v4 Configuration (CSS-First `@theme`)

In Tailwind v4, configure tokens directly inside your CSS file without a separate JS file:

```css
@import "tailwindcss";

@theme {
  /* Colors (Modern OKLCH color space supported) */
  --color-brand-50: oklch(0.97 0.05 140);
  --color-brand-500: oklch(0.70 0.20 140);
  --color-brand-900: oklch(0.35 0.15 140);

  /* Fonts */
  --font-sans: var(--font-sans), system-ui, sans-serif;
  --font-display: var(--font-heading), serif;

  /* Custom Spacing */
  --spacing-128: 32rem;

  /* Breakpoints */
  --breakpoint-3xl: 1920px;
}
```

#### Arbitrary Values and Properties
When a design requires a one-off value not in the design system, use bracket syntax:

```html
<!-- Arbitrary values -->
<div class="top-[117px] bg-[#1da1f2] p-[clamp(1rem,5vw,3rem)]">
  <!-- Arbitrary properties -->
  <div class="[mask-type:alpha] [clip-path:polygon(0_0,100%_0,100%_75%,0_100%)]">
    Arbitrary CSS
  </div>
</div>
```

---

### 3. Implement Mobile-First Responsive Design & Container Queries

Tailwind is **mobile-first** by default. Unprefixed utilities apply to all screen widths, while breakpoint prefixes apply at that breakpoint and above.

| Breakpoint | Minimum Width | CSS Media Query |
| :--- | :--- | :--- |
| `sm` | 640px | `@media (min-width: 640px) { ... }` |
| `md` | 768px | `@media (min-width: 768px) { ... }` |
| `lg` | 1024px | `@media (min-width: 1024px) { ... }` |
| `xl` | 1280px | `@media (min-width: 1280px) { ... }` |
| `2xl` | 1536px | `@media (min-width: 1536px) { ... }` |

#### Responsive Rule of Thumb
- **Do**: `<div class="w-full md:w-1/2 lg:w-1/3">` (Mobile full, tablet half, desktop third).
- **Don't**: `<div class="w-1/3 max-md:w-full">` (Avoid negative/max modifiers unless strictly necessary).

```html
<!-- Mobile-first responsive card layout -->
<div class="flex flex-col gap-4 p-4 sm:flex-row sm:items-center sm:justify-between sm:p-6 lg:p-8">
  <div>
    <h2 class="text-lg font-bold sm:text-xl lg:text-2xl">Project Velocity</h2>
    <p class="text-sm text-slate-500 sm:text-base">Track delivery metrics over time.</p>
  </div>
  <button class="w-full rounded-lg bg-indigo-600 px-4 py-2 text-white sm:w-auto">
    Export Data
  </button>
</div>
```

#### Container Queries
Style elements based on the width of their parent container rather than the browser viewport:

1. In Tailwind v3, install `@tailwindcss/container-queries`. In Tailwind v4, container queries are built-in.
2. Mark the parent with `@container`.
3. Style children using `@sm:`, `@md:`, `@lg:`, `@xl:`, etc.

```html
<!-- Parent marked as a query container -->
<div class="@container w-full max-w-2xl rounded-xl border border-slate-200 p-4">
  <div class="flex flex-col gap-4 @md:flex-row @md:items-center">
    <div class="h-20 w-20 rounded-lg bg-indigo-500 @md:h-28 @md:w-28"></div>
    <div class="flex-1">
      <h3 class="text-base font-bold @md:text-xl">Container Adaptive Card</h3>
      <p class="text-sm text-slate-600 @md:text-base">Refits layout when parent resizes.</p>
    </div>
  </div>
</div>
```

---

### 4. Implement Dark Mode Strategies

Choose between `media` (automatically matches user OS system preference) or `class` / `selector` (allows in-app toggling via theme switchers).

#### Strategy A: In-App Toggle (`class` strategy - Recommended for apps)

1. Configure dark mode mode in v3:
   ```javascript
   // tailwind.config.ts
   darkMode: 'class', // or ['selector', '[data-theme="dark"]']
   ```
2. Configure dark mode in v4:
   ```css
   /* In v4, class strategy can be configured with a custom variant */
   @custom-variant dark (&:where(.dark, .dark *));
   ```
3. Use the `dark:` prefix:
   ```html
   <div class="bg-white text-slate-900 dark:bg-slate-900 dark:text-slate-100">
     <h1 class="text-slate-800 dark:text-white">Theme-aware Content</h1>
     <p class="text-slate-600 dark:text-slate-400">Works seamlessly in light and dark mode.</p>
   </div>
   ```

#### Theme Variables Architecture (Semantic Tokens)
Instead of littering markup with duplicate `dark:` utilities on every element, use CSS variables for semantic surfaces:

```css
:root {
  --bg-page: #ffffff;
  --bg-card: #f8fafc;
  --text-main: #0f172a;
  --border-subtle: #e2e8f0;
}

.dark {
  --bg-page: #0b0f19;
  --bg-card: #111827;
  --text-main: #f8fafc;
  --border-subtle: #1f2937;
}
```

Map variables to Tailwind tokens:
```css
/* Tailwind v4 */
@theme {
  --color-page: var(--bg-page);
  --color-card: var(--bg-card);
  --color-main: var(--text-main);
  --color-subtle: var(--border-subtle);
}
```
Now `<div class="bg-card text-main border-subtle">` automatically switches palettes with zero modifier overhead.

---

### 5. Component Extraction & Dynamic Class Merging

#### The Golden Rule: Template Extraction vs `@apply`

| Scenario | Best Approach | Why |
| :--- | :--- | :--- |
| Framework components (React, Vue, Svelte, Astro) | **Component Extraction** | Preserves utility visibility, keeps bundle minimal, leverages TypeScript types |
| Dynamic state, variant props, size modifiers | **`clsx` + `tailwind-merge`** | Handles conflicting utility overrides cleanly without CSS specificity wars |
| Multi-element third-party HTML (Markdown/CMS) | **`@tailwindcss/typography` (`prose`)** | Avoids manually tagging injected HTML |
| Highly repetitive global base elements (`input`, `button` resets) | **`@layer base` or `@utility`** | Single point of normalization |
| *Anti-pattern*: Creating arbitrary CSS classes with dozens of `@apply`s | **Avoid** | Defeats utility-first benefits, increases CSS bundle size, breaks purge detection |

#### The `cn()` Helper Implementation
Always combine `clsx` (conditional joins) and `tailwind-merge` (conflict resolution):

```bash
npm install clsx tailwind-merge
```

Create `lib/utils.ts`:

```typescript
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
```

#### Building a Scalable React/Next.js Component
Example: Production-grade Button component with variants, sizes, and prop merging:

```tsx
import * as React from 'react';
import { cn } from '@/lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

const variantStyles: Record<NonNullable<ButtonProps['variant']>, string> = {
  primary: 'bg-indigo-600 text-white hover:bg-indigo-500 active:bg-indigo-700 shadow-sm',
  secondary: 'bg-slate-100 text-slate-900 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-100 dark:hover:bg-slate-700',
  outline: 'border border-slate-300 bg-transparent text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800',
  ghost: 'text-slate-700 hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800',
  danger: 'bg-rose-600 text-white hover:bg-rose-500 active:bg-rose-700 shadow-sm',
};

const sizeStyles: Record<NonNullable<ButtonProps['size']>, string> = {
  sm: 'h-8 px-3 text-xs gap-1.5',
  md: 'h-10 px-4 text-sm gap-2',
  lg: 'h-12 px-6 text-base gap-2.5',
};

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', isLoading = false, disabled, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(
          // Base styles
          'inline-flex items-center justify-center font-medium rounded-lg transition-colors',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2',
          'disabled:pointer-events-none disabled:opacity-50 select-none',
          // Variants
          variantStyles[variant],
          sizeStyles[size],
          // User overrides
          className
        )}
        {...props}
      >
        {isLoading && (
          <svg className="h-4 w-4 animate-spin text-current" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        )}
        {children}
      </button>
    );
  }
);
Button.displayName = 'Button';
```

*Why `cn()` is essential:* If a caller writes `<Button className="bg-red-500 text-black">`, `twMerge` detects that `bg-red-500` conflicts with `bg-indigo-600` and removes the latter, avoiding unpredictable CSS cascade ordering bugs.

---

### 6. Handle Transitions, Animations, and Micro-interactions

Tailwind provides transitions for smooth property changes and CSS animations for continuous or triggered motions.

#### Hover, Focus, Active, and Group Modifiers
```html
<!-- Interactive Card using group modifier -->
<div class="group relative rounded-xl border border-slate-200 p-6 transition-all duration-200 hover:-translate-y-1 hover:shadow-lg hover:border-indigo-300">
  <h3 class="text-lg font-semibold text-slate-800 transition-colors group-hover:text-indigo-600">
    Interactive Feature
  </h3>
  <span class="text-sm text-slate-500 transition-transform duration-200 group-hover:translate-x-1 inline-block">
    Explore feature &rarr;
  </span>
</div>
```

#### Peer Modifiers for Connected State
```html
<label class="flex items-center gap-3 cursor-pointer">
  <input type="checkbox" class="peer sr-only" />
  <div class="h-6 w-11 rounded-full bg-slate-300 peer-checked:bg-indigo-600 peer-focus-visible:ring-2 peer-focus-visible:ring-indigo-500 transition-colors"></div>
  <span class="text-sm text-slate-700 peer-checked:text-indigo-900 font-medium select-none">
    Sync automatically
  </span>
</label>
```

#### Custom Animation Keyframes

- **In Tailwind v3** (`tailwind.config.ts`):
  ```typescript
  theme: {
    extend: {
      keyframes: {
        shimmer: {
          '100%': { transform: 'translateX(100%)' },
        },
      },
      animation: {
        shimmer: 'shimmer 1.5s infinite',
      },
    },
  }
  ```

- **In Tailwind v4** (CSS):
  ```css
  @theme {
    --animate-shimmer: shimmer 1.5s infinite;
  }

  @keyframes shimmer {
    100% {
      transform: translateX(100%);
    }
  }
  ```

---

### 7. Extend Capabilities with Plugins & Custom Utilities

#### Official Plugin Suite
1. **Typography** (`@tailwindcss/typography`): Adds the `prose` class for rendering markdown and rich-text.
2. **Forms** (`@tailwindcss/forms`): Resets form element styles for easy styling.
3. **Container Queries** (`@tailwindcss/container-queries`): Viewport-independent responsive layouts (built into v4).

#### Custom Utilities and Variants

- **Tailwind v3 Plugin Definition**:
  ```typescript
  import plugin from 'tailwindcss/plugin';

  export default {
    plugins: [
      plugin(function ({ addUtilities }) {
        addUtilities({
          '.text-balance': {
            'text-wrap': 'balance',
          },
        });
      }),
    ],
  };
  ```

- **Tailwind v4 Native CSS Directives**:
  ```css
  /* Declare custom utility in CSS */
  @utility text-balance {
    text-wrap: balance;
  }

  /* Declare custom variant */
  @custom-variant pointer-coarse (@media (pointer: coarse));
  ```

---

## Best Practices

- **Enforce Consistent Class Ordering**: Use `prettier-plugin-tailwindcss` to automatically sort utility classes (box model $\rightarrow$ positioning $\rightarrow$ flex/grid $\rightarrow$ typography $\rightarrow$ visual $\rightarrow$ modifiers).
- **Never Build Dynamic Classes with Interpolation**:
  - ❌ **Broken**: `className={`text-${color}-500`}` (Tailwind's scanner cannot detect interpolated strings at build time).
  - ✅ **Correct**: Use a lookup map:
    ```typescript
    const colorMap = {
      blue: 'text-blue-500',
      green: 'text-green-500',
      red: 'text-red-500',
    };
    <span className={colorMap[color]} />
    ```
- **Use `focus-visible` Instead of `focus`**: Ensures focus rings only appear for keyboard navigation and accessibility, not mouse clicks.
- **Always Keep Layout Responsive from the Start**: Test at 360px (mobile), 768px (tablet), 1024px (laptop), and 1440px (desktop).
- **Keep CSS Free of `@apply` Sprawl**: Abstract repetitive UI patterns into reusable components in your UI framework rather than dumping hundreds of utility declarations into custom CSS classes.

---

## Common Pitfalls

- **Purging / Missing Styles in Production**:
  - *Cause*: In Tailwind v3, omitting a template directory from the `content` array in `tailwind.config.ts`.
  - *Fix*: Ensure all paths containing JSX/TSX/HTML files are specified in `content`. In v4, the Oxide scanner resolves this automatically.
- **Class Specificity Conflicts in Component Libraries**:
  - *Cause*: Merging classes with plain template strings (e.g. `` `${baseClasses} ${className}` ``) fails because CSS rule order determines specificity, not class string order.
  - *Fix*: Wrap all class merges in `cn()` (`twMerge(clsx(...))`).
- **Overriding Root Theme Keys Accidendally**:
  - *Cause*: Placing tokens in `theme: { colors: { ... } }` replaces the entire default palette.
  - *Fix*: Always declare additions inside `theme: { extend: { colors: { ... } } }`.
- **FOUC (Flash of Unstyled Content) During Theme Toggles**:
  - *Cause*: Dark mode class added after hydration.
  - *Fix*: Inject an inline script in `<head>` that reads `localStorage` and appends `.dark` to `document.documentElement` before render.

---

## Verification

Confirm proper Tailwind installation, purging, and styling application:

1. **Verify Development Server Compilation**:
   ```bash
   # Run the framework dev command (e.g., Vite, Next.js)
   npm run dev
   ```
   Ensure utilities render without PostCSS or build parsing errors.

2. **Verify Production Build and Purging**:
   ```bash
   npm run build
   ```
   Check the output `.css` file in the build artifacts (e.g., `dist/` or `.next/static/css/`). The production CSS file should be small (typically under 20-40 KB gzipped) and should contain only utilities actually used in the codebase.

3. **Verify Interactive & Responsive States**:
   - Inspect elements in browser DevTools device emulation mode at 375px, 768px, and 1280px to confirm breakpoint triggers.
   - Toggle `.dark` on `<html>` or `<body>` to verify dark mode styles activate cleanly.
   - Test keyboard navigation (`Tab`) to ensure `focus-visible:ring-2` indicators are prominent and accessible.
