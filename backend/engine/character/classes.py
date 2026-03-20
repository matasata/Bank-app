"""AD&D 1st Edition class definitions.

Includes all PHB classes (Fighter, Paladin, Ranger, Magic-User, Illusionist,
Cleric, Druid, Thief, Assassin, Monk) and UA classes (Cavalier, Barbarian,
Thief-Acrobat).

Each class specifies ability requirements, hit dice, weapon/armour
proficiencies, XP tables (through level 15+), level titles, saving throw
group, and THAC0 / attack matrix group reference.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class ClassDefinition:
    """Complete definition of a character class."""

    name: str
    ability_requirements: Dict[str, int]
    hit_die: str  # e.g. "d10", "d4"
    hit_die_sides: int
    weapon_proficiencies_initial: int
    weapon_proficiency_penalty: int  # non-proficiency penalty
    weapon_proficiency_slots_per_level: int  # new slot every N levels
    armour_permitted: List[str]
    shield_permitted: bool
    save_group: str  # "Fighter", "Cleric", "Magic-User", "Thief"
    attack_group: str  # same keys as combat_matrices
    xp_table: List[Tuple[int, int]]  # (level, xp_needed)
    level_titles: Dict[int, str]
    prime_requisite: List[str]
    alignment_restrictions: List[str]  # empty = any
    description: str = ""
    special_abilities: List[str] = field(default_factory=list)
    spellcasting: bool = False

    def xp_for_level(self, level: int) -> int:
        """Return the cumulative XP needed to reach *level*."""
        for lvl, xp in self.xp_table:
            if lvl == level:
                return xp
        # Beyond table: extrapolate from last two entries
        if len(self.xp_table) >= 2:
            last_lvl, last_xp = self.xp_table[-1]
            prev_lvl, prev_xp = self.xp_table[-2]
            increment = last_xp - prev_xp
            extra_levels = level - last_lvl
            return last_xp + increment * extra_levels
        return 0

    def as_dict(self) -> Dict:
        """Serialise to a plain dictionary for API responses."""
        return {
            "name": self.name,
            "ability_requirements": self.ability_requirements,
            "hit_die": self.hit_die,
            "weapon_proficiencies_initial": self.weapon_proficiencies_initial,
            "weapon_proficiency_penalty": self.weapon_proficiency_penalty,
            "armour_permitted": self.armour_permitted,
            "shield_permitted": self.shield_permitted,
            "save_group": self.save_group,
            "attack_group": self.attack_group,
            "level_titles": self.level_titles,
            "prime_requisite": self.prime_requisite,
            "alignment_restrictions": self.alignment_restrictions,
            "special_abilities": self.special_abilities,
            "spellcasting": self.spellcasting,
            "description": self.description,
        }


# ═══════════════════════════════════════════════════════════════════════════
# PHB Classes
# ═══════════════════════════════════════════════════════════════════════════

FIGHTER = ClassDefinition(
    name="Fighter",
    ability_requirements={"str": 9},
    hit_die="d10", hit_die_sides=10,
    weapon_proficiencies_initial=4,
    weapon_proficiency_penalty=-2,
    weapon_proficiency_slots_per_level=3,
    armour_permitted=["All"],
    shield_permitted=True,
    save_group="Fighter", attack_group="Fighter",
    prime_requisite=["str"],
    alignment_restrictions=[],
    xp_table=[
        (1, 0), (2, 2000), (3, 4000), (4, 8000), (5, 18000),
        (6, 35000), (7, 70000), (8, 125000), (9, 250000), (10, 500000),
        (11, 750000), (12, 1000000), (13, 1250000), (14, 1500000), (15, 1750000),
    ],
    level_titles={
        1: "Veteran", 2: "Warrior", 3: "Swordsman", 4: "Hero",
        5: "Swashbuckler", 6: "Myrmidon", 7: "Champion", 8: "Superhero",
        9: "Lord",
    },
    special_abilities=[
        "Multiple attacks at higher levels (3/2 at 7th, 2/1 at 13th)",
        "Weapon specialization (UA)",
        "Attract followers at 9th level",
    ],
    description="Masters of martial combat, fighters excel at arms and armor.",
)

PALADIN = ClassDefinition(
    name="Paladin",
    ability_requirements={"str": 12, "int": 9, "wis": 13, "con": 9, "cha": 17},
    hit_die="d10", hit_die_sides=10,
    weapon_proficiencies_initial=4,
    weapon_proficiency_penalty=-2,
    weapon_proficiency_slots_per_level=3,
    armour_permitted=["All"],
    shield_permitted=True,
    save_group="Fighter", attack_group="Fighter",
    prime_requisite=["str", "wis"],
    alignment_restrictions=["Lawful Good"],
    xp_table=[
        (1, 0), (2, 2750), (3, 5500), (4, 12000), (5, 24000),
        (6, 45000), (7, 95000), (8, 175000), (9, 350000), (10, 700000),
        (11, 1050000), (12, 1400000), (13, 1750000), (14, 2100000), (15, 2450000),
    ],
    level_titles={
        1: "Gallant", 2: "Keeper", 3: "Protector", 4: "Defender",
        5: "Warder", 6: "Guardian", 7: "Chevalier", 8: "Justiciar",
        9: "Paladin",
    },
    special_abilities=[
        "Detect evil intent within 60'",
        "Protection from evil 10' radius (continuous)",
        "Immune to disease",
        "Lay on hands (2 hp/level, 1/day)",
        "Cure disease 1/week (2/week at 6th)",
        "+2 to all saving throws",
        "Turn undead as cleric 2 levels lower (at 3rd level)",
        "Cast cleric spells at 9th level",
        "Holy sword: dispel magic in 5' radius",
        "Warhorse summon",
    ],
    spellcasting=True,
    description="Holy warriors sworn to uphold law and goodness.",
)

RANGER = ClassDefinition(
    name="Ranger",
    ability_requirements={"str": 13, "int": 13, "wis": 14, "con": 14},
    hit_die="d8", hit_die_sides=8,
    weapon_proficiencies_initial=3,
    weapon_proficiency_penalty=-2,
    weapon_proficiency_slots_per_level=3,
    armour_permitted=["All"],
    shield_permitted=True,
    save_group="Fighter", attack_group="Fighter",
    prime_requisite=["str", "int", "wis"],
    alignment_restrictions=["Lawful Good", "Neutral Good", "Chaotic Good"],
    xp_table=[
        (1, 0), (2, 2250), (3, 4500), (4, 10000), (5, 20000),
        (6, 40000), (7, 90000), (8, 150000), (9, 300000), (10, 600000),
        (11, 900000), (12, 1200000), (13, 1500000), (14, 1800000), (15, 2100000),
    ],
    level_titles={
        1: "Runner", 2: "Strider", 3: "Scout", 4: "Courser",
        5: "Tracker", 6: "Guide", 7: "Pathfinder", 8: "Ranger",
        9: "Ranger Knight", 10: "Ranger Lord",
    },
    special_abilities=[
        "Damage bonus vs. giant class: +1/level",
        "Surprise: 1-3 on d6 (opponents surprised), surprised only 1 on d6",
        "Tracking ability",
        "Cast druid spells at 8th level, magic-user spells at 9th",
        "Two-handed fighting style",
        "Attract followers at 10th level",
    ],
    spellcasting=True,
    description="Wilderness warriors who combine martial skill with nature magic.",
)

MAGIC_USER = ClassDefinition(
    name="Magic-User",
    ability_requirements={"int": 9},
    hit_die="d4", hit_die_sides=4,
    weapon_proficiencies_initial=1,
    weapon_proficiency_penalty=-5,
    weapon_proficiency_slots_per_level=5,
    armour_permitted=[],
    shield_permitted=False,
    save_group="Magic-User", attack_group="Magic-User",
    prime_requisite=["int"],
    alignment_restrictions=[],
    xp_table=[
        (1, 0), (2, 2500), (3, 5000), (4, 10000), (5, 22500),
        (6, 40000), (7, 60000), (8, 90000), (9, 135000), (10, 250000),
        (11, 375000), (12, 750000), (13, 1125000), (14, 1500000), (15, 1875000),
    ],
    level_titles={
        1: "Prestidigitator", 2: "Evoker", 3: "Conjurer", 4: "Theurgist",
        5: "Thaumaturgist", 6: "Magician", 7: "Enchanter", 8: "Warlock",
        9: "Sorcerer", 10: "Necromancer", 11: "Wizard",
    },
    special_abilities=[
        "Arcane spellcasting from 1st level",
        "Spell research and item creation",
        "Construct stronghold at 12th level",
        "Attract apprentices",
    ],
    spellcasting=True,
    description="Masters of arcane magic, wielding devastating spells.",
)

ILLUSIONIST = ClassDefinition(
    name="Illusionist",
    ability_requirements={"int": 15, "dex": 16},
    hit_die="d4", hit_die_sides=4,
    weapon_proficiencies_initial=1,
    weapon_proficiency_penalty=-5,
    weapon_proficiency_slots_per_level=5,
    armour_permitted=[],
    shield_permitted=False,
    save_group="Magic-User", attack_group="Magic-User",
    prime_requisite=["int"],
    alignment_restrictions=[],
    xp_table=[
        (1, 0), (2, 2250), (3, 4500), (4, 9000), (5, 18000),
        (6, 35000), (7, 60000), (8, 95000), (9, 145000), (10, 220000),
        (11, 440000), (12, 660000), (13, 880000), (14, 1100000), (15, 1320000),
    ],
    level_titles={
        1: "Prestidigitator", 2: "Minor Trickster", 3: "Trickster",
        4: "Master Trickster", 5: "Cabalist", 6: "Visionist",
        7: "Phantasmist", 8: "Apparitionist", 9: "Spellbinder",
        10: "Illusionist",
    },
    special_abilities=[
        "Illusion/phantasm spellcasting from 1st level",
        "All gnome illusionist abilities",
    ],
    spellcasting=True,
    description="Specialists in illusion and phantasm magic.",
)

CLERIC = ClassDefinition(
    name="Cleric",
    ability_requirements={"wis": 9},
    hit_die="d8", hit_die_sides=8,
    weapon_proficiencies_initial=2,
    weapon_proficiency_penalty=-3,
    weapon_proficiency_slots_per_level=4,
    armour_permitted=["All"],
    shield_permitted=True,
    save_group="Cleric", attack_group="Cleric",
    prime_requisite=["wis"],
    alignment_restrictions=[],
    xp_table=[
        (1, 0), (2, 1500), (3, 3000), (4, 6000), (5, 13000),
        (6, 27500), (7, 55000), (8, 110000), (9, 225000), (10, 450000),
        (11, 675000), (12, 900000), (13, 1125000), (14, 1350000), (15, 1575000),
    ],
    level_titles={
        1: "Acolyte", 2: "Adept", 3: "Priest", 4: "Curate",
        5: "Prefect", 6: "Canon", 7: "Lama", 8: "Patriarch",
        9: "High Priest",
    },
    special_abilities=[
        "Divine spellcasting from 1st level",
        "Turn undead",
        "Blunt weapons only",
        "Attract followers at 8th level",
        "Build stronghold at 8th level",
    ],
    spellcasting=True,
    description="Servants of the divine, wielding holy magic and turning undead.",
)

DRUID = ClassDefinition(
    name="Druid",
    ability_requirements={"wis": 12, "cha": 15},
    hit_die="d8", hit_die_sides=8,
    weapon_proficiencies_initial=2,
    weapon_proficiency_penalty=-4,
    weapon_proficiency_slots_per_level=5,
    armour_permitted=["Leather"],
    shield_permitted=True,
    save_group="Cleric", attack_group="Cleric",
    prime_requisite=["wis", "cha"],
    alignment_restrictions=["True Neutral"],
    xp_table=[
        (1, 0), (2, 2000), (3, 4000), (4, 7500), (5, 12500),
        (6, 20000), (7, 35000), (8, 60000), (9, 90000), (10, 125000),
        (11, 200000), (12, 300000), (13, 750000), (14, 1500000),
    ],
    level_titles={
        1: "Aspirant", 2: "Ovate", 3: "Initiate of 3rd Circle",
        4: "Initiate of 4th Circle", 5: "Initiate of 5th Circle",
        6: "Initiate of 6th Circle", 7: "Initiate of 7th Circle",
        8: "Initiate of 8th Circle", 9: "Initiate of 9th Circle",
        10: "Druid", 11: "Druid", 12: "Archdruid",
        13: "The Great Druid", 14: "Grand Druid",
    },
    special_abilities=[
        "Druid spellcasting from 1st level",
        "Identify plants, animals, pure water",
        "Pass through overgrown areas at normal rate",
        "Immune to woodland charm (dryads, etc.)",
        "Shapechange 3/day at 7th level",
        "Woodland languages at higher levels",
    ],
    spellcasting=True,
    description="Nature priests who revere balance and the natural world.",
)

THIEF = ClassDefinition(
    name="Thief",
    ability_requirements={"dex": 9},
    hit_die="d6", hit_die_sides=6,
    weapon_proficiencies_initial=2,
    weapon_proficiency_penalty=-3,
    weapon_proficiency_slots_per_level=4,
    armour_permitted=["Leather", "Studded Leather", "Elven Chain"],
    shield_permitted=False,
    save_group="Thief", attack_group="Thief",
    prime_requisite=["dex"],
    alignment_restrictions=[
        "Neutral", "Chaotic Neutral", "Neutral Evil", "Chaotic Evil",
        "True Neutral", "Chaotic Good", "Neutral Good", "Lawful Neutral",
        "Lawful Evil",
    ],
    xp_table=[
        (1, 0), (2, 1250), (3, 2500), (4, 5000), (5, 10000),
        (6, 20000), (7, 42500), (8, 70000), (9, 110000), (10, 160000),
        (11, 220000), (12, 440000), (13, 660000), (14, 880000), (15, 1100000),
    ],
    level_titles={
        1: "Rogue", 2: "Footpad", 3: "Cutpurse", 4: "Robber",
        5: "Burglar", 6: "Filcher", 7: "Sharper", 8: "Magsman",
        9: "Thief", 10: "Master Thief",
    },
    special_abilities=[
        "Backstab: +4 to hit, x2 damage (x3 at 5th, x4 at 9th, x5 at 13th)",
        "Pick Pockets", "Open Locks", "Find/Remove Traps",
        "Move Silently", "Hide in Shadows", "Hear Noise",
        "Climb Walls", "Read Languages (at 4th level)",
        "Thieves' Cant language",
    ],
    description="Skilled rogues adept at stealth, traps, and underhanded tactics.",
)

ASSASSIN = ClassDefinition(
    name="Assassin",
    ability_requirements={"str": 12, "int": 11, "dex": 12},
    hit_die="d6", hit_die_sides=6,
    weapon_proficiencies_initial=3,
    weapon_proficiency_penalty=-3,
    weapon_proficiency_slots_per_level=4,
    armour_permitted=["Leather", "Studded Leather"],
    shield_permitted=True,
    save_group="Thief", attack_group="Thief",
    prime_requisite=["str", "int", "dex"],
    alignment_restrictions=["Neutral Evil", "Lawful Evil", "Chaotic Evil"],
    xp_table=[
        (1, 0), (2, 1500), (3, 3000), (4, 6000), (5, 12000),
        (6, 25000), (7, 50000), (8, 100000), (9, 200000), (10, 300000),
        (11, 425000), (12, 575000), (13, 750000), (14, 1000000), (15, 1500000),
    ],
    level_titles={
        1: "Bravo", 2: "Rutterkin", 3: "Waghalter", 4: "Murderer",
        5: "Thug", 6: "Killer", 7: "Cutthroat", 8: "Executioner",
        9: "Assassin", 10: "Expert Assassin", 11: "Senior Assassin",
        12: "Chief Assassin", 13: "Prime Assassin",
        14: "Guildmaster Assassin", 15: "Grandfather of Assassins",
    },
    special_abilities=[
        "Assassination table (instant kill chance)",
        "Backstab as thief",
        "Disguise ability",
        "Use poison",
        "Thief abilities at reduced effectiveness",
        "Spy ability at higher levels",
    ],
    description="Lethal killers-for-hire trained in the art of the silent kill.",
)

MONK = ClassDefinition(
    name="Monk",
    ability_requirements={"str": 15, "wis": 15, "dex": 15, "con": 11},
    hit_die="d4", hit_die_sides=4,
    weapon_proficiencies_initial=1,
    weapon_proficiency_penalty=-3,
    weapon_proficiency_slots_per_level=2,
    armour_permitted=[],
    shield_permitted=False,
    save_group="Thief", attack_group="Thief",
    prime_requisite=["str", "wis", "dex"],
    alignment_restrictions=["Lawful Good", "Lawful Neutral", "Lawful Evil"],
    xp_table=[
        (1, 0), (2, 2250), (3, 4750), (4, 10000), (5, 22500),
        (6, 47500), (7, 98000), (8, 200000), (9, 350000), (10, 500000),
        (11, 700000), (12, 950000), (13, 1250000), (14, 1750000),
        (15, 2250000), (16, 2750000), (17, 3250000),
    ],
    level_titles={
        1: "Novice", 2: "Initiate", 3: "Brother", 4: "Disciple",
        5: "Immaculate", 6: "Master", 7: "Superior Master",
        8: "Master of Dragons", 9: "Master of the North Wind",
        10: "Master of the West Wind", 11: "Master of the South Wind",
        12: "Master of the East Wind", 13: "Master of Winter",
        14: "Master of Autumn", 15: "Master of Summer",
        16: "Master of Spring", 17: "Grand Master of Flowers",
    },
    special_abilities=[
        "Open hand attacks (increasing damage with level)",
        "AC improvement with level (starts at 10, improves)",
        "Deflect missiles",
        "Slow fall",
        "Stunning/killing attack at 3rd level",
        "Immune to disease",
        "Feign death at 3rd level",
        "Self-healing at 7th level",
        "Speak with animals at 8th level",
        "Immune to ESP, charm, hypnosis at 9th level",
        "Immune to poison at 11th level",
        "Quivering palm at 13th level",
    ],
    description="Disciplined martial artists who harness inner power.",
)


# ═══════════════════════════════════════════════════════════════════════════
# UA Classes
# ═══════════════════════════════════════════════════════════════════════════

CAVALIER = ClassDefinition(
    name="Cavalier",
    ability_requirements={"str": 15, "int": 10, "wis": 10, "dex": 15, "con": 15},
    hit_die="d10", hit_die_sides=10,
    weapon_proficiencies_initial=5,
    weapon_proficiency_penalty=-2,
    weapon_proficiency_slots_per_level=3,
    armour_permitted=["All"],
    shield_permitted=True,
    save_group="Fighter", attack_group="Fighter",
    prime_requisite=["str", "dex"],
    alignment_restrictions=[
        "Lawful Good", "Lawful Neutral", "Lawful Evil",
        "Neutral Good", "Chaotic Good",
    ],
    xp_table=[
        (1, 0), (2, 2500), (3, 5000), (4, 10000), (5, 18500),
        (6, 37000), (7, 85000), (8, 140000), (9, 220000), (10, 300000),
        (11, 600000), (12, 900000), (13, 1200000), (14, 1500000), (15, 1800000),
    ],
    level_titles={
        1: "Armiger", 2: "Armiger", 3: "Horseman", 4: "Horseman",
        5: "Lancer", 6: "Lancer", 7: "Knight Bachelor",
        8: "Knight Bachelor", 9: "Knight Banneret",
    },
    special_abilities=[
        "Mounted combat bonuses (+1 to hit, +3 damage with lance)",
        "Immune to fear effects",
        "Horsemanship: airborne/land-based",
        "Charge attack: double damage with lance",
        "Weapon of choice: +1/+2 to hit/damage",
        "90% immune to mind-affecting magic at higher levels",
    ],
    description="Elite mounted warriors of noble birth, masters of the charge.",
)

BARBARIAN = ClassDefinition(
    name="Barbarian",
    ability_requirements={"str": 15, "con": 15, "dex": 14, "wis": 16},
    hit_die="d12", hit_die_sides=12,
    weapon_proficiencies_initial=4,
    weapon_proficiency_penalty=-1,
    weapon_proficiency_slots_per_level=3,
    armour_permitted=["Leather", "Studded Leather", "Scale Mail", "Chain Mail"],
    shield_permitted=True,
    save_group="Fighter", attack_group="Fighter",
    prime_requisite=["str", "con"],
    alignment_restrictions=[
        "Neutral Good", "Chaotic Good", "Chaotic Neutral",
        "True Neutral", "Neutral Evil", "Chaotic Evil",
    ],
    xp_table=[
        (1, 0), (2, 6000), (3, 12000), (4, 24000), (5, 48000),
        (6, 80000), (7, 150000), (8, 275000), (9, 500000), (10, 750000),
        (11, 1000000), (12, 1500000), (13, 2000000), (14, 2500000), (15, 3000000),
    ],
    level_titles={
        1: "Barbarian", 2: "Barbarian", 3: "Barbarian", 4: "Barbarian",
        5: "Barbarian", 6: "Barbarian", 7: "Barbarian", 8: "Barbarian",
    },
    special_abilities=[
        "d12 hit die (best in game)",
        "Immune to backstab at higher levels",
        "Detect magic at 3rd level (awareness of magic near)",
        "Climbing ability (similar to thief)",
        "Hide in natural terrain",
        "First aid (bind wounds)",
        "Outdoor surprise: 3-in-6 surprise opponents",
        "Leaping and springing",
        "Fear of magic: will not willingly use most magic items",
    ],
    description="Fierce warriors from untamed lands who distrust civilisation and magic.",
)

THIEF_ACROBAT = ClassDefinition(
    name="Thief-Acrobat",
    ability_requirements={"str": 15, "dex": 16},
    hit_die="d6", hit_die_sides=6,
    weapon_proficiencies_initial=2,
    weapon_proficiency_penalty=-3,
    weapon_proficiency_slots_per_level=4,
    armour_permitted=["Leather", "Padded"],
    shield_permitted=False,
    save_group="Thief", attack_group="Thief",
    prime_requisite=["dex"],
    alignment_restrictions=[
        "Neutral", "Chaotic Neutral", "Neutral Evil", "Chaotic Evil",
        "True Neutral", "Chaotic Good", "Neutral Good",
    ],
    xp_table=[
        (1, 0), (2, 1250), (3, 2500), (4, 5000), (5, 10000),
        (6, 20000), (7, 42500), (8, 70000), (9, 110000), (10, 160000),
        (11, 220000), (12, 440000), (13, 660000), (14, 880000), (15, 1100000),
    ],
    level_titles={
        1: "Rogue", 2: "Footpad", 3: "Cutpurse", 4: "Robber",
        5: "Burglar (Acrobat)", 6: "Tumbler", 7: "Acrobat",
        8: "Master Acrobat",
    },
    special_abilities=[
        "Thief abilities (until acrobat transition at 6th level)",
        "Tightrope walking",
        "Pole vaulting",
        "High jump / standing high jump",
        "Broad jump / standing broad jump",
        "Tumbling (falling damage reduction)",
        "Evasion: dodge area effects",
    ],
    description="A thief who transitions to acrobatic abilities at higher levels.",
)


# ═══════════════════════════════════════════════════════════════════════════
# Master registry
# ═══════════════════════════════════════════════════════════════════════════

ALL_CLASSES: Dict[str, ClassDefinition] = {
    cls.name: cls
    for cls in [
        FIGHTER, PALADIN, RANGER, MAGIC_USER, ILLUSIONIST,
        CLERIC, DRUID, THIEF, ASSASSIN, MONK,
        CAVALIER, BARBARIAN, THIEF_ACROBAT,
    ]
}


def get_class(name: str) -> ClassDefinition:
    """Return the class definition for *name*, or raise ``ValueError``."""
    cls = ALL_CLASSES.get(name)
    if cls is None:
        raise ValueError(f"Unknown class '{name}'. Available: {list(ALL_CLASSES.keys())}")
    return cls


def list_classes() -> List[Dict]:
    """Return all classes as plain dictionaries (for API responses)."""
    return [cls.as_dict() for cls in ALL_CLASSES.values()]
