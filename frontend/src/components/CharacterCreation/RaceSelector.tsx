import React from 'react';
import { useCharacterStore, RACE_DATA } from '../../stores/characterStore';
import { useGameStore } from '../../stores/gameStore';
import type { Race, AbilityName } from '../../types';
import { ABILITY_NAMES } from '../../types';

export const RaceSelector: React.FC = () => {
  const {
    assignedAbilities, selectedRace, setRace, setStep,
    getAvailableRaces,
  } = useCharacterStore();
  const { addLogEntry } = useGameStore();

  const availableRaces = getAvailableRaces();
  const allRaces = Object.keys(RACE_DATA) as Race[];

  const handleSelect = (race: Race) => {
    setRace(race);
    addLogEntry({
      type: 'system',
      message: `Race selected: ${race}`,
    });
  };

  const handleConfirm = () => {
    if (selectedRace) {
      setStep(2);
    }
  };

  const formatModifier = (val: number) => {
    if (val > 0) return `+${val}`;
    return `${val}`;
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="font-display text-xl text-gold mb-2">Choose Your Race</h2>
        <p className="text-sm font-body text-parchment/50">
          Your ability scores determine which races are available to you.
        </p>
      </div>

      {/* Current abilities summary */}
      {assignedAbilities && (
        <div className="flex justify-center gap-3 flex-wrap">
          {ABILITY_NAMES.map((ability) => (
            <div key={ability} className="stat-box !min-w-[50px]">
              <span className="font-display text-[10px] font-semibold uppercase text-darkWood/60">
                {ability.slice(0, 3)}
              </span>
              <span className="font-display text-lg font-bold text-inkBlack">
                {assignedAbilities[ability]}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Race Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {allRaces.map((race) => {
          const info = RACE_DATA[race];
          const isAvailable = availableRaces.includes(race);
          const isSelected = selectedRace === race;

          return (
            <button
              key={race}
              onClick={() => isAvailable && handleSelect(race)}
              disabled={!isAvailable}
              className={`
                relative text-left p-4 rounded-lg border-2 transition-all duration-300
                ${isSelected
                  ? 'parchment-bg border-gold shadow-gold-glow'
                  : isAvailable
                    ? 'bg-darkWood/40 border-gold/20 hover:border-gold/50 hover:bg-darkWood/60'
                    : 'bg-inkBlack/30 border-parchment/10 opacity-40 cursor-not-allowed'
                }
              `}
            >
              {/* Race icon and name */}
              <div className="flex items-center gap-3 mb-3">
                <span className="text-3xl">{info.icon}</span>
                <div>
                  <h3 className={`font-display text-lg font-bold ${isSelected ? 'text-darkWood' : 'text-gold'}`}>
                    {race}
                  </h3>
                  <p className={`text-xs font-body ${isSelected ? 'text-darkWood/60' : 'text-parchment/40'}`}>
                    {info.description}
                  </p>
                </div>
              </div>

              {/* Ability adjustments */}
              {Object.keys(info.abilityAdjustments).length > 0 && (
                <div className="mb-2">
                  <span className={`text-xs font-display uppercase tracking-wider ${isSelected ? 'text-darkWood/50' : 'text-parchment/40'}`}>
                    Ability Adjustments:{' '}
                  </span>
                  {Object.entries(info.abilityAdjustments).map(([ability, adj]) => (
                    <span
                      key={ability}
                      className={`
                        inline-block px-1.5 py-0.5 rounded text-xs font-display font-bold mx-0.5
                        ${(adj as number) > 0
                          ? 'bg-forestGreen/20 text-green-400'
                          : 'bg-red-900/20 text-red-400'
                        }
                      `}
                    >
                      {ability.slice(0, 3).toUpperCase()} {formatModifier(adj as number)}
                    </span>
                  ))}
                </div>
              )}

              {/* Special abilities */}
              <div className="mb-2">
                <div className="flex flex-wrap gap-1">
                  {info.specialAbilities.slice(0, 3).map((sa, i) => (
                    <span
                      key={i}
                      className={`
                        text-[10px] px-1.5 py-0.5 rounded
                        ${isSelected
                          ? 'bg-darkWood/10 text-darkWood/70'
                          : 'bg-gold/10 text-gold/60'
                        }
                      `}
                    >
                      {sa}
                    </span>
                  ))}
                  {info.specialAbilities.length > 3 && (
                    <span className={`text-[10px] px-1 ${isSelected ? 'text-darkWood/40' : 'text-parchment/30'}`}>
                      +{info.specialAbilities.length - 3} more
                    </span>
                  )}
                </div>
              </div>

              {/* Allowed classes */}
              <div>
                <span className={`text-[10px] font-display uppercase tracking-wider ${isSelected ? 'text-darkWood/40' : 'text-parchment/30'}`}>
                  Classes:{' '}
                </span>
                <span className={`text-[10px] ${isSelected ? 'text-darkWood/60' : 'text-parchment/40'}`}>
                  {info.allowedClasses.join(', ')}
                </span>
              </div>

              {/* Infravision */}
              {info.infravision > 0 && (
                <div className="mt-1">
                  <span className={`text-[10px] ${isSelected ? 'text-darkWood/50' : 'text-parchment/40'}`}>
                    Infravision: {info.infravision} ft.
                  </span>
                </div>
              )}

              {/* Not available reason */}
              {!isAvailable && assignedAbilities && (
                <div className="absolute inset-0 flex items-center justify-center bg-inkBlack/60 rounded-lg">
                  <span className="text-xs font-display text-red-400 uppercase tracking-wider">
                    Requirements Not Met
                  </span>
                </div>
              )}

              {/* Selected indicator */}
              {isSelected && (
                <div className="absolute top-2 right-2">
                  <div className="w-6 h-6 rounded-full bg-gold flex items-center justify-center shadow-gold-glow">
                    <span className="text-darkWood text-sm font-bold">✓</span>
                  </div>
                </div>
              )}
            </button>
          );
        })}
      </div>

      {/* Navigation */}
      <div className="flex justify-between pt-4">
        <button onClick={() => setStep(0)} className="btn-secondary">
          Back to Abilities
        </button>
        <button
          onClick={handleConfirm}
          disabled={!selectedRace}
          className="btn-primary disabled:opacity-30 disabled:cursor-not-allowed"
        >
          Continue to Class Selection
        </button>
      </div>
    </div>
  );
};

export default RaceSelector;
