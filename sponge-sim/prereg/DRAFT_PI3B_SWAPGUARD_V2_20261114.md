# DRAFT — Pi 3B 600 MHz, kiểm soát swap cho một protocol mới

**Cập nhật14/11:** người dùng đã cho phép làm đầy đủ sau câu hỏi phê duyệt.
Đề xuất lịch sử dưới đây được thay bằng `PREREG_PI3B_SWAPGUARD_V2_20261114.md`;
QA/source/thay đổi stage A/A xem protocol chính và PROGRESS. Giữ nội dung
"chưa duyệt" bên dưới như trạng thái tại thời điểm viết draft, không phải cổng
quyền còn thiếu hiện tại. Chưa đo gì dưới tag mới tại checkpoint cập nhật này.

**CHƯA ĐƯỢC PHÊ DUYỆT, CHƯA ĐĂNG KÝ, CHƯA TAG, CHƯA TRIỂN KHAI.**
Tài liệu thiết kế sau khi đã thấy toàn bộ full_01. Không cho phép chạy lại dưới
tag `prereg-pi3b-600mhz-20261114`, không đổi cách chấm phiên cũ. Cần người dùng
cho phép sửa code theo HANDOFF_CODEX_PI3B_20261114.md trước khi triển khai.

## 1. Bằng chứng và phạm vi kết luận

- Phiên cũ: `results/pi3b_600mhz_20261114/protocol_status.json`, báo cáo
  `docs/reports/PI3B_600MHZ_RESULTS_20261114.md`: main hoàn tất nhưng swap FAIL;
  PI1/stages không có timing, lỗi cổng cấu hình, không thuộc ngoại lệ retry.
- Journal lịch sử cho thấy swap kích hoạt lúc 04:09:21 UTC ngày 14/11/2026,
  trước raw environment đầu tiên phát hiện swap tại dòng 243. Nguồn:
  `results/pi3b_600mhz_20261114/transfer_verification_20261114_01/read_only_swap_history_utc.json`.
- Điều tra bổ sung CHỈ ĐỌC:
  `results/pi3b_swap_diagnosis_20261114/systemd_readonly_01.json` chứa các bản ghi
  JSON trong `output`; chọn bản ghi theo `argv`. Journal cửa sổ
  04:08:50–04:09:40 UTC ghi `man-db.service` bắt đầu cùng giây với zram setup,
  và hoàn tất lúc 04:09:33, báo CPU time 2.166 s. Không quy CPU time này thành
  sai lệch timing của worker; chưa có phép gán ảnh/nhánh cho tải hệ thống đó.
- `systemd_readonly_02.json:payload.files` lưu nội dung và SHA của cấu hình
  hiện tại; `payload.commands` lưu readback dependencies và phiên bản gói.
  Generated `dev-zram0.swap` thuộc `rpi-swap`; `swap.target` Wants thiết bị này;
  `sysinit.target` Wants `swap.target`; `man-db.service` Requires `sysinit.target`.
  `rpi-zram-writeback.service` cũng Requires trực tiếp `dev-zram0.swap`, timer
  được sinh có OnBootSec=180min và OnUnitActiveSec=24h.
- Đây là các ĐƯỜNG CÓ THỂ kích hoạt, không phải chứng minh ai đã gửi job lúc
  04:09:19. Nội dung unit được đọc SAU phiên, không tự chứng minh unit lịch sử
  có cùng byte. Không thử tái hiện bằng cách khởi động dịch vụ trên Pi.

## 2. Vấn đề code cần sửa, không sửa hồi tố

Đối chiếu source đã khóa `studies/pi3b_600mhz/`:

1. `campaign.sh` chỉ `swapoff -a`; generated systemd unit vẫn có thể được kéo
   lên bởi transaction khác. Script chỉ `set -u`, chưa dừng chắc chắn khi setup
   governor/swap thất bại. Sau lỗi một phiên, vẫn chạy phiên kế tiếp.
2. `run.py:worker` kiểm swap/governor/USB trước khi tạo resultdir. Vì vậy lỗi
   chuẩn bị không có manifest/raw bên trong resultdir, chỉ có log ngoài.
