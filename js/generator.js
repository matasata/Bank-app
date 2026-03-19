/**
 * 1st Edition AD&D Character Generator - Core Generator Logic
 */

const Generator = {
    /**
     * Check if a set of ability scores qualifies for a given class.
     */
    meetsClassRequirements(abilities, className) {
        const reqs = CLASS_REQUIREMENTS[className];
        if (!reqs) return false;
        for (const [ability, minScore] of Object.entries(reqs)) {
            if ((abilities[ability] || 0) < minScore) return false;
        }
        return true;
    },

    /**
     * Get all available single classes for a race with given ability scores.
     */
    getAvailableClasses(abilities, race) {
        const allowed = RACE_CLASSES[race] || [];
        return allowed.filter(cls => this.meetsClassRequirements(abilities, cls));
    },

    /**
     * Get available multi-class options for a race with given ability scores.
     */
    getAvailableMultiClasses(abilities, race) {
        const options = RACE_MULTICLASS[race] || [];
        return options.filter(combo => {
            const classes = combo.split('/');
            return classes.every(cls => this.meetsClassRequirements(abilities, cls));
        });
    },

    /**
     * Get available alignments for a class (or multi-class).
     */
    getAvailableAlignments(className) {
        const classes = className.split('/');
        // Intersection of all class alignment lists
        let alignments = [...CLASS_ALIGNMENTS[classes[0]]];
        for (let i = 1; i < classes.length; i++) {
            const classAlignments = CLASS_ALIGNMENTS[classes[i]];
            alignments = alignments.filter(a => classAlignments.includes(a));
        }
        return alignments;
    },

    /**
     * Apply racial ability score adjustments.
     */
    applyRacialAdjustments(abilities, race) {
        const adjusted = { ...abilities };
        const adj = RACIAL_ADJUSTMENTS[race];
        const limits = RACIAL_LIMITS[race];

        for (const ability of ABILITIES) {
            adjusted[ability] += adj[ability];
            // Clamp to racial limits
            adjusted[ability] = Math.max(limits[ability][0], Math.min(limits[ability][1], adjusted[ability]));
        }
        return adjusted;
    },

    /**
     * Check if ability scores meet racial minimums.
     */
    meetsRacialMins(abilities, race) {
        const limits = RACIAL_LIMITS[race];
        for (const ability of ABILITIES) {
            if (abilities[ability] < limits[ability][0]) return false;
        }
        return true;
    },

    /**
     * Get available races for a set of ability scores.
     */
    getAvailableRaces(abilities) {
        const races = [];
        for (const race of Object.keys(RACE_LABELS)) {
            if (this.meetsRacialMins(abilities, race)) {
                // Check if they can be at least one class of this race
                const adjusted = this.applyRacialAdjustments(abilities, race);
                const classes = this.getAvailableClasses(adjusted, race);
                const multiClasses = this.getAvailableMultiClasses(adjusted, race);
                if (classes.length > 0 || multiClasses.length > 0) {
                    races.push(race);
                }
            }
        }
        return races;
    },

    /**
     * Roll exceptional strength for fighters with 18 STR.
     */
    rollExceptionalStrength(className, strength) {
        const classes = className.split('/');
        const hasFighter = classes.some(c => FIGHTER_TYPES.includes(c));
        if (hasFighter && strength === 18) {
            const roll = Dice.rollPercentile();
            const range = EXCEPTIONAL_STRENGTH_RANGES.find(r => roll >= r.min && roll <= r.max);
            return { roll, label: range.label };
        }
        return null;
    },

    /**
     * Calculate thief skills for a thief or assassin.
     */
    calculateThiefSkills(race, dexScore) {
        const skills = {};
        for (const [skill, base] of Object.entries(THIEF_SKILLS)) {
            let value = base;
            // Racial adjustment
            if (RACIAL_THIEF_ADJ[race] && RACIAL_THIEF_ADJ[race][skill] !== undefined) {
                value += RACIAL_THIEF_ADJ[race][skill];
            }
            // Dexterity adjustment (only for certain skills)
            if (DEX_THIEF_ADJ[dexScore] && DEX_THIEF_ADJ[dexScore][skill] !== undefined) {
                value += DEX_THIEF_ADJ[dexScore][skill];
            }
            skills[skill] = Math.max(1, value);
        }
        return skills;
    },

    /**
     * Get level limit for a race/class combo.
     */
    getLevelLimit(race, className) {
        if (race === 'human') return 'Unlimited';
        const limits = LEVEL_LIMITS[race];
        if (!limits) return 'N/A';
        const limit = limits[className];
        if (limit === null) return 'Unlimited';
        if (limit === undefined) return 'N/A';
        return limit.toString();
    },

    /**
     * Get the label for a class (handles multi-class).
     */
    getClassLabel(className) {
        if (className.includes('/')) {
            return className.split('/').map(c => CLASS_LABELS[c]).join(' / ');
        }
        return CLASS_LABELS[className] || className;
    },

    /**
     * Get the hit die label for a class.
     */
    getHitDieLabel(className) {
        if (className.includes('/')) {
            return className.split('/').map(c => `d${CLASS_HIT_DICE[c]}`).join(' / ');
        }
        return `d${CLASS_HIT_DICE[className]}`;
    },

    /**
     * Roll hit points for multi-class.
     */
    rollMultiClassHP(className, conScore) {
        const classes = className.split('/');
        let totalHP = 0;
        const details = [];

        for (const cls of classes) {
            const result = Dice.rollHitPoints(cls, conScore);
            details.push({ class: cls, ...result });
            totalHP += result.total;
        }

        // Multi-class divides total HP
        const dividedHP = Math.max(1, Math.floor(totalHP / classes.length));
        return {
            details,
            rawTotal: totalHP,
            dividedHP,
            isMultiClass: true,
            numClasses: classes.length
        };
    },

    /**
     * Roll starting gold for multi-class (use highest).
     */
    rollMultiClassGold(className) {
        const classes = className.split('/');
        let best = null;

        for (const cls of classes) {
            const result = Dice.rollStartingGold(cls);
            if (!best || result.total > best.total) {
                best = { class: cls, ...result };
            }
        }
        return best;
    },

    /**
     * Build the complete character.
     */
    buildCharacter(config) {
        const {
            abilities,
            race,
            className,
            alignment,
            name,
            sex
        } = config;

        const char = {
            name: name || 'Unnamed Adventurer',
            sex: sex || 'Male',
            race,
            raceName: RACE_LABELS[race],
            className,
            classLabel: this.getClassLabel(className),
            alignment,
            alignmentLabel: ALIGNMENT_LABELS[alignment],
            abilities: { ...abilities }
        };

        // Exceptional strength
        char.exceptionalStrength = this.rollExceptionalStrength(className, abilities.strength);

        // Hit points
        const isMultiClass = className.includes('/');
        if (isMultiClass) {
            const hpResult = this.rollMultiClassHP(className, abilities.constitution);
            char.hitPoints = hpResult.dividedHP;
            char.hpDetails = hpResult;
        } else {
            const hpResult = Dice.rollHitPoints(className, abilities.constitution);
            char.hitPoints = hpResult.total;
            char.hpDetails = hpResult;
        }

        // Starting gold
        if (isMultiClass) {
            const goldResult = this.rollMultiClassGold(className);
            char.gold = goldResult.total;
            char.goldDetails = goldResult;
        } else {
            const goldResult = Dice.rollStartingGold(className);
            char.gold = goldResult.total;
            char.goldDetails = goldResult;
        }

        // Saving throws (use first class for multi-class)
        const primaryClass = className.split('/')[0];
        char.savingThrows = {
            paralyzation: SAVING_THROWS[primaryClass][0],
            petrification: SAVING_THROWS[primaryClass][1],
            rodStaffWand: SAVING_THROWS[primaryClass][2],
            breathWeapon: SAVING_THROWS[primaryClass][3],
            spell: SAVING_THROWS[primaryClass][4]
        };

        // Thief skills (if thief or assassin in class)
        const allClasses = className.split('/');
        if (allClasses.includes('thief') || allClasses.includes('assassin')) {
            char.thiefSkills = this.calculateThiefSkills(race, abilities.dexterity);
        }

        // Level limits
        if (isMultiClass) {
            char.levelLimits = allClasses.map(c => ({
                class: CLASS_LABELS[c],
                limit: this.getLevelLimit(race, c)
            }));
        } else {
            char.levelLimit = this.getLevelLimit(race, className);
        }

        // Languages
        const intLangs = INT_LANGUAGES[Math.min(18, Math.max(3, abilities.intelligence))] || 0;
        char.languages = [...RACIAL_LANGUAGES[race]];
        char.additionalLanguageSlots = intLangs;

        // Movement
        char.movement = RACIAL_MOVEMENT[race];

        // Age
        char.ageDetails = Dice.rollStartingAge(race, className);
        char.age = char.ageDetails.total;

        // Height & Weight
        const hwResult = Dice.rollHeightWeight(race, sex === 'Female' ? 'female' : 'male');
        char.height = hwResult.heightStr;
        char.weight = hwResult.weight;

        // THAC0 (all level 1 characters start at 20)
        char.thac0 = 20;

        // Armor Class (base 10, no armor)
        char.armorClass = 10;

        return char;
    }
};
