---
name: shell-scripting
description: >-
  Write, refactor, debug, and harden production-grade Bash and POSIX shell scripts.
  Use when creating automation scripts, deployment hooks, CLI utilities, system
  administration tools, data processing pipelines, or diagnosing shell errors and
  shellcheck warnings.
---

# Production Shell Scripting

Shell scripting is the backbone of systems automation, continuous integration, infrastructure orchestration, and CLI utility development. Writing robust shell scripts requires strict defensive programming: handling unintended word splitting, path globbing, unset variables, pipeline failures, signal interruption, and cross-platform portability quirks.

This skill provides comprehensive methodologies and patterns for creating resilient, secure, and maintainable Bash and POSIX-compliant shell scripts.

For concrete boilerplate templates, one-liners, systemctl/cron patterns, and interactive prompts, consult the companion guide in `references/bash-patterns.md`.

---

## When to Use

- Authoring new automation scripts, build scripts, deployment scripts, or cron jobs.
- Refactoring legacy shell scripts to improve reliability, error handling, or performance.
- Hardening scripts against edge cases (filenames with spaces/newlines, unexpected unbound variables, failed commands in pipelines).
- Resolving ShellCheck diagnostics and static analysis warnings.
- Implementing robust CLI argument parsing with flags, options, and help messages.
- Designing high-throughput text processing pipelines using standard UNIX utilities (`grep`, `sed`, `awk`, `cut`, `sort`, `uniq`).
- Managing background tasks, concurrency, subprocesses, and signal traps.

---

## Prerequisites

- **Shell Interpreters**:
  - `bash` (version 4.0+ recommended for associative arrays and modern syntax).
  - `/bin/sh` (POSIX-compliant shell such as `dash`, `ash`, or `bash` in POSIX mode) when targeting minimal container or embedded environments.
- **Static Analysis**:
  - `shellcheck` (install via `apt install shellcheck`, `apk add shellcheck`, `brew install shellcheck`, or equivalent).
- **Core Utilities**: Standard POSIX coreutils (`find`, `xargs`, `sed`, `awk`, `grep`, `sort`, `mktemp`, `flock`).

---

## Steps

### Step 1: Establish Shebang and Strict Execution Mode

Every shell script must declare its interpreter explicitly and enforce defensive execution flags at the very top.

#### 1. Interpreter Selection (Shebang)
- **Bash (Portable Path Lookup)**:
  ```bash
  #!/usr/bin/env bash
  ```
  *Use when*: Writing scripts that leverage Bash-specific features (arrays, `[[ ]]`, process substitution). `env` resolves `bash` across varied paths (`/bin/bash`, `/usr/local/bin/bash`, `/opt/homebrew/bin/bash`, or NixOS).
- **POSIX Shell (Minimal / Container Environments)**:
  ```bash
  #!/bin/sh
  ```
  *Use when*: Writing scripts that must run anywhere without dependencies, such as Alpine Linux (`ash`), Debian/Ubuntu `/bin/sh` (`dash`), or minimal embedded systems.
- **Fixed System Bash**:
  ```bash
  #!/bin/bash
  ```
  *Use when*: System execution environments guarantee `/bin/bash` and restrict environment variable path overrides for security reasons.

#### 2. Strict Execution Flags (`set -euo pipefail`)
At the start of every Bash script (immediately below the shebang and comments):

```bash
set -euo pipefail
IFS=$'\n\t'
```

| Flag | Name | Functionality |
| :--- | :--- | :--- |
| `-e` | `errexit` | Exits immediately if any command returns a non-zero exit status. |
| `-u` | `nounset` | Treats references to unset variables as errors and exits immediately. |
| `-o pipefail` | `pipefail` | Returns the exit code of the rightmost command in a pipeline that failed (non-zero), rather than only evaluating the very last command. |
| `IFS=$'\n\t'` | Field Separator | Prevents spaces from splitting words during loops and variable expansion, splitting only on newlines and tabs. |

> [!IMPORTANT]
> When `-u` is active, referencing an optional environment variable requires default parameter syntax: `"${OPTIONAL_VAR:-default_value}"`. Re-check any command expected to fail safely using `|| true` or within an `if` condition:
> ```bash
> # Permitted error without triggering -e
> grep "pattern" file.txt || true
> ```

