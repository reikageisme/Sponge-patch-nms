## Đã xong

- Tạo namespace `sponge-sim/studies/pi3b_nms_predecessor_20261115/` riêng;
  copy có file/range/SHA từ các source đã khóa, không sửa source/tag f725
  hoặc dữ liệu cũ. **51 kiểm tra host PASS5.34s** ở lượt cuối; đây là kiểm
  chức năng/fake clocks, không phải timing hoặc số liệu mới trên Pi.
- Sửa readiness gap của prototype: `setup_resources()` import/bind resource
  trước predecessor/trial; `sample()` và `measure()` không tự khởi tạo.
  Cả hai mode đều từ chối trước khi chạy predecessor nếu setup còn thiếu.
  Regression chặn Python import/open sau setup và kiểm AST call-path;
  validate/increments/nonnegative_integer giữ nguyên AST của prototype.
  Điều này không loại demand-paging I/O và không chứng minh overhead nhỏ.
- `pairs.execute()` tắt GC cho cả predecessor+target, release output trước
  của predecessor rồi mới gọi target; không có hook hash/file/guard/log/
  subprocess/gc.collect chen giữa. Output target được giữ qua endpoints và
  trả live cho caller; caller tương lai vẫn phải release trước post-guard.
  Kiểm exception/lifetime/GC bằng giả đạt, không đọc wall-clock thật.
- Scheduler đã tạo đúng36cell/repetition,5repeat/ảnh =180targettrials/ảnh;
  full20=3600, smokeIDs9+30=360. Mỗicell xuất hiện5lần, gồm3predecessor,
  3target,2observer vàA/B. RNG seed theo master index được giữ khi lấy subset;
  không thay image30 thành master index1 trong smoke. Đây chỉ là lịch chuẩn bị.
- `kernel_input.capture()` trích args thực qua đúng một interception ngoài
  clock, khôi phục backend cả khi lỗi, kiểm full detections/selected indices/
  offsets/scores và replay. Input clones giữ **shape/stride/storage_offset**,
  gồm scores view stride38/offset4 trong fixture; không tự contiguous hóa
  rồi loại ngầm công việc copy bên trong kernel-call.
- Hai fixture host dùng installed Ultralytics/torchvision: head7anchors và
  head320boxes không chồng. Head320 xác nhận keep vector chưa cap320 trong
  khi wrapper chỉ trả300; không coi hai outputs là cùng endpoint. Kernel-call
  còn Python/library dispatch, không được gọi bare C++ instruction time.
  Original prediction và prepared args không bị thay đổi qua replay.
- Material helper phân biệt head/prototype không mơ hồ, đối chiếu đúng giá
  trị prototype/coefficients/boxes và k/N_tau/kernel_n với frozen cache row;
  lệch tensor/count bị chặn. Output giữ autograd graph bị chặn trước capture.
  Factories chuẩn bị clones/closures trước pair cho wrapper/kernel-call/sham
  và native32M/candidate16M/NMS-reference. Ba file renderer/cache giữ nguyên
  AST nguồn đã qualified; finite small-mask parity của hai factories đạt.

Chứng cứ: `sponge-sim/results/pi3b_nms_predecessor_prepare_20261115/` gồm
`host_core_01..05.log`, `host_failure_events.json`,
`source_inspection_01.json`, `host_runtime_inspection_01.json`,
`source_preparation.json` và **`source_preparation_final.json`**.
Hai test sources `sponge-sim/tests/test_pi3b_nms_predecessor_{bracket,core}.py`
chứa fixture/assertion và source SHA trong preparation receipt.
**Core lock hiện tại là `engineering_lock_v2.json`**, status
PREPARED_CORE_NOT_RUNNABLE, scientific_endpoint_enabled=False và
functional_device_enabled=False. Lock ban đầu vẫn giữ làm lịch sử metadata.

## Phát hiện cần biết

