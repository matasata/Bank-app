"""FastAPI entry point for the AD&D 1st Edition Game System."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from models.database import engine, Base
from api.characters import router as characters_router
from api.dungeon import router as dungeon_router
from api.combat import router as combat_router
from api.game import router as game_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="AD&D 1st Edition Game System",
    description="Complete AD&D 1st Edition game engine with character creation, dungeon generation, and combat",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(characters_router, prefix="/api")
app.include_router(dungeon_router, prefix="/api")
app.include_router(combat_router, prefix="/api")
app.include_router(game_router, prefix="/api")


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "game": "AD&D 1st Edition"}
