// ─── Ability Scores ───────────────────────────────────────────────────────────

export interface AbilityScores {
  strength: number;
  dexterity: number;
  constitution: number;
  intelligence: number;
  wisdom: number;
  charisma: number;
}

export type AbilityName = keyof AbilityScores;

export const ABILITY_NAMES: AbilityName[] = [
  'strength', 'dexterity', 'constitution',
  'intelligence', 'wisdom', 'charisma',
];

export interface AbilityModifiers {
  hitBonus: number;
  damageBonus: number;
  armorClassBonus: number;
  hitPointBonus: number;
  spellBonus: number;
  reactionAdjustment: number;
}

// ─── Exceptional Strength (Fighters with 18 STR) ─────────────────────────────

export interface ExceptionalStrength {
  percentile: number; // 01-00 (100)
}

// ─── Races ────────────────────────────────────────────────────────────────────

export type Race =
  | 'Human'
  | 'Dwarf'
  | 'Elf'
  | 'Gnome'
  | 'Half-Elf'
  | 'Halfling'
  | 'Half-Orc';

export interface RaceInfo {
  name: Race;
  abilityAdjustments: Partial<AbilityScores>;
  abilityMinimums: Partial<AbilityScores>;
  abilityMaximums: Partial<AbilityScores>;
  allowedClasses: CharacterClassName[];
  specialAbilities: string[];
  languages: string[];
  infravision: number; // feet, 0 = none
  multiClassOptions: CharacterClassName[][];
  description: string;
  icon: string;
}

// ─── Classes ──────────────────────────────────────────────────────────────────

export type CharacterClassName =
  | 'Fighter'
  | 'Paladin'
  | 'Ranger'
  | 'Cleric'
  | 'Druid'
  | 'Magic-User'
  | 'Illusionist'
  | 'Thief'
  | 'Assassin'
  | 'Monk';

export interface CharacterClass {
  name: CharacterClassName;
  hitDice: string;
  abilityRequirements: Partial<AbilityScores>;
  primeRequisites: AbilityName[];
  allowedRaces: Race[];
  allowedAlignments: Alignment[];
  savingThrows: SavingThrows;
  attackTable: number[];
  abilities: string[];
  spellcasting: boolean;
  description: string;
}

// ─── Alignment ────────────────────────────────────────────────────────────────

export type LawChaosAxis = 'Lawful' | 'Neutral' | 'Chaotic';
export type GoodEvilAxis = 'Good' | 'Neutral' | 'Evil';
export type Alignment = `${LawChaosAxis} ${GoodEvilAxis}` | 'True Neutral';

export const ALL_ALIGNMENTS: Alignment[] = [
  'Lawful Good', 'Lawful Neutral', 'Lawful Evil',
  'Neutral Good', 'True Neutral', 'Neutral Evil',
  'Chaotic Good', 'Chaotic Neutral', 'Chaotic Evil',
];

// ─── Saving Throws ────────────────────────────────────────────────────────────

export interface SavingThrows {
  paralyzation: number;
  poison: number;
  petrification: number;
  breath: number;
  spells: number;
}

// ─── Equipment ────────────────────────────────────────────────────────────────

export type EquipmentCategory =
  | 'Weapon'
  | 'Armor'
  | 'Shield'
  | 'Ammunition'
  | 'Adventuring Gear'
  | 'Potion'
  | 'Scroll'
  | 'Ring'
  | 'Miscellaneous Magic';

export interface EquipmentItem {
  id: string;
  name: string;
  category: EquipmentCategory;
  cost: number; // in gold pieces
  weight: number; // in coins (10 coins = 1 lb)
  damage?: string;
  armorClass?: number;
  speed?: number;
  description: string;
  magical?: boolean;
  bonus?: number;
  quantity: number;
}

// ─── Spells ───────────────────────────────────────────────────────────────────

export interface Spell {
  id: string;
  name: string;
  level: number;
  school: string;
  castingTime: string;
  range: string;
  duration: string;
  areaOfEffect: string;
  components: string;
  savingThrow: string;
  description: string;
  reversible: boolean;
}

export interface SpellSlots {
  [level: number]: number;
}

// ─── Character ────────────────────────────────────────────────────────────────

export type RollingMethod =
  | '3d6-in-order'
  | '4d6-drop-lowest'
  | '2d6+6'
  | '3d6-twice-best'
  | '4d6-arrange'
  | 'point-buy';

export interface DiceRollResult {
  dice: number[];
  dropped: number[];
  total: number;
  method: RollingMethod;
  timestamp: number;
}

