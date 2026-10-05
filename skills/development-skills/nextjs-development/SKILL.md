---
name: nextjs-development
description: >-
  Build, maintain, and optimize production-grade full-stack web applications using the Next.js App Router (versions 14, 15, and 16+). Covers architecture, React Server Components, Client Components, data fetching, caching, Server Actions, Route Handlers, middleware, performance optimization, and TypeScript configuration.
---

# Next.js App Router Development

A comprehensive guide for building high-performance, scalable web applications using the Next.js App Router architecture. Next.js combines React Server Components (RSC), streaming, hybrid rendering strategies, and integrated optimizations for modern web workloads.

## When to Use

- Initializing new Next.js projects with the App Router architecture.
- Migrating existing applications from Pages Router (`pages/`) to App Router (`app/`).
- Architecting Server Component and Client Component boundaries (`'use client'`).
- Implementing data fetching, caching strategies, and revalidation (`fetch`, `'use cache'`, `revalidateTag`, `revalidatePath`).
- Building backend logic via Server Actions and Route Handlers (`app/api/**/route.ts`).
- Implementing route-level security, auth guards, and redirects via `middleware.ts`.
- Optimizing media assets, typography, and Core Web Vitals (`next/image`, `next/font`, dynamic imports).
- Designing advanced routing structures including route groups, parallel slots, and intercepting routes.
- Configuring SEO metadata, Open Graph images, sitemaps, and RSS feeds via Metadata APIs.
- Upgrading codebases to handle Next.js 15+ async request APIs (`await params`, `await cookies()`).

## Prerequisites

- Node.js runtime (v18.18+ for Next.js 14; v20.9+ for Next.js 15 and 16+).
- Node package manager: `pnpm`, `npm`, `yarn`, or `bun`.
- TypeScript 5.1+ recommended for complete end-to-end type safety.

---

## Steps

### 1. Initialize and Configure the Project

Scaffold a project with standard flags or configure an existing repository for modern App Router usage.

```bash
# Initialize a new Next.js application with TypeScript, ESLint, and Tailwind CSS
npx create-next-app@latest my-app --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
```

Configure `tsconfig.json` to enable strict mode and module resolution for Next.js:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

Maintain `next.config.ts` (or `next.config.js`) for runtime flags, remote image domains, and headers:

```typescript
// next.config.ts
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'images.example.com',
        pathname: '/**',
      },
    ],
  },
  // Enable modern caching model or experimental features if using Next.js 15+
  experimental: {
    // dynamicIO: true, // For modern 'use cache' directive support in Next.js 15+
  },
};

export default nextConfig;
```

---

### 2. Structure App Router Architecture

The `app/` directory relies on nested folders to define route segments and specialized file conventions:

| File | Purpose | Execution |
| :--- | :--- | :--- |
| `layout.tsx` | Shared layout across child routes; preserves state on navigation | Server by default |
| `page.tsx` | Unique UI rendered for a specific route path | Server by default |
| `loading.tsx` | Instant loading skeleton wrapped in React Suspense | Server/Client |
| `error.tsx` | Route segment error boundary (catches runtime errors in `page.tsx`) | Must be Client (`'use client'`) |
| `not-found.tsx`| 404 UI rendered when `notFound()` is thrown or route doesn't match | Server/Client |
| `template.tsx`| Similar to layout, but mounts a new instance on every navigation | Server by default |
| `default.tsx` | Fallback component for parallel route slots during hard reload | Server/Client |
| `route.ts`    | API endpoint handler for HTTP methods (GET, POST, etc.) | Server only |

#### Root Layout Pattern (`app/layout.tsx`):

Every application requires a single root layout containing `<html>` and `<body>` tags:

```tsx
// app/layout.tsx
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: {
    template: '%s | Platform',
    default: 'Platform Home',
  },
  description: 'Production Next.js application',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="min-h-screen bg-background font-sans antialiased">
        <main>{children}</main>
      </body>
    </html>
  );
}
```

---

### 3. Establish Component Boundaries (Server vs. Client)

By default, all components inside the `app/` directory are **React Server Components (RSC)**.

