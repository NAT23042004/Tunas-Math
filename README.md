# Toán Socratic - AI-Powered Vietnamese Math Tutor

Full-stack AI application for Grade 12 Vietnamese students using the Socratic method with interactive 3D geometry visualization.

## Project Structure

```
toan-socratic/
├── backend/              # FastAPI backend with multi-provider AI
├── frontend/             # Next.js frontend with Three.js
├── docker/               # Docker configurations
├── scripts/               # Utility scripts
├── .github/              # CI/CD workflows
├── docs/                 # Documentation
└── docker-compose.yml    # Development orchestration
```

## Quick Start

### Prerequisites
- Docker with `docker compose`
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- `uv` (for local backend development)

### Using Docker

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### Local Development

```bash
# Infrastructure
docker compose up -d postgres

# Backend
cd backend
uv sync
uv run python init_db.py
uv run uvicorn toan_socratic.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

The backend depends on PostgreSQL schema and seed data created by `uv run python init_db.py`. If you skip that step, live API requests will fail with missing-table errors.

Local auth bridge baseline for Sprint 2:

- set `CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000` in `backend/.env`
- set `AUTH_BRIDGE_SECRET` in `backend/.env` and `frontend/.env.local`
- rotate `GOOGLE_CLIENT_SECRET` outside the repo before treating the branch as clean

## Tech Stack

### Backend
- **FastAPI** - Modern async web framework
- **SQLAlchemy** - Async ORM with PostgreSQL
- **LiteLLM** - Multi-provider LLM integration (Anthropic, OpenAI, Cohere, Azure, Qwen, Gemini)
- **PostgreSQL** - Database with pgvector extension

### Frontend
- **Next.js 14** - React framework with App Router
- **Three.js** - 3D geometry visualization
- **Tailwind CSS** - Styling
- **KaTeX** - Math formula rendering

### Infrastructure
- **Docker** - Containerization
- **GitHub Actions** - CI/CD
- **Vercel** - Frontend deployment
- **Railway** - Backend deployment

## Documentation

- [Backend Documentation](backend/README.md)
- [Frontend Documentation](frontend/README.md)
- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## Testing

```bash
# Backend tests
cd backend
uv run pytest tests -q

# Frontend tests
cd frontend
npm run lint
npm run build

# Local app smoke check (frontend + backend servers must already be running)
cd ..
make smoke-local
```

## Deployment

### Frontend (Vercel)
```bash
vercel --prod
```

### Backend (Railway)
```bash
railway up
```

## Project Status

- ✅ Sprint 1: Socratic AI Engine
- ✅ Sprint 2: Core UI, auth integration, session flow stabilization
- ⏳ Sprint 3: Progress, roles, and auth hardening
- ⏳ Sprint 4: UX polish, testing, and launch prep

Current branch verification:

- backend tests pass with PostgreSQL-backed async fixtures
- frontend lint/build pass
- live backend auth/session CRUD smoke path is working locally

Known boundary:

- `POST /api/auth/token` now requires the shared bridge header for local/staging use, but it is still not the final production auth design
