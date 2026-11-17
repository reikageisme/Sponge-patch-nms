# BẢN NHÁP: PREREG_E12, đo lại bảng patch có cổng trôi theo khối

Trạng thái: **nháp, chưa có hiệu lực**. Soạn 16/11/2026 sau hai bản phản biện nội bộ. Trước khi đo: tác giả sửa, đổi tên thành
`PREREG_E12.md`, commit, gắn tag `prereg-e12-<ngày>` và (nên) nộp lên OSF hoặc AsPredicted để có mốc thời gian độc lập.
Mã: `studies/e12_patch_remeasure_gated/run.py` (chưa chạy trên dữ liệu thật), phân tích dùng `studies/e11_patch_remeasure/analyze.py`.

## Lý do
E11 sửa lỗi bấm giờ của E6 nhưng phiên bị loại theo quy tắc đã đăng ký vì 11/11 điểm tham chiếu bị cờ trôi. Bảng patch của bài
vì vậy chỉ có tỉ số end-to-end do mô hình dự đoán. Phản biện coi đây là điểm yếu nặng nhất. E12 đo lại đúng bảng đó.

**Đã thấy dữ liệu:** toàn bộ E6, E11 (kể cả phiên bị loại) và E10 đã được xem. Mọi giả thuyết dưới đây là xác nhận lại.

## Khác E11 ở ba điểm, ngoài ra giữ nguyên
1. **Máy và môi trường:** Linux, một CPU logic được ghim, governor `performance`, tần số min = max (không turbo), CPU anh em SMT
   offline. Phiên chỉ bắt đầu khi `hw_linux.lock_status(cpu)['ready']` là True; kết quả kiểm được ghi vào manifest.
   (Ghi ở đây: tên máy, CPU, tần số khoá, kernel.)
2. **Cổng trôi theo khối** (`timing.DriftGate`): điểm tham chiếu đo trước và sau mỗi khối 10 ảnh. Khối được nhận khi cả hai điểm
   lệch điểm đầu phiên không quá 3% và lệch nhau không quá 3%. Khối không đạt được đo lại nguyên khối, tối đa 3 lần, chờ 60 giây
   giữa các lần. Hết lượt thì dừng phiên; phiên dừng giữa chừng không được dùng cho kết quả chính.
3. **Thứ tự đơn vị trong ảnh** là hàm tất định của (seed thứ tự, mã ảnh), để lần đo lại khối dùng đúng thứ tự cũ.
   (E11 dùng một bộ sinh số ngẫu nhiên chạy suốt phiên.)

Giữ nguyên từ PREREG_E11: 100 ảnh `IMAGE_IDS[:100]`, seed patch 0 đến 4, các nhánh clean_a, clean_b, clean640_a, clean640_b, C1 đến C4,
B1 đến B4, patch đóng băng kiểm SHA-256, bước chèn ngoài vùng đo, đo vi mô và toàn trình, fail-closed theo X1-500.

## Báo cáo bắt buộc về cổng trôi
- Số khối, số lần thử, số lần bị bỏ, độ lệch lớn nhất của các khối được nhận (`gate_summary` trong raw).
- Mọi lần thử bị bỏ có dòng `block_attempt` trong raw; dòng đo của lần bị bỏ không được ghi và không được phân tích.
- Phân tích độ nhạy: kết quả chính khi siết ngưỡng nhận khối xuống 2% (bỏ các khối có độ lệch từ 2% đến 3%).

## Endpoint
Như PREREG_E11 (E11-P1 đến P3), cộng thêm:
- **E12-P4:** với mỗi nhánh, TOST biên 1% và 5% trên tỉ số toàn trình (`stats.tost_ratio`). Câu "patch không làm chậm toàn trình"
  chỉ được viết khi tương đương trong biên 1%; nếu chỉ đạt 5% thì viết "dưới 5%".
- **E12-P5:** tỉ số N_tau báo bằng trung bình tỉ số, trung vị tỉ số và tỉ số hai trung vị (`stats.ratio_summaries`).
- **E12-P6:** p95, p99 và tỉ lệ vượt 100 ms trên từng lần lặp (`stats.tail_summary`).

## Giả thuyết (ghi trước khi đo; tác giả điền)
- H1: ...
- H2: ...

## Quy tắc dừng và loại
- verify ghim không đạt, SHA-256 patch lệch, N sạch lệch X1-500, môi trường chưa khoá: dừng, không đo.
- Trôi kéo dài (hết lượt đo lại của một khối): dừng phiên, báo cáo, chạy phiên mới sau khi tìm ra nguyên nhân.
