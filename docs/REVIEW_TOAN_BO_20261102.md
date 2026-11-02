# Rà soát toàn bộ tài liệu của đề tài (02/11/2026) — bản đồ, khoảng trống, kế hoạch

Mục đích: để phiên sau (kể cả khi mất ngữ cảnh) biết đã có gì trong repo, thầy yêu cầu gì, còn thiếu gì. Đây là bản tổng hợp từ việc đọc:
`docs/REVIEW_THAY_NAM.md`, `REVIEW/03_paper_vs_repo.md`, `REVIEW/04_q1_gap_analysis.md`, `REVIEW/05_rewrite_plan.md`, `REVIEW/06_open_items.md`,
`docs/KIEM_TOAN_Q1_SAU_HOP_NHAT_VI.md` (§9–11), `docs/Q1_SCIENTIFIC_AUDIT_VI.md` (§11–14), `docs/GD2_PLAN_VI.md`, `docs/DOAN_DONG_GOPIEN_VI.md`,
`CLEANUP_PROPOSAL.md`, đề mục của `docs/Q1_Q2_RESEARCH_ROADMAP.md`, `docs/REVIEW_SPONGE_PATCH_DETAILED.md`, `docs/REVIEWED.md`, và PDF bài cũ do người dùng gửi
(bản v2 tiếng Việt, 17 trang; nguồn `BaoCaoKhoaHocAdversarialAttacks_Q1_VI_v2.tex`).
Chưa đọc kỹ từng dòng: `REVIEW/01_inventory.md` (71 KB), `REVIEW/02_code_audit.md`, `REVIEW/06_paper_changelog.md` (48 KB), `docs/Q1_Q2_RESEARCH_ROADMAP.md` phần thân, các bản `_provenance/`.

## 1. Yêu cầu của thầy (docs/REVIEW_THAY_NAM.md) so với trạng thái hiện tại
| Yêu cầu | Trạng thái 02/11 |
|---|---|
| Đối chứng dương, tiêm N = 10^2–10^4 vào cùng pipeline, trên laptop VÀ ít nhất một board ARM | Laptop XONG (E1). ARM CHƯA: điện thoại không qua kiểm chứng ghim lõi. Thầy nói rõ: Q1 chỉ có cơ hội nếu kết quả edge rõ ràng. |
| Chạy lại giao thức ghim core trên patch thật | XONG ở 320 px (E6). Nhánh 640 px chờ clean640 (E6-A1 đang chạy). |
| Tập tối ưu >= 100 ảnh, ngưỡng 0,25, ảnh 640 px | XONG phần sinh patch (E7). Đo 640 px đang chờ. |
| Đổi khung bài: "N có dự đoán độ trễ không", SG-GA là case study; bỏ "khai thác lỗ hổng/cạn kiệt tài nguyên" | Bản `paper_en/main.tex` đã đổi. Bản Việt `paper_vi/main_vi.tex` đã đổi tiêu đề nhưng còn nhiều nhãn cũ (xem G4). |
| Viết lại tiếng Anh; gom giới hạn vào Threats to Validity | Bản Anh có Threats. Bản Việt (mới, dài) chưa dịch sang Anh. |
| Bỏ nhãn nội bộ (OLD128, X1-500, R1/R2/R3, outputs/), giảm chữ số có nghĩa, bớt câu rào đón | Bản Anh gần đạt. Bản Việt dài hiện VI PHẠM yêu cầu này (xem G4). |
| Trích dẫn nền (Sponge Examples, Brown, EOT, black-box dựa truy vấn) và so sánh rõ với EVADE | Có trong bản Anh; 15/17 mục đã kiểm bằng web. Còn 19 mục mới trong `paper_vi/refs_extra.bib` chưa kiểm. |
| Chưa có: "bản review chi tiết kèm vị trí từng lỗi" của thầy | Vẫn chưa có trong repo (REVIEW_THAY_NAM.md ghi rõ). Khi có thì thêm vào cuối tệp đó. |

