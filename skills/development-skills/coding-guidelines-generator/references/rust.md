# Rust Guidelines

> Verified: 2026-10-18, Rust Edition 2021 / 2024 Reference, applies to stable Rust 1.75+

## Error Handling & Idiomatic Rust
- **Result & Option**: Use `Result<T, E>` for fallible operations and propagate errors with the `?` operator. Avoid `.unwrap()` and `.expect()` in non-test production code unless the invariant is provably guaranteed by surrounding code, and document that invariant with a comment.
- **Custom Errors**: Implement `std::error::Error` for public error types (or use crates like `thiserror` for libraries and `anyhow` for applications).

## Unsafe Code & Concurrency
- **Unsafe Boundaries**: Every `unsafe` block must be preceded by an explanatory `// SAFETY:` comment explaining why the invariants cannot be violated.
- **Shared State**: Protect shared mutable state with `Arc<Mutex<T>>` or `Arc<RwLock<T>>`. Keep lock scopes as short as possible to prevent deadlocks.

## Tooling & Verification
- **Formatting**: `cargo fmt --check`
- **Clippy**: `cargo clippy --all-targets -- -D warnings`
- **Tests**: `cargo test`
- **Auditing**: Run `cargo audit` to detect known vulnerabilities in crate dependencies.
