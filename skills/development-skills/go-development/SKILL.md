---
name: go-development
description: >-
  Develop, test, and architect production-grade Go (Golang) applications and microservices. Covers standard project layouts, Go modules, concurrency primitives, net/http servers, table-driven testing, slog logging, database access, error wrapping, generics, and CLI tooling.
---

# Go (Golang) Development

A comprehensive guide for building high-performance, maintainable, and idiomatic Go applications and microservices. Go emphasizes simplicity, static typing, explicit error handling, and first-class concurrency.

## When to Use

- Initializing new Go microservices, APIs, CLI utilities, or background daemons.
- Structuring Go codebases according to standard layout conventions (`cmd/`, `internal/`, `pkg/`).
- Managing Go modules, dependency versioning, workspaces (`go work`), and vendoring.
- Implementing robust error handling with sentinel errors, wrapping (`%w`), `errors.Is`, and `errors.As`.
- Designing concurrent pipelines, worker pools, and mutex-protected state with proper `context.Context` lifecycle.
- Building HTTP REST APIs using standard library `net/http` (Go 1.22+ routing) or lightweight routers with middleware chains.
- Writing table-driven unit tests, benchmark tests, mocks with `testify`, and HTTP integration tests using `httptest`.
- Implementing structured logging using standard library `log/slog`, `zerolog`, or `zap`.
- Managing database access with `database/sql`, `pgx`, `sqlx`, or GORM with tuned connection pools and transactions.
- Parsing configuration using 12-factor environment loaders (`envconfig`, `viper`).
- Streamlining file I/O operations and buffered streaming using `os`, `io`, and `bufio`.
- Cross-compiling static binaries for Linux, macOS, or Windows using build tags and flags.

## Prerequisites

- **Go Compiler**: Go 1.21+ (Go 1.22+ strongly recommended for modern HTTP routing and loop variable semantics).
- **Static Analysis**: `golangci-lint` (v1.55+), `staticcheck`, and standard Go tools (`go vet`, `go fmt`).
- **Build Utilities**: `make` or task runners for automation.

---

## Steps

### 1. Initialize Go Modules and Standard Project Layout

Scaffold a project following standard Go project hierarchy. Keep non-exported business logic in `internal/` to prevent external imports.

```bash
# Initialize a new Go module
go mod init example.com/service

# Download dependencies and clean up unused requirements
go mod tidy

# Verify module dependencies and checksum integrity
go mod verify
```

Standard directory organization:

```text
├── cmd/
│   └── server/
│       └── main.go       # Application entrypoint (minimal wiring)
├── internal/             # Private application code (not importable by others)
│   ├── config/           # Environment and flag configuration
│   ├── domain/           # Core models and business interfaces
│   ├── handler/          # HTTP/gRPC transport handlers
│   ├── repository/       # Data storage implementations
│   └── service/          # Business logic and use cases
├── pkg/                  # Optional public libraries (safely importable externally)
├── api/                  # OpenAPI/Swagger specs, JSON schemas, Protobuf files
├── go.mod                # Module definitions and direct/indirect dependencies
├── go.sum                # Cryptographic checksums of dependencies
└── Makefile              # Build, test, and lint automation
```

Manage dependencies, vendoring, and local workspaces:

```bash
# Download dependencies into a vendor/ directory
go mod vendor

# Upgrade a specific dependency to latest patch/minor
go get -u github.com/google/uuid@latest

# Multi-module local development using Go workspaces
go work init ./service-a ./service-b
```

---

### 2. Model Domain with Types, Structs, and Interfaces

Favor composition over inheritance. Keep interfaces small and define them where they are consumed, not where they are implemented.

```go
package domain

import (
	"context"
	"time"
)

// User represents the domain model.
type User struct {
	ID        string    `json:"id"`
	Email     string    `json:"email"`
	Name      string    `json:"name"`
	CreatedAt time.Time `json:"created_at"`
}

// UserRepository defines the persistence contract required by business logic.
// Interfaces should be defined by the consumer.
type UserRepository interface {
	FindByID(ctx context.Context, id string) (*User, error)
	Create(ctx context.Context, user *User) error
}

// Struct embedding for composition (promotes fields and methods)
type AuditedEntity struct {
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
	CreatedBy string    `json:"created_by"`
}

type Order struct {
	AuditedEntity        // Embedded fields are promoted
	ID            string `json:"id"`
	TotalAmount   int64  `json:"total_amount"` // Represented in cents to avoid float inaccuracies
}
```

