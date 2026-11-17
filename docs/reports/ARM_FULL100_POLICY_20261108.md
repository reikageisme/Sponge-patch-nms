# Cấu hình nguồn ngoài ở100% — chuẩn bị theo chỉ dẫn mới

## Đã xong

Người dùng báo pin100% và cho phép chạy. Đã ghi chỉ dẫn này vào CLAUDE.md và
`DRAFT_ARM_EXTERNAL_FULL100_20261108.md`; triển khai lựa chọn nguồn riêng
`full_100_external`. Cấu hình mặc định E5 30–80% và đang sạc giữ nguyên, vẫn
từ chối100%. Không sửa dữ liệu hoặc chấm lại bốn FAIL A36 cũ.

Lựa chọn mới yêu cầu đúng100%, nguồn cắm đã biết và status CHARGING/FULL/
NOT_CHARGING. Mất nguồn, DISCHARGING hoặc xuống99% dừng phiên; trạng thái thiếu,
không rõ hay mâu thuẫn bị từ chối. `FULL` vẫn ghi `charging=false`. Reading
giữ source/status gốc và nhật ký đầu phiên ghi toàn bộ policy trước worker.

244 tests host đạt5.96s; kiểm cả luồng FULL không đang sạc, mất nguồn ngắt
worker/không chạy khối sau, cổng cũ vẫn từ chối100 và ngưỡng nhiệt vẫn dừng.
Nguồn: `sponge-sim/results/arm_full100_policy_20261108/offline_01/pytest.stdout`
và `receipt.json` (19 hash source/test, hash stdout, mã thoát0). Đây là fixture,
chưa chạy tải đầy pin trên điện thoại.

## Phát hiện cần biết

Đây là điều kiện nguồn mới cho A36 làm thiết bị ARM đại diện. Không gọi kết quả
tương lai ở100% là tái lập điều kiện chủ động sạc30–80%, không gộp các phiên đó
thành cùng trạng thái nguồn, và không chuyển chúng thành kết quả Pi.

Các ngưỡng dừng nhiệt70C/mọi vùng hợp lệ và40C/pin, resume tất cả<55C/pin<38C,
ba lần ngắt liên tiếp, độ mới dữ liệu, nghỉ, baseline và không retry đều giữ.
Lựa chọn mới phải được nêu trong protocol/lock/tag thực tế trước đo. DRAFT và
test code không mở cổng tải khi registry/collector/QA còn thiếu.

Đã đọc lại ABI [thermal sysfs của kernel](https://www.kernel.org/doc/Documentation/thermal/sysfs-api.txt):
temp quy định milli-Celsius. A0 có vendor sys-therm-1/2 với raw481271/662478,
node bcl-level và các giá trị−273000; cần bằng chứng driver/ý nghĩa trước khi
gán đơn vị/validity. Không chia thêm theo độ lớn, bỏ node nóng hoặc dùng0 thay
missing để vượt cổng. Nguồn raw: metadataA0 `sysfs_raw.thermal`, các ID36/37
và các type tương ứng; CPU71800 trong A0 cũng được giữ nguyên, không là nhiệt
hiện tại. Registry hiện vẫn chưa được coi là đã xác minh.

A0E đã kiểm con trực tiếp đang ngủ trên A36/proot đạt, nhưng chưa kiểm tải
Torch, phản ứng cảm biến hay ghim v2. Từ code thay đổi này phải khóa source mới
trước thử live; không chạy source mới bằng lock A0E/E5 cũ. SSH tiếp tục giữ mở.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Kiểm collector live và registry nhiệt cho cấu hình nguồn mới → gõ:
"Tiếp tục full100 trên A36".

B. Giữ code này để đối chiếu Pi khi có board → gõ:
"Giữ cùng pipeline để đo Pi4 sau".

## Đang chờ gì ở tôi

Không cần duyệt lại trạng thái100% — chỉ dẫn đã được ghi nhận. Không cần bật
SSH thêm nếu vẫn kết nối được. Nguồn cắm/status và nhiệt sẽ lấy từ cảm biến
live; xác nhận máy rảnh/mạng thực hiện khi gói đo thật đã sẵn sàng.
