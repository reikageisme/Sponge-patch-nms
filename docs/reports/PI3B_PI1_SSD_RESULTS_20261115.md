# Pi 3B một luồng (600 MHz, có SSD USB nằm im) — kết quả đạt chất lượng

Điều kiện RIÊNG, không gộp với PI4 (đo lúc không có USB). Tag `prereg-pi3b-pi1-ssd-20261115`,
commit `d5c14c83bdff26ed5722db489375742aaba217d7`. Tự tính lại từ raw, khớp summary.

## Đã xong
- Đo Pi 3B **một luồng** (ghim CPU 3), 20 cặp ảnh đã khóa, 4 lặp, ở 600 MHz do thiếu áp, có SSD
  ADATA SP900 cấp nguồn riêng, chưa mount, cắm suốt.
- **Qua toàn bộ cổng chất lượng**, gồm cổng mới `ssd_idle`: SSD ghi **0 sector** trong cả 2,5 giờ
  → chứng minh ổ nằm im, không nhiễu phép đo. Swap tắt suốt (đã vá lỗi zram của full01), xung khóa
  600 MHz, 0 cờ trôi tham chiếu, A/A lệch 0,0004 (rất ổn).
- **Ảnh nhiễu chậm hơn ảnh sạch 1,97 lần** (geomean 1,967274; 20/20 ảnh cùng chiều; CI95%
  [1,902; 2,030]; p đảo dấu 1,9×10⁻⁶).
- **Chặn ứng viên trước NMS kéo thời gian còn 0,70 lần** (0,698813; CI95% [0,682; 0,718]).
- Trung vị: sạch 10,06 s, nhiễu 20,30 s, nhiễu+chặn 13,77 s, forward 9,92 s. Forward chiếm 98,7% thời
  gian ảnh sạch.

## Phát hiện cần biết
- **Một luồng cho tỷ số CAO HƠN bốn luồng** (1,97× so với 1,80× của PI4). Hợp lý: khâu dựng mask được
  hưởng lợi từ nhiều luồng, nên khi chỉ có một luồng, phần mask mà attack bơm phồng chiếm tỷ trọng lớn
  hơn → tỷ số toàn trình tăng. Cùng một board, cùng điều kiện 600 MHz.
- Đây là **điều kiện khác PI4** (có SSD). Không gộp số, không so tuyệt đối. SSD nằm im nên ảnh hưởng tới
  thời gian là tối thiểu, nhưng vẫn ghi rõ là điều kiện riêng.
- Vẫn ở 600 MHz do thiếu áp; không đại diện Pi 3B ở 1,2 GHz.

## Nguồn số (truy tới raw)
- Raw: `sponge-sim/results/pi3b_pi1_ssd_20261115/runs/full_01/pipeline_PI1/raw.jsonl`.
- Tổng hợp + cổng: `…/summary.json:pipeline_PI1` (quality_pass, gates.ssd_idle,
  h1_adv_over_clean.geomean_ratio/ratio_ci95, h2_advcap_over_adv, aa_cleanA_over_cleanB.mean,
  mde_ratio_80pct, median_ms_across_images).
- Cổng ssd_idle: `gates.usb_sectors_written_values = {"sda":[0],"sdb":[0]}`.
