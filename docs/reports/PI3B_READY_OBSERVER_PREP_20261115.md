## Đã xong

- Kiểm code và raw của lượt giám sát đã đóng. Tìm thấy bất nhất về ngân sách lệnh: READY cũ có hạn25s cho cả truy vấn SSH, nhưng gọi một unit query hạn10s rồi System.current() với bốn manager query, mỗi query có thể chờ30s. Bốn trường active/setup được đọc nhưng không dùng trong predicate READY. Kiểm bằng AST gốc với reader/command giả xác nhận bốn lời gọi; đây là phân tích tĩnh, không phải số đo độ trễ hay kết luận nguyên nhân timeout thực tế.
- Chuẩn bị observer mới chỉ đọc tại `sponge-sim/studies/pi3b_ready_observer_20261115/probe.py`: một unit query cùng hạn10s; đọc trực tiếp governor/swap/mask mà READY cần; kiểm child PID/birth/cgroup chính xác trước và sau kiểm USB; giữ no-Torch/no-scipy, mode/source/phase binding. Không gọi System.current() hay gửi fault trong probe. Đầu ra ghi rõ đọc tuần tự, không phải ảnh chụp nguyên tử và không tự xác minh toàn bộ source.
- Chuẩn bị transport ghi nguyên byte stdin/stdout/stderr, cả prefix khi TimeoutExpired, cùng return code/trạng thái. Hạn truy vấn25s và tổng READY40s giữ nguyên; ngân sách còn lại chỉ được rút ngắn. Không retry, không coi null/JSON hỏng/NaN/response trễ là READY. Thư mục query tồn tại thì từ chối trước gửi yêu cầu.
- Chuẩn bị đủ driver, deployer và collector cho một đề xuất kiểm chứng mới. Deployer chỉ thêm một probe.py vào sidecar mới, không sửa 23 file payload cũ. Driver giữ năm tình huống, thời lượng, supervisor caps và postterminal ASSESS nguyên bản. Dừng lỗi đầu tiên; chỉ kill PID đã xác minh hoặc SSH frontend do chính driver tạo. Collector hậu terminal giữ cả thư mục normal cũ thất bại và năm case mới, kiểm SHA/source/restore độc lập; không tự bật functional/model.
- Có46 kiểm thử mới bằng procfs/unit/SSH/đồng hồ giả: các lỗi state/source/PID reuse/cgroup/USB, child mất trong lúc đọc, timeout/bad JSON/launch error, byte-exact prefix, admission thiếu/false review, đủ năm case giả và dừng ngay ở READY lỗi. Chạy chung100 kiểm thử trước: **146 PASS**. Log cuối `sponge-sim/results/pi3b_ready_observer_host_qa_20261115/host_checks_04.log`. Các log01/02/03 giữ nguyên, không có failure bị xóa.
- Đóng gói8 source/test files và kế hoạch byte-exact tại registered_materials; `qualification_lock.json` khóa nguồn mới, nguồn payload23, receipt failure cũ và8 raw cũ. Mọi entrypoint triển khai/chạy yêu cầu một review cụ thể, outer tag/commit/lock SHA và failure SHA khớp. Không tạo `method_approval.json`, không có query/triển khai/case native mới trong lượt chuẩn bị này.

## Phát hiện cần biết

- **Chưa biết nguyên nhân thực tế của TimeoutExpired trước.** Phân tích ngân sách chỉ chỉ ra rủi ro thiết kế; không tách được SSH/Tailscale với xử lý Pi, không chứng minh sửa code sẽ làm lần sau PASS. Lượt cũ vẫn CLOSED_INCOMPLETE, bốn case cũ vẫn NOT_STARTED, không đổi thành PASS từ restore tốt hay kiểm thử giả.
- Đây là thay đổi phương pháp sau failure, cần ngoại lệ cụ thể đối với quy tắc cũ “stop at first unexpected failure, no retry/QA02”. Không tự chạy lại dưới tên khác, nới25s, sửa phán quyết cũ hoặc lấy quyền full RSS đã dùng làm quyền cho lượt mới.
- Đề xuất dùng provenance kết hợp: payload giữ nguồn/tag/commit925c544; phương pháp quan sát có outer tag mới `qa-pi3b-ready-observer-20261115`. Registration trong payload ghi danh tính SOURCE cũ; outer lock/review/outcomes ghi danh tính METHOD mới. Hai lớp phải báo riêng, không được trình bày source cũ hay lượt cũ là phương pháp mới đã đạt. Việc dùng lại payload cho năm case mới nằm trong ngoại lệ cần duyệt.
- Không có NMS/model/mask/RSS/độ trễ thiết bị mới. Số giây trong log unit test không phải hiệu năng Pi. Gói này chưa đủ mở material40, scientific smoke/full hay kết luận cơ chế NMS/DoS. Mọi kết quả âm và RSS full trước giữ nguyên.

## Việc tiếp theo — chọn 1 trong các cách sau

1. Duyệt một lượt kiểm chứng mới đúng đề xuất `sponge-sim/prereg/DRAFT_QA_PI3B_READY_OBSERVER_20261115.md`, năm sleeping case/không model, sau khi xem xét rõ ngoại lệ và nguồn kết hợp. Sau review thật mới ghi sự kiện approval bind tag/commit/config; xác minh máy rảnh, unit inactive/source/old raw trước triển khai; chạy một set, chỉ chờ đúng driver trong lúc live. Nếu lỗi, dừng và giữ partial, không retry hay thêm set.
2. Giữ dừng mọi tải native và tiếp tục code/kiểm thử offline. Không cần reset mạng hay tắt SSH. Không có nhánh tự chọn phương án1 khi người dùng chưa trả lời.

## Đang chờ gì ở tôi

Quyết định về đúng ngoại lệ kiểm chứng mới nói trên. Lý do phải hỏi là quy tắc no-retry trong kế hoạch đã khóa `sponge-sim/prereg/QA_PI3B_NMS_PREDECESSOR_SUPERVISOR_20261115.md`, không phải thiếu quyền tối ưu code. Đề xuất đã có code, test, collector và cấu hình để review; chưa cần duyệt full NMS.
