# BẢN NHÁP đăng ký trước: đo lại theo góp ý của thầy (27/11/2026)

**Trạng thái: NHÁP, CHƯA có hiệu lực.** Chỉ có hiệu lực khi tác giả đọc, chốt các mục "CHỜ CHỐT" dưới đây, đổi tên file
thành `PREREG_AMD_REVISION_<ngày>.md`, commit và tạo tag `prereg-amd-revision-<ngày>` TRƯỚC smoke.

## Lý do
Góp ý 27/11 (nguyên văn trong `docs/KE_HOACH_SUA_PHAN_BIEN_20261127.md` của nhánh harness): (1) phiên YOLOv5s (E10) có MDE trong phiên
2,8%, khoảng 60 lần A/A, và Bảng 10 cho thấy mức tăng toàn trình nhỏ hơn mức tăng NMS đo riêng ở cả 6 ô; (2) N* rơi vào mức thấp nhất
của lưới; (3) cần ngưỡng "gây hại" bên cạnh ngưỡng "phát hiện được".

**Đã thấy dữ liệu:** toàn bộ kết quả `amd_20261124/full-01` và chẩn đoán post hoc `results/review_20261127/diag_posthoc.json`
(báo cáo `docs/reports/REVIEW_B_POSTHOC_20261127.md`). Chẩn đoán đó cho thấy thời gian sạch của E10 có hai mức (khoảng 270 và 299 ms)
nhảy giữa các đơn vị ngay trong cùng một ảnh, còn E9 có hai mức cố định theo ảnh. Các dự đoán dưới đây dựa trên chẩn đoán đó, không mù.

## Môi trường (giống đợt 24/11)
Xubuntu Live 24.04.5, AMD Ryzen 5 5500, CPU logic 2, `amd-pstate-epp` governor `performance`, min = max = 3 600 000 kHz,
boost tắt toàn máy, CPU 8 offline, torch 1 luồng, không swap/zram trong lúc đo. Venv cùng phiên bản gói với
`results/amd_20261124/full-01/e10/environment.txt` (CHỜ CHỐT: ghi lại `pip freeze` thực tế vào hồ sơ trước tag).
Đầu vào: `transfer/inputs_revision_20261128.tar` (sha256 `af37f48d36ad24a65536c089f09f2aa13f2da89295aaa39d34bdf842f5b20d6d`,
1403 file + `INPUTS_SHA256.txt`); runner tự kiểm SHA-256 trọng số và nhiễu loạn.

## Cổng chung
Như `PREREG_AMD_REPLICATION_20261124.md`: `lock_env.sh verify 2 --seconds 10` trước và sau mỗi thí nghiệm, CPU 8 offline, boost 0,
thêm: không có swap đang bật. HEAD đúng commit của tag, cây `sponge-sim` sạch. Không chạy việc khác trên máy trong lúc đo (quy tắc 9);
người dùng điều khiển qua SSH từ laptop, chỉ dùng lệnh đọc trạng thái sau khi một thí nghiệm kết thúc.

## Thí nghiệm (thứ tự cố định; smoke cả ba rồi dừng chờ duyệt, rồi phiên chính)
1. **E9-R** `studies/e9r_pipeline_finegrid/run.py`: như E9 phần A, lưới N mịn hơn
   (320 px: 0, 10, 30, 50, 100, 300, 1000, 2100; 640 px: 0, 10, 30, 50, 100, 300, 1000, 3000, 8400), 20 ảnh, 3 hình học, cap không/300,
   4 backend, 5 lần (320) và 3 lần (640). Ước lượng khoảng 0,9 giờ (E9 cũ 0,61 giờ).
2. **E10-R** `studies/e10r_reference_rerun/run.py`: như E10, 50 ảnh × 5 seed × 2 phương pháp + 2 nhánh sạch, nhưng 3 + 20 lần
   (micro và pipeline), mốc thời gian lồng trong lần gọi toàn trình, đếm page fault. Ước lượng 3,5-4 giờ (E10 cũ 0,67 giờ với 3 lần).
