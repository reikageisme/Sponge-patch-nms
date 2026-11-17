## Đã xong

- Giữ nguyên reader `counters.py` đã qua10test tổng hợp trên host, SHA256
  `4c18b03e448a241a2a4c551db09337f8a37da2d0ef306f315574cc9fb2f066f4`.
  Khóa engineering tag `qa-pi3b-nms-counters-20261115` tại
  `2703f8857c66eeaa9d15d888816d7b86be3910b4` trước chạy trên Pi.
- Đúng một invocation trên Linux/aarch64 lấy hai snapshot liên tiếp của
  chính process/thread. Kiểm PID/TID/startticks, affinity0–3, delta không
  giảm, schema và trạng thái optional đạt. Không có NMS, model, tensor,
  sleep, clock bracket của operator hoặc ru_maxrss endpoint.
- Đọc được process `ru_minflt`, `ru_majflt`, `ru_nvcsw`, `ru_nivcsw`;
  trạng thái/counters context-switch của calling thread; cgroup `cpu.max`
  và `cpu.stat`. Kiểm một đường dẫn không tồn tại trả UNAVAILABLE.
- JSON gốc trên Pi, bản local và hash đọc lại trên Pi khớp; source giữ
  nguyên. Governor, swaps và affinity trước–sau giống nhau, không cấp lease
  hoặc đổi cấu hình. SSH vẫn mở. Kết quả là PASS_METADATA_API_ONLY.

Nguồn: `sponge-sim/results/pi3b_nms_counter_device_qa_20261115/`:
`source_preparation.json`, `device_invocation.json`, `qa_snapshot_01.json`,
`post_fetch_verification.json`, `verification.json`. SHA trong receipt nối
raw với source/tag. Kế hoạch: `prereg/QA_PI3B_NMS_COUNTER_METADATA_20261115.md`.

## Phát hiện cần biết

- Scope thực là `/user.slice/user-1000.slice/session-319.scope` của SSH,
  chưa phải cgroup của workload NMS được systemd giám sát. Không suy khả năng
  đọc trong SSH thành đã kiểm đầy đủ cgroup của experiment tương lai.
- `memory.events` và `memory.pressure` trả FileNotFoundError trong scope này;
  raw/delta giữ UNAVAILABLE/null. Không ghi0, không kết luận không có memory
  pressure, OOM, paging hay mọi hình thức CPU throttling. Chưa đọc quota
  ancestors hoặc toàn bộ worker threads của Torch.
- Delta chứa cả thao tác observer ngoài vùng clock của operator. CPU clocks
  trong raw chỉ xác minh API tự quan sát, không phải số NMS hoặc số overhead
  được đo/hiệu chỉnh. Context switches không phải thời gian chờ; process
  CPU time không phải thời gian CPU riêng của calling thread.
- Muốn điều tra cơ chế cần kiểm inventory worker threads/cgroup thực, đối
  chứng sham cho observer, và thứ tự predecessor mask/NMS cân bằng, cố định
  trước đo. Cổng NMS timing cũ vẫn FAIL; không chấm lại hoặc loại ảnh77.
- SSD gắn để thêm dung lượng không bị tháo/eject/mount trong QA này. Metadata
  không tạo tải model nên không thay đổi cổng của protocol RSS-V1 đã đóng.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Hoàn thiện instrumentation và sham/matched-predecessor protocol trước
phép đo NMS mới → gõ: "Tiếp tục tracer NMS có đối chứng".

B. Hoàn thiện guard/preflight và review phương án RSS có USB nhàn đã soạn,
giữ nguyên V1 FAIL → gõ: "Tiếp tục phương án RSS có USB".

Không đo từ engineering tag này. Mọi endpoint mới vẫn cần PREREG/tag,
điều kiện vật lý đã khai báo và cổng đầy đủ, không tự bỏ dữ liệu khi FAIL.

## Đang chờ gì ở tôi

Không cần mở lại SSH hay cấp lại quyền code/QA đã cho phép. Người dùng đã
xác nhận mục đích giữ SSD. Hiện không có workload đo đang chạy; điều kiện
USB mới và instrumentation khoa học vẫn phải hoàn thiện trước đăng ký/đo.
