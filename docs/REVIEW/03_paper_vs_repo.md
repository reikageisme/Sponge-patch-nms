# 03 — Đối chiếu bài báo ↔ repo

Ngày 21/10/2026. Manuscript chính: `BaoCaoKhoaHocAdversarialAttacks_Q1_VI.tex` (dòng theo source hiện tại). Các DOCX/root TEX và `_paper_revision_20261013` là phiên bản khác; không tự coi mọi bản là cùng manuscript. Các số dưới đây tái tổng hợp từ raw records/metrics đã lưu; **không chạy lại inference, training hoặc COCOeval từ predictions**. JSON một dòng được dẫn `:1` kèm trường/selector cụ thể, không bịa line cho từng record.

## 1. Ba cohort phải tách

| Nhãn review | Run | Ảnh/seed | Endpoint |
|---|---|---|---|
| OLD128 | `outputs/extended_q1_20261002` | q400/q2500:128 ảnh,10 seed; q1000:32 ảnh | candidate, COCO AP; transfer riêng 6 models×16 ảnh×10 seed là latency ratio |
| X1-500 | `outputs/x1_500img_20261018` | q400/q2500:500 ảnh,10 seed; q1000:32 ảnh | candidate/AP; tanh 1.1987 thuộc cohort này |
| X2 | `outputs/x2_architecture_20261020` | 8 saved detector files;5 seed;64–100 ảnh | count ratios tại boundary từng adapter, không phải toàn bộ pre-NMS |

## 2. Bảng đối chiếu

