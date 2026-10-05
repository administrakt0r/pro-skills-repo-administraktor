---
name: database-management
description: >-
  Design, optimize, migrate, and maintain relational and hybrid database systems across PostgreSQL, MySQL, MariaDB, and SQLite. Covers schema design, normalization and denormalization, indexing strategies, transactions (ACID), migration management, ORM integration (Prisma, Drizzle, Eloquent, SQLAlchemy), security, backups, connection pooling, and engine-specific optimizations.
---

# Database Management & Schema Engineering

A production-grade guide for architecting, querying, tuning, migrating, and securing relational and hybrid database systems. This skill establishes standard patterns across PostgreSQL, MySQL, MariaDB, and SQLite, with architectural guidance on when to introduce NoSQL paradigms.

---

## When to Use

- Designing or refactoring relational database schemas, tables, relationships, and constraints.
- Choosing between PostgreSQL, MySQL/MariaDB, SQLite, or specialized NoSQL data stores.
- Selecting optimal data types, primary key strategies (UUIDv7, ULID, BigInt), and column attributes.
- Designing indexing strategies (B-Tree, composite, covering, partial, GIN/GiST, BRIN).
- Authoring zero-downtime, versioned schema migrations with backwards compatibility and rollbacks.
- Writing complex analytical or transactional queries using multi-table JOINs, subqueries, Common Table Expressions (CTEs), and window functions.
- Managing database transactions, handling concurrency anomalies, configuring isolation levels, and resolving deadlocks.
- Configuring application and proxy connection poolers (PgBouncer, ProxySQL).
- Tuning database engine configuration files (`postgresql.conf`, `my.cnf`, SQLite `PRAGMA` flags).
- Integrating Object-Relational Mappers (Prisma, Drizzle, Eloquent, SQLAlchemy) while preventing N+1 queries.
- Implementing database security controls, RBAC privileges, encryption at rest/in transit, and backup/restore workflows.

---

## Prerequisites

- **Command-line clients**: `psql` (PostgreSQL 14+), `mysql` / `mariadb` (MySQL 8.0+ / MariaDB 10.6+), `sqlite3` (3.35+).
- **Application drivers / runtimes**: Node.js (`pg`, `mysql2`, `@libsql/client`), Python (`psycopg3`, `asyncpg`, `pymysql`), PHP (`pdo_pgsql`, `pdo_mysql`), Go (`pgx`, `go-sql-driver/mysql`).
- **Migration & tooling**: Access to framework migration tools or standalone runners (`flyway`, `liquibase`, `db-migrate`, `alembic`, `prisma`, `drizzle-kit`).

---

## Steps

### 1. Database Engine Selection & Fundamentals

Evaluate workload characteristics against database engine architectures:

| Engine | Ideal Workload | Concurrency Model | Key Strengths | Limitations |
| :--- | :--- | :--- | :--- | :--- |
| **PostgreSQL** | Complex OLTP, analytical workloads, geo-spatial, rich JSON querying, enterprise scale. | Process-per-connection MVCC. | JSONB, custom types, extensions (`pgvector`, `PostGIS`), advanced indexing, strict ANSI compliance. | Higher memory footprint per connection; requires external connection pooler (PgBouncer) for massive concurrency. |
| **MySQL / MariaDB** | High-throughput web applications, read-heavy workloads, horizontal read-replica clusters. | Thread-per-connection MVCC via InnoDB. | Clustered primary key indexing, replication ecosystem, low connection overhead. | JSON capabilities less mature than PostgreSQL JSONB; DDL operations historically more prone to locking without careful flags. |
| **SQLite** | Embedded applications, desktop apps, mobile, CLI tools, low-to-medium traffic web APIs, edge nodes. | Single-file database, serverless, file-lock concurrency. | Zero deployment footprint, in-process zero-latency memory access, simple backups (single file). | Single writer limitation; lack of user permissions model; no network listener (unless using Litestream / LibSQL). |
| **NoSQL (Document / KV / Wide-Column)** | Unstructured schemaless documents, high-velocity append-only logs, distributed multi-region master writes. | Varies (DynamoDB, MongoDB, Redis, Cassandra). | Flexible schema, partition scalability across clusters. | Lack of ACID cross-document transactions (in most models), weak consistency trade-offs, lack of declarative JOINs. |

