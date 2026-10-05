---
name: vercel-cloudflare-deployment
description: >-
  Configures, builds, deploys, and manages web applications, serverless/edge functions, and static assets on Vercel and Cloudflare Pages. Covers vercel.json, wrangler configurations, routing rules (_redirects, _headers), environment variables, edge storage bindings (KV, D1, R2), monorepos, caching strategies, preview pipelines, and cross-platform migrations.
---

# Vercel & Cloudflare Deployment

Automate, configure, and operate modern web applications, static sites, and serverless/edge backends across Vercel and Cloudflare Pages. This skill provides production-grade architectural guidance, configuration templates, CLI commands, and verification protocols for both platforms.

---

## When to Use

- Deploying frontend or full-stack web applications (Next.js, Astro, Remix, SvelteKit, Nuxt, Vite/React/Vue SPAs).
- Writing and configuring platform files: `vercel.json`, `wrangler.toml`/`wrangler.json`, `_redirects`, and `_headers`.
- Establishing multi-environment configurations (Development, Preview, Production) and managing secrets.
- Implementing serverless functions, edge isolate runtimes, or Cloudflare Pages Functions with storage bindings (KV, D1, R2).
- Setting up Git-based continuous deployment, preview URL branch aliasing, or monorepo build filters.
- Configuring custom apex domains, subdomains, SSL/TLS certificates, and edge DNS routing.
- Securing deployments with password protection, Vercel Authentication, or Cloudflare Access.
- Tuning edge CDN caching, Stale-While-Revalidate headers, and asset compression.
- Migrating an existing application from Vercel to Cloudflare Pages or from Cloudflare Pages to Vercel.

---

## Prerequisites

- **Node.js**: Node.js 18.x or 20.x+ LTS runtime.
- **Package Manager**: `npm`, `pnpm`, `yarn`, or `bun`.
- **Git**: Installed and connected to a remote VCS provider (GitHub, GitLab, Bitbucket).
- **Vercel CLI**: Installed globally or executed via `npx vercel`. Authenticated via `vercel login` or `VERCEL_TOKEN`.
- **Cloudflare Wrangler CLI**: Installed locally (`wrangler`) or executed via `npx wrangler`. Authenticated via `wrangler login` or `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`.
- **curl & jq**: Recommended for local verification and header inspecting.

---

## Platform Comparison & Architecture Decision

| Architectural Dimension | Vercel | Cloudflare Pages |
| :--- | :--- | :--- |
| **Primary Execution Model** | Node.js Serverless Functions + V8 Edge Middleware | V8 Isolate Workers (Cloudflare Pages Functions) |
| **Cold Starts** | Minimal on Edge; ~150–400ms on Node Serverless | Near-zero (< 5ms) worldwide across edge isolates |
| **Native Framework Integration** | Deepest for Next.js (first-party features, ISR, Server Actions) | Framework-agnostic with `@cloudflare/next-on-pages`, Astro, Remix |
| **Edge Storage Primitives** | Vercel Blob, KV, Postgres (managed partner integrations) | First-party Edge primitives: KV, D1 (SQLite), R2 (S3-compatible) |
| **Routing & Rules Config** | Single file: `vercel.json` | Declarative files: `_redirects`, `_headers`, and `/functions` |
| **Cron Jobs** | Built-in via `vercel.json` `crons` array | Native Workers Cron Triggers (requires Worker or Pages hook) |
| **Pricing / Bandwidth** | Tiered bandwidth allowances with metered overage | Generous free/flat bandwidth model, zero egress fees on R2 |
| **Ecosystem Fit** | Full-stack Next.js, hybrid Node.js serverless dependencies | Globally distributed edge-first apps, heavy asset storage, zero-egress APIs |

---

## 1. Vercel Deployment & Configuration

### 1.1 `vercel.json` Configuration

