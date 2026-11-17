# Pi swapguard v2 — kế hoạch QA thiết bị hữu hạn, không benchmark

Ngày14/11/2026, SAU khi đã xem toàn bộ full01 cũ. Người dùng đã yêu cầu hoàn tất
phần còn thiếu như CUDA, bao gồm sửa source đã hỏi trước. Đây là kiểm kỹ thuật
cơ chế quản lý cấu hình, KHÔNG đăng ký lại hay cứu phép đo cũ, KHÔNG chạy Torch,
model, matmul, tải kiểm ghim hay timing suy luận.

## Vật liệu và điều kiện

- Source mới `studies/pi3b_600mhz_swapguard_v2/`: guard, worker copy có provenance,
  structural audit, analyzer copy/estimators nguyên, control, build_lock, stats.
- Host tests49PASS3.12s trên bản c sửa thứ tự stop/mask và kiểm setup unit; kiểm AST các hàm tính toán/estimator trùng nguồn cũ (chỉ chuyển import thống kê vào hàm).
  Thời gian test là thời gian kỹ thuật trên laptop, không endpoint nghiên cứu.
- Commit/tag kỹ thuật mới `qa-pi3b-swapguard-v2c-20261114` TRƯỚC thực hiện QA bên dưới.
  `lock.json` bind tất cả source và20input/weights nguyên; lock chưa là giấy
  phép đo. Model/inputs trên Pi được liên kết chỉ đọc từ workspace cũ, không
  ghi đè hoặc tái tạo vật liệu.
- SSH tanh@192.168.10.11, keypi_spongepi, strict hostkey; không tắt sshd.
  Không đồng thời có campaign/worker cũ hay mới. Đủ đĩa, nhiệt thấp hơn75C,
  không USB lưu trữ, trạng thái swap/governor/units được chụp trước/sau.
- Chỉ thay tạm governor/powersave và mask dưới `/run/systemd/system` của
  dev-zram0.swap, rpi-zram-writeback.service/timer. Không sửa `/etc`, nguồn,
  turbo, package, hoặc mask toàn hệ thống. Preexisting overrides/masks từ chối.
- Transient service cố định `sponge-pi3b-swapguard-v2.service`, User=tanh,
  KillMode=control-group, ExecStopPost restore, TimeoutStopSec120s. Không dùng
  shelltrap làm bảo đảm duy nhất. Mọi actionintent được ghi bền trước mutation.

## Năm case, theo thứ tự cố định

Mỗi case output riêng `~/sponge-sim/pi3b_600mhz_swapguard_v2/runs/<name>`;
chỉ một case đang chạy. Cú pháp launcher:

`~/sponge-venv/bin/python ~/sponge-sim/pi3b_600mhz_swapguard_v2/control.py launch --mode qa --name NAME --tag qa-pi3b-swapguard-v2c-20261114 --commit COMMIT --qa-seconds SECONDS --qa-timeout TIMEOUT`

1. `qa_c_normal_01`: seconds5, timeout90. Yêu cầu start swap của chính systemd
   phải bị mask từ chối; readiness ghi mainPID/childPID/startticks/invocation.
   Child chỉ ngủ; kết thúc thường và restore đạt.
2. `qa_c_mainkill_01`: seconds60, timeout120. Sau qa_ready, xác minh MainPID và
   InvocationID của đúng service khớp receipt rồi SIGKILL đúng main qua
   `systemctl kill --kill-whom=main`. Manager phải dọn child và chạy restore.
3. `qa_c_childkill_01`: seconds60, timeout120. Sau qa_ready, xác minh PID,
   startticks và cgroup service của child rồi SIGKILL chỉ child. Main phát hiện
   exit bất thường, service kết thúc lỗi, restore đạt. Không giết PID chỉ dựa
   trên số cũ mà thiếu kiểm identity.
4. `qa_c_timeout_01`: seconds90, timeout45. Phải thấy qa_ready TRƯỚC timeout;
   nếu timeout xảy ra trước apply/readiness thì case không chứng minh cleanup
   đang giữ lease. Manager phải dọn main/child và restore sau hết hạn.
5. `qa_c_disconnect_01`: seconds15, timeout90. Sau qa_ready, chỉ đóng tiến trình
   SSH frontend do trợ lý vừa mở, giữ sshd và service nguyên. Kết nối mới được
   phép đọc QA (không phải đang benchmark). Sleeping service phải hoàn tất và
   restore, không phụ thuộc frontend còn sống.

