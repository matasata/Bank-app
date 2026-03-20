import React, { useState } from 'react';
import { useDungeonStore } from '../../stores/dungeonStore';
import { useGameStore } from '../../stores/gameStore';
import Panel from '../UI/Panel';

export const DungeonControls: React.FC = () => {
  const {
    currentDungeon, isGenerating, generationParams,
    setGenerationParams, generateLocalDungeon, clearDungeon,
    showMinimap, showGrid, toggleMinimap, toggleGrid,
    selectedRoom, selectedDoor, interactWithDoor,
    explorationLog,
  } = useDungeonStore();
  const { addLogEntry } = useGameStore();

  const [showGenerate, setShowGenerate] = useState(!currentDungeon);

  const handleGenerate = () => {
    generateLocalDungeon();
    setShowGenerate(false);
    addLogEntry({
      type: 'exploration',
      message: `New dungeon generated: Level ${generationParams.dungeonLevel}`,
    });
  };

  return (
    <div className="space-y-3 p-3 h-full overflow-y-auto">
      {/* Generation Controls */}
      <Panel title="Dungeon" variant="dark" collapsible defaultCollapsed={!!currentDungeon}>
        <div className="p-3 space-y-3">
          {/* Parameters */}
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-[10px] font-display uppercase text-parchment/40 block mb-1">Width</label>
              <input
                type="number"
                value={generationParams.width}
                onChange={(e) => setGenerationParams({ width: parseInt(e.target.value) || 40 })}
                className="w-full px-2 py-1 rounded text-sm bg-inkBlack/40 text-parchment border border-gold/20 focus:border-gold/50 focus:outline-none"
                min={20} max={200}
              />
            </div>
            <div>
              <label className="text-[10px] font-display uppercase text-parchment/40 block mb-1">Height</label>
              <input
                type="number"
                value={generationParams.height}
                onChange={(e) => setGenerationParams({ height: parseInt(e.target.value) || 30 })}
                className="w-full px-2 py-1 rounded text-sm bg-inkBlack/40 text-parchment border border-gold/20 focus:border-gold/50 focus:outline-none"
                min={20} max={200}
              />
            </div>
            <div>
              <label className="text-[10px] font-display uppercase text-parchment/40 block mb-1">Rooms</label>
              <input
                type="number"
                value={generationParams.roomCount}
                onChange={(e) => setGenerationParams({ roomCount: parseInt(e.target.value) || 8 })}
                className="w-full px-2 py-1 rounded text-sm bg-inkBlack/40 text-parchment border border-gold/20 focus:border-gold/50 focus:outline-none"
                min={3} max={30}
              />
            </div>
            <div>
              <label className="text-[10px] font-display uppercase text-parchment/40 block mb-1">Level</label>
              <input
                type="number"
                value={generationParams.dungeonLevel}
                onChange={(e) => setGenerationParams({ dungeonLevel: parseInt(e.target.value) || 1 })}
                className="w-full px-2 py-1 rounded text-sm bg-inkBlack/40 text-parchment border border-gold/20 focus:border-gold/50 focus:outline-none"
                min={1} max={20}
              />
            </div>
          </div>

          {/* Sliders */}
          <div className="space-y-2">
            {[
              { label: 'Trap Density', key: 'trapDensity' as const },
              { label: 'Monster Density', key: 'monsterDensity' as const },
              { label: 'Treasure Density', key: 'treasureDensity' as const },
            ].map(({ label, key }) => (
              <div key={key}>
                <div className="flex justify-between">
                  <label className="text-[10px] font-display uppercase text-parchment/40">{label}</label>
                  <span className="text-[10px] text-parchment/40">{Math.round(generationParams[key] * 100)}%</span>
                </div>
                <input
                  type="range"
                  min={0} max={1} step={0.05}
                  value={generationParams[key]}
                  onChange={(e) => setGenerationParams({ [key]: parseFloat(e.target.value) })}
                  className="w-full h-1 bg-darkWood rounded-lg appearance-none cursor-pointer accent-gold"
                />
              </div>
            ))}
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleGenerate}
              disabled={isGenerating}
              className="flex-1 btn-primary disabled:opacity-50"
            >
              {isGenerating ? 'Generating...' : 'Generate Dungeon'}
            </button>
            {currentDungeon && (
              <button onClick={clearDungeon} className="btn-secondary">
                Clear
              </button>
            )}
          </div>
        </div>
      </Panel>

      {/* View Controls */}
      {currentDungeon && (
        <Panel title="View" variant="dark">
          <div className="p-3 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs text-parchment/60">Minimap</span>
              <button
                onClick={toggleMinimap}
                className={`px-3 py-1 rounded text-xs transition-colors ${
                  showMinimap ? 'bg-forestGreen/30 text-green-400' : 'bg-darkWood/30 text-parchment/40'
                }`}
              >
                {showMinimap ? 'ON' : 'OFF'}
              </button>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-parchment/60">Grid</span>
              <button
                onClick={toggleGrid}
                className={`px-3 py-1 rounded text-xs transition-colors ${
                  showGrid ? 'bg-forestGreen/30 text-green-400' : 'bg-darkWood/30 text-parchment/40'
                }`}
              >
                {showGrid ? 'ON' : 'OFF'}
              </button>
            </div>
          </div>
        </Panel>
      )}

      {/* Room Info */}
      {selectedRoom && (
        <Panel title={selectedRoom.name} variant="dark">
          <div className="p-3 space-y-2">
            <p className="text-sm text-parchment/70 font-body italic">
              {selectedRoom.description}
            </p>
            <div className="flex gap-3 text-[10px] text-parchment/40">
              <span>{selectedRoom.width}x{selectedRoom.height} ft</span>
              <span>Light: {selectedRoom.lightLevel}</span>
              {selectedRoom.isExplored && <span className="text-green-400">Explored</span>}
              {selectedRoom.isCleared && <span className="text-gold">Cleared</span>}
            </div>
            {selectedRoom.monsters.length > 0 && (
              <div className="text-xs text-red-400">
                Monsters: {selectedRoom.monsters.map((m) => m.name).join(', ')}
              </div>
            )}
          </div>
        </Panel>
      )}

      {/* Door Interaction */}
      {selectedDoor && (
        <Panel title="Door" variant="dark">
          <div className="p-3 space-y-2">
            <div className="flex gap-2 text-[10px] text-parchment/50">
              {selectedDoor.isLocked && <span className="text-yellow-400">Locked</span>}
              {selectedDoor.isTrapped && <span className="text-red-400">Trapped</span>}
              {selectedDoor.isSecret && <span className="text-purple-400">Secret</span>}
              {selectedDoor.isOpen && <span className="text-green-400">Open</span>}
              <span>HP: {selectedDoor.hitPoints}</span>
            </div>
            <div className="flex flex-wrap gap-1">
              {!selectedDoor.isOpen && (
                <button
                  onClick={() => interactWithDoor(selectedDoor.id, 'open')}
                  className="px-2 py-1 text-xs bg-forestGreen/30 text-green-400 border border-forestGreen/30 rounded hover:bg-forestGreen/50"
                >
                  Open
                </button>
              )}
              {selectedDoor.isOpen && (
                <button
                  onClick={() => interactWithDoor(selectedDoor.id, 'close')}
                  className="px-2 py-1 text-xs bg-darkWood/30 text-parchment/60 border border-gold/20 rounded hover:bg-darkWood/50"
                >
                  Close
                </button>
              )}
              {selectedDoor.isLocked && (
                <button
                  onClick={() => interactWithDoor(selectedDoor.id, 'unlock')}
                  className="px-2 py-1 text-xs bg-gold/20 text-gold border border-gold/30 rounded hover:bg-gold/30"
                >
                  Pick Lock
                </button>
              )}
              <button
                onClick={() => interactWithDoor(selectedDoor.id, 'bash')}
                className="px-2 py-1 text-xs bg-red-900/30 text-red-400 border border-red-400/30 rounded hover:bg-red-900/50"
              >
                Bash
              </button>
            </div>
          </div>
        </Panel>
      )}

      {/* Exploration Log */}
      <Panel title="Exploration" variant="dark">
        <div className="p-3 max-h-48 overflow-y-auto space-y-1">
          {explorationLog.length === 0 ? (
            <p className="text-xs text-parchment/20 italic">No exploration yet.</p>
          ) : (
            explorationLog.slice(-20).map((msg, i) => (
              <p key={i} className="text-xs text-parchment/50 font-body animate-slide-up">
                <span className="text-gold/40 mr-1">{'>'}</span>
                {msg}
              </p>
            ))
          )}
        </div>
      </Panel>
    </div>
  );
};

export default DungeonControls;
