# Phản biện nội bộ và hướng sửa bài Spongepatch


**Kết luận: Major revision.** Phép đo cẩn thận và minh bạch, nhưng vài kết luận chính rộng hơn bằng chứng, và bảng patch chưa có phép đo end-to-end hợp lệ.


## A. Điểm yếu nặng

### A1. Bảng patch không có phép đo end-to-end hợp lệ
- **Vấn đề:** phiên đo lại E11 bị loại vì 11/11 điểm tham chiếu trôi tần số, nên cột end-to-end của bảng patch chỉ là số mô hình dự đoán. Chính mô hình đó trượt 3/6 ô trên tấn công thật.
- **Cách sửa:** đo lại trên Linux đã khoá tần số, đo lại riêng từng khối 10 ảnh bị trôi thay vì bỏ cả phiên.
- **Code:** `studies/e12_patch_remeasure_gated/run.py` (dùng đúng phép đo của E11, thêm cổng trôi), `timing.DriftGate`, bản nháp đăng ký trước ở `prereg/DRAFT_PREREG_E12_patch_remeasure_gated.md`.
- **Trạng thái:** có code, chưa chạy thật. **Cần đo lại.**

### A2. Nền đo chưa đủ ổn định
- **Vấn đề:** Windows chế độ Balanced, không khoá tần số, turbo và luồng anh em SMT. Positive control có 12/21 điểm tham chiếu bị gắn cờ. Nhiễu trong phiên 2,5 đến 6,3%, trong khi MDE 0,55% lấy từ phiên A/A khác.
- **Cách sửa:** chuyển sang Linux; governor `performance`, tần số min = max, tắt turbo, đưa CPU anh em SMT offline; A/A đo trong cùng phiên với thí nghiệm.
- **Code:** `studies/linux_profile/lock_env.sh` (khoá, cần quyền root, đọc trước khi chạy), `studies/linux_profile/check_env.py` (kiểm, phiên chỉ bắt đầu khi `ready` là true).
- **Trạng thái:** có code, chưa chạy thật. **Cần đo lại.**

### A3. Tiêu chí trung tâm bị chính bảng của bài phản ví dụ
- **Vấn đề:** bài viết "chỉ thấy được end-to-end khi Δt_NMS > MDE × t_total". Ở bảng tấn công toàn ảnh, hai ô `tv_nms` ghi "vượt MDE" trong khi Δt_NMS (5,2 và 5,4 ms theo trung bình) dưới ngưỡng 6,2 ms.
- **Số đã tính:** 2/6 ô là phản ví dụ. Δt_total (9,1 đến 10,7 ms) vượt ngưỡng ở cả 6/6 ô.
- **Cách sửa:** phát biểu tiêu chí theo Δt_total; Δt_NMS chỉ là một thành phần. Nói rõ cột "vượt MDE" dùng cận dưới khoảng tin cậy hay dùng trung bình.
- **Trạng thái:** đã có số. Sửa chữ.

### A4. "Không vượt MDE" không có nghĩa là không có hiệu ứng
- **Vấn đề:** MDE đổi theo cỡ mẫu và phiên đo (0,55% đến 6,3%), nên nó là thuộc tính của thí nghiệm, không phải của tấn công.
- **Số đã tính:** cả 6 ô có khoảng tin cậy loại 1 và cận dưới trên 1,01; không ô nào có cận dưới trên 1,05.
- **Cách sửa:** viết "end-to-end tăng khoảng 3%, có ý nghĩa thống kê, dưới 5%". Thêm một ngưỡng hiệu ứng cố định và TOST cho mọi câu "không tăng".
- **Code:** `stats.tost_ratio`.
- **Trạng thái:** đã có số cho E10; TOST theo đơn vị cần file raw.

### A5. Luật "pass" của mô hình ngân sách không phân biệt được với đoán "không đổi"
- **Vấn đề:** tỉ số đo chỉ 1,029 đến 1,034. Một mô hình rỗng luôn đoán R = 1 có sai số khoảng 0,03, dưới ngưỡng 0,05 của luật pass.
- **Số đã tính (xấp xỉ từ trung bình):** mô hình ngân sách pass 3/6 ô; mô hình rỗng dưới 0,05 ở 6/6 ô. Ở ba ô trượt, mô hình đoán cao hơn số đo (1,065 đến 1,098 so với khoảng 1,033).
- **Cách sửa:** báo sai số của mô hình rỗng bên cạnh, thêm skill = 1 − sai số mô hình / sai số mô hình rỗng, và độ lệch có dấu. Gọi mô hình là công cụ ước lượng nhanh, không gọi là đóng góp lý thuyết: về bản chất nó là đồng nhất thức kiểu Amdahl.
- **Code:** `stats.skill_vs_null`, `studies/e10_reference/analyze_addon.py`.
- **Trạng thái:** có code, chưa chạy thật (cần file raw của E10, repo không commit).

