# Kiểm tra độ ổn định bổ sung — 06/11/2026

## Đã xong
- Một campaign hiệu chuẩn ảnh sạch cho ba host affinity, khóa lựa chọn trước timing đầy đủ; ba phiên M6 đầy đủ20 ảnh/16 lặp; một campaign matched-load sạch cho warmup5/50/200. Không đổi xung, nguồn điện hay ngân sách tấn công.
- Source/tag: `prereg-stability-calibration-20261106`, `prereg-stability-full-20261106`, `prereg-conditioning-diagnostic-20261106`. Dataset raw20 vẫn là COCO128; không gộp với cohort val500 mới.

| Host profile hiệu chuẩn sạch | Drift flags | MDE (%) | Eligible |
|---|---:|---:|---|
| all | 1 | 0.361 | True |
| one | 3 | 0.239 | False |
| four | 3 | 0.328 | False |

Lựa chọn controls-only: `all`; SHA selection ghi trong từng manifest M6. Source: `sponge-sim/results/stability_20261106/stability_cal_20261106/selection.json`.

| Phiên M6 | Drift flags | MDE clean/attacked (%) | Ratio full-res [CI95%] | Quality |
|---|---:|---|---|---|
| 1 | 14 | 0.460/0.231 | 1.9252 [1.8677;1.9812] | False |
| 2 | 14 | 0.304/0.238 | 1.9761 [1.9141;2.0373] | False |
| 3 | 10 | 0.555/0.362 | 1.9604 [1.9006;2.0169] | False |

Các ratio trên là DIAGNOSTIC, không được dùng làm kết luận timing sạch. Ba phiên báo toàn bộ; không chọn phiên đẹp. Aggregate đúng định trước (median log-ratio theo ảnh qua cả3 phiên) chỉ là descriptive vì stable=false.

| Warmup sau matched mask load sạch | Flags | MDE (%) | Eligible |
|---|---:|---:|---|
| w5 | 4 | 0.190 | False |
| w50 | 6 | 0.252 | False |
| w200 | 9 | 0.291 | False |

Source: `.../conditioning_cal_20261106/selection.json` và `*/raw.jsonl`. selected=null, vì vậy KHÔNG mở campaign M7 hay lặp tiếp để tìm phiên pass.

## Phát hiện cần biết
- Paired A/A thấp trong khi reference tuyệt đối đổi mức; không được dùng A/A thấp để bỏ qua cổng drift đã đăng ký. Tăng warmup từ5 lên200 không giải quyết được ổn định trên môi trường này.
- NVML read-only trong matched-load cho thấy P-state1, memory13801MHz và SM khoảng2760–2775MHz tại các snapshot. Biến thiên xung nhỏ này chưa giải thích được đỉnh/đổi mức reference lớn; không kết luận “do GPU clock” chỉ từ telemetry snapshot, cũng chưa xác định được host scheduling/WDDM/cache là nguyên nhân.
- Không ghi đè các run trước; không nới cổng3%/2flags, không chọn số theo độ lớn hiệu ứng. Giữ nguyên giới hạn timing trong paper.
- Người dùng yêu cầu tăng số ảnh: cohort COCO-val500 đã khóa riêng bằng seed20261106, không giao với20 ảnh COCO128 cũ. Nghiên cứu mở rộng là counts/transfer/caps, không suy latency từ thời gian xử lý PGD.

## Việc tiếp theo — chọn 1 trong các cách sau
A. Hoàn thành và phân tích cohort val500 trên hai model → đang thực hiện theo yêu cầu người dùng.

## Đang chờ gì ở tôi
Không cần duyệt thêm. Máy thuê còn được dùng cho val500; không chạy thêm absolute-timing campaign khi chưa có thay đổi môi trường cụ thể.
