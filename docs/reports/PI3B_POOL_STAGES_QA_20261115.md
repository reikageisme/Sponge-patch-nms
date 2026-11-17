## Đã xong

- Khóa engineering tag `qa-pi3b-pool-stages-20261115`, commit
  `7c019497a9f3a6d2c4245dfd20a14126270cc11f` trước device access.
  Đúng một service mới, không chạy lại QA03999b2 hay phiên NMS cũ.
- 45hosttests đạt. Bộ đầu42đạt; khi bổ sung coverage có44đạt/1NameError
  do hai assertion bị chèn nhầm scope trong file test. Chuyển nguyên hai
  assertion về hàm cũ trước tag/device; lần cuối45đạt0.64s. Ba log và
  host_failure_event giữ nguyên; không nới runtime hoặc điều kiện PASS.
- Service User=tanh, CPUAffinity0–3, env OMP/MKL/OpenBLAS4, cap180s,
  KillMode=control-group. Existing Python3.13.5/NumPy2.5.4/Torch2.15.0+cpu,
  intraop4/interop1. Một NumPy mm và một Torch mm512² toàn1 đều ra512
  chính xác. Không model/weights/NMS/mask, operator wall-clock hay ru_maxrss.
- **PASS_STAGED_POOL_METADATA_ONLY**: đủ11snapshots, process/TID/birth/names/
  affinity/cgroup và hai snapshot cuối cùng ổn định. Raw được replay độc
  lập toàn bộ transitions/deltas/hashes; đây là QA metadata, không hiệu năng.

|Mốc raw|Số native TID|Thay đổi so với mốc trước|
|---|---:|---|
|baseline|1|MainPID24414|
|numpy_import|4|+24415,24416,24417|
|numpy_mm_and_diagnostics|4|Không thêm/bớt TID được quan sát|
|torch_import|4|Không thêm/bớt TID được quan sát|
|torch_set_intraop|7|+24419,24420,24421|
|torch_set_interop|7|Không thêm/bớt TID được quan sát|
|torch_ones|10|+24422,24423,24424|
|torch_mm|10|Không thêm/bớt TID được quan sát|
|torch_validation_and_gc|10|Không thêm/bớt TID được quan sát|
|torch_diagnostics|10|Không thêm/bớt TID được quan sát|
|final_adjacent|10|Cùng identities/births; final deltas không giảm|

Mọi TID có affinity0–3 và comm `python`. Không thấy gone identity tại các
ranh giới đã lấy mẫu; không bao phủ thread được tạo/hủy giữa hai snapshot.
Tổng77 thread-observation frames; không phải77worker độc lập.

- Maps sau NumPy import có
  `numpy.libs/libscipy_openblas64_-f552eb69.so`. Sau Torch import thêm
  `torch/lib/libopenblas.so.0` và `torch/lib/libgomp.so.1` cùng các thư viện
  Torch. Đây là **những đường dẫn mapping khác nhau**, không là stack/symbol
  attribution từng TID. Các TID mới ở set_intraop/ones không đi kèm mapping
  thư viện mới trong snapshots đó. NumPy show_config là build metadata;
  các đường dẫn `/opt/_internal` trong đó không phải đường dẫn runtime được
  suy đoán thay cho proc maps. Torch parallel_info ghi backendOpenMP/max4.