### A6. Kết luận về Sponge Patch dựa trên optimizer quá yếu
- **Vấn đề:** thuật toán di truyền chỉ có 625 lần đánh giá, không có đường hội tụ. Trong khi đó gradient ascent của chính bài tăng N_τ 2,4 lần ở τ = 0,01.
- **Cách sửa:** hoặc so thêm optimizer mạnh hơn ở ngân sách tăng dần và chỉ kết luận khi đường cong đã phẳng, hoặc thu câu trong abstract về "optimizer này, ngân sách này".
- **Code:** `sponge_sim.optimizers` (random, GA, NES, ES ở cùng ngân sách truy vấn, ghi best-so-far).
- **Trạng thái:** có code, chưa chạy thật. Cần GPU nếu giữ claim; nếu thu hẹp claim thì chỉ sửa chữ.

### A7. Phần tăng ngoài NMS chưa giải thích được
- **Vấn đề:** 32 đến 50% mức tăng end-to-end nằm ngoài NMS. Hai giả thuyết của bài (bước lọc điểm; forward chậm vì số subnormal) đều chưa kiểm. Nếu forward chậm thật thì đó là một kênh tấn công khác NMS.
- **Cách sửa:** bấm giờ riêng forward, decode, lọc τ, NMS cho cùng ảnh sạch và ảnh bị tấn công; đếm subnormal; đo forward lần nữa với flush denormal.
- **Code:** `sponge_sim.stages`.
- **Trạng thái:** có code, chưa chạy thật. Cần một phiên đo nhỏ.

### A8. Lời khuyên "class-batched kernel" phụ thuộc cách chia lớp
- **Vấn đề:** ứng viên tổng hợp chia 80 lớp ngẫu nhiên. Lưới đã đo chỉ có một lớp ở 2100 anchor.
- **Số đã có:** ở 2100 anchor, một lớp không làm `tv_batched` đắt hơn. Đo nhanh ở 8400 và 10000 anchor (một luồng, **không ghim lõi**, chỉ để biết hướng): với hộp rời nhau, một lớp chậm hơn 80 lớp khoảng 11 đến 14 lần (156 ms so với 14 ms ở 8400 anchor); với hộp chồng nhau thì một lớp nhanh hơn.
- **Cách sửa:** đo lại đúng giao thức E1 bằng cờ mới, rồi ghi điều kiện "ứng viên trải trên nhiều lớp" vào lời khuyên nếu kết quả giữ nguyên.
- **Code:** `python sponge-sim/studies/e1_dose/run.py --run-dir <thư mục> --nc1-large` (36 nhóm).
- **Trạng thái:** có số chỉ dẫn. **Cần đo lại** (nhỏ).

### A9. Phạm vi kết luận rộng hơn bằng chứng
- **Vấn đề:** bằng chứng là một lõi CPU laptop, FP32. Trên GPU hoặc mô hình INT8, forward nhanh hơn nên tỉ trọng NMS lớn hơn. Tiêu đề và abstract đang đọc như kết luận chung.
- **Thêm:** "N_τ is a weak proxy" quá mạnh khi tương quan hạng với thời gian NMS là 0,84 đến 0,94; sai số "4 lần" là so với một đường cong tổng hợp tự chọn, tức là lệch hiệu chuẩn.
- **Cách sửa:** thêm "single-core CPU" vào tiêu đề; đổi câu về proxy thành "N_τ cần hiệu chuẩn theo cài đặt NMS và hình học hộp".
- **Trạng thái:** sửa chữ. Đo trên GPU là tuỳ chọn.

### A10. Thí nghiệm Raspberry Pi không đỡ được kết luận về NMS
- **Vấn đề:** dùng mô hình segmentation, bo sụt áp chạy 600 MHz, phần tách NMS trượt cổng chất lượng. Hai số 1,798 và 1,967 vẫn nằm trong abstract.
- **Cách sửa:** chuyển xuống phụ lục và bỏ khỏi abstract, hoặc đo lại bằng mô hình detection với nguồn chuẩn.
- **Trạng thái:** sửa chữ, hoặc đo lại nếu muốn giữ.

### A11. So sánh tấn công không cân xứng
- **Vấn đề:** patch đo trên YOLOv8n ở τ = 0,01, tấn công toàn ảnh trên YOLOv5s ở τ = 0,25. Thiếu siêu tham số của hai biến thể tấn công toàn ảnh.
- **Cách sửa:** ghi đủ siêu tham số; chạy hai tấn công toàn ảnh trên YOLOv8n ở cùng τ (dùng lại `studies/e10_reference/run.py`).
- **Trạng thái:** cần đo lại (một phần).

## B. Số liệu cần sửa trong bài

