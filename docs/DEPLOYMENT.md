# Deployment Guide

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

Use `GET /health` for lightweight process health and `GET /ready` for deployment readiness with a database ping.

## Required Environment Variables

### Backend

- `DATABASE_URL`
- `JWT_SECRET`
- `NEXTAUTH_SECRET`
- `AUTH_BRIDGE_SECRET`
- `CORS_ORIGINS`
- `SENTRY_DSN` optional
- `SENTRY_ENVIRONMENT` optional
- `SENTRY_TRACES_SAMPLE_RATE` optional

### Frontend

- `NEXT_PUBLIC_API_URL`
- `NEXTAUTH_URL`
- `NEXTAUTH_SECRET`
- `AUTH_BRIDGE_SECRET`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `NEXT_PUBLIC_SENTRY_DSN` optional
- `NEXT_PUBLIC_SENTRY_ENVIRONMENT` optional

## Deploy Flow

### Render

- Deploy the backend service from `render.yaml`
- Configure Supabase `DATABASE_URL` with the `postgresql+asyncpg://` prefix
- Confirm the release responds on `/health`
- Confirm the release responds on `/ready`

### Vercel

- Run deploy commands from `frontend/`
- Use `vercel pull`
- Use `vercel build`
- Use `vercel deploy --prebuilt`

## Pilot Smoke Checklist

Run these checks after each staging or production deploy:

1. `GET <backend>/health`
2. `GET <backend>/ready`
3. `GET <frontend>/api/auth/session`
4. `FRONTEND_URL=<frontend> BACKEND_URL=<backend> scripts/smoke-local.sh`

## Rollback Notes

- If the backend deploy is unhealthy, roll back to the previous Render release and inspect migration logs first.
- If the frontend deploy fails smoke checks, restore the previous Vercel deployment alias before retrying.
- If Sentry causes noisy behavior, unset the DSN variables and redeploy. The SDKs stay inert when DSNs are empty.
