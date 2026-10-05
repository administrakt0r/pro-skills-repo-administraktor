---
name: security-hardening
description: >-
  Audits, hardens, and remediates security vulnerabilities across web applications,
  APIs, and server environments. Use when implementing OWASP Top 10 defenses,
  HTTP security headers (CSP, HSTS), input validation, parameterized queries,
  authentication and session security, secrets management, file upload safety,
  rate limiting, dependency auditing, or baseline Linux server hardening.
---

# Security Hardening

Security hardening is a defense-in-depth discipline designed to eliminate attack surfaces across code, network headers, authentication flows, data storage, and host infrastructure. This skill provides a pragmatic, actionable guide for defending against the OWASP Top 10 vulnerabilities, establishing zero-trust inputs, locking down HTTP headers, securing user sessions, and enforcing operating system baselines.

## When to Use

- Conducting a security audit or pre-production vulnerability assessment.
- Implementing defense against OWASP Top 10 risks (SQLi, XSS, CSRF, SSRF, IDOR).
- Configuring strict HTTP response headers (CSP, HSTS, Permissions-Policy).
- Designing authentication flows, password storage (Argon2id/bcrypt), MFA, and session lifecycles.
- Managing application secrets, environment configurations, and preventing git credential leaks.
- Securing file upload pipelines against malware and remote code execution.
- Implementing API rate limiting, abuse prevention, and brute-force defenses.
- Hardening Linux server hosts (SSH, UFW firewall, fail2ban).
- Setting up dependency vulnerability scanning and structured audit logging.

## Prerequisites

- Node.js ($\ge 18$), Python ($\ge 3.10$), or equivalent backend runtime.
- Package managers with vulnerability auditing support (`npm`, `pnpm`, `pip`, or `cargo`).
- Access to web server configurations (Nginx, Caddy, Apache, or framework middleware).
- Linux host access with `sudo` capabilities for infrastructure hardening.

---

## Steps

### 1. Audit Dependencies and Codebase Secrets

Scan third-party packages for known CVEs and verify that no credentials or private keys are committed.

```bash
# Audit package dependencies
npm audit --audit-level=high

# Detect hardcoded secrets and API keys using GitLeaks or TruffleHog
npx gitleaks detect --source . --verbose

# Verify .env and sensitive files are ignored by git
git check-ignore -v .env .env.local id_rsa
```

Ensure `.gitignore` contains:
```gitignore
.env
.env.*
!.env.example
*.pem
*.key
id_rsa
node_modules/
```

---

### 2. Configure Strict HTTP Security Headers & Content Security Policy (CSP)

HTTP headers instruct modern browsers to enforce sandbox boundaries and suppress attacks.

#### Express.js Implementation (using `helmet`):
```javascript
import helmet from 'helmet';
import crypto from 'crypto';

// Generate a per-request cryptographically secure nonce for inline scripts
app.use((req, res, next) => {
  res.locals.cspNonce = crypto.randomBytes(16).toString('base64');
  next();
});

app.use((req, res, next) => {
  helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'", `'nonce-${res.locals.cspNonce}'`],
        styleSrc: ["'self'", "'unsafe-inline'"], // unsafe-inline only if required; prefer nonces
        imgSrc: ["'self'", 'data:', 'https://images.example.com'],
        connectSrc: ["'self'", 'https://api.example.com'],
        fontSrc: ["'self'"],
        objectSrc: ["'none'"],
        baseUri: ["'self'"],
        formAction: ["'self'"],
        frameAncestors: ["'none'"], // Replaces X-Frame-Options: DENY
        upgradeInsecureRequests: []
      }
    },
    hsts: {
      maxAge: 31536000, // 1 year
      includeSubDomains: true,
      preload: true
    },
    referrerPolicy: { policy: 'strict-origin-when-cross-origin' },
    xContentTypeOptions: true, // nosniff
    xFrameOptions: { action: 'deny' }
  })(req, res, next);
});
```

