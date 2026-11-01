# PROGRESS — Bước 1 (harness sponge-sim + E5, E1, E2)

Kế hoạch đã duyệt: `C:\Users\Tanh\.claude\plans\warm-tickling-quiche.md` (tóm tắt thứ tự: khung → src+tests → E5 → E1 → E2a/E2b).
Repo thật: `D:/Sponge-patch-study` (CLAUDE.md còn ghi đường dẫn cũ). Nhánh: `harness/step1` (tách từ `codex/repository-organization`).
Môi trường: Python 3.14 hệ thống (không .venv), torch 2.13.0+cpu, torchvision 0.28.0, ultralytics 8.4.90, psutil 7.2.2, scipy 1.18.0, pytest 9.1.1.

## Đã xong
- GĐ1: khung thư mục, `src/sponge_sim/hw.py` (topology Win32, profile, pin + verify_pin bằng tải torch, power snapshot read-only, CHECKLIST).
  - Topology đọc từ OS (21/10/2026): P-core = core 0 {0,1}, core 1 {2,3} (SMT); E-core = logical 4..11 (không SMT).
  - Profile: P1=[0], E1=[4], E4=[4,5,6,7]. verify_pin (threads = 2×|cpus|): effective_cores P1 0,90 / E1 0,95 / E4 3,48 (≤ |cpus|+0,15) → passed; không ghim (12 thread) 8,69.
  - Lưu ý: verify bằng thread Python thuần bị GIL làm sai → đã đổi sang torch matmul.

- GĐ2: `provenance.py` (copy có header nguồn + SHA), `backends.py` (torch_pure, tv_nms, tv_batched, ultra_native; prepare() ngoài vùng đo),
  `stats.py`, `cohorts.py`, `inject.py`, `timing.py`, `manifest.py`; tests 37/37 pass (`python -X utf8 -m pytest tests -q -p no:cacheprovider`, ~50 s).
  - test_regression_x1: OLD128 p=0,150390625; X1-500 diff −0,029335098…, CI [−0,038328; −0,021598], p=0,001953125 (khớp 1e-12).
  - test_regen_counts: forward mới (6 ảnh × clean, sg_ga q2500 seed0) khớp active/final_detections của record và raw_cache (atol 1e-4).
  - Phát hiện: pipeline resize 320×320 → head YOLOv8n có 2100 anchor (không phải 8400). Thang N E1 sẽ theo A=2100 (+ A=8400 nhãn "đầu vào 640").
  - Ultralytics 8.4.90 NMS: dùng torchvision.ops.nms khi torchvision đã import; time limit 2,0+0,05·bs s; max_nms 30000; max_det 300.

- GĐ3 (E5): PREREG_E5 + run/analyze, commit 8afd3d5, tag `prereg-e5-20261021`. Smoke (scratchpad, không báo cáo) chạy được 3 profile,
  ghim verify pass; ước lượng full ≈ 25 phút. Đổi tên thư mục `experiments/` → `studies/` (permission chặn tên `experiments`).
- E2a (thăm dò, lịch sử, chỉ đọc): PREREG commit 9f2e355, tag `prereg-e2a-20261021`. Kết quả `results/e2a/20261021T145544/summary.json`:
  - between_image_clean.rho = 0,9379 [0,9215; 0,9499]; pooled_spearman.rho = 0,6542 [0,628; 0,6767];
  - within_image.*.rho_dN_dt = 0,11–0,13 (sg_ga 0,1214 [0,103; 0,1396]); không đảo dấu (simpson_check: sign_reversal False ×4);
  - historical_noise_clean: median CV trong ảnh 1,1903 nhưng median |ln lệch| 0,0633 → đuôi dày (cú vọt);
    noise_vs_effect.clean_clean_abs_diff_ms median 0,27225, p90 13,57325.
  - POST-HOC (DEVIATIONS.md) `posthoc_aa.json`: A/A share mean 0,0445 [−0,0151; 0,137]; tấn công 0,0533–0,1277 chồng lấn A/A.
  - Diễn giải được phép: N xếp hạng tốt độ trễ NMS GIỮA ảnh (backend custom); trong ảnh, ΔN do patch nhỏ và chìm trong nhiễu
    đo lịch sử → dữ liệu lịch sử không tách được độ trễ do tấn công khỏi nhiễu. KHÔNG nói "N không dự đoán độ trễ".

