# Bash Patterns and Reference Cheatsheet

This reference provides production-ready templates, common one-liners, systems automation patterns, and interactive CLI idioms for modern Bash scripting.

---

## 1. Production Script Template

Use this comprehensive template as the starting point for any standalone automation utility, deployment script, or background worker.

```bash
#!/usr/bin/env bash
# ==============================================================================
# Script:      task-runner.sh
# Description: Production-ready modular script template with strict mode,
#              signal cleanup, structured logging, and robust argument parsing.
# ==============================================================================

set -euo pipefail
IFS=$'\n\t'

# ------------------------------------------------------------------------------
# Global Constants and Environment
# ------------------------------------------------------------------------------
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
readonly SCRIPT_VERSION="1.0.0"

# Temporary Directory and State Management
readonly TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/${SCRIPT_NAME%.*}.XXXXXXXXXX")"

# ------------------------------------------------------------------------------
# Terminal Color Formatting & Logging
# ------------------------------------------------------------------------------
setup_colors() {
  if [[ -t 1 && -z "${NO_COLOR:-}" ]]; then
    C_RESET='\033[0m'
    C_RED='\033[0;31m'
    C_GREEN='\033[0;32m'
    C_YELLOW='\033[0;33m'
    C_BLUE='\033[0;34m'
    C_BOLD='\033[1m'
  else
    C_RESET=''
    C_RED=''
    C_GREEN=''
    C_YELLOW=''
    C_BLUE=''
    C_BOLD=''
  fi
}

log_info() {
  printf '%b[INFO]%b  %s: %s\n' "$C_BLUE" "$C_RESET" "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" "$*"
}

log_success() {
  printf '%b[OK]%b    %s: %s\n' "$C_GREEN" "$C_RESET" "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" "$*"
}

log_warn() {
  printf '%b[WARN]%b  %s: %s\n' "$C_YELLOW" "$C_RESET" "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" "$*" >&2
}

log_error() {
  printf '%b[ERROR]%b %s: %s\n' "$C_RED" "$C_RESET" "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" "$*" >&2
}

# ------------------------------------------------------------------------------
# Signal Handling and Cleanup
# ------------------------------------------------------------------------------
cleanup() {
  local exit_code=$?
  trap - EXIT INT TERM HUP ERR

  # Purge temporary workspace
  if [[ -d "$TMP_DIR" ]]; then
    rm -rf "$TMP_DIR"
  fi

  # Terminate active background processes spawned by this shell
  local -a active_jobs
  mapfile -t active_jobs < <(jobs -p)
  if (( ${#active_jobs[@]} > 0 )); then
    kill -TERM "${active_jobs[@]}" 2>/dev/null || true
  fi

  exit "$exit_code"
}

on_error() {
  local line_no="$1"
  local cmd="$2"
  log_error "Command '${cmd}' failed at line ${line_no}."
}

trap cleanup EXIT INT TERM HUP
trap 'on_error ${LINENO} "$BASH_COMMAND"' ERR

# ------------------------------------------------------------------------------
# CLI Help and Usage
# ------------------------------------------------------------------------------
show_help() {
  cat << EOF
${SCRIPT_NAME} v${SCRIPT_VERSION}

Usage: ${SCRIPT_NAME} [OPTIONS] <TARGET>

Arguments:
  TARGET                 Target environment, file, or hostname to process.

Options:
  -c, --config FILE      Path to custom configuration file.
  -n, --dry-run          Simulate execution without modifying state.
  -v, --verbose          Enable verbose debug output.
  -h, --help             Show this help screen and exit.
      --version          Show version information.

Examples:
  ${SCRIPT_NAME} --config config.env prod-server
  ${SCRIPT_NAME} --dry-run staging-server
EOF
}

# ------------------------------------------------------------------------------
# Argument Parsing
# ------------------------------------------------------------------------------
parse_args() {
  CONFIG_FILE=""
  DRY_RUN=false
  VERBOSE=false
  TARGET=""

  local positional_args=()

  while [[ $# -gt 0 ]]; do
    case "$1" in
      -c|--config)
        [[ -n "${2:-}" ]] || { log_error "Option '$1' requires a file argument."; exit 1; }
        CONFIG_FILE="$2"
        shift 2
        ;;
      --config=*)
        CONFIG_FILE="${1#*=}"
        shift
        ;;
      -n|--dry-run)
        DRY_RUN=true
        shift
        ;;
      -v|--verbose)
        VERBOSE=true
        shift
        ;;
      -h|--help)
        show_help
        exit 0
        ;;
      --version)
        printf '%s %s\n' "$SCRIPT_NAME" "$SCRIPT_VERSION"
        exit 0
        ;;
      --)
        shift
        positional_args+=("$@")
        break
        ;;
      -*)
        log_error "Unknown option: '$1'"
        show_help
        exit 1
        ;;
      *)
        positional_args+=("$1")
        shift
        ;;
    esac
  done

  if (( ${#positional_args[@]} < 1 )); then
    log_error "Missing required positional argument: <TARGET>"
    show_help
    exit 1
  fi

  TARGET="${positional_args[0]}"
}

# ------------------------------------------------------------------------------
# Business Logic
# ------------------------------------------------------------------------------
run_task() {
  log_info "Initializing execution for target: ${TARGET}"

  if [[ -n "$CONFIG_FILE" ]]; then
    if [[ ! -f "$CONFIG_FILE" ]]; then
      log_error "Config file not found: ${CONFIG_FILE}"
      return 1
    fi
    log_info "Loading configuration from: ${CONFIG_FILE}"
  fi

  if [[ "$DRY_RUN" == "true" ]]; then
    log_warn "Dry-run mode active. No changes will be made."
    return 0
  fi

  # Example work step
  local working_file="${TMP_DIR}/payload.txt"
  printf 'target=%s\ntimestamp=%s\n' "$TARGET" "$(date +%s)" > "$working_file"

  log_success "Processing completed successfully for: ${TARGET}"
}

# ------------------------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------------------------
main() {
  setup_colors
  parse_args "$@"

  if [[ "$VERBOSE" == "true" ]]; then
    set -x
  fi

  run_task
}

main "$@"
```

