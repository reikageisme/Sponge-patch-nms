# Kế hoạch sửa bài theo góp ý của thầy (27/11/2026)

Bản thảo được đối chiếu: `paper_en/main.tex` trên nhánh `reikage/main` = `amd-replication-20261124`, commit `c7ca8e3` (24/11/2026, "Manuscript: AMD frequency-locked numbers as the primary results"). Bản trên ổ đĩa (`harness/step1` @ `721ac76`) là bản CŨ trước khi chuyển sang máy AMD; không sửa bài trên bản đó.

Đánh số bảng trong PDF hiện tại (theo thứ tự `\input` trong main.tex): 1 = định vị (tab:related), 2 = A/A, 3 = dose, 4 = cap, 5 = một lớp (nc1), 6 = N*, 7 = ngưỡng ms, 8 = patch, 9 = tấn công toàn ảnh, 10 = tách phần (decomp), 11 = M_N/M_NK, 12 = Amdahl, 13 = Pi, 14 = sai lệch.

## 0. Góp ý của thầy (nguyên văn, người dùng dán vào chat 27/11)

> Vẽ pipeline đẹp hơn đi em @Tuananh
> Còn tồn từ lần trước: thiếu Daedalus, Beyond PhantomSponges, Chen ACCV 2024, TrackFlood, YOLO26, danh mục mới có 24 tài liệu. Vẫn trích Holm và Cameron dù không dùng. Bảng 1, 4, 5, 6 lệch cột trong bản trích văn bản, cần mở PDF xem lại.
> Đã sửa: Tiêu đề đã thu hẹp về "single-core CPU". Đổi sang máy Ryzen khóa xung 3,6 GHz, tắt boost và luồng SMT, kiểm bằng turbostat trước và sau, 14/14 lần kiểm đạt. Patch đã có số đo end-to-end thật, kèm kiểm định tương đương (TOST): không đổi quá 1%. Câu về N_τ đã ghi rõ các ô ngoại lệ. Đã có đoạn và bảng định vị so với EVADE. Thầy đã đứng tên và có ORCID.
> Còn phải sửa: Phiên YOLOv5s nhiễu 2,8%, gấp khoảng 60 lần A/A (0,046%) trên cùng máy, và chính tác giả viết là chưa rõ vì sao. Abstract và kết luận lại dựa vào phiên này. Bảng 10 còn cho thấy end-to-end tăng ít hơn phần NMS đo riêng ở cả 6 ô, tức hai cách đo NMS không khớp nhau. → Cần chạy lại. Điểm mới chưa tách khỏi các công trình gần nhất. Bài chưa trích Gontara 2026 (replay ứng viên, quét top-K, đo theo công đoạn) và survey 09/2026 (đã có sẵn công thức trễ hạn kiểu Amdahl). Đóng góp (i) mâu thuẫn với chính kết quả. Mô hình ngân sách trượt quy tắc định trước ở 6/6 ô tấn công thật và kém hơn cả dự đoán "không đổi". → Nên bỏ khỏi danh sách đóng góp. Kết quả mạnh nhất của bài là phần hình học và số lớp: dồn ứng viên vào một lớp làm batched_nms chậm 17 lần, nên đưa lên làm đóng góp chính. Ngưỡng N* rơi vào mức thấp nhất của lưới ở hầu hết các ô (100 ở 320 px, 300 ở 640 px), nên không phân biệt được gì. → Cần thêm mức 10, 30, 50 vào lưới. "Phát hiện được" chưa phải "gây hại". MDE 0,046% chỉ khoảng 21 µs. → Cần thêm một ngưỡng thực tế, ví dụ phần trăm của khung 33 ms ở 30 FPS. Vẫn chỉ một lõi CPU, một luồng. Phụ lục Raspberry Pi lại cho kết quả ngược chiều (chậm 1,8 đến 2 lần), nhưng dùng mô hình khác và phiên tách công đoạn ở đó không qua kiểm tra chất lượng. Thêm so sánh CPU đa luồng và một GPU.

