# Vercel Configuration & Routing Patterns

Comprehensive production templates and pattern library for `vercel.json` and associated Vercel deployment configurations.

## 1. Single Page Application (SPA) with Client-Side Routing

For React/Vite, Vue, or Svelte single-page applications where non-asset routes should fall back to `index.html`:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "cleanUrls": true,
  "rewrites": [
    {
      "source": "/((?!assets/|favicon.ico|robots.txt).*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    },
    {
      "source": "/index.html",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=0, must-revalidate"
        }
      ]
    }
  ]
}
```

---

## 2. API Gateway & Reverse Proxy Configuration

Forward specific paths to internal or external microservices while keeping client cookies and headers intact:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "rewrites": [
    {
      "source": "/api/v1/auth/:path*",
      "destination": "https://auth-service.example.internal/:path*"
    },
    {
      "source": "/api/v1/payments/:path*",
      "destination": "https://payments.example.internal/api/:path*"
    }
  ],
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Access-Control-Allow-Credentials", "value": "true" },
        { "key": "Access-Control-Allow-Origin", "value": "https://app.example.com" },
        { "key": "Access-Control-Allow-Methods", "value": "GET,OPTIONS,PATCH,DELETE,POST,PUT" },
        { "key": "Access-Control-Allow-Headers", "value": "X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization" }
      ]
    }
  ]
}
```

---

## 3. Serverless Function Resource Tuning

Allocate specific memory sizes (from 128 MB up to 3008 MB) and execution timeouts to heavy workers while keeping lightweight endpoints small:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "functions": {
    "api/reports/*.ts": {
      "memory": 2048,
      "maxDuration": 60
    },
    "api/webhooks/*.ts": {
      "memory": 512,
      "maxDuration": 10
    },
    "api/health.ts": {
      "memory": 128,
      "maxDuration": 5
    }
  }
}
```

---

## 4. Multi-Cron Scheduled Maintenance

Configure recurring scheduled tasks using standard POSIX cron syntax:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "crons": [
    {
      "path": "/api/cron/sync-exchange-rates",
      "schedule": "0 */4 * * *"
    },
    {
      "path": "/api/cron/prune-stale-sessions",
      "schedule": "30 3 * * *"
    },
    {
      "path": "/api/cron/weekly-digest",
      "schedule": "0 9 * * 1"
    }
  ]
}
```

---

## 5. Security Headers Preset

Standard high-security header baseline compatible with modern OWASP standards:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Content-Security-Policy",
          "value": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:; frame-ancestors 'none';"
        },
        {
          "key": "Strict-Transport-Security",
          "value": "max-age=63072000; includeSubDomains; preload"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        },
        {
          "key": "Permissions-Policy",
          "value": "camera=(), microphone=(), geolocation=(), payment=()"
        }
      ]
    }
  ]
}
```
