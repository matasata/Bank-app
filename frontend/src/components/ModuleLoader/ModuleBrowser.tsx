import React, { useState } from 'react';
import { useGameStore } from '../../stores/gameStore';
import Panel from '../UI/Panel';
import type { ModuleMetadata } from '../../types';

// Sample modules for display
const SAMPLE_MODULES: ModuleMetadata[] = [
  {
    id: 'b1',
    code: 'B1',
    title: 'In Search of the Unknown',
    author: 'Mike Carr',
    levelRange: '1-3',
    playerCount: '3-6',
    description: 'The Doomed Fortress of Doomed Doominess... er, Quasqueton! This introductory module features the abandoned stronghold of two legendary adventurers, Rogahn the Fearless and Zelligar the Unknown. The dungeon is designed as a learning tool, presenting a variety of encounter situations.',
    version: '1.0',
  },
  {
    id: 'b2',
    code: 'B2',
    title: 'The Keep on the Borderlands',
    author: 'Gary Gygax',
    levelRange: '1-3',
    playerCount: '3-6',
    description: 'The most iconic introductory module in the history of the game. Features the legendary Caves of Chaos and the Keep, a base of operations for novice adventurers. Multiple factions of humanoids inhabit the caves.',
    version: '1.0',
  },
  {
    id: 't1',
    code: 'T1',
    title: 'The Village of Hommlet',
    author: 'Gary Gygax',
    levelRange: '1-3',
    playerCount: '4-8',
    description: 'The first part of the Temple of Elemental Evil saga. The village of Hommlet has grown prosperous after the defeat of the Temple, but evil stirs once more. A detailed village and a moathouse dungeon await.',
    version: '1.0',
  },
  {
    id: 's1',
    code: 'S1',
    title: 'Tomb of Horrors',
    author: 'Gary Gygax',
    levelRange: '10-14',
    playerCount: '4-8',
    description: 'The deadliest dungeon ever devised. The tomb of Acererak the demi-lich is a legendary deathtrap, filled with devious puzzles, false paths, and inescapable doom. Only the most skilled and careful adventurers will survive.',
    version: '1.0',
  },
  {
    id: 'g1',
    code: 'G1',
    title: 'Steading of the Hill Giant Chief',
    author: 'Gary Gygax',
    levelRange: '8-12',
    playerCount: '5-9',
    description: 'Hill giants have been raiding civilized lands. A party of adventurers is dispatched to deal with the menace. The first in the classic Against the Giants trilogy.',
    version: '1.0',
  },
  {
    id: 'd1',
    code: 'D1',
    title: 'Descent into the Depths of the Earth',
    author: 'Gary Gygax',
    levelRange: '9-14',
    playerCount: '5-9',
    description: 'Following the trail from the giant strongholds, adventurers descend into the Underdark. Vast caverns, strange ecosystems, and the drow await in this classic underground adventure.',
    version: '1.0',
  },
];