---

### Step 2: Declare Variables, Arrays, and Parameter Expansion

#### 1. Variable Assignment and Immutability
Always define variables in lowercase for local/script scope to avoid colliding with exported shell environment variables (which are uppercase by convention). Use `readonly` or `declare -r` for constants:

```bash
readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
readonly TIMEOUT_SECONDS=30

app_name="log-processor"
target_port=8080
```

#### 2. Indexed Arrays (Bash 3.0+)
Indexed arrays hold ordered lists and protect elements containing spaces, newlines, and special characters:

```bash
# Declaration
declare -a servers=("web-01.internal" "web-02.internal" "cache-01.internal")

# Appending elements
servers+=("db-01.internal")

# Accessing individual elements
first_server="${servers[0]}"

# Accessing all elements (ALWAYS quote with [@])
for server in "${servers[@]}"; do
  printf 'Connecting to: %s\n' "$server"
done

# Array length
total_servers="${#servers[@]}"

# Slicing (${array[@]:offset:length})
subset=("${servers[@]:1:2}")
```

#### 3. Associative Arrays (Bash 4.0+)
Associative arrays store key-value mappings (dictionaries):

```bash
declare -A service_ports=(
  ["http"]="80"
  ["https"]="443"
  ["ssh"]="22"
)

# Adding or updating a key
service_ports["metrics"]="9090"

# Accessing a value
printf 'HTTPS Port: %s\n' "${service_ports["https"]}"

# Iterating over keys (${!array[@]})
for service in "${!service_ports[@]}"; do
  printf 'Service: %-10s Port: %s\n' "$service" "${service_ports[$service]}"
done

# Checking if key exists
if [[ -v service_ports["ssh"] ]]; then
  printf 'SSH configuration is present.\n'
fi
```

#### 4. Parameter Expansion Patterns
Avoid running external utilities (`basename`, `dirname`, `sed`, `cut`) for basic string transformations. Parameter expansion executes natively in memory:

```bash
filepath="/var/log/nginx/access.log"

# Default values
echo "${UNSET_VAR:-"default_value"}"       # Returns default if unset or null
echo "${UNSET_VAR:="assigned_default"}"    # Assigns default to var if unset or null
echo "${MANDATORY_VAR:?"Variable must be set!"}" # Errors and exits if unset

# Substring extraction: ${var:offset:length}
code="ERR_404_NOT_FOUND"
prefix="${code:0:3}"                       # "ERR"

# String length: ${#var}
len="${#filepath}"                         # 25

# Prefix stripping
filename="${filepath##*/}"                 # "access.log" (longest match from start)
dirpath="${filepath%/*}"                   # "/var/log/nginx" (shortest match from end)

# Suffix stripping
base="${filename%.*}"                      # "access" (shortest match from end)
extension="${filename##*.}"                # "log"

# Search and Replace
raw_path="/usr/local/bin:/usr/bin"
single_sub="${raw_path/usr/opt}"           # "/opt/local/bin:/usr/bin"
all_sub="${raw_path//usr/opt}"             # "/opt/local/bin:/opt/bin"

# Case modification (Bash 4.0+)
text="Hello World"
upper="${text^^}"                          # "HELLO WORLD"
lower="${text,,}"                          # "hello world"
```

---

### Step 3: Implement Structured Conditionals and Tests

#### 1. Modern Test Operator `[[ ... ]]` vs POSIX `[ ... ]`
In Bash scripts, always prefer `[[ ... ]]` over `[ ... ]`. `[[` is a shell keyword, preventing unintended glob expansion and word splitting inside the condition:

```bash
# Correct in Bash: No quoting errors even if $filename contains spaces
if [[ -f $filename && $filename == *.log ]]; then
  printf 'Processing log file: %s\n' "$filename"
fi

# Regex matching with =~ (do NOT quote the regex pattern)
version="2.14.0"
semver_regex='^[0-9]+\.[0-9]+\.[0-9]+$'
if [[ $version =~ $semver_regex ]]; then
  printf 'Valid semver: %s\n' "$version"
fi
```

