"""Tests for ability score generation methods."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from engine.character.ability_scores import AbilityScoreGenerator


class TestMethodI:
    """Method I: 4d6 drop lowest, 6 times."""

    def test_returns_six_scores(self):
        gen = AbilityScoreGenerator()
        result = gen.method_i()
        assert len(result["scores"]) == 6

    def test_scores_in_valid_range(self):
        gen = AbilityScoreGenerator()
        for _ in range(100):
            result = gen.method_i()
            for score in result["scores"]:
                assert 3 <= score <= 18

    def test_returns_roll_details(self):
        gen = AbilityScoreGenerator()
        result = gen.method_i()
        assert "rolls" in result
        assert len(result["rolls"]) == 6
        for roll_set in result["rolls"]:
            assert len(roll_set) == 4
            for die in roll_set:
                assert 1 <= die <= 6

    def test_score_equals_sum_of_best_three(self):
        gen = AbilityScoreGenerator()
        result = gen.method_i()
        for i, roll_set in enumerate(result["rolls"]):
            sorted_rolls = sorted(roll_set, reverse=True)
            expected = sum(sorted_rolls[:3])
            assert result["scores"][i] == expected


class TestMethodII:
    """Method II: 3d6 twelve times, pick best 6."""

    def test_returns_six_scores(self):
        gen = AbilityScoreGenerator()
        result = gen.method_ii()
        assert len(result["scores"]) == 6

    def test_twelve_rolls_made(self):
        gen = AbilityScoreGenerator()
        result = gen.method_ii()
        assert len(result["all_rolls"]) == 12

    def test_scores_are_best_six(self):
        gen = AbilityScoreGenerator()
        result = gen.method_ii()
        all_totals = [sum(r) for r in result["all_rolls"]]
        all_totals_sorted = sorted(all_totals, reverse=True)
        scores_sorted = sorted(result["scores"], reverse=True)
        assert scores_sorted == all_totals_sorted[:6]


class TestMethodIII:
    """Method III: 3d6 six times per ability, pick best from each."""

    def test_returns_six_scores(self):
        gen = AbilityScoreGenerator()
        result = gen.method_iii()
        assert len(result["scores"]) == 6

    def test_six_rolls_per_ability(self):
        gen = AbilityScoreGenerator()
        result = gen.method_iii()
        assert len(result["rolls_per_ability"]) == 6
        for ability_rolls in result["rolls_per_ability"]:
            assert len(ability_rolls) == 6


class TestMethodIV:
    """Method IV: 3d6 twelve times per ability, pick best from each."""

    def test_returns_six_scores(self):
        gen = AbilityScoreGenerator()
        result = gen.method_iv()
        assert len(result["scores"]) == 6

    def test_twelve_rolls_per_ability(self):
        gen = AbilityScoreGenerator()
        result = gen.method_iv()
        assert len(result["rolls_per_ability"]) == 6
        for ability_rolls in result["rolls_per_ability"]:
            assert len(ability_rolls) == 12


class TestMethodV:
    """Method V: Point allocation."""

    def test_returns_allocation_info(self):
        gen = AbilityScoreGenerator()
        result = gen.method_v()
        assert "pool" in result
        assert result["pool"] == 75

    def test_allocate_valid(self):
        gen = AbilityScoreGenerator()
        scores = {"str": 15, "int": 12, "wis": 13, "dex": 12, "con": 14, "cha": 9}
        assert sum(scores.values()) == 75
        result = gen.validate_method_v_allocation(scores)
        assert result["valid"] is True

    def test_allocate_invalid_total(self):
        gen = AbilityScoreGenerator()
        scores = {"str": 18, "int": 18, "wis": 18, "dex": 18, "con": 18, "cha": 18}
        result = gen.validate_method_v_allocation(scores)
        assert result["valid"] is False


class TestMethodVI:
    """Method VI: Roll each ability in order, 6 times each, keep best."""

    def test_returns_six_ordered_scores(self):
        gen = AbilityScoreGenerator()
        result = gen.method_vi()
        assert len(result["scores"]) == 6
        abilities = ["str", "int", "wis", "dex", "con", "cha"]
        for ability in abilities:
            assert ability in result["assigned"]


class TestDiceStatistics:
    """Verify dice rolling produces expected statistical distributions."""

    def test_4d6_drop_lowest_average(self):
        """Average of 4d6 drop lowest should be ~12.24."""
        gen = AbilityScoreGenerator()
        total = 0
        n = 10000
        for _ in range(n):
            result = gen.method_i()
            total += sum(result["scores"])
        avg_per_score = total / (n * 6)
        assert 11.5 < avg_per_score < 13.0

    def test_3d6_average(self):
        """Average of 3d6 should be ~10.5."""
        gen = AbilityScoreGenerator()
        total = 0
        n = 10000
        for _ in range(n):
            result = gen.method_vi()
            total += sum(result["scores"])
        # Method VI picks best of 6, so average should be higher than 10.5
        avg_per_score = total / (n * 6)
        assert avg_per_score > 10.5
