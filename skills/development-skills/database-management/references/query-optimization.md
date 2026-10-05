# Database Query Optimization & Performance Reference

A comprehensive technical reference for diagnosing query bottlenecks, designing high-throughput indexes, rewriting inefficient SQL, architecting scalable pagination, performing bulk mutations, and sizing database connection pools.

---

## 1. Execution Plan Analysis (`EXPLAIN` & `EXPLAIN ANALYZE`)

Query execution plans reveal how the database optimizer intends to execute a query, including scan methods, join algorithms, estimated costs, and actual runtime metrics.

### 1.1 PostgreSQL Execution Plans

PostgreSQL provides deep visibility into execution metrics via the `EXPLAIN` command.

#### Basic Syntax and Recommended Options

```sql
-- Comprehensive execution analysis with buffer cache and timing
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, SETTINGS, WAL)
SELECT 
    o.id AS order_id,
    c.name AS customer_name,
    o.total_amount
FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE o.status = 'completed'
  AND o.created_at >= '2026-01-01'
ORDER BY o.total_amount DESC
LIMIT 50;
```

> **Warning**: `ANALYZE` executes the statement. For `INSERT`, `UPDATE`, or `DELETE`, wrap the statement in a transaction and roll it back:
> ```sql
> BEGIN;
> EXPLAIN ANALYZE DELETE FROM sessions WHERE expires_at < NOW();
> ROLLBACK;
> ```

#### Key PostgreSQL Plan Indicators

| Plan Node / Metric | Meaning | Optimization Action |
| :--- | :--- | :--- |
| **Seq Scan** | Sequential table scan. Reads every page in the table heap. | Acceptable on small tables (<1,000 rows). On large tables, investigate missing indexes or low predicate selectivity. |
| **Index Scan** | Traverses the B-tree index, then visits the heap page for every matching tuple. | Efficient for selective queries returning a small percentage of rows. |
| **Index Only Scan** | Retrieves all requested columns directly from the index without reading table heap pages. | Ideal. Requires index coverage (`INCLUDE` or composite index) and clean visibility map (`VACUUM`). |
| **Bitmap Index Scan + Bitmap Heap Scan** | Builds a bitmap of matching pages from the index, sorts by physical disk page, then visits heap. | Common when retrieving moderate percentages of rows or combining multiple indexes with `BitmapAnd`/`BitmapOr`. |
| **Nested Loop** | For each row in outer table, loops through inner table. | Optimal when outer relation is small and inner relation has an index lookup on join key. |
| **Hash Join** | Builds an in-memory hash table of inner relation, scans outer relation against it. | Optimal for large, unsorted datasets. If `Batches > 1`, `work_mem` is exceeded, spilling to temporary disk files. |
| **Merge Join** | Merges two sorted inputs along join keys. | Very fast if inputs are already sorted by indexes or previous steps. |
| **Buffers: shared hit vs read** | `hit` = read from RAM (`shared_buffers`). `read` = read from disk/OS cache. | High `read` indicates cold cache or excessive I/O. High `hit` on slow queries indicates inefficient filtering. |
| **Rows Removed by Filter** | Tuples fetched from disk/index that failed a secondary condition. | Indicates an index exists but does not cover all filter predicates. Composite index needed. |

#### Diagnosing Memory Spills in PostgreSQL

```text
Sort Method: external merge  Disk: 45056kB
```
- **Issue**: The sort operation exceeded allocated `work_mem`, forcing PostgreSQL to write intermediate sort batches to temporary disk files.
- **Fix**: Increase `work_mem` for the session or create an index that matches the `ORDER BY` column order:
  ```sql
  SET work_mem = '64MB';
  -- Or build an index matching the sort:
  CREATE INDEX idx_orders_amount ON orders (total_amount DESC);
  ```

---

### 1.2 MySQL & MariaDB Execution Plans

MySQL 8.0+ and MariaDB provide visual tree and JSON-formatted execution trees.

#### Syntax

```sql
-- Tree format (MySQL 8.0.16+)
EXPLAIN FORMAT=TREE
SELECT u.username, COUNT(p.id) AS post_count
FROM users u
LEFT JOIN posts p ON p.author_id = u.id AND p.is_published = 1
WHERE u.status = 'active'
GROUP BY u.id, u.username;

-- Execution profiling with real runtimes (MySQL 8.0.18+)
EXPLAIN ANALYZE
SELECT * FROM orders
WHERE customer_id = 4521 AND status = 'shipped'
ORDER BY order_date DESC LIMIT 10;
```

