# Toán Socratic - Backend API

AI-powered Vietnamese math tutor for Grade 12 students using the Socratic method.

## Features

- **Socratic Dialogue Engine**: 4-state dialogue machine (REVIEW, HEURISTIC, RECTIFY, SUMMARIZE)
- **Hint Escalation System**: 4-level hint system (L0-L3) for adaptive guidance
- **3D Geometry Detection**: Automatic detection and tool triggering for geometry problems
- **Session Management**: Complete session lifecycle with progress tracking
- **Problem Bank**: Structured problem database with geometry parameters
- **Mastery Tracking**: Progress tracking with mastery score calculation

## Tech Stack

- **FastAPI**: Modern async web framework
- **SQLAlchemy**: Async ORM with PostgreSQL support
- **LiteLLM**: Multi-provider LLM integration (Anthropic, OpenAI, Cohere, Azure)
- **Pydantic**: Data validation and settings management
- **uv**: Python package and environment manager

## Project Structure

```
backend/
├── ai/                    # AI components
│   ├── llm_client.py      # Multi-provider LLM client with streaming
│   ├── context_builder.py # Session context builder
│   ├── dialogue.py        # Dialogue state machine
│   └── prompts.py         # Socratic system prompts
├── db/                    # Database components
│   ├── database.py        # Database connection and session management
│   ├── models.py          # SQLAlchemy models
│   └── schemas.py         # Pydantic schemas
├── routers/               # API endpoints
│   ├── sessions.py        # Session management endpoints
│   └── problems.py        # Problem management endpoints
├── data/                  # Sample data
│   └── sample_problems.py # Sample problems for testing
├── tests/                 # Test suite
│   └── test_socratic_engine.py
├── config.py              # Configuration management
├── init_db.py             # Database initialization script
├── main.py                # FastAPI application entry point
├── requirements.txt       # Python dependencies
└── .env.example           # Environment variables template
```

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ with pgvector extension
- `uv`

### Installation

1. Sync the environment:
```bash
uv sync
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your actual values
```

3. Initialize database:
```bash
uv run python init_db.py
```

This step is required before using the live API. The backend will start without it, but requests that hit the database will fail because the tables and sample data do not exist yet.

### Running the Server

```bash
# Development server
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production server
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Sessions

- `POST /api/sessions` - Create new Socratic session
- `GET /api/sessions/{id}` - Get session details
- `POST /api/sessions/{id}/message` - Send message and get AI response
- `PUT /api/sessions/{id}/complete` - Complete session and update progress

### Problems

- `GET /api/problems` - List problems with filters
- `GET /api/problems/{id}` - Get problem details
- `GET /api/problems/{id}/geometry` - Get geometry parameters
- `POST /api/problems` - Create new problem

### Health

- `GET /` - Health check
- `GET /health` - Health check

### Auth

- `POST /api/auth/token` - Mint backend JWT for an existing user

This route is currently used as a local/staging bridge for the server-side NextAuth flow. It now requires the `X-Auth-Bridge-Secret` header and should still be replaced with a production auth exchange in Sprint 3.

## Testing

Run the test suite:
```bash
cd backend
uv run pytest tests -q
```

The backend test suite is currently PostgreSQL-backed. Do not assume the async SQLite path is valid here; that setup was replaced because it was not reliable in this environment.

## Socratic Dialogue Engine

### Dialogue States

1. **REVIEW**: Restate problem, assess student understanding
2. **HEURISTIC**: Ask guiding sub-questions to break down problem
3. **RECTIFY**: Identify errors without solving, guide back
4. **SUMMARIZE**: Confirm solution and generalize concept

### Hint Levels

- **L0**: Pure Socratic - only questions
- **L1**: Guided Hint - point to tools/theorems
- **L2**: Scaffolded Hint - provide first step
- **L3**: Full Worked Example - complete solution

### Geometry Detection

The system automatically detects 3D geometry problems and triggers the `render_geometry` tool for:
- Pyramids (hình chóp)
- Prisms (lăng trụ)
- Spheres (hình cầu)
- Cones (hình nón)
- Cylinders (hình trụ)
- Boxes (hình hộp)

## Environment Variables

See `.env.example` for all required environment variables:

### LLM Configuration
- `LLM_PROVIDER`: LLM provider (anthropic, openai, cohere, azure, qwen, gemini)
- `LLM_MODEL`: Model name (e.g., claude-sonnet-4-6, gpt-4, qwen-turbo, gemini-pro)
- `LLM_API_KEY`: Generic API key (optional, works for all providers)

### Provider-Specific API Keys (optional, used if LLM_API_KEY not set)
- `ANTHROPIC_API_KEY`: Anthropic API key (if using Anthropic)
- `OPENAI_API_KEY`: OpenAI API key (if using OpenAI)
- `COHERE_API_KEY`: Cohere API key (if using Cohere)
- `AZURE_API_KEY`: Azure OpenAI API key (if using Azure)
- `QWEN_API_KEY`: Qwen API key (if using Qwen)
- `GEMINI_API_KEY`: Google Gemini API key (if using Gemini)

### Other Configuration
- `DATABASE_URL`: PostgreSQL connection string
- `CORS_ORIGINS`: comma-separated frontend origins allowed by FastAPI CORS
- `JWT_SECRET`: JWT secret key
- `AUTH_BRIDGE_SECRET`: shared secret for the NextAuth-to-backend token bridge
- `GOOGLE_CLIENT_ID/SECRET`: OAuth credentials
- `NEXTAUTH_SECRET/URL`: NextAuth configuration

## Development

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions small and focused

### Git Workflow

- Create feature branches: `feat/sprint1-ai-engine`
- Commit frequently with atomic changes
- Use conventional commit messages
- Test before pushing

## Current Status

Sprint 1 is complete, and Sprint 2 backend/frontend integration is stabilized locally.

Verified locally on May 12, 2026:

- `uv run pytest tests -q`
- live requests for problems, user creation, token minting, session creation/fetch, and completion

## Next Steps

- Browser-level end-to-end smoke test across login and chat flow
- Replace the current token bridge with production-grade auth exchange
- Clean up deprecation warnings from dependency upgrades
