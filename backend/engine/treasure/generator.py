"""DMG treasure generation system - Treasure Types A through Z."""
import random
from typing import Any, Optional


# Treasure Type definitions per DMG
# Format: (percentage_chance, num_dice, die_sides, multiplier)
TREASURE_TYPES: dict[str, dict[str, Any]] = {
    "A": {
        "copper": (25, 1000, 6000),
        "silver": (30, 200, 2000),
        "electrum": (35, 300, 1800),
        "gold": (40, 1000, 6000),
        "platinum": (25, 100, 400),
        "gems": (60, 4, 40),
        "jewelry": (50, 3, 30),
        "magic_any": (30, 3, None),
    },
    "B": {
        "copper": (50, 1000, 6000),
        "silver": (25, 200, 2000),
        "electrum": (25, 100, 1000),
        "gold": (25, 100, 600),
        "gems": (25, 1, 6),
        "jewelry": (25, 1, 6),
        "magic_weapon_armor": (10, 1, None),
    },
    "C": {
        "copper": (20, 1000, 6000),
        "silver": (30, 200, 2000),
        "electrum": (10, 100, 400),
        "gems": (25, 1, 4),
        "jewelry": (25, 1, 4),
        "magic_any": (10, 2, None),
    },
    "D": {
        "copper": (10, 1000, 6000),
        "silver": (15, 200, 2000),
        "electrum": (15, 100, 600),
        "gold": (50, 100, 600),
        "gems": (30, 1, 8),
        "jewelry": (30, 1, 8),
        "magic_any_plus_potion": (15, 2, None),
    },
    "E": {
        "copper": (5, 1000, 6000),
        "silver": (25, 200, 2000),
        "electrum": (25, 300, 1800),
        "gold": (25, 200, 1200),
        "gems": (15, 1, 10),
        "jewelry": (10, 1, 10),
        "magic_any_plus_scroll": (25, 3, None),
    },
    "F": {
        "silver": (10, 300, 1800),
        "electrum": (15, 200, 1200),
        "gold": (40, 500, 3000),
        "platinum": (35, 100, 600),
        "gems": (20, 2, 12),
        "jewelry": (10, 1, 12),
        "magic_non_weapon": (30, 3, None),
    },
    "G": {
        "gold": (50, 1000, 10000),
        "platinum": (50, 200, 2000),
        "gems": (30, 3, 18),
        "jewelry": (25, 1, 10),
        "magic_any": (35, 4, None),
    },
    "H": {
        "copper": (25, 3000, 18000),
        "silver": (40, 2000, 12000),
        "electrum": (40, 2000, 10000),
        "gold": (55, 2000, 12000),
        "platinum": (25, 200, 2000),
        "gems": (50, 1, 100),
        "jewelry": (50, 10, 40),
        "magic_any": (15, 4, None),
    },
    "I": {
        "platinum": (30, 100, 800),
        "gems": (55, 2, 12),
        "jewelry": (50, 2, 12),
        "magic_any": (15, 1, None),
    },
}

# Gem value table from DMG
GEM_VALUES = [
    (10, "ornamental", ["azurite", "banded agate", "blue quartz", "eye agate",
                         "hematite", "lapis lazuli", "malachite", "moss agate",
                         "obsidian", "rhodochrosite", "tiger eye", "turquoise"]),
    (50, "semi-precious", ["bloodstone", "carnelian", "chalcedony", "chrysoprase",
                            "citrine", "jasper", "moonstone", "onyx", "rock crystal",
                            "sardonyx", "smoky quartz", "star rose quartz", "zircon"]),
    (100, "fancy", ["amber", "alexandrite", "amethyst", "chrysoberyl", "coral",
                     "garnet", "jade", "jet", "pearl", "spinel", "tourmaline"]),
    (500, "precious", ["aquamarine", "garnet", "black pearl", "peridot",
                        "topaz"]),
    (1000, "gem", ["black opal", "emerald", "fire opal", "opal", "oriental amethyst",
                    "oriental topaz", "sapphire", "star ruby", "star sapphire"]),
    (5000, "jewel", ["black sapphire", "diamond", "jacinth", "oriental emerald", "ruby"]),
]

# Magic item tables
POTION_TYPES = [
    "Animal Control", "Clairaudience", "Clairvoyance", "Climbing",
    "Diminution", "Dragon Control", "ESP", "Extra-Healing",
    "Fire Resistance", "Flying", "Gaseous Form", "Giant Control",
    "Giant Strength", "Growth", "Healing", "Heroism", "Human Control",
    "Invisibility", "Invulnerability", "Levitation", "Longevity",
    "Oil of Etherealness", "Oil of Slipperiness", "Philter of Love",
    "Philter of Persuasiveness", "Plant Control", "Polymorph Self",
    "Speed", "Super-Heroism", "Sweet Water", "Treasure Finding",
    "Undead Control", "Water Breathing",
]

