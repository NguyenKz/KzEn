---
name: kzen-module-layout
description: >-
  Enforces KzEn repository Python layout: one utils module for helpers and
  audio utilities, enums in enums.py, configuration constants and mappings
  in configs.py, Pydantic models only in schemas.py. Do not add stray helper,
  util, or feature-specific utility files (no helpers.py, text_compare_*.py,
  etc.). Use only when editing or adding Python code in the KzEn / kzen
  project; not for other repositories.
---

# Cấu trúc module KzEn (`kzen`)

## Phạm vi

- **Chỉ** repository KzEn (package `src/kzen/`). Không tái sử dụng skill này cho project khác trừ khi người dùng chủ động copy.

## Quy tắc file

| Nội dung | File | Không làm |
|----------|------|-----------|
| Hàm tiện ích, mic/WAV, ForceAlign, **so sánh text**, … | `utils.py` | Tách `helpers.py`, `*_helper.py`, `util_*.py` rời |
| `Enum` / kiểu liệt kê | `enums.py` | Để enum lẫn trong `schemas.py` hoặc `utils.py` |
| Hằng số, mapping cấu hình (vd. opcode → `DiffType`) | `configs.py` | Nhét mapping / magic dict vào `utils.py` |
| Model Pydantic (`BaseModel`) | `schemas.py` | Định nghĩa class schema trong `utils.py` |

## Khi thêm tính năng

1. Cần **enum mới** → `enums.py`.
2. Cần **hằng / bảng tra** → `configs.py` (import enum từ `.enums` nếu cần).
3. Cần **model request/response** → `schemas.py` (import enum từ `.enums`).
4. Cần **logic + hàm thuần** → `utils.py` (import từ `.configs`, `.enums`, `.schemas`).

## Không làm

- Tạo file “linh tinh” theo từng feature nhỏ chỉ để gom vài hàm.
- Nhân đôi nơi lưu cùng loại thứ (hai chỗ đều gọi là util/helper).

## Import trong package

- Giữ **relative import** giữa module trong `kzen` (`.configs`, `.utils`, …) như hiện tại; skill **imports-top-of-file** (global) quy định không lazy import.
