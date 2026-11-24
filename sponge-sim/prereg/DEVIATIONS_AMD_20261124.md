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
