"""TTS nhẹ (edge-tts), cache theo hash text đã chuẩn hóa."""
from __future__ import annotations

import asyncio
import hashlib
import re
from pathlib import Path

import edge_tts
from django.conf import settings

# Giọng nữ, dễ nghe; rate hơi nhanh một chút so với mặc định
TTS_VOICE = "en-US-JennyNeural"
TTS_RATE = "+8%"


def preprocess_text_for_tts(text: str) -> str:
    t = text.strip()
    t = re.sub(r"\s+", " ", t)
    return t


def tts_cache_key(text: str) -> str:
    return hashlib.sha256(preprocess_text_for_tts(text).encode("utf-8")).hexdigest()


async def _save_mp3(path: Path, text: str) -> None:
    communicate = edge_tts.Communicate(text, TTS_VOICE, rate=TTS_RATE)
    await communicate.save(str(path))


def get_or_create_tts_mp3(text: str) -> Path:
    pre = preprocess_text_for_tts(text)
    if not pre:
        raise ValueError("Empty text")
    cache_dir: Path = settings.TTS_CACHE_DIR
    cache_dir.mkdir(parents=True, exist_ok=True)
    out = cache_dir / f"{tts_cache_key(pre)}.mp3"
    if not out.exists():
        asyncio.run(_save_mp3(out, pre))
    return out
