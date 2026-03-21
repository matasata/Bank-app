#!/usr/bin/env bash
set -e

# AD&D 1st Edition Game System - Start
# Launches backend + frontend together

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# Activate venv for backend if it exists
if [ -d "backend/venv" ]; then
  export PATH="$DIR/backend/venv/bin:$PATH"
fi

echo ""
echo "Starting AD&D Game System..."
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop."
echo ""

npx concurrently \
  --names "API,WEB" \
  --prefix-colors "yellow,cyan" \
  "cd backend && source venv/bin/activate 2>/dev/null; uvicorn main:app --reload --port 8000" \
  "cd frontend && npm run dev"