---

### 3. Implement Robust Error Handling

Never ignore errors. Always wrap errors with execution context using `fmt.Errorf` and `%w`. Use `errors.Is` for equality checking and `errors.As` for type assertions.

```go
package service

import (
	"errors"
	"fmt"
)

// Sentinel errors for known domain failure states
var (
	ErrNotFound      = errors.New("entity not found")
	ErrAlreadyExists = errors.New("entity already exists")
	ErrUnauthorized  = errors.New("unauthorized operation")
)

// Custom error type for detailed operational failures
type ValidationError struct {
	Field   string
	Message string
}

func (e *ValidationError) Error() string {
	return fmt.Sprintf("validation failed on field '%s': %s", e.Field, e.Message)
}

// Wrap errors with context
func (s *UserService) GetUser(id string) (*User, error) {
	if id == "" {
		return nil, &ValidationError{Field: "id", Message: "cannot be empty"}
	}

	user, err := s.repo.FindByID(id)
	if err != nil {
		if errors.Is(err, ErrNotFound) {
			return nil, fmt.Errorf("user lookup failed: %w", ErrNotFound)
		}
		// Wrap unexpected database or transport error with context
		return nil, fmt.Errorf("querying user by id %s: %w", id, err)
	}

	return user, nil
}

// Inspect errors at callers/handlers
func HandleError(err error) {
	if errors.Is(err, ErrNotFound) {
		// Respond 404
		return
	}

	var valErr *ValidationError
	if errors.As(err, &valErr) {
		// Respond 400 with field details
		_ = valErr.Field
		return
	}

	// Group multiple errors (Go 1.20+)
	// combinedErr := errors.Join(err1, err2)
}
```

---

### 4. Concurrency and Context Propagation

Always pass `context.Context` as the first argument in long-running or I/O-bound functions. Ensure all goroutines have a deterministic termination condition to prevent leaks.

```go
package worker

import (
	"context"
	"fmt"
	"sync"
	"time"
)

// ProcessBatch demonstrates bounded goroutine execution with context cancellation
func ProcessBatch(ctx context.Context, items []string, maxConcurrency int) error {
	sem := make(chan struct{}, maxConcurrency) // Counting semaphore
	errCh := make(chan error, len(items))
	var wg sync.WaitGroup

	for _, item := range items {
		// Stop scheduling if context is cancelled
		select {
		case <-ctx.Done():
			return ctx.Err()
		case sem <- struct{}{}: // Acquire slot
		}

		wg.Add(1)
		go func(val string) {
			defer wg.Done()
			defer func() { <-sem }() // Release slot

			if err := processItem(ctx, val); err != nil {
				select {
				case errCh <- err:
				default:
				}
			}
		}(item)
	}

	wg.Wait()
	close(errCh)

	if len(errCh) > 0 {
		return <-errCh
	}
	return nil
}

func processItem(ctx context.Context, val string) error {
	select {
	case <-ctx.Done():
		return ctx.Err()
	case <-time.After(50 * time.Millisecond):
		return nil
	}
}
```

Synchronize shared state with `sync.Mutex`, `sync.RWMutex`, or `sync.Once`:

```go
type SafeRegistry struct {
	mu    sync.RWMutex
	items map[string]string
	once  sync.Once
}

func (r *SafeRegistry) Init() {
	r.once.Do(func() {
		r.items = make(map[string]string)
	})
}

func (r *SafeRegistry) Get(key string) (string, bool) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	val, ok := r.items[key]
	return val, ok
}

func (r *SafeRegistry) Set(key, val string) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.items[key] = val
}
```

---

### 5. Build HTTP Services and Middleware

In Go 1.22+, `net/http.ServeMux` natively supports HTTP method matching and path parameters (e.g., `GET /api/v1/users/{id}`). Always configure server timeouts and handle graceful shutdown.