3. **E10-RM (thăm dò)** cùng runner, `--malloc-fixed --n-images 10`: cố định ngưỡng mmap/trim của glibc. Không phải endpoint chính.

## Endpoint
- **E9-R, chính:** N* theo đúng quy tắc E9 (mức lưới nhỏ nhất có cận dưới KTC 95% của tỷ số toàn trình > 1 + MDE A/A Linux;
  0,046% ở 320 px, 0,020% ở 640 px). **Phụ:** N_harm = mức lưới nhỏ nhất có cận dưới KTC 95% của Δt_total trung bình > Δt_harm.
- **E10-R, chính:** như E10 (tỷ số N, tỷ số NMS, tỷ số toàn trình với MDE trong phiên, quy tắc Amdahl đã đăng ký 24/11, không đổi).
  **Mới:** (a) phân rã Bảng 10 với NMS đo TRONG lần gọi toàn trình: Δt_NMS,in so với Δt_NMS,micro, và phần còn lại
  Δt_total − Δt_NMS,in; (b) Δt_total so với Δt_harm; (c) MDE trong phiên của nhánh sạch.
- **E10-RM:** tỷ lệ đơn vị ở mức chậm và MDE trong phiên so với E10-R (mô tả).
- **Ngưỡng gây hại Δt_harm — CHỜ CHỐT:** đề xuất 5% của khung 33,33 ms ở 30 FPS = 1,667 ms (chính) và 10% = 3,333 ms (độ nhạy).

## Dự đoán (theo chẩn đoán post hoc, không mù)
- E9-R: N* ở 320 px nằm dưới 100 với ít nhất một backend (thầy hỏi chính điểm này); N_harm của thư viện ở 320 px ≥ 1000.
- E10-R: nếu hai mức thời gian còn, MDE trong phiên vẫn cỡ vài phần trăm vì 20 lần lặp không làm mất phương sai giữa đơn vị;
  Δt_NMS,in ≈ Δt_NMS,micro (khác biệt micro/pipeline nhỏ hơn 1 ms); phần còn lại nằm quanh 0.
- Nếu đơn vị chậm có số page fault lớn hơn rõ rệt, giả thuyết cấp phát bộ nhớ được ủng hộ; E10-RM khi đó có ít đơn vị chậm hơn.

## Phân tích
Script phân tích viết và commit TRƯỚC khi chạy phiên chính (CHỜ: `studies/e10r_reference_rerun/analyze.py`, dùng lại logic
`studies/e10_reference/analyze.py` và `stage_decomp.py`; E9-R dùng nguyên `studies/e9_pipeline/analyze.py`). KTC bootstrap
percentile 20 000 lần, hai tầng ảnh × seed cho E10-R. Phân tích theo trạng thái nhanh/chậm là phụ, gắn nhãn thăm dò.

## Báo cáo và quyết định
Báo mọi endpoint nguyên trạng, kèm MDE. Một phiên chính cho mỗi thí nghiệm; chạy lại chỉ khi hỏng kỹ thuật, ghi DEVIATIONS trước.
Số của đợt này là bộ số riêng; không gộp với 24/11. Đưa vào bài thay số E10/E9 cũ hay đặt cạnh: quyết định sau khi có kết quả,
ghi rõ trong bài là đo lại theo phản biện.

## Ngoài phạm vi
CPU đa luồng và GPU (cần PREREG riêng), Pi 3B, điện thoại, E1, E12, A/A (không đổi).

## Đầu ra
`runs/amd-revision/<smoke|full>/<thí nghiệm>/` trên máy live; sao về `sponge-sim/results/amd_revision_<ngày>/` kèm SHA-256 hai phía
TRƯỚC khi tắt máy live (mọi thứ trong RAM mất khi tắt).
