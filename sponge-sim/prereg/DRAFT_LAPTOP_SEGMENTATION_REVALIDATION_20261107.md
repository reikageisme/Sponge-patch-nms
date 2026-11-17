# DRAFT — CPU laptop: kiểm ổn định trước replay tấn công phân đoạn

UNRUN, chưa PREREG/tag; không phải lệnh bắt đầu benchmark.
Người dùng07/11 hỏi lại trục CPU đã yêu cầu khi thuê máy và khả năng dùng laptop.
M2 CPU4 thuê đã đạt workload MASK tổng hợp; CPU1 thuê10flags, M1/M1b laptop
cũ FAIL, M6GPU3sessionFAIL. Không sửa hoặc hợp thức hóa ngược các run đó.

Thiết bị đọc metadata local: i5-1335U,10cores/12logical; không tự coi12logical
là12physical hoặc chọn core bằng index. Chưa xác minh topology/mask/tải hiện tại.

## Thứ tự thực hiện đề xuất

1. Offline: chuẩn bị gói exact clean/adv của20M3 đã khóa, weights/source SHA,
   fixture MASK và compiled torchvision NMS. Nếu chuyển sang64audit/nested1500,
   phải là cohort riêng khóa trước, không gộp với20COCO128. Không tối ưu PGD lại
   hoặc dùng1500ảnh để chữa cổng thời gian. Chưa có gói laptop mới được chuẩn bị.
2. Khóa CPU set hợp lệ theo topologyWindows, tránh SMT siblings và không trộn
   P/E không rõ; ghi verify CPU-time/wall và backend pool. Fresh worker trước
   Torch import; đặt intra-op theo số CPU đã xác minh, interop1. Một profile
   ban đầu, chưa khóa ID; profile nhiều CPU chỉ mở nếu loadQA đạt.
3. Đăng ký controls-only A/A forward và total fixed-TV,640squareFP32,
   full-resolution mask và tham chiếu drift3%. Giữ báo mọi flags, không chọn
   phiên theo effect tấn công. Repeats/burst/warmup/reference count/MDE budget,
   cooldown và max sessions phải khóa trước tag, dùng oldfailure để định thiết
   kế chứ không tìm tham số theo phiên PASS. Cần giám sát nhiệt/timeout đọc được;
   không đổi power plan/turbo hoặc cài gói.
4. Sau A/A/MDE/drift đạt mới chạy MASK injectedK10/50/100/300 và replay cùng
   tensor clean/adv; đo forward,NMS,mask,total trực tiếp, total không cộng
   stage medians. Backend/class semantics/maxdet/maxnms/preprocessing thống nhất.
5. Primary/secondary contrasts, bootstrap image/session, family multiplicity,
   missing/incomplete policy phải khóa trong protocol chính thức. Không coi
   repeats là ảnh hoặc nhiều profile là nhiều thiết bị. FAIL thì giữ nguyên
   và dừng campaign theo ngân sách cố định; không đo đến khi có số đẹp.

Chưa có số phút feasibility hoặc kết quả mới. Trước bất kỳ timingQA/smoke/full:
PREREG+tag; người dùng xác nhận laptop rảnh/cắm nguồn; trợ lý chỉ để đúng phép
đo chạy, không web/git/soạn bài/poll song song. Smoke xong báo lại theo quy trình
dự án trước full. Chuẩn bị offline có thể tiếp tục ngay; chưa xin máy rảnh khi
gói thực thi chưa review được.
