# Đề tài NCKH: Sponge Patch (nhắm Q1)

Tiêu đề (GVHD duyệt 03/11/2026): "Tấn công cạn kiệt tài nguyên qua NMS có thực sự làm chậm bộ phát hiện? Một nghiên cứu đo lường trên CPU ghim lõi". Tiêu đề trước ("Does the Number of Pre-NMS Candidates Predict Detector Latency? …", tiếng Việt "Số lượng ứng viên trước NMS có dự đoán được độ trễ của bộ phát hiện không? …") không còn dùng; khung mới: tấn công cạn kiệt tài nguyên qua NMS là đối tượng được kiểm tra (xem docs/reports/REFRAME_REPORT.md).
Nhóm: Phạm Tuấn Anh, Mai Quốc Bảo; GVHD và tác giả liên hệ: Đinh Phương Nam (HUTECH). Ngôn ngữ làm việc: tiếng Việt; thuật ngữ kỹ thuật giữ tiếng Anh.

## Luận điểm đang theo đuổi (hướng A + C)
- A: số ứng viên trước NMS (N_tau) là proxy KHÔNG dự đoán được độ trễ/suy giảm dịch vụ; chỉ ra vùng proxy đúng và vùng sai.
- C: bản đồ điều kiện (backend × class-aware/agnostic × cap top-k × tau × số core CPU × chu kỳ phát) cho biết khi nào tấn công NMS thành lỗ hổng sẵn sàng.
- Không còn dùng cụm "máy chủ biên / Edge Server". Gọi đúng: "mô phỏng hạn chế tài nguyên trên CPU laptop ghim core", "điện thoại Arm (Galaxy A36)" và "Pi 3B bị firmware ép600MHz do thiếu áp" cho board đo14/11. Kết quả A36 ghi đúng Snapdragon6Gen3/Android/Termux/proot/RAM thực tế, không đổi nhãn thành Pi. Người dùng báo RAM8GB; A0D ghi MemTotal kernel7529500kB. Pi3B1GB đã mua/chạy14/11; full01 đầu tiên chỉ chẩn đoán do swap FAIL (`docs/reports/PI3B_600MHZ_RESULTS_20261114.md`). Protocol full20 sau pilot có main4luồng đạt chất lượng nhưng componentNMSFAIL/PI1hủy (`docs/reports/PI3B_FULL20_RESULTS_20261114.md`); giữ riêng từng protocol. Đánh giá khả thi08/11 là tài liệu trước mua.

## Quy tắc cứng (không thương lượng)
1. KHÔNG xóa, di chuyển, ghi đè dữ liệu thô hay kết quả đã chạy (`outputs/**`). Muốn dọn: đề xuất danh sách, chờ duyệt.
2. KHÔNG sửa code cũ (`core/`, `attack/`, `experiments/`). Cần dùng lại thì COPY sang `sponge-sim/` kèm header nguồn (file:dòng + SHA256) và test hồi quy.
3. KHÔNG đụng `project_yolov13/**` (nhánh B, ~32 GB, ngoài luận điểm), `.venv`, `.git`.
4. Mọi con số đưa vào bài phải truy được tới dòng raw (JSONL/JSON:selector). Không làm tròn cho đẹp, không bịa, không điền số khi chưa có nguồn.
5. Đặt trước giả thuyết/endpoint (PREREG) và `git tag` TRƯỚC khi đo. Sai lệch ghi vào DEVIATIONS.md.
6. Kết quả âm giữ nguyên. Không dùng "tương đương / không phụ thuộc / chứng minh" khi chỉ có p > 0,05 hoặc CI chứa 0; phải kèm MDE.
7. Không cài gói hệ thống, không dùng mạng, không đổi power plan/turbo: chỉ ĐỌC cấu hình và in checklist cho tôi tự làm.
8. Chỉ `git add` đúng file của việc đang làm. Repo đã dirty từ trước (5 file code đã sửa sau các lượt chạy cũ). Không reset/clean/force-push.
9. Trong lúc đo ghim core (A/A, E1, E5, E6, bất kỳ phép đo thời gian nào, trên laptop hay điện thoại), Claude Code CHỈ được chạy đúng tiến trình đo đó. KHÔNG chạy song song bất kỳ việc gì khác (đọc/ghi file, soạn bài, phân tích, git, web search, test) dù nhân danh "việc nhẹ". Chỉ được kiểm tiến độ khi tiến trình đo đã kết thúc (dùng cơ chế thông báo khi xong, không poll). Việc khác phải đợi đo xong. Lý do: A/A 640 px và E6-A1 ngày 02/11/2026 bị drift tham chiếu rất cao (8/11 và 9/11 khối bị cờ, có khối chậm 12 lần) trong lúc trợ lý làm việc song song.

