# ĐỀ XUẤT DỌN REPO — chờ bạn duyệt (chưa xóa gì)

Ngày 2026-10-21 (phiên tự chủ tối). Theo CLAUDE.md quy tắc 1 (không xóa/di chuyển
`outputs/**` hay raw/kết quả; muốn dọn thì đề xuất rồi chờ duyệt) và quy tắc 8
(không reset/clean/force). **Phiên này KHÔNG xóa bất kỳ file nào** — chỉ liệt kê để
bạn chạy khi tỉnh. Shell qua Cowork cũng bị chặn xóa mặc định, nên dù muốn tôi cũng
không thể tự xóa an toàn lúc bạn đang ngủ.

Toàn bộ file tracked đều phục hồi được qua `git`, nên xóa tracked là an toàn (có lịch sử).
Rủi ro thật chỉ nằm ở file **untracked trong `outputs/`** — đó là raw, không đụng.

---
## 0. TUYỆT ĐỐI KHÔNG ĐỤNG
- `outputs/**` — raw và kết quả đã chạy (quy tắc 1).
- `project_yolov13/**` — nhánh B, ~32 GB (quy tắc 3).
- `core/`, `attack/`, `experiments/` — code cũ (quy tắc 2; chỉ copy khi tái dùng).
- `*.pt` (vd `yolov8n.pt`, `sponge-sim/yolov8n.pt`) — trọng số, có trong provenance.
- `.git/`, `.venv/`, `_provenance/` (baseline SHA-256 của 1769 file — xóa là hỏng audit).
- `sponge-sim/` — harness + kết quả E5/E2a/R1/R2/R3 đang dùng cho bài.

---
## 1. AN TOÀN — xóa được ngay (cache tái tạo được)
Không phải nguồn, không phải kết quả; chạy lại là có.

PowerShell (Windows, tại gốc repo):
```powershell
# cache pytest + bytecode Python (BỎ QUA project_yolov13 cho nhanh)
Get-ChildItem -Recurse -Directory -Filter __pycache__ |
  Where-Object { $_.FullName -notmatch '\\project_yolov13\\' } | Remove-Item -Recurse -Force
Remove-Item -Recurse -Force .pytest_cache -ErrorAction SilentlyContinue
# rác build LaTeX nếu có ở gốc
Get-ChildItem -Include *.aux,*.bbl,*.blg,*.out,*.toc,*.synctex.gz -Recurse -File |
  Where-Object { $_.FullName -notmatch '\\project_yolov13\\' } | Remove-Item -Force
```
`.pytest_cache` hiện rỗng; `.codex_docx_review/` cũng rỗng (0 byte) — xóa được.

---
## 2. TRÙNG LẶP / ĐÃ THAY THẾ — nên DI CHUYỂN vào kho lưu, không xóa thẳng
Các bản Word/TeX cũ đã bị `BaoCaoKhoaHocAdversarialAttacks_Q1_VI_v2.tex` (bản chính)
và `paper_Q1_submission/` thay thế. Chúng vẫn được `_provenance` và các manifest tham
chiếu bằng đường dẫn → **xóa thẳng sẽ làm sai hash audit cũ**. Khuyến nghị gom vào
`paper/history/` để vừa gọn gốc repo vừa giữ truy vết:

| File (gốc repo) | Dung lượng | Xử lý đề xuất |
|---|---|---|
| `BaoCaoKhoaHocAdversarialAttacks.docx` | 2.9 MB | → `paper/history/` |
| `BaoCaoKhoaHocAdversarialAttacks_VI.docx` | 5.5 MB | → `paper/history/` |
| `BaoCaoKhoaHocAdversarialAttacks_NangCap_VI.docx` | 5.6 MB | → `paper/history/` |
| `DeCuong_NCKH.docx` | 5.1 MB | → `paper/history/` |
| `DeCuong_NCKH_Final.docx` | 5.1 MB | → `paper/history/` |
| `BaoCaoKhoaHocAdversarialAttacks.tex` | 68 KB | → `paper/history/` |
| `BaoCaoKhoaHocAdversarialAttacks_Q1_VI.tex` (v1) | 71 KB | → `paper/history/` |
| `_paper_revision_20261013/` | 30 MB | → `paper/history/` hoặc nén .zip rồi để trong `paper/history/` |

