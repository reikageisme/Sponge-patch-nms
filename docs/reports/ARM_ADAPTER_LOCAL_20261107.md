# A36: bổ sung adapter, kiểm trên local Linux — chưa chạy điện thoại

> Đây là checkpoint `29962b3`. Phần coordinator/stream/accounting được bổ sung tiếp trong `ARM_COORDINATOR_LOCAL_20261107.md`; các con số và giới hạn bên dưới mô tả checkpoint ban đầu, không được coi là trạng thái code mới nhất.

## Đã xong

Đã bổ sung trong `sponge-sim/studies/arm_preflight_v2`, không sửa runner điện thoại cũ:

- `linux_observe.py`: đọc raw stat/status và mask scheduler của từng TID trong chính tiến trình; kiểm TID/starttime, mask không khớp và thread sinh/mất. Ghim main trước pool và thử ghim tất cả TID đúng một lượt, lưu cả lỗi quyền/thay đổi dở; không tự lặp cho tới khi đạt.
- Bộ đọc cảm biến dùng manifest ID/đường dẫn/type/đơn vị rõ ràng, timestamp trước lần đọc đầu. CPU và pin được nhận diện riêng; không đoán đơn vị bằng độ lớn số, không thay sensor thiếu bằng 0, không coi trạng thái sạc không rõ là đang sạc.
- `posix_runtime.py`: tách đọc sensor và ghi event sang helper có deadline; lỗi/timeout dừng helper rồi truyền lỗi tới supervisor để dừng worker. Ghi event bằng file mới, fsync và xác nhận hash; giữ file dở nếu lỗi. Chỉ quản lý nhóm tiến trình mới do chính runner tạo; không tìm/kill theo tên.
- Sửa đường lỗi của `supervise_once`: lỗi ngay trong `poll` hoặc logger vẫn đi vào cleanup worker, không gọi lại `poll` rồi bỏ lỡ cleanup. Leader kết thúc nhưng nhóm còn tiến trình không được coi là thành công.

**52 kiểm tra giả lập đạt** trên Windows: parser/sampler cũ cùng các ca mới về TID reuse/churn, mask rộng/không khớp, lỗi quyền, pin/charging thiếu hoặc sai, sensor chậm, helper timeout, ACK sai, lỗi poll và đóng stream. Đây là test phần mềm, không phải 52 quan sát trên điện thoại.

Đã chạy thêm kiểm tích hợp local trên Ubuntu/WSL, không model và không benchmark tải CPU. Receipt `sponge-sim/results/arm_observer_local_20261107/native_01/receipt.json` có sáu kiểm tra đều true:

1. Đọc và ghim mask thread của chính tiến trình kiểm tra.
2. Đọc cảm biến từ file giả có giới hạn thời gian.
3. Ghi event mới, fsync và nhận ACK.
4. Từ chối trạng thái pin `Unknown`.
5. Từ chối reader quá hạn với fixture FIFO có thể chặn đọc.
6. Worker chờ đã bỏ qua TERM bị KILL, direct child được reap và nhóm đã hết.

Receipt ghi SHA nguồn thực thi, snapshot raw và phạm vi `LOCAL_LINUX_ENGINEERING_ONLY_NOT_A36_NO_LOAD_BENCHMARK`. Test không báo độ trễ phản ứng đo được, không chứng minh thời gian thực trên Android. Fixture/receipt mới được giữ nguyên; FIFO local mới được ghi đường dẫn trong receipt. Không truy cập điện thoại hoặc máy thuê đã xóa, không cài package hay đổi power/thermal.

## Phát hiện cần biết

Readback mask đúng chưa là bằng chứng ghim tải đạt. Vẫn cần fresh worker, mọi TID, đủ active observations, CPU-time/wall và coverage process/TID. Last-CPU của thread ngủ được giữ trong raw để chấm đối chứng cũ/active-only trên cùng snapshot; không xóa nó để làm đẹp tỷ lệ. Bốn FAIL lịch sử giữ nguyên; `little1` vượt upper CPU-time còn là lỗi độc lập với sampler.

Adapter có deadline giải quyết một phần reader/logger treo, nhưng chưa có coordinator đầy đủ. Cần lưu MỌI frame telemetry và partial burst, không chỉ latest frame trong reader; thực thi cửa sổ sạc ổn định, baseline từng sensor trước tải, nghỉ thường 60 s/tối đa 180 s, và safety cooldown đúng hysteresis. Không tự chạy lại burst bị ngắt. Chỉ burst hoàn tất an toàn được reset ba lần ngắt nhiệt liên tiếp.

Cần cộng cả cadence, deadline helper và thời gian TERM/KILL helper/worker khi khóa giới hạn phản ứng. Timeout cấu hình không chứng minh CPU/OS sẽ lập lịch đúng hạn. Chưa kiểm descendant process-group, parent-death recovery hoặc quyền đọc/ghi/ghim trong Android/proot; test direct child local không phủ các trường hợp đó. Chưa có registry sensor thật hoặc phép đo nhiệt/pin A36 mới.

Các ngưỡng cũ 70°C/40°C, resume mọi zone <55°C và pin <38°C, SOC30–80% và đang sạc vẫn giữ. Deadline 6/180 s trong prototype là tham số draft; không coi đã được đo khả thi hoặc đăng ký chính thức cho phiên mới. Không triển khai, không dùng runner cũ để đo phân đoạn.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Hoàn thiện coordinator, telemetry stream và kiểm descendant/watchdog offline → gõ: “Tiếp tục coordinator A36”. Đây là công việc tiếp tục mặc định theo ủy quyền hiện có.

B. Trở lại kế hoạch CPU nhiều luồng và đo tách MASK/NMS → gõ: “Tiếp tục CPU nhiều luồng”. Cần protocol/tag mới trước mọi timing.

## Đang chờ gì ở tôi

Không có cho code/kiểm offline. Chỉ khi adapter và protocol đã cụ thể mới cần xác nhận trạng thái điện thoại thực tế trước tải: máy rảnh, sạc ổn định, SOC trong cổng và mạng theo `CLAUDE.md`.
