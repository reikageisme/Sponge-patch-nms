# Sai lệch so với PREREG_AMD_REPLICATION_20261124

## 1. Lỗi script điều phối ở smoke lần 1 (24/11/2026)
`run_amd.sh` dưới tag `prereg-amd-replication-20261124` đổi thư mục vào `sponge-sim` rồi gọi `lock_env.sh` theo đường dẫn
tương đối, nên cổng kiểm xung trước E1 thất bại (exit 127). Chưa có lượt đo nào; thư mục `runs/amd-20261124/smoke/e1`
chỉ có `environment.txt`, `prereg_commit.txt`, `xung_truoc.log` rỗng và được giữ nguyên.
Sửa: đường dẫn tuyệt đối cho `lock_env.sh`; thư mục đợt chạy theo biến `RUN_ID`; tag mới `prereg-amd-replication-20261124-r1`.
Thiết kế, endpoint và mã đo không đổi. Smoke chạy lại với `RUN_ID=smoke-02`.

## 2. Venv thiếu gói cho E9 và E10 (smoke-02, 24/11/2026)
Smoke-02 (tag r1): E1 và E1-NC1L đạt (kiểm xung trước/sau đạt, Bzy_MHz 3575). E9 dừng ở import vì venv của A/A không có
`kornia`; kiểm thử import cho thấy E10 còn thiếu `pandas`, `tqdm`, `pkg_resources`. Chưa có lượt đo nào của E9, E10, E12.
Đã cài vào venv (không đụng hệ thống): `kornia==0.8.3`, `pandas==3.0.3` (đúng `requirements-lock.txt` của laptop),
`tqdm==4.67.1` (laptop không ghi phiên bản; chỉ import trong bộ đọc ảnh của YOLOv5) và `setuptools==80.9.0`
(bản 84.2.1 của A/A đã bỏ `pkg_resources` mà mã YOLOv5 vendored cần). Các gói này không nằm trong vùng bấm giờ của E5,
nên không ảnh hưởng A/A đã chạy. Mã đo không đổi. Smoke E9, E10, E12 chạy lại với `RUN_ID=smoke-03`, tag `-r2`;
smoke E1 và E1-NC1L của smoke-02 được giữ. Mỗi thí nghiệm ghi `pip freeze` riêng.

## 3. Phân tích sau phiên chính full-01 (24/11/2026, ghi sau khi đo xong, trước khi xem endpoint E12)
Phiên chính `full-01` (tag r2) chạy đủ 5 thí nghiệm, mã thoát 0, mọi kiểm xung trước/sau đạt (Bzy_MHz 3575, Busy 100%).
Các sai lệch chỉ nằm ở bước phân tích, không đo lại gì:
- **E12, bộ phân tích:** bản nháp PREREG E12 ghi dùng `studies/e11_patch_remeasure/analyze.py`, nhưng runner E12 ghi điểm
  tham chiếu dạng `block_attempt` (DriftGate) chứ không phải `reference`, nên analyzer E11 dừng (max() rỗng). Đã viết
  `studies/e12_patch_remeasure_gated/analyze.py`: gọi nguyên logic E11 (không sửa file E11), chỉ chuyển mỗi lần thử được nhận
  thành một điểm tham chiếu (rel_change = độ lệch lớn nhất trước/sau so với đầu phiên), và thêm E12-P4..P6 cùng phân tích
  độ nhạy ngưỡng 2% theo bản nháp. Cổng trôi: 10/10 khối nhận ở lần đầu, độ lệch lớn nhất 0,13%, nên không khối nào bị bỏ ở 3% hay 2%.
- **Bộ nhớ khi phân tích E12:** raw 122 MB làm Python bị OOM (RAM trống khoảng 900 MB). Đã bật zram 3 GB (zstd) SAU khi mọi phép đo
  đã xong; không có zram trong lúc đo.
- **E1-NC1L:** lưới `--nc1-large` không có N = 10^2 (chỉ 1000, 3000, 8400/10000), nên endpoint "tỷ số 10^2 → 10^4" trong PREREG
  không tính được. Thay bằng (ghi là post hoc): tỷ số 10^3 → 10^4 của ô một lớp, và tỷ số một lớp / 80 lớp ở cùng N, cùng phiên.
- **E9 phần B:** chỉ chạy phần kiểm chéo hình học trên E1 của đợt này (`cross_geometry_e1`); hai tập kiểm E6 320/640 không được
  đo lại trên máy AMD nên không có test1/test2.

## 4. Phân tích post hoc cho bản thảo (24/11/2026, sau khi xem kết quả)
Để mọi số thời gian trong `paper_en/main.tex` lấy từ máy AMD, chạy thêm trên raw của `full-01` (không đo mới), tất cả ghi là post hoc:
`studies/e10_reference/stage_medians.py`, `stage_decomp.py`, `analyze_addon.py`; `studies/amdahl/analyze.py` trên E1 + E9 AMD;
`studies/e9_pipeline/analyze.py --part b --test320 <E12>` (tập kiểm là mọi nhánh của E12, thay tập xác nhận E6 640 px của laptop);
`studies/amd_replication/posthoc_amd.py` (dự đoán chỉ từ N trên E12, tương quan hạng, kiểm cấu trúc E10). `studies/e6_remeasure/analyze.py`
được chép nguyên từ repo gốc để dùng lại hàm `curve`/`predict`. Kết quả ở `runs/amd-20261124/full-01/analysis/`.
Phát hiện cần ghi: ở E10, mức tăng NMS đo vi mô (6,6-9,5 ms) lớn hơn mức tăng toàn trình (3,1-5,2 ms; KTC chứa 0 ở cả 6 ô), nên phần
còn lại âm; kết luận của laptop "1/3 đến 1/2 mức tăng nằm ngoài NMS" không lặp lại. MDE trong phiên E10 là 2,8%.