export interface Character {
  id: string;
  name: string;
  race: Race;
  className: CharacterClassName;
  multiClass?: CharacterClassName[];
  level: number;
  experience: number;
  experienceNextLevel: number;
  alignment: Alignment;
  abilityScores: AbilityScores;
  exceptionalStrength?: ExceptionalStrength;
  hitPoints: number;
  maxHitPoints: number;
  armorClass: number;
  thac0: number;
  savingThrows: SavingThrows;
  equipment: EquipmentItem[];
  gold: number;
  silver: number;
  copper: number;
  electrum: number;
  platinum: number;
  spells: Spell[];
  spellSlots: SpellSlots;
  memorizedSpells: Spell[];
  specialAbilities: string[];
  proficiencies: string[];
  languages: string[];
  age: number;
  height: string;
  weight: string;
  encumbrance: number;
  maxEncumbrance: number;
  movementRate: number;
  portrait?: string;
  backstory: string;
  notes: string;
  conditions: StatusCondition[];
  isNPC: boolean;
  createdAt: number;
}

export type StatusCondition =
  | 'Poisoned'
  | 'Paralyzed'
  | 'Petrified'
  | 'Charmed'
  | 'Sleeping'
  | 'Frightened'
  | 'Invisible'
  | 'Blinded'
  | 'Deafened'
  | 'Stunned'
  | 'Dead'
  | 'Unconscious';

// ─── Party ────────────────────────────────────────────────────────────────────

export interface MarchingOrder {
  front: string[];   // character IDs
  middle: string[];
  rear: string[];
}

export interface Party {
  id: string;
  name: string;
  members: Character[];
  marchingOrder: MarchingOrder;
  partyGold: number;
  sharedInventory: EquipmentItem[];
  callerCharacterId: string;
  mapperCharacterId: string;
}

// ─── Dungeon Map ──────────────────────────────────────────────────────────────

export type TileType =
  | 'wall'
  | 'floor'
  | 'corridor'
  | 'door'
  | 'secret-door'
  | 'locked-door'
  | 'stairs-up'
  | 'stairs-down'
  | 'trap'
  | 'water'
  | 'pit'
  | 'empty';

export type FogState = 'unexplored' | 'explored' | 'visible';

export interface DungeonTile {
  x: number;
  y: number;
  type: TileType;
  fogState: FogState;
  roomId?: string;
  isRevealed: boolean;
  contents?: string;
  trapType?: string;
  trapDetected?: boolean;
}

export interface DoorInfo {
  id: string;
  x: number;
  y: number;
  orientation: 'horizontal' | 'vertical';
  isLocked: boolean;
  isTrapped: boolean;
  isSecret: boolean;
  isOpen: boolean;
  hitPoints: number;
}

export interface DungeonRoom {
  id: string;
  name: string;
  description: string;
  x: number;
  y: number;
  width: number;
  height: number;
  monsters: Monster[];
  treasure: TreasureHoard;
  traps: Trap[];
  features: string[];
  isExplored: boolean;
  isCleared: boolean;
  doors: DoorInfo[];
  lightLevel: 'dark' | 'dim' | 'bright';
}

export interface Trap {
  id: string;
  type: string;
  damage: string;
  savingThrow: string;
  detected: boolean;
  disarmed: boolean;
  description: string;
}

export interface TreasureHoard {
  copper: number;
  silver: number;
  electrum: number;
  gold: number;
  platinum: number;
  gems: string[];
  jewelry: string[];
  magicItems: EquipmentItem[];
}

export interface Monster {
  id: string;
  name: string;
  hitDice: string;
  hitPoints: number;
  maxHitPoints: number;
  armorClass: number;
  thac0: number;
  numberOfAttacks: number;
  damage: string;
  movement: number;
  specialAbilities: string[];
  morale: number;
  treasureType: string;
  experience: number;
  alignment: Alignment;
  isHostile: boolean;
  conditions: StatusCondition[];
}

export interface DungeonMap {
  id: string;
  name: string;
  level: number;
  width: number;
  height: number;
  tiles: DungeonTile[][];
  rooms: DungeonRoom[];
  doors: DoorInfo[];
  partyPosition: { x: number; y: number };
  partyFacing: 'north' | 'south' | 'east' | 'west';
  explored: boolean[][];
  lightRadius: number; // in tiles
}

export interface DungeonGenerationParams {
  width: number;
  height: number;
  roomCount: number;
  corridorDensity: number;
  trapDensity: number;
  monsterDensity: number;
  treasureDensity: number;
  dungeonLevel: number;
}

