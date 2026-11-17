# Kết quả phiên Codex — hướng phân đoạn, 06/11/2026
## Đã xong
- Toàn bộ phép đo mới có PREREG và tag trước chạy; giữ run thất bại, smoke và lịch sử. Nhánh `harness/step1`.
- Chốt cơ chế chọn NMS: Ultralytics 8.4.203 kiểm `torchvision` trong `sys.modules`; có import dùng torchvision.ops.nms, thiếu import dùng TorchNMS.nms. Các script cũ khác trạng thái import. M4 cùng tensor/tiền xử lý cho đầu ra khớp 40/40 records; không gọi chênh lệch giữa script là ngẫu nhiên trên cùng kernel.
- Đã chạy M2 CPU1, CPU4 và GPU, M3 nguồn + chuyển giao native YOLO26, M4 full và M4B fixed-tv full, COCO 8 tổ hợp × 5.000 ảnh, kiểm workload cap20 ảnh.

| Thiết bị/chế độ mask | Tỷ số total K300/K10 [CI95%] | MDE (%) | K* | Cờ drift |
|---|---|---:|---:|---:|
| CPU4, proto-res | 1.0910 [1.0758; 1.1071] | 2.072 | 300 | 0 |
| CPU4, full-res | 3.9505 [3.9141; 3.9957] | 1.611 | 50 | 0 |
| GPU, proto-res | 1.0465 [1.0317; 1.0604] | 1.383 | 300 | 2 |
| GPU, full-res | 1.9256 [1.9188; 1.9337] | 1.876 | 50 | 2 |

Nguồn bảng: `sponge-sim/results/confirmation_20261106/m2_{cpu4,gpu}_full_20261106/summary_verified.json:ratios,mde,k_star`; raw cùng thư mục, selector `kind=cell,image,k,retina,rep,copy`. Bootstrap ảnh20.000, seed20261106; MDE xấp xỉ t. Cả hai kiểm tải CPU4 đạt ~3,97 CPU hiệu dụng. Topology thuê chỉ lộ18 logical processors đồng nhất; không nhận là P/E hay lõi vật lý.

| Model | K sạch → K final (trung vị) | Số ảnh K≥50 | K≥100 | K=300 |
|---|---|---:|---:|---:|
| YOLOv8n-seg | 2.5 → 270 | 20/20 | 20/20 | 6/20 |
| YOLO26n-seg native | 2 → 3 | 0/20 | 0/20 | 0/20 |

Nguồn: `.../m3_native_full_20261106/{raw.jsonl,summary.json}`. Nhiễu tối ưu YOLOv8n-seg, CÙNG nhiễu chuyển YOLO26, `end2end=True` bật rõ; đếm score>0,25 trực tiếp trong `[1,300,38]`, không NMS trên YOLO26. Endpoint là final iterate, không chọn best iterate. Kết quả không hỗ trợ chuyển giao tới K cao trên native one-to-one; chưa kiểm tấn công riêng tối ưu trên YOLO26.

| Model | Phòng thủ | Seg mAP50–95 (%) | Δ so baseline (điểm %) |
|---|---|---:|---:|
| yolov8n-seg.pt | baseline | 30.2289 | +0.0000 |
| yolov8n-seg.pt | maxdet50 | 29.8509 | -0.3780 |
| yolov8n-seg.pt | prenms300 | 30.0117 | -0.2172 |
| yolov8n-seg.pt | prenms1000 | 30.2208 | -0.0081 |
| yolo11n-seg.pt | baseline | 31.8831 | +0.0000 |
| yolo11n-seg.pt | maxdet50 | 31.4786 | -0.4045 |
| yolo11n-seg.pt | prenms300 | 31.6362 | -0.2469 |
| yolo11n-seg.pt | prenms1000 | 31.8786 | -0.0046 |