#### MySQL Access Types (`type` column) in Order of Best to Worst

1. **`system` / `const`**: 0 or 1 row matches (primary key or unique index equality).
2. **`eq_ref`**: One row read from this table for each combination from preceding table (primary key/unique join).
3. **`ref`**: Non-unique index lookup; all matching rows fetched.
4. **`fulltext`**: Full-text index search.
5. **`ref_or_null`**: Like `ref`, but searches for `NULL` values too.
6. **`index_merge`**: Combines multiple indexes (often indicates missing multi-column composite index).
7. **`range`**: Index range scan (uses operators: `=`, `<>`, `>`, `>=`, `<`, `<=`, `IS NULL`, `BETWEEN`, `IN()`).
8. **`index`**: Full index scan; traverses the entire index tree without heap scan (if covering) or with random lookups.
9. **`ALL`**: Full table scan. Scans the entire clustered index. Avoid on large production tables.

#### Critical MySQL `Extra` Flags

- **`Using index`**: Covering index; no clustered index / table lookup needed.
- **`Using index condition`**: Index Condition Pushdown (ICP); storage engine evaluates `WHERE` clauses directly on index records before reading table rows.
- **`Using filesort`**: MySQL must perform an extra pass to retrieve rows in sorted order (spills to disk if `sort_buffer_size` is exceeded).
- **`Using temporary`**: Creates an internal temporary table to resolve queries (common in `GROUP BY` or `DISTINCT` without appropriate indexes).

---

### 1.3 SQLite Execution Plans

SQLite exposes query plan mechanics via `EXPLAIN QUERY PLAN`.

```sql
EXPLAIN QUERY PLAN
SELECT item_id, SUM(quantity) 
FROM order_items 
WHERE order_id = 90210 
GROUP BY item_id;
```

#### Interpreting SQLite Plan Output

- `SCAN TABLE <table>`: Full table scan. High cost.
- `SEARCH TABLE <table> USING INDEX <index> (<column>=?)`: Point or range lookup using index. Highly efficient.
- `SEARCH TABLE <table> USING COVERING INDEX <index> (...)`: All query attributes satisfied by index alone.
- `USE TEMP B-TREE FOR ORDER BY / GROUP BY`: In-memory or temporary disk B-tree created to fulfill sorting or aggregation.

---

## 2. Slow Query Identification & Continuous Profiling

### 2.1 PostgreSQL: `pg_stat_statements`

`pg_stat_statements` aggregates execution statistics across all executed queries.

#### Configuration (`postgresql.conf`)

```ini
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.max = 10000
pg_stat_statements.track = all
log_min_duration_statement = 200 # Log any query taking longer than 200ms
```

Enable extension inside the database:
```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

#### Top Queries by Total Execution Time

```sql
SELECT 
    queryid,
    substring(query, 1, 100) AS short_query,
    calls,
    ROUND(total_exec_time::numeric, 2) AS total_time_ms,
    ROUND(mean_exec_time::numeric, 2) AS mean_time_ms,
    ROUND((100.0 * total_exec_time / SUM(total_exec_time) OVER())::numeric, 2) AS pct_total_time,
    shared_blks_hit,
    shared_blks_read
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

#### Top Queries by Buffer Cache Misses (I/O Heavy)

```sql
SELECT 
    substring(query, 1, 100) AS short_query,
    calls,
    shared_blks_read,
    shared_blks_hit,
    ROUND((100.0 * shared_blks_read / NULLIF(shared_blks_read + shared_blks_hit, 0))::numeric, 2) AS miss_pct
FROM pg_stat_statements
WHERE calls > 50
ORDER BY shared_blks_read DESC
LIMIT 10;
```

---

### 2.2 MySQL / MariaDB: Slow Query Log & Performance Schema

#### Enable Slow Query Log (`my.cnf`)

