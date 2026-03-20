"""FastAPI router for treasure generation endpoints."""

from __future__ import annotations

from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from engine.treasure.generator import generate_treasure

router = APIRouter(prefix="/api/treasure", tags=["treasure"])


class GenerateTreasureRequest(BaseModel):
    """Request to generate treasure."""

    treasure_type: str = Field(..., min_length=1, max_length=1, description="Treasure type A-I")
    seed: Optional[int] = None


@router.post("/generate")
def generate(request: GenerateTreasureRequest) -> Dict:
    """Generate treasure from a DMG treasure type table.

    Returns coins, gems, jewelry, and magic items.
    """
    try:
        result = generate_treasure(
            treasure_type=request.treasure_type,
            seed=request.seed,
        )
        return result.as_dict()
    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