#### Decision Framework: SQL vs. NoSQL

- **Choose SQL (Relational) when**:
  - Data integrity, referential constraints, and relational relationships (1-to-many, many-to-many) are critical.
  - Transactions must guarantee strict ACID semantics across multiple entities (e-commerce, financial systems, identity).
  - Reporting, business intelligence, and ad-hoc query capabilities require complex JOINs and aggregations.
- **Choose NoSQL when**:
  - The access pattern is strictly key-value with sub-millisecond latency requirements (use Redis / KeyDB).
  - Data schema changes per record unpredictably, and documents are always retrieved and updated as complete self-contained units.
  - Write ingestion volume exceeds the vertical scaling limits of a single master relational instance, requiring native sharding.

---

### 2. Schema Design, Normalization, & Data Type Selection

#### 2.1 Normalization Forms

Apply normalization to eliminate data redundancy and prevent update/delete anomalies:

1. **First Normal Form (1NF)**:
   - Each column contains atomic (indivisible) values.
   - No repeating groups or comma-separated lists in a single field.
   - Each table must have a primary key identifying each row uniquely.
2. **Second Normal Form (2NF)**:
   - Must satisfy 1NF.
   - Every non-key attribute must depend fully on the complete primary key (relevant for composite primary keys).
3. **Third Normal Form (3NF)**:
   - Must satisfy 2NF.
   - No transitive dependencies: non-key attributes must depend *only* on the primary key, not on another non-key attribute.

```sql
-- Normalized 3NF Schema Example (PostgreSQL)

-- Lookup table (removes transitive dependency from users)
CREATE TABLE user_roles (
    id SMALLSERIAL PRIMARY KEY,
    name VARCHAR(32) NOT NULL UNIQUE
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id SMALLINT NOT NULL REFERENCES user_roles(id),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    total_amount NUMERIC(12, 2) NOT NULL CHECK (total_amount >= 0),
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE order_items (
    order_id BIGINT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    PRIMARY KEY (order_id, product_id)
);
```

#### 2.2 Strategic Denormalization

Denormalize selectively only when read performance profiling proves that joins and aggregations create severe I/O or CPU bottlenecks:
- **Precomputed Counters**: Store `comments_count` on `posts` updated via transactional triggers or application events.
- **Historical Snapshots**: Store `shipping_address_snapshot` as a JSONB or immutable text blob on `orders` to insulate historical records from future address modifications.
- **Materialized Views**: In PostgreSQL, use materialized views for heavy analytical queries that can tolerate cache lag:
  ```sql
  CREATE MATERIALIZED VIEW mv_daily_sales AS
  SELECT 
      DATE_TRUNC('day', created_at) AS sale_date,
      COUNT(id) AS total_orders,
      SUM(total_amount) AS revenue
  FROM orders
  WHERE status = 'completed'
  GROUP BY DATE_TRUNC('day', created_at);

  CREATE UNIQUE INDEX idx_mv_daily_sales_date ON mv_daily_sales (sale_date);

  -- Refresh without blocking reads:
  REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_sales;
  ```

#### 2.3 Strict Data Type Selection Rules

- **Primary Keys**:
  - Prefer **UUIDv7** (time-ordered UUIDs) or **BIGINT** / **BIGSERIAL** (64-bit integer). Avoid random UUIDv4 on high-write B-Tree clustered indexes because random values fragment B-tree index pages.
- **Monetary & Financial Data**:
  - Always use `NUMERIC(precision, scale)` or `DECIMAL(precision, scale)`. Never use `FLOAT` or `DOUBLE` due to IEEE-754 floating-point rounding errors.
