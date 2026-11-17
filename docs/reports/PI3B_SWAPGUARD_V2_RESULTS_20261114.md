# Pi 3B — swapguard v2: smoke hoàn tất, không đạt MDE

## Đã xong

**Đã sửa và kiểm cơ chế swap/khôi phục trên Pi thật. Smoke chạy hết, nhưng
không được mở full vì MDE trên2 ảnh vượt cổng đã đăng ký. Không có số full
đạt chuẩn, không chạy lại để kiếm PASS.**

Code/QA: `PI3B_SWAPGUARD_V2_QA_20261114.md`. Năm case sleeping-payload đạt;
lỗi engineering trước đó giữ nguyên. Source đo mới khóa ở tag
`prereg-pi3b-swapguard-v2-20261114`, commit
`560b3aaf657fa574240e8ab463eefc20425538d8`; lockSHA
`2041162d361e37a8a2bf045d1f58d05d181a0f16b1e13d552d7b8eb74ea00d23`.
Host59tests đạt4.88s; chưa dùng host test làm chứng nhận timing ARM.

Gốc nguồn bên dưới: `sponge-sim/results/pi3b_swapguard_v2_20261114/`.
Chép nguyên smoke_01;14file gốc SHA remote-before=local=remote-after.
Source/lock vẫn khớp sau phiên, full_01 không tồn tại, không còn worker.
Restore đạt: governor ondemand, swap/timer và helper zram active/Resultsuccess,
mọi mask đã gỡ. SSH vẫn mở. Nguồn: `protocol_status.json`,
`remote_after_smoke.json` và `runs/smoke_01/restore.json`.

### Dữ liệu smoke và từng cổng

`runs/smoke_01/pipeline_PI4/raw.jsonl`:113dòng, SHA256
`8d97e3c0ceaacc22f7fc640ccd390b952568a3c2c2b46a452b7fba337b49b7e8`.
Hai ID9/25 của tập20ảnh đã khóa;6arms×2reps×2ảnh=24timing,4reference,
72guardrecords,3conditionreadbacks,hai kiểm ghim và một dòng done.
Rawline map: `closed_smoke_audit.json:per_image.*.raw_lines`.

| Cổng | Kết quả | Đánh giá |
|---|---|---|
|Đúng ID/arms/repeats/order/source/registration|structural audit không lỗi,24timing|đạt|
|Guard/cấu hình ngoài clock|72guardrecords, không vi phạm|đạt trên các lần đọc|
|Swap tắt và mask còn hiệu lực|mọi guard SwapTotal0,/proc/swaps rỗng|đạt|
|Actual clock/governor|5snapshot actual600MHz/powersave|đạt trên các lần đọc|
|Ghim đầu/cuối|inside3.9269296501042508/3.9121155717239766,need2.8|đạt|
|Reference drift|0/4 cờ, ratio nhỏ nhất0.984610341663151|đạt|
|abs(meanlogA/A)≤0.02|0.006922236550794787|đạt|
|MDElog80%≤0.05|0.1335119103548224|**không đạt**|
|Khôi phục cấu hình|RESTORED/errors[];helperResultsuccess|đạt|

Nguồn: `runs/smoke_01/pipeline_PI4/gates.json:{audit,gates}`,
`closed_smoke_audit.json:{row_kind_counts,pin_rows,reference_rows,all_guard_swap_zero}`.
Pin nằm ở raw1/112; references raw8/17/64/109; done raw113.

Min MemAvailable ở fastguard142296kB, nhiệt fastguard cao nhất40.78C;
vcgencmd snapshot cao nhất41.3C là kênh khác. Đây đều là giá trị lấy mẫu,
không phải peakRAM/nhiệt giữa lời gọi. Nguồn:
`closed_smoke_audit.json:{min_fast_mem_available_kb,max_fast_cpu_temp_c}` và
`gates.json:gates.temp_max_c`. Không suy từ hai ảnh rằng mọi ảnh/K đều vừa RAM.

Pi3B dùng nguồn có thiếu áp, powersave600MHz. Throttled snapshots có cả
`0x50005` và `0x50000`: cờ thiếu áp hiện tại không liên tục, lịch sử vẫn được
ghi. Không nói xung600 chỉ do firmware trong mọi thời điểm; powersave cũng
yêu cầu điểm làm việc đó. Không quy đổi sang xung danh định/thiết bị khác.

### A/A, MDE và parity

MedianA/B theo từng ảnh, logratio:

| ID | Raw A | Raw B | log(A/B) |
|---|---|---|---:|
|000000000009|36,51|33,39|0.016402874846161878|
|000000000025|74,89|71,86|−0.0025584017445723028|