## Bản đồ repo (D:/Physical-Visual-DoS-EdgeAI-main)
- Cohort dữ liệu (tên bắt buộc dùng thống nhất):
  - OLD128 = `outputs/extended_q1_20261002` (128 ảnh con của 500 ID held-out; q1000 dùng 32 ảnh).
  - X1-500 = `outputs/x1_500img_20261018` (500 ảnh; là mở rộng SAU khi thấy p=0,1504 ở OLD128, KHÔNG phải tái lập độc lập vì 128 ⊂ 500).
  - X2 = `outputs/x2_architecture_20261020` (8 detector; Faster R-CNN/RetinaNet/SSDlite đếm `post_module_detections`, tức đã qua NMS nội bộ, KHÔNG dùng để kết luận tải NMS).
  - X5 v2 chỉ là mô hình hàng đợi nhiều server từ thời gian forward, không phải đo core, không có NMS: không dùng làm bằng chứng.
- Code tái sử dụng được (đã audit): `core/victim_model.py`, `experiments/extended_evaluation.py`, `experiments/extended_validation.py:113` (optimize), `experiments/local_q1_validation.py` (load_image).
- Bản thảo CHÍNH THỨC (từ 01/11/2026): `paper_en/main.tex` (tiếng Anh). Bản tiếng Việt `paper/vi_v2/BaoCaoKhoaHocAdversarialAttacks_Q1_VI_v2.tex` và các bản cũ (`paper/history/`) chỉ để tham khảo, không đồng bộ song song.
- Báo cáo review đã có: `docs/REVIEW/01_inventory.md` … `docs/REVIEW/06_*.md`. Đọc 03 và 04 trước khi đụng bản thảo.

## Kết quả đã xác minh (để không phải tính lại)
- OLD128: SG-GA − GA tâm = −0,00513, CI95% [−0,01118; 0,00071], p = 0,1504, d_z = −0,498.
- X1-500: −0,02934, CI95% [−0,03833; −0,02160], p = 0,001953 (giá trị nhỏ nhất có thể với 10 seed, cả 10 seed cùng dấu âm), d_z = −2,05. SG-GA kém hơn cả GA vị trí ngẫu nhiên, không khác tìm kiếm ngẫu nhiên.
- Suy luận hiện tại theo seed (10 seed), chưa phủ độ bất định của ảnh: cần bootstrap hai tầng (ảnh × seed).
- Backend NMS custom vs torchvision khớp trên mẫu hữu hạn (không phải tương đương mọi tie).

## Việc đang làm
Mục tiêu duy nhất (01/11/2026): hoàn thiện bài theo `docs/REVIEW_THAY_NAM.md` (trục "N có dự đoán độ trễ không", SG-GA là case study; đối chứng dương 10^2-10^4 trên laptop + ARM; patch thật qua giao thức ghim core; tập tối ưu >=100 ảnh, ngưỡng 0,25, 640 px; viết lại tiếng Anh, gom giới hạn vào Threats to Validity).
Bản thảo tiếng Anh: `paper_en/`. Thí nghiệm: E1 (tiêm), E5 (A/A), E5-phone, E6 (đo lại patch), E7 (sinh patch trên GPU). Tiến độ và lịch: `sponge-sim/PROGRESS.md` (mục cuối). Quy tắc dừng: trước mọi tag PREREG, khi cần máy rảnh, việc không đảo ngược, mâu thuẫn số liệu, bị bộ lọc an toàn chặn.

