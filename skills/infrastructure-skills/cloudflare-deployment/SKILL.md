---
name: cloudflare-deployment
description: >-
  Deploy, configure, and maintain web applications, static sites, and edge functions on Cloudflare Pages and Workers.
  Use when configuring wrangler.toml or wrangler.jsonc, managing _routes.json, _headers, and _redirects,
  binding storage (KV, D1, R2), debugging edge functions, or executing deployments with Wrangler CLI.
---

# Cloudflare Pages & Workers Deployment

Comprehensive guide and operational runbook for deploying frontend applications, static assets, and edge-native serverless functions onto Cloudflare Pages and Cloudflare Workers.

## Official Documentation & Skill References

Refer directly to official Cloudflare developer documentation and agent-ready references for live API schemas, compatibility flags, and command flags:

- **Official Cloudflare Pages Documentation**: [https://developers.cloudflare.com/pages/](https://developers.cloudflare.com/pages/)
- **Official Cloudflare Workers Documentation**: [https://developers.cloudflare.com/workers/](https://developers.cloudflare.com/workers/)
- **Official Wrangler CLI Guide**: [https://developers.cloudflare.com/workers/wrangler/](https://developers.cloudflare.com/workers/wrangler/)
- **Cloudflare Agent LLMs Reference**: [https://developers.cloudflare.com/workers/llms-full.txt](https://developers.cloudflare.com/workers/llms-full.txt)
- **Context7 Library IDs**:
  - Cloudflare Pages: `/websites/developers_cloudflare_pages`
  - Cloudflare Workers: `/llmstxt/developers_cloudflare_workers_llms-full_txt`
  - Run `npx ctx7@latest docs /websites/developers_cloudflare_pages "<query>"` for live updates.

---

## When to Use

Activate this skill when:
- Deploying full-stack web applications, blogs, or SPAs to Cloudflare Pages via Git or the Wrangler CLI.
- Configuring `wrangler.jsonc` or `wrangler.toml` for Pages and Workers projects.
- Writing and structuring file-based Pages Functions under `/functions`.
- Defining client routing and edge caching rules with `_headers`, `_redirects`, and `_routes.json`.
- Binding edge storage primitives (Workers KV, D1 SQL Database, R2 Object Storage, Vectorize, Hyperdrive).
- Setting environment variables and managing secrets with `wrangler pages secret`.
- Emulating the Cloudflare edge runtime locally using `wrangler pages dev`.
- Setting up GitHub Actions or automated CI/CD pipelines targeting Cloudflare.

---

## Prerequisites

- **Wrangler CLI**: The official developer CLI for Cloudflare Workers and Pages:
  ```bash
  npm install -D wrangler@latest
  # or invoke directly via:
  npx wrangler <command>
  ```
- **Authentication**: Authenticate using your Cloudflare account or API token:
  ```bash
  npx wrangler login
  # Or provide environment variables:
  export CLOUDFLARE_API_TOKEN="your-api-token"
  export CLOUDFLARE_ACCOUNT_ID="your-account-id"
  ```
- Node.js version 18+ or 20+ installed locally.

---

## Core Workflows

### 1. Project Configuration (`wrangler.jsonc` / `wrangler.toml`)

Wrangler 3.45.0+ supports configuring Pages projects directly via `wrangler.jsonc` (preferred) or `wrangler.toml`:

#### `wrangler.jsonc` Example
```jsonc
{
  "$schema": "node_modules/wrangler/config-schema.json",
  "name": "my-application",
  "pages_build_output_dir": "./dist",
  "compatibility_date": "2026-10-01",
  "compatibility_flags": ["nodejs_compat"],
  "vars": {
    "ENVIRONMENT": "production",
    "API_VERSION": "v1"
  },
  "kv_namespaces": [
    {
      "binding": "CACHE_KV",
      "id": "YOUR_KV_NAMESPACE_ID"
    }
  ],
  "d1_databases": [
    {
      "binding": "DB",
      "database_name": "production-db",
      "database_id": "YOUR_D1_DATABASE_ID"
    }
  ],
  "r2_buckets": [
    {
      "binding": "UPLOADS_BUCKET",
      "bucket_name": "app-uploads"
    }
  ]
}
```

---

### 2. Static Asset Routing: `_headers`, `_redirects`, and `_routes.json`

Place these files directly inside your build output directory (e.g., `./public` or `./dist`).

#### Static Security & Cache Headers (`_headers`)
```http
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()

/assets/*
  Cache-Control: public, max-age=31536000, immutable

/index.html
  Cache-Control: public, max-age=0, must-revalidate
```

#### URL Redirections & Proxies (`_redirects`)
```http
# 301 Permanent Redirect
/old-page           /new-page           301

# 302 Temporary Redirect
/temp-promo         /summer-sale        302

# 200 Proxy / Rewrite (Edge Pass-through)
/api/external/*     https://api.external.com/:splat 200

# SPA Fallback for client-side routing
/*                  /index.html         200
```

#### Function Invocation Optimization (`_routes.json`)
By default, every request is checked by Pages Functions. Use `_routes.json` to prevent unnecessary worker executions for static assets:

```json
{
  "version": 1,
  "include": [
    "/api/*",
    "/auth/*"
  ],
  "exclude": [
    "/assets/*",
    "/favicon.ico",
    "/robots.txt",
    "/sitemap.xml"
  ]
}
```

---

### 3. Pages Functions Architecture (`/functions`)

Files placed under `/functions` are automatically mounted as edge serverless endpoints using file-based routing:

```text
my-project/
├── functions/
│   ├── _middleware.ts            # Runs on every function request
│   ├── api/
│   │   ├── health.ts             # Accessible at /api/health
│   │   └── items/
│   │       ├── index.ts          # Accessible at /api/items
│   │       └── [id].ts           # Accessible at /api/items/:id
└── dist/                         # Static assets build output
```

#### Middleware Example (`functions/_middleware.ts`)
```typescript
interface Env {
  ENVIRONMENT: string;
}

export const onRequest: PagesFunction<Env> = async (context) => {
  const start = Date.now();
  const response = await context.next();
  const duration = Date.now() - start;

  response.headers.set('X-Response-Time', `${duration}ms`);
  return response;
};
```

#### CRUD Endpoint with D1 and KV (`functions/api/items/[id].ts`)
```typescript
interface Env {
  DB: D1Database;
  CACHE_KV: KVNamespace;
}

export const onRequestGet: PagesFunction<Env> = async (context) => {
  const itemId = context.params.id as string;

  // 1. Try reading from KV Cache
  const cached = await context.env.CACHE_KV.get(`item:${itemId}`, 'json');
  if (cached) {
    return Response.json(cached, {
      headers: { 'X-Cache': 'HIT' }
    });
  }

  // 2. Query D1 Database
  const item = await context.env.DB.prepare(
    'SELECT id, title, content, created_at FROM items WHERE id = ?'
  )
    .bind(itemId)
    .first();

  if (!item) {
    return new Response(JSON.stringify({ error: 'Item not found' }), {
      status: 404,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  // 3. Write through to KV cache with 5-minute TTL
  await context.env.CACHE_KV.put(`item:${itemId}`, JSON.stringify(item), {
    expirationTtl: 300
  });

  return Response.json(item, {
    headers: { 'X-Cache': 'MISS' }
  });
};
```

---

### 4. Local Development & Edge Emulation

Emulate the live Cloudflare production environment locally (including bindings, D1, KV, and R2):

```bash
# Start local emulation serving static assets from ./dist and running /functions
npx wrangler pages dev ./dist

# Emulate with a custom live port and binding local D1 storage
npx wrangler pages dev ./dist --port 8788 --d1 DB=production-db --kv CACHE_KV
```

---

### 5. Deployment Commands

#### Direct CLI Deployment
Deploy build output to Cloudflare Pages:

```bash
# Build your frontend application first
npm run build

# Deploy to preview (branch-based URL)
npx wrangler pages deploy ./dist --project-name=my-application --branch=preview

# Deploy directly to production
npx wrangler pages deploy ./dist --project-name=my-application --branch=main
```

#### Managing Production Secrets
Secrets are encrypted and never checked into source control:

```bash
# Upload a secret to Cloudflare Pages
npx wrangler pages secret put DATABASE_PASSWORD --project-name=my-application

# List configured secret names
npx wrangler pages secret list --project-name=my-application
```

---

### 6. Automated GitHub Actions Workflow

Deploy automatically from GitHub Actions without third-party actions by using Wrangler directly:

```yaml
name: Deploy to Cloudflare Pages

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      deployments: write
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build application
        run: npm run build

      - name: Deploy to Cloudflare Pages
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          command: pages deploy ./dist --project-name=my-application --branch=main
```

---

## Best Practices

1. **Always Set `compatibility_date` and `nodejs_compat`**: Lock `compatibility_date` to an explicit current date and enable `"nodejs_compat"` to leverage Node.js standard APIs (`Buffer`, `crypto`, `events`, `stream`) in Workers and Pages Functions.
2. **Optimize Invocations with `_routes.json`**: Make sure static assets are excluded in `_routes.json` so requests for images, CSS, and JS never count against Worker invocation quotas.
3. **Use D1 Prepared Statements**: Always use `.bind()` on D1 queries to prevent SQL injection vulnerabilities and utilize statement caching.
4. **Leverage KV TTL**: For read-heavy endpoints, wrap database queries with KV lookups configured with `expirationTtl` (minimum 60 seconds).

---

## Common Pitfalls

- **Deploying Unbuilt Source**: Cloudflare Pages CLI deployments (`pages deploy`) upload static files already built. Never point the deployment directory to `./src`. Point to `./dist`, `./out`, or `./build`.
- **Node.js Native Modules**: Cloudflare Workers runs on the V8 isolate runtime, not standard Node.js. C++ binary addons (`bcrypt`, native `sharp`, `canvas`) will fail. Use WebAssembly (Wasm) or pure JS equivalents (`@node-rs/bcrypt`, `argon2-wasm`).
- **Exceeding KV Write Limits**: KV is designed for read-heavy workloads (high read throughput, eventually consistent). Do not use KV for high-frequency writes or counter increments; use Durable Objects or D1 instead.

---

## Verification & Diagnostics

Validate the deployment status, logs, and routing rules:

```bash
# Tail live production logs in real time
npx wrangler pages deployment tail --project-name=my-application

# Verify build outputs and project metadata
npx wrangler pages project list

# Inspect response headers with curl
curl -I https://<my-project>.pages.dev
# Look for 'cf-ray', 'cf-cache-status', and your custom security headers
```
