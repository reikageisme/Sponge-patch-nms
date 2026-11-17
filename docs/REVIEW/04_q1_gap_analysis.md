# 04 — Gap analysis khoa học cho hướng A+C

Ngày 21/10/2026. Phản biện nội bộ theo scope ML/security/systems do tác giả cung cấp; **NOT_CALIBRATED**, chưa chọn venue/track cụ thể. Điểm 1–5 cuối báo cáo là đánh giá tư vấn theo yêu cầu, không phải rubric chính thức của mọi tạp chí Q1. Đây là tổng hợp một phiên có các nhiệm vụ audit tách biệt, không phải panel reviewer độc lập hay cross-model verification.

## 1. Luận điểm A có đứng không?

**Đứng ở dạng hẹp: Nτ đơn độc không đủ để suy ra latency toàn trình hoặc availability; quan hệ phụ thuộc backend và boundary. Chưa đứng ở dạng tuyệt đối “Nτ không dự đoán latency”.** Có quan hệ N–NMS trên các slices đã đo. Kết quả âm của patch yếu không chứng minh hệ thống chống mọi NMS attack.

| Bằng chứng đã có | Giá trị/phạm vi | Ý nghĩa và giới hạn |
|---|---|---|
| OLD128 candidate/AP | 03, K01–K04: SG 1.0278, AP 34.08→29.97% | Integrity loss không bằng availability loss; candidate ratio tăng nhỏ. |
| X1-500 mở rộng | `outputs/x1_500img_20261018/analysis.json:428-462,596-653`: SG q2500=1.02678665, AP=.26198582; SG−center=−.029335, p=.001953125 | Dữ liệu mới quan trọng; bất lợi của saliency so center rõ hơn. Không dùng p=.1504 như kết quả duy nhất. |
| Cùng decoded input, khác backend | `extended_backend_qos.py:49-84`; raw `backend_qos/backend.json` có 1920 records | τ=.01/capnull: 320 rows/backend; pooled median NMS custom 1.641ms vs torchvision .0579ms; outputs trùng trên sample. Backend đổi thời gian dù cùng input/N. |
| Thread settings | `extended_backend_qos.py:104-110,123-180`; 30 timing files | 1/2/4 intra-op threads, 7200 real samples, có whole prepared-tensor time. Chưa CPU affinity/core/resource cap. |
| Actual software streams | `extended_stream_qos.py:66-173`; 240 stream files | Có lịch cố định, worker, deadline/AP; FIFO300 không suy giảm trong các điều kiện đã đo. Adaptive có artifact jitter (02, C04). |
| Synthetic NMS lịch sử | `benchmark_hardware.py:18-66`; `outputs/benchmark/results.json:1-30`; `local_q1_validation.py:100-125` | Đã có N10…10000 và microbenchmark khác có seed/repeats; chưa là dose-response injection full pipeline đồng bộ geometry/backend/resource. |
| Reference variants | `extended_reference.py:1-5,164-176`; OLD `reference/manifest.json:141-203` | Có adapted public functions YOLOv5s640/full-image UAP, không phải exact original experiments hay equal-area baseline. |
| X2/X5 | 03, P01–P10; 02, C01–C02 | Có artifacts nhưng X2 trộn boundary, X5 sai diễn giải profiles/timing/candidate; chưa nâng thành bằng chứng availability. |

Tái tính mô tả riêng τ=.01/capnull trong raw backend: Pearson(N,NMS) custom r=.62098, torchvision r=.12163, N trong 10–270. Với chỉ clean+SG trong raw timing, 1/2/4 threads lần lượt cho N–NMS r=.68779/.66523/.71990 và N–total r=.16369/.29355/.44812. Đây là **pooled descriptive correlations**; repeats/images/seeds phụ thuộc nhau, không gắn inferential p/CI như hàng nghìn replicate độc lập. Các số phản bác câu tuyệt đối “không dự đoán”, chưa đủ làm predictive model tổng quát.

Range restriction N10–270, attack dose nhỏ, thermal noise và backend vectorization đều có thể ảnh hưởng. Không chọn một nguyên nhân sau khi xem số rồi coi là đã được nhận diện. Cần kiểm prediction trên held-out conditions và can thiệp geometry/backend/cap.

## 2. Dữ liệu còn thiếu và thiết kế cần bổ sung

