# Gói bản thảo v3 — "Số lượng ứng viên trước NMS có dự đoán được độ trễ…" (tiếng Việt, mẫu Elsevier CAS cas-dc)

Dựng ngày 02/11/2026 bằng `paper_vi/build_submission.py` từ `paper_vi/main_vi.tex` (bản tiếng Việt để rà soát), dùng lại preamble CAS tiếng Việt của `paper_Q3_submission/`.
Thư mục tự chứa: tải nguyên thư mục (hoặc `paper_Q3_submission_v4.zip` ở gốc repo) lên Overleaf là biên dịch được.

## Tệp
- `main_vi.tex` — bản thảo (tệp chính).
- `references.bib` — 40 mục (gộp `paper_en/references.bib` và `paper_vi/refs_extra.bib`); mọi khóa `\cite` đều có mục.
- `cas-dc.cls`, `cas-common.sty` — lớp và gói Elsevier CAS (chép từ gói cũ).
- `figures/fig2`–`fig8` (7 hình PDF) — sinh từ dữ liệu bằng `sponge-sim/studies/figures/make_figs.py` (Hình 2–3) và `make_figs_v3.py` (Hình 4–8); cộng một sơ đồ pipeline vẽ bằng TikZ ngay trong bài.
- `thumbnails/` — biểu tượng của mẫu CAS (tùy chọn).

## Cách biên dịch
Trên Overleaf: Menu → Compiler chọn **XeLaTeX** (preamble có nhánh XeTeX dùng font TeX Gyre) rồi Recompile; Overleaf tự chạy BibTeX.
Trên máy có TeX Live/MiKTeX đầy đủ:
```
xelatex main_vi
bibtex main_vi
xelatex main_vi
xelatex main_vi
```
pdfLaTeX cũng được nếu có gói `vntex` (mã hóa T5).

## Kiểm tra cấu trúc đã làm (02/11/2026, chưa biên dịch thật vì máy không có TeX)
- Ngoặc `{}` cân; mọi môi trường `\begin`/`\end` khớp; không nhãn trùng; mọi `\ref` có `\label`; cả 7 hình đều tồn tại.
- Không có ký tự Unicode đặc biệt ngoài chữ Latin/tiếng Việt trong thân bài.
- Đã chuyển chú thích `%` ra khỏi dòng khóa của các mục `.bib` (BibTeX không hiểu `%` bên trong mục).
- Bảng hẹp đặt trong một cột (`[!htbp]`), bảng rộng toàn trang (`table*`, `[!t]`); có `\FloatBarrier` (gói placeins) trước mỗi mục/tiểu mục và nới tham số đặt float, để hình/bảng không trôi về cuối bài.

## Lưu ý về nội dung
- Không còn chỗ đỏ. Kết quả 640 px lấy từ lần đo lại (A/A 640 px: drift 3/11, MDE 0,69%; đo patch 640 px: lệch tham chiếu tối đa 7,9%); lần đo đầu bị nhiễu nặng được giữ trong kho mã và nêu trong Bảng sai lệch.
- 19 tài liệu bổ sung (chép từ bản thảo cũ) chưa kiểm bằng web; xem chú thích trong `references.bib`.
- Các bảng của phần cohort lịch sử được chép từ bản thảo trước, phải truy lại tới dữ liệu thô trước khi nộp (danh sách ở `docs/NGUON_SO_LIEU.md` của kho mã).
- Đây là bản tiếng Việt để rà soát; bản tiếng Anh sẽ dịch sau khi tác giả duyệt bản này.

## Bản v4 (02/11/2026, sau review chi tiết của thầy)
- Cấu trúc mới: giao thức -> đối chứng dương -> ngưỡng toàn trình và mô hình kiểu Amdahl -> tấn công toàn ảnh thật (Overload, Phantom Sponges đo lại dưới ghim lõi) -> nghiên cứu tình huống SG-GA ngắn.
- Đã cắt phần cohort lịch sử và điện thoại (chỉ còn một câu trong giới hạn); bảng patch cân 100 ảnh × 5 seed; công thức dùng t_meas/t_pred; thêm Hình 9.
- Hình 8 (`fig8_historical.pdf`) còn trong thư mục nhưng không dùng.

## Bản v4 (03/11/2026)
- Bảng số trong `main_vi.tex` và `supplement_vi.tex` được chèn từ `paper_vi/tables/tab_*.tex` (sinh tự động bởi `paper_vi/tables/make_tables.py`); không sửa tay trong gói.
- Trước khi dựng gói: `python -X utf8 paper_vi/tables/check_numbers.py --all` phải in `KẾT QUẢ: ĐẠT`; rồi `python -X utf8 paper_vi/build_submission.py`.
- `supplement_vi.tex` là tài liệu bổ sung, biên dịch riêng (XeLaTeX hoặc pdfLaTeX với gói vietnamese).
- Chỗ đỏ `[TODO: ...]` là số chờ lần đo lại patch (E11) hoặc thông tin tác giả chờ nhóm quyết định.
