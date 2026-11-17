# Bản đồ bằng chứng cho chỉnh sửa bài báo — 13/10/2026

Phạm vi: đọc bản thảo Word và tạo tác kết quả; không chạy huấn luyện, không thay nguồn/số liệu. Áp dụng academic-research-suite → academic-paper (revision), hướng dẫn claim–evidence và writing_quality_check. Kiểm tra scalar/tổng hợp, không phải tái lập độc lập toàn thí nghiệm.

## 1. Danh tính, bài toán và cấu trúc gốc

Tên gốc: **Tấn công đối kháng Sponge Patch: Khai thác lỗ hổng cạn kiệt tài nguyên trên hệ thống Edge Server bằng thuật toán tối ưu không gian**.

Tác giả: **Phạm Tuấn Anh** (anh25807700004@hutech.edu.vn), **Mai Quốc Bảo** (bao2580770008@hutech.edu.vn). Cơ quan: Trường Đại học Công nghệ Thành phố Hồ Chí Minh, Việt Nam. Giảng viên hướng dẫn: **Đinh Phương Nam** (dp.nam@hutech.edu.vn). Giữ nguyên danh tính/vai trò; không tự thêm người hay thay supervisor thành đồng tác giả.

Tên khoa học đề xuất phù hợp bằng chứng: **Sponge Patch trên hệ thống thị giác tại biên: Đánh giá khuếch đại ứng viên, chi phí NMS và lựa chọn mô hình phát hiện người**. Đây là giảm mức khẳng định của tên gốc, vẫn giữ Sponge Patch làm chủ đề, không chuyển toàn bài thành benchmark YOLO.

Gốc có 1 Giới thiệu (4 tiểu mục); 2 Liên quan (5); 3 Phương pháp (8); 4 Thực nghiệm (27); 5 Kết luận/hướng phát triển (15), Lời cảm ơn, Tái lập, 29 references và 20 bảng. Nhiều ký hiệu/toán và số ± nằm trong Word equation, nên python-docx paragraph.text hiện trống ở các vị trí này; **không coi đó là dữ liệu thiếu**. Phải đọc XML equation hoặc tạo lại từ bằng chứng JSON trước khi thay nội dung.

Giữ các RQ đã established:

- RQ1: ứng viên sau threshold phản ánh chi phí NMS thực đo tới đâu; patch có tăng chi phí toàn đường xử lý so sạch?
- RQ2: cùng ngân sách query, saliency (phương sai Laplacian) giúp SG-GA hơn GA tâm/random search trên endpoint độc lập không?
- RQ3: hiệu ứng accuracy/cost duy trì khi đổi ảnh, threshold, software transforms không?

Thêm **mục tiêu bổ sung** (không tự coi như một RQ thay toàn đề tài): đánh đổi chất lượng phát hiện người, thời gian fine-tuning và latency của detector ứng viên cho nghiên cứu availability tiếp theo. Benchmark mới chưa trả lời RQ1–3 trên YOLO11/12/13.

## 2. Hai nhánh bằng chứng phải tách

**A — Sponge/NMS cục bộ 02–03/10**: YOLOv8n CPU laptop i5-1335U, ảnh 320×320, patch 64×64 (4%), gray-box pre-NMS confidence, tối ưu 4 ảnh, held-out 128 COCO val2017, 10 patch seeds. Dữ liệu chính: `outputs/extended_q1_20261002/analysis.json`, `manifest.json`, `evaluation`, `backend_qos`, `stream_qos`, `transfer`. Nhánh này kiểm nghiệm cơ chế, accuracy/candidate/QoS.

**B — Fullscale 11–13/10**: 4 model ×5 seed, 11.123 ảnh, một class person, pretrained fine-tuning GPU RTX5060, input416. Dữ liệu chính: `project_yolov13/results/BaoCao_TrienKhaiRong_YOLOv13.md`, `fullscale_experiments/records`, `epoch_history`, `latency_records.json`, `fullscale_setup`. Nhánh này so detector/đánh đổi, không có attack-vs-clean QoS causal experiment. Không gộp AP của A (COCO80 classes/subset) với person AP của B.

**C — lịch sử**: random tensors, synthetic scenes, Oct4 zero-shot AdvT-shirt, two-image diagnostic chỉ giữ ở phụ lục hoặc giải thích lịch sử. `final_academic_report.md` là báo cáo ngày04/10, mô tả task splits trống ở thời điểm đó; không dùng để nói fullscale mới chưa được chạy. `adv_tshirt_patch_final_report.md` là patch localization study khác; nếu thêm, phải công bố class khác, dataset khác, không trộn target person.

