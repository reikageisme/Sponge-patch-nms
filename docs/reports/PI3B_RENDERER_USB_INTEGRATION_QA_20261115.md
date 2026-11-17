## Đã xong

- Tích hợp guard USB vào source riêng `pi3b_renderer_memory_usb_20261115`:
  frontend kiểm trước tạo thư mục/cấp lease; payload kiểm lại trước mutation;
  parent/child dùng cùng baseline và ghi hash; auditor kiểm lại mọi frame.
  Full eligibility còn ràng buộc hash USB của smoke, không thay baseline khi
  đã thấy I/O. Static identity đăng ký riêng, baseline mới cho mỗi phase.
- Giữ nguyên AST renderer/cache/thống kê, System/Lease/record/validate_snapshot
  và các kiểm không liên quan USB. Giữ40cache,20ảnh, thứ tự, số lặp, endpoint
  và cổng A/A/MDE. Helper USB giữ nguyên SHA đã qua metadata QA465f6e5.
- Host cuối130testPASS120.15s. Log đầu129PASS/1FAIL do test đọc docstring
  tiếng Việt bằng cp1252; sửa encodingUTF8, không giảm assertion; giữ cả hai log.
  RSS của fixture là tổng hợp, không phải kết quả Pi.
- Engineering tag `qa-pi3b-renderer-memory-usb-20261115` khóa tại
  `c6a9747643b097595055cbdf7e7317ed48e8e10e`. Năm case ngủ trên Pi đều đạt:
  normal, kill main, kill child, timeout và mất kết nối localSSH. READY kiểm
  USB/hash thực trước fault. Normal15s thay5s được định trước QA để đủ thời
  gian kiểm bổ sung qua SSH, không phải chỉnh sau thất bại.
- Thu đủ44file gốc/39412bytes, SHAremote/local/remote khớp.16file gói cùng
  metadata gốc cũ được giữ đúng byte (readiness đếm17file ở root vì gồm một
  raw metadata cũ). Child gốc đã mất; independent restore/readback xác nhận
  governor, swap/helper/timer/masks đúng ban đầu, service inactive/MainPID0.
  Không Torch/scipy/model/render/RSS/latency, không mount/eject; SSH vẫn mở.

Nguồn: `sponge-sim/results/pi3b_renderer_usb_integration_qa_20261115/`:
`pytest_01.log`, `pytest_02.log`, `source_preparation.json`,
`registration_check.json`, `device_qa_outcomes.json`, `qa_*.assessment.json`,
`runs/`, `transfer_verification.json`, `final_verification.json`.

## Phát hiện cần biết

- Disconnect có warning transientunitfile không còn tại UTC17:58:31 ngày14/11;
  log giữ nguyên, nguyên nhân chưa xác định. READY, expected completion,
  child gone, restore/readback vẫn đạt tiêu chí đã khóa. Không kết luận mọi
  cảnh báo systemd đều vô hại. Traceback kill-child là lỗi chủ động tiêm.
- Đây là QA luồng điều khiển và khôi phục với child ngủ trực tiếp; chưa phải
  peak RSS, tốc độ, phục hồi mất điện/kernel treo hoặc mọi descendant tree.
  Scientific registration chưa có tại lúc QA; engineering tag không tự mở đo.
- USB phải đúng topology, unmounted/no-holder và nhàn trong phase; cache/log
  vẫn trên SD. Dùng SSD ngoài phase được phép. Dùng làm active data disk
  trong phase là điều kiện khác, không tự mount/chuyển dữ liệu hoặc nới gate.
- RSS-V1 USB-absent vẫn FAIL0/36/full hủy, không retry. Main Pi full20 cũ vẫn
  đạt, component NMS vẫn FAIL, PI1 chưa chạy. Chưa có số tiết kiệm RAM mới,
  chưa chứng minh cơ chế NMS hoặc DoS.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Khóa protocol/config/manifest và tag khoa học cho USB-present; đúng một
smoke trước full, giữ toàn bộ kết quả → gõ: "Tiếp smoke RAM có USB".

B. Tiếp instrumentation thread-pool/cgroup/sham/matched-predecessor cho NMS
trước phép đo riêng → gõ: "Tiếp tracer NMS".

Chỉ full sau smoke/audit/restore và review kết quả cụ thể; không suy quyền
full từ QA hoặc tự mở lại tag V1.

## Đang chờ gì ở tôi

Không cần mở SSH, tháo SSD hay duyệt lại code/QA đã cho phép. Không có
workload đo đang chạy ở checkpoint này; mọi điều kiện khoa học vẫn cần
PREREG/tag trước đo, các kết quả không đạt được giữ nguyên.
