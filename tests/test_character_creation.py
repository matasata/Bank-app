"""Tests for character creation validation."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from engine.character.creation import validate_race_class, create_character


class TestRaceClassValidation:
    """Test race/class combination validation."""

    def test_human_can_be_fighter(self):
        high_scores = {"str": 18, "int": 18, "wis": 18, "dex": 18, "con": 18, "cha": 18}
        result = validate_race_class("Human", "Fighter", high_scores)
        assert result.valid is True

    def test_human_can_be_paladin(self):
        high_scores = {"str": 18, "int": 18, "wis": 18, "dex": 18, "con": 18, "cha": 18}
        result = validate_race_class("Human", "Paladin", high_scores)
        assert result.valid is True

    def test_dwarf_cannot_be_magic_user(self):
        scores = {"str": 18, "int": 18, "wis": 18, "dex": 18, "con": 18, "cha": 18}
        result = validate_race_class("Dwarf", "Magic-User", scores)
        assert result.valid is False

    def test_halfling_cannot_be_paladin(self):
        scores = {"str": 18, "int": 18, "wis": 18, "dex": 18, "con": 18, "cha": 18}
        result = validate_race_class("Halfling", "Paladin", scores)
        assert result.valid is False

    def test_paladin_requires_cha_17(self, paladin_ability_scores):
        low_cha = dict(paladin_ability_scores)
        low_cha["cha"] = 16
        result = validate_race_class("Human", "Paladin", low_cha)
        assert result.valid is False
        error_text = " ".join(result.errors).lower()
        assert "cha" in error_text or "charisma" in error_text

    def test_paladin_meets_requirements(self, paladin_ability_scores):
        result = validate_race_class("Human", "Paladin", paladin_ability_scores)
        assert result.valid is True


class TestCharacterCreation:
    """Test full character creation flow."""

    def test_create_fighter(self, sample_ability_scores):
        character = create_character(
            name="Conan",
            race_name="Human",
            class_name="Fighter",
            alignment="Neutral",
            abilities=sample_ability_scores,
            seed=42,
        )
        assert character.name == "Conan"
        assert character.race == "Human"
        assert character.class_name == "Fighter"
        assert character.level == 1
        assert character.hp >= 1
        assert character.thac0 > 0
        assert character.saving_throws is not None

    def test_create_character_as_dict(self, sample_ability_scores):
        character = create_character(
            name="Test",
            race_name="Human",
            class_name="Fighter",
            alignment="Neutral",
            abilities=sample_ability_scores,
            seed=42,
        )
        d = character.as_dict()
        assert d["name"] == "Test"
        assert "hp" in d
        assert "thac0" in d
        assert "saving_throws" in d
        assert "gold" in d

    def test_invalid_combination_raises(self):
        scores = {"str": 8, "int": 8, "wis": 8, "dex": 8, "con": 8, "cha": 8}
        try:
            create_character(
                name="Bad",
                race_name="Dwarf",
                class_name="Magic-User",
                alignment="Neutral",
                abilities=scores,
            )
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_starting_gold_generated(self, sample_ability_scores):
        character = create_character(
            name="Goldie",
            race_name="Human",
            class_name="Fighter",
            alignment="Neutral",
            abilities=sample_ability_scores,
            seed=42,
        )
        assert character.gold > 0
        assert character.gold_roll_details is not None
