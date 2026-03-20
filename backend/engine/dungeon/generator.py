"""Random dungeon generator implementing DMG Appendix A tables.

Generates dungeon levels procedurally with passages, rooms, doors, stairs,
traps, and special features. Accepts parameters for dungeon level, overall
size, theme, and seed for reproducibility.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from engine.character.ability_scores import DiceRoller


class Direction(str, Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"


class DoorType(str, Enum):
    WOODEN = "wooden"
    WOODEN_LOCKED = "wooden_locked"
    WOODEN_BARRED = "wooden_barred"
    IRON = "iron"
    IRON_LOCKED = "iron_locked"
    STONE = "stone"
    SECRET = "secret"
    CONCEALED = "concealed"
    PORTCULLIS = "portcullis"
    ONE_WAY = "one_way"


class RoomShape(str, Enum):
    SQUARE = "square"
    RECTANGULAR = "rectangular"
    CIRCULAR = "circular"
    TRIANGULAR = "triangular"
    TRAPEZOIDAL = "trapezoidal"
    IRREGULAR = "irregular"
    OCTAGONAL = "octagonal"
    OVAL = "oval"
    CAVE = "cave"


class ContentType(str, Enum):
    EMPTY = "empty"
    MONSTER = "monster"
    MONSTER_TREASURE = "monster_with_treasure"
    TREASURE = "treasure"
    SPECIAL = "special"
    TRICK_TRAP = "trick_trap"


class TrapType(str, Enum):
    PIT = "pit"
    POISON_NEEDLE = "poison_needle"
    GAS = "gas"
    FALLING_BLOCK = "falling_block"
    ARROW = "arrow"
    SPEAR = "spear"
    SCYTHING_BLADE = "scything_blade"
    FLOODING = "flooding"
    FIRE = "fire"
    TELEPORT = "teleport"
    ALARM = "alarm"
    MAGIC_MOUTH = "magic_mouth"


class StairType(str, Enum):
    DOWN_ONE = "down_one_level"
    DOWN_TWO = "down_two_levels"
    DOWN_THREE = "down_three_levels"
    UP_ONE = "up_one_level"
    UP_TWO = "up_two_levels"
    CHIMNEY_UP = "chimney_up"
    CHIMNEY_DOWN = "chimney_down"
    CHUTE = "chute"
    TRAP_DOOR = "trap_door"
    SPIRAL = "spiral"


@dataclass
class Door:
    """A door connecting two areas."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    door_type: DoorType = DoorType.WOODEN
    direction: Direction = Direction.NORTH
    locked: bool = False
    trapped: bool = False
    trap_type: Optional[TrapType] = None
    secret: bool = False

    def as_dict(self) -> Dict:
        return {
            "id": self.id,
            "door_type": self.door_type.value,
            "direction": self.direction.value,
            "locked": self.locked,
            "trapped": self.trapped,
            "trap_type": self.trap_type.value if self.trap_type else None,
            "secret": self.secret,
        }


@dataclass
class Room:
    """A room or chamber in the dungeon."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    shape: RoomShape = RoomShape.RECTANGULAR
    width: int = 20  # feet
    length: int = 30  # feet
    x: int = 0
    y: int = 0
    exits: List[Door] = field(default_factory=list)
    contents: ContentType = ContentType.EMPTY
    monster: Optional[str] = None
    treasure: Optional[str] = None
    trap: Optional[TrapType] = None
    special: Optional[str] = None
    description: str = ""
    illuminated: bool = False
    explored: bool = False

    def as_dict(self) -> Dict:
        return {
            "id": self.id,
            "shape": self.shape.value,
            "width": self.width,
            "length": self.length,
            "x": self.x,
            "y": self.y,
            "exits": [e.as_dict() for e in self.exits],
            "contents": self.contents.value,
            "monster": self.monster,
            "treasure": self.treasure,
            "trap": self.trap.value if self.trap else None,
            "special": self.special,
            "description": self.description,
            "illuminated": self.illuminated,
            "explored": self.explored,
        }


@dataclass
class Passage:
    """A corridor or passage in the dungeon."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    width: int = 10  # feet
    length: int = 60  # feet
    direction: Direction = Direction.NORTH
    x: int = 0
    y: int = 0
    branches: List[Direction] = field(default_factory=list)
    doors: List[Door] = field(default_factory=list)
    trap: Optional[TrapType] = None

    def as_dict(self) -> Dict:
        return {
            "id": self.id,
            "width": self.width,
            "length": self.length,
            "direction": self.direction.value,
            "x": self.x,
            "y": self.y,
            "branches": [b.value for b in self.branches],
            "doors": [d.as_dict() for d in self.doors],
            "trap": self.trap.value if self.trap else None,
        }


