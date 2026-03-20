import React from 'react';
import { useCharacterStore, CLASS_DATA, RACE_DATA } from '../../stores/characterStore';
import { useGameStore } from '../../stores/gameStore';
import type { CharacterClassName, AbilityName, Alignment } from '../../types';
import { ABILITY_NAMES, ALL_ALIGNMENTS } from '../../types';

const CLASS_ICONS: Record<CharacterClassName, string> = {
  'Fighter': '🗡️',
  'Paladin': '🛡️',
  'Ranger': '🏹',
  'Cleric': '✝️',
  'Druid': '🌳',
  'Magic-User': '🔮',
  'Illusionist': '✨',
  'Thief': '🗝️',
  'Assassin': '🗡️',
  'Monk': '👊',
};

export const ClassSelector: React.FC = () => {
  const {
    assignedAbilities, selectedRace, selectedClass, setClass,
    selectedAlignment, setAlignment,
    characterName, setCharacterName,
    getAvailableClasses, setStep,
  } = useCharacterStore();
  const { addLogEntry } = useGameStore();

  const availableClasses = getAvailableClasses();

  const handleSelectClass = (cls: CharacterClassName) => {
    setClass(cls);
    setAlignment(null);
    addLogEntry({
      type: 'system',
      message: `Class selected: ${cls}`,
    });
  };

  const handleConfirm = () => {
    if (selectedClass && selectedAlignment && characterName.trim()) {
      addLogEntry({
        type: 'system',
        message: `${characterName} the ${selectedRace} ${selectedClass} (${selectedAlignment}) is ready for equipment.`,
      });
      setStep(3);
    }
  };

  // Determine allowed alignments based on class
  const getAllowedAlignments = (): Alignment[] => {
    if (!selectedClass) return [];
    switch (selectedClass) {
      case 'Paladin': return ['Lawful Good'];
      case 'Ranger': return ['Lawful Good', 'Neutral Good', 'Chaotic Good'];
      case 'Druid': return ['True Neutral'];
      case 'Monk': return ['Lawful Good', 'Lawful Neutral', 'Lawful Evil'];
      case 'Assassin': return ['Neutral Evil', 'Lawful Evil', 'Chaotic Evil'];
      default: return ALL_ALIGNMENTS;
    }
  };

  const allowedAlignments = getAllowedAlignments();

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="font-display text-xl text-gold mb-2">Choose Your Class</h2>
        <p className="text-sm font-body text-parchment/50">
          As a {selectedRace}, select a class that suits your abilities.
        </p>
      </div>

      {/* Class Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {CLASS_DATA.map((cls) => {
          const isAvailable = availableClasses.includes(cls.name);
          const isSelected = selectedClass === cls.name;

          return (
            <button
              key={cls.name}
              onClick={() => isAvailable && handleSelectClass(cls.name)}
              disabled={!isAvailable}
              className={`
                relative text-left p-4 rounded-lg border-2 transition-all duration-300
                ${isSelected
                  ? 'parchment-bg border-gold shadow-gold-glow'
                  : isAvailable
                    ? 'bg-darkWood/40 border-gold/20 hover:border-gold/50 hover:bg-darkWood/60'
                    : 'bg-inkBlack/30 border-parchment/10 opacity-30 cursor-not-allowed'
                }
              `}
            >
              <div className="flex items-start gap-3">
                <span className="text-2xl mt-1">{CLASS_ICONS[cls.name]}</span>
                <div className="flex-1">
                  <h3 className={`font-display text-base font-bold ${isSelected ? 'text-darkWood' : 'text-gold'}`}>
                    {cls.name}
                  </h3>
                  <p className={`text-xs font-body mt-1 ${isSelected ? 'text-darkWood/60' : 'text-parchment/40'}`}>
                    {cls.description}
                  </p>

                  {/* Hit Dice */}
                  <div className="mt-2 flex items-center gap-3">
                    <span className={`text-xs font-display ${isSelected ? 'text-darkWood/50' : 'text-parchment/40'}`}>
                      HD: <span className="font-bold">{cls.hitDice}</span>
                    </span>
                  </div>

                  {/* Requirements */}
                  <div className="mt-1 flex flex-wrap gap-1">
                    {Object.entries(cls.requirements).map(([ability, min]) => {
                      const score = assignedAbilities?.[ability as AbilityName] ?? 0;
                      const met = score >= (min as number);
                      return (
                        <span
                          key={ability}
                          className={`
                            text-[10px] px-1.5 py-0.5 rounded font-display font-bold
                            ${met
                              ? isSelected
                                ? 'bg-forestGreen/20 text-forestGreen'
                                : 'bg-forestGreen/20 text-green-400'
                              : 'bg-red-900/30 text-red-400'
                            }
                          `}
                        >
                          {ability.slice(0, 3).toUpperCase()} {min}+
                        </span>
                      );
                    })}
                  </div>

                  {/* Prime requisites */}
                  <div className="mt-1">
                    <span className={`text-[10px] ${isSelected ? 'text-darkWood/40' : 'text-parchment/30'}`}>
                      Prime: {cls.primeRequisites.map((p) => p.slice(0, 3).toUpperCase()).join(', ')}
                    </span>
                  </div>
                </div>
              </div>

              {isSelected && (
                <div className="absolute top-2 right-2 w-6 h-6 rounded-full bg-gold flex items-center justify-center shadow-gold-glow">
                  <span className="text-darkWood text-sm font-bold">✓</span>
                </div>
              )}
            </button>
          );
        })}
      </div>

      {/* Alignment Selection */}
      {selectedClass && (
        <div className="space-y-3 animate-fade-in">
          <h3 className="font-display text-sm text-gold/70 text-center tracking-wider uppercase">
            Choose Alignment
          </h3>
          <div className="grid grid-cols-3 gap-2 max-w-md mx-auto">
            {ALL_ALIGNMENTS.map((alignment) => {
              const isAllowed = allowedAlignments.includes(alignment);
              const isChosen = selectedAlignment === alignment;
              return (
                <button
                  key={alignment}
                  onClick={() => isAllowed && setAlignment(alignment)}
                  disabled={!isAllowed}
                  className={`
                    px-2 py-2 rounded text-xs font-body text-center transition-all
                    ${isChosen
                      ? 'bg-burgundy text-gold border border-gold shadow-gold-glow'
                      : isAllowed
                        ? 'bg-darkWood/30 text-parchment/60 border border-gold/15 hover:border-gold/40'
                        : 'bg-inkBlack/20 text-parchment/15 border border-transparent cursor-not-allowed'
                    }
                  `}
                >
                  {alignment}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Character Name */}
      {selectedClass && selectedAlignment && (
        <div className="space-y-3 animate-fade-in max-w-md mx-auto">
          <h3 className="font-display text-sm text-gold/70 text-center tracking-wider uppercase">
            Name Your Character
          </h3>
          <input
            type="text"
            value={characterName}
            onChange={(e) => setCharacterName(e.target.value)}
            placeholder="Enter character name..."
            className="
              w-full px-4 py-3 rounded-lg text-center
              bg-inkBlack/40 text-parchment border-2 border-gold/30
              font-display text-lg placeholder-parchment/20
              focus:outline-none focus:border-gold/60 focus:shadow-gold-glow
              transition-all
            "
          />
        </div>
      )}

      {/* Navigation */}
      <div className="flex justify-between pt-4">
        <button onClick={() => setStep(1)} className="btn-secondary">
          Back to Race
        </button>
        <button
          onClick={handleConfirm}
          disabled={!selectedClass || !selectedAlignment || !characterName.trim()}
          className="btn-primary disabled:opacity-30 disabled:cursor-not-allowed"
        >
          Continue to Equipment
        </button>
      </div>
    </div>
  );
};

export default ClassSelector;