- **Dates and Timestamps**:
  - Always use `TIMESTAMPTZ` (`TIMESTAMP WITH TIME ZONE`) in PostgreSQL.
  - Store UTC in MySQL (`DATETIME` or `TIMESTAMP`).
  - Store ISO-8601 text strings or Unix epoch integers in SQLite.
- **Strings**:
  - Use `TEXT` or `VARCHAR(n)` when bounds are known. Avoid arbitrary lengths like `VARCHAR(255)` unless specified by business rules or index prefix limits in older MySQL versions.
- **Enums vs Lookup Tables**:
  - Use database ENUMs (`CREATE TYPE status_enum AS ENUM (...)`) only for static, unchanging business values (e.g. days of week).
  - Use foreign-key lookup tables for values that may expand dynamically without requiring DDL alterations.

---

### 3. Indexing Architecture & Strategy

Indexes accelerate lookups at the cost of disk space and write amplification (every `INSERT`, `UPDATE`, and `DELETE` updates corresponding indexes).

#### 3.1 B-Tree Index Mechanics & The Leftmost Prefix Rule

Standard B-Tree indexes sort entries in a balanced tree. In a composite index `(col_a, col_b, col_c)`:
- Lookups can query `(col_a)`, `(col_a, col_b)`, or `(col_a, col_b, col_c)`.
- Lookups filtering *only* on `(col_b)` or `(col_c)` **cannot** use the index effectively.

```sql
-- Optimal composite index for: WHERE tenant_id = ? AND status = ? ORDER BY created_at DESC
CREATE INDEX idx_orders_tenant_status_created 
ON orders (tenant_id, status, created_at DESC);
```

#### 3.2 Covering Indexes (`INCLUDE` Clause)

Store additional payload columns directly in the leaf pages of the index to enable **Index Only Scans** without visiting the table heap.

```sql
-- PostgreSQL:
CREATE INDEX idx_users_email_covering 
ON users (email) 
INCLUDE (id, first_name, last_name);

-- Satisfied entirely from index leaf nodes:
SELECT id, first_name, last_name 
FROM users 
WHERE email = 'alex@example.com';
```

#### 3.3 Partial & Functional Indexes

```sql
-- Partial index: indexes only active records (reduces index size by ~90%)
CREATE INDEX idx_users_active_email 
ON users (email) 
WHERE deleted_at IS NULL;

-- Functional / Expression index: indexes transformed value
CREATE UNIQUE INDEX idx_users_normalized_email 
ON users (LOWER(email));
```

---

### 4. Transaction Management & ACID Guarantees

Every business mutation involving multiple state changes must execute inside an ACID transaction block:
- **Atomicity**: All statements succeed, or the entire transaction rolls back.
- **Consistency**: The database transitions only between valid states conforming to all schema constraints.
- **Isolation**: Concurrent transactions execute without corrupting each other's state.
- **Durability**: Committed data survives system crashes, power failures, or restarts.

#### 4.1 Transaction Isolation Levels

| Isolation Level | Dirty Read | Non-Repeatable Read | Phantom Read | Serialization Anomaly |
| :--- | :--- | :--- | :--- | :--- |
| **Read Uncommitted** | Allowed | Allowed | Allowed | Allowed |
| **Read Committed** (*PostgreSQL / MySQL Default*) | Prevented | Allowed | Allowed | Allowed |
| **Repeatable Read** | Prevented | Prevented | Prevented (in PG/InnoDB) | Allowed |
| **Serializable** | Prevented | Prevented | Prevented | Prevented |

#### 4.2 Concurrency Control Patterns

##### Pessimistic Locking (`SELECT ... FOR UPDATE`)
Locks matching rows until the current transaction commits or rolls back. Use when contention is high and mutations must serialize strictly.

```sql
BEGIN;

-- Lock the account row explicitly against concurrent writers
SELECT balance 
FROM bank_accounts 
WHERE id = 'ACC-101' 
FOR UPDATE;

UPDATE bank_accounts 
SET balance = balance - 150.00 
WHERE id = 'ACC-101';

INSERT INTO account_ledger (account_id, delta, reason) 
VALUES ('ACC-101', -150.00, 'withdrawal');

COMMIT;
```

