# Pi 3B — full20: toàn trình đạt, tách công đoạn không đạt độ ổn định NMS

## Đã xong

**Đã có phép đo toàn trình trên Pi thật qua cổng chất lượng: 20 ảnh, 4 luồng,
720 lượt đo. Ảnh nhiễu làm thời gian toàn trình tăng khoảng 1,798 lần;
chặn ứng viên trước NMS giảm thời gian còn khoảng 0,729 lần so với ảnh nhiễu.
Đây là replay tensor trên điều kiện thiết bị đã khai báo, chưa phải DoS.**

Gốc nguồn bên dưới: `sponge-sim/results/pi3b_full20_20261114/`.
Đăng ký `PREREG_PI3B_FULL20_AFTER_PILOT_20261114.md`, tag
`prereg-pi3b-full20-after-pilot-20261114`, commit
`aa6b666f13160bffe13286ec2ed7c1e75f51f0ba`, lockSHA
`1cd1789d4f30c0a6b708fad907729999f6e6e53d4ba373ce487bc8037d10be0e`.
Protocol được duyệt sau khi đã xem pilot thất bại: không đo lại pilot, giữ
nguyên cổng full, không chọn lại ảnh hay khởi tạo. Không phải cohort độc lập.

Một campaign duy nhất `runs/full_01`, kết thúc mã66 vì cổng phiên phụ. Đã
chép nguyên 21 file gốc; SHA remote trước=local=remote sau. Cả28 vật liệu/source
khóa khớp sau phiên. Không full02, không worker còn chạy. Khôi phục governor,
swap topology/priority, units/timer/helper và gỡ đúng runtime masks đạt;
SSH vẫn mở. Nguồn: `transfer_verification.json`, `remote_after_fetch.json`,
`runs/full_01/{campaign_terminal,restore,lease_state,registration}.json`.

### Trạng thái từng phần đo

| Phiên | Dữ liệu | Quyết định |
|---|---|---|
|Toàn trình 4 luồng|20 ảnh ×6 nhánh ×6 lặp =720 timings;2399 dòng raw;1572 guards|**đạt**|
|NMS/MASK 4 luồng|20 ảnh;600 base timings +105 dose timings =705;2354 dòng raw;1542 guards|không đạt cổng NMS A/A và MDE|
|Toàn trình 1 luồng|chưa khởi chạy, không có raw/timing|hủy theo quy tắc dừng sau phiên phụ thất bại|

Nguồn: `runs/full_01/summary.json:*.{audit,quality_pass}`,
`campaign_terminal.json:sessions`, `independent_audit.json:sessions.*.row_kinds`.
Một phiên phụ thất bại không xóa kết quả chính đã đạt; không gọi toàn bộ
campaign là PASS, cũng không biến phiên 1 luồng bị hủy thành phiên đã chạy.

### Các cổng toàn trình

| Cổng | Kết quả |
|---|---|
|ID, lịch shuffle, arms/lặp, guard pairs, tag/source/weights|đúng toàn bộ; audit không lỗi|
|Swap/USB/masks/affinity/governor/vmstat|không vi phạm tại các lần đọc; swap0 và masks đúng|
|Actual clock|23 snapshots, tất cả600000000Hz; powersave|
|Ghim tải đầu/cuối|inside3.9701986754966327 /3.886981469714604; ngưỡng2.8|
|Reference|0/22 cờ; ratio0.9988661143347715–1.0151972014582011|
|A/A meanlog|−0.0009716325130935908; abs≤0.02 đạt|
|A/A geometricratio/CI95%|0.9990288393689323 [0.9973671125855,1.000870050550327]|
|MDElog80%|0.0027535348095158725 ≤0.05; ratio1.002757329268415|
|Khôi phục toàn campaign|RESTORED/errors[] và readback khớp snapshot|

Nguồn: `summary.json:pipeline_PI4.{gates,aa_cleanA_over_cleanB,mde_log_80pct,mde_ratio_80pct,campaign_restore_ok}`;
pin raw dòng1/2398, done2399; nguồn dòng chi tiết trong `raw_source_map.json`.
Không suy tương đương chỉ từ p A/A=0.30908203125; cổng dùng cả bias và MDE.

### Hiệu ứng toàn trình được chấp nhận theo protocol

| Endpoint | Geometricratio | CI95% bootstrap ảnh | p exact | d_z |
|---|---:|---|---:|---:|
|H1 ảnh nhiễu/sạch|1.79807662737513|[1.7465231194596404,1.8477275683430143]|0.0000019073486328125|8.88045874872163|
|H2 cap/ảnh nhiễu|0.728911250847867|[0.7131272180811244,0.746037613300716]|0.0000019073486328125|−5.959484145093036|
|Cap/sạch, phụ|1.31063828358032|[1.2981856359897277,1.3232221434121805]|0.0000019073486328125|12.06384228700987|
|Forward nhiễu/sạch, phụ|1.0022566730289426|[0.9999236467973799,1.0048747902974693]|0.09697341918945312|0.39085778834134133|

