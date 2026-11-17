# Pi renderer —40cache chức năng đã kiểm, chưa đo lợi ích bộ nhớ/tốc độ

## Đã xong

**Đúng20cặp ảnh sạch/nhiễu, tổng40case trên Pi thật, đã qua bước so SHA đầu
ra mask baseline và renderer mới. Tạo đủ40cache CPUFP32 có thể dùng lại.**
Đây là kiểm chức năng hữu hạn; chưa có số đo peakRSS/speedup của biến thể.

Plan khóa trước tải: `sponge-sim/prereg/QA_PI3B_RENDERER_CACHE_FUNCTIONAL_20261114.md`.
Tag kỹ thuật `qa-pi3b-renderer-cache-20261114`, commit
`b5304d20ef0dbb6ae82273ec330806502431595a`. Toàn bộ11filePython giữ nguyên
byte của source đã qua66hosttests và5sleep-onlydevicecases ở tag3409c07.
Chỉ đổi qa_tag, allow_cache_preparation và thêm cache_planSHA; safety/source/
reference không đổi. Khóa cũ giữ trong Git/archive và trên Pi ở config_history.
Năm kiểm tra activation đạt trước khi mở QA chức năng.

Gốc nguồn dưới đây: `sponge-sim/results/pi3b_renderer_functional_cache_20261114/`.
Lượt duy nhất `runs/cacheprep_01`, cache `caches/cache_01`, frontendexit0.
Không cache02, không đổi source/gates sau khi thấy dữ liệu.

### Vật liệu và kiểm đầu ra

| Nội dung | Kết quả | Nguồn |
|---|---|---|
|Cohort|20ID cố định, mỗi ID clean+adv, đúng40case/đúng thứ tự|`functional_audit.json:{n_images,n_cases,cases}`|
|Source inputs/weights|21SHA khóa khớp trước forward|`caches/cache_01/manifest.json:source_material_sha256`|
|Điều kiện số học|PiTorch2.15.0+cpu,TV0.29.2+cpu,Ultra8.4.90,NumPy2.5.4,Python3.13.5; FP32/640²|`manifest.json:versions`/source khóa|
|Countparity|Nτ/K đúng mọi case so với full20Pi đã chấp nhận; kernel_n đúng boundary|`functional_audit.json:{cases,kernel_count_parity}`|
|Maskparity|baseline32M list+cat và candidate16M directcopy đi qua kiểm SHA bằng nhau trên40case|`manifest.json:cases[*].mask_sha256` và source `cache.py:compare_outputs`|
|Cache schema|40file load lại trên laptop đúngCPUFP32/finite/contiguous/shape; không rerender khác runtime|`functional_audit.json:cases[*].shapes`|

Proto mỗi cache32×160×160, coeffsK×32, boxesK×4, đích640². Kclean nằm trong
1–9, Kadv177–300;6case nhiễu cóK300. Nguồn:
`functional_audit.json:cases` lọc condition rồi min/max/count(k==300).
Không chọn riêng6case này để kiểm hoặc bỏ những case ít mask.
K0 trên Pi không có trong40case; nhánh rỗng mới có finitehosttests trước đó.

Hai renderer chạy tuần tự, không giữ hai output lớn đồng thời; hash qua
memoryview thay vì nhân thêm một bản bytes. Hàm compare_outputs chỉ trả
hash chung sau khi so hai hash và từ chối khi khác. Receipt lưu hash chung,
không lưu hai stack mask117MiB. Kiểm lại trên laptop chỉ đọc schema/tensor,
không dùng Torch2.13 trên laptop để đòi trùng bit với Torch2.15 trên Pi.

ManifestcacheSHA256:
`61b5abaaf22ea985b98f582a34f52cc19c2272ac87f66782292d843b17bbe165`.
Từng file tensor/receipt, image/condition/K và maskdigest nằm trong
`functional_audit.json:cases` và `caches/cache_01/manifest.json:cases`.
Không gọi đây là equivalence mọi input/backend hoặc COCOAP toàn bộ.

### Guard, khôi phục và dữ liệu gốc

303guardrecords không vi phạm: powersave, affinity0–3, requestedclock600000kHz,
swapoff,3masks đúng, không USBstorage; delta pswpin/out/oom đều0. Nhiệt
fastguard cao nhất39.704°C, MemAvailable thấp nhất tại guard259000kB.
Nguồn: `functional_audit.json:{guard_records,guards_all_pass,requested_khz_values,max_guard_temp_c,min_guard_mem_available_kb,condition_counters_initial,condition_counters_end}`;
mọi lần đọc gốc nằm trong `runs/cacheprep_01/functional_guards.jsonl`.

Các số cảm biến chỉ là metadata bảo vệ tại điểm đọc, **không peakRSS** và
không phải phép so sánh RAM baseline/candidate. QA này không đo actualclock
liên tục hoặc thời gian từng renderer. Không lấy thời gian service cả phiên
trong frontend để gọi là latency mỗi ảnh hay speedup.

RestoreRESTORED/errors[] và readback khớp original governor/swaptopology/
priority/unit/timer/helper; masks đã gỡ, service inactive/MainPID0, không còn
registeredworker, SSH mở. Nguồn: `runs/cacheprep_01/restore.json`,
`remote_after_fetch.json:result.{restore,snapshot,service,workers}`.

Đã lấy nguyên90file, tổng132072317bytes, SHA remote-before=local=remote-after.
Bao gồm40tensor.pt,40receipt, manifest/preparation/terminal và runlogs.
18source/materialfiles không đổi trong lượt này; lock cũ vẫn được giữ.
Nguồn: `transfer_verification.json:{n_files,files,source_unchanged,old_engineering_lock_preserved}`.
Toàn bộ tensor giữ trên Pi và local; hash bao từng file, không tạo lại để
thay cho dữ liệu gốc khi phân tích. Không sửa outputs hoặc run trước.

## Phát hiện cần biết

- Đã đủ vật liệu để khóa một phép so sánh tài nguyên riêng. Chưa có
  memory_registration.json, empirical_endpoints_enabled vẫnFalse; chưa chạy
  memory_worker360job hoặc bất kỳ latency endpoint mới nào.
- GuardMemAvailable không đo riêng từng renderer và không bắt peak giữa lời
  gọi. Không so số này với guard của full20 để kết luận tiết kiệm RAM; hai
  workload khác nhau. Mô hình byte lý thuyết trước đây vẫn chỉ là mô hình.
- Đây là40case từ cùng20cặp PGD đã thấy trước, một model và một Pi/runtime;
  không cohort độc lập, không nhiều attackseed/board/nguồn, không physicalpatch.
- Code mới chỉ thay cách dựng mask, không thử làm NMS cũ qua cổng. Component
  NMSFAIL và PI1hủy của full20 giữ nguyên; không có kết luận DoS hoặc độ ổn
  định NMS từ QAcache này. Mọi số đo sau cần protocol/tag và cổng riêng.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Hoàn thiện đề xuất so sánh RSS cho đúng40cache này, giữ A/A sạch/nhiễu,
freshprocess và giới hạn hữu hạn → gõ: **"Review protocol bộ nhớ renderer"**.

B. Tiếp tục điều tra NMS từ raw đã lưu và chuẩn bị phép trace có kiểm soát,
giữ mọi kết quả âm → gõ: **"Điều tra tiếp nguyên nhân NMS biến động"**.

## Đang chờ gì ở tôi

Không cần mở SSH hay khôi phục Pi. Vẫn có thể làm phần phân tích/chuẩn bị
độc lập; chưa mở một campaign đo mới sau cổng NMS thất bại.
