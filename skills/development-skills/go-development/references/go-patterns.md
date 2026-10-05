# Go Architectural Patterns and Reference Implementations

This document provides production-ready, reusable architectural patterns, concurrency templates, testing structures, and operational tooling for Go (Golang) applications.

---

## Table of Contents

1. [Standard Project Layout Example](#1-standard-project-layout-example)
2. [HTTP Handler Patterns with Middleware](#2-http-handler-patterns-with-middleware)
3. [Table-Driven Test Examples](#3-table-driven-test-examples)
4. [Concurrency Patterns](#4-concurrency-patterns)
   - [Worker Pool Pattern](#worker-pool-pattern)
   - [Fan-Out / Fan-In Pattern](#fan-out--fan-in-pattern)
   - [Pipeline Pattern](#pipeline-pattern)
5. [Error Handling Patterns](#5-error-handling-patterns)
6. [Repository & Service Layer Architecture](#6-repository--service-layer-architecture)
7. [Makefile for Go Projects](#7-makefile-for-go-projects)

---

## 1. Standard Project Layout Example

The standard Go directory layout separates concerns between executable binaries (`cmd/`), private implementation code (`internal/`), and reusable shared libraries (`pkg/`).

```text
service-root/
├── .github/
│   └── workflows/
│       └── ci.yml               # CI build and lint pipeline
├── api/
│   └── openapi.yaml             # API specifications and schemas
├── cmd/
│   ├── server/
│   │   └── main.go              # Primary HTTP/gRPC service entrypoint
│   └── migrate/
│       └── main.go              # Database migration CLI tool
├── internal/
│   ├── config/
│   │   └── config.go            # Environment configuration parser
│   ├── domain/
│   │   ├── user.go              # Domain entities, validation, repository interfaces
│   │   └── errors.go            # Domain-specific sentinel errors
│   ├── handler/
│   │   ├── http/
│   │   │   ├── handler.go       # HTTP routing, response encoding
│   │   │   ├── middleware.go    # Logging, recovery, authentication
│   │   │   └── user_handler.go  # Specific HTTP endpoint handlers
│   │   └── response.go          # Standard JSON response envelopes
│   ├── repository/
│   │   └── postgres/
│   │       ├── db.go            # database/sql connection pool initialization
│   │       └── user_repo.go     # PostgreSQL implementation of domain repository
│   └── service/
│       └── user_service.go      # Business logic orchestration
├── pkg/
│   └── validator/
│       └── validator.go         # Safe-to-export shared utility library
├── scripts/
│   └── setup.sh                 # Local developer setup scripts
├── .golangci.yml                # Linter configuration
├── Dockerfile                   # Multi-stage container build
├── Makefile                     # Build, lint, and test targets
├── go.mod                       # Module dependencies
└── go.sum                       # Dependency checksums
```

### Complete Entrypoint Example (`cmd/server/main.go`)

```go
package main

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"
)

func main() {
	// 1. Initialize structured logging
	logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelInfo,
	}))
	slog.SetDefault(logger)

	// 2. Load configuration
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	// 3. Setup router and middleware
	mux := http.NewServeMux()
	mux.HandleFunc("GET /healthz", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{"status":"up"}`))
	})

	server := &http.Server{
		Addr:         ":" + port,
		Handler:      mux,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	// 4. Graceful shutdown orchestration
	shutdownError := make(chan error, 1)

	go func() {
		quit := make(chan os.Signal, 1)
		signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
		s := <-quit

		logger.Info("shutting down server", slog.String("signal", s.String()))

		ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
		defer cancel()

		shutdownError <- server.Shutdown(ctx)
	}()

	logger.Info("server listening", slog.String("addr", server.Addr))

	if err := server.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
		logger.Error("server failed to start", slog.String("error", err.Error()))
		os.Exit(1)
	}

	if err := <-shutdownError; err != nil {
		logger.Error("server shutdown failed", slog.String("error", err.Error()))
		os.Exit(1)
	}

	logger.Info("server exited cleanly")
}
```

---

## 2. HTTP Handler Patterns with Middleware

The standard library `net/http` supports clean middleware chaining using standard types: `func(http.Handler) http.Handler`.

```go
package middleware

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log/slog"
	"net/http"
	"runtime/debug"
	"time"
)

// Middleware signature
type Middleware func(http.Handler) http.Handler

// Chain combines multiple middlewares sequentially
func Chain(h http.Handler, middlewares ...Middleware) http.Handler {
	for i := len(middlewares) - 1; i >= 0; i-- {
		h = middlewares[i](h)
	}
	return h
}

// Context key for request ID
type contextKey string

const RequestIDKey contextKey = "request_id"

// RequestID attaches a unique identifier to each request
func RequestID(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		reqID := r.Header.Get("X-Request-ID")
		if reqID == "" {
			b := make([]byte, 16)
			_, _ = rand.Read(b)
			reqID = hex.EncodeToString(b)
		}

		ctx := context.WithValue(r.Context(), RequestIDKey, reqID)
		w.Header().Set("X-Request-ID", reqID)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

// statusWriter captures HTTP status code and response size
type statusWriter struct {
	http.ResponseWriter
	status int
	bytes  int
}

func (w *statusWriter) WriteHeader(code int) {
	w.status = code
	w.ResponseWriter.WriteHeader(code)
}

func (w *statusWriter) Write(b []byte) (int, error) {
	if w.status == 0 {
		w.status = http.StatusOK
	}
	n, err := w.ResponseWriter.Write(b)
	w.bytes += n
	return n, err
}

// Logger logs each request with duration, status, and request ID
func Logger(logger *slog.Logger) Middleware {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()
			sw := &statusWriter{ResponseWriter: w}

			next.ServeHTTP(sw, r)

			reqID, _ := r.Context().Value(RequestIDKey).(string)
			logger.Info("http request",
				slog.String("request_id", reqID),
				slog.String("method", r.Method),
				slog.String("path", r.URL.Path),
				slog.Int("status", sw.status),
				slog.Int("bytes", sw.bytes),
				slog.Duration("duration", time.Since(start)),
			)
		})
	}
}

// Recoverer catches panics, logs the stack trace, and returns HTTP 500
func Recoverer(logger *slog.Logger) Middleware {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			defer func() {
				if rec := recover(); rec != nil {
					stack := string(debug.Stack())
					logger.Error("panic recovered",
						slog.Any("error", rec),
						slog.String("stack", stack),
					)

					w.Header().Set("Content-Type", "application/json")
					w.WriteHeader(http.StatusInternalServerError)
					_ = json.NewEncoder(w).Encode(map[string]string{
						"error": "internal server error",
					})
				}
			}()
			next.ServeHTTP(w, r)
		})
	}
}

