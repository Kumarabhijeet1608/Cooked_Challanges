#!/usr/bin/env bash
# -------------------------------------------------------------------
# run-test.sh — shared test runner for GitHub Classroom autograding
#
# Usage:
#   bash .github/scripts/run-test.sh smoke        # build app, verify HTTP 200
#   bash .github/scripts/run-test.sh vuln 1       # run solves/vuln1.* or vuln1_*.* and check flag
# -------------------------------------------------------------------
set -euo pipefail

APP_URL="http://localhost"
SOLVES_DIR="solves"
FLAGS_FILE="$SOLVES_DIR/flags.txt"

# ---------------------------------------------------------------
# detect_stack: find which template directory exists
# ---------------------------------------------------------------
detect_stack() {
  for dir in flask; do
    if [ -d "$dir" ] && [ -f "$dir/docker-compose.yml" ]; then
      echo "$dir"
      return 0
    fi
  done
  echo "ERROR: No flask/ directory with docker-compose.yml found" >&2
  return 1
}

# ---------------------------------------------------------------
# smoke: build the app and verify it responds with HTTP 200
# ---------------------------------------------------------------
cmd_smoke() {
  local stack
  stack=$(detect_stack)
  echo "Detected stack: $stack"

  echo "Building and starting app..."
  docker compose -f "$stack/docker-compose.yml" up --build -d

  echo "Waiting for app to become healthy (up to 120s)..."
  local retries=24
  local delay=5
  for i in $(seq 1 $retries); do
    if curl -sf -o /dev/null "$APP_URL"; then
      echo "App is up (attempt $i/$retries)"
      break
    fi
    if [ "$i" -eq "$retries" ]; then
      echo "FAIL: App did not respond after $((retries * delay))s"
      docker compose -f "$stack/docker-compose.yml" logs
      exit 1
    fi
    echo "Waiting... (attempt $i/$retries)"
    sleep "$delay"
  done

  local http_code
  http_code=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL")
  if [ "$http_code" -eq 200 ]; then
    echo "PASS: Smoke test — HTTP $http_code"
    exit 0
  else
    echo "FAIL: Smoke test — expected HTTP 200, got $http_code"
    exit 1
  fi
}

# ---------------------------------------------------------------
# vuln N: run solves/vulnN.* and compare output to flags.txt line N
# ---------------------------------------------------------------
cmd_vuln() {
  local n="$1"

  # Find the solve script: vulnN.ext OR vulnN_<description>.ext (e.g. vuln1_stored_xss_html_upload.sh)
  local script=""
  for ext in sh py js rb; do
    if [ -f "$SOLVES_DIR/vuln${n}.${ext}" ]; then
      script="$SOLVES_DIR/vuln${n}.${ext}"
      break
    fi
    script=$(find "$SOLVES_DIR" -maxdepth 1 -type f -name "vuln${n}_*.${ext}" 2>/dev/null | head -1)
    if [ -n "$script" ] && [ -f "$script" ]; then
      break
    fi
    script=""
  done

  # No script found — auto-pass (student has fewer than N vulns)
  if [ -z "$script" ]; then
    echo "SKIP: No vuln${n}.* script found — auto-pass"
    exit 0
  fi

  # Check flags.txt exists
  if [ ! -f "$FLAGS_FILE" ]; then
    echo "FAIL: $FLAGS_FILE not found"
    exit 1
  fi

  # Read expected flag (line N)
  local expected
  expected=$(sed -n "${n}p" "$FLAGS_FILE" | tr -d '\r' | xargs)
  if [ -z "$expected" ]; then
    echo "FAIL: No flag found on line $n of $FLAGS_FILE"
    exit 1
  fi

  # Validate flag format
  if ! echo "$expected" | grep -qE '^ENPM634\{.+\}$'; then
    echo "FAIL: Flag on line $n does not match ENPM634{...} format: $expected"
    exit 1
  fi

  echo "Running: $script"
  chmod +x "$script"

  # Execute based on extension
  local actual
  local ext="${script##*.}"
  case "$ext" in
    sh)  actual=$(bash "$script" "$APP_URL" 2>/dev/null) ;;
    py)  actual=$(python3 "$script" "$APP_URL" 2>/dev/null) ;;
    js)  actual=$(node "$script" "$APP_URL" 2>/dev/null) ;;
    rb)  actual=$(ruby "$script" "$APP_URL" 2>/dev/null) ;;
    *)   actual=$(bash "$script" "$APP_URL" 2>/dev/null) ;;
  esac

  # Trim whitespace
  actual=$(echo "$actual" | tr -d '\r' | xargs)

  if [ "$actual" = "$expected" ]; then
    echo "PASS: vuln${n} — flag matches"
    exit 0
  else
    echo "FAIL: vuln${n}"
    echo "  Expected: $expected"
    echo "  Got:      $actual"
    exit 1
  fi
}

# ---------------------------------------------------------------
# Main dispatch
# ---------------------------------------------------------------
case "${1:-}" in
  smoke)
    cmd_smoke
    ;;
  vuln)
    if [ -z "${2:-}" ]; then
      echo "Usage: $0 vuln <number>" >&2
      exit 1
    fi
    cmd_vuln "$2"
    ;;
  *)
    echo "Usage: $0 {smoke|vuln <N>}" >&2
    exit 1
    ;;
esac
