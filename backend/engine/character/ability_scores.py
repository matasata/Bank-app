"""AD&D 1st Edition ability score generation methods (DMG Methods I-VI).

Each method returns both the individual roll details (so the UI can display
what was rolled and what was dropped) and the final six ability scores.

All dice rolling is handled through the ``DiceRoller`` utility class which
supports optional seeding for reproducible results.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ── Dice Roller utility ──────────────────────────────────────────────────

class DiceRoller:
    """A simple dice-rolling utility with optional deterministic seeding."""

    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)

    def roll(self, num_dice: int, sides: int) -> List[int]:
        """Roll *num_dice* dice each with *sides* faces and return each result."""
        return [self._rng.randint(1, sides) for _ in range(num_dice)]

    def roll_sum(self, num_dice: int, sides: int) -> Tuple[List[int], int]:
        """Roll and return ``(individual_rolls, total)``."""
        rolls = self.roll(num_dice, sides)
        return rolls, sum(rolls)

    def d6(self, n: int = 1) -> List[int]:
        """Shorthand for rolling *n* d6."""
        return self.roll(n, 6)

    def d10(self, n: int = 1) -> List[int]:
        """Shorthand for rolling *n* d10."""
        return self.roll(n, 10)

    def d20(self, n: int = 1) -> List[int]:
        """Shorthand for rolling *n* d20."""
        return self.roll(n, 20)

    def d100(self) -> int:
        """Roll percentile dice (1-100)."""
        return self._rng.randint(1, 100)


# ── Data classes for structured results ──────────────────────────────────

ABILITY_NAMES: List[str] = ["str", "int", "wis", "dex", "con", "cha"]


@dataclass
class SingleRollResult:
    """The result of rolling dice for a single ability score."""

    all_dice: List[int]
    kept_dice: List[int]
    total: int


@dataclass
class AbilityScoreResult:
    """Complete output from an ability score generation method."""

    method: str
    scores: Dict[str, int] = field(default_factory=dict)
    roll_details: List[SingleRollResult] = field(default_factory=list)
    extra: Dict = field(default_factory=dict)

    def as_dict(self) -> Dict:
        return {
            "method": self.method,
            "scores": self.scores,
            "roll_details": [
                {
                    "all_dice": r.all_dice,
                    "kept_dice": r.kept_dice,
                    "total": r.total,
                }
                for r in self.roll_details
            ],
            "extra": self.extra,
        }


# ── Method implementations ───────────────────────────────────────────────

def method_i(seed: Optional[int] = None) -> AbilityScoreResult:
    """**Method I** -- Roll 4d6, drop the lowest die, six times.

    The six totals are returned unassigned so the player can arrange them
    as desired among the six abilities.
    """
    roller = DiceRoller(seed)
    result = AbilityScoreResult(method="I")

    for _ in range(6):
        dice = roller.d6(4)
        sorted_dice = sorted(dice)
        kept = sorted_dice[1:]  # drop lowest
        total = sum(kept)
        result.roll_details.append(
            SingleRollResult(all_dice=list(dice), kept_dice=kept, total=total)
        )

    # Scores left unassigned -- caller arranges them
    totals = [r.total for r in result.roll_details]
    result.extra["available_scores"] = sorted(totals, reverse=True)
    return result


def method_ii(seed: Optional[int] = None) -> AbilityScoreResult:
    """**Method II** -- Roll 3d6 twelve times, keep the best six.

    Results are unassigned.
    """
    roller = DiceRoller(seed)
    result = AbilityScoreResult(method="II")

    all_rolls: List[SingleRollResult] = []
    for _ in range(12):
        dice = roller.d6(3)
        total = sum(dice)
        all_rolls.append(
            SingleRollResult(all_dice=list(dice), kept_dice=list(dice), total=total)
        )

    # Sort by total descending and keep best 6
    all_rolls.sort(key=lambda r: r.total, reverse=True)
    result.roll_details = all_rolls  # include all 12 for UI display
    best_six = [r.total for r in all_rolls[:6]]
    result.extra["all_twelve_totals"] = [r.total for r in all_rolls]
    result.extra["available_scores"] = sorted(best_six, reverse=True)
    return result


def method_iii(seed: Optional[int] = None) -> AbilityScoreResult:
    """**Method III** -- Roll 3d6 six times *for each ability*, keep the best.

    Scores are assigned in the standard ability order.
    """
    roller = DiceRoller(seed)
    result = AbilityScoreResult(method="III")

    for ability in ABILITY_NAMES:
        best_total = 0
        best_roll: Optional[SingleRollResult] = None
        ability_rolls: List[Dict] = []

        for _ in range(6):
            dice = roller.d6(3)
            total = sum(dice)
            roll_info = {"dice": list(dice), "total": total}
            ability_rolls.append(roll_info)
            if total > best_total:
                best_total = total
                best_roll = SingleRollResult(
                    all_dice=list(dice), kept_dice=list(dice), total=total
                )

        result.roll_details.append(best_roll)  # type: ignore[arg-type]
        result.scores[ability] = best_total
        result.extra.setdefault("per_ability_rolls", {})[ability] = ability_rolls

    return result


def method_iv(seed: Optional[int] = None) -> AbilityScoreResult:
    """**Method IV** -- Roll 3d6 twelve times *for each ability*, keep the best.

    Scores are assigned in the standard ability order.
    """
    roller = DiceRoller(seed)
    result = AbilityScoreResult(method="IV")

    for ability in ABILITY_NAMES:
        best_total = 0
        best_roll: Optional[SingleRollResult] = None
        ability_rolls: List[Dict] = []

        for _ in range(12):
            dice = roller.d6(3)
            total = sum(dice)
            ability_rolls.append({"dice": list(dice), "total": total})
            if total > best_total:
                best_total = total
                best_roll = SingleRollResult(
                    all_dice=list(dice), kept_dice=list(dice), total=total
                )

        result.roll_details.append(best_roll)  # type: ignore[arg-type]
        result.scores[ability] = best_total
        result.extra.setdefault("per_ability_rolls", {})[ability] = ability_rolls

    return result


def method_v(
    allocation: Optional[Dict[str, int]] = None,
    seed: Optional[int] = None,
) -> AbilityScoreResult:
    """**Method V** -- Point allocation.

    The player distributes 75 points among the six abilities with a
    minimum of 3 and maximum of 18 per score.

    If *allocation* is ``None`` a default even split is returned for preview.
    """
    result = AbilityScoreResult(method="V")
    total_points = 75
    min_score = 3
    max_score = 18

    if allocation is None:
        # Default: distribute evenly (12 each = 72, remaining 3 spread)
        base = total_points // 6
        remainder = total_points % 6
        allocation = {}
        for i, ability in enumerate(ABILITY_NAMES):
            allocation[ability] = base + (1 if i < remainder else 0)

    # Validate
    if sum(allocation.values()) != total_points:
        raise ValueError(
            f"Total points must equal {total_points}, got {sum(allocation.values())}"
        )

    for ability in ABILITY_NAMES:
        score = allocation.get(ability, min_score)
        if score < min_score or score > max_score:
            raise ValueError(
                f"{ability} score {score} out of range [{min_score}, {max_score}]"
            )
        result.scores[ability] = score
        result.roll_details.append(
            SingleRollResult(all_dice=[], kept_dice=[], total=score)
        )

    result.extra["total_points"] = total_points
    result.extra["min_score"] = min_score
    result.extra["max_score"] = max_score
    return result


def method_vi(seed: Optional[int] = None) -> AbilityScoreResult:
    """**Method VI** -- Roll 3d6 in order, but roll each ability six times
    and keep the best.

    Scores are assigned in the standard ability order (STR, INT, WIS, DEX,
    CON, CHA) -- no rearranging.
    """
    roller = DiceRoller(seed)
    result = AbilityScoreResult(method="VI")

    for ability in ABILITY_NAMES:
        best_total = 0
        best_roll: Optional[SingleRollResult] = None
        ability_rolls: List[Dict] = []

        for _ in range(6):
            dice = roller.d6(3)
            total = sum(dice)
            ability_rolls.append({"dice": list(dice), "total": total})
            if total > best_total:
                best_total = total
                best_roll = SingleRollResult(
                    all_dice=list(dice), kept_dice=list(dice), total=total
                )

        result.roll_details.append(best_roll)  # type: ignore[arg-type]
        result.scores[ability] = best_total
        result.extra.setdefault("per_ability_rolls", {})[ability] = ability_rolls

    return result


# ── Convenience dispatcher ───────────────────────────────────────────────

METHODS = {
    "I": method_i,
    "II": method_ii,
    "III": method_iii,
    "IV": method_iv,
    "V": method_v,
    "VI": method_vi,
}


def generate_ability_scores(
    method: str = "I",
    seed: Optional[int] = None,
    allocation: Optional[Dict[str, int]] = None,
) -> AbilityScoreResult:
    """Generate ability scores using the specified DMG method.

    Args:
        method: One of ``"I"`` through ``"VI"``.
        seed: Optional RNG seed for reproducibility.
        allocation: Only used with Method V -- point distribution dict.

    Returns:
        An ``AbilityScoreResult`` with all roll details and final scores.
    """
    method = method.upper().strip()
    if method not in METHODS:
        raise ValueError(f"Unknown method '{method}'. Choose from: {list(METHODS.keys())}")

    if method == "V":
        return method_v(allocation=allocation, seed=seed)
    return METHODS[method](seed=seed)
