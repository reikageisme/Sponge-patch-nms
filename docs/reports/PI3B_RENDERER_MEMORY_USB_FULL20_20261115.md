## Đã xong

- Đã chạy **đúng một full**, sau câu duyệt “Duyệt chạy full theo PREREG”.
  Tag `prereg-pi3b-renderer-memory-usb-20261115`, commit
  `70c398ae52540e873dca0f5dd447e97bc7d00958`; config SHA256
  `a19e9202b0ace3c2f796e633aae7381a6736b500626635cb7a3013396d5bb66b`.
  Giữ nguyên mười runtime sources, 20 ảnh, ba arm, ba lặp, ngưỡng và seed
  phân tích. **360/360 fresh processes hoàn tất; full quality PASS**.
- Đây là Pi3B1GB thực, firmware thiếu áp giới hạn600MHz, bốn luồng/
  affinity0–3, FP32, tensor mask640²; SSD ADATA SP900/SupTronicsX89 gắn
  nhưng nhàn/unmounted, cache và workspace trên SD179:2. Torch2.15.0+cpu,
  numpy2.5.4, Python3.13.5; parent không import Torch, child không nạp model.
- Endpoint: Linux `ru_maxrss`, KiB×1024bytes, đọc sau render và output digest.
  Đây là **đỉnh RSS cả tiến trình** gồm import, cache validation, K1 warmup,
  observer/allocator/workspace/output/hash; không trừ startup, không phải
  bộ nhớ tăng thêm hay đỉnh riêng renderer, không ghi latency.
- Baseline A/B là cùng native renderer32M; candidate preallocate output
  uint8, direct-copy từng chunk với budget16M. Giữ coefficient matmul,
  threshold/resize/crop và output hashes. Đây là thay đổi kết hợp, không
  tách riêng tác dụng giảm chunk và bỏ list/cat. Không đổi ảnh/cap/precision.
- Inferential unit là **20 ảnh**, không phải360 mẫu độc lập. Mỗi ảnh/condition:
  numerator median3 candidate; denominator median6 baselineA+B; lấy log tỷ
  số từng ảnh rồi trung bình/geometric mean. Bootstrap percentile20000 ảnh,
  primary RNG2026111401; exact two-sided sign-flip2^20. Một endpoint xác nhận.

|Endpoint|Geometric mean candidate/baseline|95% image-bootstrap CI|p exact|d_z trên log ratio|
|---|---:|---|---:|---:|
|Attacked, primary|0.8755043265545107|[0.867515845345165, 0.8838846368082481]|1.9073486328125e-06|-5.97631344493594|
|Clean, secondary **mô tả**|0.9964752955141999|[0.9958429141540155, 0.997081369666777]|1.9073486328125e-06|-2.416605426070134|

Primary tương ứng giảm `1−ratio = 0.12449567344548929`, khoảng12.45%,
với CI giảm suy ra bằng `[1−CI_upper,1−CI_lower]`. Tất cả20 attacked image
units cùng dấu giảm; p đạt độ phân giải nhỏ nhất2/2^20, không phải p=0.
Secondary không là kết luận xác nhận bổ sung dù script giữ p mô tả.

|A/A gate|Mean log(medianA/medianB)|MDElog80% (central-t approximation)|Ngưỡng và quyết định|
|---|---:|---:|---|
|Clean|-1.546460398250075e-05|0.0001005322082965261|absmean≤.02 và MDE≤.05: PASS|
|Attacked|-1.8182937505165462e-05|7.97452843451674e-05|absmean≤.02 và MDE≤.05: PASS|

MDE dùng sampleSD(ddof1), `(t.975,19+t.8,19)*SD/sqrt20`, tổng t khóa
2.9539746046772377. A/A không phải chứng minh tương đương. Độ phân giải1KiB
và startup floor có thể che thay đổi nhỏ, nhất là clean cache.

- Mọi360 mask hashes/cache bindings khớp. **1814 original files,
  30153532bytes**, SHAremote-before/local/remote-after khớp. Replay độc lập
  không import frozen analyzer/stats: schedule/units/median/guard/digest,
  bootstrap và toàn bộ sign patterns đều khớp. Bảng40 image-condition
  rows kèm exact raw-line maps ở `full_per_image.csv` và audit JSON.
- 5158 parent +1080 child guard frames;720 actual clocks đều600000000Hz.
  Các snapshot USB đầy đủ bằng phase baseline, không block-I/O/topology/
  mount/holder/generation/datapath drift; swapOFF/vmstat/affinity/governor/
  thermal/OOM guards đạt. Min MemAvailable lấy mẫu297472KiB, Tmax lấy mẫu
  38.628C là metadata an toàn, **không phải RSS hay cực trị liên tục**.
- Controller COMPLETED/gate_returncode0, restore RESTORED/errors[], independent
  readback đạt; không worker đo còn sống. SSH **giữ mở**. Span giữa parent
  guard đầu–cuối8448.963745594025s, dưới cap21600s; đây là thời lượng vận
  hành cả campaign, không phải tốc độ renderer hay end-to-end inference.

Nguồn gốc dưới `sponge-sim/results/pi3b_renderer_memory_usb_20261115/`:

|Khẳng định|Selector / phép gộp|
|---|---|
|Tag/config/weights/input identities|`runs/memory_full_01/manifest.json`; frozen `studies/pi3b_renderer_memory_usb_20261115/memory_registration.json`|
|Primary/secondary/CI/p/dz|`runs/memory_full_01/summary.json:primary_adv_candidate_over_baseline,secondary_clean_candidate_over_baseline`; replay `independent_full_audit.json:independent_statistics`|
|Từng median, K và raw lines|`independent_full_audit.json:table[*]`; `summary.json:raw_source_map`; `full_per_image.csv`|
|RSS và mask digest|`runs/memory_full_01/original/memory/raw.jsonl:1..360`, `result.ru_maxrss_kib/bytes,mask_sha256`; từng `memory/jobs/0000..0359/{memory,started,terminal}.json`|
|A/A/MDE|`summary.json:aa_controls`; log medianA/medianB trên20 ảnh, không pooled baseline|
|Safety/USB/clocks|`original/memory/guards.jsonl`; `raw.jsonl:result.guards`; `original/usb_preflight.json`; `independent_full_audit.json`|
|SHA/restore/controller|`full_transfer_verification.json`; `full_remote_{before,after}_fetch.json`; `original/{restore,campaign_terminal}.json`|
|Budget|`full_operational_budget.json`|
|SSH và cùng invocation|`full_frontend_terminal.json`; `launch_full_01.log`; `full_transport_recovery_receipt.json`|

Raw SHA256 `ebed47867be7c65f71f7af072f8b970c41a7467055df675afe9b89b4dc66cfcc`;
full USB-preflight SHA256
`faf8c9ca7c942ff51429a6865651b3fe7990846d1690d18b88d6f6168aca90b1`.
`full_memory_per_image.{png,pdf}` dùng toàn bộ20 ảnh, không lọc outlier.

## Phát hiện cần biết

- SSH frontend mất kết nối, exit255 tại02:17:43.642525UTC; receipt lúc đó
  ghi MainPID18518/active và `authoritative_service_terminal=false`.
  Không coi đó là experiment fail hoặc khởi chạy lại. Kiểm đúng owned argv/
  cgroup và invocation `4c60b8fb7a7a42c2abd50f31c7f45237`, rồi chỉ đợi
  unit-state qua kênh SSH khác; không đọc tiến độ/raw hay làm việc đồng thời.
  Observer xác nhận inactive/MainPID0 tại03:43:55.863579UTC; sau đó mới thu raw.
  Nguyên nhân ngắt SSH **chưa biết**. Receipt phục hồi là bản dựng lại sau
  terminal từ tool observations, phân biệt với raw thiết bị. Unit đã unload
  trả defaults `RuntimeMaxUSec=infinity/Result=success` không là đổi cap hay
  bằng chứng chất lượng; cap active6h và raw/gates/restore mới là căn cứ.
- Nhãn status của `full_transfer_verification.json` còn chữ SMOKE do copy
  wrapper; giữ file gốc nguyên. Đường dẫn/hash/phase/job count đều xác nhận
  FULL360, audit độc lập kiểm1814files; không dùng nhãn đó thay kiểm dữ liệu.
  PREREG title còn DRAFT nhưng body/tag/config final đã khóa trước dữ liệu;
  không sửa bytes protocol/source sau khi đo để làm lịch sử đẹp hơn.
- Cùng20 cặp PGD đã quan sát trước, một attack initialization mỗi ảnh;
  fresh processes/ba lặp không là seed tấn công mới. Một board/nguồn thiếu
  áp/clock/phiên bản cố định; chưa generalize Pi4/5, 1.2GHz hay Android.
- Hash parity hữu hạn40cache không là chứng minh mọi input hoặc COCO mAP
  mới. Child không có model resident: chưa biết RSS toàn pipeline tích hợp,
  latency/throughput/energy, khả năng giảm paging/carryover hoặc deadline.
- K là mask count sau lọc, không phải N_tau. Không suy causal relation giữa
  K và RSS từ đồ thị; không chia RSS theo clock hoặc cộng với số pipeline cũ.
- NMS component full20 cũ vẫn **FAIL A/A/MDE**, PI1 vẫn hủy. RSS pass không
  cứu NMS, không chứng minh service DoS hay patch vật lý. RSS-V1 USB-absent
  0/36/fullcancel và các timing negatives giữ nguyên.

## Việc tiếp theo — chọn 1 trong các cách sau

1. `check báo cáo Pi`: đối chiếu report, bảng40rows và raw-map với PREREG/tag.
2. Tiếp tục cơ chế NMS: thread-pool/TID inventory, actual service/ancestor
   cgroup counters, observer sham và matched predecessor protocol trước
   operator timing; giữ mọi NMS failures, không retry tag đã đóng.
3. Tích hợp renderer vào pipeline chỉ theo protocol mới sau QA: đo tradeoff
   RSS/latency cùng model-resident condition; chưa có số của bước đó ở đây.

## Đang chờ gì ở tôi

Không cần duyệt lại full đã xong. SSD có thể dùng ngoài phase; không tự mount,
format, đổi nguồn hoặc tắt SSH. Chưa mở campaign timing tiếp theo dưới tag này.