@dataclass
class Stairs:
    """Stairs connecting dungeon levels."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    stair_type: StairType = StairType.DOWN_ONE
    x: int = 0
    y: int = 0

    def as_dict(self) -> Dict:
        return {
            "id": self.id,
            "stair_type": self.stair_type.value,
            "x": self.x,
            "y": self.y,
        }


@dataclass
class DungeonLevel:
    """A single level of a generated dungeon."""

    level: int
    rooms: List[Room] = field(default_factory=list)
    passages: List[Passage] = field(default_factory=list)
    stairs: List[Stairs] = field(default_factory=list)
    width: int = 200  # feet
    height: int = 200  # feet
    theme: str = "standard"

    def as_dict(self) -> Dict:
        return {
            "level": self.level,
            "rooms": [r.as_dict() for r in self.rooms],
            "passages": [p.as_dict() for p in self.passages],
            "stairs": [s.as_dict() for s in self.stairs],
            "width": self.width,
            "height": self.height,
            "theme": self.theme,
        }


# ── DMG Appendix A lookup tables ─────────────────────────────────────────

ROOM_SHAPES_TABLE: List[Tuple[int, RoomShape]] = [
    (20, RoomShape.SQUARE),
    (50, RoomShape.RECTANGULAR),
    (60, RoomShape.CIRCULAR),
    (70, RoomShape.TRIANGULAR),
    (80, RoomShape.TRAPEZOIDAL),
    (85, RoomShape.OCTAGONAL),
    (90, RoomShape.OVAL),
    (95, RoomShape.CAVE),
    (100, RoomShape.IRREGULAR),
]

ROOM_SIZE_TABLE: Dict[RoomShape, List[Tuple[int, Tuple[int, int]]]] = {
    RoomShape.SQUARE: [
        (30, (10, 10)), (50, (20, 20)), (70, (30, 30)),
        (85, (40, 40)), (95, (50, 50)), (100, (60, 60)),
    ],
    RoomShape.RECTANGULAR: [
        (20, (10, 20)), (35, (20, 30)), (50, (20, 40)),
        (65, (30, 40)), (80, (30, 50)), (90, (40, 60)),
        (100, (50, 80)),
    ],
}

DOOR_TYPE_TABLE: List[Tuple[int, DoorType]] = [
    (30, DoorType.WOODEN),
    (45, DoorType.WOODEN_LOCKED),
    (55, DoorType.WOODEN_BARRED),
    (65, DoorType.IRON),
    (75, DoorType.IRON_LOCKED),
    (82, DoorType.STONE),
    (90, DoorType.SECRET),
    (95, DoorType.CONCEALED),
    (98, DoorType.PORTCULLIS),
    (100, DoorType.ONE_WAY),
]

ROOM_CONTENTS_TABLE: List[Tuple[int, ContentType]] = [
    (12, ContentType.MONSTER),
    (16, ContentType.MONSTER_TREASURE),
    (17, ContentType.SPECIAL),
    (18, ContentType.TRICK_TRAP),
    (19, ContentType.TREASURE),
    (20, ContentType.EMPTY),
]

TRAP_TABLE: List[Tuple[int, TrapType]] = [
    (15, TrapType.PIT),
    (25, TrapType.POISON_NEEDLE),
    (35, TrapType.GAS),
    (45, TrapType.FALLING_BLOCK),
    (55, TrapType.ARROW),
    (65, TrapType.SPEAR),
    (75, TrapType.SCYTHING_BLADE),
    (80, TrapType.FLOODING),
    (85, TrapType.FIRE),
    (95, TrapType.TELEPORT),
    (98, TrapType.ALARM),
    (100, TrapType.MAGIC_MOUTH),
]

STAIR_TABLE: List[Tuple[int, StairType]] = [
    (20, StairType.DOWN_ONE),
    (30, StairType.DOWN_TWO),
    (35, StairType.DOWN_THREE),
    (50, StairType.UP_ONE),
    (55, StairType.UP_TWO),
    (65, StairType.CHIMNEY_UP),
    (75, StairType.CHIMNEY_DOWN),
    (85, StairType.CHUTE),
    (90, StairType.TRAP_DOOR),
    (100, StairType.SPIRAL),
]

PASSAGE_WIDTH_TABLE: List[Tuple[int, int]] = [
    (30, 5), (60, 10), (80, 20), (90, 30), (100, 40),
]

SPECIAL_FEATURES: List[str] = [
    "Altar with strange carvings",
    "Pool of unknown liquid",
    "Statue with gem eyes",
    "Magical darkness fills the area",
    "Whispering voices echo from the walls",
    "Pillars carved with ancient runes",
    "Underground stream runs through the room",
    "Phosphorescent fungi illuminate the walls",
    "Ancient mural depicts a great battle",
    "Iron cage hanging from the ceiling",
    "Collapsed section reveals natural cavern",
    "Mosaic floor tiles form a magical pattern",
    "Strong wind blows from an unknown source",
    "Temperature is unnaturally cold",
    "Temperature is unnaturally hot",
    "Illusion of a different room",
    "Anti-magic zone",
    "Gravity is reversed",
    "Time passes at different rate",
    "Mirror that shows different reflections",
]


def _roll_table(roller: DiceRoller, table: list) -> Any:
    """Roll d100 and look up the result on a percentile table."""
    roll = roller.d100()
    for threshold, value in table:
        if roll <= threshold:
            return value
    return table[-1][1]


class DungeonGenerator:
    """Procedural dungeon generator based on DMG Appendix A.

    Args:
        dungeon_level: Difficulty level (affects monsters, traps, treasure).
        num_rooms: Target number of rooms to generate.
        map_width: Map width in feet (default 200).
        map_height: Map height in feet (default 200).
        theme: Flavour theme (``"standard"``, ``"crypt"``, ``"cavern"``,
            ``"temple"``, ``"sewers"``).
        seed: Optional RNG seed for reproducibility.
    """

    def __init__(
        self,
        dungeon_level: int = 1,
        num_rooms: int = 10,
        map_width: int = 200,
        map_height: int = 200,
        theme: str = "standard",
        seed: Optional[int] = None,
    ) -> None:
        self.dungeon_level = dungeon_level
        self.num_rooms = num_rooms
        self.map_width = map_width
        self.map_height = map_height
        self.theme = theme
        self.roller = DiceRoller(seed)

    def generate(self) -> DungeonLevel:
        """Generate a complete dungeon level.

        Returns:
            A ``DungeonLevel`` containing rooms, passages, and stairs.
        """
        dungeon = DungeonLevel(
            level=self.dungeon_level,
            width=self.map_width,
            height=self.map_height,
            theme=self.theme,
        )

        # Place rooms
        for i in range(self.num_rooms):
            room = self._generate_room(i)
            dungeon.rooms.append(room)

        # Generate passages connecting rooms
        for i in range(len(dungeon.rooms) - 1):
            passage = self._generate_passage(dungeon.rooms[i], dungeon.rooms[i + 1])
            dungeon.passages.append(passage)

        # Generate stairs (1 per ~5 rooms)
        num_stairs = max(1, self.num_rooms // 5)
        for _ in range(num_stairs):
            stairs = self._generate_stairs()
            dungeon.stairs.append(stairs)

        return dungeon

    def _generate_room(self, index: int) -> Room:
        """Generate a single room with all attributes."""
        shape = _roll_table(self.roller, ROOM_SHAPES_TABLE)

        # Determine size
        size_table = ROOM_SIZE_TABLE.get(shape, ROOM_SIZE_TABLE[RoomShape.RECTANGULAR])
        width, length = _roll_table(self.roller, size_table)

        # Position on grid (simple grid placement to avoid overlap)
        cols = max(1, int(self.map_width ** 0.5 / 50))
        row = index // cols
        col = index % cols
        x = col * (self.map_width // max(1, cols))
        y = row * (self.map_height // max(1, (self.num_rooms // cols + 1)))

        # Exits
        num_exits = self.roller._rng.randint(1, 4)
        exits: List[Door] = []
        directions = list(Direction)
        self.roller._rng.shuffle(directions)
        for d in directions[:num_exits]:
            door = self._generate_door(d)
            exits.append(door)

        # Contents
        contents = _roll_table(self.roller, ROOM_CONTENTS_TABLE)

        # Details based on contents
        monster = None
        treasure = None
        trap = None
        special = None

        if contents in (ContentType.MONSTER, ContentType.MONSTER_TREASURE):
            monster = f"Level {self.dungeon_level} encounter"
        if contents in (ContentType.MONSTER_TREASURE, ContentType.TREASURE):
            treasure = f"Treasure Type {chr(64 + min(self.dungeon_level, 26))}"
        if contents == ContentType.TRICK_TRAP:
            trap = _roll_table(self.roller, TRAP_TABLE)
        if contents == ContentType.SPECIAL:
            special = self.roller._rng.choice(SPECIAL_FEATURES)

        description = self._generate_room_description(shape, contents)

        return Room(
            shape=shape,
            width=width,
            length=length,
            x=x,
            y=y,
            exits=exits,
            contents=contents,
            monster=monster,
            treasure=treasure,
            trap=trap,
            special=special,
            description=description,
        )

    def _generate_door(self, direction: Direction) -> Door:
        """Generate a door with random type and traits."""
        door_type = _roll_table(self.roller, DOOR_TYPE_TABLE)
        locked = door_type in (
            DoorType.WOODEN_LOCKED, DoorType.IRON_LOCKED,
        )
        secret = door_type in (DoorType.SECRET, DoorType.CONCEALED)

        # Chance of trapped door (~15%)
        trapped = self.roller._rng.randint(1, 20) <= 3
        trap_type = _roll_table(self.roller, TRAP_TABLE) if trapped else None

        return Door(
            door_type=door_type,
            direction=direction,
            locked=locked,
            trapped=trapped,
            trap_type=trap_type,
            secret=secret,
        )

    def _generate_passage(self, room_a: Room, room_b: Room) -> Passage:
        """Generate a passage connecting two rooms."""
        width = _roll_table(self.roller, PASSAGE_WIDTH_TABLE)
        dx = room_b.x - room_a.x
        dy = room_b.y - room_a.y
        length = max(10, abs(dx) + abs(dy))

        if abs(dx) > abs(dy):
            direction = Direction.EAST if dx > 0 else Direction.WEST
        else:
            direction = Direction.SOUTH if dy > 0 else Direction.NORTH

        # Random branch chance
        branches: List[Direction] = []
        if self.roller._rng.randint(1, 6) <= 2:
            branch_dir = self.roller._rng.choice(list(Direction))
            branches.append(branch_dir)

        # Passage trap (~10% chance)
        trap = None
        if self.roller._rng.randint(1, 10) == 1:
            trap = _roll_table(self.roller, TRAP_TABLE)

        return Passage(
            width=width,
            length=length,
            direction=direction,
            x=room_a.x + room_a.width,
            y=room_a.y,
            branches=branches,
            trap=trap,
        )

    def _generate_stairs(self) -> Stairs:
        """Generate a stairway."""
        stair_type = _roll_table(self.roller, STAIR_TABLE)
        x = self.roller._rng.randint(0, self.map_width - 10)
        y = self.roller._rng.randint(0, self.map_height - 10)
        return Stairs(stair_type=stair_type, x=x, y=y)

    def _generate_room_description(
        self, shape: RoomShape, contents: ContentType
    ) -> str:
        """Generate a flavour description for a room."""
        shape_desc = {
            RoomShape.SQUARE: "A square chamber",
            RoomShape.RECTANGULAR: "A rectangular room",
            RoomShape.CIRCULAR: "A round chamber",
            RoomShape.TRIANGULAR: "An oddly triangular room",
            RoomShape.TRAPEZOIDAL: "A trapezoidal hall",
            RoomShape.OCTAGONAL: "An octagonal chamber",
            RoomShape.OVAL: "An oval room",
            RoomShape.CAVE: "A natural cavern",
            RoomShape.IRREGULAR: "An irregularly shaped area",
        }

        theme_details = {
            "standard": "with rough stone walls.",
            "crypt": "with niches carved into the walls for the dead.",
            "cavern": "with dripping stalactites overhead.",
            "temple": "with faded religious iconography on the walls.",
            "sewers": "with damp, slimy walls and a fetid stench.",
        }

        base = shape_desc.get(shape, "A room")
        detail = theme_details.get(self.theme, "with bare stone walls.")

        content_desc = ""
        if contents == ContentType.EMPTY:
            content_desc = " It appears to be empty."
        elif contents == ContentType.MONSTER:
            content_desc = " Something stirs in the shadows."
        elif contents == ContentType.MONSTER_TREASURE:
            content_desc = " The glint of treasure catches your eye, but something guards it."
        elif contents == ContentType.TREASURE:
            content_desc = " A cache of valuables lies abandoned here."
        elif contents == ContentType.TRICK_TRAP:
            content_desc = " An uneasy feeling pervades this area."
        elif contents == ContentType.SPECIAL:
            content_desc = " Something unusual about this place demands attention."

        return f"{base} {detail}{content_desc}"


def generate_dungeon(
    dungeon_level: int = 1,
    num_rooms: int = 10,
    map_width: int = 200,
    map_height: int = 200,
    theme: str = "standard",
    seed: Optional[int] = None,
) -> Dict:
    """Generate a dungeon and return it as a dictionary.

    Convenience wrapper around ``DungeonGenerator``.
    """
    gen = DungeonGenerator(
        dungeon_level=dungeon_level,
        num_rooms=num_rooms,
        map_width=map_width,
        map_height=map_height,
        theme=theme,
        seed=seed,
    )
    return gen.generate().as_dict()
