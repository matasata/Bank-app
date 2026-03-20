"""Encounter tables by dungeon level, with wandering monster checks.

Provides monster encounter tables for dungeon levels 1-10 and a wandering
monster check system (1-in-6 chance per turn, per DMG).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from engine.character.ability_scores import DiceRoller


@dataclass
class MonsterEntry:
    """A single monster type that can appear in an encounter."""

    name: str
    hit_dice: int
    ac: int
    damage: str  # e.g. "1d8"
    num_appearing_dice: int = 1
    num_appearing_sides: int = 6
    morale: int = 8  # 2-12 scale
    xp_value: int = 0
    treasure_type: str = ""
    special: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict:
        return {
            "name": self.name,
            "hit_dice": self.hit_dice,
            "ac": self.ac,
            "damage": self.damage,
            "morale": self.morale,
            "xp_value": self.xp_value,
            "treasure_type": self.treasure_type,
            "special": self.special,
        }


@dataclass
class EncounterResult:
    """Result of a random encounter check."""

    encounter_occurred: bool
    wandering_check_roll: int
    dungeon_level: int
    monsters: List[Dict] = field(default_factory=list)
    total_xp: int = 0

    def as_dict(self) -> Dict:
        return {
            "encounter_occurred": self.encounter_occurred,
            "wandering_check_roll": self.wandering_check_roll,
            "dungeon_level": self.dungeon_level,
            "monsters": self.monsters,
            "total_xp": self.total_xp,
        }


# ── Encounter tables by dungeon level ────────────────────────────────────
# Each level has a list of (d100_threshold, MonsterEntry)

DUNGEON_LEVEL_1: List[Tuple[int, MonsterEntry]] = [
    (10, MonsterEntry("Giant Rat", 1, 7, "1d3", 3, 6, 5, 7, "J")),
    (20, MonsterEntry("Kobold", 1, 7, "1d4", 2, 4, 6, 7, "J")),
    (30, MonsterEntry("Goblin", 1, 6, "1d6", 2, 4, 7, 10, "K")),
    (40, MonsterEntry("Orc", 1, 6, "1d8", 1, 6, 8, 10, "L")),
    (48, MonsterEntry("Skeleton", 1, 7, "1d6", 1, 8, 12, 14, "")),
    (55, MonsterEntry("Zombie", 2, 8, "1d8", 1, 4, 12, 20, "")),
    (62, MonsterEntry("Giant Centipede", 1, 9, "0+poison", 1, 4, 7, 15, "")),
    (70, MonsterEntry("Giant Fire Beetle", 1, 4, "2d4", 1, 4, 7, 15, "")),
    (77, MonsterEntry("Stirge", 1, 8, "1d3+blood_drain", 2, 8, 8, 14, "")),
    (84, MonsterEntry("Piercer", 1, 3, "1d6", 1, 4, 12, 15, "")),
    (90, MonsterEntry("Hobgoblin", 1, 5, "1d8", 1, 6, 9, 15, "K")),
    (95, MonsterEntry("Bandit", 1, 7, "1d6", 2, 8, 7, 10, "K")),
    (100, MonsterEntry("Troglodyte", 2, 5, "1d4+1", 1, 4, 8, 40, "D")),
]

DUNGEON_LEVEL_2: List[Tuple[int, MonsterEntry]] = [
    (10, MonsterEntry("Orc", 1, 6, "1d8", 2, 6, 8, 10, "L")),
    (20, MonsterEntry("Hobgoblin", 1, 5, "1d8", 2, 4, 9, 15, "K")),
    (28, MonsterEntry("Gnoll", 2, 5, "2d4", 1, 6, 8, 28, "K")),
    (35, MonsterEntry("Zombie", 2, 8, "1d8", 2, 4, 12, 20, "")),
    (42, MonsterEntry("Ghoul", 2, 6, "1d3+paralysis", 1, 6, 9, 65, "B")),
    (50, MonsterEntry("Troglodyte", 2, 5, "1d4+1", 1, 6, 8, 40, "D")),
    (57, MonsterEntry("Lizard Man", 2, 5, "1d8", 1, 6, 10, 28, "D")),
    (65, MonsterEntry("Giant Spider", 2, 8, "1d6+poison", 1, 4, 8, 65, "J")),
    (72, MonsterEntry("Bugbear", 3, 5, "2d4", 1, 4, 9, 60, "B")),
    (78, MonsterEntry("Harpy", 3, 7, "1d6/1d6/1d3", 1, 4, 8, 120, "C")),
    (85, MonsterEntry("Carrion Crawler", 3, 3, "paralysis", 1, 2, 10, 420, "B")),
    (92, MonsterEntry("Gelatinous Cube", 4, 8, "2d4+paralysis", 1, 1, 12, 175, "")),
    (100, MonsterEntry("Ogre", 4, 5, "1d10", 1, 4, 10, 125, "C")),
]

DUNGEON_LEVEL_3: List[Tuple[int, MonsterEntry]] = [
    (12, MonsterEntry("Gnoll", 2, 5, "2d4", 2, 6, 8, 28, "K")),
    (22, MonsterEntry("Bugbear", 3, 5, "2d4", 2, 4, 9, 60, "B")),
    (32, MonsterEntry("Ogre", 4, 5, "1d10", 1, 6, 10, 125, "C")),
    (40, MonsterEntry("Wight", 4, 5, "1d4+energy_drain", 1, 4, 12, 275, "B")),
    (47, MonsterEntry("Werewolf", 4, 5, "2d4", 1, 4, 10, 150, "")),
    (54, MonsterEntry("Gargoyle", 4, 5, "1d4/1d4/1d6/1d4", 1, 4, 11, 175, "C")),
    (61, MonsterEntry("Owlbear", 5, 5, "1d6/1d6/2d6", 1, 2, 9, 225, "C")),
    (68, MonsterEntry("Rust Monster", 5, 2, "rust", 1, 2, 8, 250, "")),
    (75, MonsterEntry("Wraith", 5, 4, "1d6+energy_drain", 1, 4, 11, 460, "E")),
    (82, MonsterEntry("Troll", 6, 4, "1d4+1/1d4+1/2d6", 1, 4, 10, 525, "D")),
    (90, MonsterEntry("Hill Giant", 8, 4, "2d8", 1, 2, 10, 1350, "E")),
    (100, MonsterEntry("Basilisk", 6, 4, "1d10+petrify", 1, 2, 10, 750, "F")),
]

DUNGEON_LEVEL_4: List[Tuple[int, MonsterEntry]] = [
    (12, MonsterEntry("Ogre", 4, 5, "1d10", 2, 4, 10, 125, "C")),
    (22, MonsterEntry("Troll", 6, 4, "1d4+1/1d4+1/2d6", 1, 6, 10, 525, "D")),
    (32, MonsterEntry("Wraith", 5, 4, "1d6+energy_drain", 1, 6, 11, 460, "E")),
    (40, MonsterEntry("Wyvern", 7, 3, "2d8+poison", 1, 2, 10, 700, "E")),
    (48, MonsterEntry("Manticore", 6, 4, "1d3/1d3/1d8", 1, 2, 9, 525, "E")),
    (55, MonsterEntry("Displacer Beast", 6, 4, "2d4/2d4", 1, 4, 10, 475, "D")),
    (62, MonsterEntry("Minotaur", 6, 6, "1d8+2", 1, 4, 10, 350, "C")),
    (70, MonsterEntry("Spectre", 7, 2, "1d8+energy_drain", 1, 4, 11, 1100, "E")),
    (78, MonsterEntry("Chimera", 9, 6, "varies", 1, 2, 10, 1900, "F")),
    (85, MonsterEntry("Hydra (6 heads)", 6, 5, "1d8x6", 1, 2, 9, 500, "B")),
    (92, MonsterEntry("Stone Giant", 9, 0, "3d6", 1, 2, 10, 1900, "E")),
    (100, MonsterEntry("Young Dragon", 8, 2, "2d8+breath", 1, 1, 10, 2100, "H")),
]

DUNGEON_LEVEL_5: List[Tuple[int, MonsterEntry]] = [
    (15, MonsterEntry("Troll", 6, 4, "1d4+1/1d4+1/2d6", 2, 4, 10, 525, "D")),
    (28, MonsterEntry("Fire Giant", 11, 4, "5d6", 1, 2, 10, 3200, "E")),
    (40, MonsterEntry("Vampire", 8, 1, "1d6+4+energy_drain", 1, 2, 11, 3100, "F")),
    (50, MonsterEntry("Mind Flayer", 8, 5, "brain_extract", 1, 2, 10, 3000, "S")),
    (60, MonsterEntry("Beholder", 10, 0, "eye_rays", 1, 1, 11, 8000, "I")),
    (70, MonsterEntry("Frost Giant", 10, 4, "4d6", 1, 2, 10, 2600, "E")),
    (80, MonsterEntry("Adult Dragon", 10, 0, "3d8+breath", 1, 1, 10, 4000, "H")),
    (88, MonsterEntry("Iron Golem", 13, 3, "4d10", 1, 1, 12, 5500, "")),
    (95, MonsterEntry("Lich", 14, 0, "varies+paralysis", 1, 1, 12, 7500, "V")),
    (100, MonsterEntry("Ancient Dragon", 16, -2, "varies", 1, 1, 11, 12000, "H")),
]

ENCOUNTER_TABLES: Dict[int, List[Tuple[int, MonsterEntry]]] = {
    1: DUNGEON_LEVEL_1,
    2: DUNGEON_LEVEL_2,
    3: DUNGEON_LEVEL_3,
    4: DUNGEON_LEVEL_4,
    5: DUNGEON_LEVEL_5,
}

# Levels 6-10 use level 5 table with adjustments
for lvl in range(6, 11):
    ENCOUNTER_TABLES[lvl] = DUNGEON_LEVEL_5


def check_wandering_monster(
    dungeon_level: int = 1,
    chance_in_six: int = 1,
    seed: Optional[int] = None,
) -> EncounterResult:
    """Perform a wandering monster check.

    Standard AD&D: check once per turn (10 minutes), encounter occurs on
    a 1 on 1d6 (``chance_in_six=1``).

    Args:
        dungeon_level: The current dungeon level (1-10).
        chance_in_six: The number on d6 at or below which triggers an
            encounter (default 1).
        seed: Optional RNG seed.

    Returns:
        An ``EncounterResult``.
    """
    roller = DiceRoller(seed)
    check_roll = roller._rng.randint(1, 6)
    encounter_occurred = check_roll <= chance_in_six

    result = EncounterResult(
        encounter_occurred=encounter_occurred,
        wandering_check_roll=check_roll,
        dungeon_level=dungeon_level,
    )

    if not encounter_occurred:
        return result

    # Roll on the appropriate table
    table = ENCOUNTER_TABLES.get(dungeon_level, DUNGEON_LEVEL_1)
    roll = roller.d100()
    monster_entry: Optional[MonsterEntry] = None
    for threshold, entry in table:
        if roll <= threshold:
            monster_entry = entry
            break

    if monster_entry is None:
        monster_entry = table[-1][1]

    # Number appearing
    num = sum(roller.roll(
        monster_entry.num_appearing_dice,
        monster_entry.num_appearing_sides,
    ))
    num = max(1, num)

    # Create individual monster instances
    for i in range(num):
        hp_rolls = roller.roll(monster_entry.hit_dice, 8)
        hp = max(1, sum(hp_rolls))
        result.monsters.append({
            "id": f"monster_{i}",
            "name": monster_entry.name,
            "hit_dice": monster_entry.hit_dice,
            "hp": hp,
            "max_hp": hp,
            "ac": monster_entry.ac,
            "damage": monster_entry.damage,
            "morale": monster_entry.morale,
            "xp_value": monster_entry.xp_value,
        })

    result.total_xp = sum(m["xp_value"] for m in result.monsters)
    return result


def get_encounter_table(dungeon_level: int) -> List[Dict]:
    """Return the encounter table for a given dungeon level as a list of dicts."""
    table = ENCOUNTER_TABLES.get(dungeon_level, DUNGEON_LEVEL_1)
    return [
        {
            "d100_threshold": threshold,
            "monster": entry.as_dict(),
        }
        for threshold, entry in table
    ]