#### 2. File and Type Tests
```bash
[[ -e "$path" ]]  # Exists (file, directory, socket, device, etc.)
[[ -f "$path" ]]  # Exists and is a regular file
[[ -d "$path" ]]  # Exists and is a directory
[[ -h "$path" ]]  # Exists and is a symbolic link
[[ -s "$path" ]]  # Exists and has size greater than zero
[[ -r "$path" ]]  # Exists and is readable by current process
[[ -w "$path" ]]  # Exists and is writable by current process
[[ -x "$path" ]]  # Exists and is executable by current process
```

#### 3. String and Integer Tests
```bash
# String tests
[[ -z "$str" ]]          # String is empty (zero length)
[[ -n "$str" ]]          # String is non-empty
[[ "$str1" == "$str2" ]] # Strings are equal (glob matching allowed)
[[ "$str1" != "$str2" ]] # Strings are not equal

# Integer tests (inside [[ ]])
[[ "$count" -eq 10 ]]    # Equal
[[ "$count" -ne 0 ]]     # Not equal
[[ "$count" -lt 5 ]]     # Less than
[[ "$count" -ge 1 ]]     # Greater than or equal

# Arithmetic Evaluation (( ... ))
if (( count > 10 && remaining <= 2 )); then
  printf 'Threshold reached: %d\n' "$count"
fi
```

#### 4. Multi-Branch Branching with `case`
Use `case` statements for clean matching against multiple patterns and wildcards:

```bash
case "$action" in
  start|boot)
    start_service
    ;;
  stop|shutdown)
    stop_service
    ;;
  restart|reload)
    stop_service
    start_service
    ;;
  status)
    check_status
    ;;
  *)
    printf 'Error: Unknown action "%s"\n' "$action" >&2
    exit 1
    ;;
esac
```

---

### Step 4: Construct Safe Loops and Iteration

#### 1. Iterating Over Files with Wildcards (Nullglob Safe)
Never parse `ls` output. Iterate using standard shell globbing. Always enable `nullglob` so unmatched patterns expand to nothing instead of the literal glob string:

```bash
shopt -s nullglob
files=(/var/log/nginx/*.log)
shopt -u nullglob

if (( ${#files[@]} == 0 )); then
  printf 'No log files found.\n'
else
  for file in "${files[@]}"; do
    printf 'Processing: %s\n' "$file"
  done
fi
```

#### 2. Reading Streams Line by Line
Use `while IFS= read -r line || [[ -n "$line" ]]; do` to read input cleanly.
- `IFS=` prevents stripping leading and trailing whitespace.
- `-r` prevents backslash escapes from being interpreted.
- `|| [[ -n "$line" ]]` ensures the final line is processed even if it lacks a trailing newline.

```bash
while IFS= read -r line || [[ -n "$line" ]]; do
  # Ignore empty lines and comment lines
  [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
  printf 'Entry: %s\n' "$line"
done < "/etc/hosts"
```

#### 3. Process Substitution vs Subshell Pipelines
Pipelines create subshells for each segment in Bash. Variables modified inside a piped loop do **not** persist in the parent shell:

```bash
# WRONG (Anti-Pattern): $total remains 0 outside the loop
total=0
cat numbers.txt | while read -r n; do
  total=$((total + n))
done
echo "Total: $total" # Prints 0!

# CORRECT: Process Substitution feeds input directly into loop
total=0
while IFS= read -r n; do
  total=$((total + n))
done < <(grep -E '^[0-9]+$' numbers.txt)
echo "Total: $total" # Prints accurate calculated sum
```

---

### Step 5: Structure Modular Functions

Functions in shell scripts should adhere to consistent scoping, clear contract boundaries, and standard exit codes.

```bash
# Function definition (POSIX syntax: name() { ... })
sync_directory() {
  local src_dir="${1:?Source directory required}"
  local dst_dir="${2:?Destination directory required}"
  local dry_run="${3:-false}"
  local exit_code=0

  if [[ ! -d "$src_dir" ]]; then
    printf 'Error: Source directory does not exist: %s\n' "$src_dir" >&2
    return 1
  fi

  mkdir -p "$dst_dir"

  local -a rsync_cmd=("rsync" "-avz" "--delete")
  if [[ "$dry_run" == "true" ]]; then
    rsync_cmd+=("--dry-run")
  fi

  "${rsync_cmd[@]}" "$src_dir/" "$dst_dir/" || exit_code=$?

  return "$exit_code"
}
```