Nguồn: `sponge-sim/results/coco_defense_20261106/full_remote/results.jsonl`, selector model/variant và `results.metrics/mAP50-95(M)`. Đủ5.000 ảnh mỗi lượt. Đây là metric polygon-label Ultralytics; không giả là kết quả official COCO API độc lập. `metric_inputs.npz` từng model/variant đã replay8/8, sai số tối đa 0.0. Conf mAP=0,001 khác conf attack/count=0,25 theo PREREG.

| Variant trên ảnh tấn công khóa | N vào kernel min–max | K median |
|---|---|---:|
| baseline | 1728–3744 | 270 |
| maxdet50 | 1728–3744 | 50 |
| prenms300 | 300–300 | 98 |
| prenms1000 | 1000–1000 | 198.5 |

Nguồn: `_provenance/codex_gpu_20261106/cap_full_20261106/raw.jsonl`, kind=counts,arm=attacked,variant. Chỉ là đếm workload, không khẳng định latency phòng thủ.

- Bản thảo đã tích hợp phần bổ sung trong `paper_en/segmentation_extension/extension.tex`, bảng/figure sinh từ JSON bởi make_extension.py, source map `sources.json`; figure PDF+PNG đã xem kiểm trực quan.
- Đã kiểm cấu trúc LaTeX sau mở rộng các input:31/31 citations có nguồn, không thiếu label/ref, môi trường/ngoặc cân bằng, không placeholder. Hai test mới kiểm số học và gate thiếu phép lặp:2 pass. Máy local không có TeX engine, nên CHƯA build/render PDF toàn bài.
- Backup đầy đủ `sponge-sim/results/confirmation_20261106/codex_evidence_20261106.zip` (183 files,261.796.399 bytes) có SHA/CRC xác minh, gồm tensor, native outputs, weights và run lỗi. `local_backup_verification.json` xác nhận hash replay input. Metadata/raw nhỏ được extract trong `_provenance/codex_gpu_20261106`.

## Phát hiện cần biết
- CPU1 có 10 cờ drift; M4 có 4; M4B có 3. Đều vượt cổng2. Không dùng các phiên này làm bảng timing sạch; đã giữ toàn bộ. M4/M4B không được chạy lặp tới khi có phiên đẹp.
- Kết luận chính mới được chấp nhận: mặt chi phí mask tổng hợp trên CPU4/GPU; M3 đạt K cao ở nguồn; chuyển giao native YOLO26 không đạt K≥50. CHƯA có phiên timing toàn trình tấn công thật qua cổng, nên không kết luận real-attack slowdown chính xác hoặc DoS.
- Sửa claim cũ: 16–20× không được làm headline; “YOLO26 không NMS vẫn K≈300” trước đó chưa dùng đúng inference/counting path. max_det50 không “vô hiệu toàn bộ”: K*=50 vẫn là ngưỡng phát hiện trong điều kiện full-res; cap output chỉ chặn mask, không chặn NMS.
- Hướng phân đoạn còn là nghiên cứu trên nhiễu số toàn ảnh và workload tổng hợp; chưa print-camera, chưa ARM ổn định, chưa chứng minh hiệu lực tấn công riêng lên YOLO26 native.
- main.tex đã dirty từ trước phiên. Các sửa tích hợp appendix/scope/AI declaration được giữ trong working tree; không commit toàn file để tránh gom chỉnh sửa cũ của người dùng. Nguồn extension, script, evidence và báo cáo được commit riêng.

## Việc tiếp theo — chọn 1 trong các cách sau
A. Rà nội dung nghiên cứu để quyết định khung bài hợp nhất → gõ: “Rà bài sau bộ kết quả phân đoạn mới.”
B. Build PDF và sửa layout khi có TeX engine → gõ: “Biên dịch và kiểm PDF paper_en.”

## Đang chờ gì ở tôi
Không cần duyệt thêm phép đo. Đã dừng sshd trên máy thuê sau khi backup đủ; không còn tiến trình Python đo đạc theo final readback. Người dùng cần TRẢ MÁY trên dịch vụ để dừng phí8k/giờ; dừng SSH không dừng tính tiền. Không xoá dữ liệu remote hay sửa power plan.
