# DRAFT — ARM thật trên Galaxy A36, không gán số liệu Raspberry Pi

## Material Passport

- Origin: academic-research-suite / experiment-agent, plan + sponge-research.
- Ngày: 06/11/2026.
- Trạng thái: **DRAFT, UNRUN, chưa có PREREG tag**. Không dùng file này làm bằng chứng đã đo.
- Context đã biết: toàn bộ kết quả GPU/CPU thuê và nested1500 đã thấy; phone pin01/11 có bốn profile FAIL. Không retroactive preregistration.
- Người dùng hiện chỉ yêu cầu rà và nghiên cứu thiết kế; chưa có phiên điện thoại rảnh được xác nhận.

## 1. Câu hỏi và phạm vi

Đo trên CPU ARM thật của Galaxy A36: khi nào tăng số ứng viên/detection làm tăng thời gian forward–NMS–mask? Cap trước NMS và cap đầu ra tác động vào stage nào? Mô hình có thành phần mask dự báo tốt hơn mô hình NMS-only trên dữ liệu không dùng hiệu chuẩn không?

Không giả thuyết điện thoại tương đương Pi4/Pi5. Không dùng QEMU time, Geekbench scaling hoặc quota như ground truth board. Giữ tên thiết bị, Android/Termux/proot, package versions và CPU sets thực.

## 2. Gate trước phép đo mới

| Gate | Điều cần xác minh / khóa | Hiện tại |
|---|---|---|
| G0 identity/runtime | Đọc lại kiến trúc CPU, Python/torch/torchvision/ultralytics, compiled backend, CPU-only path; không dùng chuỗi kernel hoặc đuôi CUDA làm chứng cứ đủ | Chưa đọc thiết bị hiện tại |
| G1 thread affinity | Fresh process mỗi profile, mask trước torch, readback từng TID sau warmup và khi chạy; residency của active TIDs; CPU-time/wall-time | Artifact cũ tất cả FAIL; phép kiểm cần amendment |
| G2 thermal/battery | Telemetry phân biệt pin và CPU; supervisor thực thi ngưỡng đã chốt ngay trong tải, có timeout và stop counter; không hiểu denied/missing là nhiệt0 | Runner cũ chưa đáp ứng đầy đủ |
| G3 provenance | Hash weights, frozen inputs, backend source, renderer, scripts/config; checkpoint load tương thích và kiểm output shapes | Có archive local; chưa làm gói phone mới |
| G4 controls | Controls-only warmup/burst/memory/time feasibility; khóa rõ số trial mỗi arm và thứ tự; không chọn profile bằng attacked effect | Chưa chạy; chưa có ước lượng phút hợp lệ |
| G5 authorization/state | Người dùng xác nhận đang sạc ổn định, pin30–80%, rảnh, mạng di động tắt, Wi-Fi tối thiểu/tắt theo cách lấy log; tuân quy tắc đo độc quyền | Chưa yêu cầu cho phiên mới |

G0–G4 không đạt thì chưa chạy full. Không giảm yêu cầu cũ rồi đổi nhãn PASS. Nhánh ARM-unpinned nếu cần phải có protocol/claim riêng. Không root, không sửa Android, không khóa xung, không cài gói hoặc tải dữ liệu từ điện thoại trong nhiệm vụ hiện tại.

## 3. Sửa harness trước khi đăng ký chính thức

