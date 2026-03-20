"""AD&D 1st Edition attack resolution.

Uses combat matrices from the DMG to determine hits. Factors in attacker
level/HD, target AC, weapon bonuses, and situational modifiers. Returns
detailed roll breakdowns.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from engine.character.ability_scores import DiceRoller
from engine.rules.combat_matrices import get_to_hit_number, get_monster_to_hit


# ── Strength to-hit and damage bonuses ────────────────────────────────────
STR_TO_HIT: Dict[int, int] = {
    1: -5, 2: -3, 3: -3, 4: -2, 5: -2, 6: -1,
    7: -1, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0,
    15: 0, 16: 0, 17: +1, 18: +1, 19: +3,
}

STR_DAMAGE: Dict[int, int] = {
    1: -4, 2: -2, 3: -1, 4: -1, 5: -1, 6: 0,
    7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0,
    15: 0, 16: +1, 17: +1, 18: +2, 19: +7,
}

# ── Dexterity missile attack bonus ───────────────────────────────────────
DEX_MISSILE_BONUS: Dict[int, int] = {
    1: -5, 2: -4, 3: -3, 4: -2, 5: -1, 6: 0,
    7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0,
    15: 0, 16: +1, 17: +2, 18: +3, 19: +3,
}


@dataclass
class AttackResult:
    """Detailed result of a single attack resolution."""

    attacker_name: str
    target_name: str
    target_ac: int
    to_hit_needed: int
    d20_roll: int
    strength_mod: int
    magic_weapon_mod: int
    situational_mod: int
    total_attack_roll: int
    hit: bool
    natural_20: bool
    natural_1: bool
    damage_dice: List[int] = field(default_factory=list)
    base_damage: int = 0
    strength_damage_mod: int = 0
    magic_damage_mod: int = 0
    total_damage: int = 0
    critical: bool = False
    notes: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict:
        return {
            "attacker_name": self.attacker_name,
            "target_name": self.target_name,
            "target_ac": self.target_ac,
            "to_hit_needed": self.to_hit_needed,
            "d20_roll": self.d20_roll,
            "strength_mod": self.strength_mod,
            "magic_weapon_mod": self.magic_weapon_mod,
            "situational_mod": self.situational_mod,
            "total_attack_roll": self.total_attack_roll,
            "hit": self.hit,
            "natural_20": self.natural_20,
            "natural_1": self.natural_1,
            "damage_dice": self.damage_dice,
            "base_damage": self.base_damage,
            "strength_damage_mod": self.strength_damage_mod,
            "magic_damage_mod": self.magic_damage_mod,
            "total_damage": self.total_damage,
            "critical": self.critical,
            "notes": self.notes,
        }


def resolve_attack(
    attacker_name: str,
    attacker_class: str,
    attacker_level: int,
    target_name: str,
    target_ac: int,
    attacker_str: int = 10,
    attacker_dex: int = 10,
    damage_dice_num: int = 1,
    damage_dice_sides: int = 8,
    magic_weapon_bonus: int = 0,
    situational_modifier: int = 0,
    is_missile: bool = False,
    is_monster: bool = False,
    monster_hd: int = 1,
    seed: Optional[int] = None,
) -> AttackResult:
    """Resolve a single melee or missile attack.

    Uses the DMG combat matrices to determine the number needed to hit,
    then rolls a d20 with all applicable modifiers.

    Args:
        attacker_name: Display name of the attacker.
        attacker_class: Class name (for attack matrix lookup).
        attacker_level: Level of the attacker.
        target_name: Display name of the target.
        target_ac: Target's armour class.
        attacker_str: Attacker's Strength score (melee modifier).
        attacker_dex: Attacker's Dexterity score (missile modifier).
        damage_dice_num: Number of damage dice.
        damage_dice_sides: Sides per damage die.
        magic_weapon_bonus: Magic weapon bonus (to-hit AND damage).
        situational_modifier: Any additional to-hit modifier.
        is_missile: Whether this is a ranged attack.
        is_monster: Whether the attacker is a monster (uses monster matrix).
        monster_hd: Monster's Hit Dice (if *is_monster*).
        seed: Optional RNG seed.

    Returns:
        A detailed ``AttackResult``.
    """
    roller = DiceRoller(seed)

    # Determine to-hit number from matrix
    if is_monster:
        to_hit_needed = get_monster_to_hit(monster_hd, target_ac)
    else:
        to_hit_needed = get_to_hit_number(attacker_class, attacker_level, target_ac)

    # Roll d20
    d20_roll = roller._rng.randint(1, 20)
    natural_20 = d20_roll == 20
    natural_1 = d20_roll == 1

    # Ability modifiers
    if is_missile:
        str_hit_mod = DEX_MISSILE_BONUS.get(attacker_dex, 0)
        str_dmg_mod = 0  # DEX doesn't add damage (except composite bows)
    else:
        str_hit_mod = STR_TO_HIT.get(attacker_str, 0)
        str_dmg_mod = STR_DAMAGE.get(attacker_str, 0)

    total_roll = d20_roll + str_hit_mod + magic_weapon_bonus + situational_modifier

    # Determine hit
    if natural_1:
        hit = False
    elif natural_20:
        hit = True
    else:
        hit = total_roll >= to_hit_needed

    # Roll damage if hit
    damage_dice_results: List[int] = []
    base_damage = 0
    total_damage = 0

    if hit:
        damage_dice_results = roller.roll(damage_dice_num, damage_dice_sides)
        base_damage = sum(damage_dice_results)
        total_damage = max(0, base_damage + str_dmg_mod + magic_weapon_bonus)

    # Build notes
    notes: List[str] = []
    if natural_20:
        notes.append("Natural 20! Automatic hit.")
    if natural_1:
        notes.append("Natural 1! Automatic miss.")
    if hit and not natural_1:
        notes.append(f"Hit! {total_damage} damage dealt.")
    elif not hit:
        notes.append("Miss!")

    return AttackResult(
        attacker_name=attacker_name,
        target_name=target_name,
        target_ac=target_ac,
        to_hit_needed=to_hit_needed,
        d20_roll=d20_roll,
        strength_mod=str_hit_mod,
        magic_weapon_mod=magic_weapon_bonus,
        situational_mod=situational_modifier,
        total_attack_roll=total_roll,
        hit=hit,
        natural_20=natural_20,
        natural_1=natural_1,
        damage_dice=damage_dice_results,
        base_damage=base_damage,
        strength_damage_mod=str_dmg_mod,
        magic_damage_mod=magic_weapon_bonus,
        total_damage=total_damage,
        critical=natural_20,
        notes=notes,
    )