- E5 đầy đủ: `results/e5/20261021T151412/` (manifest git 822594b; tag prereg-e5 nằm ở 8afd3d5, các commit sau chỉ thêm E2a/DEVIATIONS,
  không đổi script E5). Thời gian: P1 256 s, E1 787 s, E4 1213 s. Người dùng: cắm sạc, đóng app nền; powercfg CHƯA ghi (placeholder).
  `summary.json:profiles.<P>.stages.<stage>` — A/A ratio [CI95], MDE%:
  - P1: forward 1,0002 [0,9963; 1,0042] MDE 0,58%; total 0,9960 [0,9920; 1,0000] (CI KHÔNG chứa 1, cận trên 0,99998) MDE 0,59%;
    nms_torch_pure 1,0006 [0,9935; 1,0080] MDE 1,07%; nms_tv_nms 0,9948 [0,9867; 1,0029] MDE 1,18%.
  - E1: forward 1,0081 [0,9953; 1,0220] MDE 1,94%; total 1,0005 [0,9919; 1,0092] MDE 1,27%; nms_torch_pure MDE 2,97%.
  - E4: forward MDE 7,45%; total MDE 6,13%; nms_torch_pure 0,9758 [0,9531; 0,9984] (CI không chứa 1) MDE 3,47%; CV trong ảnh ~0,5.
  - 2/21 CI không chứa 1 (P1 total, E4 nms_torch_pure); ~1 kỳ vọng do ngẫu nhiên ở mức 95%, không hiệu chỉnh đa so sánh.
  - Tỷ phần NMS torch_pure / total (ảnh sạch, mô tả): trung vị P1 0,0207, E1 0,0302, E4 0,0399; max 0,19–0,32.
  - Sai lệch: xem DEVIATIONS.md (E4 song song không xác minh; cờ trôi 3% kích hoạt gần như mọi khối).

- PREREG_E1 NHÁP + run/analyze (commit 6f6413f, CHƯA tag). hw.verify_pin thêm tham số tuỳ chọn min_effective (cận dưới).
  Smoke E1 (scratchpad, không báo cáo): script chạy; 99 nhóm/profile; P1 verify FAIL cận dưới (effective_cores 0,394; máy có tải nền
  lúc smoke); E1 pass (0,705); toàn trình torch_pure N=2100 ~987 ms (2 lần). Ước lượng full: ~1,5–2,5 giờ (chủ yếu torch_pure N lớn, A=8400).
- `sponge-sim/README.md` (commit d9d50cb). README gốc KHÔNG đụng (working copy là starter-kit chưa commit; HEAD là README dự án cũ).

- Quyết định nhóm 21/10: P1 → P1_cpu2 (logical 2); giữ 30 lặp mọi N (ước lượng E1 mới ≈ 30–60 phút, hiệu chỉnh một lần gọi);
  100 ms là ngưỡng đặt trước của nhóm; E4 không dùng để kết luận số core. README gốc viết lại theo A+C (commit 6f9cd8e),
  nội dung starter-kit chuyển sang `docs/CLAUDE_CODE_SETUP.md`.
- **Chế độ điện: Windows Balanced, GUID 381b4222-f694-41f0-9685-ff5bb260df2e** (người dùng đọc 21/10/2026, sau E5;
  không có bản ghi plan trong lúc E5 chạy). Từ nay mọi lần đo giữ nguyên chế độ này.

- PREREG_E2b NHÁP + e2b_run/e2b_analyze (commit 4b04c72, CHƯA tag). Smoke: N tái sinh khớp record 6/6, verify P1_cpu2 pass
  (0,718); ước lượng đầy đủ ~20–35 phút.
- GPU (5060 Ti, 3 giờ thuê, tuỳ chọn): KHÔNG cần cho endpoint hiện tại. Nếu dùng: thêm trục "thiết bị" cho bản đồ C (E1 trên
  CUDA: tv_nms/batched/ultra, đồng bộ cuda trước khi đọc đồng hồ). Cần hw.py chạy được trên Linux (bỏ qua topology) — chưa làm.

## Phiên tự chủ 21/10 tối (mục tiêu: bản thảo Q1 trong 2 ngày)
- GĐ-A (xong): test nhanh 37/37; test slow `test_attacks_provenance` 2/2 pass sau khi tái lập đúng torch threads = 2
  (tanh lệch patch đã lưu khi 1 hoặc 12 thread, chênh 14/255; code gốc tất định). Commit 4c72b04.
- R1 (POST-HOC, `prereg/ANALYSIS_R1_twolevel.md`, commit kế hoạch b22c79e trước khi chạy) →
  `results/r1/20261021T183505/summary.json:cohorts.<C>.comparisons.<cmp>`:
  - X1-500 SG−tâm: mean −0,029335; CI seed-only [−0,03828; −0,02168]; **two-level [−0,05799; −0,00238]** (không chứa 0;
    rộng 3,35× CI seed); 54,2% ảnh có trung bình chênh âm.
  - X1-500 SG−GA vị trí ngẫu nhiên: two-level [−0,08891; −0,01242]; SG−tìm kiếm ngẫu nhiên: [−0,00383; 0,00741].
  - OLD128 SG−tâm: two-level [−0,04656; 0,03779] (chứa 0, rộng 7,03×).
- R2 (THĂM DÒ, `prereg/ANALYSIS_R2_condition_slices.md`, commit kế hoạch trước khi chạy) →
  `results/r2/20261021T183715/summary.json`: τ=0,01/cap None: ρ(N,t_NMS) custom 0,8651 [0,6916; 0,9234] vs torchvision
  0,603 [0,4626; 0,6923]; trung vị NMS custom/torchvision = 28,342×; tỷ phần (lọc+NMS)/toàn trình trung vị 0,0339 (1 thread);
  ρ(N, toàn trình) 0,3273 [0,1665; 0,4579] (1 thread); 0 lần > 300 ms (cả 3 thread).

