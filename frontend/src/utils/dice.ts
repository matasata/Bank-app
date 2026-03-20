/**
 * Client-side dice rolling utilities.
 * These are used for animations and preview purposes.
 * Authoritative rolls happen server-side.
 */

export interface DiceResult {
  faces: number;
  rolls: number[];
  dropped: number[];
  kept: number[];
  total: number;
  modifier: number;
  finalTotal: number;
}

/** Roll a single die with the given number of faces. */
export function rollDie(faces: number): number {
  return Math.floor(Math.random() * faces) + 1;
}

/** Roll multiple dice. */
export function rollDice(count: number, faces: number): number[] {
  const results: number[] = [];
  for (let i = 0; i < count; i++) {
    results.push(rollDie(faces));
  }
  return results;
}

/** Parse a dice notation string like "3d6+2" and roll it. */
export function parseDiceNotation(notation: string): DiceResult {
  const regex = /^(\d+)d(\d+)(?:([+-])(\d+))?$/i;
  const match = notation.match(regex);

  if (!match) {
    return {
      faces: 0, rolls: [], dropped: [], kept: [],
      total: 0, modifier: 0, finalTotal: 0,
    };
  }

  const count = parseInt(match[1], 10);
  const faces = parseInt(match[2], 10);
  const modSign = match[3] === '-' ? -1 : 1;
  const modValue = match[4] ? parseInt(match[4], 10) : 0;
  const modifier = modSign * modValue;

  const rolls = rollDice(count, faces);
  const total = rolls.reduce((sum, r) => sum + r, 0);

  return {
    faces,
    rolls,
    dropped: [],
    kept: [...rolls],
    total,
    modifier,
    finalTotal: total + modifier,
  };
}

/** Roll 3d6 straight (Method I). */
export function roll3d6(): DiceResult {
  const rolls = rollDice(3, 6);
  const total = rolls.reduce((sum, r) => sum + r, 0);
  return {
    faces: 6, rolls, dropped: [], kept: [...rolls],
    total, modifier: 0, finalTotal: total,
  };
}

/** Roll 4d6 drop lowest (Method II). */
export function roll4d6DropLowest(): DiceResult {
  const rolls = rollDice(4, 6);
  const sorted = [...rolls].sort((a, b) => a - b);
  const dropped = [sorted[0]];
  const kept = sorted.slice(1);
  const total = kept.reduce((sum, r) => sum + r, 0);
  return {
    faces: 6, rolls, dropped, kept,
    total, modifier: 0, finalTotal: total,
  };
}

/** Roll 2d6+6 (Method III). */
export function roll2d6Plus6(): DiceResult {
  const rolls = rollDice(2, 6);
  const total = rolls.reduce((sum, r) => sum + r, 0);
  return {
    faces: 6, rolls, dropped: [], kept: [...rolls],
    total, modifier: 6, finalTotal: total + 6,
  };
}

/** Roll 3d6 twice, keep best (Method IV). */
export function roll3d6TwiceKeepBest(): DiceResult {
  const firstSet = rollDice(3, 6);
  const secondSet = rollDice(3, 6);
  const firstTotal = firstSet.reduce((sum, r) => sum + r, 0);
  const secondTotal = secondSet.reduce((sum, r) => sum + r, 0);

  if (firstTotal >= secondTotal) {
    return {
      faces: 6, rolls: [...firstSet, ...secondSet],
      dropped: secondSet, kept: firstSet,
      total: firstTotal, modifier: 0, finalTotal: firstTotal,
    };
  }
  return {
    faces: 6, rolls: [...firstSet, ...secondSet],
    dropped: firstSet, kept: secondSet,
    total: secondTotal, modifier: 0, finalTotal: secondTotal,
  };
}

