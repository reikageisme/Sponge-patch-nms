# Pi 3B600MHz — kết quả đầy đủ và kiểm cổng chất lượng

## Đã xong

**Pi đã chạy hết workload phân đoạn640 trên20 ảnh, nhưng phiên chính KHÔNG ĐẠT
cổng chất lượng vì swap bật lại trong lúc đo. Hai phiên phụ dừng ngay ở cổng
swap, không có timing và không được chạy lại theo ngoại lệ hạ tầng.**

Đã tiếp quản đúng `prereg-pi3b-600mhz-20261114`, commit
`c80cf8163e71e643acd2708f368f06ba6f349168`. Chép nguyên thư mục runs về laptop;
21 file khớp SHA remote/local, manifest hash phía Pi không đổi trước/sau chép.
Không sửa cấu hình, chạy thêm benchmark, đổi nguồn/governor/swap, hoặc tắt Pi.

Gốc dữ liệu dưới đây là `sponge-sim/results/pi3b_600mhz_20261114/`.
Phiên chính: `runs/full_01/pipeline_PI4/raw.jsonl`, SHA256
`83e84900fa11c9d11a8061a69d280a064f7e741f996f1d42d5666004b4170971`.
Đủ806 dòng:720 timing,20 ảnh,6 nhánh×6 lặp/ảnh,22 tham chiếu, hai kiểm ghim
đầu/cuối và dòng done. Thứ tự từng nhánh/lượt khớp seed đã đăng ký, không loại ảnh.

Đã chạy nguyên analyzer đã khóa trên full01; `runs/full_01/summary.json`
giữ `pipeline_PI4.quality_pass=false`. Analyzer tìm parity reference ở thư mục
runs, nên đã đặt một bản sao byte-identical của reference có sẵn tại đó; không
sửa analyzer. Kiểm độc lập tính lại mọi trung vị, bootstrap20000 và2²⁰ phép
đảo dấu của5 endpoint, khớp summary. Ba test nhanh của lịch/lock/liềuK đạt;
không chạy lại inference để kiểm thống kê.

### Ước lượng từ toàn bộ20 ảnh — CHỈ CHẨN ĐOÁN, KHÔNG ĐẠT CỔNG

Đơn vị suy luận là ảnh, không phải720 lượt đo. Với mỗi ảnh, lấy trung vị các
lượt; clean_total gộp12 mẫu A/B rồi lấy trung vị. Tỷ số là trung bình hình học
của tỷ số theo ảnh; không phải chia hai trung vị toàn tập. CI95% pointwise,
bootstrap theo ảnh20000 lần. Hiệu chỉnh Holm chỉ cho họ {H1,H2} đã đăng ký.

| Endpoint | Tỷ số hình học | CI95% | p đảo dấu; p Holm |
|---|---|---|---|
| H1: adv_total/clean_total |1.8047454106930743|[1.7488439384408914,1.8580617546038176]|0.0000019073486328125;0.000003814697265625|
| H2: advcap_total/adv_total |0.7259110023056329|[0.7091534498936214,0.744053345867411]|0.0000019073486328125;0.000003814697265625|
| Phụ: advcap_total/clean_total |1.3100845499827005|[1.296808651425369,1.3236369946960413]|chỉ mô tả, không thêm vào họ chính|
| Phụ: adv_forward/clean_forward |1.0038937161571846|[1.001128103148154,1.0072781922465677]|chỉ mô tả; không suy tương đương|

Nguồn: `summary.json:pipeline_PI4.{h1_adv_over_clean,h2_advcap_over_adv,holm_h1_h2,advcap_over_clean,forward_adv_over_clean}`.
Seed bootstrap tương ứng20261115/16/18/19. Hai endpoint chính đều20 ảnh cùng
dấu, nên p đạt mức nhỏ nhất2/2²⁰. Các p/CI này không vượt qua hay thay thế cổng
chất lượng. d_z lần lượt H1=8.335234287702734, H2=−5.692968149407071.

Cap trên cùng tensor nhiễu giảm thời gian theo tỷ số ghép cặp27.40889976943671%,
CI[25.594665413258898%,29.08465501063786%], **vẫn là chẩn đoán**. Không đánh giá
attacker thích nghi hoặc accuracy của cap. Nguồn phép đổi:
`derived_report_numbers.json:defense_reduction_pct,defense_reduction_pct_ci95`.

| Nhánh | Trung vị các trung vị theo ảnh, ms |
|---|---:|
| clean_total |4340.95019525|
| adv_total |8004.15041875|
| advcap_total |5697.31025775|
| clean_forward |4285.52634925|
| adv_forward |4292.0901245|