- Thu hai original files/**199122bytes**, SHAremote-before/local/remote-after
  khớp. Bốn Python sources/config giữ đúng tag. Service0exit/terminal, không
  còn owned worker; governorondemand/swaps/affinity trước–sau bằng nhau.
  SSH vẫn mở. Driver39674 chỉ được chờ đến terminal91e928/exit0; không có
  tác vụ trợ lý khác trong khi QA chạy.

Nguồn dưới `sponge-sim/results/pi3b_pool_stages_device_qa_20261115/`:
`original/qa_result_01.json` SHA256
`e3b1a9f186d8a31d7bb03d76064f54eab13d744d430cb53737dacbd493cb6d4a`;
`original/qa_manifest.json` SHA256
`86adeaa718cf4141cbc1d9d61c1394bcb1eb4e2252c1f5fac7d2db4768a27756`.
`snapshots[0..10].inventory.threads,thread_names,loaded_libraries` là nguồn
từng dòng bảng; `transitions[0..9]` giữ born/gone(startticks) và library
paths. `independent_saved_audit.json:stage_table` nối exact selectors;
`verification.json`, `terminal_{before,after}_fetch.json`, source_preparation,
manifest và device_invocation lưu SHA/tag/terminal/readback. Kế hoạch:
`sponge-sim/prereg/QA_PI3B_POOL_STAGES_20261115.md`.

## Phát hiện cần biết

- **Đã xác định được các mốc phát sinh TID trong phiên chức năng này**, chưa
  gán thư viện sở hữu mỗi TID, chưa đo active overlap/oversubscription, CPU
  utilization hoặc nguyên nhân NMS. NumPy được import trước Torch trong QA
  này, khác trình tự nội bộ khi chỉ `import torch`; không dùng census để
  viết lại lịch sử phiên trước. Các thao tác mm/check/config gộp trong một
  mốc không được tách tác dụng riêng sau khi thấy kết quả.
- Cmdline chạy thực có `cgroup_disable=memory`. Root controllers là
  `cpuset cpu io pids`, không có memory; proc/cgroups không có memory row
  (không phải một row có enabled0). File `/boot/config-6.18.50+rpt-rpi-v8`
  trùng kernel release ghi `CONFIG_MEMCG=y` tại dòng188, `CONFIG_PSI=y`137,
  `CONFIG_PSI_DEFAULT_DISABLED=y`138. File config SHA256
  `545260efb824b8999548ce483bce856bb60e72718ced820fbd951c025689c746`;
  `/proc/config.gz` không có. Không coi file config trùng release là hash
  chứng minh toàn bộ running kernel, hay khẳng định global PSI đã được đo.
- Tài liệu kernel định nghĩa `cgroup_disable` vô hiệu controller được chỉ
  định. **Diễn giải từ tài liệu và raw:** cờ boot memory giải thích việc
  không có memory controller trong hierarchy đang nhìn thấy, thay vì lỗi
  riêng reader hoặc SSH scope. Không sửa cmdline/reboot để lấy counter.
  [Linux kernel parameters](https://docs.kernel.org/admin-guide/kernel-parameters.html).
- Root subtree_control=`cpu pids`; system.slice subtree_control=`pids`;
  leaf rỗng. Tài liệu cgroup-v2 nói interface controller ở child phụ thuộc
  controller bật tại parent: điều này giải thích leaf không có cpu.max khi
  CPU chưa bật ở subtree_control của system.slice. Parent cpu.max=`max 100000`.
  `cpu.max` được mô tả cho non-root; root không có file này không phải một
  lỗi thiết bị. Không từ đó suy mọi scheduling/throttling cause đã bị loại.
  [Linux cgroup-v2](https://docs.kernel.org/admin-guide/cgroup-v2.html).
- Memory cgroup event/pressure counters vẫn UNAVAILABLE, không dùng0. Trace
  tương lai nên dùng process/thread faults/CPU counters đã có, giữ cgroup
  optional để chẩn đoán; không chặn toàn bộ nghiên cứu chỉ vì thiếu API này.
- Full inventory/proc-maps đọc tuần tự và có observer work. Chưa đo overhead;
  không đặt mọi procfs/library reads quanh một NMS ngắn rồi gọi delta là
  kernel-only cost. Cần observer nhẹ quanh call + sham, inventory ở ranh giới
  block, cố định trước phép đo. Chưa có latency hay chọn cấu hình thread tốt
  nhất từ dữ liệu này. NMS A/A–MDE cũ vẫn FAIL, PI1 hủy, RSS PASS giữ nguyên.

## Việc tiếp theo — chọn 1 trong các cách sau

1. Hoàn thiện observer nhẹ và host/device API QA; giữ full TID/cgroup census
   ngoài call bracket. Trước overhead timing phải có PREREG riêng.
2. Chuẩn bị matched-predecessor protocol: cố định input/backend, so sánh NMS
   sau workload mask và đối chứng phù hợp, bare-kernel/wrapper tách riêng,
   A/A–MDE/sham/physical guards. Không mở lại các tag đã đóng.

## Đang chờ gì ở tôi

Không cần thao tác thêm; không bật memory controller, đổi nguồn hoặc tắt SSH.
Hiện không có phép đo khoa học đang chạy. QA này không tự cấp PASS timing.
