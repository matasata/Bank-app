"""AD&D 1st Edition encumbrance and movement rate calculations.

Encumbrance is tracked in gold pieces (gp) weight. 10 coins = 1 lb.
Movement rate is reduced based on total weight carried relative to the
character's Strength-based carrying capacity.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple


# ── Strength-based carrying capacity (in gp weight) ──────────────────────
# Normal load, heavy load, maximum load (drag)
STR_CAPACITY: Dict[int, Tuple[int, int, int]] = {
    1:  (50, 100, 150),
    2:  (100, 150, 200),
    3:  (100, 200, 350),
    4:  (150, 300, 500),
    5:  (150, 300, 500),
    6:  (200, 400, 700),
    7:  (200, 400, 700),
    8:  (350, 500, 1000),
    9:  (350, 500, 1000),
    10: (400, 600, 1200),
    11: (400, 600, 1200),
    12: (450, 700, 1400),
    13: (450, 700, 1400),
    14: (550, 800, 1600),
    15: (550, 800, 1600),
    16: (700, 1000, 2000),
    17: (850, 1300, 2500),
    18: (1100, 1500, 3000),
    19: (1500, 2500, 5000),
}


# ── Movement rate by encumbrance level ────────────────────────────────────
# Base movement rate is 12" for most races
MOVEMENT_TABLE = [
    # (max_weight_ratio, move_rate_ratio)
    (0.33, 1.0),      # Light: full movement
    (0.50, 0.75),     # Moderate: 3/4 movement
    (0.67, 0.50),     # Heavy: 1/2 movement
    (0.85, 0.25),     # Very heavy: 1/4 movement
    (1.00, 0.083),    # Maximum: 1" movement
]


@dataclass
class EncumbranceResult:
    """Result of an encumbrance calculation."""

    total_weight_gp: int
    normal_capacity: int
    heavy_capacity: int
    max_capacity: int
    encumbrance_level: str  # "unencumbered", "light", "moderate", "heavy", "severe", "immobile"
    base_movement: int
    adjusted_movement: int
    movement_penalty: str

    def as_dict(self) -> Dict:
        return {
            "total_weight_gp": self.total_weight_gp,
            "normal_capacity": self.normal_capacity,
            "heavy_capacity": self.heavy_capacity,
            "max_capacity": self.max_capacity,
            "encumbrance_level": self.encumbrance_level,
            "base_movement": self.base_movement,
            "adjusted_movement": self.adjusted_movement,
            "movement_penalty": self.movement_penalty,
        }


def calculate_encumbrance(
    strength: int,
    total_weight_gp: int,
    base_movement: int = 12,
    race: Optional[str] = None,
) -> EncumbranceResult:
    """Calculate encumbrance and adjusted movement rate.

    Args:
        strength: Character's Strength score.
        total_weight_gp: Total weight carried in gp.
        base_movement: Base movement rate (default 12 for humans).
        race: Optional race name for special movement rules.

    Returns:
        An ``EncumbranceResult`` with all encumbrance details.
    """
    normal, heavy, maximum = STR_CAPACITY.get(strength, (400, 600, 1200))

    # Determine encumbrance level
    if total_weight_gp <= 0:
        level = "unencumbered"
        move_ratio = 1.0
    elif total_weight_gp <= normal:
        level = "light"
        move_ratio = 1.0
    elif total_weight_gp <= heavy:
        level = "moderate"
        move_ratio = 0.75
    elif total_weight_gp <= maximum:
        level = "heavy"
        move_ratio = 0.50
    elif total_weight_gp <= int(maximum * 1.5):
        level = "severe"
        move_ratio = 0.25
    else:
        level = "immobile"
        move_ratio = 0.0

    adjusted = max(0, int(base_movement * move_ratio))

    # Describe penalty
    if move_ratio >= 1.0:
        penalty = "None"
    elif move_ratio >= 0.75:
        penalty = "Movement reduced to 3/4"
    elif move_ratio >= 0.50:
        penalty = "Movement reduced to 1/2"
    elif move_ratio >= 0.25:
        penalty = "Movement reduced to 1/4, -1 to AC"
    else:
        penalty = "Cannot move"

    return EncumbranceResult(
        total_weight_gp=total_weight_gp,
        normal_capacity=normal,
        heavy_capacity=heavy,
        max_capacity=maximum,
        encumbrance_level=level,
        base_movement=base_movement,
        adjusted_movement=adjusted,
        movement_penalty=penalty,
    )


def coins_to_weight(
    copper: int = 0,
    silver: int = 0,
    electrum: int = 0,
    gold: int = 0,
    platinum: int = 0,
) -> int:
    """Convert coin counts to gp weight (10 coins = 1 gp weight)."""
    total_coins = copper + silver + electrum + gold + platinum
    return total_coins  # In AD&D, coins are 1 gp weight each