Đầu/giữa các case có thể đọc trạng thái và nhật ký vì không có phép đo thời
gian khoa học. Không chạy code khác song song khi sau này bắt đầu benchmark.

## Đạt, không đạt và cách lưu

- Đạt từng case khi activation_probe returncode khác0 và swap thực sự tắt;
  restore.json.status=RESTORED; governor/swap topology+priority/active states
  trở lại snapshot; cả ba runtime mask do launcher tạo đã gỡ; child cũ không
  còn đúng identity/startticks; không tiến trình sống còn trong cgroup service.
- Case1/5 kết thúc bình thường; case2/3/4 phải có trạng thái lỗi tương ứng,
  không đổi expected-failure thành đo thành công. Chỉ PASS chức năng cleanup.
- Có tối đa5case trên source này, không thử lại case lỗi để kiếm PASS. Nếu có
  lỗi code, giữ receipts, dừng QA; được sửa engineering trước đo nhưng phải
  checkpoint/tag phiên bản QA mới và ghi rõ lý do. Không thực hiện một scientific
  smoke/full nào cho tới khi mọi yêu cầu kỹ thuật đã được chứng minh.
- Lưu nguyên thư mục từng case, stdout/frontend result, kiểm SHA remote/local,
  snapshot và receipt đánh giá tại `results/pi3b_swapguard_v2_qa_20261114/`.
  Không viết đè file bằng tên run đã có; lease_state/status là journal vận hành
  thay thế atomically, lease_events là append-only; terminal/restore là exclusive.
- Mất điện/OS chết không được giả vờ đã test: runtime masks không persistent,
  nhưng đây chưa là bằng chứng khôi phục bằng ExecStopPost qua mất điện. QA
  chỉ kiểm những dạng dừng có systemd còn hoạt động đã liệt kê.

## Sau QA

Lịch sử chuẩn bị: tag kỹ thuật đầu `qa-pi3b-swapguard-v2-20261114`/1aafc852
đã deploy nhưng preflight phát hiện Pi không có scipy; CHƯA case nào chạy,
chưa đổi governor/swap/mask. Giữ `deployment_preflight.json` lỗi và42test receipt.
Bản b chuyển import thống kê đầy đủ sang lazy và khóa t-critical sums cho
n=2/20 trên laptop, cùng công thức/thứ tự nhân-chia MDE; test so khớp số và CLI
với scipy bị cấm import đều đạt. Không cài gói trên Pi. Đây là sửa engineering
trước scientific tag, không phải chạy lại benchmark lỗi hoặc nới cổng.

Bản b chạy đúng một case qa_normal_01 rồi FAIL trước activation/readiness:
mask active swap khiến stop chạy swapoff thiếu đối số; zram setup reset bị busy.
ExecStopPost gỡ hết mask/khôi phục governor và swap kernel còn active nhưng
start setup báo dependency failure, receipt RESTORE_FAILED được giữ. Không chạy
bốn case còn lại. Recovery riêng: stop unmasked swap thành công, start vẫn lỗi
setup; sau khi xác minh swap đã tắt, gọi đúng ExecStop --reset-device của setup
unit rồi start swap/timer thành công, helper Result=success. Giữ cả recovery lỗi
và recovery hoàn tất; không đổi receipt FAIL cũ.
Bản c stop unit khi vẫn còn metadata What, sau đó mask một batch/reload; restore
kiểm cả helper ActiveState/Result thay vì chỉ kernel swap. Thêm fixture partial
mask batch và helper-failed-but-kernel-matches. Đây là QA sửa code, chưa có
scientific timing/tag. Tên năm case mới tách riêng như trên, không ghi đè case b.

Viết PREREG đo mới với mọi thay đổi guard/campaign đã công khai, giữ endpoint,
cohort/model/cap/backends và ngưỡng cũ; tag mới trước smoke. Smoke và full hữu
hạn, kết quả FAIL giữ nguyên; không có full02 ở protocol cũ. Người dùng hiện
đã cho phép làm đầy đủ; không hỏi lại chỉ vì một bước vốn nằm trong phạm vi
được duyệt, nhưng không bỏ qua máy rảnh hoặc các cổng an toàn/chất lượng.
