# PREREG PI3B-PI1-SSD — Pi 3B một luồng, ở 600 MHz, có SSD USB cấp nguồn riêng nằm im

Ngày soạn: 15/11/2026. Tag dự kiến: `prereg-pi3b-pi1-ssd-20261115`. Soạn TRƯỚC khi đo.
Người dùng chọn "giữ SSD, đăng ký điều kiện riêng" (tin nhắn 15/11/2026).

## 1. Mục tiêu và vì sao là điều kiện RIÊNG

Bù mảnh còn thiếu của trục thiết bị Pi: phiên **một luồng** (logical CPU 3). Phiên này trong
protocol full20 đã bị hủy theo quy tắc dừng sau khi phiên tách-công-đoạn trượt, nên chưa có số.

Khác full20/PI4 ở đúng một điểm **đã khai báo**: một **SSD USB (ADATA SP900) cấp nguồn riêng,
dữ liệu qua USB, KHÔNG mount, nằm im** vẫn cắm trong lúc đo. Vì PI4 (số 1,80× trong bài) đo lúc
không có USB, nên **PI1 ở đây là một điều kiện phần cứng khác và KHÔNG gộp chung với PI4**. Báo
cáo để riêng, nêu rõ SSD có mặt. Lý do giữ SSD: người dùng dùng ổ làm lưu trữ và không muốn rút;
dung lượng không phải lý do (thẻ còn >1 GB, phiên chỉ ghi ~0,3 MB).

## 2. Giả thuyết và endpoint (đơn vị: ảnh, n = 20)

20 cặp ảnh sạch/nhiễu PGD đã khóa (ε = 16/255), cùng byte với full20/laptop (không chọn lại).

- **H1:** toàn trình ảnh nhiễu > ảnh sạch; endpoint `adv_total / clean_total` (tỷ số ghép cặp).
- **H2:** chặn ứng viên trước NMS (max_nms=300, max_det=300) giảm thời gian; `advcap_total / adv_total`.
- Phụ, mô tả: `advcap_total/clean_total`; `adv_forward/clean_forward` (≈1); tỷ trọng forward.
Họ {H1, H2}, hiệu chỉnh Holm.

## 3. Vật liệu và code

- 20 `*_inputs.pt` + `yolov8n-seg.pt` từ `results/laptop_seg_20261107/`, SHA trùng lock laptop và
  lock `pi3b_600mhz` (kiểm trong `build_lock.py`).
- `run.py` **sao từ** `studies/pi3b_600mhz/run.py`
  (SHA256 `9cc349be2c265fb4615d0016e9dae4a5aef53961df0d603abcb42d7a9fdbec8a`); thay đổi DUY NHẤT:
  thay vì từ chối khi có USB block device, worker **ghi nhận** thiết bị USB và bộ đếm I/O
  `/sys/block/<dev>/stat` ở mỗi lần chụp môi trường (để kiểm ổ nằm im), và yêu cầu ổ **không mount**.
  Pipeline, timing, các cổng khác, yêu cầu swap/governor giữ nguyên.
- `analyze.py` sao từ `studies/pi3b_600mhz/analyze.py`
  (SHA256 `8af562c9bca2b3e5c0889e7d11d271e0cd6d70e0c452028e239741ee002aea58`); thêm cổng `ssd_idle`
  (bộ đếm `sectors_written` của mọi ổ sd không đổi suốt phiên).
- `campaign_pi1.sh`: đặt governor `powersave`, **mask `dev-zram0.swap`** rồi `swapoff -a` (vá lỗi
  full01 bị zram bật lại giữa chừng), chạy ĐÚNG MỘT phiên `--profile PI1 --mode pipeline`, khôi
  phục governor + swap khi xong. run.py vẫn gate `SwapTotal==0` mỗi khối nên nếu swap bật lại thì
  phiên tự abort, không ra số bẩn.
- Thư viện Pi: torch 2.15.0+cpu, torchvision 0.29.2+cpu, ultralytics 8.4.90, numpy 2.5.4, Py 3.13.5;
  nms.py/ops.py SHA trùng lock laptop. torch khác laptop (2.13.0): parity chỉ mô tả.

## 4. Thiết kế đo

- Một phiên: `pipeline_PI1`, ghim CPU 3, 1 intra-op/1 inter-op thread, 20 ảnh × 6 nhánh × **4 lặp**.
- Mỗi ảnh một khối: nạp một cặp ảnh ngoài vùng bấm giờ; tham chiếu + đếm N_τ/K ngoài vùng bấm giờ;
  1 lượt khởi động/nhánh; thứ tự nhánh xáo bằng `random.Random(20261115 + 1000·ảnh + lặp)`.
- `clean_total_A` và `clean_total_B` = A/A. Đồng hồ `perf_counter_ns`, tắt gc, giải phóng sau cả hai
  mốc. Tham chiếu forward ảnh sạch đầu, đầu/mỗi khối/cuối; cờ khi lệch >3%.
- Môi trường (governor, xung thực, nhiệt, throttled, mem, vmstat, **usb_disk I/O**) ghi đầu mỗi khối,
  NGOÀI vùng bấm giờ.
- Smoke (sau tag): 2 ảnh, 2 lặp, thư mục riêng; chỉ kiểm đường chạy, không gộp.

## 5. Cổng chất lượng (đặt trước)

`quality_pass` khi đồng thời: chạy xong không abort; đủ 20 ảnh; governor `powersave` mọi điểm; xung
thực ∈ [594, 606] MHz; swap tắt mọi điểm; kiểm ghim CPU đạt đầu/cuối; cờ tham chiếu ≤ 2;
|trung bình log A/A| ≤ 0,02; MDE log ≤ 0,05; **và `ssd_idle` = đúng** (SSD không ghi gì suốt phiên).
Dừng an toàn: nhiệt ≥ 75 °C, MemAvailable < 40 MB, affinity đổi, SSD bị mount.

Phiên không đạt cổng giữ nguyên, báo là "không đạt", không chạy lại lấy số đẹp. Chỉ khởi động lại một
lần nếu chết trước dòng timing đầu vì hạ tầng (mất SSH/hết đĩa), ghi DEVIATIONS.md. Cờ tụt áp
(`0x50005`) là điều kiện khai báo, ghi lại, không phải tiêu chí loại.

## 6. Phân tích và cách báo

`analyze.py`. Mỗi endpoint: log tỷ số theo ảnh; trung bình hình học, CI95% bootstrap 20.000 lần theo
ảnh (seed 20261115 + chỉ số), p đảo dấu chính xác, d_z; Holm cho {H1, H2}; A/A + MDE. So khớp số đếm
với laptop (mô tả). Báo **"Pi 3B 1 luồng, 600 MHz do thiếu áp, có SSD USB cấp nguồn riêng nằm im"**;
không quy đổi 1,2 GHz, không gộp với PI4, không so tuyệt đối laptop/A36, không kết luận DoS.

## 7. Giới hạn biết trước

Một board cũ thiếu áp ép 600 MHz; một luồng; có SSD USB (điều kiện khác PI4); tensor đã chuẩn bị,
không camera/patch vật lý; 20 ảnh; yolov8n-seg; torch khác bản laptop; forward chiếm phần lớn thời
gian; không đo dịch vụ có hạn chót. Không đại diện Pi 3B ở 1,2 GHz hay khi không có USB.
