# QA — cache renderer trên Pi, chỉ kiểm chức năng

Người dùng cho phép hoàn thiện code và kiểm thử ARM. Bước này là QA đầu ra và
chuẩn bị vật liệu; không đo latency/ru_maxrss/peakRSS, không mở lại NMS/PI1
đã bị hủy. Đã xem mọi kết quả Pi trước, gồm mainfull20PASS/componentFAIL.

Tag kỹ thuật trước thực hiện: `qa-pi3b-renderer-cache-20261114`.
Source11filePython giữ byte-identical với tag QA supervisor3409c07 đã qua
66hosttests và5sleep-onlycases trên Pi. Chỉ cấu hình engineering chuyển
allow_cache_preparation=False→True, qa_tag mới và thêm SHA cache_plan.json.
Giữ empirical_endpoints_enabled=False, không có memory_registration.json.
Engineering lock cũ đã archive/tag và được chép riêng trên Pi trước thay
thế nguyên tử cấu hình; không chạm bất kỳ thư mục run cũ nào.

## Vật liệu và kiểm định cố định

- Chỉ20cặp của full20lockSHA1cd1789d… và summaryPi34166aa9… đã khóa; kiểm21SHA
  weights/input trước forward. Không sinh/chọn ảnh/seed mới.
- PiRuntime2.15.0+cpu/TV0.29.2+cpu/Ultra8.4.90/NumPy2.5.4/Python3.13.5;
  opsSHA828de5d2…/NMSsource khóa, torchvision import trước Ultralytics;
  FP32/640²/batch1/conf.25/IoU.45/max_nms30000/max_det300.
- Nạp1cặp/ảnh; cache riêng sạch/nhiễu gồm proto32×160×160, coeffsK×32,
  boxesK×4; CPUFP32/finite/contiguous. Đúng40case theo thứ tự clean/adv từng
  ID. Nτ/K và kernelinvocations phải khớp boundary và Nτ/K bản Pi chấp nhận.
- Với từngcase, baseline32M list+cat và candidate16M preallocate/directcopy
  phải cho cùng shape/dtype/byteSHA mask. Hash qua memoryview, thả output
  trước khi chạy renderer kế tiếp, không giữ hai stack output cùng lúc.
- Không gọi hash bằng chứng tương đương mọi input/device; chỉ kiểm finite
  tensors trên đúng Pi/runtime này. Không suy peakRSS/speed từ QA.

## Một lần chuẩn bị, có dừng và khôi phục

Launch `control.py --mode prepare` trong transientservice có KillModecontrol-group
và ExecStopPost độc lập như QA5case. Đầu ra mới duy nhất
`runs/cacheprep_01` và `caches/cache_01`; mởexclusive, không ghi đè. Tối đa
3600s, supervisorstop120s; không tiếp tục nếu bất kỳ case/precondition/hash/
parity/guard không đạt. Không retry để kiếmPASS hoặc viết cache02 sau lỗi.

Giữ điều kiện powersave/affinity0–3/threads4/inter1,3runtime masks/swapoff,
không USBstorage, fastguard trước/sau các forward/render/hash/case; dừng khi
nhiệt≥75°C/MemAvailable<40000kB/missingreadback/mask/swap/governor/affinity/
requestedclock ngoài594–606MHz hoặc pswpin/out/oomdelta. Đây là requestedclock
được đọc ở guard, không tuyên bố actualclock liên tục trong QA chức năng.
Không profiler/RSSsampler/clockedrender, không package/networkdownload/nguồn/
turbo. Chỉ SSH đã cho phép. Trong workload chỉ chờ handle, không sửa source/
đọc tiến độ hoặc làm việc song song. SSH giữ mở sau terminal.

## Sau terminal

Kiểm service/child kết thúc và restore/readback các cấu hình đã đăng ký.
Fetch nguyên run và cache vào đích local mới, đối chiếu SHA remote-before/
local/remote-after và source vẫn trùng tag. Giữ cả partial/FAIL. Terminal
hoàn thành phải có40receipt/cache, manifest/terminal và mọi guard đạt; source
registry bind đầy đủ trước dùng caches cho phép so sánh nào khác.

Chỉ sau QA này mới có thể hoàn thiện đề xuất scientificmemory, khóa manifest
cache vào PREREG/tag riêng và xin review thay đổi phương pháp theo quy tắc
không tự mở campaign mới sau một cổng thất bại. QAcache không tự cấp quyền
đo mới hoặc biến các protocol cũ thành PASS.
