import { create } from 'zustand';
import type {
  Character, AbilityScores, AbilityName, Race, CharacterClassName,
  Alignment, EquipmentItem, Spell, RollingMethod, DiceRollResult,
  RaceInfo, ExceptionalStrength,
} from '../types';
import { rollAllAbilities } from '../utils/dice';

// ─── Race Data ────────────────────────────────────────────────────────────────

export const RACE_DATA: Record<Race, RaceInfo> = {
  Human: {
    name: 'Human',
    abilityAdjustments: {},
    abilityMinimums: { strength: 3, dexterity: 3, constitution: 3, intelligence: 3, wisdom: 3, charisma: 3 },
    abilityMaximums: { strength: 18, dexterity: 18, constitution: 18, intelligence: 18, wisdom: 18, charisma: 18 },
    allowedClasses: ['Fighter', 'Paladin', 'Ranger', 'Cleric', 'Druid', 'Magic-User', 'Illusionist', 'Thief', 'Assassin', 'Monk'],
    specialAbilities: ['No level limits', 'Can be any class'],
    languages: ['Common'],
    infravision: 0,
    multiClassOptions: [],
    description: 'The most versatile of all races, humans can be any class and have no level limits.',
    icon: '👤',
  },
  Dwarf: {
    name: 'Dwarf',
    abilityAdjustments: { constitution: 1, charisma: -1 },
    abilityMinimums: { strength: 8, constitution: 12 },
    abilityMaximums: { strength: 18, dexterity: 17, constitution: 19, intelligence: 18, wisdom: 18, charisma: 16 },
    allowedClasses: ['Fighter', 'Thief', 'Assassin'],
    specialAbilities: ['Infravision 60\'', 'Detect stonework traps', '+4 save vs. magic', '+4 save vs. poison'],
    languages: ['Common', 'Dwarvish', 'Gnomish', 'Goblin', 'Kobold', 'Orcish'],
    infravision: 60,
    multiClassOptions: [['Fighter', 'Thief']],
    description: 'Stout and hardy, dwarves are master craftsmen and fierce warriors of the underground.',
    icon: '⛏️',
  },
  Elf: {
    name: 'Elf',
    abilityAdjustments: { dexterity: 1, constitution: -1 },
    abilityMinimums: { intelligence: 8, dexterity: 7, constitution: 6, charisma: 8 },
    abilityMaximums: { strength: 18, dexterity: 19, constitution: 17, intelligence: 18, wisdom: 18, charisma: 18 },
    allowedClasses: ['Fighter', 'Magic-User', 'Thief', 'Assassin'],
    specialAbilities: ['Infravision 60\'', '90% sleep/charm resistance', 'Detect secret doors', 'Surprise bonus with elven cloak'],
    languages: ['Common', 'Elvish', 'Gnomish', 'Halfling', 'Goblin', 'Hobgoblin', 'Orcish', 'Gnoll'],
    infravision: 60,
    multiClassOptions: [['Fighter', 'Magic-User'], ['Fighter', 'Thief'], ['Magic-User', 'Thief'], ['Fighter', 'Magic-User', 'Thief']],
    description: 'Graceful and long-lived, elves combine magical aptitude with martial skill.',
    icon: '🏹',
  },
  Gnome: {
    name: 'Gnome',
    abilityAdjustments: {},
    abilityMinimums: { strength: 6, constitution: 8, intelligence: 7 },
    abilityMaximums: { strength: 18, dexterity: 18, constitution: 18, intelligence: 18, wisdom: 18, charisma: 18 },
    allowedClasses: ['Fighter', 'Illusionist', 'Thief', 'Assassin'],
    specialAbilities: ['Infravision 60\'', 'Detect underground features', '+4 save vs. magic'],
    languages: ['Common', 'Dwarvish', 'Gnomish', 'Goblin', 'Kobold'],
    infravision: 60,
    multiClassOptions: [['Fighter', 'Illusionist'], ['Fighter', 'Thief'], ['Illusionist', 'Thief']],
    description: 'Smaller cousins of dwarves, gnomes are clever tinkerers and natural illusionists.',
    icon: '🔮',
  },
  'Half-Elf': {
    name: 'Half-Elf',
    abilityAdjustments: {},
    abilityMinimums: { intelligence: 4, dexterity: 6, constitution: 6 },
    abilityMaximums: { strength: 18, dexterity: 18, constitution: 18, intelligence: 18, wisdom: 18, charisma: 18 },
    allowedClasses: ['Fighter', 'Ranger', 'Cleric', 'Druid', 'Magic-User', 'Thief', 'Assassin'],
    specialAbilities: ['Infravision 60\'', '30% sleep/charm resistance', 'Detect secret doors'],
    languages: ['Common', 'Elvish'],
    infravision: 60,
    multiClassOptions: [['Fighter', 'Cleric'], ['Fighter', 'Thief'], ['Fighter', 'Magic-User'], ['Cleric', 'Magic-User'], ['Cleric', 'Ranger'], ['Thief', 'Magic-User']],
    description: 'Half-elves combine the best qualities of their human and elven heritage.',
    icon: '🌿',
  },
  Halfling: {
    name: 'Halfling',
    abilityAdjustments: { strength: -1, dexterity: 1 },
    abilityMinimums: { strength: 6, dexterity: 8, constitution: 10, intelligence: 6, wisdom: 3 },
    abilityMaximums: { strength: 17, dexterity: 19, constitution: 18, intelligence: 18, wisdom: 17, charisma: 18 },
    allowedClasses: ['Fighter', 'Thief'],
    specialAbilities: ['Infravision 60\'', '+3 missile attack bonus', '+4 save vs. magic', '+4 save vs. poison', 'Surprise bonus'],
    languages: ['Common', 'Dwarvish', 'Elvish', 'Gnomish', 'Goblin', 'Halfling', 'Orcish'],
    infravision: 60,
    multiClassOptions: [['Fighter', 'Thief']],
    description: 'Small, stout folk who love comfort but have surprising courage when needed.',
    icon: '🍀',
  },
  'Half-Orc': {
    name: 'Half-Orc',
    abilityAdjustments: { strength: 1, constitution: 1, charisma: -2 },
    abilityMinimums: { strength: 6, constitution: 13 },
    abilityMaximums: { strength: 18, dexterity: 17, constitution: 19, intelligence: 17, wisdom: 14, charisma: 12 },
    allowedClasses: ['Fighter', 'Cleric', 'Thief', 'Assassin'],
    specialAbilities: ['Infravision 60\''],
    languages: ['Common', 'Orcish'],
    infravision: 60,
    multiClassOptions: [['Fighter', 'Cleric'], ['Fighter', 'Thief'], ['Cleric', 'Thief'], ['Cleric', 'Assassin'], ['Fighter', 'Assassin']],
    description: 'Born of mixed human and orc blood, half-orcs are strong and tough but often mistrusted.',
    icon: '💀',
  },
};

