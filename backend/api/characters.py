"""API routes for character creation and management."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from models.database import SessionLocal
from engine.character.ability_scores import AbilityScoreGenerator
from engine.character.races import RACES, get_race
from engine.character.classes import CLASSES, get_class, get_available_classes
from engine.character.creation import CharacterCreator
from models.character import Character as CharacterModel, Party as PartyModel

router = APIRouter(tags=["characters"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class RollAbilitiesRequest(BaseModel):
    method: int = 1  # 1-6


class ValidateRequest(BaseModel):
    race: str
    class_name: str
    ability_scores: dict[str, int]


class CreateCharacterRequest(BaseModel):
    name: str
    race: str
    class_name: str
    alignment: str
    ability_scores: dict[str, int]
    party_id: Optional[int] = None


class AllocateScoresRequest(BaseModel):
    scores: dict[str, int]


@router.post("/characters/roll-abilities")
async def roll_abilities(request: RollAbilitiesRequest):
    """Roll ability scores using the specified method (1-6)."""
    gen = AbilityScoreGenerator()
    methods = {
        1: gen.method_i,
        2: gen.method_ii,
        3: gen.method_iii,
        4: gen.method_iv,
        5: gen.method_v,
        6: gen.method_vi,
    }
    method_func = methods.get(request.method)
    if method_func is None:
        raise HTTPException(status_code=400, detail=f"Invalid method: {request.method}. Must be 1-6.")
    return method_func()


@router.post("/characters/validate-allocation")
async def validate_allocation(request: AllocateScoresRequest):
    """Validate a Method V point allocation."""
    gen = AbilityScoreGenerator()
    return gen.validate_method_v_allocation(request.scores)


@router.get("/characters/races")
async def get_races():
    """Get all available races with their details."""
    return {name: data for name, data in RACES.items()}


@router.get("/characters/classes")
async def get_classes():
    """Get all available character classes."""
    return {name: {k: v for k, v in data.items() if k != "thief_skills"} for name, data in CLASSES.items()}


@router.get("/characters/classes/{race}")
async def get_classes_for_race(race: str, str: int = 10, int_score: int = 10,
                                wis: int = 10, dex: int = 10, con: int = 10, cha: int = 10):
    """Get available classes for a given race and ability scores."""
    scores = {"str": str, "int": int_score, "wis": wis, "dex": dex, "con": con, "cha": cha}
    available = get_available_classes(race, scores)
    return {"race": race, "available_classes": available}


@router.post("/characters/validate")
async def validate_character(request: ValidateRequest):
    """Validate a race/class/ability score combination."""
    creator = CharacterCreator()
    return creator.validate_race_class(request.race, request.class_name, request.ability_scores)


@router.post("/characters/create")
async def create_character(request: CreateCharacterRequest, db: Session = Depends(get_db)):
    """Create a new character."""
    creator = CharacterCreator()
    try:
        character = creator.create_character(
            name=request.name,
            race=request.race,
            class_name=request.class_name,
            alignment=request.alignment,
            ability_scores=request.ability_scores,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Save to database
    db_char = CharacterModel(
        name=character["name"],
        race=character["race"],
        class_name=character["class_name"],
        level=character["level"],
        alignment=character["alignment"],
        str_score=character["str"],
        int_score=character["int"],
        wis_score=character["wis"],
        dex_score=character["dex"],
        con_score=character["con"],
        cha_score=character["cha"],
        hp=character["hp"],
        max_hp=character["max_hp"],
        ac=character["ac"],
        xp=0,
        gold=character["gold"],
        party_id=request.party_id,
    )
    db.add(db_char)
    db.commit()
    db.refresh(db_char)

    character["id"] = db_char.id
    return character


@router.get("/characters/{character_id}")
async def get_character(character_id: int, db: Session = Depends(get_db)):
    """Get a character by ID."""
    char = db.query(CharacterModel).filter(CharacterModel.id == character_id).first()
    if char is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return {
        "id": char.id,
        "name": char.name,
        "race": char.race,
        "class_name": char.class_name,
        "level": char.level,
        "alignment": char.alignment,
        "str": char.str_score,
        "int": char.int_score,
        "wis": char.wis_score,
        "dex": char.dex_score,
        "con": char.con_score,
        "cha": char.cha_score,
        "hp": char.hp,
        "max_hp": char.max_hp,
        "ac": char.ac,
        "xp": char.xp,
        "gold": char.gold,
    }


@router.get("/characters/party/{party_id}")
async def get_party_characters(party_id: int, db: Session = Depends(get_db)):
    """Get all characters in a party."""
    chars = db.query(CharacterModel).filter(CharacterModel.party_id == party_id).all()
    return [
        {
            "id": c.id, "name": c.name, "race": c.race,
            "class_name": c.class_name, "level": c.level,
            "hp": c.hp, "max_hp": c.max_hp, "ac": c.ac,
        }
        for c in chars
    ]


@router.post("/party/create")
async def create_party(name: str = "Adventurers", db: Session = Depends(get_db)):
    """Create a new party."""
    party = PartyModel(name=name)
    db.add(party)
    db.commit()
    db.refresh(party)
    return {"id": party.id, "name": party.name}
