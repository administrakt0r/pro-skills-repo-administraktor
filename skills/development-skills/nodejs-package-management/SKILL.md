---
name: nodejs-package-management
description: >-
  Manage Node.js package managers, dependencies, lockfiles, workspaces, scripts,
  and module ecosystems across npm, pnpm, yarn, and bun. Use when selecting or
  migrating package managers, diagnosing dependency conflicts or phantom dependencies,
  configuring monorepos and Turborepo, hardening package.json, resolving lockfile drift,
  auditing vulnerabilities, configuring ESM/CJS compatibility, or publishing packages.
---

# Node.js Package Management

Package management in the Node.js ecosystem governs dependency resolution, execution speed, reproducibility across continuous integration (CI) environments, and runtime module compatibility. Selecting the right package manager and applying strict configuration patterns prevents phantom dependencies, supply-chain vulnerabilities, lockfile synchronization failures, and dual-package hazards.

---

## When to Use

- Initializing a new Node.js or TypeScript project and selecting the appropriate package manager (`npm`, `pnpm`, `yarn`, or `bun`).
- Diagnosing and resolving dependency anomalies: phantom dependencies, hoisting collisions, version duplication, or broken peer dependencies.
- Migrating between package managers or structuring multi-package monorepos with native workspaces or Turborepo.
- Configuring reproducible, immutable CI/CD installation pipelines with lockfile verification.
- Establishing ECMAScript Modules (ESM) and CommonJS (CJS) interoperability, subpath exports maps, and TypeScript compilation targets.
- Hardening project security through vulnerability auditing, automated overrides/resolutions, and supply-chain controls.
- Preparing, packaging, and publishing packages to the public npm registry or private scoped registries with provenance.

---

## Prerequisites

- Node.js runtime installed (Active LTS or Maintenance LTS recommended).
- Corepack enabled (`corepack enable`) or native package managers installed globally.
- Shell access with Git installed for lockfile tracking and version control.

---

## Steps

### Step 1: Select the Optimal Package Manager

Evaluate project requirements, team workflow, and infrastructure before picking a package manager:

| Feature / Metric | `npm` (v10+) | `pnpm` (v9+) | `Yarn Berry` (v4+) | `Bun` (v1+) |
| :--- | :--- | :--- | :--- | :--- |
| **Default Architecture** | Flat / Hoisted `node_modules` | Content-addressable store + symlinks | Zero-installs / PnP or `node-modules` linker | Flat `node_modules` + binary cache |
| **Phantom Dep Protection** | ❌ No (hoisted globally) | ✅ Strict (only declared deps accessible) | ✅ Strict (with PnP linker) | ❌ No (hoisted) |
| **Disk Space Efficiency** | ❌ Duplicated across repos | ✅ High (global hard-link store) | ⚠️ Moderate (global cache or zip cache) | ⚠️ Moderate (global binary cache) |
| **CI Install Speed** | Moderate (`npm ci`) | Fast (`pnpm install --frozen-lockfile`) | Very fast (Zero-install or cache) | Fastest native installer |
| **Monorepo Workspaces** | Native basic workspaces | First-class workspace protocol (`workspace:*`) | First-class workspace protocol | Basic workspace support |
| **Runtime Integration** | Node.js standard default | Node.js ecosystem tool | Node.js ecosystem tool | All-in-one JS runtime, bundler, test runner |

#### Decision Rules:
1. **Choose `pnpm`** for most production applications, libraries, and monorepos. Its hard-linked, content-addressable store saves disk space and strictly prevents phantom dependencies.
2. **Choose `npm`** when minimizing external tooling is paramount, when working in constrained corporate environments that forbid alternate package managers, or for baseline tutorials.
3. **Choose `Yarn Berry (v4+)`** when utilizing Zero-Installs (committing `.yarn/cache` for offline builds) or when existing monorepo tooling is deeply tied to Yarn Plug'n'Play (PnP).
4. **Choose `Bun`** when execution speed of installation, scripts, and runtime is top priority and the project relies entirely on Node.js-compatible APIs without deep dependence on native node-gyp bindings unsupported by Bun.

---