// ─── Class Data (Minimal) ─────────────────────────────────────────────────────

export interface ClassRequirements {
  name: CharacterClassName;
  requirements: Partial<AbilityScores>;
  allowedRaces: Race[];
  hitDice: string;
  primeRequisites: AbilityName[];
  description: string;
}

export const CLASS_DATA: ClassRequirements[] = [
  { name: 'Fighter', requirements: { strength: 9 }, allowedRaces: ['Human', 'Dwarf', 'Elf', 'Gnome', 'Half-Elf', 'Halfling', 'Half-Orc'], hitDice: '1d10', primeRequisites: ['strength'], description: 'Masters of arms and armor, fighters are the backbone of any adventuring party.' },
  { name: 'Paladin', requirements: { strength: 12, intelligence: 9, wisdom: 13, constitution: 9, charisma: 17 }, allowedRaces: ['Human'], hitDice: '1d10', primeRequisites: ['strength', 'wisdom'], description: 'Holy warriors who follow a strict code of honor and righteousness.' },
  { name: 'Ranger', requirements: { strength: 13, intelligence: 13, wisdom: 14, constitution: 14 }, allowedRaces: ['Human', 'Half-Elf'], hitDice: '2d8 (1st level)', primeRequisites: ['strength', 'intelligence', 'wisdom'], description: 'Skilled woodsmen and trackers, at home in the wilderness.' },
  { name: 'Cleric', requirements: { wisdom: 9 }, allowedRaces: ['Human', 'Half-Elf', 'Half-Orc'], hitDice: '1d8', primeRequisites: ['wisdom'], description: 'Servants of the gods, clerics wield divine magic and turn undead.' },
  { name: 'Druid', requirements: { wisdom: 12, charisma: 15 }, allowedRaces: ['Human', 'Half-Elf'], hitDice: '1d8', primeRequisites: ['wisdom', 'charisma'], description: 'Guardians of nature who draw power from the natural world.' },
  { name: 'Magic-User', requirements: { intelligence: 9 }, allowedRaces: ['Human', 'Elf', 'Half-Elf'], hitDice: '1d4', primeRequisites: ['intelligence'], description: 'Scholars of the arcane arts who wield powerful spells.' },
  { name: 'Illusionist', requirements: { intelligence: 15, dexterity: 16 }, allowedRaces: ['Human', 'Gnome'], hitDice: '1d4', primeRequisites: ['intelligence', 'dexterity'], description: 'Specialists in illusion and phantasm magic.' },
  { name: 'Thief', requirements: { dexterity: 9 }, allowedRaces: ['Human', 'Dwarf', 'Elf', 'Gnome', 'Half-Elf', 'Halfling', 'Half-Orc'], hitDice: '1d6', primeRequisites: ['dexterity'], description: 'Skilled infiltrators who rely on stealth and cunning.' },
  { name: 'Assassin', requirements: { strength: 12, intelligence: 11, dexterity: 12 }, allowedRaces: ['Human', 'Dwarf', 'Elf', 'Gnome', 'Half-Elf', 'Half-Orc'], hitDice: '1d6', primeRequisites: ['strength', 'intelligence', 'dexterity'], description: 'Deadly killers who specialize in the art of assassination.' },
  { name: 'Monk', requirements: { strength: 15, wisdom: 15, dexterity: 15, constitution: 11 }, allowedRaces: ['Human'], hitDice: '2d4', primeRequisites: ['strength', 'wisdom', 'dexterity'], description: 'Disciplined martial artists who have mastered mind and body.' },
];

