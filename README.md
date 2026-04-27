# KzEn

Dự án thử nghiệm **ghi âm tiếng Anh**, **căn chữ (force alignment)**, **STT (faster-whisper)** và **so sánh transcript với kịch bản** — phục vụ dataset cố định (`text` + `WAV`) để test lặp lại không cần nói lại mỗi lần.

## Yêu cầu

- Python 3.12+ (khuyến nghị dùng virtualenv trong `.venv`)

## Cài đặt

```bash
cd KzEn
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Lần đầu chạy **faster-whisper** / **forcealign** có thể tải model (cần mạng).

## Chạy nhanh

| Mục đích | Lệnh / file |
|----------|-------------|
| UI: ghi âm một đoạn + chạy ForceAlign | `python app_ui.py` |
| UI: tạo dataset 10 câu → `000.wav`… + `manifest.json` | `python dataset_ui.py` |
| STT: thêm trường `stt_text` vào `manifest.json` từ các file WAV | `python stt.py` (mặc định `kz_dataset/manifest.json`) |
| Ví dụ align trong code | `python main.py` (cần `sample.wav` và transcript khớp) |

## Dataset (`kz_dataset/`)

- `manifest.json`: danh sách `items` với `index`, `text`, `wav` (đường dẫn tương đối), `sample_rate`, …; có thể có thêm `stt_text` sau khi chạy `stt.py`.
- File âm thanh: `000.wav`, `001.wav`, … (mono 16 kHz khi ghi từ UI).

## Cấu trúc chính

| Đường dẫn | Mô tả |
|-----------|--------|
| `utils.py` | Mic, lưu WAV, `force_align` / `try_force_align` |
| `app_ui.py` | Tkinter: transcript + ghi âm + align |
| `dataset_ui.py` | Tkinter: 10 dòng câu + ghi âm + manifest |
| `stt.py` | faster-whisper: đọc WAV, ghi transcript vào manifest |
| `notebook_001.ipynb` | Thử nghiệm / phân tích (nếu có) |
| `journal/` | Nhật ký từng bước (Markdown) — xem `journal/README.md` |
| `.cursor/skills/project-work-journal/` | Skill Cursor: ghi nhật ký dự án |

## Ghi chú

- Quyền truy cập **microphone** cần thiết cho các UI ghi âm.
- Báo cáo / tổng hợp tiến độ: dùng các file trong `journal/steps/`.
