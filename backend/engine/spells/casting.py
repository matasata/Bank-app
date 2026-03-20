"""AD&D 1st Edition spellcasting system.

Handles spell memorization, casting time (segment-based), interruption
checks, spell slot tracking, and spell effect resolution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from engine.character.ability_scores import DiceRoller


@dataclass
class SpellSlots:
    """Current spell slot allocation for a caster."""

    max_slots: Dict[int, int]  # spell_level -> max_slots
    used_slots: Dict[int, int] = field(default_factory=dict)

    def available(self, spell_level: int) -> int:
        """Return available slots for a spell level."""
        max_s = self.max_slots.get(spell_level, 0)
        used = self.used_slots.get(spell_level, 0)
        return max(0, max_s - used)

    def use_slot(self, spell_level: int) -> bool:
        """Use a spell slot. Returns False if none available."""
        if self.available(spell_level) <= 0:
            return False
        self.used_slots[spell_level] = self.used_slots.get(spell_level, 0) + 1
        return True

    def restore_all(self) -> None:
        """Restore all spell slots (after rest/memorization)."""
        self.used_slots.clear()

    def as_dict(self) -> Dict:
        return {
            "max_slots": self.max_slots,
            "used_slots": self.used_slots,
            "available": {
                level: self.available(level)
                for level in self.max_slots
            },
        }


# ── Spell progression tables ────────────────────────────────────────────
# level -> {spell_level: num_slots}
MAGIC_USER_SLOTS: Dict[int, Dict[int, int]] = {
    1:  {1: 1},
    2:  {1: 2},
    3:  {1: 2, 2: 1},
    4:  {1: 3, 2: 2},
    5:  {1: 4, 2: 2, 3: 1},
    6:  {1: 4, 2: 2, 3: 2},
    7:  {1: 4, 2: 3, 3: 2, 4: 1},
    8:  {1: 4, 2: 3, 3: 3, 4: 2},
    9:  {1: 4, 2: 3, 3: 3, 4: 2, 5: 1},
    10: {1: 4, 2: 4, 3: 3, 4: 2, 5: 2},
    11: {1: 4, 2: 4, 3: 4, 4: 3, 5: 3},
    12: {1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 1},
    13: {1: 5, 2: 5, 3: 5, 4: 4, 5: 4, 6: 2},
    14: {1: 5, 2: 5, 3: 5, 4: 4, 5: 4, 6: 2, 7: 1},
    15: {1: 5, 2: 5, 3: 5, 4: 5, 5: 5, 6: 3, 7: 2},
    16: {1: 5, 2: 5, 3: 5, 4: 5, 5: 5, 6: 3, 7: 2, 8: 1},
    17: {1: 5, 2: 5, 3: 5, 4: 5, 5: 5, 6: 3, 7: 3, 8: 2},
    18: {1: 5, 2: 5, 3: 5, 4: 5, 5: 5, 6: 3, 7: 3, 8: 2, 9: 1},
    20: {1: 5, 2: 5, 3: 5, 4: 5, 5: 5, 6: 4, 7: 3, 8: 3, 9: 2},
}

CLERIC_SLOTS: Dict[int, Dict[int, int]] = {
    1:  {1: 1},
    2:  {1: 2},
    3:  {1: 2, 2: 1},
    4:  {1: 3, 2: 2},
    5:  {1: 3, 2: 3, 3: 1},
    6:  {1: 3, 2: 3, 3: 2},
    7:  {1: 3, 2: 3, 3: 2, 4: 1},
    8:  {1: 3, 2: 3, 3: 3, 4: 2},
    9:  {1: 4, 2: 4, 3: 3, 4: 2, 5: 1},
    10: {1: 4, 2: 4, 3: 3, 4: 3, 5: 2},
    11: {1: 5, 2: 4, 3: 4, 4: 3, 5: 2, 6: 1},
    12: {1: 6, 2: 5, 3: 5, 4: 3, 5: 2, 6: 2},
    13: {1: 6, 2: 5, 3: 5, 4: 4, 5: 3, 6: 2, 7: 1},
    14: {1: 6, 2: 6, 3: 6, 4: 5, 5: 3, 6: 2, 7: 1},
    15: {1: 7, 2: 6, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2},
}

DRUID_SLOTS: Dict[int, Dict[int, int]] = {
    1:  {1: 2},
    2:  {1: 2, 2: 1},
    3:  {1: 3, 2: 2, 3: 1},
    4:  {1: 4, 2: 2, 3: 2},
    5:  {1: 4, 2: 3, 3: 2, 4: 1},
    6:  {1: 4, 2: 3, 3: 2, 4: 2},
    7:  {1: 4, 2: 4, 3: 3, 4: 2, 5: 1},
    8:  {1: 4, 2: 4, 3: 3, 4: 3, 5: 2},
    9:  {1: 5, 2: 4, 3: 4, 4: 3, 5: 2, 6: 1},
    10: {1: 5, 2: 4, 3: 4, 4: 3, 5: 3, 6: 2},
    11: {1: 5, 2: 5, 3: 4, 4: 4, 5: 3, 6: 2, 7: 1},
    12: {1: 6, 2: 5, 3: 5, 4: 4, 5: 4, 6: 3, 7: 2},
    13: {1: 6, 2: 5, 3: 5, 4: 5, 5: 4, 6: 3, 7: 2},
    14: {1: 6, 2: 6, 3: 6, 4: 5, 5: 5, 6: 4, 7: 3},
}


SLOT_TABLES: Dict[str, Dict[int, Dict[int, int]]] = {
    "Magic-User": MAGIC_USER_SLOTS,
    "Illusionist": MAGIC_USER_SLOTS,
    "Cleric": CLERIC_SLOTS,
    "Druid": DRUID_SLOTS,
}


def get_spell_slots(class_name: str, level: int) -> SpellSlots:
    """Get spell slot allocation for a class and level."""
    table = SLOT_TABLES.get(class_name, {})
    # Find exact level or closest lower
    slots = {}
    for lvl in sorted(table.keys()):
        if lvl <= level:
            slots = table[lvl]
    return SpellSlots(max_slots=dict(slots))


@dataclass
class CastingResult:
    """Result of attempting to cast a spell."""

    success: bool
    spell_name: str
    caster_name: str
    casting_time_segments: int
    interrupted: bool = False
    interruption_reason: str = ""
    damage: int = 0
    damage_dice: List[int] = field(default_factory=list)
    saving_throw_type: str = ""
    notes: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict:
        return {
            "success": self.success,
            "spell_name": self.spell_name,
            "caster_name": self.caster_name,
            "casting_time_segments": self.casting_time_segments,
            "interrupted": self.interrupted,
            "interruption_reason": self.interruption_reason,
            "damage": self.damage,
            "damage_dice": self.damage_dice,
            "saving_throw_type": self.saving_throw_type,
            "notes": self.notes,
        }


def check_spell_interruption(
    casting_time_segments: int,
    damage_taken: int = 0,
    caster_hit: bool = False,
) -> bool:
    """Check if a spell being cast is interrupted.

    Per DMG, a caster who takes damage during casting loses the spell.
    """
    if damage_taken > 0:
        return True
    if caster_hit:
        return True
    return False


def resolve_spell_damage(
    spell_name: str,
    caster_level: int,
    num_dice: int,
    die_sides: int,
    bonus_per_die: int = 0,
    max_dice: Optional[int] = None,
    seed: Optional[int] = None,
) -> Dict:
    """Roll damage for a spell.

    Args:
        spell_name: Name of the spell.
        caster_level: Caster's level (some spells scale).
        num_dice: Number of damage dice (often = caster_level).
        die_sides: Sides per die.
        bonus_per_die: Bonus added per die (e.g. Magic Missile +1).
        max_dice: Maximum number of dice allowed.
        seed: Optional RNG seed.
    """
    roller = DiceRoller(seed)

    effective_dice = min(num_dice, max_dice) if max_dice else num_dice
    dice = roller.roll(effective_dice, die_sides)
    total_bonus = bonus_per_die * effective_dice
    total = sum(dice) + total_bonus

    return {
        "spell_name": spell_name,
        "dice": dice,
        "num_dice": effective_dice,
        "die_sides": die_sides,
        "bonus": total_bonus,
        "total_damage": max(0, total),
    }
