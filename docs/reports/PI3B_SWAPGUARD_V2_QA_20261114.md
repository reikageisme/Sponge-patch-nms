# Pi swapguard v2 — kiểm kỹ thuật trước đo

## Đã xong

Người dùng đã cho phép làm đầy đủ phần Pi sau khi đã hỏi sửa code. Source mới
tách riêng; source/tag/dữ liệu full01 cũ giữ nguyên. Không nâng gói, đổi nguồn,
turbo hoặc cấu hình persistent; không tắt sshd.

Các kiểm kỹ thuật trên Pi dùng tiến trình chỉ ngủ, không model/matmul hoặc
đo latency phân đoạn. Năm case trên tag QA-c
`271fc81716c207dbf344453966a1ae606d85247c` đều đạt phạm vi đã kiểm:

| Case | Dừng dự kiến | Kết quả kiểm khôi phục |
|---|---|---|
|qa_c_normal_01|hoàn tất thường|RESTORED, child cũ không còn|
|qa_c_mainkill_01|SIGKILL main đã kiểm identity|RESTORED, manager dọn child|
|qa_c_childkill_01|SIGKILL child đã kiểm PID/startticks/cgroup|RESTORED, main phát hiện lỗi|
|qa_c_timeout_01|RuntimeMax45s sau khi đã quan sát READY|RESTORED, main/child được dọn|
|qa_c_disconnect_01|đóng đúng SSH frontend vừa tạo|service hoàn tất thường, RESTORED, sshd vẫn mở|

Ở từng case, systemd từ chối yêu cầu start swap khi mask còn hiệu lực;
readback governor/swap/units/helper trở lại snapshot, mask gỡ hết. Case fault
có exit lỗi đúng dự kiến, không bị đổi nhãn thành inference thành công.
Nguồn: `sponge-sim/results/pi3b_swapguard_v2_qa_20261114/qa_c_verification.json:cases`;
inspection mỗi case có lệnh/assertion và40file SHA remote/local khớp.
Journal riêng case disconnect chứng minh normal deactivation sau mất frontend.

Code đo sau QA bổ sung audit pin arithmetic/count/source-registration và hai
control A/A riêng cho NMS/mask; computation/estimator gốc giữ nguyên. Control/
guard cấu hình trùng byte đã QA; source đo cuối được khóa riêng trước timing.
Host suite cuối được ghi trong registration receipt, không coi số host test là
bằng chứng đo ARM đạt. Chưa có model timing mới tại checkpoint báo cáo QA này.

## Phát hiện cần biết

Hai lỗi engineering trước đó giữ nguyên:

1. Pi thiếu scipy: dừng trước QA/mutation. Full inferential analysis chuyển
   về laptop; gate Pi dùng t-critical sums n2/n20 đã khóa, cùng công thức MDE.
   Test so công thức và CLI khi cấm import scipy đạt, không cài thêm gói.
2. Normal-b mask trước stop: journal ghi swapoff thiếu đối số và zram setup
   busy; receipt RESTORE_FAILED. Bốn case b còn lại hủy. Recovery riêng giữ
   cả lỗi start dependency và bước hoàn tất: sau khi swap thật sự tắt, dùng
   đúng reset của setup unit, khởi động lại swap/timer, helper Resultsuccess.
   Bản c stop trước mask batch và kiểm thêm helper, không sửa receipt b.

Nguồn: `deployment_preflight.json`, `failed_case_verification.json`,
`qa_normal_01/{supervisor.log,restore.json,lease_events.jsonl}` và
`qa_normal_01.recovery*.json` trong gốc QA. Case b có5file gốc được kiểm hash.
Journal case disconnect có cảnh báo thiếu transient unit file trước startup;
service thực tế vẫn started/READY/hoàn tất/restore đạt. Giữ cảnh báo, chưa gán
nguyên nhân cho systemd; không lấy việc không có cảnh báo làm tiêu chí chọn run.

QA này chỉ chứng minh cơ chế trên năm tình huống đã thực hiện với sleeping
payload. Chưa thử mất điện, kernel chết, model OOM thật hay mọi cửa sổ chết
giữa các syscall cấu hình. Không gọi QA là latency/DoS hay mọi lỗi đều an toàn.
Guard đọc trước/sau không đo peak giữa lời gọi; RSS cuối khối không phải peak.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Tiếp tục theo quyền đã duyệt: PREREG/tag mới → một smoke → tối đa một full
khi đáp ứng cổng, cùng20ảnh/cùng endpoint chính → gõ: "Cứ tiếp tục đúng protocol".

B. Xem đối chiếu engineering trước → gõ: "Kiểm báo cáo QA Pi".

Nội dung A đang là hướng thực hiện; không yêu cầu người dùng duyệt lặp code.
Full01 cũ vẫn là FAIL, không retry dưới tag cũ hoặc gộp với dữ liệu mới.

## Đang chờ gì ở tôi

Không có thông tin cần thiết cho bước chuẩn bị protocol/đo đã được duyệt.
Nếu Pi không truy cập được hoặc trạng thái máy thay đổi, giữ nguyên kết quả
đang có và báo đúng điểm chặn. Không yêu cầu restart sshd khi nó vẫn hoạt động.
