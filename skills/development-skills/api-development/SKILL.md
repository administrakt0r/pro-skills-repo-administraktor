---
name: api-development
description: >-
  Design, build, secure, document, and maintain robust RESTful and GraphQL APIs.
  Use when architecting API resource endpoints, implementing authentication and
  authorization (JWT, OAuth 2.0, API keys, RBAC/ABAC), handling pagination, filtering,
  and caching, standardizing error formats (RFC 7807), enforcing rate limits,
  authoring OpenAPI/Swagger specs, designing webhooks, or configuring CORS and security headers.
---

# API Development

API development defines the contracts, data exchange patterns, security controls, and transport protocols that enable distributed software systems to communicate reliably. Modern API engineering balances consumer ergonomics with system performance, operational resilience, and backward compatibility across RESTful and GraphQL architectures.

---

## When to Use

- Designing greenfield RESTful services, GraphQL schemas, or microservice gateways.
- Establishing authentication mechanisms (JWT with refresh rotation, OAuth 2.0 PKCE, API keys, session tokens) and granular authorization (RBAC, ABAC, OAuth scopes).
- Implementing data querying patterns: cursor-based and keyset pagination, multi-field filtering, sorting, and full-text search.
- Standardizing error responses using the RFC 7807 (Problem Details for HTTP APIs) specification.
- Hardening APIs with rate limiting (token bucket, sliding window), CORS policies, input validation, and sanitization.
- Designing HTTP caching architectures using `Cache-Control`, ETags, and conditional requests (`If-None-Match`, `If-Match`).
- Structuring API versioning (URI path, request header, media type) and managing sunset/deprecation cycles.
- Authoring OpenAPI 3.1 / Swagger specifications and generating interactive documentation.
- Building resilient webhook dispatch pipelines with HMAC-SHA256 signatures, exponential backoff, and idempotent delivery.

---

## Prerequisites

- Runtime environment: Node.js (Active LTS), Python (3.11+), Go (1.22+), or equivalent backend runtime.
- In-memory data store for stateful operations: Redis (v7+) or Valkey for distributed rate limiting, token revocation, and caching.
- HTTP testing and inspection tools: `curl`, `httpie`, or API client suites.
- Schema validation tooling: TypeScript/Zod, Python/Pydantic, or JSON Schema CLI validators.
- API linter: Spectral (`@stoplight/spectral-cli`) for OpenAPI style and contract linting.

---

## Steps

### Step 1: Architect RESTful Resource Modeling and URI Taxonomy

Follow resource-oriented architecture principles. Model resources as nouns rather than actions.

#### 1. URI Naming Rules
- Use plural lowercase nouns for collections: `/api/v1/users`, `/api/v1/orders`.
- Use kebab-case for multi-word segments: `/api/v1/order-items`, `/api/v1/payment-methods`.
- Express parent-child relationships through sub-resources (limit nesting to maximum 2 levels):
  - Valid: `/api/v1/teams/{teamId}/members`
  - Valid: `/api/v1/members/{memberId}/roles`
  - Anti-pattern: `/api/v1/organizations/{orgId}/teams/{teamId}/members/{memberId}/permissions` (flatten to `/api/v1/members/{memberId}/permissions`).
- Avoid verbs in URIs:
  - Anti-pattern: `POST /api/v1/createUser` -> `POST /api/v1/users`
  - Anti-pattern: `GET /api/v1/deleteUser?id=5` -> `DELETE /api/v1/users/5`
  - For non-CRUD business actions, represent them as sub-resource state transitions or RPC controller endpoints:
    - `POST /api/v1/orders/{orderId}/cancellation`
    - `POST /api/v1/invoices/{invoiceId}/reissue`

#### 2. HTTP Methods and Semantics Matrix
Map actions strictly to HTTP method semantics:

| Method | Safety | Idempotent | Success Status | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | Yes | Yes | `200 OK` | Retrieve resource representation |
| `POST` | No | No | `201 Created` / `202 Accepted` | Create a new subordinate resource or trigger an asynchronous job |
| `PUT` | No | Yes | `200 OK` / `204 No Content` | Completely replace an existing resource |
| `PATCH`| No | No (usually) | `200 OK` / `204 No Content` | Partially update resource attributes (JSON Merge Patch / RFC 6902) |
| `DELETE`| No | Yes | `200 OK` / `204 No Content` | Delete resource representation |
| `HEAD` | Yes | Yes | `200 OK` | Fetch HTTP headers identical to `GET` without body |
| `OPTIONS`| Yes | Yes | `204 No Content` | Discover allowed operations and CORS preflight |

