---
name: vercel-deployment
description: >-
  Deploy, configure, and manage web applications and serverless architectures on Vercel.
  Use when configuring vercel.json, managing environment variables, configuring custom domains,
  setting up edge/serverless functions, debugging builds, or automating deployments via Vercel CLI.
---

# Vercel Deployment

Comprehensive guide and operational runbook for deploying, configuring, and optimizing modern full-stack web applications on Vercel.

## Official Documentation & Skill References

Always reference the official documentation and upstream skills for the latest CLI syntax, runtime flags, and platform specifications:

- **Official Vercel Documentation**: [https://vercel.com/docs](https://vercel.com/docs)
- **Official Vercel CLI Skill & Reference Suite**: [https://github.com/vercel/vercel/tree/main/skills/vercel-cli](https://github.com/vercel/vercel/tree/main/skills/vercel-cli)
- **Vercel CLI Command Reference**: [https://vercel.com/docs/cli](https://vercel.com/docs/cli)
- **Context7 Library ID**: `/vercel/vercel` — use `npx ctx7@latest docs /vercel/vercel "<query>"` for live API and CLI lookups.

---

## When to Use

Activate this skill when:
- Setting up continuous deployment or manual releases for web applications (Next.js, Astro, Remix, SvelteKit, static SPAs) on Vercel.
- Creating or editing `vercel.json` (rewrites, redirects, custom headers, security policies, cron jobs, edge functions).
- Managing environment variables across `development`, `preview`, and `production` scopes.
- Setting up Serverless Functions (`/api/*`) or Edge Runtime endpoints.
- Configuring custom domain mapping, DNS routing, and TLS certificates.
- Diagnosing build failures, cold starts, memory limits, or timeout errors (`504 GATEWAY_TIMEOUT`).
- Automating CI/CD deployment pipelines using GitHub Actions or the Vercel CLI.

---

## Prerequisites

- **Vercel CLI**: Installed globally or invoked via package runner:
  ```bash
  npm i -g vercel
  # or
  npx vercel <command>
  ```
- **Authentication**: Authenticate CLI session:
  ```bash
  vercel login
  ```
- Node.js runtime matching the application specification (configured in `package.json` `"engines"` or project settings).

---

## Core Workflows

### 1. Project Initialization & Linking

To link a local repository to a remote Vercel project non-interactively or interactively:

```bash
# Interactive linking
vercel link

# Non-interactive linking with project and org tokens
vercel link --project <project-name> --scope <team-slug> --yes
```

This creates `.vercel/project.json` containing `projectId` and `orgId`. Add `.vercel` to your `.gitignore`:

```gitignore
.vercel
.env*.local
```

---

### 2. Environment Variable Management

Manage environment variables across environments without visiting the dashboard.

#### Pull Remote Variables Locally
```bash
# Downloads production/preview environment variables into .env.local
vercel env pull

# Pull specific environment into designated file
vercel env pull .env.development.local --environment=development
```

#### Add and Update Variables
```bash
# Add variable interactively
vercel env add DATABASE_URL production

# Non-interactive addition with explicit values
vercel env add NEXT_PUBLIC_API_URL production --value "https://api.example.com" --yes
echo "super-secret-key" | vercel env add JWT_SECRET production preview --yes

# Update an existing variable
vercel env update DATABASE_URL production --value "postgres://user:pass@host:5432/db" --yes

# List and remove variables
vercel env ls
vercel env rm OLD_TOKEN production --yes
```

---

### 3. `vercel.json` Configuration

The `vercel.json` configuration file controls routing, header policies, runtime resource allocation, and scheduled jobs.

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "cleanUrls": true,
  "trailingSlash": false,
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
        { "key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=()" }
      ]
    },
    {
      "source": "/assets/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
      ]
    }
  ],
  "redirects": [
    {
      "source": "/old-path",
      "destination": "/new-path",
      "permanent": true
    }
  ],
  "rewrites": [
    {
      "source": "/api/proxy/:path*",
      "destination": "https://external-service.internal/:path*"
    }
  ],
  "functions": {
    "api/**/*.ts": {
      "memory": 1024,
      "maxDuration": 15
    }
  },
  "crons": [
    {
      "path": "/api/cron/cleanup",
      "schedule": "0 2 * * *"
    }
  ]
}
```

Detailed architectural templates can be found in [vercel-config-patterns.md](./references/vercel-config-patterns.md).

---

### 4. Deployments (Preview vs Production)

#### Preview Deployment
Triggers a preview deployment from the current working directory, generating a unique preview URL:
```bash
vercel
```

#### Production Deployment
Deploys directly to production domains:
```bash
vercel --prod
```

#### Prebuilt Deployment Workflow
For high-performance CI/CD builds, prebuild artifacts before uploading:
```bash
# 1. Pull environment info and settings
vercel pull --yes --environment=production

