# Shell Scripting Guidelines

> Verified: 2026-10-18, ShellCheck & POSIX / Bash Reference Manuals

## Script Safety & Options
- **Strict Mode**: In Bash scripts (`#!/usr/bin/env bash`), place `set -euo pipefail` at the top of the file to exit on errors, unset variables, and pipeline failures. In POSIX scripts (`#!/bin/sh`), use `set -eu`.
- **Variable Quoting**: Always quote variable expansions: `"$variable"` and `"${array[@]}"`. Unquoted expansions undergo word splitting and globbing.

## Conditionals & Portability
- **Test Syntax**: In Bash/Zsh scripts, prefer `[[ ... ]]` for string comparison and pattern matching. In portable POSIX `#!/bin/sh` scripts, use standard `[ ... ]` (`test`), as `[[` is a non-portable extension.
- **Cleanup**: Use `trap` to clean up temporary files, directories, and background processes upon script exit or interruption:
  ```bash
  scratch_dir=$(mktemp -d)
  trap 'rm -rf "$scratch_dir"' EXIT
  ```

## Verification
- Run ShellCheck: `shellcheck -x script.sh`
