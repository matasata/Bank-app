import React, { useState, useCallback, useEffect } from 'react';
import { useCharacterStore } from '../../stores/characterStore';
import { useGameStore } from '../../stores/gameStore';
import { rollDie } from '../../utils/dice';
import type { AbilityName, RollingMethod, DiceRollResult } from '../../types';
import { ABILITY_NAMES } from '../../types';

const METHODS: { id: RollingMethod; label: string; description: string }[] = [
  { id: '3d6-in-order', label: 'Method I', description: '3d6 in order - The classic method. Roll 3d6 for each ability in order.' },
  { id: '4d6-drop-lowest', label: 'Method II', description: '4d6 drop lowest - Roll 4d6, drop the lowest die, assign as desired.' },
  { id: '2d6+6', label: 'Method III', description: '2d6+6 - Roll 2d6 and add 6, assign as desired. Heroic characters.' },
  { id: '3d6-twice-best', label: 'Method IV', description: '3d6 twice, keep best - Roll 3d6 twice per ability, keep the better roll.' },
  { id: '4d6-arrange', label: 'Method V', description: '4d6 drop lowest, arrange - Roll 12 sets, keep best 6, assign.' },
  { id: 'point-buy', label: 'Point Buy', description: 'Distribute 75 points among abilities (min 3, max 18).' },
];

interface AnimatedDie {
  value: number;
  isRolling: boolean;
  isDropped: boolean;
}

