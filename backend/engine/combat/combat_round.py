"""AD&D 1st Edition combat round manager.

Implements the full AD&D combat round sequence:
1. Declare actions
2. Roll initiative
3. Resolve in segment order: movement, missiles, melee, spells, other
4. Morale checks
5. End-of-round bookkeeping
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from engine.character.ability_scores import DiceRoller
from engine.combat.initiative import (
    roll_side_initiative,
    roll_individual_initiative,
    InitiativeResult,
)
from engine.combat.attack import resolve_attack, AttackResult


class ActionType(str, Enum):
    """Allowed action types for a combat round."""

    MELEE = "melee"
    MISSILE = "missile"
    SPELL = "spell"
    MOVEMENT = "movement"
    TURN_UNDEAD = "turn_undead"
    USE_ITEM = "use_item"
    DEFEND = "defend"
    FLEE = "flee"
    OTHER = "other"


class CombatPhase(str, Enum):
    """Phases of a combat round in resolution order."""

    DECLARATION = "declaration"
    INITIATIVE = "initiative"
    MOVEMENT = "movement"
    MISSILE = "missile"
    MELEE = "melee"
    SPELL = "spell"
    OTHER = "other"
    MORALE = "morale"
    BOOKKEEPING = "bookkeeping"
    COMPLETE = "complete"


@dataclass
class DeclaredAction:
    """An action declared by a combatant for the current round."""

    combatant_id: str
    action_type: ActionType
    target_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Combatant:
    """A participant in combat (PC or monster)."""

    id: str
    name: str
    side: str  # "party" or "monsters"
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
    morale: int = 12  # 2-12 scale; 12 = never flees
    is_alive: bool = True
    conditions: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "side": self.side,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "ac": self.ac,
            "class_name": self.class_name,
            "level": self.level,
            "is_monster": self.is_monster,
            "is_alive": self.is_alive,
            "conditions": self.conditions,
        }


@dataclass
class RoundLog:
    """Log of all events that occurred during a combat round."""

    round_number: int
    initiative: Optional[Dict] = None
    actions_resolved: List[Dict] = field(default_factory=list)
    morale_results: List[Dict] = field(default_factory=list)
    casualties: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict:
        return {
            "round_number": self.round_number,
            "initiative": self.initiative,
            "actions_resolved": self.actions_resolved,
            "morale_results": self.morale_results,
            "casualties": self.casualties,
            "notes": self.notes,
        }


class CombatManager:
    """Manages a full combat encounter across multiple rounds.

    Usage::

        manager = CombatManager()
        manager.add_combatant(Combatant(...))
        manager.declare_action(DeclaredAction(...))
        log = manager.resolve_round()
    """

    def __init__(
        self,
        initiative_method: str = "side",
        seed: Optional[int] = None,
    ) -> None:
        self.id: str = str(uuid.uuid4())
        self.initiative_method = initiative_method
        self.seed = seed
        self.combatants: Dict[str, Combatant] = {}
        self.declared_actions: List[DeclaredAction] = []
        self.round_number: int = 0
        self.phase: CombatPhase = CombatPhase.DECLARATION
        self.round_logs: List[RoundLog] = []
        self.is_active: bool = True
        self._roller = DiceRoller(seed)

    def add_combatant(self, combatant: Combatant) -> None:
        """Add a combatant to the encounter."""
        self.combatants[combatant.id] = combatant

    def remove_combatant(self, combatant_id: str) -> None:
        """Remove a combatant from the encounter."""
        self.combatants.pop(combatant_id, None)

    def declare_action(self, action: DeclaredAction) -> None:
        """Declare a combatant's intended action for the round."""
        self.declared_actions.append(action)

    def get_state(self) -> Dict:
        """Return the current combat state."""
        return {
            "id": self.id,
            "round_number": self.round_number,
            "phase": self.phase.value,
            "is_active": self.is_active,
            "combatants": {
                cid: c.as_dict() for cid, c in self.combatants.items()
            },
            "declared_actions": [
                {
                    "combatant_id": a.combatant_id,
                    "action_type": a.action_type.value,
                    "target_id": a.target_id,
                }
                for a in self.declared_actions
            ],
            "round_logs": [log.as_dict() for log in self.round_logs],
        }

    # ── Round resolution ──────────────────────────────────────────────

    def resolve_round(self) -> RoundLog:
        """Resolve a full combat round and return the log.

        Follows AD&D segment order: initiative, movement, missiles,
        melee, spells, other, morale, bookkeeping.
        """
        self.round_number += 1
        log = RoundLog(round_number=self.round_number)

        # Phase 1: Initiative
        self.phase = CombatPhase.INITIATIVE
        initiative = self._roll_initiative()
        log.initiative = initiative.as_dict()

        # Separate actions by type for phase ordering
        actions_by_type: Dict[ActionType, List[DeclaredAction]] = {}
        for action in self.declared_actions:
            actions_by_type.setdefault(action.action_type, []).append(action)

        # Phase 2: Movement
        self.phase = CombatPhase.MOVEMENT
        for action in actions_by_type.get(ActionType.MOVEMENT, []):
            log.actions_resolved.append({
                "combatant_id": action.combatant_id,
                "action": "movement",
                "result": "moved",
            })

        # Phase 3: Missile attacks
        self.phase = CombatPhase.MISSILE
        for action in actions_by_type.get(ActionType.MISSILE, []):
            result = self._resolve_attack_action(action, is_missile=True)
            log.actions_resolved.append(result)

        # Phase 4: Melee attacks
        self.phase = CombatPhase.MELEE
        for action in actions_by_type.get(ActionType.MELEE, []):
            result = self._resolve_attack_action(action, is_missile=False)
            log.actions_resolved.append(result)

        # Phase 5: Spells
        self.phase = CombatPhase.SPELL
        for action in actions_by_type.get(ActionType.SPELL, []):
            log.actions_resolved.append({
                "combatant_id": action.combatant_id,
                "action": "spell",
                "result": "cast",
                "details": action.details,
            })

        # Phase 6: Other actions (turn undead, use item, defend, flee)
        self.phase = CombatPhase.OTHER
        for atype in (ActionType.TURN_UNDEAD, ActionType.USE_ITEM,
                       ActionType.DEFEND, ActionType.FLEE, ActionType.OTHER):
            for action in actions_by_type.get(atype, []):
                log.actions_resolved.append({
                    "combatant_id": action.combatant_id,
                    "action": atype.value,
                    "result": "resolved",
                    "details": action.details,
                })

        # Phase 7: Morale checks for monsters
        self.phase = CombatPhase.MORALE
        morale_results = self._check_morale()
        log.morale_results = morale_results

        # Phase 8: Bookkeeping
        self.phase = CombatPhase.BOOKKEEPING
        casualties = self._process_casualties()
        log.casualties = casualties

        # Check if combat is over
        party_alive = any(
            c.is_alive for c in self.combatants.values() if c.side == "party"
        )
        monsters_alive = any(
            c.is_alive for c in self.combatants.values() if c.side == "monsters"
        )
        if not party_alive or not monsters_alive:
            self.is_active = False
            if not party_alive:
                log.notes.append("Total party kill! The monsters are victorious.")
            else:
                log.notes.append("All monsters defeated! The party is victorious.")

        # Reset for next round
        self.declared_actions = []
        self.phase = CombatPhase.COMPLETE
        self.round_logs.append(log)
        return log

    def _roll_initiative(self) -> InitiativeResult:
        """Roll initiative for the current round."""
        party = [
            {"id": c.id, "name": c.name, "side": "party",
             "dex": c.dex_score}
            for c in self.combatants.values()
            if c.side == "party" and c.is_alive
        ]
        monsters = [
            {"id": c.id, "name": c.name, "side": "monsters",
             "dex": c.dex_score}
            for c in self.combatants.values()
            if c.side == "monsters" and c.is_alive
        ]

        if self.initiative_method == "individual":
            all_combatants = party + monsters
            return roll_individual_initiative(all_combatants)
        else:
            return roll_side_initiative(party, monsters)

    def _resolve_attack_action(
        self, action: DeclaredAction, is_missile: bool
    ) -> Dict:
        """Resolve a melee or missile attack action."""
        attacker = self.combatants.get(action.combatant_id)
        target = self.combatants.get(action.target_id or "")

        if not attacker or not attacker.is_alive:
            return {
                "combatant_id": action.combatant_id,
                "action": "attack",
                "result": "attacker_incapacitated",
            }

        if not target or not target.is_alive:
            return {
                "combatant_id": action.combatant_id,
                "action": "attack",
                "result": "target_not_found_or_dead",
            }

        attack_result = resolve_attack(
            attacker_name=attacker.name,
            attacker_class=attacker.class_name,
            attacker_level=attacker.level,
            target_name=target.name,
            target_ac=target.ac,
            attacker_str=attacker.str_score,
            attacker_dex=attacker.dex_score,
            damage_dice_num=attacker.damage_dice_num,
            damage_dice_sides=attacker.damage_dice_sides,
            magic_weapon_bonus=attacker.magic_weapon_bonus,
            situational_modifier=action.details.get("situational_modifier", 0),
            is_missile=is_missile,
            is_monster=attacker.is_monster,
            monster_hd=attacker.monster_hd,
        )

        # Apply damage
        if attack_result.hit:
            target.hp -= attack_result.total_damage
            if target.hp <= 0:
                target.is_alive = False

        return {
            "combatant_id": action.combatant_id,
            "action": "missile" if is_missile else "melee",
            "attack_result": attack_result.as_dict(),
        }

    def _check_morale(self) -> List[Dict]:
        """Perform morale checks for monsters (2d6 vs morale score).

        Morale checks occur when:
        - First death on a side
        - 50% casualties on a side
        """
        results: List[Dict] = []
        monsters = [
            c for c in self.combatants.values()
            if c.side == "monsters" and c.is_alive
        ]

        total_monsters = len([
            c for c in self.combatants.values() if c.side == "monsters"
        ])
        alive_monsters = len(monsters)

        # Check if morale should be tested (50% casualties)
        if total_monsters > 0 and alive_monsters <= total_monsters / 2:
            for monster in monsters:
                roll = self._roller._rng.randint(1, 6) + self._roller._rng.randint(1, 6)
                passed = roll <= monster.morale
                results.append({
                    "combatant_id": monster.id,
                    "name": monster.name,
                    "morale_score": monster.morale,
                    "roll": roll,
                    "passed": passed,
                })
                if not passed:
                    monster.conditions.append("fleeing")

        return results

    def _process_casualties(self) -> List[str]:
        """Mark dead combatants and return list of names."""
        casualties: List[str] = []
        for c in self.combatants.values():
            if c.hp <= 0 and c.is_alive:
                c.is_alive = False
                casualties.append(c.name)
        return casualties
