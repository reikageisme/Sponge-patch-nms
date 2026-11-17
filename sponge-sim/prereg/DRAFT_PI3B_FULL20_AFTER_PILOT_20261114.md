# DRAFT — một full20 mới sau pilot Pi không đủ công suất

**Người dùng đã chấp thuận phương án khi trả lời câu hỏi duyệt sau pilot;
chưa tag, chưa chạy full. Không sửa hoặc mở lại protocol v2.**

Phản hồi: "với cả làm hết những gì có thể làm tối ưu và tối ưu cho số liệu
tốt nhất đẹp và khó khăn gì ghi ra luôn". Tiếp tục thực hiện trong phạm vi
đã hỏi, giữ20ảnh và cổng full, đồng thời ghi mọi lỗi/giới hạn. Phần "cần duyệt"
bên dưới là lịch sử đề xuất trước phản hồi; final PREREG/source mới sẽ khóa
trước full, không coi trạng thái duyệt này là một kết quả đo.

## Quyết định cần duyệt

Cho phép một protocol mới chạy đúng20ảnh đã dự kiến từ đầu, một lần đầy đủ,
giữ mọi cổng full, dùng smoke v2 đã thất bại làm pilot kỹ thuật; không đo lại
smoke, không gọi smoke cũ PASS, không chọn mẫu/endpoint/ngưỡng mới theo số đẹp.
Đây là thay đổi phương pháp SAU khi đã xem pilot, cần ghi công khai và chờ duyệt
trước tag/đo mới, không suy quyền đó từ thông báo tiếp tục tự động.

## Căn cứ có thể kiểm lại

- v2 smoke:2ảnh,24timing,72guardrecords; structural/swap/clock/pin/reference/A/A
  bias đạt. MDElog0.1335119103548224>0.05; full và hai phụ hủy, protocol đóng.
  Source `results/pi3b_swapguard_v2_20261114/runs/smoke_01/pipeline_PI4/gates.json`.
- Hai logA/A0.016402874846161878/−0.0025584017445723028, SD0.01340764725726188.
  t-based MDE dùng df=n−1; n2 có df1. Nếu giữ SD đó tại n20, phép tính cho
  0.008856137180298611, **chưa phải số đo hoặc bảo đảm sẽ PASS**. Không dùng
  ước lượng SD hai ảnh như chân lý; hình/JSONplanning là minh họa có điều kiện.
- Hai full cũ/QA/pilot đều đã thấy: không gọi protocol sau là độc lập hoặc
  preregistration từ trước mọi quan sát Pi. Không pool với oldfull bị swap.

## Thiết kế đề xuất, khóa trước bất kỳ full mới nào

1. Tập20IDs, tensors/model/runtime/backend/conf/IoU/640/FP32, CPUprofiles,
   sốlặp, warmups, reference schedule và seed như v2. Không đổi số ảnh thành
   giá trị nhỏ nhất đủ MDE dự đoán;20 là mục tiêu đã có từ trước pilot.
2. H1/H2 trong PI4 và Holm như cũ; image-bootstrap20k/exact signflip, AA+MDE;
   PI1/stage là phụ; A/A riêng NMS/mask vẫn có và FULL stage phải đạt.
3. Full giữ MDElog≤0.05, absmeanlogAA≤0.02, reference flags≤2, actualclock
   594–606MHz, swapOFF+mask, pinreadback+arithmetic, nhiệt/mem/USB/source/
   schedule, restore và noOOM/pswpdelta. Không nới ngưỡng nào của full.
4. Dùng pilot v2 để chứng minh đường chạy và công khai precisionFAIL, không
   lặp n2 để tìm noise nhỏ hơn. Nếu cần source/workspace mới để giữ v2 bất
   biến, copy có SHA/provenance; kiểm host/engineering không model trước tag.
   Không giấu việc quyết định mở full đã thay đổi sau khi thấy pilot.
5. Tối đa một campaign full gồm PI4→PI1→stages; từng phiên mới, dừng các phiên
   sau khi worker/gate fail. Tối đa6hcampaign/4h mỗi session; restore independently.
   FAIL/partial giữ nguyên và kết thúc; không thêm protocol tiếp để dò PASS.
6. Không mạng/gói/nguồn/turbo ngoài SSH và lease runtime đã duyệt. Không
   tắt sshd. Khi timing chỉ chờ handle, không đọc log hoặc làm việc khác.
7. Mọi raw/metadata/hashes lưu tên protocol mới. Không full02 dưới v2, không
   ghi đè source/tag/run cũ. Xác minh source/inputs/restore cả trước và sau.

## Những gì proposal không giải quyết

Không bảo đảm n20 sẽ đạt noisegate; NMS/mask control chưa được đo trên cohort
đầy đủ. Một Pi thiếu áp600MHz, cùng20ảnh, một bộ PGD không thành validation
ARM tổng quát, không có service/deadline/DoS, camera/patch thật hoặc accuracy
matched của cap. Chạy đầy đủ không đồng nghĩa thành công khoa học.

Nếu người dùng không duyệt thay đổi phương pháp này, giữ v2 CLOSED/FAIL và
chỉ hoàn thiện báo cáo/bài từ dữ liệu đã có. Không tự quyết định coi cổng
MDE của smoke là không quan trọng sau khi biết nó đã FAIL.
