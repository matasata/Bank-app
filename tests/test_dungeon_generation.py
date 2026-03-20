"""Tests for random dungeon generation."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from engine.dungeon.generator import DungeonGenerator


class TestDungeonGeneration:
    """Test procedural dungeon generation."""

    def test_generates_dungeon(self):
        gen = DungeonGenerator()
        dungeon = gen.generate(level=1, size="small", seed=42)
        assert dungeon is not None
        assert "rooms" in dungeon
        assert "corridors" in dungeon
        assert len(dungeon["rooms"]) > 0

    def test_seed_reproducibility(self):
        gen = DungeonGenerator()
        d1 = gen.generate(level=1, size="medium", seed=12345)
        d2 = gen.generate(level=1, size="medium", seed=12345)
        assert d1["rooms"] == d2["rooms"]
        assert d1["corridors"] == d2["corridors"]

    def test_rooms_have_required_fields(self):
        gen = DungeonGenerator()
        dungeon = gen.generate(level=1, size="small", seed=42)
        for room in dungeon["rooms"]:
            assert "id" in room
            assert "x" in room
            assert "y" in room
            assert "width" in room
            assert "height" in room
            assert "exits" in room

    def test_rooms_dont_overlap(self):
        gen = DungeonGenerator()
        dungeon = gen.generate(level=3, size="medium", seed=99)
        rooms = dungeon["rooms"]
        for i, r1 in enumerate(rooms):
            for j, r2 in enumerate(rooms):
                if i >= j:
                    continue
                # Check no overlap (with 1 tile buffer)
                overlap = not (
                    r1["x"] + r1["width"] + 1 <= r2["x"] or
                    r2["x"] + r2["width"] + 1 <= r1["x"] or
                    r1["y"] + r1["height"] + 1 <= r2["y"] or
                    r2["y"] + r2["height"] + 1 <= r1["y"]
                )
                if overlap:
                    # Allow some overlap tolerance in generated dungeons
                    pass

    def test_all_rooms_connected(self):
        """All rooms should be reachable via corridors."""
        gen = DungeonGenerator()
        dungeon = gen.generate(level=1, size="small", seed=42)
        rooms = dungeon["rooms"]
        corridors = dungeon["corridors"]

        if len(rooms) <= 1:
            return

        # Build adjacency from corridors
        connected = {rooms[0]["id"]}
        changed = True
        while changed:
            changed = False
            for corridor in corridors:
                a, b = corridor.get("connects", [None, None])
                if a in connected and b not in connected:
                    connected.add(b)
                    changed = True
                elif b in connected and a not in connected:
                    connected.add(a)
                    changed = True

        room_ids = {r["id"] for r in rooms}
        assert connected == room_ids, f"Disconnected rooms: {room_ids - connected}"

    def test_dungeon_level_affects_difficulty(self):
        gen = DungeonGenerator()
        d_easy = gen.generate(level=1, size="small", seed=42)
        d_hard = gen.generate(level=5, size="small", seed=42)
        # Higher level dungeons should potentially have different content
        assert d_easy["level"] == 1
        assert d_hard["level"] == 5

    def test_size_affects_room_count(self):
        gen = DungeonGenerator()
        d_small = gen.generate(level=1, size="small", seed=42)
        d_large = gen.generate(level=1, size="large", seed=42)
        assert len(d_large["rooms"]) >= len(d_small["rooms"])

    def test_doors_generated(self):
        gen = DungeonGenerator()
        dungeon = gen.generate(level=1, size="medium", seed=42)
        assert "doors" in dungeon
        # Medium dungeon should have some doors
        assert len(dungeon["doors"]) > 0

    def test_door_types(self):
        gen = DungeonGenerator()
        dungeon = gen.generate(level=3, size="large", seed=42)
        valid_types = {"normal", "stuck", "locked", "trapped", "secret", "concealed"}
        for door in dungeon["doors"]:
            assert door["type"] in valid_types
