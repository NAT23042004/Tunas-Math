# Toán Socratic - Project Status Report

## Overall Status

- Branch: `feat/sprint2-frontend`
- Phase: Sprint 3 complete
- State: core backend/frontend contracts are aligned, protected for local/staging, and ready for Sprint 4 launch-prep work across deploy readiness, monitoring, and UX polish

Sprint 3 is effectively implemented, but there is still one clear boundary: the backend JWT token route is a protected local/staging bridge, not a production-grade auth exchange.

## What Is Working

### Backend

- FastAPI app with async SQLAlchemy and PostgreSQL
- Session lifecycle endpoints:
  - create session
  - fetch session
  - stream/respond to messages
  - complete session and update progress
- Problem catalog endpoints
- JWT token minting endpoint used by the frontend auth flow
- LiteLLM-based tutoring backend
- Database initialization script with sample Grade 12 problems

### Frontend

- Next.js 14 App Router application
- Google login via NextAuth
- Backend JWT acquisition during auth flow
- Backend JWT bridge protected by a shared server-side header
- Session creation routed with the backend's actual response shape
- SSE chat consumption aligned to backend event payloads
- 3D geometry viewer and student session UI

### Tooling and Infra

- Backend managed with `uv`
- Docker Compose stack with PostgreSQL/pgvector and Redis
- Frontend lint/build passing
- Backend automated tests passing against PostgreSQL

## Recent Stabilization Work

- Fixed auth contract mismatch:
  - frontend now calls `POST /api/auth/token`
  - backend accepts `{ "user_id": ... }`
- Hardened the token bridge:
  - backend now requires `X-Auth-Bridge-Secret`
  - frontend server auth route and `make smoke-local` send the shared secret
- Replaced hard-coded CORS with `CORS_ORIGINS`
- Fixed session creation contract mismatch:
  - frontend now uses backend `id` instead of nonexistent `session_id`
- Fixed streaming contract mismatch:
  - frontend now consumes backend SSE events shaped like:
    - `{ content, done, session_state?, error? }`
- Replaced the broken async SQLite test path with PostgreSQL-backed tests
- Verified the live backend with `uv` after initializing the database

## Verification

Verified locally on May 14, 2026:

- `cd backend && uv run pytest tests -q`
- `cd frontend && npm run lint`
- `cd frontend && npm run build`
- `make smoke-local`
- live backend smoke path after DB initialization:
  - `GET /api/problems`
  - `POST /api/users`
  - `POST /api/auth/token`
  - `POST /api/sessions`
  - `GET /api/sessions/{id}`
  - `PUT /api/sessions/{id}/complete`
- browser Google OAuth path:
  - login succeeds through NextAuth
  - dashboard loads
  - session creation works
  - streamed chat path verified manually

## Required Local Backend Setup

The backend will start without schema errors only after the database is initialized:

```bash
cd backend
uv run python init_db.py
uv run uvicorn main:app --reload
```

Without that step, live API requests fail with missing-table errors from PostgreSQL.

## Known Gaps

- The token route is still a local/staging bridge and should not be treated as a final production auth design.
- Some dependency/config code still emits deprecation warnings from Pydantic v2 and SQLAlchemy.

## Next Recommended Work

1. Complete Sprint 4 launch prep: deploy readiness, Sentry setup, smoke checks, and route-level UX fallback states.
2. Replace the current backend JWT bridge with a trusted production auth exchange in a follow-up production auth sprint.
3. Expand automated coverage around the NextAuth bridge so the browser auth path has a regression check beyond manual smoke verification.
