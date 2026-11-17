# 05 — Kế hoạch viết lại, chưa thực thi

Ngày 21/10/2026. Đề xuất để tác giả quyết định; không đổi code, không dọn repo, không tạo nhánh hay chạy thí nghiệm. Repo thực tế dùng `core/`, `attack/`, `experiments/`, không có `src/` ở root. Kết luận: **viết lại harness và quản lý provenance; tái sử dụng có chọn lọc primitive đã kiểm chứng**, giữ toàn bộ raw results/source history. Lỗi chủ yếu ở boundary, cache identity, timing và resource interpretation; viết lại mọi thuật toán từ đầu sẽ tăng rủi ro mà không giải quyết câu hỏi nghiên cứu.

## 1. Cấu trúc đề xuất

```text
sponge-sim/
  configs/                 # Một YAML = một thí nghiệm xác định
  src/
    detector.py            # Adapter, raw head, scores và preprocessing contract
    nms.py                 # Filter, pre-cap, NMS backend, post max_det
    patch.py               # Overwrite, location, EOT
    attack.py              # SG-GA/center/random-location/random-search; privileged controls riêng
    timing.py              # Warm-up, paired order, raw stage clocks, telemetry
    profiles.py            # Enforce và read-back affinity/threads/cgroup
    stream.py              # Actual scheduled release + worker + admission policies
    synth.py               # Synthetic boxes/scores/geometry và injected controls
    evaluator.py           # COCO coordinates/categories/dropped-empty AP
    provenance.py          # Config/code/weights/images/patch hashes, cache identity, resume
  run.py                   # Config → kiểm profile → chạy → JSONL + manifest
  analysis/                # Chỉ đọc JSONL; thống kê, prediction validation, bảng/hình
    queue_model.py         # Mô phỏng tách hẳn actual worker measurement
  tests/
  schemas/                 # Versioned event/result/manifest contracts
```

Các module bổ sung có trách nhiệm cụ thể, không tạo abstraction/plugin framework tổng quát trước nhu cầu. Detector adapter phải phân biệt native pipeline và standardized experimental pipeline; không ép model sau NMS thành pre-NMS bằng cách đổi tên field.

Config tối thiểu: seed; dataset/split IDs; model/weights SHA; input transform/dtype/device; score boundary; backend; class-aware/agnostic; τ; `pre_nms_cap`; `max_det`; patch area/location/EOT; forward budget và backward count; allowed logical CPUs; intra/inter-op threads; workers; period/deadline; mode actual/simulated; warm-up/repeat/order policy. Không dùng duy nhất `cores=4` để đại diện mọi cơ chế tài nguyên.

Output JSONL mỗi sample: run/case/seed/image ID, raw stage counts (`n_above_tau`, `n_after_cap`, `n_nms_input`, `n_post_nms`), forward/decode/filter/NMS/whole-span times, scheduled release/actual arrival/start/end, drop reason, deadline result, actual affinity/thread settings, config/code/image/weight/patch hashes. Thời gian camera phải có boundary riêng; field thiếu không tự điền bằng số 0. Manifest lưu units, schema version, runtime binary/version và lỗi/missing cells.

## 2. Ánh xạ cũ → mới

