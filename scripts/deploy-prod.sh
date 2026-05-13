#!/bin/bash

# Production deployment script for Toán Socratic

set -e

echo "🚀 Deploying Toán Socratic to production..."

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "❌ Must be on main branch to deploy. Current branch: $CURRENT_BRANCH"
    exit 1
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ There are uncommitted changes. Please commit or stash them first."
    exit 1
fi

# Run tests
echo "🧪 Running tests..."
docker compose -f docker-compose.yml run backend uv run pytest tests/

# Build production images
echo "🏗️  Building production images..."
docker compose -f docker-compose.prod.yml build

# Deploy to Railway (Backend)
echo "🚂 Deploying backend to Railway..."
railway up

# Deploy to Vercel (Frontend)
echo "🌐 Deploying frontend to Vercel..."
vercel --prod

echo "✅ Production deployment complete!"
echo ""
echo "📍 Production URLs:"
echo "  - Backend: https://api.toan-socratic.com"
echo "  - Frontend: https://toan-socratic.com"
