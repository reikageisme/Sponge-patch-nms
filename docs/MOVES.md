# Nhật ký di chuyển 04/11/2026 (không xóa gì; đảo ngược bằng `git mv` ngược lại)

| Cũ | Mới |
|---|---|
| `paper_vi/` | `paper/vi/` |
| `paper_Q1_submission/` | `paper/submission_Q1/` |
| `paper_Q1_submission_v3/` (+ `.zip`), `paper_Q3_submission_v4/`, `paper_Q1_overleaf.zip` | `paper/versions/` |
| `paper_Q3_submission_v5/` (+ `.zip`) | `paper/submission_Q3_v5/` (+ `.zip`) |
| `zenodo_bundle/` | `paper/zenodo_bundle/` |
| `BaoCaoKhoaHocAdversarialAttacks_Q1_VI_v2.tex`, `cas-common.sty`, `cas-dc.cls`, `references.bib`, `thumbnails/`, `media/` | `paper/vi_v2/` |
| `_paper_revision_20261013/` | `archive/paper_revision_20261013/` |
| `paper_assets_20261013/` | `archive/paper_assets_20261013/` |
| `legacy/`, `logs/`, `figures/`, `latex/` | `archive/legacy/`, `archive/logs/`, `archive/figures_vi/`, `archive/latex/` |
| `REVIEW/` | `docs/REVIEW/` |
| `REFRAME_REPORT.md`, `REPORT_Q3.md`, `README_REVIEW_VI.md`, `START_HERE_VI.md`, `REPRODUCE.md`, `q1q2_word_guide.md`, `SO_SANH_Q1_Q3.md`, `CLEANUP_PROPOSAL.md` | `docs/reports/` |

## Đã sửa đường dẫn trong
`paper/vi/build_submission.py`, `paper/vi/tables/make_tables.py` (độ sâu thư mục), `paper/vi/zenodo/make_bundle.py`, `paper/vi/main_vi.tex` và `supplement_vi.tex` (graphicspath), `paper_en/tables_q3/make_tables_en.py`, `sponge-sim/figures_en/comparison_en.py`, `.gitignore`, `CLAUDE.md`, `README.md`, `README.vi.md`.

## Chưa sửa (tài liệu lịch sử, chỉ còn nhắc đường dẫn cũ dạng chữ)
`docs/REVIEW/*`, `docs/reports/*`, `sponge-sim/PROGRESS.md`, `DEVIATIONS.md`, các manifest trong `_provenance/` (băm theo đường dẫn cũ). Script trong `archive/paper_revision_20261013/` vốn trỏ tới `D:\Physical-Visual-DoS-EdgeAI-main`, không chạy được từ trước.
`.codex_docx_review/` (thư mục rỗng, không có file) không còn ở gốc.
