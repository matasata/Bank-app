import React, { useEffect } from 'react';
import { useGameStore } from './stores/gameStore';
import { useCharacterStore } from './stores/characterStore';
import type { AppView } from './types';

// Components
import AbilityScoreRoller from './components/CharacterCreation/AbilityScoreRoller';
import RaceSelector from './components/CharacterCreation/RaceSelector';
import ClassSelector from './components/CharacterCreation/ClassSelector';
import EquipmentShop from './components/CharacterCreation/EquipmentShop';
import CharacterSheet from './components/CharacterCreation/CharacterSheet';
import MapRenderer from './components/DungeonMap/MapRenderer';
import DungeonControls from './components/DungeonMap/DungeonControls';
import CombatPanel from './components/CombatTracker/CombatPanel';
import PartyOverview from './components/PartyManager/PartyOverview';
import ModuleBrowser from './components/ModuleLoader/ModuleBrowser';
import DiceRoller from './components/UI/DiceRoller';
import Panel from './components/UI/Panel';
import ActionLog from './components/UI/ActionLog';
import SettingsPanel from './components/UI/SettingsPanel';

const NAV_TABS: { id: AppView; label: string; icon: string }[] = [
  { id: 'character-creation', label: 'Characters', icon: '📜' },
  { id: 'dungeon', label: 'Dungeon', icon: '🏰' },
  { id: 'combat', label: 'Combat', icon: '⚔️' },
  { id: 'party', label: 'Party', icon: '👥' },
  { id: 'modules', label: 'Modules', icon: '📚' },
  { id: 'settings', label: 'Settings', icon: '⚙️' },
];

// ─── Character Creation View ──────────────────────────────────────────────────

const CharacterCreationView: React.FC = () => {
  const { step, characters } = useCharacterStore();

  const STEPS = [
    { label: 'Abilities', component: <AbilityScoreRoller /> },
    { label: 'Race', component: <RaceSelector /> },
    { label: 'Class', component: <ClassSelector /> },
    { label: 'Equipment', component: <EquipmentShop /> },
  ];

  return (
    <div className="h-full flex gap-4 p-4">
      {/* Main creation panel */}
      <div className="flex-1 overflow-y-auto">
        <Panel title={`Character Creation - ${STEPS[step]?.label || 'Complete'}`} variant="dark">
          <div className="p-6">
            {/* Step indicator */}
            <div className="flex items-center justify-center gap-2 mb-6">
              {STEPS.map((s, i) => (
                <React.Fragment key={i}>
                  <div className={`
                    w-8 h-8 rounded-full flex items-center justify-center text-xs font-display font-bold
                    transition-all duration-300
                    ${i === step
                      ? 'bg-gold text-darkWood shadow-gold-glow'
                      : i < step
                        ? 'bg-forestGreen text-parchment'
                        : 'bg-darkWood/50 text-parchment/30'
                    }
                  `}>
                    {i < step ? '✓' : i + 1}
                  </div>
                  {i < STEPS.length - 1 && (
                    <div className={`w-12 h-0.5 ${i < step ? 'bg-forestGreen' : 'bg-darkWood/30'}`} />
                  )}
                </React.Fragment>
              ))}
            </div>

            {/* Step content */}
            {step < STEPS.length ? STEPS[step].component : (
              <div className="text-center space-y-4">
                <h2 className="font-display text-xl text-gold">Character Created!</h2>
                <p className="text-parchment/50 font-body">
                  Your character has been added to the party.
                </p>
                <button
                  onClick={() => useCharacterStore.getState().resetCreation()}
                  className="btn-primary"
                >
                  Create Another Character
                </button>
              </div>
            )}
          </div>
        </Panel>
      </div>

      {/* Existing characters sidebar */}
      {characters.length > 0 && (
        <div className="w-72 flex-shrink-0 overflow-y-auto space-y-3">
          <Panel title={`Party (${characters.length})`} variant="dark">
            <div className="p-3 space-y-2">
              {characters.map((char) => (
                <CharacterSheet key={char.id} character={char} compact />
              ))}
            </div>
          </Panel>
        </div>
      )}
    </div>
  );
};

// ─── Dungeon View ─────────────────────────────────────────────────────────────

const DungeonView: React.FC = () => {
  return (
    <div className="h-full flex gap-0">
      {/* Map (left) */}
      <div className="flex-1 relative">
        <MapRenderer />
      </div>
      {/* Controls (right) */}
      <div className="w-80 flex-shrink-0 border-l border-gold/20 overflow-hidden">
        <DungeonControls />
      </div>
    </div>
  );
};

// ─── Combat View ──────────────────────────────────────────────────────────────

const CombatView: React.FC = () => {
  return (
    <div className="h-full">
      <CombatPanel />
    </div>
  );
};

// ─── Main App ─────────────────────────────────────────────────────────────────

const App: React.FC = () => {
  const { currentView, setView, createSession, session, addLogEntry } = useGameStore();

  // Auto-create session on first load
  useEffect(() => {
    if (!session) {
      createSession('New Campaign');
    }
  }, [session, createSession]);

  const renderView = () => {
    switch (currentView) {
      case 'character-creation':
        return <CharacterCreationView />;
      case 'dungeon':
        return <DungeonView />;
      case 'combat':
        return <CombatView />;
      case 'party':
        return <PartyOverview />;
      case 'modules':
        return <ModuleBrowser />;
      case 'settings':
        return <SettingsPanel />;
      default:
        return <CharacterCreationView />;
    }
  };

  return (
    <div className="h-screen flex flex-col bg-inkBlack text-parchment overflow-hidden">
      {/* ─── Top Navigation Bar ──────────────────────────────────── */}
      <header className="flex-shrink-0 wood-panel border-b-2 border-gold/40">
        <div className="flex items-center justify-between px-4 py-2">
          {/* Title */}
          <div className="flex items-center gap-3">
            <h1 className="font-display text-lg font-bold gold-text tracking-wider">
              AD&D
            </h1>
            <span className="text-[10px] font-display uppercase tracking-[0.3em] text-parchment/30">
              1st Edition
            </span>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex items-center gap-1">
            {NAV_TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setView(tab.id)}
                className={`
                  flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-display
                  font-semibold tracking-wider uppercase transition-all duration-200
                  ${currentView === tab.id
                    ? 'bg-burgundy/50 text-gold border border-gold/40 shadow-gold-glow'
                    : 'text-parchment/40 hover:text-parchment/70 hover:bg-darkWood/50'
                  }
                `}
              >
                <span className="text-sm">{tab.icon}</span>
                <span className="hidden md:inline">{tab.label}</span>
              </button>
            ))}
          </nav>

          {/* Quick Dice Roller */}
          <div className="flex items-center gap-3">
            <DiceRoller
              compact
              onRoll={(result) => {
                addLogEntry({
                  type: 'dice',
                  message: `Quick roll: ${result.rolls.join(', ')} = ${result.finalTotal}`,
                });
              }}
            />
          </div>
        </div>
      </header>

      {/* ─── Main Content Area ───────────────────────────────────── */}
      <div className="flex-1 flex overflow-hidden">
        {/* Primary content area */}
        <main className="flex-1 overflow-hidden">
          {renderView()}
        </main>
      </div>

      {/* ─── Bottom Panel: Action Log ────────────────────────────── */}
      <div className="flex-shrink-0 h-36 dark-panel border-t border-gold/20">
        <ActionLog showTimestamp />
      </div>
    </div>
  );
};

export default App;