## Làm việc tiết kiệm token (quan trọng: lần trước hết token giữa chừng)
- Cập nhật `sponge-sim/PROGRESS.md` sau mỗi giai đoạn nhỏ (đã xong gì, đang dở gì, lệnh để chạy tiếp, quyết định chờ tôi). Phiên mới đọc file này đầu tiên.
- Commit nhỏ, thường xuyên trên nhánh `harness/step1`.
- Việc dài (đo, build): chạy nền, ghi log ra file, chỉ đọc phần cuối log. Không in JSON lớn ra màn hình; dùng `head`, `jq`, hoặc script tóm tắt.
- Không Glob/Grep toàn repo (235k file, 45 GB). Luôn chỉ rõ thư mục con.
- Dùng skill `sponge-research` cho mọi việc về thí nghiệm, thống kê, báo số, sửa bài.

## Thiết bị ARM: điện thoại Samsung Galaxy A36 (Snapdragon 6 Gen 3), qua SSH
- Host ưu tiên qua Tailscale `100.85.153.4` (LAN cũ `192.168.1.139`), cổng `8022`, user `u0_a445`, khóa riêng `$env:USERPROFILE\.ssh\phone_a36` (Git Bash: `~/.ssh/phone_a36`). Giữ strict host-key checking; alias khóa đã tin là `[192.168.1.139]:8022`, không tắt kiểm khóa khi đổi địa chỉ.
- Metadata A0D07/11: SM-A366B/a36xq, QTI/SM6475, arm64-v8a, Android16/SDK36; MemTotal7529500kB là RAM kernel thấy dùng được, không phải8GB trống/giới hạn worker. Chi tiết `docs/reports/A36_HARDWARE_A0D_20261107.md`. A0E chỉ mới kiểm con trực tiếp đang ngủ qua proot đạt, chưa có profile ghim hoặc timing phân đoạn ARM v2 đạt.
- **08/11/2026:** người dùng báo pin100% và cho phép chạy ở trạng thái này. Chuẩn bị cấu hình nguồn riêng `full_100_external`, ghi rõ protocol/source trước đo; không sửa hồi tố E5 30–80% hay coi FULL là charging=True. Nguồn ngoài/status/SOC phải đọc live, các ngưỡng nhiệt70/40 và resume55/38 giữ nguyên. Code/host tests mới không tự mở cổng tải khi registry nhiệt/collector/QA còn thiếu. Xem `sponge-sim/prereg/DRAFT_ARM_EXTERNAL_FULL100_20261108.md`.
- Môi trường chạy: bên trong Termux, dùng proot-distro Ubuntu. Lệnh mẫu: `ssh -p 8022 -i ~/.ssh/phone_a36 u0_a445@192.168.1.139 "<lệnh>"`.
- Đây là điện thoại dùng hàng ngày của người dùng, KHÔNG phải máy thí nghiệm. Phạm vi cho phép TRÊN ĐIỆN THOẠI: chỉ đọc/ghi trong `~/sponge-sim` (hoặc thư mục tương ứng trong proot Ubuntu). Không đụng gì khác trên Termux hay Android.
- Ngoại lệ mạng (đã được người dùng cho phép): cài proot-distro + Ubuntu trong Termux, rồi cài python3, pip, git, torch trong Ubuntu. Ngoại lệ này CHỈ áp dụng trong lúc CÀI ĐẶT. Sau khi cài xong, quy tắc cứng số 7 "không dùng mạng" áp dụng cho cả điện thoại: không tải thêm gói hay dữ liệu.
- Khi ĐO thật (A/A, E5, smoke có ghi thời gian): người dùng tắt mạng di động trên điện thoại, giữ Wi-Fi ở mức tối thiểu hoặc tắt hẳn nếu SSH không cần giữ liên tục. Nếu phải tắt Wi-Fi, chạy phép đo nền trên điện thoại (log ra file trong `~/sponge-sim`), rồi lấy kết quả sau khi Wi-Fi bật lại. Không đo khi mạng di động đang bật. PREREG_E5_phone phải ghi trạng thái mạng của từng lần đo, và Claude chờ người dùng xác nhận trước khi bắt đầu.
- Cấm: `rm`/`rmdir` ngoài thư mục `sponge-sim` qua SSH; tắt/khởi động lại máy; đổi cài đặt hệ thống Android.
- **Quy tắc mới theo người dùng 07/11/2026:** giữ sshd mở xuyên suốt chiến dịch đo và kiểm thử ARM trên điện thoại. KHÔNG tắt sshd sau từng bước metadata, test, phiên đọc cảm biến, cooldown hay tạm dừng vì pin/nhiệt; chỉ tắt khi đã xong toàn bộ đo/test ARM cần thiết trên điện thoại hoặc người dùng yêu cầu rõ. Quy tắc này thay thế chỉ dẫn tắt SSH sau mỗi phiên trước đây; các log đóng SSH cũ là lịch sử, không phải việc cần lặp lại.
- Giữ SSH mở không đồng nghĩa chạy tải khi thiếu điều kiện: mọi phép đo vẫn cần PREREG/tag, cảm biến và kiểm tự dừng đã xác minh, pin/sạc và xác nhận máy rảnh/mạng như trên. Không đổi cài đặt Android hoặc mở cổng/đổi xác thực ngoài phạm vi người dùng cho phép.
- Kết quả đo lấy về `sponge-sim/results/phone_a36/`. Mọi lần đo trên điện thoại phải có PREREG riêng (PREREG_E5_phone.md) và chờ người dùng xác nhận máy rảnh (sạc, không dùng tay, Không làm phiền, tắt tiết kiệm pin) trước khi chạy đầy đủ.