SCROLL_TYPES = [
    "Protection from Demons", "Protection from Devils",
    "Protection from Elementals", "Protection from Lycanthropes",
    "Protection from Magic", "Protection from Petrification",
    "Protection from Undead", "1 spell", "2 spells", "3 spells",
    "5 spells", "7 spells",
]

RING_TYPES = [
    "Contrariness", "Delusion", "Djinni Summoning", "Elemental Command",
    "Feather Falling", "Fire Resistance", "Free Action", "Human Influence",
    "Invisibility", "Mammal Control", "Multiple Wishes", "Protection +1",
    "Protection +2", "Protection +3", "Regeneration", "Shooting Stars",
    "Spell Storing", "Spell Turning", "Swimming", "Telekinesis",
    "Three Wishes", "Warmth", "Water Walking", "Weakness",
    "Wizardry", "X-Ray Vision",
]


class TreasureGenerator:
    """Generates treasure according to DMG treasure type tables."""

    def generate_by_type(self, treasure_type: str) -> dict[str, Any]:
        """Generate treasure for a given treasure type (A-Z)."""
        type_def = TREASURE_TYPES.get(treasure_type.upper())
        if type_def is None:
            return {"error": f"Unknown treasure type: {treasure_type}"}

        result: dict[str, Any] = {"treasure_type": treasure_type, "coins": {}}

        for key, value in type_def.items():
            if key in ("copper", "silver", "electrum", "gold", "platinum"):
                chance, min_val, max_val = value
                if random.randint(1, 100) <= chance:
                    amount = random.randint(min_val, max_val)
                    result["coins"][key] = amount
            elif key == "gems":
                chance, min_count, max_count = value
                if random.randint(1, 100) <= chance:
                    count = random.randint(min_count, max_count)
                    result["gems"] = [self.generate_gem() for _ in range(count)]
            elif key == "jewelry":
                chance, min_count, max_count = value
                if random.randint(1, 100) <= chance:
                    count = random.randint(min_count, max_count)
                    result["jewelry"] = [self.generate_jewelry() for _ in range(count)]
            elif key.startswith("magic"):
                chance = value[0]
                count = value[1]
                if random.randint(1, 100) <= chance:
                    result["magic_items"] = [self.generate_magic_item() for _ in range(count)]

        return result

    def generate_gem(self) -> dict[str, Any]:
        """Generate a random gem with value."""
        roll = random.randint(1, 100)
        if roll <= 25:
            idx = 0
        elif roll <= 50:
            idx = 1
        elif roll <= 70:
            idx = 2
        elif roll <= 90:
            idx = 3
        elif roll <= 99:
            idx = 4
        else:
            idx = 5

        base_value, quality, stones = GEM_VALUES[idx]
        stone = random.choice(stones)

        # Value variation
        variation = random.choice([0.5, 0.75, 1.0, 1.0, 1.0, 1.25, 1.5, 2.0])
        final_value = int(base_value * variation)

        return {"stone": stone, "quality": quality, "value_gp": final_value}

    def generate_jewelry(self) -> dict[str, Any]:
        """Generate a random piece of jewelry."""
        roll = random.randint(1, 100)
        if roll <= 10:
            value = random.randint(1, 10) * 100
        elif roll <= 25:
            value = random.randint(1, 6) * 100 + 100
        elif roll <= 50:
            value = random.randint(1, 6) * 200 + 500
        elif roll <= 70:
            value = random.randint(1, 6) * 500 + 1000
        elif roll <= 90:
            value = random.randint(1, 4) * 1000 + 2000
        else:
            value = random.randint(1, 6) * 2000 + 5000

        types = ["ring", "necklace", "bracelet", "brooch", "crown", "tiara",
                 "pendant", "anklet", "earring", "arm band", "diadem", "choker"]
        materials = ["gold", "silver", "platinum", "electrum",
                     "gold and gem", "silver and pearl", "mithril"]

        return {
            "type": random.choice(types),
            "material": random.choice(materials),
            "value_gp": value,
        }

    def generate_magic_item(self) -> dict[str, Any]:
        """Generate a random magic item from DMG tables."""
        roll = random.randint(1, 100)

        if roll <= 20:
            return {"category": "potion", "name": f"Potion of {random.choice(POTION_TYPES)}"}
        elif roll <= 35:
            return {"category": "scroll", "name": f"Scroll: {random.choice(SCROLL_TYPES)}"}
        elif roll <= 40:
            return {"category": "ring", "name": f"Ring of {random.choice(RING_TYPES)}"}
        elif roll <= 45:
            return self._generate_magic_weapon()
        elif roll <= 50:
            return self._generate_magic_armor()
        elif roll <= 55:
            wands = ["Wand of Enemy Detection", "Wand of Fear", "Wand of Fire",
                     "Wand of Frost", "Wand of Illusion", "Wand of Lightning",
                     "Wand of Magic Detection", "Wand of Magic Missiles",
                     "Wand of Negation", "Wand of Paralyzation", "Wand of Polymorph",
                     "Wand of Secret Door Detection", "Wand of Wonder",
                     "Staff of Command", "Staff of Curing", "Staff of Power",
                     "Staff of the Magi", "Staff of the Serpent",
                     "Staff of Striking", "Staff of Withering",
                     "Rod of Cancellation", "Rod of Lordly Might", "Rod of Rulership"]
            return {"category": "wand_staff_rod", "name": random.choice(wands)}
        else:
            misc = ["Amulet of Proof Against Detection and Location",
                    "Bag of Holding", "Boots of Elvenkind", "Boots of Levitation",
                    "Boots of Speed", "Boots of Striding and Springing",
                    "Bracers of Defense AC 6", "Bracers of Defense AC 4",
                    "Broom of Flying", "Carpet of Flying", "Cloak of Displacement",
                    "Cloak of Elvenkind", "Cloak of Protection +1",
                    "Crystal Ball", "Cube of Force", "Decanter of Endless Water",
                    "Deck of Many Things", "Efreeti Bottle",
                    "Eyes of the Eagle", "Figurine of Wondrous Power",
                    "Gauntlets of Ogre Power", "Girdle of Giant Strength",
                    "Helm of Brilliance", "Helm of Telepathy", "Horn of Valhalla",
                    "Horseshoes of Speed", "Ioun Stones", "Javelin of Lightning",
                    "Medallion of ESP", "Mirror of Life Trapping",
                    "Necklace of Missiles", "Pearl of Power",
                    "Periapt of Health", "Portable Hole", "Robe of the Archmagi",
                    "Rope of Climbing", "Scarab of Protection",
                    "Sphere of Annihilation", "Stone of Controlling Earth Elementals"]
            return {"category": "miscellaneous", "name": random.choice(misc)}

    def _generate_magic_weapon(self) -> dict[str, Any]:
        """Generate a random magic weapon."""
        weapon_types = ["long sword", "short sword", "broad sword", "two-handed sword",
                        "battle axe", "mace", "war hammer", "spear", "dagger",
                        "hand axe", "morning star", "flail"]
        bonuses = [(1, 40), (2, 25), (3, 15), (4, 10), (5, 5)]
        weapon = random.choice(weapon_types)
        bonus = self._weighted_choice(bonuses)

        # 10% chance of special ability
        special = None
        if random.randint(1, 100) <= 10:
            specials = ["Flame Tongue", "Frost Brand", "Dragon Slayer",
                        "Giant Slayer", "Vorpal", "Sharpness", "Wounding",
                        "Life Stealing", "Dancing", "Defending"]
            special = random.choice(specials)

        result = {
            "category": "weapon",
            "name": f"{weapon.title()} +{bonus}",
            "type": weapon,
            "bonus": bonus,
        }
        if special:
            result["name"] = f"{weapon.title()} +{bonus}, {special}"
            result["special"] = special
        return result

    def _generate_magic_armor(self) -> dict[str, Any]:
        """Generate random magic armor."""
        armor_types = ["chain mail", "plate mail", "leather armor", "ring mail",
                       "scale mail", "banded mail", "splint mail", "shield"]
        bonuses = [(1, 40), (2, 30), (3, 20), (4, 8), (5, 2)]
        armor = random.choice(armor_types)
        bonus = self._weighted_choice(bonuses)

        return {
            "category": "armor",
            "name": f"{armor.title()} +{bonus}",
            "type": armor,
            "bonus": bonus,
        }

    def _weighted_choice(self, choices: list[tuple]) -> Any:
        total = sum(w for _, w in choices)
        r = random.randint(1, total)
        cumulative = 0
        for item, weight in choices:
            cumulative += weight
            if r <= cumulative:
                return item
        return choices[-1][0]

    def generate_individual_treasure(self, level: int = 1) -> dict[str, Any]:
        """Generate individual treasure for a single creature."""
        return {
            "copper": random.randint(0, level * 10),
            "silver": random.randint(0, level * 5),
            "gold": random.randint(0, level * 3),
        }
