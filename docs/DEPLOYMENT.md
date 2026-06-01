# Deployment Guide

This guide is the pilot launch runbook. It assumes the backend is deployed as a
Render Docker service, the frontend is deployed on Vercel, and PostgreSQL is
hosted by Supabase.

Production auth replacement is tracked separately in
[Production Auth Replacement Follow-Up](PRODUCTION_AUTH_FOLLOWUP.md). Sprint 4
launch prep does not change the current Google, NextAuth, or backend JWT bridge
API contract.

## Targets

- Frontend: Vercel
- Backend: Render
- Database: Supabase PostgreSQL

## Backend Startup

The production backend container starts through `backend/scripts/start.sh`.

That script:

1. runs `uv run alembic upgrade head`
2. runs `uv run python -m toan_socratic.init_db`
3. starts `uvicorn` only after migrations and seed checks complete

Use `GET /health` for lightweight process health and `GET /ready` for
deployment readiness. `/ready` runs a database ping, so it is the endpoint to
check before sending pilot traffic to a new backend release.

## Required Environment Variables

### Backend

- `DATABASE_URL`
- `JWT_SECRET`
- `NEXTAUTH_SECRET`
- `AUTH_BRIDGE_SECRET`
- `CORS_ORIGINS`
- `NEXTAUTH_URL`
- `LLM_PROVIDER`
- `ANTHROPIC_API_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `SENTRY_DSN` optional; leave empty to keep Sentry inert
- `SENTRY_ENVIRONMENT` optional, for example `production`
- `SENTRY_TRACES_SAMPLE_RATE` optional, for example `0.05`

`DATABASE_URL` should use SQLAlchemy's async driver:

```env
DATABASE_URL=postgresql+asyncpg://postgres:ENCODED_PASSWORD@HOST:5432/postgres
```

`NEXTAUTH_SECRET` and `AUTH_BRIDGE_SECRET` must match the corresponding Vercel
values. Set `CORS_ORIGINS` to the deployed frontend origin, for example:

```env
CORS_ORIGINS=https://tunas-math.vercel.app
NEXTAUTH_URL=https://tunas-math.vercel.app
```

### Frontend

- `NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_SITE_URL`
- `NEXTAUTH_URL`
- `NEXTAUTH_SECRET`
- `AUTH_BRIDGE_SECRET`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `NEXT_PUBLIC_SENTRY_DSN` optional; leave empty to keep Sentry inert
- `NEXT_PUBLIC_SENTRY_ENVIRONMENT` optional, for example `production`
- `SENTRY_ORG` optional, only needed for Sentry source map upload
- `SENTRY_PROJECT` optional, only needed for Sentry source map upload
- `SENTRY_AUTH_TOKEN` optional, only needed for Sentry source map upload

For production, `NEXT_PUBLIC_API_URL` points to Render and `NEXTAUTH_URL` points
to the Vercel frontend:

```env
NEXT_PUBLIC_API_URL=https://<render-service>.onrender.com
NEXTAUTH_URL=https://tunas-math.vercel.app
NEXT_PUBLIC_SITE_URL=https://tunas-math.vercel.app
```

## Deploy Flow

### Render

- Deploy the backend service from `render.yaml`
- Configure Supabase `DATABASE_URL` with the `postgresql+asyncpg://` prefix
- Leave the start command empty; the Dockerfile uses `backend/scripts/start.sh`
- Confirm the release responds on `/health`
- Confirm the release responds on `/ready`

### Vercel

- Run deploy commands from `frontend/`
- Use `vercel pull`
- Use `vercel build`
- Use `vercel deploy --prebuilt`

## Pilot Smoke Checklist

Run the deploy smoke script after each staging or production deploy:

```bash
BACKEND_URL=https://<render-service>.onrender.com \
FRONTEND_URL=https://<vercel-app>.vercel.app \
scripts/smoke-deploy.sh
```

The deploy smoke script retries these endpoints for propagation delays:

1. `GET <backend>/health`
2. `GET <backend>/ready`
3. `GET <frontend>/api/auth/session`

For a fuller local app smoke path from a fresh checkout, start Postgres, run the
backend and frontend locally, then run:

```bash
make smoke-local
```

`make smoke-local` uses `scripts/smoke-local.sh` to verify the frontend, backend
health/readiness, auth bridge token minting, session creation, session fetch,
and session completion. It needs `AUTH_BRIDGE_SECRET` or `NEXTAUTH_SECRET`
available in the shell, `backend/.env`, or `frontend/.env.local`.

## Rollback Notes

- If `/health` fails on Render, roll back to the previous successful Render
  deploy before investigating application logs.
- If `/ready` fails but `/health` passes, inspect migration logs, Supabase
  connectivity, and `DATABASE_URL` before sending traffic to the release.
- If the frontend deploy fails smoke checks, promote or alias the previous
  healthy Vercel deployment before retrying.
- If Sentry causes noisy behavior, unset the DSN variables and redeploy. The
  SDKs stay inert when DSNs are empty.
- Do not delete the previous backend provider or database until the Render
  backend, Vercel frontend, and pilot smoke checklist all pass.
