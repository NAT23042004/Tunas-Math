from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import sessions

app = FastAPI(
    title="Toán Socratic API",
    description="AI-powered Vietnamese math tutor for Grade 12 students",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sessions.router)


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)