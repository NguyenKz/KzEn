# Bước 002 — UI tạo dataset (text + WAV) & sửa layout Canvas

**Ngày:** 2026-04-27  
**Trạng thái:** hoàn thành

## Mục tiêu

- UI tạo dataset: 10 câu tiếng Anh, mỗi câu ghi âm lưu WAV + `manifest.json` để test không cần nói lại mỗi lần.
- Sửa lỗi nút «Ghi âm» không thấy trên macOS.

## Đã thực hiện

- Thêm `dataset_ui.py`: Tkinter, dùng `utils.py` (`sounddevice`, `soundfile`, 16 kHz mono), lưu `000.wav`…`009.wav` và `manifest.json`.
- Nguyên nhân nút biến mất: nội dung trong `Canvas` chỉ cuộn dọc; hàng quá rộng (Entry `width=72`) làm phần nút nằm ngoài viewport.
- Khắc phục: bind `<Configure>` trên canvas để `itemconfigure(inner_win, width=event.width)`; chuyển hàng sang `grid`, `columnconfigure(1, weight=1)` cho ô câu; bỏ `width` cố định trên Entry.

## File / module liên quan

- `dataset_ui.py`
- `utils.py` (ghi WAV, stream mic)
- `app_ui.py` (app ghi âm + align đơn, khác với dataset 10 dòng)

## Quyết định & ghi chú kỹ thuật

- Chỉ một luồng ghi âm tại một thời điểm; dừng ghi thì lưu WAV và cập nhật manifest.