Holm chỉ họ chính {H1,H2}: cả hai0.000003814697265625. Mỗi ảnh là một đơn vị
suy luận, n20, không coi720timings là720mẫu độc lập. Bootstrap20000 lần với
seed H1/H2/AA/cap-clean/forward lần lượt20261115–20261119; exactsignflip2^20,
tolerance1e−12, p nhỏ nhất2/2^20. Không bổ sung họ phụ vào Holm sau dữ liệu.
MDE trên A/A toàn trình không chứng nhận độ nhạy của endpoint forward phụ;
CI/p forward không là chứng minh tương đương.

Median qua ảnh của median thời gian (ms): sạch4351.36015375,
nhiễu7969.9644555, cap5710.18472275; forward sạch4288.08865525,
forward nhiễu4292.38771225. Tỷ trọng forward lấy median của tỷ số từng ảnh:
sạch0.9861050619864737, nhiễu0.5404548140402785. Không lấy tỷ số hai median
toàn cohort để thay estimand, không trừ hai median để dựng thời gian stage.

Nguồn: `summary.json:pipeline_PI4.{h1_adv_over_clean,h2_advcap_over_adv,holm_h1_h2,advcap_over_clean,forward_adv_over_clean,median_ms_across_images,forward_share}`.
`raw_source_map.json:pipeline_PI4.timing_lines_by_image_arm.*` liệt kê đúng
dòng, ns, CPUtime, lặp, vị trí cho từng nhánh. Median sạch gộp12lượt A+B/ảnh.
`independent_audit.json` tính độc lập đủ7endpoint bootstrap/exhaustive signflip,
MDE, Holm, lịch đo, refs và shares khớp analyzer khóa; không inference lại.

### Số đếm và khả năng chứa trong RAM

Median Nτ sạch/nhiễu=18.5/2687; K sạch/nhiễu/cap=2.5/270.5/98. Cap
max_nms300, max_det300; không đổi độ phân giải640²/FP32/batch1/renderer.
Cả20ảnh có Nτ/K trùng laptop;0/40 prediction tensors giống byte. Counts giữa
main và stages cũng khớp. Torch2.15.0+cpu/TV0.29.2+cpu khác laptop2.13.0/0.28.0;
Ultralytics8.4.90 giống. Parity số đếm hữu hạn không là tương đương số học.
Nguồn: `summary.json:pipeline_PI4.{counts,count_medians,parity_vs_laptop}`,
manifest và `independent_audit.json:sessions.*.counts`.

MemAvailable thấp nhất tại fastguard: main70400kB, stages80944kB, đều trên
ngưỡng40000. Nhiệt native fastguard cao nhất main41.856°C, stages40.78°C;
vcgencmd snapshot cao nhất tương ứng41.3/40.8°C là kênh khác. RSS cuối khối
main393973760–668860416bytes, stages441032704–675082240bytes. **Không phải
peakRSS**, không chứng nhận mọi ảnh/K/backend đều vừa1GB. Nguồn:
`independent_audit.json:sessions.*.{min_fast_mem_available_kb,max_fast_temp_c,sampled_block_rss_bytes}`.

## Phát hiện cần biết

### Công đoạn: giữ nguyên kết quả không đạt

| Đối chứng cùng tải nhiễu | Meanlog A/B | Geometricratio | MDElog80% | Cổng riêng |
|---|---:|---:|---:|---|
|NMS|−0.053783943395614195|0.9476368275804894|0.16524377233299772|bias và MDE đều FAIL|
|MASK|−0.005921711514816097|0.9940957872608773|0.02709234224835699|bias và MDE đạt|

Cổng chung đòi cả hai đạt, nên **toàn bộ phiên component/dose vẫn chẩn đoán**.
MASK có cổng riêng đạt không cho phép đổi quyết định chung sau dữ liệu.
Hai pin và0/22reference flags,23sample clocks600MHz, physicalguards đều đạt.
Nguồn: `summary.json:stages_PI4.{gates,stage_controls,quality_pass}`.

Giữ estimate chẩn đoán: NMSadv/clean7.877478034017995
[6.159342524395206,10.056147906843476]; MASKadv/clean67.95247215157052
[52.063831373654274,87.94646868250801]. Cả hai rawp2/2^20; p nhỏ không cứu
precisiongate. Medianms clean/adv NMS10.2427685/87.4471625;
MASK47.9756945/3636.1224405. Nguồn: `summary.json:stages_PI4`.
Không đưa các tỷ số này thành bằng chứng cơ chế đã qua chất lượng.

Ở ảnh77, NMSadvB có các walltimes khoảng491.95,282.38,492.60,262.12,93.21ms,
trong khi NMSadv khoảng88.44–94.06ms. Dòng raw B1649/1682/1697/1709/1724;
A1664/1676/1700/1715/1727. CPUtime/walltime của vài B thấp hơn1, khác các
A. Điều này phù hợp với khả năng có thời gian chờ/scheduling ngoài tính toán,
nhưng **chưa xác định nguyên nhân**; không có scheduler trace để quy trách
nhiệm threadpool, hệ điều hành, IRQ hay tác vụ khác. Không bỏ ảnh77 hoặc chọn
lại lượt đo. Backend torchvision cố định vẫn không tự bảo đảm wrapper ổn định.
NMS endpoint gồm lọc/chuẩn bị/sắp xếp và kernel, không phải bare-C++kernel.