> **Queue Processing Tip**: Use `FOR UPDATE SKIP LOCKED` to allow worker processes to consume tasks concurrently without locking contention:
> ```sql
> SELECT id, payload 
> FROM job_queue 
> WHERE status = 'pending' 
> ORDER BY priority DESC 
> LIMIT 1 
> FOR UPDATE SKIP LOCKED;
> ```

##### Optimistic Concurrency Control (OCC)
Does not lock rows; instead, verifies a `version` or `updated_at` column upon updating. Ideal for read-heavy workloads with low collision probability.

```sql
-- 1. Read row
SELECT id, title, content, version FROM articles WHERE id = 42;

-- 2. Update with version check in application
UPDATE articles 
SET 
    title = 'Updated Title', 
    content = 'New Body', 
    version = version + 1 
WHERE id = 42 AND version = 3;

-- If rows affected == 0, another process updated the record; abort or retry.
```

##### Deadlock Prevention Guidelines
- Always acquire locks on multiple tables in the **exact same alphabetical or deterministic order** across all transactions.
- Keep transaction lifecycles as brief as possible. Never perform external network HTTP calls or file I/O inside an active database transaction.

---

### 5. Zero-Downtime Migrations & Schema Evolution

To alter schemas in high-traffic production environments without downtime, follow the **Expand / Contract (Parallel Run)** pattern.

```
Step 1: Expand       -> Add new nullable column or table.
Step 2: Dual-Write   -> Application writes to both old and new columns.
Step 3: Backfill     -> Background worker backfills existing historical data in batches.
Step 4: Read Switch  -> Application switches reads to new column.
Step 5: Contract     -> Remove dual-write; drop old column or table in subsequent release.
```

#### 5.1 Safe DDL Operations

##### Adding Columns
- **PostgreSQL 11+**: `ALTER TABLE users ADD COLUMN bio TEXT DEFAULT NULL;` (instant metadata operation). Adding columns with non-null constant defaults is also instant in PG 11+.
- **MySQL 8.0+**: Use `ALGORITHM=INSTANT` where supported:
  ```sql
  ALTER TABLE users ADD COLUMN notification_preferences JSON NULL, ALGORITHM=INSTANT;
  ```

##### Creating Indexes Without Table Locks
Never run a standard `CREATE INDEX` on large production tables during peak traffic.

```sql
-- PostgreSQL: Non-blocking index creation
CREATE INDEX CONCURRENTLY idx_users_last_login ON users (last_login_at);

-- MySQL 8.0+: Non-blocking online DDL
ALTER TABLE users ADD INDEX idx_users_last_login (last_login_at), ALGORITHM=INPLACE, LOCK=NONE;
```

##### Renaming Columns Safely
Direct column renames break running application instances that still execute queries against the old column name.
1. Add new column with desired name.
2. Dual-write to both old and new column.
3. Backfill data.
4. Deploy code reading from new column.
5. Drop old column after deployment completes.

---

### 6. Advanced Query Construction

#### 6.1 JOIN Types & Execution Mechanics

```sql
-- Multi-table JOIN with LEFT JOIN for optional relations
SELECT 
    u.id AS user_id,
    u.email,
    p.avatar_url,
    COUNT(o.id) AS total_orders,
    COALESCE(SUM(o.total_amount), 0) AS lifetime_spend
FROM users u
INNER JOIN profiles p ON p.user_id = u.id
LEFT JOIN orders o ON o.user_id = u.id AND o.status = 'completed'
WHERE u.created_at >= '2026-01-01'
GROUP BY u.id, u.email, p.avatar_url
HAVING COUNT(o.id) > 0;
```

#### 6.2 Common Table Expressions (CTEs) & Recursive Hierarchies

Use CTEs for readable modular logic. Use recursive CTEs for hierarchical tree traversal (org charts, nested categories, threaded comments).

