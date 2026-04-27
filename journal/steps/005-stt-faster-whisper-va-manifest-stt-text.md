# Bước 005 — Helper STT (faster-whisper) + trường `stt_text` trong manifest

**Ngày:** 2026-04-27  
**Trạng thái:** hoàn thành

## Mục tiêu

- Thêm module STT dùng được trong code và từ CLI.
- Chạy trên toàn bộ `kz_dataset` và ghi **transcript thực tế** vào từng mục manifest (`stt_text`).

## Đã thực hiện

- Thêm `stt.py`: `get_model`, `transcribe_wav`, `annotate_manifest` (cache mô hình, VAD, mặc định `en`, CPU `int8`), CLI cập nhật manifest.
- Thêm `faster-whisper>=1.0.0` vào `requirements.txt`.
- Chạy `python stt.py` → cập nhật `kz_dataset/manifest.json` với trường `stt_text` cho 10 file wav.

## File / module liên quan

- `stt.py` — STT & CLI.
- `requirements.txt` — `faster-whisper`.
- `kz_dataset/manifest.json` — mỗi `items[]` có thêm `stt_text`.

## Quyết định & ghi chú kỹ thuật

- Dùng **faster-whisper** (nhanh, chạy local) thay vì gọi API; mô hình mặc định `base` (có thể đổi `--model`).
- Một số câu STT lệch so với `text` góc — phản ánh chất lượng/điều kiện ghi; có thể nâng `small` nếu cần WER tốt hơn.
- Tái chạy: `source .venv/bin/activate && python stt.py` (hoặc trỏ `manifest` / `--dataset-dir` nếu cấu trúc đổi).

## Khó khăn / rủi ro

- Lần đầu tải weights từ Hugging Face (có thể cần `HF_TOKEN` nếu bị rate limit).