### Step 2: Enforce Node.js Runtime and Package Manager Pinning

Prevent "works on my machine" discrepancies by pinning both the Node.js runtime and the exact package manager version.

#### 1. Pin the Node.js Runtime Version
Create an `.nvmrc` and `.node-version` file at the repository root:
```text
20.18.0
```
- **`nvm`**: Uses `.nvmrc` (`nvm use`).
- **`fnm` (Fast Node Manager)**: Evaluates `.node-version` and `.nvmrc` instantly via shell hooks; written in Rust for high performance.
- **`volta`**: Pins toolchains directly in `package.json`:
  ```json
  "volta": {
    "node": "20.18.0",
    "pnpm": "9.12.0"
  }
  ```

#### 2. Pin the Package Manager via Corepack
Add the `"packageManager"` field to `package.json` and enable Corepack:
```bash
corepack enable
corepack use pnpm@9.12.0
```
This writes the exact version and SHA hash to `package.json`:
```json
{
  "name": "app-template",
  "packageManager": "pnpm@9.12.0+sha512.a85f..."
}
```
Any developer running `pnpm` with Corepack enabled will automatically download and execute the exact specified version.

---

### Step 3: Architect `package.json` Anatomy and Metadata

Structure `package.json` into semantic categories to ensure correct build outputs and runtime boundaries:

```json
{
  "name": "@scope/example-package",
  "version": "1.2.0",
  "description": "Production Node.js service and utility",
  "type": "module",
  "main": "./dist/index.cjs",
  "module": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js",
      "require": "./dist/index.cjs",
      "default": "./dist/index.js"
    },
    "./package.json": "./package.json"
  },
  "files": [
    "dist",
    "README.md",
    "LICENSE"
  ],
  "engines": {
    "node": ">=20.0.0",
    "npm": ">=10.0.0"
  },
  "scripts": {
    "prepare": "husky || true",
    "prebuild": "rimraf dist",
    "build": "tsup",
    "lint": "eslint .",
    "test": "vitest run",
    "prepublishOnly": "npm run test && npm run build"
  },
  "dependencies": {
    "zod": "^3.23.8"
  },
  "devDependencies": {
    "@types/node": "^20.16.10",
    "rimraf": "^6.0.1",
    "tsup": "^8.3.0",
    "typescript": "^5.6.2",
    "vitest": "^2.1.2"
  },
  "peerDependencies": {
    "react": "^18.0.0 || ^19.0.0"
  },
  "peerDependenciesMeta": {
    "react": {
      "optional": true
    }
  }
}
```

#### Dependency Classification:
- **`dependencies`**: Packages required at runtime in production (e.g., ORM, validation library, HTTP framework).
- **`devDependencies`**: Packages needed only during local development and build phases (e.g., compilers, linters, test harnesses).
- **`peerDependencies`**: Packages the consuming application must provide. Essential for plugins, component libraries, and shared singletons.
- **`peerDependenciesMeta`**: Marks peer dependencies as `"optional": true` when functionality degrades gracefully without them.
- **`optionalDependencies`**: Packages that may fail installation without halting the overall install process (e.g., platform-specific native binaries).
- **`bundledDependencies`**: Array of package names bundled directly into the tarball when publishing.
- **`engines`**: Enforces runtime compatibility. Combine with `.npmrc` setting `engine-strict=true`.
- **`files`**: An explicit allowlist of files to include in published artifacts. Preferred over `.npmignore`.

---

### Step 4: Master Semantic Versioning (SemVer)

Node.js package managers adhere to Semantic Versioning (`MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]`):
- **MAJOR**: Incompatible API changes.
- **MINOR**: Backward-compatible new functionality.
- **PATCH**: Backward-compatible bug fixes.

