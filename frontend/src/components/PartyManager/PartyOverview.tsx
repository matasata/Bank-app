import React, { useState } from 'react';
import { useCharacterStore } from '../../stores/characterStore';
import { useGameStore } from '../../stores/gameStore';
import Panel from '../UI/Panel';
import CharacterSheet from '../CharacterCreation/CharacterSheet';
import type { Character } from '../../types';

export const PartyOverview: React.FC = () => {
  const { characters, removeCharacter, selectCharacter, selectedCharacterId } = useCharacterStore();
  const { party, updateMarchingOrder } = useGameStore();
  const [detailCharacter, setDetailCharacter] = useState<Character | null>(null);

  const marchingOrder = party?.marchingOrder || { front: [], middle: [], rear: [] };

  const handleDragStart = (e: React.DragEvent, charId: string) => {
    e.dataTransfer.setData('text/plain', charId);
  };

  const handleDrop = (e: React.DragEvent, position: 'front' | 'middle' | 'rear') => {
    e.preventDefault();
    const charId = e.dataTransfer.getData('text/plain');
    if (!charId) return;

    // Remove from all positions
    const newOrder = {
      front: marchingOrder.front.filter((id) => id !== charId),
      middle: marchingOrder.middle.filter((id) => id !== charId),
      rear: marchingOrder.rear.filter((id) => id !== charId),
    };
    // Add to new position
    newOrder[position].push(charId);
    updateMarchingOrder(newOrder);
  };

  const handleDragOver = (e: React.DragEvent) => e.preventDefault();

  if (characters.length === 0) {
    return (
      <div className="flex items-center justify-center h-full p-8">
        <div className="text-center space-y-4">
          <p className="font-display text-xl text-gold/40">No Party Members</p>
          <p className="text-sm text-parchment/30 font-body">
            Create characters in the Character Creation tab to form your adventuring party.
          </p>
        </div>
      </div>
    );
  }

  // Detail view
  if (detailCharacter) {
    return (
      <div className="p-4 space-y-4 max-h-[calc(100vh-120px)] overflow-y-auto">
        <button
          onClick={() => setDetailCharacter(null)}
          className="btn-secondary text-xs"
        >
          Back to Party
        </button>
        <CharacterSheet character={detailCharacter} />
      </div>
    );
  }

  return (
    <div className="p-4 space-y-6 max-h-[calc(100vh-120px)] overflow-y-auto">
      {/* Party Summary */}
      <div className="text-center">
        <h2 className="font-display text-xl text-gold mb-1">The Adventuring Party</h2>
        <p className="text-sm text-parchment/40">
          {characters.length} member{characters.length !== 1 ? 's' : ''}
        </p>
      </div>

      {/* Character Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {characters.map((char) => (
          <div
            key={char.id}
            draggable
            onDragStart={(e) => handleDragStart(e, char.id)}
            className={`
              relative cursor-pointer transition-all duration-200
              hover:shadow-gold-glow hover:scale-[1.02]
              ${selectedCharacterId === char.id ? 'ring-2 ring-gold' : ''}
            `}
          >
            <CharacterSheet character={char} compact />

            {/* Action overlay on hover */}
            <div className="absolute inset-0 bg-inkBlack/0 hover:bg-inkBlack/40 rounded-lg transition-all flex items-center justify-center opacity-0 hover:opacity-100 gap-2">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setDetailCharacter(char);
                }}
                className="px-3 py-1.5 text-xs font-display bg-darkWood/80 text-gold border border-gold/40 rounded hover:bg-darkWood"
              >
                Details
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  selectCharacter(char.id);
                }}
                className="px-3 py-1.5 text-xs font-display bg-forestGreen/50 text-green-300 border border-green-400/30 rounded hover:bg-forestGreen/70"
              >
                Select
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  if (confirm(`Remove ${char.name} from the party?`)) {
                    removeCharacter(char.id);
                  }
                }}
                className="px-3 py-1.5 text-xs font-display bg-red-900/50 text-red-400 border border-red-400/30 rounded hover:bg-red-900/70"
              >
                Remove
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Marching Order */}
      <Panel title="Marching Order" variant="dark">
        <div className="p-4">
          <p className="text-xs text-parchment/40 mb-3 text-center">
            Drag characters to set their position in the marching order.
          </p>
          <div className="grid grid-cols-3 gap-3">
            {(['front', 'middle', 'rear'] as const).map((position) => (
              <div
                key={position}
                onDrop={(e) => handleDrop(e, position)}
                onDragOver={handleDragOver}
                className="
                  min-h-[100px] rounded-lg border-2 border-dashed border-gold/20
                  bg-inkBlack/20 p-2 transition-colors
                  hover:border-gold/40 hover:bg-inkBlack/30
                "
              >
                <h4 className="font-display text-[10px] uppercase tracking-wider text-gold/50 text-center mb-2">
                  {position}
                </h4>
                <div className="space-y-1">
                  {marchingOrder[position].map((charId) => {
                    const char = characters.find((c) => c.id === charId);
                    if (!char) return null;
                    return (
                      <div
                        key={charId}
                        className="px-2 py-1 rounded bg-darkWood/30 text-xs text-parchment/70 text-center border border-gold/10"
                      >
                        {char.name}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      </Panel>

      {/* Party Stats */}
      <Panel title="Party Statistics" variant="dark">
        <div className="p-4 grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="text-center">
            <span className="text-[10px] font-display uppercase text-parchment/40 block">Total HP</span>
            <span className="font-display text-lg font-bold text-parchment">
              {characters.reduce((s, c) => s + c.hitPoints, 0)}/{characters.reduce((s, c) => s + c.maxHitPoints, 0)}
            </span>
          </div>
          <div className="text-center">
            <span className="text-[10px] font-display uppercase text-parchment/40 block">Avg Level</span>
            <span className="font-display text-lg font-bold text-parchment">
              {(characters.reduce((s, c) => s + c.level, 0) / characters.length).toFixed(1)}
            </span>
          </div>
          <div className="text-center">
            <span className="text-[10px] font-display uppercase text-parchment/40 block">Party Gold</span>
            <span className="font-display text-lg font-bold text-gold">
              {characters.reduce((s, c) => s + c.gold, 0)}
            </span>
          </div>
          <div className="text-center">
            <span className="text-[10px] font-display uppercase text-parchment/40 block">Best AC</span>
            <span className="font-display text-lg font-bold text-parchment">
              {Math.min(...characters.map((c) => c.armorClass))}
            </span>
          </div>
        </div>
      </Panel>
    </div>
  );
};

export default PartyOverview;