#### When to use Server Components:
- Direct database, ORM, or filesystem access.
- Sensitive credentials, API keys, and environment variables.
- Heavy dependencies that should not increase client bundle size.
- Initial HTML rendering for SEO and fast First Contentful Paint.

#### When to use Client Components (`'use client'`):
- State hooks (`useState`, `useReducer`).
- Lifecycle effects (`useEffect`, `useLayoutEffect`).
- Event listeners (`onClick`, `onChange`, `onSubmit`).
- Browser APIs (`window`, `localStorage`, geolocation, media queries).
- Custom React context providers and consumers.

#### Boundary Composition Pattern:
Push Client Components down to the leaves of the render tree. Pass Server Components as `children` into Client Component wrappers to avoid converting the entire tree into client code.

```tsx
// components/client-wrapper.tsx
'use client';

import { useState } from 'react';

export function ModalWrapper({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div>
      <button onClick={() => setIsOpen(true)}>Open Modal</button>
      {isOpen && (
        <div className="modal-backdrop">
          {/* children is rendered as a Server Component on the server */}
          {children}
          <button onClick={() => setIsOpen(false)}>Close</button>
        </div>
      )}
    </div>
  );
}
```

To enforce that code never leaks into the client bundle, install and import `server-only`:

```bash
npm install server-only
```

```typescript
// lib/db.ts
import 'server-only';

export async function queryDatabase() {
  // Safe from accidental client imports
}
```

---

### 4. Implement Data Fetching and Caching Strategies

Next.js provides multiple rendering strategies: SSG (Static Site Generation), SSR (Server-Side Rendering), and ISR (Incremental Static Regeneration).

> [!NOTE]
> **Next.js 15+ Async API Change**: In Next.js 15+, dynamic route parameters (`params`), search parameters (`searchParams`), `cookies()`, and `headers()` return **Promises** and must be awaited.

#### Static Generation with Parameters (SSG / Static):

```tsx
// app/posts/[slug]/page.tsx
import { notFound } from 'next/navigation';

interface PageProps {
  params: Promise<{ slug: string }>;
}

export async function generateStaticParams() {
  const posts = await fetch('https://api.example.com/posts').then((res) => res.json());
  return posts.map((post: { slug: string }) => ({ slug: post.slug }));
}

export default async function PostPage({ params }: PageProps) {
  const { slug } = await params;
  const post = await fetch(`https://api.example.com/posts/${slug}`).then((res) => {
    if (!res.ok) return null;
    return res.json();
  });

  if (!post) {
    notFound();
  }

  return (
    <article>
      <h1>{post.title}</h1>
      <p>{post.content}</p>
    </article>
  );
}
```

#### Time-Based Revalidation (ISR):

```typescript
// Fetch with revalidation time in seconds
const data = await fetch('https://api.example.com/items', {
  next: { revalidate: 3600 }, // Revalidate at most once every hour
});
```

#### Tag-Based On-Demand Revalidation:

```typescript
// Fetch with a cache tag
const data = await fetch('https://api.example.com/products', {
  next: { tags: ['products'] },
});
```

Revalidate the tag on-demand from a Server Action or Route Handler:

```typescript
// app/actions.ts
'use server';

import { revalidateTag, revalidatePath } from 'next/cache';

export async function refreshCatalog() {
  revalidateTag('products');
  revalidatePath('/products');
}
```

#### Modern Directive: `'use cache'` (Next.js 15+ / 16+):

When `dynamicIO` is enabled, use the `'use cache'` directive at the file or function level:

```typescript
// lib/cached-data.ts
import { unstable_cacheLife as cacheLife, unstable_cacheTag as cacheTag } from 'next/cache';

export async function getLeaderboard() {
  'use cache';
  cacheLife('hours'); // preset: seconds, minutes, hours, days, max
  cacheTag('leaderboard');

  const res = await fetch('https://api.example.com/leaderboard');
  return res.json();
}
```

---

### 5. Build API Route Handlers

Route Handlers live in `route.ts` files and handle HTTP methods via explicit exports (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS`).

