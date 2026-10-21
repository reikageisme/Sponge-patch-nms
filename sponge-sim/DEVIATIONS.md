# DEVIATIONS — sai lệch so với PREREG

Mỗi mục: ngày, PREREG nào, thay đổi gì, lý do, đã thấy dữ liệu đo chính chưa.

(chưa có)

## 2026-10-21 — E2a: phân tích A/A post-hoc
- PREREG: `prereg/PREREG_E2a.md` (tag `prereg-e2a-20261021`).
- Thêm `studies/e2_proxy/e2a_posthoc_aa.py` -> `results/e2a/20261021T145544/posthoc_aa.json`.
- Lý do: sau khi thấy `summary.json:attack_induced_share` (mean dương ở mọi case dù mean ΔN ≈ 0 hoặc âm) và
  `noise_vs_effect` (clean–clean p90 13,6 ms), nghi chỉ số bị chi phối bởi cú vọt thời gian và thứ tự đo; cần A/A cùng công thức.
- Đã thấy dữ liệu: CÓ. Gắn nhãn POST-HOC; không thay kết quả định trước.

## 2026-10-21 — E5 (run `results/e5/20261021T151412`), ghi SAU khi thấy dữ liệu
1. **Verify ghim E4 chỉ kiểm cận trên.** Tiêu chí PREREG_E5 (CPU-time/wall ≤ |allowed|+0,15 và ≥70% tải trên CPU được phép)
   cho E4 "passed" với effective_cores = 0,963 (`raw_E4.jsonl` dòng 1, `verify.effective_cores`), tức 4 thread KHÔNG chạy
   song song trong phiên đo (smoke trước đó: 3,78; kiểm lại sau phiên: 2,7–3,35). Forward E4 (trung vị 131,447 ms) gần bằng E1
   một core (138,442 ms). Hệ quả: E4 được gắn nhãn "ghim đúng tập CPU, song song không xác minh"; KHÔNG tự động dùng cho E1.
   Đề xuất cho các lần sau: thêm cận dưới effective_cores ≥ 0,7·|allowed| (chờ duyệt, chưa sửa PREREG đã tag).
2. **Cờ trôi 3% bị kích hoạt ở gần như mọi khối** (P1 11/11, E1 9/11, E4 11/11; max |Δ| 0,240 / 0,338 / 0,881).
   Phân tích độ nhạy "bỏ khối có cờ" vì vậy không thực hiện được (n_images = 0 → NaN ở P1, E4; E1 còn 20 ảnh).
   Thiết kế ABBA/BAAB trong ảnh làm trôi chậm triệt tiêu trong tỷ số A/A, nên endpoint chính vẫn tính được; nhưng
   ngưỡng 3% với benchmark tham chiếu hiện tại không phân biệt được khối tốt/xấu trên laptop này.
3. Trong phiên P1 (chạy đầu tiên), một lệnh Python ngắn (<1 s, sửa file script E1) đã chạy song song. Không loại dữ liệu.