#### Nginx Header Configuration:
```nginx
# HTTP Strict Transport Security (HSTS)
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

# Prevent MIME-type sniffing
add_header X-Content-Type-Options "nosniff" always;

# Clickjacking defense
add_header X-Frame-Options "DENY" always;

# Referrer information protection
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# Hardware feature restriction
add_header Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=()" always;

# Content Security Policy (Adjust domains to match environment)
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; object-src 'none'; frame-ancestors 'none'; upgrade-insecure-requests;" always;
```

---

### 3. Eliminate Injection: Parameterized Queries & Safe Execution

Never concatenate or interpolate untrusted strings into query strings or shell commands.

#### SQL Parameterization (PostgreSQL / SQLite / MySQL):
```javascript
// Parameterized query: User inputs are transmitted out-of-band as parameters
const query = `
  SELECT id, email, created_at
  FROM accounts
  WHERE email = $1 AND status = $2
`;
const result = await db.query(query, [sanitizedEmail, 'active']);
```

#### OS Command Execution Safety:
```javascript
// NEVER use child_process.exec(userInput)
// INSTEAD use execFile or spawn with argument arrays
import { execFile } from 'child_process';
import validator from 'validator';

if (!validator.isAlphanumeric(userSpecifiedFilename)) {
  throw new Error('Invalid filename format');
}

execFile('convert', ['-resize', '800x600', userSpecifiedFilename, 'output.jpg'], (err) => {
  if (err) console.error(err);
});
```

---

### 4. Mitigate Cross-Site Scripting (XSS)

XSS occurs when malicious scripts are rendered in a browser without sanitization.

1. **Contextual Escaping**: Frameworks like React, Vue, and Svelte escape strings bound in templates by default (`{userInput}`). Avoid `dangerouslySetInnerHTML`, `v-html`, and manual `element.innerHTML = ...`.
2. **HTML Sanitization**: When rendering user-submitted rich text (e.g. Markdown or HTML editors), sanitize using `DOMPurify`:

```javascript
import DOMPurify from 'dompurify';
import { JSDOM } from 'jsdom';

// Server-side sanitization
const window = new JSDOM('').window;
const purify = DOMPurify(window);

function sanitizeUserHtml(rawUntrustedHtml) {
  return purify.sanitize(rawUntrustedHtml, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'ul', 'ol', 'li', 'code', 'pre'],
    ALLOWED_ATTR: ['href', 'target', 'rel'],
    ALLOW_DATA_ATTR: false
  });
}
```

---

### 5. Secure Authentication, Passwords, and Sessions

Protect user identity storage and lifecycle.

#### Password Hashing with Argon2id:
```javascript
import argon2 from 'argon2';

export async function hashPassword(plainPassword) {
  return await argon2.hash(plainPassword, {
    type: argon2.argon2id,
    memoryCost: 65536, // 64 MB
    timeCost: 3,       // 3 iterations
    parallelism: 1
  });
}

export async function verifyPassword(storedHash, candidatePassword) {
  return await argon2.verify(storedHash, candidatePassword);
}
```

#### Secure Session Cookie Settings:
```javascript
app.use(session({
  name: '__Host-session',
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,     // Block JavaScript document.cookie access
    secure: true,       // Enforce HTTPS-only transmission
    sameSite: 'lax',    // Mitigate cross-site CSRF
    maxAge: 1000 * 60 * 60 * 12, // 12 hours
    path: '/'
  }
}));

// Session rotation upon login to prevent session fixation:
app.post('/api/login', async (req, res) => {
  const user = await authenticateUser(req.body.email, req.body.password);
  req.session.regenerate((err) => {
    if (err) return res.status(500).json({ error: 'Session error' });
    req.session.userId = user.id;
    res.json({ status: 'authenticated' });
  });
});
```

---

### 6. Defend Against CSRF and Broken Access Control (IDOR)

Cross-Site Request Forgery exploits ambient browser authentication (cookies).

