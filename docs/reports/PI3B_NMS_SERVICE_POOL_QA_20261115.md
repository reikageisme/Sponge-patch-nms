## Đã xong

- Gói observer mới đã khóa engineering tag
  `qa-pi3b-nms-observer-service-20261115`, commit
  `03999b202eb802ef9073a476395c83943980121a` trước truy cập thiết bị.
  Đây là **QA instrumentation**, không PREREG timing/NMS/RSS mới.
- Host31test đạt, bao gồm10test counter reader cũ. Lần đầu29đạt/1lỗi
  hiển thị ancestor root thành `/.` thay vì `/`; sửa trước tag/device,
  giữ nguyên assertion và ghi lỗi, bổ sung late-TID-reuse regression.
  Ba Python sources/config cùng plan/driver/test hashes được lưu.
- Đúng một service chạy dưới User=tanh, CPUAffinity0–3, runtime cap180s,
  KillMode=control-group, timeout-stop10s. Không đổi governor/swap/USB/
  storage/nguồn/timer/SSH, không nạp model/weights hay chạy NMS/mask.
- Lấy inventory trước import, khởi tạo existing Torch2.15.0+cpu với
  intraop4/interop1, đúng một CPUFP32 mm của hai ma trận512² toàn1.
  Output mọi phần tử512 đạt kiểm chức năng. Sau xóa tensor/gc lấy hai
  inventory liên tiếp; không ghi operator wall-time hoặc ru_maxrss.
- **PASS_SERVICE_POOL_INVENTORY_API_ONLY**: cả ba snapshot đủ TID/birth/
  affinity, hai snapshot sau giữ cùng identities và counters không giảm;
  các delta đã được replay độc lập từ raw, không import observer/Torch.

|Snapshot raw selector|PID|Số native TID quan sát|Affinity từng TID|
|---|---:|---:|---|
|`pre_import_inventory`|24264|1|0–3|
|`pool_before`|24264|10|0–3|
|`pool_after`|24264|10|0–3|

TID sau phép toán:24264,24265,24266,24267,24269,24270,24271,24272,24273,24274.
Configured intraop4, interop1, OMP/MKL/OpenBLAS environment đều4. Raw
`torch_configuration.parallel_info` ghi ATen backend OpenMP, max_threads4.
Không tự gán từng TID cho thư viện hoặc xem10TID là10luồng chạy đồng thời.

- Mỗi snapshot giữ đủ ba cgroup nodes: service thực
  `/system.slice/sponge-pi3b-nms-observer-qa-20261115.service`,
  `/system.slice`, `/`. Phạm vi này khác metadata QA cũ dưới SSH scope.
- Thu **hai original files/35651bytes**, SHAremote-before/local/remote-after
  khớp; ba source files/config giữ nguyên bytes của tag. Service terminal,
  không còn owned worker. Governorondemand và zram swap ban đầu được giữ
  nguyên, before/after readback bằng nhau; không có lease cần khôi phục.
  SSH giữ mở. Driver53998 chờ độc quyền đến terminal5a23db/exit0 rồi mới đọc
  dữ liệu; không chạy tác vụ khác trong QA trên Pi.

Nguồn: `sponge-sim/results/pi3b_nms_observer_device_qa_20261115/`.
Original `original/qa_result_01.json` SHA256
`46b61a1fea56413e7bdac6eca84632ca412aac29eedced63e6ad3644e4ec805b`,
`original/qa_manifest.json` SHA256
`233b48b83965c94661976ae49bbcd74389f29f825094b64097464fa6ad84c1bc`.
`verification.json`, `terminal_{before,after}_fetch.json`,
`device_invocation.json` và `independent_saved_audit.json` nối hashes,
terminal/state và exact selectors. Kế hoạch cố định ở
`sponge-sim/prereg/QA_PI3B_NMS_OBSERVER_SERVICE_20261115.md`.

## Phát hiện cần biết

- Không thể chỉ kiểm4TID đầu hoặc coi `torch.set_num_threads(4)` là census
  toàn bộ tiến trình. Phiên chức năng này có10TID cùng affinity đúng; chưa
  xác định TID thuộc pool nào hoặc bao nhiêu TID active khi NMS chạy.
  Cần stage inventory trước/sau import/thao tác để phân biệt pool creation,
  và tải tham chiếu riêng để kiểm parallel utilization trước scientific run.
- `cpu.max` tại service trả UNAVAILABLE/FileNotFoundError. Tại system.slice
  đọc được `max 100000`; root `cpu.max` cũng không có. Không suy leaf-file
  vắng hoặc parent unlimited thành đã loại mọi quota/throttling/config cause.
  Leaf cpu.stat đọc được usage/user/system/nice, không có các trường CFS
  throttle trong raw. Counter ở ancestor là shared, không là event của NMS.
- `memory.events`, `memory.events.local`, `memory.pressure`, `memory.max`,
  `memory.high`, `memory.current` vắng ở cả ba nodes. Root controllers raw
  là `cpuset cpu io pids`, không liệt kê memory; service controllers là
  `pids`, system.slice là `cpu pids`. Đây là giới hạn trong hierarchy nhìn
  thấy; chưa kiểm kernel/cmdline để gán nguyên nhân, không coi absent là0
  hay bằng chứng không có pressure/OOM. Không bật controller/reboot máy.
- Inventory đọc procfs tuần tự, kiểm TID set và birth lần nữa ở cuối nhưng
  không atomic. CPU ticks/faults/context switches gồm observer work; chúng
  chưa phải NMS-only cost hoặc thời gian chờ. Hai snapshot liên tiếp không
  là sham overhead experiment và không chứng minh observer rẻ.
- QA service riêng không chính là cgroup của scientific workload tương lai.
  Không có model resident, mixed workload/predecessor, bare-kernel/wrapper
  comparison hay operator timing. **Cơ chế NMS chưa chốt**; full20 NMS cũ
  vẫn FAIL A/A–MDE, PI1 vẫn hủy, RSS full PASS không thay đổi quyết định đó.

## Việc tiếp theo — chọn 1 trong các cách sau

1. Tiếp tục stage-by-stage pool metadata và đọc controller/kernel metadata
   chỉ đọc; mọi missing state giữ nguyên, không đổi cấu hình để lấy PASS.
2. Hoàn thiện sham bracket/matched-predecessor runner, bare-kernel và wrapper
   endpoints/AA/MDE riêng, model-resident và physical guards; QA rồi PREREG
   mới trước đo. Không chuyển tag engineering này thành scientific run.

## Đang chờ gì ở tôi

Không cần bật SSH hay duyệt lại quyền code/engineering QA đã cấp. Không có
phép đo khoa học đang chạy; giữ nguyên máy và các protocol đã đóng.
