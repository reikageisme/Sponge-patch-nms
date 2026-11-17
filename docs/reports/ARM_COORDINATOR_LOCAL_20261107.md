# A36: coordinator và chấm pin mới, kiểm offline — 07/11/2026

> Checkpoint `9974938`. Worker code/DRAFT package và hai lượt metadata read-only A36 sau đó được ghi tại `A36_TAILSCALE_A0_20261107.md`; cổng tải phone vẫn đóng. Các giới hạn và con số dưới đây thuộc checkpoint coordinator, không phải kết quả pin/latency A36.

## Đã xong

Đã bổ sung coordinator control trong `studies/arm_preflight_v2/session.py`:

- Nhận danh sách đợt có ID cố định/không trùng từ trước. Đợt bị ngắt hoặc chưa chạy giữ nguyên trong ledger, không tự thử lại hoặc thay thế. Không tái sử dụng cùng guard cho một phiên mới.
- Chỉ bắt đầu sau ít nhất hai mẫu sạc hợp lệ trải đủ cửa sổ đã khai; khoảng trống quan sát quá freshness bị từ chối. Baseline từng sensor và pin lấy sau cửa sổ này, trước tải đầu tiên.
- Nghỉ thường ít nhất 60 s, so từng sensor và pin với baseline riêng +1°C. Đến 180 s mà còn trên baseline nhưng an toàn thì ghi `not_cooled`; không lấy deadline nghỉ thường để bỏ qua ngưỡng nóng/hysteresis hoặc deadline safety cooldown.
- Ngắt đúng worker khi sensor/pin/power/timeout/logger/poll lỗi. Ba lần ngắt nhiệt liên tiếp kết thúc phiên; chỉ burst hoàn tất an toàn reset counter. Lỗi trong thời gian nghỉ không đổi nhãn một burst đã hoàn tất thành burst dở.
- Log kết thúc phải nhận ACK. Kết quả luồng điều khiển luôn có `study_quality=NOT_ASSESSED`, không tự biến thành kết quả timing đủ chất lượng.

`BoundedSensors` nay lưu mỗi frame hoàn chỉnh, kể cả frame không hợp lệ, dưới file mới có số thứ tự và SHA config trước khi trả ACK. Deadline bao gồm đọc và fsync. Read bị timeout có thể để lại gap/file dở; giữ nguyên, khóa reader và kết thúc phiên. Không trả lại frame tốt cũ hoặc âm thầm đọc lại.

`pin_analysis.py` chấm các snapshot MỚI bằng đủ điều kiện: mask mọi TID đúng, danh tính ổn định, tối thiểu 20 active observations, tỷ phần active last-CPU ≥99%, CPU-time/wall theo cổng gốc và tổng CPU ticks của TID khớp clock tiến trình trong khoảng bất định được khai. Tolerance accounting gồm lượng tử tick và cửa sổ đọc đầu/cuối; tỷ phần slack tối đa bắt buộc truyền vào và phải khóa trước QA. Coverage thiếu hoặc tolerance quá rộng thành `INCONCLUSIVE`; sampler đẹp không cứu được upper CPU-time vi phạm. Không dùng để chấm lại bốn artifact A36 cũ thiếu snapshot.

**104 kiểm tra đạt**: 76 ARM/control giả lập và 28 hồi quy CPU. Các ca bao gồm sạc bị mất, khoảng trống quan sát, nhiệt tăng sau spawn, ba đợt bị ngắt không retry, lỗi log, bảo toàn burst đã xong, sensor thiếu/NaN, TID reuse/churn, mask thread ngủ rộng và CPU accounting thiếu. Fixture PASS chỉ là test thuật toán.

Kiểm tích hợp thứ hai trên Ubuntu/WSL dùng sensor giả và worker chờ, không model/benchmark tải CPU/điện thoại: **9 kiểm tra đạt**, lưu **55 frame** của phiên coordinator cùng **11 event**, có ACK cuối và nghỉ thật hơn 60 s. Nguồn `sponge-sim/results/arm_observer_local_20261107/native_02/receipt.json` → `checks`, `coordinator_result`; frame/event theo thư mục cùng tên. Ledger trong terminal event khớp kết quả trả về, loại trường ACK tự tham chiếu. Frame hợp lệ và frame `Unknown` không hợp lệ đều được giữ trong `frames/`.

Source thực thi tại lượt WSL được lưu trong `native_02/executed_source/`, cả năm file khớp SHA đã có trong receipt. Snapshot được đối chiếu byte sau khi thêm chốt fresh-guard; `source_snapshot_receipt.json` ghi cách phục hồi chính xác phần thay đổi liên quan trong hai file. Chốt mới và analyzer pin có kiểm host; không gán kết quả WSL cũ cho những thay đổi này. `native_01` và các kết quả CPU/defense cũ không đổi.

## Phát hiện cần biết

Chưa chạy hay truy cập A36. WSL không kiểm được namespace/permission/descendant của Android/proot, sensor thật, thread pool Torch hoặc thời gian phản ứng thực trên điện thoại. Worker thu process-clock và snapshot khớp cửa sổ dưới tải Torch chưa có. Dù coordinator đã có luồng control, chưa có runner phân đoạn hoặc profile A36 đủ điều kiện.

Các tham số stable-power window, cadence, helper deadline và accounting-slack hiện chỉ là lựa chọn test/draft. Phải đo chi phí metadata và khóa trước QA thiết bị; tính cả thời gian cleanup helper/worker. Timeout cấu hình không chứng minh scheduler/hardware sẽ phản ứng trong một giới hạn cứng. Chưa kiểm parent-death/descendant trên Android.

Các ngưỡng 70°C/40°C, resume mọi zone <55°C và pin <38°C, SOC30–80% cùng đang sạc giữ nguyên. So pin với baseline +1°C là kiểm nghỉ thường bổ sung trước dữ liệu phone mới. Cửa sổ sạc chỉ xác minh các mẫu quan sát, không chứng minh liên tục giữa hai mẫu. Mọi burst dở được giữ, không chọn riêng burst mát hoàn tất để gọi là hiệu ứng toàn phiên.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Hoàn thiện worker QA thread pool/sampler, khóa package và kế hoạch controls trước tải A36 → gõ: “Tiếp tục worker QA A36”. Đây là hướng tiếp tục offline mặc định.

B. Chuyển sang protocol CPU nhiều luồng hoặc tách chi phí MASK/NMS → gõ: “Tiếp tục CPU”. Không chạy lại nhánh output50 đã trượt để tìm PASS.

## Đang chờ gì ở tôi

Không có cho code và kiểm offline. Trước phép đo điện thoại cần package/protocol cụ thể, PREREG/tag và xác nhận trạng thái thực tế máy rảnh, mạng và sạc theo `CLAUDE.md`; chưa bắt đầu tải phone.
