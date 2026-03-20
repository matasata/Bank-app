"""AD&D 1st Edition saving throw tables by class and level.

Tables sourced from the DMG/PHB. Each entry maps a level range to the five
saving throw categories:
  - Paralyzation, Poison, or Death Magic (PPDM)
  - Petrification or Polymorph (PP)
  - Rod, Staff, or Wand (RSW)
  - Breath Weapon (BW)
  - Spell (SP)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class SavingThrowEntry:
    """A single row from the saving throw matrix."""

    ppdm: int  # Paralyzation, Poison, Death Magic
    pp: int    # Petrification, Polymorph
    rsw: int   # Rod, Staff, Wand
    bw: int    # Breath Weapon
    sp: int    # Spell

    def as_dict(self) -> Dict[str, int]:
        """Return a plain dictionary representation."""
        return {
            "ppdm": self.ppdm,
            "pp": self.pp,
            "rsw": self.rsw,
            "bw": self.bw,
            "sp": self.sp,
        }


# ---------------------------------------------------------------------------
# Fighter group (Fighter, Paladin, Ranger, Cavalier, Barbarian)
# Level ranges: 0, 1-2, 3-4, 5-6, 7-8, 9-10, 11-12, 13-14, 15-16, 17+
# ---------------------------------------------------------------------------
FIGHTER_SAVES: List[Tuple[Tuple[int, int], SavingThrowEntry]] = [
    ((0, 0),   SavingThrowEntry(16, 17, 18, 20, 19)),
    ((1, 2),   SavingThrowEntry(14, 15, 16, 17, 17)),
    ((3, 4),   SavingThrowEntry(13, 14, 15, 16, 16)),
    ((5, 6),   SavingThrowEntry(11, 12, 13, 13, 14)),
    ((7, 8),   SavingThrowEntry(10, 11, 12, 12, 13)),
    ((9, 10),  SavingThrowEntry(8, 9, 10, 9, 11)),
    ((11, 12), SavingThrowEntry(7, 8, 9, 8, 10)),
    ((13, 14), SavingThrowEntry(5, 6, 7, 5, 8)),
    ((15, 16), SavingThrowEntry(4, 5, 6, 4, 7)),
    ((17, 99), SavingThrowEntry(3, 4, 5, 4, 6)),
]

# ---------------------------------------------------------------------------
# Cleric group (Cleric, Druid)
# Level ranges: 1-3, 4-6, 7-9, 10-12, 13-15, 16-18, 19+
# ---------------------------------------------------------------------------
CLERIC_SAVES: List[Tuple[Tuple[int, int], SavingThrowEntry]] = [
    ((1, 3),   SavingThrowEntry(10, 13, 14, 16, 15)),
    ((4, 6),   SavingThrowEntry(9, 12, 13, 15, 14)),
    ((7, 9),   SavingThrowEntry(7, 10, 11, 13, 12)),
    ((10, 12), SavingThrowEntry(6, 9, 10, 12, 11)),
    ((13, 15), SavingThrowEntry(5, 8, 9, 11, 10)),
    ((16, 18), SavingThrowEntry(4, 7, 8, 10, 9)),
    ((19, 99), SavingThrowEntry(2, 5, 6, 8, 7)),
]

# ---------------------------------------------------------------------------
# Magic-User group (Magic-User, Illusionist)
# Level ranges: 1-5, 6-10, 11-15, 16-20, 21+
# ---------------------------------------------------------------------------
MAGIC_USER_SAVES: List[Tuple[Tuple[int, int], SavingThrowEntry]] = [
    ((1, 5),   SavingThrowEntry(14, 13, 11, 15, 12)),
    ((6, 10),  SavingThrowEntry(13, 11, 9, 13, 10)),
    ((11, 15), SavingThrowEntry(11, 9, 7, 11, 8)),
    ((16, 20), SavingThrowEntry(10, 7, 5, 9, 6)),
    ((21, 99), SavingThrowEntry(8, 5, 3, 7, 4)),
]

# ---------------------------------------------------------------------------
# Thief group (Thief, Assassin, Thief-Acrobat, Monk)
# Level ranges: 1-4, 5-8, 9-12, 13-16, 17-20, 21+
# ---------------------------------------------------------------------------
THIEF_SAVES: List[Tuple[Tuple[int, int], SavingThrowEntry]] = [
    ((1, 4),   SavingThrowEntry(13, 12, 14, 16, 15)),
    ((5, 8),   SavingThrowEntry(12, 11, 12, 15, 13)),
    ((9, 12),  SavingThrowEntry(11, 10, 10, 14, 11)),
    ((13, 16), SavingThrowEntry(10, 9, 8, 13, 9)),
    ((17, 20), SavingThrowEntry(9, 8, 6, 12, 7)),
    ((21, 99), SavingThrowEntry(8, 7, 4, 11, 5)),
]

# Map class names to their save group
CLASS_SAVE_GROUP: Dict[str, List[Tuple[Tuple[int, int], SavingThrowEntry]]] = {
    "Fighter":       FIGHTER_SAVES,
    "Paladin":       FIGHTER_SAVES,
    "Ranger":        FIGHTER_SAVES,
    "Cavalier":      FIGHTER_SAVES,
    "Barbarian":     FIGHTER_SAVES,
    "Cleric":        CLERIC_SAVES,
    "Druid":         CLERIC_SAVES,
    "Magic-User":    MAGIC_USER_SAVES,
    "Illusionist":   MAGIC_USER_SAVES,
    "Thief":         THIEF_SAVES,
    "Assassin":      THIEF_SAVES,
    "Thief-Acrobat": THIEF_SAVES,
    "Monk":          THIEF_SAVES,
}


def get_saving_throws(class_name: str, level: int) -> SavingThrowEntry:
    """Return the saving throws for a given class and level.

    Args:
        class_name: The character's class (e.g. ``"Fighter"``).
        level: The character's current level.

    Returns:
        A ``SavingThrowEntry`` with the five saving throw values.

    Raises:
        ValueError: If the class name is not recognised.
    """
    save_table = CLASS_SAVE_GROUP.get(class_name)
    if save_table is None:
        raise ValueError(f"Unknown class '{class_name}' for saving throws.")

    for (low, high), entry in save_table:
        if low <= level <= high:
            return entry

    # Fallback to the last entry if level exceeds table
    return save_table[-1][1]
