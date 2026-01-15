"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    settings.ensure_storage_dirs()
    await init_db()
    print(f"🚀 Meeting Transcription & Analyzer API started on {settings.host}:{settings.port}")
    yield
    # Shutdown
    print("👋 Shutting down...")


app = FastAPI(
    title="Meeting Transcription & Analyzer API",
    description="API for transcribing and analyzing meeting recordings",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "status": "healthy",
        "message": "Meeting Transcription & Analyzer API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Import and include routers after app is created to avoid circular imports
def include_routers():
    from app.routers import media, transcription, processing, persona, template, benchmark, settings
    
    app.include_router(media.router, prefix="/api/media", tags=["Media"])
    app.include_router(transcription.router, prefix="/api/transcriptions", tags=["Transcriptions"])
    app.include_router(processing.router, prefix="/api/process", tags=["Processing"])
    app.include_router(persona.router, prefix="/api/personas", tags=["Personas"])
    app.include_router(template.router, prefix="/api/templates", tags=["Templates"])
    app.include_router(benchmark.router, prefix="/api/benchmark", tags=["Benchmark"])
    app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])


include_routers()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
