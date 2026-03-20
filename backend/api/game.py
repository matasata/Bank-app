"""FastAPI router for game session management endpoints.

Provides save/load functionality, game settings management, and session
listing.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from models.database import get_db
from models.character import GameSession

router = APIRouter(prefix="/api/game", tags=["game"])


# ── In-memory settings store ─────────────────────────────────────────────
_game_settings: Dict = {
    "initiative_method": "side",
    "auto_save": True,
    "auto_save_interval_minutes": 5,
    "show_dice_rolls": True,
    "difficulty_modifier": 0,
    "fog_of_war": True,
    "allow_critical_hits": True,
    "encumbrance_tracking": False,
    "time_tracking": True,
}


# ── Request / Response schemas ────────────────────────────────────────────

class SaveGameRequest(BaseModel):
    """Request to save the current game state."""

    name: str = Field(..., min_length=1, max_length=128)
    party_id: Optional[int] = None
    dungeon_state: Optional[Dict] = None
    map_state: Optional[Dict] = None
    auto_save: bool = True


class LoadGameResponse(BaseModel):
    """Response when loading a game session."""

    id: int
    name: str
    party_id: Optional[int] = None
    dungeon_state: Optional[Dict] = None
    map_state: Optional[Dict] = None
    created_at: str
    updated_at: str
    auto_save: bool

    class Config:
        from_attributes = True


class GameSettingsUpdate(BaseModel):
    """Request to update game settings."""

    initiative_method: Optional[str] = None
    auto_save: Optional[bool] = None
    auto_save_interval_minutes: Optional[int] = None
    show_dice_rolls: Optional[bool] = None
    difficulty_modifier: Optional[int] = None
    fog_of_war: Optional[bool] = None
    allow_critical_hits: Optional[bool] = None
    encumbrance_tracking: Optional[bool] = None
    time_tracking: Optional[bool] = None


# ── Endpoints ─────────────────────────────────────────────────────────────

@router.post("/save")
def save_game(
    request: SaveGameRequest,
    db: Session = Depends(get_db),
) -> Dict:
    """Save the current game session to the database.

    Creates a new save slot or updates an existing one with the same name.
    Stores dungeon state and map state as JSON.
    """
    # Check if a save with this name already exists
    existing = (
        db.query(GameSession)
        .filter(GameSession.name == request.name)
        .first()
    )

    if existing:
        existing.dungeon_state = request.dungeon_state
        existing.map_state = request.map_state
        existing.party_id = request.party_id
        existing.auto_save = request.auto_save
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        session = existing
    else:
        session = GameSession(
            name=request.name,
            party_id=request.party_id,
            dungeon_state=request.dungeon_state,
            map_state=request.map_state,
            auto_save=request.auto_save,
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    return {
        "id": session.id,
        "name": session.name,
        "party_id": session.party_id,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
        "auto_save": session.auto_save,
        "message": "Game saved successfully",
    }


@router.get("/saves")
def list_saves(db: Session = Depends(get_db)) -> List[Dict]:
    """List all saved game sessions.

    Returns a summary of each save (no large JSON state fields) sorted
    by most recently updated.
    """
    sessions = (
        db.query(GameSession)
        .order_by(GameSession.updated_at.desc())
        .all()
    )
    return [
        {
            "id": s.id,
            "name": s.name,
            "party_id": s.party_id,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat(),
            "auto_save": s.auto_save,
            "has_dungeon": s.dungeon_state is not None,
            "has_map": s.map_state is not None,
        }
        for s in sessions
    ]


@router.post("/load/{session_id}")
def load_game(session_id: int, db: Session = Depends(get_db)) -> Dict:
    """Load a saved game session by ID.

    Returns the full session data including dungeon and map state JSON.
    """
    session = (
        db.query(GameSession)
        .filter(GameSession.id == session_id)
        .first()
    )
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game session with id {session_id} not found",
        )

    return {
        "id": session.id,
        "name": session.name,
        "party_id": session.party_id,
        "dungeon_state": session.dungeon_state,
        "map_state": session.map_state,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
        "auto_save": session.auto_save,
    }


@router.get("/settings")
def get_settings() -> Dict:
    """Return the current game settings."""
    return dict(_game_settings)


@router.put("/settings")
def update_settings(request: GameSettingsUpdate) -> Dict:
    """Update game settings.

    Only fields present in the request body are updated; unset fields
    retain their current values.
    """
    updates = request.model_dump(exclude_unset=True)

    # Validate initiative method
    if "initiative_method" in updates:
        if updates["initiative_method"] not in ("side", "individual"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="initiative_method must be 'side' or 'individual'",
            )

    # Validate difficulty modifier
    if "difficulty_modifier" in updates:
        mod = updates["difficulty_modifier"]
        if not isinstance(mod, int) or mod < -5 or mod > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="difficulty_modifier must be an integer between -5 and 5",
            )

    _game_settings.update(updates)
    return {
        "message": "Settings updated",
        "settings": dict(_game_settings),
    }