// Standard JSON response helpers
func RenderJSON(w http.ResponseWriter, status int, data any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if err := json.NewEncoder(w).Encode(data); err != nil {
		slog.Error("failed to encode response", slog.String("error", err.Error()))
	}
}

func RenderError(w http.ResponseWriter, status int, message string) {
	RenderJSON(w, status, map[string]string{"error": message})
}
```

---

## 3. Table-Driven Test Examples

Table-driven tests are the standard idiom in Go. Use `t.Parallel()` inside subtests to catch data races and speed up execution.

```go
package service_test

import (
	"context"
	"errors"
	"testing"
)

// Subject under test
type InputValidator struct{}

func (v *InputValidator) ValidateUsername(username string) error {
	if len(username) < 3 {
		return errors.New("username too short: minimum 3 characters")
	}
	if len(username) > 20 {
		return errors.New("username too long: maximum 20 characters")
	}
	for _, ch := range username {
		if !((ch >= 'a' && ch <= 'z') || (ch >= '0' && ch <= '9') || ch == '_') {
			return errors.New("username contains invalid characters")
		}
	}
	return nil
}

func TestInputValidator_ValidateUsername(t *testing.T) {
	t.Parallel()

	validator := &InputValidator{}

	tests := []struct {
		name          string
		username      string
		wantErr       bool
		expectedError string
	}{
		{
			name:     "valid standard alphanumeric",
			username: "john_doe99",
			wantErr:  false,
		},
		{
			name:     "valid minimum boundary",
			username: "abc",
			wantErr:  false,
		},
		{
			name:          "too short",
			username:      "ab",
			wantErr:       true,
			expectedError: "username too short: minimum 3 characters",
		},
		{
			name:          "too long",
			username:      "this_username_is_way_too_long_for_system",
			wantErr:       true,
			expectedError: "username too long: maximum 20 characters",
		},
		{
			name:          "invalid special characters",
			username:      "invalid!user",
			wantErr:       true,
			expectedError: "username contains invalid characters",
		},
	}

	for _, tt := range tests {
		tt := tt // Explicit pin for parallel test safety
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()

			err := validator.ValidateUsername(tt.username)

			if (err != nil) != tt.wantErr {
				t.Fatalf("ValidateUsername(%q) error = %v, wantErr = %v", tt.username, err, tt.wantErr)
			}

			if tt.wantErr && err.Error() != tt.expectedError {
				t.Errorf("ValidateUsername(%q) error = %q, expectedError = %q", tt.username, err.Error(), tt.expectedError)
			}
		})
	}
}

