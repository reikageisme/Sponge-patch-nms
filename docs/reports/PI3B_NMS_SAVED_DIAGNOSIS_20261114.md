# Pi NMS — chẩn đoán bổ sung từ raw cũ, chưa xác định nguyên nhân

## Đã xong

Đã đối chiếu **toàn bộ20ảnh và200lượt NMSadv/advB** trong phiên component
full20 không đạt chất lượng. Không chạy thêm benchmark, không sửa raw,
không loại ảnh hoặc thay quyết định cổng. Phân tích này được chọn sau khi
đã thấy dữ liệu, chỉ để thiết kế kiểm tra cơ chế tiếp theo.

Nguồn gốc: `sponge-sim/results/pi3b_full20_20261114/runs/full_01/stages_PI4/raw.jsonl`,
SHA`3bfc20f3f9a82794ea6d3c3493a4e4f70db3a906973ecbc02b45e23c7d5d697c`.
Derivedfiles trong cùng resultsroot: `saved_nms_diagnosis.json`,
`saved_nms_transitions.json`; scripts kèm đầy đủ selectors/rawlinemap.
Hình `saved_nms_diagnosis.png/pdf` đã kiểm hình, giữ đủ mọi ảnh/lượt.

### Những gì dữ liệu thực sự cho thấy

Bộ đếm `/proc/vmstat` của toàn hệ thống, cộtpgmajfault, tăng6022 giữa các
snapshot đầu20khối ảnh và snapshot cuối. Bốn cửa sổ tăng nhiều nhất:

| Ảnh / thứ tự1-based | Δpgmajfault toàn hệ thống | Hai dòng environment raw |
|---|---:|---|
|73 /12|2951|1435→1536|
|77 /14|2039|1637→1738|
|74 /13|689|1536→1637|
|78 /15|310|1738→1839|

Nguồn: `saved_nms_diagnosis.json:{global_pgmajfault_block_sum,blocks}`;
`saved_nms_transitions.json:largest_global_counter_blocks`.
Các delta bao trùm cả loadpair, reference, warmup, mask, NMS và việc khác
trên hệ thống trong khối. Không phải counters của riêng NMS/process.

Trong200lượt NMSadv/B,11lượt có processCPUtime nhỏ hơn walltime.
Phân loại theo **arm đã ghi thời gian ngay trước trong cùng khối**:

| Lượt NMS xuất hiện sau | Số lượt | CPUtime<walltime |
|---|---:|---:|
|maskadv hoặc maskadvB|71|10|
|NMS bất kỳ|80|0|
|maskclean|30|0|
|maskdose|12|0|
|lượt đầu khối, sau các warmup không clock|7|1|

Nguồn: `saved_nms_transitions.json:groups` và `calls_by_group` (đủ200dòng
raw, không chỉ các lượt chậm). Bảy trường hợp cuối là NMSadv/B được xếp
ngay vị trí0; không phải tổng số khối, và không giả định warmup là một lượt
timing đã quan sát. Giữa hai timing còn guard, clone/setup và releaseoutput.

Ví dụ ảnh77 (giữ nguyên cả10lượt A/B, không loại4lượt dưới đây):

| Raw /arm | Wallms | ProcessCPUms | Arm timing trước |
|---|---:|---:|---|
|1649 /B|491.954795|185.420109|đầu khối sau warmup|
|1682 /B|282.384785|177.820777|maskadv|
|1697 /B|492.601036|194.414078|maskadvB|
|1709 /B|262.117649|178.086924|maskadv|

Median gộp10lượt NMS A/B của ảnh77 là93.7555545ms; đây chỉ là thống kê
chẩn đoán mới, **không thay estimand A-only đã đăng ký**. A/B của protocol
vẫn FAILmeanlog/MDE; kết quả MASKcontrol riêng không cứu jointcomponentgate.
Nguồn: `saved_nms_diagnosis.json:blocks[image==000000000077]`.

## Phát hiện cần biết

Dữ liệu gợi ý cần kiểm **ảnh hưởng từ workload vừa chạy trước NMS**, bên
cạnh chính backend/kernel. Nhiều lượt sau maskadv vẫn bình thường:10/71
có CPUtime<walltime,61/71không có dấu hiệu đó. Không thể kết luận cứ chạy
mask lớn là NMS chậm, hoặc paging là nguyên nhân duy nhất.

Các nhóm được hình thành sau dữ liệu; ảnh/geometry/K/thứ tự/lịch sử bộ nhớ/
hoạt động hệ thống đều có thể gây nhiễu. Không tính p hay causal speedup từ
bảng này. ProcessCPUtime là tổng qua các thread nên ratioCPU/wall có thể>1;
ratio<1 không xác định chính xác thời gian mainthread ngủ hay ai làm nó chờ.

Counters toàn hệ thống không cho biết lỗi trang thuộc process nào hoặc
thuộc lời gọi nào. Ví dụ khối78 vẫn có delta310 mà các NMSadv/B không có
CPUtime<walltime. Không quy trách nhiệm cho RAM1GB, swap, thẻSD, threadpool,
IRQ hay tác vụ nền chỉ từ sự trùng cửa sổ; swap vẫn tắt theo guard.

Giả thuyết cần phân biệt ở phép kiểm có kiểm soát:

- code/data bị lấy lại từ bộ nhớ/file sau workload mask;
- trạng thái chờ/wake của threadpool hoặc scheduling;
- giới hạn/counters cgroup hoặc việc khác của hệ thống.

Đây không là đo mới, không phải NMS đã ổn định, không nâng cấp chẩn đoán
thành bằng chứng DoS. Mainfull20 vẫn giữ quyết định theo cổng đã đăng ký;
không thêm gatepgmajfault hồi tố hoặc đổi mainPASS/componentFAIL/PI1hủy.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Chuẩn bị tracer lấy counters **của process** trước/sau NMS, CPUmainthread,
contextswitch và cgroup; so predecessor có kiểm soát trên cùng tensor đã khóa,
có bracketcontrol cho ảnh hưởng đo → gõ: **"Chuẩn bị trace nguyên nhân NMS"**.

B. Tiếp tục trục renderer bộ nhớ đã có40cacheparity, đăng ký và báo riêng
RSS của freshprocess; kết quả đó không thay phép trace nguyên nhân → gõ:
**"Tiếp tục so sánh bộ nhớ renderer"**.

## Đang chờ gì ở tôi

Không có — việc đọc raw/chuẩn bị source tiếp tục được. Chưa có trace mới
hoặc endpointRAM/latency mới; SSH vẫn mở, mọi run cũ giữ nguyên.