#### 1. Range Operator Syntax
| Specifier | Syntax Example | Matches | Explanation |
| :--- | :--- | :--- | :--- |
| **Exact** | `1.2.3` | `1.2.3` only | Strict pinning. Zero drift. |
| **Patch / Tilde** | `~1.2.3` | `>=1.2.3 <1.3.0` | Updates patch releases only. |
| **Minor / Caret** | `^1.2.3` | `>=1.2.3 <2.0.0` | Updates minor and patch releases. |
| **Caret on Zero** | `^0.2.3`<br>`^0.0.3` | `>=0.2.3 <0.3.0`<br>`0.0.3` only | In `0.x.x`, minor bump is breaking. In `0.0.x`, patch bump is breaking. |
| **Comparative** | `>=18.0.0 <21.0.0` | `18.0.0` up to `20.x` | Bounded version range. |
| **Union (OR)** | `^18.0.0 \|\| ^19.0.0` | Any matching either range | Multi-major support for peer dependencies. |
| **Wildcard** | `*` or `x` | Any version | **Anti-pattern**: Highly unstable. Never use in production. |

#### 2. Safe Versioning Strategies
- **For Applications and Services**:
  - Prefer exact versions in `dependencies` (`save-exact=true` in `.npmrc`).
  - Rely on CI lockfile freezing to guarantee identical production deployments.
- **For Published Libraries**:
  - Use caret (`^`) ranges for `dependencies` to permit non-breaking upgrades in consumers.
  - Use broad range unions (`^18.0.0 || ^19.0.0`) for `peerDependencies` to avoid peer conflict errors in consumer projects.

---

### Step 5: Master Lockfiles and Deterministic CI Installations

Never run standard install commands (`npm install`, `pnpm install`, `yarn`) in CI/CD pipelines. Standard install commands update lockfiles and permit nondeterministic transitive updates.

#### 1. Immutable CI Commands
Always use the frozen/immutable flag for the detected package manager:

```bash
# npm: Deletes existing node_modules and strictly installs from package-lock.json
npm ci

# pnpm: Verifies pnpm-lock.yaml matches package.json and aborts if out of sync
pnpm install --frozen-lockfile

# Yarn (v2+): Fails if yarn.lock requires modifications
yarn install --immutable

# Bun: Enforces lockfile consistency
bun install --frozen-lockfile
```

#### 2. Resolving Lockfile Merge Conflicts
When git merge conflicts occur in lockfiles, never attempt manual text editing of multi-thousand-line diffs.
1. Check out the target branch version of the lockfile.
2. Regenerate the lockfile from the merged `package.json`:
```bash
# For npm
git checkout --theirs package-lock.json
npm install --package-lock-only

# For pnpm
git checkout --theirs pnpm-lock.yaml
pnpm install --lockfile-only

# For Yarn
git checkout --theirs yarn.lock
yarn install --mode update-lockfile
```

---

### Step 6: Eliminate Phantom Dependencies, Hoisting Conflicts, and Deduplication

#### 1. Understanding Phantom Dependencies
A **phantom dependency** occurs when code imports a package that exists inside `node_modules` (because another dependency pulled it in and it was hoisted to the top level) but is not declared in `package.json`. If the intermediate dependency updates and drops that package, the application breaks at runtime.

- `npm` and `yarn classic` hoist dependencies to a flat tree by default.
- `pnpm` builds a symlinked nested tree inside `node_modules/.pnpm`, preventing code from importing unlisted packages unless explicitly declared in `package.json`.

#### 2. Deduplication Commands
Remove duplicate versions of packages resolved across the dependency graph:
```bash
# npm
npm dedupe

# pnpm
pnpm dedupe

# Yarn
yarn dedupe
```

#### 3. Forcing Single Dependency Versions (Overrides & Resolutions)
When a nested transitive dependency contains a bug or security vulnerability, force a specific version across the entire dependency graph:

##### In `package.json` for npm:
```json
{
  "overrides": {
    "semver": "7.6.3",
    "lodash": {
      ".": "^4.17.21"
    }
  }
}
```

##### In `package.json` for pnpm:
```json
{
  "pnpm": {
    "overrides": {
      "semver": "7.6.3"
    }
  }
}
```

##### In `package.json` for Yarn:
```json
{
  "resolutions": {
    "semver": "7.6.3"
  }
}
```

---

### Step 7: Configure Monorepo Workspaces and Turborepo

Organize multi-package repositories into workspaces to share dependencies and manage internal package references without local file paths.

