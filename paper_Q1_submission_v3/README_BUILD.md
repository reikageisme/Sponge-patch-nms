# Gói bản thảo v3 — "Số lượng ứng viên trước NMS có dự đoán được độ trễ…" (tiếng Việt, mẫu Elsevier CAS cas-dc)

Dựng ngày 02/11/2026 từ `paper_vi/main_vi.tex` (bản tiếng Việt để rà soát), dùng lại preamble CAS tiếng Việt của `paper_Q1_submission/`.
Thư mục tự chứa: tải nguyên thư mục (hoặc `paper_Q1_submission_v3.zip` ở gốc repo) lên Overleaf là biên dịch được.

## Tệp
- `main_vi.tex` — bản thảo (tệp chính).
- `references.bib` — 40 mục (gộp `paper_en/references.bib` và `paper_vi/refs_extra.bib`); mọi khóa `\cite` đều có mục.
- `cas-dc.cls`, `cas-common.sty` — lớp và gói Elsevier CAS (chép từ gói cũ).
- `figures/fig2_dose_response.pdf`, `figures/fig3_pred_vs_measured.pdf` — hình sinh từ dữ liệu bằng `sponge-sim/studies/figures/make_figs.py`.
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
- Ngoặc `{}` cân; mọi môi trường `\begin`/`\end` khớp; không nhãn trùng; mọi `\ref` có `\label`; hai hình đều tồn tại.
- Không có ký tự Unicode đặc biệt ngoài chữ Latin/tiếng Việt trong thân bài.
- Đã chuyển chú thích `%` ra khỏi dòng khóa của các mục `.bib` (BibTeX không hiểu `%` bên trong mục).
- Mọi bảng đặt ở dạng toàn trang (`table*`) để không tràn cột trong mẫu hai cột.

## Lưu ý về nội dung
- Còn đúng một chỗ đỏ "CHƯA CÓ SỐ": tác động của patch 640 px lên độ trễ (lần đo lại ở 640 px bị drift tham chiếu rất cao; chờ đo lại khi máy rảnh).
- 19 tài liệu bổ sung (chép từ bản thảo cũ) chưa kiểm bằng web; xem chú thích trong `references.bib`.
- Các bảng của phần cohort lịch sử được chép từ bản thảo trước, phải truy lại tới dữ liệu thô trước khi nộp (danh sách ở `docs/NGUON_SO_LIEU.md` của kho mã).
- Đây là bản tiếng Việt để rà soát; bản tiếng Anh sẽ dịch sau khi tác giả duyệt bản này.