// ─── Store Types ──────────────────────────────────────────────────────────────

interface CharacterCreationState {
  step: number;
  rollingMethod: RollingMethod;
  abilityRolls: DiceRollResult[];
  assignedAbilities: AbilityScores | null;
  exceptionalStrength: ExceptionalStrength | null;
  selectedRace: Race | null;
  selectedClass: CharacterClassName | null;
  selectedAlignment: Alignment | null;
  characterName: string;
  gold: number;
  selectedEquipment: EquipmentItem[];
  selectedSpells: Spell[];
}

interface CharacterStoreState extends CharacterCreationState {
  characters: Character[];
  selectedCharacterId: string | null;

  // Creation actions
  setStep: (step: number) => void;
  setRollingMethod: (method: RollingMethod) => void;
  rollAbilities: () => void;
  setAbilityRolls: (rolls: DiceRollResult[]) => void;
  assignAbilities: (scores: AbilityScores) => void;
  setExceptionalStrength: (es: ExceptionalStrength | null) => void;
  setRace: (race: Race | null) => void;
  setClass: (cls: CharacterClassName | null) => void;
  setAlignment: (alignment: Alignment | null) => void;
  setCharacterName: (name: string) => void;
  setGold: (gold: number) => void;
  addEquipment: (item: EquipmentItem) => void;
  removeEquipment: (itemId: string) => void;
  addSpell: (spell: Spell) => void;
  removeSpell: (spellId: string) => void;
  resetCreation: () => void;
  finalizeCharacter: () => Character | null;

  // Character management
  addCharacter: (character: Character) => void;
  removeCharacter: (id: string) => void;
  updateCharacter: (id: string, updates: Partial<Character>) => void;
  selectCharacter: (id: string | null) => void;
  getSelectedCharacter: () => Character | undefined;

  // Validation helpers
  getAvailableRaces: () => Race[];
  getAvailableClasses: () => CharacterClassName[];
}

const METHOD_MAP: Record<RollingMethod, 'roll3d6' | 'roll4d6' | 'roll2d6p6' | 'roll3d6x2' | 'roll4d6arr' | 'pointbuy'> = {
  '3d6-in-order': 'roll3d6',
  '4d6-drop-lowest': 'roll4d6',
  '2d6+6': 'roll2d6p6',
  '3d6-twice-best': 'roll3d6x2',
  '4d6-arrange': 'roll4d6arr',
  'point-buy': 'pointbuy',
};

const initialCreationState: CharacterCreationState = {
  step: 0,
  rollingMethod: '4d6-drop-lowest',
  abilityRolls: [],
  assignedAbilities: null,
  exceptionalStrength: null,
  selectedRace: null,
  selectedClass: null,
  selectedAlignment: null,
  characterName: '',
  gold: 0,
  selectedEquipment: [],
  selectedSpells: [],
};