## 3. Bảng Sponge chính đã đối chiếu từ analysis.json

Ngân sách2.500 image forwards, confidence0,01, không cap trước NMS, 128 held-out images, 10 seed. Ratio = trung bình theo ảnh của candidates(patched)/max(candidates(clean),1), sau đó tổng hợp theo seed. Không phải ratio của hai mean counts.

| Điều kiện | Candidate ratio μ±SD | AP hộp (%) μ±SD |
|---|---:|---:|
| Sạch | 1 (theo định nghĩa) | 34,08 (baseline được lưu; không tạo SD giả) |
| SG-GA | 1,027802 ±0,008322 |29,967882 ±0,468259 |
| GA tâm |1,032934 ±0,009287 |25,880380 ±0,455081 |
| GA vị trí ngẫu nhiên |1,051862 ±0,009227 |30,266224 ±0,641704 |
| Tìm kiếm ngẫu nhiên |1,026813 ±0,007190 |29,928604 ±0,260889 |

Endpoint primary SG-GA minus GA tâm: mean **−0,005132356**, SD0,010297744; paired-seed bootstrap95%CI **[−0,011178379;0,000706024]**,20.000 draws; exact two-sided sign-flip p **0,150390625** (1.024 assignments). Không hỗ trợ ưu thế SG-GA. CI conditional on fixed held-out images, không phải CI quần thể ảnh. Các kiểm định secondary phải ghi exploratory/Holm nếu báo; không chọn một p thuận lợi rồi biến thành kết luận primary.

AP giảm từ34,08 xuống29,97 không chứng minh DoS. Ratio hơi tăng có thể đồng thời mean absolute candidates giảm vì average-of-ratios khác ratio-of-averages; không cố sửa số để khiến cơ chế có vẻ thuận chiều.

Nhánh backend processing, CPU1thread, deadline300ms, median toàn đường đo (mean của seed medians): sạch **51,087545ms**, SG-GA **52,870940ms**, GA tâm **51,176985ms**, GA random location52,045445ms, random search51,933360ms. Mean p95 của sạch78,195026 và SG-GA82,691833ms. Late fraction0 ở mọi seed của các cấu hình này. **Đây không phải webcam deadline**. Có CPU2/4threads results riêng; không ghép chúng với dòng1thread.

Stream QoS:240 blocks,7.680 records, period100/300ms, deadline300ms, FIFO/drop-if-busy/adaptive throttle. Review xác minh: FIFO100ms thiếu/trễ85,31% ngay sạch; FIFO300ms đáp ứng ở sạch và patches đã thử. Baseline overload không phải attack causal effect. Báo riêng emitted/dropped/processed/late/on-time và accuracy trên toàn bộ emitted frames; throughput sau bỏ ảnh không tự chứng minh giữ dịch vụ.

## 4. Bảng fullscale mới tái tính trực tiếp

Đọc20 record JSON; lấy mỗi model đúng milestone `sweet_spot_minutes` từ latency JSON. SD = sample SD(ddof1) của5seed. Latency = mean của5per-checkpoint median, SD giữa những medians; không phải pooled per-frame SD.

|Model|Mốc(min)|Precision(%)|Recall(%)|mAP50(%)|mAP50:95(%)|Pipeline FP32(ms)|
|---|---:|---:|---:|---:|---:|---:|
|YOLO11n|120|77,099336±0,353249|55,981676±0,568648|65,074467±0,294879|42,444880±0,224866|2,584530±0,420702|
|YOLOv12n|120|75,321080±1,380706|54,247197±0,359227|62,919606±0,274851|40,488609±0,310843|2,772172±0,073727|
|YOLOv13n|5|76,428666±2,365063|54,351073±0,872430|63,194001±0,722026|40,795714±0,967807|4,162780±0,207227|
|YOLOv13s|10|80,462073±1,438297|61,077553±1,222079|70,942177±1,060498|47,970523±1,130778|51,786076±2,082358|

Rounded2decimals sufficient manuscript. Compared YOLO13s vs11n: +5,525643percentage points mAP95; latency ratio20,04× **different model capacity and different selected budgets**, descriptive tradeoff, not architecture causal gain. YOLO13n −1,649166pp vs11n. Do not claim YOLOv13 always superior.

