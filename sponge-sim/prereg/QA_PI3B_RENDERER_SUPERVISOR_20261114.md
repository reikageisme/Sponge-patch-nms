# QA — supervisor renderer, chỉ ngủ, trước mọi endpoint mới

Đây là QA kỹ thuật trong phạm vi code/QA được người dùng cho phép, không
phải đăng ký hay mở một campaign khoa học sau NMSFAIL. Không chạy Torch,
model, pinload, cache thực, ru_maxrss hoặc latency endpoint.

Source `studies/pi3b_renderer_prealloc_20261114/`; lớp System/Lease, hàm
record/validate_snapshot và toàn bộ guard có AST khớp source full20 đã kiểm.
Entry points mới chỉ cho qa/prepare/memory. Engineering lock trước5case khóa
11sourcefiles, hai referencefull20, allow_cache_preparation=False và không
cấp quyền endpoint khoa học. Prepare bị từ chối; memory còn thiếu scientific
registration và cache, bị từ chối trước mutation. Không cài gói hoặc đổi
nguồn/turbo/network. SSH luôn giữ mở.

Tag kỹ thuật: `qa-pi3b-renderer-memory-20261114`, trước deviceQA. Workspace
Pi mới `/home/tanh/sponge-sim/pi3b_renderer_prealloc_20261114`. Chia sẻ tên
service cũ để không có hai lease trên cùng swap/governor đồng thời. Chỉ đổi
tạm powersave và ba runtime masks như lease trước; ExecStopPost độc lập khôi
phục đúng original governor, swap topology/priority, helper/unit/timer và masks.

|Case mới trong workspace mới|Sleep / RuntimeMax|Hành động|
|---|---|---|
|qa_normal_01|5/90s|không fault|
|qa_mainkill_01|60/120s|SIGKILL đúng mainPID/invocation/service đã quan sát|
|qa_childkill_01|60/120s|SIGKILL đúng childPID/startticks/cgroup đã quan sát|
|qa_timeout_01|90/45s|manager timeout sau READY|
|qa_disconnect_01|15/90s|terminate đúng localSSHfrontend, không tắt sshd|

Driver `results/pi3b_renderer_supervisor_qa_20261114/run_device_qa.py COMMIT`
adapt có SHA/filelines từ driver full20, thêm xác minh READY không import
Torch/scipy. Readiness phải quan sát trước fault; source/lockSHA kiểm trước
mọi runtime mutation. Sleepingchild là directchild của payload, toàn bộ
cgroup được systemd giám sát. Fault expectednonzero không là scientificFAIL;
case chỉ PASS nếu đúng fault, childidentitygone và restore/readback hoàn toàn
khớp snapshot. Normal/disconnect cần manager normaldeactivation.

Một case không đạt thì hủy các case chưa bắt đầu, giữ toàn bộ logs/receipts;
không lặp case để kiếm PASS. Sau terminal fetch originalfiles mới, SHA
remote-before/local/remote-after; source/lock/materials không đổi. Không suy
QA ngủ thành peakRAM/speedup/parent-death của arbitrary workloads hay powerloss.

Sau QA vẫn cần plan cache chức năng riêng/actualoutputparity, scientificPREREG
và tag cho endpoint mới. Không tự chạy memory campaign từ thông báo goal
continuation hoặc từ việc code đã qua test.