Chẩn đoán bổ sung toàn20ảnh/200NMSadv-B từ chính raw này được ghi riêng ở
`PI3B_NMS_SAVED_DIAGNOSIS_20261114.md`: có sự trùng cửa sổ giữa counters
pgmajfault toàn hệ thống, workload mask trước NMS và một số CPU/wall gaps.
Đây là phân tích sau dữ liệu, chưa quy được nguyên nhân/process/lời gọi;
không đổi cổng, không loại ảnh77 hay diễn giải lại các estimate đã đăng ký.

Liều K trên5ảnh đầu có4/4/5/4/4 mức sẵn có; chỉ ảnh30 đủK300, không padding.
Toàn bộ21median liều và fits nằm trong `summary.json:stages_PI4.{mask_dose_ms,mask_dose_linear_fit_descriptive}`,
rawmap chỉ đúng từng dòng/lặp. Đây là mô tả trong phiên không đạt; R² cao
không chứng minh độ phức tạp O(K). Không dùng smoke hay GPU để điền ô thiếu.

### Giới hạn và khó khăn giữ trong hồ sơ

- Một Pi3B1GB, nguồn có thiếu áp, governor powersave/600MHz, headless64-bit.
  Snapshots có cả0x50000 và0x50005; không nói thiếu áp hiện tại liên tục hay
  quy xung600 hoàn toàn cho firmware. Không quy đổi đến1.2GHz/Pi4/Pi5/A36.
- Cùng20ảnh/PGD đã thấy trước, mộtmodel, không bất định nhiềuseed/board/nguồn.
  Không physicalpatch/camera, service/deadline, DoS, hay curve accuracy–latency
  ghép cùng điều kiện. Cap còn chậm hơn sạch; không tuyên bố loại bỏ tấn công.
- Guard trước/sau call và snapshot cuối khối không quan sát liên tục ở giữa;
  syscall/log ngoài clock vẫn có thể đổi cache và nhiễu. Không peakRAM trace.
- Trong phiên, người dùng xin lệnh chụp tiến độ; đã được cung cấp lệnh đọc
  process/raw. Chưa biết họ có chạy, lúc nào hay bao lâu. Trợ lý chỉ chờ handle
  đến terminal; không suy đã có giám sát ngoài hoặc gán nguyên nhân NMS cho nó.
- Collector ban đầu so sánh dictionary fail do Windows dùng dấu `\\` trong
  key đường dẫn còn remote dùng `/`; normalize key local rồi SHA cả21file
  khớp. Không dữ liệu hỏng, không fetch lại/ghi đè raw. Receipt ghi rõ lỗi.
- Công cụ hậu kỳ gặp lỗi đọc mặc định cp1252 trên báo cáo tiếng Việt và lỗi
  Windows OSError22 khi chép văn bản TeX đã sinh. Đọc UTF-8 rõ ràng và ghi
  file mới rồi thay thế nguyên tử giải quyết việc này; không sửa raw/source đo.
  Một kiểm tra artifact thất bại vì văn bản cũ CRLF chưa được thay thành output
  LF của generator; giữ test nguyên và chạy lại sau khi chép đủ:7/7 đạt3.43s.
  `postdata_tooling.json` giữ lịch sử; không gán nguyên nhân cho bộ lọc an toàn.
- Hai protocol Pi trước vẫn giữ FAIL swap và FAIL MDEpilot; full20 này không
  hợp thức hóa chúng. Không retry phiên component/PI1 dưới tag này.

Hình độc lập `full20_quality_and_effects.png/pdf` và `component_diagnostics.png/pdf` được kiểm hình;
rà soát tiếp phát hiện chú thích hình component ghi nhầm thứ tự ảnh77 là15
thay vì14. Hình sửa là `component_diagnostics_corrected.png/pdf`, lấy vị trí
trực tiếp từ danh sách ID trong audit; hình cũ giữ nguyên. Tọa độ điểm, dữ liệu
và mọi thống kê không đổi; `figure_label_correction.json` ghi việc sửa.
nguồn từng điểm ở audit/rawmap. TeX tích hợp qua generator và source map;
kiểm cấu trúc/tests không thay thế compile/render toàn bản thảo.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Đối chiếu báo cáo với raw/PREREG và hoàn thiện bản thảo, giữ mọi âm tính →
gõ: **"Check báo cáo Pi full20"**.

B. Chuẩn bị renderer preallocation riêng, kiểm output parity trước; mọi timing
hoặc điều tra scheduler mới cần proposal/tag riêng sau khi đóng baseline,
không tạo chuỗi đo lại để kiếm PASS → gõ: **"Chuẩn bị tối ưu renderer riêng"**.

## Đang chờ gì ở tôi

Không cần thao tác để khôi phục Pi hoặc mở lại SSH. Không cần duyệt lại
việc phân tích/tài liệu đã cho phép. Phiên đo này đã đóng, không tự đo lại.