| Source cũ | Module mới | Giữ/viết lại; độ khó |
|---|---|---|
| `core/victim_model.py:19,60,80` VictimModel/raw score extraction | detector.py | Giữ ý tưởng extraction/score semantics; viết adapter shape contract và native/experimental modes. Vừa. |
| `extended_evaluation.py:29,35` decode/postprocess; `core/victim_model.py:263` IoU | detector.py+nms.py | Tách stage, sửa epsilon/scope/tie policy; giữ fixtures. Vừa. |
| `core/sponge_fitness.py:21` | attack.py/fitness helper | Có thể giữ nguyên hàm sau golden tests và license check; proxy là objective, không tự là latency. Thấp. |
| `extended_validation.py:61,84` find_locations/insert | patch.py | Giữ semantics Laplacian và overwrite để replay; parameterize H/W, validate bounds. Thấp. |
| `extended_validation.py:41`; `core/eot_transforms.py:17` | patch.py | Chọn một nguồn EOT; giữ protocol wrapper cho historical replay, tách RNG. Vừa. |
| `extended_validation.py:113,158-216` optimize | attack.py | Dùng vòng extended đã audit; tách budget/checkpoint/RNG khỏi I/O. Không lấy legacy evolve thay thế. Vừa/cao. |
| `attack/genetic_algo.py:19` và train scripts root | helper được kiểm chứng hoặc legacy | Có thể giữ crossover/helper riêng; legacy evolve không đưa vào main harness. “Bỏ” ở đây là khỏi entry point mới, không xóa source. Thấp. |
| `extended_evaluation.py:51,70` COCO metrics/conversion | evaluator.py | Giữ công thức conversion/direct resize và COCO pooling; khóa category/maxDets/empty-frame contract. Thấp/vừa. |
| `extended_backend_qos.py:49,87,153-164` | timing.py+run.py | Giữ whole-clock measurement pattern; viết paired orchestration/telemetry/profile enforcement. Cao. |
| `extended_stream_qos.py:36,66` Admission/execute_stream | stream.py | Giữ scheduling/worker/error propagation; sửa actual-jitter admission artifact; test deadline/AP. Vừa/cao. |
| `extended_backend_qos.py:29` queue_model | analysis/queue_model.py | Tách simulator khỏi actual timing, khai deadline riêng period. Thấp. |
| `benchmark_hardware.py:18,36`; `local_q1_validation.py:100` | synth.py | Tham khảo generator; viết raw fixtures, geometry controls, same-pipeline injection. Vừa. |
| `extended_analysis.py:30,50,64` paired/Holm/ratio | analysis/ | Giữ công thức sau kiểm độc lập (03); tách typed endpoints, seed/image scope, family IDs. Thấp/vừa. |
| `extended_transfer.py`; `x2_architecture_boundary.py:122,189,327` | detector adapters+configs | Native boundary hooks/score semantics/cache identity phải viết lại; không NMS lần hai rồi gọi native latency. Cao. |
| `x5_resource_profile*.py` | profiles.py; optional queue_model.py | Không tái dùng v2 như core measurement; sửa shape/timing/queue metrics hoặc giữ historical simulator ngoài main evidence. Cao. |
| `extended_reference.py`, `extended_phantom_local.py` | Baseline adapters riêng | Giữ native/adapted tracks và threat/budget differences; pin vendor commit và runtime. Vừa/cao. |
| `extended_pipeline.py`, các manifests/cache guards | run.py+provenance.py | Viết lại identity/resume/fail-closed; không resume chỉ theo file tồn tại. Cao, làm sớm. |
| `scripts/verify_env.py`, Docker/requirements | tooling/environment | Tái dùng checks có ích; pin torchvision/runtime thật, image digest/source snapshot, không đọc PASS như tái lập mọi phép đo. Vừa. |
| Web/camera, nhánh B/person training, legacy demos | Ngoài main harness | Không đưa vào main article pipeline; đề xuất lưu lịch sử, chờ duyệt từng nhóm. |

## 3. Cái gì có thể giữ nguyên văn?

Candidate: `calculate_sponge_fitness`, công thức image-ratio/floor1, exact sign-flip/Holm, direct-resize inverse coordinates, hash helper. Điều kiện trước reuse nguyên văn: source hash đúng phiên bản, golden input/output đã lưu, unit tests độc lập và license phù hợp. Chưa chuyển/copy mã trong review. “Giữ công thức đúng” khác “giữ nguyên module với side effects/cache guards”.

Phải viết lại: run/case/cache identity; detector output contracts; real resource enforcement/read-back; timing orchestration và per-trial raw logging; X5 profile interpretation; X2 native-stage tracing; adaptive schedule admission. Mutation/selection nên tách khỏi persistence để dễ kiểm, không đổi thuật toán giữa các lần replay mà vẫn dùng run ID cũ.

Ước lượng cho một kỹ sư quen PyTorch: 4–7 tuần công để có harness và vòng kiểm chứng ban đầu, chưa gồm compute toàn condition grid và chờ thiết bị ARM. Đây là ước lượng lập kế hoạch, không cam kết tiến độ. Thí nghiệm mới có thể cho kết quả âm; acceptance là đo đúng và tái lập, không bắt buộc SG-GA mạnh hơn.

## 4. Thứ tự ưu tiên và acceptance criteria

