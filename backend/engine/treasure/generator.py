"""Treasure generation per DMG treasure type tables (A-Z).

Includes gem and jewelry value generation and magic item table rolls
(swords, potions, scrolls, rings, wands, armour, miscellaneous).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from engine.character.ability_scores import DiceRoller


# ── Gem base value table (DMG) ────────────────────────────────────────────
GEM_BASE_VALUES: List[Tuple[int, int, str]] = [
    (25, 10, "Ornamental"),
    (50, 50, "Semi-precious"),
    (70, 100, "Fancy"),
    (90, 500, "Precious"),
    (99, 1000, "Gem"),
    (100, 5000, "Jewel"),
]

GEM_TYPES: Dict[int, List[str]] = {
    10: ["Azurite", "Banded agate", "Blue quartz", "Eye agate",
         "Hematite", "Lapis lazuli", "Malachite", "Moss agate",
         "Obsidian", "Rhodochrosite", "Tiger eye", "Turquoise"],
    50: ["Bloodstone", "Carnelian", "Chalcedony", "Chrysoprase",
         "Citrine", "Jasper", "Moonstone", "Onyx", "Rock crystal",
         "Sardonyx", "Smoky quartz", "Star rose quartz", "Zircon"],
    100: ["Amber", "Alexandrite", "Amethyst", "Chrysoberyl",
          "Coral", "Garnet", "Jade", "Jet", "Pearl", "Spinel",
          "Tourmaline"],
    500: ["Aquamarine", "Black pearl", "Blue spinel", "Peridot",
          "Topaz"],
    1000: ["Black opal", "Emerald", "Fire opal", "Opal",
           "Oriental amethyst", "Oriental topaz", "Sapphire",
           "Star ruby", "Star sapphire"],
    5000: ["Black sapphire", "Diamond", "Jacinth", "Oriental emerald",
           "Ruby"],
}


# ── Jewelry value table ──────────────────────────────────────────────────
JEWELRY_VALUES: List[Tuple[int, Tuple[int, int, int]]] = [
    # (d100_threshold, (num_dice, sides, multiplier))
    (10, (1, 10, 100)),
    (25, (2, 6, 100)),
    (50, (3, 6, 100)),
    (70, (5, 6, 100)),
    (85, (1, 6, 1000)),
    (92, (1, 10, 1000)),
    (97, (2, 6, 1000)),
    (99, (3, 6, 1000)),
    (100, (5, 6, 1000)),
]


# ── Magic item master tables ─────────────────────────────────────────────

POTION_TABLE: List[Tuple[int, str]] = [
    (3, "Potion of Animal Control"), (6, "Potion of Clairaudience"),
    (9, "Potion of Clairvoyance"), (12, "Potion of Climbing"),
    (15, "Potion of Delusion"), (18, "Potion of Diminution"),
    (21, "Potion of Dragon Control"), (24, "Potion of ESP"),
    (30, "Potion of Extra-Healing"), (33, "Potion of Fire Resistance"),
    (36, "Potion of Flying"), (39, "Potion of Gaseous Form"),
    (42, "Potion of Giant Control"), (45, "Potion of Giant Strength"),
    (48, "Potion of Growth"), (54, "Potion of Healing"),
    (57, "Potion of Heroism"), (60, "Potion of Human Control"),
    (63, "Potion of Invisibility"), (66, "Potion of Invulnerability"),
    (69, "Potion of Levitation"), (72, "Potion of Longevity"),
    (75, "Potion of Oil of Etherealness"),
    (78, "Potion of Oil of Slipperiness"),
    (81, "Potion of Philter of Love"),
    (84, "Potion of Philter of Persuasiveness"),
    (87, "Potion of Plant Control"), (89, "Potion of Polymorph Self"),
    (97, "Potion of Speed"), (100, "Potion of Super-Heroism"),
]

SCROLL_TABLE: List[Tuple[int, str]] = [
    (5, "Scroll of Protection from Demons"),
    (10, "Scroll of Protection from Devils"),
    (15, "Scroll of Protection from Elementals"),
    (20, "Scroll of Protection from Lycanthropes"),
    (25, "Scroll of Protection from Magic"),
    (30, "Scroll of Protection from Petrification"),
    (35, "Scroll of Protection from Possession"),
    (40, "Scroll of Protection from Undead"),
    (55, "Scroll with 1 spell (level 1-4)"),
    (65, "Scroll with 2 spells (level 1-6)"),
    (75, "Scroll with 3 spells (level 2-7)"),
    (85, "Scroll with 4 spells (level 2-9)"),
    (90, "Scroll with 5 spells (level 3-9)"),
    (95, "Scroll with 6 spells (level 4-9)"),
    (98, "Scroll with 7 spells (level 5-9)"),
    (100, "Cursed scroll"),
]

RING_TABLE: List[Tuple[int, str]] = [
    (6, "Ring of Contrariness"), (12, "Ring of Delusion"),
    (18, "Ring of Djinni Summoning"), (26, "Ring of Feather Falling"),
    (32, "Ring of Fire Resistance"), (38, "Ring of Free Action"),
    (44, "Ring of Human Influence"), (50, "Ring of Invisibility"),
    (56, "Ring of Mammal Control"), (61, "Ring of Multiple Wishes"),
    (63, "Ring of Protection +1"), (72, "Ring of Protection +2"),
    (74, "Ring of Protection +3"), (76, "Ring of Regeneration"),
    (79, "Ring of Shooting Stars"), (82, "Ring of Spell Storing"),
    (86, "Ring of Spell Turning"), (89, "Ring of Swimming"),
    (92, "Ring of Telekinesis"), (96, "Ring of Three Wishes"),
    (98, "Ring of Warmth"), (99, "Ring of Water Walking"),
    (100, "Ring of Wizardry"),
]

WAND_TABLE: List[Tuple[int, str]] = [
    (8, "Wand of Enemy Detection"), (14, "Wand of Fear"),
    (20, "Wand of Fire"), (26, "Wand of Frost"),
    (32, "Wand of Illumination"), (38, "Wand of Illusion"),
    (44, "Wand of Lightning"), (50, "Wand of Magic Detection"),
    (55, "Wand of Magic Missiles"), (60, "Wand of Metal Detection"),
    (65, "Wand of Negation"), (70, "Wand of Paralyzation"),
    (75, "Wand of Polymorphing"), (80, "Wand of Secret Door Detection"),
    (85, "Wand of Wonder"), (90, "Staff of Commanding"),
    (93, "Staff of Curing"), (95, "Staff of the Magi"),
    (97, "Staff of Power"), (99, "Staff of the Serpent"),
    (100, "Staff of Striking"),
]

SWORD_TABLE: List[Tuple[int, str]] = [
    (25, "Sword +1"), (30, "Sword +1, +2 vs. magic-using types"),
    (35, "Sword +1, +3 vs. lycanthropes"),
    (40, "Sword +1, +3 vs. regenerating creatures"),
    (45, "Sword +1, +4 vs. reptiles"),
    (50, "Sword +1, Flame Tongue"),
    (55, "Sword +1, Luck Blade"),
    (60, "Sword +2"),
    (65, "Sword +2, Giant Slayer"),
    (70, "Sword +2, Dragon Slayer"),
    (75, "Sword +3"),
    (78, "Sword +3, Frost Brand"),
    (82, "Sword +4"),
    (85, "Sword +4, Defender"),
    (88, "Sword +5"),
    (90, "Sword +5, Defender"),
    (91, "Sword +5, Holy Avenger"),
    (93, "Sword of Sharpness"),
    (95, "Vorpal Sword"),
    (97, "Sword +1, Cursed"),
    (99, "Sword -2, Cursed"),
    (100, "Sword of Dancing"),
]

ARMOR_TABLE: List[Tuple[int, str]] = [
    (20, "Armor +1"), (35, "Armor +2"), (45, "Armor +3"),
    (50, "Armor +4"), (52, "Armor +5"),
    (55, "Shield +1"), (65, "Shield +2"), (70, "Shield +3"),
    (72, "Shield +4"), (73, "Shield +5"),
    (78, "Armor of Vulnerability"), (85, "Plate Mail of Etherealness"),
    (90, "Elven Chain Mail"), (95, "Shield, Large, +1, +4 vs. missiles"),
    (100, "Armor +1, Cursed (AC worsened)"),
]

MISC_MAGIC_TABLE: List[Tuple[int, str]] = [
    (5, "Amulet of Inescapable Location"), (8, "Amulet of Life Protection"),
    (12, "Amulet of Proof Against Detection and Location"),
    (15, "Amulet of the Planes"), (17, "Apparatus of Kwalish"),
    (20, "Arrow of Direction"), (22, "Bag of Beans"),
    (24, "Bag of Devouring"), (28, "Bag of Holding"),
    (31, "Bag of Tricks"), (33, "Beaker of Plentiful Potions"),
    (35, "Boat, Folding"), (37, "Book of Exalted Deeds"),
    (38, "Book of Infinite Spells"), (39, "Book of Vile Darkness"),
    (41, "Boots of Dancing"), (45, "Boots of Elvenkind"),
    (47, "Boots of Levitation"), (50, "Boots of Speed"),
    (52, "Boots of Striding and Springing"),
    (55, "Bowl Commanding Water Elementals"),
    (57, "Bracers of Defense AC 6"), (59, "Bracers of Defense AC 4"),
    (60, "Bracers of Defense AC 2"),
    (62, "Brazier Commanding Fire Elementals"),
    (65, "Brooch of Shielding"), (68, "Broom of Flying"),
    (70, "Carpet of Flying"), (72, "Censer Controlling Air Elementals"),
    (73, "Chime of Opening"), (75, "Cloak of Displacement"),
    (78, "Cloak of Elvenkind"), (81, "Cloak of Protection +1"),
    (83, "Cloak of Protection +2"), (84, "Cloak of Protection +3"),
    (85, "Crystal Ball"), (87, "Cube of Force"),
    (88, "Cube of Frost Resistance"),
    (89, "Cubic Gate"), (91, "Decanter of Endless Water"),
    (93, "Deck of Many Things"), (95, "Dust of Appearance"),
    (96, "Dust of Disappearance"), (97, "Dust of Sneezing and Choking"),
    (98, "Efreeti Bottle"), (99, "Eyes of the Eagle"),
    (100, "Figurine of Wondrous Power"),
]

# ── The master "magic item category" table ───────────────────────────────
MAGIC_ITEM_CATEGORY: List[Tuple[int, str]] = [
    (20, "potion"),
    (35, "scroll"),
    (40, "ring"),
    (45, "wand"),
    (55, "sword"),
    (70, "armor"),
    (100, "misc"),
]

MAGIC_TABLES: Dict[str, List[Tuple[int, str]]] = {
    "potion": POTION_TABLE,
    "scroll": SCROLL_TABLE,
    "ring": RING_TABLE,
    "wand": WAND_TABLE,
    "sword": SWORD_TABLE,
    "armor": ARMOR_TABLE,
    "misc": MISC_MAGIC_TABLE,
}


# ── Treasure type tables (A-Z) ──────────────────────────────────────────
# Format per type:
#   copper, silver, electrum, gold, platinum, gems, jewelry, magic
# Each entry: (chance%, num_dice, sides, multiplier) or None
@dataclass
class TreasureTypeEntry:
    """Definition for a single coin/gem/magic row in a treasure type."""

    chance: int  # percent chance
    num_dice: int = 0
    sides: int = 0
    multiplier: int = 1

    def roll(self, roller: DiceRoller) -> int:
        """Roll the quantity if the chance succeeds, else return 0."""
        if roller.d100() > self.chance:
            return 0
        if self.num_dice == 0:
            return 0
        rolls = roller.roll(self.num_dice, self.sides)
        return sum(rolls) * self.multiplier


@dataclass
class TreasureType:
    """A complete treasure type from the DMG tables."""

    name: str
    copper: Optional[TreasureTypeEntry] = None
    silver: Optional[TreasureTypeEntry] = None
    electrum: Optional[TreasureTypeEntry] = None
    gold: Optional[TreasureTypeEntry] = None
    platinum: Optional[TreasureTypeEntry] = None
    gems: Optional[TreasureTypeEntry] = None
    jewelry: Optional[TreasureTypeEntry] = None
    magic_chance: int = 0  # percent
    magic_items: int = 0  # number of rolls on magic tables


TREASURE_TYPES: Dict[str, TreasureType] = {
    "A": TreasureType(
        name="A",
        copper=TreasureTypeEntry(25, 1, 6, 1000),
        silver=TreasureTypeEntry(30, 1, 6, 1000),
        electrum=TreasureTypeEntry(35, 1, 6, 1000),
        gold=TreasureTypeEntry(40, 1, 10, 1000),
        platinum=TreasureTypeEntry(25, 1, 4, 100),
        gems=TreasureTypeEntry(60, 4, 10, 1),
        jewelry=TreasureTypeEntry(50, 3, 10, 1),
        magic_chance=30, magic_items=3,
    ),
    "B": TreasureType(
        name="B",
        copper=TreasureTypeEntry(50, 1, 8, 1000),
        silver=TreasureTypeEntry(25, 1, 6, 1000),
        electrum=TreasureTypeEntry(25, 1, 4, 1000),
        gold=TreasureTypeEntry(25, 1, 3, 1000),
        gems=TreasureTypeEntry(25, 1, 8, 1),
        jewelry=TreasureTypeEntry(25, 1, 4, 1),
        magic_chance=10, magic_items=1,
    ),
    "C": TreasureType(
        name="C",
        copper=TreasureTypeEntry(20, 1, 12, 1000),
        silver=TreasureTypeEntry(30, 1, 6, 1000),
        electrum=TreasureTypeEntry(10, 1, 4, 1000),
        gems=TreasureTypeEntry(25, 1, 6, 1),
        jewelry=TreasureTypeEntry(20, 1, 3, 1),
        magic_chance=10, magic_items=2,
    ),
    "D": TreasureType(
        name="D",
        copper=TreasureTypeEntry(10, 1, 8, 1000),
        silver=TreasureTypeEntry(15, 1, 12, 1000),
        electrum=TreasureTypeEntry(15, 1, 8, 1000),
        gold=TreasureTypeEntry(50, 1, 6, 1000),
        gems=TreasureTypeEntry(30, 1, 10, 1),
        jewelry=TreasureTypeEntry(25, 1, 6, 1),
        magic_chance=15, magic_items=2,
    ),
    "E": TreasureType(
        name="E",
        copper=TreasureTypeEntry(5, 1, 10, 1000),
        silver=TreasureTypeEntry(25, 1, 12, 1000),
        electrum=TreasureTypeEntry(25, 1, 6, 1000),
        gold=TreasureTypeEntry(25, 1, 8, 1000),
        gems=TreasureTypeEntry(15, 1, 12, 1),
        jewelry=TreasureTypeEntry(10, 1, 8, 1),
        magic_chance=25, magic_items=3,
    ),
    "F": TreasureType(
        name="F",
        silver=TreasureTypeEntry(10, 1, 20, 1000),
        electrum=TreasureTypeEntry(15, 1, 12, 1000),
        gold=TreasureTypeEntry(40, 1, 10, 1000),
        platinum=TreasureTypeEntry(35, 1, 8, 100),
        gems=TreasureTypeEntry(20, 2, 12, 1),
        jewelry=TreasureTypeEntry(10, 1, 12, 1),
        magic_chance=30, magic_items=3,
    ),
    "G": TreasureType(
        name="G",
        gold=TreasureTypeEntry(50, 1, 4, 10000),
        platinum=TreasureTypeEntry(50, 1, 6, 1000),
        gems=TreasureTypeEntry(30, 3, 6, 1),
        jewelry=TreasureTypeEntry(25, 1, 10, 1),
        magic_chance=35, magic_items=4,
    ),
    "H": TreasureType(
        name="H",
        copper=TreasureTypeEntry(25, 5, 6, 1000),
        silver=TreasureTypeEntry(40, 1, 100, 1000),
        electrum=TreasureTypeEntry(40, 1, 4, 10000),
        gold=TreasureTypeEntry(55, 1, 6, 10000),
        platinum=TreasureTypeEntry(25, 1, 8, 1000),
        gems=TreasureTypeEntry(50, 1, 100, 1),
        jewelry=TreasureTypeEntry(50, 10, 4, 1),
        magic_chance=15, magic_items=4,
    ),
    "I": TreasureType(
        name="I",
        platinum=TreasureTypeEntry(30, 1, 8, 100),
        gems=TreasureTypeEntry(55, 2, 10, 1),
        jewelry=TreasureTypeEntry(50, 6, 10, 1),
        magic_chance=15, magic_items=1,
    ),
    "J": TreasureType(
        name="J",
        copper=TreasureTypeEntry(100, 3, 8, 1),
    ),
    "K": TreasureType(
        name="K",
        silver=TreasureTypeEntry(100, 3, 6, 1),
    ),
    "L": TreasureType(
        name="L",
        gems=TreasureTypeEntry(50, 1, 4, 1),
    ),
    "M": TreasureType(
        name="M",
        gold=TreasureTypeEntry(100, 2, 4, 1),
    ),
    "N": TreasureType(
        name="N",
        platinum=TreasureTypeEntry(100, 1, 6, 1),
    ),
    "O": TreasureType(
        name="O",
        copper=TreasureTypeEntry(100, 1, 4, 10),
        silver=TreasureTypeEntry(100, 1, 3, 10),
    ),
    "P": TreasureType(
        name="P",
        silver=TreasureTypeEntry(100, 1, 6, 100),
        electrum=TreasureTypeEntry(100, 1, 2, 100),
    ),
    "Q": TreasureType(
        name="Q",
        gems=TreasureTypeEntry(50, 1, 4, 1),
    ),
    "R": TreasureType(
        name="R",
        gold=TreasureTypeEntry(100, 2, 6, 100),
        platinum=TreasureTypeEntry(100, 1, 4, 10),
        gems=TreasureTypeEntry(55, 2, 8, 1),
        jewelry=TreasureTypeEntry(45, 1, 12, 1),
    ),
    "S": TreasureType(
        name="S",
        magic_chance=40, magic_items=2,
    ),
    "T": TreasureType(
        name="T",
        magic_chance=50, magic_items=3,
    ),
    "U": TreasureType(
        name="U",
        gems=TreasureTypeEntry(90, 2, 8, 1),
        jewelry=TreasureTypeEntry(80, 1, 6, 1),
        magic_chance=70, magic_items=4,
    ),
    "V": TreasureType(
        name="V",
        magic_chance=85, magic_items=5,
    ),
    "W": TreasureType(
        name="W",
        gold=TreasureTypeEntry(60, 5, 6, 100),
        platinum=TreasureTypeEntry(15, 1, 8, 100),
        gems=TreasureTypeEntry(60, 1, 8, 1),
        jewelry=TreasureTypeEntry(50, 1, 8, 1),
        magic_chance=55, magic_items=3,
    ),
    "X": TreasureType(
        name="X",
        magic_chance=60, magic_items=4,
    ),
    "Y": TreasureType(
        name="Y",
        gold=TreasureTypeEntry(70, 2, 6, 1000),
    ),
    "Z": TreasureType(
        name="Z",
        copper=TreasureTypeEntry(20, 1, 3, 1000),
        silver=TreasureTypeEntry(25, 1, 4, 1000),
        electrum=TreasureTypeEntry(25, 1, 4, 1000),
        gold=TreasureTypeEntry(30, 1, 4, 1000),
        platinum=TreasureTypeEntry(30, 1, 6, 100),
        gems=TreasureTypeEntry(55, 1, 6, 1),
        jewelry=TreasureTypeEntry(50, 1, 6, 1),
        magic_chance=50, magic_items=3,
    ),
}


# ── Generator functions ──────────────────────────────────────────────────

@dataclass
class GemResult:
    """A generated gem."""

    name: str
    base_value: int
    category: str

    def as_dict(self) -> Dict:
        return {"name": self.name, "base_value": self.base_value, "category": self.category}


@dataclass
class JewelryResult:
    """A generated piece of jewelry."""

    value: int
    roll_details: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict:
        return {"value": self.value, "roll_details": self.roll_details}


@dataclass
class MagicItemResult:
    """A generated magic item."""

    category: str
    name: str

    def as_dict(self) -> Dict:
        return {"category": self.category, "name": self.name}


@dataclass
class TreasureResult:
    """Complete result of treasure generation."""

    treasure_type: str
    coins: Dict[str, int] = field(default_factory=dict)
    gems: List[GemResult] = field(default_factory=list)
    jewelry: List[JewelryResult] = field(default_factory=list)
    magic_items: List[MagicItemResult] = field(default_factory=list)
    total_gp_value: float = 0.0

    def as_dict(self) -> Dict:
        return {
            "treasure_type": self.treasure_type,
            "coins": self.coins,
            "gems": [g.as_dict() for g in self.gems],
            "jewelry": [j.as_dict() for j in self.jewelry],
            "magic_items": [m.as_dict() for m in self.magic_items],
            "total_gp_value": self.total_gp_value,
        }


def _generate_gem(roller: DiceRoller) -> GemResult:
    """Generate a single gem with type and value."""
    roll = roller.d100()
    base_value = 10
    category = "Ornamental"
    for threshold, value, cat in GEM_BASE_VALUES:
        if roll <= threshold:
            base_value = value
            category = cat
            break

    gem_list = GEM_TYPES.get(base_value, ["Unknown gem"])
    name = roller._rng.choice(gem_list)
    return GemResult(name=name, base_value=base_value, category=category)


def _generate_jewelry(roller: DiceRoller) -> JewelryResult:
    """Generate a single piece of jewelry with value."""
    roll = roller.d100()
    num_dice, sides, multiplier = 3, 6, 100  # default
    for threshold, (nd, sd, mult) in JEWELRY_VALUES:
        if roll <= threshold:
            num_dice, sides, multiplier = nd, sd, mult
            break

    dice_rolls = roller.roll(num_dice, sides)
    value = sum(dice_rolls) * multiplier
    return JewelryResult(
        value=value,
        roll_details={
            "d100_roll": roll,
            "dice": dice_rolls,
            "multiplier": multiplier,
        },
    )


def _generate_magic_item(roller: DiceRoller) -> MagicItemResult:
    """Generate a single magic item from the master tables."""
    # Determine category
    cat_roll = roller.d100()
    category = "misc"
    for threshold, cat in MAGIC_ITEM_CATEGORY:
        if cat_roll <= threshold:
            category = cat
            break

    # Roll on the specific table
    table = MAGIC_TABLES[category]
    item_roll = roller.d100()
    name = table[-1][1]
    for threshold, item_name in table:
        if item_roll <= threshold:
            name = item_name
            break

    return MagicItemResult(category=category, name=name)


def generate_treasure(
    treasure_type: str = "A",
    seed: Optional[int] = None,
) -> TreasureResult:
    """Generate treasure according to DMG treasure type tables.

    Args:
        treasure_type: Letter A-Z identifying the treasure type.
        seed: Optional RNG seed.

    Returns:
        A ``TreasureResult`` with coins, gems, jewelry, and magic items.
    """
    tt = TREASURE_TYPES.get(treasure_type.upper())
    if tt is None:
        raise ValueError(
            f"Unknown treasure type '{treasure_type}'. "
            f"Available: {list(TREASURE_TYPES.keys())}"
        )

    roller = DiceRoller(seed)
    result = TreasureResult(treasure_type=treasure_type.upper())

    # Coins
    coin_names = [
        ("copper", tt.copper),
        ("silver", tt.silver),
        ("electrum", tt.electrum),
        ("gold", tt.gold),
        ("platinum", tt.platinum),
    ]
    for coin_name, entry in coin_names:
        if entry:
            amount = entry.roll(roller)
            if amount > 0:
                result.coins[coin_name] = amount

    # Gems
    if tt.gems:
        num_gems = tt.gems.roll(roller)
        for _ in range(num_gems):
            result.gems.append(_generate_gem(roller))

    # Jewelry
    if tt.jewelry:
        num_jewelry = tt.jewelry.roll(roller)
        for _ in range(num_jewelry):
            result.jewelry.append(_generate_jewelry(roller))

    # Magic items
    if tt.magic_chance > 0 and roller.d100() <= tt.magic_chance:
        for _ in range(tt.magic_items):
            result.magic_items.append(_generate_magic_item(roller))

    # Calculate total GP value
    coin_gp_rates = {
        "copper": 0.01, "silver": 0.1, "electrum": 0.5,
        "gold": 1.0, "platinum": 5.0,
    }
    total = sum(
        amount * coin_gp_rates.get(coin, 0)
        for coin, amount in result.coins.items()
    )
    total += sum(g.base_value for g in result.gems)
    total += sum(j.value for j in result.jewelry)
    result.total_gp_value = round(total, 2)

    return result