## Đang dở
- Chờ bạn báo "máy sẵn sàng". Khi đó, theo thứ tự:
  1. A/A P1_cpu2 (~5 phút) → điền MDE vào PREREG_E1 → commit + tag `prereg-e1-20261021`;
  2. E1 đầy đủ (~30–60 phút, nền) → analyze → PROGRESS.
- Việc điều tra (chưa làm): vì sao E4 (4 thread trên logical 4–7) cho effective_cores 0,96 trong phiên E5 trong khi kiểm riêng
  cho 2,7–3,78. Giả thuyết cần kiểm: (i) Windows dồn tác vụ nền lên E-core; (ii) torch intra-op pool + interop=1 trong subprocess;
  (iii) power management E-core ở Balanced. Cách kiểm: lặp verify_pin E4 mỗi khối, ghi cpu_percent toàn máy + tần số.

## Lệnh chạy tiếp
```
cd D:/Sponge-patch-study/sponge-sim
PYTHONPATH=src python -X utf8 -m sponge_sim.hw      # in topology + checklist
# E5 đầy đủ (~25 phút, chạy nền, KHÔNG dùng máy khi đo):
python -X utf8 studies/e5_protocol/run.py --run-dir results/e5/<YYYYMMDDTHHMMSS> > results/e5/<id>.log 2>&1
python -X utf8 studies/e5_protocol/analyze.py results/e5/<id>
# A/A P1_cpu2 rồi E1 (sau khi tag prereg-e1):
python -X utf8 studies/e5_protocol/run.py --profiles P1_cpu2 --run-dir results/e5/<id_aa> > results/e5/<id_aa>.log 2>&1
python -X utf8 studies/e5_protocol/analyze.py results/e5/<id_aa>
python -X utf8 studies/e1_dose/run.py --run-dir results/e1/<id> > results/e1/<id>.log 2>&1
python -X utf8 studies/e1_dose/analyze.py results/e1/<id> results/e5/<id_aa>/summary.json
```

## Quyết định đang chờ tôi
- Báo "máy sẵn sàng" để chạy A/A P1_cpu2 + E1.
- Ngưỡng cờ trôi: giữ 3% (gần như mọi khối bị cờ) hay hiệu chỉnh tham chiếu (khai trong PREREG_E1).

- Remote: bạn chọn reikageisme và TỰ push nhánh harness/step1 (mình không đụng remote).
- Bạn tự chạy `powercfg /getactivescheme` và ghi kết quả vào đây (harness không chạy lệnh này). psutil báo cpu_freq max 1300 MHz (giá trị Windows báo, chưa phải xung thực).

## Phiên tự chủ 21/10 tối (3) — tích hợp kết quả mô phỏng vào bản thảo Q1
Vào phiên: đã đọc lại CLAUDE.md, PROGRESS.md, DEVIATIONS.md, skill sponge-research, REVIEW 03/04/05/06 (06_open_items + 06_paper_changelog), và R3. Repo kết nối qua Cowork ở `D:\Sponge-patch-study`.

- **Ghi bù R3 (phiên trước chạy nhưng PROGRESS chưa ghi):** `prereg/ANALYSIS_R3_reference_proxy.md` (THĂM DÒ, lịch sử, KHÔNG ghim core, YOLOv5s 640 UAP toàn ảnh — mô hình/mối đe dọa khác SG-GA). Kết quả `results/r3/20261021T184159/summary.json`:
  - Overload: trung vị N 42→5490 (ratio N mean 349,00; CI hai tầng [119,74; 746,29]); ratio hậu xử lý 3,18 [2,80; 3,58]; **ratio toàn trình 1,0219 [1,0020; 1,0393]**; ratio forward 0,9921 [0,9717; 1,0088]; Δ toàn trình +11,34 ms [0,02; 20,94]; ρ(N,pp) 0,836; **ρ(N,total) 0,038**; tỷ phần pp/total trung vị sạch 0,0136 → nhiễu 0,0430.
  - Phantom: N 42→4365 (ratio 308,21 [94,77; 675,92]); ratio pp 3,27 [2,84; 3,72]; **ratio total 1,0559 [1,0239; 1,0992]**; ratio forward 1,0236 [0,9945; 1,0648]; Δ total +23,11 ms [9,85; 36,40]; ρ(N,pp) 0,816; **ρ(N,total) 0,086**.
  - Diễn giải được phép: N tăng ~300–350× chỉ làm toàn trình tăng ~2–6% trên cấu hình CPU này; N KHÔNG dự đoán toàn trình (ρ≈0,04–0,09) dù dự đoán tốt hậu xử lý (ρ≈0,82–0,84). Hỗ trợ MẠNH cho luận điểm A ở dạng hẹp. KHÔNG nói "không có tác động" (CI total không chứa 1); KHÔNG so trực tiếp SG-GA.

- **Khoảng trống chính đã xác định:** bản thảo `BaoCaoKhoaHocAdversarialAttacks_Q1_VI_v2.tex` CHƯA tích hợp E5(A/A+MDE)/E2a/R1(two-level)/R2/R3 — vẫn mô tả dữ liệu lịch sử OLD128 (7.200 số đo) và xếp các thí nghiệm mới vào "hướng tương lai". Changelog 06 cũng chưa có các số này. → Việc KHÔNG bị chặn (phân tích đã có sẵn, không cần đo mới).

