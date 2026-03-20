"""Character creation orchestrator for AD&D 1st Edition.

Validates race/class combinations, applies racial modifiers, calculates
derived statistics (HP, AC, saving throws, THAC0), generates starting
gold, and produces a complete ready-to-play character.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from engine.character.ability_scores import DiceRoller, ABILITY_NAMES
from engine.character.races import ALL_RACES, RaceDefinition, get_race
from engine.character.classes import ALL_CLASSES, ClassDefinition, get_class
from engine.rules.saving_throws import get_saving_throws, SavingThrowEntry
from engine.rules.combat_matrices import get_thac0


# ── Starting gold by class (dice formula) ────────────────────────────────
# Format: (num_dice, sides, multiplier)
STARTING_GOLD: Dict[str, Tuple[int, int, int]] = {
    "Fighter":       (5, 4, 10),
    "Paladin":       (5, 4, 10),
    "Ranger":        (5, 4, 10),
    "Cavalier":      (5, 4, 10),
    "Barbarian":     (5, 4, 10),
    "Magic-User":    (2, 4, 10),
    "Illusionist":   (2, 4, 10),
    "Cleric":        (3, 6, 10),
    "Druid":         (3, 6, 10),
    "Thief":         (2, 6, 10),
    "Assassin":      (2, 6, 10),
    "Thief-Acrobat": (2, 6, 10),
    "Monk":          (5, 4, 1),   # Monks have very little gold
}


# ── Constitution HP bonus table ──────────────────────────────────────────
CON_HP_BONUS: Dict[int, int] = {
    1: -3, 2: -2, 3: -2, 4: -1, 5: -1, 6: -1,
    7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0,
    15: 1, 16: 2, 17: 3, 18: 4, 19: 5,
}

# Fighters (including Paladin, Ranger, Cavalier, Barbarian) can get
# the full CON bonus; others are capped at +2.
FIGHTER_GROUP = {"Fighter", "Paladin", "Ranger", "Cavalier", "Barbarian"}


@dataclass
class ValidationResult:
    """Result of a character-creation validation check."""

    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class CreatedCharacter:
    """A fully-created character with all derived statistics."""

    name: str
    race: str
    class_name: str
    level: int
    alignment: str
    abilities: Dict[str, int]
    hp: int
    max_hp: int
    ac: int
    thac0: int
    saving_throws: Dict[str, int]
    xp: int
    gold: float
    gold_roll_details: Dict[str, Any]
    special_abilities: List[str]
    level_title: str

    def as_dict(self) -> Dict:
        return {
            "name": self.name,
            "race": self.race,
            "class_name": self.class_name,
            "level": self.level,
            "alignment": self.alignment,
            "abilities": self.abilities,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "ac": self.ac,
            "thac0": self.thac0,
            "saving_throws": self.saving_throws,
            "xp": self.xp,
            "gold": self.gold,
            "gold_roll_details": self.gold_roll_details,
            "special_abilities": self.special_abilities,
            "level_title": self.level_title,
        }


# ── Validation ────────────────────────────────────────────────────────────

def validate_race_class(
    race_name: str,
    class_name: str,
    abilities: Dict[str, int],
    alignment: Optional[str] = None,
) -> ValidationResult:
    """Check whether a race/class/ability combination is legal.

    Returns a ``ValidationResult`` with ``valid=True`` if the combination
    is permitted, or ``valid=False`` with details of all violations.
    """
    result = ValidationResult(valid=True)

    # ── Race exists? ──
    try:
        race = get_race(race_name)
    except ValueError as exc:
        result.valid = False
        result.errors.append(str(exc))
        return result

    # ── Class exists? ──
    try:
        cls = get_class(class_name)
    except ValueError as exc:
        result.valid = False
        result.errors.append(str(exc))
        return result

    # ── Class permitted for race? ──
    if class_name not in race.permitted_classes:
        result.valid = False
        result.errors.append(
            f"{race_name} cannot be a {class_name}. "
            f"Permitted: {race.permitted_classes}"
        )

    # ── Ability score minimums for class ──
    for ability, minimum in cls.ability_requirements.items():
        score = abilities.get(ability, 0)
        if score < minimum:
            result.valid = False
            result.errors.append(
                f"{class_name} requires {ability.upper()} >= {minimum}, "
                f"but character has {score}"
            )

    # ── Ability score minimums for race ──
    for ability, minimum in race.ability_minimums.items():
        score = abilities.get(ability, 0)
        if score < minimum:
            result.valid = False
            result.errors.append(
                f"{race_name} requires {ability.upper()} >= {minimum}, "
                f"but character has {score}"
            )

    # ── Ability score maximums for race ──
    for ability, maximum in race.ability_maximums.items():
        score = abilities.get(ability, 18)
        if score > maximum:
            result.valid = False
            result.errors.append(
                f"{race_name} maximum {ability.upper()} is {maximum}, "
                f"but character has {score}"
            )

    # ── Alignment restrictions ──
    if alignment and cls.alignment_restrictions:
        if alignment not in cls.alignment_restrictions:
            result.valid = False
            result.errors.append(
                f"{class_name} alignment must be one of "
                f"{cls.alignment_restrictions}, got '{alignment}'"
            )

    # ── Level limits warning ──
    if race_name != "Human" and class_name in race.level_limits:
        limit = race.level_limits[class_name]
        if limit > 0:
            result.warnings.append(
                f"{race_name} {class_name} is limited to level {limit}"
            )

    return result


# ── Derived stat helpers ──────────────────────────────────────────────────

def _apply_racial_adjustments(
    abilities: Dict[str, int], race: RaceDefinition
) -> Dict[str, int]:
    """Return a copy of *abilities* with racial modifiers applied."""
    adjusted = dict(abilities)
    for ability, mod in race.ability_adjustments.items():
        adjusted[ability] = max(3, min(19, adjusted.get(ability, 10) + mod))
    return adjusted


def _con_hp_modifier(con: int, class_name: str) -> int:
    """Return the per-level HP modifier from Constitution."""
    bonus = CON_HP_BONUS.get(con, 0)
    if class_name not in FIGHTER_GROUP and bonus > 2:
        bonus = 2
    return bonus


def _roll_starting_gold(class_name: str, roller: DiceRoller) -> Tuple[float, Dict]:
    """Roll starting gold and return ``(total, details)``."""
    num_dice, sides, multiplier = STARTING_GOLD.get(class_name, (3, 6, 10))
    dice = [roller._rng.randint(1, sides) for _ in range(num_dice)]
    total = sum(dice) * multiplier
    return float(total), {
        "num_dice": num_dice,
        "sides": sides,
        "multiplier": multiplier,
        "rolls": dice,
        "subtotal": sum(dice),
        "total": total,
    }


def _get_level_title(cls: ClassDefinition, level: int) -> str:
    """Return the level title for *level*, falling back to the highest."""
    if level in cls.level_titles:
        return cls.level_titles[level]
    # Return highest available
    highest = max(cls.level_titles.keys()) if cls.level_titles else 0
    return cls.level_titles.get(highest, cls.name)


# ── Main creation function ────────────────────────────────────────────────

def create_character(
    name: str,
    race_name: str,
    class_name: str,
    abilities: Dict[str, int],
    alignment: str,
    level: int = 1,
    seed: Optional[int] = None,
) -> CreatedCharacter:
    """Create a complete 1st-level character.

    This is the main orchestrator that:
    1. Validates the race / class / ability combination.
    2. Applies racial modifiers to ability scores.
    3. Rolls HP (including CON modifier).
    4. Calculates base AC (10 unarmoured).
    5. Looks up saving throws and THAC0.
    6. Rolls starting gold.
    7. Gathers special abilities from race and class.

    Args:
        name: Character name.
        race_name: One of the defined race names.
        class_name: One of the defined class names.
        abilities: Raw (pre-racial-adjustment) ability scores.
        alignment: e.g. "Lawful Good".
        level: Starting level (default 1).
        seed: Optional RNG seed.

    Returns:
        A ``CreatedCharacter`` with all stats calculated.

    Raises:
        ValueError: If the combination is invalid.
    """
    # Validate
    validation = validate_race_class(race_name, class_name, abilities, alignment)
    if not validation.valid:
        raise ValueError(
            "Invalid character: " + "; ".join(validation.errors)
        )

    race = get_race(race_name)
    cls = get_class(class_name)
    roller = DiceRoller(seed)

    # Apply racial adjustments
    adjusted = _apply_racial_adjustments(abilities, race)

    # HP
    con_mod = _con_hp_modifier(adjusted.get("con", 10), class_name)
    hp_roll = roller._rng.randint(1, cls.hit_die_sides)
    hp = max(1, hp_roll + con_mod)

    # For levels > 1 (if starting at higher level)
    for _ in range(1, level):
        extra_roll = roller._rng.randint(1, cls.hit_die_sides)
        hp += max(1, extra_roll + con_mod)

    # AC (base 10, no armour)
    ac = 10

    # THAC0
    thac0 = get_thac0(cls.attack_group, level)

    # Saving throws
    saves = get_saving_throws(cls.save_group, level)

    # Starting gold
    gold, gold_details = _roll_starting_gold(class_name, roller)

    # Special abilities (combine race + class)
    special = list(race.special_abilities) + list(cls.special_abilities)

    # Level title
    title = _get_level_title(cls, level)

    return CreatedCharacter(
        name=name,
        race=race_name,
        class_name=class_name,
        level=level,
        alignment=alignment,
        abilities=adjusted,
        hp=hp,
        max_hp=hp,
        ac=ac,
        thac0=thac0,
        saving_throws=saves.as_dict(),
        xp=0,
        gold=gold,
        gold_roll_details=gold_details,
        special_abilities=special,
        level_title=title,
    )
