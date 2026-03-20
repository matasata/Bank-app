import { create } from 'zustand';
import type {
  AppView, GameSession, GameSettings, GameLogEntry,
  SaveSlot, Party, MarchingOrder, PanelLayout,
} from '../types';

interface GameStoreState {
  // View management
  currentView: AppView;
  setView: (view: AppView) => void;

  // Panel layout
  panelLayout: PanelLayout;
  setPanelLayout: (layout: Partial<PanelLayout>) => void;

  // Game session
  session: GameSession | null;
  createSession: (name: string) => void;

  // Settings
  settings: GameSettings;
  updateSettings: (updates: Partial<GameSettings>) => void;
  resetSettings: () => void;

  // Action log
  actionLog: GameLogEntry[];
  addLogEntry: (entry: Omit<GameLogEntry, 'id' | 'timestamp'>) => void;
  clearLog: () => void;

  // Save/Load
  saveSlots: SaveSlot[];
  saveGame: (slotNumber: number) => void;
  loadGame: (slotId: string) => void;
  deleteSave: (slotId: string) => void;
  setSaveSlots: (slots: SaveSlot[]) => void;

  // Party (quick access)
  party: Party | null;
  setParty: (party: Party) => void;
  updateMarchingOrder: (order: MarchingOrder) => void;

  // Misc
  isLoading: boolean;
  setLoading: (loading: boolean) => void;
  error: string | null;
  setError: (error: string | null) => void;
}

const defaultSettings: GameSettings = {
  criticalHitsEnabled: true,
  criticalFumbleEnabled: true,
  encumbranceRulesEnabled: true,
  speedFactorInitiativeEnabled: false,
  autoRollMonsterHD: true,
  showDamageNumbers: true,
  darkMode: true,
  soundEffectsEnabled: true,
  animationsEnabled: true,
  fontSize: 'medium',
  autoSaveEnabled: true,
  autoSaveInterval: 5,
};

const defaultLayout: PanelLayout = {
  leftWidth: 60,
  rightWidth: 40,
  bottomHeight: 25,
};

export const useGameStore = create<GameStoreState>((set, get) => ({
  currentView: 'character-creation',
  panelLayout: defaultLayout,
  session: null,
  settings: defaultSettings,
  actionLog: [],
  saveSlots: [],
  party: null,
  isLoading: false,
  error: null,

  setView: (view) => set({ currentView: view }),

  setPanelLayout: (layout) =>
    set((state) => ({
      panelLayout: { ...state.panelLayout, ...layout },
    })),

  createSession: (name) => {
    const session: GameSession = {
      id: crypto.randomUUID(),
      name,
      party: {
        id: crypto.randomUUID(),
        name: 'Adventuring Party',
        members: [],
        marchingOrder: { front: [], middle: [], rear: [] },
        partyGold: 0,
        sharedInventory: [],
        callerCharacterId: '',
        mapperCharacterId: '',
      },
      settings: get().settings,
      actionLog: [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
      playTimeSeconds: 0,
    };
    set({ session, party: session.party });
    get().addLogEntry({
      type: 'system',
      message: `Game session "${name}" created.`,
    });
  },

  updateSettings: (updates) =>
    set((state) => ({
      settings: { ...state.settings, ...updates },
    })),

  resetSettings: () => set({ settings: defaultSettings }),

  addLogEntry: (entry) => {
    const fullEntry: GameLogEntry = {
      ...entry,
      id: crypto.randomUUID(),
      timestamp: Date.now(),
    };
    set((state) => ({
      actionLog: [...state.actionLog, fullEntry],
    }));
  },

  clearLog: () => set({ actionLog: [] }),

  saveGame: (slotNumber) => {
    const state = get();
    if (!state.session) return;

    const slot: SaveSlot = {
      id: crypto.randomUUID(),
      slotNumber,
      sessionName: state.session.name,
      partyName: state.party?.name || 'Unknown Party',
      partyLevel: state.party?.members.length
        ? `Avg Lvl ${Math.round(state.party.members.reduce((s, m) => s + m.level, 0) / state.party.members.length)}`
        : 'No members',
      dungeonName: state.session.currentDungeon?.name,
      timestamp: Date.now(),
      playTime: formatPlayTime(state.session.playTimeSeconds),
    };

    set((s) => ({
      saveSlots: [
        ...s.saveSlots.filter((ss) => ss.slotNumber !== slotNumber),
        slot,
      ],
    }));

    get().addLogEntry({
      type: 'system',
      message: `Game saved to slot ${slotNumber}.`,
    });
  },

  loadGame: (_slotId) => {
    get().addLogEntry({
      type: 'system',
      message: 'Game loaded.',
    });
  },

  deleteSave: (slotId) =>
    set((s) => ({
      saveSlots: s.saveSlots.filter((ss) => ss.id !== slotId),
    })),

  setSaveSlots: (slots) => set({ saveSlots: slots }),

  setParty: (party) => set({ party }),

  updateMarchingOrder: (order) => {
    const party = get().party;
    if (!party) return;
    set({ party: { ...party, marchingOrder: order } });
  },

  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
}));

function formatPlayTime(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return `${hours}h ${minutes}m`;
}