#### 1. npm Workspaces
In the root `package.json`:
```json
{
  "name": "root-monorepo",
  "private": true,
  "workspaces": [
    "packages/*",
    "apps/*"
  ]
}
```
Run workspace-specific commands:
```bash
# Run script in a specific workspace
npm run test --workspace=@scope/shared-utils

# Install a dependency into a specific workspace
npm install axios --workspace=@scope/web-app
```

#### 2. pnpm Workspaces
Create `pnpm-workspace.yaml` in the monorepo root:
```yaml
packages:
  - 'packages/*'
  - 'apps/*'
```

Consume internal workspace packages using the `workspace:*` protocol inside `apps/web-app/package.json`:
```json
{
  "dependencies": {
    "@scope/shared-utils": "workspace:*"
  }
}
```
Run scoped commands with `--filter`:
```bash
# Run build only for @scope/web-app and its dependencies
pnpm --filter @scope/web-app... build

# Run test in all workspace packages recursively
pnpm -r run test
```

#### 3. Turborepo Orchestration
Integrate Turborepo (`turbo`) for intelligent task pipelines, parallel execution, and artifact caching. Create `turbo.json`:
```json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", "!dist/.cache"]
    },
    "test": {
      "dependsOn": ["build"],
      "inputs": ["src/**/*.tsx", "src/**/*.ts", "test/**/*.ts"]
    },
    "lint": {
      "cache": true
    },
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```
Execute with:
```bash
npx turbo run build
```

---

### Step 8: Standardize npm Scripts and Cross-Platform Execution

#### 1. Forwarding CLI Arguments
Use `--` to forward extra arguments to the underlying script or binary:
```bash
npm run test -- --watch --coverage
pnpm run test -- --bail
```

#### 2. Cross-Platform Scripts
Avoid Unix-only shell builtins (`rm -rf`, `export VAR=val`) that fail on Windows. Use cross-platform libraries:
```json
{
  "scripts": {
    "clean": "rimraf dist coverage",
    "start:prod": "cross-env NODE_ENV=production node dist/index.js",
    "build:all": "npm run clean && npm run build"
  }
}
```

#### 3. Composing Scripts and Lifecycle Hooks
- `prepare`: Executes before package is packed and published, and on local `npm install` without arguments. Ideal for initializing Git hooks (e.g., Husky).
- `prepublishOnly`: Executes strictly before `npm publish`. Perfect for clean builds and running test suites before registry deployment.
- *Caution*: Avoid chaining dozens of implicit `pre*` and `post*` scripts (e.g., `pretest`, `posttest`) because some package managers (Yarn Berry, pnpm) do not execute custom prefix hooks automatically. Declare pipelines explicitly in your primary script or orchestrator.

---

### Step 9: Manage Environment Variables Safely

#### 1. Native Node.js `--env-file` (Node.js 20.6+)
Node.js 20.6 and later supports loading `.env` files natively without third-party dependencies:
```bash
# In package.json scripts
node --env-file=.env dist/index.js
```

#### 2. The `dotenv` Library (for Older Node.js or Multi-File Chains)
```bash
pnpm add dotenv
```
Preload in script execution:
```json
{
  "scripts": {
    "dev": "node -r dotenv/config src/index.js"
  }
}
```

#### 3. Best Practices for `.env` Files
- Commit `.env.example` with blank or dummy values into git.
- Add `.env`, `.env.local`, and `.env.*.local` to `.gitignore`.
- Validate environment variables at application startup using a runtime schema (e.g., Zod):
```typescript
import { z } from 'zod';

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'test', 'production']).default('development'),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
});

export const env = envSchema.parse(process.env);
```

---

### Step 10: Run Ephemeral Tools and Local Binaries

Execute CLI utilities without polluting project dependencies or downloading unverified binaries.

#### 1. Local Project Binaries
When a package is installed in `devDependencies`, execute it without global installation:
```bash
# Executes binary from ./node_modules/.bin/
npx eslint .
pnpm exec eslint .
yarn run eslint .
bunx eslint .
```

