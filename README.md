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
pip install -e .
```

`pip install -e .` đăng ký package **`kzen`** từ thư mục `src/kzen/` (import được `kzen.utils`, chạy được `python -m kzen.app_ui`, …).

Lần đầu chạy **faster-whisper** / **forcealign** có thể tải model (cần mạng).

## Chạy nhanh

Chạy từ **thư mục gốc repo** (để đường dẫn `kz_dataset/`, `sample.wav` đúng).

| Mục đích | Lệnh |
|----------|------|
| UI: ghi âm một đoạn + ForceAlign | `python -m kzen.app_ui` |
| UI: dataset 10 câu → WAV + `manifest.json` | `python -m kzen.dataset_ui` |
| STT: ghi `stt_text` vào manifest | `python -m kzen.stt` (mặc định `kz_dataset/manifest.json`) |
| Ví dụ align | `python -m kzen.main` (cần `sample.wav`) |

## Dataset (`kz_dataset/`)

- `manifest.json`: danh sách `items` với `index`, `text`, `wav`, …; có thể có `stt_text` sau STT.
- File âm thanh: `000.wav`, … (mono 16 kHz khi ghi từ UI).
- UI dataset mặc định lưu vào `kz_dataset/` **ở gốc repo** (`repo_root()` trong `kzen.configs`).

## Cấu trúc chính

| Đường dẫn | Mô tả |
|-----------|--------|
| `src/kzen/` | Package Python `kzen` |
| `src/kzen/utils.py` | Mic, WAV, ForceAlign, `compare_text`, … |
| `src/kzen/configs.py` | Hằng số + `DIFFLIB_OPCODE_TO_DIFF_TYPE`, `repo_root()` |
| `src/kzen/enums.py` | `DiffType`, `IouLevel` |
| `src/kzen/schemas.py` | Pydantic: `DiffResult`, `CompareResult` |
| `src/kzen/app_ui.py` | Tkinter: ghi âm + align |
| `src/kzen/dataset_ui.py` | Tkinter: 10 câu + manifest |
| `src/kzen/stt.py` | faster-whisper → manifest |
| `pyproject.toml` | Cấu hình setuptools / `pip install -e .` |
| `notebook_001.ipynb` | Notebook: dùng `from kzen.utils import …` (cần đã `pip install -e .`) |
| `journal/` | Nhật ký — `journal/README.md` |

## Ghi chú

- Cần quyền **microphone** cho các UI ghi âm.
- Báo cáo: `journal/steps/`.