## 1. Phát hiện mới khi chuẩn bị kế hoạch (chẩn đoán thăm dò, CHƯA đưa vào bài)

Đọc lại dữ liệu thô phiên YOLOv5s trên AMD (`sponge-sim/results/amd_20261124/full-01/e10/run/raw_P1_cpu2.jsonl`, nhánh main; 12 614 bản ghi, 5 400 bản ghi `kind=pipeline`). Chỉ đọc, không đo mới. Phân tích sau khi đã thấy dữ liệu, nên chỉ là manh mối để thiết kế lần chạy lại.

1. **Mỗi ô chỉ đo 3 lần** (`config.pipeline_repeats = 3`, `pipeline_warmup = 1`), trong khi A/A đo 20 lần/ảnh và tiêm ứng viên 30 lần/ô. Cả phiên chỉ mất 0,67 giờ.
2. **Nhiễu không phải do trôi xung nhịp.** Trong cùng một ô (cùng ảnh, cùng nhánh, cùng backend) 3 lần đo gần như trùng nhau: hệ số biến thiên trung vị 0,16% (p90 0,40%). Benchmark tham chiếu phẳng suốt phiên (11,90–11,93 ms).
3. **Thời gian ảnh sạch có hai mức tách bạch**: một cụm quanh 268–275 ms và một cụm quanh 292–299 ms (chênh khoảng 9%), gần như không có giá trị ở giữa. Trạng thái "nhanh/chậm" đổi theo từng bội số 9 bản ghi = đúng một đơn vị đầu vào (3 backend × 3 lần), tức là đổi mỗi khi tạo tensor đầu vào mới, không đổi giữa các lần lặp của cùng tensor.
4. Hai bản sao sạch của cùng một ảnh (clean_a, clean_b, cùng khối) lệch nhau với độ lệch chuẩn log-ratio 0,0698 trên 50 ảnh, giống hệt nhau ở cả 3 backend (0,0698 / 0,0698 / 0,0693). Đây chính là nguồn của MDE 2,8%.
5. Giả thuyết (chưa kiểm): hiệu ứng phụ thuộc vị trí bộ nhớ của tensor (căn lề địa chỉ, trang lớn trong suốt THP, xung đột cache) trong forward của YOLOv5s. Nếu đúng, nó cũng giải thích phần dư âm của Bảng 10: nhánh bị tấn công và nhánh sạch rơi ngẫu nhiên vào trạng thái nhanh/chậm, nhiễu ±9% nuốt mất mức tăng 6–10 ms của NMS.
6. Cần kiểm thêm: (a) các phiên YOLOv8n (E9, E12, A/A) có hai mức tương tự không; (b) manifest của E10 ghi `weights = yolov8n.pt` dù E10 chạy YOLOv5s qua `yolov5_ref.py` — cần xác nhận hash trọng số YOLOv5s được ghi ở chỗ khác, nếu không thì phải ghi vào DEVIATIONS.

Lệnh tái lập chẩn đoán: xem Phụ lục A.

## 2. Các gói việc

Ký hiệu: [Chữ] = sửa chữ, không đo; [Offline] = phân tích lại dữ liệu đã lưu; [ĐO] = đo mới, cần PREREG + git tag trước, máy rảnh, tuân quy tắc cứng số 9.

### Nhóm A — Sửa chữ, làm ngay được

