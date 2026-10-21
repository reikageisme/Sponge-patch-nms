# PREREG E1 — Đối chứng dương và dose-response tại ranh giới decoded → NMS

Trạng thái: **NHÁP, chờ duyệt** (chưa tag). Tag dự kiến sau khi duyệt: `prereg-e1-20261021`.
Script: `sponge-sim/studies/e1_dose/run.py` (đo), `analyze.py` (phân tích). Cấu hình: `CONFIG` trong `run.py`.

## Mục đích
Chứng minh testbed nhạy với tải NMS (đối chứng dương) và lập đường độ trễ theo N_tau cho từng backend × hình học × cap,
TÁCH khỏi forward. Đây là trục "backend × class-aware/agnostic × cap" của bản đồ điều kiện C và là nền cho luận điểm A:
cùng N_tau, độ trễ khác nhau theo backend/hình học thì N_tau một mình không đủ dự đoán độ trễ.
Không có patch, không quang học; ứng viên được tiêm tổng hợp (`src/sponge_sim/inject.py`).

## Phạm vi
CPU laptop ghim core (i5-1335U), tensor chuẩn bị sẵn, YOLOv8n đầu vào 320×320 (head 2100 anchor). Lưới A = 8400 (đầu vào 640)
chỉ là tham chiếu ngoài pipeline, gắn nhãn riêng, không trộn với A = 2100 trong một bảng.

## Đầu vào từ E5 (`results/e5/20261021T151412/summary.json`)
- Profile: **P1** = logical {0} (chính) và **E1** = logical {4} (phụ). E4 KHÔNG dùng: song song không xác minh trong E5
  (DEVIATIONS.md 2026-10-21 mục 1). [CHỜ DUYỆT: thay vì E1 có thể đo lại E4 với cận dưới effective_cores ≥ 2,8.]
- Mức nhiễu (MDE A/A, 80% công suất): P1 `nms_torch_pure` 1,07%, `nms_tv_nms` 1,18%, `tau` 1,28%, `total` 0,59%;
  E1 `nms_torch_pure` 2,97%, `nms_tv_nms` 2,05%, `tau` 1,67%, `total` 1,27%.
  Chênh lệch tương đối nhỏ hơn MDE của profile/công đoạn tương ứng KHÔNG được diễn giải (kể cả "không có khác biệt").
- Cờ trôi 3% ghi lại để mô tả, KHÔNG dùng để loại dữ liệu (E5 cho thấy ngưỡng này kích hoạt ở gần như mọi khối).
- Verify ghim: cận trên như E5 **và** thêm cận dưới cho profile một core: effective_cores ≥ 0,5 (P1 trong E5: 0,656; E1: 0,957).

## Thiết kế
- Lưới A = 2100: N ∈ {0, 10, 30, 100, 300, 600, 1000, 1500, 2100}, nc ∈ {80, 1}. Lưới A = 8400: N ∈ {0, 100, 300, 1000, 3000, 8400}, nc = 80.
  Điểm 600/1500 đặt trước để dày quanh vùng knee dự kiến (không chọn bằng pilot).
- Hình học: disjoint (IoU = 0, NMS giữ hết), dense_cluster (8 cụm, IoU cao), mixed (nửa/nửa). N = 0 chỉ một ô.
- Cap ∈ {None, 300} (top-k theo score trước NMS); ô cap = 300 chỉ khi N > 300.
- Backend: torch_pure (agnostic, vòng lặp Python, bản copy pipeline cũ), tv_nms (agnostic), tv_batched (class-aware),
  ultra_native (class-aware, mặc định Ultralytics 8.4.90: max_det 300, max_nms 30000, time limit 2,0 + 0,05·bs s).
- Seed tiêm: `inject_seed_base + crc32("A|N|nc|geometry") mod 100000`; SHA256 tensor ghi theo từng phép đo.
- Lặp: 3 warm-up + 30 lần/ô. Trong mỗi nhóm (A, N, nc, geometry, cap) đo xen kẽ 4 backend vòng tròn, thứ tự theo hình vuông
  Latin (seed 1023); thứ tự nhóm hoán vị (seed 1022); tham chiếu đầu mỗi 12 nhóm và cuối phiên; thứ tự profile seed 1021.
  Mỗi lần đo ghi riêng `tau_ns` (lọc tau trên đủ A hàng) và `nms_ns` (prepare() ngoài vùng đo).
- Phần B (toàn trình, thứ cấp): ảnh sạch ID 139, forward thật + ứng viên tiêm (A = 2100, disjoint, nc = 80, cap None)
  thay decoded → tau → NMS, đo trực tiếp một lần gọi; N ∈ {0, 100, 300, 1000, 2100}; torch_pure và ultra_native; 3 warm-up + 20 lần.
  Hạn chót 100 ms (chu kỳ 10 FPS, đặt trước).

## Endpoint
- **Chính 1 (đối chứng dương độ trễ NMS)**: P1, torch_pure, disjoint, A = 2100, nc = 80, cap None:
  R = median(nms | N = 2100) / median(nms | N = 10). CI95% bootstrap percentile (rút lại lần lặp trong từng ô, 20.000, seed 20261021).
  Đạt nếu cận dưới CI > 1,0107 (1 + MDE P1 nms_torch_pure).
- **Chính 2 (đối chứng dương vượt hạn chót)**: P1, phần B, torch_pure, N = 2100: tỷ lệ lần lặp có total > 100 ms, kèm CI Wilson.
  Đạt nếu ≥ 50%. Không đạt thì báo nguyên trạng: testbed không tạo được deadline miss ở mức tải tối đa mà head 320 cho phép.
- **Phụ (mô tả, không p-value)**, theo profile × backend × hình học × nc × cap:
  (a) đường median nms theo N, CI bootstrap theo lần lặp; (b) độ dốc log–log trên N ≥ 100 kèm CI bootstrap: chỉ mô tả, KHÔNG suy bậc
  phức tạp; (c) tỷ số backend / tv_nms tại cùng N (cùng đầu vào); (d) tỷ số hình học: disjoint / dense_cluster tại cùng N, backend;
  (e) tỷ số cap300 / capNone tại N ≥ 600; (f) tỷ số nc=80 / nc=1 cho backend class-aware; (g) phần B tại mọi N và ultra_native;
  (h) số lần nms_ns > 2,05 s (chạm time limit của Ultralytics).
- Câu hỏi A định trước (mô tả): tại cùng N_tau, khoảng chênh độ trễ giữa backend và giữa hình học có vượt MDE hay không.
  Nếu có: bằng chứng N_tau một mình không xác định độ trễ NMS. Nếu không: báo nguyên trạng.

## Tiêu chí loại
Không loại theo giá trị. Profile verify FAIL → giữ raw, gắn nhãn, không dùng cho endpoint chính.

## Smoke (trước khi đo chính)
`run.py --smoke` (2 lặp, 6 nhóm/profile) vào scratchpad, chỉ kiểm script + ước lượng thời gian; dừng chờ duyệt trước khi chạy đầy đủ.

## Đầu ra
`sponge-sim/results/e1/<run_id>/`: manifest.json, raw_{P1,E1}.jsonl, summary.json, run.log.