| Khoảng trống | Thí nghiệm cần có | Điều kiện để kết luận |
|---|---|---|
| Testbed sensitivity | Inject synthetic boxes tại đúng detector→NMS boundary, có positive/negative controls | Tăng load tạo NMS latency và ít nhất một controlled deadline crossing; không dùng forward-only timing. |
| Dose-response | N100/300/1000/3000/10000, thêm điểm quanh knee; disjoint boxes, dense clusters, mixed geometry; kiểm score/order | Lưu raw boxes/scores/seed; so cùng N khác geometry. Không giả định mọi overlap đều làm chậm hơn. |
| Vùng proxy đúng/sai | N-only model vs N+backend+cap+geometry; held-out images/conditions/blocks | Báo prediction error, calibration, interval; không leak cùng ảnh/repeats sang train/test. |
| Condition map C | backend×top-k×τ×actual allowed CPUs×period, staged factorial | Có metadata từng cell, khai missing cells; post-NMS counts không thay input N. |
| Arrival knee/headroom | Chu kỳ 100/120/150/180/200/250/300ms, thêm điểm quanh knee của từng profile | Clean phải viable trước; effect ghép cặp có CI. Clean đã overload không là patch-induced failure. |
| Matched baselines | Native/original track và adapted local-patch track cho Overload/Phantom/EVADE | Cùng model/preprocess/boundary/area/access/budget trong matched track; khác thì khai rõ và không xếp hạng xuyên threat. |
| External validity | 500 fixed images đã có; bổ sung random/stratified sample, sessions và detector adapters đúng endpoint | 10 patch seeds không là 10 devices; nhiều ảnh không tự tăng số seed. Tách held-out cohort khỏi quá trình chọn thiết kế. |
| Statistics/power | Đăng ký primary contrasts, practical margin, seed/session unit và correction family trước confirmation | 20.000 bootstrap không tăng sample size; CI hiện tại conditional theo fixed images. |
| Reproducibility | Config/code/weights/images/patch hashes, raw stage timings và source snapshot | Cache mismatch fail closed; aggregate replay không được gọi là inference reproduction. |

Không có một số detector/số ảnh hoặc p<.05 tự bảo đảm Q1. Cần đóng góp mới, thiết kế nhận diện đúng cơ chế, đo đúng quantity và kết luận đúng phạm vi.

## 3. Tính mới sau EVADE và ba phương án đóng góp

[EVADE, NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/hash/371713c3e5314dff9483c62c5abb98a8-Abstract-Conference.html) đã đánh giá tính thực tiễn NMS latency attacks qua hardware, formats, quantization và downstream latency requirements. Chỉ báo “patch không gây DoS trên laptop” chồng lấn đáng kể với công trình này. Cần cơ chế, condition map và predictive validation vượt negative demonstration đơn lẻ.

Ba phương án là **đề xuất, chưa khẳng định đã đạt**:

1. **Chọn A+C:** “Lập bản đồ điều kiện liên kết candidate geometry/workload trước NMS với latency và deadline failures; tách tương tác backend, cap và resource allocation, xác định khi nào Nτ hữu ích và khi nào dự báo sai.” Positive controls, interventions và held-out prediction tạo khác biệt cần thiết so EVADE.
2. “Kiểm định giả thuyết vị trí Laplacian giúp GA patch dưới cùng query/area/access budget; báo kết quả âm và phân tích cơ chế không gian qua seed/cohort/architecture.” Gần dữ liệu hiện có hơn nhưng tính mới hạn chế, cần spatial ablation.
3. “Benchmark boundary-aware có raw stage timings, scheduled timestamps và replayable synthetic controls để nghiên cứu availability trong object detection.” Artifact contribution có giá trị nếu chất lượng và kiểm chứng đủ mạnh; thêm harness đơn thuần chưa đủ Q1.

Tên đề xuất: **“Giới hạn của chỉ số ứng viên trong đánh giá suy giảm tính sẵn sàng của pipeline phát hiện vật thể dựa trên NMS”**. Bỏ claim đã chứng minh DoS/edge/physical khỏi title; laptop resource profile được nêu là testbed, không đổi tên thành thiết bị edge.

## 4. Threat model

`core/victim_model.py:1-9` mô tả score-based gray-box/white-box-at-output-head. Đọc pre-NMS scores mạnh hơn API chỉ trả detections. SG-GA không dùng gradient/trọng số trong fitness không biến local model copy thành remote black-box. Nêu attacker biết preprocessing/interface nào, đọc scores/tọa độ nào, query unit và kênh telemetry thực tế đến từ đâu.

Câu đề xuất: “Nghiên cứu sử dụng giao diện hộp xám cung cấp điểm lớp trước NMS; không giả định camera API thương mại có giao diện này. Patch được chèn số trong tensor đã resize; EOT là biến đổi phần mềm. Whitebox và Phantom adapted là privileged controls, khác quyền truy cập với SG-GA.” Tách forward budget, backward count và wall time; giữ area/location/EOT khi so các GA variants.

## 5. Giao thức hạn chế tài nguyên hợp lệ

