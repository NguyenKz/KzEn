# Bước 006 — `transcribe_wav` nhận cả mảng sóng (numpy)

**Ngày:** 2026-04-27  
**Trạng thái:** hoàn thành

## Mục tiêu

- Mở rộng `stt.py`: ngoài **đường dẫn file** (`str` / `os.PathLike`), hỗ trợ **một `np.ndarray`** (waveform) như `faster_whisper.WhisperModel.transcribe` hỗ trợ.

## Đã thực hiện

- Thêm `_as_mono_float32`, `_resample_linear`, `_audio_input_for_model` — với ndarray: float32 mono, resample tuyến tính về 16 kHz (hằng `WHISPER_SAMPLE_RATE`); tham số `sample_rate` (mặc định 16 kHz khi ndarray).
- `transcribe_wav(wav, *, sample_rate=None, ...)` — `sample_rate` chỉ dùng khi `wav` là ndarray.

## File liên quan

- `stt.py`

## Ghi chú

- Với file path, `faster-whisper` tự giải mã/ resample; với buffer tự chuẩn hóa về 16 kHz trước khi gọi model.
