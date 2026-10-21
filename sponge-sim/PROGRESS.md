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
