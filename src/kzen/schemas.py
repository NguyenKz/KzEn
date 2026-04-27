"""Pydantic models (không chứa enum — enum nằm trong enums.py)."""
from __future__ import annotations

from pydantic import BaseModel, Field

from .enums import DiffType, IouLevel


class DiffResult(BaseModel):
    ref_text: str
    stt_text: str
    type: DiffType


class CompareResult(BaseModel):
    diff_results: list[DiffResult]
    iou_level: IouLevel
    iou: int = Field(
        description="Jaccard IoU trên tập từ (sau chuẩn hóa), thang 0–100."
    )