1. **SameSite Cookies**: Setting `SameSite=Lax` or `SameSite=Strict` stops third-party sites from sending session cookies with cross-site POST requests.
2. **Double Submit Cookie or Anti-CSRF Token** on state-changing requests:
   ```javascript
   import csrf from 'csurf';
   const csrfProtection = csrf({ cookie: { httpOnly: true, secure: true, sameSite: 'strict' } });
   app.post('/api/transfer-funds', csrfProtection, handleTransfer);
   ```
3. **IDOR Prevention (Broken Access Control)**: Always scope database operations by the verified `req.session.userId`, never by client-supplied route IDs alone:
   ```javascript
   // SECURE: Enforces tenant isolation
   const record = await db.invoices.findOne({
     where: { id: req.params.invoiceId, accountId: req.user.accountId }
   });
   if (!record) return res.status(404).json({ error: 'Resource not found' });
   ```

---

### 7. Secure File Uploads

File uploads are a common vector for remote code execution, server exhaustion, and malware distribution.

```javascript
import multer from 'multer';
import { fileTypeFromBuffer } from 'file-type';
import crypto from 'crypto';
import path from 'path';

const ALLOWED_MIME_TYPES = new Set(['image/jpeg', 'image/png', 'image/webp', 'application/pdf']);
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: MAX_FILE_SIZE }
});

app.post('/api/upload', upload.single('document'), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'No file uploaded' });

  // 1. Verify actual binary magic bytes (do not trust user extension or req.file.mimetype)
  const detectedType = await fileTypeFromBuffer(req.file.buffer);
  if (!detectedType || !ALLOWED_MIME_TYPES.has(detectedType.mime)) {
    return res.status(400).json({ error: 'Invalid or prohibited file type' });
  }

  // 2. Generate randomized non-guessable filename
  const safeFilename = `${crypto.randomUUID()}.${detectedType.ext}`;

  // 3. Store outside public webroot or stream to S3 bucket with private ACL
  await saveToPrivateStorage(safeFilename, req.file.buffer);

  res.json({ fileId: safeFilename });
});
```

---

### 8. Implement Rate Limiting and Brute-Force Protection

Limit request frequency to throttle credential-stuffing, scraping, and DoS attacks.

```javascript
import rateLimit from 'express-rate-limit';

// Strict limiter for sensitive authentication endpoints
export const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5,                   // 5 attempts per IP per window
  standardHeaders: true,    // Return standard RateLimit-* headers
  legacyHeaders: false,
  message: { error: 'Too many authentication attempts. Please try again in 15 minutes.' }
});

// General API limiter
export const apiLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minute
  max: 120,                // 120 requests per minute
  standardHeaders: true,
  legacyHeaders: false
});

app.use('/api/auth/login', authLimiter);
app.use('/api/', apiLimiter);
```

---

### 9. Prevent Server-Side Request Forgery (SSRF)

When the server must fetch remote URLs (webhooks, avatar imports, link previews), enforce strict IP destination checks:

```javascript
import dns from 'dns/promises';
import ipRangeCheck from 'ip-range-check';

const RESTRICTED_IP_RANGES = [
  '127.0.0.0/8',    // Loopback
  '10.0.0.0/8',     // RFC 1918 Private
  '172.16.0.0/12',  // RFC 1918 Private
  '192.168.0.0/16', // RFC 1918 Private
  '169.254.0.0/16', // Link-local / Cloud Metadata (AWS, GCP, Azure)
  '::1/128',
  'fc00::/7',
  'fe80::/10'
];

export async function assertSafeUrl(inputUrl) {
  const url = new URL(inputUrl);

  if (url.protocol !== 'https:') {
    throw new Error('Only HTTPS protocol is allowed');
  }

  // Resolve hostname to IP to prevent DNS rebinding
  const lookup = await dns.lookup(url.hostname, { all: true });
  for (const { address } of lookup) {
    if (ipRangeCheck(address, RESTRICTED_IP_RANGES)) {
      throw new Error(`Target address ${address} is prohibited`);
    }
  }

  return url.toString();
}
```