| # | Việc | Góp ý | Cách làm | Ghi chú |
|---|---|---|---|---|
| A1 | Sắp lại đóng góp | "Đóng góp (i) mâu thuẫn" | Bỏ (i) khỏi danh sách. Đóng góp chính mới: bản đồ chi phí NMS theo cài đặt × hình học × **phân bố lớp** × cap, với kết quả dồn một lớp làm `batched_nms` chậm 17,0 lần ở N=10^4 rời nhau (Bảng 5). Sau đó: đối chứng dương với ngưỡng N*; giao thức đo khóa xung + A/A. Công thức Amdahl chuyển thành "công cụ kiểm tra nhanh, trích từ survey 09/2026", kết quả âm của nó giữ ở RQ4 như một phát hiện. | Sửa đồng bộ: abstract, mục Contributions, 5.2, kết luận. Không đổi số. |
| A2 | Tài liệu tham khảo | Thiếu 7 tài liệu; còn Holm, Cameron | Thêm Daedalus, Beyond PhantomSponges, Chen ACCV 2024, TrackFlood, YOLO26, Gontara 2026, survey 09/2026. Xóa câu trích Holm và Cameron ở mục 4.3 (viết lại câu thống kê không cần chúng). | Hiện có 24 khóa được trích / 33 mục trong `references.bib`. Cần nguồn chính xác cho Gontara, survey, Chen ACCV, TrackFlood (xem mục 4). |
| A3 | Tách điểm mới | "Điểm mới chưa tách khỏi các công trình gần nhất" | Sau khi đọc Gontara 2026 và survey: thêm 2 hàng vào Bảng 1, viết đoạn "khác gì" theo từng trục: (a) sàn nhiễu A/A + MDE trên lõi khóa xung, (b) phân bố lớp và `batched_nms`, (c) patch thật đo end-to-end + TOST, (d) kết quả âm của mô hình ngân sách trên tấn công thật. Trục nào Gontara đã làm (replay ứng viên, quét top-K, đo theo công đoạn) thì ghi thẳng là đã có, không nhận là mới. | Phải đọc bài gốc trước khi viết; không suy đoán nội dung. |
| A4 | Vẽ lại sơ đồ pipeline (Hình 1) | "Vẽ pipeline đẹp hơn" | TikZ mới: hai nhóm công đoạn tô màu khác nhau (không phụ thuộc N: resize, forward, decode; phụ thuộc N: lọc τ + top-k, NMS); thanh tỉ lệ thời gian thật của ảnh sạch (forward 42,9 / tổng 46,5 ms ở 320 px, Bảng 2); đường tiêm ứng viên tổng hợp tách bạch; đặt bộ đếm giờ dưới từng khối và một thanh t_total. | Máy này không có LaTeX: dựng trên Overleaf (`paper_en/make_bundle.py`). Số trong hình lấy từ `numbers_en.json`. |
| A5 | Lệch cột Bảng 1, 4, 5, 6 | "lệch cột trong bản trích văn bản" | Dựng PDF, mở xem từng bảng; kiểm bằng trích văn bản (pypdf). Nguyên nhân hay gặp: `p{}`/`X` xuống dòng trong ô, tiêu đề gộp cột, `adjustbox` co bảng. Sửa trong `make_tables_en.py` (Bảng 4–6 sinh tự động) và trực tiếp trong main.tex (Bảng 1), rồi chạy `check_numbers_en.py`. | |
| A6 | Phụ lục Raspberry Pi | "kết quả ngược chiều… mô hình khác… phiên tách công đoạn không qua QC" | Hai lựa chọn (chờ quyết định): **(a)** bỏ khỏi bài, giữ trong repo; **(b)** giữ nhưng rút gọn, đổi tên thành "chế độ hậu xử lý chiếm ưu thế (YOLOv8n-seg)", nói rõ chiều kết quả khớp H4 (forward chỉ còn 54% thời gian) chứ không mâu thuẫn, nhưng không quy cơ chế cho NMS vì phiên công đoạn FAIL. | Không chạy lại protocol Pi cũ (quy tắc trong CLAUDE.md). |
| A7 | Viết lại abstract và kết luận | "Abstract và kết luận dựa vào phiên YOLOv5s" | Tạm thời: bỏ câu YOLOv5s khỏi vị trí chính của abstract, đưa kết quả hình học/số lớp lên đầu. Viết bản cuối sau khi có kết quả C1. | Phụ thuộc C1. |

### Nhóm B — Phân tích lại dữ liệu đã lưu (không đo)