- Tách verify worker mới theo profile; pin trước nhập torch, ghi mask main thread và mọi TID tồn tại sau khởi tạo/warmup. Dùng đúng ID từng luồng của chính tiến trình; lỗi quyền hạn ghi rõ, không tìm cách vượt SELinux.
- Residency sampler phải giữ TID/state/CPU-time delta và nhận biết luồng ngủ. Đọc CPU cuối không đủ làm bằng chứng một luồng đang chạy ngoài tập. Ghi cả mask của luồng, không chỉ main readback.
- Giữ kiểm tải thật: one-core upper <=1.15 effective CPUs, lower>=0.5; multi-core upper<=|S|+0.15, lower>=0.7|S| là **gate cũ**, chưa được hạ. Phần sampler thay đổi cần ghi amendment và test bằng fixture tổng hợp; revalidation mới không sửa artifact01/11.
- Hai profile ban đầu đề xuất F1/F4; số CPU cụ thể chưa khóa. CPU nhanh/chậm phải xác minh lại, không mặc định CPU0 hoặc nhóm từ bản01/11 còn đúng.
- Supervisor quan sát nhiệt/pin trong lúc worker hoạt động, đáp ứng chính sách đã có: CPU zone>=70°C hoặc pin>=40°C dừng tải; điều kiện hạ nhiệt55/38°C; ba lần dừng liên tiếp kết thúc phiên. Ghi missing sensors; full không mở khi không có cách thực thi giới hạn pin. Không tự tắt nhiệt bảo vệ máy.
- Tách thời gian stage khỏi tổng đo trực tiếp; khóa rõ class-aware/agnostic semantics, dtype, tensor shape, resize và max_det/max_nms ở mọi nhánh. `total()` phải dùng backend đã khóa. Total cũ là torch_pure agnostic, không phải tổng của stage tv_nms đo riêng.
- Phải có finite timeout, không vòng chờ nhiệt vô hạn. Khóa timeout/RSS limit sau kiểm controls-only và trước smoke/full, không điều chỉnh bằng hiệu ứng tấn công.

Đây là yêu cầu sửa, không phải code đã triển khai hay kết quả các gate đã đạt.

## 4. Bốn giai đoạn đề xuất

### A. Readback và preflight

Tái dùng phạm vi metadata A0 đã được duyệt trong `PREREG_E5_phone.md`; chỉ đọc các file được phép, ghi denied. Chỉ ghi trong `~/sponge-sim`. Kiểm thư viện qua import/cấu hình đang có, không tự nâng version. Dữ liệu đẩy từ archive local, không tải từ Internet bằng điện thoại.

Ghim từng profile trong tiến trình mới; QA riêng bằng matmul có giới hạn thời gian. Không đọc timing/điều kiện tấn công để chọn profile. Mọi số thu được từ bước này là QA, chưa là kết quả attack latency.

### B. A/A và positive control mask

- Model đầu tiên đề xuất: YOLOv8n-seg; exact weight SHA theo gói nested1500. CPU FP32, batch1, unfused eval, 640-square, conf.25, IoU.45, nc80, fixed torchvision NMS.
- Mask workload K10/50/100/300, hai độ phân giải mask theo M2; fixture seed/hash cố định trước chạy. Đây là injection tổng hợp, tách khỏi hiệu quả tấn công.
- Có hai bản clean A/A giống nhau, reference đầu/giữa/cuối, cân bằng thứ tự và timestamp. Ngưỡng drift3% và mọi flags được giữ; số reference/flags tối đa, warmup và repeats phải khóa rõ ở PREREG chính thức sau feasibility controls-only.
- Không chạy việc khác trên local/phone trong thời gian đo, kể cả phân tích, git, web hoặc poll tiến độ. Logger cần thiết của phép đo là một phần harness đã khóa.

### C. Replay tấn công thật trên64 audit images

- Nguồn: `large_seed/cohort1500.json`, toàn bộ `audit=true`; source v8, seed0, exact `audit_adv.npz`. Không chọn theo K, không dùng 64case như64patch seeds.
- 64 ảnh sạch từ contextZIP + exact inputs float32 từ hai stageZIP. So hash trước khi forward. Không dùng phép tái tạo gần đúng rồi gọi là cùng byte input.
- Sáu arm: sạch/nhiễu × baseline/output-cap50/pre-NMS-cap300. A/A bổ sung có tên riêng. Primary là paired baseline total-time ratio; defense contrasts secondary. Cap nhỏ hơn không được tự gọi an toàn vì K* có thể khác trên ARM.
- Đề xuất hai profiles và ba phiên tách biệt. 64 ảnh/3 phiên là lựa chọn thực dụng ban đầu, **chưa chứng minh đủ power**. Dùng A/A để báo MDE và chốt feasibility; mọi thay đổi phải trước đo attack chính thức, không tăng mẫu theo p-value hoặc chọn phiên đẹp.
- Khóa một zero start để replay cùng input, không PGD trên điện thoại; đây là chuyển thực thi sang runtime khác, không phải bitwise repetition của batch4 CUDA Graph. Đếm N và K lại trên ARM, lưu sai khác với GPU.
- Kết quả native26 là nhánh riêng tùy tương thích runtime. Nếu dùng phải kiểm đầu native `[B,300,38]`, score column4>.25 và không NMS; không mặc định model cũ có cùng API.

