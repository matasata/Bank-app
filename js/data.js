/**
 * 1st Edition AD&D Character Generator - Game Data
 * All data sourced from the 1e PHB and DMG.
 */

const ABILITIES = ['strength', 'intelligence', 'wisdom', 'dexterity', 'constitution', 'charisma'];

const ABILITY_LABELS = {
    strength: 'Strength',
    intelligence: 'Intelligence',
    wisdom: 'Wisdom',
    dexterity: 'Dexterity',
    constitution: 'Constitution',
    charisma: 'Charisma'
};

const ABILITY_ABBREV = {
    strength: 'STR',
    intelligence: 'INT',
    wisdom: 'WIS',
    dexterity: 'DEX',
    constitution: 'CON',
    charisma: 'CHA'
};

/**
 * Racial ability score adjustments.
 * Applied after score assignment.
 */
const RACIAL_ADJUSTMENTS = {
    human:    { strength: 0, intelligence: 0, wisdom: 0, dexterity: 0, constitution: 0, charisma: 0 },
    dwarf:    { strength: 0, intelligence: 0, wisdom: 0, dexterity: 0, constitution: +1, charisma: -1 },
    elf:      { strength: 0, intelligence: 0, wisdom: 0, dexterity: +1, constitution: -1, charisma: 0 },
    gnome:    { strength: 0, intelligence: 0, wisdom: 0, dexterity: 0, constitution: 0, charisma: 0 },
    halfelf:  { strength: 0, intelligence: 0, wisdom: 0, dexterity: 0, constitution: 0, charisma: 0 },
    halfling: { strength: -1, intelligence: 0, wisdom: 0, dexterity: +1, constitution: 0, charisma: 0 },
    halforc:  { strength: +1, intelligence: 0, wisdom: 0, dexterity: 0, constitution: +1, charisma: -2 }
};

/**
 * Racial ability score minimums and maximums (after adjustments).
 */
const RACIAL_LIMITS = {
    human:    { strength: [3,18], intelligence: [3,18], wisdom: [3,18], dexterity: [3,18], constitution: [3,18], charisma: [3,18] },
    dwarf:    { strength: [8,18], intelligence: [3,18], wisdom: [3,18], dexterity: [3,17], constitution: [12,19], charisma: [3,16] },
    elf:      { strength: [3,18], intelligence: [8,18], wisdom: [3,18], dexterity: [7,19], constitution: [6,17], charisma: [8,18] },
    gnome:    { strength: [6,18], intelligence: [7,18], wisdom: [3,18], dexterity: [3,18], constitution: [8,18], charisma: [3,18] },
    halfelf:  { strength: [3,18], intelligence: [4,18], wisdom: [3,18], dexterity: [6,18], constitution: [6,18], charisma: [3,18] },
    halfling: { strength: [6,17], intelligence: [6,18], wisdom: [3,17], dexterity: [8,18], constitution: [10,19], charisma: [3,18] },
    halforc:  { strength: [6,18], intelligence: [3,17], wisdom: [3,14], dexterity: [3,17], constitution: [13,19], charisma: [3,12] }
};

const RACE_LABELS = {
    human: 'Human',
    dwarf: 'Dwarf',
    elf: 'Elf',
    gnome: 'Gnome',
    halfelf: 'Half-Elf',
    halfling: 'Halfling',
    halforc: 'Half-Orc'
};

const RACE_DESCRIPTIONS = {
    human: 'Humans are the most adaptable and ambitious of the common races. They can be any class with no level limits.',
    dwarf: 'Stout and hardy folk who dwell in mountain strongholds. +1 CON, -1 CHA. Infravision 60\'.',
    elf: 'Graceful and long-lived denizens of ancient forests. +1 DEX, -1 CON. Infravision 60\'. Resistance to sleep and charm.',
    gnome: 'Small, clever folk related to dwarves. Infravision 60\'. Bonus to saves vs. magic.',
    halfelf: 'Children of two worlds with mixed heritage. Infravision 60\'. 30% resistance to sleep and charm.',
    halfling: 'Small, nimble folk who love comfort. -1 STR, +1 DEX. Infravision 30\' (some). Bonus to saves vs. magic.',
    halforc: 'Tough crossbreeds shunned by many. +1 STR, +1 CON, -2 CHA. Infravision 60\'.'
};