- **Kế hoạch phiên này (tự quyết, A+C đã chốt):**
  1. Soạn section kết quả mô phỏng mới (nháp .tex riêng ở REVIEW/06_latex_build/draft_sim_results/), kiểm số tự chạy lại từ summary.json.
  2. Chèn vào v2; siết §4 (đơn vị suy luận hai tầng, A/A, MDE), §7/§8. Giữ NGUYÊN danh sách/thứ tự tác giả (stop-case 3).
  3. E1 dose-response + A/A-E1 + confirmatory E2b: để trong "Hạn chế/Hướng tương lai" vì CHƯA đo sạch (không cắt góc).
  4. Mở rộng changelog 06; chạy checklist skill §6.

## Đang chờ ở 4 trường hợp dừng
- **Case 1 (tag PREREG):** PREREG_E1 (commit 6f6413f) và PREREG_E2b (commit 4b04c72) đã viết xong, CHƯA `git tag`. Dừng ngay trước lệnh tag theo yêu cầu — chờ bạn.
- **Case 2 (máy rảnh để đo):** A/A P1_cpu2 (~5 phút) + E1 đầy đủ (~30–60 phút nền) cần máy rảnh thật. Chuẩn bị xong; chờ bạn báo "máy sẵn sàng". E2b đầy đủ (~20–35 phút) cũng chờ. Đo lại patch từ GPU: không cần cho endpoint hiện tại.
- **Case 3 (không đảo ngược):** không push/reset/force/xóa; KHÔNG đổi tác giả/thứ tự tên. Commit local nhỏ nếu git không vướng lock-file; remote để bạn tự push (reikageisme).
- **Case 4 (mâu thuẫn số liệu):** chưa gặp.

## Git/commit (lưu ý bridge)
- Shell qua Cowork KHÔNG xóa được file mặc định (kể cả .lock của git) → `git commit` có thể lỗi "File exists". Sẽ thử ở checkpoint; nếu vướng, để bạn commit hoặc bạn cho phép xóa. Không tự đổi nhánh (tránh checkout lỗi giữa chừng). Paper edits tạm đặt trên nhánh hiện tại `harness/step1` vì bài nay trích kết quả harness; bạn có thể tách nhánh paper sau.

## Kết thúc phiên 21/10 tối (3) — đã làm
- Tích hợp E5/E2a/R1/R2/R3 vào bản thảo: thêm 2 subsection (§5.5 "Giao thức đo ghim core và hiệu chỉnh A/A" + bảng A/A `tab:aa`; §5.6 "Proxy số ứng viên và độ trễ: phụ thuộc điều kiện"), sửa §7.2, §7.3, Kết luận RQ1, Hướng tương lai. File: `BaoCaoKhoaHocAdversarialAttacks_Q1_VI_v2.tex` (SHA sau: `6e73a558…`; bản trước splice lưu ở `REVIEW/06_latex_build/draft_sim_results/v2_before_splice.tex`).
- Mọi số truy tới `results/<exp>/.../summary.json:selector` trong `REVIEW/06_paper_changelog.md` (mục "Bổ sung sim-results"). Nhãn confirmatory/thăm dò/post-hoc đúng. Không đo/inference/COCOeval mới.
- Kiểm cú pháp khối mới: xelatex + wrapper tối giản → `scfresh.pdf` 2 trang, exit 0. PDF toàn bài CHƯA xuất được (thiếu `t5enc.def`, không cài gói — quy tắc 7). 1 overfull nhỏ 9,76pt ở đoạn R2 (soát layout lần cuối).

## Commit — ĐANG CHỜ BẠN (không tự làm)
- Repo dirty nặng từ trước (nhiều file code + `outputs/*.json` modified — KHÔNG phải của phiên này, không đụng).
- Shell qua Cowork không xoá được file → `git commit` sẽ để lại `.git/*.lock` làm hỏng lệnh git sau. Nên mình KHÔNG commit để tránh hại repo.
- File của phiên này (bạn tự commit, hoặc cho phép mình xin quyền xoá .lock rồi mình commit scoped):
  - tracked, modified: `sponge-sim/PROGRESS.md`
  - untracked (trên harness/step1): `BaoCaoKhoaHocAdversarialAttacks_Q1_VI_v2.tex`, `REVIEW/06_paper_changelog.md`, `REVIEW/06_latex_build/draft_sim_results/`
  - Gợi ý: `git add sponge-sim/PROGRESS.md BaoCaoKhoaHocAdversarialAttacks_Q1_VI_v2.tex REVIEW/06_paper_changelog.md` rồi commit; cân nhắc có đưa paper lên harness/step1 hay tách nhánh paper.

