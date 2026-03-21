#!/usr/bin/env bash
set -e

# AD&D 1st Edition Game System - One-Command Setup
# Usage: ./setup.sh

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[+]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
fail()  { echo -e "${RED}[✗]${NC} $1"; exit 1; }

echo ""
echo "==================================="
echo "  AD&D 1st Edition Game System"
echo "  One-Command Setup"
echo "==================================="
echo ""

# --- Check prerequisites ---

# Node.js
if ! command -v node &>/dev/null; then
  if command -v brew &>/dev/null; then
    info "Installing Node.js via Homebrew..."
    brew install node
  else
    fail "Node.js not found. Install it from https://nodejs.org or run: brew install node"
  fi
fi
NODE_VER=$(node -v | sed 's/v//' | cut -d. -f1)
if [ "$NODE_VER" -lt 18 ]; then
  fail "Node.js 18+ required (found v$NODE_VER). Update: brew upgrade node"
fi
info "Node.js $(node -v) ✓"

# Python 3
PYTHON=""
for cmd in python3 python; do
  if command -v "$cmd" &>/dev/null; then
    PY_VER=$("$cmd" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
    PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
    PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)
    if [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -ge 10 ]; then
      PYTHON="$cmd"
      break
    fi
  fi
done

if [ -z "$PYTHON" ]; then
  if command -v brew &>/dev/null; then
    info "Installing Python 3 via Homebrew..."
    brew install python@3.12
    PYTHON="python3"
  else
    fail "Python 3.10+ not found. Install it from https://python.org or run: brew install python@3.12"
  fi
fi
info "Python $($PYTHON --version) ✓"

# --- Install backend ---
info "Setting up Python virtual environment..."
cd backend
if [ ! -d "venv" ]; then
  $PYTHON -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
deactivate
cd ..
info "Backend dependencies installed ✓"

# --- Install frontend ---
info "Installing frontend dependencies..."
cd frontend
npm install --silent 2>/dev/null
cd ..
info "Frontend dependencies installed ✓"

# --- Install root (concurrently) ---
info "Installing dev tools..."
npm install --silent 2>/dev/null
info "Dev tools installed ✓"

echo ""
echo "==================================="
echo -e "  ${GREEN}Setup complete!${NC}"
echo "==================================="
echo ""
echo "  To start the game, run:"
echo ""
echo "    ./start.sh"
echo ""
echo "  Or manually:"
echo "    Terminal 1:  cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000"
echo "    Terminal 2:  cd frontend && npm run dev"
echo ""
echo "  Then open http://localhost:5173"
echo ""
