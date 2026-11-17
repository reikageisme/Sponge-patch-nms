# 02 — Kiểm toán mã CORE

Ngày 21/10/2026. Trạng thái **ANALYZED**, không chạy lại detector/training/benchmark. Đọc source, AST, manifest và raw JSON; tính độc lập nhẹ trong bộ nhớ. Source hiện tại khác source của một số lượt cũ, nên phân biệt lỗi của code hiện tại, đường sinh số đã lưu, và thiếu bằng chứng. Mức BLOCKER dưới đây là blocker cho **kết luận khoa học/tái lập**, không có nghĩa mọi số liệu đều sai.

## 1. Phát hiện ưu tiên

| ID | Mức | Bằng chứng | Vấn đề và tác động | Cách sửa đề xuất, chưa thực hiện |
|---|---|---|---|---|
| C01 | BLOCKER cho bản đồ resource | `experiments/x5_resource_profile_v2.py:66-80,109-129` | `threads` chỉ là số server trong simulator (`free_at=np.zeros(threads)`); service times được đo một lần trước vòng profiles. Không có ghim core/đổi intra-op threads theo profile. Không được diễn giải X5 thành CPU 1/2/4 core hoặc các container profile đã đo. | Tách số server, CPU affinity và intra-op threads thành ba biến; đo lại service từng resource profile, log affinity/cgroup thực. |
| C02 | BLOCKER cho chuỗi NMS→QoS X5 | `experiments/x5_resource_profile_v2.py:48-62` | Đồng hồ chỉ bao `model(image)`, không decode/filter/NMS. Sau `pred=pred[0]`, pred đã 2D nên nhánh transpose ở dòng59 không chạy; YOLO `[84,2100]` bị hiểu theo hàng channel. Candidate đếm tối đa84, có thể gồm tọa độ box; không phải Nτ hợp lệ. | Adapter có output contract `[B,N,4+C]` + kiểm shape; service bao đúng công đoạn tuyên bố; đối chiếu raw tensor với native detector. Không dùng số candidate X5 hiện tại để suy luận NMS. |
| C03 | BLOCKER cho exact-source replay | `outputs/extended_q1_20261002/manifest.json` các trường script/source SHA; `outputs/env_verify/latest.json:2,43-53`; `core/victim_model.py:43-52` | Optimizer script và victim source hiện tại không khớp hash lượt02/10; comments có sửa sau đó. Weight khớp. Không tái tạo chính xác source chỉ bằng current checkout. Đây không phải bằng chứng giả số. | Đóng băng đúng source snapshot từng run và diff đã chuẩn hóa LF; giữ nguyên raw; replay bằng snapshot/lock tương ứng. |
| C04 | MAJOR | `experiments/extended_stream_qos.py:57-62,117,126-136` | Adaptive dùng actual inter-arrival với so sánh strict `<period`. Jitter 299.xms ở chu kỳ300 tự gây drop ngay khi worker rảnh. Raw clean bỏ114/320=35.625%, tất cả `adaptive_interval`, interval tối đa300. | Quyết định admission gắn scheduled release/next eligibility; kiểm jitter và worker nhanh; lưu actual/scheduled timestamps. Không gọi 35.6% này là DoS hay chi phí defense tất yếu. |
| C05 | MAJOR | `experiments/extended_validation.py:115-117,264-267`; `experiments/extended_evaluation.py:94-96,116-120,211-221`; `experiments/x2_architecture_boundary.py:327-331` | Có đường reuse chỉ theo file tồn tại. Guard cấp run không khóa mọi dependency/patch/weight; X2 đọc cached detector output dù thay request images/patch/source. Có thể dùng lại kết quả/timing khác cấu hình. Chưa chứng minh điều đó đã xảy ra ở raw đang audit. | Content-addressed case/cache theo config+code+weights+patch+image; fail closed mismatch; timing mới không reuse như phép đo độc lập. |
| C06 | MAJOR nếu gọi native YOLO | `experiments/extended_evaluation.py:29-44`; `core/victim_model.py:157-164,183-184` | Argmax class rồi class-agnostic NMS. Đây là pipeline tự định nghĩa, không cùng native class-aware Ultralytics. AP/workload khác; hợp lệ nếu khai rõ, sai phạm vi nếu khái quát thành mặc định triển khai. | Config class-aware/agnostic tường minh; native matched control; giữ pipeline hiện tại như một backend đã định nghĩa. |
| C07 | MAJOR giới hạn timing | `experiments/extended_backend_qos.py:123-138,153-180`; `experiments/extended_evaluation.py:107-145` | Có warm-up, randomization và raw timings nhưng chưa pair-interleave sạch/patch từng trial; chưa affinity, thermal/frequency control, GC policy. `set_num_threads` không ghim core. | Randomized paired blocks, warm-up theo tiêu chí ổn định; log CPU IDs/frequency/thermal/background load; đo tổng một clock interval. |
| C08 | MINOR ngoài input thường gặp | `core/victim_model.py:263`; `experiments/test_extended_evaluation.py:52` | IoU cộng epsilon cố định1e-6 khiến box rất nhỏ khác torchvision. Tie/near-threshold chưa bảo đảm tương đương mọi input. | Chỉ guard union không hợp lệ; tests small/degenerate boxes, ties, IoU sát ngưỡng; quy định equivalence theo tập detection với tie policy. |
| C09 | MINOR thiết kế | `experiments/extended_validation.py:62-66,84-89` | Hardcode320 và thiếu validation size/location ở helper; spec đã chạy hợp lệ, chưa thấy patch tràn ở run chuẩn. | Dùng H/W của tensor; reject vị trí/shape/range không hợp lệ; tests border. |
| C10 | MAJOR cho dùng X5 v1 | `experiments/x5_resource_profile.py:1-3,91` | `ast.parse` lỗi `unterminated triple-quoted string literal (detected at line206)`. Source hiện tại không runnable; không dùng nó chứng minh cách sinh v2. | Lưu source run thật; bỏ v1 khỏi entry points sau duyệt. |

