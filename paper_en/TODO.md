# paper_en/TODO.md — việc còn lại cho bản thảo tiếng Anh (đọc trước khi sửa `main.tex`)

Bản này là bản NHÁP MỚI, viết riêng; KHÔNG thay bản tiếng Việt chính thức (`BaoCaoKhoaHocAdversarialAttacks_Q1_VI_v2.tex`).
Tiêu đề trong `main.tex` là ĐỀ XUẤT theo yêu cầu thầy (bỏ "khai thác lỗ hổng/cạn kiệt tài nguyên"); chờ tác giả quyết định trước khi thay bản chính.

## 1. Chỗ trống dữ liệu (`\nodata{...}`) -> nguồn số
Đếm: `python paper_en/check_manuscript.py`. Mỗi ô lấy từ `sponge-sim/results/<run>/summary.json` (selector) khi có số đo; KHÔNG ước lượng.
| Chỗ trong bài | Nguồn (khi có) |
|---|---|
| Bảng A/A (MDE theo công đoạn/profile; số khối bị cờ) | `results/e5/<A/A P1_cpu2>/summary.json:profiles.P1_cpu2.stages.<stage>.mde_ratio_pct`; điện thoại: `results/phone_a36/<run>/summary.json:primary` + `drift_headline_first` |
| Bảng dose-response (tỷ số N=10^4 / 10^2) | `results/e1/<run>/summary.json:dose_1e2_to_1e4`; điện thoại cùng khóa |
| Bảng tác động patch (tỷ số N, NMS, toàn trình, MDE) | `results/e6/<run>/summary.json:arms.<arm>.N_tau0.01/N_tau0.25/nms_tau0.01_<backend>/total_<backend>` |
| Dự đoán chỉ-từ-N | `results/e6/<run>/summary.json:n_only_prediction_from_e1` |
| Tóm tắt, Discussion, Conclusion | viết sau khi có bảng, không trước |

## 2. Việc còn lại trước khi nộp
- Thay `\figtodo` (Hình 2, 3) bằng hình thật từ `results/e1`, `results/e6` (vẽ bằng script từ JSON, ghi script vào repo).
- Kiểm từng mục `[from memory]` trong `references.bib` với DOI/trang hội nghị (không có mạng khi soạn). Kiểm lại cách mô tả EVADE, Overload, SlowTrack với bài gốc.
- Biên dịch bằng TeX Live/MiKTeX (máy hiện không có TeX; mới chỉ kiểm cấu trúc bằng `check_manuscript.py`). Lệnh trong đầu `main.tex`.
- Giảm chữ số có nghĩa: tỷ số 3 chữ số có nghĩa, MDE 2 chữ số, khoảng tin cậy cùng độ chính xác với ước lượng.
- Thêm URL kho mã (ẩn danh khi nộp nếu tạp chí yêu cầu). Bổ sung Acknowledgement/Funding/Declaration of competing interest theo mẫu tạp chí.
- Cân nhắc thêm tài liệu nền cho Q1: khảo sát tính toán hiệu quả/độ bền hiệu năng, kiểm định benchmark đo thời gian, các NMS-free detector; mỗi mục mới phải kiểm nguồn.