| Chỗ | Bài viết | Thực tế |
|---|---|---|
| Abstract, kết luận | N_τ tăng "340 đến 389 lần" | Đó là trung bình các tỉ số (khoảng tin cậy 104 đến 753). Tỉ số hai trung vị là 107 và 124. Báo cả hai, ghi tên thống kê |
| Trang 9 | "the intervals of the ratio contain 1" | Sai: 4 dòng có khoảng nằm trên 1 (B2 và C4 ở τ = 0,01; B4 ở cả hai τ), 3 dòng nằm dưới 1 (B1, B2, C2 ở τ = 0,25) |
| Bảng patch | Không bàn | Ở τ = 0,25 patch làm **giảm** N_τ có ý nghĩa ở ba nhánh |
| Abstract | "thousands for library kernels" | Chỉ đúng ở 640 px; ở 320 px ngưỡng là 100 đến 1000 |
| Trang 11 | Δt_NMS "below Δt* in every cell" | Một ô bằng ngưỡng (6,2 và 6,2) |
| §5.4 và Table 11 | 6,55 và 6,57; 1,58 và 1,57 | Hai cách gộp khác nhau; thêm một câu giải thích |
| Trang 9 | Δt* là 0,28 ms rồi 0,29 ms | Thống nhất một số |
| §5.3 | 80,3; 2,92; 1,33; 192; 13,2; 35/48 | Không truy được về bảng nào; thêm bảng hoặc bỏ |
| Table 2 | "0/11" và "11/11" điểm bị cờ | Là hai lần đo khác nhau; đặt tên rõ để khỏi đọc thành mâu thuẫn |

## C. Tài liệu tham khảo

- Chuẩn áp dụng: hội nghị CORE A*, A, B và tạp chí Q1, Q2 đều dùng được.
- Nhiều mục thiếu DOI hoặc arXiv ID (khoảng một nửa danh mục). Bổ sung cho đủ.
- Xác minh kỷ yếu chính thức của các mục ghi năm 2026 và của bài EVADE (bài đối sánh chính, hiện chỉ trỏ tới trang poster). **Chưa ai tra mạng phần này.**
- Bài YOLO 2016 đang được trích cho YOLOv8n; đổi sang nguồn đúng. Định luật Amdahl chưa có trích dẫn.
- Cụm trích dẫn về patch né phát hiện không liên quan tới đo độ trễ; rút bớt.

## D. Hình thức

- En dash ở khắp bài (khoảng số, khoảng trang, từ ghép). Đổi hết sang gạch nối thường. Bản LaTeX trong repo có 153 chỗ `--`.
- Câu hỏi nghiên cứu đang đặt tên Q1 đến Q4, dễ lẫn với hạng tạp chí; đổi thành RQ1 đến RQ4, thêm ô "Answer to RQ" cho từng câu.
- 9 caption dài hơn 60 từ (dài nhất 194 từ); chuyển phần phương pháp vào thân bài.
- Hình: đường và điểm che nhau ở Fig. 3 và Fig. 6; nhãn trục đè chữ ở Fig. 5; Fig. 1 nên vẽ lại.
- MDE 640 px không nhất quán giữa hai bảng (1,88% và 0,69%).
- Kết luận dài khoảng 330 từ; rút về 150 đến 200.
- Table 2 liệt kê lỗi nội bộ; rút gọn và chuyển xuống phụ lục.
- Đăng ký trước chỉ bằng git tag nội bộ; lần đo tới nên nộp thêm lên OSF hoặc AsPredicted để có mốc thời gian độc lập.

Soát tự động: `python paper_en/lint_style.py <thư mục LaTeX mới nhất>`. Bản LaTeX trong repo cũ hơn bản PDF, nên chạy lại trên bản mới.

## E. Việc cần làm, theo thứ tự

1. **Sửa chữ, không cần đo:** A3, A4, A9, A10, toàn bộ mục B, C, D.
2. **Phân tích lại trên file raw sẵn có:** chạy `analyze_addon.py` cho E10 (A5, TOST, đuôi phân phối p95 và p99).
3. **Chuẩn bị đo lại:** chạy `pytest` đầy đủ trong `repo\sponge-sim`; hoàn thiện và gắn tag đăng ký trước cho E12 và cho lưới `--nc1-large`.
4. **Đo trên Linux đã khoá:** bảng patch (A1, A2), phần dư ngoài NMS (A7), lưới một lớp (A8).
5. **Nếu giữ claim về Sponge Patch:** so optimizer trên GPU (A6). Nếu không, thu hẹp câu trong abstract.

## F. Cách chạy code

Trong thư mục `repo\`, nhánh `review-fixes-20261116` (chưa đưa lên GitHub). Tổng kết thay đổi: `repo\REVIEW_FIXES_20261116.md`.

```bash
# test cho phần mới (15 test); không cần ultralytics
python sponge-sim/tests/test_review_fixes.py

# tính lại các bảng kiểm từ summary đã commit
python sponge-sim/studies/review_20261116/criterion_null_model.py . sponge-sim/results/review_20261116
python sponge-sim/studies/review_20261116/single_class_check.py . sponge-sim/results/review_20261116

# phân tích bổ sung E10 (cần thư mục phiên đo có raw_*.jsonl)
python sponge-sim/studies/e10_reference/analyze_addon.py <thư mục phiên E10> sponge-sim/results/e1/E1_P1cpu2_20261101/summary.json <file json ra>

# trước mỗi phiên đo trên Linux
python sponge-sim/studies/linux_profile/check_env.py <cpu>
```