The `vercel.json` file controls routing, header policies, runtime resources, and build overrides. Place this file in the project root.

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "cleanUrls": true,
  "trailingSlash": false,
  "rewrites": [
    {
      "source": "/api/v1/:path*",
      "destination": "https://api.external-service.com/v1/:path*"
    },
    {
      "source": "/((?!api/|_next/|assets/|favicon.ico).*)",
      "destination": "/index.html"
    }
  ],
  "redirects": [
    {
      "source": "/legacy-docs/:slug",
      "destination": "/docs/:slug",
      "permanent": true
    },
    {
      "source": "/old-pricing",
      "destination": "/pricing",
      "statusCode": 308
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        },
        {
          "key": "Permissions-Policy",
          "value": "camera=(), microphone=(), geolocation=()"
        },
        {
          "key": "Content-Security-Policy",
          "value": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;"
        }
      ]
    },
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ],
  "functions": {
    "api/**/*.js": {
      "memory": 1024,
      "maxDuration": 15
    },
    "api/reports/*.js": {
      "memory": 3008,
      "maxDuration": 60
    }
  },
  "crons": [
    {
      "path": "/api/cron/nightly-cleanup",
      "schedule": "0 2 * * *"
    }
  ]
}
```

### 1.2 Environment Variables Management

Vercel segregates variables into three distinct environments:
- **Production**: Applied to pushes against the production branch (typically `main` or `master`).
- **Preview**: Applied to branch builds, pull requests, and manual preview deployments.
- **Development**: Downloaded locally via `vercel env pull`.

#### CLI Management Commands:
```bash
# Add a variable to specific environments (prompts or interactive flags)
vercel env add DATABASE_URL production
vercel env add API_BASE_URL preview,development

# Add non-interactively via pipe
echo -n "secret-token-value" | vercel env add API_SECRET production

# List environment variables across environments
vercel env ls

# Pull environment variables into local .env.local file
vercel env pull .env.local

# Remove a variable
vercel env rm DATABASE_URL production -y
```

#### Framework Prefixing Rules:
- Server-side secrets (`DATABASE_URL`, `STRIPE_KEY`): Do not prefix. Kept private to functions.
- Next.js client-exposed variables: Must start with `NEXT_PUBLIC_` (e.g., `NEXT_PUBLIC_APP_ID`).
- Vite client-exposed variables: Must start with `VITE_` (e.g., `VITE_API_ENDPOINT`).

#### Built-in Vercel System Variables:
Vercel exposes ambient environment variables during builds and runtime:
- `VERCEL_ENV`: `"production"`, `"preview"`, or `"development"`.
- `VERCEL_URL`: Domain host of the deployment (e.g., `project-abc-org.vercel.app`).
- `VERCEL_GIT_COMMIT_SHA`: SHA hash of the triggered commit.
- `VERCEL_GIT_COMMIT_REF`: Target branch name.

### 1.3 Serverless & Edge Functions

Vercel supports two function execution runtimes in `/api`:

#### Standard Serverless Function (Node.js Runtime):
```typescript
// api/users/[id].ts
import type { VercelRequest, VercelResponse } from '@vercel/node';

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  const { id } = req.query;

  try {
    // Database query or external I/O
    return res.status(200).json({
      id,
      timestamp: new Date().toISOString(),
      runtime: 'nodejs-serverless',
    });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Internal Server Error';
    return res.status(500).json({ error: message });
  }
}
```

#### Edge Function (V8 Runtime, Web Standards):
```typescript
// api/edge-hello.ts
export const config = {
  runtime: 'edge', // Explicitly switches execution to V8 Edge
};

