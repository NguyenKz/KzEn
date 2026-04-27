# Bước 009 — Logic so sánh transcript STT với kịch bản tham chiếu

**Ngày:** 2026-04-27  
**Trạng thái:** hoàn thành

## Mục tiêu

- Đo độ khớp giữa **chuỗi STT** (`stt_text`) và **kịch bản** (`text`) để phục vụ đánh giá / báo cáo.
- Xuất vừa **điểm tổng hợp** (IoU + mức chất lượng) vừa **diff có cấu trúc** (từng khối equal/replace/delete/insert).

## Thuật toán (mức từ)

1. **Chuẩn hóa token**  
   Tách theo khoảng trắng, bỏ ký tự không phải chữ/số (regex), chữ thường, bỏ token rỗng sau khi làm sạch — hàm `split_normalized_words`.

2. **IoU (Jaccard) trên tập từ**  
   Coi mỗi câu là tập các **kiểu từ** (unique words) sau chuẩn hóa:  
   `IoU = |ref ∩ stt| / |ref ∪ stt|`.  
   Nếu `ref ∪ stt` rỗng → coi IoU = 1.0 (hai câu đều không có từ).  
   Giá trị hiển thị: **`iou`** nguyên 0–100 (`int(jaccard * 100)`).

3. **Mức chất lượng từ IoU** (`normalize_iou` → `IouLevel`)  
   - ≥ 0.85 → excellent  
   - ≥ 0.70 → good  
   - ≥ 0.50 → average  
   - ≥ 0.30 → bad  
   - &lt; 0.30 → poor  

4. **Diff tuần tự (giữ thứ tự từ)**  
   `difflib.SequenceMatcher` trên hai **danh sách từ** (không phải multiset): mỗi opcode sinh một `DiffResult`: `ref_text` / `stt_text` (chuỗi ghép từ các slice tương ứng), `type` = `DiffType` ánh xạ từ opcode chuẩn của thư viện (`DIFFLIB_OPCODE_TO_DIFF_TYPE` trong `configs`).

## Model dữ liệu (Pydantic / enum)

- **`DiffType`**, **`IouLevel`**: `enums.py` (`str, Enum` để serialize JSON).
- **`DiffResult`**, **`CompareResult`**: `schemas.py` (`diff_results`, `iou_level`, `iou`).

## Input / output mẫu

**Chữ ký:** `compare_text(stt_text: str, ref_text: str) -> CompareResult`  
- **`ref_text`**: kịch bản chuẩn (ground truth).  
- **`stt_text`**: transcript từ STT (cần so với kịch bản).

### Ví dụ 1 — Khớp hoàn toàn

**Input**

```text
ref_text = "Hello, how are you today?"
stt_text = "Hello, how are you today?"
```

**Output** (ý tưởng; số liệu khớp code thực tế)

```text
iou = 100
iou_level = excellent
diff_results = [
  { ref_text: "hello how are you today", stt_text: "hello how are you today", type: equal }
]
```

(Sau chuẩn hóa, dấu câu bị bỏ nên hai chuỗi token trùng nhau.)

### Ví dụ 2 — Sai một từ

**Input**

```text
ref_text = "What time is the meeting?"
stt_text = "What time is the misting?"
```

**Output**

```text
iou = 66          # Jaccard trên tập từ: 4 chung / 6 hợp (meeting ≠ misting)
iou_level = average
diff_results = [
  { ref_text: "what time is the", stt_text: "what time is the", type: equal },
  { ref_text: "meeting", stt_text: "misting", type: replace }
]
```

### Ví dụ 3 — Nhiều khối thay thế (rút gọn)

**Input**

```text
ref_text = "The quick brown fox jumps over the lazy dog."
stt_text = "The quick bro forced zoom over the lazy dock."
```

**Output** (không liệt kê hết nếu dài; cấu trúc tương tự)

```text
iou ≈ 33 (tùy tập từ unique sau chuẩn hóa)
iou_level = bad
diff_results ≈ [
  { type: equal,   ref_text: "the quick",           stt_text: "the quick" },
  { type: replace, ref_text: "brown fox jumps",     stt_text: "bro forced zoom" },
  { type: equal,   ref_text: "over the lazy",       stt_text: "over the lazy" },
  { type: replace, ref_text: "dog",                 stt_text: "dock" },
]
```

**Ghi chú:** `ref_text` / `stt_text` trong mỗi `DiffResult` là **chuỗi đã ghép từ các từ đã chuẩn hóa** (không có dấu câu gốc), để khớp với nội bộ `SequenceMatcher`.

## Triển khai trong code

- Hàm chính: **`compare_text(stt_text, ref_text)`** trong `utils.py` (package `kzen`).
- Phụ thuộc: `configs` (ánh xạ opcode), `schemas`, `enums`.

## Nguồn gốc

- Thử nghiệm ban đầu trong `notebook_001.ipynb`; sau đó đưa vào module, thêm `pydantic`, gộp/refactor file (helpers → utils) và tách enum/config/schema — **chỉ là chỗ đặt code**; nội dung bước này là **logic so sánh** ở trên.

## Việc tiếp theo (gợi ý)

- Có thể bổ sung metric khác (WER/CER) nếu cần so với IoU tập từ.