---

### 10. Server and Host Hardening Basics

Harden the Linux host hosting application containers or services.

```bash
# 1. Configure UFW Firewall: Deny all incoming, allow only SSH and Web
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw enable

# 2. Harden SSH (/etc/ssh/sshd_config)
# Ensure the following directives are set:
# PermitRootLogin no
# PasswordAuthentication no
# PubkeyAuthentication yes
# X11Forwarding no
# MaxAuthTries 3
sudo sshd -t && sudo systemctl restart ssh

# 3. Install and configure fail2ban
sudo apt-get install -y fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable --now fail2ban
```

---

### 11. Structured Security Logging and Monitoring

Log security events without recording passwords, tokens, or personal identifiers.

```javascript
import winston from 'winston';

const auditLogger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  defaultMeta: { service: 'auth-service' },
  transports: [
    new winston.transports.File({ filename: 'security-audit.log' })
  ]
});

export function recordSecurityEvent(action, { userId, ip, status, reason }) {
  auditLogger.warn({
    timestamp: new Date().toISOString(),
    event_type: 'SECURITY_AUDIT',
    action,
    userId: userId || 'anonymous',
    ip,
    status, // 'SUCCESS' | 'FAILURE'
    reason: reason || null
  });
}
```

For the comprehensive OWASP Top 10 verification checklist covering all 10 categories (A01 through A10), refer to [OWASP Top 10 Audit Checklist](references/owasp-checklist.md).

---

## Best Practices

- **Validate on input, encode on output**: Use strict schema validation (e.g., Zod, Joi) on all inbound request bodies; encode dynamically generated output based on rendering context (HTML, JS, URL).
- **Enforce Principle of Least Privilege**: Application database connections should use an account with only `SELECT`, `INSERT`, `UPDATE`, `DELETE` permissions on specific tables (no `DROP`, `ALTER`, or `GRANT`).
- **Fail securely**: In error conditions, catch exceptions and return neutral, standardized error messages without leaking stack traces or database driver details.
- **Rotate secrets regularly**: Implement automated rotation for API tokens, database passwords, and encryption keys.
- **Automate dependency updates**: Configure automated security PRs via Dependabot, Renovate, or Snyk to remediate CVEs immediately upon disclosure.

## Common Pitfalls

- **Relying solely on frontend validation**: Client-side validation is a UX feature, not a security boundary; any client can bypass it using `curl` or Postman.
- **Using `md5`, `sha1`, or plain `sha256` for passwords**: Modern GPUs compute billions of SHA-256 hashes per second. Always use memory-hard algorithms like Argon2id.
- **Trusting `req.file.mimetype` or file extensions**: Attackers rename `.php` or executable files to `.png` while retaining malicious payloads. Always verify magic bytes using a binary parser.
- **Exposing internal services to SSRF via URL query params**: Allowing arbitrary fetching of web resources without private IP range blocking allows attackers to extract cloud instance credentials via metadata APIs.
- **Storing sensitive secrets in `.git` history**: Simply deleting a file in a new commit does not remove it from Git history. Use automated secret scanners.

---

## Verification

Run verification checks to confirm defenses are active:

```bash
# 1. Verify HTTP security headers on live host
curl -sI https://example.com | grep -iE "(strict-transport-security|content-security-policy|x-content-type-options|x-frame-options|referrer-policy|permissions-policy)"

# 2. Verify TLS certificate and configuration
openssl s_client -connect example.com:443 -tls1_3 < /dev/null

# 3. Test rate limiting enforcement (5 quick requests to login endpoint)
for i in {1..6}; do curl -s -o /dev/null -w "%{http_code}\n" -X POST https://example.com/api/auth/login; done
# The 6th request should return HTTP 429 Too Many Requests

# 4. Verify dependency vulnerability status
npm audit --omit=dev

# 5. Check firewall status on server
sudo ufw status verbose
```
