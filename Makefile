.PHONY: help setup dev test clean build deploy logs restart smoke-local

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*?##/ { printf "  %-15s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

setup: ## Set up development environment
	@./scripts/setup-dev.sh

dev: ## Start development environment
	@docker compose up -d
	@echo "Development environment started!"
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"

test: ## Run all tests
	@echo "Running backend tests..."
	@docker compose exec backend uv run pytest tests/ -v
	@echo "Running frontend tests..."
	@docker compose exec frontend npm test

test-backend: ## Run backend tests only
	@docker compose exec backend uv run pytest tests/ -v

test-frontend: ## Run frontend tests only
	@docker compose exec frontend npm test

lint: ## Run linters
	@echo "Linting backend..."
	@docker compose exec backend uv run ruff check .
	@echo "Linting frontend..."
	@docker compose exec frontend npm run lint

clean: ## Clean up containers and volumes
	@docker compose down -v
	@echo "Cleaned up containers and volumes"

build: ## Build production images
	@docker compose -f docker-compose.prod.yml build

deploy: ## Deploy to production
	@./scripts/deploy-prod.sh

logs: ## Show logs from all services
	@docker compose logs -f

logs-backend: ## Show backend logs
	@docker compose logs -f backend

logs-frontend: ## Show frontend logs
	@docker compose logs -f frontend

restart: ## Restart all services
	@docker compose restart

restart-backend: ## Restart backend service
	@docker compose restart backend

restart-frontend: ## Restart frontend service
	@docker compose restart frontend

db-init: ## Initialize database
	@docker compose exec backend uv run python init_db.py

db-shell: ## Open database shell
	@docker compose exec postgres psql -U toan_user -d toansc

backend-shell: ## Open backend shell
	@docker compose exec backend bash

frontend-shell: ## Open frontend shell
	@docker compose exec frontend sh

install: ## Install dependencies
	@echo "Installing backend dependencies..."
	@cd backend && uv sync
	@echo "Installing frontend dependencies..."
	@cd frontend && npm install

format: ## Format code
	@echo "Formatting backend code..."
	@docker compose exec backend uv run ruff format .
	@echo "Formatting frontend code..."
	@docker compose exec frontend npm run format

check: ## Run all checks (lint + test)
	@make lint
	@make test

smoke-local: ## Run local frontend/backend smoke check against running dev servers
	@bash ./scripts/smoke-local.sh
