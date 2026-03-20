"""API routes for dungeon generation and exploration."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from engine.dungeon.generator import DungeonGenerator, generate_dungeon
from engine.encounter.tables import generate_encounter, check_wandering_monster

router = APIRouter(tags=["dungeon"])

# In-memory dungeon state (would be in DB in production)
_active_dungeons: dict[str, dict] = {}
_dungeon_counter = 0


class GenerateDungeonRequest(BaseModel):
    level: int = 1
    num_rooms: int = 10
    width: int = 200
    height: int = 200
    theme: str = "standard"
    seed: Optional[int] = None


class MoveRequest(BaseModel):
    direction: str  # "north", "south", "east", "west"
    room_id: Optional[str] = None


class InteractRequest(BaseModel):
    target_type: str  # "door", "room", "chest", "trap"
    target_id: str
    action: str  # "open", "listen", "search", "detect_traps"


@router.post("/dungeon/generate")
async def generate_dungeon_endpoint(request: GenerateDungeonRequest):
    """Generate a new random dungeon."""
    global _dungeon_counter
    _dungeon_counter += 1
    dungeon_id = f"dungeon_{_dungeon_counter}"

    dungeon = generate_dungeon(
        dungeon_level=request.level,
        num_rooms=request.num_rooms,
        map_width=request.width,
        map_height=request.height,
        theme=request.theme,
        seed=request.seed,
    )
    dungeon["id"] = dungeon_id
    dungeon["party_position"] = {"room_index": 0}
    dungeon["explored_rooms"] = [0]
    dungeon["turn_count"] = 0

    _active_dungeons[dungeon_id] = dungeon
    return dungeon


@router.get("/dungeon/{dungeon_id}")
async def get_dungeon(dungeon_id: str):
    """Get the current state of a dungeon."""
    dungeon = _active_dungeons.get(dungeon_id)
    if dungeon is None:
        raise HTTPException(status_code=404, detail="Dungeon not found")
    return dungeon


@router.post("/dungeon/{dungeon_id}/move")
async def move_in_dungeon(dungeon_id: str, request: MoveRequest):
    """Move the party within the dungeon."""
    dungeon = _active_dungeons.get(dungeon_id)
    if dungeon is None:
        raise HTTPException(status_code=404, detail="Dungeon not found")

    dungeon["turn_count"] = dungeon.get("turn_count", 0) + 1
    current_room_idx = dungeon["party_position"]["room_index"]
    rooms = dungeon.get("rooms", [])

    # Find target room based on direction or room_id
    if request.room_id:
        target_idx = next(
            (i for i, r in enumerate(rooms) if r.get("id") == request.room_id),
            None
        )
    else:
        # Simple: move to next/previous room
        if request.direction in ("north", "east"):
            target_idx = min(current_room_idx + 1, len(rooms) - 1)
        else:
            target_idx = max(current_room_idx - 1, 0)

    if target_idx is None:
        raise HTTPException(status_code=400, detail="Invalid destination")

    dungeon["party_position"]["room_index"] = target_idx
    if target_idx not in dungeon["explored_rooms"]:
        dungeon["explored_rooms"].append(target_idx)

    result = {
        "moved_to": rooms[target_idx] if target_idx < len(rooms) else None,
        "turn_count": dungeon["turn_count"],
    }

    # Wandering monster check every 3 turns
    if dungeon["turn_count"] % 3 == 0 and check_wandering_monster():
        result["wandering_monster"] = generate_encounter(dungeon.get("level", 1))

    return result


@router.post("/dungeon/{dungeon_id}/interact")
async def interact_in_dungeon(dungeon_id: str, request: InteractRequest):
    """Interact with something in the dungeon."""
    dungeon = _active_dungeons.get(dungeon_id)
    if dungeon is None:
        raise HTTPException(status_code=404, detail="Dungeon not found")

    import random
    result: dict = {"target_type": request.target_type, "action": request.action}

    if request.action == "listen":
        # Listen at door - 15% chance to hear something
        heard = random.random() < 0.15
        result["heard_something"] = heard
        if heard:
            result["description"] = random.choice([
                "You hear shuffling footsteps beyond.",
                "Faint growling echoes from the other side.",
                "You hear nothing but dripping water.",
                "Muffled voices can be heard.",
                "A scraping sound comes from beyond.",
            ])
        else:
            result["description"] = "You hear nothing."

    elif request.action == "open":
        # Try to open a door
        roll = random.randint(1, 6)
        opened = roll <= 2  # Open on 1-2 on d6
        result["opened"] = opened
        result["roll"] = roll
        if opened:
            result["description"] = "The door opens!"
        else:
            result["description"] = "The door won't budge."

    elif request.action == "search":
        # Search for traps/secret doors
        roll = random.randint(1, 6)
        found = roll == 1  # Find on 1 on d6 (elves get 1-2)
        result["found_something"] = found
        result["roll"] = roll
        if found:
            result["description"] = "You discover a hidden mechanism!"
        else:
            result["description"] = "You find nothing unusual."

    elif request.action == "detect_traps":
        roll = random.randint(1, 100)
        result["roll"] = roll
        result["description"] = "You check for traps."

    return result
