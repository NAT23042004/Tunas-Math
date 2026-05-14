# Database Management

This project currently uses PostgreSQL as the real backend database for:

- local runtime
- Docker runtime
- backend automated tests

`pgAdmin` is available for visual inspection, but it is only one part of the workflow. The important current behavior is:

- the backend is managed locally with `uv`
- a fresh database must be initialized before the live API can use it
- backend tests are PostgreSQL-backed

## Current State

Database-related components in this repo:

- PostgreSQL service in [docker-compose.yml](/home/natus/Project/Tunas-Math/docker-compose.yml)
- async SQLAlchemy engine in [db/database.py](/home/natus/Project/Tunas-Math/backend/db/database.py)
- schema/sample-data initialization in [init_db.py](/home/natus/Project/Tunas-Math/backend/init_db.py)
- pgAdmin service for visual access

The database is persistent if the Docker volume is preserved. You do not need to initialize it again after every laptop restart. You only need to initialize it again when the database is fresh, empty, or recreated.

## Local Backend Workflow

### 1. Start the database service

```bash
docker compose up -d postgres
```

If you want the full local stack:

```bash
docker compose up -d
```

### 2. Initialize a fresh database

Run this only when tables/data are missing, or when you are not sure the DB has already been prepared:

```bash
cd backend
uv run python init_db.py
```

This script:

- creates tables if missing
- loads sample problems if the problems table is empty

### 3. Run the backend locally

```bash
cd backend
uv run uvicorn toan_socratic.main:app --host 127.0.0.1 --port 8000
```

### 4. Verify the app path

```bash
cd /home/natus/Project/Tunas-Math
make smoke-local
```

That smoke check validates the frontend/backend path without requiring a manual browser OAuth flow.

## When You Need `init_db.py`

You usually **do not** need to run it on every restart.

Run it when:

- you created a new Postgres container/volume
- you deleted the DB volume
- the DB is empty
- the backend returns missing-table errors

Typical failure symptom:

- `/api/problems` or `/api/users` returns database errors like missing relations/tables

## Fast Checks

Check backend health:

```bash
curl http://127.0.0.1:8000/health
```

Check whether the initialized problems data is available:

```bash
curl http://127.0.0.1:8000/api/problems
```

If `/health` works but `/api/problems` fails due to schema errors, initialize the DB:

```bash
cd backend
uv run python init_db.py
```

## pgAdmin

`pgAdmin` is useful for browsing and querying the database, but it does not replace initialization or backend verification.

### Access pgAdmin

- URL: `http://localhost:5050`
- Email: `admin@toansocratic.com`
- Password: `admin`

### Add the database server

Use these values in pgAdmin:

- Name: `Toán Socratic DB`
- Host name/address: `postgres`
- Port: `5432`
- Database: `toansc`
- Username: `toan_user`
- Password: `toan_password`

These values are for the Docker network path used by the containers.

## Command-Line Access

### Connect to Postgres in Docker

```bash
docker exec -it toan_socratic_db psql -U toan_user -d toansc
```

Useful commands:

```sql
\dt
\d problems
SELECT COUNT(*) FROM problems;
SELECT * FROM sessions ORDER BY started_at DESC LIMIT 10;
\q
```

## Useful Queries

```sql
SELECT * FROM problems;
SELECT status, COUNT(*) FROM sessions GROUP BY status;
SELECT * FROM sessions ORDER BY started_at DESC LIMIT 10;
SELECT * FROM progress WHERE mastery_score > 0.5;
```

## Management Commands

Start only pgAdmin:

```bash
docker compose up -d pgadmin
```

Restart pgAdmin:

```bash
docker compose restart pgadmin
```

View pgAdmin logs:

```bash
docker logs -f toan_socratic_pgadmin
```

Open a DB shell via Make:

```bash
make db-shell
```

Initialize DB via Make inside Docker backend service:

```bash
make db-init
```

## Schema Overview

Core tables:

- `users`
- `problems`
- `sessions`
- `progress`

Key relationships:

- `sessions.user_id -> users.id`
- `sessions.problem_id -> problems.id`
- `progress.user_id -> users.id`

Sample data:

- sample Grade 12 math problems are loaded by `init_db.py`

## Tests

Backend tests currently use PostgreSQL-backed async fixtures. Do not assume SQLite is the active or authoritative test path for this repo.

Run tests with:

```bash
cd backend
uv run pytest tests -q
```

## Recommended Resume Flow After Restart

If the machine restarts and you want to continue work:

1. Start Docker services:

```bash
docker compose up -d
```

2. Start backend:

```bash
cd backend
uv run uvicorn toan_socratic.main:app --host 127.0.0.1 --port 8000
```

3. Start frontend:

```bash
cd /home/natus/Project/Tunas-Math/frontend
npm run dev
```

4. Run smoke check:

```bash
cd /home/natus/Project/Tunas-Math
make smoke-local
```

Only run `uv run python init_db.py` if the database is fresh or broken.
