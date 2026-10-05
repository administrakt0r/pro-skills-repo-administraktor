---
name: docker-containerization
description: >-
  Containerize applications, design multi-stage Dockerfiles, configure Docker Compose v2 stacks, optimize image layers and caching, manage networks, volumes, and secrets, and harden container security across PHP/WordPress, Node.js/Next.js, and Python environments.
---

# Docker and Containerization

A standardized guide for building, orchestrating, optimizing, and securing containerized applications using Docker Engine and Docker Compose v2. Covers multi-stage builds, BuildKit caching, minimal base images, production security hardening, and ecosystem stacks for PHP/WordPress, Node.js/Next.js, and Python.

## When to Use

- Authoring new Dockerfiles or modernizing legacy single-stage Docker configurations.
- Optimizing container image size, build speed, and layer cache hit ratios using BuildKit.
- Designing multi-container service architectures with Docker Compose v2 (`docker compose`).
- Creating `.dockerignore` filters to protect build context and prevent credential leakage.
- Implementing container security policies: non-root execution, minimal base images, read-only root filesystems, and Linux capability dropping.
- Managing persistent data and isolated inter-service communication via named volumes and custom bridge networks.
- Implementing production health checks and dependency chains with `depends_on: condition: service_healthy`.
- Setting up development workflows with live reloading (bind mounts, Docker Compose Watch) vs. immutable production deployments.
- Containerizing stacks across PHP-FPM / WordPress, Node.js / Next.js (standalone), and Python (FastAPI, Django, Flask).
- Debugging container lifecycle failures, inspecting runtime metrics, and executing resource cleanup.

## Prerequisites

- **Docker Engine**: Version 24.0+ (or Docker Desktop with Docker Compose v2 plugin).
- **Docker BuildKit**: Enabled by default in modern Docker; ensure `DOCKER_BUILDKIT=1` is active in build environments.
- **Docker Compose**: v2.20+ (accessed as `docker compose`, not legacy `docker-compose`).
- User permissions: Active user belongs to the `docker` group (`sudo usermod -aG docker $USER`) or has rootless Docker configured.

---

## Steps

### 1. Base Image Selection

Selecting the proper base image balances attack surface, compatibility, and final image size.

| Image Variant | Typical Size | C Standard Library | Package Manager | Recommended Use Case | Tradeoffs & Pitfalls |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Debian / Ubuntu Slim** (`*-slim-bookworm`) | 50–150 MB | `glibc` | `apt` | Default choice for Python, Node.js, and general runtimes | Slightly larger than Alpine, but avoids C extension compilation errors |
| **Alpine Linux** (`*-alpine`) | 5–15 MB | `musl` | `apk` | Go/Rust static binaries, lightweight Nginx proxies, simple scripts | DNS resolver differences (`musl`), precompiled Python wheels (`manylinux`) often missing and require slow compilation |
| **Distroless** (`gcr.io/distroless/*`) | 20–60 MB | `glibc` | None | Hardened production runtimes (Node.js, Java, Python, Go) | No package manager or interactive shell (`sh`/`bash`); debugging requires debug variants or ephemeral debug containers |
| **Scratch** (`FROM scratch`) | 0 MB | None | None | Statically compiled binaries (Go, Rust, C) | Completely empty; cannot run dynamic binaries, lacks root CA certificates unless explicitly copied |

#### Base Image Selection Rules
- **Node.js**: Use `node:<version>-bookworm-slim` for standard apps or `node:<version>-alpine` if native addons (like `bcrypt` or `sharp`) are precompiled or not needed.
- **Python**: Use `python:<version>-slim-bookworm`. Avoid `python:alpine` for data science, NumPy, Pandas, or PyTorch, as missing `manylinux` wheels force compile-from-source, multiplying build times.
- **PHP**: Use `php:<version>-fpm-bookworm` or `php:<version>-fpm-alpine`. Install extensions via `mlocati/docker-php-extension-installer`.
- **Compiled binaries (Go/Rust)**: Build inside a full SDK stage, copy the static binary into `scratch` or `gcr.io/distroless/static-debian12`.

