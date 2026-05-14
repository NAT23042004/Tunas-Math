from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from routers import admin, auth, problems, progress, sessions, users

def create_app(cors_origins: list[str] | None = None) -> FastAPI:
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

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