export const AbilityScoreRoller: React.FC = () => {
  const {
    rollingMethod, setRollingMethod,
    abilityRolls, rollAbilities, setAbilityRolls,
    assignedAbilities, assignAbilities,
    setStep,
  } = useCharacterStore();
  const { addLogEntry } = useGameStore();

  const [animatedDice, setAnimatedDice] = useState<AnimatedDie[][]>([]);
  const [isAnimating, setIsAnimating] = useState(false);
  const [dragSource, setDragSource] = useState<number | null>(null);
  const [assignments, setAssignments] = useState<Record<AbilityName, number | null>>({
    strength: null, dexterity: null, constitution: null,
    intelligence: null, wisdom: null, charisma: null,
  });
  const [pointBuyScores, setPointBuyScores] = useState<Record<AbilityName, number>>({
    strength: 10, dexterity: 10, constitution: 10,
    intelligence: 10, wisdom: 10, charisma: 10,
  });

  const canArrange = rollingMethod !== '3d6-in-order';
  const pointBuyTotal = 75;
  const pointBuyUsed = Object.values(pointBuyScores).reduce((s, v) => s + v, 0);

  const animateRoll = useCallback(async () => {
    setIsAnimating(true);
    rollAbilities();

    // Get the results after rolling
    const store = useCharacterStore.getState();
    const rolls = store.abilityRolls;

    // Animate each set of dice
    for (let i = 0; i < rolls.length; i++) {
      const roll = rolls[i];
      const diceCount = roll.dice.length;

      // Start with random values
      const initialDice: AnimatedDie[] = roll.dice.map(() => ({
        value: rollDie(6),
        isRolling: true,
        isDropped: false,
      }));
      setAnimatedDice((prev) => {
        const next = [...prev];
        next[i] = initialDice;
        return next;
      });

      // Animate
      for (let frame = 0; frame < 8; frame++) {
        await new Promise((r) => setTimeout(r, 60));
        setAnimatedDice((prev) => {
          const next = [...prev];
          next[i] = next[i].map((d) => ({
            ...d,
            value: d.isRolling ? rollDie(6) : d.value,
          }));
          return next;
        });
      }

      // Final values
      setAnimatedDice((prev) => {
        const next = [...prev];
        next[i] = roll.dice.map((val, j) => ({
          value: val,
          isRolling: false,
          isDropped: roll.dropped.includes(val) &&
            roll.dropped.indexOf(val) === roll.dice.indexOf(val) &&
            j === roll.dice.indexOf(val),
        }));
        return next;
      });

      await new Promise((r) => setTimeout(r, 200));
    }

    // For 3d6-in-order, auto-assign
    if (store.rollingMethod === '3d6-in-order') {
      const autoAssign: Record<AbilityName, number | null> = {
        strength: rolls[0]?.total ?? null,
        dexterity: rolls[1]?.total ?? null,
        constitution: rolls[2]?.total ?? null,
        intelligence: rolls[3]?.total ?? null,
        wisdom: rolls[4]?.total ?? null,
        charisma: rolls[5]?.total ?? null,
      };
      setAssignments(autoAssign);
    } else {
      setAssignments({
        strength: null, dexterity: null, constitution: null,
        intelligence: null, wisdom: null, charisma: null,
      });
    }

    setIsAnimating(false);
  }, [rollingMethod, rollAbilities]);

  const handleDragStart = (rollIndex: number) => {
    if (!canArrange) return;
    setDragSource(rollIndex);
  };

  const handleDrop = (ability: AbilityName) => {
    if (dragSource === null || !canArrange) return;
    const roll = abilityRolls[dragSource];
    if (!roll) return;

    // Check if this roll is already assigned somewhere
    const newAssignments = { ...assignments };
    for (const key of ABILITY_NAMES) {
      if (newAssignments[key] === roll.total && key !== ability) {
        // If the target already has a value, swap
        const existing = newAssignments[ability];
        newAssignments[key] = existing;
        break;
      }
    }
    newAssignments[ability] = roll.total;
    setAssignments(newAssignments);
    setDragSource(null);
  };

  const handleAssignClick = (rollIndex: number) => {
    if (!canArrange || assignments === null) return;
    const roll = abilityRolls[rollIndex];
    if (!roll) return;

    // Find first unassigned ability
    const firstEmpty = ABILITY_NAMES.find((a) => assignments[a] === null);
    if (firstEmpty) {
      setAssignments({ ...assignments, [firstEmpty]: roll.total });
    }
  };

  const confirmAssignment = () => {
    if (rollingMethod === 'point-buy') {
      assignAbilities(pointBuyScores);
      addLogEntry({ type: 'dice', message: `Ability scores assigned via point buy: STR ${pointBuyScores.strength}, DEX ${pointBuyScores.dexterity}, CON ${pointBuyScores.constitution}, INT ${pointBuyScores.intelligence}, WIS ${pointBuyScores.wisdom}, CHA ${pointBuyScores.charisma}` });
      setStep(1);
      return;
    }

    const allAssigned = ABILITY_NAMES.every((a) => assignments[a] !== null);
    if (!allAssigned) return;

    const scores = {
      strength: assignments.strength!,
      dexterity: assignments.dexterity!,
      constitution: assignments.constitution!,
      intelligence: assignments.intelligence!,
      wisdom: assignments.wisdom!,
      charisma: assignments.charisma!,
    };
    assignAbilities(scores);
    addLogEntry({ type: 'dice', message: `Ability scores rolled (${rollingMethod}): STR ${scores.strength}, DEX ${scores.dexterity}, CON ${scores.constitution}, INT ${scores.intelligence}, WIS ${scores.wisdom}, CHA ${scores.charisma}` });
    setStep(1);
  };

  const allAssigned = rollingMethod === 'point-buy'
    ? pointBuyUsed <= pointBuyTotal
    : ABILITY_NAMES.every((a) => assignments[a] !== null);

  return (
    <div className="space-y-6">
      {/* Method Selection Tabs */}
      <div className="flex flex-wrap gap-1 p-1 bg-inkBlack/30 rounded-lg">
        {METHODS.map((method) => (
          <button
            key={method.id}
            onClick={() => {
              setRollingMethod(method.id);
              setAnimatedDice([]);
              setAbilityRolls([]);
              setAssignments({
                strength: null, dexterity: null, constitution: null,
                intelligence: null, wisdom: null, charisma: null,
              });
            }}
            className={`
              flex-1 min-w-[100px] px-3 py-2 rounded-md text-xs font-display font-semibold
              tracking-wider uppercase transition-all duration-200
              ${rollingMethod === method.id
                ? 'bg-burgundy text-gold shadow-md border border-gold/40'
                : 'text-parchment/50 hover:text-parchment/80 hover:bg-darkWood/30'
              }
            `}
          >
            {method.label}
          </button>
        ))}
      </div>

      {/* Method Description */}
      <div className="text-center">
        <p className="text-sm font-body text-parchment/60 italic">
          {METHODS.find((m) => m.id === rollingMethod)?.description}
        </p>
      </div>

      {/* Point Buy Mode */}
      {rollingMethod === 'point-buy' ? (
        <div className="space-y-4">
          <div className="text-center">
            <span className="font-display text-lg text-gold">
              Points: {pointBuyUsed} / {pointBuyTotal}
            </span>
            <span className={`ml-2 text-sm ${pointBuyUsed > pointBuyTotal ? 'text-red-400' : 'text-forestGreen'}`}>
              ({pointBuyTotal - pointBuyUsed} remaining)
            </span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {ABILITY_NAMES.map((ability) => (
              <div key={ability} className="stat-box">
                <span className="font-display text-xs font-semibold uppercase text-darkWood/70 tracking-wider">
                  {ability.slice(0, 3)}
                </span>
                <div className="flex items-center gap-2 mt-1">
                  <button
                    onClick={() =>
                      setPointBuyScores((s) => ({
                        ...s,
                        [ability]: Math.max(3, s[ability] - 1),
                      }))
                    }
                    className="w-6 h-6 rounded bg-darkWood text-parchment text-xs hover:bg-burgundy transition-colors"
                  >
                    -
                  </button>
                  <span className="font-display text-xl font-bold text-inkBlack w-8 text-center">
                    {pointBuyScores[ability]}
                  </span>
                  <button
                    onClick={() =>
                      setPointBuyScores((s) => ({
                        ...s,
                        [ability]: Math.min(18, s[ability] + 1),
                      }))
                    }
                    className="w-6 h-6 rounded bg-darkWood text-parchment text-xs hover:bg-burgundy transition-colors"
                  >
                    +
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <>
          {/* Roll Button */}
          <div className="text-center">
            <button
              onClick={animateRoll}
              disabled={isAnimating}
              className="
                btn-primary text-lg px-8 py-3
                disabled:opacity-50 disabled:cursor-not-allowed
              "
            >
              {isAnimating ? 'Rolling...' : abilityRolls.length > 0 ? 'Re-Roll All' : 'Roll Ability Scores'}
            </button>
          </div>

          {/* Dice Results */}
          {abilityRolls.length > 0 && (
            <div className="space-y-4">
              <h3 className="font-display text-sm text-gold/70 text-center tracking-wider uppercase">
                {canArrange ? 'Click or drag rolls to assign them' : 'Rolls assigned in order'}
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {abilityRolls.map((roll, idx) => {
                  const isUsed = Object.values(assignments).includes(roll.total);
                  return (
                    <div
                      key={idx}
                      draggable={canArrange && !isUsed}
                      onDragStart={() => handleDragStart(idx)}
                      onClick={() => !isUsed && handleAssignClick(idx)}
                      className={`
                        p-3 rounded-lg border text-center transition-all duration-200
                        ${isUsed
                          ? 'bg-darkWood/20 border-gold/10 opacity-50'
                          : canArrange
                            ? 'bg-darkWood/40 border-gold/30 cursor-grab hover:border-gold/60 hover:shadow-gold-glow'
                            : 'bg-darkWood/40 border-gold/20'
                        }
                      `}
                    >
                      {/* Individual dice */}
                      <div className="flex justify-center gap-1 mb-2">
                        {(animatedDice[idx] || roll.dice.map((v) => ({
                          value: v,
                          isRolling: false,
                          isDropped: roll.dropped.includes(v),
                        }))).map((die, dIdx) => (
                          <span
                            key={dIdx}
                            className={`
                              dice-result text-xs
                              ${die.isRolling ? 'animate-dice-roll' : ''}
                              ${die.isDropped ? 'opacity-30 line-through border-red-400/50' : ''}
                            `}
                          >
                            {die.value}
                          </span>
                        ))}
                      </div>
                      {/* Total */}
                      <div className="font-display text-2xl font-bold text-gold text-shadow-glow">
                        {roll.total}
                      </div>
                      {!canArrange && (
                        <div className="font-display text-xs text-parchment/50 uppercase tracking-wider mt-1">
                          {ABILITY_NAMES[idx]?.slice(0, 3)}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Assignment Targets */}
          {abilityRolls.length > 0 && canArrange && (
            <div className="space-y-2">
              <h3 className="font-display text-sm text-gold/70 text-center tracking-wider uppercase">
                Ability Assignments
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {ABILITY_NAMES.map((ability) => (
                  <div
                    key={ability}
                    onDragOver={(e) => e.preventDefault()}
                    onDrop={() => handleDrop(ability)}
                    onClick={() => {
                      if (assignments[ability] !== null) {
                        setAssignments({ ...assignments, [ability]: null });
                      }
                    }}
                    className={`
                      stat-box cursor-pointer transition-all duration-200
                      ${assignments[ability] !== null
                        ? 'border-gold shadow-gold-glow'
                        : 'border-dashed border-darkWood/50 hover:border-gold/50'
                      }
                    `}
                  >
                    <span className="font-display text-xs font-semibold uppercase text-darkWood/70 tracking-wider">
                      {ability.slice(0, 3)}
                    </span>
                    <span className="font-display text-2xl font-bold text-inkBlack mt-1">
                      {assignments[ability] ?? '—'}
                    </span>
                    <span className="text-xs text-darkWood/50 capitalize">{ability}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Confirm Button */}
      {(abilityRolls.length > 0 || rollingMethod === 'point-buy') && (
        <div className="text-center pt-4">
          <button
            onClick={confirmAssignment}
            disabled={!allAssigned}
            className="
              btn-primary text-lg px-10 py-3
              disabled:opacity-30 disabled:cursor-not-allowed
            "
          >
            Confirm Ability Scores
          </button>
        </div>
      )}
    </div>
  );
};

export default AbilityScoreRoller;