---

### 2. Context Hygiene and `.dockerignore`

Every build sends the context directory to the Docker daemon. A missing or inadequate `.dockerignore` slows builds, breaks caching, and risks baking secrets, credentials, or host-specific binaries into image layers.

Create a `.dockerignore` file in the same directory as the `Dockerfile`:

```gitignore
# Git & VCS
.git/
.gitignore
.gitattributes

# Environment & Secrets (NEVER transfer to build context)
.env*
!.env.example
*.pem
*.key
*.cert
*.crt
id_rsa*
secrets/

# Build outputs & dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
.next/
dist/
build/
out/
coverage/
.turbo/

# Python artifacts
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.pytest_cache/
.mypy_cache/
.ruff_cache/

# PHP / Composer artifacts
vendor/
.phpunit.result.cache

# Operating System & IDE junk
.DS_Store
Thumbs.db
.idea/
.vscode/
*.sublime-project
*.sublime-workspace
*.swp
*.swo
*~

# Temporary & logs
*.log
tmp/
temp/
Dockerfile*
docker-compose*.yml
README.md
```

---

### 3. Dockerfile Optimization and Multi-Stage Builds

#### Layer Caching Order
Docker evaluates cache from top to bottom. Place frequently changing instructions (`COPY src/ .`) as late as possible, and place infrequently changing instructions (package manager updates, dependency manifests) early.

#### Modern BuildKit Syntax and Cache Mounts
Enable BuildKit features by adding `# syntax=docker/dockerfile:1` at the beginning of the Dockerfile. Use `--mount=type=cache` to cache package downloads across builds without bloating the image layers.

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm AS base