#### 3. Standard HTTP Status Codes

| Code | Label | Usage Trigger |
| :--- | :--- | :--- |
| `200` | OK | Successful `GET`, `PUT`, `PATCH`, or `DELETE` with payload. |
| `201` | Created | Resource created via `POST`. Include `Location` header. |
| `202` | Accepted | Request accepted for asynchronous processing; background task queued. |
| `204` | No Content | Action succeeded; response contains no payload body (common in `DELETE`). |
| `304` | Not Modified | Conditional request validation (`ETag` matches `If-None-Match`). Client uses cache. |
| `400` | Bad Request | Syntactically malformed request, missing required headers or invalid JSON. |
| `401` | Unauthorized | Missing, expired, or invalid authentication credentials (`WWW-Authenticate`). |
| `403` | Forbidden | Authenticated client lacks authorization/permissions to access resource. |
| `404` | Not Found | Requested URI does not correspond to an existing resource. |
| `409` | Conflict | Request conflicts with current server state (e.g., duplicate unique email, version drift). |
| `412` | Precondition Failed | Conditional update failed (e.g., `If-Match` ETag mismatch in optimistic locking). |
| `415` | Unsupported Media Type | Request payload `Content-Type` not supported by the server. |
| `422` | Unprocessable Entity | Request syntax is valid, but semantic/domain validation failed (e.g., field-level errors). |
| `429` | Too Many Requests | Rate limit exceeded. Include `Retry-After` header. |
| `500` | Internal Server Error | Uncaught server exception; internal failure. |
| `502` | Bad Gateway | Upstream proxy or microservice returned an invalid response. |
| `503` | Service Unavailable | Service overloaded or undergoing maintenance. |
| `504` | Gateway Timeout | Upstream service failed to respond within configured timeout. |

---

### Step 2: Establish Consistent Request/Response Formats and Content Negotiation

Deliver consistent envelope structures across all REST endpoints.

#### 1. Content Negotiation
Clients and servers negotiate data formats via headers:
- `Content-Type`: Format of the payload body (e.g., `application/json; charset=utf-8`).
- `Accept`: Accepted response formats (e.g., `application/json`, `application/problem+json`).

Enforce validation middleware:
```typescript
import { Request, Response, NextFunction } from 'express';

export function enforceJsonContentType(req: Request, res: Response, next: NextFunction): void {
  if (['POST', 'PUT', 'PATCH'].includes(req.method)) {
    const contentType = req.headers['content-type'];
    if (!contentType || !contentType.includes('application/json')) {
      res.status(415).json({
        type: 'https://api.example.com/errors/unsupported-media-type',
        title: 'Unsupported Media Type',
        status: 415,
        detail: "Requests with bodies must declare Content-Type: application/json",
      });
      return;
    }
  }
  next();
}
```

#### 2. Standard Success Response Envelope
```json
{
  "data": {
    "id": "usr_01HZX87K4N",
    "email": "user@example.com",
    "displayName": "Alex Chen",
    "status": "active",
    "createdAt": "2026-10-01T12:00:00.000Z",
    "updatedAt": "2026-10-05T14:30:00.000Z"
  },
  "meta": {
    "requestId": "req_8f17a86e-92e1-4bb2-b5e0-47b14d3f572a",
    "timestamp": "2026-10-06T00:00:00.000Z"
  }
}
```

---

### Step 3: Implement Authentication and Authorization Architecture

Enforce defense-in-depth authentication and granular authorization.

