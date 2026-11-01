# Gói nộp Q1 — Sponge Patch (bản tiếng Việt, mẫu Elsevier CAS cas-dc)

Thư mục này tự chứa để biên dịch bản thảo Q1.

## Tệp
- `BaoCaoKhoaHocAdversarialAttacks_Q1_VI.tex` — bản thảo chính (bản sao của `...Q1_VI_v2.tex` ở gốc repo, ngày 2026-10-21).
- `references.bib` — thư mục tham khảo đầy đủ, 31 mục (khớp 1-1 với các `\bibitem` trong bài).
- `cas-dc.cls`, `cas-common.sty` — lớp và gói Elsevier CAS.
- `media/*.png` — toàn bộ 9 hình (tên tiếng Anh) được `\includegraphics` tham chiếu; `\graphicspath` trỏ `media/`.
- `thumbnails/*.jpeg` — biểu tượng mạng xã hội của mẫu CAS (tuỳ chọn).

## Cách build (khuyến nghị — máy có TeX đầy đủ + vntex)
Bản thảo dùng mã hoá tiếng Việt T5 (`\usepackage[T5]{fontenc}` + `babel vietnamese`), cần **vntex**.
Trình biên dịch có nhánh XeTeX sẵn (fontspec + TeX Gyre) nên **xelatex** là lựa chọn tốt nhất:

```
xelatex BaoCaoKhoaHocAdversarialAttacks_Q1_VI
xelatex BaoCaoKhoaHocAdversarialAttacks_Q1_VI   # chạy 2 lần cho mục lục/tham chiếu
```

Bài dùng `thebibliography` nhúng sẵn nên **không bắt buộc chạy bibtex**. `references.bib` kèm theo để:
(1) nhiều tạp chí Q1 yêu cầu nộp .bib; (2) dễ chuyển sang BibTeX nếu muốn.

### Nếu muốn dùng BibTeX thay cho danh sách nhúng
Thay khối `\begin{thebibliography}...\end{thebibliography}` bằng:
```
\bibliographystyle{cas-model2-names} % hoặc model1-num-names
\bibliography{references}
```
rồi chạy: `xelatex → bibtex → xelatex → xelatex`.

## Kiểm tra cấu trúc đã làm (2026-10-21)
- `table*`: 15 mở / 15 đóng; `figure*`: 11/11; `tabularx`: 15/15 — cân bằng.
- Dấu `$` nội dòng: 962 (chẵn).
- Không có `\label` trùng.
- 31 `\bibitem`; mọi khoá `\cite` đều có mục; không mục nào thừa.
- Cả 9 ảnh `\includegraphics` đều tồn tại trong thư mục này.

## Chưa build được PDF trong môi trường Cowork (VM Linux)
TeXLive của VM thiếu `t5enc.def` (vntex), `babel-vietnamese`, `algorithm.sty`.
Không cài gói trong môi trường này theo quy tắc dự án. Hãy build trên máy Windows
(MiKTeX/TeX Live đầy đủ) như các lần trước.

## Lưu ý trung thực về nội dung
- E1 (dose-response) và E2b (confirmatory) **chưa đo sạch trên Windows ghim core**;
  bài để chúng ở phần Hạn chế/Hướng phát triển, không trình bày như kết quả đã có.
- Kết quả âm (SG-GA không vượt tìm kiếm ngẫu nhiên trên X1-500) được **giữ nguyên**.
- Bảng so sánh `tab:prior_attacks` mô tả định tính theo công trình gốc; không trừ số
  liệu giữa các cột để xếp hạng hiệu lực xuyên mối đe dọa.
- Hai mục arXiv 2026 (`trackflood2026`, `ebt2026`) trong `references.bib` **chưa xác minh**
  (ghi chú trong .bib); một số số trang 2025–2026 của các mục gốc chưa đối chiếu độc lập.
