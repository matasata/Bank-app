import React, { useRef, useEffect } from 'react';
import { useCombatStore } from '../../stores/combatStore';
import type { CombatAction } from '../../types';

const getActionColor = (action: CombatAction): string => {
  if (action.actorId === 'system') return 'text-parchment/50';
  switch (action.hitResult) {
    case 'critical': return 'text-yellow-400';
    case 'hit': return 'text-green-400';
    case 'miss': return 'text-parchment/40';
    case 'fumble': return 'text-red-500';
    default: return 'text-parchment/60';
  }
};

const getActionIcon = (action: CombatAction): string => {
  if (action.actorId === 'system') return '---';
  switch (action.type) {
    case 'attack': return '⚔️';
    case 'cast-spell': return '✨';
    case 'use-item': return '🧪';
    case 'move': return '👣';
    case 'turn-undead': return '✝️';
    case 'flee': return '🏃';
    case 'parry': return '🛡️';
    case 'charge': return '🐎';
    default: return '▸';
  }
};

export const CombatLog: React.FC = () => {
  const { combat } = useCombatStore();
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [combat?.combatLog.length]);

  if (!combat) {
    return (
      <div className="p-3 text-center text-parchment/30 text-sm italic">
        No combat log.
      </div>
    );
  }

  return (
    <div ref={scrollRef} className="overflow-y-auto max-h-64 p-3 space-y-1">
      {combat.combatLog.map((action) => {
        const isSystem = action.actorId === 'system';
        const color = getActionColor(action);
        const icon = getActionIcon(action);

        return (
          <div
            key={action.id}
            className={`
              text-xs font-body animate-slide-up
              ${isSystem ? 'text-center py-1' : 'flex items-start gap-2'}
            `}
          >
            {isSystem ? (
              <span className="text-parchment/30 font-display text-[10px] tracking-widest uppercase">
                {action.description}
              </span>
            ) : (
              <>
                <span className="flex-shrink-0 w-5 text-center">{icon}</span>
                <div className="flex-1">
                  <span className={color}>{action.description}</span>

                  {/* Detailed roll breakdown */}
                  {action.attackRoll !== undefined && (
                    <div className="mt-0.5 flex items-center gap-2">
                      <span className="dice-result !w-6 !h-6 !text-[10px]">
                        {action.attackRoll}
                      </span>
                      {action.hitResult === 'critical' && (
                        <span className="text-[10px] px-1 py-0.5 rounded bg-yellow-900/30 text-yellow-400 font-display uppercase animate-glow-pulse">
                          Critical!
                        </span>
                      )}
                      {action.hitResult === 'fumble' && (
                        <span className="text-[10px] px-1 py-0.5 rounded bg-red-900/30 text-red-400 font-display uppercase">
                          Fumble!
                        </span>
                      )}
                      {action.damageRoll !== undefined && (
                        <span className="text-[10px] text-red-400">
                          DMG: {action.damageRoll}
                        </span>
                      )}
                    </div>
                  )}
                </div>
                <span className="flex-shrink-0 text-[9px] text-parchment/20 font-mono">
                  {new Date(action.timestamp).toLocaleTimeString('en-US', {
                    hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false,
                  })}
                </span>
              </>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default CombatLog;
