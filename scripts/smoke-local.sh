#!/bin/bash

set -euo pipefail

FRONTEND_URL="${FRONTEND_URL:-http://127.0.0.1:3000}"
BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:8000}"
TOPIC_ID="${TOPIC_ID:-hinh-hoc.lang-tru}"

trim_quotes() {
  local value="$1"
  value="${value%\"}"
  value="${value#\"}"
  value="${value%\'}"
  value="${value#\'}"
  printf '%s' "$value"
}

read_env_value() {
  local file="$1"
  local key="$2"
  local line

  [[ -f "$file" ]] || return 1
  line="$(grep -E "^${key}=" "$file" | tail -n 1 || true)"
  [[ -n "$line" ]] || return 1

  trim_quotes "${line#*=}"
}

fail() {
  echo
  echo "Smoke check failed: $1" >&2
  exit 1
}

echo "==> Checking frontend"
curl -fsS "$FRONTEND_URL" >/dev/null
AUTH_SESSION_JSON="$(curl -fsS "$FRONTEND_URL/api/auth/session")"
echo "Frontend OK"
echo "Auth session: $AUTH_SESSION_JSON"

echo "==> Checking backend"
curl -fsS "$BACKEND_URL/health" >/dev/null
curl -fsS "$BACKEND_URL/ready" >/dev/null
echo "Backend OK"
echo "Backend readiness OK"

EMAIL="smoke-$(date +%s)@example.com"
NAME="Smoke Test User"
AUTH_BRIDGE_SECRET="${AUTH_BRIDGE_SECRET:-}"

if [[ -z "$AUTH_BRIDGE_SECRET" ]]; then
  AUTH_BRIDGE_SECRET="$(read_env_value "backend/.env" "AUTH_BRIDGE_SECRET" || true)"
fi
if [[ -z "$AUTH_BRIDGE_SECRET" ]]; then
  AUTH_BRIDGE_SECRET="$(read_env_value "frontend/.env.local" "AUTH_BRIDGE_SECRET" || true)"
fi
if [[ -z "$AUTH_BRIDGE_SECRET" ]]; then
  AUTH_BRIDGE_SECRET="${NEXTAUTH_SECRET:-}"
fi
if [[ -z "$AUTH_BRIDGE_SECRET" ]]; then
  AUTH_BRIDGE_SECRET="$(read_env_value "backend/.env" "NEXTAUTH_SECRET" || true)"
fi
if [[ -z "$AUTH_BRIDGE_SECRET" ]]; then
  AUTH_BRIDGE_SECRET="$(read_env_value "frontend/.env.local" "NEXTAUTH_SECRET" || true)"
fi
[[ -n "$AUTH_BRIDGE_SECRET" ]] || fail "missing auth bridge secret. Set AUTH_BRIDGE_SECRET first, or fall back to NEXTAUTH_SECRET in the shell, backend/.env, or frontend/.env.local."

echo "==> Creating backend user"
USER_JSON="$(curl -fsS \
  -X POST "$BACKEND_URL/api/users" \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMAIL\",\"name\":\"$NAME\"}")"
USER_ID="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<<"$USER_JSON")"
echo "User created: $USER_ID"

echo "==> Minting backend token"
TOKEN_JSON="$(curl -fsS \
  -X POST "$BACKEND_URL/api/auth/token" \
  -H 'Content-Type: application/json' \
  -H "X-Auth-Bridge-Secret: $AUTH_BRIDGE_SECRET" \
  -d "{\"user_id\":\"$USER_ID\"}")"
ACCESS_TOKEN="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["access_token"])' <<<"$TOKEN_JSON")"
echo "Token minted"

AUTH_HEADER="Authorization: Bearer $ACCESS_TOKEN"

echo "==> Creating session"
SESSION_JSON="$(curl -fsS \
  -X POST "$BACKEND_URL/api/sessions" \
  -H 'Content-Type: application/json' \
  -H "$AUTH_HEADER" \
  -d "{\"user_id\":\"$USER_ID\",\"topic_id\":\"$TOPIC_ID\"}")"
SESSION_ID="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<<"$SESSION_JSON")"
echo "Session created: $SESSION_ID"

echo "==> Fetching session"
FETCH_JSON="$(curl -fsS \
  -H "$AUTH_HEADER" \
  "$BACKEND_URL/api/sessions/$SESSION_ID")"
FETCH_STATE="$(python3 -c 'import json,sys; data=json.load(sys.stdin); print(data["dialogue_state"], data["hint_level"])' <<<"$FETCH_JSON")"
echo "Session state: $FETCH_STATE"

echo "==> Completing session"
COMPLETE_JSON="$(curl -fsS \
  -X PUT "$BACKEND_URL/api/sessions/$SESSION_ID/complete" \
  -H 'Content-Type: application/json' \
  -H "$AUTH_HEADER" \
  -d '{"student_rating":4}')"
echo "Completion payload: $COMPLETE_JSON"

echo
echo "Smoke check passed"
echo "Frontend: $FRONTEND_URL"
echo "Backend: $BACKEND_URL"
echo "User: $USER_ID"
echo "Session: $SESSION_ID"
