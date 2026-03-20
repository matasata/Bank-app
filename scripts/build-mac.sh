#!/bin/bash
set -e

echo "Building AD&D Game System for macOS..."

# Build frontend
cd frontend
npm run build
cd ..

# Package with electron-builder
npx electron-builder --mac

echo "macOS build complete! Check dist/ directory."
