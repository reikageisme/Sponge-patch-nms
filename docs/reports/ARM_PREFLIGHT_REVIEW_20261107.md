# Kiểm lại ổn định, ghim lõi và dừng nhiệt/pin

Ngày07/11/2026. Phân tích SAU khi biết kết quả; không có benchmark mới.

## Đã xong

- Đọc lại PREREG, source và raw; tính lại cả ba session M6 bằng analyzer cũ,
  kiểm agreement với summary đã lưu, không gọi CLI ghi vào thư mục run cũ.
  Kết quả mới ở `ARM_PREFLIGHT_AUDIT_20261107.json`, gồm SHA nguồn và số dòng
  từng reference. Không sửa raw hoặc quyết định FAIL.
- Rà pin theo thread, sampler, thời điểm tạo pool và vòng điều phối nhiệt.
  Bản mới `sponge-sim/studies/arm_preflight_v2/checks.py` chỉ là parser/policy
  và hợp đồng supervisor với adapters giả lập; 23 test local PASS. Chưa có
  adapter cảm biến/process-group Android, chưa triển khai hoặc tải A36.
- Viết `DRAFT_ARM_PREFLIGHT_AMENDMENT_20261107.md`, chưa tag/chưa chạy.
- Đối chiếu lại CPU máy thuê theo yêu cầu người dùng: M2 CPU1/CPU4 đã chạy,
  không phải bỏ qua CPU. CPU4 đã đạt với workload MASK tổng hợp; CPU1 không
  đạt drift. Máy local đọc được i5-1335U,10cores/12logical; chưa đo lại laptop.

## Phát hiện cần biết

### 1. Timing thất bại ở đâu?

| M6 session | References bị cờ /22 | Cờ chậm hơn baseline | Cờ nhanh hơn baseline | Min–max ratio reference | A/A MDE sạch/nhiễu (%) |
|---|---:|---:|---:|---|---|
| 1 | 14/22 | 14 | 0 | 0.995695–1.210693 | 0.460073 /0.231268 |
| 2 | 14/22 | 0 | 14 | 0.888755–1.010948 | 0.304121 /0.238168 |
| 3 | 10/22 | 10 | 0 | 0.988976–1.101848 | 0.554859 /0.361953 |

Nguồn: audit JSON `sessions[*].references,aa_mde_fraction`; raw
`results/stability_20261106/stability_full_20261106/session{1,2,3}/raw.jsonl`,
`kind=reference`,31samples/reference. Ratio=median/reference đầu phiên;
flag=abs(ratio−1)>.03. Cổng<=2flags, A/A MDE mỗi arm<=1%, completeness.
Cả ba đạt completeness và MDE nhưng trượt drift. Audit kiểm khớp chính xác
MDE/flags/decision/rawSHA với `confirmation_summary.json`.

Phiên2 bị cờ do NHANH hơn, không chỉ chậm dần. Vì vậy không mô tả toàn bộ
failure là “máy càng chạy càng nóng/chậm”. Reference có thể đổi mức so với
baseline; chưa xác định nguyên nhân vật lý. A/A gần nhau ít nhiễu vẫn có
thể cùng trôi theo thời gian; A/A tốt không hợp thức hóa drift thất bại.

Source M6: reference luôn cùng ảnh sạch đầu tiên,200forward đầu phiên,
5warmforward trước mỗi31samples; đo trước từng image block và cuối phiên.
Các block chứa NMS/mask/tổng sạch+nhiễu xen kẽ; CUDA sync hai đầu, GC-off,
clone ngoài timing, buffered raw. Đây là reference forward đặt cạnh tải hỗn
hợp, không phải phép đo xung GPU trực tiếp. Diagnostic conditioning w5/50/200
cũng FAIL; không tiếp tục tăng warmup đến khi gặp PASS.

Chênh NMS0.8–175ms lịch sử còn lẫn dispatch theo trạng thái import torchvision;
không gọi đó là cùng một kernel biến động. NMS fixed-TV còn đo toàn wrapper
lọc/sort/NMS; min/max nhiều ảnh không chứng minh cùng3000boxes có cùng hình học
hoặc cùng workload. Candidate count không mô tả hết overlap/class/score order.
NVML snapshots không đủ tách clock/WDDM/scheduling/cache/proot hay host load.

