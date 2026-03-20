import React, { useState, useMemo } from 'react';
import { useCharacterStore } from '../../stores/characterStore';
import { useGameStore } from '../../stores/gameStore';
import type { EquipmentItem, EquipmentCategory } from '../../types';
import { rollDie } from '../../utils/dice';

// ─── Sample Equipment Data ────────────────────────────────────────────────────

const EQUIPMENT_CATALOG: EquipmentItem[] = [
  // Weapons
  { id: 'longsword', name: 'Longsword', category: 'Weapon', cost: 15, weight: 60, damage: '1d8', speed: 5, description: 'A versatile one-handed blade.', quantity: 1 },
  { id: 'shortsword', name: 'Short Sword', category: 'Weapon', cost: 8, weight: 35, damage: '1d6', speed: 3, description: 'A quick thrusting blade.', quantity: 1 },
  { id: 'twohanded', name: 'Two-Handed Sword', category: 'Weapon', cost: 30, weight: 100, damage: '1d10', speed: 10, description: 'A massive blade requiring both hands.', quantity: 1 },
  { id: 'battleaxe', name: 'Battle Axe', category: 'Weapon', cost: 5, weight: 75, damage: '1d8', speed: 7, description: 'A fearsome chopping weapon.', quantity: 1 },
  { id: 'mace', name: 'Mace', category: 'Weapon', cost: 8, weight: 50, damage: '1d6+1', speed: 7, description: 'A heavy bludgeoning weapon.', quantity: 1 },
  { id: 'warhammer', name: 'War Hammer', category: 'Weapon', cost: 2, weight: 50, damage: '1d6+1', speed: 4, description: 'Effective against armored foes.', quantity: 1 },
  { id: 'flail', name: 'Flail', category: 'Weapon', cost: 3, weight: 35, damage: '1d6+1', speed: 7, description: 'A chain weapon that wraps around shields.', quantity: 1 },
  { id: 'dagger', name: 'Dagger', category: 'Weapon', cost: 2, weight: 10, damage: '1d4', speed: 2, description: 'A small blade, easily concealed.', quantity: 1 },
  { id: 'spear', name: 'Spear', category: 'Weapon', cost: 1, weight: 50, damage: '1d6', speed: 6, description: 'A versatile reach weapon.', quantity: 1 },
  { id: 'longbow', name: 'Long Bow', category: 'Weapon', cost: 60, weight: 50, damage: '1d6', description: 'A powerful ranged weapon.', quantity: 1 },
  { id: 'shortbow', name: 'Short Bow', category: 'Weapon', cost: 15, weight: 50, damage: '1d6', description: 'A compact ranged weapon.', quantity: 1 },
  { id: 'crossbow-lt', name: 'Light Crossbow', category: 'Weapon', cost: 12, weight: 50, damage: '1d4+1', description: 'Mechanical ranged weapon.', quantity: 1 },
  { id: 'sling', name: 'Sling', category: 'Weapon', cost: 0.05, weight: 1, damage: '1d4', description: 'A simple projectile weapon.', quantity: 1 },
  { id: 'staff', name: 'Quarterstaff', category: 'Weapon', cost: 0, weight: 40, damage: '1d6', speed: 4, description: 'A simple wooden staff.', quantity: 1 },

  // Armor
  { id: 'leather', name: 'Leather Armor', category: 'Armor', cost: 5, weight: 150, armorClass: 8, description: 'Light, flexible protection.', quantity: 1 },
  { id: 'studded', name: 'Studded Leather', category: 'Armor', cost: 15, weight: 200, armorClass: 7, description: 'Leather reinforced with metal studs.', quantity: 1 },
  { id: 'ringmail', name: 'Ring Mail', category: 'Armor', cost: 30, weight: 250, armorClass: 7, description: 'Rings sewn onto a leather backing.', quantity: 1 },
  { id: 'scalemail', name: 'Scale Mail', category: 'Armor', cost: 45, weight: 400, armorClass: 6, description: 'Overlapping metal scales on leather.', quantity: 1 },
  { id: 'chainmail', name: 'Chain Mail', category: 'Armor', cost: 75, weight: 300, armorClass: 5, description: 'Interlocking metal rings.', quantity: 1 },
  { id: 'splintmail', name: 'Splint Mail', category: 'Armor', cost: 80, weight: 400, armorClass: 4, description: 'Vertical metal strips on chain.', quantity: 1 },
  { id: 'platemail', name: 'Plate Mail', category: 'Armor', cost: 400, weight: 450, armorClass: 3, description: 'Full metal plate protection.', quantity: 1 },

  // Shields
  { id: 'shield-sm', name: 'Small Shield', category: 'Shield', cost: 10, weight: 50, armorClass: -1, description: 'A buckler-style shield (-1 AC).', quantity: 1 },
  { id: 'shield-lg', name: 'Large Shield', category: 'Shield', cost: 15, weight: 100, armorClass: -1, description: 'A full-size shield (-1 AC).', quantity: 1 },

  // Ammunition
  { id: 'arrows-20', name: 'Arrows (20)', category: 'Ammunition', cost: 2, weight: 30, description: 'A quiver of 20 arrows.', quantity: 1 },
  { id: 'bolts-20', name: 'Crossbow Bolts (20)', category: 'Ammunition', cost: 2, weight: 20, description: 'A case of 20 bolts.', quantity: 1 },
  { id: 'sling-stones', name: 'Sling Stones (20)', category: 'Ammunition', cost: 0, weight: 20, description: 'A pouch of smooth stones.', quantity: 1 },

  // Adventuring Gear
  { id: 'backpack', name: 'Backpack', category: 'Adventuring Gear', cost: 2, weight: 20, description: 'A sturdy leather backpack.', quantity: 1 },
  { id: 'rope-50', name: 'Rope (50 ft)', category: 'Adventuring Gear', cost: 1, weight: 75, description: 'Hemp rope, 50 feet.', quantity: 1 },
  { id: 'torches-6', name: 'Torches (6)', category: 'Adventuring Gear', cost: 0.06, weight: 50, description: 'Bundle of 6 torches.', quantity: 1 },
  { id: 'lantern', name: 'Lantern', category: 'Adventuring Gear', cost: 7, weight: 30, description: 'A hooded lantern.', quantity: 1 },
  { id: 'oil-flask', name: 'Oil Flask', category: 'Adventuring Gear', cost: 0.1, weight: 10, description: 'A flask of lamp oil.', quantity: 1 },
  { id: 'tinderbox', name: 'Tinderbox', category: 'Adventuring Gear', cost: 1, weight: 2, description: 'Flint and steel for fire-making.', quantity: 1 },
  { id: 'rations-7', name: 'Iron Rations (1 week)', category: 'Adventuring Gear', cost: 5, weight: 75, description: 'Preserved food for one week.', quantity: 1 },
  { id: 'waterskin', name: 'Waterskin', category: 'Adventuring Gear', cost: 1, weight: 30, description: 'A leather water container.', quantity: 1 },
  { id: 'thieves-tools', name: "Thieves' Tools", category: 'Adventuring Gear', cost: 30, weight: 10, description: 'Lockpicks and other tools of the trade.', quantity: 1 },
  { id: 'holy-symbol', name: 'Holy Symbol', category: 'Adventuring Gear', cost: 25, weight: 1, description: 'A silver holy symbol.', quantity: 1 },
  { id: 'spellbook', name: 'Spellbook (blank)', category: 'Adventuring Gear', cost: 25, weight: 30, description: 'A blank book for recording spells.', quantity: 1 },
  { id: 'mirror', name: 'Mirror, Small Steel', category: 'Adventuring Gear', cost: 10, weight: 5, description: 'A small polished steel mirror.', quantity: 1 },
  { id: 'pole-10', name: '10-foot Pole', category: 'Adventuring Gear', cost: 0.02, weight: 50, description: 'A wooden pole for probing ahead.', quantity: 1 },
  { id: 'pitons-12', name: 'Iron Spikes (12)', category: 'Adventuring Gear', cost: 0.05, weight: 50, description: 'A dozen iron spikes.', quantity: 1 },
  { id: 'hammer', name: 'Hammer', category: 'Adventuring Gear', cost: 0.5, weight: 20, description: 'A small hammer for spikes.', quantity: 1 },
  { id: 'grapple', name: 'Grappling Hook', category: 'Adventuring Gear', cost: 2, weight: 40, description: 'An iron grappling hook.', quantity: 1 },
];

