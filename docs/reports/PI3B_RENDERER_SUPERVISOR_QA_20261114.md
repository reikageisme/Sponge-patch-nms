# Pi renderer — supervisor và analyzer: host QA và5case ngủ trên Pi

## Đã xong

**Source mới qua66kiểm tra host; cả5kiểm tra chỉ-ngủ trên Pi đạt đúng điều
kiện cleanup. Chưa đo RAM/tốc độ renderer hoặc tạo cache thực.**

Tag kỹ thuật `qa-pi3b-renderer-memory-20261114`, commit
`3409c07d7e5c912dba02bc238106637de54bd6bf`, khóa trước các case trên Pi.
Plan: `sponge-sim/prereg/QA_PI3B_RENDERER_SUPERVISOR_20261114.md`.
Source: `sponge-sim/studies/pi3b_renderer_prealloc_20261114/`.
Gốc chứng cứ bên dưới: `sponge-sim/results/pi3b_renderer_supervisor_qa_20261114/`.

### Code và kiểm tra trên host

- Supervisor mới dùng nguyên AST của System/Lease/record/validate_snapshot
  và guard từ sourcefull20 đã chạy. Tên service dùng chung ngăn hai lease
  đồng thời; log riêng, KillModecontrol-group, ExecStopPost độc lập. Mỗi run
  mới mở exclusive, khôi phục chỉ masks sở hữu và đúng trạng thái gốc.
- Analyzer yêu cầu đủ360job đúng lịch cho20ảnh/clean+adv/3arms/3lặp,40cache
  đúng ID/hash, PID khớp receipts, child đã kết thúc, endpoint/đơn vị KiB
  đúng, guards và sampledclock đạt. Không lọc ảnh để tạo CI từ cohort thiếu.
- Hai A/A sạch/nhiễu phải cùng qua bias/MDE. Qualification cuối còn đòi
  controllerterminalCOMPLETED/gate0 và restorePASS; localgate trước restore
  chưa là kết quả cuối đạt. CI theo ảnh và exactsignflip dùng helper thống kê
  chép nguyên có provenance. D_z trảnull nếu SD0, không sinhInfinity/NaN hoặc
  suy tương đương; độ phân giải1024bytes/startupfloor có thể che chênh lệch.
- EntryQA từ chối import Torch/scipy trước thay cấu hình. Entryfunctionalprep
  bị khóa bằng allow_cache_preparation=False; scientificentry còn thiếu
  memory_registration.json nên chưa thể mở. Không có tag khoa học mới.

HostQA:61PASS36.73s với2SyntaxWarnings regex; đã sửa rawregex trước mọi
devicecase. Sau đó64PASS68.97s, cuối66PASS67.17s không cảnh báo. Cả ba log
giữ ở `pytest_01/02/03.log`; thời gian pytest không là endpoint hiệu năng.
`source_preparation.json` giữ SHA source/tests/log và archive byte-identical.
Các file-based tests dùng360job tổng hợp, không là số đo Pi hay cache thật.

### Năm case trên Pi

| Case | Kết quả kỹ thuật | Ý nghĩa đúng phạm vi |
|---|---|---|
|qa_normal_01|PASS_NORMAL|kết thúc thường, child thu hồi, restore đạt|
|qa_mainkill_01|PASS_MAIN|kill đúng main sau READY, manager thu hồi child/restore|
|qa_childkill_01|PASS_CHILD|kill đúng childPID/startticks/cgroup, main báo lỗi, restore|
|qa_timeout_01|PASS_TIMEOUT|manager timeout sau READY, child thu hồi, restore|
|qa_disconnect_01|PASS_DISCONNECT|ngắt đúng SSHfrontend cục bộ; service vẫn hoàn tất/restore|

Mỗi READY xác nhận torch_imported=False/scipy_imported=False, swap tắt,
masks đúng và powersave. Faultcases expectednonzero; PASS nói đúng fault
và cleanup, không nói tiến trình bị kill đã exit0. Nguồn:
`device_qa_outcomes.json`, `*.ready_observation.json`, `*.assessment.json`,
`*.action.json`/`*.disconnect.json` và `runs/qa_*_01/`.

Đã chép nguyên39file gốc, SHA remote-before=local=remote-after;17file
source/materials vẫn byte-identical với source chuẩn bị trước tag. Nguồn:
`qa_verification.json:{cases,n_original_files,original_sha256,source_sha256}`,
`remote_before_fetch.json`, `remote_after_fetch.json`, `registration_check.json`.

Sau phiên: service inactive/MainPID0; governorondemand, zram/timer active,
writebackservice inactive, helperactive/Resultsuccess, mọi masks đã gỡ;
readback của từng case khớp snapshot phần cấu hình đã đăng ký. Không đòi
MemAvailable phải trở về cùng con số vì đây là trạng thái động, không phải
một cấu hình được khôi phục. SSH vẫn mở.

## Phát hiện cần biết

Journal của disconnectcase có dòng20:50:40giờVN (13:50:40UTC) báo không mở
được transientunitfile trong `/run/systemd/transient/`. Log giữ nguyên;
nguyên nhân chưa xác định. Case vẫn đạt các điều kiện đã khóa: đúng service/
invocation đã được quan sát READY, childidentitygone, manager báo normal
deactivation và restore/readback đạt. Không xóa warning hoặc gán cho phần
mềm bảo vệ. Nguồn: `qa_disconnect_01.assessment.json:journal`.

Các dòng FAILED(signal/exit-code/timeout) ở ba faultcase là can thiệp dự kiến,
khác lỗi safety/restore ngoài dự kiến; assessment kiểm riêng từng loại.
Không có case nào bị chạy lại; không hủy hay ghi đè run cũ để tìmPASS.

QA chỉ kiểm những sleepingchild cụ thể. Chưa phải bằng chứng mọi descendant,
kernelstall/powerloss hay workloadTorch thực đều được xử lý; chưa deviceQA
cache/model/peakRSS. Analyzer bootstrap chưa áp dụng cho dữ liệu memory thực
vì chưa có dữ liệu đó. Hostgraph/filefixtures không thay các kiểm này.

Memoryendpoint đã chuẩn bị đo high-water RSS toàn tiến trình qua rendering
và digest, gồm imports/cachevalidation/warmup/allocator; không peak riêng
renderer, không latency, không accuracy equivalence/DoS. Cả hai protocol Pi
âm cũ và componentNMSFAIL/PI1hủy của full20 giữ nguyên. Mainfull20 đạt không
bị thay source hoặc dùng làm baseline ghép cặp giả cho renderer mới.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Chuẩn bị plan và QA cache chức năng trên40case trước, vẫn không ghi
endpointRAM/tốc độ → gõ: **"Tiếp tục kiểm cache renderer trên Pi"**.

B. Review phương pháp so sánh bộ nhớ mới sau khi cache/source đã đủ để khóa
PREREG và tag; không tự chạy campaign khác sau NMSFAIL → gõ:
**"Review protocol bộ nhớ renderer"**.

## Đang chờ gì ở tôi

Không cần thao tác mở SSH hoặc khôi phục Pi. Phần chuẩn bị code/QA tiếp tục
được; phép đo mới chưa mở và còn cần protocol cụ thể theo quy tắc đã ghi.
