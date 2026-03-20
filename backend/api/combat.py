"""API routes for combat management."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from engine.combat.initiative import InitiativeManager
from engine.combat.attack import AttackResolver

router = APIRouter(tags=["combat"])

# In-memory combat state
_active_combats: dict[str, dict] = {}
_combat_counter = 0


class StartCombatRequest(BaseModel):
    party: list[dict]
    monsters: list[dict]
    initiative_method: str = "side"  # "side" or "individual"


class CombatActionRequest(BaseModel):
    combatant_name: str
    action_type: str  # "attack", "cast", "move", "use_item", "defend", "flee"
    target: Optional[str] = None
    spell_name: Optional[str] = None
    details: dict = {}


class ResolveRoundRequest(BaseModel):
    combat_id: str
    actions: list[CombatActionRequest]


@router.post("/combat/start")
async def start_combat(request: StartCombatRequest):
    """Start a new combat encounter."""
    global _combat_counter
    _combat_counter += 1
    combat_id = f"combat_{_combat_counter}"

    # Initialize combat state
    initiative_mgr = InitiativeManager()
    surprise = initiative_mgr.resolve_surprise()

    combatants = {}
    for p in request.party:
        combatants[p["name"]] = {
            **p,
            "side": "party",
            "is_alive": True,
            "conditions": [],
        }
    for m in request.monsters:
        name = m["name"]
        if name in combatants:
            count = sum(1 for k in combatants if k.startswith(m["name"]))
            name = f"{m['name']} #{count + 1}"
        combatants[name] = {
            **m,
            "name": name,
            "side": "monsters",
            "is_alive": True,
            "conditions": [],
        }

    combat_state = {
        "id": combat_id,
        "round": 0,
        "is_active": True,
        "combatants": combatants,
        "log": [f"Combat begins! {surprise}"],
        "surprise": surprise,
        "initiative_method": request.initiative_method,
    }

    _active_combats[combat_id] = combat_state
    return combat_state


@router.post("/combat/initiative")
async def roll_initiative(combat_id: str):
    """Roll initiative for the current round."""
    combat = _active_combats.get(combat_id)
    if not combat:
        raise HTTPException(status_code=404, detail="Combat not found")

    mgr = InitiativeManager()
    if combat["initiative_method"] == "individual":
        combatants_list = [
            {"name": name, "dex_modifier": c.get("dex_modifier", 0), "weapon_speed": c.get("weapon_speed", 5)}
            for name, c in combat["combatants"].items()
            if c["is_alive"]
        ]
        result = mgr.roll_individual_initiative(combatants_list)
        return {"method": "individual", "order": result}
    else:
        result = mgr.roll_side_initiative()
        return {"method": "side", **result}


@router.post("/combat/resolve-round")
async def resolve_round(request: ResolveRoundRequest):
    """Resolve a full combat round."""
    combat = _active_combats.get(request.combat_id)
    if not combat:
        raise HTTPException(status_code=404, detail="Combat not found")
    if not combat["is_active"]:
        raise HTTPException(status_code=400, detail="Combat is already over")

    combat["round"] += 1
    round_log = [f"--- Round {combat['round']} ---"]

    # Roll initiative
    mgr = InitiativeManager()
    initiative = mgr.roll_side_initiative()
    round_log.append(f"Initiative: Party {initiative['party']}, Monsters {initiative['monsters']}")

    resolver = AttackResolver()

    # Process party actions
    import random
    for action in request.actions:
        combatant = combat["combatants"].get(action.combatant_name)
        if not combatant or not combatant["is_alive"]:
            continue

        if action.action_type == "attack" and action.target:
            target = combat["combatants"].get(action.target)
            if target and target["is_alive"]:
                result = resolver.resolve_attack(
                    attacker_class=combatant.get("class_name", "fighter"),
                    attacker_level=combatant.get("level", 1),
                    target_ac=target.get("ac", 10),
                )
                if result["hit"]:
                    damage = resolver.resolve_damage(
                        combatant.get("damage", "1d8")
                    )
                    target["hp"] = target.get("hp", 10) - damage["total"]
                    round_log.append(
                        f"{action.combatant_name} hits {action.target} for {damage['total']} damage! "
                        f"(roll: {result['natural_roll']}, need: {result['needed']})"
                    )
                    if target["hp"] <= 0:
                        target["is_alive"] = False
                        round_log.append(f"{action.target} is slain!")
                else:
                    round_log.append(
                        f"{action.combatant_name} misses {action.target} "
                        f"(roll: {result['natural_roll']}, need: {result['needed']})"
                    )
            elif action.action_type == "cast":
                round_log.append(f"{action.combatant_name} casts {action.spell_name}!")

    # Monster actions (basic AI)
    party_alive = [
        name for name, c in combat["combatants"].items()
        if c["side"] == "party" and c["is_alive"]
    ]
    for name, monster in combat["combatants"].items():
        if monster["side"] != "monsters" or not monster["is_alive"]:
            continue
        if not party_alive:
            break

        target_name = random.choice(party_alive)
        target = combat["combatants"][target_name]
        result = resolver.resolve_attack(
            attacker_class="monster",
            attacker_level=monster.get("hd", 1),
            target_ac=target.get("ac", 10),
        )
        if result["hit"]:
            damage = resolver.resolve_damage(monster.get("damage", "1d6"))
            target["hp"] = target.get("hp", 10) - damage["total"]
            round_log.append(
                f"{name} hits {target_name} for {damage['total']} damage!"
            )
            if target["hp"] <= 0:
                target["is_alive"] = False
                round_log.append(f"{target_name} falls!")
                party_alive.remove(target_name)
        else:
            round_log.append(f"{name} misses {target_name}")

    # Check combat end
    party_alive_check = any(
        c["is_alive"] for c in combat["combatants"].values() if c["side"] == "party"
    )
    monsters_alive = any(
        c["is_alive"] for c in combat["combatants"].values() if c["side"] == "monsters"
    )

    if not party_alive_check:
        round_log.append("The party has been defeated!")
        combat["is_active"] = False
    elif not monsters_alive:
        total_xp = sum(
            c.get("xp_value", 0) for c in combat["combatants"].values()
            if c["side"] == "monsters"
        )
        round_log.append(f"Victory! Total XP: {total_xp}")
        combat["is_active"] = False

    combat["log"].extend(round_log)

    return {
        "round": combat["round"],
        "initiative": initiative,
        "log": round_log,
        "combatants": combat["combatants"],
        "is_active": combat["is_active"],
    }


@router.get("/combat/{combat_id}/state")
async def get_combat_state(combat_id: str):
    """Get the current combat state."""
    combat = _active_combats.get(combat_id)
    if not combat:
        raise HTTPException(status_code=404, detail="Combat not found")
    return combat
