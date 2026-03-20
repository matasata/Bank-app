"""AD&D 1st Edition character progression and leveling.

Handles XP tracking, level advancement, HP rolling on level up,
new spell slots, improved saving throws, and attack matrix advancement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from engine.character.ability_scores import DiceRoller
from engine.character.classes import get_class, ClassDefinition
from engine.character.creation import _con_hp_modifier, FIGHTER_GROUP
from engine.rules.saving_throws import get_saving_throws
from engine.rules.combat_matrices import get_thac0


@dataclass
class LevelUpResult:
    """Result of a level-up operation."""

    new_level: int
    old_level: int
    hp_roll: int
    con_modifier: int
    hp_gained: int
    new_total_hp: int
    new_thac0: int
    new_saving_throws: Dict[str, int]
    new_level_title: str
    new_abilities: List[str]  # any new abilities gained
    spell_slots_gained: Optional[Dict[int, int]] = None  # level -> slots

    def as_dict(self) -> Dict:
        return {
            "new_level": self.new_level,
            "old_level": self.old_level,
            "hp_roll": self.hp_roll,
            "con_modifier": self.con_modifier,
            "hp_gained": self.hp_gained,
            "new_total_hp": self.new_total_hp,
            "new_thac0": self.new_thac0,
            "new_saving_throws": self.new_saving_throws,
            "new_level_title": self.new_level_title,
            "new_abilities": self.new_abilities,
            "spell_slots_gained": self.spell_slots_gained,
        }


def check_level_up(
    class_name: str,
    current_level: int,
    current_xp: int,
) -> bool:
    """Check if the character has enough XP to advance a level."""
    cls = get_class(class_name)
    next_level = current_level + 1
    xp_needed = cls.xp_for_level(next_level)
    return current_xp >= xp_needed


def xp_for_next_level(class_name: str, current_level: int) -> int:
    """Return the XP needed for the next level."""
    cls = get_class(class_name)
    return cls.xp_for_level(current_level + 1)


def award_xp(
    current_xp: int,
    xp_gained: int,
    prime_req_bonus: float = 0.0,
) -> Tuple[int, int]:
    """Award XP with optional prime requisite bonus.

    Returns (new_total_xp, effective_xp_gained).
    """
    bonus = int(xp_gained * prime_req_bonus)
    effective = xp_gained + bonus
    return current_xp + effective, effective


def level_up(
    class_name: str,
    current_level: int,
    current_hp: int,
    con: int,
    seed: Optional[int] = None,
) -> LevelUpResult:
    """Perform a level-up and return all changes.

    Args:
        class_name: Character's class.
        current_level: Current level (before advancement).
        current_hp: Current max HP.
        con: Constitution score.
        seed: Optional RNG seed.

    Returns:
        A ``LevelUpResult`` with all the changes from leveling up.
    """
    cls = get_class(class_name)
    roller = DiceRoller(seed)
    new_level = current_level + 1

    # Roll HP
    con_mod = _con_hp_modifier(con, class_name)

    # After name level (typically 9-10), fighters get fixed HP, others get less
    if new_level <= 9:
        hp_roll = roller._rng.randint(1, cls.hit_die_sides)
        hp_gained = max(1, hp_roll + con_mod)
    else:
        # Post name-level: fighters get 3/level, others get 1-2/level
        if class_name in FIGHTER_GROUP:
            hp_roll = 3
            hp_gained = 3  # Fixed 3 HP per level after 9
        elif cls.hit_die_sides >= 6:
            hp_roll = 2
            hp_gained = 2
        else:
            hp_roll = 1
            hp_gained = 1

    new_hp = current_hp + hp_gained

    # New THAC0
    new_thac0 = get_thac0(cls.attack_group, new_level)

    # New saving throws
    new_saves = get_saving_throws(cls.save_group, new_level)

    # Level title
    if new_level in cls.level_titles:
        new_title = cls.level_titles[new_level]
    else:
        highest = max(cls.level_titles.keys()) if cls.level_titles else 0
        new_title = cls.level_titles.get(highest, cls.name)

    # New abilities at certain levels
    new_abilities: List[str] = []

    # Fighter extra attacks
    if class_name in FIGHTER_GROUP:
        if new_level == 7:
            new_abilities.append("Gains 3/2 attacks per round")
        elif new_level == 13:
            new_abilities.append("Gains 2 attacks per round")

    # Spell slot changes (for spellcasters)
    spell_slots_gained = None
    if cls.spellcasting:
        spell_slots_gained = {}
        # This would need spell progression tables per class
        # For now, indicate that spell slots have changed
        spell_slots_gained[new_level] = 1  # placeholder

    return LevelUpResult(
        new_level=new_level,
        old_level=current_level,
        hp_roll=hp_roll,
        con_modifier=con_mod,
        hp_gained=hp_gained,
        new_total_hp=new_hp,
        new_thac0=new_thac0,
        new_saving_throws=new_saves.as_dict(),
        new_level_title=new_title,
        new_abilities=new_abilities,
        spell_slots_gained=spell_slots_gained,
    )
