#!/bin/bash
set -e

echo "Building AD&D Game System for Windows..."

# Build frontend
cd frontend
npm run build
cd ..

# Package with electron-builder
npx electron-builder --win

echo "Windows build complete! Check dist/ directory."
