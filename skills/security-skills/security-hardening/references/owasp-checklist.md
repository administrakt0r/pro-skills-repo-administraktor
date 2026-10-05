# OWASP Top 10 Comprehensive Security Audit Checklist

This reference document provides a complete audit matrix and remediation guide structured around the OWASP Top 10 Web Application Security Risks. Each category includes vulnerability descriptions, an actionable audit checklist, vulnerable vs. secure implementation patterns, and testing commands.

---

## A01:2021 – Broken Access Control

### Description
Flaws permitting unauthorized information disclosure, data tampering, or unauthorized privilege elevation. This includes Insecure Direct Object References (IDOR), missing function level access control, bypassing CORS policies, and path traversal.

### Verification Checklist
- [ ] Every API endpoint enforces explicit authorization checks on the server side (never trust client-side role claims).
- [ ] Users can only access, modify, or delete records belonging to their tenant/account (IDOR protection).
- [ ] Sensitive directory browsing is disabled on the web server.
- [ ] CORS policies restrict allowed origins (`Access-Control-Allow-Origin: *` is prohibited on authenticated routes).
- [ ] File access parameters are sanitized against path traversal (`../`).

### Code Patterns

#### Vulnerable Pattern (IDOR & Path Traversal)
```javascript
// Express.js - VULNERABLE: Direct object reference without ownership check
app.get('/api/documents/:id', async (req, res) => {
  const doc = await db.documents.findById(req.params.id);
  res.json(doc); // Any authenticated user can read any document
});

// VULNERABLE: Path traversal
app.get('/api/view-file', (req, res) => {
  const filepath = path.join('/var/data', req.query.filename);
  res.sendFile(filepath); // Attacker passes "?filename=../../etc/passwd"
});
```

#### Secure Pattern (Ownership Verification & Path Confinement)
```javascript
// Express.js - SECURE: Scope query to authenticated user ID
app.get('/api/documents/:id', requireAuth, async (req, res) => {
  const doc = await db.documents.findOne({
    _id: req.params.id,
    userId: req.user.id // Enforce strict ownership / tenant boundary
  });
  if (!doc) return res.status(404).json({ error: 'Document not found' });
  res.json(doc);
});

// SECURE: Whitelist filename and verify path resolution
app.get('/api/view-file', requireAuth, (req, res) => {
  const safeFilename = path.basename(req.query.filename); // Strip directory segments
  const basePath = '/var/data/uploads';
  const resolvedPath = path.resolve(basePath, safeFilename);

  // Guard against symlink and escape attacks
  if (!resolvedPath.startsWith(basePath)) {
    return res.status(403).json({ error: 'Access denied' });
  }
  res.sendFile(resolvedPath);
});
```

### Audit Commands
```bash
# Test for horizontal privilege escalation / IDOR
curl -H "Authorization: Bearer <USER_A_TOKEN>" https://api.example.com/api/documents/<USER_B_DOC_ID>

# Test for path traversal
curl -s "https://api.example.com/api/view-file?filename=../../../../etc/passwd"
```

---

## A02:2021 – Cryptographic Failures

### Description
Failures in protecting data in transit or at rest. Includes using outdated algorithms (MD5, SHA1, DES, RC4), hardcoded keys, unencrypted transport, or weak pseudorandom number generators.

### Verification Checklist
- [ ] Enforce TLS 1.2+ with forward secrecy ciphers; disable SSLv3, TLS 1.0, and TLS 1.1.
- [ ] All passwords hashed using memory-hard algorithms (Argon2id, scrypt, or bcrypt with work factor $\ge 12$).
- [ ] Cryptographic secrets generated using cryptographically secure PRNG (`crypto.randomBytes`).
- [ ] Sensitive data at rest (tokens, PII, keys) encrypted with authenticated ciphers (e.g., AES-256-GCM).
- [ ] No hardcoded secrets, keys, or passwords committed to version control.

### Code Patterns

