"""AD&D 1st Edition race definitions.

Includes all PHB races (Human, Dwarf, Elf, Gnome, Half-Elf, Halfling,
Half-Orc) and UA races (Drow, Deep Gnome / Svirfneblin, Gray Dwarf /
Duergar, Valley Elf, Wild Elf, Wood Elf).

Each race specifies ability adjustments, minimum/maximum ability scores,
permitted classes (with level limits for demi-humans), multi-class
combinations, special abilities, age ranges, height/weight ranges, and
base movement rate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class AgeRange:
    """Starting age range and age category thresholds."""

    starting_min: int
    starting_max: int
    middle_age: int
    old: int
    venerable: int


@dataclass(frozen=True)
class HeightWeight:
    """Height (inches) and weight (lbs) ranges by sex."""

    male_height_base: int
    male_height_mod: str  # e.g. "1d10"
    female_height_base: int
    female_height_mod: str
    male_weight_base: int
    male_weight_mod: str
    female_weight_base: int
    female_weight_mod: str


@dataclass
class RaceDefinition:
    """Complete definition of a playable race."""

    name: str
    ability_adjustments: Dict[str, int] = field(default_factory=dict)
    ability_minimums: Dict[str, int] = field(default_factory=dict)
    ability_maximums: Dict[str, int] = field(default_factory=dict)
    permitted_classes: List[str] = field(default_factory=list)
    level_limits: Dict[str, int] = field(default_factory=dict)
    multi_class_options: List[Tuple[str, ...]] = field(default_factory=list)
    special_abilities: List[str] = field(default_factory=list)
    age_range: Optional[AgeRange] = None
    height_weight: Optional[HeightWeight] = None
    movement_rate: int = 12  # base movement in inches (squares)
    infravision: int = 0  # range in feet, 0 = none
    languages: List[str] = field(default_factory=list)
    description: str = ""

    def as_dict(self) -> Dict:
        """Serialise to a plain dictionary for API responses."""
        return {
            "name": self.name,
            "ability_adjustments": self.ability_adjustments,
            "ability_minimums": self.ability_minimums,
            "ability_maximums": self.ability_maximums,
            "permitted_classes": self.permitted_classes,
            "level_limits": self.level_limits,
            "multi_class_options": [list(mc) for mc in self.multi_class_options],
            "special_abilities": self.special_abilities,
            "movement_rate": self.movement_rate,
            "infravision": self.infravision,
            "languages": self.languages,
            "description": self.description,
        }


# ═══════════════════════════════════════════════════════════════════════════
# PHB Races
# ═══════════════════════════════════════════════════════════════════════════

HUMAN = RaceDefinition(
    name="Human",
    ability_adjustments={},
    ability_minimums={"str": 3, "int": 3, "wis": 3, "dex": 3, "con": 3, "cha": 3},
    ability_maximums={"str": 18, "int": 18, "wis": 18, "dex": 18, "con": 18, "cha": 18},
    permitted_classes=[
        "Fighter", "Paladin", "Ranger", "Magic-User", "Illusionist",
        "Cleric", "Druid", "Thief", "Assassin", "Monk",
        "Cavalier", "Barbarian", "Thief-Acrobat",
    ],
    level_limits={},  # Unlimited for all classes
    multi_class_options=[],
    special_abilities=["Unlimited level advancement in all classes"],
    age_range=AgeRange(starting_min=15, starting_max=20, middle_age=40, old=60, venerable=90),
    height_weight=HeightWeight(
        male_height_base=60, male_height_mod="1d10",
        female_height_base=59, female_height_mod="1d10",
        male_weight_base=140, male_weight_mod="3d10",
        female_weight_base=100, female_weight_mod="3d10",
    ),
    movement_rate=12,
    infravision=0,
    languages=["Common"],
    description="Humans are the most adaptable and ambitious of the common races.",
)

DWARF = RaceDefinition(
    name="Dwarf",
    ability_adjustments={"con": +1, "cha": -1},
    ability_minimums={"str": 8, "int": 3, "wis": 3, "dex": 3, "con": 12, "cha": 3},
    ability_maximums={"str": 18, "int": 18, "wis": 18, "dex": 17, "con": 19, "cha": 16},
    permitted_classes=["Fighter", "Thief", "Assassin", "Cleric"],
    level_limits={"Fighter": 9, "Thief": -1, "Assassin": 9, "Cleric": 8},
    multi_class_options=[("Fighter", "Thief")],
    special_abilities=[
        "Infravision 60'",
        "+1 to hit vs. orcs, half-orcs, goblins, hobgoblins",
        "-4 AC vs. giants, ogres, trolls, titans",
        "Detect stonework traps, sliding walls, new construction (1-2 on d6)",
        "Determine approximate depth underground (50%)",
        "Magic resistance: +1 per 3.5 CON to saves vs. magic/poison",
    ],
    age_range=AgeRange(starting_min=40, starting_max=60, middle_age=150, old=200, venerable=350),
    height_weight=HeightWeight(
        male_height_base=43, male_height_mod="1d10",
        female_height_base=41, female_height_mod="1d10",
        male_weight_base=130, male_weight_mod="4d10",
        female_weight_base=105, female_weight_mod="4d10",
    ),
    movement_rate=9,
    infravision=60,
    languages=["Common", "Dwarven", "Gnome", "Goblin", "Kobold", "Orcish"],
    description="Stout and sturdy, dwarves are renowned miners and fierce warriors.",
)

ELF = RaceDefinition(
    name="Elf",
    ability_adjustments={"dex": +1, "con": -1},
    ability_minimums={"str": 3, "int": 8, "wis": 3, "dex": 7, "con": 6, "cha": 8},
    ability_maximums={"str": 18, "int": 18, "wis": 18, "dex": 19, "con": 17, "cha": 18},
    permitted_classes=[
        "Fighter", "Ranger", "Magic-User", "Thief", "Assassin", "Cleric",
    ],
    level_limits={
        "Fighter": 7, "Ranger": 8, "Magic-User": 11, "Thief": -1,
        "Assassin": 10, "Cleric": 7,
    },
    multi_class_options=[
        ("Fighter", "Magic-User"),
        ("Fighter", "Thief"),
        ("Magic-User", "Thief"),
        ("Fighter", "Magic-User", "Thief"),
    ],
    special_abilities=[
        "Infravision 60'",
        "90% resistance to sleep and charm spells",
        "+1 to hit with bows and short/long swords",
        "Detect secret doors: 1 on d6 (passing), 1-2 on d6 (searching)",
        "Surprise opponents 4-in-6 when alone or with other elves",
    ],
    age_range=AgeRange(starting_min=100, starting_max=175, middle_age=500, old=750, venerable=1200),
    height_weight=HeightWeight(
        male_height_base=55, male_height_mod="1d10",
        female_height_base=50, female_height_mod="1d10",
        male_weight_base=90, male_weight_mod="3d10",
        female_weight_base=70, female_weight_mod="3d10",
    ),
    movement_rate=12,
    infravision=60,
    languages=["Common", "Elven", "Gnome", "Halfling", "Goblin", "Hobgoblin", "Orcish", "Gnoll"],
    description="Elves are graceful and long-lived, with a natural affinity for magic.",
)

GNOME = RaceDefinition(
    name="Gnome",
    ability_adjustments={"int": +1, "wis": -1},
    ability_minimums={"str": 6, "int": 7, "wis": 3, "dex": 3, "con": 8, "cha": 3},
    ability_maximums={"str": 18, "int": 18, "wis": 18, "dex": 18, "con": 18, "cha": 18},
    permitted_classes=["Fighter", "Illusionist", "Thief", "Assassin", "Cleric"],
    level_limits={"Fighter": 6, "Illusionist": 7, "Thief": -1, "Assassin": 8, "Cleric": 7},
    multi_class_options=[
        ("Fighter", "Illusionist"),
        ("Fighter", "Thief"),
        ("Illusionist", "Thief"),
    ],
    special_abilities=[
        "Infravision 60'",
        "+1 to hit vs. kobolds and goblins",
        "-4 AC vs. gnolls, bugbears, ogres, trolls, ogre magi, giants, titans",
        "Detect unsafe walls/ceilings/floors (1-7 on d12)",
        "Determine approximate depth (1-4 on d6)",
        "Determine approximate direction (1-3 on d6)",
        "Magic resistance: +1 per 3.5 CON to saves vs. magic",
    ],
    age_range=AgeRange(starting_min=60, starting_max=90, middle_age=200, old=300, venerable=500),
    height_weight=HeightWeight(
        male_height_base=38, male_height_mod="1d6",
        female_height_base=36, female_height_mod="1d6",
        male_weight_base=72, male_weight_mod="5d4",
        female_weight_base=68, female_weight_mod="5d4",
    ),
    movement_rate=9,
    infravision=60,
    languages=["Common", "Gnomish", "Dwarven", "Halfling", "Goblin", "Kobold"],
    description="Gnomes are clever and industrious, with a natural talent for illusion.",
)

HALF_ELF = RaceDefinition(
    name="Half-Elf",
    ability_adjustments={},
    ability_minimums={"str": 3, "int": 4, "wis": 3, "dex": 6, "con": 6, "cha": 3},
    ability_maximums={"str": 18, "int": 18, "wis": 18, "dex": 18, "con": 18, "cha": 18},
    permitted_classes=[
        "Fighter", "Ranger", "Magic-User", "Cleric", "Druid",
        "Thief", "Assassin",
    ],
    level_limits={
        "Fighter": 8, "Ranger": 8, "Magic-User": 8, "Cleric": 5,
        "Druid": -1, "Thief": -1, "Assassin": 11,
    },
    multi_class_options=[
        ("Fighter", "Magic-User"),
        ("Fighter", "Thief"),
        ("Fighter", "Magic-User", "Cleric"),
        ("Fighter", "Magic-User", "Thief"),
        ("Cleric", "Ranger"),
        ("Cleric", "Magic-User"),
        ("Thief", "Magic-User"),
    ],
    special_abilities=[
        "Infravision 30'",
        "30% resistance to sleep and charm spells",
        "Detect secret doors: 1 on d6 (passing), 1-2 on d6 (searching)",
    ],
    age_range=AgeRange(starting_min=22, starting_max=45, middle_age=100, old=150, venerable=250),
    height_weight=HeightWeight(
        male_height_base=58, male_height_mod="1d10",
        female_height_base=56, female_height_mod="1d10",
        male_weight_base=110, male_weight_mod="3d12",
        female_weight_base=85, female_weight_mod="3d12",
    ),
    movement_rate=12,
    infravision=30,
    languages=["Common", "Elven", "Gnome", "Halfling", "Goblin", "Hobgoblin", "Orcish", "Gnoll"],
    description="Half-elves combine human versatility with elven grace.",
)

HALFLING = RaceDefinition(
    name="Halfling",
    ability_adjustments={"dex": +1, "str": -1},
    ability_minimums={"str": 6, "int": 6, "wis": 3, "dex": 8, "con": 10, "cha": 3},
    ability_maximums={"str": 17, "int": 18, "wis": 17, "dex": 18, "con": 19, "cha": 18},
    permitted_classes=["Fighter", "Thief", "Druid"],
    level_limits={"Fighter": 4, "Thief": -1, "Druid": 6},
    multi_class_options=[("Fighter", "Thief")],
    special_abilities=[
        "Infravision 30' (Stout Halflings only)",
        "+1 to hit with slings and thrown weapons",
        "Magic resistance: +1 per 3.5 CON to saves vs. magic/poison",
        "Surprise opponents 4-in-6 (alone or with halflings/elves)",
        "Hide in natural surroundings: 90% if alone, 2-in-6 in dungeon",
    ],
    age_range=AgeRange(starting_min=20, starting_max=40, middle_age=75, old=100, venerable=150),
    height_weight=HeightWeight(
        male_height_base=32, male_height_mod="2d8",
        female_height_base=30, female_height_mod="2d8",
        male_weight_base=52, male_weight_mod="5d4",
        female_weight_base=48, female_weight_mod="5d4",
    ),
    movement_rate=9,
    infravision=30,
    languages=["Common", "Halfling", "Dwarven", "Elven", "Gnome", "Goblin", "Orcish"],
    description="Halflings are small but resilient, preferring comfort but capable of great courage.",
)

HALF_ORC = RaceDefinition(
    name="Half-Orc",
    ability_adjustments={"str": +1, "con": +1, "cha": -2},
    ability_minimums={"str": 6, "int": 3, "wis": 3, "dex": 3, "con": 13, "cha": 3},
    ability_maximums={"str": 18, "int": 17, "wis": 14, "dex": 17, "con": 19, "cha": 12},
    permitted_classes=["Fighter", "Cleric", "Thief", "Assassin"],
    level_limits={"Fighter": 10, "Cleric": 4, "Thief": 8, "Assassin": -1},
    multi_class_options=[
        ("Fighter", "Thief"),
        ("Fighter", "Cleric"),
        ("Cleric", "Thief"),
        ("Cleric", "Assassin"),
        ("Fighter", "Assassin"),
    ],
    special_abilities=[
        "Infravision 60'",
    ],
    age_range=AgeRange(starting_min=13, starting_max=18, middle_age=30, old=45, venerable=60),
    height_weight=HeightWeight(
        male_height_base=58, male_height_mod="2d4",
        female_height_base=56, female_height_mod="2d4",
        male_weight_base=130, male_weight_mod="5d4",
        female_weight_base=100, female_weight_mod="5d4",
    ),
    movement_rate=12,
    infravision=60,
    languages=["Common", "Orcish"],
    description="Half-orcs combine orcish strength with human cunning.",
)


# ═══════════════════════════════════════════════════════════════════════════
# UA (Unearthed Arcana) Races
# ═══════════════════════════════════════════════════════════════════════════

DROW = RaceDefinition(
    name="Drow",
    ability_adjustments={"dex": +1, "con": -1, "cha": +1, "int": +1},
    ability_minimums={"str": 3, "int": 8, "wis": 3, "dex": 8, "con": 6, "cha": 8},
    ability_maximums={"str": 18, "int": 18, "wis": 18, "dex": 19, "con": 17, "cha": 18},
    permitted_classes=["Fighter", "Magic-User", "Cleric", "Thief", "Assassin"],
    level_limits={"Fighter": 10, "Magic-User": 12, "Cleric": 9, "Thief": -1, "Assassin": 10},
    multi_class_options=[
        ("Fighter", "Magic-User"),
        ("Fighter", "Thief"),
        ("Magic-User", "Thief"),
        ("Fighter", "Magic-User", "Thief"),
    ],
    special_abilities=[
        "Infravision 120'",
        "Magic resistance: 50% + 2%/level",
        "Dancing lights, faerie fire, darkness at will",
        "Detect secret doors: 1 on d6 (passing), 1-2 on d6 (searching)",
        "90% resistance to sleep and charm",
        "Surprise 4-in-6",
        "Light sensitivity: -2 to hit in bright light",
    ],
    age_range=AgeRange(starting_min=100, starting_max=175, middle_age=500, old=750, venerable=1000),
    height_weight=HeightWeight(
        male_height_base=50, male_height_mod="1d10",
        female_height_base=50, female_height_mod="1d10",
        male_weight_base=80, male_weight_mod="3d10",
        female_weight_base=80, female_weight_mod="3d10",
    ),
    movement_rate=12,
    infravision=120,
    languages=["Common", "Undercommon", "Elven", "Drow Sign Language"],
    description="Dark elves dwelling in the Underdark, powerful but light-sensitive.",
)

DEEP_GNOME = RaceDefinition(
    name="Deep Gnome",
    ability_adjustments={"int": +1, "wis": -1, "dex": +1, "cha": -2},
    ability_minimums={"str": 6, "int": 7, "wis": 3, "dex": 3, "con": 8, "cha": 3},
    ability_maximums={"str": 18, "int": 18, "wis": 18, "dex": 18, "con": 18, "cha": 16},
    permitted_classes=["Fighter", "Illusionist", "Thief", "Assassin"],
    level_limits={"Fighter": 6, "Illusionist": 7, "Thief": -1, "Assassin": 8},
    multi_class_options=[
        ("Fighter", "Illusionist"),
        ("Fighter", "Thief"),
        ("Illusionist", "Thief"),
    ],
    special_abilities=[
        "Infravision 120'",
        "Magic resistance: 20% + 5%/level",
        "Blindness, blur, change self -- each 1/day",
        "Non-detection (permanent, self only)",
        "Surprise opponents 1-9 on d10, surprised only on 1 on d10",
        "+1 to hit vs. kobolds and goblins",
        "-4 AC vs. gnolls, bugbears, ogres, trolls, giants, titans",
    ],
    age_range=AgeRange(starting_min=60, starting_max=90, middle_age=200, old=300, venerable=500),
    height_weight=HeightWeight(
        male_height_base=36, male_height_mod="1d6",
        female_height_base=34, female_height_mod="1d6",
        male_weight_base=68, male_weight_mod="5d4",
        female_weight_base=64, female_weight_mod="5d4",
    ),
    movement_rate=9,
    infravision=120,
    languages=["Common", "Gnomish", "Undercommon", "Dwarven"],
    description="Svirfneblin: deep-dwelling gnomes with potent innate magical abilities.",
)

GRAY_DWARF = RaceDefinition(
    name="Gray Dwarf",
    ability_adjustments={"con": +1, "cha": -2},
    ability_minimums={"str": 8, "int": 3, "wis": 3, "dex": 3, "con": 12, "cha": 3},
    ability_maximums={"str": 18, "int": 18, "wis": 18, "dex": 17, "con": 19, "cha": 14},
    permitted_classes=["Fighter", "Thief", "Assassin"],
    level_limits={"Fighter": 9, "Thief": -1, "Assassin": 9},
    multi_class_options=[("Fighter", "Thief")],
    special_abilities=[
        "Infravision 120'",
        "Enlarged (self) 1/day",
        "Invisibility (self) 1/day",
        "Immune to paralysis, illusion/phantasm, poison",
        "Light sensitivity: -2 to hit in bright light",
        "Detect stonework traps, sliding walls (1-2 on d6)",
        "+1 per 3.5 CON save bonus vs. magic",
    ],
    age_range=AgeRange(starting_min=40, starting_max=60, middle_age=150, old=200, venerable=350),
    height_weight=HeightWeight(
        male_height_base=42, male_height_mod="1d8",
        female_height_base=40, female_height_mod="1d8",
        male_weight_base=120, male_weight_mod="4d10",
        female_weight_base=100, female_weight_mod="4d10",
    ),
    movement_rate=9,
    infravision=120,
    languages=["Common", "Dwarven", "Undercommon"],
    description="Duergar: grim dwarves of the Underdark with psionic-like abilities.",
)

VALLEY_ELF = RaceDefinition(
    name="Valley Elf",
    ability_adjustments={"dex": +1, "con": -1},
    ability_minimums={"str": 3, "int": 8, "wis": 3, "dex": 7, "con": 6, "cha": 8},
    ability_maximums={"str": 18, "int": 18, "wis": 18, "dex": 19, "con": 17, "cha": 18},
    permitted_classes=["Fighter", "Ranger", "Magic-User", "Thief", "Assassin", "Cleric"],
    level_limits={
        "Fighter": 7, "Ranger": 8, "Magic-User": 12, "Thief": -1,
        "Assassin": 10, "Cleric": 7,
    },
    multi_class_options=[
        ("Fighter", "Magic-User"),
        ("Fighter", "Thief"),
        ("Magic-User", "Thief"),
        ("Fighter", "Magic-User", "Thief"),
    ],
    special_abilities=[
        "Infravision 60'",
        "90% resistance to sleep and charm",
        "+1 to hit with bows and swords",
        "Detect secret doors: 1 on d6 (passing), 1-2 on d6 (searching)",
        "Surprise opponents 4-in-6",
    ],
    age_range=AgeRange(starting_min=100, starting_max=175, middle_age=550, old=800, venerable=1300),
    height_weight=HeightWeight(
        male_height_base=55, male_height_mod="1d10",
        female_height_base=50, female_height_mod="1d10",
        male_weight_base=90, male_weight_mod="3d10",
        female_weight_base=70, female_weight_mod="3d10",
    ),
    movement_rate=12,
    infravision=60,
    languages=["Common", "Elven", "Gnome", "Halfling", "Goblin", "Hobgoblin", "Orcish"],
    description="Valley elves are reclusive high elves dwelling in hidden mountain vales.",
)

WILD_ELF = RaceDefinition(
    name="Wild Elf",
    ability_adjustments={"dex": +1, "con": -1},
    ability_minimums={"str": 3, "int": 8, "wis": 3, "dex": 7, "con": 6, "cha": 8},
    ability_maximums={"str": 18, "int": 18, "wis": 18, "dex": 19, "con": 17, "cha": 18},
    permitted_classes=["Fighter", "Thief"],
    level_limits={"Fighter": 6, "Thief": -1},
    multi_class_options=[("Fighter", "Thief")],
    special_abilities=[
        "Infravision 60'",
        "90% resistance to sleep and charm",
        "+1 to hit with bows and short swords",
        "Detect secret doors: 1 on d6 (passing), 1-2 on d6 (searching)",
        "Surprise opponents 4-in-6",
        "Camouflage in natural terrain (95%)",
    ],
    age_range=AgeRange(starting_min=100, starting_max=175, middle_age=500, old=750, venerable=1200),
    height_weight=HeightWeight(
        male_height_base=54, male_height_mod="1d10",
        female_height_base=49, female_height_mod="1d10",
        male_weight_base=85, male_weight_mod="3d10",
        female_weight_base=65, female_weight_mod="3d10",
    ),
    movement_rate=12,
    infravision=60,
    languages=["Common", "Elven"],
    description="Grugach: fiercely territorial elves of the deep forests.",
)

WOOD_ELF = RaceDefinition(
    name="Wood Elf",
    ability_adjustments={"dex": +1, "con": -1},
    ability_minimums={"str": 3, "int": 8, "wis": 3, "dex": 7, "con": 6, "cha": 8},
    ability_maximums={"str": 18, "int": 18, "wis": 18, "dex": 19, "con": 17, "cha": 18},
    permitted_classes=["Fighter", "Ranger", "Magic-User", "Thief", "Druid"],
    level_limits={"Fighter": 7, "Ranger": 7, "Magic-User": 9, "Thief": -1, "Druid": 7},
    multi_class_options=[
        ("Fighter", "Magic-User"),
        ("Fighter", "Thief"),
        ("Magic-User", "Thief"),
    ],
    special_abilities=[
        "Infravision 60'",
        "90% resistance to sleep and charm",
        "+1 to hit with bows and short swords",
        "Detect secret doors: 1 on d6 (passing), 1-2 on d6 (searching)",
        "Surprise opponents 4-in-6",
        "Pass without trace in forests",
    ],
    age_range=AgeRange(starting_min=100, starting_max=175, middle_age=500, old=750, venerable=1200),
    height_weight=HeightWeight(
        male_height_base=54, male_height_mod="1d10",
        female_height_base=49, female_height_mod="1d10",
        male_weight_base=85, male_weight_mod="3d10",
        female_weight_base=65, female_weight_mod="3d10",
    ),
    movement_rate=12,
    infravision=60,
    languages=["Common", "Elven", "Gnome", "Halfling", "Goblin", "Orcish"],
    description="Sylvan elves inhabiting temperate woodlands, close to nature.",
)


# ═══════════════════════════════════════════════════════════════════════════
# Master registry
# ═══════════════════════════════════════════════════════════════════════════

ALL_RACES: Dict[str, RaceDefinition] = {
    race.name: race
    for race in [
        HUMAN, DWARF, ELF, GNOME, HALF_ELF, HALFLING, HALF_ORC,
        DROW, DEEP_GNOME, GRAY_DWARF, VALLEY_ELF, WILD_ELF, WOOD_ELF,
    ]
}


def get_race(name: str) -> RaceDefinition:
    """Return the race definition for *name*, or raise ``ValueError``."""
    race = ALL_RACES.get(name)
    if race is None:
        raise ValueError(f"Unknown race '{name}'. Available: {list(ALL_RACES.keys())}")
    return race


def list_races() -> List[Dict]:
    """Return all races as plain dictionaries (for API responses)."""
    return [race.as_dict() for race in ALL_RACES.values()]
