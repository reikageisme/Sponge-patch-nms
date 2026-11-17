> **Hồ sơ nhánh B (13/10/2026).** Tài liệu dưới đây chỉ review benchmark GPU/person. Điểm vào nghiên cứu Sponge/NMS hiện tại là [README tiếng Việt](README.vi.md); xem [danh mục bằng chứng](docs/results.md) để không trộn cohort hoặc metric.

# Đọc review bản thực nghiệm mới

**Cập nhật:** 13/10/2026  
**Nguồn thực nghiệm:** [`sudo-baoz/Physical-Visual-DoS-EdgeAI`, nhánh `codex/local-validation-vi-20261002`](https://github.com/sudo-baoz/Physical-Visual-DoS-EdgeAI/tree/codex/local-validation-vi-20261002)  
**Commit đã review:** `5bdc3c1dbb30f4df708a3c1be35f0879953a7bb0`

README này hướng dẫn đọc **bản đã chạy thực nghiệm của đồng đội** và báo cáo review tương ứng. Tài liệu, kết quả Sponge/NMS trước bàn giao vẫn được giữ trong folder nhưng thuộc phép nghiên cứu khác; không gộp chúng thành bằng chứng cho benchmark YOLO mới.

## 1. Đọc gì trước?

| Bạn muốn biết | Mở tài liệu |
|---|---|
| Kết luận review và việc cần làm tiếp | [Báo cáo review tổng hợp](docs/2026-10-13_research-review-report_VI.md), mục 1, 5 và 8 |
| Thực nghiệm mới chạy thế nào, đạt kết quả gì | [Báo cáo quy mô lớn YOLO](project_yolov13/results/BaoCao_TrienKhaiRong_YOLOv13.md) |
| Vì sao code/phương pháp cần chỉnh | [Review phương pháp và mã](_provenance/review_evidence/branch_yolo_review.md) |
| Số liệu nào đã kiểm tra, phần nào chưa tái lập được | [Audit bằng chứng thực nghiệm](_provenance/review_evidence/branch_yolo_evidence.md) |

**Nếu chỉ có 5 phút:** đọc mục 2–5 bên dưới. Khi cần xác minh một nhận xét, mở hai báo cáo chi tiết ở bảng trên.

## 2. Bản thực nghiệm mới gồm những gì?

- **Bài toán:** phát hiện một lớp `person` — người trong ảnh.
- **Dữ liệu:** 11.123 ảnh, gồm 10.000 ảnh COCO và 1.123 ảnh AdvT-shirt; train/validation/test lần lượt 7.786/1.669/1.668 ảnh.
- **Mô hình:** YOLO11n, YOLOv12n, YOLOv13n và YOLOv13s; năm seed cho mỗi mô hình, tổng 20 lượt huấn luyện.
- **Ngân sách:** các mốc 5, 10, 20, 30, 60 và 120 phút. Checkpoint được chọn bằng validation; test dùng để đánh giá.
- **Thiết bị/cấu hình:** RTX 5060, đầu vào 416 px, batch huấn luyện 8. Đo latency riêng ở batch 1, FP32.

Đây là benchmark phát hiện người trên bộ ảnh đã chọn. Việc có ảnh áo đối kháng trong dữ liệu **chưa chứng minh khả năng phát hiện patch, chống Visual DoS hoặc giữ dịch vụ camera khi bị tấn công**.

## 3. Kết quả chính nên hiểu thế nào?

| Mô hình | Mốc được chọn theo validation | Test mAP@0.5:0.95 (%) | Latency pipeline (ms/ảnh) |
|---|---:|---:|---:|
| YOLO11n | 120 phút | 42,44 ± 0,22 | 2,58 ± 0,42 |
| YOLOv12n | 120 phút | 40,49 ± 0,31 | 2,77 ± 0,07 |
| YOLOv13n | 5 phút | 40,80 ± 0,97 | 4,16 ± 0,21 |
| YOLOv13s | 10 phút | 47,97 ± 1,13 | 51,79 ± 2,08 |

`mAP` cao hơn cho thấy chất lượng phát hiện tốt hơn theo phép đánh giá này; latency thấp hơn nghĩa là xử lý nhanh hơn. Dấu `±` là độ lệch chuẩn giữa năm seed/checkpoint.

**YOLOv13s đạt mAP cao nhất nhưng chậm nhất.** YOLO11n có độ trễ thấp nhất và mAP cao hơn hai bản n còn lại ở các mốc được chọn. Đây là kết quả của cấu hình đã đo; các hàng dùng ngân sách khác nhau, và bản s lớn hơn các bản n.

“Sweet spot” là mốc sớm nhất có mAP validation trung bình cách đỉnh quan sát trong 120 phút không quá 0,5 điểm phần trăm. Nó được xác định sau khi xem toàn bộ quỹ đạo. YOLOv13n/s chọn checkpoint epoch 1 ở cả năm seed: **chưa thể diễn giải thành hội tụ ổn định trong 5–10 phút hoặc lợi ích rõ ràng của fine-tuning**. Cần đo trọng số pretrained ở mốc 0.

Latency trên bảng không gồm đọc/giải mã ảnh, camera và I/O ứng dụng. Không lấy `1000/latency` để cam kết FPS camera thực tế.

## 4. Review đã xác minh tới đâu?

**Đã đối chiếu:** 20 training records, hash của 20 lịch sử epoch, 119 mốc hợp lệ, cách chọn checkpoint theo validation/timestamp CSV, các tổng hợp mAP/SD/CI và 20 bản ghi latency. Các phép tính được kiểm tra khớp báo cáo. Một mốc YOLOv13s seed 2026 ở 5 phút thiếu epoch hoàn tất được giữ đúng là thiếu, không điền bằng 0.

**Chưa tái chạy độc lập:** huấn luyện, test mAP từ checkpoint, độ trễ GPU và kiểm tra ảnh/nhãn fullscale. Gói đang có thiếu dataset fullscale, checkpoint đã huấn luyện và source YOLOv13 đúng bản đã chạy. Vì vậy, “số tổng hợp khớp” không đồng nghĩa toàn bộ nghiên cứu đã được tái lập.

Audit checksum source trả exit 1: 162 file YOLOv12 khác byte do xuống dòng CRLF trên Windows; khi chuẩn hóa về LF trong bộ nhớ thì khớp toàn bộ. Báo cáo giữ rõ kết quả này, không gọi toàn bộ audit là PASS.

## 5. Sáu điểm cần xử lý

| Mã | Vấn đề | Vì sao cần sửa trước lượt tiếp theo |
|---|---|---|
| F01 | Cache kết quả chưa khóa đầy đủ cấu hình/nguồn | Đổi ngân sách hoặc input vẫn có thể dùng lại kết quả cũ. |
| F02 | Setup lấy YOLOv13 HEAD, chưa pin bản đã đo | Cài mới có thể tạo implementation khác máy thực nghiệm. |
| F03 | Generator cần `runs/train` dù đã có CSV lưu trữ | Chưa sinh lại báo cáo chỉ từ gói bằng chứng được chia sẻ. |
| F04 | Timestamp CSV có thể đứng trước lúc lưu checkpoint xong | Cần mô tả đúng ngân sách thời gian; chưa có timestamp để chứng minh checkpoint sẵn có trước hạn. |
| F05 | Chưa ghi đầy đủ threshold/config của accuracy và latency | Hai phép đo có thể dùng operating point khác nhau, ảnh hưởng NMS và cách chọn triển khai. |
| F06 | Chưa lưu raw timing và hash đầy đủ của checkpoint fine-tuned | Chưa tính lại được median, p95/p99 hoặc truy vết đầy đủ số đo. |

Chi tiết file/dòng, điều kiện lỗi và giới hạn xác minh nằm trong [báo cáo review](docs/2026-10-13_research-review-report_VI.md#5-những-vấn-đề-cần-xử-lý). Các mục này **không phải bằng chứng số liệu hiện tại đã bị sửa hoặc bị trộn**. Chưa áp dụng bản sửa code trong lượt review.

## 6. Làm gì tiếp theo?

Thứ tự đề xuất để tác giả quyết định:

1. **Lấy gói bằng chứng từ máy đồng đội:** manifest và split dữ liệu, source YOLOv13 đúng commit, trọng số/checkpoint cùng SHA-256, log và predictions/timing thô nếu có. Chưa cần chạy lại 40+ giờ huấn luyện chỉ để kiểm tra số tổng hợp.
2. **Sửa đường tái lập:** khóa config khi resume, pin môi trường, cho generator đọc CSV đã lưu và công bố cấu hình đo accuracy/latency.
3. **Đo baseline pretrained mốc 0**, rồi xem lại learning rate/warm-up qua validation để giải thích checkpoint epoch 1.
4. **Đo latency lặp với thứ tự ngẫu nhiên**, lưu từng ảnh và tail latency; kiểm tra thiết bị/pipeline dự kiến triển khai.
5. **Kiểm tra ngoài miền**, tách người/video và làm rõ ảnh có thể trùng pretraining.
6. Nếu mục tiêu cuối vẫn là **Visual DoS**, bổ sung phép thử riêng về candidate/NMS, deadline, hàng đợi và chất lượng dịch vụ với đối chứng sạch/tấn công.

## 7. Tìm dữ liệu và nguồn ở đâu?

| Thư mục/file | Nội dung |
|---|---|
| [Fullscale experiments](project_yolov13/results/fullscale_experiments/) | Training records, epoch histories, latency summaries và trạng thái thực nghiệm |
| [Fullscale setup](project_yolov13/results/fullscale_setup/) | Provenance, phiên bản và audit dữ liệu đã lưu |
| [Review evidence](_provenance/review_evidence/) | Báo cáo chi tiết, log và scripts kiểm tra |
| [Assembly manifest](_provenance/assembly_manifest.json) | File từ nhánh thực nghiệm, hash và lịch sử hợp nhất |
| [Local before overlay](_provenance/local_before_overlay/) | Phiên bản cục bộ khác nội dung được giữ trước khi hợp nhất |

Các báo cáo lịch sử trong `results/` giữ phạm vi/ngày của chúng. Để đọc kết quả mới, bắt đầu bằng **BaoCao_TrienKhaiRong_YOLOv13.md** và review ngày **13/10/2026**. Phần Sponge/NMS trong `outputs/extended_q1_20261002` là bằng chứng bổ sung riêng.
