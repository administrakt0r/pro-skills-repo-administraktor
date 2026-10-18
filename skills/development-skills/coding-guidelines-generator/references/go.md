# Go Guidelines

> Verified: 2026-10-18, Effective Go & Go Standard Library, applies to Go 1.21+ / 1.22 / 1.23

## Formatting & Code Style
- **Gofmt**: Code formatting must be produced strictly by `gofmt` or `goimports`. No competing style formatting rules.
- **Naming**: Avoid stuttering names (e.g. use `user.Service`, not `user.UserService`). Keep package names short, lowercase, and single-word.

## Error Handling & Flow
- **Error Propagation**: Return errors explicitly as the last return value. Check `if err != nil` immediately after each fallible call.
- **Error Wrapping**: When adding context to an error, wrap it using `%w` in `fmt.Errorf`:
  ```go
  if err != nil {
      return fmt.Errorf("reading configuration from %s: %w", configPath, err)
  }
  ```
- **No Panic in Libraries**: Never invoke `panic()` in packages or libraries intended for reuse. Reserve panics for unrecoverable startup initialization failures.

## Concurrency & Context
- **Context Propagation**: The first parameter of any function performing I/O, network calls, or long-running computation must be `ctx context.Context`. Respect cancellation via `ctx.Done()`.
- **Goroutine Lifecycles**: Never start a goroutine without a clear termination guarantee or cancellation signal to prevent goroutine leaks.

## Verification
- Format: `gofmt -s -w .`
- Tests: `go test -race ./...`
- Lint: `golangci-lint run`