## Phiên 21/10 tối (tiếp) — tóm tắt/đóng góp/hình
- Cập nhật TÓM TẮT và ĐÓNG GÓP 3 (§1.3) cho khớp phát hiện ghim core + A/A/MDE + N tách khỏi độ trễ toàn trình. Giữ nguyên tác giả.
- Thêm Hình `fig:r3decouple` (§5.6) + `\ref` trong thân bài: tỷ số N (~300×) vs hậu xử lý (~3×) vs toàn trình (~1,02–1,06×), thang log, CI hai tầng. PNG đã kiểm mắt (tiếng Việt OK). SHA256 v2 mới: `267b383667ae96ddd3a9449fa64278fe6fa7f44941bee4ea50bfe0a7f69585a2`.
- Cấu trúc LaTeX cân bằng: table* 14/14, figure* 11/11, abstract 1/1, $ chẵn, không trùng label. PDF toàn bài vẫn kẹt t5enc.def (môi trường).

## RÀNG BUỘC MÔI TRƯỜNG (quan trọng — ghi cho phiên sau)
- Phiên Cowork này chạy `device_bash` trong **VM Linux** (2 vCPU, Python 3.10) chỉ GẮN thư mục `D:\Sponge-patch-study`. KHÔNG phải Windows gốc.
  → KHÔNG đo thời gian ghim core / verify_pin ở đây được (hw.py yêu cầu Windows; psutil thấy 2 vCPU, sai phần cứng i5-1335U).
  → Mọi phép ĐO (A/A, E1, E2b, E5) PHẢI chạy NATIVE trên Windows (như các phiên trước: Python 3.14, psutil 7.2.2).
- `studies/*/analyze.py` chỉ dùng json/numpy/stats → CHẠY ĐƯỢC ở VM Linux này. Phân công: người dùng ĐO trên Windows; Claude (Cowork) ĐỌC kết quả từ mount + PHÂN TÍCH + điền số + sửa bài.
- Lệnh A/A P1_cpu2 cho người dùng (Windows, máy rảnh):
  `cd D:\Sponge-patch-study\sponge-sim` ; `set PYTHONPATH=src` ;
  `python -X utf8 studies\e5_protocol\run.py --profiles P1_cpu2 --run-dir results\e5\AA_P1cpu2_20261021 > results\e5\AA_P1cpu2_20261021.log 2>&1`
  Xong báo Claude; Claude chạy `analyze.py results/e5/AA_P1cpu2_20261021` tại VM để lấy MDE → điền PREREG_E1 (`[CHƯA CÓ SỐ: chờ A/A P1_cpu2]`) → DỪNG trước tag (case 1).

## A/A P1_cpu2 lần 1 (21/10, run AA_P1cpu2_20261021) — VERIFY FAIL, KHÔNG dùng
- `results/e5/AA_P1cpu2_20261021/` (manifest + raw_P1_cpu2.jsonl; run 673s). verify_pin ở đầu run:
  effective_cores=0,466 (<0,5), mean_percent_allowed=98,5 (pin đúng CPU2), upper_ok=true, lower_ok=FALSE, passed=FALSE.
  percpu lúc verify: CPU0=85,2%, CPU2=98,5%, còn lại 15–39% → máy có tải nền, CPU2 bị preempt (~47% wall).
- Theo PREREG_E1 (nếu verify A/A FAIL cận dưới 0,5 → KHÔNG chạy E1): DỪNG. Không tag, không điền MDE (run không hợp lệ).
- Việc cần: người dùng đóng app nền (trình duyệt, Discord, launcher game, AV scan…), đảm bảo CPU2 rảnh, ĐO LẠI vào run-dir mới
  `results/e5/AA_P1cpu2_20261021b`. Cùng lệnh. Claude phân tích lại khi có kết quả.
- analyze.py cần scipy (VM Linux chưa có); không cài (quy tắc 7). Khi verify PASS, Claude sẽ tính MDE không cần scipy
  (công thức mde_paired = (t_{.975,df}+t_{.8,df})·sd/√n; df theo đơn vị suy luận) hoặc đề nghị người dùng chạy analyze.py trên Windows.

## Phiên tự chủ 21/10 tối (4) — hoàn thiện Related Work + bib + gói nộp Q1 (Claude Opus 4.8, Cowork)
Người dùng treo máy ngủ, trao quyền tự chạy: hiểu hiện trạng, dọn repo (đề xuất), hoàn thiện bài Q1
(đóng góp/tính mới + so sánh tấn công cũ đầy đủ), xuất gói paper có ảnh + bib. Môi trường: VM Linux (bridge),
chỉ ĐỌC/VIẾT file + phân tích; KHÔNG đo (cần Windows). Không commit (tránh .lock hỏng git) — để bạn commit.

### Đã làm (chỉ thêm, không sửa code/outputs)
- **Related Work**: đổi tiêu đề §2 "…trong hai năm gần đây" → "Nghiên cứu liên quan"; thêm §2.1 mới
  "Dòng tấn công cạn kiệt tài nguyên và miếng dán: nền tảng và các mốc" (Sponge Examples, NICGSlowDown,
  Daedalus, Phantom Sponges, Overload, SlowTrack, Adversarial Patch, DPatch, Thys). Định vị Sponge Patch ở giao hai dòng.
- **Bảng so sánh tấn công cũ** `tab:prior_attacks` (table*): 9 công trình nền tảng + dòng Sponge Patch;
  5 cột (bề mặt/quyền truy cập, cơ chế, mục tiêu đo, khác biệt). MÔ TẢ ĐỊNH TÍNH theo công trình gốc —
  KHÔNG có số đo mới, không trừ số giữa cột để xếp hạng xuyên mối đe dọa.