```go
package server

import (
	"context"
	"encoding/json"
	"errors"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"
)

// Middleware chaining helper
type Middleware func(http.Handler) http.Handler

func Chain(h http.Handler, middlewares ...Middleware) http.Handler {
	for i := len(middlewares) - 1; i >= 0; i-- {
		h = middlewares[i](h)
	}
	return h
}

func LoggingMiddleware(logger *slog.Logger) Middleware {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()
			next.ServeHTTP(w, r)
			logger.Info("handled request",
				slog.String("method", r.Method),
				slog.String("path", r.URL.Path),
				slog.Duration("duration", time.Since(start)),
			)
		})
	}
}

func SetupServer(logger *slog.Logger) *http.Server {
	mux := http.NewServeMux()

	// Go 1.22+ route pattern with method and path parameter
	mux.HandleFunc("GET /api/v1/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		_ = json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
	})

	mux.HandleFunc("GET /api/v1/users/{id}", func(w http.ResponseWriter, r *http.Request) {
		userID := r.PathValue("id") // Go 1.22+ path parameter extraction
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]string{"id": userID})
	})

	handler := Chain(mux, LoggingMiddleware(logger))

	return &http.Server{
		Addr:         ":8080",
		Handler:      handler,
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 10 * time.Second,
		IdleTimeout:  60 * time.Second,
	}
}

func RunWithGracefulShutdown(srv *http.Server, logger *slog.Logger) error {
	shutdownErr := make(chan error, 1)

	go func() {
		sigCh := make(chan os.Signal, 1)
		signal.Notify(sigCh, os.Interrupt, syscall.SIGTERM)
		<-sigCh

		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()

		logger.Info("shutting down HTTP server...")
		shutdownErr <- srv.Shutdown(ctx)
	}()

	logger.Info("starting server", slog.String("addr", srv.Addr))
	if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
		return err
	}

	return <-shutdownErr
}
```

---

### 6. JSON Marshaling and Struct Tags

Use struct tags for JSON mapping, omit empty values when appropriate, and configure decoders to reject unknown fields in strict APIs.

```go
package dto

import (
	"encoding/json"
	"fmt"
	"io"
	"time"
)

type UserRequest struct {
	Email    string `json:"email"`
	Name     string `json:"name"`
	Nickname string `json:"nickname,omitempty"` // Omitted if empty string
	Role     string `json:"role"`
}

// Strict decoding prevents silent injection of unknown JSON fields
func DecodeJSONStrict(r io.Reader, dst any) error {
	decoder := json.NewDecoder(r)
	decoder.DisallowUnknownFields()
	return decoder.Decode(dst)
}

// Custom marshaling for domain types (e.g., custom date formats)
type CustomDate struct {
	time.Time
}

const dateFormat = "2006-01-02"

func (d CustomDate) MarshalJSON() ([]byte, error) {
	return []byte(fmt.Sprintf("%q", d.Format(dateFormat))), nil
}

func (d *CustomDate) UnmarshalJSON(b []byte) error {
	str := string(b)
	str = str[1 : len(str)-1] // Remove quotes
	t, err := time.Parse(dateFormat, str)
	if err != nil {
		return err
	}
	d.Time = t
	return nil
}
```

---

### 7. Structured Logging (slog, zerolog, zap)

Go 1.21+ includes `log/slog` in the standard library. For ultra-high throughput or legacy stacks, `zerolog` and `zap` are standard alternatives.

```go
package telemetry

import (
	"log/slog"
	"os"
)

// Standard slog setup (Go 1.21+)
func InitSlog(isProduction bool) *slog.Logger {
	var handler slog.Handler
	opts := &slog.HandlerOptions{Level: slog.LevelInfo}

	if isProduction {
		handler = slog.NewJSONHandler(os.Stdout, opts)
	} else {
		opts.Level = slog.LevelDebug
		handler = slog.NewTextHandler(os.Stdout, opts)
	}

	logger := slog.New(handler)
	slog.SetDefault(logger)
	return logger
}

// Usage with contextual attributes
func LogOperation(logger *slog.Logger, traceID, userID string, count int) {
	logger.Info("job completed",
		slog.String("trace_id", traceID),
		slog.String("user_id", userID),
		slog.Int("count", count),
	)
}
```

Logging tool comparison:
- **`log/slog`**: Built into standard library, zero external dependencies, fast JSON and text handlers.
- **`rs/zerolog`**: Zero-allocation JSON logger, extremely fast, chaining syntax.
- **`uber-go/zap`**: Blazing fast structured logger with typed field constructors (`zap.String()`, `zap.Int()`).

---

### 8. Database Access (database/sql, pgx, sqlx, GORM)