#### Vulnerable Pattern (Weak Hashing & Insecure PRNG)
```javascript
// VULNERABLE: MD5 / SHA-256 without salt and Math.random for security tokens
const crypto = require('crypto');
function hashPassword(pass) {
  return crypto.createHash('md5').update(pass).digest('hex');
}
const resetToken = Math.random().toString(36).substring(2);
```

#### Secure Pattern (Argon2id & Secure PRNG)
```javascript
const argon2 = require('argon2');
const crypto = require('crypto');

// SECURE: Memory-hard password hashing
async function hashPassword(plainPassword) {
  return await argon2.hash(plainPassword, {
    type: argon2.argon2id,
    memoryCost: 65536, // 64 MB
    timeCost: 3,
    parallelism: 1
  });
}

async function verifyPassword(hash, plainPassword) {
  return await argon2.verify(hash, plainPassword);
}

// SECURE: Cryptographically secure random token
function generateSecureToken(byteLength = 32) {
  return crypto.randomBytes(byteLength).toString('hex');
}
```

### Audit Commands
```bash
# Check TLS cipher suites and protocol versions
npx testssl.sh --protocols --ciphers https://example.com

# Scan codebase for hardcoded cryptographic keys and weak hashes
grep -rnE "(md5|sha1|des|rc4)" src/
```

---

## A03:2021 – Injection

### Description
Hostile data submitted by an attacker is parsed and executed by an interpreter (SQL, NoSQL, OS command, LDAP, XPath, or Server-Side Template Injection).

### Verification Checklist
- [ ] All database queries use parameterized queries / prepared statements or safe ORM accessors.
- [ ] No concatenation or string interpolation in raw database queries or commands.
- [ ] System commands never invoke shell execution (`exec`) with raw user input; use argument-array based spawn.
- [ ] Input schemas validate strict types, lengths, and regex boundaries before passing to drivers.

### Code Patterns

#### Vulnerable Pattern (SQL & Command Injection)
```javascript
// VULNERABLE: String concatenation in SQL
app.post('/api/users', async (req, res) => {
  const query = `SELECT * FROM users WHERE email = '${req.body.email}'`;
  const result = await db.query(query);
  res.json(result);
});

// VULNERABLE: Shell command execution with untrusted input
const { exec } = require('child_process');
exec(`ping -c 1 ${req.query.ip}`, (err, stdout) => { ... });
```

#### Secure Pattern (Parameterized SQL & Safe Process Spawning)
```javascript
// SECURE: Parameterized SQL Query (Postgres pg library)
app.post('/api/users', async (req, res) => {
  const query = 'SELECT id, email, role FROM users WHERE email = $1';
  const result = await db.query(query, [req.body.email]);
  res.json(result.rows);
});

// SECURE: Argument-array process execution with strict IP validation
const { execFile } = require('child_process');
const net = require('net');

if (!net.isIP(req.query.ip)) {
  return res.status(400).json({ error: 'Invalid IP address' });
}
execFile('ping', ['-c', '1', req.query.ip], (err, stdout) => { ... });
```

### Audit Commands
```bash
# Automated injection testing against test endpoints
sqlmap -u "https://example.com/api/search?q=test" --batch --random-agent --level=1
```

---

## A04:2021 – Insecure Design

### Description
Architectural and design flaws that cannot be fixed by implementation alone. Includes lack of threat modeling, failure to rate-limit business transactions, or missing defense-in-depth boundaries.

### Verification Checklist
- [ ] Threat modeling performed on sensitive business flows (payments, password resets, funds transfer).
- [ ] Rate limiting enforced per user ID, IP address, and tenant boundary.
- [ ] Graceful failure handling prevents exposing system state or sensitive operational details.
- [ ] Multi-step sensitive actions require re-authentication or one-time verification.

---

## A05:2021 – Security Misconfiguration

### Description
Missing appropriate security hardening, default configurations left in place, verbose error messages exposing stack traces, open cloud storage buckets, or missing HTTP security headers.

