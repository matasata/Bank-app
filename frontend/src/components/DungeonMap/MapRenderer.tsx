import React, { useRef, useEffect, useState, useCallback } from 'react';
import { useDungeonStore } from '../../stores/dungeonStore';
import type { FogState, TileType } from '../../types';

const TILE_SIZE = 24;
const MINIMAP_SCALE = 3;

const TILE_COLORS: Record<TileType, string> = {
  wall: '#2C1B18',
  floor: '#8B7355',
  corridor: '#6B5B45',
  door: '#A0522D',
  'secret-door': '#6B5B45',
  'locked-door': '#8B4513',
  'stairs-up': '#4CAF50',
  'stairs-down': '#F44336',
  trap: '#8B7355', // same as floor when hidden
  water: '#1565C0',
  pit: '#1A1A2E',
  empty: '#000000',
};

const FOG_ALPHA: Record<FogState, number> = {
  unexplored: 1.0,
  explored: 0.5,
  visible: 0.0,
};

export const MapRenderer: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const minimapRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const {
    currentDungeon, viewportX, viewportY, zoom,
    setViewport, setZoom, showMinimap, showGrid,
    moveParty,
  } = useDungeonStore();

  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [canvasSize, setCanvasSize] = useState({ width: 800, height: 600 });

  // Resize observer
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        setCanvasSize({
          width: entry.contentRect.width,
          height: entry.contentRect.height,
        });
      }
    });
    observer.observe(container);
    return () => observer.disconnect();
  }, []);

  // Keyboard controls
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case 'ArrowUp': case 'w': case 'W':
          e.preventDefault(); moveParty('north'); break;
        case 'ArrowDown': case 's': case 'S':
          e.preventDefault(); moveParty('south'); break;
        case 'ArrowLeft': case 'a': case 'A':
          e.preventDefault(); moveParty('west'); break;
        case 'ArrowRight': case 'd': case 'D':
          e.preventDefault(); moveParty('east'); break;
        case '+': case '=':
          setZoom(zoom + 0.2); break;
        case '-':
          setZoom(zoom - 0.2); break;
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [moveParty, setZoom, zoom]);

  // Mouse drag for panning
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.button === 0) {
      setIsDragging(true);
      setDragStart({ x: e.clientX, y: e.clientY });
    }
  }, []);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDragging) return;
    const dx = (e.clientX - dragStart.x) / (TILE_SIZE * zoom);
    const dy = (e.clientY - dragStart.y) / (TILE_SIZE * zoom);
    setViewport(viewportX - dx, viewportY - dy);
    setDragStart({ x: e.clientX, y: e.clientY });
  }, [isDragging, dragStart, viewportX, viewportY, zoom, setViewport]);

  const handleMouseUp = useCallback(() => setIsDragging(false), []);

  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.15 : 0.15;
    setZoom(zoom + delta);
  }, [zoom, setZoom]);

  // Main canvas render
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !currentDungeon) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const { width, height } = canvasSize;
    canvas.width = width;
    canvas.height = height;

    const tileSize = TILE_SIZE * zoom;
    const offsetX = width / 2 - viewportX * tileSize;
    const offsetY = height / 2 - viewportY * tileSize;

    // Clear canvas
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, width, height);

    // Calculate visible range
    const startX = Math.max(0, Math.floor(-offsetX / tileSize));
    const startY = Math.max(0, Math.floor(-offsetY / tileSize));
    const endX = Math.min(currentDungeon.width, Math.ceil((width - offsetX) / tileSize));
    const endY = Math.min(currentDungeon.height, Math.ceil((height - offsetY) / tileSize));

    // Draw tiles
    for (let y = startY; y < endY; y++) {
      for (let x = startX; x < endX; x++) {
        const tile = currentDungeon.tiles[y]?.[x];
        if (!tile) continue;

        const px = x * tileSize + offsetX;
        const py = y * tileSize + offsetY;

        if (tile.fogState === 'unexplored') {
          ctx.fillStyle = '#000000';
          ctx.fillRect(px, py, tileSize, tileSize);
          continue;
        }

        // Draw tile
        ctx.fillStyle = TILE_COLORS[tile.type];
        ctx.fillRect(px, py, tileSize, tileSize);

        // Fog overlay for explored tiles
        if (tile.fogState === 'explored') {
          ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
          ctx.fillRect(px, py, tileSize, tileSize);
        }

        // Grid overlay
        if (showGrid && tile.type !== 'wall' && tile.fogState === 'visible') {
          ctx.strokeStyle = 'rgba(201, 169, 78, 0.1)';
          ctx.lineWidth = 0.5;
          ctx.strokeRect(px, py, tileSize, tileSize);
        }
      }
    }

    // Draw doors
    for (const door of currentDungeon.doors) {
      const tile = currentDungeon.tiles[door.y]?.[door.x];
      if (!tile || tile.fogState === 'unexplored') continue;

      const px = door.x * tileSize + offsetX;
      const py = door.y * tileSize + offsetY;

      if (door.isOpen) {
        ctx.fillStyle = '#6B5B45';
        ctx.fillRect(px, py, tileSize, tileSize);
        // Open door arc
        ctx.strokeStyle = '#A0522D';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(px, py, tileSize * 0.8, 0, Math.PI / 2);
        ctx.stroke();
      } else {
        ctx.fillStyle = door.isLocked ? '#8B4513' : '#A0522D';
        ctx.fillRect(px + 2, py + 2, tileSize - 4, tileSize - 4);

        // Door decoration
        ctx.strokeStyle = '#3E2723';
        ctx.lineWidth = 1;
        ctx.strokeRect(px + 2, py + 2, tileSize - 4, tileSize - 4);

        if (door.isLocked) {
          // Lock symbol
          ctx.fillStyle = '#FFD700';
          ctx.font = `${tileSize * 0.5}px serif`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText('🔒', px + tileSize / 2, py + tileSize / 2);
        }

        if (door.isSecret && tile.fogState === 'visible') {
          ctx.fillStyle = 'rgba(255, 0, 0, 0.5)';
          ctx.font = `${tileSize * 0.4}px monospace`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText('S', px + tileSize / 2, py + tileSize / 2);
        }
      }

      if (tile.fogState === 'explored') {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
        ctx.fillRect(px, py, tileSize, tileSize);
      }
    }

    // Draw party token
    const { x: partyX, y: partyY } = currentDungeon.partyPosition;
    const ppx = partyX * tileSize + offsetX + tileSize / 2;
    const ppy = partyY * tileSize + offsetY + tileSize / 2;
    const radius = tileSize * 0.35;

    // Glow
    const glow = ctx.createRadialGradient(ppx, ppy, 0, ppx, ppy, radius * 3);
    glow.addColorStop(0, 'rgba(201, 169, 78, 0.3)');
    glow.addColorStop(1, 'rgba(201, 169, 78, 0)');
    ctx.fillStyle = glow;
    ctx.beginPath();
    ctx.arc(ppx, ppy, radius * 3, 0, Math.PI * 2);
    ctx.fill();

    // Token
    ctx.fillStyle = '#C9A94E';
    ctx.beginPath();
    ctx.arc(ppx, ppy, radius, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#3E2723';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Direction indicator
    const facing = currentDungeon.partyFacing;
    const arrowLen = radius * 0.7;
    let ax = 0, ay = 0;
    switch (facing) {
      case 'north': ay = -arrowLen; break;
      case 'south': ay = arrowLen; break;
      case 'east': ax = arrowLen; break;
      case 'west': ax = -arrowLen; break;
    }
    ctx.strokeStyle = '#3E2723';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(ppx, ppy);
    ctx.lineTo(ppx + ax, ppy + ay);
    ctx.stroke();

  }, [currentDungeon, viewportX, viewportY, zoom, canvasSize, showGrid]);

  // Minimap render
  useEffect(() => {
    if (!showMinimap || !currentDungeon) return;
    const canvas = minimapRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const mw = currentDungeon.width * MINIMAP_SCALE;
    const mh = currentDungeon.height * MINIMAP_SCALE;
    canvas.width = mw;
    canvas.height = mh;

    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, mw, mh);

    for (let y = 0; y < currentDungeon.height; y++) {
      for (let x = 0; x < currentDungeon.width; x++) {
        const tile = currentDungeon.tiles[y]?.[x];
        if (!tile || tile.fogState === 'unexplored') continue;

        ctx.fillStyle = tile.type === 'wall' ? '#333' : '#888';
        if (tile.fogState === 'explored') {
          ctx.globalAlpha = 0.4;
        } else {
          ctx.globalAlpha = 1;
        }
        ctx.fillRect(x * MINIMAP_SCALE, y * MINIMAP_SCALE, MINIMAP_SCALE, MINIMAP_SCALE);
      }
    }

    // Party position on minimap
    ctx.globalAlpha = 1;
    ctx.fillStyle = '#C9A94E';
    ctx.fillRect(
      currentDungeon.partyPosition.x * MINIMAP_SCALE - 1,
      currentDungeon.partyPosition.y * MINIMAP_SCALE - 1,
      MINIMAP_SCALE + 2,
      MINIMAP_SCALE + 2
    );

    // Viewport indicator
    const tileSize = TILE_SIZE * zoom;
    const vw = canvasSize.width / tileSize;
    const vh = canvasSize.height / tileSize;
    ctx.strokeStyle = 'rgba(201, 169, 78, 0.5)';
    ctx.lineWidth = 1;
    ctx.strokeRect(
      (viewportX - vw / 2) * MINIMAP_SCALE,
      (viewportY - vh / 2) * MINIMAP_SCALE,
      vw * MINIMAP_SCALE,
      vh * MINIMAP_SCALE
    );
  }, [currentDungeon, showMinimap, viewportX, viewportY, zoom, canvasSize]);

  if (!currentDungeon) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <p className="font-display text-xl text-gold/50 mb-4">No Dungeon Loaded</p>
          <p className="text-sm text-parchment/30 font-body">
            Generate a dungeon or load a module to begin exploring.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="relative w-full h-full overflow-hidden bg-black cursor-crosshair"
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onWheel={handleWheel}
    >
      <canvas ref={canvasRef} className="w-full h-full" />

      {/* Minimap overlay */}
      {showMinimap && (
        <div className="absolute top-3 right-3 border-2 border-gold/40 rounded shadow-panel bg-black/80">
          <canvas ref={minimapRef} style={{ display: 'block' }} />
        </div>
      )}

      {/* Position and zoom info */}
      <div className="absolute bottom-3 left-3 text-[10px] font-mono text-parchment/30 space-y-0.5">
        <div>Position: ({currentDungeon.partyPosition.x}, {currentDungeon.partyPosition.y})</div>
        <div>Facing: {currentDungeon.partyFacing}</div>
        <div>Level: {currentDungeon.level}</div>
        <div>Zoom: {zoom.toFixed(1)}x</div>
      </div>

      {/* Movement controls (touch friendly) */}
      <div className="absolute bottom-3 right-3 grid grid-cols-3 gap-1">
        <div />
        <button
          onClick={() => moveParty('north')}
          className="w-9 h-9 rounded bg-darkWood/60 text-gold/70 hover:text-gold hover:bg-darkWood font-bold text-sm border border-gold/20"
        >
          N
        </button>
        <div />
        <button
          onClick={() => moveParty('west')}
          className="w-9 h-9 rounded bg-darkWood/60 text-gold/70 hover:text-gold hover:bg-darkWood font-bold text-sm border border-gold/20"
        >
          W
        </button>
        <div className="w-9 h-9 rounded bg-gold/20 flex items-center justify-center text-[10px] text-gold/50">
          ●
        </div>
        <button
          onClick={() => moveParty('east')}
          className="w-9 h-9 rounded bg-darkWood/60 text-gold/70 hover:text-gold hover:bg-darkWood font-bold text-sm border border-gold/20"
        >
          E
        </button>
        <div />
        <button
          onClick={() => moveParty('south')}
          className="w-9 h-9 rounded bg-darkWood/60 text-gold/70 hover:text-gold hover:bg-darkWood font-bold text-sm border border-gold/20"
        >
          S
        </button>
        <div />
      </div>
    </div>
  );
};

export default MapRenderer;