3. `run.py:guard` giữa các khối chỉ chặn affinity/nhiệt/bộ nhớ; ghi lại swap và
   governor nhưng chưa chặn vi phạm; chưa kiểm lại USB tại đó.
4. `campaign.sh:restore` luôn swapon `/dev/zram0`, chưa phục hồi theo trạng thái
   ban đầu của từng unit/device. EXIT trap riêng lẻ không bảo đảm khôi phục
   sau SIGKILL, mất cha hoặc mất phiên SSH.
5. `analyze.py:gates` chưa đủ để tự chứng minh lịch hoàn chỉnh: số ảnh không
   kiểm ID cụ thể, `all()` trên tập pin rỗng có thể True, chưa bắt buộc số mẫu
   mỗi nhánh/lượt. Phiên full_01 đã được kiểm bổ sung bằng structural_audit;
   vấn đề này không làm mất audit cũ nhưng phải sửa cho phiên mới.

## 3. Thiết kế triển khai đề xuất

Tạo thư mục nghiên cứu MỚI, dự kiến `studies/pi3b_600mhz_swapguard_v2/`, không
sửa source tag cũ. Header nguồn kèm file/dòng/SHA; lock mới bind toàn bộ runner,
launcher, analyzer, helpers và cấu hình. Không cài gói, không sửa `/etc`, không
đổi nguồn/turbo, không tắt SSH và không chạm dữ liệu cũ.

### 3.1. Giao dịch cấu hình có sổ theo dõi quyền sở hữu

- Chụp governor, swap devices/priority, ActiveState/UnitFileState/mask của các
  unit liên quan, symlink runtime và timer. Chỉ tiếp tục nếu topology đúng mẫu
  đã khai báo; trường hợp lạ từ chối, không tự suy đoán hay tắt mọi timer.
- Nếu được duyệt: tạm dừng timer writeback và runtime-mask đúng
  `dev-zram0.swap`, `rpi-zram-writeback.service` cùng timer của nó; thứ tự và
  lệnh cụ thể phải được kiểm kỹ thuật trước khi khóa. Không mask swap.target,
  sysinit.target hay dịch vụ hệ thống khác. Không tự tắt man-db/apt/cron.
- Chỉ thay đổi unit/runtime symlink mà launcher sở hữu; không unmask mask có
  sẵn. Không ghi cấu hình persistent. Giữ ghi nhận từng bước đã thành công để
  partial setup cũng có thể khôi phục đúng.
- Kiểm `SwapTotal==0`, `/proc/swaps` không có device, trạng thái unit masked
  đúng dự kiến và governor readback trước khi cho worker chạy. Chỉ dừng timer
  hoặc chỉ gọi swapoff không được coi là đủ.
- Khôi phục governor và swap/unit/timer theo snapshot, có readback và receipt.
  Không mặc định swapon khi ban đầu swap tắt. Chỉ owner có quyền dọn mask mình
  tạo. Nếu restore thất bại: kết thúc lỗi và báo, không ghi thành công giả.
- Trước tải phải có cơ chế supervisor/cleanup độc lập với SSH được kiểm cho
  mất worker, mất parent, timeout và partial setup. Không hứa SIGKILL sẽ chạy
  Python finally/shell trap. Nếu cơ chế chưa được chứng minh thì KHÔNG ĐO.

### 3.2. Worker và chứng cứ

- Tạo thư mục độc quyền/receipt chuẩn bị TRƯỚC import nặng, ghi nguồn/config và
  lý do từ chối có cấu trúc; không ghi đè tên đã tồn tại.
- Guard ngoài đồng hồ trước/sau mỗi đơn vị đo đã đăng ký: swap, governor,
  affinity, nhiệt, MemAvailable và USB. Vi phạm/đọc lỗi thì ghi terminal abort,
  flush dữ liệu đã có và dừng; không tự sửa điều kiện rồi tiếp tục.
- Kiểm swap đầu/cuối mỗi vùng gọi không chứng minh swap tắt liên tục giữa hai
  lần đọc. Runtime mask, lịch sử unit và delta pswpin/pswpout là kiểm bổ sung;
  không gọi bộ đếm toàn hệ thống là của riêng worker. Tần suất guard/chi phí
  ngoài đồng hồ phải khóa trước đo, vì chính guard có thể làm đổi cache/drift.