/**
 * Allowed classes per race. true = allowed, false = not allowed.
 */
const RACE_CLASSES = {
    human:    ['fighter', 'paladin', 'ranger', 'cleric', 'druid', 'magicuser', 'illusionist', 'thief', 'assassin', 'monk', 'bard'],
    dwarf:    ['fighter', 'cleric', 'thief', 'assassin'],
    elf:      ['fighter', 'ranger', 'magicuser', 'thief', 'assassin'],
    gnome:    ['fighter', 'cleric', 'illusionist', 'thief', 'assassin'],
    halfelf:  ['fighter', 'ranger', 'cleric', 'druid', 'magicuser', 'thief', 'assassin'],
    halfling: ['fighter', 'cleric', 'thief'],
    halforc:  ['fighter', 'cleric', 'thief', 'assassin']
};

/**
 * Multi-class options per race.
 */
const RACE_MULTICLASS = {
    human: [],
    dwarf: ['fighter/thief'],
    elf: ['fighter/magicuser', 'fighter/thief', 'magicuser/thief', 'fighter/magicuser/thief'],
    gnome: ['fighter/illusionist', 'fighter/thief', 'illusionist/thief'],
    halfelf: ['cleric/fighter', 'cleric/ranger', 'cleric/magicuser', 'fighter/magicuser', 'fighter/thief',
              'magicuser/thief', 'cleric/fighter/magicuser', 'fighter/magicuser/thief'],
    halfling: ['fighter/thief'],
    halforc: ['cleric/thief', 'cleric/assassin', 'cleric/fighter', 'fighter/thief', 'fighter/assassin']
};

/**
 * Level limits by race/class. null = unlimited (human).
 */
const LEVEL_LIMITS = {
    dwarf:    { fighter: 9, cleric: 8, thief: null, assassin: 9 },
    elf:      { fighter: 7, ranger: 8, magicuser: 11, thief: null, assassin: 10 },
    gnome:    { fighter: 6, cleric: 7, illusionist: 7, thief: null, assassin: 8 },
    halfelf:  { fighter: 8, ranger: 8, cleric: 5, druid: null, magicuser: 8, thief: null, assassin: 11 },
    halfling: { fighter: 6, cleric: 4, thief: null },
    halforc:  { fighter: 10, cleric: 4, thief: 8, assassin: null }
};

const CLASS_LABELS = {
    fighter: 'Fighter',
    paladin: 'Paladin',
    ranger: 'Ranger',
    cleric: 'Cleric',
    druid: 'Druid',
    magicuser: 'Magic-User',
    illusionist: 'Illusionist',
    thief: 'Thief',
    assassin: 'Assassin',
    monk: 'Monk',
    bard: 'Bard'
};

/**
 * Minimum ability scores required for each class.
 */
const CLASS_REQUIREMENTS = {
    fighter:     { strength: 9 },
    paladin:     { strength: 12, intelligence: 9, wisdom: 13, constitution: 9, charisma: 17 },
    ranger:      { strength: 13, intelligence: 13, wisdom: 14, constitution: 14, charisma: 0 },
    cleric:      { wisdom: 9 },
    druid:       { wisdom: 12, charisma: 15 },
    magicuser:   { intelligence: 9 },
    illusionist: { intelligence: 15, dexterity: 16 },
    thief:       { dexterity: 9 },
    assassin:    { strength: 12, intelligence: 11, dexterity: 12 },
    monk:        { strength: 15, wisdom: 15, dexterity: 15, constitution: 11 },
    bard:        { strength: 15, intelligence: 12, wisdom: 15, dexterity: 15, constitution: 10, charisma: 15 }
};

const CLASS_DESCRIPTIONS = {
    fighter: 'A warrior skilled in combat. Masters of arms and armor. Hit die: d10.',
    paladin: 'A holy warrior devoted to law and good. Must be Lawful Good. Hit die: d10.',
    ranger: 'A woodland warrior and tracker. Must be Good alignment. Hit die: d8 (2d8 at 1st level).',
    cleric: 'A priestly warrior who serves a deity. Can turn undead. Hit die: d8.',
    druid: 'A priest of nature. Must be True Neutral. Hit die: d8.',
    magicuser: 'A student of the arcane arts. Casts spells from a spellbook. Hit die: d4.',
    illusionist: 'A specialist in illusion magic. Hit die: d4.',
    thief: 'A rogue skilled in stealth and subterfuge. Hit die: d6.',
    assassin: 'A killer for hire. Must be Evil alignment. Hit die: d6.',
    monk: 'A martial artist devoted to discipline. Must be Lawful. Hit die: d4.',
    bard: 'A jack-of-all-trades poet and loremaster. Dual-class path (Fighter then Thief then Bard). Hit die: d6.'
};

