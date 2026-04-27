# Bước 007 — So khớp **script (text góc)** và **STT** bằng `difflib`

**Ngày:** 2026-04-27  
**Trạng thái:** hoàn thành (ghi chú thiết kế + thử nghiệm notebook)

## Mục tiêu

- Có cách **so sánh hai đoạn văn bản** — cột **reference / script** (`text` trong manifest) và bản **nhận dạng thực tế** (`stt_text`) — để thấy **khối từ giống / thay thế / thêm / bớt** (dư, thiếu, lệch).

## Input

Hai chuỗi văn bản thuần (Unicode), không bắt buộc cùng độ dài:

| Tham số (ý nghĩa) | Nguồn trong dự án | Ví dụ (mục `index: 1` manifest) |
|-------------------|-------------------|----------------------------------|
| **Script / reference** | `item["text"]` | `The quick brown fox jumps over the lazy dog.` |
| **STT (thực tế nói)** | `item["stt_text"]` | `The quick bro forced zoom over the lazy dock.` |

Sau bước chuẩn hóa (lower + bỏ ký tự không phải chữ-số) và tách từ, **input nội bộ** cho `SequenceMatcher` là hai list cùng kiểu phần tử (một từ mỗi phần tử), thứ tự giữ theo câu:

```text
ref_words = ["the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"]
stt_words = ["the", "quick", "bro", "forced", "zoom", "over", "the", "lazy", "dock"]
```

Gọi matcher với cùng quy ước, ví dụ `SequenceMatcher(None, stt_words, ref_words)` thì cột thứ nhất = STT, cột thứ hai = script (khi cần diễn giải “lời nói thật lệch script” cho đúng hướng). Notebook có thể đổi thứ tự `a` / `b`; quan trọng là thống nhất **bên nào là `old_text` (= slice của `a`)** và **bên nào là `new_text` (= slice của `b`)** trong từng bản ghi.

## Output

- **Cấu trúc tối thiểu (mỗi opcode):** mảng **dict** (hoặc list các record tương đương), mỗi phần tử ứng với **một đoạn liên tục** trên cả hai trục từ:

| Trường | Kiểu | Ý nghĩa (khi `a` = STT, `b` = script) |
|--------|------|--------------------------------------|
| `type` | `str` | Một trong: `equal`, `replace`, `delete`, `insert` |
| `stt_span` / `old_text` | `str` | Chuỗi nối các từ `a[i1:i2]` (khối phía **STT**) |
| `ref_span` / `new_text` | `str` | Chuỗi nối các từ `b[j1:j2]` (khối phía **script**) |

(Trong notebook gọn nhẹ dùng tên `old_text` / `new_text` tương ứng `a` / `b`.)

- **Ví dụ output** — cùng cặp đã chuẩn hóa + tách từ như mục Input, với `a = stt_words`, `b = ref_words`:

```text
[
  {"old_text": "the quick", "new_text": "the quick", "type": "equal"},
  {"old_text": "bro forced zoom", "new_text": "brown fox jumps", "type": "replace"},
  {"old_text": "over the lazy", "new_text": "over the lazy", "type": "equal"},
  {"old_text": "dock", "new_text": "dog", "type": "replace"}
]
```

(Cell notebook khác có thể dùng list từ minh hoạ tương tự, ví dụ thêm từ `is` để tập cấu trúc — **cùng công thức input/output** như bảng trên.)

- **Diễn giải nhanh cho báo cáo / UI:**
  - `equal` — đoạn từ **khớp** giữa hai bên.
  - `replace` — **lệch / đọc khác** (cùng lúc thay nhiều từ).
  - `delete` — từ có ở `a` nhưng trống ở `b` tương ứng (tùy hướng: **có ở STT, không ở script** hoặc ngược lại, cần thống nhất quy ước a/b).
  - `insert` — từ có ở `b` mà `a` không che đủ ở vị trí ấy (thừa / bổ sung).

## Cách làm (mức từ)

1. **Chuẩn hóa** hai chuỗi trước khi tách từ: thường `lower()`, bỏ ký tự không phải chữ-số dùng chung một quy tắc (ví dụ `re.sub` chỉ giữ `\w` và khoảng trắng) để câu có dấu câu không làm lệch diff vô ích.
2. **Tách từ** bằng `split()` → hai **list từ** `ref_words` và `stt_words` (tên đặt: một bên script, một bên STT; thứ tự tham số với `SequenceMatcher` chỉ cần **nhất quán** khi diễn giải `old_text` / `new_text` trong kết quả).
3. **`difflib.SequenceMatcher(None, a, b)`** với so sánh theo phần tử từ (không cần hàm băm, tham số đầu là `None` cho chuỗi/từ).
4. **`matcher.get_opcodes()`** trả từng đoạn `(tag, i1, i2, j1, j2)`:
   - **`equal`**: cùng nội dung trên cả hai phía (đoạn khớp).
   - **`replace`**: thay hàng từ bên này bằng hàng từ bên kia.
   - **`delete`**: có trong chuỗi thứ nhất, không (hoặc ít) tương ứng ở chuỗi thứ hai — diễn giải thường là **“thiếu ở phía b / đọc khác”** tùy cách gán a/b.
   - **`insert`**: thêm ở chuỗi thứ hai — **thừa / bổ sung** so với bên còn lại.
5. Gói mỗi opcode thành cấu trúc dễ đọc, ví dụ:
   - `"old_text"`: nối `a[i1:i2]`
   - `"new_text"`: nối `b[j1:j2]`
   - `"type"`: `tag`  
   (Ví dụ thử nghiệm: `notebook_001.ipynb`, cell `difflib` + tách từ.)

## Ghi chú

- Diff **mức từ** ổn với cặp script–STT tiếng Anh; lệch dấu câu hoặc tách từ sai sẽ làm `replace` dài.
- Nếu cần metric tổng hợp, có thể bổ sung **WER** (ví dụ `jiwer`) trên cùng hai chuỗi đã chuẩn hóa.
- Lỗi STT (“nghe nhầm”) vẫn xuất hiện như thay thế/ chèn, không tách rời lỗi mô hình với lỗi phát âm nếu không có nhãn thủ công.

## File liên quan

- `notebook_001.ipynb` — chuỗi thử: list từ từ script vs STT, `SequenceMatcher`, `get_opcodes()`.

## Việc tiếp theo (optional)

- Tách hàm `tokenize_for_compare` + `diff_script_stt(ref, stt) -> list[dict]` vào `utils` hoặc module riêng nếu dùng lặp ngoài notebook.