#### 1. Authentication Mechanisms
- **JWT (JSON Web Tokens)**: Stateless access tokens signed with asymmetric keys (RS256 or Ed25519) with short TTL (e.g., 15 minutes). Paired with stateful or rotating refresh tokens (TTL 7–30 days) stored securely.
- **API Keys**: High-entropy strings (e.g., `sk_live_...`) passed in `Authorization: Bearer <key>` or `X-API-Key` for machine-to-machine integrations. Store hashed using SHA-256 in the database.
- **Session Tokens**: Opaque random tokens stored server-side (in Redis) with strict HTTP-only, Secure, SameSite cookies for first-party web apps.
- **OAuth 2.0 / OIDC**: Industry standard for third-party authorization delegation.

#### 2. Authorization Frameworks
- **RBAC (Role-Based Access Control)**: Evaluate static roles (`admin`, `editor`, `viewer`).
- **ABAC (Attribute-Based Access Control)**: Evaluate attributes of the user, resource, action, and environment:
  `allow if user.id == resource.ownerId OR user.role == 'admin'`
- **OAuth Scopes**: Capability strings (`read:orders`, `write:invoices`) limiting client delegation.

#### 3. Authorization Middleware Example
```typescript
import { Request, Response, NextFunction } from 'express';

export interface AuthenticatedUser {
  id: string;
  role: 'admin' | 'member' | 'guest';
  permissions: string[];
}

declare global {
  namespace Express {
    interface Request {
      user?: AuthenticatedUser;
    }
  }
}

export function requirePermissions(...requiredPermissions: string[]) {
  return (req: Request, res: Response, next: NextFunction): void => {
    const user = req.user;
    if (!user) {
      res.status(401).json({
        type: 'https://api.example.com/errors/unauthorized',
        title: 'Unauthorized',
        status: 401,
        detail: 'Authentication required to access this resource.',
      });
      return;
    }

    const hasPermission = requiredPermissions.every((perm) =>
      user.permissions.includes(perm) || user.role === 'admin'
    );

    if (!hasPermission) {
      res.status(403).json({
        type: 'https://api.example.com/errors/forbidden',
        title: 'Forbidden',
        status: 403,
        detail: 'Insufficient permissions to perform this operation.',
      });
      return;
    }

    next();
  };
}
```

---

### Step 4: Implement High-Performance Pagination, Filtering, and Sorting

Provide scalable querying primitives across data collections.

#### 1. Pagination Strategies

| Strategy | Query Parameters | Performance | Pros | Cons |
| :--- | :--- | :--- | :--- | :--- |
| **Offset-based** | `?page=3&limit=20` or `?offset=40&limit=20` | Degrades at large offsets ($O(N)$ scanning) | Easy to implement; supports jumping to arbitrary page numbers | Inefficient for large datasets; unstable when rows are inserted/deleted |
| **Keyset pagination** | `?limit=20&created_before=2026-10-05T10:00:00Z&id_before=100` | High ($O(\log N)$ with B-tree index) | Constant performance; stable against concurrent writes | Requires strict monotonic/indexed sort keys; cannot jump to page $N$ |
| **Cursor-based** | `?limit=20&cursor=ZXlKMGVYQWlPaU...` | High ($O(\log N)$ indexed seek) | Encapsulates keyset details into opaque token; prevents client tampering | Cursor serialization required; no arbitrary page jumps |

#### Cursor-Based Response Standard
```json
{
  "data": [
    { "id": "evt_01HZX87K4N", "name": "Payment Completed" }
  ],
  "pagination": {
    "hasMore": true,
    "limit": 20,
    "nextCursor": "ZXlKMWMyVnlYMmxrSWpv..."
  }
}
```

#### 2. Filtering Conventions
- Direct equality: `GET /api/v1/orders?status=completed&currency=USD`
- Range and comparison operators (Bracket notation):
  - `GET /api/v1/products?price[gte]=100&price[lte]=500`
  - `GET /api/v1/users?created_at[gt]=2026-01-01T00:00:00Z`
- In-list queries: `GET /api/v1/orders?status[in]=shipped,delivered`

#### 3. Sorting Conventions
Use `sort` parameter with comma-separated fields. Prepend `-` for descending:
- Ascending: `GET /api/v1/products?sort=price`
- Descending: `GET /api/v1/products?sort=-created_at`
- Multi-field: `GET /api/v1/products?sort=-priority,name`

---

### Step 5: Implement Standardized Error Handling (RFC 7807 Problem Details)

Adopt the RFC 7807 / RFC 9457 specification (`application/problem+json`) for uniform machine-readable error responses.