/**
 * Hit dice per class.
 */
const CLASS_HIT_DICE = {
    fighter: 10,
    paladin: 10,
    ranger: 8,   // Gets 2d8 at level 1
    cleric: 8,
    druid: 8,
    magicuser: 4,
    illusionist: 4,
    thief: 6,
    assassin: 6,
    monk: 4,
    bard: 6
};

/**
 * Starting gold (in gp) dice formulas.
 * Format: [numDice, dieSize, multiplier]
 */
const STARTING_GOLD = {
    fighter:     [5, 4, 10],   // 5d4 x 10
    paladin:     [5, 4, 10],
    ranger:      [5, 4, 10],
    cleric:      [3, 6, 10],   // 3d6 x 10
    druid:       [3, 6, 10],
    magicuser:   [2, 4, 10],   // 2d4 x 10
    illusionist: [2, 4, 10],
    thief:       [2, 6, 10],   // 2d6 x 10
    assassin:    [2, 6, 10],
    monk:        [5, 4, 1],    // 5d4 (no multiplier)
    bard:        [2, 6, 10]
};

/**
 * Alignment restrictions by class.
 */
const CLASS_ALIGNMENTS = {
    fighter:     ['lg', 'ng', 'cg', 'ln', 'tn', 'cn', 'le', 'ne', 'ce'],
    paladin:     ['lg'],
    ranger:      ['lg', 'ng', 'cg'],
    cleric:      ['lg', 'ng', 'cg', 'ln', 'tn', 'cn', 'le', 'ne', 'ce'],
    druid:       ['tn'],
    magicuser:   ['lg', 'ng', 'cg', 'ln', 'tn', 'cn', 'le', 'ne', 'ce'],
    illusionist: ['lg', 'ng', 'cg', 'ln', 'tn', 'cn', 'le', 'ne', 'ce'],
    thief:       ['ln', 'tn', 'cn', 'le', 'ne', 'ce', 'ng', 'cg'],
    assassin:    ['le', 'ne', 'ce'],
    monk:        ['lg', 'ln', 'le'],
    bard:        ['tn']
};

const ALIGNMENT_LABELS = {
    lg: 'Lawful Good',
    ng: 'Neutral Good',
    cg: 'Chaotic Good',
    ln: 'Lawful Neutral',
    tn: 'True Neutral',
    cn: 'Chaotic Neutral',
    le: 'Lawful Evil',
    ne: 'Neutral Evil',
    ce: 'Chaotic Evil'
};

/**
 * Saving throw tables by class group.
 * Index 0 = level 1 values: [paralyzation, petrification, rod/staff/wand, breath weapon, spell]
 */
const SAVING_THROWS = {
    fighter:     [14, 15, 16, 17, 17],
    paladin:     [14, 15, 16, 17, 17],
    ranger:      [14, 15, 16, 17, 17],
    cleric:      [10, 13, 14, 16, 15],
    druid:       [10, 13, 14, 16, 15],
    magicuser:   [14, 13, 11, 15, 12],
    illusionist: [14, 13, 11, 15, 12],
    thief:       [13, 12, 14, 16, 15],
    assassin:    [13, 12, 14, 16, 15],
    monk:        [13, 12, 14, 16, 15],
    bard:        [13, 12, 14, 16, 15]
};

/**
 * Constitution HP adjustment table.
 * Key = CON score, value = HP adjustment per die.
 * For fighters (and subclasses), special bonuses apply at 17+.
 */
const CON_HP_ADJ = {
    3: -2, 4: -1, 5: -1, 6: -1,
    7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0,
    15: +1, 16: +2,
    17: +3,  // +2 for non-fighters
    18: +4,  // +2 for non-fighters
    19: +5   // +2 for non-fighters
};