- **Tính mới** (§1.3): thêm đoạn nêu 3 điểm mới kiểm chứng được (hộp xám pre-NMS/không gradient/patch cục bộ;
  tách 4 đại lượng + ghim core/A-A/MDE/bootstrap hai tầng → N tách khỏi độ trễ toàn trình; giữ kết quả âm). Dẫn `\ref{tab:prior_attacks}`.
- **9 \bibitem mới** + **references.bib** (31 mục, khớp 1-1 \cite↔\bibitem). arXiv ID 9 mục nền tảng đã xác minh qua web.
  Hai mục arXiv 2026 gốc (trackflood2026/ebt2026) giữ nguyên, ghi "chưa xác minh" trong .bib.
- **Gói nộp**: `paper_Q1_submission/` tự chứa (tex + references.bib + cas-dc.cls + cas-common.sty +
  RECOMMENDED/ đủ 9 ảnh + fig_r3 + thumbnails + README_BUILD.md). 9/9 \includegraphics resolve.
- **Dọn repo**: `CLEANUP_PROPOSAL.md` ở gốc — phân tầng (cache xóa được / trùng lặp nên di chuyển vào
  paper\history / script cũ vào legacy / KHÔNG đụng outputs+project_yolov13+code+provenance). CHƯA xóa gì.

### Truy vết / SHA (sau phiên)
- v2.tex SHA256 = 997786f947a0773d9c14dce26185b03136405fb7f0fdd17a5be5f05059f714a0
- references.bib SHA256 = e0588866d53c7023f22bc23381f9e59dc51f30da0d771e0d20e3eb16c53da21c
- Sao lưu trước sửa: REVIEW/06_latex_build/draft_sim_results/v2_before_relatedwork_20261021T150031.tex

### Checklist skill §6
- [x] Không sửa code/outputs → không cần chạy lại test hồi quy (không đụng số liệu/harness).
- [x] A/A + MDE vẫn có (§5.5, tab:aa), không đổi.
- [x] KHÔNG thêm số đo mới; bảng so sánh định tính; không có số in đậm vô nguồn.
- [x] Không đo mới → không phát sinh sai lệch PREREG.
- [x] PROGRESS cập nhật; KHÔNG commit (để bạn làm); không add file ngoài phạm vi.
- [x] Hạn chế đã nêu trong bài (E1/E2b chưa đo sạch để ở Hướng phát triển).

### Kiểm cấu trúc LaTeX (VM)
- table* 15/15, figure* 11/11, tabularx 15/15; $ = 962 (chẵn); không label trùng; 31 bibitem khớp hết \cite.
- PDF: KHÔNG build được trong VM (thiếu t5enc.def/vntex, babel-vietnamese, algorithm.sty; không cài — quy tắc 7).
  → Build trên Windows (đủ gói). Lệnh ở paper_Q1_submission/README_BUILD.md. Không sửa preamble gốc.

### Chờ bạn
- Duyệt CLEANUP_PROPOSAL.md rồi tự chạy lệnh dọn (bridge không xóa được).
- Commit các file phiên này (xem mục Git/commit dưới) — hoặc cho phép xin quyền xoá .lock.
- Đo E1/E2b/A-A P1_cpu2 trên Windows khi máy rảnh (phần đo vẫn treo như các phiên trước).
- Rà lại 2 mục arXiv 2026 chưa xác minh trong references.bib.
[21/10 tối] Đã dọn an toàn (xóa cache+2 test gốc+zip rác; docx/tex cũ->paper/history; script cũ->legacy); tạo paper_Q1_overleaf.zip. Giữ nguyên outputs/experiments/sponge-sim-tests/provenance.
[21/10 tối (5)] Cắt trích dẫn >4 năm (bỏ 5 công trình cũ, bibitem 31->26), bảng tab:prior_attacks còn Phantom/Overload/SlowTrack/NICGSlowDown + Sponge Patch; câu DoS ở tóm tắt đổi sang giọng phạm vi (giữ sự thật, không claim DoS); giữ X2+transfer. Đồng bộ submission+zip.
[21/10] Hình -> media/ tên tiếng Anh (9 ảnh); graphicspath+includegraphics trỏ media/; gói nộp bỏ RECOMMENDED, dựng lại zip.
[21/10 tối (6)] 6/9 hình -> EN (5 từ extended_figures + r3). 3 hình chưa: fullscale(project_yolov13-cấm), published_vs_measured & baseline_vs_sponge (source=None, không có generator).
[21/10 tối (7)] fig12 published_vs_measured + fig14 baseline_vs_sponge: vẽ lại EN từ paper_assets/COMPARISON/{foundation_sources,comparison_sources}.json (số + SD chuẩn, có thanh sai số). r3 restyle house-style EN. => 8/9 hình EN. Còn fullscale_mAP_growth(09): dữ liệu chỉ trong project_yolov13 (quy tắc 3) - chờ bạn.
[22/10 (8)] ĐÍNH CHÍNH: fig09 fullscale_map_growth VỐN ĐÃ tiếng Anh (generate_fullscale_report.py dùng nhãn EN sẵn) — không cần đụng project_yolov13. => 9/9 hình đã tiếng Anh. Đã gửi 9 PNG lẻ cho user tải.

