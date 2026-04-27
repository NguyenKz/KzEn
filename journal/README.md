# Nhật ký dự án KzEn

Thư mục này lưu **từng bước làm việc** dưới dạng Markdown để sau này viết báo cáo, tài liệu, hoặc onboarding.

## Cấu trúc

| Đường dẫn | Mục đích |
|-----------|----------|
| `steps/NNN-slug-ngan.md` | Một file = một **bước** (feature, bugfix, quyết định kỹ thuật, buổi làm việc). |
| `_template.md` | Bản mẫu copy khi tạo bước mới. |

- `NNN`: số thứ tự 3 chữ số (`001`, `002`, …), tăng dần theo thời gian.
- `slug-ngan`: mô tả ngắn bằng chữ thường, gạch ngang (ví dụ `sua-ui-ghi-am`).

## Quy tắc

1. **Một bước = một file** (không gộp nhiều milestone không liên quan vào cùng file).
2. Ghi **ngày**, **mục tiêu**, **việc đã làm**, **file/code chạm tới**, **vấn đề & cách xử lý** (nếu có).
3. Ưu tiên tiếng Việt; thuật ngữ kỹ thuật có thể giữ tiếng Anh.
4. Agent (Cursor) được nhắc bởi skill `project-work-journal` trong `.cursor/skills/`.

## Mục lục (cập nhật tay khi cần)

- [001 — Khởi tạo nhật ký & skill](steps/001-khoi-tao-nhat-ky-va-skill.md)
- [002 — UI dataset & sửa layout Canvas](steps/002-ui-dataset-sua-layout-canvas.md)
- [003 — Skill: nhật ký tự động từ lời kể + diff](steps/003-skill-nhat-ky-tu-dong-tu-loi-ke.md)
- [004 — Đề xuất dịch vụ STT và nhận xét / align](steps/004-de-xuat-dich-vu-stt-va-nhan-xet.md)
- [005 — STT faster-whisper & manifest `stt_text`](steps/005-stt-faster-whisper-va-manifest-stt-text.md)
- [006 — `transcribe_wav` hỗ trợ numpy waveform](steps/006-stt-transcribe-wav-ndarray.md)
- [007 — Diff script vs STT (`difflib` mức từ)](steps/007-script-vs-stt-diff-difflib.md)