Dữ liệu:10.000 COCO samples (8.000 with noncrowd person,2.000 no person),1.123 AdvT-shirt mirror images;fixed splitseed2026:7.786train/1.669val/1.668test. Target only person; patch boxes not included. 0 byte/COCO-ID overlap does not prove subject/video separation.1.429 test images derived COCOtrain2017 potentially present in pretraining. AdvT-shirt authors describe1.131;mirror1.123;state discrepancy,do not silently replace count.

Train416px,batch8,SGD lr0=.01/lrf=.01/momentum.937/decay.0005,AMP,deterministic,workers0;seeds42,100,2026,777,999;max120min,checkpoints per epoch;budgets5/10/20/30/60/120min.1 missing cell YOLO13s2026 at5min excluded,never impute0.119valid milestones.

Sweet spot: earliest complete5seed budget whose mean val mAP95 within0,5percentage points of observed120min-window peak. Retrospective against later peak, not validated online stopping. v13n/s keep epoch1 at every seed's sweet spot. Need mốc0pretrained to claim rapid learning/fine-tuning gain;current best-so-far retention does not prove convergence/saturation.11/12peak boundary120min does not prove ceiling.

Latency416px,batch1,FP32,32warmup,500fixedtestframes,RTX5060,Ultralytics timer preprocessing+inference+postprocessing;exclude decode/loading/camera/network/app I/O. Sum of per-frame stages used for total median;sum of stage medians not generally total median. Raw per-frame timing not stored in shared evidence;no p95/p99 from this dataset. Existing FPS values393,85/360,93/240,68/19,33 are mean of per-seed reciprocal medians, not reciprocal of mean latency. Omit FPS if cramped;do not silently recompute differently.

Review audit limitation:scalar aggregation/CSVhashes checked,not replay fullscale predictions/checkpoints. YOLO13source correct measured commit73289949533efac82bb5f72ec19b746618656bd2 absent from shared clone. YOLO12Windows raw CRLFhash mismatch normalizedLFmatches162files: report byte mismatch context,not scientific drift accusation. Accuracy/latency resolved conf/iou/rect incomplete;do not invent common operating threshold. YAML/source defaults differ potentially. CSVtimer written before checkpointsave in inspected fork;describe metrictimestamp budget,not guaranteed save-completion cap.

## 5. Outline đề xuất tiếng Việt

Tóm tắt: vấn đề availability;SG-GA/no-gradient-graybox;A128images×10seed primary negative result;B11.123images×20runs descriptive accuracy/latency;no physicalDoS evidence. Có thể250–350words,Englishabstract optional if venue notspecified.

1.Giới thiệu: integrity vs availability;NMS proxy vs true QoS;contributions bounded;RQ1–3 unchanged,supplementary detector-selection objective.

2.Liên quan: patch/EOT/gradient-free;Sponge/NMS latency;deployment sensitivity;recentdetectors and AdvT-shirtbenchmark relation.

3.Phương pháp: threatmodel;formalpatchoperation;candidates/fitness;Laplacianlocation;GA/EOT;measurementstageboundaries;criterionforavailability relativeclean.

4.Thiết kế thực nghiệm: **4.1A Sponge128/10seed CPU**,**4.2Bpersonbenchmark4models/5seed GPU**;datasetprovenance/splits;accuracy/cost/statisticalunits;baselineandcontrols;ethicalscope.

5.Kết quả: **5.1SG-GA primary and controls**,**5.2NMSbackend/streamQoS**,**5.3threshold/transfer exploratory (condensed)**,**5.4newfullscale learningcurves**,**5.5accuracy-latencytradeoff**. Mainfigures6–8 suffices;historicalexploratoryappendix.

6.Thảo luận/giới hạn:answereachRQ;negativefinding;fitnessmismatch;modelselectioncannotreplaceavailabilityvalidation;seedvsimageinference;pretraining/splitdependency;timingscope;replay/physical limits.

7.Kết luận/hướng tiếp:conditionalassessment only;pretrained0baseline,repeatedrawtailtiming,properpairedattack/cleanQoS,futureopticalevaluation. No new training reported.

Tái lập:LaptopbranchAandGPUbranchBseparatemanifestpaths;providedarchives vs absentdata/checkpoints;statedcommit/hash;acknowledgmentretained;referenceIEEErenumberedconsistently.

## 6. Claim decisions

### Cập nhật theo phản hồi giảng viên: phải nêu giá trị phương án, không chỉ viện khác protocol