```typescript
// app/api/items/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server';

interface RouteContext {
  params: Promise<{ id: string }>;
}

export async function GET(request: NextRequest, { params }: RouteContext) {
  const { id } = await params;
  const { searchParams } = new URL(request.url);
  const filter = searchParams.get('filter');

  return NextResponse.json({ id, filter, timestamp: Date.now() }, { status: 200 });
}

export async function POST(request: NextRequest, { params }: RouteContext) {
  const { id } = await params;

  try {
    const body = await request.json();

    if (!body.title) {
      return NextResponse.json({ error: 'Title is required' }, { status: 400 });
    }

    return NextResponse.json({ success: true, id, item: body }, { status: 201 });
  } catch {
    return NextResponse.json({ error: 'Invalid JSON payload' }, { status: 400 });
  }
}
```

---

### 6. Enforce Security and Routing with Middleware

Create `middleware.ts` in the root directory (or inside `src/`) to intercept requests before routing completes.

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('session_token')?.value;
  const pathname = request.nextUrl.pathname;

  // Protect private routes
  if (pathname.startsWith('/dashboard') && !token) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Add security headers to response
  const response = NextResponse.next();
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');

  return response;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico, sitemap.xml, robots.txt
     */
    '/((?!_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt).*)',
  ],
};
```

---

### 7. Optimize Media Assets and Fonts

#### Image Optimization (`next/image`):
Prevents Cumulative Layout Shift (CLS) and serves modern formats (WebP, AVIF) with responsive srcset.

```tsx
import Image from 'next/image';

export function ProductHero({ imageUrl }: { imageUrl: string }) {
  return (
    <div className="relative aspect-video w-full overflow-hidden rounded-lg">
      <Image
        src={imageUrl}
        alt="Featured Product"
        fill
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
        priority // Preloads LCP image
        className="object-cover"
      />
    </div>
  );
}
```

#### Font Optimization (`next/font`):
Zero layout shift with automatic font self-hosting and CSS variable binding:

```tsx
// lib/fonts.ts
import { Inter, JetBrains_Mono } from 'next/font/google';

export const fontSans = Inter({
  subsets: ['latin'],
  variable: '--font-sans',
  display: 'swap',
});

export const fontMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
});
```

---

### 8. Implement Parallel and Intercepting Routes

Advanced routing patterns enable complex modal views, split dashboards, and conditional states.

#### Parallel Routes (`@slot`):
Defined using named slots with `@` prefix. Rendered simultaneously in a parent layout:

```tsx
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
  analytics,
  notifications,
}: {
  children: React.ReactNode;
  analytics: React.ReactNode;
  notifications: React.ReactNode;
}) {
  return (
    <div className="dashboard-grid">
      <div className="main-content">{children}</div>
      <aside className="sidebar">
        {analytics}
        {notifications}
      </aside>
    </div>
  );
}
```
*Note: Always create `default.tsx` inside each slot folder to prevent 404 errors during client-side navigation.*

#### Intercepting Routes:
Allow loading a route within the current layout while sharing the URL (e.g., photo modal overlays):
- `(.)` matches segments on the **same level**
- `(..)` matches segments **one level above**
- `(..)(..)` matches segments **two levels above**
- `(...)` matches segments from the **root `app` directory**

---

### 9. Configure Metadata and Search Engine Optimization (SEO)

#### Static and Dynamic Metadata:

```tsx
// app/blog/[slug]/page.tsx
import type { Metadata } from 'next';

interface Props {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const post = await fetch(`https://api.example.com/posts/${slug}`).then((res) => res.json());

  if (!post) {
    return { title: 'Post Not Found' };
  }