| ID; con số/khẳng định trong bài | Vị trí trong bài | File gốc/selector | Giá trị tái tính/xác minh | Khớp? | Ghi chú/câu sửa đề xuất |
|---|---|---|---|---|---|
| K01 SG 1.0278±.0083, center 1.0329±.0093 | TEX:70,228-238,606 | OLD128 `evaluation/{sg_ga,ga_center}_seed0..9_q2500.json:1`, records τ=.01/capnull | 1.0278018122082635±.008322017510560954;1.0329341682335595±.009286812157733637 | Y cho OLD128 | Giữ run ID,128 ảnh; không gọi đây primary X1-500. |
| K02 diff−.0051,CI[−.0112,.0007],p.1504 | TEX:70,606 | Cùng raw K01; `analysis.json:598` là derived comparator | diff−.005132356025296;CI[−.011178378580684,.000706024479203];p=.150390625;dz−.498396136142396 | Y | Không suy equivalent hoặc SG=GA tâm từ p > .05. |
| K03 AP34.08→29.97/25.88% | TEX:70,280 | OLD128 clean/SG/center files, metrics τ=.01/capnull | .3407944995428243→.2996788246698827/.2588038032468697 | Y tổng hợp | Đây saved COCOeval outputs, chưa tái sinh AP từ predictions. |
| K04 133.29→131.05 nhưng ratio>1 | TEX:280 | OLD128 records clean/SG q2500 τ=.01/capnull | clean 133.2890625;SG 131.05;ratio means≈.98320145;mean image ratios 1.02780181 | Y, không lỗi | Hai estimands khác nhau. Viết: “Trung bình tỷ số theo ảnh tăng nhẹ, dù số ứng viên trung bình giảm; không diễn giải hai phép gộp như cùng đại lượng.” |
| P01 Tám kiến trúc nhưng danh sách có RT-DETR | TEX:428-430; bảng 440-445 | X2 detector JSONs; OLD128 `transfer/manifest.json:16-35` | Dòng430 liệt kê 9 tên; X2 có 8 saved results không có RT-DETR; OLD128 có 6 gồm DETR ResNet50 | N | Bỏ RT-DETR khỏi kết quả X2 chưa có artifact; giữ DETR cũ trong phép thử tách biệt. Code adapter không là bằng chứng đã đo. |
| P02 Mười patch nguồn cho X2 | TEX:430 | X2 manifest trường seeds/patch_sha256 và từng detector file |5 seed0..4,5 patches; old transfer mới là10 | N | “X2 dùng 5 miếng dán nguồn; old transfer dùng 10.” |
| P03 1.02–1.24/FRCNN1.11/Retina1.24 vs bảng1.0419/1.0071 | TEX:70,438-445,458,604,608 | X2 `fasterrcnn.json:35`, `retinanet.json:35`; OLD128 `transfer/*_seed*.json:1` | X2 count 1.1107434494/1.2356262624; OLD latency 1.0419370672/1.0071135501 | N do metric/cohort | Tách bảng “latency OLD” và “counts X2”, ghi denominator/boundary. Bảng cũ tự khớp raw; văn bản xung quanh trộn. |
| P04 64–100 ảnh vs Hình16 ảnh | TEX:430 vs454 | X2 từng file trường images; OLD transfer manifest | X2 100 ảnh cho v8n/v8s/11n,64 cho 5 models khác; old 16 | N do cohort | Chú thích hình cũ đúng với nguồn cũ; tách phép thử hoặc dựng hình X2 mới sau duyệt. |
| P05 Đồng nhất mọi ratio là pre-NMS | TEX:430,458,604 | `experiments/x2_architecture_boundary.py:122-151`; raw trường boundary | YOLO pre_nms_head; FRCNN/Retina/SSD post_module_detections đã qua NMS nội bộ | N | “Tỷ số số lượng tại boundary từng adapter”; không dùng post-module count để kết luận NMS workload. |
| P06 Whitebox 1.199 vs 1.1552, không khai cohort | TEX:238,426,606 | OLD analysis:2125; X1 analysis:1955; `docs/X1_500IMG_TABLE_VI.md:26,91` | old 128=1.155248224291879;new 500=1.198715943019521; cả hai q400 | N về trình bày | “Tanh q400:1.1552 trên 128 ảnh và 1.1987 trên 500 ảnh.” Không so tanh mới với SG cũ như cùng giao thức. |
| P07 Nguyên nhân nằm ở fitness, không GA | TEX:606 | `extended_validation.py:165-178,192-202`; TEX:426 tự khai gradient access | Không có factorial tách objective/access/optimizer | Không suy ra | “Chênh lệch gợi ý cần kiểm tra objective và optimizer; thiết kế hiện tại chưa phân biệt nguyên nhân.” |
| P08 Hiệu ứng không phụ thuộc mạnh architecture NMS-specific | TEX:458,608 | X2 mixed boundaries và không có RT-DETR artifact | Không có interaction test trên endpoint đồng nhất | Không suy ra | “Các count ratios tại boundary đã khảo sát tăng hạn chế; chưa đủ so sánh tính nhạy NMS xuyên kiến trúc.” |
| K05 16 configs/160 runs/240 checkpoints/250 eval cases | TEX:216 | OLD `manifest.json:244`, protocol.specifications; `evaluation/manifest.json:21`; filesystem counts |16 specs;160 complete.json;240 checkpoint_q*.json;250 main cases | Y | Main cases lọc tên trong specs+clean. Glob*_q*.json có420 files, gồm170 EOT phụ; không đếm tất cả là main. |
| K06 7.200 processing measurements | TEX:335 | OLD `backend_qos/timing_seed*_threads*.json:1` |30 blocks,7200 records=10 seed×3 threads×5 conditions×16 images×3 repeats;0 late300 | Y | Prepared-tensor measurement, không core pinning/camera. |
| K07 51.09/52.87ms sạch/SG | TEX:335,604 | Các raw timing blocks,threads 1 | Mean block medians 51.087545/52.87094ms | Y | Không gọi median pooled 7200 hoặc số của X5v2. |
| K08 240 luồng | TEX:250 | OLD `stream_qos/*_period*.json:1` |240 files | Y count | FIFO300 mọi điều kiện nêu trong 02 có 0 missing/late; không chứng minh mọi tải/thiết bị an toàn. |
| K09 Benchmark hộp tổng hợp | TEX:604 | `experiments/benchmark_hardware.py:18-66`; `outputs/benchmark/results.json:1-30` |N10..10000;mean NMS.16825→192.23083ms | Có dữ liệu | Thiếu raw repeats/seed/geometry/hardware/hash; cần đưa method/results vào thân bài. Không “chứng minh O(N²)” từ fit ép qua một endpoint. |
| K10 Đổi backend | TEX:604 | OLD `backend_qos/backend.json:2`, manifest:1 |1920 records custom/torchvision;all outputs_exactly_equal=True trong sample | Có dữ liệu | Khớp finite sample không là equivalence mọi tie/near-IoU. Đã có data, không đề xuất như chưa từng làm. |
| P09 “Tái lập từng số” | TEX:70 vs594-596 | OLD manifest script/source/weights hashes; X2 hashes; saved env report |Weight YOLOv8n/4 train/500 heldout khớp; victim+optimizer source hiện tại khác run;X2 nhiều weights_sha256 null;nhánh B thiếu replay artifacts | Quá rộng | “Cho phép kiểm lại các tổng hợp từ artifacts đã lưu; chưa tái lập độc lập toàn bộ inference/training/timing.” |
| P10 QoS container/resource validation | TEX:604; `docs/GD2_TABLES_SUMMARY_VI.md` bảng C | `outputs/x5_resource_profile_20261020/profile_results_v2.json:19,29-31,59-63`; source v2:48-80,109-140 |32 ảnh service forward;500 simulated frames;profiles là 1/2/4 server lý tưởng;string container_image không chứng minh cap; candidate shape sai ở output YOLO chuẩn | N nếu diễn giải đã hiệu chỉnh resource | “X5v2 là mô hình hàng đợi nhiều server từ forward times, chưa là phép đo 1/2/4 core hay NMS end-to-end.” |
| U01 Hình camera là SG hay random? | TEX:462-467 | `paper_assets_20261013/inventory.json:3-11`; `archive/test_webcam.py:11`; `web_simulation.py:31-33` |Historical provenance insufficient;expected sponge_patch_final.png không tìm thấy;demo có random fallback nhưng chưa bind screenshot | CHƯA XÁC MINH | Bỏ khỏi main A+C hoặc giữ historical supplement. Không khẳng định ảnh chắc chắn random/SG. Cần patch file/hash, config, scene/raw frames, timestamp. |

