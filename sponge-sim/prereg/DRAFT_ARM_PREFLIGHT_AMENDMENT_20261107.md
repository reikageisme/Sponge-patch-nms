# DRAFT — điều tra thread pool, sampler và dừng nhiệt A36

Trạng thái: **UNRUN, chưa PREREG/tag; không cho phép đo bằng file này.**
Đã thấy bốn FAIL ngày01/11 và toàn bộ M6/conditioning failures trước khi viết.
Đây là thiết kế sau quan sát, không đăng ký ngược và không sửa các run cũ.
Đi kèm `DRAFT_ARM_A36_SEGMENTATION_20261106.md`; bước này chỉ QA, không attack.

## Vấn đề cần phân biệt

H1: thread pool có mask cũ vì chỉ ghim main thread sau khi pool đã tạo.
H2: sampler đếm CPU cuối của luồng ngủ, tạo FAIL giả về residency.
H3: affinity thật sự không thực thi được cho mọi TID trong môi trường hiện tại.
H1/H2 là giả thuyết kiểm được, chưa là lời giải lịch sử. Cả ba có thể cùng xảy ra.
`little1` CPU-time/wall=1.7581064471255095 >1.15 giữ nguyên FAIL độc lập H2.

## Thiết kế phân biệt tối thiểu trước đo phân đoạn

1. Metadata/readback không tải theo phạm vi A0 đã duyệt; ghi thư viện,
   OpenMP/BLAS, `torch.__config__.parallel_info()`, biến môi trường threading,
   tất cả TID/mask/starttime. Không nâng thư viện, không root hoặc sửa hệ thống.
2. Khóa một logical CPU đọc được (chưa khóa ID, chưa gọi fast/big). Bốn cell
   controls-only, mỗi cell tiến trình mới: pool-init trước/sau main pin ×
   chỉ main pin/áp mask cho mọi TID đang có sau pool warmup. Chưa chọn thứ tự,
   thời gian/ngân sách cuối: phải khóa trước tag, không lặp đến khi PASS.
   Cell pool-before-pin chỉ dùng để phân biệt cơ chế, không thành profile đo.
3. Cùng raw snapshot trong mỗi cell được chấm hai cách: sampler cũ (mọi TID)
   và diagnostic active-only (delta utime+stime>0, ghép bằng TID+starttime).
   Nhờ vậy khác biệt hai sampler không lẫn với hai lượt chạy khác nhau.
4. Sau warmup, readback mask mọi TID và trong tải; không tự sửa mask giữa vùng
   đo để che vi phạm. TID mới/mất, denied, counter giảm hoặc mẫu trống =>
   INCONCLUSIVE/FAIL theo rule khóa trước, không âm thầm bỏ qua. Chỉ sampler
   cần thiết của phép đo được chạy; log chi phí của sampler bằng controls.
5. Giữ nguyên CPU-time/wall upper |S|+0.15, lower0.5 cho một CPU,
   lower0.7|S| cho nhiều CPU. Ghi thời gian CPU process và tổng delta TID để
   phát hiện lệch coverage; không cộng CPU-time child/sshd/proot khác thành
   CPU-time worker rồi so cùng gate. Nếu proc accounting không kiểm được,
   ghi không xác định, không hạ gate.
6. Đề xuất active last-CPU share>=.99 với >=20 active observations, kèm
   exact-mask của TẤT CẢ TID và coverage. Đây là **endpoint sampler mới**,
   không phải cách chấm lại artifact cũ. Last-CPU vẫn không chứng minh residency
   liên tục; không gọi đây là scheduler trace. Phải khóa rule theo interval,
   tổng số samples và xử lý churn trước tag. Chưa có profile nào đủ điều kiện.
7. Nếu fresh+all-TID đạt, mới mở QA1/4-CPU và A/A pipeline. Nếu chỉ sampler
   khác nhau nhưng CPU-time upper vẫn FAIL, không công nhận pin. Nếu permission
   hoặc readback fail, ghi đúng môi trường không xác minh được; không suy
   cả điện thoại hoặc mọi Android không ghim được.

## Dừng nhiệt/pin: các điều kiện đã chốt phải thực thi

- Bất kỳ thermal zone đọc hợp lệ nào>=70C hoặc pin>=40C: ngắt worker đang
  chạy, đánh dấu block dở và lý do. Chờ TẤT CẢ zone<55C VÀ pin<38C mới xét
  đợt mới. Không hiểu dấu `/` trong protocol cũ là chỉ cần một trong hai.