# Install system dependencies with apt cache mount
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
    && rm -rf /var/lib/apt/lists/*
```

#### Multi-Stage Architecture Template
Multi-stage builds separate build-time toolchains (compilers, dev dependencies, build caches) from the lean runtime container:

```dockerfile
# syntax=docker/dockerfile:1

# Stage 1: Dependency resolution & build
FROM base-runtime AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci
COPY . .
RUN npm run build && npm prune --production

# Stage 2: Minimal runtime
FROM base-runtime AS runner
WORKDIR /app
# Run as non-root user
USER 10001:10001
# Copy only the compiled output and production dependencies
COPY --from=builder --chown=10001:10001 /app/package.json ./
COPY --from=builder --chown=10001:10001 /app/node_modules ./node_modules
COPY --from=builder --chown=10001:10001 /app/dist ./dist

EXPOSE 3000
CMD ["node", "dist/index.js"]
```

---

### 4. Stack-Specific Production Dockerfiles

#### A. Node.js / Next.js (Standalone Mode)
Configure `output: 'standalone'` in `next.config.js` to automatically bundle only required production dependencies.

```dockerfile
# syntax=docker/dockerfile:1
FROM node:20-bookworm-slim AS base
WORKDIR /app
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

# Stage 1: Dependencies
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --include=dev

# Stage 2: Build
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NODE_ENV=production
RUN npm run build

# Stage 3: Production Runner
FROM base AS runner
WORKDIR /app

# Create dedicated non-root user and group
RUN groupadd --system --gid 1001 nodejs && \
    useradd --system --uid 1001 nextjs

# Copy standalone output and static assets with explicit ownership
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs:nodejs
EXPOSE 3000
ENV PORT=3000 \
    HOSTNAME="0.0.0.0"

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD node -e "fetch('http://localhost:3000/api/health').then(r => process.exit(r.ok ? 0 : 1)).catch(() => process.exit(1))"

CMD ["node", "server.js"]
```

#### B. PHP 8.3 FPM / WordPress Stack
Uses the official PHP installer script for extensions and configures `php-fpm` for high-throughput production.

```dockerfile
# syntax=docker/dockerfile:1
FROM php:8.3-fpm-bookworm AS base

# Install official extension installer tool
ADD --chmod=0755 https://github.com/mlocati/docker-php-extension-installer/releases/latest/download/install-php-extensions /usr/local/bin/

# Install essential extensions for WordPress / modern PHP
RUN install-php-extensions \
    bcmath \
    exif \
    gd \
    intl \
    mysqli \
    opcache \
    pdo_mysql \
    redis \
    zip

# Configure production opcache and php.ini settings
RUN { \
    echo 'opcache.memory_consumption=128'; \
    echo 'opcache.interned_strings_buffer=8'; \
    echo 'opcache.max_accelerated_files=10000'; \
    echo 'opcache.revalidate_freq=2'; \
    echo 'opcache.validate_timestamps=1'; \
    echo 'opcache.fast_shutdown=1'; \
    echo 'opcache.enable_cli=1'; \
} > /usr/local/etc/php/conf.d/opcache-recommended.ini

RUN { \
    echo 'upload_max_filesize = 64M'; \
    echo 'post_max_size = 64M'; \
    echo 'memory_limit = 256M'; \
    echo 'max_execution_time = 300'; \
    echo 'expose_php = Off'; \
} > /usr/local/etc/php/conf.d/custom.ini

WORKDIR /var/www/html

# Install Composer for dependency management
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# Copy application files
COPY --chown=www-data:www-data . /var/www/html

USER www-data
EXPOSE 9000

HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD SCRIPT_NAME=/ping SCRIPT_FILENAME=/ping REQUEST_METHOD=GET cgi-fcgi -bind -connect 127.0.0.1:9000 || exit 1

CMD ["php-fpm", "-F"]
```

#### C. Python (FastAPI / Django with Virtual Environment)
Uses multi-stage compilation to isolate build dependencies (`gcc`, build headers) from the final runtime image.

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Stage 1: Build virtual environment
FROM base AS builder
WORKDIR /build

RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Stage 2: Lean runtime
FROM base AS runner
WORKDIR /app

# Install runtime libraries only (e.g. libpq for PostgreSQL)
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Create unprivileged user
RUN groupadd --system --gid 10001 appgroup && \
    useradd --system --uid 10001 --gid appgroup appuser

# Copy virtualenv and code from builder
COPY --from=builder --chown=appuser:appgroup /opt/venv /opt/venv
COPY --chown=appuser:appgroup . /app

ENV PATH="/opt/venv/bin:$PATH"
USER appuser:appgroup
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### 5. Container Security Hardening

Implement defense-in-depth across the container layer:

#### Principle of Least Privilege (Non-Root User)
Never run containers as `root` (UID 0). A container breakout from a root container grants root host access.
```dockerfile
# Create system user and group with explicit non-conflicting UID/GID
RUN groupadd -g 10001 appuser && \
    useradd -u 10001 -g appuser -s /sbin/nologin -d /app appuser
USER 10001:10001
```

#### Read-Only Root Filesystem & Dropping Capabilities
Enforce that runtime files cannot be overwritten or injected by attackers. Use Docker Compose or CLI flags:

```yaml
services:
  app:
    image: my-app:latest
    read_only: true
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    tmpfs:
      - /tmp:rw,noexec,nosuid,size=64m
      - /run:rw,noexec,nosuid,size=16m
```

#### Secure Secret Handling (BuildKit Secrets)
Never pass tokens or private keys using `ARG` or `ENV` in a Dockerfile, as they persist in image history.
Use `--mount=type=secret`:

```dockerfile
# syntax=docker/dockerfile:1
FROM node:20-bookworm-slim
WORKDIR /app
COPY package.json ./

# Access secret securely without leaking it into image layers
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm ci
```
Execute the build passing the secret file:
```bash
docker buildx build --secret id=npmrc,src=$HOME/.npmrc -t my-app .
```

---

### 6. Volume Management and Networking

#### Volume Types and Use Cases
1. **Named Volumes**: Managed entirely by Docker (`/var/lib/docker/volumes/`). Ideal for database storage, stateful caches, and persistent production data.
2. **Bind Mounts**: Maps a specific host filesystem directory or file directly into the container (`./src:/app/src`). Ideal for local development source code mounting.
3. **tmpfs Mounts**: Stored strictly in host memory. Ideal for sensitive files or transient write operations (session caches, `/tmp`).

#### Isolated Network Topologies
Avoid default bridge networks. Use custom user-defined bridge networks with segmented tiers (e.g., `frontend` vs `backend`):

```yaml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # Prevents direct egress/ingress outside Docker host
```

---

### 7. Docker Compose v2 Core Architecture

Docker Compose v2 standardizes service definitions and lifecycle orchestration. Do not include the obsolete `version:` top-level attribute.

```yaml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
      target: runner
    restart: unless-stopped
    ports:
      - "8080:8000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgres://${DB_USER:-postgres}:${DB_PASSWORD}@postgres:5432/${DB_NAME:-app}
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - app-network
    volumes:
      - app-storage:/app/uploads
    deploy:
      resources:
        limits:
          cpus: "1.50"
          memory: 512M
        reservations:
          cpus: "0.25"
          memory: 128M

  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME:-app}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres} -d ${DB_NAME:-app}"]
      interval: 5s
      timeout: 5s
      retries: 5
      start_period: 10s

networks:
  app-network:
    driver: bridge

volumes:
  postgres-data:
  app-storage:
```

---

### 8. Development vs. Production Configurations

Use compose file inheritance to separate local development convenience from production hardening.

#### Base File (`docker-compose.yml`)
Contains common service relationships, network definitions, and volume names.

#### Development Override (`docker-compose.override.yml`)
Automatically picked up by `docker compose up` without flags:
- Mounts host source code via bind mounts.
- Enables debugging ports.
- Sets `NODE_ENV=development`.
- Uses Compose Watch for automated sync:

```yaml
# docker-compose.override.yml
services:
  api:
    build:
      target: builder
    command: npm run dev
    environment:
      - NODE_ENV=development
    volumes:
      - .:/app
      - /app/node_modules
    develop:
      watch:
        - action: sync
          path: ./src
          target: /app/src
        - action: rebuild
          path: package.json
```

#### Production Overlay (`docker-compose.prod.yml`)
Run with `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d`:
- Enforces `restart: always` or `restart: unless-stopped`.
- Applies CPU and memory limits.
- Binds ports only to reverse proxy or localhost (`127.0.0.1:8080:8000`).
- Configures log rotation drivers to avoid exhausting host disk storage.

---

### 9. Logging, Debugging, and CLI Essentials

#### Essential Commands Cheat Sheet

| Task | Command |
| :--- | :--- |
| **Build with BuildKit** | `docker buildx build -t app:v1.0.0 -f Dockerfile .` |
| **Build without cache** | `docker buildx build --no-cache -t app:v1.0.0 .` |
| **Run interactive container** | `docker run --rm -it -p 8080:80 app:v1.0.0 sh` |
| **Run in background** | `docker run -d --name web -p 8080:80 app:v1.0.0` |
| **Execute inside running container**| `docker exec -it web sh` |
| **View logs with timestamp** | `docker logs -f --tail 100 -t web` |
| **Inspect container health/state** | `docker inspect --format '{{json .State.Health}}' web` |
| **View resource metrics (RAM/CPU)** | `docker stats --no-stream` |
| **Compose start detached** | `docker compose up -d` |
| **Compose rebuild and restart** | `docker compose up -d --build` |
| **Compose stop and remove volumes**| `docker compose down -v` |
| **Compose view process status** | `docker compose ps` |
| **Prune unused resources safely** | `docker system prune -f` |
| **Prune all unused images** | `docker image prune -a -f` |
| **Prune orphaned volumes** | `docker volume prune -f` |

#### Container Log Configuration
Prevent unmanaged log growth from exhausting host disk space by configuring the JSON-file logging driver:

```yaml
services:
  app:
    logging:
      driver: "json-file"
      options:
        max-size: "20m"
        max-file: "5"
```

#### Debugging Crashed or Distroless Containers
If a container fails immediately on startup or lacks a shell (`distroless`/`scratch`):
```bash
# 1. Inspect exit code and last logs
docker inspect <container-id> --format '{{.State.ExitCode}}'
docker logs <container-id>

# 2. Override entrypoint to inspect filesystem
docker run --rm -it --entrypoint /bin/sh my-app:latest

# 3. For distroless images without shell, mount the container's filesystem in a debugging container:
docker run --rm -it --pid=container:<target-container> --net=container:<target-container> nicolaka/netshoot
```

---

## Best Practices

- **Explicit Tagging**: Never use `:latest` in production Dockerfiles or Compose files. Always pin major/minor versions or SHA digests (`node:20.11.0-bookworm-slim` or `node:20-slim@sha256:...`).
- **One Process Per Container**: Run only one service per container (e.g., separate Nginx and PHP-FPM into two distinct containers instead of combining them with supervisord).
- **Signal Forwarding**: Use `exec` syntax for `CMD` and `ENTRYPOINT` (`CMD ["node", "server.js"]` instead of `CMD node server.js`). Shell form wraps the process in `/bin/sh -c`, which does not forward `SIGTERM`, causing 10-second stop delays.
- **Clean Up in the Same RUN Layer**: When installing packages with `apt-get`, clean up lists in the same layer (`apt-get clean && rm -rf /var/lib/apt/lists/*`) to prevent residual files from staying in intermediate layers.
- **Order COPY Commands by Volatility**: Copy dependency declarations (`package.json`, `requirements.txt`, `composer.json`) and run installation commands before copying project source code.
- **Resource Constraints**: Always configure `mem_limit` / `cpus` limits in production Compose definitions to prevent rogue processes from causing host Out-Of-Memory (OOM) kills.

---

## Common Pitfalls

- **Leaking Host `node_modules` or `.venv`**: Failing to add `node_modules` or `.venv` to `.dockerignore` copies host-compiled binaries into Linux containers, causing binary incompatibility crashes.
- **Ignoring Zombie Processes (PID 1 Problem)**: Running applications as PID 1 that do not reap child processes or handle Unix signals. Use `--init` flag or `tini` as entrypoint for complex multi-process tools.
- **Hardcoding Secrets via ARG**: Storing API keys or tokens in `ARG` values in Dockerfiles leaves secrets permanently readable in image metadata via `docker history`. Use BuildKit secret mounts instead.
- **Port Mapping Confusion**: Confusing `HOST:CONTAINER` port mapping (`ports: - "8080:80"` exposes port 80 inside container to 8080 on host). `expose:` only exposes ports to other containers on the same Docker network.
- **Alpine Musl Incompatibilities**: Compiling native C/C++ extensions or running Node/Python binaries on Alpine often fails silently or causes subtle performance degradation due to the `musl` memory allocator.
- **Writing to Read-Only Directories**: Deploying an image with `read_only: true` without creating writable `tmpfs` mounts for `/tmp` or `/var/run` causes runtime crashes for applications expecting temporary scratch space.

---

## Verification

Execute the following checklist to confirm container build quality, image security, and Compose stack health:

### 1. Build & Layer Inspection
```bash
# Verify build succeeds with BuildKit
DOCKER_BUILDKIT=1 docker build -t test-image:local .

# Inspect layer sizes and detect unexpected bloated layers
docker history test-image:local --format "table {{.Size}}\t{{.CreatedBy}}"
```

### 2. Runtime Security & User Verification
```bash
# Verify non-root user execution (should return non-zero UID, e.g. 10001)
docker run --rm test-image:local id

# Verify container cannot gain new privileges
docker run --rm --security-opt=no-new-privileges:true test-image:local id
```

### 3. Image Vulnerability Scan
```bash
# Scan image for known CVEs using Docker Scout or Trivy
docker scout cves test-image:local || trivy image test-image:local
```

### 4. Compose Health & Network Orchestration
```bash
# Validate compose file syntax without starting services
docker compose config

# Start services in detached mode
docker compose up -d

# Verify all services achieve healthy state
docker compose ps

# Check logs for startup errors or missing dependencies
docker compose logs --tail 50
```

---

## Deep Dive Reference

For production-ready Compose architectures, hot-reload configurations, database integrations, and reverse proxy patterns:
- [Docker Compose Patterns Reference](references/compose-patterns.md)
