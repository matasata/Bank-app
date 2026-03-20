"""FastAPI router for adventure module management.

Handles loading, listing, and validating user-provided adventure
modules from the ``modules/`` directory.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, status
from pydantic import BaseModel

router = APIRouter(prefix="/api/modules", tags=["modules"])

# Resolve modules directory relative to the project root
_MODULES_DIR = Path(__file__).resolve().parent.parent.parent / "modules"


def _scan_modules() -> List[Dict]:
    """Scan the modules directory for valid JSON module files."""
    modules: List[Dict] = []
    if not _MODULES_DIR.exists():
        return modules

    for fp in sorted(_MODULES_DIR.glob("*.json")):
        try:
            data = json.loads(fp.read_text())
            modules.append({
                "filename": fp.name,
                "name": data.get("name", fp.stem),
                "author": data.get("author", "Unknown"),
                "description": data.get("description", ""),
                "min_level": data.get("min_level", 1),
                "max_level": data.get("max_level", 20),
                "num_encounters": len(data.get("encounters", [])),
                "num_rooms": len(data.get("rooms", [])),
                "valid": True,
            })
        except (json.JSONDecodeError, Exception) as exc:
            modules.append({
                "filename": fp.name,
                "name": fp.stem,
                "valid": False,
                "error": str(exc),
            })

    return modules


@router.get("/")
def list_modules() -> List[Dict]:
    """List all available adventure modules in the modules directory."""
    return _scan_modules()


@router.get("/{filename}")
def get_module(filename: str) -> Dict:
    """Load and return a specific module by filename."""
    fp = _MODULES_DIR / filename
    if not fp.exists() or not fp.suffix == ".json":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module '{filename}' not found",
        )

    # Prevent path traversal
    try:
        fp.resolve().relative_to(_MODULES_DIR.resolve())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid module path",
        )

    try:
        data = json.loads(fp.read_text())
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Module is not valid JSON: {exc}",
        )

    return {
        "filename": fp.name,
        "module": data,
    }


@router.post("/upload")
async def upload_module(file: UploadFile = File(...)) -> Dict:
    """Upload a new adventure module JSON file."""
    if not file.filename or not file.filename.endswith(".json"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Module must be a .json file",
        )

    content = await file.read()

    # Validate JSON
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON: {exc}",
        )

    # Validate required fields
    if "name" not in data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Module must have a 'name' field",
        )

    # Save to modules directory
    _MODULES_DIR.mkdir(parents=True, exist_ok=True)
    dest = _MODULES_DIR / file.filename
    dest.write_bytes(content)

    return {
        "message": f"Module '{data['name']}' uploaded successfully",
        "filename": file.filename,
        "name": data["name"],
    }


@router.delete("/{filename}")
def delete_module(filename: str) -> Dict:
    """Delete an adventure module."""
    fp = _MODULES_DIR / filename
    if not fp.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module '{filename}' not found",
        )

    # Prevent path traversal
    try:
        fp.resolve().relative_to(_MODULES_DIR.resolve())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid module path",
        )

    fp.unlink()
    return {"message": f"Module '{filename}' deleted"}
