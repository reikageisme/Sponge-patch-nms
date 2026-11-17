# M4 smoke — 06/11/2026, không dùng làm kết quả chính trong bài

## Truy vết
- Branch harness/step1, tag prereg-m4-nms-dispatch-20261106,
  commit e16f9ed6338536ae412107f730985c7302a054c4, đặt TRƯỚC smoke.
- Runner: sponge-sim/studies/m4_nms_dispatch/run.py.
- Run: sponge-sim/results/m4_nms_dispatch/m4_smoke_20261106/.
- manifest.json chứa hash code/protocol/weights/config/images/historical attack;
  raw.jsonl có 119 dòng, kết thúc kind=done; input snapshots giữ cục bộ cả local/remote.
- summary.json chỉ là derived; analyzer và test tổng hợp được commit cùng protocol.

## Cơ chế từ source và phép kiểm cùng tensor
`ultralytics_nms_source.py` trong run là snapshot thư viện thực trên máy thuê.
`use_torchvision = prediction.device.type != "xpu" and "torchvision" in sys.modules`:
nhánh true gọi torchvision.ops.nms, false gọi TorchNMS.nms.
Manifest dispatch_before_torchvision_import=false; thư viện lúc đọc là 8.4.203
theo preflight máy thuê; hash source ghi trong manifest.
Historical diag.py/gpu_decomp.py không import torchvision; gpu_mechanism.py có.
Do đó có lời giải cụ thể cho khác biệt script: cùng API không đồng nghĩa cùng kernel.
Không gọi các số cũ là biến động ngẫu nhiên trên một backend cố định nữa.

Smoke thay DUY NHẤT kernel trong cùng wrapper Ultralytics, giữ tiền xử lý,
class offset, max_nms, max_det; tensor đầu vào cùng hash cho mỗi cặp.
Torchvision được import rõ, nhánh pure ép kernel TorchNMS.nms, restore ngay sau gọi.

| Ảnh | N trước NMS attacked | K clean → attacked | NMS pure (ms) | NMS tv (ms) | mask full clean → attacked (ms) | total tv full clean → attacked (ms) |
|---|---:|---|---:|---:|---|---|
| 000000000009 | 2130 | 6 → 222 | 97.4860 | 0.8255 | 0.3887 → 4.9186 | 6.2451 → 11.6614 |
| 000000000025 | 2411 | 2 → 231 | 110.7521 | 0.9144 | 0.3385 → 5.0989 | 6.5059 → 12.0238 |

Nguồn: raw.jsonl lọc kind=counts hoặc timing, image=<ID>.jpg,
arm=clean/attacked, stage=nms_pure/nms_tv/mask_True/total_tv_True;
trung vị 3 lần lặp trong từng ô. Bảng derived tương ứng:
summary.json:counts và stages.<arm>|<stage>.image_medians_ms (thứ tự ảnh như bảng).
outputs_equal=true trong cả 4 records clean/attacked (sample hữu hạn, không suy tương đương mọi tie).
Tỷ số pure/tv trung bình nhân hai ảnh 119.5970;
total_tv_True attacked/clean 1.8577 (summary:primary_pure_over_tv và contrasts.total_tv_True).
Không cộng trung vị từng công đoạn để suy ra total.

## Giới hạn và cổng tiếp theo
- Chỉ SMOKE 2 ảnh, 3 lặp; bootstrap hẹp của hai ảnh KHÔNG là bằng chứng tổng quát.
- 2 điểm reference bị cờ (>3%): block 1 và end. Chưa vượt ngưỡng >2 nhưng không coi là phiên sạch để thay bảng chính.
- A/A MDE smoke: clean 25.05%, attacked 55.33% (n=2, xấp xỉ t rất bất ổn).
  Cổng quality_pass chỉ kiểm hoàn tất/số cờ, KHÔNG là chứng nhận đủ lực suy luận.
- Proto mask đo upsample=False để khớp microbenchmark lịch sử; không đại diện mọi default predictor.
- M4 dùng lại PGD lịch sử, không hợp thức hoá hồi tố M2/M3 hay GPU runs cũ.
- Chưa đo CPU đa luồng, COCO val đầy đủ, chặn tiền-NMS, YOLO26 endpoint; chưa sửa paper_en.
- Full đã định trước: 20 ảnh IDs trong PREREG, 15 lặp, 5 warmup. Ước tính từ smoke:
  vài phút, ~190 MiB input snapshots. Cần duyệt sau smoke theo skill sponge-research §1.4.
- Remote code/provenance hiện ở C:/sponge/m4_run.py và m4_provenance.json;
  lệnh full: python -u m4_run.py --run-dir C:/sponge/m4_full_20261106 --provenance C:/sponge/m4_provenance.json
  (python executable per-user ghi trong handoff; không chạy lại vào thư mục smoke).
- Phiên SSH đo đã kết thúc. Không còn phép đo do Codex khởi chạy đang chạy;
  giữ sshd cho lượt full sau duyệt. Khi kết thúc thuê cần người dùng trả máy.
