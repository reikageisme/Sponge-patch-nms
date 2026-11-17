# Tài liệu tham khảo gần đây để tác giả lọc

Cửa sổ nghiêm ngặt: **13/10/2024–13/10/2026**. Có **25 công trình duy nhất**, không đếm đôi bản preprint/hội nghị. A là cốt lõi; B bổ sung liên quan; C ngoại vi, có thể bỏ khỏi bài. Chỉ kiểm metadata/abstract nguồn gốc, chưa đọc toàn văn tất cả. Tháng xuất bản theo BibTeX CVF; không bịa ngày.

## underload2025 — mức A

**Can't Slow Me Down: Learning Robust and Hardware-Adaptive Object Detectors against Latency Attacks for Edge Devices**. Tianyi Wang, Zichen Wang, Cong Wang, Yuanchao Shu, Ruilong Deng, Peng Cheng, Jiming Chen. CVPR, 2025-06, tr. 19230–19240. peer-reviewed conference.

[Trang nguồn chính](https://openaccess.thecvf.com/content/CVPR2025/html/Wang_Cant_Slow_Me_Down_Learning_Robust_and_Hardware-Adaptive_Object_Detectors_CVPR_2025_paper.html).

Dùng cho: Hardware-sensitive latency threat and background-attentive defense; reported FPS on Jetson are not our platform measurements.

## evade2025 — mức A

**Latency NMS Attacks: Is It Real Life or Is It Just Fantasy?**. Jean-Philippe Monteuuis, Cong Chen, Jonathan Petit. NeurIPS 38, 2025. peer-reviewed conference.

[Trang nguồn chính](https://proceedings.neurips.cc/paper_files/paper/2025/hash/371713c3e5314dff9483c62c5abb98a8-Abstract-Conference.html); DOI: 10.52202/085713-1289.

Dùng cho: Practical evaluation depends on hardware, model format, quantization and downstream latency requirements.

## bitflip2025 — mức A

**Bit-Flip Induced Latency Attacks in Object Detection**. Manojna Sistla, Yu Wen, Aamir Bader Shah, Chenpei Huang, Lening Wang, Xuqing Wu, Jiefu Chen, Miao Pan, Xin Fu. WACV, 2025-02, tr. 6709–6718. peer-reviewed conference.

[Trang nguồn chính](https://openaccess.thecvf.com/content/WACV2025/html/Sistla_Bit-Flip_Induced_Latency_Attacks_in_Object_Detection_WACV_2025_paper.html).

Dùng cho: NMS latency attack with model-parameter bit flips; threat model differs from fixed-weight input patch.

## trackflood2026 — mức A

**TrackFlood: Relocating Latency Attacks from NMS-Free Detectors to Real-Time Trackers**. Zonghua Gu, Julian Singh-Smith, Junlin Liao, Di Liu, Amin Saremi. arXiv 2609.33948v1, 2026-09-27. preprint; no venue verified.

[Trang nguồn chính](https://arxiv.org/abs/2609.33948).

Dùng cho: NMS-free detectors can relocate workload to tracking; requires pipeline and deadline measurement.

## ebt2026 — mức B

**Event Burst Trigger: An Availability Backdoor Attack on Event-Based SNN Object Detection**. Jaesun Baek, Chanwook Lee, Eun-Kyu Lee. arXiv 2607.09115v2; DSN 2026 related resource, 2026-07-10. arXiv verified; DSN-related DOI present, exact proceedings category not publisher-verified.

[Trang nguồn chính](https://arxiv.org/abs/2607.09115); DOI: 10.1109/DSN-S70715.2026.00020.

Dùng cho: Phantom candidates can drive NMS load in event-based SNN detection; poison-only threat differs from RGB patch.

## apde2025 — mức A

**Revisiting Adversarial Patch Defenses on Object Detectors: Unified Evaluation, Large-Scale Dataset, and New Insights**. Junhao Zheng, Jiahao Sun, Chenhao Lin, Zhengyu Zhao, Chen Ma, Chong Zhang, Cong Wang, Qian Wang, Chao Shen. ICCV, 2025-10, tr. 23476–23486. peer-reviewed conference.

[Trang nguồn chính](https://openaccess.thecvf.com/content/ICCV2025/html/Zheng_Revisiting_Adversarial_Patch_Defenses_on_Object_Detectors_Unified_Evaluation_Large-Scale_ICCV_2025_paper.html).

Dùng cho: Attacked-object AP and patch localization accuracy measure distinct outcomes; unified/adaptive evaluation matters.

## pbcat2025 — mức A

**PBCAT: Patch-Based Composite Adversarial Training against Physically Realizable Attacks on Object Detection**. Xiao Li, Yiming Zhu, Yifan Huang, Wei Zhang, Yingzhe He, Jie Shi, Xiaolin Hu. ICCV, 2025-10, tr. 24456–24466. peer-reviewed conference.

[Trang nguồn chính](https://openaccess.thecvf.com/content/ICCV2025/html/Li_PBCAT_Patch-Based_Composite_Adversarial_Training_against_Physically_Realizable_Attacks_on_ICCV_2025_paper.html).

Dùng cho: Detector robustness should be assessed across physical attack families; ordinary fine-tuning is not adversarial training.

## oddr2025 — mức B

**ODDR: Outlier Detection & Dimension Reduction Based Defense Against Adversarial Patches**. Nandish Chattopadhyay, Amira Guesmi, Muhammad Abdullah Hanif, Bassem Ouni, Muhammad Shafique. ICCV, 2025-10, tr. 22999–23008. peer-reviewed conference.

[Trang nguồn chính](https://openaccess.thecvf.com/content/ICCV2025/html/Chattopadhyay_ODDR_Outlier_Detection__Dimension_Reduction_Based_Defense_Against_Adversarial_ICCV_2025_paper.html).

Dùng cho: Statistical outlier patch defenses are a separate possible defense family; no result reproduced locally.

## iap2025 — mức B

**IAP: Invisible Adversarial Patch Attack through Perceptibility-Aware Localization and Perturbation Optimization**. Subrat Kishore Dutta, Xiao Zhang. ICCV, 2025-10, tr. 14766–14775. peer-reviewed conference.

[Trang nguồn chính](https://openaccess.thecvf.com/content/ICCV2025/html/Dutta_IAP_Invisible_Adversarial_Patch_Attack_through_Perceptibility-Aware_Localization_and_Perturbation_ICCV_2025_paper.html).

Dùng cho: Patch placement can balance model susceptibility and visibility; gradient sensitivity is different from image Laplacian heuristic.

## grac2025 — mức A

**Gradient-Reweighted Adversarial Camouflage for Physical Object Detection Evasion**. Jiawei Liang, Siyuan Liang, Tianrui Lou, Ming Zhang, Wenjin Li, Dunqiu Fan, Xiaochun Cao. ICCV, 2025-10, tr. 13880–13889. peer-reviewed conference.

[Trang nguồn chính](https://openaccess.thecvf.com/content/ICCV2025/html/Liang_Gradient-Reweighted_Adversarial_Camouflage_for_Physical_Object_Detection_Evasion_ICCV_2025_paper.html).

Dùng cho: Viewpoint, distance and lighting require physical-specific optimization and tests; software transforms alone insufficient.

## 3dgs2025 — mức B

**3D Gaussian Splatting Driven Multi-View Robust Physical Adversarial Camouflage Generation**. Tianrui Lou, Xiaojun Jia, Siyuan Liang, Jiawei Liang, Ming Zhang, Yanjun Xiao, Xiaochun Cao. ICCV, 2025-10, tr. 28752–28762. peer-reviewed conference.

[Trang nguồn chính](https://openaccess.thecvf.com/content/ICCV2025/html/Lou_3D_Gaussian_Splatting_Driven_Multi-View_Robust_Physical_Adversarial_Camouflage_Generation_ICCV_2025_paper.html).

Dùng cho: Multi-view physical camouflage and sim-to-real gap; larger surface attack distinct from 4% digital patch.

## badpatch2025 — mức A

**BadPatch: Diffusion-Based Generation of Physical Adversarial Patches**. Zhixiang Wang, Xingjun Ma, Yu-Gang Jiang. ICCV Workshops, Findings, 2025-10, tr. 6303–6313. peer-reviewed workshop.

[Trang nguồn chính](https://openaccess.thecvf.com/content/ICCV2025W/Findings/html/Wang_BadPatch_Diffusion-Based_Generation_of_Physical_Adversarial_Patches_ICCVW_2025_paper.html).

Dùng cho: AdvT-shirt-1K source and naturalistic physical clothing patches; original 1131 vs local mirror 1123 discrepancy.

## yolo12_2025 — mức A

**YOLOv12: Attention-Centric Real-Time Object Detectors**. Yunjie Tian, Qixiang Ye, David Doermann. arXiv 2502.12524v1, 2025-02-18. preprint; venue not verified.

[Trang nguồn chính](https://arxiv.org/abs/2502.12524).

Dùng cho: Architecture and attention mechanism provenance; published timing cannot replace local RTX5060 data.

## yolo13_2025 — mức A

**YOLOv13: Real-Time Object Detection with Hypergraph-Enhanced Adaptive Visual Perception**. Mengqi Lei, Siqi Li, Yihong Wu, Han Hu, You Zhou, Xinhu Zheng, Guiguang Ding, Shaoyi Du, Zongze Wu, Yue Gao. arXiv 2506.17733v2, 2025-06-21. preprint; venue not verified.

[Trang nguồn chính](https://arxiv.org/abs/2506.17733).

Dùng cho: HyperACE and FullPAD model provenance; benchmark is not causal ablation of these modules.

## antistyler2026 — mức A

**AntiStyler: Defending Object Detection Models Against Adversarial Patch Attacks Using Style Removal**. Idan Yankelev, Edita Grolman, Yarin Yerushalmi Levi, Amit Giloni, Omer Hofman, Toshiya Shimizu, Yuval Elovici, Asaf Shabtai. CVPR, 2026-06, tr. 27936–27945. peer-reviewed conference.

[Trang nguồn chính](https://openaccess.thecvf.com/content/CVPR2026/html/Yankelev_AntiStyler_Defending_Object_Detection_Models_Against_Adversarial_Patch_Attacks_Using_CVPR_2026_paper.html).

Dùng cho: Defense must preserve clean AP and processing cost; zero-shot style masking includes digital and physical evaluations.

## trace2026 — mức A

**TRACE: Confounder-free Adversarial Fine-tuning for Robust Object Detection**. Wonho Lee, Jisu Lee, Hyunsik Na, Sohee Park, Daeseon Choi. WACV, 2026-03, tr. 6705–6714. peer-reviewed conference.

[Trang nguồn chính](https://openaccess.thecvf.com/content/WACV2026/html/Lee_TRACE_Confounder-free_Adversarial_Fine-tuning_for_Robust_Object_Detection_WACV_2026_paper.html).

Dùng cho: Fine-tuning defense addresses patch variations and physical testbeds; conventional person fine-tuning alone does not establish this.

## advpatchxai2025 — mức B

**A Unified, Resilient, and Explainable Adversarial Patch Detector**. Vishesh Kumar, Akshay Agarwal. CVPR, 2025-06, tr. 30387–30397. peer-reviewed conference.

[Trang nguồn chính](https://openaccess.thecvf.com/content/CVPR2025/html/Kumar_A_Unified_Resilient_and_Explainable_Adversarial_Patch_Detector_CVPR_2025_paper.html).

Dùng cho: Patch detection/generalization and interpretability are separate from person detection accuracy.

## diffpad2025 — mức B

**DiffPAD: Denoising Diffusion-Based Adversarial Patch Decontamination**. Jia Fu, Xiao Zhang, Sepideh Pashami, Fatemeh Rahimian, Anders Holst. WACV, 2025-02, tr. 6602–6611. peer-reviewed conference.

[Trang nguồn chính](https://openaccess.thecvf.com/content/WACV2025/html/Fu_DiffPAD_Denoising_Diffusion-Based_Adversarial_Patch_Decontamination_WACV_2025_paper.html).

Dùng cho: Diffusion-based localized patch removal alternative; reconstruction quality and runtime need own evaluation.

## remoteshape2025 — mức B

**Universal Shape of Strong Remote Adversarial Patches for Object Detection with Convolutional Neural Networks**. Kento Oonishi, Tsunato Nakai. CVPR Workshops, SAIAD, 2025-06, tr. 4369–4379. peer-reviewed workshop.

[Trang nguồn chính](https://openaccess.thecvf.com/content/CVPR2025W/SAIAD/html/Oonishi_Universal_Shape_of_Strong_Remote_Adversarial_Patches_for_Object_Detection_CVPRW_2025_paper.html).

Dùng cho: Patch geometry and model structure matter; single square-area ablation has limited scope.

## afog2025 — mức B

**Adversarial Attention Perturbations for Large Object Detection Transformers**. Zachary Yahn, Selim Furkan Tekin, Fatih Ilhan, Sihao Hu, Tiansheng Huang, Yichang Xu, Margaret Loper, Ling Liu. ICCV, 2025-10, tr. 3184–3193. peer-reviewed conference.

[Trang nguồn chính](https://openaccess.thecvf.com/content/ICCV2025/html/Yahn_Adversarial_Attention_Perturbations_for_Large_Object_Detection_Transformers_ICCV_2025_paper.html).

Dùng cho: Learned vulnerable-region attention versus handcrafted saliency; cross-architecture vulnerability does not guarantee transfer.

## norp2026 — mức B

**Physical Adversarial Clothing Evades Visible-Thermal Detectors via Non-Overlapping RGB-T Pattern**. Xiaopei Zhu, Guanning Zeng, Zhanhao Hu, Jun Zhu, Xiaolin Hu. CVPR, 2026-06, tr. 13356–13365. peer-reviewed conference.

[Trang nguồn chính](https://openaccess.thecvf.com/content/CVPR2026/html/Zhu_Physical_Adversarial_Clothing_Evades_Visible-Thermal_Detectors_via_Non-Overlapping_RGB-T_Pattern_CVPR_2026_paper.html).

Dùng cho: Multimodal clothing and physical-view diversity; outside single RGB/NMS threat, candidate future discussion only.

## thermalcloth2026 — mức B

**Thermally Activated Dual-Modal Adversarial Clothing against AI Surveillance Systems**. Jiahuan Long, Tingsong Jiang, Hanqing Liu, Chao Ma, Weien Zhou, Yang Yang, Wen Yao. CVPR, 2026-06, tr. 34929–34939. peer-reviewed conference.

[Trang nguồn chính](https://openaccess.thecvf.com/content/CVPR2026/html/Long_Thermally_Activated_Dual-Modal_Adversarial_Clothing_against_AI_Surveillance_Systems_CVPR_2026_paper.html).

Dùng cho: Physical material/activation constraints differ from digital patch simulation; not a DoS result.

## queryupdate2025 — mức C

**Mind the Gap: Detecting Black-box Adversarial Attacks in the Making through Query Update Analysis**. Jeonghwan Park, Niall McLaughlin, Ihsen Alouani. CVPR, 2025-06, tr. 10235–10243. peer-reviewed conference.

[Trang nguồn chính](https://openaccess.thecvf.com/content/CVPR2025/html/Park_Mind_the_Gap_Detecting_Black-box_Adversarial_Attacks_in_the_Making_CVPR_2025_paper.html).

Dùng cho: Query access exposes a defensive surface; peripheral support for future API attack monitoring, not NMS-specific.

## patchdemux2025 — mức C

**PatchDEMUX: A Certifiably Robust Framework for Multi-label Classifiers Against Adversarial Patches**. Dennis Jacob, Chong Xiang, Prateek Mittal. CVPR, 2025-06, tr. 9944–9953. peer-reviewed conference.

[Trang nguồn chính](https://openaccess.thecvf.com/content/CVPR2025/html/Jacob_PatchDEMUX_A_Certifiably_Robust_Framework_for_Multi-label_Classifiers_Against_Adversarial_CVPR_2025_paper.html).

Dùng cho: Certified robustness depends on task and patch constraints; multi-label classification, not object detector/NMS defense.

## contextgan2026 — mức C

**Seeing Isn't Believing: Context-Aware Adversarial Patch Synthesis via Conditional GAN**. Roie Kazoom, Alon Goldberg, Hodaya Cohen, Ofer Hadar. WACV Workshops, SAFE-2026, 2026-03, tr. 202–211. peer-reviewed workshop.

[Trang nguồn chính](https://openaccess.thecvf.com/content/WACV2026W/SAFE-2026/html/Kazoom_Seeing_Isnt_Believing_Context-Aware_Adversarial_Patch_Synthesis_via_Conditional_GAN_WACVW_2026_paper.html).

Dùng cho: Grad-CAM-based semantic placement and realism; classification target, not local availability validation.

## Áp dụng cho bản thảo

Bỏ Brown2017, Athalye2018, Phantom2023, OverloadCVPR2024, COCO2014 và các classic khỏi bibliography theo yêu cầu ngày. Phần lịch sử có thể viết qua tổng quan gần đây APDE/EVΑDE/PBCAT, nhưng không nói họ phát minh EOT/miếng dán/COCO. Mô tả EOT đúng như kỹ thuật kế thừa; nguồn dữ liệu COCO chính thức có thể nằm ở provenance/phụ lục, không đếm như một bài báo. Phần availability dùng underload/evade/bitflip/trackflood (preprint rõ). Phần patch/physical dùng APDE/PBCAT/BadPatch/GRAC/TRACE/AntiStyler. Phần kiến trúc chỉ dùng yolo12/yolo13. Những paper C ở thư viện ứng viên để tác giả lọc, không ép trích vào mọi đoạn.

**Cảnh báo trạng thái EBT:** arXiv có DSN2026 comment và DOI DSN-S; chưa xác minh exact proceedings category từ publisher. Cứ trích arXiv với ghi chú liên quan DSN, không tự gọi main conference/full paper.

