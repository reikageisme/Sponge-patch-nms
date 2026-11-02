# Nguồn số liệu của bài báo và trạng thái truy vết

Chuyển ra khỏi thân bài (02/11/2026) theo yêu cầu của thầy: không đưa đường dẫn `outputs/`, `sponge-sim/...` vào văn bản. Dùng cho `paper_vi/main_vi.tex` và `paper_en/main.tex`.
"Đã kiểm lại" = con số được đọc lại từ tệp tóm tắt trong phiên soạn bài này. "Chép từ bản v2" = lấy từ bản thảo trước (PDF `AdversarialSpongeAttack.pdf`, nguồn `BaoCaoKhoaHocAdversarialAttacks_Q1_VI_v2.tex`, đã qua audit ở `REVIEW/03`), CHƯA truy lại tới dòng thô trong phiên này; phải truy lại hoặc bỏ bảng trước khi nộp.

| Nhóm số trong bài | Tệp nguồn (từ gốc kho mã) | Trạng thái |
|---|---|---|
| A/A 320 px (CPU logic 2, lõi hiệu năng thứ hai) | `sponge-sim/results/e5/AA_P1cpu2_20261101/summary.json` | Đã kiểm lại |
| A/A 640 px (số dùng trong bài: lần đo lại) | `sponge-sim/results/e5/AA640_P1cpu2_20261102b/summary.json` (lần đầu, nhiễu: `AA640_P1cpu2_20261102`) | Đã kiểm lại |
| A/A lần đầu (một lõi hiệu năng P1; một lõi tiết kiệm điện E1; bốn lõi E4) | `sponge-sim/results/e5/20261021T151412/summary.json` | Đã kiểm lại (tỷ số, MDE, drift) |
| Tiêm ứng viên (đáp ứng liều, top-k, số lớp, độ dốc, pipeline) | `sponge-sim/results/e1/E1_P1cpu2_20261101/summary.json` | Đã kiểm lại |
| Đo lại patch 320 px, dự đoán chỉ-từ-N | `sponge-sim/results/e6/E6_P1cpu2_20261102/summary.json` | Đã kiểm lại |
| Đo patch 640 px so với ảnh sạch 640 px (số dùng trong bài: lần đo lại) | `sponge-sim/results/e6/E6A1_P1cpu2_20261102b/summary.json` (lần đầu, nhiễu: `E6A1_P1cpu2_20261102`) | Đã kiểm lại |
| Độ nhạy E9 với MDE 640 px mới và dữ liệu 640 px mới | `sponge-sim/results/e9/E9_P1cpu2_20261102/summary_part_a_sens_aa640b.json`, `summary_part_b_sens_e6a1b.json` | Đã kiểm lại (ngoài đăng ký) |
| Tiêm toàn pipeline, ngưỡng N* (Bảng N*) | `sponge-sim/results/e9/E9_P1cpu2_20261102/summary_part_a.json` | Đã kiểm lại |
| Bộ dự đoán M_N / M_NK (Bảng sai số) | `sponge-sim/results/e9/E9_P1cpu2_20261102/summary_part_b.json` | Đã kiểm lại |
| Hình 4–8 | `sponge-sim/studies/figures/make_figs_v3.py` (đọc các tệp ở trên) | Sinh lại được |
| Mô hình Amdahl so với phép tiêm toàn pipeline (Bảng Amdahl, post hoc); sàn nhiễu trong phiên; độ nhạy bỏ khối bị cờ | `sponge-sim/results/amdahl/amdahl_vs_e9_posthoc.json` | Đã kiểm lại |
| Tấn công toàn ảnh thật (Bảng tấn công, Hình 9) | `sponge-sim/results/e10/E10_P1cpu2_20261102/summary.json`, `structural_check_posthoc.json` | Đã kiểm lại |
| Baseline B1-B4 gộp 100 ảnh (bảng patch) | `sponge-sim/results/e6/E6_pooled_baselines_100img/summary.json` (ảnh 51-100: `E6A2_P1cpu2_20261102`) | Đã kiểm lại |
| Fitness huấn luyện (sinh patch trên GPU) | `sponge-sim/results/e7_gpu/final/runs/e7/*/seed*/checkpoint_q*.json` | Đã kiểm lại |
| Nhóm 128 ảnh và nhóm 500 ảnh: chênh lệch SG-GA trừ GA tâm | `outputs/extended_q1_20261002`, `outputs/x1_500img_20261018` | Số chính đã xác minh trong ghi chú dự án; các bảng chi tiết chép từ bản v2 |
| Diện tích, EOT, ngân sách, luồng dịch vụ, đánh đổi phòng thủ, chuyển giao, khảo sát đa kiến trúc, biến thể tham chiếu | `outputs/` (thư mục các nhóm tương ứng), `outputs/x2_architecture_20261020` (khảo sát đa kiến trúc) | Chép từ bản v2; cần truy lại |
| Vi benchmark hộp lịch sử | `outputs/benchmark/results.json` | Chép từ bản v2 |

Ghi chú: nhiều trường `weights_sha256` của khảo sát đa kiến trúc là null (xem `REVIEW/03`); giữ nguyên, không bịa hash.

Ghi chú 02/11 (bản v4 sau review chi tiết của thầy): các bảng cohort lịch sử (diện tích, EOT, luồng dịch vụ, đánh đổi phòng thủ, chuyển giao, khảo sát đa kiến trúc, biến thể tham chiếu lịch sử, A/A lần đầu) ĐÃ BỊ CẮT khỏi bài. Bài chỉ còn một đoạn với hai chênh lệch SG-GA trừ GA tâm (128 ảnh: -0,005; 500 ảnh: -0,029), đã xác minh trong ghi chú dự án.
