# 06 — Changelog bản thảo v2

Ngày 21/10/2026; branch `paper/q1-fixes`. Chỉ chỉnh bản sao `BaoCaoKhoaHocAdversarialAttacks_Q1_VI_v2.tex`; không commit, không sửa code thí nghiệm, không inference/training/COCOeval, không chuyển/xóa dữ liệu. Original SHA256 trước/sau: `a602b4422842a2e56a7bb8994dd5b4274649a64f22ecbefbbb10d1a2353c1eb5`.

Áp dụng ARS-Codex cho các block tác giả yêu cầu sửa; tóm tắt được sửa theo chỉ định rõ trong attachment. Không tuyên bố PASS cho schema revision tự động hoặc tái lập inference. Giữ CAS/T5/babel và nhãn Việt hóa; thêm TikZ/PGFPlots, graphicspath, cờ nhánh B và nhánh fontspec/TU chỉ cho XeTeX (đường pdfLaTeX giữ T5). Thư mục `REVIEW/06_latex_build/` là bản sao phục vụ compiler, không là dữ liệu thí nghiệm.

## Bảng thay đổi

| ID | Vị trí cũ (TEX gốc) | Trước | Sau | Nguồn số / selector | Trạng thái |
|---|---|---|---|---|---|
| Tên/đơn vị | 56–58,70,82,130,190,335,588 | Ngụ ý Edge Server | Tiêu đề đúng yêu cầu; laptop constrained simulation; chưa có ARM/edge thật | Yêu cầu tác giả; OLD/X1 manifest.protocol.device/input_size/limitations | Đã sửa |
| Tác giả liên hệ | 59–65 | cormark gắn Anh; Nam trong ghi chú | cortext ghi liên hệ Đinh Phương Nam, giữ hai author hiện có, không tự thêm đồng tác giả | Tên/email Nam từ nonumnote gốc; chỉ định mới của tác giả | Đã sửa; author-list còn cần quyết định |
| P09/tóm tắt | 70 | Tái lập từng số; chỉ OLD; trộn X2 | Báo cả OLD128/X1; chỉ kiểm lại tổng hợp; không claim replay toàn bộ | OLD/X1 analysis.primary/methods; raw selector mục dưới | Đã sửa |
| Tắt nhánh B | 74,92,96,112,122–124,188–210,471–536,557,582–596,610 | B hiện trong main | ifbranchB mặc định false; nội dung giữ nguyên trong nhánh chờ duyệt; bảng2 có bản chỉ Sponge | Nội dung gốc được giữ theo cờ, không thêm số B | Đã đánh dấu, chưa xóa |
| Thuật toán/lưu đồ | 156–178 | Chỉ bảng tổng quan | algorithm*+algpseudocode và TikZ: mean4×draws; elite reevaluation; exact budget | experiments/extended_validation.py:113–226; core/sponge_fitness.py:47–57; crossover helper | Đã đối chiếu source; không chạy optimizer |
| Cohort/power | 214–246 | primary không tách; dz−.45; causal tanh | Local-before-eval; X1 mở rộng sau quan sát; dz−.4984; không bảo đảm power; hai Δ cùng âm | OLD/X1 manifest.protocol.primary_hypothesis/minimum_relevant_candidate_ratio_difference/limitations; evaluation.manifest.started_utc; analysis.preregistration; docs/GD2_PLAN_VI.md:15–26 | Đã sửa, không nói đổi dấu hoặc đủ power |
| K01–K03; X1 | 260–289 | Bảng3/Hình1 chỉ128ảnh | Bảng chung và hình hai panel mean/CI, AP, secondary theo từng cohort | OLD/X1 analysis.methods[name,budget2500],primary,secondary_holm_family; raw records/metrics | Đã kiểm độc lập X1 |
| K04 | 280 | Dễ đọc thành mâu thuẫn counts | Giải thích mean ratios khác ratio means; nhãn OLD128 | OLD evaluation/{clean,sg_ga}_seed0..9_q{0,2500}.json:records[τ=.01,cap=null].active_candidates | 133.2890625→131.05;ratio1.0278018122 |
| Ngân sách | 293–298 | Chỉ nêu OLD32 | 32ID chung OLD/X1; không nối mean500 với mean32 | X1 analysis.same_image_budget_curves[name,budget].statistics; raw counts trên32ID nhỏ nhất | 12/12 curves khớp |
| Diện tích/EOT | 304–329 | Diện tích OLD, peak4% | Bảng diện tích/EOT X1; hình EOT bitmap vẫn ghi OLD128 | X1 analysis.methods[area_*,sg_ga,eot_*,q400];independent_eot; secondary_holm_family | Có đủ dữ liệu; sửa peak sang45×45, không causal area |
| K06/K07/K08 | 335–389 | Resource/boundary chưa tường minh | Prepared tensor, OLD128, thread count; chưa core/camera;FIFO300 không suy mọi tải | OLD backend_qos/timing_seed*_threads*.json:records; stream_qos/*period300_fifo.json:missing_or_late_fraction | Giữ số đã khớp |
| K09/K10/P10 | 363,604 | Kết luận container; synth thiếu thân bài | Bổ sung microbenchmark lịch sử, finite backend match; X5 chỉ forward multi-server simulation | outputs/benchmark/results.json:N,latency_ms; benchmark_hardware.py:18–66; backend_qos/backend.json; x5_resource_profile_v2.py:48–80,109–140 | Đã hạ phạm vi; không O(N²) proof |
| P06/P07 | 238,426,606 | Tanh500 lẫn128;fitness cause | Tanh q400 ghi cohort; objective/access/optimizer chưa cô lập | OLD/X1 analysis.methods[name=tanh_whitebox_patch,budget400].candidate_ratio.mean/AP_mean_over_patch_seeds | Đã sửa |
| P01–P05/P08 | 428–458 | Text X2 trộn old latency;RT-DETR;10patch | Hai bảng/hình riêng; X2 boundary/ảnh/5patch; không architecture-independence | OLD transfer/*_seed*.json; X2 từng detector JSON:boundary,images,per_seed,pooled_mean_ratio | Đã sửa; DETR cũ khác RT-DETR |
| U01/Hình7 | 460–469 | Giao diện camera lịch sử | Bỏ figure khỏi main; giữ hai câu giới hạn | paper_assets_20261013/inventory.json; REVIEW/03 U01 | Chờ quyết định phụ lục, không xóa ảnh |
| P09/replay | 594–596 | Scope tái lập quá rộng | Victim/optimizer khác OLD; weights/ảnh khớp; X2 hashnull; optimizer khớp X1 | OLD/X1 manifest.script_sha256/sources_sha256/weights_sha256; X2 detector JSON.weights_sha256; REVIEW/03 hash receipt | Đã sửa đúng tên file |
| Kết luận | 604–612 | Trộn metrics, fitness cause, B | RQ1–RQ3 tách cohort; condition map là hướng tiếp theo | Bảng tra số bên dưới; không thêm measurement mới | Đã sửa |

## Tính độc lập của kiểm số học

Đọc tuần tự 250 main evaluation files X1-500. Không import helper repo. Ghép image_id, chọn `records[threshold==0.01 && pre_nms_cap==null]`; trong seed tính mean_i(patched.active_candidates/max(clean.active_candidates,1)); sau đó mean/sampleSDddof1 qua10seed. AP lấy `metrics[threshold==0.01 && pre_nms_cap==null].coco_subset_bbox.AP`, tổng hợp output COCOeval đã lưu, không tái chạy COCOeval. Bootstrap20.000 với RNGseed20261002; exact sign-flip1024 cấu hình hai phía; Holm family15. Kết quả: **24/24 method-budget,15/15 Holm,12/12 curves,17/17 independentEOT summaries khớp** (<1e-12). Theo script riêng REVIEW/03 mục6, đổi run-dir và xử lý từng seed để giảm RAM.

OLD128 d_z tái tính mean(Δ)/sampleSDddof1(Δ)=−.49839613614239564. X1 d_z=−2.0545644255415554; chênh vài1e-14 do thứ tự cộng không ảnh hưởng làm tròn. OLD và X1 có cùng dấu âm. Tác giả yêu cầu mục tiêu tăng power; repo chỉ hỗ trợ mô tả tăng thông tin/precision, không đủ prospective power guarantee.

## Bảng tra số tóm tắt / in đậm / kết luận

| Số trong v2 | File:selector | Phép gộp |
|---|---|---|
| OLD128: Δ=-0.005132356025295937; CI=[-0.011178378580683919, 0.0007060244792033402]; p=0.150390625; dz=-0.4983961361423898 | `outputs/extended_q1_20261002/analysis.json:primary`; raw `evaluation/{sg_ga,ga_center,clean}_seed0..9_q*.json:records[τ=.01,cap=null]` | Paired seed effects,20kbootstrap,1024signflip,dz=meanΔ/SDddof1Δ |
| OLD128 sg_ga q2500: ratio=1.0278018122082635±0.00832201751056098;CI=[1.0228859202464444, 1.0326067411474387]; AP=29.967882466988264%±0.46825911622831545% | `outputs/extended_q1_20261002/analysis.json:methods[name=sg_ga,budget=2500]`; raw `evaluation/sg_ga_seed0..9_q2500.json:records/metrics[τ=.01,cap=null]` | Mean±SD10seed;AP×100;figure CIs conditional |
| OLD128 ga_center q2500: ratio=1.0329341682335593±0.009286812157733602;CI=[1.027405238364058, 1.0381760443167798]; AP=25.880380324686968%±0.45508088534188024% | `outputs/extended_q1_20261002/analysis.json:methods[name=ga_center,budget=2500]`; raw `evaluation/ga_center_seed0..9_q2500.json:records/metrics[τ=.01,cap=null]` | Mean±SD10seed;AP×100;figure CIs conditional |
| OLD128 ga_random_location q2500: ratio=1.0518620662277636±0.009227108813925394;CI=[1.0461823394382113, 1.0570092000540643]; AP=30.266223503740857%±0.6417040089519134% | `outputs/extended_q1_20261002/analysis.json:methods[name=ga_random_location,budget=2500]`; raw `evaluation/ga_random_location_seed0..9_q2500.json:records/metrics[τ=.01,cap=null]` | Mean±SD10seed;AP×100;figure CIs conditional |
| OLD128 random_search q2500: ratio=1.026812727875204±0.007190072586189135;CI=[1.022989101727791, 1.0314800872624426]; AP=29.928604220658883%±0.26088879656307234% | `outputs/extended_q1_20261002/analysis.json:methods[name=random_search,budget=2500]`; raw `evaluation/random_search_seed0..9_q2500.json:records/metrics[τ=.01,cap=null]` | Mean±SD10seed;AP×100;figure CIs conditional |
| OLD128 tanh_whitebox_patch q400: ratio=1.155248224291879±0.03681635782891523;CI=[1.136000748149502, 1.1785873814376733]; AP=28.618798909944605%±0.4377248650691646% | `outputs/extended_q1_20261002/analysis.json:methods[name=tanh_whitebox_patch,budget=400]`; raw `evaluation/tanh_whitebox_patch_seed0..9_q400.json:records/metrics[τ=.01,cap=null]` | Mean±SD10seed;AP×100;figure CIs conditional |
| X1-500: Δ=-0.029335098118660065; CI=[-0.03832823790339332, -0.021598326633977788]; p=0.001953125; dz=-2.0545644255415554 | `outputs/x1_500img_20261018/analysis.json:primary`; raw `evaluation/{sg_ga,ga_center,clean}_seed0..9_q*.json:records[τ=.01,cap=null]` | Paired seed effects,20kbootstrap,1024signflip,dz=meanΔ/SDddof1Δ |
| X1-500 sg_ga q2500: ratio=1.0267866513471344±0.007378131407361161;CI=[1.0224952806828669, 1.031102147774531]; AP=26.198581704676236%±0.2017095986670433% | `outputs/x1_500img_20261018/analysis.json:methods[name=sg_ga,budget=2500]`; raw `evaluation/sg_ga_seed0..9_q2500.json:records/metrics[τ=.01,cap=null]` | Mean±SD10seed;AP×100;figure CIs conditional |
| X1-500 ga_center q2500: ratio=1.0561217494657946±0.012286505419326044;CI=[1.0497272572239487, 1.0640315708094696]; AP=24.607030339549812%±0.11870825973535946% | `outputs/x1_500img_20261018/analysis.json:methods[name=ga_center,budget=2500]`; raw `evaluation/ga_center_seed0..9_q2500.json:records/metrics[τ=.01,cap=null]` | Mean±SD10seed;AP×100;figure CIs conditional |
| X1-500 ga_random_location q2500: ratio=1.0706513905176493±0.014321394225359135;CI=[1.062088869115, 1.0787638280891338]; AP=27.329344773757047%±0.41266246139047447% | `outputs/x1_500img_20261018/analysis.json:methods[name=ga_random_location,budget=2500]`; raw `evaluation/ga_random_location_seed0..9_q2500.json:records/metrics[τ=.01,cap=null]` | Mean±SD10seed;AP×100;figure CIs conditional |
| X1-500 random_search q2500: ratio=1.0250448878199405±0.004025170331286743;CI=[1.0228456372756831, 1.0276062330010813]; AP=26.27797283621106%±0.09810863809506686% | `outputs/x1_500img_20261018/analysis.json:methods[name=random_search,budget=2500]`; raw `evaluation/random_search_seed0..9_q2500.json:records/metrics[τ=.01,cap=null]` | Mean±SD10seed;AP×100;figure CIs conditional |
| X1-500 tanh_whitebox_patch q400: ratio=1.1987159430195207±0.03800431454600541;CI=[1.1780960641622125, 1.22227408564092]; AP=25.577150323887544%±0.3305303776629562% | `outputs/x1_500img_20261018/analysis.json:methods[name=tanh_whitebox_patch,budget=400]`; raw `evaluation/tanh_whitebox_patch_seed0..9_q400.json:records/metrics[τ=.01,cap=null]` | Mean±SD10seed;AP×100;figure CIs conditional |
| OLD clean AP34.0794499543%;X1 clean30.2702464173% | `outputs/{extended_q1_20261002,x1_500img_20261018}/evaluation/clean_seed0_q0.json:metrics[τ=.01,cap=null].coco_subset_bbox.AP` | Fraction×100 |
| 128/500/32ảnh;10seed;400/2500forwards;6detectors/16ảnh/10patch;8detectors/64–100ảnh/5patch | OLD/X1 `manifest.json:protocol`, `evaluation/*.json:images`; OLD `transfer/manifest.json`; X2 từng detector `images,per_seed` | Thiết kế/count artifacts |
| 51.09/52.87ms;FIFO300ms0%thiếu/trễ | OLD `backend_qos/timing_seed*_threads1.json:records[condition=clean/sg_ga].total_prepared_tensor_ms`; `stream_qos/*period300_fifo.json:missing_or_late_fraction` | Mean block medians;1threadsetting;actual software stream |
| X2 min1.0214588472530495/max1.2356262624141319 | X2 `yolo11s.json:pooled_mean_ratio`;`retinanet.json:pooled_mean_ratio` | Min/max8saved models; mixed boundaries |
| SyntheticN10…10000;0.16825/192.23083ms;320px;edges10–50;IoU.45;warmup5/runs10 | `outputs/benchmark/results.json:N,latency_ms[0,-1]`; `experiments/benchmark_hardware.py:18–66` | Historical NMS aggregate; no raw/hardware binding |
| 500ảnh/3541annotations/80categories | `outputs/datasets/coco_val2017_extended/instances_subset.json:len(images),len(annotations),len(categories)` | Đếm JSON stdlib |
| Fitness4ảnh/EOTm,20population/5elite/15con,pMutation.1,Gaussian.2 | `experiments/extended_validation.py:122–126,154–157,182–216` | Source contract, không số đo mới |

## Số bảng/ablation/budget mới bổ sung và selectors

| Method X1 | q | Ratio mean±SD | AP% mean±SD | Source selector |
|---|---:|---|---|---|
| sg_ga | 400 | 1.0264773442318016±0.0031427338202957527 | 26.28113141012219±0.21968884081359505 | `outputs/x1_500img_20261018/analysis.json:methods[name=sg_ga,budget=400]`; raw evaluation cùng tên/seed/q,selector như trên |
| sg_ga | 1000 | 1.0056867401009337±0.013648560518441896 | 34.60223944598327±0.7690738231452926 | `outputs/x1_500img_20261018/analysis.json:methods[name=sg_ga,budget=1000]`; raw evaluation cùng tên/seed/q,selector như trên |
| sg_ga | 2500 | 1.0267866513471344±0.007378131407361161 | 26.198581704676236±0.2017095986670433 | `outputs/x1_500img_20261018/analysis.json:methods[name=sg_ga,budget=2500]`; raw evaluation cùng tên/seed/q,selector như trên |
| ga_center | 400 | 1.0502027890735455±0.00604425098978661 | 24.692365126921604±0.13935182986789724 | `outputs/x1_500img_20261018/analysis.json:methods[name=ga_center,budget=400]`; raw evaluation cùng tên/seed/q,selector như trên |
| ga_center | 1000 | 1.004417885022108±0.00657998310679356 | 33.92781558278314±0.4720598289828205 | `outputs/x1_500img_20261018/analysis.json:methods[name=ga_center,budget=1000]`; raw evaluation cùng tên/seed/q,selector như trên |
| ga_center | 2500 | 1.0561217494657946±0.012286505419326044 | 24.607030339549812±0.11870825973535946 | `outputs/x1_500img_20261018/analysis.json:methods[name=ga_center,budget=2500]`; raw evaluation cùng tên/seed/q,selector như trên |
| ga_random_location | 400 | 1.0630669385832687±0.012080220830499037 | 27.329500674026143±0.441886629802365 | `outputs/x1_500img_20261018/analysis.json:methods[name=ga_random_location,budget=400]`; raw evaluation cùng tên/seed/q,selector như trên |
| ga_random_location | 1000 | 1.0345038713195074±0.019541416191485677 | 35.19747249608921±1.4600891147114534 | `outputs/x1_500img_20261018/analysis.json:methods[name=ga_random_location,budget=1000]`; raw evaluation cùng tên/seed/q,selector như trên |
| ga_random_location | 2500 | 1.0706513905176493±0.014321394225359135 | 27.329344773757047±0.41266246139047447 | `outputs/x1_500img_20261018/analysis.json:methods[name=ga_random_location,budget=2500]`; raw evaluation cùng tên/seed/q,selector như trên |
| random_search | 400 | 1.0270814356507476±0.005487366532035916 | 26.163377005820763±0.17481159058776588 | `outputs/x1_500img_20261018/analysis.json:methods[name=random_search,budget=400]`; raw evaluation cùng tên/seed/q,selector như trên |
| random_search | 1000 | 0.9938053738292203±0.013221226242583066 | 34.90691170082244±0.6972049057407287 | `outputs/x1_500img_20261018/analysis.json:methods[name=random_search,budget=1000]`; raw evaluation cùng tên/seed/q,selector như trên |
| random_search | 2500 | 1.0250448878199405±0.004025170331286743 | 26.27797283621106±0.09810863809506686 | `outputs/x1_500img_20261018/analysis.json:methods[name=random_search,budget=2500]`; raw evaluation cùng tên/seed/q,selector như trên |
| area_1 | 400 | 1.030770077150257±0.004732242828677237 | 29.068946299974108±0.12869108812020266 | `outputs/x1_500img_20261018/analysis.json:methods[name=area_1,budget=400]`; raw evaluation cùng tên/seed/q,selector như trên |
| area_2 | 400 | 1.0311574269958839±0.004937577475479848 | 27.911716553850933±0.0843852789315413 | `outputs/x1_500img_20261018/analysis.json:methods[name=area_2,budget=400]`; raw evaluation cùng tên/seed/q,selector như trên |
| area_8 | 400 | 1.02254785547774±0.010419511578742973 | 23.308447909445913±0.20362627562122096 | `outputs/x1_500img_20261018/analysis.json:methods[name=area_8,budget=400]`; raw evaluation cùng tên/seed/q,selector như trên |
| area_16 | 400 | 0.9965057976408446±0.01705672135681638 | 18.193642372526757±0.09674798172494574 | `outputs/x1_500img_20261018/analysis.json:methods[name=area_16,budget=400]`; raw evaluation cùng tên/seed/q,selector như trên |
| eot_none | 400 | 1.0309208375956296±0.008189493444205002 | 26.192659207195135±0.194627617585728 | `outputs/x1_500img_20261018/analysis.json:methods[name=eot_none,budget=400]`; raw evaluation cùng tên/seed/q,selector như trên |
| eot_no_rotation | 400 | 1.033121630159377±0.003534248944367667 | 26.256734805363063±0.11986125169864183 | `outputs/x1_500img_20261018/analysis.json:methods[name=eot_no_rotation,budget=400]`; raw evaluation cùng tên/seed/q,selector như trên |
| eot_no_color | 400 | 1.0249454765646402±0.0071320841214272705 | 26.241293689199285±0.1706573742402324 | `outputs/x1_500img_20261018/analysis.json:methods[name=eot_no_color,budget=400]`; raw evaluation cùng tên/seed/q,selector như trên |
| eot_no_blur | 400 | 1.0247465921963956±0.005853325886899712 | 26.214910239326773±0.1432780374843267 | `outputs/x1_500img_20261018/analysis.json:methods[name=eot_no_blur,budget=400]`; raw evaluation cùng tên/seed/q,selector như trên |
| eot_no_noise | 400 | 1.028472388044364±0.006885706569294425 | 26.19303534810754±0.15085809149775856 | `outputs/x1_500img_20261018/analysis.json:methods[name=eot_no_noise,budget=400]`; raw evaluation cùng tên/seed/q,selector như trên |
| eot_four_draws | 400 | 1.0271903934861542±0.008872583069966779 | 26.212698173181764±0.16029718656855146 | `outputs/x1_500img_20261018/analysis.json:methods[name=eot_four_draws,budget=400]`; raw evaluation cùng tên/seed/q,selector như trên |
| adaptive_cap100 | 400 | 1.0269155229634788±0.008636896489017023 | 26.221095801993442±0.14289493224709277 | `outputs/x1_500img_20261018/analysis.json:methods[name=adaptive_cap100,budget=400]`; raw evaluation cùng tên/seed/q,selector như trên |
| tanh_whitebox_patch | 400 | 1.1987159430195207±0.03800431454600541 | 25.577150323887544±0.3305303776629562 | `outputs/x1_500img_20261018/analysis.json:methods[name=tanh_whitebox_patch,budget=400]`; raw evaluation cùng tên/seed/q,selector như trên |

Diện tích phần trăm tính trực tiếp size²/320²×100; 45px=1.9775390625%,90px=7.91015625%. EOT independent full q400:−20.13466523736715±1.4069041717666746, nguồn X1 analysis.independent_eot (name=sg_ga,budget400), raw evaluation/eot_sg_ga_seed0..9_q400.json, trung bình samples[].difference theo8ảnh×16draws rồi giữa seed. Hình bitmap EOT giữ nhãnOLD128, không thay số pixel thành X1.

## Build và kiểm tra bàn giao

ĐANG KIỂM TRA compiler tích hợp. Repo lớn bị từ chối, nên tạo bản sao chỉ paper/supporting files trong REVIEW/06_latex_build/before và after. Lượt before trả `Compilation timed out`; Docker client29.6.2 có sẵn nhưng daemon không kết nối được; không có pdflatex/xelatex/lualatex/latexmk/tectonic trong PATH. Không cài gói hệ thống. Số trang/warnings sẽ cập nhật theo kết quả cuối; không coi timeout là compilation success.

## Git diff --stat của nhánh (tracked, bao gồm dirty có trước)

V2 và REVIEW mới là untracked, không tự stage để làm diff trông như đã commit. Các thay đổi tracked bên dưới không phải các sửa code của nhiệm vụ này.

```text
BaoCaoKhoaHocAdversarialAttacks_Q1_VI.tex | 1142 ++++++++---------------------
 README.md                                 |   36 +-
 README.vi.md                              |   36 +-
 core/victim_model.py                      |   16 +-
 experiments/extended_analysis.py          |    3 +-
 experiments/extended_validation.py        |    8 +-
 experiments/local_q1_validation.py        |   13 +-
 experiments/multi_seed_experiment.py      |   15 +-
 experiments/random_search.py              |   10 +
 9 files changed, 417 insertions(+), 862 deletions(-)
```

So riêng original→v2 bằng `git diff --no-index --stat` để thấy delta bản thảo:

```text
...=> BaoCaoKhoaHocAdversarialAttacks_Q1_VI_v2.tex | 361 ++++++++++++++-------
 1 file changed, 238 insertions(+), 123 deletions(-)
```

## Sửa bổ sung từ kiểm tra chéo

- Chiều chênh lệch Phantom: đổi nhãn thành **Phantom trừ SG-GA**; không đổi số. Nguồn `outputs/extended_q1_20261002/phantom_local/summary.json:comparisons[0].local_reference_minus_sg400`, mean−.0016224979, CI[−.0053951007,.0019365961]. Bản cũ/v2 nháp đã gọi ngược chiều.
- Mã giả thêm tiền điều kiện mọi mốc dương/chia hết4m theo `extended_validation.py:155–157`; thế hệ khởi tạo chưa có elite.
- Synthetic warm-up: năm lời gọi N=100 một lần trước toàn sweep, không phải warm-up riêng từngN (`benchmark_hardware.py:45–48`).

Compiler tích hợp dùng Tectonic/XeTeX, không phải pdfLaTeX. Lượt after đầu tiên dừng ở `\DeclareUnicodeCharacter` (macro chỉ có với inputenc/pdfLaTeX); chưa xuất trang. Sửa tương thích số1: bọc khai báo gốc trong `\ifdefined`, giữ CAS/T5/babel và nhãn Việt hóa; không cài gói hệ thống. Các cảnh báo font T5/stix, inputenc ignored và hyphenation Vietnamese đã xuất hiện, chưa phải build thành công.

## Rà chuỗi trung gian (trước bổ sung compatibility/layout; xem bảng cuối để lấy dòng giao)

Dòng dưới là vị trí source v2 sau sửa; đếm cả vùng bị tắt, ghi rõ visible/disabled. Phép tìm nhận diện cả dấu phẩy LaTeX `{,}`.

| Chuỗi | Dòng / trạng thái | Lý do mọi kết quả còn lại |
|---|---|---|
| `máy chủ biên` | 246 disabled/preamble | Chỉ giữ nguyên nội dung nhánh B đã tắt; không là claim thiết bị thật. |
| `Edge Server` | 0 kết quả | Không được giữ trong title/shorttitle. |
| `tám kiến trúc` | 0 kết quả | Danh sách X2 đổi thành tám detector với boundary rõ. |
| `1,02` | 82 visible, 82 visible, 323 visible, 329 visible, 332 visible, 335 visible, 338 visible, 390 visible, 391 visible, 403 visible, 406 visible, 407 visible, 408 visible, 409 visible, 512 visible, 512 visible, 528 visible, 529 visible, 550 visible, 551 visible, 552 visible, 566 visible, 725 visible | Tiền tố các ratio đã dẫn nguồn (không phải khoảng cũ 1,02–1,24). |
| `1,24` | 0 kết quả | Không còn khoảng sai1,02–1,24. |
| `RT-DETR` | 545 visible | Câu phủ định: không có kết quả RT-DETR trong X2. |
| `1,199` | 0 kết quả | Không dùng rounding gây trộn cohort; tanh ghi1,1987@500. |
| `tái lập từng` | 0 kết quả | Đã thay bằng kiểm tổng hợp artifacts, không claim inference replay. |
| `không phụ thuộc mạnh` | 0 kết quả | Đã bỏ inference architecture-independence. |
| `Nguyên nhân nằm` | 0 kết quả | Đã bỏ causal attribution fitness. |
| `container` | 0 kết quả | Không dùng container làm bằng chứngresource. |
| `primary` | 339 visible | Nếu còn thì chỉ trong nội dung B bị tắt; visible dùng so sánh chính. |
| `0,1504` | 82 visible, 286 visible, 304 visible, 323 visible, 723 visible | p của OLD128, luôn ở đoạn đã nêu cohort. |
| `−0,45` | 0 kết quả | Đã sửa dz thành−.4984. |
| `Hình 7` | 0 kết quả | Đã bỏ camera figure; số hình tự đổi theo LaTeX labels. |

Static labels/refs: 20 labels, duplicate=0, unresolved targets=0; citation keys thiếu=0. Đây là kiểm source, không thay kiểm undefined-reference sau build. Tất cả8includegraphics (gồm2của nhánhB tắt) tồn tại qua graphicspath. Algorithm*1, lưu đồTikZ1; hai panel candidate và một plotX2 là PGFPlots native, không overwrite hình cũ.

Sửa build số2: bổ sung bản sao `thumbnails/*` mà CAS dùng (lỗi thiếu cas-email.jpeg không phải hình scientific). XeTeX bỏ qua inputenc, T5 8-bit không nhận Unicode tiếng Việt nên thêm nhánh fontspec/TU **chỉ cho XeTeX**, dùng TeX Gyre qua tên file; đường pdfLaTeX giữ T5/babel và các nhãn gốc. Không chấp nhận PDF mất dấu tiếng Việt là build đạt.

## Tra số bổ sung cho kiểm định và X2

| So sánh X1 (SG trừ comparator) | Mean | CI95% | p exact | p Holm | Selector |
|---|---:|---|---:|---:|---|
| sg_ga_q2500_minus_ga_center_q2500 | -0.029335098118660065 | [-0.03832823790339332, -0.021598326633977788] | 0.001953125 | 0.029296875 | `outputs/x1_500img_20261018/analysis.json:secondary_holm_family[comparison=sg_ga_q2500_minus_ga_center_q2500]`; raw evaluation theo tên/seed/q cùng filter |
| sg_ga_q2500_minus_ga_random_location_q2500 | -0.04386473917051496 | [-0.05451467454218171, -0.03384820834655482] | 0.001953125 | 0.029296875 | `outputs/x1_500img_20261018/analysis.json:secondary_holm_family[comparison=sg_ga_q2500_minus_ga_random_location_q2500]`; raw evaluation theo tên/seed/q cùng filter |
| sg_ga_q2500_minus_random_search_q2500 | 0.001741763527193907 | [-0.0026979027523237873, 0.006405325132177353] | 0.5 | 1.0 | `outputs/x1_500img_20261018/analysis.json:secondary_holm_family[comparison=sg_ga_q2500_minus_random_search_q2500]`; raw evaluation theo tên/seed/q cùng filter |
| sg_ga_q400_minus_area_1_q400 | -0.004292732918455245 | [-0.007573558520499993, -0.0012209100423281605] | 0.033203125 | 0.33203125 | `outputs/x1_500img_20261018/analysis.json:secondary_holm_family[comparison=sg_ga_q400_minus_area_1_q400]`; raw evaluation theo tên/seed/q cùng filter |
| sg_ga_q400_minus_area_2_q400 | -0.00468008276408185 | [-0.00867332096993495, -0.0010244102687800183] | 0.048828125 | 0.439453125 | `outputs/x1_500img_20261018/analysis.json:secondary_holm_family[comparison=sg_ga_q400_minus_area_2_q400]`; raw evaluation theo tên/seed/q cùng filter |
| sg_ga_q400_minus_area_8_q400 | 0.0039294887540617385 | [-0.0027689235884612363, 0.010181162296929074] | 0.283203125 | 1.0 | `outputs/x1_500img_20261018/analysis.json:secondary_holm_family[comparison=sg_ga_q400_minus_area_8_q400]`; raw evaluation theo tên/seed/q cùng filter |
| sg_ga_q400_minus_area_16_q400 | 0.02997154659095741 | [0.020030296466094916, 0.039452826356149426] | 0.001953125 | 0.029296875 | `outputs/x1_500img_20261018/analysis.json:secondary_holm_family[comparison=sg_ga_q400_minus_area_16_q400]`; raw evaluation theo tên/seed/q cùng filter |
| sg_ga_q400_minus_eot_none_q400 | -0.004443493363827766 | [-0.008767382371839721, -0.0005920249599089046] | 0.08203125 | 0.65625 | `outputs/x1_500img_20261018/analysis.json:secondary_holm_family[comparison=sg_ga_q400_minus_eot_none_q400]`; raw evaluation theo tên/seed/q cùng filter |
| sg_ga_q400_minus_eot_no_rotation_q400 | -0.0066442859275750886 | [-0.009746555339447039, -0.0033678926062829964] | 0.009765625 | 0.107421875 | `outputs/x1_500img_20261018/analysis.json:secondary_holm_family[comparison=sg_ga_q400_minus_eot_no_rotation_q400]`; raw evaluation theo tên/seed/q cùng filter |
| sg_ga_q400_minus_eot_no_color_q400 | 0.0015318676671618903 | [-0.0029280345449098945, 0.005743914981606623] | 0.51171875 | 1.0 | `outputs/x1_500img_20261018/analysis.json:secondary_holm_family[comparison=sg_ga_q400_minus_eot_no_color_q400]`; raw evaluation theo tên/seed/q cùng filter |
| sg_ga_q400_minus_eot_no_blur_q400 | 0.00173075203540618 | [-0.002629900889205427, 0.006117005702746632] | 0.466796875 | 1.0 | `outputs/x1_500img_20261018/analysis.json:secondary_holm_family[comparison=sg_ga_q400_minus_eot_no_blur_q400]`; raw evaluation theo tên/seed/q cùng filter |
| sg_ga_q400_minus_eot_no_noise_q400 | -0.0019950438125620586 | [-0.007221874434489794, 0.0025915008692990477] | 0.4921875 | 1.0 | `outputs/x1_500img_20261018/analysis.json:secondary_holm_family[comparison=sg_ga_q400_minus_eot_no_noise_q400]`; raw evaluation theo tên/seed/q cùng filter |
| sg_ga_q400_minus_eot_four_draws_q400 | -0.0007130492543520273 | [-0.005664584132256778, 0.0038046205384575727] | 0.78515625 | 1.0 | `outputs/x1_500img_20261018/analysis.json:secondary_holm_family[comparison=sg_ga_q400_minus_eot_four_draws_q400]`; raw evaluation theo tên/seed/q cùng filter |
| sg_ga_q400_minus_adaptive_cap100_q400 | -0.0004381787316767749 | [-0.00767570575183453, 0.005216673493629415] | 0.908203125 | 1.0 | `outputs/x1_500img_20261018/analysis.json:secondary_holm_family[comparison=sg_ga_q400_minus_adaptive_cap100_q400]`; raw evaluation theo tên/seed/q cùng filter |
| sg_ga_q400_minus_tanh_whitebox_patch_q400 | -0.1722385987877188 | [-0.19515723283887834, -0.15176514802131005] | 0.001953125 | 0.029296875 | `outputs/x1_500img_20261018/analysis.json:secondary_holm_family[comparison=sg_ga_q400_minus_tanh_whitebox_patch_q400]`; raw evaluation theo tên/seed/q cùng filter |

| X2 detector | Images | Boundary | Ratio | File:selector |
|---|---:|---|---:|---|
| yolov8n | 100 | pre_nms_head | 1.034332240167192 | `outputs/x2_architecture_20261020/yolov8n.json:images,boundary,pooled_mean_ratio`; per_seed seed0..4; records[].clean/seed*.active_candidates |
| yolov8s | 100 | pre_nms_head | 1.0261953681683476 | `outputs/x2_architecture_20261020/yolov8s.json:images,boundary,pooled_mean_ratio`; per_seed seed0..4; records[].clean/seed*.active_candidates |
| yolo11n | 100 | pre_nms_head | 1.0259116222646463 | `outputs/x2_architecture_20261020/yolo11n.json:images,boundary,pooled_mean_ratio`; per_seed seed0..4; records[].clean/seed*.active_candidates |
| yolo11s | 64 | pre_nms_head | 1.0214588472530495 | `outputs/x2_architecture_20261020/yolo11s.json:images,boundary,pooled_mean_ratio`; per_seed seed0..4; records[].clean/seed*.active_candidates |
| yolov12n | 64 | pre_nms_head | 1.036032440025616 | `outputs/x2_architecture_20261020/yolov12n.json:images,boundary,pooled_mean_ratio`; per_seed seed0..4; records[].clean/seed*.active_candidates |
| fasterrcnn | 64 | post_module_detections | 1.110743449429335 | `outputs/x2_architecture_20261020/fasterrcnn.json:images,boundary,pooled_mean_ratio`; per_seed seed0..4; records[].clean/seed*.active_candidates |
| retinanet | 64 | post_module_detections | 1.2356262624141319 | `outputs/x2_architecture_20261020/retinanet.json:images,boundary,pooled_mean_ratio`; per_seed seed0..4; records[].clean/seed*.active_candidates |
| ssdlite | 64 | post_module_detections | 1.0339737975420094 | `outputs/x2_architecture_20261020/ssdlite.json:images,boundary,pooled_mean_ratio`; per_seed seed0..4; records[].clean/seed*.active_candidates |

Các số budget32: `outputs/x1_500img_20261018/analysis.json:same_image_budget_curves[name=sg_ga,budget=400/1000/2500].statistics.mean` lần lượt1.0004409001194488/1.0056867401009337/.9954181896265695. Mẫu chung32ID nên không nối với mean500ảnh. Nguồn raw: cùng các evaluation files, restrict32imageIDs nhỏ nhất.

Giới hạn vật lý đã rút lại thành ba câu (không print-and-camera/ARM/energy; EOT phần mềm chưa calibration; không thay nghiên cứu physical bằng tensor), ngoài hai câu ở mục quan sát vật lý. Các số section/table/figure có thể tự đổi khi tắt mục6 và thêm bảng X1/X2; v2 dùng label/ref thay số tham chiếu cứng.

Sửa layout số3 sau chẩn đoán: shorttitle rút gọn; công thức(1)/(3) chia dòng bằng aligned; đường dẫn dài dùng path có ngắt dòng; boundary post_module_detections có điểm ngắt; bullets thống kê tách dòng, danh sách N có allowbreak. Không thay giá trị số. Probe ban đầu cho14trang trước/13trang sau ở pass đầu, có undefined refs do cố ý dừng trước rerun; sẽ kiểm counter lại sau pass2, không gọi các cảnh báo pass1 là lỗi tham chiếu cuối cùng.

## Kết quả kiểm cuối cùng (thay trạng thái ĐANG KIỂM TRA phía trên)

**Biên dịch v2: SUCCESS**, compiler tích hợp Tectonic/XeTeX, trên `REVIEW/06_latex_build/after/main.tex`, khớp byte với bản v2 root. Không cài hệ thống, không chạy model. Hai lần sửa tương thích và một lần sửa layout; không đổi CAS class/style gốc.

**Số trang: trước14 → sau13**, cùng engine/font compatibility. Số trang lấy sau khi flush floats và pass2 qua các bản probe riêng; probe cố ý dừng bằng `PAPER-AUDIT-COMPLETED-PAGES`, không phải bản giao. Bản before chỉ thêm compatibility để engine đọc được template; không thay body, original file nguyên trạng. Source v2 giao không chứa diagnostic errmessage.

Diagnostic pass2 không thấy undefined reference/citation; kiểm static cũng0missing targets và0missing citation keys. Không có main image thiếu file:8includegraphics tồn tại (2ảnh thuộcB tắt), vàCAS thumbnails đã copy vào staging. Không coi đây là visual QA hoàn chỉnh vì chưa có raster/PDF export để xem từng trang.

**Warnings còn lại:** Overfull123.62721pt tại maketitle kế thừa cảbefore/after; v2 còn10.28891pt,5.75583pt,8.0789pt,16.97978pt ở các đoạn dài. Cảnh báo glyphU+009D vẫn xuất hiện; không tuyên bố camera-ready hoặc hết lỗi font. Nhiều Underfull ở bảng4cột. Công thức/đường dẫn đã giảm các tràn lớn31/52/97/104pt được phát hiện ở bản nháp. Xem `REVIEW/06_latex_build/{before_probe,after_probe}/compiler_diagnostic.log` (diagnostic tool có giới hạn độ dài).

**PDF:** compiler xác nhận thành công và đã mở project `after/` để xem preview. Tool compile không exportPDF; workspace không có filePDF mới. Không có TeXCLI trongPATH, Docker daemon không chạy; connector DocumentControl không có session để export. Vì vậy chưa bàn giao được PDF local và chưa kiểm hình rendered từng trang. Không tải bản thảo lên dịch vụ ngoài để khắc phục.

### Grep cuối trên đúng source giao

| Chuỗi | Dòng v2 / trạng thái | Lý do còn lại |
|---|---|---|
| `máy chủ biên` | 259 tắt/preamble | Nội dung B cũ giữ trong vùng tắt; không phải claim thiết bị thật. |
| `Edge Server` | 0 kết quả | Đã bỏ khỏi title/shorttitle. |
| `tám kiến trúc` | 0 kết quả | Đã thay bằng tám detector và boundary rõ. |
| `1,02` | 92 visible, 92 visible, 338 visible, 344 visible, 347 visible, 350 visible, 353 visible, 405 visible, 406 visible, 418 visible, 421 visible, 422 visible, 423 visible, 424 visible, 527 visible, 527 visible, 543 visible, 544 visible, 565 visible, 566 visible, 567 visible, 581 visible, 740 visible | Tiền tố của ratio đã dẫn nguồn, không phải khoảng cũ1,02–1,24. |
| `1,24` | 0 kết quả | Không giữ khoảng sai1,02–1,24. |
| `RT-DETR` | 560 visible | Chỉ câu phủ định không có kết quả X2. |
| `1,199` | 0 kết quả | Dùng1,1987@X1-500 có nhãn cohort. |
| `tái lập từng` | 0 kết quả | Đã thay bằng kiểm tổng hợp, không inference replay. |
| `không phụ thuộc mạnh` | 0 kết quả | Không giữ kết luận architecture-independence. |
| `Nguyên nhân nằm` | 0 kết quả | Đã bỏ causal attribution. |
| `container` | 0 kết quả | Không dùng để chứng minh resource profile. |
| `primary` | 354 visible | Visible dùng tiếng Việt; nếu còn trong vùng tắt là nội dung gốc. |
| `0,1504` | 92 visible, 299 visible, 319 visible, 338 visible, 738 visible | p của OLD128, đã chỉ rõ cohort hoặc lịch sử mở rộng. |
| `−0,45` | 0 kết quả | Đã sửa dz−.4984. |
| `Hình 7` | 0 kết quả | Camera figure đã bỏ; numbering tự cập nhật. |

V2 SHA256: `ec23513a02ad427717b892d855581584e0078ccf256e77622b56dcb2f04730de`; original SHA256 vẫn `a602b4422842a2e56a7bb8994dd5b4274649a64f22ecbefbbb10d1a2353c1eb5`. Branch hiện tại: `paper/q1-fixes`. Không commit hoặc tự stage; code/data ngoài scope không được ghi bởi nhiệm vụ này.

### Diff bản thảo cuối (original→v2, không tính dirty có trước)

```text
...=> BaoCaoKhoaHocAdversarialAttacks_Q1_VI_v2.tex | 381 ++++++++++++++-------
 1 file changed, 257 insertions(+), 124 deletions(-)
```

## Bổ sung sim-results (phiên 21/10 tối, nhánh harness/step1)

Chèn hai subsection mới vào v2 giữa §5.4 (backend NMS) và §5.5 (dịch vụ): "Giao thức đo ghim core và hiệu chỉnh A/A" (tab:aa) và "Proxy số ứng viên và độ trễ: phụ thuộc điều kiện". Sửa §7.2, §7.3, Kết luận RQ1, Hướng tương lai cho nhất quán. SHA256 v2: trước splice `ec23513a02ad427717b892d855581584e0078ccf256e77622b56dcb2f04730de`; sau splice+4 sửa `6e73a5589c7e959e3b071cf2fc405187d2e2792797ffb699a213a46c7e755aa3`. Bản sao trước splice: `REVIEW/06_latex_build/draft_sim_results/v2_before_splice.tex`.

Nhãn: E5 = confirmatory (PREREG_E5, tag `prereg-e5-20261021`). R1/R2/R3/E2a = THĂM DÒ/POST-HOC (ghi rõ trong bài). Tất cả là phân tích dữ liệu đã lưu, KHÔNG đo/inference/COCOeval mới.

Kiểm cú pháp: khối mới compile sạch bằng xelatex + wrapper tối giản (`REVIEW/06_latex_build/draft_sim_results/scfresh.tex` → `build/scfresh.pdf`, 2 trang, exit 0). PDF toàn bài CHƯA xuất được: thiếu `t5enc.def` trong TeX Live máy (không cài gói/không mạng — quy tắc 7). Overfull nhỏ 9,76pt ở đoạn R2 (cần soát layout lần cuối, cùng loại với các tràn đã ghi ở 06_open_items).

| Số trong bài (mới) | File:selector | Phép gộp |
|---|---|---|
| A/A tab:aa P1: total 0,9960 [0,9920;1,0000] MDE 0,59%; forward 1,0002 [0,9963;1,0042] MDE 0,58%; NMS thuần 1,0006 [0,9935;1,0080] MDE 1,07%; NMS tv 0,9948 [0,9867;1,0029] MDE 1,18% | `sponge-sim/results/e5/20261021T151412/summary.json:profiles.P1.stages.<stage>.{aa_ratio,aa_ci95_ratio,mde_ratio_pct}` | A/A log-ratio, bootstrap seed 20261021; MDE 80% công suất |
| A/A E1: total 1,0005 [0,9919;1,0092] MDE 1,27%; forward 1,0081 [0,9953;1,0220] MDE 1,94%. E4: total 0,9875 [0,9476;1,0279] MDE 6,13%; NMS thuần 0,9758 [0,9531;0,9984] MDE 3,47% | `...e5/...summary.json:profiles.{E1,E4}.stages.<stage>` | như trên |
| Tỷ phần NMS thuần/total (sạch) trung vị: P1 2,1%, E1 3,0%, E4 4,0%; cực đại 19–32% | `...e5/...summary.json:profiles.<P>.nms_torch_pure_share_of_total.{median,max}` | trung vị/max theo ảnh |
| 2/21 CI không chứa 1 (P1 total, E4 NMS thuần) | `...e5/...summary.json:profiles.<P>.stages.<stage>.aa_ci_contains_1` | đếm |
| R1 X1-500 SG−tâm two-level [−0,0580;−0,0024]; OLD128 [−0,0466;+0,0379]; SG−tìm kiếm ngẫu nhiên [−0,0038;+0,0074]; SG−vị trí ngẫu nhiên [−0,0889;−0,0124]; 54,2% ảnh âm | `sponge-sim/results/r1/20261021T183505/summary.json:cohorts.<C>.comparisons.<cmp>.ci95_two_level` + `.frac_images_mean_diff_negative` | bootstrap hai tầng (ảnh×seed) 20k, seed 20261021 |
| R1 độ rộng CI two-level / seed: X1-500 ×3,35; OLD128 ×7,032 | `...r1/...summary.json:cohorts.<C>.comparisons.<cmp>.width_ratio_two_level_over_seed_only` | tỷ lệ độ rộng CI (trường lưu sẵn) |
| R2 custom τ=0,01 cap None: median NMS 1,641 ms; ρ(N,t) 0,865 [0,692;0,923]. torchvision: 0,0579 ms; ρ 0,603 [0,463;0,692]. Tỷ số ≈28× (1,641/0,0579) | `sponge-sim/results/r2/20261021T183715/summary.json:backend_cells.{custom\|0.01\|None,torchvision\|0.01\|None}.{median_nms_ms,rho_N_t,rho_N_t_ci95_cluster_image}` | trung vị; Spearman cụm theo ảnh |
| R2 tỷ phần hậu xử lý/total trung vị 3,4% (1 luồng); ρ(N,total) 0,327 [0,167;0,458]; 0/2400 >300 ms | `...r2/...summary.json:timing.threads1.{postprocess_share_of_total.median,rho_N_total,rho_N_total_ci95_cluster_image,late_over_300ms,n_records}` | như trên |
| R3 Overload: N 42→5490, ratio N 349,0 [119,7;746,3]; pp 3,18 [2,80;3,58]; total 1,022 [1,002;1,039]; forward 0,992 [0,972;1,009]; ρ(N,pp) 0,836; ρ(N,total) 0,038 | `sponge-sim/results/r3/20261021T184159/summary.json:methods.overload.*` | trung vị N; two-level CI 20k; Spearman pooled |
| R3 Phantom: N 42→4365, ratio N 308,2 [94,8;675,9]; pp 3,27 [2,84;3,72]; total 1,056 [1,024;1,099]; ρ(N,pp) 0,816; ρ(N,total) 0,086 | `...r3/...summary.json:methods.phantom_sponges.*` | như trên |
| E2a between-image ρ 0,938 [0,922;0,950] (sạch, thuần); within-image ρ_dN_dt ≈0,12 (4 case); không đảo dấu Simpson | `sponge-sim/results/e2a/20261021T145544/summary.json:{between_image_clean.rho/ci95, within_image.<case>.rho_dN_dt, simpson_check}` | Spearman |
| E2a A/A share 0,044 [−0,015;0,137] chồng lấn attack share (ga_center 0,128 [0,034;0,235]) | `...e2a/.../posthoc_aa.json:{AA_clean_shift1.mean/ci95_mean, ga_center.mean/ci95_mean}` | POST-HOC (DEVIATIONS.md) |

## Phiên 21/10 tối (tiếp) — tóm tắt, đóng góp, hình R3
SHA256 v2 sau các sửa này: `267b383667ae96ddd3a9449fa64278fe6fa7f44941bee4ea50bfe0a7f69585a2`. Bản trước sửa tóm tắt: `REVIEW/06_latex_build/draft_sim_results/v2_before_abstract.tex`.

| Thay đổi | Vị trí | Nguồn số / selector |
|---|---|---|
| Tóm tắt: thêm 1 câu về giao thức ghim core + A/A (MDE total 0,59%) + biến thể tham chiếu N×~300 → total +2–6% | `\begin{abstract}` | như bảng sim-results (E5 P1 total mde_ratio_pct; R3 methods.*.ratio_total) |
| Đóng góp 3 (§1.3): nêu ghim core + A/A + MDE + bootstrap hai tầng + N tách khỏi độ trễ toàn trình | §1.3 | R2/R3/E5 selectors đã liệt kê |
| Hình mới `fig:r3decouple`: tỷ số N vs hậu xử lý vs toàn trình (log, CI hai tầng), Overload/Phantom | §5.6, sau đoạn R3 | `sponge-sim/results/r3/20261021T184159/summary.json:methods.<m>.{ratio_N,ratio_pp,ratio_total}.{mean,ci95_two_level}` |
| PNG `paper_assets_20261013/fig_r3_ratio_decoupling.png` (trong graphicspath); script `REVIEW/06_latex_build/draft_sim_results/make_fig_r3.py` | — | sinh từ summary.json, không đo mới |

---
## Bổ sung 2026-10-21 tối (4): Related Work nền tảng + bảng so sánh + references.bib

Phạm vi: CHỈ thêm nội dung tổng quan/trích dẫn và một bảng so sánh ĐỊNH TÍNH. KHÔNG thêm/sửa số đo,
KHÔNG chạy inference/COCOeval/thống kê mới. Mọi số liệu thực nghiệm giữ nguyên như các mục trên.

### Thêm vào bản thảo (v2)
- §2 đổi tiêu đề → "Nghiên cứu liên quan"; thêm subsection nền tảng (lineage 2017–2024).
- Bảng `tab:prior_attacks` (table*): định vị Sponge Patch với Sponge Examples, NICGSlowDown, Daedalus,
  Phantom Sponges, Overload, SlowTrack, Adversarial Patch, DPatch, Thys. Các ô là mô tả cơ chế/mối đe dọa
  theo công trình gốc; KHÔNG trích số định lượng, KHÔNG so hiệu lực xuyên mối đe dọa.
- §1.3 thêm 1 đoạn "tính mới" (3 điểm), dẫn `\ref{tab:prior_attacks}`. Không tuyên bố tấn công mạnh hơn.

### Nguồn trích dẫn mới (arXiv ID xác minh qua web 2026-10-21)
| key | công trình | nơi/năm | arXiv |
|---|---|---|---|
| sponge2021 | Sponge Examples (Shumailov và cs.) | EuroS&P 2021 | 2006.03463 |
| nicgslowdown2022 | NICGSlowDown (Simin Chen và cs.) | CVPR 2022 | 2203.15859 |
| daedalus2021 | Daedalus (Derui Wang và cs.) | IEEE TCYB 2022 | 1902.02067 |
| phantom2023 | Phantom Sponges (Shapira và cs.) | WACV 2023 | 2205.13618 |
| overload2024 | Overload (Erh-Chung Chen và cs.) | CVPR 2024 | 2304.05370 |
| slowtrack2024 | SlowTrack (Chen Ma và cs.) | AAAI 2024 | 2312.09520 |
| advpatch2017 | Adversarial Patch (Brown và cs.) | NeurIPS-W 2017 | 1712.09665 |
| dpatch2019 | DPatch (Xin Liu và cs.) | AAAI-W 2019 | 1806.02299 |
| thys2019 | Thys và cs. (person patch) | CVPR-W 2019 | 1904.08653 |

### references.bib
- 31 mục = 22 mục gốc (chép nguyên theo thebibliography của bản thảo) + 9 mục nền tảng trên.
- Cảnh báo giữ nguyên: 2 mục arXiv 2026 (trackflood2026 arXiv:2609.33948, ebt2026 arXiv:2607.09115) CHƯA xác minh;
  một số số trang 2025–2026 của các mục gốc chưa đối chiếu độc lập. Cần tác giả rà trước khi nộp.

### Kiểm cấu trúc (xelatex VM, trước lỗi gói)
- table* 15/15, figure* 11/11, tabularx 15/15; `$` chẵn (962); không label trùng; 31 bibitem khớp hết \cite; 9/9 ảnh resolve.
- Không build được PDF trong VM: thiếu t5enc.def (vntex), babel-vietnamese, algorithm.sty. Build trên Windows.
- v2.tex SHA256 = 997786f947a0773d9c14dce26185b03136405fb7f0fdd17a5be5f05059f714a0

---
## Sửa 2026-10-21 tối (5): cắt trích dẫn >4 năm + đổi giọng câu DoS (theo yêu cầu tác giả)
- Related Work: viết lại mục "dòng tấn công cạn kiệt tài nguyên" chỉ dùng công trình ≤4 năm. BỎ khỏi bảng tab:prior_attacks + mục nền tảng + bibitem + references.bib: Sponge Examples 2021, Daedalus 2019/22, Adversarial Patch 2017, DPatch 2019, Thys 2019. GIỮ: NICGSlowDown 2022, Phantom Sponges 2023, Overload 2024, SlowTrack 2024 (+ dòng Sponge Patch). bibitem 31→26.
- Dòng miếng dán trong mục này nay dẫn các ref gần đây đã có trong bài (apde2025, pbcat2025, iap2025, badpatch2025).
- Tóm tắt: câu "Chưa có thiết bị edge/ARM... chưa xác lập DoS" → đổi sang giọng PHẠM VI ("nghiên cứu cục bộ/mô phỏng; DoS edge thật ngoài phạm vi, hướng phát triển"). Giữ đúng sự thật (không tuyên bố DoS). Item kết quả cohort cũng reword tương tự. CÁC câu hạn chế trong §Thảo luận/Hạn chế GIỮ NGUYÊN (reviewer Q1 yêu cầu phần limitations trung thực).
- Phần nhiều-model (X2 8 detector + chuyển giao 6 detector) GIỮ: có dữ liệu thật trong outputs/x2_architecture_20261020 + outputs/transferability. Nhánh B (train YOLO11/12/13) vẫn TẮT (\branchBfalse).
- Kiểm: table*15/15, figure*11/11, tabularx15/15; $ chẵn(962); không trùng label; 26 bibitem khớp hết \cite; không còn key cũ. Đồng bộ paper_Q1_submission/ + dựng lại paper_Q1_overleaf.zip.

---
## Sửa 2026-10-21 tối (6): vẽ lại hình với nhãn tiếng Anh (6/9)
- Copy experiments/extended_figures.py -> sponge-sim/figures_en/extended_figures_en.py (header nguồn + SHA, KHÔNG sửa bản gốc, KHÔNG đè outputs/). Dịch toàn bộ nhãn/tiêu đề/legend sang EN, đọc cùng analysis.json. Sinh EN: query_budget, eot_ablation, transferability, defense_tradeoff, processing_budget. Đã kiểm mắt 2 hình (query_budget, defense_tradeoff) — chữ EN đúng, số liệu khớp.
- sponge-sim/figures_en/r3_decouple_en.py: vẽ lại fig_r3 (r3_ratio_decoupling) EN từ sponge-sim/results/r3/20261021T184159/summary.json. Kiểm mắt: 349x/308x (N), 3.18x/3.27x (pp), 1.02x/1.06x (total), log scale, CI hai tầng — khớp.
- media/ (gốc + submission) nay có 6 hình EN. Dựng lại paper_Q1_overleaf.zip; 9/9 includegraphics resolve.
- CHƯA chuyển được sang EN (giữ bản tiếng Việt), lý do trung thực:
  * fullscale_map_growth (09): nguồn project_yolov13/results/ — nhánh B 32GB, CLAUDE.md quy tắc 3 cấm đụng.
  * published_vs_measured (12) & baseline_vs_sponge (14): recommended_figures.json ghi source=None — hình COMPARISON làm thủ công, KHÔNG có generator/dữ liệu trong code đã commit. Tái tạo sẽ phải đoán số → vi phạm quy tắc 4. Chờ tác giả cấp script/dữ liệu gốc.