- Read-only source inspection trên Pi xác nhận service đo inactive/MainPID0;
  không import Torch/model hoặc chạy operator ở Pi trong lượt này. Installed
  `ultralytics/utils/nms.py` SHA
  `3220699ae742312e3fc3816ea917ff17ffd17a96b57593c4c2caff3ff72cf4f7`
  khớp old lock. Raw selected lines25/143–159 ghi max_wh7680, scores=x[:,4],
  class-offset boxes, torchvision call rồi mới cap300 và x[i]. Host có cùng
  source Python NMS này; **không suy compiled backend hai thiết bị tương đương**.
- Imported host runtime: Python3.14.6, Torch2.13.0+cpu, torchvision0.28.0+cpu,
  NumPy2.5.0; target Pi dùng Python3.13.5/Torch2.15.0+cpu/
  torchvision0.29.2+cpu/NumPy2.5.4. Host có registered torchvision::nms và
  tests gọi operator thật nhưng không đo thời gian. Native real-cohort/input/
  mask/kernel parity còn thiếu, không được dùng51tests thay thế bước đó.
- Initial preparation lấy version bằng importlib.metadata, trong đó
  torchvision ghi0.1.6, khác imported runtime0.28.0+cpu. Giữ nguyên initial
  lock/receipt, ghi cả hai ở lockv2 và runtime inspection; future lock phải
  dùng module.__version__ như old Pi worker, không distribution metadata
  thay cho module đang chạy. Không cài/sửa package hay đoán nguyên nhân lệch.
- Host attempt đầu36PASS/2FAIL: hook cấm import được bật quá sớm làm chính
  pytest monkeypatch import inspect bị chặn; đổi thứ tự setup/undo của hook,
  giữ nguyên invariant. Toy head6anchors kích hoạt shortcut end-to-end
  six-column của Ultralytics nên không có kernel call; đổi positive fixture
  sang7anchors và giữ6anchors thành negative test bắt buộc từ chối. Không
  đổi bất kỳ ảnh/cohort/điều kiện/gate khoa học nào. Các log cũ giữ nguyên.
- Lần host đầu Ultralytics fallback settings tới `/tmp/Ultralytics` vì parent
  temp config được chỉ định chưa tồn tại. Không xóa/di chuyển fallback đó.
  Fixture sau tạo parent trước import; offline=True/autoinstall=False khi
  import Ultralytics, không download model/dataset/package.
- Chưa có worker giữ model/clean+adv buffers theo contract, native material
  export/audit40cases, warmups/reference/actual-load sentry, physical guards,
  USB phase baseline, supervisor/independent restore QA hoặc analyzer đầy đủ.
  Core helper không có CLI khởi chạy timing. Không có scientific PREREG/tag
  hay nguồn evidence mới về overhead/latency/NMS cause/DoS.
- Native full-pool inventory/proc maps chỉ được đặt ở block boundaries;
  source/kernel/layout/parity checks ở setup, không chen predecessor-target.
  Kernel-call và wrapper là hai scope riêng: không trừ median để gọi phần
  còn lại là wrapper overhead hoặc reconstruct pipeline.
- Full20 NMSFAIL, PI1cancel và RSSPASS cũ giữ nguyên; native f725 API PASS
  vẫn không là integrated-timing qualification. Không chạy lại tag đã đóng.

## Việc tiếp theo — chọn 1 trong các cách sau

1. Hoàn thiện model/material worker cùng guard/supervisor và fault-injection
   QA; đối chiếu native40case/true-input layouts/outputs trong một plan hữu hạn
   trước khi scientific registration được mở.
2. Chốt warmups/reference/parallelism sentry và resident-buffer/lifetime
   contract trong DRAFT trước mọi timing; sau QA mới PREREG/tag/smoke thật,
   audit/budget rồi review trước full. Không lấy engineering PASS làm số NMS.

## Đang chờ gì ở tôi

Không cần thao tác thêm. SSH vẫn mở, không có workload đo đang chạy. Các
quyền code/QA đã có; chưa đến bước smoke review cho full khoa học mới.
