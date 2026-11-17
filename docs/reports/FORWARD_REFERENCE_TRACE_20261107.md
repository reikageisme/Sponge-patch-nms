# Forward tham chiếu có drift ngay cả khi không chạy NMS/MASK

## Đã xong

Đã hoàn tất đúng hai trace đã đăng ký dưới tag `prereg-forward-reference-20261107`, commit `e9dda8a90752c7ff0dd311f4f0db19c519a96b30`. Hai tiến trình mới, mỗi tiến trình 12 khối × 15 mẫu forward = 180 mẫu; tổng 360 mẫu. Mỗi khối có ba lượt warmup cố định. Một lịch không cố ý nghỉ giữa các khối; lịch kia nghỉ hai giây. Thứ tự cố định từ seed đăng ký là liên tục trước, nghỉ sau. Không chạy NMS, dựng mask hay tấn công trong workload.

Cả hai lượt exit0, đủ thứ tự mẫu, ghim CPU2 đầu/cuối đạt, điều kiện AC/power/QoS/priority được kiểm tra tại các mốc trong source. Đã khôi phục đúng affinity 45/45 tiến trình ứng dụng trước phân tích. Đã đối chiếu source/tag/input/config và giữ ngoại lệ CRLF/LF của `hw.py` như đăng ký. 38 tests CPU đạt trước phép đo; tests mới dùng hàm giả để kiểm tra lịch hữu hạn và vị trí observer, không phải chứng nhận thiết bị.

Raw, manifest, log, bảng kiểm source và biểu đồ PNG/PDF được lưu trong `sponge-sim/results/laptop_reference_trace_20261107/`. Bảng phân tích `run_01/analysis.json` có SHA nguồn, số dòng JSONL của từng mẫu và tham chiếu. Biểu đồ đã xem trực quan. Protocol đã đóng sau đúng hai trace; không chạy lại.

## Phát hiện cần biết

| Lịch chạy | Trung vị khối đầu (ms) | Trung vị khối cuối (ms) | Cờ chẩn đoán trên 3% |
|---|---:|---:|---:|
| Liên tục | 214,0099 | 212,2552 | 4/12, đều nhanh hơn |
| Nghỉ hai giây | 213,1007 | 204,4556 | 2/12, đều nhanh hơn |

Nguồn: `run_01/analysis.json:conditions.<continuous|pause2>.blocks[0|11].wall_median_ms,diagnostic_flags,flagged_faster`; tính trung vị 15 `ns` trong từng khối, chia 1e6. Tỷ số thấp nhất theo khối lần lượt là 0,9609508718989168 và 0,9594318554561294; nguồn `blocks[*].initial_ratio`, lấy minimum. Cờ dùng đúng `abs(ratio-1)>0.03` và luôn so với khối đầu, không chọn baseline mới.

**Đã quan sát drift vượt 3% khi không chạy NMS/MASK.** Điều này bổ sung bằng chứng rằng không nên tự quy mọi cờ tham chiếu của lượt công đoạn cho NMS hay MASK. Nó chưa xác định nguyên nhân vật lý của các lượt cũ. Bối cảnh runtime, tải pin-check, cache và lịch chạy khác nhau; không phải tái hiện giống hệt phiên NMS full trước.

Trung vị `% Processor Performance` theo khối nằm trong [247,13619275075152; 247,59124428749482] ở lịch liên tục và [247,33600143093503; 247,60710102603346] ở lịch nghỉ. Nguồn `blocks[*].pdh_counters.% Processor Performance.values.median`, lấy min/max theo khối. Counter ghi tương đối phẳng trong khi wall median biến động, nhưng chưa đủ để loại trừ thay đổi xung nhịp, nhiệt, cache hoặc scheduler. Không đo nhiệt độ CPU hay có scheduler trace; CPU time cũng có lượng tử hóa.

**Không được kết luận nghỉ hai giây tốt hơn từ 4 cờ so với 2 cờ.** Chỉ có một tiến trình cho mỗi lịch và lịch liên tục luôn chạy trước, nên hiệu ứng lịch nghỉ lẫn với phiên/thời điểm. Không có CI, p-value hay A/A MDE cho phép so sánh nhân quả này. Đây là trace chẩn đoán hữu hạn, không có PASS cho độ nhạy thời gian tấn công và không chọn cấu hình thắng để chạy lại.

NMS full và MASK smoke của protocol trước vẫn FAIL; hai phiên CPU toàn trình và phòng thủ đã đạt trước đó giữ kết luận trong phạm vi riêng. Không có kết quả DoS, ARM, ảnh chụp vật lý hoặc độ ổn định đuôi mới.

SHA256 raw:

- `run_01/continuous/raw.jsonl`: `c897e4903944c07c64ded321bbce6faacbbd2173b37c27bee58faa8b770399b6`.
- `run_01/pause2/raw.jsonl`: `368862d88ee3873d4b0376553476d22f74cb9a5a1e4dee9fa0cdda9f4067e02e`.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Rà khoảng trống của toàn nghiên cứu và ưu tiên phép đo còn thiếu thay vì lặp đo cho PASS → gõ: "Rà các cổng còn thiếu trước khi chạy thêm".

B. Ưu tiên nguồn pin/sạc, registry nhiệt và supervisor A36 → gõ: "Tiếp tục gỡ điều kiện đo A36".

## Đang chờ gì ở tôi

Chưa cần thao tác. Không có benchmark đang chạy; protocol trace đã dừng đúng kế hoạch. Mình có thể tiếp tục rà offline. A36 chưa được mở cổng chạy tải; máy thuê đã xóa và không được truy cập lại.
