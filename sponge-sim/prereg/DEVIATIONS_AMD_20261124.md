# Sai lệch so với PREREG_AMD_REPLICATION_20261124

## 1. Lỗi script điều phối ở smoke lần 1 (24/11/2026)
`run_amd.sh` dưới tag `prereg-amd-replication-20261124` đổi thư mục vào `sponge-sim` rồi gọi `lock_env.sh` theo đường dẫn
tương đối, nên cổng kiểm xung trước E1 thất bại (exit 127). Chưa có lượt đo nào; thư mục `runs/amd-20261124/smoke/e1`
chỉ có `environment.txt`, `prereg_commit.txt`, `xung_truoc.log` rỗng và được giữ nguyên.
Sửa: đường dẫn tuyệt đối cho `lock_env.sh`; thư mục đợt chạy theo biến `RUN_ID`; tag mới `prereg-amd-replication-20261124-r1`.
Thiết kế, endpoint và mã đo không đổi. Smoke chạy lại với `RUN_ID=smoke-02`.