```powershell
# DI CHUYỂN (an toàn, giữ file). Chạy ở gốc repo:
New-Item -ItemType Directory -Force paper\history | Out-Null
Move-Item BaoCaoKhoaHocAdversarialAttacks.docx,BaoCaoKhoaHocAdversarialAttacks_VI.docx,`
  BaoCaoKhoaHocAdversarialAttacks_NangCap_VI.docx,DeCuong_NCKH.docx,DeCuong_NCKH_Final.docx,`
  BaoCaoKhoaHocAdversarialAttacks.tex,BaoCaoKhoaHocAdversarialAttacks_Q1_VI.tex paper\history\
Move-Item _paper_revision_20261013 paper\history\
```
Nếu bạn CHẮC CHẮN không cần (git vẫn giữ lịch sử): thay `Move-Item` bằng `git rm -r <file>`.

Lưu ý: GIỮ `BaoCaoKhoaHocAdversarialAttacks_Q1_VI_v2.tex` ở gốc (bản chính hiện tại)
và GIỮ `paper_Q1_submission/` (gói nộp mới tạo).

---
## 3. SCRIPT CŨ Ở GỐC — gom vào `legacy/` (không xóa; là code cũ, quy tắc 2)
Các script edge/train/demo thời kỳ đầu, README cũ còn trỏ tới → di chuyển, đừng xóa:
`fast_train.py`, `main_train.py`, `proper_dos_sim.py`, `simulate_edge_server.py`,
`test_headless_pi.py`, `test_physical_dos.py`, `train_blackbox.py`, `web_simulation.py`,
`check_x1.ps1`, `watch_x1.ps1`, `watch_x1_eval.ps1`.
```powershell
New-Item -ItemType Directory -Force legacy | Out-Null
Move-Item fast_train.py,main_train.py,proper_dos_sim.py,simulate_edge_server.py,`
  test_headless_pi.py,test_physical_dos.py,train_blackbox.py,web_simulation.py,`
  check_x1.ps1,watch_x1.ps1,watch_x1_eval.ps1 legacy\
```

---
## 4. XEM LẠI RỒI QUYẾT (không nằm trong phạm vi phiên này)
- `paper_assets_20261013/` (69 MB): thư viện ảnh lớn; bản nộp chỉ cần 9 ảnh (đã tách sẵn
  sang `paper_Q1_submission/`). Có thể nén để lưu trữ, nhưng manifest curation còn trỏ path cũ.
- `media/` (2.8 MB), `docs/media/` (3.3 MB), `archive/` (72 KB), `latex/` (8 KB),
  `logs/` (40 KB), `thumbnails/` (48 KB): rà từng cái, phần lớn là tư liệu cũ.
- Đổi tên folder/GitHub thành `sponge-patch-study`: xem `docs/repository-organization.md`
  (đã có phương án, About/topics, mapping remote) — việc này thuộc quyền bạn.

---
## Gợi ý thứ tự chạy
1) Mục 1 (cache) — vô hại, làm ngay.
2) Mục 3 (legacy/) rồi mục 2 (paper/history/) — kiểm `git status` sau mỗi bước.
3) Build lại `paper_Q1_submission/` trên Windows để chắc không hỏng gì.
4) Mục 4 cân nhắc sau.
Sau khi di chuyển, nếu README/đường dẫn nào gãy thì chỉ cần cập nhật link, không mất dữ liệu.

---
## ĐÃ THỰC HIỆN 2026-10-21 22:xx (bạn chọn "Dọn an toàn", đã cấp quyền xóa)
- XÓA cache: `__pycache__` ở _paper_revision_20261013, attack, core, experiments, sponge-sim/src, sponge-sim/tests, utils; `.pytest_cache`. (CHỪA `outputs/vendor_underload/__pycache__` theo quy tắc 1.)
- XÓA ở gốc: `test_headless_pi.py`, `test_physical_dos.py`, `ziDk7t3h` (file zip rác do lệnh zip lỗi để lại).
- CHUYỂN → `paper/history/`: 5 .docx cũ + `BaoCaoKhoaHocAdversarialAttacks.tex` + `..._Q1_VI.tex` (v1).
- CHUYỂN → `legacy/`: fast_train, main_train, proper_dos_sim, simulate_edge_server, train_blackbox, web_simulation (.py) + check_x1, watch_x1, watch_x1_eval (.ps1).
- GIỮ NGUYÊN: `outputs/`, `project_yolov13/`, `core/ attack/ experiments/` (+ test_extended_*), `sponge-sim/tests/`, `_provenance/`, weights.
- Tạo `paper_Q1_overleaf.zip` (gói Overleaf, main .tex ở gốc zip).