```ini
[mysqld]
slow_query_log = 1
slow_query_log_file = /var/log/mysql/mysql-slow.log
long_query_time = 0.2           # Log queries running longer than 200 milliseconds
log_queries_not_using_indexes = 1 # Flag queries executing full table scans
min_examined_row_limit = 100    # Ignore tiny tables
```

#### Querying Performance Schema (Zero Log File Parsing)

```sql
SELECT 
    DIGEST_TEXT AS query,
    COUNT_STAR AS exec_count,
    ROUND(SUM_TIMER_WAIT / 1000000000000, 3) AS total_time_sec,
    ROUND(AVG_TIMER_WAIT / 1000000000000, 3) AS avg_time_sec,
    SUM_ROWS_EXAMINED AS total_examined,
    SUM_ROWS_SENT AS total_sent,
    ROUND(SUM_ROWS_EXAMINED / NULLIF(SUM_ROWS_SENT, 0), 1) AS examine_to_sent_ratio
FROM performance_schema.events_statements_summary_by_digest
WHERE DIGEST_TEXT IS NOT NULL
ORDER BY SUM_TIMER_WAIT DESC
LIMIT 10;
```
> A high `examine_to_sent_ratio` (e.g. > 100) indicates the engine reads hundreds of rows for every 1 row returned, pointing to missing or inefficient indexes.

---

## 3. Index Optimization Patterns

### 3.1 The ESR Rule (Equality, Sort, Range) for Multi-Column Indexes

When building composite indexes for queries containing filtering and sorting, follow the **ESR Rule**:
1. **E (Equality)**: Columns tested with `=` or `IS NULL` come first.
2. **S (Sort)**: Columns used in `ORDER BY` come second (if ordering by single direction).
3. **R (Range)**: Columns tested with inequalities (`<`, `>`, `<=`, `>=`, `BETWEEN`, `LIKE 'prefix%'`) come last.

#### Example Scenario

```sql
SELECT id, account_id, amount, created_at
FROM transactions
WHERE account_id = 'ACC-8912'          -- Equality
  AND created_at >= '2026-01-01'       -- Range
ORDER BY created_at DESC;              -- Sort
```

- **Ineffective Index**: `(created_at, account_id)`: Forces index range scan on `created_at`, then filters each row by `account_id`.
- **Optimal Index**: `(account_id, created_at DESC)`: Jumps directly to `account_id`, then reads already-ordered records for the date range without filesort.

---

### 3.2 Covering Indexes & The `INCLUDE` Clause

A covering index contains all columns requested by a query, allowing the database to satisfy the query entirely from the index structure (Index Only Scan).

#### PostgreSQL Covering Index with `INCLUDE`

Keep non-search columns out of the B-tree search tree to maintain high branch fan-out and compact index size:

```sql
-- Search columns in index key, payload columns in INCLUDE
CREATE INDEX idx_users_lookup 
ON users (email) 
INCLUDE (id, first_name, last_name, role);

-- Satisfied entirely via Index Only Scan:
SELECT id, first_name, last_name, role
FROM users
WHERE email = 'user@example.com';
```

#### MySQL Clustered Index Awareness

In MySQL InnoDB, secondary indexes automatically append the primary key column(s) as row pointers.
If table has primary key `id`:
```sql
CREATE INDEX idx_users_email ON users (email);
-- In MySQL, this index physically stores (email, id).
-- Therefore, SELECT id FROM users WHERE email = '...' is automatically a covering index query.
```

---

### 3.3 Partial / Filtered Indexes

Index only rows that match a specific predicate to dramatically reduce index size, disk I/O, and write amplification.

```sql
-- PostgreSQL: Index only unhandled records
CREATE INDEX idx_jobs_pending 
ON background_jobs (priority, scheduled_at) 
WHERE status = 'pending';

-- Fast pickup query using partial index:
SELECT id, payload 
FROM background_jobs 
WHERE status = 'pending' 
ORDER BY priority DESC, scheduled_at ASC 
LIMIT 1;

-- Soft-delete filtering pattern (only active rows indexed):
CREATE INDEX idx_users_active_email 
ON users (email) 
WHERE deleted_at IS NULL;
```

---

### 3.4 Functional & Expression Indexes

Allows index lookups when predicates apply deterministic functions or cast expressions.