#### 2. Ephemeral One-Off CLI Tools
To run a command from a remote package without installing it:
```bash
# npm (prompts for confirmation unless -y is specified)
npx --yes create-vite@latest my-app

# pnpm (use dlx; pnpx is a deprecated alias)
pnpm dlx create-vite@latest my-app

# Yarn Berry
yarn dlx create-vite@latest my-app

# Bun
bunx create-vite@latest my-app
```

#### 3. Safety Guard
Use `--no-install` to ensure `npx` only runs binaries already installed locally:
```bash
npx --no-install prettier --check .
```

---

### Step 11: Configure ESM vs CommonJS Modules and Interoperability

Modern Node.js projects should prioritize ECMAScript Modules (ESM) while supporting CommonJS (CJS) where backward compatibility is required.

#### 1. ESM Defaults and File Extensions
- Set `"type": "module"` in `package.json` to treat `.js` files as ESM.
- File extension conventions:
  - `.mjs`: Always parsed as ESM, regardless of `package.json`.
  - `.cjs`: Always parsed as CommonJS, regardless of `package.json`.
  - `.js`: Inherits behavior from the nearest parent `package.json` `"type"` field (defaults to CJS if omitted).

#### 2. ESM Globals Interop
ESM does not provide `__dirname` or `__filename`. Replace them using `import.meta.url`:
```javascript
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const configPath = join(__dirname, 'config.json');
```
*Note*: ESM natively supports top-level `await` without requiring wrapping async IIFEs.

#### 3. Dual-Package Hazard
The **dual-package hazard** occurs when a stateful package is loaded by both CJS and ESM consumers, creating two distinct instances in memory. Avoid this by:
- Structuring libraries as ESM-first.
- Or ensuring the CJS build is a thin wrapper that imports or delegates to the ESM implementation, maintaining shared singleton state.

---

### Step 12: Configure TypeScript Compilation and `tsconfig.json`

Align TypeScript compiler options with the Node.js module resolution algorithm:

```json
{
  "$schema": "https://json.schemastore.org/tsconfig",
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"]
}
```

#### Dual CJS/ESM Bundling:
Rather than running `tsc` twice, use modern bundlers such as `tsup` configured for dual outputs:
```typescript
// tsup.config.ts
import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['cjs', 'esm'],
  dts: true,
  clean: true,
  sourcemap: true,
});
```

---

### Step 13: Configure `.npmrc` and `.npmignore` Packaging Hygiene

#### 1. `.npmrc` Configuration
Create an `.npmrc` file at the project root for strict build controls and scoped registries:
```ini
# Enforce strict Node version checking
engine-strict=true

# Save exact versions by default on install
save-exact=true

# Auto-install peer dependencies (pnpm specific)
auto-install-peers=true

# Scoped package registry assignment
@myorg:registry=https://npm.pkg.github.com/

# Auth token interpolation (read from environment variable in CI)
//registry.npmjs.org/:_authToken=${NODE_AUTH_TOKEN}
```

#### 2. `.npmignore` vs `"files"` in `package.json`
- **Gold Standard**: Use the `"files"` field in `package.json` as an explicit **allowlist** (`["dist", "README.md", "LICENSE"]`).
- **Denylist Risk**: `.npmignore` is a blocklist. Forgetting to update `.npmignore` when adding test suites, scratchpads, or temporary tokens can accidentally publish proprietary code or secrets to the public registry.
- If `.npmignore` is omitted, npm defaults to `.gitignore`. Never rely on `.gitignore` alone for library publishing.

---

### Step 14: Security Auditing and Supply-Chain Hardening

#### 1. Audit Vulnerabilities
Regularly inspect installed packages against the Advisory Database:
```bash
# npm audit
npm audit
# Fix non-breaking changes only
npm audit fix

# pnpm audit
pnpm audit
```

> [!WARNING]
> Avoid running `npm audit fix --force`. It forces major version upgrades on dependencies and often introduces breaking changes, unresolvable peer dependency conflicts, or broken builds. Use selective `overrides` or update direct dependencies manually.

#### 2. Prevent Supply-Chain Attacks in CI
Disable execution of arbitrary post-install scripts from untrusted packages when installing in security-sensitive environments:
```bash
pnpm install --ignore-scripts
```