Manage relational data access with connection pool tuning, parameterized queries, and transactional safety.

#### Connection Pooling with `database/sql` & `pgx`

```go
package db

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	_ "github.com/jackc/pgx/v5/stdlib" // pgx driver for database/sql
)

func NewPool(dsn string) (*sql.DB, error) {
	db, err := sql.Open("pgx", dsn)
	if err != nil {
		return nil, fmt.Errorf("opening db: %w", err)
	}

	// Always tune pool limits
	db.SetMaxOpenConns(25)
	db.SetMaxIdleConns(10)
	db.SetConnMaxLifetime(15 * time.Minute)
	db.SetConnMaxIdleTime(5 * time.Minute)

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := db.PingContext(ctx); err != nil {
		return nil, fmt.Errorf("ping db: %w", err)
	}
	return db, nil
}
```

#### Struct Scanning with `sqlx`

```go
// github.com/jmoiron/sqlx maps DB columns to structs automatically
type Product struct {
	ID    int64  `db:"id"`
	Name  string `db:"name"`
	Price int64  `db:"price"`
}

func GetProducts(ctx context.Context, db *sqlx.DB) ([]Product, error) {
	var products []Product
	err := db.SelectContext(ctx, &products, "SELECT id, name, price FROM products WHERE price > $1", 100)
	return products, err
}
```

#### ORM with `gorm.io/gorm`

```go
// GORM usage for rapid prototyping or simple relational mapping
type Account struct {
	ID        uint      `gorm:"primaryKey"`
	Email     string    `gorm:"uniqueIndex;not null"`
	CreatedAt time.Time
}

func CreateAccount(db *gorm.DB, email string) (*Account, error) {
	acc := &Account{Email: email}
	result := db.Create(acc)
	return acc, result.Error
}
```

---

### 9. Configuration Management (envconfig, viper)

Follow 12-factor principles by loading typed configurations from environment variables.

#### Struct-based Config with `kelseyhightower/envconfig`

```go
package config

import (
	"fmt"
	"time"

	"github.com/kelseyhightower/envconfig"
)

type Config struct {
	Port         int           `envconfig:"PORT" default:"8080"`
	DatabaseURL  string        `envconfig:"DATABASE_URL" required:"true"`
	Debug        bool          `envconfig:"DEBUG" default:"false"`
	ReadTimeout  time.Duration `envconfig:"READ_TIMEOUT" default:"5s"`
}

func Load() (*Config, error) {
	var cfg Config
	if err := envconfig.Process("APP", &cfg); err != nil {
		return nil, fmt.Errorf("parsing env config: %w", err)
	}
	return &cfg, nil
}
```

#### Multi-source Config with `spf13/viper`

```go
// viper loads from JSON/YAML files, flags, and environment variables
import "github.com/spf13/viper"

func LoadViperConfig() (*Config, error) {
	viper.SetConfigName("config")
	viper.SetConfigType("yaml")
	viper.AddConfigPath("./configs")
	viper.AutomaticEnv() // Read matching environment variables

	if err := viper.ReadInConfig(); err != nil {
		return nil, err
	}

	var cfg Config
	err := viper.Unmarshal(&cfg)
	return &cfg, err
}
```

---

### 10. Dependency Injection and Functional Options

Use constructor injection with interfaces to decouple components for testing. Use the Functional Options pattern for flexible, readable configuration.

```go
package server

import (
	"log/slog"
	"net/http"
	"time"
)

// Server configuration via functional options
type Server struct {
	addr         string
	timeout      time.Duration
	logger       *slog.Logger
	router       *http.ServeMux
}

type Option func(*Server)

func WithAddr(addr string) Option {
	return func(s *Server) {
		s.addr = addr
	}
}

func WithTimeout(d time.Duration) Option {
	return func(s *Server) {
		s.timeout = d
	}
}

func WithLogger(l *slog.Logger) Option {
	return func(s *Server) {
		s.logger = l
	}
}

// NewServer constructor using functional options
func NewServer(opts ...Option) *Server {
	srv := &Server{
		addr:    ":8080",
		timeout: 10 * time.Second,
		logger:  slog.Default(),
		router:  http.NewServeMux(),
	}

	for _, opt := range opts {
		opt(srv)
	}

	return srv
}
```

---

### 11. File I/O and the `os` Package