| # | Việc | Cách làm |
|---|---|---|
| B1 | Xác nhận hiệu ứng hai mức | Script chẩn đoán đặt trong `sponge-sim/studies/` (bản sao mới, không sửa code cũ): phân bố thời gian sạch, độ dài chuỗi trạng thái, áp cho E10, E9, E12 và A/A. Ghi báo cáo `docs/reports/E10_BIMODAL_DIAG_20261127.md`, gắn nhãn thăm dò. |
| B2 | Bảng 10 có do hai mức không | Tách phần dư (end-to-end − NMS riêng) theo trạng thái nhanh/chậm của từng đơn vị. Gắn nhãn post hoc; dùng để thiết kế C1, không thay kết quả. |
| B3 | Ngưỡng "gây hại" | Tính trên dữ liệu đã có một ngưỡng thực tế (mục 4, quyết định 3), gắn nhãn post hoc. Lưu ý: trên một lõi, thời gian sạch đã là 39–46 ms (YOLOv8n 320 px), 141–164 ms (640 px), khoảng 273 ms (YOLOv5s), nghĩa là chưa tấn công đã không đạt 30 FPS. Vì vậy "phần trăm của khung 33 ms" phải viết thành ngưỡng tuyệt đối (ví dụ 5% × 33,3 ms = 1,67 ms thêm vào mỗi khung), còn "lỡ hạn khung" thì định nghĩa theo tốc độ khung đạt được của máy. MDE 0,046% × 46,5 ms ≈ 21 µs, đúng như thầy tính. |

### Nhóm C — Đo mới trên máy AMD khóa xung (PREREG + tag TRƯỚC khi đo)

Mọi phép đo C1–C3 chạy trên cùng máy Ryzen 5 5500, cùng cách khóa xung (3,6 GHz, tắt boost, tắt SMT anh em, turbostat trước/sau). Một PREREG chung `PREREG_AMD_REVISION_<ngày>.md` cho C1+C2, tag riêng; C3 có thể cùng hoặc tách. Smoke nhỏ trước, dừng chờ duyệt rồi mới chạy đầy đủ.

| # | Thí nghiệm | Thay đổi so với lần trước | Ước lượng |
|---|---|---|---|
| C1 | **Chạy lại YOLOv5s (E10-r)** | (1) 20 lần/ô thay vì 3, warm-up 3; (2) đầu vào chép vào **một bộ đệm cấp phát sẵn** (cùng địa chỉ cho mọi nhánh), đồng thời ghi `data_ptr` % 4096 và % 2 MB để kiểm giả thuyết bộ nhớ; (3) đo NMS **bên trong** chính lần gọi end-to-end (mốc thời gian lồng nhau: trước/sau forward, trước/sau NMS) bên cạnh micro-benchmark cũ, để trả lời trực tiếp mâu thuẫn Bảng 10; (4) ghi riêng thời gian forward của ảnh sạch và ảnh bị tấn công (bài đã viết "a measurement that times the forward pass separately … would settle"); (5) A/A trong phiên với nhiều lần cấp phát mới để đo riêng hiệu ứng cấp phát. Endpoint chính, quy tắc Amdahl và 50 ảnh/5 seed giữ nguyên để so được. | Phiên cũ 0,67 h với 3 lần/ô; 20 lần/ô ≈ 4–5 h. |
| C2 | **Lưới N\* mịn hơn (E9-r)** | Thêm N ∈ {10, 30, 50} ở 320 px và {10, 30, 50, 100} ở 640 px vào lưới tiêm toàn pipeline, cùng 20 ảnh, cùng quy tắc đọc N\*. Báo N\* kèm ngưỡng "gây hại" B3 đặt trước. | Cần đọc thời lượng E9 cũ để ước tính. |
| C3 | **CPU đa luồng** | 1, 2, 4, 6 luồng (mỗi luồng một lõi vật lý, các SMT anh em tắt, cùng tần số khóa). Tập con: A/A, E9 (rời nhau + trộn; torch thuần, tv_nms, Ultralytics), E10-r. Dự đoán đặt trước theo H4: forward nhanh lên còn NMS chạy tuần tự, nên tỉ phần NMS và tỉ số end-to-end tăng theo số luồng. | Mỗi mức luồng cần A/A riêng. |
| C4 | **GPU** | Đo trên một GPU: đồng bộ `torch.cuda.synchronize`/CUDA event, khóa xung GPU nếu được (người dùng tự đặt, Claude chỉ in checklist), NMS trên GPU và NMS trên CPU sau forward GPU. Tập con: A/A, E9, E10-r. | Phụ thuộc GPU nào dùng được (mục 4). |

