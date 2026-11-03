# DEVIATIONS — sai lệch so với PREREG

Mỗi mục: ngày, PREREG nào, thay đổi gì, lý do, đã thấy dữ liệu đo chính chưa.

(chưa có)

## 2026-10-21 — E2a: phân tích A/A post-hoc
- PREREG: `prereg/PREREG_E2a.md` (tag `prereg-e2a-20261021`).
- Thêm `studies/e2_proxy/e2a_posthoc_aa.py` -> `results/e2a/20261021T145544/posthoc_aa.json`.
- Lý do: sau khi thấy `summary.json:attack_induced_share` (mean dương ở mọi case dù mean ΔN ≈ 0 hoặc âm) và
  `noise_vs_effect` (clean–clean p90 13,6 ms), nghi chỉ số bị chi phối bởi cú vọt thời gian và thứ tự đo; cần A/A cùng công thức.
- Đã thấy dữ liệu: CÓ. Gắn nhãn POST-HOC; không thay kết quả định trước.

## 2026-10-21 — E5 (run `results/e5/20261021T151412`), ghi SAU khi thấy dữ liệu
1. **Verify ghim E4 chỉ kiểm cận trên.** Tiêu chí PREREG_E5 (CPU-time/wall ≤ |allowed|+0,15 và ≥70% tải trên CPU được phép)
   cho E4 "passed" với effective_cores = 0,963 (`raw_E4.jsonl` dòng 1, `verify.effective_cores`), tức 4 thread KHÔNG chạy
   song song trong phiên đo (smoke trước đó: 3,78; kiểm lại sau phiên: 2,7–3,35). Forward E4 (trung vị 131,447 ms) gần bằng E1
   một core (138,442 ms). Hệ quả: E4 được gắn nhãn "ghim đúng tập CPU, song song không xác minh"; KHÔNG tự động dùng cho E1.
   Đề xuất cho các lần sau: thêm cận dưới effective_cores ≥ 0,7·|allowed| (chờ duyệt, chưa sửa PREREG đã tag).
2. **Cờ trôi 3% bị kích hoạt ở gần như mọi khối** (P1 11/11, E1 9/11, E4 11/11; max |Δ| 0,240 / 0,338 / 0,881).
   Phân tích độ nhạy "bỏ khối có cờ" vì vậy không thực hiện được (n_images = 0 → NaN ở P1, E4; E1 còn 20 ảnh).
   Thiết kế ABBA/BAAB trong ảnh làm trôi chậm triệt tiêu trong tỷ số A/A, nên endpoint chính vẫn tính được; nhưng
   ngưỡng 3% với benchmark tham chiếu hiện tại không phân biệt được khối tốt/xấu trên laptop này.
3. Trong phiên P1 (chạy đầu tiên), một lệnh Python ngắn (<1 s, sửa file script E1) đã chạy song song. Không loại dữ liệu.

## 2026-10-21 — Đổi profile chính P1 → P1_cpu2 (quyết định của nhóm, sau E5 và smoke E1)
- Lý do: smoke E1 cho verify CPU 0 effective_cores 0,394 (< cận dưới 0,5); CPU 0 thường gánh ngắt/tác vụ hệ thống.
- Thay đổi: `hw.profiles` thêm `P1_cpu2` = logical đầu của P-core thứ hai (logical 2). Tên `P1` giữ nghĩa CPU 0 cho lịch sử E5.
- `studies/e5_protocol/run.py` (đã tag prereg-e5) được sửa SAU tag: thêm `--profiles` và cận dưới verify 0,5 cho P1_cpu2.
  Giao thức đo (ảnh, số lần, ABBA, công đoạn, tham chiếu) KHÔNG đổi. Run A/A P1_cpu2 dùng để lấy MDE cho PREREG_E1.
- Đã thấy dữ liệu: có (E5 đầy đủ + smoke E1). Run A/A P1_cpu2 chưa chạy (máy đang bận lúc quyết định: CPU 2 ở 75%).

## 01/11/2026 — A/A P1_cpu2 (AA_P1cpu2_20261101)
- Toi (Claude) chay analyze.py tren file raw dang duoc ghi trong luc phep do dang chay (tuong tien trinh nen da ket thuc vi thong bao cua cong cu). Tao tai CPU ngan ngay khi do khoi 1. Co drift gan o khoi 1 va 3 (khoi 3 khong ro nguyen nhan). Giu moi du lieu; bao cao ca ket qua day du va ket qua loai 2 khoi co drift (xem PROGRESS). summary.json cuoi duoc tao lai sau khi do xong.