// Mocking dependencies via interface implementation
type MockUserStore struct {
	FindByIDFn func(ctx context.Context, id string) (string, error)
}

func (m *MockUserStore) FindByID(ctx context.Context, id string) (string, error) {
	return m.FindByIDFn(ctx, id)
}

func TestUserService_WithMock(t *testing.T) {
	mockStore := &MockUserStore{
		FindByIDFn: func(ctx context.Context, id string) (string, error) {
			if id == "existing-123" {
				return "Alice", nil
			}
			return "", errors.New("user not found")
		},
	}

	name, err := mockStore.FindByID(context.Background(), "existing-123")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if name != "Alice" {
		t.Errorf("got %q, want 'Alice'", name)
	}
}
```

---

## 4. Concurrency Patterns

### Worker Pool Pattern

Maintains a fixed number of goroutines processing jobs from a channel, preventing resource exhaustion.

```go
package concurrency

import (
	"context"
	"fmt"
	"sync"
)

type Job struct {
	ID    int
	Input string
}

type Result struct {
	JobID  int
	Output string
	Err    error
}

// WorkerPool runs a fixed number of workers to process jobs concurrently
func RunWorkerPool(ctx context.Context, numWorkers int, jobs []Job) []Result {
	jobsCh := make(chan Job, len(jobs))
	resultsCh := make(chan Result, len(jobs))

	var wg sync.WaitGroup

	// Launch fixed number of workers
	for w := 1; w <= numWorkers; w++ {
		wg.Add(1)
		go func(workerID int) {
			defer wg.Done()
			for {
				select {
				case <-ctx.Done():
					return
				case job, ok := <-jobsCh:
					if !ok {
						return
					}
					// Execute work
					res := executeJob(ctx, job)
					resultsCh <- res
				}
			}
		}(w)
	}

	// Send jobs
	for _, job := range jobs {
		jobsCh <- job
	}
	close(jobsCh)

	// Wait for workers to finish, then close results channel
	go func() {
		wg.Wait()
		close(resultsCh)
	}()

	// Collect results
	var results []Result
	for res := range resultsCh {
		results = append(results, res)
	}

	return results
}

func executeJob(ctx context.Context, j Job) Result {
	if ctx.Err() != nil {
		return Result{JobID: j.ID, Err: ctx.Err()}
	}
	return Result{
		JobID:  j.ID,
		Output: fmt.Sprintf("processed:%s", j.Input),
	}
}
```

### Fan-Out / Fan-In Pattern

Splits execution across multiple worker channels (fan-out) and merges the outputs into a single stream (fan-in).

```go
package concurrency

import (
	"sync"
)

// FanIn merges multiple input channels into a single output channel
func FanIn[T any](done <-chan struct{}, channels ...<-chan T) <-chan T {
	out := make(chan T)
	var wg sync.WaitGroup

	multiplex := func(c <-chan T) {
		defer wg.Done()
		for val := range c {
			select {
			case out <- val:
			case <-done:
				return
			}
		}
	}

	wg.Add(len(channels))
	for _, c := range channels {
		go multiplex(c)
	}

	go func() {
		wg.Wait()
		close(out)
	}()

	return out
}
```

### Pipeline Pattern

Chains processing stages connected by channels. Cancellation signals propagate through `done` or `context.Context` to prevent goroutine leaks.

```go
package concurrency

import "context"

// Stage 1: Generator emits numbers
func Generator(ctx context.Context, nums ...int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for _, n := range nums {
			select {
			case <-ctx.Done():
				return
			case out <- n:
			}
		}
	}()
	return out
}

// Stage 2: Multiplier squares each number
func SquareStage(ctx context.Context, in <-chan int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for n := range in {
			select {
			case <-ctx.Done():
				return
			case out <- n * n:
			}
		}
	}()
	return out
}

// Stage 3: Consumer drains and accumulates
func DrainPipeline(ctx context.Context, in <-chan int) []int {
	var result []int
	for val := range in {
		result = append(result, val)
	}
	return result
}
```

---

## 5. Error Handling Patterns

Production-grade error handling combines sentinel errors, typed domain errors, wrapping, and error classification.

```go
package errpattern

import (
	"errors"
	"fmt"
	"net/http"
)

