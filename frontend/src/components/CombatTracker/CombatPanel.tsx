import React, { useState } from 'react';
import { useCombatStore } from '../../stores/combatStore';
import { useCharacterStore } from '../../stores/characterStore';
import { useGameStore } from '../../stores/gameStore';
import Panel from '../UI/Panel';
import InitiativeTracker from './InitiativeTracker';
import CombatLog from './CombatLog';
import type { CombatActionType, Monster, Character } from '../../types';

const ACTION_BUTTONS: { type: CombatActionType; label: string; icon: string; color: string }[] = [
  { type: 'attack', label: 'Attack', icon: '⚔️', color: 'bg-red-900/30 border-red-400/30 text-red-400 hover:bg-red-900/50' },
  { type: 'cast-spell', label: 'Cast Spell', icon: '✨', color: 'bg-purple-900/30 border-purple-400/30 text-purple-400 hover:bg-purple-900/50' },
  { type: 'use-item', label: 'Use Item', icon: '🧪', color: 'bg-blue-900/30 border-blue-400/30 text-blue-400 hover:bg-blue-900/50' },
  { type: 'move', label: 'Move', icon: '👣', color: 'bg-green-900/30 border-green-400/30 text-green-400 hover:bg-green-900/50' },
  { type: 'turn-undead', label: 'Turn Undead', icon: '✝️', color: 'bg-gold/20 border-gold/30 text-gold hover:bg-gold/30' },
  { type: 'parry', label: 'Parry', icon: '🛡️', color: 'bg-darkWood/40 border-gold/20 text-parchment/60 hover:bg-darkWood/60' },
  { type: 'charge', label: 'Charge', icon: '🐎', color: 'bg-orange-900/30 border-orange-400/30 text-orange-400 hover:bg-orange-900/50' },
  { type: 'flee', label: 'Flee', icon: '🏃', color: 'bg-gray-900/30 border-gray-400/30 text-gray-400 hover:bg-gray-900/50' },
  { type: 'delay', label: 'Delay', icon: '⏳', color: 'bg-inkBlack/30 border-parchment/20 text-parchment/40 hover:bg-inkBlack/50' },
];

// Sample monsters for testing
const SAMPLE_MONSTERS: Monster[] = [
  {
    id: 'goblin-1', name: 'Goblin', hitDice: '1d8-1', hitPoints: 5, maxHitPoints: 5,
    armorClass: 6, thac0: 19, numberOfAttacks: 1, damage: '1d6', movement: 6,
    specialAbilities: [], morale: 7, treasureType: 'K', experience: 15,
    alignment: 'Lawful Evil', isHostile: true, conditions: [],
  },
  {
    id: 'goblin-2', name: 'Goblin Chieftain', hitDice: '2d8', hitPoints: 11, maxHitPoints: 11,
    armorClass: 5, thac0: 18, numberOfAttacks: 1, damage: '1d8', movement: 6,
    specialAbilities: [], morale: 9, treasureType: 'K', experience: 35,
    alignment: 'Lawful Evil', isHostile: true, conditions: [],
  },
  {
    id: 'skeleton-1', name: 'Skeleton', hitDice: '1d8', hitPoints: 6, maxHitPoints: 6,
    armorClass: 7, thac0: 19, numberOfAttacks: 1, damage: '1d6', movement: 12,
    specialAbilities: ['Undead', 'Immune to sleep and charm'], morale: 12, treasureType: '-',
    experience: 14, alignment: 'Neutral Evil', isHostile: true, conditions: [],
  },
];