Giữ kết luận:1.500ảnh và30.000cases xác minh counts/transfer/direct objectives,
không xác minh latency/DoS. MASK tổng hợp CPU4/GPU đạt cổng là đối chứng cơ chế,
không phải timing tấn công thật. Để gọi DoS cần baseline sạch khả thi, deadline/
queue/drop đã khóa và thực nghiệm worker thật; không suy từ K>=50.

### 2. Có dữ liệu CPU máy thuê; phần còn thiếu là gì?

Nguồn CPU4: `results/confirmation_20261106/m2_cpu4_full_20261106/manifest.json`
`config.device=cpu,threads=4,affinity=[2,3,4,5]`; summary/raw cùng thư mục.
Đây là host thuê Windows,torch2.11.0+cu128; đuôi CUDA không đổi `device=cpu`.
Không gán bốn logical CPU là bốn P-core/physical core: topology host lộ18logical
đồng nhất, không đủ xác minh P/E hoặc SMT thực của môi trường thuê.

- CPU4 full-res tổng K300/K10=3.9505, CI95%[3.9141,3.9957],0reference flags.
- CPU1 đã chạy nhưng10flags, không đạt. M1/M1b laptop trước cũng trượt drift.
- Các số trên từ báo cáo `FULL_SEGMENTATION_CODEX_20261106.md` và nguồn raw nó
  trỏ tới; không có kết quả CPU tấn công phân đoạn thật ổn định để điền thay.

Người dùng đã yêu cầu làm trọn trục CPU hôm06/11. Công việc mới hoàn thành một
phần ở MASK CPU4; chưa đóng được CPU1 sạch và latency attack thật. Phải báo là
CHƯA HOÀN TẤT, không diễn đạt “chưa chạy CPU” hoặc suy yêu cầu đó đã được đáp ứng
toàn bộ. Máy thuê đã xóa, không thể bổ sung trên cùng host. Có thể dùng i5-1335U
local cho campaign mới nếu controls đạt; laptop không mặc nhiên ổn định hơn.

### 3. Bốn profile A36 chưa chứng minh điện thoại không ghim được

Nguồn: `results/phone_a36/pin_20261101/pin_verify.json:verify`.

| Profile lịch sử | CPU hiệu dụng | Mẫu CPU cuối trong tập | Quyết định cũ |
|---|---:|---:|---|
| big1 | 0.906282 | 40.0000% | FAIL sampler |
| big4 | 3.402703 | 87.4126% | FAIL sampler |
| little1 | 1.758106 | 30.0000% | FAIL sampler VÀ upper1.15 |
| little4 | 3.129678 | 61.9048% | FAIL sampler |