---

## 2. Common One-Liners Cheatsheet

### File and Directory Operations
```bash
# Find files larger than 100MB and sort by human-readable size
find . -type f -size +100M -exec ls -lh {} + | awk '{print $5, $9}' | sort -hr

# Recursively delete empty directories
find . -type d -empty -delete

# Find files modified within the last 24 hours
find /var/log -type f -mtime -1 -name "*.log"

# Batch calculate SHA256 checksums for all files in a directory
find . -maxdepth 1 -type f -print0 | xargs -0 sha256sum > checksums.sha256

# Verify SHA256 checksums
sha256sum --check checksums.sha256
```

### Text and Stream Processing
```bash
# Extract and sort unique visitor IPs from an Nginx access log
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -nr | head -n 20

# Strip empty lines and comment lines (# or //) from a configuration file
grep -vE '^[[:space:]]*($|#|//)' config.conf

# Extract values between two delimiters (e.g., [KEY=...])
sed -n 's/.*\[KEY=\([^]]*\)\].*/\1/p' audit.log

# Replace delimiter from comma to tab in a CSV
tr ',' '\t' < input.csv > output.tsv

# Convert multiple consecutive spaces or tabs into a single space
tr -s '[:blank:]' ' ' < input.txt
```

### Process and Port Inspection
```bash
# Check if a specific TCP port is listening (no netstat/lsof dependency)
timeout 1 bash -c '</dev/tcp/127.0.0.1/8080' && echo "Open" || echo "Closed"

# Find which PID is listening on port 8080
lsof -ti :8080 2>/dev/null || ss -tulpn | grep ':8080'

# List top 10 memory-consuming processes
ps aux --sort=-%mem | awk 'NR<=10 {printf "%-10s %-8s %-6s %s\n", $1, $2, $4, $11}'

# Gracefully terminate matching processes, with fallback to SIGKILL
pkill -TERM -f "worker-queue" || true
```

---

## 3. File Processing Patterns

### Pattern A: Atomic File Write
Prevents readers from observing half-written or corrupted files during network interruptions or abrupt terminations:

