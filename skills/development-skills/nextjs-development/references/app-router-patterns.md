# Next.js App Router Architecture & Patterns

This reference document provides production-grade code patterns and architectural blueprints for Next.js App Router (versions 14, 15, and 16+). All code samples use TypeScript and adhere to modern React Server Component (RSC) principles.

---

## Table of Contents

1. [Layout Nesting & Route Groups](#1-layout-nesting--route-groups)
2. [Dynamic & Catch-All Routing](#2-dynamic--catch-all-routing)
3. [Loading States & Error Boundaries](#3-loading-states--error-boundaries)
4. [Server Actions & Form Handling](#4-server-actions--form-handling)
5. [Streaming with Suspense](#5-streaming-with-suspense)
6. [Parallel & Intercepting Routes (Modals)](#6-parallel--intercepting-routes-modals)
7. [Route Handlers & API Endpoints](#7-route-handlers--api-endpoints)
8. [Modern Caching & Directives](#8-modern-caching--directives)

---

## 1. Layout Nesting & Route Groups

### 1.1 Root Layout and Nested Sub-Layouts

A nested layout wraps child pages while preserving its own state across navigations within that segment.

```
app/
├── layout.tsx             # Root layout (<html>, <body>, global providers)
├── page.tsx               # Root landing page (/)
└── dashboard/
    ├── layout.tsx         # Dashboard layout (Sidebar, Header, Breadcrumbs)
    ├── page.tsx           # Dashboard overview (/dashboard)
    └── settings/
        └── page.tsx       # Settings (/dashboard/settings)
```

```tsx
// app/layout.tsx (Root Layout)
import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: {
    template: '%s | Enterprise Suite',
    default: 'Enterprise Suite',
  },
  description: 'Scalable application platform',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased">
        {children}
      </body>
    </html>
  );
}
```

```tsx
// app/dashboard/layout.tsx (Nested Layout)
import Link from 'next/link';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen">
      <aside className="w-64 border-r border-slate-200 bg-white p-6">
        <nav className="flex flex-col gap-2">
          <Link href="/dashboard" className="rounded p-2 hover:bg-slate-100">
            Overview
          </Link>
          <Link href="/dashboard/settings" className="rounded p-2 hover:bg-slate-100">
            Settings
          </Link>
        </nav>
      </aside>
      <main className="flex-1 p-8">{children}</main>
    </div>
  );
}
```

---

### 1.2 Route Groups for Organizational Isolation

Route groups enclose folder names in parentheses `(groupName)`. They do not add segments to the URL path, allowing developers to organize routes and apply distinct layouts.

```
app/
├── (marketing)/
│   ├── layout.tsx         # Marketing layout (Public navbar, Footer)
│   ├── page.tsx           # Resolves to /
│   └── pricing/
│       └── page.tsx       # Resolves to /pricing
└── (portal)/
    ├── layout.tsx         # Portal layout (Sidebar, Auth header)
    └── console/
        └── page.tsx       # Resolves to /console
```

#### Multiple Root Layouts:
To support entirely different HTML documents (e.g., an unauthenticated auth flow with no top-level navbar and a distinct background), delete the top-level `app/layout.tsx` and place root layouts inside each route group:

```tsx
// app/(marketing)/layout.tsx
export default function MarketingRootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="marketing-theme">{children}</body>
    </html>
  );
}

// app/(portal)/layout.tsx
export default function PortalRootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="portal-theme">{children}</body>
    </html>
  );
}
```

---

### 1.3 Layouts vs. Templates

- **`layout.tsx`**: Mounts once, preserves state, does not re-render sub-trees or trigger CSS animation lifecycles on navigation between child routes.
- **`template.tsx`**: Mounts a new instance on every navigation. Ideal for enter/exit animations or resetting component state (e.g., clearing filter forms on page navigation).

```tsx
// app/dashboard/template.tsx
'use client';

export default function Template({ children }: { children: React.ReactNode }) {
  return (
    <div className="animate-fadeIn transition-opacity duration-200">
      {children}
    </div>
  );
}
```

---

## 2. Dynamic & Catch-All Routing

Next.js 15+ requires route segment parameters to be accessed asynchronously as Promises.

### 2.1 Single Segment: `[slug]`

```tsx
// app/articles/[slug]/page.tsx
import { notFound } from 'next/navigation';
import type { Metadata } from 'next';

interface ArticlePageProps {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

export async function generateStaticParams() {
  const articles: Array<{ slug: string }> = await fetch('https://api.example.com/articles')
    .then((r) => r.json());

  return articles.map((article) => ({
    slug: article.slug,
  }));
}

export async function generateMetadata({ params }: ArticlePageProps): Promise<Metadata> {
  const { slug } = await params;
  const article = await getArticleBySlug(slug);

  if (!article) return { title: 'Not Found' };

  return {
    title: article.title,
    description: article.excerpt,
  };
}

async function getArticleBySlug(slug: string) {
  const res = await fetch(`https://api.example.com/articles/${slug}`);
  if (!res.ok) return null;
  return res.json();
}

export default async function ArticlePage({ params, searchParams }: ArticlePageProps) {
  const { slug } = await params;
  const resolvedSearchParams = await searchParams;
  const viewMode = resolvedSearchParams.view ?? 'standard';

  const article = await getArticleBySlug(slug);
  if (!article) notFound();

  return (
    <article className="prose mx-auto py-8">
      <h1>{article.title}</h1>
      <p className="text-sm text-slate-500">Mode: {viewMode}</p>
      <div>{article.content}</div>
    </article>
  );
}
```

---

### 2.2 Catch-All (`[...slug]`) and Optional Catch-All (`[[...slug]]`)

- **`[...slug]`**: Matches one or more segments (e.g., `/docs/a`, `/docs/a/b`). Does not match `/docs`.
- **`[[...slug]]`**: Matches zero or more segments (e.g., `/docs`, `/docs/a`, `/docs/a/b`).

```tsx
// app/docs/[[...slug]]/page.tsx
import { notFound } from 'next/navigation';

interface DocsPageProps {
  params: Promise<{ slug?: string[] }>;
}

export async function generateStaticParams() {
  return [
    { slug: [] },
    { slug: ['getting-started'] },
    { slug: ['getting-started', 'installation'] },
  ];
}

export default async function DocsPage({ params }: DocsPageProps) {
  const { slug } = await params;
  const pathSegments = slug ?? [];
  const currentPath = pathSegments.join('/') || 'index';

  const doc = await fetch(`https://api.example.com/docs/${currentPath}`).then((r) =>
    r.ok ? r.json() : null
  );

  if (!doc) notFound();

  return (
    <div>
      <div className="text-xs text-slate-400">Path: /{currentPath}</div>
      <h2>{doc.title}</h2>
      <div dangerouslySetInnerHTML={{ __html: doc.html }} />
    </div>
  );
}
```

---

## 3. Loading States & Error Boundaries

### 3.1 Instant Loading Skeletons (`loading.tsx`)

Next.js automatically wraps `page.tsx` in a `<Suspense fallback={<Loading />}>` boundary when `loading.tsx` is defined in the same directory.

```tsx
// app/dashboard/loading.tsx
export default function DashboardLoading() {
  return (
    <div className="space-y-4 p-6 animate-pulse">
      <div className="h-8 w-1/3 rounded bg-slate-200" />
      <div className="grid grid-cols-3 gap-4">
        <div className="h-32 rounded bg-slate-200" />
        <div className="h-32 rounded bg-slate-200" />
        <div className="h-32 rounded bg-slate-200" />
      </div>
      <div className="h-64 rounded bg-slate-200" />
    </div>
  );
}
```

---

### 3.2 Granular Error Boundary (`error.tsx`)

Error boundaries must be Client Components. They catch unhandled errors from child components and `page.tsx`.

```tsx
// app/dashboard/error.tsx
'use client';

import { useEffect } from 'react';

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Forward error to centralized monitoring
    console.error('Segment Error Caught:', error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <h2 className="text-xl font-bold text-red-600">Something went wrong</h2>
      <p className="mt-2 text-sm text-slate-600">
        {error.message || 'An unexpected error occurred while loading this section.'}
      </p>
      {error.digest && (
        <code className="mt-2 rounded bg-slate-100 px-2 py-1 text-xs text-slate-500">
          Ref: {error.digest}
        </code>
      )}
      <button
        onClick={() => reset()}
        className="mt-4 rounded bg-slate-900 px-4 py-2 text-sm text-white hover:bg-slate-800"
      >
        Retry Segment
      </button>
    </div>
  );
}
```

---

### 3.3 Root Error Boundary (`global-error.tsx`)

`error.tsx` cannot catch errors originating inside the Root Layout (`app/layout.tsx`). To handle root-level failures, define `global-error.tsx`. It must define its own `<html>` and `<body>` tags.

```tsx
// app/global-error.tsx
'use client';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="en">
      <body className="flex min-h-screen items-center justify-center bg-red-50 p-6 text-center">
        <div>
          <h1 className="text-2xl font-bold text-red-900">Critical Application Error</h1>
          <p className="mt-2 text-slate-700">{error.message}</p>
          <button
            onClick={() => reset()}
            className="mt-4 rounded bg-red-800 px-4 py-2 text-white hover:bg-red-700"
          >
            Reload Platform
          </button>
        </div>
      </body>
    </html>
  );
}
```

---

## 4. Server Actions & Form Handling

Server Actions run on the server and are callable directly from client forms or event handlers.

### 4.1 Server Action Definition with Zod Validation

```typescript
// app/actions/user-actions.ts
'use server';

import { revalidatePath, revalidateTag } from 'next/cache';
import { z } from 'zod';

const CreateUserSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  role: z.enum(['admin', 'member', 'viewer']),
});

export type FormState = {
  success: boolean;
  message?: string;
  errors?: Record<string, string[]>;
};

export async function createUserAction(
  prevState: FormState,
  formData: FormData
): Promise<FormState> {
  // Simulate network latency or auth check
  const rawData = {
    name: formData.get('name'),
    email: formData.get('email'),
    role: formData.get('role'),
  };

  const validation = CreateUserSchema.safeParse(rawData);

  if (!validation.success) {
    return {
      success: false,
      errors: validation.error.flatten().fieldErrors,
      message: 'Validation failed. Check form fields.',
    };
  }

  try {
    // Database write invocation
    await fetch('https://api.example.com/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(validation.data),
    });

    revalidateTag('users');
    revalidatePath('/dashboard/users');

    return {
      success: true,
      message: 'User successfully created.',
    };
  } catch (err) {
    return {
      success: false,
      message: 'Database persistence failed. Please try again.',
    };
  }
}
```

---

### 4.2 Modern Client Form with `useActionState` (React 19)

In modern Next.js / React 19, `useActionState` replaces `useFormState`.

```tsx
// components/create-user-form.tsx
'use client';

import { useActionState } from 'react';
import { useFormStatus } from 'react-dom';
import { createUserAction, type FormState } from '@/app/actions/user-actions';

const initialState: FormState = {
  success: false,
};

function SubmitButton() {
  const { pending } = useFormStatus();

  return (
    <button
      type="submit"
      disabled={pending}
      className="w-full rounded bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
    >
      {pending ? 'Submitting...' : 'Create Account'}
    </button>
  );
}

export function CreateUserForm() {
  const [state, formAction] = useActionState(createUserAction, initialState);

  return (
    <form action={formAction} className="max-w-md space-y-4 rounded border bg-white p-6 shadow-sm">
      {state.message && (
        <div
          className={`rounded p-3 text-sm ${
            state.success ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
          }`}
        >
          {state.message}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium">Name</label>
        <input
          name="name"
          type="text"
          className="mt-1 block w-full rounded border border-slate-300 p-2"
        />
        {state.errors?.name && (
          <p className="mt-1 text-xs text-red-500">{state.errors.name[0]}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium">Email</label>
        <input
          name="email"
          type="email"
          className="mt-1 block w-full rounded border border-slate-300 p-2"
        />
        {state.errors?.email && (
          <p className="mt-1 text-xs text-red-500">{state.errors.email[0]}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium">Role</label>
        <select name="role" className="mt-1 block w-full rounded border border-slate-300 p-2">
          <option value="viewer">Viewer</option>
          <option value="member">Member</option>
          <option value="admin">Admin</option>
        </select>
      </div>

      <SubmitButton />
    </form>
  );
}
```

---

### 4.3 Optimistic Updates with `useOptimistic`

```tsx
// components/todo-list.tsx
'use client';

import { useOptimistic, useTransition } from 'react';
import { toggleTodoAction } from '@/app/actions/todo-actions';

interface Todo {
  id: string;
  title: string;
  completed: boolean;
}

export function TodoList({ initialTodos }: { initialTodos: Todo[] }) {
  const [, startTransition] = useTransition();
  const [optimisticTodos, setOptimisticTodo] = useOptimistic(
    initialTodos,
    (state, updatedId: string) =>
      state.map((todo) =>
        todo.id === updatedId ? { ...todo, completed: !todo.completed } : todo
      )
  );

  const handleToggle = (id: string) => {
    startTransition(async () => {
      setOptimisticTodo(id);
      await toggleTodoAction(id);
    });
  };

  return (
    <ul className="space-y-2">
      {optimisticTodos.map((todo) => (
        <li key={todo.id} className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={todo.completed}
            onChange={() => handleToggle(todo.id)}
          />
          <span className={todo.completed ? 'line-through text-slate-400' : ''}>
            {todo.title}
          </span>
        </li>
      ))}
    </ul>
  );
}
```

---

## 5. Streaming with Suspense

Streaming allows breaking the page down into smaller HTML chunks that are progressively transmitted to the browser as soon as they resolve.

### 5.1 Decomposed Suspense Architecture

```tsx
// app/dashboard/page.tsx
import { Suspense } from 'react';

async function RevenueMetrics() {
  // Simulate slow metric fetch
  const data = await fetch('https://api.example.com/metrics/revenue', {
    next: { revalidate: 60 },
  }).then((r) => r.json());

  return <div className="rounded border bg-white p-4">Revenue: ${data.total}</div>;
}

async function UserActivities() {
  // Fast query
  const activities = await fetch('https://api.example.com/activities', {
    cache: 'no-store',
  }).then((r) => r.json());

  return (
    <ul className="rounded border bg-white p-4">
      {activities.map((a: { id: string; desc: string }) => (
        <li key={a.id}>{a.desc}</li>
      ))}
    </ul>
  );
}

export default function DashboardOverviewPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Analytics Overview</h1>

      {/* Instant static or fast layout */}
      <div className="grid grid-cols-2 gap-4">
        {/* Suspended slow component */}
        <Suspense fallback={<div className="h-24 animate-pulse rounded bg-slate-200" />}>
          <RevenueMetrics />
        </Suspense>

        {/* Suspended independent component */}
        <Suspense fallback={<div className="h-24 animate-pulse rounded bg-slate-200" />}>
          <UserActivities />
        </Suspense>
      </div>
    </div>
  );
}
```

---

## 6. Parallel & Intercepting Routes (Modals)

This pattern renders a modal overlay when navigating client-side, while rendering a standalone page on hard reload or direct URL link.

### Directory Structure:
```
app/
├── feed/
│   ├── @modal/
│   │   ├── (.)photo/[id]/
│   │   │   └── page.tsx      # Intercepted route modal UI
│   │   └── default.tsx       # Returns null when modal is inactive
│   ├── layout.tsx            # Renders children and @modal slot
│   └── page.tsx              # Grid of photos with Links
└── photo/
    └── [id]/
        └── page.tsx          # Full standalone photo view
```

### 6.1 Feed Layout (`app/feed/layout.tsx`):

```tsx
// app/feed/layout.tsx
export default function FeedLayout({
  children,
  modal,
}: {
  children: React.ReactNode;
  modal: React.ReactNode;
}) {
  return (
    <div>
      {children}
      {modal}
    </div>
  );
}
```

### 6.2 Default Slot Fallback (`app/feed/@modal/default.tsx`):

```tsx
// app/feed/@modal/default.tsx
export default function DefaultModalSlot() {
  return null;
}
```

### 6.3 Intercepted Route Modal (`app/feed/@modal/(.)photo/[id]/page.tsx`):

```tsx
// app/feed/@modal/(.)photo/[id]/page.tsx
'use client';

import { useRouter } from 'next/navigation';
import { use } from 'react';

export default function InterceptedPhotoModal({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const router = useRouter();
  const { id } = use(params);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="relative max-w-lg rounded-lg bg-white p-6 shadow-xl">
        <button
          onClick={() => router.back()}
          className="absolute right-4 top-4 text-slate-500 hover:text-black"
        >
          ✕
        </button>
        <h3 className="text-lg font-bold">Photo Modal #{id}</h3>
        <p className="mt-2 text-sm text-slate-600">
          This was rendered via an intercepting route. Navigating back closes the modal.
        </p>
      </div>
    </div>
  );
}
```

---

## 7. Route Handlers & API Endpoints

Route Handlers support Web standard `Request` and `Response` objects.

```typescript
// app/api/webhooks/stripe/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const signature = req.headers.get('stripe-signature');
    if (!signature) {
      return NextResponse.json({ error: 'Missing webhook signature' }, { status: 400 });
    }

    const rawPayload = await req.text();

    // Verify webhook signature logic here...

    return NextResponse.json({ received: true }, { status: 200 });
  } catch (error) {
    return NextResponse.json(
      { error: 'Webhook processing error', details: (error as Error).message },
      { status: 500 }
    );
  }
}
```

### 7.1 Streaming Server-Sent Events (SSE) Route Handler

```typescript
// app/api/events/route.ts
import { NextRequest } from 'next/server';

export async function GET(request: NextRequest) {
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      for (let i = 1; i <= 5; i++) {
        const payload = `data: ${JSON.stringify({ step: i, timestamp: Date.now() })}\n\n`;
        controller.enqueue(encoder.encode(payload));
        await new Promise((res) => setTimeout(res, 1000));
      }
      controller.close();
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      Connection: 'keep-alive',
    },
  });
}
```

---

## 8. Modern Caching & Directives

### 8.1 Modern `'use cache'` Directive (Next.js 15+ / 16+)

Enabled with `experimental: { dynamicIO: true }` in `next.config.ts`. Replaces legacy fetch-only caching with granular function and component caching.

```typescript
// lib/inventory.ts
import { unstable_cacheLife as cacheLife, unstable_cacheTag as cacheTag } from 'next/cache';

export async function getProductInventory(sku: string) {
  'use cache';
  cacheLife('minutes'); // built-in profile: seconds, minutes, hours, days, max
  cacheTag(`inventory-${sku}`);

  const res = await fetch(`https://inventory.internal/items/${sku}`);
  return res.json();
}
```

### 8.2 Invalidation Workflow

```typescript
// app/actions/inventory-actions.ts
'use server';

import { revalidateTag } from 'next/cache';

export async function updateStockLevel(sku: string, count: number) {
  await fetch(`https://inventory.internal/items/${sku}`, {
    method: 'PATCH',
    body: JSON.stringify({ count }),
  });

  // Purges cached result for getProductInventory across all server edges
  revalidateTag(`inventory-${sku}`);
}
```
