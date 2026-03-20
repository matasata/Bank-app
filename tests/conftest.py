"""Test configuration and fixtures for AD&D game system tests."""
import sys
import os
import pytest

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


@pytest.fixture
def sample_ability_scores():
    """Standard ability scores for testing."""
    return {
        "str": 16, "int": 12, "wis": 14,
        "dex": 13, "con": 15, "cha": 10
    }


@pytest.fixture
def paladin_ability_scores():
    """Minimum ability scores for a Paladin."""
    return {
        "str": 12, "int": 9, "wis": 13,
        "dex": 6, "con": 9, "cha": 17
    }


@pytest.fixture
def low_ability_scores():
    """Low ability scores that restrict class options."""
    return {
        "str": 8, "int": 8, "wis": 8,
        "dex": 8, "con": 8, "cha": 8
    }
