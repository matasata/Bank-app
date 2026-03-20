"""FastAPI router for combat encounter endpoints."""

from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from engine.combat.combat_round import (
    CombatManager,
    Combatant,
    DeclaredAction,
    ActionType,
)

router = APIRouter(prefix="/api/combat", tags=["combat"])

# ── In-memory combat store ────────────────────────────────────────────────
_active_combats: Dict[str, CombatManager] = {}


# ── Request / Response schemas ────────────────────────────────────────────

class CombatantSchema(BaseModel):
    """Schema for adding a combatant."""

    id: str
    name: str
    side: str = Field(..., description="'party' or 'monsters'")
    hp: int
    max_hp: int
    ac: int
    class_name: str = "Fighter"
    level: int = 1
    str_score: int = 10
    dex_score: int = 10
    is_monster: bool = False
    monster_hd: int = 1
    damage_dice_num: int = 1
    damage_dice_sides: int = 8
    magic_weapon_bonus: int = 0
    morale: int = 12


class StartCombatRequest(BaseModel):
    """Request to start a new combat encounter."""

    party: List[CombatantSchema]
    monsters: List[CombatantSchema]
    initiative_method: str = Field(
        "side",
        description="'side' (d6 per side) or 'individual' (d10 + mods)",
    )
    seed: Optional[int] = None


class InitiativeRequest(BaseModel):
    """Request to roll initiative for the current round."""

    combat_id: str


class ActionRequest(BaseModel):
    """Request to declare a combat action."""

    combat_id: str
    combatant_id: str
    action_type: str = Field(..., description="melee, missile, spell, movement, defend, flee, etc.")
    target_id: Optional[str] = None
    details: Dict = Field(default_factory=dict)


class ResolveRoundRequest(BaseModel):
    """Request to resolve the current combat round."""

    combat_id: str


# ── Endpoints ─────────────────────────────────────────────────────────────

@router.post("/start")
def start_combat(request: StartCombatRequest) -> Dict:
    """Start a new combat encounter with the given party and monsters.

    Returns the combat ID and initial state.
    """
    manager = CombatManager(
        initiative_method=request.initiative_method,
        seed=request.seed,
    )

    for member in request.party:
        manager.add_combatant(Combatant(
            id=member.id,
            name=member.name,
            side="party",
            hp=member.hp,
            max_hp=member.max_hp,
            ac=member.ac,
            class_name=member.class_name,
            level=member.level,
            str_score=member.str_score,
            dex_score=member.dex_score,
            is_monster=False,
            damage_dice_num=member.damage_dice_num,
            damage_dice_sides=member.damage_dice_sides,
            magic_weapon_bonus=member.magic_weapon_bonus,
            morale=12,
        ))

    for monster in request.monsters:
        manager.add_combatant(Combatant(
            id=monster.id,
            name=monster.name,
            side="monsters",
            hp=monster.hp,
            max_hp=monster.max_hp,
            ac=monster.ac,
            class_name=monster.class_name,
            level=monster.level,
            str_score=monster.str_score,
            dex_score=monster.dex_score,
            is_monster=True,
            monster_hd=monster.monster_hd,
            damage_dice_num=monster.damage_dice_num,
            damage_dice_sides=monster.damage_dice_sides,
            magic_weapon_bonus=monster.magic_weapon_bonus,
            morale=monster.morale,
        ))

    _active_combats[manager.id] = manager

    return {
        "combat_id": manager.id,
        "state": manager.get_state(),
    }


@router.post("/initiative")
def roll_initiative(request: InitiativeRequest) -> Dict:
    """Roll initiative for the current round.

    Returns the initiative order with individual roll breakdowns.
    """
    manager = _active_combats.get(request.combat_id)
    if manager is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Combat '{request.combat_id}' not found",
        )

    result = manager._roll_initiative()
    return result.as_dict()


@router.post("/action")
def declare_action(request: ActionRequest) -> Dict:
    """Declare a combat action for a combatant.

    Actions are queued and resolved when the round is resolved.
    """
    manager = _active_combats.get(request.combat_id)
    if manager is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Combat '{request.combat_id}' not found",
        )

    if request.combatant_id not in manager.combatants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Combatant '{request.combatant_id}' not in combat",
        )

    try:
        action_type = ActionType(request.action_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action type '{request.action_type}'. "
            f"Valid: {[a.value for a in ActionType]}",
        )

    action = DeclaredAction(
        combatant_id=request.combatant_id,
        action_type=action_type,
        target_id=request.target_id,
        details=request.details,
    )
    manager.declare_action(action)

    return {
        "message": f"Action '{action_type.value}' declared for {request.combatant_id}",
        "declared_actions": len(manager.declared_actions),
    }


@router.post("/resolve-round")
def resolve_round(request: ResolveRoundRequest) -> Dict:
    """Resolve the current combat round.

    Processes all declared actions in AD&D segment order (movement,
    missiles, melee, spells, other), performs morale checks, and returns
    a detailed round log.
    """
    manager = _active_combats.get(request.combat_id)
    if manager is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Combat '{request.combat_id}' not found",
        )

    if not manager.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Combat has already ended",
        )

    log = manager.resolve_round()

    # Clean up finished combats
    if not manager.is_active:
        # Keep for retrieval but mark as done
        pass

    return {
        "round_log": log.as_dict(),
        "combat_active": manager.is_active,
        "state": manager.get_state(),
    }


@router.get("/{combat_id}/state")
def get_combat_state(combat_id: str) -> Dict:
    """Retrieve the current state of a combat encounter."""
    manager = _active_combats.get(combat_id)
    if manager is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Combat '{combat_id}' not found",
        )
    return manager.get_state()
