# Rà drift công đoạn từ raw đã lưu — phân tích thăm dò, không đo mới

## Đã xong

Đã xác nhận không còn tiến trình benchmark, rồi đọc lại raw của ba lượt công đoạn. Các raw, summary, receipt và kết luận cổng cũ được giữ nguyên. Không chạy model, thu thêm counter, đổi power plan hoặc kết nối điện thoại/máy thuê.

Đã xác định vì sao bảng PDH theo công đoạn trong summary cũ trống: `analyze_attack.py` đổi nhãn thành `nms_kernel`/`mask_native`, nhưng `analyze_pdh.py:analyze` chỉ duyệt `forward`/`total`. Counter gốc vẫn có trong từng dòng timing. Bộ phân tích bổ sung `sponge-sim/studies/laptop_seg/analyze_stage_drift.py` đọc trực tiếp các counter đó, kiểm SHA raw với summary, xuất file mới bằng chế độ không ghi đè. Giữ nguyên hai file phân tích đã khóa trong protocol cũ để không làm mất khả năng kiểm source của các run.

Đã kiểm tra 36 tests CPU đạt, gồm ba tests mới: tên công đoạn/counter được giữ lại, đơn vị khối 64 lần gọi được phân biệt với mỗi lần gọi, và giá trị CPU rời rạc/counter lỗi không bị biến thành quyết định chất lượng. Các kết quả thăm dò mới nằm tại `sponge-sim/results/laptop_components_20261107/offline_drift_01/{nms_smoke,nms_full,mask_smoke}.json`.

## Phát hiện cần biết

### Phần thiếu là bảng chẩn đoán, không phải dữ liệu đo hay cổng chất lượng

Cả hai arm trong mỗi summary cũ đều có `pdh_diagnostics.<arm>.stages={}`. Bộ bổ sung khôi phục cách nhìn counter từ raw, không sửa các flag hoặc tính lại tiêu chuẩn đạt. NMS full vẫn FAIL 20/22 cờ, MASK smoke vẫn FAIL 1/4 cờ. Không có contrast công đoạn đủ điều kiện suy luận chính.

### CPU bằng 0 trên khối ngắn không xác định việc bị giành CPU

| Dữ liệu đã lưu | Arm | Khối timing | CPU time bằng 0 | CPU time / wall > 1 |
|---|---|---:|---:|---:|
| NMS full | Sạch | 1.920 | 1.808 | 112 |
| NMS full | Tấn công | 1.920 | 0 | 907 |
| MASK smoke | Sạch | 192 | 72 | 36 |
| MASK smoke | Tấn công | 192 | 0 | 61 |

Nguồn: các file bổ sung, `arms.<arm>.raw_block_wall_ms.n`, `zero_process_cpu_count`, `cpu_over_wall_above_one_count`; các số này được đếm trực tiếp từ raw `kind=timing` và `process_cpu_ns/ns`. Danh sách `raw_timing_lines` chỉ tới số dòng JSONL gốc. Giá trị CPU được giữ nguyên, không cắt về khoảng [0,1]. Những quan sát này phù hợp với lượng tử hóa đồng hồ CPU ở khối ngắn; chúng không xác định được thời lượng off-CPU hay thủ phạm gây drift. Không gọi bước nhảy quan sát được là phép đo độ phân giải phần cứng/API.

### PDH cần đọc đúng khoảng thời gian và đơn vị

Ở NMS full, trung vị thời gian đọc PDH là 0,0278 ms cho arm sạch và 0,0752 ms cho arm tấn công. Trung vị của tỷ số thời gian đọc / wall của **cả khối 64 lần gọi** lần lượt là 0,01623721432618193 và 0,0006062761092159982. Đây là trung vị từng tỷ số, không phải chia hai trung vị. Không chia mẫu số thêm 64; không lấy các giá trị này trừ khỏi endpoint.

PDH ghi `% Processor Performance` với trung vị 248,0296423319797 ở sạch và 247,99613731043365 ở tấn công. Counter `Processor Frequency` luôn báo 1.300, `% Performance Limit` luôn 100 và `Performance Limit Flags` luôn 0 trong các mẫu NMS full. Đây chỉ là giá trị counter đã ghi, **không chứng minh CPU thực sự chạy 1.300 MHz hoặc không bị giới hạn nhiệt**. Không có nhiệt độ CPU hay scheduler trace trong dữ liệu này.

Nguồn: `offline_drift_01/nms_full.json:arms.<arm>.pdh_read_ms,pdh_read_over_raw_block_wall,pdh_counters`. Khoảng PDH còn chứa phần việc ngoài đồng hồ; các dòng đầu sau tham chiếu có thể chứa cả forward, chuẩn bị và warmup. Bộ bổ sung giữ thời điểm và mức bao phủ ở `pdh_intervals`, không coi counter đó là xung nhịp chính xác trong endpoint. Vì tham chiếu forward không được thu PDH riêng, chưa thể dùng counter của NMS để giải thích trực tiếp 19 cờ tham chiếu nhanh hơn mốc đầu.

### Điểm cần kiểm chứng tiếp

Code đã khóa giải phóng output sau đồng hồ và trước lần gọi kế tiếp; không tìm thấy bằng chứng mới rằng output tham chiếu bị giữ qua lần đo sau. Tuy nhiên global warmup ở protocol công đoạn dùng công đoạn đã chuẩn bị, còn tham chiếu đo forward. Đây là khác biệt kích thích/cadence có thật trong source, chỉ tạo giả thuyết về trạng thái ban đầu; chưa xác lập nguyên nhân drift. Không sửa số warmup, chọn lại baseline hoặc tăng ngưỡng trên dữ liệu cũ.

Kiểm tra tiến cứu sau đó đã hoàn tất đúng hai trace forward không NMS/MASK: lịch liên tục có 4/12 cờ, lịch nghỉ hai giây có 2/12, đều nhanh hơn mốc đầu. Xem `FORWARD_REFERENCE_TRACE_20261107.md`. Đây không phải phép chạy lại công đoạn và không thay đổi FAIL cũ; một tiến trình mỗi lịch không đủ suy tác động nhân quả của lịch nghỉ.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Chuẩn bị kiểm tra hữu hạn về trạng thái tham chiếu, không dùng để đổi điểm FAIL cũ → gõ: "Thiết kế kiểm tra tham chiếu CPU trước khi đo lại".

B. Tiếp tục hoàn thiện nguồn pin/nhiệt và supervisor A36 → gõ: "Ưu tiên điều kiện đo A36".

## Đang chờ gì ở tôi

Không cần duyệt phân tích raw đã lưu. Chưa có benchmark mới được khởi chạy. Mọi phép đo tiếp theo cần endpoint, lịch chạy, tiêu chí dừng và tag riêng trước khi đo; không tự lặp protocol công đoạn đã đóng để tìm PASS. Giai đoạn A36 vẫn cần nguồn SOC/sạc và registry nhiệt hợp lệ trước tải.
