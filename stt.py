"""STT: nhận dạng lời nói từ file WAV hoặc mảng sóng (numpy) bằng faster-whisper."""
from __future__ import annotations

import argparse
import json
import os
from collections.abc import Iterator
from typing import Any

import numpy as np
from faster_whisper import WhisperModel

# faster-whisper / Whisper mặc định 16 kHz cho waveform thô
WHISPER_SAMPLE_RATE = 16000

_model: WhisperModel | None = None
_model_key: tuple[str, str, str] | None = None


def get_model(
    model_size: str = "base",
    *,
    device: str = "cpu",
    compute_type: str = "int8",
) -> WhisperModel:
    """Tải/cache một WhisperModel theo (size, device, compute_type)."""
    global _model, _model_key
    key = (model_size, device, compute_type)
    if _model is not None and _model_key == key:
        return _model
    _model = WhisperModel(model_size, device=device, compute_type=compute_type)
    _model_key = key
    return _model


def _as_mono_float32(wave: np.ndarray) -> np.ndarray:
    a = np.asarray(wave, dtype=np.float32)
    if a.ndim > 1:
        a = np.ascontiguousarray(a[:, 0])
    return np.ascontiguousarray(a)


def _resample_linear(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    if orig_sr == target_sr:
        return audio
    n = int(round(len(audio) * target_sr / orig_sr))
    if n < 1:
        return np.zeros(0, dtype=np.float32)
    x_old = np.linspace(0.0, 1.0, num=len(audio), dtype=np.float64)
    x_new = np.linspace(0.0, 1.0, num=n, dtype=np.float64)
    return np.interp(x_new, x_old, audio.astype(np.float64)).astype(np.float32)


def _audio_input_for_model(
    wav: str | os.PathLike[str] | np.ndarray,
    sample_rate: int | None,
) -> str | np.ndarray:
    """
    Chuẩn bị tham số `audio` cho WhisperModel.transcribe:
    - đường dẫn file: trả về chuỗi path tuyệt đối;
    - `np.ndarray` mono/đa kênh: chuyển float32 mono, resample về 16 kHz nếu cần.
    """
    if isinstance(wav, (str, os.PathLike)):
        path = os.path.abspath(os.fspath(wav))
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
        return path
    wave = _as_mono_float32(wav)
    sr = sample_rate if sample_rate is not None else WHISPER_SAMPLE_RATE
    return _resample_linear(wave, sr, WHISPER_SAMPLE_RATE)


def transcribe_wav(
    wav: str | os.PathLike[str] | np.ndarray,
    *,
    sample_rate: int | None = None,
    model_size: str = "base",
    language: str | None = "en",
    device: str = "cpu",
    compute_type: str = "int8",
    vad_filter: bool = True,
) -> str:
    """
    Nhận dạng toàn bộ nội dung nói, trả về transcript một chuỗi.

    - **Đường tới file** (``str`` / ``os.PathLike``): đọc file (WAV, …) như faster-whisper.
    - **Mảng sóng** (``np.ndarray``): mono hoặc đa kênh (lấy kênh 0), float/int;
      mặc định coi tần số lấy mẫu = ``16000`` Hz; nếu khác, truyền ``sample_rate=…``.
    - ``language``: ví dụ ``'en'``; ``None`` để tự phát hiện (chậm hơn).
    """
    model = get_model(model_size, device=device, compute_type=compute_type)
    kwargs: dict[str, Any] = {"vad_filter": vad_filter}
    if language is not None:
        kwargs["language"] = language
    audio_in = _audio_input_for_model(wav, sample_rate)
    segments, _info = model.transcribe(audio_in, **kwargs)
    parts: list[str] = []
    for seg in segments:
        t = seg.text.strip()
        if t:
            parts.append(t)
    return " ".join(parts).strip()


def iter_items_wav_paths(
    manifest: dict[str, Any],
    *,
    dataset_dir: str,
) -> Iterator[tuple[dict[str, Any], str]]:
    for it in manifest.get("items", []):
        wav = it.get("wav")
        if not wav:
            continue
        wpath = os.path.join(dataset_dir, wav) if not os.path.isabs(wav) else wav
        yield it, wpath


def annotate_manifest(
    manifest_path: str,
    *,
    dataset_dir: str | None = None,
    stt_key: str = "stt_text",
    model_size: str = "base",
    language: str | None = "en",
    device: str = "cpu",
    compute_type: str = "int8",
) -> None:
    """
    Đọc JSON manifest, ghi `stt_key` (mặc định `stt_text`) cho mỗi item có `wav`, ghi đè file.
    `dataset_dir`: thư mục chứa file wav; mặc định = thư mục cha của manifest.
    """
    mp = os.path.abspath(manifest_path)
    with open(mp, "r", encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)
    base = dataset_dir if dataset_dir is not None else os.path.dirname(mp)
    base = os.path.abspath(base)
    for it, wpath in iter_items_wav_paths(data, dataset_dir=base):
        it[stt_key] = transcribe_wav(
            wpath,
            model_size=model_size,
            language=language,
            device=device,
            compute_type=compute_type,
        )
    with open(mp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main() -> None:
    p = argparse.ArgumentParser(
        description="Cập nhật manifest với stt_text (faster-whisper)."
    )
    p.add_argument(
        "manifest",
        nargs="?",
        default="kz_dataset/manifest.json",
        help="Đường tới manifest.json",
    )
    p.add_argument(
        "--dataset-dir",
        default=None,
        help="Thư mục chứa .wav (mặc định: cùng thư mục với manifest).",
    )
    p.add_argument("--model", default="base", help="Kích thước mô hình (base, small, …).")
    p.add_argument(
        "--language",
        default="en",
        help="Mã ngôn ngữ ISO hoặc 'auto' (tự phát hiện).",
    )
    p.add_argument("--device", default="cpu")
    p.add_argument("--compute-type", default="int8")
    p.add_argument(
        "--stt-key",
        default="stt_text",
        help="Tên trường lưu transcript trong mỗi item.",
    )
    args = p.parse_args()
    lang: str | None
    if args.language.lower() == "auto":
        lang = None
    else:
        lang = args.language
    annotate_manifest(
        args.manifest,
        dataset_dir=args.dataset_dir,
        stt_key=args.stt_key,
        model_size=args.model,
        language=lang,
        device=args.device,
        compute_type=args.compute_type,
    )
    print("OK:", os.path.abspath(args.manifest))


if __name__ == "__main__":
    main()