Meanlog0.006922236550794787, SD(ddof1)0.01340764725726188. A/A geometricratio
1.0069462506085785, CI95%[0.9974448681759864,1.016538140567963]; p=1 trên
hai đơn vị ảnh không chứng minh tương đương. MDElog0.1335119103548224,
ratio1.1428348776229462; đây là mức hiệu ứng có thể phát hiện theo xấp xỉ80%
công suất, **không phải hệ thống đã được đo là nhiễu14%**.
Nguồn: `runs/smoke_01/summary.json:pipeline_PI4.{aa_cleanA_over_cleanB,mde_log_80pct}`;
`closed_smoke_audit.json:{per_image,aa_sd_log,mde_ratio}`.

Nτclean/adv và Kclean/adv/cap trùng laptop trên2/2ảnh; predictions byte-equal
0/4; maxabsKdiff0. Nguồn: `summary.json:pipeline_PI4.parity_vs_laptop`.
Chỉ là parity số đếm hữu hạn trên cùng ảnh, không numerical equivalence hay
khái quát sang mọi ảnh. Torch/torchvision hai máy vẫn khác phiên bản đã khai báo.

H1/H2, tỷ trọngforward **FULL20 chưa có**. Analyzer giữ các ước lượng smoke
trong summary để kiểm đường chạy; không đưa tỷ số tấn công smoke vào bài.
PI1 và stages chưa bắt đầu vì campaign dừng sau main gate66: không có NMS/MASK
full, stageA/A/MDE hay liềuK của v2. Không thay bằng smoke cũ/GPU/laptop.
Khác phiên cũ: lần này hai phụ bị hủy, không phải đã chạy rồi lỗi precondition.

## Phát hiện cần biết

Phiên lần này đã qua swap, ghim, reference và toàn bộ kiểm cấu trúc. Điểm
không đạt là độ chính xác suy luận trên chỉ2ảnh: công thức t có df=1 nên
cổng MDE rất bảo thủ. Không thể đổi trạng thái này thành PASS chỉ vì các cổng
vật lý đạt hoặc A/A trung bình gần1. Cũng chưa đủ để kết luận Pi không ghim
được, thiếu RAM hay không thể đo ổn định ở tập lớn hơn.

`analyze_closed_smoke.py` tính lại A/A/MDE từ raw, khớp analyzer. Hình
`smoke_quality_and_planning.{png,pdf}` có reference/A/A quan sát và đường MDE
**tính giả định khi giữ nguyên SD của2ảnh**, không phải phép đo ở n khác.
Điểm tính giả định tại n20 là0.008856137180298611; SD từ2ảnh rất bất định,
nên không bảo đảm full20 sẽ đạt. Không dùng đường này làm kết quả nghiên cứu.

Đây là thiếu sót của thiết kế pilot: áp cổng công suất của tập đầy đủ lên
một smoke rất nhỏ có thể chặn full dù đường đo hoạt động. Việc nhận ra điều
này SAU dữ liệu không cho phép sửa ngưỡng, đánh lại smoke hay tự chạy full
dưới tag cũ. Source/tag/raw vẫn nguyên; protocol hiện đã đóng.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Xem và duyệt proposal một protocol mới, **chỉ một full20 với ngưỡng chất
lượng full giữ nguyên**, smokeFAIL này giữ làm pilot, không đo lại smoke
→ gõ: "Duyệt protocol full20 mới, giữ cổng chất lượng và giữ smoke FAIL".

B. Đối chiếu báo cáo/raw trước khi quyết định → gõ: "Kiểm báo cáo smoke Pi".

Proposal: `sponge-sim/prereg/DRAFT_PI3B_FULL20_AFTER_PILOT_20261114.md`.
Không chọn n3/n5 chỉ vì đường giả định vừa vượt cổng, không full02 dưới v2,
không đổi dữ liệu/cap/backend để tăng hiệu ứng. Cần phê duyệt phương pháp mới
vì đây là thay đổi quyết định mở full sau khi đã thấy một cổng FAIL.

## Đang chờ gì ở tôi

Người dùng đã trả lời câu hỏi phương pháp ở A, yêu cầu làm đầy đủ/tối ưu và
ghi mọi khó khăn. Tiếp tục chuẩn bị một protocol full20 mới theo proposal;
không cần duyệt lại code/QA vốn được phép. V2 vẫn CLOSED/FAIL và chưa có full.
Số liệu đẹp được hiểu là số đo tin cậy, truy được raw; các ngưỡng full giữ nguyên.
Đã lưu đầy đủ dữ liệu/âm tính và giải thích thống kê. Máy đã khôi phục, không
cần bật lại SSH; source/QA/tag mới phải sẵn trước bất kỳ full nào.
