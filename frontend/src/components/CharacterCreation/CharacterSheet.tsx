import React from 'react';
import type { Character, AbilityName } from '../../types';
import { ABILITY_NAMES } from '../../types';
import { getAbilityModifier } from '../../utils/dice';
import Panel from '../UI/Panel';

interface CharacterSheetProps {
  character: Character;
  compact?: boolean;
}

export const CharacterSheet: React.FC<CharacterSheetProps> = ({ character, compact = false }) => {
  const modifiers = ABILITY_NAMES.reduce((acc, ability) => {
    acc[ability] = getAbilityModifier(ability, character.abilityScores[ability]);
    return acc;
  }, {} as Record<AbilityName, Record<string, number>>);

  if (compact) {
    return (
      <div className="p-3 parchment-bg rounded-lg border-2 border-darkWood/40">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h3 className="font-display text-sm font-bold text-darkWood">{character.name}</h3>
            <p className="text-[10px] text-darkWood/60">
              {character.race} {character.className} Lvl {character.level}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div className="text-center">
              <span className="text-[10px] text-darkWood/40 block">HP</span>
              <span className={`font-display text-sm font-bold ${character.hitPoints <= character.maxHitPoints / 4 ? 'text-red-600' : 'text-darkWood'}`}>
                {character.hitPoints}/{character.maxHitPoints}
              </span>
            </div>
            <div className="text-center">
              <span className="text-[10px] text-darkWood/40 block">AC</span>
              <span className="font-display text-sm font-bold text-darkWood">{character.armorClass}</span>
            </div>
          </div>
        </div>
        <div className="flex gap-1">
          {ABILITY_NAMES.map((ability) => (
            <div key={ability} className="flex-1 text-center bg-white/30 rounded px-1 py-0.5">
              <span className="text-[8px] font-display uppercase text-darkWood/50 block">
                {ability.slice(0, 3)}
              </span>
              <span className="font-display text-xs font-bold text-darkWood">
                {character.abilityScores[ability]}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="parchment-bg rounded-lg border-2 border-darkWood/50 p-6 space-y-6">
      {/* Header - Name and Title Block */}
      <div className="text-center border-b-2 border-darkWood/30 pb-4">
        <h2 className="font-display text-2xl font-bold text-darkWood tracking-wider">
          {character.name}
        </h2>
        <p className="font-display text-sm text-darkWood/60 tracking-wider uppercase mt-1">
          {character.race} {character.className}
          {character.multiClass && ` / ${character.multiClass.join(' / ')}`}
        </p>
        <p className="text-xs text-darkWood/40 mt-1">
          Level {character.level} | {character.alignment} | XP: {character.experience.toLocaleString()}/{character.experienceNextLevel.toLocaleString()}
        </p>
      </div>

      {/* Ability Scores */}
      <div>
        <h3 className="font-display text-xs font-semibold uppercase tracking-[0.2em] text-darkWood/50 text-center mb-3">
          Ability Scores
        </h3>
        <div className="grid grid-cols-6 gap-2">
          {ABILITY_NAMES.map((ability) => (
            <div key={ability} className="stat-box">
              <span className="font-display text-[10px] font-bold uppercase text-darkWood/50 tracking-wider">
                {ability.slice(0, 3)}
              </span>
              <span className="font-display text-2xl font-bold text-inkBlack leading-tight">
                {character.abilityScores[ability]}
              </span>
              {character.exceptionalStrength && ability === 'strength' && character.abilityScores.strength === 18 && (
                <span className="text-[10px] font-display font-bold text-burgundy">
                  /{character.exceptionalStrength.percentile.toString().padStart(2, '0')}
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Combat Stats */}
      <div className="grid grid-cols-4 gap-3">
        <Panel title="HP" variant="parchment">
          <div className="text-center py-2">
            <span className={`font-display text-2xl font-bold ${character.hitPoints <= character.maxHitPoints / 4 ? 'text-red-600' : 'text-darkWood'}`}>
              {character.hitPoints}
            </span>
            <span className="text-darkWood/40 font-display text-sm">/{character.maxHitPoints}</span>
            {/* HP bar */}
            <div className="w-full h-2 bg-darkWood/20 rounded-full mt-2 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${
                  character.hitPoints / character.maxHitPoints > 0.5
                    ? 'bg-forestGreen'
                    : character.hitPoints / character.maxHitPoints > 0.25
                      ? 'bg-yellow-600'
                      : 'bg-red-600'
                }`}
                style={{ width: `${(character.hitPoints / character.maxHitPoints) * 100}%` }}
              />
            </div>
          </div>
        </Panel>
        <Panel title="AC" variant="parchment">
          <div className="text-center py-2">
            <span className="font-display text-3xl font-bold text-darkWood">{character.armorClass}</span>
          </div>
        </Panel>
        <Panel title="THAC0" variant="parchment">
          <div className="text-center py-2">
            <span className="font-display text-3xl font-bold text-darkWood">{character.thac0}</span>
          </div>
        </Panel>
        <Panel title="Move" variant="parchment">
          <div className="text-center py-2">
            <span className="font-display text-3xl font-bold text-darkWood">{character.movementRate}</span>
            <span className="text-[10px] text-darkWood/40 block">ft/round</span>
          </div>
        </Panel>
      </div>

      {/* Saving Throws */}
      <div>
        <h3 className="font-display text-xs font-semibold uppercase tracking-[0.2em] text-darkWood/50 text-center mb-3">
          Saving Throws
        </h3>
        <div className="grid grid-cols-5 gap-2">
          {Object.entries(character.savingThrows).map(([save, value]) => (
            <div key={save} className="stat-box">
              <span className="font-display text-[9px] font-bold uppercase text-darkWood/50 tracking-wider text-center leading-tight">
                {save === 'paralyzation' ? 'Para' :
                 save === 'poison' ? 'Poison' :
                 save === 'petrification' ? 'Petri' :
                 save === 'breath' ? 'Breath' : 'Spell'}
              </span>
              <span className="font-display text-xl font-bold text-inkBlack">{value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Equipment */}
      <div>
        <h3 className="font-display text-xs font-semibold uppercase tracking-[0.2em] text-darkWood/50 text-center mb-3">
          Equipment
        </h3>
        {character.equipment.length === 0 ? (
          <p className="text-center text-darkWood/30 text-sm italic">No equipment</p>
        ) : (
          <div className="space-y-1">
            {character.equipment.map((item) => (
              <div key={item.id} className="flex items-center justify-between px-3 py-1.5 bg-white/20 rounded">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-body text-darkWood">{item.name}</span>
                  {item.damage && (
                    <span className="text-[10px] px-1 py-0.5 rounded bg-red-100 text-red-700 font-mono">
                      {item.damage}
                    </span>
                  )}
                  {item.armorClass !== undefined && (
                    <span className="text-[10px] px-1 py-0.5 rounded bg-blue-100 text-blue-700 font-mono">
                      AC {item.armorClass}
                    </span>
                  )}
                </div>
                <span className="text-[10px] text-darkWood/40">{item.weight} cn</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Wealth */}
      <div className="flex justify-center gap-3">
        {[
          { label: 'PP', value: character.platinum },
          { label: 'GP', value: character.gold, highlight: true },
          { label: 'EP', value: character.electrum },
          { label: 'SP', value: character.silver },
          { label: 'CP', value: character.copper },
        ].map(({ label, value, highlight }) => (
          <div key={label} className="text-center">
            <span className="text-[9px] font-display uppercase text-darkWood/40 block">{label}</span>
            <span className={`font-display text-sm font-bold ${highlight ? 'text-gold' : 'text-darkWood'}`}>
              {value}
            </span>
          </div>
        ))}
      </div>

      {/* Special Abilities */}
      {character.specialAbilities.length > 0 && (
        <div>
          <h3 className="font-display text-xs font-semibold uppercase tracking-[0.2em] text-darkWood/50 text-center mb-2">
            Special Abilities
          </h3>
          <div className="flex flex-wrap gap-1 justify-center">
            {character.specialAbilities.map((ability, i) => (
              <span
                key={i}
                className="text-[10px] px-2 py-1 rounded bg-gold/10 text-darkWood/70 border border-darkWood/10"
              >
                {ability}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Languages */}
      {character.languages.length > 0 && (
        <div className="text-center">
          <span className="text-[10px] font-display uppercase text-darkWood/40">
            Languages:{' '}
          </span>
          <span className="text-xs text-darkWood/60">
            {character.languages.join(', ')}
          </span>
        </div>
      )}

      {/* Encumbrance */}
      <div className="text-center text-xs text-darkWood/40">
        <span>Encumbrance: {character.encumbrance} / {character.maxEncumbrance} cn</span>
        <div className="w-48 h-1.5 bg-darkWood/10 rounded-full mt-1 mx-auto overflow-hidden">
          <div
            className="h-full rounded-full bg-darkWood/40 transition-all"
            style={{ width: `${Math.min(100, (character.encumbrance / character.maxEncumbrance) * 100)}%` }}
          />
        </div>
      </div>

      {/* Status Conditions */}
      {character.conditions.length > 0 && (
        <div className="flex flex-wrap gap-1 justify-center">
          {character.conditions.map((condition) => (
            <span
              key={condition}
              className="text-[10px] px-2 py-1 rounded bg-red-900/20 text-red-400 border border-red-400/20 font-display uppercase"
            >
              {condition}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};

export default CharacterSheet;