```sql
-- Recursive CTE: Category taxonomy tree
WITH RECURSIVE category_tree AS (
    -- Anchor member: root categories
    SELECT id, name, parent_id, 1 AS depth, ARRAY[id] AS path
    FROM categories
    WHERE parent_id IS NULL

    UNION ALL

    -- Recursive member: child categories
    SELECT c.id, c.name, c.parent_id, ct.depth + 1, ct.path || c.id
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT id, name, depth, path 
FROM category_tree 
ORDER BY path;
```

#### 6.3 Window Functions

Window functions compute values across sets of rows related to the current row without collapsing the result set like `GROUP BY`.

```sql
SELECT 
    id,
    department_id,
    salary,
    -- Rank salaries within department
    DENSE_RANK() OVER (
        PARTITION BY department_id 
        ORDER BY salary DESC
    ) AS salary_rank,
    -- Running cumulative salary total
    SUM(salary) OVER (
        PARTITION BY department_id 
        ORDER BY hired_at ASC 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_dept_salary,
    -- Difference from previous employee hire
    salary - LAG(salary, 1, salary) OVER (
        PARTITION BY department_id 
        ORDER BY hired_at ASC
    ) AS diff_from_prev_hire
FROM employees;
```

---

### 7. Engine-Specific Configuration & Tuning

#### 7.1 PostgreSQL Architecture & Tuning

PostgreSQL allocates a dedicated backend process for each client connection.

##### Key `postgresql.conf` Settings
```ini
# Memory Configuration (Assuming 16GB Dedicated RAM)
shared_buffers = 4GB                  # 25% of total system RAM
effective_cache_size = 12GB           # 75% of total system RAM
work_mem = 64MB                       # Memory per sort/hash operation (keep conservative)
maintenance_work_mem = 1GB            # Memory for vacuum, index creation
wal_buffers = 16MB

# Checkpoints & Write-Ahead Log (WAL)
checkpoint_completion_target = 0.9    # Smooth out disk I/O over checkpoint window
max_wal_size = 16GB
min_wal_size = 2GB

# Query Planner Cost Tuning (for NVMe SSD storage)
random_page_cost = 1.1                # Default 4.0 assumes spinning disks; 1.1 for SSDs
effective_io_concurrency = 200        # NVMe concurrent request capability
```

##### PostgreSQL JSONB Operations & Indexing
```sql
-- Querying JSONB documents
SELECT id, metadata->>'plan' AS subscription_plan
FROM customers
WHERE metadata @> '{"status": "active", "tier": "gold"}';

-- GIN indexing for high-speed key/value containment
CREATE INDEX idx_customers_metadata_gin ON customers USING GIN (metadata jsonb_path_ops);
```

##### Essential Extensions
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";       -- UUID generation functions
CREATE EXTENSION IF NOT EXISTS "pg_trgm";         -- Fuzzy and regex text search indexing
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements"; -- Query execution profiling
CREATE EXTENSION IF NOT EXISTS "vector";          -- Vector similarity search for AI/ML embeddings
```

---

#### 7.2 MySQL / MariaDB InnoDB Tuning

InnoDB uses a single multi-threaded process with a centralized memory buffer pool.

##### Key `my.cnf` Settings
```ini
[mysqld]
# Storage Engine
default_storage_engine = InnoDB

# Memory Configuration (Assuming 16GB Dedicated RAM)
innodb_buffer_pool_size = 12G        # 70-80% of total system RAM for dedicated MySQL
innodb_buffer_pool_instances = 8     # 1 instance per 1GB-2GB of buffer pool
innodb_log_buffer_size = 64M

# Redo Log / Durability Trade-offs
innodb_redo_log_capacity = 2G        # MySQL 8.0.30+ (or innodb_log_file_size = 1G)
innodb_flush_log_at_trx_commit = 1   # 1 = Full ACID compliance. 2 = Flush to OS cache every commit (faster, 1s data loss risk on OS crash)
innodb_flush_method = O_DIRECT       # Bypass OS page cache to avoid double-buffering

