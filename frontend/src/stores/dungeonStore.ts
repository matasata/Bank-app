import { create } from 'zustand';
import type {
  DungeonMap, DungeonRoom, DungeonTile, DoorInfo,
  DungeonGenerationParams, FogState, TileType,
} from '../types';

interface DungeonStoreState {
  currentDungeon: DungeonMap | null;
  isGenerating: boolean;
  generationParams: DungeonGenerationParams;
  viewportX: number;
  viewportY: number;
  zoom: number;
  selectedRoom: DungeonRoom | null;
  selectedDoor: DoorInfo | null;
  showMinimap: boolean;
  showGrid: boolean;
  explorationLog: string[];

  // Actions
  setDungeon: (dungeon: DungeonMap) => void;
  clearDungeon: () => void;
  setGenerationParams: (params: Partial<DungeonGenerationParams>) => void;
  generateLocalDungeon: () => void;
  moveParty: (direction: 'north' | 'south' | 'east' | 'west') => void;
  setViewport: (x: number, y: number) => void;
  setZoom: (zoom: number) => void;
  selectRoom: (room: DungeonRoom | null) => void;
  selectDoor: (door: DoorInfo | null) => void;
  toggleMinimap: () => void;
  toggleGrid: () => void;
  revealTile: (x: number, y: number) => void;
  updateFogOfWar: () => void;
  openDoor: (doorId: string) => void;
  interactWithDoor: (doorId: string, action: 'open' | 'close' | 'lock' | 'unlock' | 'bash') => void;
  addExplorationLog: (message: string) => void;
  markRoomExplored: (roomId: string) => void;
  markRoomCleared: (roomId: string) => void;
}

const defaultParams: DungeonGenerationParams = {
  width: 80,
  height: 60,
  roomCount: 12,
  corridorDensity: 0.5,
  trapDensity: 0.2,
  monsterDensity: 0.4,
  treasureDensity: 0.3,
  dungeonLevel: 1,
};

function createEmptyTile(x: number, y: number): DungeonTile {
  return {
    x, y,
    type: 'wall',
    fogState: 'unexplored',
    isRevealed: false,
  };
}

function generateSimpleDungeon(params: DungeonGenerationParams): DungeonMap {
  const { width, height, roomCount } = params;

  // Initialize tile grid
  const tiles: DungeonTile[][] = [];
  for (let y = 0; y < height; y++) {
    tiles[y] = [];
    for (let x = 0; x < width; x++) {
      tiles[y][x] = createEmptyTile(x, y);
    }
  }

  const explored: boolean[][] = [];
  for (let y = 0; y < height; y++) {
    explored[y] = new Array(width).fill(false);
  }

  const rooms: DungeonRoom[] = [];
  const doors: DoorInfo[] = [];

  // Generate rooms
  for (let i = 0; i < roomCount; i++) {
    const roomW = 4 + Math.floor(Math.random() * 6);
    const roomH = 4 + Math.floor(Math.random() * 6);
    const roomX = 2 + Math.floor(Math.random() * (width - roomW - 4));
    const roomY = 2 + Math.floor(Math.random() * (height - roomH - 4));

    // Check overlap
    let overlaps = false;
    for (const existing of rooms) {
      if (
        roomX < existing.x + existing.width + 2 &&
        roomX + roomW + 2 > existing.x &&
        roomY < existing.y + existing.height + 2 &&
        roomY + roomH + 2 > existing.y
      ) {
        overlaps = true;
        break;
      }
    }
    if (overlaps) continue;

    // Carve room
    for (let ry = roomY; ry < roomY + roomH; ry++) {
      for (let rx = roomX; rx < roomX + roomW; rx++) {
        if (ry >= 0 && ry < height && rx >= 0 && rx < width) {
          tiles[ry][rx] = {
            ...tiles[ry][rx],
            type: 'floor',
            roomId: `room-${rooms.length}`,
          };
        }
      }
    }

    rooms.push({
      id: `room-${rooms.length}`,
      name: `Chamber ${rooms.length + 1}`,
      description: 'A stone chamber stretches before you.',
      x: roomX,
      y: roomY,
      width: roomW,
      height: roomH,
      monsters: [],
      treasure: { copper: 0, silver: 0, electrum: 0, gold: 0, platinum: 0, gems: [], jewelry: [], magicItems: [] },
      traps: [],
      features: [],
      isExplored: false,
      isCleared: false,
      doors: [],
      lightLevel: 'dark',
    });
  }

  // Connect rooms with corridors
  for (let i = 0; i < rooms.length - 1; i++) {
    const r1 = rooms[i];
    const r2 = rooms[i + 1];
    const x1 = Math.floor(r1.x + r1.width / 2);
    const y1 = Math.floor(r1.y + r1.height / 2);
    const x2 = Math.floor(r2.x + r2.width / 2);
    const y2 = Math.floor(r2.y + r2.height / 2);

    // Horizontal first, then vertical
    const stepX = x1 < x2 ? 1 : -1;
    for (let x = x1; x !== x2; x += stepX) {
      if (y1 >= 0 && y1 < height && x >= 0 && x < width && tiles[y1][x].type === 'wall') {
        tiles[y1][x] = { ...tiles[y1][x], type: 'corridor' };
      }
    }
    const stepY = y1 < y2 ? 1 : -1;
    for (let y = y1; y !== y2; y += stepY) {
      if (y >= 0 && y < height && x2 >= 0 && x2 < width && tiles[y][x2].type === 'wall') {
        tiles[y][x2] = { ...tiles[y][x2], type: 'corridor' };
      }
    }

    // Add door between corridor and room
    const doorX = x2;
    const doorY = y2 > y1 ? r2.y : r2.y + r2.height - 1;
    doors.push({
      id: `door-${doors.length}`,
      x: doorX,
      y: doorY,
      orientation: 'horizontal',
      isLocked: Math.random() < 0.3,
      isTrapped: Math.random() < params.trapDensity,
      isSecret: Math.random() < 0.1,
      isOpen: false,
      hitPoints: 10,
    });
  }

  // Set starting position in first room
  const startRoom = rooms[0];
  const partyX = Math.floor(startRoom.x + startRoom.width / 2);
  const partyY = Math.floor(startRoom.y + startRoom.height / 2);

  return {
    id: crypto.randomUUID(),
    name: `Dungeon Level ${params.dungeonLevel}`,
    level: params.dungeonLevel,
    width,
    height,
    tiles,
    rooms,
    doors,
    partyPosition: { x: partyX, y: partyY },
    partyFacing: 'north',
    explored,
    lightRadius: 3,
  };
}

