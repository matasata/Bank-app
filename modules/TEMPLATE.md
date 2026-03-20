# AD&D Module Template

## Overview

Custom adventure modules are JSON files placed in the `modules/` directory. The game will automatically detect and load them.

## Module Schema

```json
{
  "module_id": "unique-id-for-your-module",
  "title": "Module Title",
  "author": "Your Name",
  "description": "A brief description of the adventure.",
  "recommended_levels": [1, 3],
  "maps": [
    {
      "map_id": "level-1",
      "name": "First Level",
      "grid_width": 40,
      "grid_height": 30,
      "tiles": [],
      "rooms": [
        {
          "room_id": "r1",
          "name": "Entry Hall",
          "description": "A long hall with crumbling pillars...",
          "x": 5,
          "y": 10,
          "width": 6,
          "height": 4,
          "contents": {
            "monsters": [
              {
                "monster_id": "goblin",
                "count": 4,
                "hp_override": null
              }
            ],
            "treasure": [
              {
                "type": "gold",
                "amount": 50
              }
            ],
            "traps": [
              {
                "type": "pit",
                "damage": "1d6",
                "detection_modifier": 0,
                "description": "A concealed pit trap"
              }
            ],
            "features": [
              {
                "type": "altar",
                "description": "A crumbling stone altar dedicated to an unknown deity"
              }
            ]
          },
          "on_enter": "event_id_or_null",
          "read_aloud": "You step into a dusty chamber. The air is thick with the smell of decay."
        }
      ],
      "doors": [
        {
          "door_id": "d1",
          "x": 5,
          "y": 12,
          "orientation": "vertical",
          "type": "wooden",
          "locked": false,
          "trapped": false,
          "secret": false,
          "connects": ["r1", "corridor-1"]
        }
      ],
      "corridors": [
        {
          "corridor_id": "corridor-1",
          "points": [
            {"x": 4, "y": 12},
            {"x": 1, "y": 12},
            {"x": 1, "y": 20}
          ],
          "width": 2
        }
      ]
    }
  ],
  "encounters": [
    {
      "encounter_id": "enc1",
      "name": "Goblin Patrol",
      "monsters": [
        {"monster_id": "goblin", "count": "1d4+2"}
      ],
      "trigger": "room_enter",
      "trigger_room": "r1"
    }
  ],
  "events": [
    {
      "event_id": "evt1",
      "name": "Collapsing Ceiling",
      "type": "trap",
      "description": "The ceiling begins to rumble...",
      "effect": {
        "damage": "2d6",
        "save_type": "petrification",
        "save_for": "half"
      },
      "one_time": true
    }
  ],
  "npcs": [
    {
      "npc_id": "npc1",
      "name": "Old Barthen",
      "race": "human",
      "class": "fighter",
      "level": 3,
      "alignment": "neutral_good",
      "description": "A weathered old warrior turned shopkeeper.",
      "dialogue": {
        "greeting": "Well met, adventurers!",
        "quest": "There's trouble in the old mines..."
      },
      "location": "r1"
    }
  ],
  "custom_items": [
    {
      "item_id": "sword-of-karak",
      "name": "Sword of Karak-Zhul",
      "type": "weapon",
      "subtype": "long_sword",
      "magical": true,
      "bonus": 2,
      "damage_bonus": 2,
      "special": "Glows blue within 60ft of orcs",
      "description": "An ancient elven blade forged in the First Age.",
      "value_gp": 5000
    }
  ],
  "custom_monsters": [
    {
      "monster_id": "karak-guardian",
      "name": "Guardian of Karak-Zhul",
      "hd": "6+6",
      "hp": 42,
      "ac": 2,
      "movement": 12,
      "attacks": [
        {"name": "Slam", "damage": "2d8+4"}
      ],
      "special_abilities": ["immune_to_non_magical_weapons"],
      "special_defenses": ["regeneration_3"],
      "magic_resistance": 0,
      "alignment": "neutral",
      "intelligence": "low",
      "size": "L",
      "xp_value": 975,
      "description": "A massive stone construct animated by ancient magic."
    }
  ]
}
```

## Field Reference

### Module Root
- `module_id`: Unique identifier (use kebab-case)
- `title`: Display name of the module
- `recommended_levels`: Array of [min_level, max_level] for the party

### Maps
Each map represents one dungeon level or area.
- `grid_width`/`grid_height`: Map dimensions in 10ft squares
- `tiles`: Optional array for custom tile data
- `rooms`: Array of room definitions
- `doors`: Array of door definitions
- `corridors`: Array of corridor paths

### Rooms
- `x`, `y`: Top-left corner position on grid
- `width`, `height`: Room dimensions in grid squares
- `contents`: Object containing monsters, treasure, traps, and features
- `on_enter`: Event ID to trigger when party enters (null if none)
- `read_aloud`: Flavor text to display to players

### Monsters in Rooms
- `monster_id`: References a monster from the database or `custom_monsters`
- `count`: Number of monsters (integer or dice expression like "1d4+2")
- `hp_override`: Set specific HP, or null for random roll

### Doors
- `orientation`: "vertical" or "horizontal"
- `type`: "wooden", "iron", "stone", "portcullis"
- `connects`: Array of two IDs (room or corridor) that the door connects

### Events
- `type`: "trap", "encounter", "narrative", "puzzle"
- `one_time`: If true, only triggers once per game

## Tips

1. Use the monster database IDs for common monsters
2. Custom monsters only need to be defined if they don't exist in the base database
3. Test your module by loading it in the Module Browser
4. Keep room descriptions concise but evocative
5. Use events for scripted encounters and traps for maximum flexibility