# 2. Build artifacts locally or inside runner
vercel build --prod

# 3. Deploy prebuilt artifacts instantly
vercel deploy --prebuilt --prod
```

---

### 5. Serverless & Edge Functions

Vercel automatically provisions routes defined in the `/api` directory:

#### Node.js Serverless Function (`api/health.ts`)
```typescript
import type { VercelRequest, VercelResponse } from '@vercel/node';

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  return res.status(200).json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    region: process.env.VERCEL_REGION || 'local'
  });
}
```

#### Edge Runtime Function (`api/edge-geo.ts`)
```typescript
export const config = {
  runtime: 'edge',
};

export default function handler(request: Request) {
  const country = request.headers.get('x-vercel-ip-country') || 'US';
  const city = request.headers.get('x-vercel-ip-city') || 'Unknown';

  return new Response(
    JSON.stringify({ country, city, edge: true }),
    {
      headers: { 'Content-Type': 'application/json' },
      status: 200,
    }
  );
}
```

---

### 6. Scheduled Cron Jobs & Authentication

When using the `crons` array in `vercel.json`, verify incoming requests using the `CRON_SECRET` header:

```typescript
import type { VercelRequest, VercelResponse } from '@vercel/node';

export default async function handler(req: VercelRequest, res: VercelResponse) {
  const authHeader = req.headers['authorization'];
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  // Execute scheduled batch logic
  return res.status(200).json({ success: true, processed: 100 });
}
```

---

### 7. Automated CI/CD (GitHub Actions)

Sample production workflow using Vercel CLI with GitHub Actions:

```yaml
name: Vercel Production Deployment

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Install Vercel CLI
        run: npm install --global vercel@latest

      - name: Pull Vercel Environment Information
        run: vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}
        env:
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}

      - name: Build Project Artifacts
        run: vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}

      - name: Deploy Project Artifacts to Vercel
        run: vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}
```

---

## Best Practices

1. **Keep Secrets out of Client Code**: Only prefix variables with `NEXT_PUBLIC_` or `VITE_` if they are strictly required in the browser. All database credentials, internal endpoints, and private keys must remain un-prefixed.
2. **Explicit MaxDuration**: If a Serverless Function performs long-running queries or external API calls, explicitly configure `"maxDuration"` in `vercel.json` (within plan limits: Hobby up to 60s, Pro up to 300s).
3. **Use Immutable Caching for Static Assets**: Add long-term immutable caching headers to fingerprinted files (`/static/*`, `/_next/static/*`) and use `stale-while-revalidate` for dynamic pages.
4. **Prefer `--prebuilt` in CI**: Avoid rebuilding in Vercel's cloud if your CI already runs tests and builds. Prebuilding guarantees that the exact code tested in CI is deployed.

---

## Common Pitfalls

- **Exceeding Edge Runtime Memory or APIs**: The Edge Runtime uses V8 isolates, not Node.js. It does not support arbitrary native Node modules (`fs`, `child_process`). Use the standard Serverless Runtime for Node-specific dependencies.
- **Missing Deployment Protection Bypass**: If preview deployments are protected by Vercel Authentication, automated E2E tests (Playwright, Cypress) will fail with 401. Generate a bypass secret in project settings and pass `x-vercel-protection-bypass: <secret>` in request headers.
- **Uncommitted `.vercel` Folder**: Never commit `.vercel/project.json` or credentials to public source control.

---

## Verification & Troubleshooting

Execute these commands to verify configuration and deployment status:

```bash
# Check current project link status
vercel project ls

# Tail live deployment execution logs
vercel logs <deployment-url-or-id> --follow

# Inspect domain routing and SSL status
vercel domains inspect <your-domain.com>

# Inspect response headers with curl
curl -I https://<your-project>.vercel.app
# Verify presence of 'x-vercel-id', 'x-vercel-cache', and security headers
```
