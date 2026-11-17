# A36: nguồn pin qua Termux đã đọc được, chưa đủ điều kiện chạy tải

## Đã xong

Sau khi người dùng tự cài CLI và mời SSH, đã đăng ký phạm vi đọc mới trước khi
truy cập: tag `prereg-arm-power-a0c-20261107`, commit
`e48d114bed4398c357725e5e350048fc3b60926f`. Một lần đọc trong Termux gốc,
không vào proot, không lặp đường sysfs đã thất bại. Không cài gói, đổi quyền,
Torch import, ghim lõi, chạy ma trận/model hoặc đo tốc độ trên điện thoại.

Nguồn `termux_power_metadata.sh` SHA256
`d708e809716b890266e1a2c034b8a324fc9ebd7eedc29d2974ec646730d3f54a`
đã được kiểm trên máy trước khi gọi. Câu lệnh pin trả mã0, stderr rỗng;
toàn bộ 14 file thu được khớp hash remote/local. Bản đọc gốc:

| Trường JSON | Giá trị |
|---|---|
| `present`, `health` | `true`, `GOOD` |
| `plugged`, `status` | `UNPLUGGED`, `DISCHARGING` |
| `percentage` | 24 |
| `temperature` | 35.7 |

Nguồn: `sponge-sim/results/phone_a36/power_a0c_20261107_01/capture/battery.raw.json`,
SHA256 `99697461b34ed73f686cf281eb56e6502fafcb6ea0a0d891c8c9dbdce22fce96`;
`verification.json:remote_local_files_sha256,battery_raw_selector_values`.
Nguồn pin đã truy cập được; kết quả hiện tại vẫn chặn tải vì SOC thấp và đang xả.

Metadata native ghi `TERMUX_VERSION=googleplay.2026.10.09`, còn
`TERMUX_APK_RELEASE` rỗng. `packages.txt` ghi CLI `termux-api=0.59.1` và
`termux-tools=3.0.9`; đây không phải version ứng dụng bổ sung Android.
Thông tin người dùng gửi trước đó (25%,36.1) được giữ riêng tại
`operator_update_api_working.json`, không thay raw đọc qua SSH (24%,35.7).

Đã viết `termux_power.py` để kiểm bytes JSON, không tạo thời gian lấy mẫu khi
chỉ phân tích dữ liệu lưu. Hàm nối dữ liệu live yêu cầu thời gian monotonic
bắt đầu/kết thúc của cả pin và bộ cảm biến nhiệt đã xác minh. Nó giữ thời điểm
bắt đầu cũ nhất, từ chối dữ liệu thiếu/cũ/tương lai và không điền CPU bằng0.
Không chia nhiệt độ lần nữa, suy đang sạc từ cắm dây hoặc suy SOC từ level/scale.

216 tests host đạt trong5.88s, gồm parser/guard mới và hồi quy ARM/CPU/paper.
Đợt đầu có215 tests đạt và2 lỗi setup/teardown cho cùng case64KiB: pytest đưa
toàn bộ bytes vào tên test, vượt giới hạn biến môi trường Windows32767 ký tự.
Đã đặt tên test ngắn; giữ nguyên payload64KiB và mọi điều kiện chấp nhận.
Đây là kiểm code với fixture, không phải kiểm cảm biến live hay chất lượng ARM.
Nguồn receipt: `host_tests.json` trong cùng thư mục kết quả A0C.

Đã đóng sshd sau lấy dữ liệu; probe trả connection refused. Không có tải chạy
trên điện thoại khi kết thúc giai đoạn. Mọi raw/run cũ giữ nguyên.

## Phát hiện cần biết

Cần đính chính hướng dẫn cài app chung trước khi biết nguồn Termux: source
Google Play hiện xử lý `BatteryStatus` ngay trong app chính; đọc pin thành
công không tự chứng minh app bổ sung vừa cài đã được dùng. Không cần gỡ hay
chuyển bản Termux. Căn cứ:
[bộ định tuyến Google Play](https://github.com/termux-play-store/termux-apps/blob/main/termux-app/src/main/java/com/termux/app/api/TermuxApiHandler.java).
Đây là source nhánh main đã đọc, chưa phải fingerprint nhị phân trên A36.

[Source pin Google Play](https://github.com/termux-play-store/termux-apps/blob/main/termux-app/src/main/java/com/termux/app/api/BatteryStatusAPI.java)
trả nhiệt độ số theo Celsius, giá trị thiếu có thể là null; bộ đọc từ chối null.
Hợp đồng ban đầu để viết parser là [API v0.53.0](https://github.com/termux/termux-api/blob/v0.53.0/app/src/main/java/com/termux/api/apis/BatteryStatusAPI.java).
Chưa xác minh đúng source/release/binary tuyến gọi thực tế của APK đã cài.
Không dùng độ lớn35.7 làm bằng chứng đơn vị hoặc coi CLI0.59.1 là APK0.59.1.

Yêu cầu healthGOOD là điều kiện mới của adapter dự thảo, phải ghi trước khi
dùng trong protocol live; không thêm hồi tố vào các phiên cũ. FULL và
NOT_CHARGING được giữ là trạng thái biết rõ nhưng không đang sạc, nên không
qua cổng sạc hiện tại. Dòng điện âm/dương không thay trạng thái sạc.

Timestamp A0C là UTC wall trước/sau query, không phải monotonic của supervisor.
Không gắn lại thời gian hiện tại vào raw này để coi như live Reading. Timeout
metadata10s+kill2 cũng không đáp ứng mặc nhiên helperdeadline2s/freshness6s
của dự thảo. Cần kiểm tuyến native/proot, tần suất và giới hạn phản ứng riêng.

Vẫn thiếu registry nhiệt CPU xác minh type/đơn vị/sentinel, runtime import đúng
fingerprint, kiểm dọn tiến trình con/cha chết trên Android/proot, chi phí cảm biến
và phản ứng thật. Nhiệt độ pin không thay nhiệt CPU. Chưa có worker v2 hoặc
thêm kết quả tốc độ A36/Pi; bốn FAIL điện thoại lịch sử không được chấm lại.
Parser mới chưa được nối vào collector thiết bị và không có trong bundle cũ.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Tiếp tục kiểm source và bộ đọc/giám sát offline → gõ: "Tiếp tục phần offline".

B. Khi pin đã30–80%, báo trạng thái sạc để chuẩn bị bước chỉ đọc kế tiếp → gõ:
"Pin đã trong30–80%, đang sạc; chuẩn bị kiểm cảm biến". Điều này chưa mở cổng tải.

## Đang chờ gì ở tôi

Đang chờ pin về30–80% và trạng thái sạc trước bước thiết bị kế tiếp. Chưa cần
bật SSH chỉ để lặp bản đọc A0C. Có thể tiếp tục việc A; không chờ thông tin này
để sửa/kiểm offline. Đo thật còn cần xác nhận máy rảnh và trạng thái mạng theo
CLAUDE.md, registry nhiệt, QA thiết bị và protocol/tag riêng.
