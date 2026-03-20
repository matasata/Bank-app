import React from 'react';
import { useGameStore } from '../../stores/gameStore';
import Panel from './Panel';
import type { GameSettings } from '../../types';

export const SettingsPanel: React.FC = () => {
  const { settings, updateSettings, resetSettings, saveGame, saveSlots, deleteSave } = useGameStore();

  const Toggle: React.FC<{
    label: string;
    description?: string;
    checked: boolean;
    onChange: (val: boolean) => void;
  }> = ({ label, description, checked, onChange }) => (
    <div className="flex items-center justify-between py-2 border-b border-gold/10">
      <div>
        <span className="text-sm font-body text-parchment">{label}</span>
        {description && (
          <p className="text-xs text-parchment/40 mt-0.5">{description}</p>
        )}
      </div>
      <button
        onClick={() => onChange(!checked)}
        className={`
          relative w-11 h-6 rounded-full transition-colors duration-200
          ${checked
            ? 'bg-gradient-to-r from-forestGreen to-green-700'
            : 'bg-darkWood border border-parchment/20'
          }
        `}
      >
        <div
          className={`
            absolute top-0.5 w-5 h-5 rounded-full transition-transform duration-200
            ${checked
              ? 'translate-x-5 bg-gold shadow-gold-glow'
              : 'translate-x-0.5 bg-parchment/50'
            }
          `}
        />
      </button>
    </div>
  );

  const SelectOption: React.FC<{
    label: string;
    value: string;
    options: { value: string; label: string }[];
    onChange: (val: string) => void;
  }> = ({ label, value, options, onChange }) => (
    <div className="flex items-center justify-between py-2 border-b border-gold/10">
      <span className="text-sm font-body text-parchment">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="
          px-3 py-1 rounded text-sm font-body
          bg-inkBlack/50 text-parchment border border-gold/30
          focus:outline-none focus:border-gold/60
        "
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );

  const NumberInput: React.FC<{
    label: string;
    description?: string;
    value: number;
    min: number;
    max: number;
    onChange: (val: number) => void;
  }> = ({ label, description, value, min, max, onChange }) => (
    <div className="flex items-center justify-between py-2 border-b border-gold/10">
      <div>
        <span className="text-sm font-body text-parchment">{label}</span>
        {description && (
          <p className="text-xs text-parchment/40 mt-0.5">{description}</p>
        )}
      </div>
      <input
        type="number"
        value={value}
        min={min}
        max={max}
        onChange={(e) => onChange(parseInt(e.target.value, 10))}
        className="
          w-20 px-2 py-1 rounded text-sm font-body text-center
          bg-inkBlack/50 text-parchment border border-gold/30
          focus:outline-none focus:border-gold/60
        "
      />
    </div>
  );

  return (
    <div className="p-4 space-y-6 max-h-[calc(100vh-120px)] overflow-y-auto">
      {/* Game Rules */}
      <Panel title="Game Rules" variant="dark">
        <div className="p-4 space-y-1">
          <Toggle
            label="Critical Hits"
            description="Natural 20 deals double damage"
            checked={settings.criticalHitsEnabled}
            onChange={(val) => updateSettings({ criticalHitsEnabled: val })}
          />
          <Toggle
            label="Critical Fumbles"
            description="Natural 1 causes fumble effects"
            checked={settings.criticalFumbleEnabled}
            onChange={(val) => updateSettings({ criticalFumbleEnabled: val })}
          />
          <Toggle
            label="Encumbrance Rules"
            description="Track weight and movement penalties"
            checked={settings.encumbranceRulesEnabled}
            onChange={(val) => updateSettings({ encumbranceRulesEnabled: val })}
          />
          <Toggle
            label="Speed Factor Initiative"
            description="Weapon speed affects initiative order"
            checked={settings.speedFactorInitiativeEnabled}
            onChange={(val) => updateSettings({ speedFactorInitiativeEnabled: val })}
          />
          <Toggle
            label="Auto-Roll Monster HD"
            description="Automatically roll hit dice for monsters"
            checked={settings.autoRollMonsterHD}
            onChange={(val) => updateSettings({ autoRollMonsterHD: val })}
          />
        </div>
      </Panel>

      {/* Display Settings */}
      <Panel title="Display" variant="dark">
        <div className="p-4 space-y-1">
          <Toggle
            label="Show Damage Numbers"
            checked={settings.showDamageNumbers}
            onChange={(val) => updateSettings({ showDamageNumbers: val })}
          />
          <Toggle
            label="Animations"
            description="Enable dice and combat animations"
            checked={settings.animationsEnabled}
            onChange={(val) => updateSettings({ animationsEnabled: val })}
          />
          <SelectOption
            label="Font Size"
            value={settings.fontSize}
            options={[
              { value: 'small', label: 'Small' },
              { value: 'medium', label: 'Medium' },
              { value: 'large', label: 'Large' },
            ]}
            onChange={(val) => updateSettings({ fontSize: val as GameSettings['fontSize'] })}
          />
        </div>
      </Panel>

      {/* Sound Settings */}
      <Panel title="Audio" variant="dark">
        <div className="p-4">
          <Toggle
            label="Sound Effects"
            description="Play sound effects for actions and events"
            checked={settings.soundEffectsEnabled}
            onChange={(val) => updateSettings({ soundEffectsEnabled: val })}
          />
        </div>
      </Panel>

      {/* Auto-Save */}
      <Panel title="Auto-Save" variant="dark">
        <div className="p-4 space-y-1">
          <Toggle
            label="Auto-Save Enabled"
            checked={settings.autoSaveEnabled}
            onChange={(val) => updateSettings({ autoSaveEnabled: val })}
          />
          {settings.autoSaveEnabled && (
            <NumberInput
              label="Save Interval (minutes)"
              value={settings.autoSaveInterval}
              min={1}
              max={60}
              onChange={(val) => updateSettings({ autoSaveInterval: val })}
            />
          )}
        </div>
      </Panel>

      {/* Save Slots */}
      <Panel title="Save / Load" variant="dark">
        <div className="p-4 space-y-3">
          <div className="grid grid-cols-2 gap-2">
            {[1, 2, 3, 4, 5, 6].map((slot) => {
              const save = saveSlots.find((s) => s.slotNumber === slot);
              return (
                <div
                  key={slot}
                  className="
                    p-3 rounded border border-gold/20
                    bg-inkBlack/30 hover:bg-inkBlack/50
                    transition-colors
                  "
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-display text-xs text-gold font-semibold">
                      Slot {slot}
                    </span>
                    {save && (
                      <button
                        onClick={() => deleteSave(save.id)}
                        className="text-xs text-red-400/60 hover:text-red-400"
                        title="Delete save"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                  {save ? (
                    <div className="text-xs text-parchment/60 space-y-0.5">
                      <p className="truncate">{save.sessionName}</p>
                      <p>{save.partyLevel}</p>
                      <p className="text-parchment/30">{save.playTime}</p>
                    </div>
                  ) : (
                    <p className="text-xs text-parchment/20 italic">Empty</p>
                  )}
                  <button
                    onClick={() => saveGame(slot)}
                    className="
                      mt-2 w-full px-2 py-1 text-xs font-display
                      bg-darkWood/50 text-gold/70 border border-gold/20
                      rounded hover:bg-darkWood hover:text-gold
                      transition-colors
                    "
                  >
                    Save
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      </Panel>

      {/* Reset */}
      <div className="flex justify-center pt-2 pb-4">
        <button
          onClick={resetSettings}
          className="
            px-6 py-2 font-display text-sm tracking-wider uppercase
            bg-burgundy/30 text-parchment/60 border border-burgundy/50
            rounded hover:bg-burgundy/50 hover:text-parchment
            transition-colors
          "
        >
          Reset to Defaults
        </button>
      </div>
    </div>
  );
};

export default SettingsPanel;