const CON_HP_ADJ_NONFIGHTER = {
    3: -2, 4: -1, 5: -1, 6: -1,
    7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0,
    15: +1, 16: +2,
    17: +2, 18: +2, 19: +2
};

const FIGHTER_TYPES = ['fighter', 'paladin', 'ranger'];

/**
 * Exceptional strength table (fighters with 18 STR).
 * Only fighters, paladins, and rangers can have exceptional strength.
 */
const EXCEPTIONAL_STRENGTH_RANGES = [
    { min: 1,   max: 50,  label: '18/01-50' },
    { min: 51,  max: 75,  label: '18/51-75' },
    { min: 76,  max: 90,  label: '18/76-90' },
    { min: 91,  max: 99,  label: '18/91-99' },
    { min: 100, max: 100, label: '18/00' }
];

/**
 * Thief skill base percentages at level 1.
 */
const THIEF_SKILLS = {
    pickPockets: 30,
    openLocks: 25,
    findTraps: 20,
    moveSilently: 15,
    hideInShadows: 10,
    hearNoise: 10,
    climbWalls: 85,
    readLanguages: 0
};

const THIEF_SKILL_LABELS = {
    pickPockets: 'Pick Pockets',
    openLocks: 'Open Locks',
    findTraps: 'Find/Remove Traps',
    moveSilently: 'Move Silently',
    hideInShadows: 'Hide in Shadows',
    hearNoise: 'Hear Noise',
    climbWalls: 'Climb Walls',
    readLanguages: 'Read Languages'
};

/**
 * Racial thief skill adjustments.
 */
const RACIAL_THIEF_ADJ = {
    human:    { pickPockets: 0, openLocks: 0, findTraps: 0, moveSilently: 0, hideInShadows: 0, hearNoise: 0, climbWalls: 0, readLanguages: 0 },
    dwarf:    { pickPockets: 0, openLocks: 10, findTraps: 15, moveSilently: 0, hideInShadows: 0, hearNoise: 0, climbWalls: -10, readLanguages: -5 },
    elf:      { pickPockets: 5, openLocks: -5, findTraps: 0, moveSilently: 5, hideInShadows: 10, hearNoise: 5, climbWalls: 0, readLanguages: 0 },
    gnome:    { pickPockets: 0, openLocks: 5, findTraps: 10, moveSilently: 5, hideInShadows: 5, hearNoise: 10, climbWalls: -15, readLanguages: 0 },
    halfelf:  { pickPockets: 10, openLocks: 0, findTraps: 0, moveSilently: 0, hideInShadows: 5, hearNoise: 0, climbWalls: 0, readLanguages: 0 },
    halfling: { pickPockets: 5, openLocks: 5, findTraps: 5, moveSilently: 10, hideInShadows: 15, hearNoise: 5, climbWalls: -15, readLanguages: -5 },
    halforc:  { pickPockets: -5, openLocks: 5, findTraps: 5, moveSilently: 5, hideInShadows: 5, hearNoise: 5, climbWalls: 5, readLanguages: -10 }
};

/**
 * Dexterity thief skill adjustments.
 */
const DEX_THIEF_ADJ = {
    9:  { pickPockets: -15, openLocks: -10, findTraps: -10, moveSilently: -20, hideInShadows: -10 },
    10: { pickPockets: -10, openLocks: -5, findTraps: -10, moveSilently: -15, hideInShadows: -5 },
    11: { pickPockets: -5, openLocks: 0, findTraps: -5, moveSilently: -10, hideInShadows: 0 },
    12: { pickPockets: 0, openLocks: 0, findTraps: 0, moveSilently: -5, hideInShadows: 0 },
    13: { pickPockets: 0, openLocks: 0, findTraps: 0, moveSilently: 0, hideInShadows: 0 },
    14: { pickPockets: 0, openLocks: 0, findTraps: 0, moveSilently: 0, hideInShadows: 0 },
    15: { pickPockets: 0, openLocks: 0, findTraps: 0, moveSilently: 0, hideInShadows: 0 },
    16: { pickPockets: 0, openLocks: 5, findTraps: 0, moveSilently: 0, hideInShadows: 0 },
    17: { pickPockets: 5, openLocks: 10, findTraps: 0, moveSilently: 5, hideInShadows: 5 },
    18: { pickPockets: 10, openLocks: 15, findTraps: 5, moveSilently: 10, hideInShadows: 10 },
    19: { pickPockets: 15, openLocks: 20, findTraps: 10, moveSilently: 15, hideInShadows: 15 }
};