| Bước | Công việc/ước lượng | Tiêu chí hoàn thành đo được | Thí nghiệm xác nhận |
|---|---|---|---|
| 0 | Đóng băng lineage, schema, primitive fixtures;2–3ngày | OLD128/X1/X2/X5 có run ID riêng; source/weights/patch/image hashes đầy đủ hoặc ghi thiếu; thay config/weight/image/source làm cache reject; không ghi vào old outputs | Replay phép tổng hợp03 từ raw; kiểm altered-hash fixture, missing-file fixture, interrupted-resume fixture |
| 1 | detector+nms+timing+synth;1–2tuần | Adapter assert shape/score boundary; empty/tie/near-IoU/classwise/cap fixtures pass; whole time đo một clock span; raw samples+box geometry tái sinh bằng seed | N100…10000×ít nhất3geometry trên2backend; same-pipeline positive injection tạo measurable workload increase và bounded deadline crossing; không chỉ fit quadratic curve |
| 2 | Resource enforcement và calibration;3–5ngày host, thêm~1tuầnARMnếu có | Read-back affinity/cgroup/threads khớp config; không áp được thì fail hoặc gắn explicit unconstrained mode; ghi frequency/thermal; paired baseline drift trong ngưỡng đăng ký trước | Clean/positive-control repeated balanced blocks trên actual profiles; ARM matched stage shares/knee nếu có; chưa ARM thì chỉ claim laptop |
| 3 | Attack+stream;1–2tuần | Exact forward budget gồm EOT/elite; backward count riêng; seed/resume replay trong pinned environment; patch đúng ROI; schedule không drift; dropped/late AP đúng định nghĩa; nhanh worker không tự drop do ±jitter | Reproduce golden OLD metrics trong tolerance định trước bằng đúng snapshot; GA variants matched budget; quét100/120/150/180/200/250/300ms quanh knee từng profile |
| 4 | Condition map;thời gian compute phụ thuộc pilot | Ma trận backend×cap×τ×allowedCPUs×period có metadata/missing cells; clean overloaded tách; primary contrasts/power/family correction đóng băng trước confirmation; held-out prediction errors và uncertainty được báo | Pilot synthetic xác định transitions → xác nhận trên real predictions/patches và held-out blocks; so N-only vs model thêm geometry/backend/cap |
| 5 | Optional NMS-aware fitness;1–2tuần thêm | Chỉ triển khai nếu diagnostic bước4 cho thấy proxy mới đo đúng workload; cùng access/area/forward budget/held-out selection; backward/wall-time riêng | Pair original vs proposed fitness trên cùng optimizer/access; positive/negative controls; không mặc định overlap-pair count luôn tương quan NMS cost |

Không cần đợi full factorial cực lớn mới kiểm được điều cốt lõi: bắt đầu từ geometry/backend và một actual CPU profile; mở rộng khi positive control và timing có độ tin cậy. Mọi adaptive search của condition grid được ghi là exploratory; dành held-out cells/sessions cho xác nhận.

Power: định nghĩa minimum practically relevant difference cho deadline-miss/latency trước; dùng variance paired seed/session từ pilot với giả định bảo thủ. Số20.000bootstrap không tăng sample size10seed. Nếu cần kết luận không suy giảm đáng kể, dùng equivalence/noninferiority margin và thiết kế riêng; không suy từ nonsignificant superiority test.

## 5. Tests tự động tối thiểu

| Nhóm | Fixture / assertion độc lập |
|---|---|
| Patch | Toy RGB image từng channel có giá trị khác; chỉ ROI đổi, ngoài ROI nguyên; border đầy đủ, out-of-bounds reject; [0,1] và CHW validation. |
| Preprocess/coordinates | Direct resize và letterbox có metadata riêng; round-trip box về ảnh nguồn trong tolerance; không dùng transform này inverse cho transform kia. |
| Budget | Population20/top5, cost4×draws, budgets400/1000/2500; elite reevaluation tính đủ; cuối generation không vượt; whitebox backward riêng. |
| RNG/resume | Seed lặp bằng local generators; interrupted/resumed run khớp uninterrupted trong runtime đã khóa; khác device/version phải có explicit replay scope. |
| Counts/cap | Raw `[B,4+C,N]` và canonical `[B,N,4+C]` toy tensor; max class không nhầm coordinates/objectness; threshold/cap counts riêng; cap sau NMS không giả làm pre-cap. |
| NMS | Empty, one box, disjoint, identical, tiny boxes, IoU sát .45, equal scores, two classes, top-k/max_det; distinct-score ordinary inputs khớp; ties theo policy hợp lệ, không bắt index y hệt mọi backend/device. |
| Ratio | Hai ảnh counts cho mean ratios khác ratio means; zero denominator floor1; intersection IDs; thiếu image không silently thay denominator. |
| Statistics | Toy n nhỏ enumerate sign-flip tay; dz dùng paired SDddof1; Holm monotonic/ranking; deterministic bootstrap quantile; regression fixture từ03 với tolerance rõ. |
| COCO | Golden detections có category mapping/crowd/ignore/empty predictions; pooled-per-seed AP; dropped image vẫn có trong imgIds. |
| Timing | Fake clock xác nhận single-span total; stage boundaries không cộng median; warm-up excluded; cached timing không bị coi trial mới; raw sample count khớp design. |
| Stream | Release schedule không drift; deadline tính từ lịch; worker-fast + inter-arrival299/301ms ở period300 không gây drop policy ngoài dự kiến; busy/backlog/error/drop/late metrics kiểm bằng trace tính tay. |
| Profile | Read-back mismatch bị reject; allowed CPUs khác intra-op threads khác workers; mode simulated/actual không thể lẫn. |
| Cache/provenance | Đổi patch/weights/code/config/image/seed làm identity khác; missing artifact không đánh dấu complete; manifest checksum không thay thế source snapshot. |
| Simulator riêng | Multi-worker throughput dùng max completion; queue depth đếm waiting jobs đúng; arrivals/deadlines theo toy trace; không gán kết quả thành hardware measurement. |