- Ba thermal interruptions liên tiếp kết thúc phiên. Đề xuất định nghĩa rõ:
  chỉ một burst hoàn tất an toàn reset bộ đếm; cooling đơn thuần không reset.
  Không đếm mỗi poll nóng là một lần dừng. Phải chốt trước tag.
- Pin30..80% inclusive và đang sạc ổn định trước chạy và trong tải. Chưa có
  telemetry pin/charging đã xác minh trên A36. Nếu không đọc được bằng phạm vi
  đã cho phép thì dừng chuẩn bị full, không mặc định pin mát hoặc đang sạc.
- Map cảm biến theo ID+type+đường dẫn+đơn vị, không đoán từ độ lớn số. Thermal
  sysfs chuẩn là millidegrees Celsius; adapter Android khác phải có hợp đồng
  đơn vị riêng. Không mặc định battery nằm trong thermal zones hay suy từ CPU.
- Sensor mất, stale, NaN, logger chết hoặc reader treo phải ngăn tải tiếp.
  Tập cảm biến khóa trước; không bỏ sensor sau khi thấy nó nóng. Cần cơ chế
  bounded reader/watchdog độc lập để reader treo không treo cả supervisor.
- Chu kỳ5s là cadence cũ, không bảo đảm phản ứng ngay khi vượt ngưỡng giữa
  hai mẫu. Đo/khóa worst-case detection+termination bound từ adapter smoke;
  nếu không đủ, sửa cadence bằng amendment trước main run, không tự hạ threshold.
- Nghỉ thường60s, rồi tới từng sensor<=baseline riêng+1C, tối đa180s:
  baseline lấy TRƯỚC tải; ghi not_cooled khi quá hạn. Ngưỡng an toàn luôn
  ưu tiên, không có nhánh “hết180s thì chạy tiếp” khi còn hot.

## Tham số còn là đề xuất, cần chốt trước tag

Prototype local dùng freshness6s, worker180s, safety-cooldown180s để test
logic; không phải thời lượng đã chứng minh hợp lý trên phone và không phải
giới hạn cooldown an toàn đã đăng ký cũ. Ước lượng controls-only để khóa timeout
thực, stable-charging window, bộ nhớ, burst/repeats, thứ tự và tiêu chí coverage.
Mọi phép đo QA/smoke cũng cần protocol/tag trước và điều kiện máy rảnh/mạng.

`checks.py` có pure logic + own-child contract. Đã bổ sung `linux_observe.py`,
`posix_runtime.py`, `session.py` và `pin_analysis.py`; 76 ARM/control mock tests
(104 khi thêm28CPUregression) và checkpoint native_02 có9 Linux/WSL engineering
checks (không model/tải benchmark/phone). Stream lưu mọi frame hoàn chỉnh đã có,
kể cả invalid; timeout giữ gap/partial rồi khóa reader. Coordinator có observed
stable-charging window, baseline riêng trước tải, nghỉ60..180 và safetycooldown,
ledger khôngretry, terminalACK. Accounting analyzer yêu cầu khóa slackfraction
trước QA; active-lastCPU không là continuousresidency. Native2 source snapshot
được giữ theo SHA; fresh-guard check/pinanalysis sau đó chỉ có test host.
Worker pin_worker.py đã có mã thu process/TID clocks cùng cửa sổ, nhưng chỉ
fake-runtime tests, chưa realTorch/device. Latest121hosttests(93ARM+28CPU).
A0/A0Breadonlyđãtag/đọcA36quaTailscale: xem A36_TAILSCALE_A0_20261107.md.
Vẫnchưa registrytyped/liveSOCcharging hoặc descendantQA/proot/supervisedload
launcher;rawCPU71800/power_supplylistingdenied+4fixedbatteryfilesmissinggiữ
cổngloadđóng. Không chuyển DIST2.15.0 thành importedruntimeversionđãkiểm.
Không coi các kiểm local này là giấy phép triển khai hay mở full;
không triển khai hoặc chạy file cũ. Kết thúc burst dở không tự retry cùng block.
Giữ partial raw và accounting theo intention-to-measure; không chỉ phân tích
các block mát hoàn tất rồi gọi là hiệu ứng toàn bộ.

## Bằng chứng cần để mở full

Locked sensor/source/input manifests; fake-event tests; Android readback;
kill/reap smoke của CHÍNH worker/descendants; bounded sensor/logger failure;
all-TID affinity QA; A/A/MDE/reference gate; người dùng xác nhận idle/network;
PREREG/tag và smoke review theo CLAUDE. Chưa điều kiện nào được coi đã đạt
chỉ vì unit test trên Windows pass.
