"""AD&D 1st Edition attack matrices (THAC0 / to-hit tables) from the DMG.

The attack matrix maps an attacker's class group and level to the d20 roll
needed to hit each Armour Class from 10 down to -10.

THAC0 (To Hit Armour Class 0) is provided as a convenience; the full row
gives the target number for every AC.
"""

from __future__ import annotations

from typing import Dict, List, Tuple


# Each row is a tuple of 21 integers: the roll needed to hit AC 10, 9, 8 ... -10
# Index 0 = AC 10, Index 10 = AC 0, Index 20 = AC -10
AttackRow = Tuple[
    int, int, int, int, int, int, int, int, int, int, int,
    int, int, int, int, int, int, int, int, int, int,
]

# ---------------------------------------------------------------------------
# Fighter group attack matrix (Fighter, Paladin, Ranger, Cavalier, Barbarian)
# ---------------------------------------------------------------------------
FIGHTER_ATTACK_MATRIX: List[Tuple[Tuple[int, int], AttackRow]] = [
    ((0, 0),   (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20)),
    ((1, 1),   (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20)),
    ((2, 2),   (9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20)),
    ((3, 3),   (8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20, 20, 20, 20, 20, 20, 20, 20)),
    ((4, 4),   (7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20, 20, 20, 20, 20, 20, 20)),
    ((5, 5),   (6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20, 20, 20, 20, 20, 20)),
    ((6, 6),   (5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20, 20, 20, 20, 20)),
    ((7, 7),   (4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20, 20, 20, 20)),
    ((8, 8),   (3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20, 20, 20)),
    ((9, 9),   (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20, 20)),
    ((10, 10), (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20)),
    ((11, 11), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20)),
    ((12, 12), (-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19)),
    ((13, 13), (-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18)),
    ((14, 14), (-3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17)),
    ((15, 15), (-4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)),
    ((16, 16), (-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)),
    ((17, 99), (-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)),
]

# ---------------------------------------------------------------------------
# Cleric group attack matrix (Cleric, Druid)
# ---------------------------------------------------------------------------
CLERIC_ATTACK_MATRIX: List[Tuple[Tuple[int, int], AttackRow]] = [
    ((1, 3),   (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20)),
    ((4, 6),   (8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20, 20, 20, 20, 20, 20, 20, 20)),
    ((7, 9),   (6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20, 20, 20, 20, 20, 20)),
    ((10, 12), (4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20, 20, 20, 20)),
    ((13, 15), (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20, 20)),
    ((16, 18), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20)),
    ((19, 99), (-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18)),
]

# ---------------------------------------------------------------------------
# Magic-User group attack matrix (Magic-User, Illusionist)
# ---------------------------------------------------------------------------
MAGIC_USER_ATTACK_MATRIX: List[Tuple[Tuple[int, int], AttackRow]] = [
    ((1, 5),   (11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21)),
    ((6, 10),  (9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 21, 21, 21, 21, 21, 21, 21, 21)),
    ((11, 15), (7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 21, 21, 21, 21, 21, 21)),
    ((16, 20), (5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 21, 21, 21, 21)),
    ((21, 99), (3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 21, 21)),
]

# ---------------------------------------------------------------------------
# Thief group attack matrix (Thief, Assassin, Thief-Acrobat, Monk)
# ---------------------------------------------------------------------------
THIEF_ATTACK_MATRIX: List[Tuple[Tuple[int, int], AttackRow]] = [
    ((1, 4),   (11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21)),
    ((5, 8),   (9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 21, 21, 21, 21, 21, 21, 21, 21)),
    ((9, 12),  (7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 21, 21, 21, 21, 21, 21)),
    ((13, 16), (5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 21, 21, 21, 21)),
    ((17, 20), (3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 21, 21)),
    ((21, 99), (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21)),
]

# ---------------------------------------------------------------------------
# Monster attack matrix (by Hit Dice)
# ---------------------------------------------------------------------------
MONSTER_ATTACK_MATRIX: List[Tuple[Tuple[int, int], AttackRow]] = [
    ((0, 0),   (11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21)),
    ((1, 1),   (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20)),
    ((2, 3),   (9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20)),
    ((4, 5),   (7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20, 20, 20, 20, 20, 20, 20)),
    ((6, 7),   (5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20, 20, 20, 20, 20)),
    ((8, 9),   (3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20, 20, 20)),
    ((10, 11), (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20)),
    ((12, 13), (-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19)),
    ((14, 15), (-3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17)),
    ((16, 99), (-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)),
]


# Map class names to their attack matrix group
CLASS_ATTACK_GROUP: Dict[str, List[Tuple[Tuple[int, int], AttackRow]]] = {
    "Fighter":       FIGHTER_ATTACK_MATRIX,
    "Paladin":       FIGHTER_ATTACK_MATRIX,
    "Ranger":        FIGHTER_ATTACK_MATRIX,
    "Cavalier":      FIGHTER_ATTACK_MATRIX,
    "Barbarian":     FIGHTER_ATTACK_MATRIX,
    "Cleric":        CLERIC_ATTACK_MATRIX,
    "Druid":         CLERIC_ATTACK_MATRIX,
    "Magic-User":    MAGIC_USER_ATTACK_MATRIX,
    "Illusionist":   MAGIC_USER_ATTACK_MATRIX,
    "Thief":         THIEF_ATTACK_MATRIX,
    "Assassin":      THIEF_ATTACK_MATRIX,
    "Thief-Acrobat": THIEF_ATTACK_MATRIX,
    "Monk":          THIEF_ATTACK_MATRIX,
}


def _lookup_row(
    matrix: List[Tuple[Tuple[int, int], AttackRow]], level: int
) -> AttackRow:
    """Find the correct attack row for a given level / HD."""
    for (low, high), row in matrix:
        if low <= level <= high:
            return row
    return matrix[-1][1]


def get_thac0(class_name: str, level: int) -> int:
    """Return the THAC0 for a class at a given level.

    THAC0 is the value at index 10 of the attack row (the roll needed to
    hit AC 0).
    """
    matrix = CLASS_ATTACK_GROUP.get(class_name)
    if matrix is None:
        raise ValueError(f"Unknown class '{class_name}' for attack matrix.")
    row = _lookup_row(matrix, level)
    return row[10]


def get_to_hit_number(
    class_name: str, level: int, target_ac: int
) -> int:
    """Return the d20 roll needed to hit a specific AC.

    Args:
        class_name: Attacker's class.
        level: Attacker's level.
        target_ac: Defender's armour class (10 to -10).

    Returns:
        The minimum d20 roll needed.
    """
    matrix = CLASS_ATTACK_GROUP.get(class_name)
    if matrix is None:
        raise ValueError(f"Unknown class '{class_name}' for attack matrix.")
    row = _lookup_row(matrix, level)
    index = 10 - target_ac  # AC 10 -> index 0, AC 0 -> index 10, AC -10 -> index 20
    index = max(0, min(20, index))
    return row[index]


def get_monster_to_hit(hit_dice: int, target_ac: int) -> int:
    """Return the d20 roll a monster needs to hit a given AC."""
    row = _lookup_row(MONSTER_ATTACK_MATRIX, hit_dice)
    index = 10 - target_ac
    index = max(0, min(20, index))
    return row[index]