### D. Dự báo và availability — protocol tiếp theo nếu cần

Khóa tập calibration/test trước khi đo. Tham số predictor chỉ lấy controls/calibration; không dùng attacked NMS/mask time của test để dự báo chính total test. Đánh giá lỗi dự báo và MDE, không chỉ correlation hoặc p-value. So NMS-only với NMS+mask là giả thuyết có thể bị bác bỏ.

Nếu chuyển sang deadline: xác định kỳ phát từ clean controls, khóa trước attack; dùng worker thực sự chạy inference, ghi scheduled_release/start/finish/drop và queue bound. Trước kết luận phải chứng minh sạch khả thi ở kỳ phát đó. Mô phỏng từ service times không thay cho thực nghiệm worker. Không gọi đây là camera test nếu vẫn dùng tensor số.

## 5. Phân tích và artifact cần khóa

- Đơn vị image là64, sessions là3 đề xuất trên cùng một thiết bị; repeats không thành sample độc lập. Không gộp với COCO128 hoặc1500 như cùng experiment.
- Primary paired log-ratio theo image/session; CI20.000 bootstrap, RNG và cách lấy lại image/session phải ghi chính xác trước main run. Với3 sessions, báo từng session và giới hạn độ bất định ở tầng session; không dùng một CI ảnh để nói đã phủ variability mọi thiết bị.
- Mean/median count, reach threshold, paired gain và per-image/runtime differences là secondary. Không mặc định K>=50 là ngưỡng latency ARM.
- Family defense contrasts và Holm nếu kiểm định phải khai trước. A/A sizing không dùng kết luận equivalence; MDE có mặt khi nói không phát hiện hiệu ứng.
- Thu: `manifest.json`, `pin_verify.json`, `thread_masks.jsonl`, `thermal.jsonl`, `raw.jsonl`, per-session summary, quality decisions và SHA/CRC receipt. Paths dưới `~/sponge-sim`; local kết quả ở thư mục run mới, không ghi đè `phone_a36/pin_20261101`.
- Raw timing ghi timestamp và order, GC-off trong vùng đo; buffer dữ liệu ngoài vùng đo. Peak RSS, unreadable sensors và timeout là kết quả phải giữ.
- QA counts/budget/input SHA và backup hoàn tất trước khi coi run xong. Kết thúc SSH theo quy tắc điện thoại trong CLAUDE.md.

## 6. Điều còn phải chốt trước tag

Sửa và review pin/supervisor; xác nhận runtime/checkpoint thật; khóa CPU IDs, memory limit, repeats/trials, burst/warmup/ref/quality thresholds, timeout, split/calibration endpoint, hash cả64inputs và điều kiện phiên rảnh. Smoke nhỏ trước, báo thời gian thật; full theo quy trình dự án. Không có thông số nào trong bản DRAFT được trình bày như kết quả đã thu.

## 7. Cách gọi kết quả

Được: “Galaxy A36, Snapdragon 6 Gen3, Android/Termux/proot, CPU ARM FP32, verified CPU set S, q intra-op threads.”

Chưa được: “Raspberry Pi4/Pi5 simulated measurements”, “hai board ARM bổ sung”, “CPU bị giới hạn tương đương Pi”, “đã chứng minh DoS/physical/camera”. Nếu có board thật, dùng một protocol và artifact identity riêng.
