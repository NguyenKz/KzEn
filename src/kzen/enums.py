"""Enum dùng chung trong project (so sánh text, v.v.)."""
from __future__ import annotations

from enum import Enum


class DiffType(str, Enum):
    EQUAL = "equal"
    REPLACE = "replace"
    DELETE = "delete"
    INSERT = "insert"


class IouLevel(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    BAD = "bad"
    POOR = "poor"
