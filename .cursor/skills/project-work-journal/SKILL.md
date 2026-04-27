---
name: project-work-journal
description: >-
  Maintains a step-by-step Markdown project journal under journal/steps/ for
  reports and documentation. Use when working in this repository, after
  completing a meaningful task, when the user asks for a diary/log, nhật ký,
  báo cáo tiến độ, or wants progress recorded for later reporting. Also use
  when the user states informally that they just did work (e.g. Vietnamese:
  «tôi mới làm…», «vừa sửa…», «xong phần…») so the agent infers a journal
  update is needed and reconciles git/workspace changes with that summary.
---

# Nhật ký tiến trình dự án (KzEn)

## Khi phải ghi

- Kết thúc một **bước** rõ ràng: feature, bugfix, refactor có ý nghĩa, thay đổi cấu hình quan trọng, hoặc buổi làm việc có kết quả cụ thể.
- Người dùng nhắc **nhật ký**, **log tiến độ**, **để viết báo cáo**, hoặc **ghi lại**.

Không cần file mới cho mỗi tin nhắn nhỏ; gộp các thay đổi liên quan trong **một** bước.

## Thêm điều kiện: người dùng chỉ mô tả miệng, không gõ «ghi nhật ký»

Áp dụng **cùng** các quy tắc phía trên; đây chỉ là **cách kích hoạt** và **cách lấy dữ liệu** bổ sung.

### Khi nào

- Người dùng nói kiểu ngắn: đã / mới / vừa làm X (tiếng Việt hoặc Anh), ví dụ *«tôi mới làm abcd…»*, *«xong refactor phần Y»*, *«vừa thêm tính năng Z»* — **không** cần họ yêu cầu explicit «cập nhật nhật ký».
- Coi như họ muốn **một bước nhật ký** phản ánh đúng thực tế repo, không chỉ lời kể.

### Việc agent phải làm (bắt buộc)

1. **Kiểm tra thay đổi thật** trong working tree / commit gần nhất: `git status`, `git diff` (và nếu cần `git diff --staged`), hoặc đọc file vừa sửa trong phiên — không chỉ tin lời tóm tắt.
2. **Ghép** lời người dùng với diff: phần nào khớp thì ghi; phần diff có mà user không nhắc thì vẫn liệt kê trong «Đã thực hiện» / «File liên quan»; nếu user nói làm X nhưng diff không có X, ghi rõ **chưa thấy thay đổi trong repo** (hoặc chỉ ghi những gì diff cho thấy).
3. **Tạo hoặc cập nhật** một file bước mới trong `journal/steps/` theo quy ước `NNN-slug-ngan.md` (bước mới = số tiếp theo), rồi cập nhật mục lục trong `journal/README.md` nếu đang dùng.
4. **Không** bịa chi tiết không có trong diff hoặc trong nội dung file; có thể trích ngắn ý nghĩa thay đổi từ diff.

### Khi không tạo bước mới

- Chỉ là chat / câu hỏi, **không** có thay đổi file và user không khẳng định đã làm việc trên code → có thể bỏ qua hoặc hỏi lại một dòng.

## Vị trí và tên file

- Thư mục: `journal/steps/` (đã có `journal/README.md` và `journal/_template.md`).
- Tên file: `NNN-slug-ngan.md`
  - `NNN`: số thứ tự **tiếp theo** sau file lớn nhất hiện có trong `journal/steps/` (ví dụ đã có `002-...` thì bước mới là `003-...`).
  - `slug-ngan`: mô tả ngắn, chữ thường, gạch ngang.

Nếu chưa có bước nào, bắt đầu từ `001-...`.

## Nội dung tối thiểu trong mỗi file

Dùng cấu trúc giống `journal/_template.md`, ít nhất:

1. Tiêu đề `# Bước NNN — …`
2. **Ngày** (YYYY-MM-DD, theo ngữ cảnh phiên làm việc nếu có)
3. **Mục tiêu** (1–3 gạch đầu dòng)
4. **Đã thực hiện** (cụ thể: chức năng, hành vi, lỗi đã sửa)
5. **File / module liên quan** (đường dẫn tương đối trong repo)
6. **Quyết định / ghi chú kỹ thuật** (nếu có)

Viết súc tích, **đủ để sau này dựng báo cáo** (ai làm gì, vì sao, chạm file nào).

## Sau khi tạo file

- Cập nhật mục lục trong `journal/README.md` (bảng hoặc danh sách link tới file bước mới) nếu repo đang dùng mục lục đó.

## Không làm

- Không xóa hoặc sửa đè nhật ký cũ để che lịch sử; nếu sửa sai, thêm bước mới ghi rõ **đính chính**.
- Không lưu secret, token, dữ liệu cá nhân vào nhật ký.