Lý do lựa chọn đường nghiên cứu SG-GA: ràng buộc **không gradient**, chỉ patch4% và phản hồi confidence trước NMS tương ứng một năng lực can thiệp đầu vào hẹp hơn white-box/full-image. Đây là **giá trị thực dụng của câu hỏi cần kiểm nghiệm**, không phải kết quả ưu thế đã chứng minh. Một phương pháp gradient-free có thể áp dụng nơi không cung cấp gradient nếu có đúng kênh confidence; đồng thời nhu cầu nội bộ pre-NMS khiến nó vẫn gray-box, không tuyên bố dễ triển khai black-box.

Điểm phân biệt có bằng chứng: (1) so vị trí saliency/tâm/ngẫu nhiên dưới **cùng image-forward budget và diện tích**, (2) đo độc lập candidates, AP, backend và stream QoS, (3) giữ kết quả âm để phát hiện surrogatefitness không đủ. **Không chỉ khác dataset**: thiết kế đo trả lời trực tiếp câu hỏi liệu tăng ứng viên nhỏ có biến thành giảm sẵn sàng, trong khi proxy đơn thuần có thể khiến suy luận sai. Giá trị nằm ở kiểm định/ranh giới hiệu quả, không tự xưng tấn công mạnh hơn.

Evidence endpoint: primarySG-GA−GAcenter=-0,005132CI95%[-0,011178;0,000706],p=.150391; SG-GA không đạt ưu thế chính. Phiên bản tham chiếu gradient/fullimage có quyền và diện tích khác nên không kết luận SG-GA hiệu quả hơn từ đối chiếu chưa đồng nhất. Nếu cần so hiệu quả attack mạnh/yếu, phải thiết kế phép so cùng threatmodel/area/budget/evaluator, hoặc biểu diễn tradeoff rõ từng constraint; nghiên cứu hiện chưa thực hiện đủ để claim superiority.

Đối với benchmarkYOLO mới: route hữu ích vì đo **đánh đổi cụ thể để chọn detector** trên cùng fixedsplit/hardware, chứ không vì tên kiến trúc mới. YOLO13s nâng observedpersonmAP95+5,53pp so11n nhưng latency khoảng20,04× và kháccapacity/budget;YOLO11n là lựa chọn latencythấp trong cấu hình đã đo, không tự động là detectorchốngDoS. Rationale cần nêu nhu cầu mAP/latency của ứng dụng (chưa có targetconfirmed) rồi mới quyết định. Phần benchmark là cơ sở định lượng cho bước lựa chọn tiếp theo, không bằng chứng sự kết hợpSG-GA+YOLO13 là đóng góp mới tối ưu.

Giữ:gray-boxpreNMSconfidence;gradient-freeGA;patcharea4%;separateaccuracy/NMS/overalltimers;nullSG-GA superiority;threshold/topKtradeoff;GPUbenchmark20runs.

Giảm mức:``khai thác lỗ hổng cạn kiệt tài nguyên``→``đánh giá nguy cơ tăng chi phí``;``edgevalidated``→``laptop/RTX5060measuredplatforms``;``converges5min``→``checkpointselectedwithin5minbyretrospectivecriterion``;``HyperACEcausesgain``→``detectorconfigurationobservedtradeoff``.

Không giữ:universalDoS/webcamphysicalvalidation;newbenchmarkprovesrobustpatchdefense;smallscaleequivalentcapacity;statisticallysignificantbestclaimfromSDalone;rawtimingp95/p99forfullscale;source/checkpoint replaycompleted;imagegroupindependence/pretrainingindependence.

## 7. HISTORICAL ONLY — SUPERSEDED by user's two-year reference constraint

**Không đưa các classic dưới đây vào bibliography bản viết lại.** Yêu cầu cập nhật của tác giả giới hạn13/10/2024–13/10/2026. Dùng `recent_refs.json` và `recent_refs.md` (25 papers) làm nguồn tham khảo hiện hành; danh sách dưới đây chỉ ghi lại audit nguồn của bản gốc, không phải đề xuất citation mới.