Main mask readback8/8 thành công. `sched_setaffinity(0,...)` chỉ ghim luồng gọi,
không áp dụng cả pool đã tồn tại. Linux ghi affinity theo từng thread.
[Linux sched_setaffinity](https://man7.org/linux/man-pages/man2/sched_setaffinity.2.html)

`pin_verify.py` nhập Torch rồi benchmark cácCPU và đổi profile trong cùng process.
Pool cũ giữ mask rộng là giả thuyết phù hợp mã, CHƯA xác nhận trên A36.
Worker đo ở `e5_phone/run.py` lại ghim TRƯỚC importTorch: không đánh đồng hai đường.
PyTorch cũng yêu cầu đặt số thread trước eager/JIT/autograd work để bảo đảm cấu
hình có hiệu lực. [PyTorch set_num_threads](https://docs.pytorch.org/docs/2.15/generated/torch.set_num_threads.html)

Sampler cũ lấy field39 mọi TID, kể cả luồng ngủ; nó là CPU chạy lần cuối,
không phải đang chạy. Test giả lập: một thread hoạt động đúngmask, một thread
ngủ có lastCPU cũ ngoài tập => sampler cũ50%, active-only100%; đây là fixture,
KHÔNG phải số đo A36. Vẫn phải kiểm mask cả thread ngủ để phát hiện pool rộng.
[Linux proc_pid_stat](https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html)

Raw cũ không có snapshot TID/mask/ticks/state để tính lại sampler. Không đổi
bốn FAIL thành PASS; little1 vượt CPU-time là bằng chứng độc lập với staleCPU.
Không tin giả thuyết sampler đủ để giải thích tất cả. Amendment đề xuất2×2
controls tách pool-init order/all-TID pin, và chấm hai sampler trên cùng raw.

### 4. Dừng nhiệt/pin chưa được thực thi đúng

Đối chiếu `prereg/PREREG_E5_phone.md:B` với `studies/e5_phone/run.py:main`:

| Đã đăng ký | Source hiện có | Hệ quả |
|---|---|---|
| Bất kỳ zone>=70C: dừng đo | Chờ subprocess.run xong, nghỉ rồi kiểm | Không ngắt được tải đang chạy; đỉnh có thể nguội trước kiểm |
| Pin>=40C; resume<38C | Không có nhánh pin riêng | CPU chưa70C không bảo đảm pin dưới40C |
| Resume mọi zone<55C | Vòng chờ dùng >55; chưa có pin | Có thể resume ở đúng55; thiếu điều kiện pin |
| Ba lần dừng liên tiếp kết thúc | Không có counter | Không thực thi quy tắc kết thúc phiên |
| Pin30–80%, sạc ổn định | Không giám sát SOC/charging | Manifest khai báo không thay telemetry trong tải |
| Nghỉ theo nhiệt đầu phiên+1C | Baseline lấy sau burst đầu, max gộp sensors | Không đúng baseline đầu phiên; sensor nóng nhất che trôi sensor khác |
| Logger5s | Không gate freshness/lỗi logger/NaN | Dữ liệu cũ/mất có thể được dùng tiếp hoặc gây lỗi max(empty) |

Ngoài ra worker/cooldown không có timeout; exception không bảo đảm đóng logger
bằng finally. Không thấy bằng chứng máy từng quá nhiệt từ đây; đây là lỗi bảo
đảm thực thi source, không phải quan sát một tai nạn. Chưa chạy full điện thoại
mới. Không dùng lại runner detectorconf.01,totalpure như segmentation fixedTV.

`hw_linux.read_thermal` đoán đơn vị bằng abs(value)>1000. Chuẩn thermal sysfs
dùng millidegrees Celsius; phải map node/unit rõ ràng, không suy từ độ lớn.
Battery có thể không xuất hiện trong thermal zones; chưa xác minh nguồn pin
được quyền đọc. Không cài gói mới hoặc vượt quyền để có sensor.
[Linux thermal sysfs](https://www.kernel.org/doc/Documentation/thermal/sysfs-api.txt)

Prototype mới chặn nóng trước spawn; khi phát hiện nóng trong loop thì terminate,
kill khi cần, giữ abort; hysteresis55/38; chỉ burst thành công reset counter;
telemetry stale/missing/NaN và power gate kết thúc. **23fake tests không chứng
minh kill/read latency trên Android.** Đọc cảm biến bị treo vẫn cần watchdog
độc lập ở adapter; cadence5s cũng không phát hiện ngay đỉnh giữa hai mẫu.
Timeout6/180s trong prototype là đề xuất test, chưa đăng ký, chưa feasibility.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Ưu tiên CPU laptop đang có: chuẩn bị controls-only và replay input đã khóa,
   rồi mới đo thật sau protocol/tag và xác nhận máy rảnh → gõ: “Ưu tiên CPU laptop.”
B. Đóng preflight A36: hoàn thiện adapter sensor/process, rồi QA phân biệt hai
   giả thuyết pin theo amendment mới → gõ: “Hoàn thiện preflight A36.”

Không chạy thêm1500ảnh×nhiều seed để chữa drift; không mua board chỉ để tăng
số thiết bị trước khi harness được kiểm. Cả hai lựa chọn dùng raw cũ làm đầu
vào, không cần thuê lại GPU để tối ưu nhiễu.

## Đang chờ gì ở tôi

Không cần xác nhận cho phần audit/local tests đã làm. Chưa bắt đầu benchmark.
Trước đo thật cần protocol/tag và điều kiện máy rảnh theo CLAUDE; chưa xin duyệt
full khi adapter và cấu hình còn chưa hoàn thiện. Không truy cập máy thuê đã xóa.