- Main vi phạm cổng cấu hình/safety thì dừng campaign, không chạy tiếp phụ để
  có thêm số trong cùng tình trạng hỏng. Mọi phiên chưa bắt đầu ghi rõ cancelled.
- Analyzer mới kiểm đúng ID, nhánh, repeats, thứ tự seed, positive durations,
  đầy đủ pin/reference/env/start/terminal, source/config hash; không cho cổng
  pass nhờ tập rỗng. Thiếu dữ liệu => diagnostic/incomplete, không lọc ảnh cứu.

## 4. Kiểm kỹ thuật bắt buộc trước PREREG/tag đo mới

Tất cả dưới đây là KẾ HOẠCH, chưa được thực hiện hay coi là PASS:

- Host fixtures: swap tái bật, governor/USB đổi, đọc lỗi, partial setup, mask
  có sẵn, swap ban đầu tắt, restore lỗi, reused output, missing/duplicate rows,
  pin/reference thiếu, wrong ID và sai lịch => từ chối đúng và giữ chứng cứ.
- Thiết bị: kiểm setup/restore có giới hạn, không model/matmul/inference;
  chứng minh yêu cầu start swap bị chặn trong khi mask do launcher sở hữu.
  Không chạy fault injection trên cấu hình không được phép hoặc qua SSH duy
  nhất nếu cleanup chưa bảo đảm. Giữ toàn bộ receipt; lỗi kết thúc QA hữu hạn.
- Kiểm cleanup khi worker/launcher chết và khi mất kết nối bằng payload chỉ
  ngủ, không benchmark. Không gây OOM/nhiệt/thiếu áp chủ động để thử cổng.
- Kiểm trên fixture thống kê và cấu trúc raw; không chạy model để tối ưu
  threshold. Không thay renderer/backend/conf/cap để cải thiện hiệu ứng.

## 5. Thiết kế đo dự kiến — chưa có quyền chạy

- Điều kiện vẫn Pi 3B thiếu áp, 600 MHz/powersave, cùng weights/runtime/backend
  đã xác minh, cùng 20 cặp tensor, seed và endpoints H1/H2; không chọn lại ảnh
  vì đã thấy hiệu ứng. Đơn vị suy luận ảnh, không phải số lần lặp.
- Đây là phép đo sửa lỗi điều kiện SAU khi thấy full_01, không phải cohort mới
  hoặc tái lập độc lập. Báo cả phiên cũ FAIL và phiên mới, không pool hai phiên.
- Dự kiến giữ số lặp, thứ tự ba phiên, warm-up, liều K, A/A, MDE và ngưỡng drift
  của bản cũ. Khóa mọi khác biệt guard/supervisor như yếu tố protocol mới.
  Giữ giới hạn suy luận và Holm {H1,H2}; chưa có camera/service/DoS.
- Sau khi người dùng duyệt source và protocol: commit/tag mới TRƯỚC đo; một
  smoke cố định 2 ảnh/2 lặp, không grid, không retry để kiếm PASS. Smoke không
  góp kết quả; phân tích xong dừng chờ duyệt trước full theo sponge-research.
- Chỉ một full hữu hạn nếu được duyệt sau smoke; output riêng, không full_02
  dưới tag cũ. Lỗi code/cấu hình/safety hoặc đã có timing => không retry.
  Nếu cần thay code/guard/threshold sau tag, đóng protocol và hỏi trước.
- Chỉ tiến trình đo hoạt động khi timing; điều khiển chỉ chờ handle hoàn tất,
  không polling/readback thủ công song song. Guard đăng ký nằm trong worker.

## 6. Điểm chờ phê duyệt

Người dùng có thể duyệt **triển khai source mới và kiểm thử offline** trước;
việc đó chưa cho phép thay cấu hình Pi, device QA hay chạy smoke/full. Sau khi
có source/test reviewable sẽ xin duyệt bước thiết bị/PREREG theo đúng phạm vi.
Không có dữ liệu đo mới hoặc cải thiện chất lượng nào được tuyên bố từ draft.
