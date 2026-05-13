# Toán Socratic - Project Status Report

## Overall Status

- Branch: `feat/sprint2-frontend`
- Phase: Sprint 2 stabilization
- State: core backend/frontend contracts are aligned and verified locally

Sprint 2 is effectively implemented, but there is still one clear boundary: the backend JWT token route is a development bridge, not a production-grade auth exchange.

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
- Fixed session creation contract mismatch:
  - frontend now uses backend `id` instead of nonexistent `session_id`
- Fixed streaming contract mismatch:
  - frontend now consumes backend SSE events shaped like:
    - `{ content, done, session_state?, error? }`
- Replaced the broken async SQLite test path with PostgreSQL-backed tests
- Verified the live backend with `uv` after initializing the database

## Verification

Verified locally on May 12, 2026:

- `cd backend && uv run pytest tests -q`
- `cd frontend && npm run lint`
- `cd frontend && npm run build`
- live backend smoke path after DB initialization:
  - `GET /api/problems`
  - `POST /api/users`
  - `POST /api/auth/token`
  - `POST /api/sessions`
  - `GET /api/sessions/{id}`
  - `PUT /api/sessions/{id}/complete`

## Required Local Backend Setup

The backend will start without schema errors only after the database is initialized:

```bash
cd backend
uv run python init_db.py
uv run uvicorn main:app --reload
```

Without that step, live API requests fail with missing-table errors from PostgreSQL.

## Known Gaps

- The token route is still a dev bridge and should not be treated as a final production auth design.
- Some dependency/config code still emits deprecation warnings from Pydantic v2 and SQLAlchemy.
- Full browser-level end-to-end verification of the Google OAuth flow is still pending.

## Next Recommended Work

1. Run a browser-level end-to-end smoke test across login, session start, chat streaming, and progress views.
2. Replace the current backend JWT bridge with a trusted production auth exchange.
3. Document the Postgres-backed backend test workflow and local service prerequisites.
4. Clean up deprecation warnings once the product path is stable.