# Connection Limits
max_connections = 200                # Do not set to thousands; use connection pooler
thread_cache_size = 50
```

---

#### 7.3 SQLite Configuration & High-Concurrency Usage

SQLite is an in-process library. By default, it operates in rollback journal mode, locking the entire database during writes.

##### Essential Runtime PRAGMA Directives
Execute these directives on **every new SQLite connection**:

```sql
-- Enable Write-Ahead Logging: allows concurrent readers while a write occurs
PRAGMA journal_mode = WAL;

-- Relax disk syncs for huge write speedups while preserving durability against app crashes
PRAGMA synchronous = NORMAL;

-- Enforce foreign key constraints (disabled by default in SQLite for backwards compatibility!)
PRAGMA foreign_keys = ON;

-- Increase memory cache to 64MB (negative value specifies kilobytes)
PRAGMA cache_size = -64000;

-- Wait up to 5000ms for busy table locks before throwing SQLITE_BUSY error
PRAGMA busy_timeout = 5000;

-- Store temporary tables and indices in memory
PRAGMA temp_store = MEMORY;
```

---

### 8. Connection Pooling Architecture

Direct connection establishment incurs significant latency (TCP 3-way handshake, TLS exchange, authentication, backend process allocation). High connection counts exhaust server memory and increase context switching.

```
[ App Instances (100+ pods) ]
              │
              ▼  (thousands of ephemeral connections)
   [ Connection Pooler (PgBouncer / ProxySQL) ]
              │
              ▼  (small, optimal pool: e.g. 25-50 connections)
     [ Database Server ]
```

#### Pool Sizing Rule of Thumb
$$\text{max\_connections} \approx (\text{CPU Cores} \times 2) + \text{Disk Spindle Count}$$
A 16-core database server on NVMe storage achieves maximum query throughput with approximately **32 to 40 active database connections**.

#### Application-Level vs External Poolers
- **Application Poolers** (e.g. HikariCP in Java, `node-postgres` Pool, SQLAlchemy `QueuePool`): Pool connections within a single application process.
- **External Proxy Poolers** (PgBouncer for PostgreSQL, ProxySQL for MySQL): Pool connections centrally across hundreds of serverless functions, microservice pods, or container instances.

---

### 9. ORM Integration Patterns

Object-Relational Mappers (ORMs) provide productivity and type safety, but improper use causes severe performance defects.

#### 9.1 Eliminating the N+1 Query Problem

The N+1 problem occurs when an application executes 1 query to fetch parent records, and then executes $N$ additional queries to fetch children inside a loop.

##### TypeScript: Prisma
```typescript
// Anti-Pattern: N+1 queries
const users = await prisma.user.findMany();
for (const user of users) {
  const posts = await prisma.post.findMany({ where: { authorId: user.id } }); // N queries
}

// Optimized: Eager Loading (Single or Batched Join Query)
const usersWithPosts = await prisma.user.findMany({
  include: {
    posts: {
      select: { id: true, title: true, publishedAt: true },
      where: { published: true },
    },
  },
});
```

##### TypeScript: Drizzle ORM
```typescript
import { db } from './db';
import { users, posts } from './schema';
import { eq } from 'drizzle-orm';

// Type-safe join with precise column selection
const results = await db
  .select({
    userId: users.id,
    userName: users.name,
    postId: posts.id,
    postTitle: posts.title,
  })
  .from(users)
  .leftJoin(posts, eq(users.id, posts.authorId))
  .where(eq(users.status, 'active'));
```

##### PHP: Laravel Eloquent
```php
// Anti-Pattern: N+1 queries
$books = Book::all();
foreach ($books as $book) {
    echo $book->author->name; // 1 query per book
}

// Optimized: Eager Loading with constraints
$books = Book::with(['author:id,name', 'reviews' => function ($query) {
    $query->where('rating', '>=', 4);
}])->get();
```

##### Python: SQLAlchemy 2.0
```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Eager load relationships using selectinload to prevent N+1
stmt = (
    select(User)
    .options(selectinload(User.orders))
    .where(User.is_active == True)
)
users = session.scalars(stmt).all()
```

---

### 10. Database Security, Permissions, & Backup Operations

#### 10.1 SQL Injection Prevention

Never construct SQL statements using raw string concatenation or interpolation. Always use parameterized queries or prepared statements.

```typescript
// INSECURE: Vulnerable to SQL injection
const query = `SELECT * FROM users WHERE email = '${userInput}'`;

