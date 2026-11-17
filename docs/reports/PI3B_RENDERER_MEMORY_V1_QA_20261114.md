## Đã xong

- Tách bộ đo RAM mới khỏi code, cache và các lượt đo cũ. Tag kỹ thuật
  `qa-pi3b-renderer-memory-v1-20261114` khóa tại
  `d58118f8162398925076c4ac0fe0d1db856694d0` trước kiểm thử trên Pi.
- Bộ kiểm thử host cuối đạt77test; phiên65test ban đầu và cả hai log được
  giữ nguyên. Các tình huống mới kiểm cổng smoke/full, thứ tự ngẫu nhiên theo
  chỉ số ảnh gốc, thiếu review, raw bị đổi, sai phase, restore/controller lỗi
  và giá trị báo đạt sai kiểu. Đây là dữ liệu tổng hợp để kiểm code, không
  phải số RAM hoặc hiệu quả thuật toán.
- Năm tình huống dùng tiến trình ngủ trên Pi đều đạt: kết thúc bình thường,
  dừng tiến trình cha, dừng tiến trình con, hết thời hạn và mất kết nối phía
  máy điều khiển. Đã đối chiếu39file gốc bằng SHA256 giữa remote-trước,
  local và remote-sau;14file nguồn/tham chiếu trên Pi giữ nguyên so với tag.
- Kiểm độc lập sau khi kết thúc xác nhận governor, cấu trúc/ưu tiên swap,
  helper/timer và runtime masks khôi phục đúng ban đầu; tiến trình con gốc
  đã mất, service inactive/MainPID0. SSH vẫn mở. Không import Torch/scipy
  trong payload ngủ, không tạo scientific registration hay đo RSS mới.
- Phần đọc counters NMS đạt10test tổng hợp riêng: nhận diện đúng process/
  calling-thread/cgroup, từ chối counter giảm hoặc đổi định danh, giữ trạng
  thái UNAVAILABLE khi không đọc được. Chưa chạy tracer trên workload NMS.

Nguồn: `sponge-sim/results/pi3b_renderer_memory_v1_qa_20261114/`
(`pytest_01.log`, `pytest_02.log`, `source_preparation.json`,
`device_qa_outcomes.json`, từng `qa_*.assessment.json`, `runs/`,
`remote_before_fetch.json`, `remote_after_fetch.json`,
`transfer_verification.json`, `final_verification.json`).
Counters: `sponge-sim/results/pi3b_nms_trace_qa_20261114/verification.json`
và log kiểm thử đi kèm. Mỗi receipt chứa SHA của nguồn/raw liên quan.

## Phát hiện cần biết

- Case mất kết nối vẫn có cảnh báo systemd không mở được transient unitfile
  tại `2026-11-14T16:54:23+00:00`. Log giữ nguyên; nguyên nhân chưa xác định.
  Đây là hiện tượng đã xuất hiện trong QA trước. Quan sát READY, kết thúc
  bình thường, child identity gone và restore/readback vẫn đạt tiêu chí
  đã định trước. Không suy từ đó rằng mọi lỗi systemd đều vô hại. Traceback
  case dừng child là lỗi được chủ động tiêm và phải kết thúc đúng nhánh đó.
- QA ngủ chỉ kiểm những tiến trình con trực tiếp đã xác định. Nó không
  chứng nhận phục hồi khi kernel treo, mất điện hoặc mọi dạng descendant.
  Test trên host không thay cho kiểm bộ đo RSS thật trên Linux/aarch64.
- Chưa có số tiết kiệm RAM hoặc tốc độ của renderer mới. Endpoint dự kiến
  là whole-process high-water RSS sau hash đầu ra, có cả import/cache/warmup/
  allocator. Không thể gọi đó là peak riêng renderer hoặc trừ RSS khởi động
  để tạo một con số tiết kiệm giả. Đỉnh RAM lúc khởi động có thể che hiệu ứng.
- Draft mới định trước smoke kỹ thuật hai ảnh9+30 (có K300),36processes,
  A/A/MDE chỉ chẩn đoán; smoke không tạo kết luận hiệu quả. Full20/360processes
  vẫn phải đạt bias/MDE của cả clean và adv. Chính sách này được ghi trước
  RSS đầu tiên, không sửa protocol hoặc kết quả FAIL của pilot latency cũ.
- Kết quả Pi full20 cũ giữ nguyên: main đạt, component NMS không đạt,
  PI1 chưa chạy. Đọc counters và đo RAM riêng không giải quyết thay cổng
  timing NMS, chưa xác định nguyên nhân biến động và chưa chứng minh DoS.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Hoàn thiện khóa khoa học, PREREG/tag, chạy một smoke RSS theo đúng draft
và đọc toàn bộ cổng/khôi phục trước full → gõ: "Tiếp tục phép đo RAM Pi".

B. Hoàn thiện tracer NMS với đối chứng thao tác đọc counters và cân bằng
workload đi trước; đăng ký riêng trước đo → gõ: "Tiếp tục điều tra NMS Pi".

Không tự chạy lại protocol NMS/PI1 đã đóng hoặc thay ảnh/ngưỡng để lấy PASS.
Kế hoạch RSS cụ thể ở
`sponge-sim/prereg/DRAFT_PI3B_RENDERER_MEMORY_V1_20261114.md`;
engineering QA không cấp quyền chạy full khoa học thay cho các cổng đó.

## Đang chờ gì ở tôi

Không cần duyệt lại code hoặc QA đã cho phép. Chưa có workload đo khoa học
đang chạy sau bước này; việc tiếp theo còn phải khóa PREREG/tag và thực hiện
smoke, review theo quy trình. Không có yêu cầu đổi nguồn, cài gói hoặc tắt SSH.
