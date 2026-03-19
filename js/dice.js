/**
 * 1st Edition AD&D Character Generator - Dice Rolling
 */

const Dice = {
    /**
     * Roll a single die of the given size.
     */
    roll(sides) {
        return Math.floor(Math.random() * sides) + 1;
    },

    /**
     * Roll multiple dice and return the individual results.
     */
    rollMultiple(numDice, sides) {
        const results = [];
        for (let i = 0; i < numDice; i++) {
            results.push(this.roll(sides));
        }
        return results;
    },

    /**
     * Roll multiple dice and return the sum.
     */
    rollSum(numDice, sides) {
        return this.rollMultiple(numDice, sides).reduce((a, b) => a + b, 0);
    },

    /**
     * Roll 4d6 and drop the lowest die.
     */
    roll4d6DropLowest() {
        const rolls = this.rollMultiple(4, 6);
        rolls.sort((a, b) => a - b);
        const kept = rolls.slice(1); // drop lowest
        return {
            allRolls: [...rolls],
            kept: kept,
            total: kept.reduce((a, b) => a + b, 0)
        };
    },

    /**
     * Roll 3d6.
     */
    roll3d6() {
        const rolls = this.rollMultiple(3, 6);
        return {
            allRolls: rolls,
            total: rolls.reduce((a, b) => a + b, 0)
        };
    },

    /**
     * Roll percentile dice (d100).
     */
    rollPercentile() {
        return this.roll(100);
    },

    /**
     * Roll for starting gold.
     * @param {string} className - The character class key
     * @returns {{ rolls: number[], multiplier: number, total: number }}
     */
    rollStartingGold(className) {
        const [numDice, dieSize, multiplier] = STARTING_GOLD[className];
        const rolls = this.rollMultiple(numDice, dieSize);
        const sum = rolls.reduce((a, b) => a + b, 0);
        return {
            rolls,
            multiplier,
            total: sum * multiplier
        };
    },

    /**
     * Roll hit points for a class at level 1.
     * Rangers get 2d8 at level 1.
     * @param {string} className - The character class key
     * @param {number} conScore - Constitution score
     * @returns {{ rolls: number[], conBonus: number, total: number }}
     */
    rollHitPoints(className, conScore) {
        const hitDie = CLASS_HIT_DICE[className];
        const isFighter = FIGHTER_TYPES.includes(className);
        const conAdj = isFighter ? (CON_HP_ADJ[conScore] || 0) : (CON_HP_ADJ_NONFIGHTER[conScore] || 0);

        let numDice = 1;
        if (className === 'ranger') numDice = 2; // Rangers get 2 hit dice at level 1

        const rolls = this.rollMultiple(numDice, hitDie);
        const rawTotal = rolls.reduce((a, b) => a + b, 0);
        const total = Math.max(1, rawTotal + (conAdj * numDice));

        return {
            rolls,
            hitDie,
            numDice,
            conBonus: conAdj * numDice,
            total
        };
    },

    /**
     * Roll starting age.
     */
    rollStartingAge(race, className) {
        // For multi-class, use the first class
        const baseClass = className.split('/')[0];
        const ageData = STARTING_AGE[race] && STARTING_AGE[race][baseClass];
        if (!ageData) {
            // Fallback
            return { base: 20, diceTotal: 0, total: 20 };
        }
        const [base, numDice, dieSize] = ageData;
        const diceTotal = this.rollSum(numDice, dieSize);
        return {
            base,
            diceTotal,
            total: base + diceTotal
        };
    },

    /**
     * Roll height and weight.
     */
    rollHeightWeight(race, sex) {
        const data = HEIGHT_WEIGHT[race][sex];
        const [baseH, hDice, hDie, baseW, wDice, wDie] = data;
        const heightExtra = this.rollSum(hDice, hDie);
        const weightExtra = this.rollSum(wDice, wDie);
        const heightInches = baseH + heightExtra;
        const feet = Math.floor(heightInches / 12);
        const inches = heightInches % 12;
        return {
            heightInches,
            heightStr: `${feet}'${inches}"`,
            weight: baseW + weightExtra
        };
    }
};