Handle files using streamed readers/writers to minimize memory consumption when processing large datasets.

```go
package fileio

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"path/filepath"
)

// ReadFileBuffered reads line-by-line without loading entire file into memory
func ReadFileBuffered(filePath string, onLine func(string) error) error {
	cleanPath := filepath.Clean(filePath)
	file, err := os.Open(cleanPath)
	if err != nil {
		return fmt.Errorf("opening file %s: %w", cleanPath, err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := scanner.Text()
		if err := onLine(line); err != nil {
			return err
		}
	}

	if err := scanner.Err(); err != nil {
		return fmt.Errorf("scanning file: %w", err)
	}
	return nil
}

// AtomicWriteFile writes content to a temp file and atomically renames it
func AtomicWriteFile(destPath string, data []byte, perm os.FileMode) error {
	dir := filepath.Dir(destPath)
	tmpFile, err := os.CreateTemp(dir, "temp-*.tmp")
	if err != nil {
		return fmt.Errorf("creating temp file: %w", err)
	}
	tmpName := tmpFile.Name()

	defer func() {
		_ = tmpFile.Close()
		_ = os.Remove(tmpName) // Clean up if rename didn't happen
	}()

	if _, err := tmpFile.Write(data); err != nil {
		return fmt.Errorf("writing data: %w", err)
	}

	if err := tmpFile.Chmod(perm); err != nil {
		return fmt.Errorf("setting permissions: %w", err)
	}

	if err := tmpFile.Close(); err != nil {
		return fmt.Errorf("closing temp file: %w", err)
	}

	return os.Rename(tmpName, destPath)
}
```

---

### 12. Generics (Go 1.18+)

Use Go generics for generic data structures, slice helpers, and collection utilities.

```go
package collections

// Filter returns slice elements matching predicate
func Filter[T any](slice []T, predicate func(T) bool) []T {
	result := make([]T, 0, len(slice))
	for _, v := range slice {
		if predicate(v) {
			result = append(result, v)
		}
	}
	return result
}

// Map transforms slice elements
func Map[T any, R any](slice []T, transform func(T) R) []R {
	result := make([]R, len(slice))
	for i, v := range slice {
		result[i] = transform(v)
	}
	return result
}

// Generic thread-safe Set using comparable constraint
type Set[T comparable] struct {
	items map[T]struct{}
}

func NewSet[T comparable]() *Set[T] {
	return &Set[T]{items: make(map[T]struct{})}
}

func (s *Set[T]) Add(val T) {
	s.items[val] = struct{}{}
}

func (s *Set[T]) Contains(val T) bool {
	_, exists := s.items[val]
	return exists
}
```

---

### 13. CLI Tools (flag and cobra)

For simple CLI scripts, use the standard library `flag` package. For enterprise CLI apps with subcommands and auto-documentation, use `github.com/spf13/cobra`.

#### Standard Library `flag`

```go
package main

import (
	"flag"
	"fmt"
	"os"
)

func runFlagCLI() {
	port := flag.Int("port", 8080, "server listening port")
	flag.Parse()

	if *port <= 0 || *port > 65535 {
		fmt.Fprintf(os.Stderr, "invalid port: %d\n", *port)
		os.Exit(1)
	}
}
```

#### Enterprise CLI with `spf13/cobra`

```go
package main

import (
	"fmt"
	"github.com/spf13/cobra"
	"os"
)

func main() {
	var verbose bool

	rootCmd := &cobra.Command{
		Use:   "app",
		Short: "Application CLI tool",
	}

	serveCmd := &cobra.Command{
		Use:   "serve",
		Short: "Run the API server",
		RunE: func(cmd *cobra.Command, args []string) error {
			fmt.Printf("Server starting (verbose=%v)\n", verbose)
			return nil
		},
	}

	serveCmd.Flags().BoolVarP(&verbose, "verbose", "v", false, "Enable verbose logging")
	rootCmd.AddCommand(serveCmd)

	if err := rootCmd.Execute(); err != nil {
		os.Exit(1)
	}
}
```

---

### 14. Testing and Benchmarking

Write table-driven tests, parallel subtests (`t.Parallel()`), HTTP handler tests with `httptest`, and assertions with `testify`.

