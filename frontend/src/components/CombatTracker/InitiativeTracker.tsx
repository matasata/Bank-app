import React from 'react';
import { useCombatStore } from '../../stores/combatStore';
import type { Character, Monster } from '../../types';

export const InitiativeTracker: React.FC = () => {
  const { combat } = useCombatStore();

  if (!combat || !combat.isActive) {
    return (
      <div className="p-4 text-center">
        <p className="text-parchment/30 font-body italic text-sm">
          No active combat encounter.
        </p>
      </div>
    );
  }

  const { initiativeOrder, currentTurnIndex, round, phase } = combat;

  return (
    <div className="space-y-3">
      {/* Round and Phase Info */}
      <div className="flex items-center justify-between px-3 py-2 bg-inkBlack/40 rounded">
        <div className="flex items-center gap-3">
          <span className="font-display text-xs text-gold uppercase tracking-wider">
            Round {round}
          </span>
          <span className="text-[10px] px-2 py-0.5 rounded bg-burgundy/30 text-parchment/60 font-display uppercase">
            {phase}
          </span>
        </div>
        {combat.surpriseState.surpriseRounds > 0 && (
          <span className="text-[10px] text-red-400 font-display uppercase animate-glow-pulse">
            Surprise Round!
          </span>
        )}
      </div>

      {/* Initiative List */}
      <div className="space-y-1">
        {initiativeOrder.length === 0 ? (
          <p className="text-center text-parchment/30 text-xs italic py-2">
            Roll initiative to begin.
          </p>
        ) : (
          initiativeOrder.map((entry, index) => {
            const isCurrentTurn = index === currentTurnIndex;
            const participant = combat.participants.find((p) => p.id === entry.entityId);
            const isCharacter = entry.entityType === 'character';
            const hp = participant?.hitPoints ?? 0;
            const maxHp = participant?.maxHitPoints ?? 1;
            const hpPercent = (hp / maxHp) * 100;
            const isDead = hp <= 0;

            return (
              <div
                key={entry.id}
                className={`
                  flex items-center gap-3 px-3 py-2 rounded-lg border transition-all duration-300
                  ${isCurrentTurn
                    ? 'combat-highlight bg-burgundy/20 border-gold'
                    : entry.hasActed
                      ? 'bg-inkBlack/20 border-parchment/5 opacity-50'
                      : 'bg-darkWood/20 border-gold/10'
                  }
                  ${isDead ? 'opacity-30 line-through' : ''}
                `}
              >
                {/* Turn Indicator */}
                <div className={`
                  w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-display font-bold flex-shrink-0
                  ${isCurrentTurn
                    ? 'bg-gold text-darkWood animate-glow-pulse'
                    : 'bg-darkWood/50 text-parchment/40'
                  }
                `}>
                  {entry.total}
                </div>

                {/* Entity Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className={`
                      text-sm font-display font-semibold truncate
                      ${isCharacter ? 'text-parchment' : 'text-red-400'}
                    `}>
                      {entry.entityName}
                    </span>
                    {isCurrentTurn && (
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-gold/20 text-gold font-display uppercase animate-pulse">
                        Active
                      </span>
                    )}
                    {isDead && (
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-red-900/30 text-red-400 font-display uppercase">
                        Dead
                      </span>
                    )}
                  </div>

                  {/* HP Bar */}
                  <div className="flex items-center gap-2 mt-1">
                    <div className="flex-1 h-1.5 bg-inkBlack/40 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          hpPercent > 50 ? 'bg-forestGreen' :
                          hpPercent > 25 ? 'bg-yellow-600' :
                          'bg-red-600'
                        }`}
                        style={{ width: `${hpPercent}%` }}
                      />
                    </div>
                    <span className="text-[10px] text-parchment/40 font-mono whitespace-nowrap">
                      {hp}/{maxHp}
                    </span>
                  </div>
                </div>

                {/* Type Badge */}
                <div className={`
                  text-[9px] px-1.5 py-0.5 rounded flex-shrink-0 font-display uppercase
                  ${isCharacter
                    ? 'bg-forestGreen/20 text-green-400/70'
                    : 'bg-red-900/20 text-red-400/70'
                  }
                `}>
                  {isCharacter ? 'PC' : 'MON'}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default InitiativeTracker;
