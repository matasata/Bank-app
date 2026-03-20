import { useState } from 'react';
import AbilityScoreRoller from './components/CharacterCreation/AbilityScoreRoller';
import RaceSelector from './components/CharacterCreation/RaceSelector';
import ClassSelector from './components/CharacterCreation/ClassSelector';
import CharacterSheet from './components/CharacterCreation/CharacterSheet';
import EquipmentShop from './components/CharacterCreation/EquipmentShop';
import MapRenderer from './components/DungeonMap/MapRenderer';
import DungeonControls from './components/DungeonMap/DungeonControls';
import InitiativeTracker from './components/CombatTracker/InitiativeTracker';
import CombatPanel from './components/CombatTracker/CombatPanel';
import CombatLog from './components/CombatTracker/CombatLog';
import PartyOverview from './components/PartyManager/PartyOverview';
import ModuleBrowser from './components/ModuleLoader/ModuleBrowser';
import Panel from './components/UI/Panel';
import ActionLog from './components/UI/ActionLog';
import SettingsPanel from './components/UI/SettingsPanel';
import { useGameStore } from './stores/gameStore';

type Tab = 'character' | 'dungeon' | 'combat' | 'party' | 'modules' | 'settings';

const TABS: { id: Tab; label: string }[] = [
  { id: 'character', label: 'Character Creation' },
  { id: 'dungeon', label: 'Dungeon' },
  { id: 'combat', label: 'Combat' },
  { id: 'party', label: 'Party' },
  { id: 'modules', label: 'Modules' },
  { id: 'settings', label: 'Settings' },
];

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('character');
  const [charStep, setCharStep] = useState(0);
  const actionLog = useGameStore((s) => s.actionLog);

  return (
    <div className="min-h-screen bg-inkBlack text-parchment font-body flex flex-col">
      {/* Top Navigation */}
      <header className="bg-darkWood border-b-2 border-gold/40 px-4 py-2 flex items-center gap-4 shadow-lg">
        <h1 className="font-display text-2xl text-gold tracking-wider mr-6">
          AD&D 1st Edition
        </h1>
        <nav className="flex gap-1">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-t font-display text-sm tracking-wide transition-colors
                ${activeTab === tab.id
                  ? 'bg-burgundy text-parchment border-b-2 border-gold'
                  : 'text-parchment/60 hover:text-parchment hover:bg-darkWood/80'
                }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </header>

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-auto p-4">
            {activeTab === 'character' && (
              <div className="space-y-4">
                {/* Step indicator */}
                <div className="flex gap-2 mb-4">
                  {['Abilities', 'Race', 'Class', 'Equipment', 'Sheet'].map((step, i) => (
                    <button
                      key={step}
                      onClick={() => setCharStep(i)}
                      className={`px-3 py-1 rounded text-sm font-display ${
                        charStep === i
                          ? 'bg-burgundy text-parchment'
                          : 'bg-darkWood/50 text-parchment/50 hover:text-parchment'
                      }`}
                    >
                      {i + 1}. {step}
                    </button>
                  ))}
                </div>

                {charStep === 0 && <AbilityScoreRoller onComplete={() => setCharStep(1)} />}
                {charStep === 1 && <RaceSelector onComplete={() => setCharStep(2)} />}
                {charStep === 2 && <ClassSelector onComplete={() => setCharStep(3)} />}
                {charStep === 3 && <EquipmentShop onComplete={() => setCharStep(4)} />}
                {charStep === 4 && <CharacterSheet />}
              </div>
            )}

            {activeTab === 'dungeon' && (
              <div className="flex gap-4 h-full">
                <div className="flex-1">
                  <MapRenderer />
                </div>
                <div className="w-80">
                  <DungeonControls />
                </div>
              </div>
            )}

            {activeTab === 'combat' && (
              <div className="flex gap-4 h-full">
                <div className="flex-1 space-y-4">
                  <InitiativeTracker />
                  <CombatPanel />
                </div>
                <div className="w-96">
                  <CombatLog />
                </div>
              </div>
            )}

            {activeTab === 'party' && <PartyOverview />}
            {activeTab === 'modules' && <ModuleBrowser />}
            {activeTab === 'settings' && <SettingsPanel />}
          </div>

          {/* Bottom Panel - Action Log */}
          <Panel title="Action Log" collapsible defaultHeight={180}>
            <ActionLog entries={actionLog} />
          </Panel>
        </div>

        {/* Right Panel - Party Info (always visible) */}
        <aside className="w-72 bg-darkWood/30 border-l border-gold/20 p-3 overflow-auto hidden lg:block">
          <h2 className="font-display text-gold text-lg mb-3">Party</h2>
          <PartyOverview compact />
        </aside>
      </div>
    </div>
  );
}

export default App;
