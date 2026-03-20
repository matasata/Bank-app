"""FastAPI router for character-related endpoints.

Provides ability score rolling, race/class lookup, validation, character
creation, and character retrieval.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from models.database import get_db
from models.character import Character as CharacterModel, Party
from engine.character.ability_scores import generate_ability_scores, ABILITY_NAMES
from engine.character.races import list_races, get_race
from engine.character.classes import list_classes, get_class
from engine.character.creation import validate_race_class, create_character

router = APIRouter(prefix="/api/characters", tags=["characters"])


# ── Request / Response schemas ────────────────────────────────────────────

class RollAbilitiesRequest(BaseModel):
    """Request to roll ability scores."""

    method: str = Field("I", description="Generation method: I-VI")
    seed: Optional[int] = Field(None, description="Optional RNG seed")
    allocation: Optional[Dict[str, int]] = Field(
        None, description="Point allocation for Method V"
    )


class ValidateRequest(BaseModel):
    """Request to validate a race/class/ability combination."""

    race: str
    class_name: str
    abilities: Dict[str, int]
    alignment: Optional[str] = None


class CreateCharacterRequest(BaseModel):
    """Request to create a new character."""

    name: str = Field(..., min_length=1, max_length=128)
    race: str
    class_name: str
    abilities: Dict[str, int]
    alignment: str
    level: int = Field(1, ge=1, le=20)
    party_id: Optional[int] = None
    seed: Optional[int] = None


class CharacterResponse(BaseModel):
    """Character data returned to the client."""

    id: int
    name: str
    race: str
    class_name: str
    level: int
    alignment: str
    abilities: Dict[str, int]
    hp: int
    max_hp: int
    ac: int
    xp: int
    gold: float
    party_id: Optional[int] = None

    class Config:
        from_attributes = True


# ── Endpoints ─────────────────────────────────────────────────────────────

@router.post("/roll-abilities")
def roll_abilities(request: RollAbilitiesRequest) -> Dict:
    """Roll ability scores using one of the six DMG methods.

    Returns the full roll details so the UI can animate / display what was
    rolled and what was kept.
    """
    try:
        result = generate_ability_scores(
            method=request.method,
            seed=request.seed,
            allocation=request.allocation,
        )
        return result.as_dict()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get("/races")
def get_races() -> List[Dict]:
    """Return all available player races with their attributes."""
    return list_races()


@router.get("/classes")
def get_classes() -> List[Dict]:
    """Return all available character classes with their attributes."""
    return list_classes()


@router.post("/validate")
def validate_character(request: ValidateRequest) -> Dict:
    """Check whether a race/class/ability combination is valid.

    Returns ``{"valid": true/false, "errors": [...], "warnings": [...]}``.
    """
    result = validate_race_class(
        race_name=request.race,
        class_name=request.class_name,
        abilities=request.abilities,
        alignment=request.alignment,
    )
    return {
        "valid": result.valid,
        "errors": result.errors,
        "warnings": result.warnings,
    }


@router.post("/create")
def create_new_character(
    request: CreateCharacterRequest,
    db: Session = Depends(get_db),
) -> Dict:
    """Create a new character, persist it, and return the full sheet.

    The character creation engine validates the combination, applies racial
    modifiers, rolls HP and gold, and computes all derived statistics.
    """
    try:
        created = create_character(
            name=request.name,
            race_name=request.race,
            class_name=request.class_name,
            abilities=request.abilities,
            alignment=request.alignment,
            level=request.level,
            seed=request.seed,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    # Persist to database
    db_char = CharacterModel(
        name=created.name,
        race=created.race,
        class_name=created.class_name,
        level=created.level,
        alignment=created.alignment,
        str=created.abilities.get("str", 10),
        int=created.abilities.get("int", 10),
        wis=created.abilities.get("wis", 10),
        dex=created.abilities.get("dex", 10),
        con=created.abilities.get("con", 10),
        cha=created.abilities.get("cha", 10),
        hp=created.hp,
        max_hp=created.max_hp,
        ac=created.ac,
        xp=created.xp,
        gold=created.gold,
        party_id=request.party_id,
    )
    db.add(db_char)
    db.commit()
    db.refresh(db_char)

    response = created.as_dict()
    response["id"] = db_char.id
    return response


@router.get("/{character_id}")
def get_character(character_id: int, db: Session = Depends(get_db)) -> Dict:
    """Retrieve a character by ID."""
    char = db.query(CharacterModel).filter(CharacterModel.id == character_id).first()
    if char is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with id {character_id} not found",
        )
    return {
        "id": char.id,
        "name": char.name,
        "race": char.race,
        "class_name": char.class_name,
        "level": char.level,
        "alignment": char.alignment,
        "abilities": {
            "str": char.str,
            "int": char.int,
            "wis": char.wis,
            "dex": char.dex,
            "con": char.con,
            "cha": char.cha,
        },
        "hp": char.hp,
        "max_hp": char.max_hp,
        "ac": char.ac,
        "xp": char.xp,
        "gold": char.gold,
        "party_id": char.party_id,
    }


@router.get("/party/{party_id}")
def get_party_characters(party_id: int, db: Session = Depends(get_db)) -> Dict:
    """Retrieve all characters belonging to a party."""
    party = db.query(Party).filter(Party.id == party_id).first()
    if party is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Party with id {party_id} not found",
        )

    characters = (
        db.query(CharacterModel)
        .filter(CharacterModel.party_id == party_id)
        .all()
    )
    return {
        "party": {"id": party.id, "name": party.name},
        "characters": [
            {
                "id": c.id,
                "name": c.name,
                "race": c.race,
                "class_name": c.class_name,
                "level": c.level,
                "hp": c.hp,
                "max_hp": c.max_hp,
            }
            for c in characters
        ],
    }
