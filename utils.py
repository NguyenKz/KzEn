"""Helper: cấu hình ghi âm, lưu WAV, chạy ForceAlign."""
import os
import tempfile
from collections.abc import Sequence

import numpy as np
import sounddevice as sd
import soundfile as sf
from forcealign import ForceAlign

SAMPLE_RATE = 16000
CHANNELS = 1
SD_DTYPE = "float32"
DEFAULT_REC_WAV_BASENAME = "kzalign_recording.wav"


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
