# Render Migration Guide

This moves the backend off Railway while keeping the frontend on Vercel.

## Target Stack

- Frontend: Vercel
- Backend API: Render Web Service, Docker runtime
- Database: Supabase Postgres

Use Supabase Postgres instead of Render Postgres on the free path. Render's free Postgres option is not a durable production database.

## 1. Create Postgres

Create a database in Supabase and copy the connection string from project database settings.

Set the backend `DATABASE_URL` with the async SQLAlchemy driver:

```env
DATABASE_URL=postgresql+asyncpg://postgres:ENCODED_PASSWORD@HOST:5432/postgres
```

If Supabase gives you `postgresql://...`, replace the prefix with `postgresql+asyncpg://...`. URL-encode the password if it contains special characters such as `@`, `#`, `/`, `?`, or `:`.

## 2. Create Render Backend

Use the repo's `render.yaml` Blueprint, or create a Render Web Service manually with:

```text
Runtime: Docker
Dockerfile Path: ./backend/Dockerfile
Docker Context: ./backend
Health Check Path: /health
```

Leave the start command empty. The Dockerfile already runs `backend/scripts/start.sh`, which:

1. applies Alembic migrations
2. seeds sample problems if missing
3. starts Uvicorn on Render's `$PORT`

## 3. Set Render Environment Variables

Required:

```env
DATABASE_URL=postgresql+asyncpg://postgres:ENCODED_PASSWORD@HOST:5432/postgres
DEBUG=false
JWT_SECRET=<generate a strong secret>
NEXTAUTH_SECRET=<same value used in Vercel>
AUTH_BRIDGE_SECRET=<same value used in Vercel>
CORS_ORIGINS=https://tunas-math.vercel.app
NEXTAUTH_URL=https://tunas-math.vercel.app
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=<your key>
GOOGLE_CLIENT_ID=<your Google OAuth client id>
GOOGLE_CLIENT_SECRET=<your Google OAuth client secret>
```

Optional:

```env
SENTRY_DSN=<backend Sentry DSN>
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.05
```

## 4. Smoke Test Render

After Render deploys, test the new backend:

```bash
BACKEND_URL=https://<your-render-service>.onrender.com

curl "$BACKEND_URL/health"
curl "$BACKEND_URL/ready"
curl "$BACKEND_URL/api/problems"
```

Expected:

- `/health` returns `{"status":"ok"}`
- `/ready` returns `{"status":"ready"}`
- `/api/problems` returns the seeded sample problems

For release smoke checks, prefer the reusable deploy smoke script after both the
backend and frontend are deployed:

```bash
BACKEND_URL=https://<your-render-service>.onrender.com \
FRONTEND_URL=https://<your-vercel-app>.vercel.app \
scripts/smoke-deploy.sh
```

For a full local app smoke path from a fresh checkout, start the local backend
and frontend first, then run:

```bash
make smoke-local
```

## 5. Point Vercel To Render

Update Vercel frontend environment:

```env
NEXT_PUBLIC_API_URL=https://<your-render-service>.onrender.com
NEXTAUTH_URL=https://tunas-math.vercel.app
NEXT_PUBLIC_SITE_URL=https://tunas-math.vercel.app
NEXTAUTH_SECRET=<same value used in Render>
AUTH_BRIDGE_SECRET=<same value used in Render>
GOOGLE_CLIENT_ID=<your Google OAuth client id>
GOOGLE_CLIENT_SECRET=<your Google OAuth client secret>
```

Redeploy Vercel after changing env vars.

## 6. Keep Railway Until Render Passes

Do not delete Railway until Render passes:

```bash
curl https://<your-render-service>.onrender.com/health
curl https://<your-render-service>.onrender.com/ready
curl https://<your-render-service>.onrender.com/api/problems
```

Then verify the frontend can:

- load the dashboard
- sign in
- start a session
- send one message

If a new Render release fails `/health`, roll back to the previous Render deploy.
If `/health` passes but `/ready` fails, inspect migration logs and Supabase
connectivity before retrying. If a Vercel release fails the smoke check, restore
the previous healthy Vercel deployment alias.

After those checks pass, shut down the Railway backend service.
