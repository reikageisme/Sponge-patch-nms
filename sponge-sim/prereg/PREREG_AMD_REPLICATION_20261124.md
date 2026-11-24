# Đăng ký trước: đo lại các phép đo thời gian CPU của bài trên máy AMD khóa xung

24/11/2026. Người dùng (chủ máy) cho phép đo lại toàn bộ trên máy này, không giới hạn thời gian.
Nhánh `amd-replication-20261124`, tách từ tag `prereg-aa-linux-20261124`. Chốt bằng commit và tag
`prereg-amd-replication-20261124` TRƯỚC smoke và trước mọi phiên chính.

## Lý do
Phản biện nội bộ 16/11 (A1, A2, A8) yêu cầu đo trên máy khóa tần số. Laptop Windows không khóa được.
A/A trên máy này (`PREREG_AA_LINUX_20261124.md`, phiên `full-01`) đã đạt audit với MDE toàn trình
0,046% (320 px) và 0,020% (640 px). Đợt này lặp lại các phép đo đưa vào bảng của bài trên cùng máy, cùng cấu hình.

**Đã thấy dữ liệu:** toàn bộ kết quả laptop (E1, E5, E6, E9, E10, E11) và A/A Linux đã được xem.
Mọi dự đoán dưới đây là xác nhận lại trên thiết bị mới, không phải giả thuyết mù.

## Môi trường (giống A/A Linux)
Xubuntu Live 24.04.5, kernel 7.0.0-31-generic, AMD Ryzen 5 5500 (B450M-HDV), RAM 3,7 GB, không swap.
CPU logic 2, `amd-pstate-epp` governor `performance`, min = max = 3 600 000 kHz, boost tắt toàn máy,
CPU 8 (SMT anh em của CPU 2) offline. Profile `P1_cpu2` = `{"P1_cpu2": [2]}`; torch 1 luồng.
Mã: bản `main` trên GitHub (gồm phần sửa theo phản biện), không sửa. Venv: Torch 2.13.0+cpu, torchvision 0.28.0+cpu,
Ultralytics 8.4.90 (đã dùng cho A/A). Đầu vào lấy từ repo gốc (chỉ đọc), kiểm SHA-256 bởi chính các runner:
trọng số YOLOv8n `f59b3d83…`, 100 ảnh E5, patch E7 `patch_q62500` seed 0–4, nhiễu E10 seed 0–4, bản ghi X1-500 sạch.

## Cổng chung (mỗi thí nghiệm, smoke và phiên chính)
- Trước và sau: `lock_env.sh verify 2 --seconds 10` đạt (mọi mẫu `Bzy_MHz` trong ±1% mục tiêu, Busy ≥ 95%),
  CPU 8 offline, boost = 0. Không đạt: dừng, không chạy thí nghiệm tiếp theo.
- HEAD đúng commit của tag, cây `sponge-sim` sạch.
- Trong lúc đo không chạy việc nào khác trên máy (quy tắc 9), người dùng không dùng máy. Ngoại lệ do người dùng chọn: `btop` để mở cho người dùng theo dõi; ghi trạng thái này vào hồ sơ, không coi là sai lệch.
- Không swap, không zram trong lúc đo. Nếu thiếu bộ nhớ làm hỏng phiên: ghi DEVIATIONS trước khi chạy lại.

## Thí nghiệm (thứ tự cố định; mỗi cái smoke rồi phiên chính)
1. **E1** (đối chứng dương, dose-response, cap): thiết kế, lưới, seed và endpoint như `PREREG_E1.md`,
   chỉ profile `P1_cpu2` (`--profiles P1_cpu2`). MDE lấy từ A/A Linux 320 px.
2. **E1-NC1L** (A8, đối chứng dương với ứng viên dồn vào một lớp): `run.py --nc1-large`, cùng endpoint E1.
3. **E9** (tiêm vào toàn pipeline, ngưỡng n*): như `PREREG_E9.md` phần A; phần B dùng A/A Linux 320/640 và E1 của đợt này.
4. **E10** (Overload, Phantom Sponges trên YOLOv5s): như `PREREG_E10.md`, 50 ảnh × 5 seed.
5. **E12** (bảng patch, A1): `DRAFT_PREREG_E12_patch_remeasure_gated.md` có hiệu lực từ tag này, giữ nguyên E11
   (100 ảnh, 12 nhánh, patch đóng băng, fail-closed X1-500), cộng cổng trôi theo khối và E12-P4..P6.

## Dự đoán (theo kết quả laptop)
- E1: thời gian NMS tăng theo N_tau ở mọi ô (cận dưới CI của tỷ số 10^2 → 10^4 > 1); cap top-300 giảm thời gian ở mọi ô có N > 300.
- E1-NC1L: tỷ số 10^2 → 10^4 của ô một lớp > 1 ở mọi backend.
- E9: tồn tại ngưỡng n* hữu hạn cho torch_pure ở 320 px; với thư viện, n* ở 640 px lớn hơn ở 320 px.
- E10: ít nhất một biến thể × backend có cận dưới CI tỷ số toàn trình > 1 + MDE trong phiên.
- E12 (giữ H1–H3 của E11): H1 với tv_nms không nhánh GA nào (C1–C4, B1, B2) làm chậm toàn trình phát hiện được;
  H2 B4 với torch_pure làm chậm phát hiện được, B4 với tv_nms thì không; H3 R̂ nằm trong CI 95% của R ở ≥ 14/16 ô.

## Báo cáo và quyết định
- Báo mọi endpoint nguyên trạng, kể cả khi trái dự đoán; kèm MDE. Không chọn giữa nhiều lần chạy.
- Mỗi thí nghiệm một phiên chính; chạy lại chỉ khi hỏng kỹ thuật, lý do ghi vào DEVIATIONS trước khi chạy lại.
- Số AMD là bộ số riêng của thiết bị này; không gộp với số laptop. Cách đưa vào bài quyết định sau khi có kết quả.

## Ngoài phạm vi
A6 (cần GPU), A7 (chưa có runner tách công đoạn riêng; E10 có tách công đoạn post hoc), A11 (chưa chốt siêu tham số),
Pi 3B, điện thoại, phần phân đoạn (segmentation).

## Đầu ra
`runs/amd-20261124/<smoke|full>/<thí nghiệm>/`: manifest, raw JSONL, summary, log kiểm xung trước/sau, `pip freeze`,
commit của tag. Sao về máy Windows `sponge-sim/results/amd_20261124/` kèm SHA-256 hai phía.