export const ModuleBrowser: React.FC = () => {
  const { addLogEntry } = useGameStore();
  const [selectedModule, setSelectedModule] = useState<ModuleMetadata | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [levelFilter, setLevelFilter] = useState('');

  const filteredModules = SAMPLE_MODULES.filter((mod) => {
    const matchesSearch = !searchQuery ||
      mod.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      mod.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      mod.author.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesLevel = !levelFilter || mod.levelRange.includes(levelFilter);

    return matchesSearch && matchesLevel;
  });

  const handleLoadModule = (module: ModuleMetadata) => {
    addLogEntry({
      type: 'system',
      message: `Module loaded: ${module.code} - ${module.title}`,
    });
    // In a real implementation, this would load the module data
    alert(`Module "${module.code} - ${module.title}" would be loaded here. This feature requires a backend connection.`);
  };

  return (
    <div className="p-4 space-y-6 max-h-[calc(100vh-120px)] overflow-y-auto">
      <div className="text-center">
        <h2 className="font-display text-xl text-gold mb-1">Module Library</h2>
        <p className="text-sm text-parchment/40 font-body">
          Browse and load classic AD&D modules for your campaign.
        </p>
      </div>

      {/* Search and Filter */}
      <div className="flex gap-3">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search modules..."
          className="
            flex-1 px-3 py-2 rounded
            bg-inkBlack/40 text-parchment border border-gold/20
            font-body text-sm placeholder-parchment/20
            focus:outline-none focus:border-gold/50
          "
        />
        <select
          value={levelFilter}
          onChange={(e) => setLevelFilter(e.target.value)}
          className="
            px-3 py-2 rounded text-sm
            bg-inkBlack/40 text-parchment border border-gold/20
            focus:outline-none focus:border-gold/50
          "
        >
          <option value="">All Levels</option>
          <option value="1">Level 1+</option>
          <option value="3">Level 3+</option>
          <option value="5">Level 5+</option>
          <option value="8">Level 8+</option>
          <option value="10">Level 10+</option>
        </select>
      </div>

      {/* Module Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredModules.map((module) => {
          const isSelected = selectedModule?.id === module.id;

          return (
            <button
              key={module.id}
              onClick={() => setSelectedModule(isSelected ? null : module)}
              className={`
                text-left p-4 rounded-lg border-2 transition-all duration-300
                ${isSelected
                  ? 'parchment-bg border-gold shadow-gold-glow'
                  : 'bg-darkWood/30 border-gold/15 hover:border-gold/40 hover:bg-darkWood/50'
                }
              `}
            >
              {/* Module Code Badge */}
              <div className="flex items-start justify-between mb-2">
                <span className={`
                  font-display text-lg font-bold px-2 py-0.5 rounded
                  ${isSelected
                    ? 'bg-burgundy text-gold'
                    : 'bg-burgundy/30 text-gold/70'
                  }
                `}>
                  {module.code}
                </span>
                <div className="text-right">
                  <span className={`text-[10px] font-display uppercase ${isSelected ? 'text-darkWood/50' : 'text-parchment/30'}`}>
                    Levels {module.levelRange}
                  </span>
                  <br />
                  <span className={`text-[10px] ${isSelected ? 'text-darkWood/40' : 'text-parchment/20'}`}>
                    {module.playerCount} players
                  </span>
                </div>
              </div>

              {/* Title and Author */}
              <h3 className={`font-display text-base font-bold mb-1 ${isSelected ? 'text-darkWood' : 'text-gold'}`}>
                {module.title}
              </h3>
              <p className={`text-xs mb-2 ${isSelected ? 'text-darkWood/50' : 'text-parchment/30'}`}>
                by {module.author}
              </p>

              {/* Description */}
              <p className={`text-xs font-body leading-relaxed ${isSelected ? 'text-darkWood/70' : 'text-parchment/40'}`}>
                {module.description}
              </p>

              {/* Load Button */}
              {isSelected && (
                <div className="mt-3 flex gap-2 animate-fade-in">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleLoadModule(module);
                    }}
                    className="btn-primary text-xs"
                  >
                    Load Module
                  </button>
                  <span className="text-[10px] text-darkWood/40 self-center">
                    v{module.version}
                  </span>
                </div>
              )}
            </button>
          );
        })}
      </div>

      {filteredModules.length === 0 && (
        <div className="text-center py-8">
          <p className="text-parchment/30 font-body">No modules match your search.</p>
        </div>
      )}

      {/* Custom Module Upload */}
      <Panel title="Custom Modules" variant="dark">
        <div className="p-4 text-center space-y-3">
          <p className="text-xs text-parchment/40 font-body">
            Upload custom module JSON files to add your own adventures.
          </p>
          <div className="border-2 border-dashed border-gold/20 rounded-lg p-6 hover:border-gold/40 transition-colors cursor-pointer">
            <input
              type="file"
              accept=".json"
              className="hidden"
              id="module-upload"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) {
                  addLogEntry({
                    type: 'system',
                    message: `Module file selected: ${file.name}`,
                  });
                }
              }}
            />
            <label htmlFor="module-upload" className="cursor-pointer">
              <span className="text-gold/50 font-display text-sm">
                Click to upload a module file
              </span>
              <br />
              <span className="text-[10px] text-parchment/20">
                Accepts .json format
              </span>
            </label>
          </div>
        </div>
      </Panel>
    </div>
  );
};

export default ModuleBrowser;
