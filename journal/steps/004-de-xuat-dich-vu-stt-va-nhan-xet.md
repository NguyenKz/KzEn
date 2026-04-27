# Bước 004 — Đề xuất dịch vụ STT và so sánh với text góc (align)

**Ngày:** 2026-04-27  
**Trạng thái:** hoàn thành (bước thiết kế / ghi chú; chưa code)

## Mục tiêu

- Ghi lại hướng mở rộng: có **text góc (manifest) + audio**; **ForceAlign** hiện giả định lời nói khớp script — cần **STT** để lấy **bề mặt nói thật** trên file wav.
- Làm rõ lợi ích: (1) **nhận xét** đọc đúng / dư / thiếu so với chuẩn; (2) **dùng transcript STT** (hoặc STT + timestamp) để **align / cắt timeline** chính xác hơn khi lời nói lệch script.

## Đã thực hiện

- Thống nhất pipeline khái niệm:
  - **Đánh giá:** chuẩn hóa cả text góc và STT → WER, diff từ, hoặc align hai chuỗi; lưu ý lỗi STT có thể bị tính như “sai từ”.
  - **Alignment:** tùy chọn **STT có timestamp** (Whisper, v.v.) hoặc `force_align(wav, transcript_stt)` thay vì `transcript` từ manifest.
  - **Hybrid gợi ý:** so reference vs STT; lệch nhỏ vẫn align text góc, lệch lớn dùng STT align hoặc cảnh báo.
- **Trong repo:** chưa thêm module STT, dependency hay thay đổi `utils.py` / notebook — chỉ bàn thiết kế.

## File / module liên quan (hiện trạng, chưa sửa)

- `utils.py` — `force_align`, `try_force_align` (transcript từ ngoài vào).
- `notebook.ipynb` — thử `ForceAlign` với `manifest["text"]` và wav trong `kz_dataset/`.
- `main.py` — mẫu gọi `force_align("sample.wav", "hello world")`.

## Quyết định & ghi chú kỹ thuật

- **Text góc** = chuẩn kỳ vọng; **STT** = bề mặt thực tế; kết hợp cho workflow “script + bản nói thật”.
- Khi triển khai: cân nhắc **offline (Whisper)** vs **API cloud** (latency, bảo mật, chi phí).

## Khó khăn / rủi ro

- Không tách 100% “người đọc sai” vs “STT nghe nhầm” nếu không rà soát thủ công.

## Việc tiếp theo (optional)

- Thêm `stt` module + hàm so sánh reference/STT; chọn transcript cho align theo ngưỡng lệch hoặc luôn ưu tiên STT cho bước cắt.