#### 1. Standard Error Envelope
```json
{
  "type": "https://api.example.com/errors/validation-failed",
  "title": "Validation Failed",
  "status": 422,
  "detail": "The payload contained semantic validation errors on 2 fields.",
  "instance": "/api/v1/users",
  "invalidParams": [
    {
      "name": "email",
      "reason": "Must be a valid email format."
    },
    {
      "name": "password",
      "reason": "Must contain at least 12 characters including uppercase, lowercase, and special symbols."
    }
  ]
}
```

#### 2. Express Global Error Handler
```typescript
import { Request, Response, NextFunction } from 'express';

export interface AppError extends Error {
  status?: number;
  type?: string;
  invalidParams?: Array<{ name: string; reason: string }>;
}

export function globalErrorHandler(
  err: AppError,
  req: Request,
  res: Response,
  next: NextFunction
): void {
  const status = err.status || 500;
  const isProduction = process.env.NODE_ENV === 'production';

  const problemDetails = {
    type: err.type || (status === 500
      ? 'https://api.example.com/errors/internal-server-error'
      : 'https://api.example.com/errors/bad-request'),
    title: err.name || 'Internal Server Error',
    status,
    detail: status === 500 && isProduction
      ? 'An unexpected error occurred. Please contact support.'
      : err.message,
    instance: req.originalUrl,
    ...(err.invalidParams && { invalidParams: err.invalidParams }),
  };

  res.setHeader('Content-Type', 'application/problem+json');
  res.status(status).json(problemDetails);
}
```

---

### Step 6: Configure Rate Limiting and Traffic Throttling

Protect endpoints from abuse and brute-force attacks using Redis-backed rate limiting.

#### 1. Rate Limiting Algorithms
- **Token Bucket**: Accumulates tokens up to capacity; consumed on request. Smooths bursts.
- **Sliding Window Counter**: Tracks request timestamps in a rolling window; avoids fixed-window edge-case bursts (2x limit at window boundaries).

#### 2. Standard Rate Limiting Headers (IETF Draft)
Always return rate limit telemetry:
```http
RateLimit-Limit: 100
RateLimit-Remaining: 94
RateLimit-Reset: 1728172800
Retry-After: 60
```

#### 3. Sliding Window Rate Limiting Implementation
```typescript
import { Request, Response, NextFunction } from 'express';
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

export function createSlidingWindowLimiter(windowSecs: number, maxRequests: number) {
  return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    const key = `ratelimit:${req.ip}:${req.path}`;
    const now = Date.now();
    const clearBefore = now - windowSecs * 1000;

    const multi = redis.multi();
    multi.zremrangebyscore(key, 0, clearBefore);
    multi.zadd(key, now, `${now}-${Math.random()}`);
    multi.zcard(key);
    multi.expire(key, windowSecs);

    const results = await multi.exec();
    const count = (results?.[2]?.[1] as number) || 0;

    const remaining = Math.max(0, maxRequests - count);
    const resetTime = Math.ceil((now + windowSecs * 1000) / 1000);

    res.setHeader('RateLimit-Limit', maxRequests);
    res.setHeader('RateLimit-Remaining', remaining);
    res.setHeader('RateLimit-Reset', resetTime);

    if (count > maxRequests) {
      res.setHeader('Retry-After', windowSecs);
      res.status(429).json({
        type: 'https://api.example.com/errors/rate-limit-exceeded',
        title: 'Too Many Requests',
        status: 429,
        detail: `Exceeded quota of ${maxRequests} requests per ${windowSecs} seconds.`,
      });
      return;
    }

    next();
  };
}
```

---

### Step 7: Configure API Versioning and Deprecation

Plan for API evolution from day one without breaking existing clients.

#### 1. Versioning Approaches

| Strategy | Syntax | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **URI Path** (Recommended) | `/api/v1/orders` | Explicit, easy to test in browser and routing layers | Clutters URI space; promotes duplicate routing trees |
| **Custom Header** | `X-API-Version: 2026-10-01` | Clean URIs; flexible for fine-grained breaking changes | Cannot test directly in static HTML links; CDN cache key must include header |
| **Content Negotiation** | `Accept: application/vnd.company.v1+json` | Follows pure REST HATEOAS specifications | Complex client configuration; CDN caching headers must vary on `Accept` |

