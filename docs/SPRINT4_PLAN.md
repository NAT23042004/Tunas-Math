# Sprint 4 Pilot-Ready Launch Implementation Plan

## Summary

Build the next Sprint 4 slice as a pilot-ready deployment
and polish pass. The plan keeps production auth
replacement out of scope and focuses on launch readiness:
reliable deploy startup, monitoring, smoke checks, core
loading/error UX, and deployment documentation.

## Public Interfaces And Config

- Add GET /ready on the backend for deployment readiness.
It should verify database connectivity with SELECT 1 and
return { "status": "ready" }; keep existing GET /health
as lightweight process health.
- Add optional monitoring env vars:
    - Backend: SENTRY_DSN, SENTRY_ENVIRONMENT,
    SENTRY_TRACES_SAMPLE_RATE
    - Frontend: NEXT_PUBLIC_SENTRY_DSN,
    NEXT_PUBLIC_SENTRY_ENVIRONMENT
- Do not change auth API contracts in this sprint. Keep
the current Google/NextAuth/backend JWT flow and
document production auth replacement as a separate
follow-up.

## Implementation Changes

- Backend deploy readiness
    - Add a production startup script under backend/
    scripts/start.sh that runs uv run alembic upgrade
    head before starting uvicorn.
    - Update backend/Dockerfile production CMD to use the
    startup script.
    - Add /ready in backend/toan_socratic/main.py with a
    DB ping through SQLAlchemy.
    - Add backend tests for /health remaining DB-
    independent and /ready returning success when the
    test database is reachable.
- Monitoring
    - Add sentry-sdk[fastapi] to backend dependencies and
    initialize Sentry in app creation only when
    SENTRY_DSN is set.
    - Add @sentry/nextjs to frontend dependencies, add
    Sentry config files, and wrap frontend/
    next.config.mjs with Sentry config while keeping
    current webpack externals.
    - Update .env.example files with Sentry vars and safe
    defaults.
- Frontend polish and performance
    - Replace boilerplate root metadata in frontend/app/
    layout.tsx with Toán Socratic title/description and
    set lang="vi".
    - Add shared LoadingState and ErrorState components,
    then add route-level loading.tsx and error.tsx for
    student/admin route groups.
    - Update dashboard, history, and session pages to use
    consistent empty/error/loading states instead of raw
    text blocks.
    - Lazy-load GeometryViewer from MessageBubble with
    next/dynamic, ssr: false, and a stable-height
    loading placeholder.
- CI/CD and pilot smoke checks
    - Update .github/workflows/ci-cd.yml deployment jobs
    so frontend deploy runs from frontend/ with Vercel
    CLI: vercel pull, vercel build, vercel deploy
    --prebuilt.
    - Keep Render backend deploy, but add post-deploy
    smoke checks for backend /health, backend /ready,
    and frontend /api/auth/session.
    rollback notes, and the pilot smoke checklist.
    - Update README project status: Sprint 3 complete,
    Sprint 4 launch prep in progress.

## Test Plan

- Backend:
    - ./backend/.venv/bin/python -m pytest backend/tests/
    test_api.py backend/tests/test_turn_assessment.py
    backend/tests/test_models.py -q
    - Add targeted tests for /ready success and /health
    success.
- Frontend:
    - npm run lint
    - npx tsc --noEmit
    - npm run build
- Deployment checks:
    - docker build -t toan-socratic-backend:test ./backend
    - docker build -t toan-socratic-frontend:test ./frontend
    - BACKEND_URL=<url> FRONTEND_URL=<url> scripts/smoke-deploy.sh
- Acceptance:
    - CI passes on PR.
    - Backend container starts from an empty deployed
    database by running migrations before serving.
    - Frontend no longer shows boilerplate metadata or raw
    loading/error text on key routes.
    - Sentry is inert when DSNs are unset and active when
    DSNs are configured.

## Assumptions

- Deployment targets stay as documented: Vercel for
frontend, Render for backend, and Supabase for PostgreSQL.
- Production auth replacement is a separate project and
should not block this Sprint 4 launch-prep slice.
- Pilot problem-bank expansion and student recruiting are
operational follow-ups; this plan only adds the
technical launch path and documentation needed to
support them.
- Existing untracked docs/ files remain untouched unless a
later task explicitly adopts or replaces them.
