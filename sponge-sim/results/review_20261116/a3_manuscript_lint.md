# A3. Soát hình thức bản thảo

Thư mục: `..\paper_en` (13 file .tex).

## 1. Dấu gạch (en dash, em dash, `--`, `---`): 153 chỗ

- `main.tex`: 47 chỗ. Ví dụ dòng 176: `is expressed in candidate--image forward passes: 10{`
- `tables_q3/tab_amdahl.tex`: 20 chỗ. Ví dụ dòng 11: `57 & 0.020 & 100 / 100 & -- \\`
- `tables_q3/tab_attacks.tex`: 8 chỗ. Ví dụ dòng 10: `0 $\to$ 5578.5 & 389 (135--753) & torchvision \textt`
- `tables_q3/tab_cap.tex`: 12 chỗ. Ví dụ dòng 10: `2129 & 29.6 & 72.0 (71.1--72.9) \\`
- `tables_q3/tab_decomp.tex`: 18 chỗ. Ví dụ dòng 10: `\texttt{nms} & 10.5 (6.8--14) & 5.24 (4.1--6.4) & 5`
- `tables_q3/tab_dose.tex`: 12 chỗ. Ví dụ dòng 10: `& 9.46 & 2129 & 225 & 221--231 & yes \\`
- `tables_q3/tab_patches.tex`: 25 chỗ. Ví dụ dòng 4: `mages $\times$ 5 seeds (0--4, chosen in advance). Th`
- `tables_q3/tab_spec.tex`: 1 chỗ. Ví dụ dòng 4: `use software EOT, seeds 0--9, and three budget level`
- `tables_q3/tab_threshold.tex`: 4 chỗ. Ví dụ dòng 17: `sured (ms) & 0.017 (0.014--0.019) & 0.99 (0.86--1.1)`
- `tables_q3/tab_x2.tex`: 6 chỗ. Ví dụ dòng 4: `patches inserted (seeds 0--4, optimized on YOLOv8n i`

Sửa: đổi mọi `--` trong khoảng số và từ ghép thành `-`; trong bib, `pages = {284--293}` do kiểu bst in ra en dash, đổi thành `284-293` hoặc sửa bst.

## 2. Tài liệu tham khảo: 21 mục, 13 mục không có doi / eprint / url

- `nicgslowdown2022` (inproceedings)
- `phantom2023` (inproceedings)
- `overload2024` (inproceedings)
- `underload2025` (inproceedings)
- `evade2025` (inproceedings)
- `bitflip2025` (inproceedings)
- `brown2017patch` (misc)
- `athalye2018eot` (inproceedings)
- `ilyas2018blackbox` (inproceedings)
- `jocher2023ultralytics` (misc)
- `paszke2019pytorch` (inproceedings)
- `efron1979bootstrap` (article)
- `holm1979` (article)

- 13 mục có khoảng trang viết bằng `--`.

## 3. Độ dài

- Abstract: khoảng 258 từ (hướng dẫn: 200 đến 260).
- Kết luận: khoảng 148 từ (hướng dẫn: 150 đến 200).
- Caption: 26 cái, 9 cái dài hơn 60 từ.
  - 194 từ, `tables_q3/tab_amdahl.tex`: Amdahl-type model $R_{\mathrm{pred}} = 1+\Delta t_{\mathrm{N...
  - 171 từ, `tables_q3/tab_patches.tex`: Effect of the frozen patches (SHA-256) relative to clean ima...
  - 149 từ, `tables_q3/tab_nstar.tex`: Threshold $N^{*}$: the smallest grid level at which end-to-e...
  - 111 từ, `tables_q3/tab_attacks.tex`: Adaptive variants of two whole-image attacks, after Overload...
  - 84 từ, `tables_q3/tab_x2.tex`: \textbf{Post hoc, historical data}: pre-NMS candidate counts...
  - 82 từ, `tables_q3/tab_decomp.tex`: \textbf{Post hoc}, YOLOv5s (640 px, one pinned CPU core): de...
  - 73 từ, `tables_q3/tab_threshold.tex`: \textbf{Post hoc.} Threshold $\Delta t^{*}$ for the end-to-e...
  - 72 từ, `tables_q3/tab_aa.tex`: A/A calibration on the pinned laptop profile (logical CPU 2;...
  - 65 từ, `main.tex`: Effect of optimized patches relative to clean images on the ...

## 4. Cấu trúc theo hướng dẫn viết

- Nhắc "RQn": 0 lần; nhắc "Q1..Q4": 6 lần. Nếu câu hỏi nghiên cứu đang đặt tên Q1 đến Q4 thì đổi thành RQ1 đến RQ4 để khỏi lẫn với hạng tạp chí.
- Ô "Answer to RQ": 0. Danh sách đóng góp C1..Cn: có.
- Trích định luật Amdahl: chưa thấy lệnh cite nào có khoá chứa amdahl.