# Thay đổi sau phản biện 16/11/2026

Nhánh `review-fixes-20261116`, tách từ `e41b00f`. Chưa commit, chưa push. Không file kết quả đã đo nào bị sửa; không file nào
trong danh sách khoá SHA-256 của `.gitattributes` bị đụng tới (`core/`, `attack/`, `experiments/local_*`).

Bản phản biện và phần giải thích từng hướng sửa nằm ngoài repo, ở file `PHAN_BIEN_VA_HUONG_SUA.md` cạnh thư mục repo này.

## File sửa (chỉ thêm, không đổi hành vi cũ)

| File | Thêm gì |
|---|---|
| `sponge-sim/src/sponge_sim/stats.py` | `tost_ratio`, `skill_vs_null`, `ratio_summaries`, `tail_summary` ở cuối file |
| `sponge-sim/src/sponge_sim/timing.py` | `DriftGate`, `SessionAbort` ở cuối file |
| `sponge-sim/src/sponge_sim/hw_linux.py` | `lock_status(cpu)` ở cuối file |
| `sponge-sim/studies/e1_dose/run.py` | cấu hình `NC1_LARGE` và cờ `--nc1-large`; lưới mặc định vẫn 123 nhóm |

## File mới

| File | Việc |
|---|---|
| `sponge-sim/src/sponge_sim/stages.py` | bấm giờ riêng forward, decode, lọc tau, NMS; đếm subnormal; forward với flush denormal |
| `sponge-sim/src/sponge_sim/optimizers.py` | random, GA, NES, (1+lambda)-ES ở cùng ngân sách truy vấn, có đường hội tụ |
| `sponge-sim/studies/e10_reference/analyze_addon.py` | mô hình rỗng, skill, TOST, ba cách tóm tắt N_tau, đuôi phân phối, tiêu chí theo Delta t_total (cần raw) |
| `sponge-sim/studies/e12_patch_remeasure_gated/run.py` | đo lại bảng patch như E11, thêm cổng trôi theo khối và kiểm khoá tần số |
| `sponge-sim/studies/review_20261116/*.py` | kiểm tiêu chí, mô hình rỗng, N_tau, bảng patch, một lớp so với 80 lớp trên summary đã commit |
| `sponge-sim/studies/linux_profile/check_env.py`, `lock_env.sh` | kiểm và khoá governor, tần số, turbo, SMT |
| `sponge-sim/prereg/DRAFT_PREREG_E12_patch_remeasure_gated.md` | bản nháp đăng ký trước cho E12 (chưa có hiệu lực) |
| `sponge-sim/results/review_20261116/` | kết quả của ba script kiểm, tính từ summary đã commit |
| `sponge-sim/tests/test_review_fixes.py` | 15 test cho mọi phần trên |
| `paper_en/lint_style.py` | soát dấu gạch, DOI, độ dài caption, tên câu hỏi nghiên cứu |

## Đã kiểm tới đâu

- `python sponge-sim/tests/test_review_fixes.py`: 15/15 qua (Python 3.13, torch, torchvision; không có pytest và ultralytics trên máy chạy thử).
- Test cũ của repo, chạy bằng trình chạy tạm vì thiếu pytest: 17 qua, 3 lỗi vì thiếu ultralytics, giống hệt trước và sau thay đổi.
  23 file test cần pytest nên chưa chạy. Cần chạy lại `pytest` đầy đủ trên máy có đủ môi trường.
- **Chưa chạy trên dữ liệu thật:** `analyze_addon.py` (repo không commit raw), `e12_patch_remeasure_gated/run.py` (cần ultralytics, ảnh,
  patch E7), `lock_env.sh` (cần Linux và quyền root), `stages.py` và `optimizers.py` trên YOLO.

## Kết quả mới có được từ dữ liệu đã commit (`results/review_20261116/`)

- Tiêu chí "chỉ thấy được khi Delta t_NMS > MDE x t_total" có 2/6 ô phản ví dụ ở E10; viết theo Delta t_total thì 6/6 ô nhất quán.
- Cả 6 ô E10 có khoảng tin cậy loại 1 và cận dưới trên 1,01; không ô nào trên 1,05.
- Mô hình ngân sách pass 3/6; mô hình rỗng R = 1 có sai số điểm dưới 0,05 ở 6/6 (xấp xỉ từ trung bình).
- "340 đến 389 lần" là trung bình tỉ số; tỉ số hai trung vị là 107 và 124.
- Bảng patch: 4 dòng có khoảng tin cậy trên 1, 3 dòng dưới 1.

## Một lớp so với 80 lớp: phép đo chỉ dẫn, chưa ghim

Lưới E1 đã commit chỉ có nc = 1 ở 2100 anchor. Đo nhanh `torchvision.ops.batched_nms` trên máy chạy thử (một luồng, KHÔNG ghim lõi,
7 lần, lấy trung vị; chỉ để biết hướng, không dùng làm số của bài):

| Anchor | Hình học | nc = 80 (ms) | nc = 1 (ms) | Tỉ số |
|---|---|---|---|---|
| 8400 | disjoint | 14,1 | 156,3 | 11,1 |
| 8400 | mixed | 12,6 | 58,0 | 4,6 |
| 8400 | dense_cluster | 11,0 | 2,0 | 0,2 |
| 10000 | disjoint | 16,0 | 221,5 | 13,9 |
| 10000 | mixed | 13,9 | 85,6 | 6,1 |
| 10000 | dense_cluster | 12,0 | 2,3 | 0,2 |

Với hộp rời nhau dồn vào một lớp, batched NMS chậm hơn khoảng 11 đến 14 lần so với khi trải trên 80 lớp. Lời khuyên
"class-batched kernel làm NMS không nhạy" vì vậy cần điều kiện "ứng viên trải trên nhiều lớp", hoặc phải đo lại đúng giao thức:

```bash
python sponge-sim/studies/e1_dose/run.py --run-dir sponge-sim/results/e1/E1_nc1_large --nc1-large
```

## Việc tiếp theo, theo thứ tự

1. Chạy `pytest` đầy đủ trên máy đo.
2. Chạy `analyze_addon.py` trên raw của E10 (không cần đo lại).
3. Sửa bản thảo theo `results/review_20261116/*.md`.
4. Hoàn thiện và gắn tag đăng ký trước cho E12 và cho lưới `--nc1-large`, rồi mới đo trên Linux đã khoá.