#### Principles for Shell Functions:
1. **Always use `local`**: Declare all internal variables with `local` to prevent polluting global scope.
2. **Explicit Validation**: Use parameter expansion assertions (`${1:?error message}`) for required arguments.
3. **Stdout is for Data, Stderr is for Logs**: Return computed values or data via stdout (`printf '%s\n' "$val"`). Send logs, diagnostics, and errors to stderr (`>&2`).
4. **Exit Codes**: Functions return status via `return 0` (success) through `return 255`.

---

### Step 6: Parse Command-Line Arguments

Choose between `getopts` for short-option POSIX utilities or a custom `while` loop for modern tools supporting both short and long flags.

#### 1. Native `getopts` (Short Options)
```bash
parse_args() {
  local verbose=false
  local output_file=""
  local opt

  while getopts ":hvo:" opt; do
    case "$opt" in
      h)
        show_help
        exit 0
        ;;
      v)
        verbose=true
        ;;
      o)
        output_file="$OPTARG"
        ;;
      :)
        printf 'Error: Option -%s requires an argument.\n' "$OPTARG" >&2
        exit 1
        ;;
      \?)
        printf 'Error: Invalid option -%s.\n' "$OPTARG" >&2
        exit 1
        ;;
    esac
  done
  shift "$((OPTIND - 1))"

  # Remaining positional arguments are in "$@"
  local target="${1:-}"
}
```

#### 2. Hybrid Argument Parser (Supporting `--long` and `-s` Flags)
```bash
parse_cli() {
  local config_path=""
  local dry_run=false
  local positional_args=()

  while [[ $# -gt 0 ]]; do
    case "$1" in
      -c|--config)
        [[ -n "${2:-}" ]] || { printf 'Error: %s requires a value.\n' "$1" >&2; exit 1; }
        config_path="$2"
        shift 2
        ;;
      --config=*)
        config_path="${1#*=}"
        shift
        ;;
      -n|--dry-run)
        dry_run=true
        shift
        ;;
      -h|--help)
        print_usage
        exit 0
        ;;
      --) # End of all options
        shift
        positional_args+=("$@")
        break
        ;;
      -*)
        printf 'Error: Unknown option "%s"\n' "$1" >&2
        exit 1
        ;;
      *)
        positional_args+=("$1")
        shift
        ;;
    esac
  done

  # Restore positional arguments into $@
  set -- "${positional_args[@]:-}"
}
```

---

### Step 7: Manage Signals, Traps, and Graceful Cleanup

Scripts creating temporary directories, locks, background processes, or state files must reliably clean them up on exit, failure, or interruption.

```bash
# Setup isolated temporary working directory
readonly TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/script-task.XXXXXXXXXX")"

cleanup() {
  local exit_code=$?
  # Prevent recursive trap execution
  trap - EXIT INT TERM HUP

  # Remove temporary resources
  if [[ -d "$TMP_DIR" ]]; then
    rm -rf "$TMP_DIR"
  fi

  # Terminate any remaining child background jobs
  local -a pids
  mapfile -t pids < <(jobs -p)
  if (( ${#pids[@]} > 0 )); then
    kill -TERM "${pids[@]}" 2>/dev/null || true
  fi

  exit "$exit_code"
}

# Register traps across common termination conditions
trap cleanup EXIT INT TERM HUP
```

---

### Step 8: Orchestrate Processes, Concurrency, and I/O Redirection

#### 1. Background Jobs and Controlled Parallelism
```bash
run_parallel_tasks() {
  local -a pids=()
  local -a targets=("node-1" "node-2" "node-3" "node-4")

  for target in "${targets[@]}"; do
    (
      # Subshell execution
      printf 'Starting sync on %s\n' "$target"
      # Perform task...
      sleep 2
      printf 'Finished sync on %s\n' "$target"
    ) &
    pids+=("$!")
  done

  # Wait for all child processes and track failures
  local failed=0
  for pid in "${pids[@]}"; do
    if ! wait "$pid"; then
      ((failed++))
    fi
  done

  if (( failed > 0 )); then
    printf 'Error: %d parallel job(s) failed.\n' "$failed" >&2
    return 1
  fi
}
```