#### 2. Deprecation Protocol
When sunsetting an endpoint:
1. Announce migration period in release notes and developer portal.
2. Return standard HTTP headers:
   - `Deprecation: @1794355200` (Unix timestamp) or `true`
   - `Sunset: Sat, 01 Nov 2026 00:00:00 GMT` (RFC 8594)
   - `Link: <https://api.example.com/migration-v2>; rel="deprecation"`

---

### Step 8: Harden Security: CORS, Input Validation, and Sanitization

#### 1. CORS Configuration
Never use `Access-Control-Allow-Origin: *` in production for endpoints with credentials or authentication.

```typescript
import cors from 'cors';

const allowedOrigins = (process.env.CORS_ALLOWED_ORIGINS || '').split(',').map((o) => o.trim());

export const corsMiddleware = cors({
  origin: (origin, callback) => {
    // Allow non-browser requests (e.g. server-to-server curl, mobile apps)
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Blocked by CORS policy'));
    }
  },
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With', 'Idempotency-Key'],
  exposedHeaders: ['RateLimit-Limit', 'RateLimit-Remaining', 'RateLimit-Reset', 'ETag'],
  credentials: true,
  maxAge: 86400, // Preflight cache 24 hours
});
```

#### 2. Strict Input Validation (Zod Example)
Validate headers, query parameters, route params, and body before execution:

```typescript
import { z } from 'zod';
import { Request, Response, NextFunction } from 'express';

export const CreateUserSchema = z.object({
  body: z.object({
    email: z.string().email().max(255).trim().toLowerCase(),
    password: z.string().min(12).max(128),
    displayName: z.string().min(2).max(100).trim(),
  }),
});

export function validateSchema(schema: z.ZodSchema) {
  return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    const result = await schema.safeParseAsync({
      body: req.body,
      query: req.query,
      params: req.params,
    });

    if (!result.success) {
      const invalidParams = result.error.errors.map((err) => ({
        name: err.path.slice(1).join('.'),
        reason: err.message,
      }));

      res.status(422).json({
        type: 'https://api.example.com/errors/validation-failed',
        title: 'Validation Failed',
        status: 422,
        detail: 'The submitted request contained invalid fields.',
        invalidParams,
      });
      return;
    }

    req.body = (result.data as any).body;
    next();
  };
}
```

---

### Step 9: Implement HTTP Caching and Conditional Requests

Optimize network bandwidth and server latency using HTTP standard caching headers.

#### 1. Cache-Control Header Directives
- Sensitive or mutating endpoints: `Cache-Control: no-store`
- User-specific private data: `Cache-Control: private, no-cache`
- Public cacheable data with revalidation: `Cache-Control: public, max-age=3600, stale-while-revalidate=600`

#### 2. Conditional Requests via ETags
Generate a deterministic hash of the resource representation:

```typescript
import crypto from 'crypto';
import { Request, Response, NextFunction } from 'express';

export function handleResourceEtag(req: Request, res: Response, data: unknown): void {
  const content = JSON.stringify(data);
  const etag = `"${crypto.createHash('sha256').update(content).digest('hex')}"`;

  res.setHeader('ETag', etag);
  res.setHeader('Cache-Control', 'public, max-age=60, must-revalidate');

  // Conditional GET
  if (req.headers['if-none-match'] === etag) {
    res.status(304).end();
    return;
  }

  // Conditional PUT / PATCH (Optimistic Concurrency Control)
  const ifMatch = req.headers['if-match'];
  if (ifMatch && ifMatch !== etag) {
    res.status(412).json({
      type: 'https://api.example.com/errors/precondition-failed',
      title: 'Precondition Failed',
      status: 412,
      detail: 'Resource has been modified by another process since last read.',
    });
    return;
  }

  res.status(200).json(data);
}
```

---

### Step 10: Contract-First Design with OpenAPI 3.1 & Documentation

Define your API contract with OpenAPI 3.1 before writing implementation code.