```sql
-- PostgreSQL: Case-insensitive unique search
CREATE UNIQUE INDEX idx_users_lower_email 
ON users (LOWER(email));

-- Query utilizing the expression index:
SELECT id FROM users WHERE LOWER(email) = LOWER('User@Example.COM');

-- PostgreSQL: JSONB field index
CREATE INDEX idx_events_customer_id 
ON audit_events (((payload->>'customer_id')::bigint));

SELECT * FROM audit_events WHERE (payload->>'customer_id')::bigint = 4521;
```

---

### 3.5 Specialized Index Types (GIN, GiST, BRIN)

#### GIN (Generalized Inverted Index) for PostgreSQL

Used for multi-value structures: JSONB, Arrays, and Full-Text Search.

```sql
-- GIN for JSONB containment (@>)
CREATE INDEX idx_users_metadata_gin ON users USING GIN (metadata jsonb_path_ops);

-- Accelerated query:
SELECT id FROM users WHERE metadata @> '{"tier": "enterprise", "country": "DE"}';

-- GIN with pg_trgm for arbitrary substring / regex matching
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_products_title_trgm ON products USING GIN (title gin_trgm_ops);

-- Handles leading wildcard searches efficiently:
SELECT id, title FROM products WHERE title LIKE '%mechanical keyboard%';
```

#### BRIN (Block Range Index) for Massive Time-Series Data

BRIN stores min/max values for ranges of physical disk pages (e.g. 128 pages per block).
Optimal for multi-gigabyte or terabyte tables where data is inserted in chronological order.

```sql
-- BRIN takes megabytes of RAM instead of gigabytes
CREATE INDEX idx_telemetry_timestamp_brin 
ON device_telemetry USING BRIN (recorded_at);

SELECT AVG(temperature) 
FROM device_telemetry 
WHERE recorded_at BETWEEN '2026-03-01' AND '2026-03-02';
```

---

## 4. Query Rewriting Patterns

### 4.1 Eliminating Correlated Subqueries

Correlated subqueries execute once for every candidate row in the outer query, leading to $O(N \times M)$ runtime complexity.

#### Anti-Pattern (Slow)
```sql
SELECT 
    c.id,
    c.name,
    (SELECT MAX(o.created_at) FROM orders o WHERE o.customer_id = c.id) AS last_order_date,
    (SELECT SUM(o.total_amount) FROM orders o WHERE o.customer_id = c.id) AS total_spent
FROM customers c
WHERE c.country = 'FR';
```

#### Optimized: Aggregated Join or CTE
```sql
SELECT 
    c.id,
    c.name,
    o_agg.last_order_date,
    COALESCE(o_agg.total_spent, 0) AS total_spent
FROM customers c
LEFT JOIN (
    SELECT 
        customer_id,
        MAX(created_at) AS last_order_date,
        SUM(total_amount) AS total_spent
    FROM orders
    GROUP BY customer_id
) o_agg ON o_agg.customer_id = c.id
WHERE c.country = 'FR';
```

---

### 4.2 Replacing `NOT IN` with `NOT EXISTS` or Anti-Join

When a subquery returns a single `NULL` value, `NOT IN` returns zero rows due to SQL three-valued logic (`NULL = value` evaluates to `UNKNOWN`). Additionally, optimizers struggle to index `NOT IN`.

#### Anti-Pattern
```sql
SELECT id, name 
FROM products 
WHERE id NOT IN (SELECT product_id FROM order_items WHERE product_id IS NOT NULL);
```

#### Optimized Pattern: `NOT EXISTS`
```sql
SELECT p.id, p.name 
FROM products p
WHERE NOT EXISTS (
    SELECT 1 
    FROM order_items oi 
    WHERE oi.product_id = p.id
);
```

#### Alternative Pattern: `LEFT JOIN` Anti-Join
```sql
SELECT p.id, p.name 
FROM products p
LEFT JOIN order_items oi ON oi.product_id = p.id
WHERE oi.product_id IS NULL;
```

---

### 4.3 Avoiding Function Wrapping on Indexed Columns (Sargability)

Non-sargable (Search Argument Able) predicates prevent the database from using B-tree range scans.

