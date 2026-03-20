# AD&D 1st Edition Complete Game System

## Project Structure
- `frontend/` - React 18 + TypeScript + Vite + Tailwind CSS
- `backend/` - Python FastAPI + SQLAlchemy + SQLite
- `electron/` - Electron main/preload for desktop packaging
- `modules/` - User drop-in adventure modules (JSON)
- `tests/` - Python unit/integration tests

## Development
```bash
# Backend
cd backend && pip install -r requirements.txt && uvicorn main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev

# Both (from root)
npm run dev
```

## Key Rules
- AD&D 1st Edition rules fidelity - use DMG as primary authority
- Combat matrices (not THAC0) are canonical - THAC0 is display convenience only
- Segment-based spell timing must be tracked
- Encumbrance affects movement rate
- All 6 DMG ability score generation methods must be available

## Tech Stack
- FastAPI backend on port 8000
- Vite dev server on port 5173 (proxies /api to backend)
- SQLite for game state persistence
- Zustand for frontend state
- HTML5 Canvas for dungeon map rendering