## Board Raspberry Pi 3B — cập nhật14/11/2026
- **15/11 READY METHOD mới7c6b8a8 đã PASS:** sau actualuserngoạilệ duyệt, ONE5sleepingcasesnormal/mainkill/childkill/timeout/disconnectđạt;44new+8oldoriginalSHA/39requests/restore/childgone/source23+probe verified. Review ghi rõ METHOD7c6b8a8 vsPAYLOADSOURCE925c544; old925campaign vẫnINCOMPLETE. ReportPI3B_READY_OBSERVER_DEVICE_20261115.md. Đang chuẩn bị ONEfunctional material40 dưới tagqa-pi3b-nms-predecessor-material-20261115, cùng19Pythonbytes/no timing, standingfiniteQAauthorization; không dùngsleepingPASS/ngoạilệhẹp làmapprovalfullNMS. SSHOPEN/no retry.
- **15/11 whole-session controls chỉ host:** `studies/pi3b_nms_trial_runtime_20261115` có53testmới/combined199PASS; enginefull20/smoke2, warmup/reference/sentry/pairlifetime chuẩn bị nhưng chưa nativeworker/provider/admission/auditor/scientifictag. Đã sửa lỗi factory giữmaterial saucontext trướcreference, logregression giữnguyên; Pythonweakref không phảiRSS. READYproposal`qa-pi3b-ready-observer-20261115`/7c6b8a8 vẫnCHỜngoạilệngườidùng, goalcontinuationKHÔNGapproval/no newnative. Report `docs/reports/PI3B_NMS_TRIAL_RUNTIME_PREP_20261115.md`; xemPROGRESScuối trước bước tiếp, khôngrunDRAFT/model khi thiếugate.
- **15/11 integrated supervisor native QA đã đóng, CHƯA ĐẠT:** tag `qa-pi3b-nms-predecessor-supervisor-20261115`/`925c544f618491e5b21a3621d77804a10686d111`, sau user mở lại Tailscale đã deploy đúng23file rồi ONEdriver chỉ mở normal01. ClientREADYquery timeout25s; normalpayloadexit0/restore+independentreadbackPASS/8originalSHAremote-local-remote, nhưng liveREADYobservation thiếu nên qualification5case KHÔNGPASS,4casekhácNOT_STARTED. No retry/QA02/tăngtimeout/functionalactivation; rootcauseUNKNOWN. Report `docs/reports/PI3B_NMS_PREDECESSOR_SUPERVISOR_DEVICE_20261115.md`. Source/tag/raw/baselines giữnguyên, SSHOPEN. Nextcodeoffline/proposal review trướcnewnativequalification, khôngrunDRAFT/material/model.
- **15/11 integrated predecessor core:** `studies/pi3b_nms_predecessor_20261115` có51hostfunctional/fakeclocktestsPASS, explicitresourcesetup loại lazyimportkhỏicallpath; scheduler3600/360 fixed, immediatepair/lifetime, truekernel-inputcapture giữstride/offset/uncappedkeep vàfinitecacheparity. Chưa native40case/worker/guard/supervisor/reference/sentry/analyzer/PREREG/timing. Authoritativecorelock`engineering_lock_v2.json` PREPARED_CORE_NOT_RUNNABLE/flagsFalse; initialversionmetadata0.1.6 giữlịch sử, importedhostTV0.28.0+cpu, PiTV0.29.2+cpu, nms.pySHA322giốngkhôngchứngminhCppbackendequivalence. ReportPI3B_NMS_PREDECESSOR_CORE_20261115.md. Khôngrundraft/oldtags; NEXT completeintegratedworker+finiteQA beforetiming.
- **15/11 light observer API:** tag `qa-pi3b-nms-light-api-20261115`/`f7258a5e24a23fce475e4e058bb73e657436c334`,25fakeclockhosttests+ONE2-samplenativeAPI PASS. RUSAGE_SELF+RUSAGE_THREAD/CPUclocks/PIDTID schema+delta verified; nativeNEVERcalledmeasure()/nooverhead/NMStiming. Sourcef725haslazyimportresource atfirstsample; initialnofilesystemdescriptionwasTOOBROAD, recordedreport/DEVIATIONS, doNOTclaiminvariantqualified. Futuretracercopy mustbindresourceatsetup+regression/integrationQA, keepf725immutable. `DRAFT_PI3B_NMS_PREDECESSOR_20261115.md` concrete3predecessors×wrapper/kernel-call/sham×2observer×A/B×5rep, full20=3600targettrials isNOTregistered/runnable; missingwarmup/reference/sentry/supervisor/materialQA beforePREREG. ReportPI3B_NMS_LIGHT_API_QA_20261115.md; SSHOPEN/noQA02.
- **15/11 staged-pool/kernel metadata:** tag `qa-pi3b-pool-stages-20261115`/`7c019497a9f3a6d2c4245dfd20a14126270cc11f`,45hosttests+ONE11-stageQA PASS. TID census1→4sauNumPyimport→7sauTorchsetintraop4→10sauTorchones, allaffinity0–3; temporalnotlibraryownership/NMScause. Bootcmdline `cgroup_disable=memory`, matching-releasebootconfigMEMCG=y/PSIdefaultdisabled, rootmemorycontrollerabsent; parent system.slice subtree_control=pids explains leafcpu.maxmissing (rootcpu+pids,parentcpu.maxmax100000). No boot/controller changes/reboot; missingcountersnot0. Report `docs/reports/PI3B_POOL_STAGES_QA_20261115.md`. NEXT light process/thread observer+sham/matchedpredecessor before science; fullinventory/procmaps outsideoperatorbracket. SSHOPEN/noQA02.
- **15/11 NMS observer engineering:** tag `qa-pi3b-nms-observer-service-20261115`/`03999b202eb802ef9073a476395c83943980121a`, 31hosttests+ONEservicefunctionalQA PASS. Selfpool1→10TID sauTorch/mm512; cấu hìnhintraop4/interop1, tấtcảaffinity0–3, KHÔNG suy10activeworkers/parallelutilization. Actualservice/ancestor/root inventory đã có, nhưng memorycgroupfiles vẫnUNAVAILABLE và leafcpu.maxvắng; rawkhôngđổi0. Xem `docs/reports/PI3B_NMS_SERVICE_POOL_QA_20261115.md`. Chưashamoverhead/matchedpredecessor/NMSmechanism, không timing từ engineeringtag/không QA02. Governorondemand/swaps giữnguyên, SSHOPEN.
- **15/11 RSS USB-present full đã đóng:** tag `prereg-pi3b-renderer-memory-usb-20261115`/`70c398ae52540e873dca0f5dd447e97bc7d00958`, đúng360/360freshprocesses/20ảnh, quality+restorePASS. Candidatepreallocate/directcopy16M/native32M whole-process high-water RSS primaryadv geom0.8755043265545107, CI[0.867515845345165,0.8838846368082481]; AA/MDEcảclean+advPASS. Xem `docs/reports/PI3B_RENDERER_MEMORY_USB_FULL20_20261115.md`. Đây là cache-only/no modelresident, không renderer-only peak/latency/DoS hay cứuNMSFAIL. SSHfrontend255 nhưng cùngsystemdinvocationtiếp tục, state-onlywaitđếnterminal; không restart. Không chạy lại launch_full.py/full02. SSDgắn/idle/unmounted, SDpaths, SSHOPEN. Mọi protocol âm cũ giữ nguyên.
- **15/11 cấu hình USB chủ đích:** người dùng xác nhận cắm SSD để bổ sung dung lượng. Metadata chỉ đọc nhận ADATA SP900 qua SupTronicsX89 (sda+sdb); tại lúc kiểm chưa mount sda1, workspace vẫn trên thẻnhớ179:2. Không tự eject/tháo ổ, mount/format hoặc chuyển workspace. RSS-V1 tag289c2e3 dừng guardUSB trước childđầu tiên,0/36RSS, fullhủy/no retry; giữFAIL nguyên. Thiết kế tương lai nếu cóUSB phải ghi rõ khác điều kiện, bind topology/I/O/materials và cóPREREG riêng; không sửa cổng của protocol đã đóng. Xem `docs/reports/PI3B_RENDERER_MEMORY_V1_SMOKE_20261115.md`.
- **Kết quả full20 sau pilot đã đóng:** tag `prereg-pi3b-full20-after-pilot-20261114`/`aa6b666f13160bffe13286ec2ed7c1e75f51f0ba`. Main4luồng20ảnh720timings PASS toàn bộ cổng và restore; H1geom1.79807662737513, H2cap/adv0.728911250847867, raw/CI ở `docs/reports/PI3B_FULL20_RESULTS_20261114.md`. Stage20ảnh705timings đủ nhưng NMS A/A/MDEFAIL, MASKcontrol riêngPASS nên jointstageFAIL; PI1hủy chưa chạy. Không full02/retry/loại ảnh77. Hai protocol âm cũ giữ nguyên. Có estimate toàn trình ARM đạt trong điều kiện600MHz đã khai báo, chưa có component mechanism đạt/DoS. SSH vẫn mở. Tối ưu renderer chỉ chuẩn bị riêng sau baseline; không tự mở campaign mới vì kết quả phụ FAIL.
- **Phê duyệt tiếp sau pilot v2:** khi được hỏi cụ thể về protocol full20 mới giữ cổng full/giữ smokeFAIL/không đo lại smoke, người dùng trả lời "với cả làm hết những gì có thể làm tối ưu và tối ưu cho số liệu tốt nhất đẹp và khó khăn gì ghi ra luôn". Tiếp tục theo proposal full20 mới; ghi minh bạch thiết kế sau pilot, giữ ngưỡng và toàn bộ âm tính. V2 đã đóng vì MDE n2FAIL, không mở full hoặc sửa source dưới tag đó. Ưu tiên tối ưu độ tin cậy/bộ nhớ/chi phí ngoài clock; biến thể thuật toán thay baseline phải là nhánh so sánh có protocol riêng sau baseline, không chọn số đẹp.
- **Cho phép mới của người dùng14/11:** "Còn những gì thiếu cứ làm hết cho đầy đủ và chi tiết như việc đã làm với phàn cuda" sau khi đã hỏi sửa runner. Tiếp tục source v2, host/device QA, kiểm soát swap tạm thời có khôi phục, PREREG/tag mới và gói đo hữu hạn khi đủ điều kiện. Không cần xin lại quyền sửa code đã được xác nhận; không sửa hoặc retry protocol cũ, không đổi nguồn/turbo/cài gói hay nới cổng để kiếm PASS. Ghi rõ mọi thay đổi sau khi đã thấy full01. Việc đo vẫn phải theo protocol/tag và máy rảnh; không tự chuyển sang thí nghiệm khác khi FAIL.
- Pi3B Rev1.2, Wi-Fi lỗi dùng Ethernet, OS Lite64-bit trixie, SSH `tanh@192.168.10.11` qua Tailscale subnet, khóa `$env:USERPROFILE\.ssh\pi_spongepi`; venv `~/sponge-venv`, workspace `~/sponge-sim/pi3b_600mhz`. Giữ strict host-key checking. Không tự sửa nguồn/governor/swap hay source để cứu phiên.
- Protocol `prereg-pi3b-600mhz-20261114`/`c80cf8163e71e643acd2708f368f06ba6f349168`: primary4luồng20ảnh hoàn tất720timings nhưng swap bật lại từ khối6 → quality_pass=false. PI1 và stagesPI4 dừng ở precondition swap, timing0; đây là lỗi cổng cấu hình, KHÔNG được chạy lại theo ngoại lệ hạ tầng. Không tạo full02 dưới tag cũ. Cần hỏi trước thay đổi code sau tag như `HANDOFF_CODEX_PI3B_20261114.md` yêu cầu.
- Mọi raw/full/smoke đã lưu nguyên ở `sponge-sim/results/pi3b_600mhz_20261114/runs/` với21 SHA khớp hai phía. Số full01 chỉ báo chẩn đoán; không dùng smoke thay stage/dose thiếu, không quy đổi1.2GHz hoặc kết luận DoS. Giữ bản thảo chính đang dirty ngoài phạm vi bàn giao phân tích này.

## Quy ước báo cáo (bắt buộc cho mọi phiên, mọi báo cáo cuối việc)
Viết cho người không rành kỹ thuật đọc hiểu ngay, không cần hỏi lại ai. Dùng đúng khuôn 4 mục sau, theo thứ tự:

```
## Đã xong
(mỗi dòng 1 việc, không thuật ngữ nội bộ khó hiểu)

## Phát hiện cần biết
(bất thường/rủi ro nói bằng câu thường, không chỉ trích dòng code)

## Việc tiếp theo — chọn 1 trong các cách sau
A. [mô tả] → gõ: "[tin nhắn mẫu để copy-dán]"
B. [mô tả] → gõ: "[tin nhắn mẫu để copy-dán]"
(tối đa 3 lựa chọn, luôn kèm sẵn câu để copy-dán, không bắt người dùng tự nghĩ câu lệnh)

## Đang chờ gì ở tôi
(nếu không có: "Không có — có thể làm tiếp việc A/B ở trên")
```
Số liệu vẫn phải truy được tới nguồn (quy tắc cứng số 4); nguồn đưa vào mục "Đã xong" hoặc phụ lục ngắn cuối báo cáo, không làm rối thân báo cáo.