### Verification Checklist
- [ ] All default administrative accounts and passwords removed or disabled.
- [ ] Debug modes, developer diagnostics, and test endpoints disabled in production.
- [ ] Detailed stack traces suppressed from client HTTP responses (generic error messages returned).
- [ ] All essential HTTP security headers configured (HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy).
- [ ] Unused ports, frameworks, and web server modules uninstalled or disabled.

### Code Patterns

#### Error Handler Misconfiguration vs Remediation
```javascript
// VULNERABLE: Leaking stack trace to client
app.use((err, req, res, next) => {
  res.status(500).json({ error: err.message, stack: err.stack });
});

// SECURE: Log internally, respond with generic error
app.use((err, req, res, next) => {
  logger.error('Unhandled application exception', {
    message: err.message,
    stack: err.stack,
    url: req.originalUrl,
    requestId: req.headers['x-request-id']
  });
  res.status(500).json({
    error: 'An internal server error occurred. Please contact support.',
    code: 'INTERNAL_ERROR'
  });
});
```

### Audit Commands
```bash
# Check HTTP Security Headers
curl -sI https://example.com | grep -iE "strict-transport-security|content-security-policy|x-frame-options|x-content-type-options|referrer-policy|permissions-policy"
```

---

## A06:2021 – Vulnerable and Outdated Components

### Description
Using client-side or server-side libraries, frameworks, dependencies, or base container images with known CVE vulnerabilities.

### Verification Checklist
- [ ] Software composition analysis (SCA) integrated into local workflows and CI/CD pipelines.
- [ ] Exact dependency lockfiles (`package-lock.json`, `pnpm-lock.yaml`, `Pipfile.lock`, `Cargo.lock`) tracked in version control.
- [ ] Automated vulnerability scanning runs on every pull request.
- [ ] Continuous alerting configured for newly disclosed CVEs on existing dependencies.

### Audit Commands
```bash
# Node.js
npm audit --audit-level=high

# Trivy (filesystem & lockfile scan)
trivy fs --severity HIGH,CRITICAL .

# Snyk (if installed)
snyk test
```

---

## A07:2021 – Identification and Authentication Failures

### Description
Vulnerabilities allowing attackers to compromise passwords, keys, or session tokens to assume other users' identities.

### Verification Checklist
- [ ] Multi-Factor Authentication (MFA / TOTP) available and enforced for administrative access.
- [ ] Defense against brute-force attacks: account lockouts, progressive delays, or IP-based rate limiting.
- [ ] Passwords checked against known breached password lists (e.g., HaveIBeenPwned).
- [ ] Session tokens generated with cryptographic randomness ($\ge 128$ bits).
- [ ] Session tokens rotated upon login and privilege elevation; destroyed upon logout.
- [ ] Session cookies set with `HttpOnly`, `Secure`, and `SameSite=Lax` or `Strict`.

### Code Patterns

#### Secure Cookie Configuration
```javascript
app.use(session({
  name: '__Host-session', // Prefixed for extra browser security guarantees
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,     // Prevents client JavaScript access (mitigates XSS token theft)
    secure: true,       // Only transmitted over HTTPS
    sameSite: 'lax',    // Mitigates CSRF
    maxAge: 1000 * 60 * 60 * 8, // 8 hours
    path: '/'
  }
}));
```

---

## A08:2021 – Software and Data Integrity Failures

### Description
Code and infrastructure that do not protect against integrity violations. Includes unverified software updates, loading untrusted scripts without Subresource Integrity (SRI), and insecure deserialization.

### Verification Checklist
- [ ] Subresource Integrity (SRI) hashes applied to all third-party CDN scripts and stylesheets.
- [ ] Insecure object deserialization functions (`node-serialize`, Python `pickle`, Java `ObjectInputStream`) avoided when handling untrusted data.
- [ ] CI/CD pipelines enforce cryptographic signing or verified commit integrity.