Tests phù hợp theo từng thay đổi sau khi được duyệt; review này chỉ đọc, không thêm hoặc chạy suite có side effects. Tests NMS tie policy dựa [torchvision docs](https://docs.pytorch.org/vision/main/generated/torchvision.ops.nms.html), vì equal-score selections có thể khác CPU/GPU. Timing protocol tham khảo [PyTorch benchmark recipe](https://docs.pytorch.org/tutorials/recipes/recipes/benchmark.html); phải kiểm version/runtime thật, không dựa metadata lạ như0.1.6 để tự chọn binary.

## 6. Dọn repo an toàn — chỉ là đề xuất

| Nhóm cần duyệt riêng | Candidate | Điều kiện trước khi chuyển |
|---|---|---|
| G1 cache tái sinh | `__pycache__`, `.pytest_cache`, `.cache`, temp files theo01 | Xác minh không chứa dữ liệu duy nhất, không tiến trình dùng; lập path/size/hash manifest; venv/runtime/Git không tự coi cache rác. |
| G2 demos | Camera/web/UI assets, root simulation scripts | Truy phụ thuộc README/manuscript/assets; giữ patch nguồn/raw frames nếu có; ảnh giao diện chưa rõ nguồn phải bảo toàn. |
| G3 legacy experiments | `archive/`, local/pre-extended experiments, X5v1, historical source copies | Đối chiếu01 dependency graph và manifests; giữ old run source để replay; không chuyển raw outputs theo nhãn “dead”. |
| G4 nhánh B | `project_yolov13/**` | Có data,weights,vendor,venv,runs có thể ignored/untracked; backup byte-level cùng SHA, không chỉ branch Git. Bổ sung mapping đường dẫn cross-branch weight trước khi chuyển. |

Sau khi tác giả duyệt từng nhóm: tạo nhánh Git **`archive/legacy`** đúng tên yêu cầu, lưu snapshot dirty/untracked/ignored cần thiết, chuyển có manifest old→new+SHA và khả năng restore. Chưa có phê duyệt nên **không tạo nhánh hoặc chuyển gì**. Branch Git đơn thuần không bảo toàn ignored data; dataset/weights/raw NPZ/predictions/logs phải nằm ngoài danh sách xóa mặc định. Không tự commit/push.

## 7. Quyết định tác giả cần đưa ra trước implementation

1. Hướng A+C đã được tác giả chọn; venue/track mục tiêu cụ thể để khóa tiêu chí phản biện là gì?
2. Dùng X1-500 làm cohort chính, OLD128 làm replication lịch sử, hay giữ OLD128 chính và X1 thành robustness check?
3. Chuẩn hóa pipeline native class-aware hay giữ custom class-agnostic như một experimental backend có native control?
4. Có thiết bị ARM nào để hiệu chỉnh, hay giai đoạn đầu chỉ giới hạn laptop CPU profiles?
5. Nhóm G1–G4 nào được duyệt chuyển vào `archive/legacy` ở lượt sau? Có thể trả lời “chưa nhóm nào”; không ảnh hưởng việc giữ nguyên bằng chứng.

**Dừng ở báo cáo review.** Không tự bắt đầu sửa code, tối ưu patch, huấn luyện, dựng Docker, cài package hoặc dọn repo.
