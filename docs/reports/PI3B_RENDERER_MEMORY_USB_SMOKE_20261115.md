## Đã xong

- Đúng một smoke RSS USB-present chạy dưới tag
  `prereg-pi3b-renderer-memory-usb-20261115`, commit
  `70c398ae52540e873dca0f5dd447e97bc7d00958`. Runtime10file giữ nguyên bản
  c6a9747 đã qua130test host và năm tình huống ngủ trên Pi; giữ SSD gắn.
- **36/36 tiến trình đo hoàn tất**, hai ảnh9+30, cả clean/adv, ba arm và
  ba lặp. Output mask hashes, cache hashes và mọi identity/units/schedule
  kiểm lại đều khớp. Technical smoke PASS; quality_pass=False theo thiết kế
  vì đây không phải kết quả full20 hoặc kết luận hiệu quả.
- Lưu519frame guard parent,108frame child và72clock samples; tất cả cổng
  vật lý đã khai báo đạt. USB block counters không đổi so với baseline của
  phase; không đổi topology/mount/holder/generation/datapath.72clock samples
  đều600000000Hz. Minimum MemAvailable được lấy mẫu307188KiB, maximum nhiệt
  được lấy mẫu36.476C là metadata an toàn, **không phải peak RSS**.
- Thu194file gốc/3034389bytes, SHAremote-trước/local/remote-sau khớp. Ten
  runtime sources, references/caches/protocol giữ nguyên. Restore và kiểm
  độc lập trạng thái ban đầu đạt; service inactive/MainPID0, không worker
  đo. SSH vẫn mở. Không bắt đầu full.
- Replay độc lập bằng stdlib kiểm lại tất cả median, đơn vị byte/KiB,
  A/A/MDE và mask hashes; khớp summary. Các con số dưới đây có raw-line map.

Median mô tả riêng từng cache; KiB=1024bytes, giữ giá trị chính xác. Baseline
là median của sáu mẫu A+B, candidate là median của ba mẫu. K là số mask sau
chọn/lọc của cache, **không phải số ứng viên trước NMS**.

|Ảnh|Điều kiện|K|Pooled baseline KiB|Candidate16M KiB|
|---|---|---:|---:|---:|
|000000000009|clean|6|256596|255772|
|000000000009|adv|202|455516|417676|
|000000000030|clean|1|247914|247372|
|000000000030|adv|300|523148|456008|

A/A chỉ chẩn đoán hai ảnh, không phải cổng eligibility của smoke:

|Điều kiện|Mean log(A/B)|MDElog80%|
|---|---:|---:|
|clean|-8.887000440564518e-06|0.0007837245288998985|
|adv|3.40592256533309e-06|0.000694018623694906|

Nguồn: `sponge-sim/results/pi3b_renderer_memory_usb_20261115/`:
`runs/memory_smoke_01/manifest.json`, `runs/memory_smoke_01/original/`,
`runs/memory_smoke_01/summary.json`, `smoke_transfer_verification.json`,
`independent_smoke_audit.json`, `audit_smoke_raw.py`,
`smoke_operational_budget.json`. Raw SHA256
`5e945cf1ec3b612dd282b19294755d3c3bd965ea73fbf296b08c29b6ddc64ca7`.
`independent_smoke_audit.json:table[*].raw_lines` nối từng median tới
`original/memory/raw.jsonl`; `summary:raw_source_map` còn ghi job_index/rep.
Guard/clock nguồn `original/memory/guards.jsonl`; guards child trong từng
raw row. Baseline USB SHA
`9e43068edf6f29dd5933761531692afdaf6c9150d31620bfe8dadebb847a0080`.

## Phát hiện cần biết

- Chỉ hai ảnh được định trước để kiểm kỹ thuật, có một cache K300. Không
  tính primary effect/CI/p hay suy hiệu quả chung từ bảng này. Đỉnh đo là
  whole-process Linux ru_maxrss tới sau digest, gồm import/cache validation/
  K1warmup/guard allocations/allocator/output, không phải peak riêng renderer.
  Startup floor và độ phân giải1KiB có thể che khác biệt ở cache nhỏ.
- A/A/MDE hai ảnh không chứng minh tương đương hoặc bảo đảm full ổn định.
  Full vẫn buộc cả clean và adv đạt absmeanlog<=.02, MDElog<=.05, toàn bộ
  360job/hash/physical/cleanup; mọi lỗi dừng, không lọc ảnh/lặp lại để lấy PASS.
- Span giữa guard đầu–cuối846.945547580719s là thời lượng vận hành gồm
  fresh-process import/render/hash/metadata, **không phải latency renderer**.
  Nhân10 theo số job cho8469.45547580719s, khoảng2giờ21phút full20; chỉ
  ngoại suy, không cam kết. Giới hạn full đã khóa21600s/6giờ.194file hiện
  chiếm3034389bytes; full dự kiến lớn hơn, không đổi sample/time cap vì ETA.
- RSS-V1 USB-absent vẫn0/36/FAIL/full hủy, không retry. Main full20 cũ đạt,
  component NMS vẫn FAIL/PI1 chưa chạy. Không suy số RAM này thành speedup,
  giảm latency toàn trình, giải thích NMS, DoS hay khả năng của Pi4/A36.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Chạy đúng full20/360process theo tag hiện tại, giữ SSD nhàn trong phase,
giữ mọi gate/ảnh/arm/RNG → gõ: "Duyệt full RAM Pi theo PREREG".

B. Chưa mở full; tiếp code instrumentation/sham/predecessor NMS → gõ:
"Chưa chạy full RAM, tiếp NMS".

Full launcher/collector đã chuẩn bị, kiểm từ chối trước mọi remote action
khi chưa có full_approval.json/manifest. Người dùng sau đó trả lời rõ
"Duyệt chạy full theo PREREG" ở câu hỏi có budget/gates như trên; phê duyệt
được lưu gắn đúng tag/config/smoke summary, không tự suy từ goal continuation.
Lượt full sẽ có dữ liệu/báo cáo riêng; bảng ở đây vẫn chỉ là smoke hai ảnh.

## Đang chờ gì ở tôi

Người dùng đã duyệt full; không cần xác nhận lại cùng bước. Không cần tháo
SSD, mở lại SSH, cài gói hoặc cấp lại quyền code/QA. Chưa mở full tại checkpoint
smoke này; theo dõi trạng thái full ở PROGRESS.md và artifacts của lượt full.

Theo `.claude/skills/sponge-research/SKILL.md` mục1.4: "Chạy smoke nhỏ trước,
ước lượng thời gian/dung lượng, dừng chờ duyệt rồi mới chạy đầy đủ."