| Non-Sargable (Index Ignored) | Sargable Replacement (Uses Index) |
| :--- | :--- |
| `WHERE DATE(created_at) = '2026-03-15'` | `WHERE created_at >= '2026-03-15 00:00:00' AND created_at < '2026-03-16 00:00:00'` |
| `WHERE amount * 1.2 > 100` | `WHERE amount > 100 / 1.2` |
| `WHERE SUBSTRING(code, 1, 3) = 'XYZ'` | `WHERE code LIKE 'XYZ%'` |
| `WHERE COALESCE(status, 'new') = 'new'` | `WHERE status = 'new' OR status IS NULL` |

---

### 4.4 `UNION` vs `UNION ALL`

- `UNION` implicitly performs a deduplication sort (`Sort Unique` or `Hash Aggregate`) over the combined datasets.
- `UNION ALL` preserves rows and concatenates streams without sorting.

```sql
-- Inefficient: sorts millions of log records to find duplicates
SELECT event_id, payload FROM active_logs
UNION
SELECT event_id, payload FROM archived_logs;

-- Optimized: Zero sorting overhead
SELECT event_id, payload FROM active_logs
UNION ALL
SELECT event_id, payload FROM archived_logs;
```

---

### 4.5 Controlling CTE Materialization (PostgreSQL)

In PostgreSQL 12+, CTEs (`WITH` clauses) are inlined automatically unless materialized. You can force behavior explicitly:

```sql
-- Force CTE to inline (optimizer pushes down WHERE filters into the CTE)
WITH regional_sales AS NOT MATERIALIZED (
    SELECT region, product_id, SUM(amount) AS total
    FROM sales
    GROUP BY region, product_id
)
SELECT * FROM regional_sales WHERE region = 'EMEA';

-- Force CTE to evaluate once as an optimization fence (prevents repeated expensive calculations)
WITH expensive_stats AS MATERIALIZED (
    SELECT compute_heavy_metric(dept_id) AS metric, dept_id
    FROM departments
)
SELECT * FROM expensive_stats es1 JOIN expensive_stats es2 ON es1.metric = es2.metric;
```

---

## 5. High-Performance Pagination Patterns

### 5.1 The `OFFSET` Penalty

When executing `OFFSET 100000 LIMIT 20`, the database must read and traverse $100,020$ rows from the index or table heap, evaluate visibility, and discard the first $100,000$. Query response time degrades linearly: $O(N)$.

---

### 5.2 Keyset (Cursor-Based) Pagination

Keyset pagination uses deterministic columns (e.g. `(created_at, id)`) as a cursor to resume scanning directly at the required index leaf. Complexity remains constant: $O(1)$.

#### Implementation (PostgreSQL & MySQL 8+)

```sql
-- Initial Page Request (Page 1)
SELECT id, title, created_at
FROM articles
WHERE category_id = 4
ORDER BY created_at DESC, id DESC
LIMIT 20;

-- Client receives the last record: { id: 89412, created_at: '2026-03-10 14:22:10.123456' }
-- Subsequent Page Request (Page 2) using tuple comparison:
SELECT id, title, created_at
FROM articles
WHERE category_id = 4
  AND (created_at, id) < ('2026-03-10 14:22:10.123456', 89412)
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

Required supporting index:
```sql
CREATE INDEX idx_articles_cat_created_id 
ON articles (category_id, created_at DESC, id DESC);
```

#### Multi-Column Keyset without Row-Constructor Syntax (Universal)

If a database or driver does not support row comparisons `(col1, col2) < (val1, val2)`:
```sql
SELECT id, title, created_at
FROM articles
WHERE category_id = 4
  AND (
      created_at < '2026-03-10 14:22:10.123456'
      OR (created_at = '2026-03-10 14:22:10.123456' AND id < 89412)
  )
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

---

### 5.3 Deferred JOIN (Late Row Lookup) for Offset Requirements

When business requirements strictly mandate jump-to-page numerical offset pagination, use a deferred join. The offset traverses only compact index leaf nodes before joining table row data for the 20 rows needed.

#### Anti-Pattern: Scans 50,020 wide table rows
```sql
SELECT id, title, content, author_id, metadata, created_at
FROM articles
ORDER BY created_at DESC
LIMIT 20 OFFSET 50000;
```

