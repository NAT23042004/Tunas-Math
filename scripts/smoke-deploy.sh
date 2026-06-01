#!/bin/bash

set -euo pipefail

MAX_ATTEMPTS="${SMOKE_MAX_ATTEMPTS:-12}"
SLEEP_SECONDS="${SMOKE_SLEEP_SECONDS:-10}"

fail() {
  echo "Deploy smoke check failed: $1" >&2
  exit 1
}

require_url() {
  local name="$1"
  local value="${!name:-}"

  [[ -n "$value" ]] || fail "$name is required"
}

check_endpoint() {
  local label="$1"
  local url="$2"
  local attempt

  for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
    if curl -fsS "$url" >/dev/null; then
      echo "$label OK: $url"
      return 0
    fi

    if [[ "$attempt" -lt "$MAX_ATTEMPTS" ]]; then
      echo "$label not ready yet ($attempt/$MAX_ATTEMPTS): $url"
      sleep "$SLEEP_SECONDS"
    fi
  done

  fail "$label did not become available after $MAX_ATTEMPTS attempts: $url"
}

require_url BACKEND_URL
require_url FRONTEND_URL

BACKEND_URL="${BACKEND_URL%/}"
FRONTEND_URL="${FRONTEND_URL%/}"

echo "==> Running deploy smoke checks"
check_endpoint "Backend health" "$BACKEND_URL/health"
check_endpoint "Backend readiness" "$BACKEND_URL/ready"
check_endpoint "Frontend auth session" "$FRONTEND_URL/api/auth/session"
echo "Deploy smoke checks passed"