export default async function handler(request: Request) {
  const url = new URL(request.url);
  const name = url.searchParams.get('name') || 'Guest';

  return new Response(
    JSON.stringify({
      greeting: `Hello, ${name}!`,
      region: process.env.VERCEL_REGION || 'edge',
      timestamp: Date.now(),
    }),
    {
      status: 200,
      headers: {
        'content-type': 'application/json',
        'cache-control': 'public, s-maxage=60, stale-while-revalidate=300',
      },
    }
  );
}
```

### 1.4 Preview Deployments & Branch Deploys

- Every Git push to a non-production branch generates a dedicated preview deployment URL with automatic SSL.
- Pull requests receive automatic bot comments containing the live preview URL and build inspection link.
- **Custom Branch Domains**: Assign persistent domain aliases for long-running branches:
  - Settings -> Domains -> Add `staging.yourdomain.com` -> Select branch `staging`.

### 1.5 Custom Domains & DNS Configuration

#### Domain Assignment Rules:
- **Apex Domain (`example.com`)**:
  - `A` Record: `@` pointing to `76.76.21.21`
  - Or ALIAS / ANAME pointing to `cname.vercel-dns.com.`
- **Subdomain (`app.example.com` or `www.example.com`)**:
  - `CNAME` Record: pointing to `cname.vercel-dns.com.`

#### Managing via CLI:
```bash
# Add a domain to the current project
vercel domains add app.example.com

# Inspect DNS verification status
vercel domains inspect app.example.com

# Verify configuration issues
vercel dns ls
```

### 1.6 Build Settings & Framework Presets

Vercel automatically detects presets (Next.js, Vite, Astro, SvelteKit, Nuxt, Remix). Custom overrides can be set in project settings or `vercel.json`:

```json
{
  "buildCommand": "pnpm build",
  "outputDirectory": "dist",
  "installCommand": "pnpm install --frozen-lockfile",
  "framework": "vite"
}
```

### 1.7 Vercel CLI Workflows

```bash
# 1. Link current directory to Vercel project
vercel link

# 2. Emulate production/preview locally with live environment parity
vercel dev --listen 3000

# 3. Deploy an ephemeral Preview build from local files
vercel

# 4. Deploy directly to Production
vercel --prod

# 5. Tail live production logs
vercel logs <DEPLOYMENT_URL_OR_ID> --follow
```

### 1.8 Cron Jobs

Configure scheduled endpoints using the `crons` array in `vercel.json`. The endpoints must be reachable via standard HTTP GET.

```json
{
  "crons": [
    {
      "path": "/api/cron/sync-orders",
      "schedule": "*/15 * * * *"
    }
  ]
}
```

#### Securing Cron Handlers:
Vercel automatically includes an `Authorization: Bearer <CRON_SECRET>` header on cron invocations:

```typescript
// api/cron/sync-orders.ts
import type { VercelRequest, VercelResponse } from '@vercel/node';

export default async function handler(req: VercelRequest, res: VercelResponse) {
  const authHeader = req.headers['authorization'];
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return res.status(401).json({ error: 'Unauthorized invocation' });
  }

  // Idempotent background operation
  return res.status(200).json({ success: true, processedAt: new Date().toISOString() });
}
```

### 1.9 Analytics & Speed Insights

Instrument real-user monitoring (RUM) and Core Web Vitals tracking:

```bash
npm install @vercel/analytics @vercel/speed-insights
```

```typescript
// In root layout or app component:
import { Analytics } from '@vercel/analytics/react';
import { SpeedInsights } from '@vercel/speed-insights/react';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        {children}
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}
```

### 1.10 Deployment Protection

Protect non-production previews or production staging environments:
- **Standard Password Protection**: Require a single shared password to view deployments.
- **Vercel Authentication**: Require users to be members of your Vercel Team.
- **Bypass Tokens for Automated Testing (CI/CD)**:
  Configure `x-vercel-protection-bypass` header or secret query parameter `?_vercel_share=<SECRET>` to permit headless browser suites (Playwright, Cypress) through protected previews.

---

## 2. Cloudflare Pages Deployment & Configuration

### 2.1 Project Architecture & Setup

Cloudflare Pages serves static assets globally from Cloudflare's edge network, while dynamic backends are powered by Pages Functions built on the V8 isolate Cloudflare Workers runtime.

#### Wrangler Configuration (`wrangler.toml`):
Create `wrangler.toml` in your project root to declare compatibility dates, bindings, and environment behaviors:

```toml
name = "web-application-pages"
compatibility_date = "2024-09-23"
compatibility_flags = ["nodejs_compat"]
pages_build_output_dir = "dist"

