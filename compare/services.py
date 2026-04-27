"""Gọi logic có sẵn trong package kzen (không viết lại so sánh / STT)."""
from __future__ import annotations

import os
import tempfile

from django.conf import settings

from kzen.schemas import CompareResult
from kzen.stt import transcribe_wav
from kzen.utils import compare_text


def transcribe_file_to_text(upload_path: str) -> str:
    model = getattr(settings, "KZEN_STT_MODEL", "tiny")
    return transcribe_wav(
        upload_path,
        model_size=model,
        language="en",
        device="cpu",
        compute_type="int8",
    )


def compare_stt_to_reference(stt_text: str, reference_text: str) -> CompareResult:
    return compare_text(stt_text=stt_text, ref_text=reference_text)


def transcribe_upload_and_compare(
    uploaded_file,
    reference_text: str,
) -> tuple[str, CompareResult]:
    """
    Lưu upload tạm, chạy STT, so sánh với kịch bản.
    Trả về (transcript, CompareResult).
    """
    suffix = os.path.splitext(getattr(uploaded_file, "name", "") or "")[1] or ".webm"
    fd, tmp = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    try:
        with open(tmp, "wb") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        stt_text = transcribe_file_to_text(tmp)
        result = compare_stt_to_reference(stt_text, reference_text)
        return stt_text, result
    finally:
        if os.path.isfile(tmp):
            os.remove(tmp)
