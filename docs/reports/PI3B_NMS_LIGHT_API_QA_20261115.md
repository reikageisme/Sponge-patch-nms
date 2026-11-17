## Đã xong

- Đã triển khai observer per-call mới trong namespace riêng, giữ nguyên mọi
  source/tag/raw trước. Provenance từ output_lifetime helper và counter reader
  có file/range/SHA ngay đầu `bracket.py`.
- 25hosttests PASS0.13s, chỉ clock/counter giả: kiểm thứ tự sampler ngoài
  wall interval, lifetime output qua tất cả endpoints, GC true/false và
  khôi phục khi operator/sampler lỗi, counter/schema/identity/monotonicity,
  uninstrumented không đọc resource/CPU, null khác0, platform/mode validation.
  Không có benchmark thật trên laptop.
- Khóa engineering tag `qa-pi3b-nms-light-api-20261115`, commit
  `f7258a5e24a23fce475e4e058bb73e657436c334` trước đúng một native invocation.
  Hai source Python/config giữ đúng bytes của tag, plan/driver/test hashes
  được lưu trước khi đo API. Không phải PREREG hiệu năng.
- **PASS_LIGHT_RESOURCE_API_ONLY** trên Linux/aarch64/Python3.13.5: hai
  `sample()` liên tiếp và một `increments()` đọc được process
  `RUSAGE_SELF` cùng calling-thread `RUSAGE_THREAD`, bốn trường
  ru_minflt/ru_majflt/ru_nvcsw/ru_nivcsw và process/thread CPU clocks ns.
  PID/callingTID24574 nhất quán; các trường integer không âm/delta không giảm.
- Native QA **không gọi `measure()`**, không ghi wall interval quanh operator,
  không Torch/NumPy/model/NMS/mask/RSS hay overhead benchmark. Không suy số
  overhead từ chênh lệch CPU metadata của hai lần đọc. Native chỉ xác minh
  API/schema/arithmetic, host giả chỉ xác minh logic bracket.
- Hai original files/2969bytes có SHAremote-before/local/remote-after khớp.
  Replay độc lập không import helper đã kiểm lại raw/schema/deltas/source/tag/
  manifests. Service terminal, không owned worker; governorondemand/swaps/
  affinity0–3/GC trước–sau bằng nhau, SSH vẫn mở. Không đổi nguồn/controller/
  bộ nhớ/swap/governor, không cài package. Driver11245 chỉ được chờ đến
  terminalc5e4c4/exit0; không tác vụ trợ lý khác khi service chạy.

Nguồn dưới `sponge-sim/results/pi3b_nms_light_device_qa_20261115/`:
`original/qa_result_01.json` SHA256
`8ac3e25561ef2e5c23b89bf8d986cc930bfcaf8ddefdcb09ec0018c892175388`;
`original/qa_manifest.json` SHA256
`074d99eb4e37bd86ccda174a5b314064087418e0778d9e83f1352440c277a9f7`.
Selectors `before/after.{process,calling_thread,process_cpu_ns,calling_thread_cpu_ns}`,
`increments`, context và flags chỉ rõ scope. `verification.json`,
`terminal_{before,after}_fetch.json`, `device_invocation.json`,
`independent_saved_audit.json`, source_preparation và host_checks_01.log
nối từng số/field tới raw/source/tag. Kế hoạch:
`sponge-sim/prereg/QA_PI3B_NMS_LIGHT_API_20261115.md`.

## Phát hiện cần biết

- “Nhẹ” ở đây là bớt thao tác, **chưa đo được overhead nhỏ hoặc bằng0**.
  Helper không đọc procfs/cgroup/inventory/library maps/log/subprocess quanh
  call. Process và calling-thread resource snapshots nằm ngoài perf interval;
  full pool/cgroup inventory phải đặt ở ranh giới block trong runner tương lai.
- Review source sau QA phát hiện `sample()` còn lazy `import resource`:
  lần gọi đầu có thể nạp extension/module qua filesystem. Câu “no filesystem
  operation” trong plan/docstring ban đầu **quá rộng và chưa được kiểm chứng**,
  vì không tính import initialization hay demand paging. Source/tagf725 giữ
  nguyên; API schema/
  arithmetic PASS không phải PASS invariant này. Gói tracer tích hợp phải
  bind/import resource ở setup trước mọi predecessor, kiểm không lazy-import
  trong call path bằng regression và qua integration QA trước timing.
- Process/thread clocks được đọc tuần tự, không cùng khoảng thời gian tuyệt
  đối. Không buộc process delta≥thread delta hoặc clamp tỷ số CPU/wall vào
  [0,1]. Deltas gồm observer work, không phải faults/CPU chính xác chỉ của
  NMS; context switches không là thời gian chờ hoặc nguyên nhân duy nhất.
- Hai mode tương lai có cùng wall interval/GC/lifetime; mode không
  instrumentation giữ counters null/NOT_RECORDED. Cần so sánh cùng input/
  predecessor và sham thực dưới PREREG để kiểm tác động của observer, kể cả
  tác động ngoài clock lên cache/scheduler. GC của hàm bracket mới được host
  kiểm bằng giả, chưa được native operator benchmark xác nhận.
- Memory cgroup vẫn không có do cờ boot đã ghi; không cần bật controller để
  dùng hai API resource này. Native API PASS không sửa các cổng scientific
  đã thất bại, không chứng minh parallel utilization hay cơ chế NMS.
- Full20 NMS cũ vẫn FAIL, PI1 vẫn hủy. RSS USB-present full vẫn PASS với
  phạm vi cache-only đã công bố, không tự chuyển thành speedup hoặc DoS.

## Việc tiếp theo — chọn 1 trong các cách sau

1. Thực hiện runner matched predecessor: cùng input NMS sau native32M/
   candidate16M mask renderer có output parity và NMS-reference, với wrapper/
   kernel-call boundary/sham và hai mode observer. Hoàn thiện functional/
   supervisor/physical QA trước PREREG timing mới.
2. Review bản nháp `DRAFT_PI3B_NMS_PREDECESSOR_20261115.md`; chưa là
   đăng ký, không được chạy timing từ engineering tag này.

## Đang chờ gì ở tôi

Không cần thao tác thêm hay duyệt lại quyền code/API QA. Khi có smoke khoa
học thật và audit/budget cụ thể mới cần review trước full; chưa tới bước đó.