# KV Namespace Bindings
[[kv_namespaces]]
binding = "CACHE_STORE"
id = "2d0b5e39660c4a45a22c54d1d9183419"
preview_id = "7c1b5e39660c4a45a22c54d1d9183420"

# D1 Database Bindings
[[d1_databases]]
binding = "DB"
database_name = "production-db"
database_id = "8f3b41e2-5401-49fa-9486-e2bb134d1933"
preview_database_id = "8f3b41e2-5401-49fa-9486-e2bb134d1934"

# R2 Object Storage Bucket Bindings
[[r2_buckets]]
binding = "BUCKET"
bucket_name = "production-assets-bucket"
preview_bucket_name = "preview-assets-bucket"

# Plain Environment Variables
[vars]
PUBLIC_API_URL = "https://api.example.com"
APP_ENV = "production"

[env.preview.vars]
PUBLIC_API_URL = "https://staging-api.example.com"
APP_ENV = "preview"
```

### 2.2 Build Settings & Secrets Management

#### Wrangler Secret Commands:
Store sensitive keys securely in Cloudflare's encrypted key vault:

```bash
# Add an encrypted secret to production
npx wrangler pages secret put DATABASE_PASSWORD --project-name my-app-pages

# Add a secret for preview environments
npx wrangler pages secret put DATABASE_PASSWORD --project-name my-app-pages --env preview

# List configured secrets
npx wrangler pages secret list --project-name my-app-pages

# Delete a secret
npx wrangler pages secret delete DATABASE_PASSWORD --project-name my-app-pages
```

### 2.3 `_redirects` and `_headers` Routing Files

Place these files in the build output directory (`dist/`, `build/`, or `public/` depending on the framework).

#### `_redirects` File Rules:
Lines are evaluated top-to-bottom. Supported status codes: `301`, `302`, `307`, `308`, and `200` (proxy rewrite).

```text
# Exact 301 Permanent Redirect
/old-page              /new-page               301

# Placeholders
/users/:id/profile     /profiles/:id           302

