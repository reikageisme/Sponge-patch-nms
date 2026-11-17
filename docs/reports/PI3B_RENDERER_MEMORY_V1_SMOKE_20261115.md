## Đã xong

- Đăng ký trước protocol RSS-V1 dưới tag
  `prereg-pi3b-renderer-memory-v1-20261114`, commit
  `289c2e373c6f965337aaeea7edddc1d7ade29497`. Đuôi ngày giữ theo kế hoạch/UTC
  14/11; giờ Việt Nam đã sang15/11. Chín file runtime giữ nguyên bản đã qua
  77test host và năm tình huống QA trên Pi, không sửa sau tag.
- Khóa protocol, cấu hình, model/input/cache hashes; lưu manifest trước tải
  ở local và Pi. Kiểm40cache nguyên trạng trước khi mở đúng một smoke.
- Smoke kết thúc không đạt trước tiến trình đo đầu tiên: **0/36 mẫu RSS**.
  Guard báo USB; không có tiến trình con, render hoặc đọc ru_maxrss. Full20
  không bắt đầu và bị hủy theo protocol. Không chạy lại.
- Thu đủ10file gốc,8588bytes; SHA256 remote-trước/local/remote-sau khớp.
  Runtime/protocol/reference/cache hashes giữ nguyên. Restore báo RESTORED,
  errors rỗng; kiểm độc lập xác nhận governor, swap/helper/timer/masks đúng
  ban đầu, service inactive/MainPID0, không có worker đo. SSH vẫn mở.

Nguồn ở `sponge-sim/results/pi3b_renderer_memory_v1_20261114/`:
`runs/memory_smoke_01/manifest.json`, `runs/memory_smoke_01/original/`,
`runs/memory_smoke_01/summary.json`, `smoke_transfer_verification.json`,
`smoke_remote_before_fetch.json`, `smoke_remote_after_fetch.json`.
Schedule có36job; `original/memory/raw.jsonl` có0dòng và SHA256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
Guard đầu tiên `original/memory/guards.jsonl:1` ghi `usb=["sda","sdb"]`;
`original/memory/terminal.json` và `original/supervisor.log` ghi nguyên nhân.

## Phát hiện cần biết

- Đây là lỗi cổng điều kiện thiết bị, không phải bằng chứng thuật toán
  không chạy, hết RAM, hoặc không tiết kiệm RAM. Không có số RSS/CI/MDE
  thực nghiệm để báo cáo; không lấy QA chức năng hoặc mẫu cũ thay thế.
- Kiểm tra chỉ đọc sau terminal nhận diện `sda` là ADATA SP900 qua
  SupTronics X89/USB hub, `sdb` cùng adapter có dung lượng0sector. Kiểm thêm
  `sda1` không thấy mount hoặc holder tại thời điểm đọc; workspace nằm trên
  thiết bị179:2. Metadata tức thời không cho phép tự eject/tháo ổ hoặc kết
  luận USB gây sụt áp/chậm NMS. Người dùng xác nhận cắm SSD để thêm dung
  lượng; đây là cấu hình chủ đích, không yêu cầu tự động tháo SSD.
- Preflight đã kiểm source/swap/cache nhưng thiếu kiểm USB trước khi cấp
  lease. Guard runtime vẫn chặn đúng trước job đầu tiên. Đây là thiếu sót
  preflight cần sửa cho thiết kế tương lai; không sửa source đã tag, nới
  cổng USB hoặc tạo smoke02 để cứu lượt đã đóng.
- Runtime15.817s trong frontend là thời gian vận hành service bị hủy, không
  phải latency renderer. Không ngoại suy full từ0job;
  `smoke_operational_budget.json` để ước lượng full lànull.
- Main Pi full20 cũ vẫn đạt, component NMS vẫn không đạt, PI1 vẫn chưa chạy.
  RSS-V1 không xác định cơ chế NMS và không chứng minh DoS.

USB receipts: `readonly_usb_diagnosis.json`, `readonly_usb_partitions.json`.
Kiểm đầu chỉ xét disk; kiểm bổ sung bao gồm `sda1`, giữ cả hai receipt.
Không đọc nội dung ổ, mount/eject hoặc đổi hệ thống.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Review một thiết kế RSS mới với cấu hình SSD hiện có; giữ V1 FAIL và
ngưỡng chất lượng/ảnh/renderer nguyên → gõ: "Xem phương án RSS có USB".

B. Tiếp tục tracer NMS và QA đọc counters Linux không tải model,
không chạm protocol RSS đã đóng → gõ: "Tiếp tục phần counters NMS".

Không tạo `smoke_review.json` đạt giả hoặc tự mở full. Mọi thay đổi phải
được mô tả trước PREREG/tag; không lặp protocol tới khi kiếm được PASS.

## Đang chờ gì ở tôi

Bạn đã xác nhận SSD dùng để thêm dung lượng. Chưa tự mount/eject, sửa gate
hay chạy lại. Tiếp tục chuẩn bị phương án USB riêng và code/QA metadata;
không có workload đo khoa học đang chạy.
