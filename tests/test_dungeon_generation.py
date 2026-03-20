"""Tests for random dungeon generation."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from engine.dungeon.generator import DungeonGenerator, generate_dungeon, DungeonLevel


class TestDungeonGeneration:
    """Test procedural dungeon generation."""

    def test_generates_dungeon(self):
        gen = DungeonGenerator(dungeon_level=1, num_rooms=5, seed=42)
        dungeon = gen.generate()
        assert isinstance(dungeon, DungeonLevel)
        assert len(dungeon.rooms) == 5

    def test_seed_reproducibility(self):
        d1 = generate_dungeon(dungeon_level=1, num_rooms=8, seed=12345)
        d2 = generate_dungeon(dungeon_level=1, num_rooms=8, seed=12345)
        # IDs use uuid4 so strip them for comparison
        def strip_ids(rooms):
            result = []
            for r in rooms:
                r2 = {k: v for k, v in r.items() if k != "id"}
                r2["exits"] = [{k: v for k, v in e.items() if k != "id"} for e in r2.get("exits", [])]
                result.append(r2)
            return result
        assert strip_ids(d1["rooms"]) == strip_ids(d2["rooms"])

    def test_rooms_have_required_fields(self):
        dungeon = generate_dungeon(dungeon_level=1, num_rooms=5, seed=42)
        for room in dungeon["rooms"]:
            assert "id" in room
            assert "x" in room
            assert "y" in room
            assert "width" in room
            assert "shape" in room
            assert "exits" in room
            assert "contents" in room

    def test_dungeon_level_stored(self):
        dungeon = generate_dungeon(dungeon_level=3, num_rooms=5, seed=42)
        assert dungeon["level"] == 3

    def test_size_affects_room_count(self):
        d_small = generate_dungeon(dungeon_level=1, num_rooms=3, seed=42)
        d_large = generate_dungeon(dungeon_level=1, num_rooms=15, seed=42)
        assert len(d_large["rooms"]) > len(d_small["rooms"])

    def test_passages_connect_rooms(self):
        gen = DungeonGenerator(dungeon_level=1, num_rooms=5, seed=42)
        dungeon = gen.generate()
        # Should have num_rooms - 1 passages (linear connection)
        assert len(dungeon.passages) == len(dungeon.rooms) - 1

    def test_stairs_generated(self):
        gen = DungeonGenerator(dungeon_level=1, num_rooms=10, seed=42)
        dungeon = gen.generate()
        assert len(dungeon.stairs) >= 1

    def test_doors_on_rooms(self):
        gen = DungeonGenerator(dungeon_level=1, num_rooms=10, seed=42)
        dungeon = gen.generate()
        total_doors = sum(len(r.exits) for r in dungeon.rooms)
        assert total_doors > 0

    def test_room_descriptions_generated(self):
        gen = DungeonGenerator(dungeon_level=1, num_rooms=5, seed=42)
        dungeon = gen.generate()
        for room in dungeon.rooms:
            assert room.description != ""

    def test_theme_affects_description(self):
        gen1 = DungeonGenerator(dungeon_level=1, num_rooms=3, seed=42, theme="crypt")
        gen2 = DungeonGenerator(dungeon_level=1, num_rooms=3, seed=42, theme="cavern")
        d1 = gen1.generate()
        d2 = gen2.generate()
        # Same seed but different themes should produce different descriptions
        descs1 = [r.description for r in d1.rooms]
        descs2 = [r.description for r in d2.rooms]
        assert descs1 != descs2

    def test_as_dict(self):
        dungeon = generate_dungeon(dungeon_level=1, num_rooms=5, seed=42)
        assert isinstance(dungeon, dict)
        assert "rooms" in dungeon
        assert "passages" in dungeon
        assert "stairs" in dungeon
        assert "level" in dungeon