export const useCharacterStore = create<CharacterStoreState>((set, get) => ({
  ...initialCreationState,
  characters: [],
  selectedCharacterId: null,

  setStep: (step) => set({ step }),
  setRollingMethod: (method) => set({ rollingMethod: method }),

  rollAbilities: () => {
    const method = get().rollingMethod;
    const rolls = rollAllAbilities(METHOD_MAP[method]);
    const diceRolls: DiceRollResult[] = rolls.map((r) => ({
      dice: r.rolls,
      dropped: r.dropped,
      total: r.finalTotal,
      method: method,
      timestamp: Date.now(),
    }));
    set({ abilityRolls: diceRolls, assignedAbilities: null });
  },

  setAbilityRolls: (rolls) => set({ abilityRolls: rolls }),

  assignAbilities: (scores) => set({ assignedAbilities: scores }),

  setExceptionalStrength: (es) => set({ exceptionalStrength: es }),

  setRace: (race) => set({ selectedRace: race, selectedClass: null }),

  setClass: (cls) => set({ selectedClass: cls }),

  setAlignment: (alignment) => set({ selectedAlignment: alignment }),

  setCharacterName: (name) => set({ characterName: name }),

  setGold: (gold) => set({ gold }),

  addEquipment: (item) =>
    set((state) => ({
      selectedEquipment: [...state.selectedEquipment, item],
      gold: state.gold - item.cost * item.quantity,
    })),

  removeEquipment: (itemId) =>
    set((state) => {
      const item = state.selectedEquipment.find((e) => e.id === itemId);
      return {
        selectedEquipment: state.selectedEquipment.filter((e) => e.id !== itemId),
        gold: state.gold + (item ? item.cost * item.quantity : 0),
      };
    }),

  addSpell: (spell) =>
    set((state) => ({ selectedSpells: [...state.selectedSpells, spell] })),

  removeSpell: (spellId) =>
    set((state) => ({
      selectedSpells: state.selectedSpells.filter((s) => s.id !== spellId),
    })),

  resetCreation: () => set(initialCreationState),

  finalizeCharacter: () => {
    const state = get();
    if (!state.assignedAbilities || !state.selectedRace || !state.selectedClass || !state.selectedAlignment || !state.characterName) {
      return null;
    }

    const character: Character = {
      id: crypto.randomUUID(),
      name: state.characterName,
      race: state.selectedRace,
      className: state.selectedClass,
      level: 1,
      experience: 0,
      experienceNextLevel: 2000,
      alignment: state.selectedAlignment,
      abilityScores: state.assignedAbilities,
      exceptionalStrength: state.exceptionalStrength ?? undefined,
      hitPoints: 10,
      maxHitPoints: 10,
      armorClass: 10,
      thac0: 20,
      savingThrows: { paralyzation: 14, poison: 14, petrification: 13, breath: 16, spells: 15 },
      equipment: state.selectedEquipment,
      gold: state.gold,
      silver: 0,
      copper: 0,
      electrum: 0,
      platinum: 0,
      spells: state.selectedSpells,
      spellSlots: {},
      memorizedSpells: [],
      specialAbilities: RACE_DATA[state.selectedRace].specialAbilities,
      proficiencies: [],
      languages: RACE_DATA[state.selectedRace].languages,
      age: 20,
      height: '5\'10"',
      weight: '170 lbs',
      encumbrance: 0,
      maxEncumbrance: 1500,
      movementRate: 12,
      backstory: '',
      notes: '',
      conditions: [],
      isNPC: false,
      createdAt: Date.now(),
    };

    set((s) => ({
      characters: [...s.characters, character],
      ...initialCreationState,
    }));

    return character;
  },

  addCharacter: (character) =>
    set((state) => ({ characters: [...state.characters, character] })),

  removeCharacter: (id) =>
    set((state) => ({
      characters: state.characters.filter((c) => c.id !== id),
      selectedCharacterId: state.selectedCharacterId === id ? null : state.selectedCharacterId,
    })),

  updateCharacter: (id, updates) =>
    set((state) => ({
      characters: state.characters.map((c) =>
        c.id === id ? { ...c, ...updates } : c
      ),
    })),

  selectCharacter: (id) => set({ selectedCharacterId: id }),

  getSelectedCharacter: () => {
    const state = get();
    return state.characters.find((c) => c.id === state.selectedCharacterId);
  },

  getAvailableRaces: () => {
    const state = get();
    if (!state.assignedAbilities) return [];
    const scores = state.assignedAbilities;
    return (Object.keys(RACE_DATA) as Race[]).filter((race) => {
      const info = RACE_DATA[race];
      return Object.entries(info.abilityMinimums).every(
        ([ability, min]) => scores[ability as AbilityName] >= (min as number)
      );
    });
  },

  getAvailableClasses: () => {
    const state = get();
    if (!state.assignedAbilities || !state.selectedRace) return [];
    const scores = state.assignedAbilities;
    const race = state.selectedRace;

    return CLASS_DATA
      .filter((cls) => {
        const raceAllowed = cls.allowedRaces.includes(race);
        const meetsRequirements = Object.entries(cls.requirements).every(
          ([ability, min]) => scores[ability as AbilityName] >= (min as number)
        );
        return raceAllowed && meetsRequirements;
      })
      .map((cls) => cls.name);
  },
}));
