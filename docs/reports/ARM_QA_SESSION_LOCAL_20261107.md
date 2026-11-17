# Nối worker QA với supervisor — kiểm offline và Linux cục bộ

## Đã xong

Đã nối bốn khối kiểm ghim theo thứ tự cố định với bộ giám sát nhiệt/pin, nghỉ giữa khối và nhật ký có xác nhận ghi. `qa_session.py` chuẩn bị file mới trong workspace, khóa hash source/config, tạo tiến trình con mới và giữ trách nhiệm dọn đúng nhóm tiến trình đã tạo. Không có lệnh triển khai/chạy tải điện thoại được đưa ra.

Đã xử lý hai điểm ở giao diện worker:

- Chuẩn bị ghim thất bại hoặc kết quả thiếu/sai cấu trúc trả mã thoát 65 để dừng phiên, giữ các khối sau là chưa chạy. Không nhầm việc “hàm trả về bình thường” với hoàn tất một khối đo.
- Một chẩn đoán đã hoàn tất nhưng FAIL/INCONCLUSIVE được giữ làm dữ liệu, có thể đi tiếp đúng khối đã định. Nó không chứng nhận profile. Checksum NaN/Inf được lưu `null`, kèm `output_finite=false` và FAIL, thay vì mất bản ghi vì JSON không nhận NaN.

**154 tests host đạt**, gồm ARM, CPU và phụ lục. Các trường hợp kiểm thêm gồm lỗi cảm biến/logger, mã thoát sau lỗi chuẩn bị, không chạy lại khối, source/config đổi, đường ghi ngoài workspace, lỗi dọn tiến trình và lỗi xác nhận nhật ký cuối.

Kiểm Linux cục bộ trên Ubuntu/WSL đã đạt **sáu kiểm tra điều khiển**, dùng worker giả không Torch/model/ma trận và cảm biến bằng file mẫu. Thực tế đã quan sát:

- Worker giả trả mã 65 khi chuẩn bị thất bại; nhóm tiến trình đã hết, ba khối sau không được tạo.
- Một chẩn đoán giả FAIL hoàn tất trả mã 0 nhưng vẫn `profile_qualified=false`.
- Bốn frame cảm biến mẫu được giữ đủ với hash config.
- Xác nhận ghi cuối sau dọn dẹp được giữ riêng; không dùng xác nhận của coordinator trước đó thay thế.

Source được commit **trước** kiểm Linux tại `b0362697e2bbcc93acc8caafdb3c3a407c3b42fb`. Tám file source thực thi được chụp lại và khớp checkpoint; 56 file artifact khớp SHA receipt. Hai hàm ánh xạ mã thoát trong worker giả được so AST với source thật, khớp định nghĩa. Nguồn:

- `sponge-sim/results/arm_qa_session_local_20261107/checkpoint_before_native.json`.
- `native_01/receipt.json` và `executed_source/`; SHA receipt `792ff6cec9e69cb736e050a8dd3787e81f7a08f030e6ab3e76cdf0f98f874ca1`.
- `native_postcheck.json`, với selector `checks_passed,source_files,artifact_files,captured_fixture_frames,copied_exit_function_ast_sha256`.

Đã xuất `sponge-sim/artifacts/arm_preflight_draft_20261107/bundle_02`: 14 file có hash, gồm tám file source. Bundle01 cũ giữ nguyên và cả 13 hash vẫn khớp. Các template CPU/runtime chưa được điền vẫn bị từ chối; bundle mới mang nhãn DRAFT/UNRUN, không cấp phép chạy tải.

## Phát hiện cần biết

Đây là sửa và kiểm giao diện điều khiển mới, **chưa xác định nguyên nhân bốn FAIL A36 lịch sử**. Worker trả dictionary là một giao diện cần ánh xạ đúng khi chạy thành tiến trình; chưa có bằng chứng A36 trước đây thất bại vì bỏ qua giá trị đó.

Ba mức bằng chứng phải giữ riêng:

| Mức kiểm | Đã kiểm được | Chưa kiểm được |
|---|---|---|
| Tests host | Logic guard, kết quả worker, kế hoạch, lỗi và dọn dẹp với hàm giả | Cảm biến, Torch hay quyền trên Android |
| Linux/WSL cục bộ | Tiến trình/helper thật, mã thoát, nhóm con, file/ACK với worker và cảm biến giả | Ghim tải, phản ứng nhiệt, chi phí quan sát hoặc hành vi proot Android |
| A36 | Chỉ có metadata A0/A0B trước đó | Chưa chạy worker v2, chưa có profile/timing ARM đạt |

Kiểm PID cha lúc khởi động chỉ phát hiện cha đã đổi **trước** khi worker bắt đầu. Nó không tự bảo đảm worker/descendant sẽ dừng nếu cha chết sau đó. Parent-death, descendant, độ trễ phản ứng và overhead trên Android/proot vẫn cần QA thật trước tải. Không dùng kết quả WSL để đóng các cổng này.

Nguồn SOC/sạc live, registry nhiệt đã xác minh type/đơn vị/sentinel và runtime import đúng fingerprint của A36 vẫn chưa đủ. Không đoán đơn vị từ độ lớn, bỏ sensor nóng/không rõ hoặc điền version runtime bằng DIST metadata. CLI pin/sạc không tìm thấy trước đây cũng không chứng minh ứng dụng Android Termux:API chưa được cài; đã hỏi thông tin này riêng, chưa giả định câu trả lời.

Mọi kết quả điều khiển vẫn `study_quality=NOT_ASSESSED` và `profile_qualified=false`. Không có thêm số liệu tốc độ điện thoại/Pi, A/A/MDE của model hay bằng chứng DoS. Không kết nối điện thoại, đổi power plan, cài gói hoặc truy cập máy thuê trong giai đoạn này.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Chốt nguồn pin/sạc và cảm biến A36 trước khi đăng ký QA thật → gõ: "Chốt nguồn pin/sạc A36".

B. Rà riêng dọn descendant và trường hợp cha chết, tiếp tục kiểm cục bộ → gõ: "Tiếp tục kiểm dọn tiến trình".

## Đang chờ gì ở tôi

Đang chờ thông tin Termux:API đã hỏi để chọn bước gỡ nguồn pin/sạc. Chưa cần bật lại SSH. Có thể tiếp tục việc B offline; không chạy tải A36 khi các cổng thiết bị còn thiếu.
