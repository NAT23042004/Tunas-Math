# Sprint 2 Closeout Plan

## Summary

Close Sprint 2 by turning the now-working local auth/session flow
into a safer, repeatable, documented baseline. The scope is
stabilization and hardening, not Sprint 3 features. The target end
state is: Google login works, dashboard/session/chat smoke paths
pass, secrets are no longer logged, the backend token bridge is
protected for local/staging use, and docs reflect the current uv +
docker compose workflow.

## Completion Status

Closed locally on May 14, 2026.

- Google login was verified through the browser path.
- `make smoke-local` passed end to end against the local frontend and backend.
- The auth bridge now fails sign-in when backend JWT minting fails.
- `scripts/smoke-local.sh` now prefers `AUTH_BRIDGE_SECRET` before falling back to `NEXTAUTH_SECRET`.
- The remaining boundary is unchanged: this bridge is acceptable for Sprint 2 local/staging use, but it is not the final production auth design.

## Key Changes

- Remove unsafe OAuth debug logging from frontend/app/api/auth/
[...nextauth]/route.ts; keep debug controlled by env only, and
never log provider metadata or secrets.
- Rotate GOOGLE_CLIENT_SECRET in Google Cloud Console, then update
local .env.local and backend .env; treat the old secret as
compromised because it appeared in terminal logs.
    - update scripts/smoke-local.sh to read the same env value and
    send the header
- Make CORS configurable:
    - add CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
    - parse it in backend config
    - replace the hard-coded allow_origins=["http://localhost:3000"]
- Update docs/status to mark browser Google login verified and
document the remaining boundary: this bridge is acceptable for
Sprint 2 local/staging, but true production auth hardening belongs
in Sprint 3.

## Test Plan

- Backend:
    - cd backend && uv run pytest tests -q
    - add/update tests that POST /api/auth/token returns 401 without
    the bridge header and 200 with the correct header
    - add a CORS config test if the existing API test style supports
    it cleanly
- Frontend:
    - cd frontend && npm run lint
    - cd frontend && npm run build
    - verify NextAuth still requests the backend token successfully
    after adding the bridge header
- Local integration:
    - start Postgres with docker compose up -d postgres
    - run backend with uv run uvicorn main:app --host 127.0.0.1
    --port 8000
    - run frontend with npm run dev
    - run make smoke-local
    - manually verify Google login, dashboard load, session
    creation, and one streamed chat message

## Assumptions

- Sprint 2 closeout should prioritize local/staging safety and
reliability over a full production auth redesign.
- The backend token route remains a server-to-server bridge for now,
but it must no longer be publicly mintable with only a user_id.
- docker compose is the only supported Compose command for this
repo; docker-compose v1 remains unsupported.
- The Google client secret will be rotated manually outside the repo
before this branch is considered clean.
