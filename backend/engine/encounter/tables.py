"""Encounter tables by dungeon level from the DMG."""
import random
from typing import Any


# Wandering monster tables by dungeon level
ENCOUNTER_TABLES: dict[int, list[tuple[int, str, str, int]]] = {
    # Level: [(weight, monster_id, count_dice, xp_value), ...]
    1: [
        (15, "kobold", "2d4", 7),
        (15, "giant_rat", "2d6", 3),
        (12, "goblin", "2d4", 10),
        (10, "orc", "1d6", 15),
        (10, "skeleton", "1d6", 14),
        (8, "giant_centipede", "1d4", 5),
        (7, "stirge", "1d6", 35),
        (5, "zombie", "1d4", 20),
        (5, "hobgoblin", "1d4", 20),
        (5, "gnoll", "1d4", 30),
        (3, "giant_spider", "1d2", 50),
        (3, "troglodyte", "1d4", 25),
        (2, "bugbear", "1d2", 90),
    ],
    2: [
        (12, "orc", "2d4", 15),
        (12, "hobgoblin", "1d6", 20),
        (10, "gnoll", "1d6", 30),
        (10, "zombie", "1d6", 20),
        (8, "skeleton", "2d4", 14),
        (8, "troglodyte", "1d6", 25),
        (7, "giant_spider", "1d4", 50),
        (7, "stirge", "2d4", 35),
        (6, "bugbear", "1d4", 90),
        (5, "ghoul", "1d4", 65),
        (5, "lizardman", "1d6", 35),
        (5, "piercer", "1d4", 40),
        (3, "carrion_crawler", "1", 250),
        (2, "ogre", "1", 125),
    ],
    3: [
        (12, "bugbear", "1d6", 90),
        (10, "ghoul", "1d6", 65),
        (10, "ogre", "1d3", 125),
        (8, "wight", "1d3", 250),
        (8, "carrion_crawler", "1d2", 250),
        (7, "gelatinous_cube", "1", 175),
        (7, "shadow", "1d4", 135),
        (7, "doppelganger", "1d2", 200),
        (6, "gargoyle", "1d4", 175),
        (5, "owlbear", "1d2", 250),
        (5, "rust_monster", "1d2", 125),
        (5, "grey_ooze", "1", 125),
        (5, "ochre_jelly", "1", 175),
        (3, "troll", "1", 650),
        (2, "displacer_beast", "1d2", 350),
    ],
    4: [
        (12, "ogre", "1d4", 125),
        (10, "gargoyle", "1d6", 175),
        (10, "wraith", "1d3", 500),
        (8, "troll", "1d3", 650),
        (8, "owlbear", "1d3", 250),
        (7, "displacer_beast", "1d3", 350),
        (7, "hell_hound", "1d4", 175),
        (7, "ghast", "1d4", 175),
        (5, "mimic", "1", 250),
        (5, "umber_hulk", "1", 600),
        (5, "black_pudding", "1", 750),
        (5, "manticore", "1d2", 350),
        (3, "chimera", "1", 750),
        (3, "basilisk", "1", 700),
        (3, "spectre", "1d2", 750),
        (2, "vampire", "1", 2000),
    ],
    5: [
        (10, "troll", "1d4", 650),
        (10, "mummy", "1d3", 750),
        (8, "spectre", "1d3", 750),
        (8, "umber_hulk", "1d2", 600),
        (7, "hill_giant", "1d2", 750),
        (7, "chimera", "1d2", 750),
        (7, "basilisk", "1d2", 700),
        (6, "hydra_5head", "1", 500),
        (6, "mind_flayer", "1", 2000),
        (5, "roper", "1", 1000),
        (5, "fire_giant", "1", 1500),
        (5, "frost_giant", "1", 1250),
        (4, "beholder", "1", 4000),
        (4, "vampire", "1d2", 2000),
        (4, "stone_giant", "1", 1000),
        (2, "purple_worm", "1", 5000),
        (2, "dragon_young", "1", 3000),
    ],
}


def get_encounter_table(dungeon_level: int) -> list[dict[str, Any]]:
    """Get the encounter table for a given dungeon level."""
    level = min(dungeon_level, max(ENCOUNTER_TABLES.keys()))
    level = max(level, min(ENCOUNTER_TABLES.keys()))
    table = ENCOUNTER_TABLES.get(level, ENCOUNTER_TABLES[1])
    return [
        {"weight": w, "monster_id": m, "count": c, "xp_value": xp}
        for w, m, c, xp in table
    ]


def check_wandering_monster(chance: int = 1) -> bool:
    """Check for wandering monster (default: 1 in 6 per turn)."""
    return random.randint(1, 6) <= chance


def generate_encounter(dungeon_level: int) -> dict[str, Any]:
    """Generate a random encounter for the given dungeon level."""
    level = min(dungeon_level, max(ENCOUNTER_TABLES.keys()))
    level = max(level, min(ENCOUNTER_TABLES.keys()))
    table = ENCOUNTER_TABLES.get(level, ENCOUNTER_TABLES[1])

    # Weighted random selection
    total_weight = sum(w for w, _, _, _ in table)
    roll = random.randint(1, total_weight)
    cumulative = 0

    for weight, monster_id, count_dice, xp_value in table:
        cumulative += weight
        if roll <= cumulative:
            # Parse count dice (e.g., "2d4", "1d6", "1")
            count = _roll_count(count_dice)
            return {
                "monster_id": monster_id,
                "count": count,
                "xp_per_monster": xp_value,
                "total_xp": xp_value * count,
                "dungeon_level": dungeon_level,
            }

    # Fallback
    return {"monster_id": "orc", "count": 2, "xp_per_monster": 15, "total_xp": 30, "dungeon_level": dungeon_level}


def _roll_count(dice_str: str) -> int:
    """Roll dice for monster count."""
    dice_str = dice_str.strip()
    if "d" not in dice_str:
        return int(dice_str)

    parts = dice_str.split("d")
    num = int(parts[0])
    sides = int(parts[1])
    return sum(random.randint(1, sides) for _ in range(num))
