# Bước 010 — Package `src/kzen` và cài đặt editable

**Ngày:** 2026-04-27  
**Trạng thái:** hoàn thành

## Mục tiêu

- Gom mã Python vào một package có tên import rõ ràng; chạy entrypoint qua `python -m kzen.…`.

## Đã thực hiện

- Thư mục `src/kzen/`: toàn bộ module (trong đó có `utils` chứa `compare_text`, cùng UI/STT).
- Import nội bộ dạng relative (`.configs`, `.utils`, …).
- **`configs.repo_root()`**: hai cấp lên từ `src/kzen/` → gốc repo; `dataset_ui` mặc định `kz_dataset/` tại gốc repo.
- `pyproject.toml` + **`pip install -e .`**; lệnh: `python -m kzen.app_ui`, `kzen.dataset_ui`, `kzen.stt`, `kzen.main`.
- Notebook: `from kzen.utils import compare_text` sau khi cài package.
- `.gitignore`: `*.egg-info/`.

## File liên quan

- `src/kzen/*`, `pyproject.toml`, `README.md`, `requirements.txt`, `notebook_001.ipynb`

## Ghi chú

- Bước này **không đổi thuật toán** so sánh text; logic nằm ở nhật ký **009**.
