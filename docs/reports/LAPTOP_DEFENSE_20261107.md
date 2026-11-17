# Phòng thủ phân đoạn trên CPU laptop — 07/11/2026

## Đã xong

Đã hoàn tất hai nhánh đã đăng ký dưới tag `prereg-laptop-defense-20261107`, commit `e0aa31370a054327454918238b1085c6a2805328`: chặn 300 ứng viên trước NMS và giới hạn 50 mask đầu ra. Mỗi nhánh so sánh với baseline mới đo xen kẽ trên **cùng tensor tấn công**, không dùng độ trễ baseline từ phiên trước. Cùng 20 cặp PGD toàn ảnh đã khóa, YOLOv8n-seg FP32 640 px, torchvision NMS cố định, i5-1335U ghim CPU2/1 luồng Torch, AboveNormal/HighQoS. Không thay pixel/attack để chọn hiệu ứng.

| Nhánh | Dữ liệu | Cổng chất lượng | Trạng thái |
|---|---|---|---|
| Chặn trước NMS 300 | Smoke 2 ảnh rồi full 20 ảnh, 3.840 lần đo full | Full 1/22 mốc bị cờ; MDE A/A baseline 0,14906148592681065%, phòng thủ 0,31469981328543437%; ghim CPU/readback/khôi phục đạt | Đạt |
| Giới hạn output 50 | Smoke 2 ảnh, 384 lần đo | 1/4 mốc bị cờ, vượt cổng smoke 0/4 | Không đạt; hủy full, không chạy lại |

Với chặn trước NMS, tỷ số phòng thủ/baseline là **0,5267729129217924**, CI95% **[0,5070065901746184; 0,5489211762237983]**. Tức giảm **47,32270870782076%**, CI95% **[45,107882377620165; 49,29934098253816]%**. Chênh lệch trung vị trung bình theo ảnh **−468,9201475 ms**, CI95% **[−510,11350656249994; −425,61318687499994] ms**. CI bootstrap theo 20 ảnh/20.000 lần/RNG20261107, không tính các lần lặp như ảnh độc lập; CI là pointwise, không phải CI đồng thời cho hai phép so sánh.

Đếm trực tiếp tại lời gọi kernel ngoài vùng timing xác nhận số ứng viên từ 1.726–3.744 giảm còn đúng 300 trên cả 20 ảnh. Số mask từ trung vị 270,5 (177–300) còn 98 (84–118). Hash prediction, số ứng viên và K của baseline khớp phiên CPU đạt trước; input giữa hai nhánh không đổi. Wrapper đếm được khôi phục trong `finally` trước warmup/timing; vùng đo dùng kernel gốc. A/A dùng cùng callable và lịch cân bằng carryover; output được bỏ giữ sau cả hai đồng hồ. Không bỏ spike/ảnh nào.

Cả 20 log-ratio phòng thủ/baseline đều âm. Kiểm sign-flip hai phía duyệt hết 2^20 dấu cho p = **0,0000019073486328125**, giá trị nhỏ nhất khi cả 20 ảnh cùng dấu. Holm trên hai phép so sánh đăng ký cho p = **0,000003814697265625**. Nhánh output không đủ điều kiện được gán p kiểm định bằng 1 chỉ để giữ kích thước họ; đây không phải kết luận không có hiệu ứng. Phép sign-flip cần giả định đối xứng/hoán đổi dấu dưới giả thuyết không; không biến 20 ảnh đầu đã biết thành mẫu ngẫu nhiên đại diện quần thể.

Nguồn chính:

- `sponge-sim/results/laptop_defense_20261107/pre300/full_01/P1_cpu2/defense_summary.json` → `quality_pass`, `aa`, `contrasts.total`, `counts`, `references`, `cpu_diagnostics`; raw SHA256 `afbc88b2723f0396d6f9e12552ce5580617edf82dcde4d5c759d5f635a62487a`.
- `sponge-sim/results/laptop_defense_20261107/out50/smoke_01/P1_cpu2/defense_summary.json` → `feasibility_pass`, `flags`, `references`; raw SHA256 `8a31e711b340c40cb0dbe4583b063430c16ad0a5d133c8c75be50ea247e75731`.
- `sponge-sim/results/laptop_defense_20261107/family_analysis.json` → `pre300.raw_p`, `pre300.holm_p`, `pre300.reduction_percent`, `out50.full_status`; protocol và `defense_stats.py` đã có trong tag trước đo.
- Mỗi run có `verification_receipt.json`: source/tag/input/lock/hash, exact schedule, counts, môi trường, journal và summary tính lại. Ngoại lệ shared `hw.py` chỉ CRLF/LF đã khai rõ từ trước; lock chứa đúng SHA byte thực thi.

