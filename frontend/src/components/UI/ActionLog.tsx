import React, { useRef, useEffect } from 'react';
import { useGameStore } from '../../stores/gameStore';
import type { GameLogEntry } from '../../types';

interface ActionLogProps {
  maxHeight?: string;
  showTimestamp?: boolean;
}

const typeStyles: Record<GameLogEntry['type'], { color: string; icon: string }> = {
  system: { color: 'text-parchment/60', icon: '⚙' },
  combat: { color: 'text-red-400', icon: '⚔' },
  exploration: { color: 'text-green-400', icon: '🗺' },
  dialogue: { color: 'text-blue-400', icon: '💬' },
  loot: { color: 'text-gold', icon: '💰' },
  dice: { color: 'text-purple-400', icon: '🎲' },
  error: { color: 'text-red-500', icon: '⚠' },
};

export const ActionLog: React.FC<ActionLogProps> = ({
  maxHeight = '100%',
  showTimestamp = false,
}) => {
  const { actionLog, clearLog } = useGameStore();
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [actionLog.length]);

  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    });
  };

  return (
    <div className="flex flex-col h-full" style={{ maxHeight }}>
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-gold/20">
        <span className="font-display text-xs font-semibold tracking-wider uppercase text-gold/70">
          Action Log
        </span>
        <button
          onClick={clearLog}
          className="text-xs text-parchment/40 hover:text-parchment/70 transition-colors font-body"
          title="Clear log"
        >
          Clear
        </button>
      </div>

      {/* Log entries */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-3 py-2 space-y-1"
      >
        {actionLog.length === 0 ? (
          <p className="text-parchment/30 text-sm font-body italic text-center py-4">
            No actions yet. Begin your adventure...
          </p>
        ) : (
          actionLog.map((entry) => {
            const style = typeStyles[entry.type];
            return (
              <div
                key={entry.id}
                className="animate-slide-up flex items-start gap-2 text-sm font-body"
              >
                <span className="flex-shrink-0 w-4 text-center" title={entry.type}>
                  {style.icon}
                </span>
                {showTimestamp && (
                  <span className="flex-shrink-0 text-xs text-parchment/30 font-mono pt-0.5">
                    {formatTime(entry.timestamp)}
                  </span>
                )}
                <span className={style.color}>{entry.message}</span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default ActionLog;
