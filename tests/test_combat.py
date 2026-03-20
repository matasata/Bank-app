"""Tests for combat resolution system."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from engine.combat.attack import AttackResolver


class TestAttackResolution:
    """Test attack rolls against combat matrices."""

    def test_fighter_level1_vs_ac10(self):
        resolver = AttackResolver()
        # Level 1 fighter needs 10 to hit AC 10
        result = resolver.resolve_attack(
            attacker_class="fighter",
            attacker_level=1,
            target_ac=10,
            roll_override=10
        )
        assert result["hit"] is True

    def test_fighter_level1_vs_ac10_miss(self):
        resolver = AttackResolver()
        result = resolver.resolve_attack(
            attacker_class="fighter",
            attacker_level=1,
            target_ac=10,
            roll_override=9
        )
        assert result["hit"] is False

    def test_natural_20_always_hits(self):
        resolver = AttackResolver()
        result = resolver.resolve_attack(
            attacker_class="fighter",
            attacker_level=1,
            target_ac=-5,
            roll_override=20
        )
        assert result["hit"] is True

    def test_natural_1_always_misses(self):
        resolver = AttackResolver()
        result = resolver.resolve_attack(
            attacker_class="fighter",
            attacker_level=20,
            target_ac=10,
            roll_override=1
        )
        assert result["hit"] is False

    def test_higher_level_fighter_hits_easier(self):
        resolver = AttackResolver()
        # High level fighter should need lower roll
        low_level = resolver.get_number_needed(
            attacker_class="fighter", attacker_level=1, target_ac=5
        )
        high_level = resolver.get_number_needed(
            attacker_class="fighter", attacker_level=10, target_ac=5
        )
        assert high_level < low_level

    def test_magic_bonus_applies(self):
        resolver = AttackResolver()
        result_no_bonus = resolver.resolve_attack(
            attacker_class="fighter",
            attacker_level=1,
            target_ac=5,
            roll_override=14,
            magic_bonus=0
        )
        result_with_bonus = resolver.resolve_attack(
            attacker_class="fighter",
            attacker_level=1,
            target_ac=5,
            roll_override=14,
            magic_bonus=3
        )
        # With +3, a roll that might miss should now hit
        assert result_with_bonus["effective_roll"] == 17

    def test_attack_returns_details(self):
        resolver = AttackResolver()
        result = resolver.resolve_attack(
            attacker_class="fighter",
            attacker_level=5,
            target_ac=3,
            roll_override=15
        )
        assert "natural_roll" in result
        assert "effective_roll" in result
        assert "needed" in result
        assert "hit" in result


class TestInitiative:
    """Test initiative system."""

    def test_side_initiative_returns_valid(self):
        from engine.combat.initiative import InitiativeManager
        mgr = InitiativeManager()
        result = mgr.roll_side_initiative()
        assert "party" in result
        assert "monsters" in result
        assert 1 <= result["party"] <= 6
        assert 1 <= result["monsters"] <= 6

    def test_individual_initiative(self):
        from engine.combat.initiative import InitiativeManager
        mgr = InitiativeManager()
        combatants = [
            {"name": "Fighter", "dex_modifier": 0, "weapon_speed": 5},
            {"name": "Thief", "dex_modifier": 1, "weapon_speed": 2},
        ]
        result = mgr.roll_individual_initiative(combatants)
        assert len(result) == 2
        for entry in result:
            assert "name" in entry
            assert "roll" in entry
            assert "modified" in entry
