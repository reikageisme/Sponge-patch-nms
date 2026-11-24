# Đăng ký trước A/A trên Linux khóa xung

24/11/2026. Phép hiệu chuẩn trên ảnh sạch theo E5; khác máy so với E5 gốc.
Môi trường đo là Xubuntu Live 24.04.5 LTS, kernel 7.0.0-31-generic, AMD Ryzen 5 5500,
CPU logic 2, governor `performance`, giới hạn 3600000 kHz, global boost tắt, CPU 8 offline.
Trong phép kiểm phần cứng trước nghiên cứu, tải SHA-256 cho `Bzy_MHz` 3574 trong 45/45 mẫu.
Kết quả A/A trước đây trên Windows đã được xem; đây là hiệu chuẩn mới trên cấu hình cụ thể.
Chốt thiết kế và mã bằng commit và tag `prereg-aa-linux-20261124` trong bản sao thực nghiệm trước smoke và phiên chính.

## Thiết kế

- Dùng đúng 100 ID ảnh sạch COCO val2017 trong `studies/e5_protocol/run.py:IMAGE_IDS`,
  cùng trọng số YOLOv8n với E5 (SHA-256 `f59b3d833e2ff32e194b5bb8e08d211dc7c5bdf144b90d2c8412c47ccfc83b36`).
  Lưu URL, ID, kích thước và SHA-256 ảnh tải xuống. Đối chiếu trọng số với manifest E5.
- Hai phiên độc lập tuần tự 320 rồi 640 px, FP32, batch 1, một thread inter-op và một thread intra-op.
  Hai nhãn dùng cùng đường xử lý và cùng ảnh. Mỗi ảnh một warm-up rồi 10 lượt A và 10 lượt B
  theo ABBA hoặc BAAB với seed E5. Dùng resize RGB bilinear trực tiếp. Giữ thứ tự ảnh, khối 10 ảnh
  và điểm tham chiếu E5. Smoke kỹ thuật ở mỗi kích thước gồm 4 ảnh, 2 lượt mỗi nhãn, không gộp vào phiên chính.
- Giữ các phiên bản Torch CPU 2.13.0, torchvision CPU 0.28.0 và Ultralytics 8.4.90 của E5 gốc.
  Python và bản dựng Linux được ghi trong manifest. Ghi phiên bản phụ thuộc và SHA-256 dữ liệu trước đo.
- Ghi hiệu chuẩn phần cứng trước và sau mỗi phiên bằng `turbostat`, chấp nhận khi toàn bộ mẫu trong ±1%
  mục tiêu và Busy% ≥ 95. Kiểm trạng thái CPUFreq và affinity dưới tải trước và sau mỗi phiên.
  Ghi độ trôi của tham chiếu E5 so với đầu phiên, cờ khi độ lệch tuyệt đối lớn hơn 3%.

## Endpoint và quyết định

- Chính cho từng canvas: tỷ số trung bình hình học giữa trung vị A và B theo ảnh của `forward` và `total`,
  CI95% bootstrap percentile 20.000 lần theo ảnh, seed 20261021, và MDE công suất 80%, alpha 0,05
  trên log tỷ số rồi đưa về phần trăm, theo E5. `total` bấm trực tiếp đường load/resize, forward, decode,
  lọc điểm và NMS pure PyTorch. Đây là thời gian theo định nghĩa E5, cần khớp định nghĩa trước khi áp MDE sang một phép đo khác.
- Phụ: thống kê cho các công đoạn còn lại, độ biến thiên trong ảnh, độ trôi tham chiếu và tỷ phần NMS.
  Chạy độ nhạy bỏ khối drift đầu khối theo quy tắc E5, giữ kết quả chính gồm toàn bộ khối. Điểm kết thúc
  bị cờ vẫn được báo cáo. Khi không còn đủ ảnh cho CI trong phân tích độ nhạy, ghi không ước lượng được.
- Audit tính đầy đủ: mỗi phiên chính đúng 100 ảnh, từng ảnh có đủ 10 lượt A và 10 lượt B, đúng thứ tự
  đã ấn định, 2.000 dòng đo, 11 điểm tham chiếu, và ghim/khóa đạt ở hai đầu. Audit smoke dùng số lượng
  cấu hình smoke. Giữ raw mọi lượt kể cả lượt hỏng. Báo CI lệch khỏi 1 hoặc khối bị cờ đúng nguyên trạng.
  Không chọn giữa nhiều lần chạy theo MDE hay CI. Nếu hỏng kỹ thuật thì ghi lý do trước khi chạy lại.
- Chỉ mô tả chênh lệch với số Windows. Thiết kế dùng đồng thời CPU, hệ điều hành và bản dựng khác nhau,
  nên không ước lượng riêng ảnh hưởng của việc khóa xung. CI bao gồm 1 không phải một kiểm định tương đương.

Đầu ra: manifest, raw JSONL, summary, log kiểm xung và pin, manifest ảnh, freeze môi trường và thông tin tag.