#### 2. Redirection Mechanics
```bash
# Redirect stdout and stderr to a file
command > output.log 2>&1
# Modern Bash shorthand:
command &> output.log

# Discard all output completely
command &> /dev/null

# Redirect stderr only
command 2> errors.log

# Here Documents (unexpanded with quoted EOF)
cat << 'EOF' > /etc/default/app
PORT=8080
LOG_LEVEL="info"
EOF

# Here Documents with variable expansion
cat << EOF > dynamic-config.json
{
  "host": "$HOSTNAME",
  "port": $target_port
}
EOF

# Here Strings (feed variable directly into stdin)
grep -q "ACTIVE" <<< "$status_response"
```

---

### Step 9: Process Text with Core UNIX Utilities

When pipelines demand high-performance text parsing, combine core tools with streaming semantics:

#### 1. `grep` Rules
- `-q`: Quiet mode (returns exit code 0 if match found, 1 if not; prints nothing).
- `-E`: Extended regular expressions (`+`, `?`, `|`, `()`).
- `-F`: Fixed strings (disables regex interpretation; faster and prevents escaping issues).
- `-v`: Invert match.
- `-o`: Print only matching parts.

```bash
# Check if user exists without generating output
if grep -q -F "deploy_user" /etc/passwd; then
  printf 'User already exists.\n'
fi
```

#### 2. `sed` Rules
Avoid macOS vs GNU `sed -i` incompatibilities by using portable temporary files or Perl/awk when editing in-place:

```bash
# Portable in-place replacement pattern:
replace_in_file() {
  local pattern="$1"
  local replacement="$2"
  local file="$3"
  local tmp_file
  tmp_file="$(mktemp)"

  sed "s|${pattern}|${replacement}|g" "$file" > "$tmp_file" && mv "$tmp_file" "$file"
}
```

#### 3. `awk` Rules
Use `awk` for tabular data, column manipulation, and arithmetic summation:

```bash
# Sum column 3 for rows matching "ERROR"
total_errors=$(awk '$2 == "ERROR" { sum += $3 } END { print sum + 0 }' audit.log)

# Extract users with UID >= 1000 from /etc/passwd
awk -F: '$3 >= 1000 && $3 != 65534 { print $1, $3, $7 }' /etc/passwd
```

#### 4. `find` and `xargs` Safe File Processing
Filenames can contain spaces, tabs, and newlines. Always terminate entries with NUL (`\0`):

```bash
# Find files older than 30 days and compress safely
find /var/log/app -type f -name "*.log" -mtime +30 -print0 | xargs -0 -r gzip -9

# Find and execute directly with find -exec
find /tmp/cache -type f -name "*.tmp" -delete
```

---

### Step 10: Implement Structured Logging and Output Formatting

Never use ambiguous `echo -e` across systems (behavior varies wildly between POSIX `sh`, Dash, GNU Bash, and BSD Bash). Use `printf`:

```bash
# Color definitions with NO_COLOR and TTY detection
setup_colors() {
  if [[ -t 1 && -z "${NO_COLOR:-}" ]]; then
    C_RESET='\033[0m'
    C_RED='\033[0;31m'
    C_GREEN='\033[0;32m'
    C_YELLOW='\033[0;33m'
    C_BLUE='\033[0;34m'
  else
    C_RESET=''
    C_RED=''
    C_GREEN=''
    C_YELLOW=''
    C_BLUE=''
  fi
}

log_info() {
  printf '%b[INFO]%b  %s %s\n' "$C_BLUE" "$C_RESET" "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" "$*"
}

log_warn() {
  printf '%b[WARN]%b  %s %s\n' "$C_YELLOW" "$C_RESET" "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" "$*" >&2
}

log_error() {
  printf '%b[ERROR]%b %s %s\n' "$C_RED" "$C_RESET" "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" "$*" >&2
}
```

---

### Step 11: Security Hardening & ShellCheck Verification