// ─── Combat ───────────────────────────────────────────────────────────────────

export type CombatPhase =
  | 'initiative'
  | 'movement'
  | 'missile'
  | 'magic'
  | 'melee'
  | 'resolution';

export interface InitiativeEntry {
  id: string;
  entityId: string;
  entityName: string;
  entityType: 'character' | 'monster';
  roll: number;
  dexterityModifier: number;
  weaponSpeed: number;
  total: number;
  hasActed: boolean;
  surpriseRounds: number;
}

export type CombatActionType =
  | 'attack'
  | 'cast-spell'
  | 'use-item'
  | 'move'
  | 'turn-undead'
  | 'flee'
  | 'parry'
  | 'set-weapon'
  | 'charge'
  | 'withdraw'
  | 'delay';

export interface CombatAction {
  id: string;
  actorId: string;
  actorName: string;
  type: CombatActionType;
  targetId?: string;
  targetName?: string;
  attackRoll?: number;
  damageRoll?: number;
  hitResult?: 'hit' | 'miss' | 'critical' | 'fumble';
  spellId?: string;
  itemId?: string;
  description: string;
  timestamp: number;
}

export interface CombatState {
  isActive: boolean;
  round: number;
  phase: CombatPhase;
  initiativeOrder: InitiativeEntry[];
  currentTurnIndex: number;
  combatLog: CombatAction[];
  participants: (Character | Monster)[];
  surpriseState: {
    partySurprised: boolean;
    monstersSurprised: boolean;
    surpriseRounds: number;
  };
  environmentalEffects: string[];
}

// ─── Game Session ─────────────────────────────────────────────────────────────

export interface GameSettings {
  criticalHitsEnabled: boolean;
  criticalFumbleEnabled: boolean;
  encumbranceRulesEnabled: boolean;
  speedFactorInitiativeEnabled: boolean;
  autoRollMonsterHD: boolean;
  showDamageNumbers: boolean;
  darkMode: boolean;
  soundEffectsEnabled: boolean;
  animationsEnabled: boolean;
  fontSize: 'small' | 'medium' | 'large';
  autoSaveEnabled: boolean;
  autoSaveInterval: number; // minutes
}

export interface GameSession {
  id: string;
  name: string;
  party: Party;
  currentDungeon?: DungeonMap;
  combat?: CombatState;
  settings: GameSettings;
  actionLog: GameLogEntry[];
  createdAt: number;
  updatedAt: number;
  playTimeSeconds: number;
}

export interface GameLogEntry {
  id: string;
  timestamp: number;
  type: 'system' | 'combat' | 'exploration' | 'dialogue' | 'loot' | 'dice' | 'error';
  message: string;
  details?: string;
  rollResult?: DiceRollResult;
}

export interface SaveSlot {
  id: string;
  slotNumber: number;
  sessionName: string;
  partyName: string;
  partyLevel: string;
  dungeonName?: string;
  timestamp: number;
  playTime: string;
  preview?: string;
}

// ─── Modules ──────────────────────────────────────────────────────────────────

export interface ModuleMetadata {
  id: string;
  code: string; // e.g., "B1", "T1"
  title: string;
  author: string;
  levelRange: string;
  playerCount: string;
  description: string;
  version: string;
  thumbnail?: string;
}

export interface ModuleRoom extends DungeonRoom {
  readAloudText: string;
  dmNotes: string;
  encounterTriggers: EncounterTrigger[];
}

export interface EncounterTrigger {
  id: string;
  type: 'enter' | 'search' | 'interact' | 'time';
  condition?: string;
  action: string;
  oneShot: boolean;
  triggered: boolean;
}

export interface GameModule {
  metadata: ModuleMetadata;
  maps: DungeonMap[];
  rooms: ModuleRoom[];
  wanderingMonsters: WanderingMonsterTable;
  customMonsters: Monster[];
  customItems: EquipmentItem[];
  introText: string;
  conclusionText: string;
}

export interface WanderingMonsterEntry {
  roll: [number, number]; // min, max on d20
  monster: string;
  quantity: string;
}

export interface WanderingMonsterTable {
  checkFrequency: number; // in turns
  entries: WanderingMonsterEntry[];
}

// ─── UI State ─────────────────────────────────────────────────────────────────

export type AppView =
  | 'character-creation'
  | 'dungeon'
  | 'combat'
  | 'party'
  | 'modules'
  | 'settings';

export interface PanelLayout {
  leftWidth: number;
  rightWidth: number;
  bottomHeight: number;
}