#### Optimized Deferred JOIN
```sql
SELECT a.id, a.title, a.content, a.author_id, a.metadata, a.created_at
FROM articles a
JOIN (
    -- Subquery scans ONLY the compact index tree
    SELECT id
    FROM articles
    ORDER BY created_at DESC
    LIMIT 20 OFFSET 50000
) AS page_keys ON a.id = page_keys.id
ORDER BY a.created_at DESC;
```

---

## 6. Bulk Insert & Update Patterns

Executing thousands of individual `INSERT` or `UPDATE` statements incurs network round-trip latency, transaction logging overhead, and disk sync penalties.

### 6.1 Multi-Row Batch Inserts

Batch statements into chunks of 1,000 to 5,000 rows.

```sql
INSERT INTO sensor_readings (sensor_id, reading_value, recorded_at)
VALUES 
    (101, 23.4, '2026-03-15 10:00:00'),
    (102, 19.8, '2026-03-15 10:00:00'),
    (103, 44.1, '2026-03-15 10:00:01')
    -- up to ~2,000 parameters per statement
ON CONFLICT (sensor_id, recorded_at) 
DO UPDATE SET reading_value = EXCLUDED.reading_value;
```

---

### 6.2 Native Engine Bulk Loaders

For millions of records, use native protocol-level streaming.

#### PostgreSQL `COPY` Protocol
```bash
# Direct streaming via psql CLI
psql -d mydatabase -c "\COPY raw_events (event_id, source, payload, created_at) FROM 'events.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"
```

In application code (e.g. Node.js `pg-copy-streams`, Python `psycopg2.copy_expert`):
```python
import psycopg2

conn = psycopg2.connect("postgresql://user:pass@localhost:5432/mydb")
cur = conn.cursor()
with open("data.csv", "r") as f:
    cur.copy_expert("COPY transactions FROM STDIN WITH (FORMAT csv, HEADER true)", f)
conn.commit()
```

#### MySQL `LOAD DATA INFILE`
```sql
LOAD DATA LOCAL INFILE '/var/data/transactions.csv'
INTO TABLE transactions
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(transaction_id, account_id, amount, status, created_at);
```

---

### 6.3 Batch Updates via Temporary / Staging Tables

To update 500,000 rows without locking tables for minutes:

```sql
-- 1. Create temporary unlogged staging table
CREATE TEMP TABLE tmp_price_updates (
    sku VARCHAR(64) PRIMARY KEY,
    new_price NUMERIC(10, 2)
) ON COMMIT DROP;

-- 2. Bulk load data into staging table (zero WAL overhead)
COPY tmp_price_updates FROM '/tmp/prices.csv' WITH (FORMAT csv);

-- 3. Execute set-based join update
UPDATE products p
SET 
    price = u.new_price,
    updated_at = NOW()
FROM tmp_price_updates u
WHERE p.sku = u.sku;
```

---

### 6.4 PostgreSQL Batch UPDATE via `UNNEST`

Pass arrays of parameters in a single query to update hundreds of distinct rows with distinct values:

```sql
UPDATE products AS p
SET 
    price = v.price,
    stock = v.stock,
    updated_at = NOW()
FROM (
    SELECT 
        UNNEST($1::bigint[]) AS id,
        UNNEST($2::numeric[]) AS price,
        UNNEST($3::int[]) AS stock
) AS v
WHERE p.id = v.id;
```

---

## 7. Connection Pool & Resource Configuration

### 7.1 The Connection Sizing Formula

Configuring excessive database connections degrades performance due to context switching, thread contention, and memory consumption.

The standard sizing formula established by PostgreSQL performance benchmarks:

$$\text{pool\_size} = (\text{CPU Cores} \times 2) + \text{Effective Spindle Count}$$

- For a server with 8 CPU cores and SSD storage (effective spindle = 1 to 2):
  $$\text{pool\_size} = (8 \times 2) + 1 = 17 \text{ connections}$$
- Running 500 open backend server connections on a 4-core database server degrades throughput dramatically compared to 20 well-utilized connections.

---

### 7.2 Application-Level Pool Configuration Parameters