#### Minimal OpenAPI 3.1 Spec Template (`openapi.yaml`):
```yaml
openapi: 3.1.0
info:
  title: Core Service API
  version: 1.0.0
  description: Universal production API contract
servers:
  - url: https://api.example.com/v1
    description: Production gateway
paths:
  /users:
    get:
      summary: List users
      operationId: listUsers
      parameters:
        - name: limit
          in: query
          required: false
          schema:
            type: integer
            default: 20
            maximum: 100
      responses:
        '200':
          description: Users retrieved successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserListResponse'
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  schemas:
    UserListResponse:
      type: object
      required:
        - data
      properties:
        data:
          type: array
          items:
            type: object
            required:
              - id
              - email
            properties:
              id:
                type: string
              email:
                type: string
                format: email
```

---

### Step 11: Architect GraphQL APIs (Schema, Resolvers, and DataLoader)

Use GraphQL when consumers require flexible, granular queries and aggregations across multiple domains.

#### 1. Schema Definition Language (SDL)
```graphql
type User {
  id: ID!
  email: String!
  displayName: String!
  posts(first: Int, after: String): PostConnection!
}

type Query {
  user(id: ID!): User
  me: User!
}

type Mutation {
  updateUser(input: UpdateUserInput!): UserPayload!
}

input UpdateUserInput {
  displayName: String
}

type UserPayload {
  user: User
  errors: [UserError!]!
}

type UserError {
  field: String!
  message: String!
}
```

#### 2. Resolving the N+1 Problem with DataLoader
Wrap database batch fetches in memoized DataLoaders to prevent $N+1$ queries:
```typescript
import DataLoader from 'dataloader';

export interface Author {
  id: string;
  name: string;
}

export function createAuthorLoader(fetchAuthorsBatch: (ids: readonly string[]) => Promise<Author[]>) {
  return new DataLoader<string, Author | null>(async (authorIds) => {
    const authors = await fetchAuthorsBatch(authorIds);
    const authorMap = new Map(authors.map((a) => [a.id, a]));
    return authorIds.map((id) => authorMap.get(id) || null);
  });
}
```

---

### Step 12: Design Resilient Webhook Infrastructure

Webhooks provide asynchronous event notifications pushed to consumer endpoints over HTTP POST.

#### 1. Webhook Payload Anatomy
```json
{
  "id": "evt_01HZX87K4N",
  "event": "invoice.paid",
  "apiVersion": "2026-10-01",
  "createdAt": "2026-10-06T00:00:00.000Z",
  "data": {
    "invoiceId": "inv_12345",
    "amountPaid": 4900,
    "currency": "USD",
    "customer": "cus_99887"
  }
}
```

#### 2. Webhook Signature Generation & Verification (HMAC-SHA256)
Dispatch payloads signed with a shared secret to prevent spoofing and replay attacks:
```typescript
import crypto from 'crypto';

export function signWebhookPayload(payload: string, secret: string, timestamp: number): string {
  const signaturePayload = `t=${timestamp},v1=${payload}`;
  const hmac = crypto.createHmac('sha256', secret).update(signaturePayload).digest('hex');
  return `t=${timestamp},v1=${hmac}`;
}

export function verifyWebhookSignature(
  rawBody: string,
  signatureHeader: string,
  secret: string,
  toleranceSecs = 300
): boolean {
  const parts = signatureHeader.split(',').reduce((acc, part) => {
    const [k, v] = part.split('=');
    acc[k] = v;
    return acc;
  }, {} as Record<string, string>);

  const timestamp = parseInt(parts.t, 10);
  const signature = parts.v1;

  if (isNaN(timestamp) || !signature) return false;

  // Protect against replay attacks
  const currentTime = Math.floor(Date.now() / 1000);
  if (Math.abs(currentTime - timestamp) > toleranceSecs) return false;

  const expectedPayload = `t=${timestamp},v1=${rawBody}`;
  const expectedSignature = crypto.createHmac('sha256', secret).update(expectedPayload).digest('hex');

  return crypto.timingSafeEqual(Buffer.from(signature, 'hex'), Buffer.from(expectedSignature, 'hex'));
}
```

---

### Step 13: Implement Hypermedia and HATEOAS Controls

When building APIs that drive UI workflows or dynamic state machines, embed hypermedia affordances (e.g., using HAL or JSON:API conventions):