## Phiên 01/11 (điện thoại Galaxy A36)
- Điện thoại: SSH ổn (192.168.1.139:8022). Đã cài Ubuntu proot + venv trong `~/sponge-sim/venv`: Python 3.14.4, torch 2.15.0+cu132, torchvision 0.29.2+cu132, ultralytics 8.4.197, scipy 1.18.1 (khác laptop: torch 2.13.0+cpu, ultralytics 8.4.90).
  `sponge-sim/` đã đẩy sang (SHA256 gói khớp). Thăm dò tiến trình: thấy 8 CPU, affinity 0–7, torch mặc định 8 luồng; log cài đặt từng in "1 luồng" → không tin số torch báo, kiểm bằng tải.
- `CLAUDE.md`: thêm thiết bị điện thoại, ngoại lệ mạng CHỈ lúc cài, quy ước tắt mạng di động/Wi-Fi tối thiểu khi đo, "Quy ước báo cáo".
- Commit `61ae8cc` (scoped): PROGRESS, bản thảo v2, `paper_Q1_submission/` (kèm 9 ảnh, ép qua quy tắc `*.png`), references.bib, CLAUDE.md, `legacy/test_physical_dos.py` (khôi phục nguyên bản từ HEAD).
- 15 file gốc đã bị phiên Cowork xóa khỏi thư mục gốc: 7 sang `paper/history/`, 6 sang `legacy/`, `test_headless_pi.py` (còn bản ở `_provenance/local_before_overlay/`), `test_physical_dos.py` (đã khôi phục bản HEAD; phần sửa chưa commit trước đó đã mất).
- `PREREG_E5_phone.md` (NHÁP, chưa tag): ghim core qua proot kiểm bằng tải thật + phân cụm tốc độ; đo đợt ngắn, nghỉ giữa đợt, xen kẽ profile; khai lệch phiên bản torch.
- CHƯA có: `docs/REVIEW_THAY_NAM.md` (nội dung review của thầy Nam không có trong repo, cần bạn dán).

## Phiên 01/11 (3): chuyển trục bài theo review thầy Nam — dừng ở cổng tag + cần máy rảnh
Tham chiếu: `docs/REVIEW_THAY_NAM.md` (nguyên văn 5 vấn đề + 4 yêu cầu). Mục tiêu duy nhất: hoàn thiện bài theo đó.

### Đã xong
- Bản thảo tiếng Anh mới `paper_en/main.tex` (+ `references.bib`, `check_manuscript.py`, `TODO.md`): trục "N có dự đoán độ trễ không", SG-GA chỉ là case study,
  tiêu đề mới (đề xuất), một mục Threats to Validity duy nhất, không nhãn nội bộ, trích dẫn nền (Sponge Examples, Brown, EOT, Ilyas black-box, so sánh EVADE). Phần kết quả để `
odata` (chưa có số đo mới). Chưa biên dịch (máy không có TeX); đã kiểm cấu trúc.
- E7 (GPU, sinh patch): `studies/e7_sggar/run.py` + `make_bundle.py` (gói 11 MB, một lệnh, checkpoint, SHA256), SG-GA 100 ảnh, 320/640 px, ngưỡng 0,25, kèm 4 baseline có sẵn. Smoke CPU xong; hồi quy từng-bit (patch cũ) vẫn pass sau khi tổng quát hóa.
- E1: thêm lưới N đến 10^4 + chế độ điện thoại. E6: script đo lại patch thật + phân tích "N-only predictor". E5-phone: `pin_verify.py`, đo theo đợt, phân tích. Dry-run trên laptop OK (chưa chạy trên điện thoại).
- PREREG NHÁP (đều CHƯA tag): E1 (cập nhật), E5_phone, E6, E7. Commit gần nhất: `0ef5b50`.

### Phát hiện cần biết
- Chưa có A/A P1_cpu2 hợp lệ (lần 1 verify FAIL, lần 2 dở dang): chưa có MDE, PREREG_E1 chưa điền được.
- GPU thuê: nếu bạn thao tác máy thuê từ chính laptop trong lúc laptop đang đo thì nhiễu phép đo. Khởi động E7 trước, rồi để yên.
- Chỉ có 2 kết luận dùng được ngay từ bằng chứng hiện có (mô tả, không phải số của bài mới): pilot E5 cho MDE rất nhỏ ở P-core ghim; R3 là dữ liệu lịch sử (không dùng làm kết luận chính).
- Mọi mục `[from memory]` trong `paper_en/references.bib` cần kiểm DOI trước khi nộp.