## 2. A — Patch, vị trí, preprocessing

`experiments/local_q1_validation.py:64-67` mở RGB, resize trực tiếp 320×320 bằng bilinear, chia255; không letterbox. `extended_validation.insert:84-89` clone và ghi đè đúng CHW region, giữ gradient. Vì direct resize, inverse box dùng sx/sy riêng là đúng; không áp inverse letterbox vào pipeline này.

`find_locations:69-80` tính Laplacian trên grayscale uint8 của ảnh **đã resize**; cửa sổ patch-sized, stride=max(size//4,8), thêm coordinate cuối, quét y rồi x. Dùng `>` nên tie giữ cửa sổ đầu. Center/random ở dòng62-66; random bao cả biên. Mặc định64²/320²=4%, các baseline chính cùng diện tích. Không gọi Laplacian là saliency đạo hàm của detector, cũng chưa có bằng chứng vị trí là NP-hard trong bài toán này.

`make_eot:41-57` đúng rotation±15 p=.8, color .2 p=.8, blur3×3 sigma .1–1 p=.5, sensor noise .02/clamp. EOT biến đổi **toàn scene đã chèn patch**, không chỉ patch. Đây là EOT phần mềm, không xác nhận tính in được/camera/góc nhìn vật lý.

Legacy `attack/genetic_algo.py` chỉ tái dùng một số helper trong main optimizer; `_compute_saliency_location` và `evolve` không đồng nhất với đường extended. Không lấy lỗi/đột biến uniform của legacy evolve để phủ nhận Gaussian mutation trong số liệu extended.

## 3. B — GA, ngân sách và rò rỉ

| Kiểm tra | Kết quả xác minh |
|---|---|
| Main GA | Vòng riêng `extended_validation.py:158-216`, không gọi legacy evolve. |
| Budget | `:155-163,182-188`: cost=4×EOT draws mỗi candidate; kiểm divisible; dừng trước overshoot. 400/1000/2500 draws1 =100/250/625 candidate evaluations. Budget2500 kết thúc population cuối còn5 evaluations; không phải tất cả đều trọn generation. |
| Elite | Top5 được đánh giá lại trong mỗi generation; **đã tính** forward budget. 15 children, mutation Bernoulli .1 từng cá thể, Gaussian sigma .2/clamp ở `:209-216`. |
| Fitness | Mean trên4 ảnh rồi mean draws (`:185-186`), threshold sum confidence+1.5N từ `core/sponge_fitness.py:21`. Không nhầm sum/mean với effective λ. |
| Best selection | Global best EOT sample `:190-191` có selection optimism; không gọi nó expected robust fitness. Có independent EOT ở `extended_evaluation.py:163-189`:8 ảnh×16 fresh draws với common RNG clean/patch. |
| Whitebox | Tanh smooth objective + sign update1/255 ở `:165-178,192-202`; save đúng candidate pre-update đã đo. Equal forwards không equal FLOPs/backward/access. Không là phép tách duy nhất ảnh hưởng fitness khỏi GA. |
| Phantom local | `extended_phantom_local.py:142-143,165-185,197-201`: clean+patched4+4 forwards/step; budget400=50 backward calls. Khác GA compute. |
| Seed/resume | `extended_validation.py:118-120,141-143,218-220`: Python/NumPy/torch và RNG resume. Chưa deterministic algorithms toàn cục, chưa đảm bảo bit-to-bit liên nền tảng. Legacy SpongeGA tự chọn CUDA khi có GPU trước `.cpu()` có thể đổi khởi tạo dù đo CPU. |
| Split | `prepare_extended_validation.py:104-106` kiểm IDs COCO128 không giao held-out; agent raw audit kiểm4 ảnh tối ưu,500 ảnh hash và split. Unknown pretraining/model selection được khai `:125`; không gọi mọi ảnh hoàn toàn unseen bởi pretrained model. |
| Test-set selection | Đường code chọn patch theo training fitness, không theo test AP (`optimize`). Nhiều lượt/thay thiết kế sau kết quả cần ghi exploratory history, không tự chứng minh không có researcher degrees of freedom. |

## 4. C — Candidate, ratio, NMS

YOLOv8 dùng max class score, không objectness×class (`core/victim_model.py:80-84`, `extended_evaluation.py:29-32`). `active_candidates` đếm sau threshold, trước cap; `nms_input_candidates` sau cap (`:37-46`). `max_det=300` áp **sau NMS**, không phải pre-NMS top-k defense. Tanh/Phantom và các detector khác phải giữ endpoint/boundary riêng.

`extended_analysis.py:64-69`: mean theo ảnh của patched/max(clean,1), đúng định nghĩa đề bài. Raw q2500 cho mean clean133.2890625, patched131.05 nhưng mean ratio1.0278018122; ratio of means chỉ .9832014536. Hai thống kê có trọng số khác nhau: không mâu thuẫn toán học. Không suy nguyên nhân từng subgroup khi chưa phân tích per-image differences (xem03).

Backend raw có1.920 records, **1.920/1.920 outputs_exactly_equal=True**; đây là phạm vi sample đã đo. Ví dụ hai hộp trùng1e-4×1e-4: union1e-8 và epsilon1e-6 cho custom IoU≈.0099 thay vì1; đủ giải thích vì sao không tuyên bố equivalence mọi input. Tie ordering CPU/GPU cũng phải khai riêng.

## 5. D — Đo thời gian

`extended_evaluation.py:122-145` dùng perf_counter_ns, warmup1,3 repeats, lưu raw forward samples/cache; postprocessing đo riêng. `:157-158` **không cộng hai median thành total**. Whole prepared-tensor measurement thực có ở `extended_backend_qos.py:153-164`, một clock interval bao forward/decode/filter/NMS. Không phát hiện lỗi cấm “sum of medians” ở đường chính này.

Các điều kiện/cấu hình được shuffle (`extended_evaluation.py:224-225,107-109,134-135`); backend random condition blocks/image order. Chưa xen kẽ sạch/patch từng pair như thiết kế mới yêu cầu. Transfer cũ có shuffle sạch/patch từng image (`extended_transfer.py:246-257`). Warmup1–3 chưa chứng minh thermal steady state. Không có GC disable/restore policy; đó là biến nhiễu cần kiểm soát, không tự làm mọi measurement vô hiệu.

Đường chính CPU không cần CUDA synchronize. Không áp phép timing CPU này sang GPU rồi gọi đúng. Camera/decode disk/patch placement không nằm trong whole prepared-tensor boundary; phải nói rõ boundary, không gọi là camera end-to-end. Thread settings2/interop1 không tương đương2 pinned cores.

## 6. E — Stream QoS

Actual software stream trong `extended_stream_qos.py:80-117` dùng fixed epoch+scheduled release và worker riêng. Deadline từ scheduled release (`:104-106`), không từ start; không trôi lịch theo service duration. Drop-if-busy kiểm cả pending queue; worker errors propagate (`:94-99,131,153-154`). Missing-or-late=1−on_time/offered (`:164-173`). COCOeval nhận toàn image IDs để dropped frames là empty predictions (`:326-342`); late predictions chỉ loại trong deadline-delivered AP, vẫn giữ trong full-offered AP. Hai AP có định nghĩa khác nhau, không phải bug.

EMA .25, margin1.2, cap600 đúng (`Admission:38-55`), nhưng luật actual-arrival có bug C04. Independent read-only calculation trên10 clean adaptive300 files:114 discarded/320 offered=35.625%; toàn bộ `adaptive_interval`, interval max300, nhiều worker_busy=False. Seed0 frame1 actual gap299.5914ms trong khi service đầu141.1525ms. FIFO300 clean/SG400/SG2500/tanh đều0 missing/late. Chưa đủ để khái quát an toàn ở120–250ms hoặc thiết bị khác.

Offline `extended_backend_qos.queue_model:40` dùng late>period, không deadline300. Đã khai modeled và not camera (`:43-46`). X5 v2 cũng là simulation nhưng lại đổi số server; không gộp ba đường này thành cùng một thực nghiệm.

## 7. F — AP/COCO

`extended_evaluation.py:70-79` quy đổi direct-resize đúng sx/sy về ảnh nguồn; sorted category IDs ánh xạ contiguous YOLO COCO classes (`:98,77`). Giữ annotations crowd/ignore native trong COCOeval (`:51-67`). NMS cap300 nhưng COCOeval default maxDets1/10/100 (`:156`) là hai bước khác nhau, không tự mâu thuẫn.

AP gộp ảnh trong seed, rồi lấy mean/SD giữa seed (`extended_analysis.py:116-121`) đúng. Clean deterministic predictions lặp giữa seeds không tạo10 tập ảnh độc lập. AP thuộc **class-agnostic custom pipeline** và fixed subset; không đồng nhất COCO official full-val AP hay native Ultralytics defaults. Chưa rerun predictions→COCOeval trong review này; con số03 tái tổng hợp saved per-seed COCOeval outputs, không chứng nhận inference/AP computation được tái chạy độc lập.

## 8. G — Thống kê, tái tính độc lập

`extended_analysis.py:30-47` yêu cầu10 finite seed effects, SD ddof1;20.000 bootstrap resamples mỗi10 seeds; percentile CI; exhaustive1024 sign assignments, two-sided p; dz=paired mean diff/SD diff. Holm stepdown monotonic ở `:50-56`, family15 alternatives bỏ primary ở `:122-128`, đúng công thức. Không gọi family15 là tất cả tests toàn repo.

Read-only độc lập từ evaluation JSON: primary diff−.0051323560, dz−.4983961361, exact p.150390625, bootstrap RNG20261002 CI[−.01117837858,.000706024479]. 15 Holm values khớp analysis. Lưu công thức và receipt trong03. CI conditional theo seeds trên fixed images; không CI population image/hardware.10 patch seeds không thay thế replicate hardware/session.

Fallacy scan ARS (11/11 đã xét, không suy cáo buộc từ việc thiếu thông tin):

| Loại | Kết luận phạm vi này |
|---|---|
| Simpson | Mean ratios vs ratio means đổi dấu hướng; khác estimand, chưa phải chứng minh Simpson subgroup paradox. |
| Ecological | Không suy pooled image timings thành effect giữa seed/hardware; nguy cơ nếu dùng pooled r với inferential p. |
| Berkson | Fixed first500 IDs không random population sample; chưa xác minh collider selection cụ thể. |
| Collider | Chưa thấy phân tích causal adjustment trên collider; NOT_ASSESSED ngoài source đã đọc. |
| Base rate neglect | AP không là PPV ở prevalence deployment; chưa có deployment base-rate claim định lượng để kiểm. |
| Regression to mean | Chọn best noisy EOT có optimism; có independent EOT giúp tách training extrema. |
| Survivorship | Cần fail/missing run ledger; cache/manifest completion không đủ nếu bỏ failed attempts khỏi báo cáo. Chưa chứng minh số liệu bị chọn lọc. |
| Look-elsewhere | Holm15 đúng cho family được định nghĩa; defense/transfer/QoS/exploration cần family riêng hoặc mô tả exploratory. |
| Forking paths | Nhiều run và draft trộn; đóng băng endpoint/design trước lượt xác nhận mới. Không cáo buộc p-hacking. |
| Correlation→causation | Câu nguyên nhân ở fitness không GA không được baseline whitebox xác định; thay nhiều yếu tố. |
| Reverse causality | Nghiên cứu can thiệp patch có temporal order; association candidate↔latency vẫn bị confound geometry/backend/hardware, chưa có causal identification đầy đủ. |

`p>.05` không chứng minh equivalence, không effect hoặc an toàn. Nếu muốn no-meaningful-service-degradation, đặt equivalence/noninferiority margin và power trước, không thêm sau để hợp thức hóa kết quả âm.

## 9. H — Chuyển giao

Legacy `extended_transfer.py:33,197` có6 detectors,10 seeds,16 ảnh; quantity trong `extended_analysis.py:201-207` là **within-model prepared-tensor latency ratio**, không candidate ratio. DETR no NMS: softmax loại no-object ở `extended_transfer.py:129-137`; không gọi DETR là RT-DETR.

YOLO input RGB0–1; TV dùng native normalization nhưng FasterRCNN/RetinaNet min/max resize320 override ở `:79-86`; DETR ImageNet norm. TV traces có proposal và detection NMS events riêng (`:104-108,123-125`), không cùng YOLO anchor boundary. AP native category mapping được xử lý (`:144-154`, test additional:50).

X2 mới ở `x2_architecture_boundary.py` có các adapter và candidate counts, 5 seeds, 64–100 ảnh tùy detector; normalized score trước/sau proposal selection không đồng nhất giữa model families. Adapter RT-DETR cho phép đối chứng không NMS về mặt mã, nhưng chưa có result; query count cũng không tự là NMS workload. Cached outputs dòng327-331 không kiểm request identity (C05). Không gộp bảng latency cũ 6 model với văn bản candidate mới 8 model.

Xác minh bổ sung X2: **RT-DETR mới chỉ có adapter code, không có saved result**, nên không gọi đây là đối chứng đã đo. `x2_architecture_boundary.py:189-200` NMS thêm trên detections torchvision đã hậu xử lý; không coi timing đó là native internal NMS. `build:240-250` pop `kind` khỏi spec, nhưng writer:352 kiểm lại `spec.get('kind')`, khiến một số weight hashes null (**MAJOR provenance**). `run_detector:263-270` không có forward timer; wall_seconds tổng không thay forward_ms dù docstring hứa latency.

Xác minh bổ sung X5 v2 (**MAJOR simulator correctness**, chưa sửa): `:80` đếm số server bận, luôn ≤ số server, không phải queue depth gồm jobs chờ. `:84` dùng completions[-1] để tính throughput, trong nhiều server completion cuối theo arrival order có thể chưa muộn nhất; drain time cần max(completions). `:111-119` đo clean rồi SG rồi tanh, không pair-interleave. Không lưu raw per-image service samples/shape/thread telemetry, nên chưa truy nguyên chênh tanh khoảng70ms với clean220ms. Không suy patch làm nhanh hơn3×. Script SHA trong `profile_results_v2.json` khớp current v2; dấu hiệu provenance này không sửa được sai measurement boundary.

## 10. I — Chất lượng chung và tái sử dụng

Có nhiều tests trong `experiments/test_*.py` cho patch/budget/EOT/COCO/NMS/stream/stats/Phantom; không viết rằng repo không có test. Review không chạy suite vì imports/fixtures có thể tạo file/download/runtime state. AST first-party parse được trừ X5 v1; đây không chứng minh tests pass.

`core/eot_transforms.py:6` tạo augmentation object ở import; `extended_validation.py:19-29` sửa env/sys.path/runtime path. Code phụ thuộc đường dẫn/run-dir/hardcode320/10seed và JSON schemas chưa versioned. Helpers hash/save/bootstrap, patch/EOT/NMS lặp ở nhiều phiên. Notebook không phải nguồn logic duy nhất trong tuyến chính đã đọc. Exceptions worker được propagate; không thấy silent random-result fallback trên tuyến extended chính. Demo có fallback riêng, không gộp làm kết quả khoa học.

**Kết luận:** viết lại glue/harness/provenance/timing/resource simulation; tái sử dụng có chọn lọc các primitive đã có kiểm thử. Không viết lại toàn bộ detector/COCO/statistics từ đầu. Giữ tất cả raw outputs và source history. Bản mapping, acceptance tests và điều kiện dọn an toàn ở05.