export const useDungeonStore = create<DungeonStoreState>((set, get) => ({
  currentDungeon: null,
  isGenerating: false,
  generationParams: defaultParams,
  viewportX: 0,
  viewportY: 0,
  zoom: 1,
  selectedRoom: null,
  selectedDoor: null,
  showMinimap: true,
  showGrid: true,
  explorationLog: [],

  setDungeon: (dungeon) => set({ currentDungeon: dungeon }),
  clearDungeon: () => set({ currentDungeon: null, selectedRoom: null, selectedDoor: null }),

  setGenerationParams: (params) =>
    set((state) => ({
      generationParams: { ...state.generationParams, ...params },
    })),

  generateLocalDungeon: () => {
    set({ isGenerating: true });
    const params = get().generationParams;
    const dungeon = generateSimpleDungeon(params);

    // Reveal starting area
    const { x, y } = dungeon.partyPosition;
    for (let dy = -dungeon.lightRadius; dy <= dungeon.lightRadius; dy++) {
      for (let dx = -dungeon.lightRadius; dx <= dungeon.lightRadius; dx++) {
        const tx = x + dx;
        const ty = y + dy;
        if (ty >= 0 && ty < dungeon.height && tx >= 0 && tx < dungeon.width) {
          dungeon.tiles[ty][tx].fogState = 'visible';
          dungeon.tiles[ty][tx].isRevealed = true;
          dungeon.explored[ty][tx] = true;
        }
      }
    }

    set({
      currentDungeon: dungeon,
      isGenerating: false,
      viewportX: x,
      viewportY: y,
      explorationLog: ['You enter the dungeon. Darkness surrounds you beyond the torchlight.'],
    });
  },

  moveParty: (direction) => {
    const dungeon = get().currentDungeon;
    if (!dungeon) return;

    const dx = direction === 'east' ? 1 : direction === 'west' ? -1 : 0;
    const dy = direction === 'south' ? 1 : direction === 'north' ? -1 : 0;
    const newX = dungeon.partyPosition.x + dx;
    const newY = dungeon.partyPosition.y + dy;

    // Bounds check
    if (newX < 0 || newX >= dungeon.width || newY < 0 || newY >= dungeon.height) return;

    const targetTile = dungeon.tiles[newY][newX];
    if (targetTile.type === 'wall') return;

    // Update position
    const newTiles = dungeon.tiles.map((row) => row.map((t) => ({ ...t })));
    const newExplored = dungeon.explored.map((row) => [...row]);

    // Set old visible tiles to explored
    for (let ty = 0; ty < dungeon.height; ty++) {
      for (let tx = 0; tx < dungeon.width; tx++) {
        if (newTiles[ty][tx].fogState === 'visible') {
          newTiles[ty][tx].fogState = 'explored';
        }
      }
    }

    // Reveal around new position
    for (let rdy = -dungeon.lightRadius; rdy <= dungeon.lightRadius; rdy++) {
      for (let rdx = -dungeon.lightRadius; rdx <= dungeon.lightRadius; rdx++) {
        const tx = newX + rdx;
        const ty = newY + rdy;
        if (ty >= 0 && ty < dungeon.height && tx >= 0 && tx < dungeon.width) {
          newTiles[ty][tx].fogState = 'visible';
          newTiles[ty][tx].isRevealed = true;
          newExplored[ty][tx] = true;
        }
      }
    }

    // Check if entering a new room
    const roomId = targetTile.roomId;
    const logs: string[] = [];
    if (roomId) {
      const room = dungeon.rooms.find((r) => r.id === roomId);
      if (room && !room.isExplored) {
        logs.push(`You enter ${room.name}. ${room.description}`);
      }
    }

    set({
      currentDungeon: {
        ...dungeon,
        tiles: newTiles,
        explored: newExplored,
        partyPosition: { x: newX, y: newY },
        partyFacing: direction,
      },
      viewportX: newX,
      viewportY: newY,
      explorationLog: [...get().explorationLog, ...logs],
    });
  },

  setViewport: (x, y) => set({ viewportX: x, viewportY: y }),
  setZoom: (zoom) => set({ zoom: Math.max(0.5, Math.min(3, zoom)) }),
  selectRoom: (room) => set({ selectedRoom: room }),
  selectDoor: (door) => set({ selectedDoor: door }),
  toggleMinimap: () => set((s) => ({ showMinimap: !s.showMinimap })),
  toggleGrid: () => set((s) => ({ showGrid: !s.showGrid })),

  revealTile: (x, y) => {
    const dungeon = get().currentDungeon;
    if (!dungeon) return;
    const newTiles = dungeon.tiles.map((row) => row.map((t) => ({ ...t })));
    if (y >= 0 && y < dungeon.height && x >= 0 && x < dungeon.width) {
      newTiles[y][x].isRevealed = true;
      newTiles[y][x].fogState = 'visible';
    }
    set({ currentDungeon: { ...dungeon, tiles: newTiles } });
  },

  updateFogOfWar: () => {
    const dungeon = get().currentDungeon;
    if (!dungeon) return;
    const { x, y } = dungeon.partyPosition;
    const newTiles = dungeon.tiles.map((row) => row.map((t) => ({
      ...t,
      fogState: t.fogState === 'visible' ? 'explored' as FogState : t.fogState,
    })));

    for (let dy = -dungeon.lightRadius; dy <= dungeon.lightRadius; dy++) {
      for (let dx = -dungeon.lightRadius; dx <= dungeon.lightRadius; dx++) {
        const tx = x + dx;
        const ty = y + dy;
        if (ty >= 0 && ty < dungeon.height && tx >= 0 && tx < dungeon.width) {
          newTiles[ty][tx].fogState = 'visible';
          newTiles[ty][tx].isRevealed = true;
        }
      }
    }

    set({ currentDungeon: { ...dungeon, tiles: newTiles } });
  },

  openDoor: (doorId) => {
    const dungeon = get().currentDungeon;
    if (!dungeon) return;
    set({
      currentDungeon: {
        ...dungeon,
        doors: dungeon.doors.map((d) =>
          d.id === doorId ? { ...d, isOpen: true } : d
        ),
      },
      explorationLog: [...get().explorationLog, 'You open the door.'],
    });
  },

  interactWithDoor: (doorId, action) => {
    const dungeon = get().currentDungeon;
    if (!dungeon) return;
    const door = dungeon.doors.find((d) => d.id === doorId);
    if (!door) return;

    let message = '';
    let updatedDoor = { ...door };

    switch (action) {
      case 'open':
        if (door.isLocked) {
          message = 'The door is locked!';
        } else {
          updatedDoor.isOpen = true;
          message = 'You open the door.';
        }
        break;
      case 'close':
        updatedDoor.isOpen = false;
        message = 'You close the door.';
        break;
      case 'lock':
        updatedDoor.isLocked = true;
        updatedDoor.isOpen = false;
        message = 'You lock the door.';
        break;
      case 'unlock':
        updatedDoor.isLocked = false;
        message = 'You unlock the door.';
        break;
      case 'bash':
        updatedDoor.hitPoints -= Math.floor(Math.random() * 6) + 1;
        if (updatedDoor.hitPoints <= 0) {
          updatedDoor.isOpen = true;
          updatedDoor.isLocked = false;
          message = 'You bash the door open!';
        } else {
          message = `You strike the door! (HP remaining: ${updatedDoor.hitPoints})`;
        }
        break;
    }

    set({
      currentDungeon: {
        ...dungeon,
        doors: dungeon.doors.map((d) => d.id === doorId ? updatedDoor : d),
      },
      explorationLog: [...get().explorationLog, message],
    });
  },

  addExplorationLog: (message) =>
    set((s) => ({ explorationLog: [...s.explorationLog, message] })),

  markRoomExplored: (roomId) => {
    const dungeon = get().currentDungeon;
    if (!dungeon) return;
    set({
      currentDungeon: {
        ...dungeon,
        rooms: dungeon.rooms.map((r) =>
          r.id === roomId ? { ...r, isExplored: true } : r
        ),
      },
    });
  },

  markRoomCleared: (roomId) => {
    const dungeon = get().currentDungeon;
    if (!dungeon) return;
    set({
      currentDungeon: {
        ...dungeon,
        rooms: dungeon.rooms.map((r) =>
          r.id === roomId ? { ...r, isCleared: true } : r
        ),
      },
    });
  },
}));