  return {
    title: post.title,
    description: post.summary,
    openGraph: {
      title: post.title,
      description: post.summary,
      url: `https://example.com/blog/${slug}`,
      images: [
        {
          url: post.ogImageUrl || '/og-default.png',
          width: 1200,
          height: 630,
          alt: post.title,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: post.title,
      description: post.summary,
    },
  };
}
```

#### Sitemap and Robots (`app/sitemap.ts` and `app/robots.ts`):

```typescript
// app/sitemap.ts
import type { MetadataRoute } from 'next';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const posts = await fetch('https://api.example.com/posts').then((res) => res.json());

  const postEntries: MetadataRoute.Sitemap = posts.map((post: { slug: string; updatedAt: string }) => ({
    url: `https://example.com/blog/${post.slug}`,
    lastModified: new Date(post.updatedAt),
    changeFrequency: 'weekly',
    priority: 0.7,
  }));

  return [
    {
      url: 'https://example.com',
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 1.0,
    },
    ...postEntries,
  ];
}
```

---

### 10. Manage Environment Variables and Type Safety

- `.env.local`: Local overrides (ignored by Git).
- `.env.production`: Production defaults.
- Variables prefixed with `NEXT_PUBLIC_` are bundled into the client code.
- Non-prefixed variables remain strictly server-side.

Validate environment variables at build/runtime using schema libraries:

```typescript
// lib/env.ts
import { z } from 'zod';

const envSchema = z.object({
  DATABASE_URL: z.string().url(),
  NEXT_PUBLIC_API_URL: z.string().url(),
  NODE_ENV: z.enum(['development', 'test', 'production']).default('development'),
});

export const env = envSchema.parse({
  DATABASE_URL: process.env.DATABASE_URL,
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  NODE_ENV: process.env.NODE_ENV,
});
```

---

## Best Practices

- **Server-First Principle**: Default to Server Components. Add `'use client'` only when interactive event handlers or state hooks are strictly necessary.
- **Async Request APIs**: Always `await params`, `await searchParams`, `await cookies()`, and `await headers()` in Next.js 15+ to prevent runtime deprecation warnings and errors.
- **Granular Suspense Boundaries**: Wrap slow data fetching components in `<Suspense fallback={<Skeleton />}>` rather than blocking the entire route page.
- **Colocate Features**: Keep domain-specific components, hooks, actions, and schemas in feature directories or colocated with route folders.
- **Strict Secret Protection**: Use `import 'server-only'` in database, payment, or auth utility modules to prevent accidental bundle leaks to the client.
- **Explicit Image Dimensions**: Always provide `width`/`height` or use `fill` with an accurate `sizes` prop on `next/image` to prevent CLS.
- **Safe Server Actions**: Validate all action inputs on the server using Zod or equivalent schemas before performing mutations.

---

## Common Pitfalls

- **Synchronous `params` Access in Next.js 15+**: Attempting to read `props.params.slug` directly without `await` causes hydration mismatch or runtime warnings.
- **Accidental Client Tree Bloat**: Placing `'use client'` at the top of a page or high-level layout converts all child components (and their imported modules) into client bundles.
- **Client-Side Secret Leakage**: Accessing `process.env.SECRET_KEY` inside a Client Component renders `undefined` or risks bundling secrets into client assets.
- **Missing `default.tsx` in Parallel Routes**: Failing to supply a `default.tsx` file in `@slot` directories causes Next.js to render 404 when refreshing or hard-navigating to unmatched sub-routes.
- **Error Boundary Without `'use client'`**: Defining an `error.tsx` file without `'use client'` throws a build error; error boundaries must be Client Components.
- **Layout Reset Misconception**: Expecting `layout.tsx` to re-mount state during navigation. Use `template.tsx` if full component unmount/remount on navigation is required.

---

## Verification

Confirm proper configuration and application health with these automated gates:

1. **Linting Inspection**:
   ```bash
   npx next lint
   ```
   Ensures compliance with Next.js ESLint rules (`@next/next/recommended`, Core Web Vitals checks).

2. **TypeScript Compilation Check**:
   ```bash
   npx tsc --noEmit
   ```
   Validates end-to-end typing, route context props, and Promise resolution for Next.js 15+ request APIs.

3. **Production Build & Route Manifest Inspection**:
   ```bash
   npx next build
   ```
   Inspect the output summary table:
   - `○ (Static)`: Prerendered as static content.
   - `● (SSG)`: Prerendered using `generateStaticParams`.
   - `ƒ (Dynamic)`: Server-rendered on demand via dynamic request headers/cookies.

4. **Production Runtime Verification**:
   ```bash
   npx next start
   ```
   Test end-to-end navigations, streaming Suspense fallbacks, image optimization endpoints, and middleware redirection behavior.

---

## Deep Dive Reference

For detailed code patterns, nested layout implementations, Server Actions, streaming, and intercepting route walkthroughs, refer to:
- [App Router Patterns Reference](references/app-router-patterns.md)
