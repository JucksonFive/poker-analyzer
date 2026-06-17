"""FastAPI application factory and configuration."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.src.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: creates tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Poker Analytics Platform API",
        description="REST API for Texas Hold'em hand history analysis",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS — allow the Vite dev server and production origin
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # Vite dev server
            "http://localhost:8000",  # Production
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    from backend.src.api import hands, import_, analytics, players, sessions, ai

    app.include_router(hands.router, prefix="/api/hands", tags=["Hands"])
    app.include_router(import_.router, prefix="/api/import", tags=["Import"])
    app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
    app.include_router(players.router, prefix="/api/players", tags=["Players"])
    app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])
    app.include_router(ai.router, prefix="/api/ai", tags=["AI Assistant"])

    @app.get("/api/health")
    async def health_check():
        return {"status": "ok", "version": "0.1.0"}

    return app


app = create_app()