## 02/11/2026 — E6 lan 1 dung giua chung (ultra_native, N = 6); sua backend va chay lai tu dau
- Lan 1 (results/e6/E6_P1cpu2_20261101, 152015 dong raw) dung voi ValueError o backends.py (Ultra.run) khi mot don vi co dung N=6 ung vien: ultralytics coi tensor shape[-1]==6 la dau ra end-to-end va tra ve khong kem chi so. Du lieu lan 1 KHONG dung de bao cao (khong hoan tat, giu nguyen thu muc, khong xoa).
- Sua: Ultra.prepare them 1 cot diem 0 khi n==6 (bi loai boi nguong conf > 0.0 nen khong doi tap giu lai; kich thuoc tensor 6->7 cot, anh huong thoi gian khong dang ke nhung chua dinh luong). Test moi: tests/test_backends.py::test_small_n_including_six_keeps_same_set (N=0,1,5,6,7); 57 test nhanh pass.
- E6 chay lai tu dau vao results/e6/E6_P1cpu2_20261102 (cung PREREG_E6, cung patch SHA256). Loi nay chi xuat hien khi N=6 tren backend ultra_native; E1 (N danh theo luoi) khong gap loi.

## 02/11/2026 — E6: thiếu nhánh clean ở 640 px
PREREG_E6 (tag prereg-e6-20261101) chỉ có nhánh `clean` ở 320 px; C2 và C4 đo ở 640 px nên tỷ số toàn trình 3,5–3,6 là chi phí độ phân giải (results/e6/E6_P1cpu2_20261102/summary.json:arms.C2.total_tv_nms). Phát hiện sau khi đo. Không dùng C2/C4 để kết luận tác động patch ở 640 px. Đề xuất bổ sung: prereg/PREREG_E6_addendum_clean640.md (chưa tag, chờ duyệt).

## 02/11/2026 — A/A 640 px và E6-A1: drift tham chiếu rất cao
- A/A 640 px (`results/e5/AA640_P1cpu2_20261102`): ghim PASS (0,756) nhưng 8/11 điểm tham chiếu bị cờ, lệch tối đa 18%. MDE toàn trình 1,9%.
- E6-A1 (`results/e6/E6A1_P1cpu2_20261102`): ghim PASS (0,951) nhưng 9/11 điểm bị cờ. Khối 3 (09:55) benchmark tham chiếu chậm 12 lần (115,7 ms so với 9,75 ms lúc đầu); khối 3→4 kéo dài 27 phút (bình thường ~5 phút); các khối 4–9 chậm hơn 9–154%. Máy bị một tải khác chiếm trong khoảng 09:41–10:45; nguyên nhân chưa xác định. Trong thời gian này trợ lý có chạy các tác vụ đọc/ghi tệp và soạn văn bản (nhẹ) và người dùng có thể đã dùng máy; không loại trừ được.
- Xử lý theo PREREG: giữ trong phân tích chính, báo kèm. Kết quả chính: không tỷ số toàn trình nào của C2/C4 so với clean640 có cận dưới CI vượt 1 + MDE (1,9%); các CI rộng (ví dụ C4 torch_pure 1,131 [1,005; 1,317]). Không đủ tin cậy để kết luận về 640 px.
- Đề xuất (chờ người dùng duyệt): chạy lại E6-A1 (cùng mã, cùng tag prereg-e6a1-20261102, thư mục run mới) và nếu cần A/A 640 px, khi máy rảnh thật và trợ lý không chạy bất kỳ tác vụ nào song song. Run hiện tại giữ nguyên, không xóa.

## 02/11/2026 — Đo lại A/A 640 px và E6-A1 (người dùng yêu cầu, không chờ máy rảnh)
- Cùng mã, cùng tag `prereg-e6a1-20261102`, thư mục mới `results/e5/AA640_P1cpu2_20261102b`, `results/e6/E6A1_P1cpu2_20261102b`; lần đo đầu giữ nguyên. Trong lúc đo trợ lý không chạy việc gì khác (quy tắc 9).
- A/A 640 px lần 2: ghim 0,953; 3/11 điểm tham chiếu bị cờ, lệch tối đa 3,8%; MDE toàn trình 0,69% (lần 1: 1,9%, 8/11, 18%). E6-A1 lần 2: ghim 0,945; 7/11 điểm bị cờ nhưng lệch tối đa 7,9% (lần 1: 9/11, một khối chậm 12 lần).
- Bài báo dùng lần đo 2 làm số chính cho 640 px (sạch hơn rõ rệt), nêu lần 1 trong Bảng sai lệch. Đây là lựa chọn sau khi xem chất lượng (drift), KHÔNG dựa trên giá trị tỷ số; tỷ số N giống hệt nhau (tất định).
- E9: endpoint đăng ký dùng MDE 640 px của lần 1 (1,9%) và dữ liệu E6-A1 lần 1 cho Phần B; giữ nguyên làm kết quả chính. Phân tích độ nhạy (ngoài đăng ký): với MDE 0,69% của lần 2, N* ở 640 px không đổi trừ một ô (torchvision theo lô, hỗn hợp: 3000 -> 1000); Phần B trên E6-A1 lần 2 cùng chiều (PyTorch thuần Δ 0,69 [0,57; 0,81]; torchvision nms 0,03 [-0,11; 0,14]; hai cài đặt phân biệt lớp tệ hơn).