# Wildcard / Splat Redirect
/blog-legacy/*         /news/:splat            301

# Single Page Application (SPA) Fallback Rewrite (Status 200)
/*                     /index.html             200

# Edge Reverse Proxy Rewrite
/proxy-api/*           https://api.backend.io/:splat  200!
```

#### `_headers` File Rules:
Defines response headers matching path patterns:

```text
/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';

# Static immutable assets
/assets/*
  Cache-Control: public, max-age=31536000, immutable

# Prevent caching on dynamic app config
/config.json
  Cache-Control: no-cache, no-store, must-revalidate
```

### 2.4 Cloudflare Pages Functions

Directory-based routing using the `/functions` directory in your root folder.

#### Dynamic API Route:
```typescript
// functions/api/users/[id].ts
interface Env {
  CACHE_STORE: KVNamespace;
  DB: D1Database;
  BUCKET: R2Bucket;
  AUTH_SECRET: string;
}

export const onRequestGet: PagesFunction<Env> = async (context) => {
  const { id } = context.params;
  const { CACHE_STORE, DB } = context.env;

  // 1. Check KV Edge Cache
  const cacheKey = `user:${id}`;
  const cachedUser = await CACHE_STORE.get(cacheKey, { type: 'json' });
  if (cachedUser) {
    return Response.json(cachedUser, {
      headers: { 'X-Cache': 'HIT', 'Cache-Control': 'public, max-age=60' },
    });
  }

  // 2. Query D1 SQL Database
  const result = await DB.prepare('SELECT id, name, email, created_at FROM users WHERE id = ?')
    .bind(id)
    .first();

  if (!result) {
    return new Response(JSON.stringify({ error: 'User not found' }), {
      status: 404,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // 3. Write to KV Edge Cache asynchronously (does not block response)
  context.waitUntil(CACHE_STORE.put(cacheKey, JSON.stringify(result), { expirationTtl: 300 }));

  return Response.json(result, {
    headers: { 'X-Cache': 'MISS', 'Cache-Control': 'public, max-age=60' },
  });
};
```

#### Middleware Handler:
Intercept requests before they reach static assets or downstream function handlers:

```typescript
// functions/_middleware.ts
interface Env {
  ENVIRONMENT: string;
}

export const onRequest: PagesFunction<Env> = async (context) => {
  const start = Date.now();
  
  // Custom auth validation or header checks
  const authHeader = context.request.headers.get('Authorization');
  if (context.request.url.includes('/api/protected') && !authHeader) {
    return new Response('Unauthorized', { status: 401 });
  }

  // Continue to next handler / asset
  const response = await context.next();

  // Clone or modify response headers
  const newResponse = new Response(response.body, response);
  newResponse.headers.set('X-Response-Time-Ms', String(Date.now() - start));
  newResponse.headers.set('X-Edge-Region', context.request.cf?.colo as string || 'unknown');

  return newResponse;
};
```

### 2.5 Storage Bindings (KV, D1, R2)

#### 1. Cloudflare KV (Low-latency Key-Value):
```bash
# Create production and preview namespaces
npx wrangler kv:namespace create CACHE_STORE
npx wrangler kv:namespace create CACHE_STORE --preview
```

Usage in functions:
```typescript
await env.CACHE_STORE.put('session:abc', JSON.stringify(sessionData), { expirationTtl: 86400 });
const session = await env.CACHE_STORE.get('session:abc', 'json');
await env.CACHE_STORE.delete('session:abc');
```

#### 2. Cloudflare D1 (Serverless Distributed SQLite):
```bash
# Create database
npx wrangler d1 create production-db

# Execute schema migrations locally and remotely
npx wrangler d1 execute production-db --local --file=./schema.sql
npx wrangler d1 execute production-db --remote --file=./schema.sql
```

Usage in functions:
```typescript
// Batch query execution inside a transaction
const results = await env.DB.batch([
  env.DB.prepare('UPDATE accounts SET balance = balance - ? WHERE id = ?').bind(100, sourceId),
  env.DB.prepare('UPDATE accounts SET balance = balance + ? WHERE id = ?').bind(100, targetId),
]);
```

#### 3. Cloudflare R2 (Zero-Egress Object Storage):
```bash
# Create R2 bucket
npx wrangler r2 bucket create production-assets-bucket
```

Usage in functions:
```typescript
// Upload file
await env.BUCKET.put(`uploads/${filename}`, fileBuffer, {
  httpMetadata: { contentType: mimeType },
});

// Retrieve file
const object = await env.BUCKET.get(`uploads/${filename}`);
if (!object) return new Response('Not Found', { status: 404 });
return new Response(object.body, {
  headers: { 'Content-Type': object.httpMetadata?.contentType || 'application/octet-stream' },
});
```

### 2.6 Wrangler CLI Workflows

```bash
# 1. Create a new Pages project
npx wrangler pages project create my-app-pages --production-branch main

# 2. Emulate static assets and functions locally with binding simulation
npx wrangler pages dev ./dist --kv CACHE_STORE --d1 DB --compatibility-date 2024-09-23

# 3. Deploy direct build output as a Preview deployment
npx wrangler pages deploy ./dist --project-name my-app-pages --branch feature-navbar

# 4. Deploy direct build output to Production
npx wrangler pages deploy ./dist --project-name my-app-pages --branch main

# 5. Tail real-time live execution logs
npx wrangler pages deployment tail --project-name my-app-pages
```

### 2.7 Custom Domains & Cloudflare DNS

- **Automated Zone**: If the domain is already hosted in Cloudflare DNS, adding a custom domain to Pages automatically provisions DNS records (CNAME flattening) and generates universal SSL certificates with zero manual DNS record creation.
- **External DNS**: Add a `CNAME` pointing to `<project-name>.pages.dev`. Cloudflare validates domain verification via an ownership TXT record.

### 2.8 Pages Plugins

Pages Plugins encapsulate complex function logic (e.g., authentication, static forms, Sentry error monitoring) as reusable packages:

```bash
npm install @cloudflare/pages-plugin-static-forms
```

```typescript
// functions/contact.ts
import staticFormsPlugin from '@cloudflare/pages-plugin-static-forms';

export const onRequest = staticFormsPlugin({
  respondWith: () => new Response('Thank you for contacting us!'),
});
```

---

## 3. Cross-Platform Unified Architectures

### 3.1 Git-Based CI/CD Pipelines

Both platforms integrate directly with GitHub, GitLab, and Bitbucket. For teams using custom GitHub Actions runners or self-hosted pipelines, use the following headless deployment patterns:

#### GitHub Actions Workflow for Vercel:
```yaml
name: Deploy to Vercel
on:
  push:
    branches: [main]
  pull_request:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Install Vercel CLI
        run: pnpm add -g vercel@latest

      - name: Pull Vercel Environment Information
        run: |
          if [ "${{ github.event_name }}" = "push" ]; then
            vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}
          else
            vercel pull --yes --environment=preview --token=${{ secrets.VERCEL_TOKEN }}
          fi

      - name: Build Project Artifacts
        run: |
          if [ "${{ github.event_name }}" = "push" ]; then
            vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}
          else
            vercel build --token=${{ secrets.VERCEL_TOKEN }}
          fi

      - name: Deploy to Vercel
        run: |
          if [ "${{ github.event_name }}" = "push" ]; then
            vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}
          else
            vercel deploy --prebuilt --token=${{ secrets.VERCEL_TOKEN }}
          fi
```

#### GitHub Actions Workflow for Cloudflare Pages:
```yaml
name: Deploy to Cloudflare Pages
on:
  push:
    branches: [main]
  pull_request:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Build Application
        run: pnpm build

      - name: Deploy to Cloudflare Pages
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          command: >-
            pages deploy dist
            --project-name=my-app-pages
            --branch=${{ github.head_ref || github.ref_name }}
```

### 3.2 Monorepo Configuration (Turborepo / pnpm / Nx)

When deploying applications located in a subfolder of a monorepo (e.g., `apps/web`), configure project root and build cancellation scripts to prevent redundant builds when unrelated packages change.

#### Root Directory Setting:
Set Root Directory in Vercel or Cloudflare Pages project settings to: `apps/web`.

#### Vercel Ignored Build Step:
Configure in Project Settings -> Git -> Ignored Build Step (or via `npx turbo-ignore`):
```bash
# Custom verification script
git diff --quiet HEAD^ HEAD . || exit 1
```
- Exit code `1`: Changes detected -> Build proceeds.
- Exit code `0`: No changes detected -> Build is canceled without counting against limits.

#### Cloudflare Pages Monorepo Build Command:
Run builds from monorepo root or set working directory:
```bash
# Build script configured in Pages settings
pnpm --filter web build
```

### 3.3 Static vs SSR Deployment Mechanics

| Framework | Vercel Deployment Target | Cloudflare Pages Deployment Target |
| :--- | :--- | :--- |
| **Next.js** | Native (`next build`) | `@cloudflare/next-on-pages` |
| **Astro** | `@astrojs/vercel` (server or static) | `@astrojs/cloudflare` |
| **Remix** | `@vercel/remix` | `@remix-run/cloudflare` |
| **SvelteKit** | `@sveltejs/adapter-vercel` | `@sveltejs/adapter-cloudflare` |
| **Vite SPA** | Native static output (`dist`) | Native static output (`dist`) with `/* /index.html 200` |

#### Astro Adapter Configuration Example:
```typescript
// astro.config.mjs
import { defineConfig } from 'astro/config';
import vercel from '@astrojs/vercel/serverless';
import cloudflare from '@astrojs/cloudflare';

const isVercel = process.env.DEPLOY_TARGET === 'vercel';

export default defineConfig({
  output: 'server',
  adapter: isVercel
    ? vercel()
    : cloudflare({
        imageService: 'cloudflare',
        platformProxy: { enabled: true },
      }),
});
```

### 3.4 CDN, Caching & Edge Performance Strategies

#### Modern Cache-Control Header Patterns:
```text
# 1. Immutable static content (hashed assets, scripts, stylesheets, fonts)
Cache-Control: public, max-age=31536000, immutable

# 2. Dynamic content with Edge Stale-While-Revalidate (instant edge response, async background refresh)
Cache-Control: public, s-maxage=60, stale-while-revalidate=86400

# 3. Dynamic API responses that must never be cached at any proxy or edge
Cache-Control: private, no-cache, no-store, must-revalidate
```

#### Cache Status Headers:
- **Vercel**: Inspect the `x-vercel-cache` response header:
  - `HIT`: Served directly from Vercel edge cache.
  - `MISS`: Fetched from origin serverless function and stored.
  - `BYPASS`: Cache bypassed due to request headers or configuration.
  - `STALE`: Stale response returned while revalidation runs in background.
- **Cloudflare**: Inspect the `cf-cache-status` response header:
  - `HIT`: Served from Cloudflare Edge cache.
  - `DYNAMIC`: Request was not eligible for caching (passed to Function/Worker).
  - `REVALIDATED`: Stale cache verified with origin using `If-Modified-Since`.
  - `EXPIRED`: Cache expired; fresh copy fetched from origin.

### 3.5 Cross-Platform Migration Guide

#### Migrating from Vercel to Cloudflare Pages:
1. **Routing and Rewrites**:
   - Extract `vercel.json` `redirects` into root `public/_redirects`.
   - Extract `vercel.json` `headers` into root `public/_headers`.
2. **API Routes**:
   - Move Node.js `/api` endpoints to `/functions/api`.
   - Replace Node-specific modules (`fs`, `net`, `http`) with Web standard APIs (`Request`, `Response`, `fetch`, `crypto`).
   - Add `nodejs_compat` to `compatibility_flags` in `wrangler.toml` for supported Node APIs (`Buffer`, `events`, `util`).
3. **Database & Storage**:
   - Replace Vercel Blob with Cloudflare R2 (`env.BUCKET.put()`).
   - Replace Vercel KV with Cloudflare KV (`env.CACHE.get()`).
   - Replace external SQL or Vercel Postgres with Cloudflare D1 or connect via Hyperdrive.
4. **Environment Variables**:
   - Migrate via `wrangler pages secret put <KEY>`.

#### Migrating from Cloudflare Pages to Vercel:
1. **Routing and Rewrites**:
   - Convert `_redirects` rules into the `redirects` and `rewrites` arrays in `vercel.json`.
   - Convert `_headers` into the `headers` array in `vercel.json`.
2. **Functions**:
   - Move `/functions` logic into `/api` handlers.
   - Replace Cloudflare-specific bindings (`env.DB`, `env.BUCKET`, `env.CACHE_STORE`) with standard Node client libraries (e.g., `@aws-sdk/client-s3` for S3/R2, `pg` for Postgres, `@upstash/redis` for KV).
3. **Cron Jobs**:
   - Convert scheduled cron hooks into `vercel.json` `crons` entries with authorization guards.

---

## Best Practices

- **Zero Secret Exposure**: Never commit `.env*` files, sensitive API tokens, or `.vercel` / `.wrangler` local state directories to version control. Maintain `.gitignore`:
  ```text
  .vercel
  .wrangler
  .env*.local
  .env
  dist
  .turbo
  ```
- **Explicit Compatibility Locking**: Always declare an explicit `compatibility_date` in Cloudflare Pages configurations to prevent runtime behavior shifts when new edge runtimes release.
- **Node.js Compatibility Flag**: In Cloudflare Pages, include `compatibility_flags = ["nodejs_compat"]` whenever using modern libraries that rely on Node.js globals or streaming utilities.
- **Immutable Asset Hashing**: Ensure build tools generate content-hashed asset names (e.g., `bundle.8a3c9b.js`) so that long-lived caching (`max-age=31536000, immutable`) never serves stale assets.
- **Fail-Open Verification**: Guard edge middlewares and functions with structured error handlers to prevent total edge site lockouts on database/storage connection hiccups.
- **Least-Privilege CI Tokens**: Grant CI/CD tokens scope only to the targeted project rather than full administrative organization permissions.

---

## Common Pitfalls

- **Using Node.js APIs on Edge Runtimes without Compatibility Flags**:
  - *Symptom*: Build or execution error `process is not defined`, `Buffer is not defined`, or `Dynamic require of "..." is not supported`.
  - *Remedy*: In Cloudflare, enable `nodejs_compat` in `wrangler.toml`. In Vercel, ensure edge functions do not import Node core modules or switch `runtime` from `'edge'` to standard serverless Node.js.
- **Missing SPA Rewrite**:
  - *Symptom*: Navigating directly to `/dashboard/settings` returns 404 on Vite or React SPAs.
  - *Remedy*: Add `/* /index.html 200` to `_redirects` (Cloudflare) or a wildcard rewrite rule to `/index.html` in `vercel.json`.
- **Misplaced `_redirects` or `_headers` Files**:
  - *Symptom*: Redirects or security headers are completely ignored by Cloudflare Pages.
  - *Remedy*: Ensure build tools copy these files from `public/` into the final build output directory (`dist/` or `build/`). Check the output folder after `pnpm build`.
- **Exceeding Execution Time Limits**:
  - *Symptom*: Requests return HTTP 504 Gateway Timeout or function crashes.
  - *Remedy*: Standard Vercel Hobby tier caps serverless functions at 10-15 seconds. Cloudflare Pages Functions run on worker isolate limits (up to 30s wall time). Offload long-running batch work to dedicated queues or external workers.
- **CORS Failures on Edge Proxies**:
  - *Symptom*: Browser blocks API requests from cross-origin clients.
  - *Remedy*: Explicitly handle `OPTIONS` preflight requests in `/api` or `/functions` with appropriate `Access-Control-Allow-Origin` and `Access-Control-Allow-Methods` headers.

---

## Verification & Validation

Execute these steps to confirm proper configuration and deployment behavior:

### 1. Build & Local Emulation Check
```bash
# Verify local build output is created without errors
pnpm build

# Verify presence of routing files in build output (for Cloudflare)
ls -la dist/_redirects dist/_headers 2>/dev/null || echo "Files missing in build folder"

# Local emulation test: Vercel
npx vercel dev --listen 3000

# Local emulation test: Cloudflare Pages
npx wrangler pages dev ./dist --compatibility-date 2024-09-23
```

### 2. HTTP Header & Routing Inspection
Run against your deployed URL (Preview or Production):

```bash
# Verify security headers and HTTP status
curl -I -s https://your-deployment-url.app | grep -iE 'x-frame-options|content-security-policy|x-content-type-options'

# Inspect caching behavior
curl -I -s https://your-deployment-url.app/assets/index.js | grep -iE 'cache-control|cf-cache-status|x-vercel-cache'

# Verify redirect rule (expect 301 / 308)
curl -I -s https://your-deployment-url.app/old-page | grep -iE 'http/|location'

# Verify SPA fallback on deep routes (expect HTTP 200 with HTML content)
curl -s -o /dev/null -w "%{http_code}\n" https://your-deployment-url.app/deep/nested/route
```

### 3. Edge Function & Binding Health Check
```bash
# Test API endpoint response and timing
curl -w "\nTime: %{time_total}s | Status: %{http_code}\n" -s https://your-deployment-url.app/api/health

# Tail live execution logs during test invocations
# For Vercel:
npx vercel logs <DEPLOYMENT_URL>

# For Cloudflare:
npx wrangler pages deployment tail --project-name <PROJECT_NAME>
```