**10 nhóm P01–P10 đã xác nhận**: gồm 8 nhóm trộn số/metric/cohort/diễn giải và 2 nhóm kết luận không được nhận diện bởi thiết kế (P07/P08). Không đếm các lần lặp trong abstract/body/conclusion thành nhiều lỗi. Camera U01 không tính vào 10;133.29→131.05 và các counts khớp không tính lỗi. “Khẳng định vượt bằng chứng” khác “tái tính ra số khác”; bảng ghi rõ từng loại.

## 3. Bảng transfer OLD128 được kiểm lại

Từngseed lấy mean trên 16 ảnh của patched.total_prepared_tensor_ms/clean.total_prepared_tensor_ms; sau đó mean 10 seed. AP cột dưới là mean saved COCO metrics, không rerun.

| Detector | Latency ratio | AP sạch | AP patch |
|---|---:|---:|---:|
| YOLOv8n |1.0179883882|.3627686466|.2943285800|
| YOLOv8s |1.0084399765|.4742504132|.3819744050|
| SSDlite |1.0065805004|.2661571749|.2445123214|
| FasterRCNN |1.0419370672|.2715556707|.2356118128|
| RetinaNet |1.0071135501|.3516580299|.3036662446|
| DETR |.9969117109|.3136830452|.2698944559|

BảngTEX440-445 khớp rounding. Không đổi nhãn của những số này thành candidate ratio.

## 4. X2 mới: saved detector outputs