```bash
write_atomic_file() {
  local target_file="$1"
  local content="$2"
  local target_dir
  target_dir="$(dirname -- "$target_file")"

  # Write to temporary file on the SAME filesystem to guarantee atomic mv
  local tmp_file
  tmp_file="$(mktemp "${target_dir}/.tmp.XXXXXXXXXX")"

  printf '%s\n' "$content" > "$tmp_file"

  # Atomic replacement (atomic inode rename on POSIX filesystems)
  mv -f "$tmp_file" "$target_file"
}
```

### Pattern B: Safe File Modification with Automatic Backup and Rollback
Ensures that if an in-place modification crashes midway, the original file is fully restored:

```bash
safe_edit_file() {
  local target_file="${1:?Target file required}"
  local backup_file="${target_file}.bak.$(date +%s)"

  if [[ ! -f "$target_file" ]]; then
    printf 'Error: File %s not found.\n' "$target_file" >&2
    return 1
  fi

  # Create backup copy
  cp -p "$target_file" "$backup_file"

  # Perform changes using temporary file
  local tmp_file
  tmp_file="$(mktemp)"

  if sed 's/LOG_LEVEL=.*/LOG_LEVEL="debug"/' "$target_file" > "$tmp_file"; then
    mv -f "$tmp_file" "$target_file"
    rm -f "$backup_file"
    return 0
  else
    printf 'Error: Edit failed. Restoring from backup.\n' >&2
    mv -f "$backup_file" "$target_file"
    rm -f "$tmp_file"
    return 1
  fi
}
```

### Pattern C: Exclusive File Locking with `flock`
Guarantees that only one instance of a critical section runs at any time:

```bash
execute_with_lock() {
  local lock_file="/var/lock/app-sync.lock"
  local lock_fd=200

  # Open lock file on file descriptor 200
  exec 200>"$lock_file"

  # Non-blocking lock acquisition (-n)
  if ! flock -n 200; then
    printf 'Another instance is already running. Exiting.\n' >&2
    exit 1
  fi

  printf 'Lock acquired. Performing operations...\n'
  # Execute work...

  # Release lock and close descriptor
  flock -u 200
  exec 200>&-
}
```

---

## 4. Service Management Patterns (`systemctl`)

### Pattern A: Verify Unit Status Safely
```bash
check_service_health() {
  local unit_name="${1:?Service unit name required}"

  # Check if unit file exists
  if ! systemctl list-unit-files "${unit_name}.service" &>/dev/null; then
    printf 'Service %s does not exist on this host.\n' "$unit_name" >&2
    return 1
  fi

  # Check if active
  if systemctl is-active --quiet "$unit_name"; then
    printf 'Service %s is active and running.\n' "$unit_name"
  else
    printf 'Service %s is inactive or failed.\n' "$unit_name" >&2
    return 2
  fi
}
```

### Pattern B: Safe Restart with Healthcheck and Retry Loop
```bash
restart_service_with_verification() {
  local unit_name="${1:?Service unit name required}"
  local max_retries="${2:-15}"
  local wait_seconds="${3:-2}"

  printf 'Restarting service: %s\n' "$unit_name"
  systemctl restart "$unit_name"

  local attempt=1
  while (( attempt <= max_retries )); do
    if systemctl is-active --quiet "$unit_name"; then
      printf 'Service %s is healthy (attempt %d/%d).\n' "$unit_name" "$attempt" "$max_retries"
      return 0
    fi
    printf 'Waiting for %s to become healthy (%d/%d)...\n' "$unit_name" "$attempt" "$max_retries"
    sleep "$wait_seconds"
    ((attempt++))
  done

  printf 'Error: Service %s failed to enter active state after restart.\n' "$unit_name" >&2
  journalctl -u "$unit_name" -n 50 --no-pager >&2
  return 1
}
```

---

## 5. Cron Job and Scheduled Task Patterns

### Pattern A: Self-Locking Cron Job Wrapper
Cron jobs execute with minimal, unpredictable environments. Always define `PATH`, set working directories, and lock against overlap:

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1. Guarantee standard PATH
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# 2. Establish script directory
readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
cd "$SCRIPT_DIR"