```json
{
  "id": "ord_9901",
  "status": "pending_payment",
  "total": 150.00,
  "_links": {
    "self": { "href": "/api/v1/orders/ord_9901" },
    "payment": { "href": "/api/v1/orders/ord_9901/payments", "method": "POST" },
    "cancel": { "href": "/api/v1/orders/ord_9901/cancellation", "method": "POST" }
  }
}
```

---

## Best Practices

- **Validate at the Perimeter**: Intercept and validate all inbound data before it reaches business logic or database layers.
- **Fail Closed**: Return `401 Unauthorized` or `403 Forbidden` if permissions or scopes cannot be unequivocally verified.
- **Enforce Strict Content-Types**: Only accept `application/json` for mutation payloads; reject ambiguous or missing media types with `415`.
- **Implement Idempotency Keys**: Use `Idempotency-Key` headers for critical mutating operations (`POST /payments`) to safeguard against duplicate execution during network retries.
- **Adopt Constant-Time Comparisons**: Use `crypto.timingSafeEqual` when verifying API keys, webhook signatures, or authentication tokens to prevent timing side-channel attacks.
- **Never Leak Sensitive Data in Errors**: Omit stack traces, database schema details, and infrastructure IPs from error payloads in production environments.
- **Always Page Collections**: Never expose unpaginated collection endpoints; enforce maximum page limits (e.g., `maxLimit = 100`).

---

## Common Pitfalls

- **Verb-Heavy URIs**: Creating endpoints like `/api/getUser`, `/api/updateStatus` instead of `/api/users/{id}`, `PATCH /api/users/{id}`.
- **Status Code Misuse**: Returning `200 OK` with `{ "error": "User not found" }` in the response body.
- **Unbounded Offsets**: Using `OFFSET 1000000` in SQL queries, causing full index/table scans and server CPU spikes. Use keyset/cursor pagination instead.
- **Loose CORS Policies**: Configuring `Access-Control-Allow-Origin: *` while passing authorization headers or credentials.
- **N+1 Resolver Queries in GraphQL**: Failing to use DataLoader in GraphQL field resolvers, resulting in hundreds of parallel database queries for a single API call.
- **Missing Replay Attack Prevention on Webhooks**: Failing to verify timestamps alongside webhook HMAC signatures.
- **Silent Schema Drift**: Changing API fields without updating the OpenAPI specification or without deprecation notices.

---

## Verification

Perform these verification procedures to validate your API implementation:

### 1. Verify Status Codes and RFC 7807 Error Format
```bash
# Test 404 Not Found
curl -s -i http://localhost:8080/api/v1/nonexistent-resource | grep -E "HTTP/|Content-Type"
# Expected: HTTP/1.1 404 Not Found, Content-Type: application/problem+json

# Test 422 Validation Error
curl -s -i -X POST http://localhost:8080/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"email":"invalid-email"}' | grep -E "HTTP/|invalidParams"
# Expected: HTTP/1.1 422 Unprocessable Entity, invalidParams array present
```

### 2. Verify Rate Limiting Headers
```bash
curl -s -i http://localhost:8080/api/v1/users | grep -i "RateLimit"
# Expected headers:
# RateLimit-Limit: <number>
# RateLimit-Remaining: <number>
# RateLimit-Reset: <timestamp>
```

### 3. Verify Cache Control and Conditional ETag Requests
```bash
# Initial GET
ETAG=$(curl -s -i http://localhost:8080/api/v1/users/1 | grep -i "ETag:" | awk '{print $2}' | tr -d '\r')

# Conditional GET
curl -s -i -H "If-None-Match: $ETAG" http://localhost:8080/api/v1/users/1 | grep "HTTP/"
# Expected: HTTP/1.1 304 Not Modified
```

### 4. Verify OpenAPI Contract Compliance
```bash
npx @stoplight/spectral-cli lint openapi.yaml
# Expected: 0 errors, 0 warnings
```

---

## Detailed Reference Material

For end-to-end code implementations, OAuth 2.0 sequence diagrams, GraphQL schema designs, and production rate limiters, refer to:
- [`references/rest-graphql-patterns.md`](references/rest-graphql-patterns.md)
