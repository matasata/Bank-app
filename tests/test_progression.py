"""Tests for character progression and leveling."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from engine.character.progression import (
    check_level_up, level_up, xp_for_next_level, award_xp,
)


class TestXPTracking:
    def test_award_xp_basic(self):
        new_total, effective = award_xp(0, 500)
        assert new_total == 500
        assert effective == 500

    def test_award_xp_with_bonus(self):
        new_total, effective = award_xp(0, 1000, prime_req_bonus=0.1)
        assert effective == 1100
        assert new_total == 1100

    def test_award_xp_accumulates(self):
        total, _ = award_xp(500, 300)
        assert total == 800

    def test_xp_for_next_level(self):
        xp = xp_for_next_level("Fighter", 1)
        assert xp > 0  # Fighter needs 2000 for level 2

    def test_check_level_up_not_enough(self):
        assert check_level_up("Fighter", 1, 100) is False

    def test_check_level_up_enough(self):
        # Fighter needs 2000 XP for level 2
        assert check_level_up("Fighter", 1, 2000) is True


class TestLevelUp:
    def test_level_up_basic(self):
        result = level_up(
            class_name="Fighter",
            current_level=1,
            current_hp=8,
            con=14,
            seed=42,
        )
        assert result.new_level == 2
        assert result.old_level == 1
        assert result.hp_gained >= 1
        assert result.new_total_hp > 8

    def test_level_up_thac0_improves(self):
        result = level_up("Fighter", 1, 8, con=10, seed=42)
        # Level 2 fighter should have same or better THAC0
        assert result.new_thac0 <= 20

    def test_level_up_saves_present(self):
        result = level_up("Fighter", 1, 8, con=10, seed=42)
        assert "ppdm" in result.new_saving_throws
        assert "bw" in result.new_saving_throws

    def test_level_up_as_dict(self):
        result = level_up("Fighter", 1, 8, con=10, seed=42)
        d = result.as_dict()
        assert "new_level" in d
        assert "hp_gained" in d
        assert "new_thac0" in d

    def test_high_level_fighter_extra_attacks(self):
        result = level_up("Fighter", 6, 50, con=14, seed=42)
        assert result.new_level == 7
        assert any("attacks" in a.lower() for a in result.new_abilities)

    def test_post_name_level_fixed_hp(self):
        result = level_up("Fighter", 9, 70, con=14, seed=42)
        assert result.new_level == 10
        assert result.hp_gained == 3  # Fixed 3 HP post name level for fighters
