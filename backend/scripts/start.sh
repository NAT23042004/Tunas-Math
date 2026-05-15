#!/bin/sh

set -eu

uv run alembic upgrade head
uv run python -m toan_socratic.init_db
exec uv run uvicorn toan_socratic.main:app --host 0.0.0.0 --port "${PORT:-8000}"