#### 3. Automated Audit Gates
Incorporate `audit-ci` into CI workflows to fail only on high or critical vulnerabilities:
```bash
npx audit-ci --high --critical
```

---

### Step 15: Package and Publish to the npm Registry

#### 1. Package Artifact Validation
Before publishing, inspect the exact file archive that will be uploaded:
```bash
# Perform dry run
npm publish --dry-run

# Or generate and inspect the tarball
npm pack
tar -tf myorg-example-package-1.0.0.tgz
```

#### 2. Publish with Supply Chain Provenance
Publish scoped packages publicly with cryptographic attestations linking the package directly to its source build commit and CI workflow:
```bash
npm publish --access public --provenance
```

---

## Best Practices

- **Lock Down Production Applications**: Use `save-exact=true` in `.npmrc` for standalone applications and services to prevent accidental minor/patch breakages.
- **Use Permissive Ranges for Libraries**: Use caret (`^`) ranges and broad `peerDependencies` (`>=18.0.0 <20.0.0`) in published libraries so consuming applications do not encounter dependency version duplication.
- **Prefer `"files"` in `package.json`**: Always use an explicit allowlist in `"files"` rather than a denylist in `.npmignore` to prevent leaking source maps, test fixtures, or sensitive internal credentials.
- **Keep Lockfiles in Git**: Never add `package-lock.json`, `pnpm-lock.yaml`, or `yarn.lock` to `.gitignore`. They are essential for reproducible builds across machines and CI.
- **Centralize Node Versioning**: Commit both `.node-version` (for `fnm` and general tooling) and `.nvmrc` (for `nvm` users) containing identical LTS version strings.
- **Validate Environment Variables at Boot**: Prevent runtime crashes by failing fast during container boot if required environment variables are absent.

---

## Common Pitfalls

- **Using `npm install` in CI**: Causes lockfile drift, ignores frozen constraints, and leads to irreproducible builds. Always use `npm ci` or `pnpm install --frozen-lockfile`.
- **Relying on Phantom Dependencies**: Working locally with flat `node_modules` without noticing that a consumed module is not in `package.json`. Use `pnpm` or enable strict linting (`eslint-plugin-import` / `knip`).
- **Running `npm audit fix --force`**: Blanket-upgrades transitive dependencies across major versions, causing silent runtime failures and breaking API changes.
- **Mixing Package Managers in One Repository**: Committing multiple lockfiles (`package-lock.json` AND `pnpm-lock.yaml`) creates desynchronized dependencies and unpredictable builds. Remove obsolete lockfiles immediately when migrating.
- **Dual Package Hazard**: Publishing a library that exports both CJS and ESM without matching singletons or separate state, causing code importing the CJS version and code importing the ESM version to create duplicate internal instances.
- **Forgetting `--` in npm scripts**: Running `npm test --watch` instead of `npm test -- --watch` results in `npm` consuming the `--watch` flag itself rather than forwarding it to the test runner.

---

## Verification

Run these verification steps to confirm package management integrity:

1. **Verify Lockfile Integrity and Reproducibility**:
   ```bash
   # For npm
   npm ci --dry-run

   # For pnpm
   pnpm install --frozen-lockfile
   ```
   *Expected output*: Installation completes with exit code `0` and reports zero modified files.

2. **Verify Engine Compliance**:
   ```bash
   npm run build
   ```
   Ensure no `EBADENGINE` warnings or errors occur when running under the specified Node.js version.

3. **Check for Unused and Phantom Dependencies**:
   ```bash
   npx knip
   ```
   *Expected output*: Reports no undeclared dependencies or unused production packages.

4. **Verify Package Export Maps**:
   ```bash
   npx @arethetypeswrong/cli --pack .
   ```
   *Expected output*: All export formats (ESM, CJS, Types) resolve cleanly across Node10, Node16, and Bundler resolutions without type definition mismatches.

5. **Verify Security Status**:
   ```bash
   npm audit --audit-level=high
   # or
   pnpm audit --audit-level=high
   ```
   *Expected output*: `0 vulnerabilities found` at or above the designated severity threshold.
