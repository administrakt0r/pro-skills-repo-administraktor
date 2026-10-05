# Cloudflare Wrangler & Pages Patterns

Comprehensive production templates and pattern library for `wrangler.jsonc`, `wrangler.toml`, storage bindings, and Cloudflare Pages Functions.

## 1. Full Production `wrangler.jsonc`

Complete configuration demonstrating multiple storage bindings, environment overrides, and modern Node.js compatibility:

```jsonc
{
  "$schema": "node_modules/wrangler/config-schema.json",
  "name": "edge-saas-platform",
  "pages_build_output_dir": "./dist",
  "compatibility_date": "2026-10-01",
  "compatibility_flags": [
    "nodejs_compat"
  ],
  "vars": {
    "APP_ENV": "production",
    "MAX_UPLOAD_BYTES": 10485760
  },
  "kv_namespaces": [
    {
      "binding": "SESSION_KV",
      "id": "e4f87a82914041b3a5b6d9e0f317b621"
    },
    {
      "binding": "CACHE_KV",
      "id": "9b12c83f982142e0947baef00c7a1512"
    }
  ],
  "d1_databases": [
    {
      "binding": "PRIMARY_DB",
      "database_name": "saas-production",
      "database_id": "78b45610-d321-4f90-a42e-cf65421098ef"
    }
  ],
  "r2_buckets": [
    {
      "binding": "ASSETS_BUCKET",
      "bucket_name": "customer-assets-prod"
    }
  ],
  "env": {
    "staging": {
      "vars": {
        "APP_ENV": "staging"
      },
      "d1_databases": [
        {
          "binding": "PRIMARY_DB",
          "database_name": "saas-staging",
          "database_id": "99c12345-e432-4a01-b53f-ef12345678ab"
        }
      ]
    }
  }
}
```

---

## 2. Advanced Pages Function: R2 File Uploader & Streaming

Demonstrating direct uploads to R2 buckets with presigned URLs or direct byte streaming:

```typescript
// functions/api/upload.ts
interface Env {
  ASSETS_BUCKET: R2Bucket;
  MAX_UPLOAD_BYTES: number;
}

export const onRequestPost: PagesFunction<Env> = async (context) => {
  const { request, env } = context;

  const contentType = request.headers.get('content-type') || '';
  if (!contentType.includes('multipart/form-data')) {
    return new Response(JSON.stringify({ error: 'Expected multipart/form-data' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const formData = await request.formData();
  const file = formData.get('file');

  if (!file || !(file instanceof File)) {
    return new Response(JSON.stringify({ error: 'No valid file provided' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  if (file.size > (env.MAX_UPLOAD_BYTES || 10 * 1024 * 1024)) {
    return new Response(JSON.stringify({ error: 'File size exceeds allowed quota' }), {
      status: 413,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const key = `uploads/${crypto.randomUUID()}-${file.name.replace(/[^a-zA-Z0-9.-]/g, '_')}`;

  await env.ASSETS_BUCKET.put(key, file.stream(), {
    httpMetadata: {
      contentType: file.type || 'application/octet-stream',
    },
    customMetadata: {
      uploadedAt: new Date().toISOString(),
      originalName: file.name,
    },
  });

  return Response.json({
    success: true,
    key,
    size: file.size,
    type: file.type,
  });
};
```

---

## 3. High-Performance Caching & Routing Rule (`_routes.json`)

Granular rule set separating client-side routing from API execution:

```json
{
  "version": 1,
  "include": [
    "/api/*",
    "/auth/*",
    "/webhooks/*"
  ],
  "exclude": [
    "/assets/*",
    "/static/*",
    "/fonts/*",
    "/images/*",
    "/favicon.ico",
    "/robots.txt",
    "/sitemap.xml",
    "/index.html"
  ]
}
```

---

## 4. D1 Database Schema Migration Pattern

Local and remote migration workflow using Wrangler:

```sql
-- migrations/0001_init_schema.sql
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    created_at INTEGER NOT NULL DEFAULT (unixepoch())
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

CREATE TABLE IF NOT EXISTS api_keys (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key_hash TEXT NOT NULL,
    expires_at INTEGER,
    created_at INTEGER NOT NULL DEFAULT (unixepoch())
);

CREATE INDEX IF NOT EXISTS idx_api_keys_user ON api_keys(user_id);
```

#### CLI Execution Commands
```bash
# Execute migration against local SQLite development store
npx wrangler d1 execute production-db --local --file=./migrations/0001_init_schema.sql

# Execute migration against live production Cloudflare D1
npx wrangler d1 execute production-db --remote --file=./migrations/0001_init_schema.sql
```