## 2. Khoảng trống phát hiện khi rà (xếp theo mức ảnh hưởng)
G1 (CAO NHẤT) Chưa có kết quả ARM. Đây là điểm thầy gắn với Q1. Phát hiện review mã #2 (`hw_linux.py:56`, ghim chỉ cho luồng gọi) là một nguyên nhân CÓ THỂ khiến pin_verify trên điện thoại không qua; chưa kiểm chứng. Hướng: sửa/kiểm ghim từng luồng, chạy lại pin_verify, nếu qua thì A/A + E1 rút gọn trên điện thoại (cần PREREG mới, người dùng duyệt, điện thoại bật sshd, mạng tắt, máy rảnh).
G2 Nhánh 640 px chưa đọc được (E6-A1 đang chạy; A/A 640 có MDE 1,9% và drift 8/11, nên kết luận ở 640 px sẽ yếu).
G3 SAI TRONG BẢN VIỆT: `paper_vi/main_vi.tex` ghi tác giả thứ ba là Đinh Phương Nam. `REVIEW/06_open_items.md` mục 4 quy định: giữ hai tác giả Anh/Bảo, Nam là tác giả liên hệ/GVHD, không tự thêm đồng tác giả. Cần sửa đầu bài về hai tác giả + ghi chú liên hệ (như `paper_en/main.tex`).
G4 Bản Việt dài vi phạm yêu cầu (5) của thầy: còn nhãn OLD128/X1-500/X2/R3/E5, đường dẫn `outputs/` trong Phụ lục A và bảng cohort, bốn chữ số thập phân khắp nơi, nhiều câu rào đón rải trong phần Kết quả. Khi dịch sang Anh phải: đổi tên thành "first held-out cohort (128 images)", "extended cohort (500 images)", chuyển đường dẫn sang README kho mã, làm tròn (tỷ số 3 chữ số có nghĩa, MDE 2 chữ số), gom rào đón vào Threats.
G5 Khác biệt với EVADE chưa đủ sắc: phát hiện "N tăng ~300 lần, toàn trình +2–6%" của bài cũ dựa trên YOLOv5s, chưa ghim lõi, và thầy nói nó gần kết luận EVADE. Đối chứng mới có: tiêm vào pipeline đầy đủ chỉ 1 ảnh, 2 backend, tối đa N=2100 (Bảng pipeline). Chưa có: tiêm toàn pipeline cho cả 4 backend trên nhiều ảnh; so sánh bộ dự đoán chỉ-từ-N với bộ dự đoán có thêm backend/cap/hình học (REVIEW/04 §2 yêu cầu "N-only vs model thêm geometry/backend/cap, held-out"). Bài mới mới có N-only.
G6 Tuyên bố "đăng ký trước trong kho công khai": các tag chỉ nằm trong git cục bộ; nhánh harness/step1 chưa push (người dùng tự push). Cần push cả tag trước khi nộp; git tag không phải bằng chứng thời gian độc lập, nên nêu hash commit và ngày trong bài.
G7 Bản thảo chưa từng biên dịch (máy không có TeX). Có sẵn `cas-dc.cls`, `cas-common.sty` trong `paper_Q1_submission/`. Gợi ý: đóng gói gói Overleaf cho `paper_en` (như `paper_Q1_overleaf.zip` đã làm 21/10) để người dùng biên dịch và kiểm layout; mình không cài gói hệ thống (quy tắc 7).
G8 Trích dẫn: 19 mục trong `paper_vi/refs_extra.bib` chép từ bài cũ, chưa kiểm web; hai mục arXiv (TrackFlood, Event Burst Trigger) mang ID 2609.x và 2607.x cần kiểm tồn tại; Efron và Ultralytics chưa kiểm online.
G9 Đối chứng tấn công mạnh dưới ngân sách tương đương (E01/X3 trong audit cũ) chưa làm; chỉ có baseline gradient tanh (B4) và các biến thể thích nghi lịch sử. Phản biện Q1 sẽ hỏi.
G10 Số liệu chép từ PDF bài cũ chưa truy tới dòng thô: diện tích, EOT, luồng dịch vụ, đánh đổi phòng thủ, chuyển giao, X2, biến thể tham chiếu (Phụ lục A của bản Việt đã ghi rõ). Số chính OLD128/X1-500 đã xác minh. X2 có `weights_sha256 = null` ở nhiều file (REVIEW/03): giữ nguyên, không bịa hash.
G11 Lần A/A đầu của bài cũ (profile P1/E1/E4) bị cờ drift ở 11/11, 9/11, 11/11 điểm (đã kiểm lại ở `results/e5/20261021T151412`). Bài cũ báo "MDE 0,59%" mà không nói điều này; không được dùng số đó làm headline.
G12 11 phát hiện /code-review `sponge-sim/src` chưa sửa (liệt kê trong PROGRESS.md). Ảnh hưởng bài: nhãn fitness B4 ("tốt nhất" thực là bước cuối).
G13 Lý do hai lần A/A đầu (20261021, 20261021b) "không hợp lệ" chưa ghi rõ trong bài; cần lấy từ DEVIATIONS.md/PROGRESS rồi nêu đúng lý do.
G14 Mục còn mở từ các audit cũ, ngoài phạm vi hiện tại nhưng phản biện có thể hỏi: patch in và camera (nếu giữ "physical" thì bắt buộc), phòng thủ thích nghi, kiểm định cỡ mẫu/biên thực tiễn trước (power), quét chu kỳ phát 100–300 ms quanh điểm gãy, nhánh B (đang tắt, giữ), hình camera lịch sử (không dùng làm bằng chứng), danh sách tác giả cuối cùng do tác giả xác nhận, bản tiếng Anh chỉ dịch sau khi tác giả duyệt bản Việt.
G15 Quyết định thiết kế cũ (REVIEW/05 §7) chưa chốt rõ: venue/track mục tiêu; dùng cohort nào làm chính (hiện: đo ghim lõi mới là chính, cohort cũ là tham khảo); có thiết bị ARM hay chỉ laptop; nhóm dọn repo G1–G4 nào duyệt (mục 1–3 đã thực hiện 21/10, các mục còn lại chưa).