Nguồn: `summary.json:pipeline_PI4.median_ms_across_images`. Tất cả thời gian
chỉ mô tả **Pi 3B bị firmware ép600MHz do thiếu áp**, với powersave ở điểm làm
việc đã đăng ký; không quy đổi1.2GHz và không so thời gian tuyệt đối laptop/A36.

Tỷ trọng forward là trung vị của tỷ số theo ảnh, không chia các trung vị riêng:
clean0.9874712394973826, adv0.5352795934786096.
Nguồn: `summary.json:pipeline_PI4.forward_share`. Đây là hai nhánh đo riêng;
không trừ các trung vị để suy ra thời gian NMS hoặc MASK.

### A/A, MDE và từng cổng

| Cổng đã đăng ký | Kết quả | Đánh giá |
|---|---|---|
| Hoàn tất, không abort, đủ20 ảnh |done,720 timing; đủ6 mẫu/nhánh/ảnh|đạt|
| Governor powersave |mọi điểm đọc đúng|đạt|
| Xung594–606MHz |23 điểm đều600000000Hz|đạt trên các điểm đọc|
| Swap tắt toàn phiên |bật từ trước khối6, còn bật cuối phiên|**KHÔNG ĐẠT**|
| Ghim đầu/cuối |cả hai passed; mask0–3|đạt phép kiểm đã đăng ký|
| Tham chiếu bị cờ≤2 |1/22; điểm cuối ratio1.0548902072087372|đạt ngưỡng cho phép|
| abs(mean log A/A)≤0.02 |0.0015310758398949134|đạt|
| MDE log≤0.05 |0.004523353197703807|đạt|

A/A ratio0.9984700956587581, CI[0.9955733569430457,1.0013328876462824],
p=0.330322265625; không dùng p này để khẳng định tương đương. MDE80% xấp xỉ t
theo ảnh là log0.004523353197703807, ratio1.004533599002419. A/A nhỏ không sửa
được sai điều kiện swap. Nguồn: `summary.json:pipeline_PI4.{gates,aa_cleanA_over_cleanB,mde_log_80pct,mde_ratio_80pct}`.

Nhiệt cao nhất tại điểm ghi40.8C, dưới ngưỡng dừng Pi75C. MemAvailable thấp
nhất ở đầu khối134760kB. RSS lớn nhất ghi cuối khối663420928byte, không phải
peak trong phép đo. Bộ đếm swap toàn hệ thống tăng, không có tăng oom_kill
trong các snapshot. Không quy toàn bộ page fault/swap của hệ thống cho worker.
Nguồn: raw environment/done/memory, chỉ mục tại `raw_source_map.json` và
`structural_audit.json`; không dùng các snapshot để tuyên bố liên tục không
throttle/không thiếu RAM giữa hai lần đọc. Cờ thiếu áp0x50000/0x50005 là điều
kiện đã khai báo, không phải lý do FAIL được thêm sau dữ liệu.

### Parity với laptop

Cả20/20 ảnh khớp K sạch, K nhiễu, K cap; N_tau sạch/nhiễu cũng20/20. Chênh K
lớn nhất0. Tuy nhiên tensor dự đoán sạch/nhiễu trùng byte0/40. Torch trên Pi
2.15.0+cpu/torchvision0.29.2+cpu khác laptop2.13.0+cpu/0.28.0+cpu, đúng khác biệt
đã khai báo. K/N khớp trên tập này không chứng minh số học hoặc mọi tie tương
đương. Trung vị N_tau/K: sạch18.5/2.5, nhiễu2687/270.5, cap2687/98.
Nguồn: `summary.json:pipeline_PI4.{parity_vs_laptop,count_medians}` và raw counts.

## Phát hiện cần biết

### Swap bật lại khi nào?

Campaign tắt swap lúc03:44:00UTC. Journal đọc đúng cửa sổ UTC ghi systemd bắt
đầu `systemd-zram-setup@zram0` lúc04:09:19, activate `dev-zram0.swap` lúc04:09:21.
Lần ghi raw đầu thấy bật là dòng243, khối zero-based6, ảnh000000000049, lúc
04:10:52.302931UTC, SwapTotal926716kB. Vì vậy không phải chỉ bật lại lúc cleanup
cuối campaign05:13:28. Chưa xác định tác nhân khiến systemd khởi động lại unit;
không khẳng định nguồn yếu hay model gây việc đó.

