#!/bin/bash

# Development setup script for Toán Socratic

set -e

echo "🚀 Setting up Toán Socratic development environment..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "❌ Docker Compose v2 plugin is required but not installed. Aborting." >&2; exit 1; }

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your actual API keys and secrets"
fi

# Start services
echo "🐳 Starting Docker services..."
docker compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
docker compose ps

# Initialize database
echo "🗄️  Initializing database..."
docker compose exec backend uv run python init_db.py

echo "✅ Development environment setup complete!"
echo ""
echo "📝 Available services:"
echo "  - Backend API: http://localhost:8000"
echo "  - Frontend: http://localhost:3000"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "🛠️  Useful commands:"
echo "  - View logs: docker compose logs -f"
echo "  - Stop services: docker compose down"
echo "  - Restart services: docker compose restart"
echo "  - Run backend tests: docker compose exec backend uv run pytest tests/"
