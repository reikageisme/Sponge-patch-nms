# Worker khi tiến trình giám sát chết — kiểm Linux cục bộ

## Đã xong

Đã sửa `posix_runtime.OwnGroup`: tiến trình mới bật cơ chế Linux gửi SIGKILL khi
luồng cha tạo nó chết, rồi mới exec lệnh worker/helper. Có kiểm PID cha trước
và sau thiết lập, đọc lại tín hiệu đã đặt và dừng nếu không hỗ trợ hoặc sai.
Mọi helper cảm biến/nhật ký và worker qua OwnGroup đều dùng cùng đường này.
Thời gian khởi động thêm thuộc deadline, chưa được coi là overhead chấp nhận
được trên A36. Không có phương án chạy tiếp mà bỏ cơ chế này khi thiết lập lỗi.

Source đã commit trước kiểm Linux tại
`a93902882df3d80abdbb14246f17158ad467999f`. Kiểm host tập trung40 tests đạt;
toàn bộ231 tests ARM/CPU/paper đạt6.87s. Các case mới gồm lỗi prctl, đọc lại sai,
cha đổi trước/sau thiết lập, sai argv, thứ tự thiết lập trước exec và giữ stdin
cho payload. Đây là fixture, chưa phải hành vi thiết bị.

Hai kiểm Linux mới đã kết thúc mã0:

| Kiểm | Điều đã quan sát |
|---|---|
| Cha thoát bằng `os._exit(23)` | Con trực tiếp đang ngủ kết thúc bằng SIGKILL, đã reap |
| Cha bị SIGKILL | Con trực tiếp đang ngủ kết thúc bằng SIGKILL, đã reap |
| Dọn thường | Worker bỏ qua TERM vẫn được KILL/reap; nhóm đã hết |
| Nối supervisor | Lỗi chuẩn bị trả65, ba cell sau chưa chạy, không retry |
| Nhật ký/cảm biến fixture | Đủ frame có hash và xác nhận cuối riêng sau cleanup |

Worker thực đọc lại death signal sau exec là SIGKILL, PID/PPID/PGID khớp.
Riêng tiến trình kiểm tạm làm subreaper để thu hồi orphan của chính nó rồi
khôi phục trạng thái cũ. Không đổi thiết lập toàn máy hoặc gắn vào tiến trình
có sẵn. Chỉ tiến trình ngủ/fixture; không Torch import, ma trận, model, affinity
hay endpoint đo hiệu năng/phản ứng trên phần cứng.

Nguồn bằng chứng:

- `sponge-sim/results/arm_parent_death_local_20261107/checkpoint_before_native.json`:
  chín source hash đối chiếu commit trước thực thi.
- `native_01/receipt.json`: năm kiểm cục bộ đạt, hai case parent death;
  SHA256 `ba8ede953e41cb97f26e39025574c32ec7c28229168c36ea3a36d3fc27017494`.
- `sponge-sim/results/arm_qa_session_local_20261107/native_02/receipt.json`:
  sáu kiểm phối hợp đạt, source/fixture riêng với native01 cũ;
  SHA256 `6cfaa90b1ba0215ead4519740ed3a755fcb1c25d49abc5f4adea4962442f9f77`.
- `native_postcheck.json`: snapshot source khớp checkpoint, toàn bộ68 file
  artifact của hai kiểm được kiểm hash; `host_tests.json` giữ hash16 test files.

## Phát hiện cần biết

Đây là bảo vệ **con trực tiếp** khi luồng cha chết, chưa giải quyết mọi cây
tiến trình. Theo [Linux man-pages](https://man7.org/linux/man-pages/man2/PR_SET_PDEATHSIG.2const.html),
fork không truyền thiết lập này cho tiến trình cháu; exec thường giữ thiết lập,
còn thay thông tin đặc quyền có thể xóa nó. Luồng tạo con chết cũng kích hoạt
tín hiệu dù các luồng khác của cha còn sống. Do đó worker phải được tạo từ
luồng giám sát còn sống suốt phiên; không được tự fork/đổi quyền rồi coi bảo vệ
vẫn đầy đủ. Bộ giám sát bị treo nhưng còn sống cũng là tình huống khác.

Không lấy PASS WSL làm PASS Android/proot. Còn cần kiểm chính trên A36 về quyền,
PID/PGID, tiến trình cháu, đoạn import/warmup và phản ứng cảm biến/nhật ký. Các
timeout trong kiểm chỉ là hạn chờ điều khiển fixture, không phải số liệu độ trễ
phản ứng đủ chuẩn hoặc bảo đảm dưới mọi trạng thái scheduler/OS.

Không có thêm số đo tốc độ ARM hoặc Pi, không chấm lại bốn FAIL A36 cũ và không
thay cổng A/A/MDE/reference. Các bundle01/02 và native receipts trước được giữ
nguyên; code đã đổi nên phải khóa source/protocol mới trước dùng trên thiết bị.

Theo chỉ dẫn mới của người dùng, CLAUDE.md đã sửa để giữ sshd mở suốt chiến dịch
ARM, chỉ đóng sau toàn bộ đo/test hoặc khi người dùng yêu cầu. A0C đóng SSH
trước khi có chỉ dẫn mới là log lịch sử. Khi bật lại, không đóng sau từng bước.
A36 Snapdragon6Gen3/RAM8GB theo user là thiết bị ARM đại diện để hoàn thiện
pipeline; metadata RAM thực tế còn cần kiểm. Không đổi tên kết quả thành Pi4.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Tiếp tục hoàn thiện cảm biến và giám sát cục bộ → gõ: "Tiếp tục offline".

B. Sau khi bật lại sshd, báo pin/sạc để chuẩn bị metadata thiết bị kế tiếp → gõ:
"Đã bật sshd, pin ...%, đang sạc". Chỉ chạy tải sau các cổng thiết bị/protocol.

## Đang chờ gì ở tôi

Câu hỏi trạng thái SSH/pin/sạc đã gửi; không cần duyệt lại các việc code đã cho
phép. Người dùng cho biết sẽ sạc qua đêm; đó chưa xác nhận SOC hiện tại nằm
trong30–80% hoặc nhiệt CPU đủ thấp. Tiếp tục việc A được trong lúc chờ.