# 3. Lock file path
readonly LOCK_FILE="/tmp/daily-sync.lock"

# 4. Execute wrapped inside flock
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  # Exit silently without error so cron does not send duplicate alarm emails
  exit 0
fi

# 5. Direct output to log file with timestamps
log_file="/var/log/cron-daily-sync.log"
exec >> >(awk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $0 }' >> "$log_file") 2>&1

printf 'Starting scheduled maintenance run.\n'
# Run actual task logic here...
printf 'Scheduled maintenance complete.\n'
```

### Pattern B: Failure Notification via Webhook
```bash
notify_on_failure() {
  local webhook_url="${ALERT_WEBHOOK_URL:-}"
  local script_name="${1:-$0}"
  local exit_code="$2"

  if [[ -n "$webhook_url" ]]; then
    curl -s -X POST -H "Content-Type: application/json" \
      --data "{\"text\":\"[ALERT] Cron job ${script_name} failed with exit code ${exit_code} on host $(hostname)\"}" \
      "$webhook_url" >/dev/null || true
  fi
}

trap 'notify_on_failure "$0" $?' ERR
```

---

## 6. Interactive Prompt Patterns

### Pattern A: Yes/No Confirmation (with Configurable Default)
```bash
confirm_action() {
  local prompt_msg="$1"
  local default_choice="${2:-N}" # "Y" or "N"
  local answer=""

  local prompt_suffix="[y/N]"
  if [[ "${default_choice^^}" == "Y" ]]; then
    prompt_suffix="[Y/n]"
  fi

  while true; do
    printf '%s %s: ' "$prompt_msg" "$prompt_suffix"
    read -r answer

    # If empty, fall back to default
    if [[ -z "$answer" ]]; then
      answer="$default_choice"
    fi

    case "${answer^^}" in
      Y|YES)
        return 0
        ;;
      N|NO)
        return 1
        ;;
      *)
        printf 'Invalid input. Please enter y or n.\n'
        ;;
    esac
  done
}

# Usage:
# if confirm_action "Do you want to proceed with deployment?" "N"; then
#   deploy
# fi
```

### Pattern B: Masked Password / Token Input
```bash
prompt_secret() {
  local prompt_label="$1"
  local secret=""
  local secret_confirm=""

  while true; do
    printf '%s: ' "$prompt_label"
    # -s disables echoing characters to terminal
    read -r -s secret
    printf '\n'

    if [[ -z "$secret" ]]; then
      printf 'Error: Value cannot be empty.\n' >&2
      continue
    fi

    printf 'Confirm %s: ' "$prompt_label"
    read -r -s secret_confirm
    printf '\n'

    if [[ "$secret" == "$secret_confirm" ]]; then
      break
    fi

    printf 'Values did not match. Please try again.\n' >&2
  done

  # Return via stdout
  printf '%s' "$secret"
}
```

### Pattern C: Menu Selection Prompt
```bash
select_environment() {
  local -a environments=("development" "staging" "production")
  local choice=""

  printf 'Available environments:\n'
  for i in "${!environments[@]}"; do
    printf '  [%d] %s\n' "$((i + 1))" "${environments[i]}"
  done

  while true; do
    printf 'Select environment [1-%d]: ' "${#environments[@]}"
    read -r choice

    if [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= ${#environments[@]} )); then
      local selected_env="${environments[$((choice - 1))]}"
      printf 'Selected: %s\n' "$selected_env"
      printf '%s' "$selected_env"
      return 0
    fi

    printf 'Invalid choice. Enter a number between 1 and %d.\n' "${#environments[@]}" >&2
  done
}
```

### Pattern D: Non-Interactive Automation Fallback
Ensure scripts capable of interactive execution also run cleanly in automated pipelines via `--yes` or `-y`:

```bash
ASSUME_YES=false

# In argument parsing:
# -y|--yes) ASSUME_YES=true ;;

safe_prompt() {
  local message="$1"
  if [[ "$ASSUME_YES" == "true" ]]; then
    return 0
  fi
  confirm_action "$message" "N"
}
```
