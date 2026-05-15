FROM python:3.11-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy uv binary
COPY --from=ghcr.io/astral-sh/uv:0.9.5 /uv /uvx /bin/

# Copy dependency metadata first for better caching
COPY pyproject.toml uv.lock ./

FROM base AS development

RUN uv sync --locked --no-install-project

# Copy application code after dependency installation
COPY . .

RUN uv sync --locked

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uv", "run", "uvicorn", "toan_socratic.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM base AS production

RUN uv sync --locked --no-dev --no-install-project

COPY . .

RUN chmod +x /app/scripts/start.sh

RUN uv sync --locked --no-dev

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["./scripts/start.sh"]