### Code Patterns

#### Subresource Integrity (SRI) Example
```html
<!-- SECURE: SRI hash verifies the external asset was not tampered with -->
<script
  src="https://cdn.example.com/ajax/libs/purify/3.0.6/purify.min.js"
  integrity="sha384-NhpjU3h1H8hX9M9GZ2vY4R+TjV0nI4Lq7+Z4+L+BwXn2"
  crossorigin="anonymous"
></script>
```

---

## A09:2021 – Security Logging and Monitoring Failures

### Description
Insufficient logging of security events (authentication failures, access denials, critical input validation exceptions) and lack of active real-time monitoring/alerting.

### Verification Checklist
- [ ] All login successes, login failures, password changes, and permission modifications logged.
- [ ] High-volume input validation failures or unauthorized access attempts logged with IP and user identity.
- [ ] Log messages NEVER contain raw passwords, credit card numbers, session tokens, or unredacted PII.
- [ ] Log data formatted as structured JSON for automated SIEM ingestion and alerting.
- [ ] Log files protected against unauthorized tampering or truncation.

### Code Patterns

#### Sanitized Structured Security Logger
```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [new winston.transports.Console()]
});

function logSecurityEvent(eventType, metadata) {
  // Redact sensitive keys
  const sanitized = { ...metadata };
  ['password', 'token', 'secret', 'creditCard'].forEach((key) => {
    if (sanitized[key]) sanitized[key] = '[REDACTED]';
  });

  logger.warn({
    timestamp: new Date().toISOString(),
    category: 'SECURITY_AUDIT',
    event: eventType,
    ...sanitized
  });
}
```

---

## A10:2021 – Server-Side Request Forgery (SSRF)

### Description
Vulnerabilities occurring when a web application fetches a remote resource without validating the user-supplied URL. Attackers use SSRF to pivot into internal networks, query local services (`localhost:6379`), or access cloud instance metadata services (`http://169.254.169.254/`).

### Verification Checklist
- [ ] User-supplied URLs validated against a strict protocol allowlist (`https:` only).
- [ ] URL host resolved via DNS and checked against private/reserved IP ranges before request execution:
  - Loopback (`127.0.0.0/8`, `::1`)
  - RFC 1918 private spaces (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`)
  - Link-local and cloud metadata (`169.254.169.254`, `169.254.0.0/16`, `fe80::/10`)
- [ ] HTTP redirects disabled or re-validated at each redirect hop.
- [ ] Application server isolated in network segment without direct route to internal management interfaces.

### Code Patterns

#### SSRF Defense Implementation
```javascript
const dns = require('dns').promises;
const ipRangeCheck = require('ip-range-check');

const BLOCKED_RANGES = [
  '127.0.0.0/8',
  '10.0.0.0/8',
  '172.16.0.0/12',
  '192.168.0.0/16',
  '169.254.0.0/16', // AWS / GCP / Azure metadata endpoint
  '::1/128',
  'fc00::/7',
  'fe80::/10'
];

async function validateSafeUrl(rawUrl) {
  const parsed = new URL(rawUrl);

  // 1. Strict protocol validation
  if (parsed.protocol !== 'https:') {
    throw new Error('Only HTTPS protocol is permitted');
  }

  // 2. Resolve DNS to get actual IP addresses
  const addresses = await dns.lookup(parsed.hostname, { all: true });

  for (const { address } of addresses) {
    // 3. Block private or link-local destinations
    if (ipRangeCheck(address, BLOCKED_RANGES)) {
      throw new Error(`Forbidden destination IP: ${address}`);
    }
  }

  return parsed.toString();
}
```

### Audit Commands
```bash
# Attempt cloud metadata fetch via SSRF candidate endpoint
curl -X POST https://example.com/api/fetch-preview \
  -H "Content-Type: application/json" \
  -d '{"url":"http://169.254.169.254/latest/meta-data/"}'
```