Đã thêm bảng/hình/source map vào `paper_en/segmentation_extension/laptop_defense.tex`, include từ extension hiện hành, cập nhật generator để giữ include về sau. Hình được xem kiểm tra. Không sửa/stage `paper_en/main.tex` đang dirty; chưa build PDF toàn bài vì thiếu TeX engine. Hai phiên timing tấn công đạt trước được trình bày riêng tại `LAPTOP_CARRYOVER_20261107.md`.

## Phát hiện cần biết

Giới hạn output 50 không đủ điều kiện chạy full vì mốc tham chiếu đầu ảnh đầu có tỷ số **1,0376245029873103**, lệch hơn 3%. Dù timing smoke có vẻ giảm, không dùng nó làm kết luận phòng thủ hoặc so sánh xếp hạng với pre300. Giữ nguyên smoke không đạt và không tăng cỡ mẫu/đổi cổng để cứu kết quả. Pre300 full có một mốc bị cờ tại block13, tỷ số **1,0367600022682102**, nằm trong ngân sách tối đa hai mốc của full.

Đuôi độ trễ vẫn còn nhiễu: pre300 full có 50/1.920 lần baseline và 29/1.920 lần phòng thủ vượt 1,5 lần trung vị cùng ảnh; tất cả process-CPU/wall <0,75. Wall lớn nhất 3.000,0364 và 2.322,6869 ms. Không tuyên bố deadline an toàn hoặc DoS đã bị loại bỏ. Cổng kiểm trung vị không kiểm chứng toàn bộ đuôi dịch vụ. Tất cả ba run đã đo trong protocol đều khôi phục đúng 45/45 tiến trình ứng dụng, không lỗi; không còn benchmark active.

Chặn trước NMS giảm đồng thời đầu vào kernel và mask giữ lại; phép đo toàn pipeline này không tách riêng phần tiết kiệm từ NMS hay MASK. Mask vẫn tốn công do còn 84–118 mask. Endpoint là tensor đã chuẩn bị → mask native trả về, không gồm giải mã JPEG, truyền mạng, serialization, giải phóng output hoặc hàng đợi.

Đây là 20 perturbation PGD toàn ảnh đã cố định trên một laptop/một model, không phải patch nhỏ/universal/camera. Chưa tối ưu attacker thích ứng với defense, chưa đo ARM/Pi hoặc nhiều core. COCO mAP 5.000 ảnh trước dùng letterbox/conf0,001, còn timing này dùng tensor vuông/conf0,25; không ghép thành đường đánh đổi accuracy–latency đã kiểm soát. Quy mô 1.500 ảnh đếm trước không phải cỡ mẫu timing này.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Kiểm tra lại thread pool/sampler và hoàn thiện supervisor nhiệt–pin cho A36 trước tải thật → gõ: “Tiếp tục runner A36”. Có thể tiếp tục code/kiểm offline theo ủy quyền hiện có; chưa tự chạy điện thoại.

B. Thiết kế phép tách MASK/NMS hoặc CPU nhiều luồng với baseline và cổng riêng → gõ: “Tiếp tục kiểm cơ chế và nhiều luồng”. Mỗi phép đo mới cần mục tiêu khoa học và PREREG/tag riêng, không chạy lại out50 để tìm PASS.

## Đang chờ gì ở tôi

Không có cho việc code/phân tích offline. Điện thoại cần xác nhận trạng thái máy rảnh, mạng và sạc thực tế trước khi đo; máy thuê đã bị xóa, không kết nối lại. Protocol phòng thủ hiện tại đã đóng đúng quy tắc, tất cả kết quả được giữ nguyên.