/** Roll all 6 ability scores with a given method. */
export function rollAllAbilities(
  method: 'roll3d6' | 'roll4d6' | 'roll2d6p6' | 'roll3d6x2' | 'roll4d6arr' | 'pointbuy'
): DiceResult[] {
  const results: DiceResult[] = [];
  for (let i = 0; i < 6; i++) {
    switch (method) {
      case 'roll3d6':
        results.push(roll3d6());
        break;
      case 'roll4d6':
        results.push(roll4d6DropLowest());
        break;
      case 'roll2d6p6':
        results.push(roll2d6Plus6());
        break;
      case 'roll3d6x2':
        results.push(roll3d6TwiceKeepBest());
        break;
      case 'roll4d6arr':
        results.push(roll4d6DropLowest());
        break;
      default:
        results.push(roll3d6());
    }
  }
  return results;
}

/** Generate animated intermediate values for a dice roll animation. */
export function generateAnimationFrames(
  finalValue: number,
  faces: number,
  frameCount: number = 10
): number[] {
  const frames: number[] = [];
  for (let i = 0; i < frameCount - 1; i++) {
    frames.push(rollDie(faces));
  }
  frames.push(finalValue);
  return frames;
}

/** Get the ability score modifier for AD&D 1st Edition. */
export function getAbilityModifier(ability: string, score: number): Record<string, number> {
  // Simplified AD&D 1e modifier tables
  switch (ability) {
    case 'strength':
      if (score <= 3) return { hitBonus: -3, damageBonus: -1, openDoors: 1, bendBars: 0 };
      if (score <= 5) return { hitBonus: -2, damageBonus: -1, openDoors: 1, bendBars: 0 };
      if (score <= 7) return { hitBonus: -1, damageBonus: 0, openDoors: 1, bendBars: 0 };
      if (score <= 15) return { hitBonus: 0, damageBonus: 0, openDoors: 2, bendBars: 1 };
      if (score === 16) return { hitBonus: 0, damageBonus: 1, openDoors: 3, bendBars: 2 };
      if (score === 17) return { hitBonus: 1, damageBonus: 1, openDoors: 3, bendBars: 3 };
      if (score === 18) return { hitBonus: 1, damageBonus: 2, openDoors: 3, bendBars: 4 };
      return { hitBonus: 3, damageBonus: 6, openDoors: 5, bendBars: 16 };

    case 'dexterity':
      if (score <= 3) return { reactionAdj: -3, missileAdj: -3, acAdj: 4 };
      if (score <= 5) return { reactionAdj: -2, missileAdj: -2, acAdj: 3 };
      if (score <= 6) return { reactionAdj: -1, missileAdj: -1, acAdj: 2 };
      if (score <= 8) return { reactionAdj: 0, missileAdj: 0, acAdj: 1 };
      if (score <= 14) return { reactionAdj: 0, missileAdj: 0, acAdj: 0 };
      if (score === 15) return { reactionAdj: 0, missileAdj: 0, acAdj: -1 };
      if (score === 16) return { reactionAdj: 1, missileAdj: 1, acAdj: -2 };
      if (score === 17) return { reactionAdj: 2, missileAdj: 2, acAdj: -3 };
      return { reactionAdj: 3, missileAdj: 3, acAdj: -4 };

    case 'constitution':
      if (score <= 3) return { hpAdj: -2, systemShock: 35, resurrection: 40 };
      if (score <= 6) return { hpAdj: -1, systemShock: 50, resurrection: 55 };
      if (score <= 14) return { hpAdj: 0, systemShock: 75, resurrection: 80 };
      if (score === 15) return { hpAdj: 1, systemShock: 80, resurrection: 85 };
      if (score === 16) return { hpAdj: 2, systemShock: 85, resurrection: 90 };
      if (score === 17) return { hpAdj: 2, systemShock: 90, resurrection: 95 };
      return { hpAdj: 3, systemShock: 95, resurrection: 99 };

    default:
      return {};
  }
}

/** Format a dice result for display. */
export function formatDiceResult(result: DiceResult): string {
  const diceStr = result.rolls.map((r, i) =>
    result.dropped.includes(r) && result.dropped.indexOf(r) === i
      ? `~~${r}~~`
      : `${r}`
  ).join(', ');

  const modStr = result.modifier > 0
    ? ` + ${result.modifier}`
    : result.modifier < 0
      ? ` - ${Math.abs(result.modifier)}`
      : '';

  return `[${diceStr}]${modStr} = ${result.finalTotal}`;
}