// Sentinel errors representing standard business failure modes
var (
	ErrNotFound     = errors.New("resource not found")
	ErrConflict     = errors.New("resource already exists")
	ErrInvalidInput = errors.New("invalid input data")
	ErrUnauthorized = errors.New("unauthorized")
)

// DomainError carries structured HTTP status and caller-safe messages
type DomainError struct {
	Code    string `json:"code"`
	Message string `json:"message"`
	Err     error  `json:"-"` // Underlying cause (not exposed to client)
}

func (e *DomainError) Error() string {
	if e.Err != nil {
		return fmt.Sprintf("%s: %v", e.Message, e.Err)
	}
	return e.Message
}

// Unwrap enables errors.Is and errors.As traversal
func (e *DomainError) Unwrap() error {
	return e.Err
}

// NewDomainError constructs a classified domain error
func NewDomainError(code, message string, underlying error) *DomainError {
	return &DomainError{
		Code:    code,
		Message: message,
		Err:     underlying,
	}
}

// MapErrorToHTTP maps domain errors to appropriate HTTP status codes
func MapErrorToHTTP(err error) (int, string) {
	if err == nil {
		return http.StatusOK, ""
	}

	// 1. Check for specific typed domain errors
	var domErr *DomainError
	if errors.As(err, &domErr) {
		switch domErr.Code {
		case "INVALID_ARGUMENT":
			return http.StatusBadRequest, domErr.Message
		case "NOT_FOUND":
			return http.StatusNotFound, domErr.Message
		}
	}

	// 2. Check for wrapped sentinel errors
	if errors.Is(err, ErrNotFound) {
		return http.StatusNotFound, "requested item was not found"
	}
	if errors.Is(err, ErrConflict) {
		return http.StatusConflict, "resource conflict occurred"
	}
	if errors.Is(err, ErrUnauthorized) {
		return http.StatusUnauthorized, "authentication required"
	}

	// 3. Fallback to generic internal server error (never leak raw DB/system errors)
	return http.StatusInternalServerError, "an unexpected internal error occurred"
}
```

---

## 6. Repository & Service Layer Architecture

This pattern separates domain logic, database operations, and transport handling using interfaces and dependency injection.

```go
package architecture

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"time"
)

// --- Domain Models ---

type Customer struct {
	ID        string    `json:"id"`
	Email     string    `json:"email"`
	Name      string    `json:"name"`
	CreatedAt time.Time `json:"created_at"`
}

type CreateCustomerParams struct {
	Email string
	Name  string
}

// --- Repository Contract (Defined by Consumer) ---

type CustomerRepository interface {
	GetByID(ctx context.Context, id string) (*Customer, error)
	GetByEmail(ctx context.Context, email string) (*Customer, error)
	Create(ctx context.Context, customer *Customer) error
}

// --- Service Layer (Business Logic) ---

type CustomerService struct {
	repo CustomerRepository
}

func NewCustomerService(repo CustomerRepository) *CustomerService {
	return &CustomerService{repo: repo}
}

func (s *CustomerService) Register(ctx context.Context, params CreateCustomerParams) (*Customer, error) {
	if params.Email == "" {
		return nil, errors.New("email is required")
	}

	// Check if already exists
	existing, err := s.repo.GetByEmail(ctx, params.Email)
	if err == nil && existing != nil {
		return nil, fmt.Errorf("customer registration: %w", ErrConflict)
	}

	customer := &Customer{
		ID:        fmt.Sprintf("cust_%d", time.Now().UnixNano()),
		Email:     params.Email,
		Name:      params.Name,
		CreatedAt: time.Now().UTC(),
	}

	if err := s.repo.Create(ctx, customer); err != nil {
		return nil, fmt.Errorf("creating customer record: %w", err)
	}

	return customer, nil
}

// --- PostgreSQL Repository Implementation ---

type PostgresCustomerRepository struct {
	db *sql.DB
}

func NewPostgresCustomerRepository(db *sql.DB) *PostgresCustomerRepository {
	return &PostgresCustomerRepository{db: db}
}

func (r *PostgresCustomerRepository) GetByID(ctx context.Context, id string) (*Customer, error) {
	query := `SELECT id, email, name, created_at FROM customers WHERE id = $1`
	row := r.db.QueryRowContext(ctx, query, id)

	var c Customer
	if err := row.Scan(&c.ID, &c.Email, &c.Name, &c.CreatedAt); err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, ErrNotFound
		}
		return nil, fmt.Errorf("scanning customer: %w", err)
	}
	return &c, nil
}