Nguồn: `transfer_verification_20261114_01/read_only_swap_history_utc.json`,
`structural_audit.json:first_swap_enabled`, `raw_source_map.json:first_swap_enabled_line`.
Lần query journal đầu dùng bounds không ghi timezone nên không bao đúng cửa
sổ; đã giữ record đó và truy vấn lại với UTC tường minh. Không đổi dịch vụ/
cài đặt để tìm bằng chứng. Campaign restore governor ondemand/swap ở cuối
được giữ nguyên trong `runs/full_01/campaign.log`.

### Hai phiên phụ và quyết định không chạy lại

`pipeline_PI1.log` và `stages_PI4.log` đều báo tại run.py:132:
`RuntimeError: swap must be off for the registered condition`.
Cả hai returncode1, chưa tạo thư mục kết quả/manifest/raw, timing0. Đây là lỗi
cổng cấu hình swap, không phải ngoại lệ mất SSH/hết đĩa của mục7 PREREG. Không
chạy lại, không tạo full02, không sửa runner/lock. Dữ liệu phiên chính đã được
đọc trước quyết định này; không chọn lại ảnh/phiên theo hiệu ứng.

Analyzer ghi hai phiên phụ `missing=true` vì raw chưa được tạo; phải đọc cùng
log/status để hiểu đây là **đã thử và bị từ chối**, không phải chưa lên lịch.
`protocol_status.json` và `structural_audit.json:auxiliary` giữ trạng thái rõ.

Tách NMS/MASK, tỷ số mask_adv/clean, NMS_adv/clean và liềuK của FULL:
**[CHƯA CÓ SỐ: phiên stages_PI4 bị chặn trước timing]**. Không lấy smoke thay
full, không cộng/trừ các trung vị riêng để điền số thiếu. Phiên1 luồng cũng
không có A/A/MDE/effect đủ20 ảnh. Smoke giữ riêng trong runs/smoke_01 và không
đưa vào các bảng số trên.

### Truy vết và giới hạn

`transfer_verification_20261114_01/verification.json` lưu21 hash fetched;
`raw_source_map.json` ánh xạ từng ảnh/nhánh tới đúng dòng raw. Kiểm tính lại ở
`transfer_verification_20261114_01/{check_saved_summary.py,independent_summary_check.json}`
khớp toàn bộ endpoint, không thay estimator hoặc filter dữ liệu.

run.py/campaign.sh/analyze.py/build_lock.py/parity_ref.py khớp byte tag. Lock
deployed/working/manifest đều SHA c645656a96a8faea160143159fcad7db253f93d6664c3c19baa78ed74e117099;
blob lock trong Git tag là LF SHA48c8ceaaa7b94a01e1109c0d1828f24acdfbb41dfef84cd9c75e153d532b10ca.
Đã xác nhận chỉ khác CRLF/LF, JSON/giá trị điều kiện giống nhau, không chuẩn hóa
hay sửa file đã dùng. Bản bytes deployed được giữ trong
`registered_materials/lock.json`, cùng source và phiên bản thư viện phân tích.
Chi tiết: `transfer_verification_20261114_01/source_verification.json`.

Một board cũ thiếu áp/600MHz, một model, một bộ PGD toàn ảnh và20 ảnh; không
camera/patch vật lý, không attacker thích nghi hay accuracy matched của cap.
Không có đo dịch vụ/hạn chót nên không kết luận DoS. Các ước lượng Pi này chỉ
là chẩn đoán theo quality gate đã định, không đưa thành headline xác nhận.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Nhờ đối chiếu báo cáo đã đóng với raw/PREREG → gõ: "check báo cáo Pi".

B. Chuẩn bị một protocol mới kiểm soát swap trước đo, giữ nguyên thất bại này
→ gõ: "Soạn protocol Pi mới chặn swap tự bật, chưa đo lại".

Không dùng full02 dưới tag cũ để cứu cổng. Nếu cần sửa runner/campaign hoặc
đổi quản lý swap sau tag, phải xin chỉ dẫn như bàn giao yêu cầu, trước khi áp
dụng/chạy. Bước chuẩn bị mới không biến full01 thành kết quả đạt.

## Đang chờ gì ở tôi

Không có gì cần thiết để hoàn tất bàn giao phân tích này. Đã giữ raw và kết
quả âm, không chạy lại phiên bị gate chặn và không sửa source đã khóa. Chỉ
cần chọn bước B nếu muốn mở giai đoạn đo mới; có thể gửi "check báo cáo Pi"
cho người bàn giao ngay. Không push, không sửa bản thảo chính đang dirty.
