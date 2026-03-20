"""Tests for FastAPI API endpoints."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


class TestHealthCheck:
    def test_health(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestCharacterAPI:
    def test_roll_abilities_method_i(self):
        response = client.post("/api/characters/roll-abilities", json={"method": "I", "seed": 42})
        assert response.status_code == 200
        data = response.json()
        assert data["method"] == "I"
        assert "roll_details" in data

    def test_roll_abilities_method_v(self):
        allocation = {"str": 15, "int": 12, "wis": 13, "dex": 12, "con": 14, "cha": 9}
        response = client.post("/api/characters/roll-abilities", json={
            "method": "V",
            "allocation": allocation,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["scores"] == allocation

    def test_roll_abilities_invalid_method(self):
        response = client.post("/api/characters/roll-abilities", json={"method": "X"})
        assert response.status_code == 400

    def test_get_races(self):
        response = client.get("/api/characters/races")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        race_names = [r["name"] for r in data]
        assert "Human" in race_names
        assert "Dwarf" in race_names

    def test_get_classes(self):
        response = client.get("/api/characters/classes")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        class_names = [c["name"] for c in data]
        assert "Fighter" in class_names

    def test_validate_valid_combination(self):
        response = client.post("/api/characters/validate", json={
            "race": "Human",
            "class_name": "Fighter",
            "abilities": {"str": 16, "int": 12, "wis": 14, "dex": 13, "con": 15, "cha": 10},
        })
        assert response.status_code == 200
        assert response.json()["valid"] is True

    def test_validate_invalid_combination(self):
        response = client.post("/api/characters/validate", json={
            "race": "Dwarf",
            "class_name": "Magic-User",
            "abilities": {"str": 10, "int": 10, "wis": 10, "dex": 10, "con": 10, "cha": 10},
        })
        assert response.status_code == 200
        assert response.json()["valid"] is False

    def test_create_character(self):
        response = client.post("/api/characters/create", json={
            "name": "Conan",
            "race": "Human",
            "class_name": "Fighter",
            "abilities": {"str": 16, "int": 12, "wis": 14, "dex": 13, "con": 15, "cha": 10},
            "alignment": "Neutral",
            "seed": 42,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Conan"
        assert data["race"] == "Human"
        assert "id" in data
        assert data["hp"] >= 1

    def test_get_character(self):
        # First create one
        create_resp = client.post("/api/characters/create", json={
            "name": "Elric",
            "race": "Human",
            "class_name": "Fighter",
            "abilities": {"str": 16, "int": 12, "wis": 14, "dex": 13, "con": 15, "cha": 10},
            "alignment": "Neutral",
        })
        char_id = create_resp.json()["id"]
        response = client.get(f"/api/characters/{char_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Elric"

    def test_get_nonexistent_character(self):
        response = client.get("/api/characters/99999")
        assert response.status_code == 404


class TestDungeonAPI:
    def test_generate_dungeon(self):
        response = client.post("/api/dungeon/generate", json={
            "level": 1,
            "num_rooms": 5,
            "seed": 42,
        })
        assert response.status_code == 200
        data = response.json()
        assert "dungeon" in data
        assert "rooms" in data["dungeon"]

    def test_generate_dungeon_default(self):
        response = client.post("/api/dungeon/generate", json={})
        assert response.status_code == 200


class TestGameAPI:
    def test_get_settings(self):
        response = client.get("/api/game/settings")
        assert response.status_code == 200

    def test_get_saves(self):
        response = client.get("/api/game/saves")
        assert response.status_code == 200