### Nhóm D — Hoàn thiện

D1. Sinh lại bảng (`make_tables_en.py`), kiểm số (`check_numbers_en.py`), sinh lại hình, dựng PDF trên Overleaf, kiểm lại bảng lệch cột và caption. D2. Cập nhật Bảng 14 (sai lệch) với lần chạy lại và lý do. D3. Gửi thầy bản PDF kèm danh sách "đã sửa theo từng góp ý".

## 3. Thứ tự đề xuất

1. Tuần này, không cần máy đo: A1, A2 (phần đã có nguồn), A4, A5, B1, B2, B3; viết PREREG cho C1+C2 dựa trên B1.
2. Khi máy AMD rảnh: smoke → duyệt → C1 + C2 (một buổi, khoảng 1 ngày máy).
3. Sau C1: A7 (abstract/kết luận bản cuối), A3 khi đã có bài Gontara/survey.
4. C3 trên AMD; C4 khi có GPU.
5. D1–D3.

## 4. Quyết định đang chờ người dùng

1. **Nhánh làm việc**: đề xuất tạo thư mục làm việc riêng (git worktree) cho nhánh `amd-replication-20261124` để sửa bài, giữ nguyên thư mục hiện tại (`harness/step1`, đang có 323 thay đổi chưa commit). Không gộp `main` vào `harness/step1`: `main` là bản công khai đã lược bớt hàng nghìn file, gộp sẽ xóa file ở nhánh này.
2. **Nguồn tài liệu**: quy tắc cứng 7 cấm dùng mạng. Cần một trong hai: người dùng gửi PDF/BibTeX của Gontara 2026, survey 09/2026, Chen ACCV 2024, TrackFlood (Daedalus, Beyond PhantomSponges, YOLO26 cũng nên có bản chính thức); hoặc cho phép tìm trên web riêng cho việc tra tài liệu.
3. **Ngưỡng "gây hại"**: đề xuất Δt_total ≥ 5% của khung 33,3 ms (= 1,67 ms) làm ngưỡng chính, kèm 10% (3,33 ms) làm độ nhạy. Có thể chọn khác, nhưng phải chốt trước PREREG.
4. **Phụ lục Pi**: (a) bỏ hay (b) giữ rút gọn.
5. **GPU**: máy nào, GPU gì (V100 dùng cho E7 trước đây ở đâu, còn dùng được không).
6. **Máy AMD**: ai chạy và khi nào (các commit 24/11 do tài khoản Reikage đẩy, máy chạy Xubuntu live).

## Phụ lục A — tái lập chẩn đoán mục 1

```
git -c safe.directory=D:/Sponge-patch-study show reikage/main:sponge-sim/results/amd_20261124/full-01/e10/run/raw_P1_cpu2.jsonl > e10raw.jsonl
```
Rồi với các bản ghi `kind == "pipeline"`: nhóm theo (image_id, arm, seed, backend) → CV của `total_ns` trong nhóm; với clean_a/clean_b: log(median clean_b / median clean_a) theo ảnh, SD trên 50 ảnh; histogram `total_ns` của nhánh sạch theo bin 4 ms; độ dài chuỗi trạng thái (<283 ms / ≥283 ms) theo thứ tự bản ghi. Script chính thức sẽ đặt trong B1.
