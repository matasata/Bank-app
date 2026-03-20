"""Tests for character creation validation."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from engine.character.creation import CharacterCreator


class TestRaceClassValidation:
    """Test race/class combination validation."""

    def test_human_can_be_any_class(self):
        creator = CharacterCreator()
        classes = ["fighter", "paladin", "ranger", "magic_user", "illusionist",
                   "cleric", "druid", "thief", "assassin", "monk"]
        high_scores = {"str": 18, "int": 18, "wis": 18, "dex": 18, "con": 18, "cha": 18}
        for cls in classes:
            result = creator.validate_race_class("human", cls, high_scores)
            assert result["valid"] is True, f"Human should be able to be {cls}"

    def test_dwarf_cannot_be_magic_user(self):
        creator = CharacterCreator()
        scores = {"str": 18, "int": 18, "wis": 18, "dex": 18, "con": 18, "cha": 18}
        result = creator.validate_race_class("dwarf", "magic_user", scores)
        assert result["valid"] is False

    def test_halfling_cannot_be_paladin(self):
        creator = CharacterCreator()
        scores = {"str": 18, "int": 18, "wis": 18, "dex": 18, "con": 18, "cha": 18}
        result = creator.validate_race_class("halfling", "paladin", scores)
        assert result["valid"] is False

    def test_paladin_requires_cha_17(self):
        creator = CharacterCreator()
        low_cha = {"str": 12, "int": 9, "wis": 13, "dex": 6, "con": 9, "cha": 16}
        result = creator.validate_race_class("human", "paladin", low_cha)
        assert result["valid"] is False
        assert "cha" in str(result.get("reason", "")).lower() or "charisma" in str(result.get("reason", "")).lower()

    def test_paladin_meets_requirements(self, paladin_ability_scores):
        creator = CharacterCreator()
        result = creator.validate_race_class("human", "paladin", paladin_ability_scores)
        assert result["valid"] is True

    def test_racial_ability_adjustments(self):
        creator = CharacterCreator()
        scores = {"str": 10, "int": 10, "wis": 10, "dex": 10, "con": 10, "cha": 10}
        adjusted = creator.apply_racial_adjustments("dwarf", scores.copy())
        assert adjusted["con"] == 11  # Dwarf gets +1 CON
        assert adjusted["cha"] == 9   # Dwarf gets -1 CHA

    def test_elf_adjustments(self):
        creator = CharacterCreator()
        scores = {"str": 10, "int": 10, "wis": 10, "dex": 10, "con": 10, "cha": 10}
        adjusted = creator.apply_racial_adjustments("elf", scores.copy())
        assert adjusted["dex"] == 11  # Elf gets +1 DEX
        assert adjusted["con"] == 9   # Elf gets -1 CON


class TestStartingGold:
    """Test starting gold generation by class."""

    def test_fighter_starting_gold_range(self):
        creator = CharacterCreator()
        for _ in range(100):
            gold = creator.roll_starting_gold("fighter")
            # Fighter: 5d4 x 10 = 50-200
            assert 50 <= gold <= 200

    def test_magic_user_starting_gold_range(self):
        creator = CharacterCreator()
        for _ in range(100):
            gold = creator.roll_starting_gold("magic_user")
            # Magic-User: 2d4 x 10 = 20-80
            assert 20 <= gold <= 80

    def test_thief_starting_gold_range(self):
        creator = CharacterCreator()
        for _ in range(100):
            gold = creator.roll_starting_gold("thief")
            # Thief: 2d6 x 10 = 20-120
            assert 20 <= gold <= 120


class TestCharacterCreation:
    """Test full character creation flow."""

    def test_create_fighter(self, sample_ability_scores):
        creator = CharacterCreator()
        character = creator.create_character(
            name="Conan",
            race="human",
            class_name="fighter",
            alignment="neutral",
            ability_scores=sample_ability_scores
        )
        assert character["name"] == "Conan"
        assert character["race"] == "human"
        assert character["class_name"] == "fighter"
        assert character["level"] == 1
        assert 1 <= character["hp"] <= 10  # d10 hit die
        assert "saves" in character
        assert "thac0" in character or "attack_matrix" in character

    def test_create_character_applies_racial_mods(self):
        creator = CharacterCreator()
        scores = {"str": 10, "int": 10, "wis": 10, "dex": 12, "con": 14, "cha": 10}
        character = creator.create_character(
            name="Gimli",
            race="dwarf",
            class_name="fighter",
            alignment="lawful_good",
            ability_scores=scores
        )
        assert character["con"] == 15  # +1 from dwarf
        assert character["cha"] == 9   # -1 from dwarf
