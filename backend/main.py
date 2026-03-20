"""AD&D 1st Edition Game System -- FastAPI application entry point.

Configures CORS middleware, initialises the database on startup, includes
all API routers, and provides a health-check endpoint.

Run with::

    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.database import Base, engine
from api.characters import router as characters_router
from api.dungeon import router as dungeon_router
from api.combat import router as combat_router
from api.game import router as game_router
from api.modules import router as modules_router
from api.treasure import router as treasure_router

# Import models so SQLAlchemy registers them, then create tables eagerly.
# This ensures the DB schema exists both when running via uvicorn (lifespan)
# and when the module is imported by test clients.
import models.character  # noqa: F401

Base.metadata.create_all(bind=engine)


# ── Lifespan (startup / shutdown) ────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler.

    Tables are already created at import time; this hook is kept for any
    future async startup work.
    """
    yield


# ── Application setup ────────────────────────────────────────────────────

app = FastAPI(
    title="AD&D 1st Edition Game System",
    description=(
        "A complete backend for an Advanced Dungeons & Dragons 1st Edition "
        "game system, including character creation, combat resolution, "
        "dungeon generation, treasure, and encounter management."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS -- allow all origins during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include routers ──────────────────────────────────────────────────────

app.include_router(characters_router)
app.include_router(dungeon_router)
app.include_router(combat_router)
app.include_router(game_router)
app.include_router(modules_router)
app.include_router(treasure_router)


# ── Health check ─────────────────────────────────────────────────────────

@app.get("/api/health", tags=["system"])
def health_check() -> Dict[str, str]:
    """Simple health check endpoint.

    Returns ``{"status": "ok"}`` when the service is running.
    """
    return {"status": "ok"}