/**
 * Languages known based on Intelligence.
 */
const INT_LANGUAGES = {
    3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 1, 9: 1,
    10: 2, 11: 2, 12: 3, 13: 3, 14: 4, 15: 4,
    16: 5, 17: 6, 18: 7
};

/**
 * Racial languages.
 */
const RACIAL_LANGUAGES = {
    human: ['Common'],
    dwarf: ['Common', 'Dwarven', 'Gnome', 'Goblin', 'Kobold', 'Orcish'],
    elf: ['Common', 'Elven', 'Gnoll', 'Gnome', 'Goblin', 'Halfling', 'Hobgoblin', 'Orcish'],
    gnome: ['Common', 'Dwarven', 'Gnome', 'Goblin', 'Halfling', 'Kobold'],
    halfelf: ['Common', 'Elven', 'Gnome', 'Halfling', 'Goblin', 'Hobgoblin', 'Orcish'],
    halfling: ['Common', 'Dwarven', 'Elven', 'Gnome', 'Goblin', 'Halfling', 'Orcish'],
    halforc: ['Common', 'Orcish']
};

/**
 * Movement rates by race.
 */
const RACIAL_MOVEMENT = {
    human: 12,
    dwarf: 6,
    elf: 12,
    gnome: 6,
    halfelf: 12,
    halfling: 6,
    halforc: 12
};

/**
 * Age ranges by race/class for starting age.
 * Format: [baseAge, numDice, dieSize]
 */
const STARTING_AGE = {
    human:    { fighter: [15, 1, 4], paladin: [17, 1, 4], ranger: [20, 1, 4], cleric: [18, 1, 4], druid: [18, 2, 4], magicuser: [24, 2, 8], illusionist: [30, 1, 6], thief: [18, 1, 4], assassin: [20, 1, 4], monk: [21, 1, 4], bard: [18, 1, 4] },
    dwarf:    { fighter: [40, 5, 4], cleric: [250, 2, 20], thief: [75, 3, 6], assassin: [75, 4, 4] },
    elf:      { fighter: [130, 5, 6], ranger: [160, 1, 10], magicuser: [150, 5, 6], thief: [100, 5, 6], assassin: [100, 5, 6] },
    gnome:    { fighter: [60, 5, 4], cleric: [300, 3, 12], illusionist: [100, 2, 12], thief: [80, 5, 4], assassin: [80, 5, 4] },
    halfelf:  { fighter: [22, 3, 4], ranger: [30, 2, 4], cleric: [40, 2, 4], druid: [40, 2, 4], magicuser: [30, 2, 8], thief: [22, 3, 8], assassin: [30, 2, 4] },
    halfling: { fighter: [20, 3, 4], cleric: [30, 1, 4], thief: [40, 2, 4] },
    halforc:  { fighter: [13, 1, 4], cleric: [20, 1, 4], thief: [20, 2, 4], assassin: [20, 2, 4] }
};

/**
 * Height and weight by race and sex.
 * Format: [baseHeight (inches), heightDice, heightDie, baseWeight (lbs), weightDice, weightDie]
 */
const HEIGHT_WEIGHT = {
    human:    { male: [60, 2, 10, 140, 6, 10], female: [59, 2, 10, 100, 6, 10] },
    dwarf:    { male: [43, 1, 10, 130, 4, 10], female: [41, 1, 10, 105, 4, 10] },
    elf:      { male: [55, 1, 10, 90, 3, 10],  female: [50, 1, 10, 70, 3, 10] },
    gnome:    { male: [38, 1, 6, 72, 5, 4],     female: [36, 1, 6, 68, 5, 4] },
    halfelf:  { male: [60, 2, 6, 110, 3, 12],   female: [58, 2, 6, 85, 3, 12] },
    halfling: { male: [32, 2, 8, 52, 5, 4],     female: [30, 2, 8, 48, 5, 4] },
    halforc:  { male: [58, 2, 10, 120, 5, 10],  female: [56, 2, 10, 90, 5, 10] }
};
