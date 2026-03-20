import React, { useState, useCallback } from 'react';
import { parseDiceNotation, rollDie, type DiceResult } from '../../utils/dice';

interface DiceRollerProps {
  onRoll?: (result: DiceResult) => void;
  compact?: boolean;
}

interface AnimatedDie {
  id: number;
  faces: number;
  currentValue: number;
  finalValue: number;
  isRolling: boolean;
  color: string;
}

const DICE_TYPES = [
  { faces: 4, label: 'd4', color: 'from-red-700 to-red-900' },
  { faces: 6, label: 'd6', color: 'from-blue-700 to-blue-900' },
  { faces: 8, label: 'd8', color: 'from-green-700 to-green-900' },
  { faces: 10, label: 'd10', color: 'from-purple-700 to-purple-900' },
  { faces: 12, label: 'd12', color: 'from-yellow-700 to-yellow-900' },
  { faces: 20, label: 'd20', color: 'from-red-600 to-red-800' },
  { faces: 100, label: 'd%', color: 'from-gray-600 to-gray-800' },
];

export const DiceRoller: React.FC<DiceRollerProps> = ({ onRoll, compact = false }) => {
  const [animatedDice, setAnimatedDice] = useState<AnimatedDie[]>([]);
  const [customNotation, setCustomNotation] = useState('');
  const [lastResult, setLastResult] = useState<DiceResult | null>(null);
  const [isRolling, setIsRolling] = useState(false);

  const animateDieRoll = useCallback(
    (faces: number, finalValue: number, id: number, color: string) => {
      return new Promise<void>((resolve) => {
        const die: AnimatedDie = {
          id,
          faces,
          currentValue: 1,
          finalValue,
          isRolling: true,
          color,
        };

        setAnimatedDice((prev) => [...prev, die]);

        let frame = 0;
        const totalFrames = 12;
        const interval = setInterval(() => {
          frame++;
          if (frame >= totalFrames) {
            clearInterval(interval);
            setAnimatedDice((prev) =>
              prev.map((d) =>
                d.id === id
                  ? { ...d, currentValue: finalValue, isRolling: false }
                  : d
              )
            );
            resolve();
          } else {
            setAnimatedDice((prev) =>
              prev.map((d) =>
                d.id === id
                  ? { ...d, currentValue: rollDie(faces) }
                  : d
              )
            );
          }
        }, 60);
      });
    },
    []
  );

  const rollSingleDie = useCallback(
    async (faces: number) => {
      setIsRolling(true);
      setAnimatedDice([]);
      const finalValue = rollDie(faces);
      const color = DICE_TYPES.find((d) => d.faces === faces)?.color || 'from-gray-600 to-gray-800';

      await animateDieRoll(faces, finalValue, Date.now(), color);

      const result: DiceResult = {
        faces,
        rolls: [finalValue],
        dropped: [],
        kept: [finalValue],
        total: finalValue,
        modifier: 0,
        finalTotal: finalValue,
      };
      setLastResult(result);
      onRoll?.(result);
      setIsRolling(false);
    },
    [animateDieRoll, onRoll]
  );

  const rollCustom = useCallback(async () => {
    if (!customNotation.trim()) return;
    setIsRolling(true);
    setAnimatedDice([]);

    const result = parseDiceNotation(customNotation.trim());
    const color = 'from-amber-700 to-amber-900';

    const promises = result.rolls.map((val, i) =>
      animateDieRoll(result.faces, val, Date.now() + i, color)
    );
    await Promise.all(promises);

    setLastResult(result);
    onRoll?.(result);
    setIsRolling(false);
  }, [customNotation, animateDieRoll, onRoll]);

  if (compact) {
    return (
      <div className="flex items-center gap-1">
        {DICE_TYPES.slice(0, 6).map((die) => (
          <button
            key={die.faces}
            onClick={() => rollSingleDie(die.faces)}
            disabled={isRolling}
            className={`
              w-8 h-8 rounded text-xs font-display font-bold text-white
              bg-gradient-to-br ${die.color}
              border border-gold/40 shadow-md
              hover:shadow-gold-glow hover:scale-110
              active:scale-95 transition-all duration-150
              disabled:opacity-50
            `}
            title={`Roll ${die.label}`}
          >
            {die.label}
          </button>
        ))}
        {lastResult && (
          <span className="ml-2 font-display font-bold text-gold text-sm">
            = {lastResult.finalTotal}
          </span>
        )}
      </div>
    );
  }

  return (
    <div className="p-4">
      {/* Dice buttons */}
      <div className="flex flex-wrap gap-2 mb-4">
        {DICE_TYPES.map((die) => (
          <button
            key={die.faces}
            onClick={() => rollSingleDie(die.faces)}
            disabled={isRolling}
            className={`
              relative w-14 h-14 rounded-lg font-display font-bold text-white text-sm
              bg-gradient-to-br ${die.color}
              border-2 border-gold/40 shadow-lg
              hover:shadow-gold-glow hover:scale-110 hover:border-gold/70
              active:scale-95 transition-all duration-200
              disabled:opacity-50 disabled:cursor-not-allowed
            `}
          >
            <div className="absolute inset-0 rounded-lg bg-white/5" />
            <span className="relative z-10">{die.label}</span>
          </button>
        ))}
      </div>

      {/* Custom notation input */}
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={customNotation}
          onChange={(e) => setCustomNotation(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && rollCustom()}
          placeholder="e.g., 3d6+2"
          className="
            flex-1 px-3 py-2 rounded
            bg-inkBlack/50 text-parchment border border-gold/30
            font-body text-sm placeholder-parchment/30
            focus:outline-none focus:border-gold/60 focus:ring-1 focus:ring-gold/30
          "
        />
        <button
          onClick={rollCustom}
          disabled={isRolling || !customNotation.trim()}
          className="btn-primary disabled:opacity-50"
        >
          Roll
        </button>
      </div>

      {/* Animated dice display */}
      {animatedDice.length > 0 && (
        <div className="flex flex-wrap gap-3 justify-center mb-4">
          {animatedDice.map((die) => (
            <div
              key={die.id}
              className={`
                relative w-16 h-16 rounded-lg flex items-center justify-center
                bg-gradient-to-br ${die.color}
                border-2 shadow-lg text-white font-display font-bold text-xl
                ${die.isRolling
                  ? 'animate-dice-roll border-white/50'
                  : 'animate-dice-bounce border-gold shadow-gold-glow'
                }
              `}
            >
              {/* Die face decoration */}
              <div className="absolute inset-1 rounded border border-white/10" />
              <span className="relative z-10 text-shadow-dark">
                {die.currentValue}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Result display */}
      {lastResult && !isRolling && (
        <div className="text-center animate-fade-in">
          <div className="flex items-center justify-center gap-2 flex-wrap mb-2">
            {lastResult.rolls.map((roll, i) => (
              <span
                key={i}
                className={`
                  dice-result
                  ${lastResult.dropped.includes(roll) ? 'opacity-40 line-through' : ''}
                `}
              >
                {roll}
              </span>
            ))}
            {lastResult.modifier !== 0 && (
              <span className="text-gold font-display font-bold">
                {lastResult.modifier > 0 ? '+' : ''}{lastResult.modifier}
              </span>
            )}
          </div>
          <div className="text-2xl font-display font-bold text-gold text-shadow-glow">
            Total: {lastResult.finalTotal}
          </div>
        </div>
      )}
    </div>
  );
};

export default DiceRoller;