func (r *PostgresCustomerRepository) GetByEmail(ctx context.Context, email string) (*Customer, error) {
	query := `SELECT id, email, name, created_at FROM customers WHERE email = $1`
	row := r.db.QueryRowContext(ctx, query, email)

	var c Customer
	if err := row.Scan(&c.ID, &c.Email, &c.Name, &c.CreatedAt); err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, ErrNotFound
		}
		return nil, fmt.Errorf("scanning customer by email: %w", err)
	}
	return &c, nil
}

func (r *PostgresCustomerRepository) Create(ctx context.Context, c *Customer) error {
	query := `
		INSERT INTO customers (id, email, name, created_at)
		VALUES ($1, $2, $3, $4)
	`
	_, err := r.db.ExecContext(ctx, query, c.ID, c.Email, c.Name, c.CreatedAt)
	if err != nil {
		return fmt.Errorf("inserting customer: %w", err)
	}
	return nil
}
```

---

## 7. Makefile for Go Projects

A production-ready Makefile providing standardized targets for testing, linting, race detection, cross-compilation, and coverage reports.

```makefile
.DEFAULT_GOAL := help

# Build configuration variables
BINARY_NAME   ?= app
MAIN_PACKAGE  ?= ./cmd/server
BIN_DIR       ?= bin
GO_FILES      = $(shell find . -type f -name '*.go' -not -path './vendor/*')

# Version metadata
VERSION       ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
COMMIT        ?= $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")
BUILD_TIME    ?= $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

# Compiler flags: strip debugging symbols (-s -w) and embed metadata
LDFLAGS       = -s -w \
                -X 'main.Version=$(VERSION)' \
                -X 'main.GitCommit=$(COMMIT)' \
                -X 'main.BuildTime=$(BUILD_TIME)'

.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: tidy
tidy: ## Ensure modules are tidy and verified
	go mod tidy
	go mod verify

.PHONY: fmt
fmt: ## Format Go source files
	gofmt -s -w $(GO_FILES)

.PHONY: vet
vet: ## Run go vet static analysis
	go vet ./...

.PHONY: lint
lint: ## Run golangci-lint
	golangci-lint run --timeout=5m ./...

.PHONY: test
test: ## Run unit tests
	go test -v -count=1 ./...

.PHONY: test-race
test-race: ## Run tests with the Go race detector enabled
	go test -v -race -count=1 ./...

.PHONY: test-coverage
test-coverage: ## Run tests and generate HTML coverage report
	@mkdir -p $(BIN_DIR)
	go test -coverprofile=$(BIN_DIR)/coverage.out ./...
	go tool cover -html=$(BIN_DIR)/coverage.out -o $(BIN_DIR)/coverage.html
	@echo "Coverage report saved to $(BIN_DIR)/coverage.html"

.PHONY: build
build: tidy ## Build binary for host platform
	@mkdir -p $(BIN_DIR)
	CGO_ENABLED=0 go build -ldflags="$(LDFLAGS)" -o $(BIN_DIR)/$(BINARY_NAME) $(MAIN_PACKAGE)
	@echo "Binary built: $(BIN_DIR)/$(BINARY_NAME)"

.PHONY: run
run: ## Run the service locally
	go run $(MAIN_PACKAGE)

.PHONY: clean
clean: ## Remove compiled binaries and test reports
	rm -rf $(BIN_DIR)

.PHONY: cross-compile
cross-compile: ## Cross-compile static binaries for multiple OS/architectures
	@mkdir -p $(BIN_DIR)
	# Linux AMD64
	CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -ldflags="$(LDFLAGS)" -o $(BIN_DIR)/$(BINARY_NAME)-linux-amd64 $(MAIN_PACKAGE)
	# Linux ARM64
	CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -ldflags="$(LDFLAGS)" -o $(BIN_DIR)/$(BINARY_NAME)-linux-arm64 $(MAIN_PACKAGE)
	# Darwin (macOS) ARM64
	CGO_ENABLED=0 GOOS=darwin GOARCH=arm64 go build -ldflags="$(LDFLAGS)" -o $(BIN_DIR)/$(BINARY_NAME)-darwin-arm64 $(MAIN_PACKAGE)
	# Windows AMD64
	CGO_ENABLED=0 GOOS=windows GOARCH=amd64 go build -ldflags="$(LDFLAGS)" -o $(BIN_DIR)/$(BINARY_NAME)-windows-amd64.exe $(MAIN_PACKAGE)
	@echo "Cross-compilation complete."
```
