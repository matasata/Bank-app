"""Tests for combat resolution system."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from engine.combat.attack import resolve_attack, AttackResult
from engine.combat.initiative import roll_side_initiative, roll_individual_initiative


class TestAttackResolution:
    """Test attack rolls against combat matrices."""

    def test_attack_returns_attack_result(self):
        result = resolve_attack(
            attacker_name="Fighter",
            attacker_class="Fighter",
            attacker_level=1,
            target_name="Goblin",
            target_ac=6,
            seed=42,
        )
        assert isinstance(result, AttackResult)

    def test_natural_20_always_hits(self):
        # Use seed that produces nat 20 -- or test via the result properties
        # We'll test many seeds and verify nat 20 logic
        for seed in range(1000):
            result = resolve_attack(
                attacker_name="Fighter",
                attacker_class="Fighter",
                attacker_level=1,
                target_name="Dragon",
                target_ac=-5,
                seed=seed,
            )
            if result.natural_20:
                assert result.hit is True

    def test_natural_1_always_misses(self):
        for seed in range(1000):
            result = resolve_attack(
                attacker_name="Fighter",
                attacker_class="Fighter",
                attacker_level=20,
                target_name="Goblin",
                target_ac=10,
                seed=seed,
            )
            if result.natural_1:
                assert result.hit is False

    def test_hit_deals_damage(self):
        for seed in range(200):
            result = resolve_attack(
                attacker_name="Fighter",
                attacker_class="Fighter",
                attacker_level=10,
                target_name="Goblin",
                target_ac=10,
                seed=seed,
            )
            if result.hit and not result.natural_1:
                assert result.total_damage >= 0
            if not result.hit:
                assert result.total_damage == 0

    def test_magic_weapon_bonus_applies(self):
        result = resolve_attack(
            attacker_name="Fighter",
            attacker_class="Fighter",
            attacker_level=1,
            target_name="Goblin",
            target_ac=5,
            magic_weapon_bonus=3,
            seed=42,
        )
        assert result.magic_weapon_mod == 3

    def test_result_as_dict(self):
        result = resolve_attack(
            attacker_name="Fighter",
            attacker_class="Fighter",
            attacker_level=5,
            target_name="Orc",
            target_ac=6,
            seed=42,
        )
        d = result.as_dict()
        assert "d20_roll" in d
        assert "total_attack_roll" in d
        assert "to_hit_needed" in d
        assert "hit" in d
        assert "total_damage" in d

    def test_monster_attack(self):
        result = resolve_attack(
            attacker_name="Ogre",
            attacker_class="monster",
            attacker_level=4,
            target_name="Fighter",
            target_ac=3,
            is_monster=True,
            monster_hd=4,
            seed=42,
        )
        assert isinstance(result, AttackResult)


class TestInitiative:
    """Test initiative system."""

    def test_side_initiative_returns_result(self):
        party = [{"id": "p1", "name": "Fighter"}, {"id": "p2", "name": "Cleric"}]
        monsters = [{"id": "m1", "name": "Goblin"}]
        result = roll_side_initiative(party, monsters, seed=42)
        assert result.method == "side"
        assert len(result.entries) == 3

    def test_side_initiative_rolls_valid(self):
        party = [{"id": "p1", "name": "Fighter"}]
        monsters = [{"id": "m1", "name": "Goblin"}]
        result = roll_side_initiative(party, monsters, seed=42)
        for entry in result.entries:
            assert 1 <= entry.roll <= 6

    def test_side_initiative_order(self):
        party = [{"id": "p1", "name": "Fighter"}]
        monsters = [{"id": "m1", "name": "Goblin"}]
        result = roll_side_initiative(party, monsters, seed=42)
        assert len(result.order) == 2

    def test_individual_initiative(self):
        combatants = [
            {"id": "p1", "name": "Fighter", "side": "party", "dex": 12, "modifier": 5},
            {"id": "p2", "name": "Thief", "side": "party", "dex": 16, "modifier": 2},
            {"id": "m1", "name": "Goblin", "side": "monsters", "dex": 10, "modifier": 4},
        ]
        result = roll_individual_initiative(combatants, seed=42)
        assert result.method == "individual"
        assert len(result.entries) == 3
        # Should be sorted by total ascending
        totals = [e.total for e in result.entries]
        assert totals == sorted(totals)

    def test_individual_initiative_as_dict(self):
        combatants = [
            {"id": "p1", "name": "Fighter", "side": "party", "dex": 10},
        ]
        result = roll_individual_initiative(combatants, seed=42)
        d = result.as_dict()
        assert "method" in d
        assert "entries" in d
        assert "order" in d