| Detector/file dưới X2 | Boundary | Images | Seeds | Mean ratio |
|---|---|---:|---:|---:|
| `yolov8n.json` |pre_nms_head|100|5|1.0343322402|
| `yolov8s.json` |pre_nms_head|100|5|1.0261953682|
| `yolo11n.json` |pre_nms_head|100|5|1.0259116223|
| `yolo11s.json` |pre_nms_head|64|5|1.0214588473|
| `yolov12n.json` |pre_nms_head|64|5|1.0360324400|
| `fasterrcnn.json` |post_module_detections|64|5|1.1107434494|
| `retinanet.json` |post_module_detections|64|5|1.2356262624|
| `ssdlite.json` |post_module_detections|64|5|1.0339737975|

`manifest.json` hiện chỉ bind 5 entries của invocation sau, trong folder có 8 JSON. Ba100-image files và năm 64-image files phải có run identity riêng; không dùng manifest 64 ảnh cho tất cả. `build` pop kind ở `x2_architecture_boundary.py:240-250` nhưng writer kiểm spec.get('kind') ở:352 khiến nhiều weight hashes null. Null không chứng minh weight sai; thiếu provenance để xác nhận.

## 5. X1-500 làm thay đổi primary outcome

Nguồn `outputs/x1_500img_20261018/analysis.json:428-462,596-653` (derived, đối chiếu raw evaluation theo cùng receipt dưới): SG q2500=1.02678665;AP SG=.26198582;SG−center=−.029335,CI[−.038328;−.021598],p=.001953125,dz≈−2.05456. Đây **không phải** p=.1504 của128 ảnh. Dữ liệu mới không hỗ trợ ưu thế SG-GA; hiệu ứng so center đổi rõ khi đổi tập đánh giá. Không thay silently old primary bằng new result; khai replication/expanded cohort và selection history.

## 6. Receipt số học và script kiểm độc lập

Không import helper thống kê của repo. Đơn vị lặp=seed. Floor mẫu số=1. Filter đúng τ=.01/capnull, không lấy record đầu vì configs đã shuffle. Seed bootstrap=20261002,20.000 draws,percentile. Sign-flip two-sided với tolerance1e-12 và1024 assignments; SDddof1. Tái tính15 p rồi Holm stepdown cumulative max: **15/15 adjustedp khớp**. Ví dụ SG−randomlocation mean−.0240602540195,p.001953125,Holm.029296875;SG−randomsearch mean.00098908433306,p.751953125,Holm1.

Script riêng dưới đây là nội dung trong report để tái chạy nhẹ bằng `python -X utf8 -B -` qua stdin, không tạo thêm file, không import/execute repo, không ghi output. Nó tái dựng primary và secondary từ raw; `analysis.json` chỉ dùng làm comparator sau tính. Nó không chạy COCOeval.

