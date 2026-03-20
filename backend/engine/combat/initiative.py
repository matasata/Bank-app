"""AD&D 1st Edition initiative systems.

Implements both side-based initiative (d6, per DMG) and individual
initiative (d10 + modifiers).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from engine.character.ability_scores import DiceRoller


@dataclass
class InitiativeEntry:
    """A single combatant's initiative result."""

    combatant_id: str
    name: str
    side: str  # "party" or "monsters" or a custom side name
    roll: int
    modifier: int
    total: int

    def as_dict(self) -> Dict:
        return {
            "combatant_id": self.combatant_id,
            "name": self.name,
            "side": self.side,
            "roll": self.roll,
            "modifier": self.modifier,
            "total": self.total,
        }


@dataclass
class InitiativeResult:
    """Complete initiative results for a round."""

    method: str  # "side" or "individual"
    entries: List[InitiativeEntry] = field(default_factory=list)
    order: List[str] = field(default_factory=list)  # combatant_ids in order
    ties: List[List[str]] = field(default_factory=list)

    def as_dict(self) -> Dict:
        return {
            "method": self.method,
            "entries": [e.as_dict() for e in self.entries],
            "order": self.order,
            "ties": self.ties,
        }


# ── Dexterity reaction/attacking adjustment (for individual initiative) ──
DEX_INITIATIVE_MOD: Dict[int, int] = {
    1: +5, 2: +4, 3: +3, 4: +2, 5: +1, 6: 0,
    7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0,
    15: 0, 16: -1, 17: -2, 18: -3, 19: -3,
}


def roll_side_initiative(
    party_members: List[Dict],
    monsters: List[Dict],
    seed: Optional[int] = None,
) -> InitiativeResult:
    """Roll side-based initiative (d6 per side).

    Each side rolls a d6; lower number goes first. Ties mean simultaneous
    action.

    Args:
        party_members: List of dicts with at least ``id`` and ``name``.
        monsters: List of dicts with at least ``id`` and ``name``.
        seed: Optional RNG seed.

    Returns:
        An ``InitiativeResult`` with all combatants ordered.
    """
    roller = DiceRoller(seed)
    result = InitiativeResult(method="side")

    party_roll = roller._rng.randint(1, 6)
    monster_roll = roller._rng.randint(1, 6)

    # Create entries for party
    for member in party_members:
        result.entries.append(InitiativeEntry(
            combatant_id=str(member["id"]),
            name=member["name"],
            side="party",
            roll=party_roll,
            modifier=0,
            total=party_roll,
        ))

    # Create entries for monsters
    for monster in monsters:
        result.entries.append(InitiativeEntry(
            combatant_id=str(monster["id"]),
            name=monster["name"],
            side="monsters",
            roll=monster_roll,
            modifier=0,
            total=monster_roll,
        ))

    # Determine order: lower roll goes first in AD&D side-based initiative
    if party_roll < monster_roll:
        first_side, second_side = "party", "monsters"
    elif monster_roll < party_roll:
        first_side, second_side = "monsters", "party"
    else:
        # Tie: simultaneous actions
        result.ties.append(["party", "monsters"])
        first_side, second_side = "party", "monsters"

    # Build ordered list
    for entry in result.entries:
        if entry.side == first_side:
            result.order.append(entry.combatant_id)
    for entry in result.entries:
        if entry.side == second_side:
            result.order.append(entry.combatant_id)

    return result


def roll_individual_initiative(
    combatants: List[Dict],
    seed: Optional[int] = None,
) -> InitiativeResult:
    """Roll individual initiative (d10 + modifiers).

    Each combatant rolls a d10 and adds their Dexterity-based modifier
    (and any weapon speed factor or spell casting time). Lower totals
    act first.

    Args:
        combatants: List of dicts with ``id``, ``name``, ``side``, and
            optionally ``dex`` (ability score), ``modifier`` (extra
            adjustment like weapon speed).
        seed: Optional RNG seed.

    Returns:
        An ``InitiativeResult`` sorted by total (ascending).
    """
    roller = DiceRoller(seed)
    result = InitiativeResult(method="individual")

    for c in combatants:
        roll = roller._rng.randint(1, 10)
        dex = c.get("dex", 10)
        dex_mod = DEX_INITIATIVE_MOD.get(dex, 0)
        extra_mod = c.get("modifier", 0)
        total_mod = dex_mod + extra_mod
        total = roll + total_mod

        result.entries.append(InitiativeEntry(
            combatant_id=str(c["id"]),
            name=c["name"],
            side=c.get("side", "unknown"),
            roll=roll,
            modifier=total_mod,
            total=total,
        ))

    # Sort by total ascending (lower goes first)
    result.entries.sort(key=lambda e: e.total)

    # Detect ties
    seen_totals: Dict[int, List[str]] = {}
    for entry in result.entries:
        seen_totals.setdefault(entry.total, []).append(entry.combatant_id)
    result.ties = [ids for ids in seen_totals.values() if len(ids) > 1]

    result.order = [e.combatant_id for e in result.entries]
    return result
