# Bước 003 — Bổ sung skill: nhật ký tự động khi user chỉ nói «mới làm…»

**Ngày:** 2026-04-27  
**Trạng thái:** hoàn thành

## Mục tiêu

- Thêm **điều kiện kích hoạt** (không xóa nội dung cũ): khi user mô tả ngắn việc vừa làm, agent tự **đối chiếu git/diff** và cập nhật `journal/steps/`.

## Đã thực hiện

- Mở rộng `description` trong frontmatter skill (từ khóa tiếng Việt + hành vi reconcile).
- Thêm mục **«Thêm điều kiện: người dùng chỉ mô tả miệng»** trong `.cursor/skills/project-work-journal/SKILL.md`: bắt buộc `git status`/`git diff`, ghép với lời user, không bịa chi tiết.

## File / module liên quan

- `.cursor/skills/project-work-journal/SKILL.md`

## Quyết định & ghi chú kỹ thuật

- Giữ nguyên các mục quy tắc cũ; phần mới là **bổ sung** điều kiện và quy trình lấy dữ liệu.
