# Toán Socratic - AI-Powered Vietnamese Math Tutor

Full-stack AI application for Grade 12 Vietnamese students using the Socratic method with interactive 3D geometry visualization.

## 🏗️ Project Structure

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

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Using Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## 🛠️ Tech Stack

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

## 📖 Documentation

- [Backend Documentation](backend/README.md)
- [Frontend Documentation](frontend/README.md)
- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

## 🚢 Deployment

### Frontend (Vercel)
```bash
vercel --prod
```

### Backend (Railway)
```bash
railway up
```

## 📊 Project Status

- ✅ Sprint 1: Socratic AI Engine (Complete)
- ✅ Sprint 2: Core UI + 3D Viewer + Auth (Complete)
- ⏳ Sprint 3: Progress, Roles & Polish
- ⏳ Sprint 4: UX Polish, Testing & Launch Prep

### Sprint 2 Accomplishments
- ✅ Google OAuth authentication with NextAuth
- ✅ Server-Sent Events (SSE) streaming for chat
- ✅ Centralized API client with TypeScript types
- ✅ React Query integration for state management
- ✅ 3D geometry viewer with Three.js
- ✅ Session management with JWT tokens
- ✅ Route protection with middleware