#### 1. Security Rules
- **Never use `eval`**: `eval` introduces arbitrary code execution vulnerabilities when handling dynamic or external data.
- **Always quote variables**: Prevent word splitting and command injection:
  ```bash
  # Vulnerable:
  rm -rf $DIR_PATH/*
  # Secure:
  rm -rf -- "${DIR_PATH:?Path unset}/"*
  ```
- **Restrict File Permissions**: Apply `umask 077` at initialization if the script writes sensitive data or keys.
- **Validate Input**: Check that inputs conform strictly to allowlists before executing operations.
- **Avoid hardcoding secrets**: Read credentials via environment variables or secret vaults.

#### 2. ShellCheck Integration
Run ShellCheck during development and in CI pipelines:

```bash
shellcheck -x -s bash my-script.sh
```

When an intentional deviation is required, document the suppression directly above the line with rationale:
```bash
# shellcheck disable=SC2034 # Variable is sourced and consumed by parent environment
EXPORTED_SETTING="active"
```

---

## Best Practices

| Category | Do | Don't |
| :--- | :--- | :--- |
| **Execution** | Use `set -euo pipefail` at script start. | Run scripts with permissive defaults where failures go unnoticed. |
| **Quoting** | Always double-quote variable expansions: `"$var"`, `"${array[@]}"`. | Leave variables bare: `$var`, `${array[*]}`. |
| **Testing** | Use `[[ ... ]]` in Bash and `(( ... ))` for arithmetic. | Use single brackets `[ ... ]` or `expr` in modern Bash. |
| **Command Lookup** | Check tool existence using `command -v binary &>/dev/null`. | Use `which binary` (unportable, depends on alias state). |
| **Looping** | Read lines with `while IFS= read -r line`. | Iterate lines with `for line in $(cat file)` (breaks on spaces/lines). |
| **Command Output** | Capture command output with `$(command)`. | Use legacy backticks `` `command` ``. |
| **Exit Status** | Check exit codes directly: `if my_cmd; then`. | Store and compare manually: `my_cmd; if [ $? -eq 0 ]; then`. |
| **Cleanup** | Clean resources deterministically using `trap cleanup EXIT`. | Rely on manual cleanup lines at the bottom of the script. |

---

## Common Pitfalls

- **The Subshell Variable Trap**: Piping into a `while` loop (`cat file | while read -r line; do ... done`) runs the loop in a child process. State modified inside the loop is lost upon completion. Use process substitution (`while ... done < <(command)`).
- **Unintended Globbing**: Running `rm "$DIR/*"` with double quotes will attempt to delete a literal asterisk file. The glob must remain unquoted: `rm -- "$DIR"/*`.
- **Incompatible `sed -i`**: `sed -i` on macOS requires an extension argument (`sed -i '' 's/a/b/'`), whereas GNU `sed` rejects that syntax (`sed -i 's/a/b/'`). Use a temporary file with `mktemp` and `mv` for portability.
- **Missing `pipefail`**: In `cmd1 | cmd2`, if `cmd1` crashes with exit code 137 (OOM) but `cmd2` succeeds, `$?` evaluates to 0 unless `set -o pipefail` is active.
- **Using `==` in POSIX `/bin/sh`**: POSIX shell `test` (`[ ... ]`) mandates `=` for string comparison; `==` is a Bash-specific extension and fails on strict Dash/Ash interpreters.

---

## Verification

To verify that a shell script is syntactically sound, portable, and hardened:

1. **Syntax Validation**:
   ```bash
   bash -n my-script.sh
   # Or for POSIX sh:
   sh -n my-script.sh
   ```
   *Expected output*: Zero output, return code `0`.

2. **Static Analysis with ShellCheck**:
   ```bash
   shellcheck -x -a -P . my-script.sh
   ```
   *Expected output*: No warnings, errors, or stylistic issues.

3. **Execution Trace Testing**:
   Execute with trace flags in a safe test environment:
   ```bash
   bash -x my-script.sh --dry-run
   ```
   *Expected output*: Step-by-step trace showing parameters correctly quoted without unexpected splitting.

4. **Exit-on-Error and Unset Variable Verification**:
   - Verify unbound variable protection: Pass an empty environment or invoke without required inputs; script must immediately terminate with a clear error.
   - Verify cleanup trap execution: Send `kill -INT $$` during a running test; temporary directories must be cleanly purged.
