# Pi renderer — bộ cache và bộ thu bộ nhớ riêng: QA trên host

## Đã xong

Tiếp nối code renderer tại commitf438ab9, đã thêm bộ chuẩn bị cache và bộ thu
high-water RSS riêng trong `sponge-sim/studies/pi3b_renderer_prealloc_20261114/`.
Đây là code chuẩn bị, **chưa triển khai/chạy phép đo mới trên Pi**.

- `build_cache.py`: chuẩn bị đúng20 cặp ảnh đã khóa, kiểm SHA weights/inputs,
  phiên bản Pi và NMS/ops, ràng buộc summary full20 đã chấp nhận. Đầu ra40cache
  clean/adv được kiểm số đếm và parity mask baseline/candidate. Không tạo số
  latency/RSS. Chỉ cho phép context chuẩn bị có supervisor trên Pi thật.
- `cache.py`: file mới mở exclusive, kiểm schema/shape/FP32/finite/ID/SHA,
  không path traversal, không load file trước khi SHA khớp. Hash mask qua
  memoryview; không tạo thêm bản byte lớn. Kiểm hai renderer tuần tự và thả
  output thứ nhất trước renderer thứ hai.
- `memory_worker.py`: một tiến trình mới cho mỗi case/arm. Endpoint dự kiến
  là `ru_maxrss` Linux lấy sau renderer và outputdigest, gồm cả import,
  cachevalidation, warmupK1 nếu có, allocator/workspaces. Không nạp model,
  không trừ RSS ban đầu để gọi là peak riêng renderer, không ghi latency.
- `memory_campaign.py`: parent không import Torch; kiểm khoa học chỉ cho đúng
  baselineA/baselineB/candidate16M, cả clean/adv,3lặp×20ảnh, tổng360child hữu
  hạn. Lịch shuffle theo seed cố định; child180s/campaign21600s. Guard thiếu
  điều kiện hoặc child thất bại thì dừng, giữ file, không retry.

**37 kiểm tra cache/collector đạt trên source cuối**, log
`sponge-sim/results/pi3b_renderer_cache_qa_20261114/pytest_03.log`,7.37s.
Lượt trước gồm cache controls và12rendererparity cũ cũng đạt; lịch sử cả ba
lượt giữ trong `verification.json:test_runs`. Thời gian pytest chỉ là thông
tin QA, không phải endpoint hiệu năng. Source/log/testSHA nằm trong receipt.

Các case kiểm: cache roundtrip và từ chối ghi đè; tensor sai shape/dtype/NaN;
file hỏng bị chặn trước Torchload; đường dẫn/ID sai; thiếu/trùng/đảo cohort;
không giữ hai output cùng lúc; parity sai phải FAIL; parentimport không kéo
Torch; lịch360job đúng và tái tạo từ seed; child exit0/exit23; timeout; guard
dừng; lỗi ghi journal sau spawn; lỗi trước spawn; không tái dùng jobdir;
đổi source/config phải bị từ chối.

Nguồn: `sponge-sim/tests/test_pi3b_renderer_cache_collector.py` và
`results/pi3b_renderer_cache_qa_20261114/verification.json`. Đây là kiểm host
với tensor tổng hợp và sleeping child của chính test, không phải chứng nhận
trên Pi hoặc bằng chứng đã giảm RAM/tăng tốc.

## Phát hiện cần biết

- Parent collector mà import Torch sẽ giữ thêm runtime trong RAM1GB. Đã tách
  import tensor vào worker/hàm dùng tensor; kiểm bằng một Pythonprocess sạch
  xác nhận importcollector không có Torch trong `sys.modules`.
- Rà code trước QA phát hiện đường lỗi ghi `started.json` sau spawn cần nằm
  trong phạm vi cleanup. Đã đặt việc terminate/kill/wait trong finally ngoài;
  test tiêm lỗi journal chứng nhận directchild được thu hồi trên host. Không
  tuyên bố đây là một lỗi từng xảy ra trong phiên đo Pi.
- Cleanup trên host chỉ phủ directchild thuộc Popen của runner. SIGKILLparent,
  descendant/cgroup và khôi phục governor/swap phải có supervisor độc lập và
  QA trên Pi; hiện chưa làm với source này. Không suy từ test Windows rằng
  mọi đường chết trên Linux/board đã an toàn.
- BaselineA/B bộ nhớ và nhánh clean được bổ sung vào DRAFT trước mọi số đo
  biến thể, tránh chỉ kiểm ảnh nhiễu có lợi. Giữ mọi ảnh kể cảK0/tải nhỏ, nơi
  high-water import có thể che tác dụng renderer. Cổng dự kiến absmeanlog≤.02
  và MDElog≤.05 cho cả hai A/A; analyzer/PREREG cuối còn cần hoàn thiện.
- Đã sửa một lỗi nhãn hình của gói full20: ảnh77 có vị trí14, không phải15.
  Hình mới `component_diagnostics_corrected.png/pdf` lấy index từ ID thực,
  hình cũ giữ nguyên; `figure_label_correction.json` ghi lịch sử. Raw, vị trí
  các điểm và mọi thống kê không đổi.

Chưa có cache thực40case, actual-device output parity, peakRSS thực đo, timing
renderer, hay scientificregistration/tag. Các cổng lỗi NMS và PI1hủy của
full20 giữ nguyên; code này không phải một lượt chạy lại để cứu chúng.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Hoàn thiện supervisor/analyzer, kiểm việc khôi phục và chuẩn bị protocol
cụ thể trước khi xét đo mới → gõ: **"Tiếp tục hoàn thiện bộ đo renderer"**.

B. Đối chiếu gói full20 và bản thảo trước → gõ: **"Check báo cáo Pi full20"**.

Draft cập nhật: `sponge-sim/prereg/DRAFT_PI3B_RENDERER_PREALLOCATION_20261114.md`.
Không tự mở một campaign khác sau cổng thất bại; mọi thiết kế mới phải được
khóa và xem xét riêng, giữ kết quả cũ nguyên vẹn.

## Đang chờ gì ở tôi

Không có — phần chuẩn bị code/QA độc lập vẫn làm tiếp được. Chưa yêu cầu bạn
duyệt phép đo khi supervisor/analyzer và protocol còn chưa hoàn thiện. SSH giữ mở.