1. T.B.Brown,D.Mané,A.Roy,M.Abadi,J.Gilmer. **Adversarial Patch**. arXiv1712.09665,2017(initial;v2May2018). https://arxiv.org/abs/1712.09665 . Patchconcept;do not transfer theirphysicalsuccess to thisstudy.
2. A.Athalye,L.Engstrom,A.Ilyas,K.Kwok. **Synthesizing Robust Adversarial Examples**. ICML2018,PMLR80:284–293. https://proceedings.mlr.press/v80/athalye18b.html . EOTdefinition;softwaretransforms alone not opticalvalidation.
3. I.Shumailov,Y.Zhao,D.Bates,N.Papernot,R.Mullins,R.Anderson. **Sponge Examples: Energy-Latency Attacks on Neural Networks**. IEEE EuroS&P2021;arXiv2006.03463. https://arxiv.org/abs/2006.03463 . Availabilityseparatefromaccuracy.
4. D.Wang,C.Li,S.Wen,Q.-L.Han,S.Nepal,X.Zhang,Y.Xiang. **Daedalus: Breaking Non-Maximum Suppression in Object Detection via Adversarial Examples**. arXiv1902.02067(v3June2020);originalmanuscriptjournaldetailsIEEETransCybernetics52(8):7427–7440,2022notrecheckedatpublisher. https://arxiv.org/abs/1902.02067 . NMSmanipulation;usearxivmetadataifpublishernotverified.
5. A.Shapira,A.Zolfi,L.Demetrio,B.Biggio,A.Shabtai. **Phantom Sponges: Exploiting Non-Maximum Suppression to Attack Deep Object Detectors**. WACV2023;arXiv2205.13618. https://arxiv.org/abs/2205.13618 . UniversalperturbationNMSlatency. CurrentCVFfetchfailed;arxividentityverified.
6. E.-C.Chen,P.-Y.Chen,I.-H.Chung,C.-R.Lee. **Overload: Latency Attacks on Object Detection for Edge Devices**. CVPR2024;arXiv2304.05370v4. https://arxiv.org/abs/2304.05370 . Spatialattentionlatency;localadaptationnotidenticalreplication.
7. J.-P.Monteuuis,C.Chen,J.Petit. **Latency NMS Attacks: Is It Real Life or Is It Just Fantasy?**. NeurIPS2025,vol38,doi10.52202/085713-1289. https://proceedings.neurips.cc/paper_files/paper/2025/hash/371713c3e5314dff9483c62c5abb98a8-Abstract-Conference.html . Supportsdeployment-format/hardware-dependentlimits,notuniversalassertionallattacksfail.
8. M.Alzantot,Y.Sharma,S.Chakraborty,H.Zhang,C.-J.Hsieh,M.Srivastava. **GenAttack: Practical Black-box Attacks with Gradient-Free Optimization**. GECCO2019;arXiv1805.11090v3. https://arxiv.org/abs/1805.11090 . GAgradientfreecontext;itsblackboxlabelnotautomaticallythismethod'slabel.
9. T.-Y.Lin etal. **Microsoft COCO: Common Objects in Context**. ECCV2014;arXiv1405.0312. https://arxiv.org/abs/1405.0312 . Officialpaperanddataset:https://cocodataset.org/ . Avoidmixingdifferentauthorlistsarxivvsconferenceversion;``etal``acceptableIEEEabbrev.
10. Y.Tian,Q.Ye,D.Doermann. **YOLOv12: Attention-Centric Real-Time Object Detectors**. arXiv2502.12524,2025. https://arxiv.org/abs/2502.12524 . Architecturecontext;theirT4timingnotourRTXtiming.
11. M.Lei,S.Li,Y.Wu,H.Hu,Y.Zhou,X.Zheng,G.Ding,S.Du,Z.Wu,Y.Gao. **YOLOv13: Real-Time Object Detection with Hypergraph-Enhanced Adaptive Visual Perception**. arXiv2506.17733v2,2025. https://arxiv.org/abs/2506.17733 . HyperACE/FullPADcontext,noarchitecturalcausalablationinourbenchmark.
12. Z.Wang,X.Ma,Y.-G.Jiang. **BadPatch: Diffusion-Based Generation of Physical Adversarial Patches**. arXiv2412.01440v5,2025revision(initialDec2024). https://arxiv.org/abs/2412.01440 . **Important**:datasetREADMEstillcitesolderDiffPatchtitle/sevenauthors;currentv5identityhasthreeauthors. Datasetrepository https://github.com/Wwangb/AdvT-shirt-1K describes1.131images,person/patchlabels;localmirror1.123images. Ourpersonprotocolcannotclaimpatchlocalization.

Optionalsoftwarecite (outside12papers): Ultralytics **YOLO11**,documentationaccess13/10/2026 https://docs.ultralytics.com/models/yolo11 . No inventedYOLO11peerreviewedpaper.

Allwebaccessusedpublicmetadata/primarypages;noWorduploaded. AccuracyclaimsaboutthisstudyderivefromlocalJSON/CSV,notexternalpapers. Citationtitles/years distinguishfirstpreprintandlaterversion/conference. Compactliteratureparagraphsadequate;notasystematicrevieworclaimsexhaustivecoverage.