1. Chọn **laptop CPU profile** làm đối tượng; ghi CPU/OS/kernel/memory, graph/backend/dtype/resolution/τ/cap. Map logical CPU→physical core/P/E/SMT bằng thông tin hệ điều hành; không mặc định CPU0 là P-core.
2. Tách `allowed_cpus`, `intra_op_threads`, `interop_threads`, `num_workers`. Pin process/worker rồi read-back. Một worker 4 threads khác 4 server lý tưởng. X5v2 chưa làm việc này (`:66-80,109-129`).
3. Linux/cgroup ghi effective cpuset, cpu.max, memory limit và throttling stats; Docker Desktop/WSL ghi cả VM allocation và host/guest mapping. [Docker CPU constraints](https://docs.docker.com/engine/containers/resource_constraints/) phân biệt CPU-time quota với tập CPU được phép; `--cpus` không đồng nghĩa `--cpuset-cpus`.
4. Nếu có quyền, fix governor/tắt turbo và ghi actual read-back. Nếu không, giữ cấu hình được đo và log frequency/temperature/throttling, khai giới hạn. Review không tự đổi BIOS hay host settings.
5. Warm-up theo tiêu chí ổn định định trước; randomized paired clean/patch blocks, cân bằng thứ tự, cùng ảnh; lưu raw trials và telemetry. Không quy chênh clean đo đầu/tanh đo cuối cho attack khi chưa loại drift.
6. Đo prepared-tensor stages và scheduled release→completion riêng. Deadline từ lịch phát. Fixed-FPS simulator chỉ là model nếu không có actual worker processing; không đổi nhãn thành camera measurement.
7. Hiệu chỉnh trên ARM thật nếu có: Raspberry Pi/Ampere/Graviton là các nền khác nhau, phải ghi rõ device/backend. Cùng graph/dtype/resolution/τ/cap; so stage shares, ratios, knee và uncertainty. Không dùng một scale factor để gọi laptop capped cores tương đương ARM cho mọi cấu hình.
8. Chưa có ARM vẫn hoàn thành laptop study với giới hạn rõ. Mô phỏng không thay bằng chứng physical deployment; ngoại suy edge chưa được xác nhận.

X5 cần đo lại: 32 ảnh service×11 conditions, 99 aggregate rows và 500 simulated frames không là 500 ảnh đo thật. `container_image` là string metadata, không phải receipt container resource cap. Script SHA khớp artifact v2, nên sai boundary không chỉ là phỏng đoán từ source khác lượt chạy (02/03).

## 6. Bài nền và phần cần cắt

[Overload](https://arxiv.org/abs/2304.05370) tối ưu latency với spatial attention và đánh giá YOLOv5/Nvidia NX; [Phantom Sponges](https://arxiv.org/abs/2205.13618) dùng UAP nhắm NMS. Không so trực tiếp hệ số công bố của họ với patch overwrite 64×64/YOLOv8n CPU để xếp hạng. Repo có adapted reference variants ghi `original_paper_experiment_reproduction:false` trong OLD reference manifest; giữ ranh giới này và bổ sung matched track nếu cần.

| Phần cần cắt/hạ claim | Lý do và bằng chứng |
|---|---|
| Nhánh B person/AdvT-shirt/YOLO11/12/13 training và published YOLO13 rankings | TEX190-216,475 trở đi: target/device/preprocess khác, không nhận diện NMS availability. Giữ artifact/report riêng, không xóa. |
| Hình7 camera | TEX462-467 đã khai giới hạn; 03,U01 chưa bind patch/raw. Giữ historical supplement nếu cần, không làm bằng chứng A+C. |
| Tám kiến trúc với pre-NMS endpoint đồng nhất; RT-DETR control đã đo | X2 trộn post-module/pre-NMS và thiếu RT-DETR result; P01–P05. |
| Fitness là nguyên nhân, không GA; null p suy ra không effect | TEX606 thay nhiều yếu tố; không có factorial/equivalence test. |
| X5 core/container validation | 02,C01–C02: mô hình nhiều server trên forward times, candidate estimator sai với output YOLO chuẩn. |
| Physical robustness/edge DoS đã chứng minh | EOT phần mềm; chưa calibrated ARM/camera measurement và failure quy được cho NMS. |

## 7. Đạo đức và công bố

Theo yêu cầu tác giả về dual-use: công bố measurement harness, schemas/manifests, synthetic fixtures và raw timing/analysis đủ kiểm chứng. A+C không nhất thiết cần phát hành optimized patch; nếu cần artifact review, nêu scientific need và phạm vi truy cập. Không đóng gói patch vũ khí hóa hay attack service. Positive injections giới hạn trên local authorized testbed, có timeout/backlog bound phục vụ phép đo. Đây là đề xuất công bố, không thêm bước xin phép cho audit hiện tại.

## 8. Đánh giá tư vấn

| Mục | Điểm1–5 | Lý do |
|---|---:|---|
| Novelty |2|Kết quả âm chồng lấn EVADE; causal condition map chưa đủ. |
| Soundness |2|Số học OLD đúng nhưng X2/X5 boundary và suy luận causal còn blocker. |
| Significance |2|Câu hỏi systems quan trọng, chưa định lượng failure boundary có khả năng tổng quát. |
| Clarity |2|Trộn cohort/metric/seed/model count và nhánh B. |
| Reproducibility |3|Nhiều raw/hash/tests thật; historical source chưa khớp current, cache identity và raw X5 thiếu. |

**Dự đoán: reject ở trạng thái hiện tại**; major revision nếu venue cho phép bổ sung thí nghiệm căn bản. Căn cứ là central claim, measurement và novelty; kết quả âm/p>.05 không tự là lý do reject. Không cộng điểm hay chuyển điểm máy móc thành quyết định. Chưa có venue criteria được xác nhận nên không tuyên bố đây là phán quyết theo rubric chính thức Q1.