```go
package service_test

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestValidateEmail(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name    string
		email   string
		wantErr bool
	}{
		{name: "valid standard email", email: "user@example.com", wantErr: false},
		{name: "empty email", email: "", wantErr: true},
		{name: "missing at-sign", email: "userexample.com", wantErr: true},
	}

	for _, tc := range tests {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()
			err := ValidateEmail(tc.email)
			if tc.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
			}
		})
	}
}

// HTTP handler testing with httptest
func TestHealthEndpoint(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	rr := httptest.NewRecorder()

	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{"status":"up"}`))
	})

	handler.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusOK, rr.Code)
	assert.JSONEq(t, `{"status":"up"}`, rr.Body.String())
}

// Benchmark testing
func BenchmarkEmailValidation(b *testing.B) {
	email := "bench.user@example.com"
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = ValidateEmail(email)
	}
}
```

---

### 15. Static Analysis, Quality Gates, and Compilation

Format code, enforce linter standards, and compile static, stripped binaries:

```bash
# 1. Format code check
test -z "$(gofmt -l .)"

# 2. Vet suspicious constructs
go vet ./...

# 3. Staticcheck analysis
staticcheck ./...

# 4. golangci-lint with all linters
golangci-lint run --timeout=5m ./...

# 5. Security vulnerability check
govulncheck ./...

# 6. Cross-compile static binary (Linux AMD64)
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
  -ldflags="-s -w -X main.version=1.0.0" \
  -o bin/server-linux-amd64 \
  ./cmd/server
```

Conditional compilation using build tags:

```go
//go:build linux && cgo

package platform

// Linux-specific CGO-dependent logic
```

---

## Best Practices

- **Accept Interfaces, Return Structs**: Functions should accept the smallest interface required for their job and return concrete structs.
- **Context is Always First**: Never store a `context.Context` inside a struct; pass it explicitly as the first argument: `func Do(ctx context.Context, ...)`.
- **Handle Errors Once**: Either log the error or return it up the call chain with contextual wrapping (`fmt.Errorf("...: %w", err)`). Never do both.
- **Explicit Nil Checks**: Check for `err != nil` immediately after calling a function that returns an error. Avoid nesting deep logic.
- **Deterministic Goroutine Lifecycles**: Every `go` routine must have an explicit exit trigger (channel close, context cancellation, or waitgroup decrement).
- **Close Resources Promptly**: Always check deferred resource closures when writing data (`f.Close()`), or handle error on write flush.
- **Zero Values Must Be Useful**: Design types so their zero value is ready for immediate use (e.g., `bytes.Buffer`, `sync.Mutex`).

---

## Common Pitfalls

- **Goroutine Leaks**: Launching goroutines that block forever waiting on a channel that nobody writes to or reads from.
- **Loop Variable Capture**: In Go versions prior to 1.22, variables declared in `for` loops were shared across iterations, causing goroutines to capture the final value. Always use Go 1.22+ or redeclare `val := val`.
- **Ignoring HTTP Response Body Close**: Failing to execute `defer resp.Body.Close()` and `io.Copy(io.Discard, resp.Body)`, causing connection reuse to fail and leaking TCP sockets.
- **Shadowing Variables with `:=`**: Accidental shadowing when assigning to an existing outer-scope variable inside an `if` block:
  ```go
  // PITFALL: Shadows err or user in outer scope
  if user, err := findUser(); err != nil { ... }
  ```
- **Copying Mutexes**: Passing structs containing `sync.Mutex` by value copies the lock state and causes deadlocks or race conditions. Always pass mutex-containing structs by pointer.
- **Data Races on Slices**: Appending to a shared slice from multiple goroutines without mutex protection causes memory corruption.

---

## Verification

To verify that a Go codebase adheres to quality and correctness standards, execute the following commands:

```bash
# 1. Format code check (exits non-zero if files are unformatted)
test -z "$(gofmt -l .)"

# 2. Run Go vet for compiler-level static analysis
go vet ./...

# 3. Run comprehensive linter
golangci-lint run ./...

# 4. Run tests with race detection and code coverage
go test -v -race -cover -count=1 ./...

# 5. Verify module consistency
go mod verify

# 6. Build production binary
CGO_ENABLED=0 go build -ldflags="-s -w" -o /dev/null ./cmd/...
```

Refer to [references/go-patterns.md](references/go-patterns.md) for concrete architectural patterns, worker pools, table-driven test templates, and Makefiles.