## 3. Kế hoạch đề xuất theo thứ tự
1. Sửa nhanh, không đụng dữ liệu: G3 (tác giả bản Việt), nhãn B4, ghi lý do hai A/A hỏng (G13).
2. Khi E6-A1 xong: phân tích, điền hàng 640 px, ghi DEVIATIONS (drift A/A 640), cập nhật cả hai bản.
3. G1: sửa/kiểm ghim từng luồng (sau khi E6-A1 xong, branch mới, có test), soạn PREREG điện thoại (chưa tag, chờ duyệt), chạy pin_verify lại.
4. G5: PREREG bổ sung (chưa tag) cho tiêm toàn pipeline 4 backend x nhiều ảnh và bộ dự đoán N + backend + cap + hình học.
5. G4 + dịch: sau khi người dùng duyệt bản Việt, dịch sang Anh theo đúng quy tắc bỏ nhãn/làm tròn/gom rào đón; đóng gói Overleaf (G7).
6. G8/G10: kiểm trích dẫn bằng web; truy lại số các bảng lịch sử tới `outputs/` hoặc bỏ bảng nào không truy được.
7. Push nhánh và tag (người dùng làm, G6).

## 4. Quyết định cần người dùng
- Có làm G1 (ARM) không, hay chấp nhận bài chỉ ở mức Q2–Q3 với laptop? Thầy: "Q2 nếu làm đủ, cơ hội Q1 nếu edge rõ ràng".
- Duyệt/sửa bản Việt trước khi dịch.
- Xác nhận danh sách tác giả (hai tác giả + Nam là tác giả liên hệ) và đưa bản review chi tiết của thầy khi có.
- Hủy máy GPU thuê (chưa xác nhận).