// SECURE: Parameterized placeholder
const query = `SELECT id, email, role FROM users WHERE email = $1`;
await client.query(query, [userInput]);
```

#### 10.2 Role-Based Access Control (RBAC) & Least Privilege

Never allow the runtime application to connect using the database superuser (`postgres` or `root`).

```sql
-- PostgreSQL: Create isolated application user with least privilege
CREATE ROLE app_runtime WITH LOGIN PASSWORD 'secure_random_password';

-- Grant connection to specific database
GRANT CONNECT ON DATABASE production_db TO app_runtime;

-- Grant usage on schema
GRANT USAGE ON SCHEMA public TO app_runtime;

-- Grant selective DML privileges (NO DDL: no ALTER, DROP, TRUNCATE)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_runtime;

-- Read-only role for reporting / analytics / read-replicas
CREATE ROLE app_readonly WITH LOGIN PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE production_db TO app_readonly;
GRANT USAGE ON SCHEMA public TO app_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;
```

#### 10.3 Encryption

- **In-Transit**: Enforce TLS 1.3 encryption on all connections (`sslmode=verify-full` in PostgreSQL, `ssl-mode=VERIFY_IDENTITY` in MySQL).
- **At-Rest**: Enable transparent disk encryption (LUKS, AWS EBS Encryption, GCP CMEK) and use column-level encryption for sensitive PII/secrets (e.g. `pgcrypto` with AES-256-GCM).

#### 10.4 Backup & Restore Strategies

##### Logical Backups
Export schema and data as portable SQL statements or custom archive formats.

```bash
# PostgreSQL: Consistent logical backup with directory format and parallel workers
pg_dump -h localhost -U postgres -d production_db -F c -b -v -f /backups/prod_$(date +%Y%m%d).dump

# PostgreSQL Restore:
pg_restore -h localhost -U postgres -d production_db_restore -v -j 4 /backups/prod_20260315.dump

# MySQL: Single-transaction consistent backup (non-blocking for InnoDB)
mysqldump -u root -p --single-transaction --quick --routines --triggers --databases production_db > /backups/mysql_prod_$(date +%Y%m%d).sql