```python
from pathlib import Path
import itertools, json, re
import numpy as np

run = Path('outputs/extended_q1_20261002')
def read(name, seed, q):
    return json.loads((run/'evaluation'/f'{name}_seed{seed}_q{q}.json').read_text(encoding='utf-8'))
def counts(case):
    return {r['image_id']: r['active_candidates'] for r in case['records']
            if r['threshold'] == .01 and r['pre_nms_cap'] is None}
def ratio(case, clean, ids=None):
    a, b = counts(case), counts(clean)
    keys = sorted(set(a) & set(b) if ids is None else set(ids) & set(a) & set(b))
    assert keys
    return np.mean([a[i]/max(b[i], 1) for i in keys])
def exact_p(x):
    x = np.asarray(x, dtype=float)
    return sum(abs(np.mean(x*np.asarray(s))) >= abs(x.mean())-1e-12
               for s in itertools.product((-1, 1), repeat=len(x))) / 2**len(x)

clean = [read('clean', s, 0) for s in range(10)]
sg = [read('sg_ga', s, 2500) for s in range(10)]
center = [read('ga_center', s, 2500) for s in range(10)]
x = np.array([ratio(sg[s],clean[s])-ratio(center[s],clean[s]) for s in range(10)])
draws = np.random.default_rng(20261002).integers(0,10,(20000,10))
ci = np.quantile(x[draws].mean(axis=1),[.025,.975])
print('PRIMARY', x.tolist(), x.mean(), x.std(ddof=1), ci, exact_p(x), x.mean()/x.std(ddof=1))

summary = json.loads((run/'analysis.json').read_text(encoding='utf-8'))
np.testing.assert_allclose(x, summary['primary']['seed_values'], atol=1e-14, rtol=0)
np.testing.assert_allclose(ci, summary['primary']['conditional_paired_seed_bootstrap_95ci'], atol=1e-14, rtol=0)
family = summary['secondary_holm_family']
pvalues = []
for row in family:
    left, ql, right, qr = re.fullmatch(r'(.+)_q(\d+)_minus_(.+)_q(\d+)', row['comparison']).groups()
    cases_a = [read(left,s,int(ql)) for s in range(10)]
    cases_b = [read(right,s,int(qr)) for s in range(10)]
    ids = set(cases_a[0]['image_ids']) & set(cases_b[0]['image_ids'])
    diff = [ratio(cases_a[s],clean[s],ids)-ratio(cases_b[s],clean[s],ids) for s in range(10)]
    np.testing.assert_allclose(diff,row['statistics']['seed_values'],atol=1e-14,rtol=0)
    pvalues.append(exact_p(diff))
order = sorted(range(len(family)), key=lambda i:pvalues[i])
adj = [0.]*len(family); previous = 0.
for rank,i in enumerate(order):
    previous = max(previous,min(1.,(len(family)-rank)*pvalues[i])); adj[i] = previous
np.testing.assert_allclose(adj,[r['holm_p_within_declared_secondary_family'] for r in family],atol=0,rtol=0)
print('HOLM_MATCH',len(family))
```

Receipt thực thi read-only: primary−.005132356025296;CI[−.011178378580684,.000706024479203];p=.150390625;dz−.498396136142396. Khác vài1e-16 do thứ tự phép cộng không đổi kết luận. Không dùng “script độc lập” như chứng nhận source/inference chính xác.

## 7. Provenance và những gì chưa tái lập

Kiểm hash trực tiếp cho thấy root `yolov8n.pt` khớp manifest;4 training images tồn tại và khớp;500 heldout images không thiếu và không hash mismatch;IDs train/test không giao. `core/victim_model.py` khác cảbyte lẫn sau normalizeLF;3 sources EOT/fitness/genetic khớp byte. Optimizer script hiện tại cũng khác script SHA của lượtOLD. Chưa tái chạy mô hình với source snapshot lịch sử.

Dataset manifest cũ không mất: `outputs/datasets/coco_val2017_extended/_archive_128/manifest.json` SHA256=`0bcb83bcd9e96949696f200803885daf3806cc24735f5f64968a626a1e708e22`, khớpOLD evaluation manifest. Manifest500 ảnh hiện tại khác là thay đổi dataset có lưu lịch sử, không tự là mất provenance.

Nhánh B cần dataset/checkpoints/source đúng phiên bản để replay theo `README_REVIEW_VI.md` vàTEX594-596; không lấy đủ bằng chứng nhánhA để gọi toàn repo tái lập. Không kiểm lại toàn bộ references, nội dung PDF, từng bbox annotation hoặc mọi binary trong scope này. Hìnhcamera chưa bind nguồn patch; giữCHƯA XÁC MINH. Không sửa manuscript trong review.

Receipt bổ sung X1-500 (tái tính trực tiếp từng seed từ raw evaluation JSON, không import repo): SG=1.0267866513471344; center=1.0561217494657946; AP_SG=.2619858170467624; diff=−.029335098118660065; CI95%=[−.03832823790339332,−.021598326633977788]; exact p=.001953125; dz=−2.0545644255415554. Script dùng cùng filter/count/ratio/bootstrap/sign-flip ở mục6, đổi run-dir và xử lý tuần tự từng seed để giảm RAM.
