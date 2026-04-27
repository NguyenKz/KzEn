"""Hằng số cấu hình: âm thanh/ghi âm, ánh xạ thư viện chuẩn → enum nội bộ."""
from __future__ import annotations

import os

from .enums import DiffType


def repo_root() -> str:
    """Thư mục gốc repo (cha của `src/`), với package tại `src/kzen/`."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))


# --- Ghi âm / WAV (đồng bộ với UI dataset & ForceAlign pipeline) ---
SAMPLE_RATE = 16000
CHANNELS = 1
SD_DTYPE = "float32"
DEFAULT_REC_WAV_BASENAME = "kzalign_recording.wav"

# --- difflib.SequenceMatcher.get_opcodes() ---
# Mỗi opcode là chuỗi: "equal" | "replace" | "delete" | "insert".
# Ánh xạ sang DiffType để dùng trong Pydantic / API thống nhất.
DIFFLIB_OPCODE_TO_DIFF_TYPE: dict[str, DiffType] = {
    "equal": DiffType.EQUAL,
    "replace": DiffType.REPLACE,
    "delete": DiffType.DELETE,
    "insert": DiffType.INSERT,
}
