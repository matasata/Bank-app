import { create } from 'zustand';
import type {
  CombatState, CombatAction, CombatPhase, CombatActionType,
  InitiativeEntry, Character, Monster,
} from '../types';
import { rollDie } from '../utils/dice';

interface CombatStoreState {
  combat: CombatState | null;
  selectedTargetId: string | null;
  selectedActionType: CombatActionType | null;
  isAnimating: boolean;

  // Actions
  startCombat: (characters: Character[], monsters: Monster[]) => void;
  endCombat: () => void;
  rollInitiative: () => void;
  nextTurn: () => void;
  nextPhase: () => void;
  performAction: (action: Omit<CombatAction, 'id' | 'timestamp'>) => void;
  selectTarget: (targetId: string | null) => void;
  selectActionType: (type: CombatActionType | null) => void;
  resolveAttack: (attackerId: string, defenderId: string) => CombatAction;
  applyCombatDamage: (targetId: string, damage: number) => void;
  addCombatLogEntry: (entry: CombatAction) => void;
  setAnimating: (animating: boolean) => void;
  getCurrentTurnEntity: () => InitiativeEntry | null;
  isCharacterTurn: (characterId: string) => boolean;
}

export const useCombatStore = create<CombatStoreState>((set, get) => ({
  combat: null,
  selectedTargetId: null,
  selectedActionType: null,
  isAnimating: false,

  startCombat: (characters, monsters) => {
    // Check for surprise
    const partySurpriseRoll = rollDie(6);
    const monsterSurpriseRoll = rollDie(6);
    const partySurprised = partySurpriseRoll <= 2;
    const monstersSurprised = monsterSurpriseRoll <= 2;

    const combat: CombatState = {
      isActive: true,
      round: 1,
      phase: 'initiative',
      initiativeOrder: [],
      currentTurnIndex: 0,
      combatLog: [],
      participants: [...characters, ...monsters],
      surpriseState: {
        partySurprised,
        monstersSurprised,
        surpriseRounds: (partySurprised || monstersSurprised) ? 1 : 0,
      },
      environmentalEffects: [],
    };

    const logEntries: CombatAction[] = [
      {
        id: crypto.randomUUID(),
        actorId: 'system',
        actorName: 'System',
        type: 'attack',
        description: '--- COMBAT BEGINS ---',
        timestamp: Date.now(),
      },
    ];

    if (partySurprised) {
      logEntries.push({
        id: crypto.randomUUID(),
        actorId: 'system',
        actorName: 'System',
        type: 'attack',
        description: 'The party is surprised!',
        timestamp: Date.now(),
      });
    }
    if (monstersSurprised) {
      logEntries.push({
        id: crypto.randomUUID(),
        actorId: 'system',
        actorName: 'System',
        type: 'attack',
        description: 'The monsters are surprised!',
        timestamp: Date.now(),
      });
    }

    combat.combatLog = logEntries;
    set({ combat });
  },

  endCombat: () => {
    const combat = get().combat;
    if (combat) {
      const endEntry: CombatAction = {
        id: crypto.randomUUID(),
        actorId: 'system',
        actorName: 'System',
        type: 'attack',
        description: '--- COMBAT ENDS ---',
        timestamp: Date.now(),
      };
      set({
        combat: {
          ...combat,
          isActive: false,
          combatLog: [...combat.combatLog, endEntry],
        },
        selectedTargetId: null,
        selectedActionType: null,
      });
    }
  },

  rollInitiative: () => {
    const combat = get().combat;
    if (!combat) return;

    const entries: InitiativeEntry[] = combat.participants.map((p) => {
      const isCharacter = 'className' in p;
      const roll = rollDie(6); // AD&D uses d6 for initiative (lower is better)
      const dexMod = 0; // Simplified
      const weaponSpeed = 0;

      return {
        id: crypto.randomUUID(),
        entityId: p.id,
        entityName: isCharacter ? (p as Character).name : (p as Monster).name,
        entityType: isCharacter ? 'character' : 'monster',
        roll,
        dexterityModifier: dexMod,
        weaponSpeed,
        total: roll + dexMod + weaponSpeed,
        hasActed: false,
        surpriseRounds: 0,
      };
    });

    // Sort by initiative (lower is better in AD&D)
    entries.sort((a, b) => a.total - b.total);

    const logEntry: CombatAction = {
      id: crypto.randomUUID(),
      actorId: 'system',
      actorName: 'System',
      type: 'attack',
      description: `Initiative rolled! Order: ${entries.map((e) => `${e.entityName} (${e.total})`).join(', ')}`,
      timestamp: Date.now(),
    };

    set({
      combat: {
        ...combat,
        initiativeOrder: entries,
        currentTurnIndex: 0,
        phase: 'missile',
        combatLog: [...combat.combatLog, logEntry],
      },
    });
  },

  nextTurn: () => {
    const combat = get().combat;
    if (!combat) return;

    const nextIndex = combat.currentTurnIndex + 1;

    if (nextIndex >= combat.initiativeOrder.length) {
      // New round
      set({
        combat: {
          ...combat,
          round: combat.round + 1,
          currentTurnIndex: 0,
          phase: 'initiative',
          initiativeOrder: combat.initiativeOrder.map((e) => ({ ...e, hasActed: false })),
        },
      });
    } else {
      set({
        combat: {
          ...combat,
          currentTurnIndex: nextIndex,
          initiativeOrder: combat.initiativeOrder.map((e, i) =>
            i === combat.currentTurnIndex ? { ...e, hasActed: true } : e
          ),
        },
      });
    }
  },

  nextPhase: () => {
    const combat = get().combat;
    if (!combat) return;

    const phases: CombatPhase[] = ['initiative', 'movement', 'missile', 'magic', 'melee', 'resolution'];
    const currentIdx = phases.indexOf(combat.phase);
    const nextPhase = phases[(currentIdx + 1) % phases.length];

    set({ combat: { ...combat, phase: nextPhase } });
  },

  performAction: (action) => {
    const combat = get().combat;
    if (!combat) return;

    const fullAction: CombatAction = {
      ...action,
      id: crypto.randomUUID(),
      timestamp: Date.now(),
    };

    set({
      combat: {
        ...combat,
        combatLog: [...combat.combatLog, fullAction],
      },
    });
  },

  selectTarget: (targetId) => set({ selectedTargetId: targetId }),
  selectActionType: (type) => set({ selectedActionType: type }),

  resolveAttack: (attackerId, defenderId) => {
    const combat = get().combat;
    if (!combat) {
      return {
        id: crypto.randomUUID(),
        actorId: attackerId,
        actorName: 'Unknown',
        type: 'attack' as CombatActionType,
        description: 'No active combat',
        timestamp: Date.now(),
      };
    }

    const attacker = combat.participants.find((p) => p.id === attackerId);
    const defender = combat.participants.find((p) => p.id === defenderId);
    if (!attacker || !defender) {
      return {
        id: crypto.randomUUID(),
        actorId: attackerId,
        actorName: 'Unknown',
        type: 'attack',
        description: 'Invalid attacker or defender',
        timestamp: Date.now(),
      };
    }

    const attackerName = 'className' in attacker ? (attacker as Character).name : (attacker as Monster).name;
    const defenderName = 'className' in defender ? (defender as Character).name : (defender as Monster).name;
    const thac0 = attacker.thac0;
    const defenderAC = attacker.armorClass;
    const attackRoll = rollDie(20);
    const needed = thac0 - defenderAC;
    const isHit = attackRoll >= needed;
    const isCritical = attackRoll === 20;
    const isFumble = attackRoll === 1;

    let damageRoll = 0;
    let hitResult: 'hit' | 'miss' | 'critical' | 'fumble' = 'miss';

    if (isFumble) {
      hitResult = 'fumble';
    } else if (isCritical || isHit) {
      hitResult = isCritical ? 'critical' : 'hit';
      damageRoll = rollDie(8) + (isCritical ? rollDie(8) : 0);
    }

    let description = '';
    switch (hitResult) {
      case 'critical':
        description = `${attackerName} scores a CRITICAL HIT on ${defenderName}! (Roll: ${attackRoll}, needed ${needed}) Damage: ${damageRoll}`;
        break;
      case 'hit':
        description = `${attackerName} hits ${defenderName}! (Roll: ${attackRoll}, needed ${needed}) Damage: ${damageRoll}`;
        break;
      case 'fumble':
        description = `${attackerName} FUMBLES! (Roll: ${attackRoll})`;
        break;
      case 'miss':
        description = `${attackerName} misses ${defenderName}. (Roll: ${attackRoll}, needed ${needed})`;
        break;
    }

    const action: CombatAction = {
      id: crypto.randomUUID(),
      actorId: attackerId,
      actorName: attackerName,
      type: 'attack',
      targetId: defenderId,
      targetName: defenderName,
      attackRoll,
      damageRoll: hitResult === 'hit' || hitResult === 'critical' ? damageRoll : undefined,
      hitResult,
      description,
      timestamp: Date.now(),
    };

    // Apply damage
    if (damageRoll > 0) {
      get().applyCombatDamage(defenderId, damageRoll);
    }

    set({
      combat: {
        ...get().combat!,
        combatLog: [...get().combat!.combatLog, action],
      },
    });

    return action;
  },

  applyCombatDamage: (targetId, damage) => {
    const combat = get().combat;
    if (!combat) return;

    const updatedParticipants = combat.participants.map((p) => {
      if (p.id !== targetId) return p;
      const newHP = Math.max(0, p.hitPoints - damage);
      const updated = { ...p, hitPoints: newHP };

      if (newHP <= 0) {
        const name = 'className' in p ? (p as Character).name : (p as Monster).name;
        const deathEntry: CombatAction = {
          id: crypto.randomUUID(),
          actorId: 'system',
          actorName: 'System',
          type: 'attack',
          description: `${name} has fallen!`,
          timestamp: Date.now(),
        };
        set({
          combat: {
            ...get().combat!,
            combatLog: [...get().combat!.combatLog, deathEntry],
          },
        });
      }

      return updated;
    });

    set({
      combat: { ...get().combat!, participants: updatedParticipants },
    });
  },

  addCombatLogEntry: (entry) => {
    const combat = get().combat;
    if (!combat) return;
    set({ combat: { ...combat, combatLog: [...combat.combatLog, entry] } });
  },

  setAnimating: (animating) => set({ isAnimating: animating }),

  getCurrentTurnEntity: () => {
    const combat = get().combat;
    if (!combat || combat.initiativeOrder.length === 0) return null;
    return combat.initiativeOrder[combat.currentTurnIndex] || null;
  },

  isCharacterTurn: (characterId) => {
    const current = get().getCurrentTurnEntity();
    return current?.entityId === characterId;
  },
}));