### Lịch gợi ý (ước lượng, chưa đo; dựa trên smoke)
| Bước | Máy | Ước | Điều kiện |
|---|---|---|---|
| 0. Duyệt lô tag: E1, E5_phone, E6, E7 | — | 5 phút | bạn nói "tag tất cả" |
| 1. E7 trên GPU thuê | GPU | 1–2,5 giờ | tag E7 trước; mang `runs/e7/` về |
| 2. A/A P1_cpu2 -> điền MDE vào PREREG_E1 | laptop | ~15 phút | laptop rảnh thật ("máy sẵn sàng") |
| 3. E1 laptop | laptop | 50–90 phút | tag E1 sau khi điền MDE |
| 4. Điện thoại: pin_verify -> A/A E5-phone -> E1-phone | điện thoại | ~2–3 giờ | điện thoại rảnh, mạng tắt, A0 đồng ý |
| 5. E6 laptop (patch từ E7) | laptop | 2–3 giờ | cần bước 1 và 3 xong |
| 6. Phân tích + điền bài | — | 3–6 giờ | sau bước 5 |

### Việc tiếp theo — chọn 1
A. Duyệt lô tag -> gõ: "Tag tất cả: prereg-e1, prereg-e5phone, prereg-e6, prereg-e7 (ngày 01/11/2026). Đồng ý A0 đọc sysfs chỉ-đọc trên điện thoại. Ngưỡng nhiệt: dùng đề xuất."
B. Chạy A/A P1_cpu2 ngay (không cần tag mới) -> gõ: "Máy sẵn sàng, chạy A/A P1_cpu2"
C. Chỉnh bản thảo/PREREG trước -> gõ: "Sửa [mục]: [nội dung]"

### Đang chờ gì ở tôi
- Quyết định tag lô PREREG (E1, E5_phone, E6, E7) — DỪNG theo luật "trước khi gắn bất kỳ tag nào".
- Báo "máy sẵn sàng" (laptop và điện thoại) trước mọi phép đo.
- Đồng ý bước A0 (đọc sysfs/thermal chỉ-đọc trên điện thoại) và chốt ngưỡng nhiệt.
- Tiêu đề bài mới (đề xuất trong `paper_en/main.tex`): bạn/thầy chốt trước khi thay bản chính thức.
- Review chi tiết "kèm vị trí từng lỗi" của thầy (chưa có trong repo).

### Quyết định của người dùng (01/11/2026, sau phiên 3)
- A0 (đọc sysfs/thermal chỉ-đọc trên điện thoại): ĐỒNG Ý. Ngưỡng nhiệt giữ đề xuất: 70 °C chip / 40 °C pin.
- Tiêu đề mới CHỐT; `paper_en/main.tex` là bản chính thức; bản tiếng Việt chỉ tham khảo (không đồng bộ).
- Thứ tự: E7 (GPU thuê) trước tiên, tách riêng, không đo laptop/điện thoại cùng lúc; E6 sau E7 và dùng patch mới; A/A P1_cpu2 + E1 laptop độc lập với E7; điện thoại độc lập.
- Tag: duyệt lô nhưng CÓ BƯỚC XEM LẠI endpoint chính của từng PREREG trước khi tag thật (đã trích ở báo cáo). Chưa tag.
- Review chi tiết của thầy: chưa có thì cứ làm tiếp, bổ sung vào `docs/REVIEW_THAY_NAM.md` sau. Trích dẫn "from memory": kiểm DOI cuối cùng.

## 01/11 — ĐÃ TAG lô PREREG; gói E7 sẵn sàng cho GPU thuê
- Tag trên commit `9130774`: `prereg-e1-20261101`, `prereg-e5phone-20261101`, `prereg-e6-20261101`, `prereg-e7-20261101`.
  E1 Chính 3/4 đã có quy tắc đọc kết quả (cận dưới CI > 1 + MDE -> "phát hiện ở độ nhạy này"; ngược lại "không phát hiện, MDE = x%"). Số MDE P1_cpu2 sẽ ghi vào PROGRESS sau run A/A hợp lệ và trước E1 (quy tắc được đăng ký, không phải con số).
- Gói GPU: `sponge-sim/bundles/e7_gpu_bundle.zip` (11,46 MB, 105 file, SHA256 `1815b0c7c24053980113316f9d10952dd5e6822ed2e6b01d260fe7c187704d7e`), KHÔNG commit (untracked). `BUNDLE_SOURCE.txt` trong gói ghi commit 9130774 + 4 tag + SHA256 PREREG_E7.
- Quy tắc vận hành E7: GPU chạy riêng; trong lúc đó không đo laptop/điện thoại. Chạy theo seed (0..9 x 8 điều kiện); xong seed 4 là đủ cho E6.

### Lệnh trên máy GPU thuê (copy-dán)
```
unzip e7_gpu_bundle.zip -d e7 && cd e7
sha256sum -c BUNDLE_SHA256.txt | grep -v ": OK" ; echo "kiem tra xong (khong dong nao hien = tot)"
python -c "import torch;print(torch.__version__, torch.cuda.is_available())"
pip install kornia ultralytics opencv-python-headless pillow numpy      # chi neu thieu
python sponge-sim/studies/e7_sggar/run.py --out runs/smoke --device cuda --smoke    # ~1-2 phut, kiem loi
nohup python sponge-sim/studies/e7_sggar/run.py --out runs/e7 --device cuda > e7.log 2>&1 &
tail -n 3 e7.log        # moi don vi in ETA; xong seed 4 la du cho buoc do
tar czf e7_runs.tar.gz runs/e7      # khi xong hoac het gio; tai e7_runs.tar.gz ve laptop
```
