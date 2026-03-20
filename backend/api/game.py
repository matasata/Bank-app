"""API routes for game session management."""
import json
import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

from models.database import SessionLocal
from models.character import GameSession

router = APIRouter(tags=["game"])

# In-memory settings (would persist to file/DB in production)
_game_settings = {
    "dice_method": 1,
    "optional_rules": {
        "weapon_vs_armor_type": False,
        "individual_initiative": False,
        "critical_hits": True,
        "bleeding_out": True,
    },
    "dungeon_defaults": {
        "level": 1,
        "size": "medium",
        "theme": "standard",
    },
    "auto_save_frequency": "every_action",
    "ui_theme": "dark",
    "sound_enabled": False,
    "module_directory": "modules",
}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class SaveGameRequest(BaseModel):
    name: str
    party_id: int
    dungeon_state: Optional[dict] = None
    map_state: Optional[dict] = None


class SettingsUpdate(BaseModel):
    settings: dict


@router.post("/game/save")
async def save_game(request: SaveGameRequest, db: Session = Depends(get_db)):
    """Save the current game state."""
    session = GameSession(
        name=request.name,
        party_id=request.party_id,
        dungeon_state=json.dumps(request.dungeon_state) if request.dungeon_state else None,
        map_state=json.dumps(request.map_state) if request.map_state else None,
        auto_save=False,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "id": session.id,
        "name": session.name,
        "saved_at": session.created_at.isoformat() if session.created_at else datetime.now().isoformat(),
    }


@router.get("/game/saves")
async def list_saves(db: Session = Depends(get_db)):
    """List all save slots."""
    saves = db.query(GameSession).order_by(GameSession.created_at.desc()).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "party_id": s.party_id,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "auto_save": s.auto_save,
        }
        for s in saves
    ]


@router.post("/game/load/{save_id}")
async def load_game(save_id: int, db: Session = Depends(get_db)):
    """Load a saved game."""
    session = db.query(GameSession).filter(GameSession.id == save_id).first()
    if session is None:
        raise HTTPException(status_code=404, detail="Save not found")

    return {
        "id": session.id,
        "name": session.name,
        "party_id": session.party_id,
        "dungeon_state": json.loads(session.dungeon_state) if session.dungeon_state else None,
        "map_state": json.loads(session.map_state) if session.map_state else None,
    }


@router.get("/game/settings")
async def get_settings():
    """Get current game settings."""
    return _game_settings


@router.put("/game/settings")
async def update_settings(update: SettingsUpdate):
    """Update game settings."""
    _game_settings.update(update.settings)
    return _game_settings


@router.get("/game/modules")
async def list_modules():
    """List available adventure modules."""
    module_dir = _game_settings.get("module_directory", "modules")
    modules = []

    if os.path.exists(module_dir):
        for filename in os.listdir(module_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(module_dir, filename)
                try:
                    with open(filepath) as f:
                        data = json.load(f)
                        modules.append({
                            "filename": filename,
                            "module_id": data.get("module_id", filename),
                            "title": data.get("title", "Untitled"),
                            "author": data.get("author", "Unknown"),
                            "description": data.get("description", ""),
                            "recommended_levels": data.get("recommended_levels", []),
                        })
                except (json.JSONDecodeError, OSError):
                    continue

    return modules


@router.get("/game/modules/{module_id}")
async def load_module(module_id: str):
    """Load a specific adventure module."""
    module_dir = _game_settings.get("module_directory", "modules")

    if os.path.exists(module_dir):
        for filename in os.listdir(module_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(module_dir, filename)
                try:
                    with open(filepath) as f:
                        data = json.load(f)
                        if data.get("module_id") == module_id:
                            return data
                except (json.JSONDecodeError, OSError):
                    continue

    raise HTTPException(status_code=404, detail=f"Module {module_id} not found")
