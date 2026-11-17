# Pi renderer — kiểm chức năng và mô hình bộ nhớ, chưa đo trên board

## Đã xong

Sau khi đóng full20, đã chuẩn bị renderer riêng tại
`sponge-sim/studies/pi3b_renderer_prealloc_20261114/`. Giữ phép nhân hệ số,
nội suy, threshold và crop; cấp phát sẵn outputuint8, chép float0/1 trực tiếp
vào output, giảm floatchunkbudget xuống16triệu pixel. Không sửa baseline,
package đang cài hoặc source/tag của bất kỳ lượt đo trước.

`baseline_ops.py` chép nguyên ba hàm từ opsSHA
`828de5d265ab91a792acae836f9380d07abda2a15a501170fc9f49d7a448688d`:
crop461–481, native513–538, scale541–578, giữ AGPL và provenance.
Test đối chiếu AST từng hàm với package đang cài, đồng thời kiểm SHA nguồn.

**12 kiểm tra chức năng đạt**, log
`sponge-sim/results/pi3b_renderer_prealloc_qa_20261114/pytest_01.log`.
Thử empty/zero logits/boxes ngoài ảnh và rỗng/noncontiguous coefficients,
các biên chunk39/40/78/79 và K300 với proto32×160×160/output640².
Ba budget được kiểm đầu ra trên các ca parameterized; tensoruint8 khớp từng
pixel, đầu vào không bị sửa. Đây là finite synthetic FP32 parity trên laptop,
không parity trên mọi input/device và không số đo hiệu năng.

## Phát hiện cần biết

**Cấp phát sẵn đơn thuần có thể làm bộ nhớ sống cao hơn.** Output toàn bộ
tồn tại ngay trong lúc nội suy floatchunk đầu tiên, còn baseline chỉ ghép
output lớn sau cùng. Đã sửa giả định “bỏ cat luôn giảm peak”; không giấu trường
hợp bất lợi này hoặc tuyên bố tiết kiệm một output là peakRSS thực đo.

| Mô hình tại K300/640², proto160² | Max tensor sống mô hình, MiB |
|---|---:|
|Baseline list+cat/chunk32M|263.671875|
|Preallocate/directcopy/chunk32M|268.359375|
|Preallocate/directcopy/chunk16M|207.421875|

Nguồn số: `static_memory.json:rows` theo `{k:300,pixel_budget}`;
công thức trong `static_memory.py:model`. Hiệu mô hình baseline−candidate16M
58982400bytes=56.25MiB; candidate32M cao hơn4915200bytes=4.6875MiB.
Bao gồm coeffs và output/chunk, **không gồm** model/input/proto/cropgrids,
allocator/threadstacks/workspaces của kernel. Nội suy có thể có cấp phát nội
bộ chưa mô hình hóa. Không dùng bảng này thay số RSS, không claim tốc độ.

Chưa chạy real-image cache parity hay workload trên Pi. Thiết kế kế tiếp cần
đo peakRSS toàn tiến trình trong freshprocess riêng từng biến thể, tách phiên
timing để không bị profiler làm nhiễu. Startup high-water RSS có thể che lợi
ích renderer; nếu không thấy khác biệt phải giữ kết quả âm. Chưa có protocol
khoa học/tag cho phép đo này. Full20 mainPASS/componentFAIL không đổi.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Review draft, hoàn thiện cache/collector/QA trước khi quyết định một phép
so sánh mới → gõ: **"Hoàn thiện phép so sánh renderer riêng"**.

B. Ưu tiên review gói số liệu full20 đã lưu → gõ: **"Check báo cáo Pi full20"**.

Draft: `sponge-sim/prereg/DRAFT_PI3B_RENDERER_PREALLOCATION_20261114.md`.
Không phải một cách chạy lại NMS/PI1 hoặc thay source để cứu cổng thất bại.

## Đang chờ gì ở tôi

Không cần thao tác cho phần code/kiểm chức năng đã làm. Mọi phép đo mới còn
phải hoàn thiện protocol và khóa tag trước; hiện chưa có tải Pi mới, SSH mở.