| Parameter | Recommended Production Value | Description |
| :--- | :--- | :--- |
| `max_connections` (Pool Size) | Match sizing formula divided by app instances | Maximum active connections allowed in the pool. |
| `min_idle` | 2 to 5 | Minimum idle connections kept warm. Avoid setting equal to max if traffic fluctuates. |
| `idle_timeout` | 10,000 to 30,000 ms (10-30s) | Time before unused idle connections are closed. |
| `max_lifetime` | 1,800,000 ms (30 min) | Maximum connection lifespan. Prevents memory leaks and handles cloud load-balancer drops. |
| `connection_timeout` | 3,000 to 5,000 ms (3-5s) | Fail fast if pool cannot vend a connection within threshold. |

---

### 7.3 Server-Side Connection Pooling: PgBouncer

When hundreds of microservice instances connect to PostgreSQL, use PgBouncer in front of the database.

#### Pool Modes

1. **Session Pooling**: Connection assigned to client until client disconnects. Works with all PostgreSQL features. Sizing capacity identical to direct connections.
2. **Transaction Pooling** (*Recommended*): Connection assigned to client only for the duration of a transaction block (`BEGIN` ... `COMMIT`). Releases connection to pool immediately upon commit.
   - *Limitation*: Prepared statements (`PREPARE`), `LISTEN`/`NOTIFY`, session variables (`SET LOCAL` must be used instead of `SET`), and temporary tables are not persistent across transactions.
3. **Statement Pooling**: Connection assigned for a single SQL statement. Disallows multi-statement transactions. Rarely used.

#### Sample `pgbouncer.ini` Configuration

```ini
[databases]
app_db = host=127.0.0.1 port=5432 dbname=app_db pool_size=25

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 5000
default_pool_size = 20
min_pool_size = 5
reserve_pool_size = 5
reserve_pool_timeout = 5
server_idle_timeout = 600
server_lifetime = 3600
server_reset_query = DISCARD ALL
ignore_startup_parameters = extra_float_digits, search_path
```

---

### 7.4 MySQL Connection Proxying: ProxySQL

ProxySQL provides transparent layer-7 connection routing, query caching, and multiplexing for MySQL.

```sql
-- Configure ProxySQL MySQL users and backend servers
INSERT INTO mysql_servers (hostgroup_id, hostname, port, max_connections) 
VALUES (0, '10.0.0.1', 3306, 100); -- Writer
INSERT INTO mysql_servers (hostgroup_id, hostname, port, max_connections) 
VALUES (1, '10.0.0.2', 3306, 200); -- Reader

-- Read/Write splitting rule
INSERT INTO mysql_query_rules (rule_id, active, match_pattern, destination_hostgroup, apply_pattern)
VALUES (1, 1, '^SELECT .* FOR UPDATE', 0, 1); -- Locks routed to writer

INSERT INTO mysql_query_rules (rule_id, active, match_pattern, destination_hostgroup, apply_pattern)
VALUES (2, 1, '^SELECT', 1, 1); -- Read queries routed to read replica hostgroup

LOAD MYSQL SERVERS TO RUNTIME;
SAVE MYSQL SERVERS TO DISK;
LOAD MYSQL QUERY RULES TO RUNTIME;
SAVE MYSQL QUERY RULES TO DISK;
```

---

## 8. Index Maintenance & Anti-Bloat Operations

### 8.1 PostgreSQL Index Bloat & Concurrent Reindexing

Frequent `UPDATE` and `DELETE` operations generate dead tuples that cause index bloat, degrading scan performance.

```sql
-- Check for index bloat via pgstattuple
CREATE EXTENSION IF NOT EXISTS pgstattuple;
SELECT * FROM pgstattuple('idx_orders_customer_id');

-- Rebuild index online without locking readers or writers
REINDEX INDEX CONCURRENTLY idx_orders_customer_id;

-- Rebuild all indexes on a table concurrently
REINDEX TABLE CONCURRENTLY orders;
```

### 8.2 MySQL InnoDB Index Optimization

In MySQL, deleted records in secondary B-trees leave sparse pages.

```sql
-- Rebuild table and defragment secondary indexes online
OPTIMIZE TABLE orders;

-- Check table fragmentation
SELECT 
    table_name, 
    ROUND(data_length / 1024 / 1024, 2) AS data_mb,
    ROUND(index_length / 1024 / 1024, 2) AS index_mb,
    ROUND(data_free / 1024 / 1024, 2) AS free_mb
FROM information_schema.tables
WHERE table_schema = 'production_db'
  AND data_free > 50 * 1024 * 1024;
```
