"""Tiện ích: ghi âm/WAV/ForceAlign và so sánh text STT vs kịch bản."""
from __future__ import annotations

import difflib
import os
import re
import tempfile
from collections.abc import Sequence

import numpy as np
import sounddevice as sd
import soundfile as sf
from forcealign import ForceAlign

from .configs import (
    CHANNELS,
    DEFAULT_REC_WAV_BASENAME,
    DIFFLIB_OPCODE_TO_DIFF_TYPE,
    SAMPLE_RATE,
    SD_DTYPE,
)
from .enums import IouLevel
from .schemas import CompareResult, DiffResult


def default_recording_wav_path() -> str:
    return os.path.join(tempfile.gettempdir(), DEFAULT_REC_WAV_BASENAME)


def save_mic_frames_to_wav(
    frames: Sequence[np.ndarray],
    path: str,
    sample_rate: int = SAMPLE_RATE,
) -> float:
    """Nối các chunk từ mic và ghi WAV. Trả về thời lượng (giây), 0 nếu rỗng."""
    if not frames:
        return 0.0
    data = np.concatenate(list(frames), axis=0)
    if data.ndim > 1:
        data = data[:, 0]
    sf.write(path, data, sample_rate, subtype="PCM_16")
    return len(data) / sample_rate


def open_mic_input_stream(
    callback,
    *,
    sample_rate: int = SAMPLE_RATE,
    channels: int = CHANNELS,
    dtype: str = SD_DTYPE,
) -> sd.InputStream:
    """InputStream mặc định (mono, sample_rate). Gọi .start() sau khi tạo."""
    return sd.InputStream(
        channels=channels,
        samplerate=sample_rate,
        dtype=dtype,
        callback=callback,
    )


def force_align(wav_path: str, transcript: str):
    """Chạy ForceAlign, trả về danh sách Word từ forcealign."""
    aligner = ForceAlign(audio_file=wav_path, transcript=transcript)
    return aligner.inference()


def try_force_align(
    wav_path: str, transcript: str
) -> tuple[Exception | None, list[str]]:
    """
    Bọc force_align, trả về (lỗi hoặc None, dòng text mỗi từ).
    Dùng cho UI/CLI cần bắt mọi lỗi tại một chỗ.
    """
    try:
        words = force_align(wav_path, transcript)
        return None, [f"{w}\n" for w in words]
    except Exception as e:
        return e, []


def remove_special_characters(text: str) -> str:
    return re.sub(r"[^\w\s]", "", text)


def normalize_iou(iou: float) -> IouLevel:
    # >= 0.85  rất tốt
    # 0.70–0.85 tốt
    # 0.50–0.70 trung bình
    # 0.30–0.50 tệ
    # < 0.30   rất tệ
    if iou >= 0.85:
        return IouLevel.EXCELLENT
    if iou >= 0.70:
        return IouLevel.GOOD
    if iou >= 0.50:
        return IouLevel.AVERAGE
    if iou >= 0.30:
        return IouLevel.BAD
    return IouLevel.POOR


def split_normalized_words(text: str) -> list[str]:
    words: list[str] = []
    for raw in text.split():
        if not raw.strip():
            continue
        w = remove_special_characters(raw.lower()).strip()
        if w:
            words.append(w)
    return words


def compare_text(stt_text: str, ref_text: str) -> CompareResult:
    stt_words = split_normalized_words(stt_text)
    ref_words = split_normalized_words(ref_text)
    ref_set = set(ref_words)
    stt_set = set(stt_words)
    intersection = ref_set & stt_set
    union = ref_set | stt_set
    if not union:
        jaccard = 1.0
    else:
        jaccard = len(intersection) / len(union)

    matcher = difflib.SequenceMatcher(None, ref_words, stt_words)
    diff_results: list[DiffResult] = []
    for opcode, i1, i2, j1, j2 in matcher.get_opcodes():
        diff_results.append(
            DiffResult(
                ref_text=" ".join(ref_words[i1:i2]),
                stt_text=" ".join(stt_words[j1:j2]),
                type=DIFFLIB_OPCODE_TO_DIFF_TYPE[opcode],
            )
        )
    return CompareResult(
        diff_results=diff_results,
        iou_level=normalize_iou(jaccard),
        iou=int(jaccard * 100),
    )
