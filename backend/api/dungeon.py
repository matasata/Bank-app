"""FastAPI router for dungeon generation and exploration endpoints."""

from __future__ import annotations

from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from engine.dungeon.generator import generate_dungeon, DungeonGenerator

router = APIRouter(prefix="/api/dungeon", tags=["dungeon"])

# ── In-memory dungeon store (production would use DB) ────────────────────
_active_dungeons: Dict[str, Dict] = {}
_dungeon_counter: int = 0


def _next_dungeon_id() -> str:
    """Generate a sequential dungeon ID."""
    global _dungeon_counter
    _dungeon_counter += 1
    return str(_dungeon_counter)


# ── Request / Response schemas ────────────────────────────────────────────

class GenerateDungeonRequest(BaseModel):
    """Request to generate a new dungeon level."""

    dungeon_level: int = Field(1, ge=1, le=20, description="Difficulty level")
    num_rooms: int = Field(10, ge=1, le=100, description="Number of rooms")
    map_width: int = Field(200, ge=100, le=1000, description="Map width in feet")
    map_height: int = Field(200, ge=100, le=1000, description="Map height in feet")
    theme: str = Field("standard", description="Theme: standard, crypt, cavern, temple, sewers")
    seed: Optional[int] = Field(None, description="RNG seed for reproducibility")


class MoveRequest(BaseModel):
    """Request to move the party within a dungeon."""

    direction: str = Field(..., description="Direction: north, south, east, west")
    room_id: Optional[str] = Field(None, description="Specific room to enter")


class InteractRequest(BaseModel):
    """Request to interact with a dungeon feature."""

    action: str = Field(..., description="Action: search, open_door, disarm_trap, listen, rest")
    target_id: Optional[str] = Field(None, description="ID of the target object")
    details: Dict = Field(default_factory=dict, description="Additional action parameters")


# ── Endpoints ─────────────────────────────────────────────────────────────

@router.post("/generate")
def generate(request: GenerateDungeonRequest) -> Dict:
    """Generate a new random dungeon level.

    Returns the complete dungeon data including rooms, passages, doors,
    traps, and special features.
    """
    dungeon_data = generate_dungeon(
        dungeon_level=request.dungeon_level,
        num_rooms=request.num_rooms,
        map_width=request.map_width,
        map_height=request.map_height,
        theme=request.theme,
        seed=request.seed,
    )

    dungeon_id = _next_dungeon_id()
    state = {
        "id": dungeon_id,
        "dungeon": dungeon_data,
        "party_position": {
            "room_index": 0,
            "x": dungeon_data["rooms"][0]["x"] if dungeon_data["rooms"] else 0,
            "y": dungeon_data["rooms"][0]["y"] if dungeon_data["rooms"] else 0,
        },
        "explored_rooms": [0] if dungeon_data["rooms"] else [],
        "events": [],
    }

    # Mark first room as explored
    if dungeon_data["rooms"]:
        dungeon_data["rooms"][0]["explored"] = True

    _active_dungeons[dungeon_id] = state

    return state


@router.get("/{dungeon_id}")
def get_dungeon(dungeon_id: str) -> Dict:
    """Retrieve the current state of a dungeon."""
    state = _active_dungeons.get(dungeon_id)
    if state is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dungeon with id '{dungeon_id}' not found",
        )
    return state


@router.post("/{dungeon_id}/move")
def move_in_dungeon(dungeon_id: str, request: MoveRequest) -> Dict:
    """Move the party within the dungeon.

    Handles door checking, trap triggering, and room discovery.
    """
    state = _active_dungeons.get(dungeon_id)
    if state is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dungeon with id '{dungeon_id}' not found",
        )

    dungeon = state["dungeon"]
    rooms = dungeon["rooms"]
    current_room_idx = state["party_position"]["room_index"]

    if current_room_idx >= len(rooms):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid current position",
        )

    current_room = rooms[current_room_idx]

    # Find an exit in the requested direction
    matching_exit = None
    for door in current_room.get("exits", []):
        if door["direction"] == request.direction:
            matching_exit = door
            break

    events: list = []

    if matching_exit is None:
        events.append({
            "type": "blocked",
            "message": f"There is no exit to the {request.direction}.",
        })
        return {"success": False, "events": events, "state": state}

    # Check for locked door
    if matching_exit.get("locked"):
        events.append({
            "type": "locked_door",
            "message": f"The {matching_exit['door_type']} door to the {request.direction} is locked!",
            "door_id": matching_exit["id"],
        })
        return {"success": False, "events": events, "state": state}

    # Check for trapped door
    if matching_exit.get("trapped"):
        events.append({
            "type": "trap_triggered",
            "message": f"A trap activates as you open the door! ({matching_exit.get('trap_type', 'unknown')})",
            "trap_type": matching_exit.get("trap_type"),
            "door_id": matching_exit["id"],
        })
        # Mark trap as sprung
        matching_exit["trapped"] = False

    # Move to next room
    next_room_idx = min(current_room_idx + 1, len(rooms) - 1)
    if request.room_id:
        for idx, room in enumerate(rooms):
            if room["id"] == request.room_id:
                next_room_idx = idx
                break

    state["party_position"] = {
        "room_index": next_room_idx,
        "x": rooms[next_room_idx]["x"],
        "y": rooms[next_room_idx]["y"],
    }

    # Mark room as explored
    if next_room_idx not in state["explored_rooms"]:
        state["explored_rooms"].append(next_room_idx)
        rooms[next_room_idx]["explored"] = True
        events.append({
            "type": "new_room",
            "message": rooms[next_room_idx].get("description", "You enter a new area."),
            "room": rooms[next_room_idx],
        })

        # Check room contents
        contents = rooms[next_room_idx].get("contents", "empty")
        if contents == "monster" or contents == "monster_with_treasure":
            events.append({
                "type": "encounter",
                "message": "Monsters are here!",
                "contents": contents,
            })
        elif contents == "treasure":
            events.append({
                "type": "treasure",
                "message": "You spot treasure!",
            })
        elif contents == "trick_trap":
            events.append({
                "type": "room_trap",
                "message": "You sense danger...",
                "trap_type": rooms[next_room_idx].get("trap"),
            })
        elif contents == "special":
            events.append({
                "type": "special",
                "message": rooms[next_room_idx].get("special", "Something unusual here."),
            })

    state["events"].extend(events)
    return {"success": True, "events": events, "state": state}


