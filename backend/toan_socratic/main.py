import sentry_sdk
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sentry_sdk.integrations.fastapi import FastApiIntegration
from toan_socratic.config import settings
from toan_socratic.db.database import get_db
from toan_socratic.routers import admin, auth, problems, progress, sessions, users

_SENTRY_INITIALIZED = False


def init_sentry() -> None:
    global _SENTRY_INITIALIZED

    if _SENTRY_INITIALIZED or not settings.sentry_dsn:
        return

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        integrations=[FastApiIntegration()],
    )
    _SENTRY_INITIALIZED = True

def create_app(cors_origins: list[str] | None = None) -> FastAPI:
    init_sentry()
    app = FastAPI(
        title="Toán Socratic API",
        description="AI-powered Vietnamese math tutor for Grade 12 students",
        version="0.1.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins or settings.parsed_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(sessions.router)
    app.include_router(problems.router)
    app.include_router(progress.router)
    app.include_router(users.router)
    app.include_router(auth.router)
    app.include_router(admin.router)

    @app.get("/")
    async def root():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "Toán Socratic API",
            "version": "0.1.0"
        }

    @app.get("/health")
    async def health():
        """Health check endpoint"""
        return {"status": "ok"}

    @app.get("/ready")
    async def ready(db: AsyncSession = Depends(get_db)):
        """Readiness probe that verifies database connectivity."""
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