const CATEGORIES: EquipmentCategory[] = [
  'Weapon', 'Armor', 'Shield', 'Ammunition', 'Adventuring Gear',
];

export const EquipmentShop: React.FC = () => {
  const { gold, setGold, selectedEquipment, addEquipment, removeEquipment, setStep, finalizeCharacter } = useCharacterStore();
  const { addLogEntry, addCharacter } = useGameStore();
  const [activeCategory, setActiveCategory] = useState<EquipmentCategory>('Weapon');
  const [hasRolledGold, setHasRolledGold] = useState(false);

  const filteredItems = useMemo(
    () => EQUIPMENT_CATALOG.filter((item) => item.category === activeCategory),
    [activeCategory]
  );

  const totalWeight = useMemo(
    () => selectedEquipment.reduce((sum, item) => sum + item.weight * item.quantity, 0),
    [selectedEquipment]
  );

  const rollStartingGold = () => {
    // Roll 3d6 * 10 for starting gold
    const roll = rollDie(6) + rollDie(6) + rollDie(6);
    const startingGold = roll * 10;
    setGold(startingGold);
    setHasRolledGold(true);
    addLogEntry({
      type: 'dice',
      message: `Starting gold: ${roll} x 10 = ${startingGold} gp`,
    });
  };

  const handleBuy = (item: EquipmentItem) => {
    if (gold < item.cost) return;
    const purchaseItem = { ...item, id: `${item.id}-${Date.now()}` };
    addEquipment(purchaseItem);
    addLogEntry({
      type: 'loot',
      message: `Purchased ${item.name} for ${item.cost} gp`,
    });
  };

  const handleRemove = (item: EquipmentItem) => {
    removeEquipment(item.id);
    addLogEntry({
      type: 'loot',
      message: `Returned ${item.name}, refunded ${item.cost} gp`,
    });
  };

  const handleFinalize = () => {
    const character = finalizeCharacter();
    if (character) {
      addCharacter(character);
      addLogEntry({
        type: 'system',
        message: `${character.name} the ${character.race} ${character.className} has been created!`,
      });
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="font-display text-xl text-gold mb-2">Equipment Shop</h2>
        <p className="text-sm font-body text-parchment/50">
          Outfit your character for the dungeons ahead.
        </p>
      </div>

      {/* Gold Display */}
      <div className="flex items-center justify-center gap-6">
        {!hasRolledGold ? (
          <button onClick={rollStartingGold} className="btn-primary">
            Roll Starting Gold (3d6 x 10)
          </button>
        ) : (
          <>
            <div className="stat-box">
              <span className="font-display text-[10px] uppercase text-darkWood/60">Gold</span>
              <span className="font-display text-2xl font-bold text-gold">{gold.toFixed(1)}</span>
              <span className="text-[10px] text-darkWood/40">gp</span>
            </div>
            <div className="stat-box">
              <span className="font-display text-[10px] uppercase text-darkWood/60">Weight</span>
              <span className="font-display text-lg font-bold text-inkBlack">{totalWeight}</span>
              <span className="text-[10px] text-darkWood/40">cn</span>
            </div>
            <div className="stat-box">
              <span className="font-display text-[10px] uppercase text-darkWood/60">Items</span>
              <span className="font-display text-lg font-bold text-inkBlack">{selectedEquipment.length}</span>
            </div>
          </>
        )}
      </div>

      {hasRolledGold && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Category Tabs + Item List */}
          <div className="lg:col-span-2 space-y-3">
            {/* Category tabs */}
            <div className="flex flex-wrap gap-1">
              {CATEGORIES.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setActiveCategory(cat)}
                  className={`
                    px-3 py-1.5 rounded text-xs font-display font-semibold tracking-wider uppercase
                    transition-all
                    ${activeCategory === cat
                      ? 'bg-burgundy text-gold border border-gold/40'
                      : 'bg-darkWood/30 text-parchment/50 hover:text-parchment/80'
                    }
                  `}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Item list */}
            <div className="space-y-1 max-h-96 overflow-y-auto pr-2">
              {filteredItems.map((item) => {
                const canAfford = gold >= item.cost;
                return (
                  <div
                    key={item.id}
                    className={`
                      flex items-center justify-between p-3 rounded-lg border
                      transition-all
                      ${canAfford
                        ? 'bg-darkWood/30 border-gold/15 hover:border-gold/40'
                        : 'bg-inkBlack/20 border-parchment/5 opacity-50'
                      }
                    `}
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-display text-sm font-semibold text-parchment">
                          {item.name}
                        </span>
                        {item.damage && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-red-900/20 text-red-400 font-mono">
                            {item.damage}
                          </span>
                        )}
                        {item.armorClass !== undefined && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-900/20 text-blue-400 font-mono">
                            AC {item.armorClass}
                          </span>
                        )}
                      </div>
                      <p className="text-[10px] text-parchment/40 mt-0.5">{item.description}</p>
                      <div className="flex gap-3 mt-1 text-[10px] text-parchment/30">
                        <span>Weight: {item.weight} cn</span>
                        {item.speed && <span>Speed: {item.speed}</span>}
                      </div>
                    </div>
                    <div className="flex items-center gap-3 ml-4">
                      <span className="font-display text-sm font-bold text-gold whitespace-nowrap">
                        {item.cost} gp
                      </span>
                      <button
                        onClick={() => handleBuy(item)}
                        disabled={!canAfford}
                        className="
                          px-3 py-1 text-xs font-display
                          bg-forestGreen/30 text-green-400 border border-forestGreen/40
                          rounded hover:bg-forestGreen/50
                          disabled:opacity-30 disabled:cursor-not-allowed
                          transition-colors
                        "
                      >
                        Buy
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Inventory */}
          <div className="space-y-3">
            <h3 className="font-display text-sm text-gold/70 tracking-wider uppercase text-center">
              Your Equipment
            </h3>
            <div className="space-y-1 max-h-96 overflow-y-auto">
              {selectedEquipment.length === 0 ? (
                <p className="text-center text-parchment/30 text-sm italic py-8">
                  No equipment purchased yet.
                </p>
              ) : (
                selectedEquipment.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center justify-between p-2 rounded bg-darkWood/20 border border-gold/10"
                  >
                    <div>
                      <span className="text-sm text-parchment font-body">{item.name}</span>
                      <span className="text-[10px] text-parchment/30 ml-2">{item.weight} cn</span>
                    </div>
                    <button
                      onClick={() => handleRemove(item)}
                      className="text-xs text-red-400/60 hover:text-red-400 px-2 transition-colors"
                      title="Remove item"
                    >
                      ✕
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Navigation */}
      <div className="flex justify-between pt-4">
        <button onClick={() => setStep(2)} className="btn-secondary">
          Back to Class
        </button>
        <button
          onClick={handleFinalize}
          disabled={!hasRolledGold}
          className="btn-primary disabled:opacity-30 disabled:cursor-not-allowed"
        >
          Finalize Character
        </button>
      </div>
    </div>
  );
};

export default EquipmentShop;