# SQLite: Safe online live backup
sqlite3 app.db ".backup '/backups/sqlite_backup_$(date +%Y%m%d).db'"
```

##### Physical Backups & Point-In-Time Recovery (PITR)
For multi-terabyte databases, logical dumps take hours. Deploy physical continuous archiving:
- **PostgreSQL**: Continuous WAL (Write-Ahead Log) archiving via `pgBackRest` or `wal-g` with baseline base backups.
- **MySQL**: Physical non-blocking hot backups using Percona XtraBackup.

---

## Best Practices

- **Explicit Schema Constraints**: Define `NOT NULL`, `CHECK`, `UNIQUE`, and `FOREIGN KEY` constraints at the database level. Never rely solely on application-layer validation.
- **Order Composite Indexes by Selectivity**: Follow the ESR (Equality, Sort, Range) rule: place exact equality columns first, sorting columns second, and range inequality columns last.
- **Index Foreign Keys**: Relational engines do not automatically index foreign key columns (except MySQL InnoDB). Always add indexes on foreign keys in PostgreSQL and SQLite to prevent table scans during child lookups and cascade deletes.
- **Use UTC Everywhere**: Store all timestamps in UTC (`TIMESTAMPTZ`). Convert to local user timezones exclusively at the presentation layer.
- **Set Statement Timeouts**: Prevent runaway queries from consuming server resources indefinitely:
  ```sql
  -- PostgreSQL: Kill any query exceeding 5 seconds
  SET statement_timeout = '5000ms';
  ```
- **Bound All Pagination**: Always require an explicit `LIMIT` clause on user-facing list queries. Never allow unbounded `SELECT * FROM table`.
- **Monitor Autovacuum (PostgreSQL)**: Ensure autovacuum runs regularly on high-churn tables to prevent table bloat and transaction ID wraparound.

---

## Common Pitfalls

- **Using `SELECT *` in Production**: Fetches unused columns, wastes network bandwidth, breaks Index Only Scans, and can trigger out-of-memory errors on large text/BLOB columns.
- **Random UUIDv4 as Primary Key**: Causes severe B-Tree index fragmentation and high disk I/O on large tables. Use sequential `UUIDv7` or `BIGINT`.
- **Mixing Up `CHAR` and `VARCHAR`**: `CHAR(n)` pads with spaces up to $n$ characters, wasting storage and causing subtle string comparison bugs. Use `VARCHAR(n)` or `TEXT`.
- **Unindexed Soft Deletes (`deleted_at`)**: Adding `WHERE deleted_at IS NULL` to every query causes full table scans unless supported by a partial index (`CREATE INDEX ... WHERE deleted_at IS NULL`).
- **Implicit Type Coercion**: Comparing mismatched types (e.g. `WHERE varchar_column = 12345`) prevents the engine from using indexes because it casts the column on every row.
- **Long-Running Transactions**: Holding an open transaction while waiting on external APIs locks row resources, prevents vacuuming of dead tuples, and bloats WAL logs.
- **Missing Rollback Handling in Migrations**: Writing migration scripts without tested rollback instructions leaves databases in inconsistent states when migrations fail midway.

---

## Verification

Validate database schema health, index effectiveness, and configuration state with these diagnostic queries:

### 1. Unused Index Audit (PostgreSQL)
Identifies indexes consuming disk space and write I/O without being read:
```sql
SELECT 
    schemaname || '.' || relname AS table_name,
    indexrelname AS index_name,
    idx_scan AS number_of_scans,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexrelname NOT LIKE '%_pkey'
ORDER BY pg_relation_size(indexrelid) DESC;
```

### 2. Missing Indexes on Foreign Keys (PostgreSQL)
Finds child foreign keys lacking supporting indexes:
```sql
SELECT 
    c.conrelid::regclass AS table_name,
    a.attname AS foreign_key_column
FROM pg_constraint c
JOIN pg_attribute a ON a.attnum = ANY(c.conkey) AND a.attrelid = c.conrelid
WHERE c.contype = 'f'
  AND NOT EXISTS (
      SELECT 1 FROM pg_index i
      WHERE i.indrelid = c.conrelid
        AND a.attnum = ANY(i.indkey)
  );
```

### 3. Active Connection & Lock Contention Check (PostgreSQL)
```sql
SELECT 
    pid,
    usename,
    client_addr,
    state,
    wait_event_type,
    wait_event,
    NOW() - query_start AS query_duration,
    query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY query_duration DESC;
```

### 4. MySQL Processlist & Lock Inspection
```sql
SHOW FULL PROCESSLIST;

-- Check running InnoDB transactions and locks (MySQL 8.0+)
SELECT 
    r.trx_id waiting_trx_id,
    r.trx_mysql_thread_id waiting_thread,
    r.trx_query waiting_query,
    b.trx_id blocking_trx_id,
    b.trx_mysql_thread_id blocking_thread,
    b.trx_query blocking_query
FROM performance_schema.data_lock_waits w
JOIN information_schema.innodb_trx b ON b.trx_id = w.blocking_engine_transaction_id
JOIN information_schema.innodb_trx r ON r.trx_id = w.requesting_engine_transaction_id;
```

### 5. SQLite Integrity Check
```bash
sqlite3 app.db "PRAGMA quick_check;"
sqlite3 app.db "PRAGMA foreign_key_check;"
```

---

## Deep Dive Reference

For in-depth execution plan analysis (`EXPLAIN ANALYZE`), slow query logs, cursor pagination blueprints, bulk insertion optimizations, and PgBouncer/ProxySQL configurations:
- [Query Optimization & Performance Reference](references/query-optimization.md)
