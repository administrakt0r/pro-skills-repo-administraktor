# Docker Compose v2 Production & Development Patterns

This guide provides tested, reusable Docker Compose v2 patterns for common application architectures. All patterns adhere to modern Docker standards: no obsolete `version:` top-level attribute, user-defined bridge networks, persistent named volumes, strict health check dependencies, and non-root security.

---

## Table of Contents
1. [LEMP Stack (PHP-FPM, Nginx, MariaDB, Redis)](#1-lemp-stack-php-fpm-nginx-mariadb-redis)
2. [Node.js / Next.js + PostgreSQL + Redis Stack](#2-nodejs--nextjs--postgresql--redis-stack)
3. [WordPress + MariaDB + Redis + WP-CLI Stack](#3-wordpress--mariadb--redis--wp-cli-stack)
4. [Multi-Service Microservices Pattern](#4-multi-service-microservices-pattern)
5. [Development Hot-Reload & Compose Watch Patterns](#5-development-hot-reload--compose-watch-patterns)
6. [Hardened Production Deployment Pattern](#6-hardened-production-deployment-pattern)
7. [Reverse Proxy Patterns (Nginx & Traefik v3)](#7-reverse-proxy-patterns-nginx--traefik-v3)

---

## 1. LEMP Stack (PHP-FPM, Nginx, MariaDB, Redis)

A high-performance PHP 8.3 architecture decoupling static web serving (Nginx) from PHP execution (PHP-FPM) and caching (Redis).

```yaml
# docker-compose.yml
services:
  nginx:
    image: nginx:1.25-alpine
    restart: unless-stopped
    ports:
      - "80:80"
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
      - app-code:/var/www/html:ro
    depends_on:
      php:
        condition: service_healthy
    networks:
      - frontend-net
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  php:
    build:
      context: ./php
      dockerfile: Dockerfile
    restart: unless-stopped
    volumes:
      - app-code:/var/www/html
    environment:
      - DB_HOST=mariadb
      - DB_NAME=${DB_NAME:-app_database}
      - DB_USER=${DB_USER:-app_user}
      - DB_PASSWORD=${DB_PASSWORD}
      - REDIS_HOST=redis
    depends_on:
      mariadb:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - frontend-net
      - backend-net
    healthcheck:
      test: ["CMD-SHELL", "cgi-fcgi -bind -connect 127.0.0.1:9000 || exit 1"]
      interval: 10s
      timeout: 3s
      retries: 3
      start_period: 5s

  mariadb:
    image: mariadb:10.11
    restart: unless-stopped
    environment:
      MARIADB_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MARIADB_DATABASE: ${DB_NAME:-app_database}
      MARIADB_USER: ${DB_USER:-app_user}
      MARIADB_PASSWORD: ${DB_PASSWORD}
    volumes:
      - db-data:/var/lib/mysql
    networks:
      - backend-net
    healthcheck:
      test: ["CMD", "healthcheck.sh", "--connect", "--innodb_initialized"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 15s

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: ["redis-server", "--appendonly", "yes", "--requirepass", "${REDIS_PASSWORD}"]
    volumes:
      - redis-data:/data
    networks:
      - backend-net
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

networks:
  frontend-net:
    driver: bridge
  backend-net:
    driver: bridge
    internal: true

volumes:
  app-code:
  db-data:
  redis-data:
```

### Supporting Nginx Configuration (`nginx/default.conf`)
```nginx
server {
    listen 80;
    server_name localhost;
    root /var/www/html/public;
    index index.php index.html;

    client_max_body_size 32M;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
        fastcgi_pass php:9000;
        fastcgi_index index.php;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME /var/www/html/public$fastcgi_script_name;
        fastcgi_param PATH_INFO $fastcgi_path_info;
        fastcgi_intercept_errors off;
        fastcgi_buffer_size 16k;
        fastcgi_buffers 4 16k;
    }

    location ~ /\.ht {
        deny all;
    }
}
```

---

## 2. Node.js / Next.js + PostgreSQL + Redis Stack

A modern full-stack web setup with database migration management and caching.

```yaml
# docker-compose.yml
services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
      target: runner
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-app}?schema=public
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - NEXTAUTH_SECRET=${NEXTAUTH_SECRET}
      - NEXTAUTH_URL=${NEXTAUTH_URL:-http://localhost:3000}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - app-net
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 1024M
        reservations:
          cpus: "0.25"
          memory: 256M

  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB:-app}
    volumes:
      - postgres-storage:/var/lib/postgresql/data
      - ./init-db:/docker-entrypoint-initdb.d:ro
    networks:
      - app-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-app}"]
      interval: 5s
      timeout: 5s
      retries: 5
      start_period: 10s

  redis:
    image: redis:7.2-alpine
    restart: unless-stopped
    command: ["redis-server", "--requirepass", "${REDIS_PASSWORD}"]
    volumes:
      - redis-storage:/data
    networks:
      - app-net
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

networks:
  app-net:
    driver: bridge

volumes:
  postgres-storage:
  redis-storage:
```

---

## 3. WordPress + MariaDB + Redis + WP-CLI Stack

A production-ready WordPress orchestration featuring automatic database synchronization, persistent uploads, Redis object caching, and a WP-CLI automation container.

```yaml
# docker-compose.yml
services:
  wordpress:
    image: wordpress:6-fpm-alpine
    restart: unless-stopped
    environment:
      WORDPRESS_DB_HOST: db:3306
      WORDPRESS_DB_NAME: ${WORDPRESS_DB_NAME:-wordpress}
      WORDPRESS_DB_USER: ${WORDPRESS_DB_USER:-wpuser}
      WORDPRESS_DB_PASSWORD: ${WORDPRESS_DB_PASSWORD}
      WORDPRESS_TABLE_PREFIX: wp_
    volumes:
      - wp-data:/var/www/html
      - ./php/custom.ini:/usr/local/etc/php/conf.d/custom.ini:ro
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - wp-frontend
      - wp-backend
    healthcheck:
      test: ["CMD-SHELL", "nc -z 127.0.0.1 9000 || exit 1"]
      interval: 10s
      timeout: 3s
      retries: 3

  webserver:
    image: nginx:1.25-alpine
    restart: unless-stopped
    ports:
      - "80:80"
    volumes:
      - wp-data:/var/www/html:ro
      - ./nginx/wordpress.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      wordpress:
        condition: service_healthy
    networks:
      - wp-frontend

  db:
    image: mariadb:10.11
    restart: unless-stopped
    environment:
      MARIADB_DATABASE: ${WORDPRESS_DB_NAME:-wordpress}
      MARIADB_USER: ${WORDPRESS_DB_USER:-wpuser}
      MARIADB_PASSWORD: ${WORDPRESS_DB_PASSWORD}
      MARIADB_ROOT_PASSWORD: ${MARIADB_ROOT_PASSWORD}
    volumes:
      - db-data:/var/lib/mysql
    networks:
      - wp-backend
    healthcheck:
      test: ["CMD", "healthcheck.sh", "--connect", "--innodb_initialized"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 15s

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: ["redis-server", "--maxmemory", "128mb", "--maxmemory-policy", "allkeys-lru"]
    networks:
      - wp-backend
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  wpcli:
    image: wordpress:cli-2-php8.2
    restart: "no"
    user: "33:33" # Matches www-data UID/GID
    environment:
      WORDPRESS_DB_HOST: db:3306
      WORDPRESS_DB_NAME: ${WORDPRESS_DB_NAME:-wordpress}
      WORDPRESS_DB_USER: ${WORDPRESS_DB_USER:-wpuser}
      WORDPRESS_DB_PASSWORD: ${WORDPRESS_DB_PASSWORD}
    volumes:
      - wp-data:/var/www/html
    depends_on:
      wordpress:
        condition: service_healthy
    networks:
      - wp-backend
    entrypoint: ["wp"]
    command: ["--info"]

networks:
  wp-frontend:
    driver: bridge
  wp-backend:
    driver: bridge
    internal: true

volumes:
  wp-data:
  db-data:
```

---

## 4. Multi-Service Microservices Pattern

A segmented tier architecture containing a public frontend, internal API service, asynchronous message queue, background task worker, and secured database.

```yaml
# docker-compose.yml
services:
  # Tier 1: Frontend SPA / Static Gateway
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: unless-stopped
    ports:
      - "80:80"
    networks:
      - ingress-net
    depends_on:
      api:
        condition: service_healthy

  # Tier 2: Public-facing API Service
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    environment:
      - PORT=8000
      - DATABASE_URL=postgresql://api_user:${DB_PASS}@database:5432/api_db
      - AMQP_URL=amqp://guest:${RABBIT_PASS}@messagebroker:5672/
      - REDIS_URL=redis://cache:6379/0
    networks:
      - ingress-net
      - internal-net
    depends_on:
      database:
        condition: service_healthy
      messagebroker:
        condition: service_healthy
      cache:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 3s
      retries: 3

  # Tier 3: Asynchronous Worker (Internal Only)
  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.worker
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql://api_user:${DB_PASS}@database:5432/api_db
      - AMQP_URL=amqp://guest:${RABBIT_PASS}@messagebroker:5672/
    networks:
      - internal-net
    depends_on:
      database:
        condition: service_healthy
      messagebroker:
        condition: service_healthy

  # Tier 4: Message Broker
  messagebroker:
    image: rabbitmq:3.13-management-alpine
    restart: unless-stopped
    environment:
      RABBITMQ_DEFAULT_PASS: ${RABBIT_PASS}
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq
    networks:
      - internal-net
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "-q", "ping"]
      interval: 15s
      timeout: 5s
      retries: 5

  # Tier 5: Internal Cache
  cache:
    image: redis:7-alpine
    restart: unless-stopped
    networks:
      - internal-net
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  # Tier 6: Core Relational Database
  database:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: api_db
      POSTGRES_USER: api_user
      POSTGRES_PASSWORD: ${DB_PASS}
    volumes:
      - db-data:/var/lib/postgresql/data
    networks:
      - internal-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U api_user -d api_db"]
      interval: 5s
      timeout: 5s
      retries: 5

networks:
  ingress-net:
    driver: bridge
  internal-net:
    driver: bridge
    internal: true

volumes:
  rabbitmq-data:
  db-data:
```

---

## 5. Development Hot-Reload & Compose Watch Patterns

Docker Compose v2.22+ introduces the `develop.watch` feature, enabling near-instant file synchronization and targeted rebuilding without restarting containers or running external sync scripts.

### Pattern 5.1: Node.js / Next.js with Compose Watch

```yaml
# docker-compose.yml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    command: npm run dev
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - WATCHPACK_POLLING=true # Useful for file-event sync on virtualized filesystems
    volumes:
      # Anonymous volume prevents local node_modules from overriding container node_modules
      - /app/node_modules
    develop:
      watch:
        # Sync changes immediately without restarting
        - action: sync
          path: ./src
          target: /app/src
          ignore:
            - ./src/**/*.test.ts
        - action: sync
          path: ./public
          target: /app/public
        # Rebuild container image when dependencies change
        - action: rebuild
          path: ./package.json
```

### Pattern 5.2: Python FastAPI / Flask with Hot-Reload

```yaml
# docker-compose.yml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.dev
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - PYTHONDONTWRITEBYTECODE=1
    develop:
      watch:
        - action: sync
          path: ./app
          target: /app/app
        - action: rebuild
          path: ./requirements.txt
```

Run compose in watch mode:
```bash
docker compose watch
```

---

## 6. Hardened Production Deployment Pattern

A zero-trust configuration adhering to least privilege: read-only root filesystems, dropped capabilities, memory/CPU quotas, secret file mounting, and strict log retention.

```yaml
# docker-compose.prod.yml
services:
  web:
    image: registry.example.com/org/application:v1.4.2
    restart: unless-stopped
    read_only: true
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    user: "10001:10001"
    ports:
      - "127.0.0.1:8080:8080" # Bound strictly to localhost; exposed via host proxy
    environment:
      - NODE_ENV=production
      - DB_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password
    tmpfs:
      - /tmp:rw,noexec,nosuid,size=32m
      - /app/.cache:rw,noexec,nosuid,size=64m
    deploy:
      resources:
        limits:
          cpus: "1.00"
          memory: 512M
        reservations:
          cpus: "0.20"
          memory: 128M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"
        tag: "{{.ImageName}}/{{.Name}}/{{.ID}}"

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

---

## 7. Reverse Proxy Patterns (Nginx & Traefik v3)

### Pattern 7.1: Nginx Edge Reverse Proxy with SSL Termination

Orchestrates automated SSL routing, HTTP-to-HTTPS redirection, and reverse-proxy header forwarding.

```yaml
# docker-compose.yml
services:
  proxy:
    image: nginx:1.25-alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./certs:/etc/nginx/certs:ro
    networks:
      - proxy-net
    logging:
      driver: "json-file"
      options:
        max-size: "20m"
        max-file: "3"

  app-service:
    image: my-app:latest
    restart: unless-stopped
    networks:
      - proxy-net
    # No host port exposed; only accessible via proxy-net

networks:
  proxy-net:
    driver: bridge
```

#### Production Nginx Reverse Proxy Config (`nginx/conf.d/app.conf`)
```nginx
upstream backend_app {
    server app-service:3000;
    keepalive 32;
}

server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com www.example.com;

    ssl_certificate /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    location / {
        proxy_pass http://backend_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
        proxy_connect_timeout 10s;
    }
}
```

---

### Pattern 7.2: Traefik v3 Dynamic Reverse Proxy with Automatic Let's Encrypt

Traefik monitors the Docker socket and dynamically creates routing rules and SSL certificates from container labels.

```yaml
# docker-compose.yml
services:
  traefik:
    image: traefik:v3.0
    restart: unless-stopped
    command:
      - "--api.dashboard=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      # Global HTTP -> HTTPS Redirection
      - "--entrypoints.web.http.redirections.entrypoint.to=websecure"
      - "--entrypoints.web.http.redirections.entrypoint.scheme=https"
      # ACME / Let's Encrypt Configuration
      - "--certificatesresolvers.myresolver.acme.tlschallenge=true"
      - "--certificatesresolvers.myresolver.acme.email=${ACME_EMAIL}"
      - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - traefik-certificates:/letsencrypt
    networks:
      - web-gateway
    labels:
      - "traefik.enable=true"
      # Protect the Traefik dashboard
      - "traefik.http.routers.dashboard.rule=Host(`traefik.example.com`)"
      - "traefik.http.routers.dashboard.service=api@internal"
      - "traefik.http.routers.dashboard.entrypoints=websecure"
      - "traefik.http.routers.dashboard.tls.certresolver=myresolver"
      - "traefik.http.routers.dashboard.middlewares=auth"
      - "traefik.http.middlewares.auth.basicauth.users=${DASHBOARD_AUTH}"

  api-service:
    image: my-backend-api:latest
    restart: unless-stopped
    networks:
      - web-gateway
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`api.example.com`)"
      - "traefik.http.routers.api.entrypoints=websecure"
      - "traefik.http.routers.api.tls.certresolver=myresolver"
      - "traefik.http.services.api.loadbalancer.server.port=8000"

  frontend-service:
    image: my-frontend-app:latest
    restart: unless-stopped
    networks:
      - web-gateway
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`example.com`)"
      - "traefik.http.routers.frontend.entrypoints=websecure"
      - "traefik.http.routers.frontend.tls.certresolver=myresolver"
      - "traefik.http.services.frontend.loadbalancer.server.port=80"

networks:
  web-gateway:
    driver: bridge

volumes:
  traefik-certificates:
```

---

## 8. Compose Best Practice Checklist

When assembling multi-container deployments:
- [ ] **Omit `version:`**: Docker Compose v2 specifies format automatically; top-level `version:` triggers deprecation warnings.
- [ ] **Define Explicit Health Checks**: Ensure dependent containers (`web`, `worker`) delay startup until databases and brokers are fully initialized (`condition: service_healthy`).
- [ ] **Isolate Networks**: Place databases and internal caches on `internal: true` networks without external gateway access.
- [ ] **Pin Volume Names**: Declare named volumes under the root `volumes:` block to prevent accidental data destruction across container redeploys.
- [ ] **Set Resource Limits**: Always declare `deploy.resources.limits` for production containers to prevent noisy neighbor memory exhaustion.
- [ ] **Protect Secrets**: Never commit `.env` containing production credentials; use Docker Compose secrets (`secrets:`) or external secret managers in production.