@router.post("/{dungeon_id}/interact")
def interact_in_dungeon(dungeon_id: str, request: InteractRequest) -> Dict:
    """Interact with a feature in the current room.

    Supports actions like searching, opening doors, disarming traps,
    listening, and resting.
    """
    state = _active_dungeons.get(dungeon_id)
    if state is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dungeon with id '{dungeon_id}' not found",
        )

    dungeon = state["dungeon"]
    rooms = dungeon["rooms"]
    current_room_idx = state["party_position"]["room_index"]
    current_room = rooms[current_room_idx]
    events: list = []

    if request.action == "search":
        # Check for secret doors
        secret_exits = [
            d for d in current_room.get("exits", []) if d.get("secret")
        ]
        if secret_exits:
            # 1-2 on d6 for elves, 1 on d6 for others
            import random
            roll = random.randint(1, 6)
            if roll <= 2:
                for door in secret_exits:
                    door["secret"] = False
                events.append({
                    "type": "secret_found",
                    "message": "You discovered a secret door!",
                    "roll": roll,
                })
            else:
                events.append({
                    "type": "search_result",
                    "message": "Your search reveals nothing unusual.",
                    "roll": roll,
                })
        else:
            events.append({
                "type": "search_result",
                "message": "You find nothing of note.",
            })

    elif request.action == "open_door":
        target_door = None
        for door in current_room.get("exits", []):
            if door["id"] == request.target_id:
                target_door = door
                break

        if target_door is None:
            events.append({
                "type": "error",
                "message": "No such door found.",
            })
        elif target_door.get("locked"):
            # Attempt to force open (Str check or thief skill)
            import random
            roll = random.randint(1, 6)
            if roll <= 2:
                target_door["locked"] = False
                events.append({
                    "type": "door_opened",
                    "message": "You force the door open!",
                    "roll": roll,
                })
            else:
                events.append({
                    "type": "door_stuck",
                    "message": "The door resists your efforts.",
                    "roll": roll,
                })
        else:
            events.append({
                "type": "door_opened",
                "message": "The door opens easily.",
            })

    elif request.action == "disarm_trap":
        if current_room.get("trap"):
            import random
            roll = random.randint(1, 100)
            # Base 25% chance, modified by thief level
            if roll <= 25:
                current_room["trap"] = None
                events.append({
                    "type": "trap_disarmed",
                    "message": "The trap has been successfully disarmed!",
                    "roll": roll,
                })
            else:
                events.append({
                    "type": "disarm_failed",
                    "message": "You fail to disarm the trap!",
                    "roll": roll,
                })
        else:
            events.append({
                "type": "no_trap",
                "message": "There is no trap here to disarm.",
            })

    elif request.action == "listen":
        import random
        roll = random.randint(1, 6)
        if roll == 1:
            events.append({
                "type": "listen_success",
                "message": "You hear sounds beyond the door...",
                "roll": roll,
            })
        else:
            events.append({
                "type": "listen_fail",
                "message": "You hear nothing.",
                "roll": roll,
            })

    elif request.action == "rest":
        # Resting triggers a wandering monster check
        from engine.encounter.tables import check_wandering_monster
        encounter = check_wandering_monster(
            dungeon_level=dungeon["level"],
        )
        if encounter.encounter_occurred:
            events.append({
                "type": "wandering_monster",
                "message": "Your rest is interrupted by wandering monsters!",
                "encounter": encounter.as_dict(),
            })
        else:
            events.append({
                "type": "rest_success",
                "message": "You rest without incident.",
            })
    else:
        events.append({
            "type": "unknown_action",
            "message": f"Unknown action: {request.action}",
        })

    state["events"].extend(events)
    return {"events": events, "state": state}