## 03/11/2026 — Bất đối xứng trong phép đo toàn trình của E6/E6-A1/E6-A2: bước chèn patch nằm trong vùng bấm giờ của nhánh có patch
- Phát hiện khi viết mục "ngưỡng Δt_NMS" theo góp ý GVHD: trong `studies/e6_remeasure/run.py` (hàm full()), nhánh có patch gọi `insert` bên trong vùng đo, nhánh sạch thì không. Mức tăng toàn trình 1,1–1,5% của mọi patch (kể cả patch không làm N đổi) vì vậy gồm chi phí chèn.
- Đo chẩn đoán riêng (post hoc, ghim lõi, `studies/diag_insert/run.py` -> `results/diag_insert/insert_cost_20261103.json`): insert 0,354 ms (320 px, patch 64), 1,658 ms (640 px, patch 128), 0,535 ms (640 px, patch 64).
- Hiệu chỉnh (post hoc, `studies/amdahl/threshold_check.py` -> `results/amdahl/threshold_check_posthoc.json`): R_corr = t_patched / (t_clean + t_insert). Sau hiệu chỉnh, tỷ số toàn trình torchvision của C1, C3, B1–B4, C2 có KTC chứa 1 hoặc sát 1 (vd C1 1,006 [0,999; 1,014], B4 1,001 [0,994; 1,007]); C4 640 px 1,009 [1,002; 1,016].
- Giới hạn của hiệu chỉnh: t_insert đo ở phiên khác. Không sửa mã E6 (giữ nguyên để tái lập); E9 (tiêm) và E10 (nhiễu loạn áp dụng ngoài vùng đo) không bị ảnh hưởng. Bài báo cáo cả số chưa hiệu chỉnh và đã hiệu chỉnh.

## 03/11/2026 — Sửa lỗi chèn patch: thí nghiệm E11 thay cột toàn trình của bảng patch
- GVHD không chấp nhận số hiệu chỉnh bằng phép trừ (t_insert từ phiên khác) làm kết quả chính. Mã đo mới `studies/e11_patch_remeasure/run.py`: ảnh đầu vào dựng ngoài vùng đo, mọi nhánh đo cùng `pipeline_fn`. Test hồi quy `tests/test_e11_symmetry.py` (3 test: cùng chuỗi thao tác trong vùng đo ở nhánh sạch và nhánh patch; hàm đo không tham chiếu insert; ảnh patch chỉ khác ảnh gốc ở vùng patch).
- Kiểm các phép đo khác: (1) E6 nhánh 640 px (E6-A1, `studies/e6_remeasure/run.py:199`, cùng hàm full()) có CÙNG lỗi: C2/C4 tính insert, clean640 không. (2) E9 tiêm toàn pipeline (`studies/e9_pipeline/run.py:102,116-122`): ảnh nạp một lần trước vòng ô, ứng viên tiêm dựng sẵn (`:92`); trong full() mọi ô cùng forward → tau_filter → prepare → run; không có thao tác riêng theo ô ngoài kích thước đầu vào NMS. Không bị lỗi. (3) E10 tấn công toàn ảnh (`studies/e10_reference/run.py:84`): nhiễu loạn cộng vào ảnh trước khi đo, full() (`:103-108`) giống hệt cho clean_a/clean_b và nhánh tấn công. Không bị lỗi. (4) E1/E5 không có bước chèn.
- Thiết kế E11 cân: mọi nhánh trên cùng 100 ảnh, seed 0–4; thêm hai nhánh sạch mỗi canvas để có sàn nhiễu trong phiên. Bỏ R_sg/R_tanh. Smoke 2 ảnh `results/e11/smoke_20261103` (chỉ kiểm chạy, không dùng số).
- Số hiệu chỉnh cũ (`results/amdahl/threshold_check_posthoc.json`) chuyển sang tài liệu bổ sung, nhãn "kiểm tra chéo, post hoc". Dữ liệu E6 cũ giữ nguyên.
