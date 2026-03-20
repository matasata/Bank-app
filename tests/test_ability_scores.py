"""Tests for ability score generation methods."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from engine.character.ability_scores import (
    generate_ability_scores, method_i, method_ii, method_iii,
    method_iv, method_v, method_vi, ABILITY_NAMES,
)


class TestMethodI:
    """Method I: 4d6 drop lowest, 6 times."""

    def test_returns_six_roll_details(self):
        result = method_i(seed=42)
        assert len(result.roll_details) == 6

    def test_scores_in_valid_range(self):
        for _ in range(100):
            result = method_i()
            for rd in result.roll_details:
                assert 3 <= rd.total <= 18

    def test_returns_roll_details_with_four_dice(self):
        result = method_i(seed=42)
        for rd in result.roll_details:
            assert len(rd.all_dice) == 4
            for die in rd.all_dice:
                assert 1 <= die <= 6

    def test_score_equals_sum_of_best_three(self):
        result = method_i(seed=42)
        for rd in result.roll_details:
            sorted_rolls = sorted(rd.all_dice, reverse=True)
            expected = sum(sorted_rolls[:3])
            assert rd.total == expected

    def test_available_scores_in_extra(self):
        result = method_i(seed=42)
        assert "available_scores" in result.extra
        assert len(result.extra["available_scores"]) == 6


class TestMethodII:
    """Method II: 3d6 twelve times, pick best 6."""

    def test_returns_twelve_roll_details(self):
        result = method_ii(seed=42)
        assert len(result.roll_details) == 12

    def test_best_six_available(self):
        result = method_ii(seed=42)
        assert "available_scores" in result.extra
        assert len(result.extra["available_scores"]) == 6

    def test_scores_are_best_six(self):
        result = method_ii(seed=42)
        all_totals = sorted([rd.total for rd in result.roll_details], reverse=True)
        best_six = sorted(result.extra["available_scores"], reverse=True)
        assert best_six == all_totals[:6]


class TestMethodIII:
    """Method III: 3d6 six times per ability, pick best from each."""

    def test_returns_six_scores(self):
        result = method_iii(seed=42)
        assert len(result.scores) == 6

    def test_scores_assigned_to_abilities(self):
        result = method_iii(seed=42)
        for ability in ABILITY_NAMES:
            assert ability in result.scores
            assert 3 <= result.scores[ability] <= 18

    def test_per_ability_rolls_in_extra(self):
        result = method_iii(seed=42)
        assert "per_ability_rolls" in result.extra
        for ability in ABILITY_NAMES:
            assert ability in result.extra["per_ability_rolls"]
            assert len(result.extra["per_ability_rolls"][ability]) == 6


class TestMethodIV:
    """Method IV: 3d6 twelve times per ability, pick best from each."""

    def test_returns_six_scores(self):
        result = method_iv(seed=42)
        assert len(result.scores) == 6

    def test_twelve_rolls_per_ability(self):
        result = method_iv(seed=42)
        for ability in ABILITY_NAMES:
            assert len(result.extra["per_ability_rolls"][ability]) == 12


class TestMethodV:
    """Method V: Point allocation."""

    def test_default_allocation(self):
        result = method_v()
        assert result.extra["total_points"] == 75
        assert sum(result.scores.values()) == 75

    def test_custom_allocation_valid(self):
        scores = {"str": 15, "int": 12, "wis": 13, "dex": 12, "con": 14, "cha": 9}
        assert sum(scores.values()) == 75
        result = method_v(allocation=scores)
        assert result.scores == scores

    def test_invalid_total_raises(self):
        scores = {"str": 18, "int": 18, "wis": 18, "dex": 18, "con": 18, "cha": 18}
        try:
            method_v(allocation=scores)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass


class TestMethodVI:
    """Method VI: Roll each ability in order, 6 times each, keep best."""

    def test_returns_six_assigned_scores(self):
        result = method_vi(seed=42)
        assert len(result.scores) == 6
        for ability in ABILITY_NAMES:
            assert ability in result.scores


class TestGenerateAbilityScores:
    """Test the convenience dispatcher."""

    def test_method_i(self):
        result = generate_ability_scores(method="I", seed=42)
        assert result.method == "I"

    def test_method_v_with_allocation(self):
        scores = {"str": 15, "int": 12, "wis": 13, "dex": 12, "con": 14, "cha": 9}
        result = generate_ability_scores(method="V", allocation=scores)
        assert result.scores == scores

    def test_invalid_method_raises(self):
        try:
            generate_ability_scores(method="VII")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass


class TestDiceStatistics:
    """Verify dice rolling produces expected statistical distributions."""

    def test_4d6_drop_lowest_average(self):
        """Average of 4d6 drop lowest should be ~12.24."""
        total = 0
        n = 5000
        for i in range(n):
            result = method_i(seed=i)
            total += sum(rd.total for rd in result.roll_details)
        avg_per_score = total / (n * 6)
        assert 11.5 < avg_per_score < 13.0

    def test_method_vi_average_above_straight_3d6(self):
        """Method VI picks best of 6 rolls, average should be > 10.5."""
        total = 0
        n = 5000
        for i in range(n):
            result = method_vi(seed=i)
            total += sum(result.scores.values())
        avg_per_score = total / (n * 6)
        assert avg_per_score > 10.5
