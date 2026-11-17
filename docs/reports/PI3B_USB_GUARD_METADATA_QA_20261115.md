## Đã xong

- Viết helper chỉ đọc `usb_guard.py` trong namespace mới
  `pi3b_renderer_memory_usb_20261115`; không sửa guard/renderer/tag cũ.
  Helper kiểm topology/danh tính USB, phân vùng, mount/holder, vị trí dữ
  liệu, diskseq, địa chỉ USB và toàn bộ block-stat hiện có.
- 41kiểm thử tổng hợp đạt trong6.93s. Các nhánh sai/thiếu/thêm thiết bị,
  đổi phân vùng, I/O tăng/giảm, request đang chờ, mount/holder, cache/log
  trên USB, dữ liệu sai kiểu/thiếu và đổi địa chỉ giữa frame đều bị chặn.
- Khóa engineering tag `qa-pi3b-usb-guard-metadata-20261115` tại
  `465f6e5ac27815498e6da6db112e92eabe485f8c` trước đúng một invocation
  trên Pi. Hai frame liên tiếp đạt, cộng ba nhánh âm trên bản sao dictionary
  (sai model, I/O tăng, in-flight); không thao tác lên thiết bị thật.
- API thật đọc6thiết bị USB gồm hub/Ethernet, hai disk `sda/sdb`, phân
  vùng `sda1`, diskseq và17trường block-stat mỗi disk. Cặp frame không có
  lỗi identity/I/O/generation/mount/holder. Workspace mới và cache cũ đều
  trên SD179:2. Governor, cấu trúc swap và affinity trước–sau giống nhau.
- JSON gốc remote/local/remote và source SHA khớp. Không import Torch/scipy,
  chạy model/renderer, tạo tải I/O, đo RSS/latency, mount/eject hoặc đổi
  nguồn/swap/governor. SSH vẫn mở. Kết quả PASS_USB_METADATA_API_ONLY.

Nguồn: `sponge-sim/results/pi3b_usb_guard_qa_20261115/`:
`pytest_01.log`, `source_preparation_final.json`, `registered_materials/`,
`device_invocation.json`, `qa_metadata_01.json`, `verification.json`,
`post_fetch_verification.json`, `final_verification.json`.
Source SHA256 `9a1c2ef0124e5a54ac1d5e0e252c759636443a3d4ea7f7d50edd1b5aff821cd4`.
API frame bắt đầu tại UTC2026-11-14T17:30:19.438784 (00:30:19.438784giờ VN15/11).

## Phát hiện cần biết

- Đây chỉ là helper standalone. Frontend kiểm trước lease, sampler trong
  runner, baseline truyền sang child, auditor và supervisor mới **chưa được
  tích hợp/kiểm**. Không dùng PASS này để mở ngay phép đo khoa học.
- Bản draft đã làm rõ trước mọi RSS: đăng ký danh tính/topology cố định,
  còn absolute counters/diskseq/địa chỉ USB/namespace lấy baseline riêng cho
  mỗi phase. SSD có thể được dùng ngoài phase. Trong phase, mọi thay đổi
  counters hoặc re-enumeration đều bị chặn. Không dùng lifetime counters
  từ hôm trước để cấm hoạt động lưu trữ hợp lệ ngoài thí nghiệm.
- Dữ liệu chỉ nói hai frame kề nhau khớp. Chưa chứng nhận nhiều giờ nhàn,
  ổn định khi có tải, mọi mount namespace hay mọi thao tác hotplug. Model/
  dung lượng/topology không phải chứng thực mật mã của đúng chiếc SSD.
  Không có kết luận USB gây hoặc không gây sụt áp/chậm NMS.
- Guard mới yêu cầu mount/holder USB rỗng và cache/log trên SD theo draft
  hiện tại. Dùng SSD làm nơi lưu dữ liệu trong thí nghiệm là điều kiện khác;
  không tự mount, chuyển workspace hoặc nới cổng sau khi FAIL.
- RSS-V1 vẫn đóng:0/36RSS, full hủy, không retry. NMS timing cũ vẫn không
  đạt cổng; counters NMS đã đọc được API nhưng chưa có sham/pool inventory/
  matched-predecessor mechanism test. Chưa có số tiết kiệm RAM hay speedup.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Tích hợp guard vào frontend trước lease, mọi sampler và auditor trong
source mới; giữ các gate/caches/ảnh/renderer đã dự kiến → gõ:
"Tiếp tích hợp guard USB vào bộ đo".

B. Tiếp instrumentation thread-pool/cgroup và đối chứng sham/predecessor cho
NMS trước protocol mới → gõ: "Tiếp instrumentation NMS".

Chưa có scientific registration/tag cho cấu hình USB-present. Cần regression,
kiểm supervisor/restore và PREREG trước endpoint mới; không tự mở lại V1.

## Đang chờ gì ở tôi

Không cần mở lại SSH, tháo SSD hoặc cấp lại quyền code/QA đã cho phép.
Hiện không có workload đo đang chạy. Không yêu cầu mount/format hay đổi nguồn.
