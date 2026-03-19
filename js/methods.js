/**
 * 1st Edition AD&D Character Generator - DMG Ability Score Methods I-IV
 */

const Methods = {
    /**
     * Method I: Roll 4d6, drop lowest die. Repeat 6 times.
     * Player arranges the 6 scores among abilities as desired.
     *
     * @returns {{ scores: object[], arranged: boolean }}
     */
    methodI() {
        const scores = [];
        for (let i = 0; i < 6; i++) {
            scores.push(Dice.roll4d6DropLowest());
        }
        return {
            method: 1,
            description: 'Method I: 4d6, drop lowest. Arrange as desired.',
            scores,
            totals: scores.map(s => s.total).sort((a, b) => b - a),
            arrangeable: true
        };
    },

    /**
     * Method II: Roll 3d6 twelve times. Select best 6 scores.
     * Player arranges the 6 scores among abilities as desired.
     *
     * @returns {{ allScores: object[], bestSix: number[], arranged: boolean }}
     */
    methodII() {
        const allScores = [];
        for (let i = 0; i < 12; i++) {
            allScores.push(Dice.roll3d6());
        }
        // Sort all totals descending and pick best 6
        const sorted = [...allScores].sort((a, b) => b.total - a.total);
        const bestSix = sorted.slice(0, 6);

        return {
            method: 2,
            description: 'Method II: 3d6 twelve times, keep best 6. Arrange as desired.',
            allScores,
            bestSix: bestSix.map(s => s.total).sort((a, b) => b - a),
            totals: bestSix.map(s => s.total).sort((a, b) => b - a),
            arrangeable: true
        };
    },

    /**
     * Method III: Roll 3d6 six times for each ability score.
     * Keep the highest roll for each. Scores are assigned to specific abilities.
     *
     * @returns {{ abilities: object }}
     */
    methodIII() {
        const abilities = {};
        const details = {};

        ABILITIES.forEach(ability => {
            const rolls = [];
            for (let i = 0; i < 6; i++) {
                rolls.push(Dice.roll3d6());
            }
            const best = rolls.reduce((a, b) => a.total > b.total ? a : b);
            abilities[ability] = best.total;
            details[ability] = {
                allRolls: rolls,
                best: best.total
            };
        });

        return {
            method: 3,
            description: 'Method III: 3d6 six times per ability. Keep highest for each.',
            abilities,
            details,
            totals: ABILITIES.map(a => abilities[a]),
            arrangeable: false
        };
    },

    /**
     * Method IV: Roll 3d6 for each ability to create 12 characters.
     * Player selects the character they prefer.
     *
     * @returns {{ characters: object[] }}
     */
    methodIV() {
        const characters = [];
        for (let i = 0; i < 12; i++) {
            const abilities = {};
            ABILITIES.forEach(ability => {
                abilities[ability] = Dice.roll3d6().total;
            });
            const total = ABILITIES.reduce((sum, a) => sum + abilities[a], 0);
            characters.push({ abilities, total });
        }

        return {
            method: 4,
            description: 'Method IV: 3d6 for each ability, generate 12 characters. Pick one.',
            characters,
            arrangeable: false
        };
    }
};
