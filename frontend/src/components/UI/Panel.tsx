import React, { useState, useCallback, useRef, useEffect } from 'react';

interface PanelProps {
  title?: string;
  variant?: 'parchment' | 'dark' | 'wood';
  resizable?: boolean;
  collapsible?: boolean;
  defaultCollapsed?: boolean;
  minWidth?: number;
  minHeight?: number;
  maxWidth?: number;
  maxHeight?: number;
  className?: string;
  headerExtra?: React.ReactNode;
  children: React.ReactNode;
  onResize?: (width: number, height: number) => void;
}

const variantStyles = {
  parchment: 'parchment-bg text-inkBlack',
  dark: 'dark-panel text-parchment',
  wood: 'wood-panel text-parchment',
};

const headerVariantStyles = {
  parchment: 'bg-darkWood/90 text-gold border-b border-gold/40',
  dark: 'bg-inkBlack/80 text-gold border-b border-gold/30',
  wood: 'bg-darkWood text-gold border-b border-gold/40',
};

export const Panel: React.FC<PanelProps> = ({
  title,
  variant = 'dark',
  resizable = false,
  collapsible = false,
  defaultCollapsed = false,
  minWidth = 200,
  minHeight = 100,
  className = '',
  headerExtra,
  children,
  onResize,
}) => {
  const [collapsed, setCollapsed] = useState(defaultCollapsed);
  const [isResizing, setIsResizing] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);
  const startPos = useRef({ x: 0, y: 0, w: 0, h: 0 });

  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      if (!resizable || !panelRef.current) return;
      e.preventDefault();
      const rect = panelRef.current.getBoundingClientRect();
      startPos.current = { x: e.clientX, y: e.clientY, w: rect.width, h: rect.height };
      setIsResizing(true);
    },
    [resizable]
  );

  useEffect(() => {
    if (!isResizing) return;

    const handleMouseMove = (e: MouseEvent) => {
      if (!panelRef.current) return;
      const dw = e.clientX - startPos.current.x;
      const dh = e.clientY - startPos.current.y;
      const newW = Math.max(minWidth, startPos.current.w + dw);
      const newH = Math.max(minHeight, startPos.current.h + dh);
      panelRef.current.style.width = `${newW}px`;
      panelRef.current.style.height = `${newH}px`;
      onResize?.(newW, newH);
    };

    const handleMouseUp = () => setIsResizing(false);

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing, minWidth, minHeight, onResize]);

  return (
    <div
      ref={panelRef}
      className={`
        relative rounded-lg overflow-hidden shadow-panel
        ${variantStyles[variant]}
        ${className}
      `}
    >
      {title && (
        <div
          className={`
            flex items-center justify-between px-4 py-2
            font-display text-sm font-semibold tracking-wider uppercase
            ${headerVariantStyles[variant]}
          `}
        >
          <div className="flex items-center gap-2">
            {collapsible && (
              <button
                onClick={() => setCollapsed(!collapsed)}
                className="text-gold/70 hover:text-gold transition-colors w-5 text-center"
              >
                {collapsed ? '▶' : '▼'}
              </button>
            )}
            <span className="text-shadow-glow">{title}</span>
          </div>
          {headerExtra && <div className="flex items-center gap-2">{headerExtra}</div>}
        </div>
      )}

      {!collapsed && (
        <div className="relative z-10">
          {children}
        </div>
      )}

      {resizable && (
        <div
          onMouseDown={handleMouseDown}
          className="absolute bottom-0 right-0 w-4 h-4 cursor-se-resize opacity-50 hover:opacity-100 transition-opacity"
          style={{
            background: 'linear-gradient(135deg, transparent 50%, rgba(201,169,78,0.5) 50%)',
          }}
        />
      )}

      {/* Decorative corner elements */}
      <div className="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-gold/30 rounded-tl-lg pointer-events-none" />
      <div className="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-gold/30 rounded-tr-lg pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-gold/30 rounded-bl-lg pointer-events-none" />
      <div className="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-gold/30 rounded-br-lg pointer-events-none" />
    </div>
  );
};

export default Panel;