export const CombatPanel: React.FC = () => {
  const {
    combat, selectedTargetId, selectedActionType,
    startCombat, endCombat, rollInitiative, nextTurn,
    selectTarget, selectActionType, resolveAttack,
    getCurrentTurnEntity,
  } = useCombatStore();
  const { characters } = useCharacterStore();
  const { addLogEntry } = useGameStore();

  const [showStartDialog, setShowStartDialog] = useState(false);
  const [selectedMonsters, setSelectedMonsters] = useState<string[]>([]);

  const currentTurn = getCurrentTurnEntity();
  const isPlayerTurn = currentTurn?.entityType === 'character';

  const handleStartCombat = () => {
    const monsters = SAMPLE_MONSTERS.filter((m) => selectedMonsters.includes(m.id));
    if (characters.length === 0 || monsters.length === 0) return;

    startCombat(characters, monsters);
    setShowStartDialog(false);
    addLogEntry({ type: 'combat', message: 'Combat has begun!' });
  };

  const handleAction = () => {
    if (!selectedActionType || !currentTurn) return;

    if (selectedActionType === 'attack' && selectedTargetId) {
      resolveAttack(currentTurn.entityId, selectedTargetId);
      nextTurn();
    } else if (selectedActionType === 'flee') {
      const success = Math.random() > 0.5;
      addLogEntry({
        type: 'combat',
        message: success
          ? `${currentTurn.entityName} flees from combat!`
          : `${currentTurn.entityName} fails to disengage!`,
      });
      nextTurn();
    } else if (selectedActionType === 'delay') {
      addLogEntry({ type: 'combat', message: `${currentTurn.entityName} delays their action.` });
      nextTurn();
    } else if (selectedActionType === 'parry') {
      addLogEntry({ type: 'combat', message: `${currentTurn.entityName} takes a defensive stance.` });
      nextTurn();
    } else {
      addLogEntry({ type: 'combat', message: `${currentTurn.entityName} uses ${selectedActionType}.` });
      nextTurn();
    }

    selectTarget(null);
    selectActionType(null);
  };

  // Auto-advance for monster turns
  React.useEffect(() => {
    if (!combat?.isActive || !currentTurn || currentTurn.entityType === 'character') return;

    const timer = setTimeout(() => {
      // Find a random player character to attack
      const targets = combat.participants.filter(
        (p) => 'className' in p && p.hitPoints > 0
      );
      if (targets.length > 0) {
        const target = targets[Math.floor(Math.random() * targets.length)];
        resolveAttack(currentTurn.entityId, target.id);
      }
      nextTurn();
    }, 1500);

    return () => clearTimeout(timer);
  }, [currentTurn?.entityId, combat?.currentTurnIndex]);

  return (
    <div className="h-full flex flex-col">
      {/* Top Controls */}
      <div className="p-3 border-b border-gold/20">
        {!combat?.isActive ? (
          <div className="flex gap-2">
            <button
              onClick={() => setShowStartDialog(true)}
              className="btn-primary flex-1"
              disabled={characters.length === 0}
            >
              Start Combat
            </button>
          </div>
        ) : (
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {combat.initiativeOrder.length === 0 && (
                <button onClick={rollInitiative} className="btn-primary text-xs px-3 py-1.5">
                  Roll Initiative
                </button>
              )}
            </div>
            <button
              onClick={() => {
                endCombat();
                addLogEntry({ type: 'combat', message: 'Combat has ended.' });
              }}
              className="px-3 py-1.5 text-xs font-display bg-red-900/30 text-red-400 border border-red-400/30 rounded hover:bg-red-900/50"
            >
              End Combat
            </button>
          </div>
        )}
      </div>

      {/* Start Combat Dialog */}
      {showStartDialog && (
        <div className="p-4 border-b border-gold/20 bg-inkBlack/50 space-y-3">
          <h3 className="font-display text-sm text-gold uppercase tracking-wider">Select Enemies</h3>
          <div className="space-y-1">
            {SAMPLE_MONSTERS.map((monster) => (
              <label
                key={monster.id}
                className={`
                  flex items-center gap-2 p-2 rounded cursor-pointer transition-colors
                  ${selectedMonsters.includes(monster.id)
                    ? 'bg-red-900/20 border border-red-400/30'
                    : 'bg-darkWood/20 border border-transparent hover:border-gold/20'
                  }
                `}
              >
                <input
                  type="checkbox"
                  checked={selectedMonsters.includes(monster.id)}
                  onChange={(e) => {
                    setSelectedMonsters(e.target.checked
                      ? [...selectedMonsters, monster.id]
                      : selectedMonsters.filter((id) => id !== monster.id)
                    );
                  }}
                  className="accent-gold"
                />
                <span className="text-sm text-parchment">{monster.name}</span>
                <span className="text-[10px] text-parchment/40 ml-auto">
                  HD: {monster.hitDice} | AC: {monster.armorClass} | HP: {monster.hitPoints}
                </span>
              </label>
            ))}
          </div>
          <div className="flex gap-2">
            <button onClick={handleStartCombat} className="btn-primary flex-1 text-xs" disabled={selectedMonsters.length === 0}>
              Begin Combat
            </button>
            <button onClick={() => setShowStartDialog(false)} className="btn-secondary text-xs">
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto">
        {/* Initiative Tracker */}
        <Panel title="Initiative Order" variant="dark" className="m-3">
          <InitiativeTracker />
        </Panel>

        {/* Action Buttons (visible during player turn) */}
        {combat?.isActive && isPlayerTurn && combat.initiativeOrder.length > 0 && (
          <div className="px-3 space-y-3">
            <h3 className="font-display text-xs text-gold/70 uppercase tracking-wider">
              {currentTurn?.entityName}'s Turn - Choose Action
            </h3>

            {/* Action type selection */}
            <div className="grid grid-cols-3 gap-1">
              {ACTION_BUTTONS.map(({ type, label, icon, color }) => (
                <button
                  key={type}
                  onClick={() => selectActionType(type)}
                  className={`
                    flex items-center gap-1.5 px-2 py-2 rounded text-xs font-display border transition-all
                    ${selectedActionType === type
                      ? 'ring-2 ring-gold shadow-gold-glow'
                      : ''
                    }
                    ${color}
                  `}
                >
                  <span>{icon}</span>
                  <span>{label}</span>
                </button>
              ))}
            </div>

            {/* Target selection */}
            {selectedActionType === 'attack' && (
              <div className="space-y-1">
                <h4 className="text-[10px] font-display uppercase text-parchment/40">Select Target</h4>
                {combat.participants
                  .filter((p) => {
                    const isMonster = !('className' in p);
                    return isMonster && p.hitPoints > 0;
                  })
                  .map((target) => {
                    const monster = target as Monster;
                    const isSelected = selectedTargetId === monster.id;
                    return (
                      <button
                        key={monster.id}
                        onClick={() => selectTarget(monster.id)}
                        className={`
                          w-full flex items-center justify-between px-3 py-2 rounded text-xs transition-all
                          ${isSelected
                            ? 'bg-red-900/30 border border-red-400/50 text-red-400'
                            : 'bg-darkWood/20 border border-transparent text-parchment/60 hover:border-red-400/30'
                          }
                        `}
                      >
                        <span>{monster.name}</span>
                        <span className="text-[10px]">
                          HP: {monster.hitPoints}/{monster.maxHitPoints} | AC: {monster.armorClass}
                        </span>
                      </button>
                    );
                  })}
              </div>
            )}

            {/* Confirm action */}
            {selectedActionType && (
              <button
                onClick={handleAction}
                disabled={selectedActionType === 'attack' && !selectedTargetId}
                className="w-full btn-primary disabled:opacity-30 disabled:cursor-not-allowed"
              >
                {selectedActionType === 'attack'
                  ? selectedTargetId
                    ? `Attack ${combat.participants.find((p) => p.id === selectedTargetId)?.name || 'target'}`
                    : 'Select a target'
                  : `Confirm ${selectedActionType}`
                }
              </button>
            )}
          </div>
        )}

        {/* Combat Log */}
        <Panel title="Combat Log" variant="dark" className="m-3">
          <CombatLog />
        </Panel>
      </div>
    </div>
  );
};

export default CombatPanel;
