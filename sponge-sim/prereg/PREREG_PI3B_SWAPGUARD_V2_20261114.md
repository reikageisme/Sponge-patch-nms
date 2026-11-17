# PREREG — Pi 3B 600 MHz, swapguard v2

Ngày14/11/2026. Tag: `prereg-pi3b-swapguard-v2-20261114`.
Viết trước mọi timing model của protocol này, SAU khi đã xem toàn bộ full01
của protocol cũ. Người dùng đã yêu cầu hoàn tất các phần thiếu như CUDA sau
câu hỏi cho phép sửa source. Quyền này bao gồm smoke và full hữu hạn khi đủ
cổng, không bao gồm retry để tìm PASS hay thay kết quả cũ.

## 1. Những gì đã biết và điều gì mới

- Pi3B Rev1.2,4×Cortex-A53,1GB; OS Lite64-bit trixie; nguồn thiếu áp đã khai báo,
  firmware thực600MHz/powersave. Không đại diện Pi3B ở xung danh định.
- Protocol cũ `prereg-pi3b-600mhz-20261114` hoàn tất main20ảnh/720timing nhưng
  swap bật lại giữa phiên, nên không đạt. Hai phụ lỗi swap trước timing, không
  retry. H1/H2 cũ đã thấy; tất cả ảnh/âm tính giữ nguyên, không chọn lại ảnh.
- Đây là phép đo điều kiện đã sửa trên CHÍNH tập tensor đó, không cohort mới,
  tái lập độc lập, hoặc đăng ký hồi tố full01. Không pool hai protocol.
- QA kỹ thuật: ban đầu thiếu scipy; tiếp theo normal-b lỗi stop sau mask và
  helper zram. Giữ tất cả lỗi/recovery. Tag QA-c `271fc81716c207dbf344453966a1ae606d85247c`
  đạt5case sleep-only normal/mainkill/childkill/timeout/disconnect;40filehash
  khớp hai phía. Không có model/matmul/timing nghiên cứu trong QA.
- Control/guard thực thi cấu hình của source đo trùng byte source QA-c. Sau QA
  bổ sung kiểm pin/count/registration vào audit và A/A stage vào worker; host
  tests kiểm hồi quy compute/estimator không đổi. Các thay đổi đều trước tag đo.

## 2. Vật liệu khóa và phạm vi suy luận

`studies/pi3b_600mhz_swapguard_v2/lock.json` khóa:

- Đúng20 `inputs` của laptop carryover và Pi cũ, thứ tự/byte không đổi;
  weights `yolov8n-seg.pt`, SHA từng file,7source runtime/helpers và builder.
  Các file input/weights trên Pi là symlink tới vật liệu cũ chỉ đọc.
- torch2.15.0+cpu, torchvision0.29.2+cpu, Ultralytics8.4.90,
  numpy2.5.4/Python3.13.5; NMS/ops sourceSHA như protocol cũ. Không nâng/hạ gói.
- FP32/batch1,640×640, conf0.25,IoU0.45,nc80; torchvision import trước Ultra,
  cùng full-resolution `process_mask_native`. Native mask chunking giữ nguyên.
- PGD toàn ảnh đã sinh trên máy khác, budget16/255; không tối ưu đầu vào trên
  Pi, không best-of-trajectory hay chọn mẫu theo timing. Không patch vật lý.
- Cap can thiệp `max_nms=300,max_det=300`, baseline max_nms30000/max_det300;
  áp trên cùng tensor nhiễu. Không đổi conf,IoU,precision hoặc renderer để cứu.
- n=20 ảnh là đơn vị suy luận. Repeats không là mẫu độc lập; một board/model/
  perturbation set, CI không phủ seed tối ưu, board, nguồn hoặc thiết bị khác.

Manifest mỗi phiên ghi tag+commit, lock/source/weightsSHA, versions/parallel_info,
CPUset/threads, config, firmware/kernel/model, môi trường bắt đầu. Registration
campaign phải khớp manifest. Local script/tag và remote source được kiểm SHA
trước/sau; không gọi build_lock sau tag.

## 3. Câu hỏi, endpoint và họ kiểm định

- H1 chính PI4: tỷ số toàn trình `adv_total/clean_total` theo ảnh.
- H2 chính PI4: `advcap_total/adv_total` theo ảnh.
- Holm chỉ cho {H1,H2}. Clean_total là median của12mẫu A+B/ảnh ở fullPI4.
  Mean log paired ratios → exp thành geometric mean; CI percentile bootstrap
  ảnh20000lần, seed20261115/16. Exact sign flip2^20, two-sided/tolerance1e-12,
  p nhỏ nhất2/2^20; d_z mean/SD(ddof1). Không chia hai global medians.
- Phụ: cap/clean (seed20261118), forwardadv/clean(20261119), A/A(20261117),
  tỷ trọng forward là median tỷ số mỗi ảnh. PI1 là phụ, không kiểm speedup
  nhân quả giữa hai profile và không gom PI1/PI4 thành một họ chính mới.
- Stage NMSadv/clean, maskadv/clean và liềuK là phụ/mô tả; CI như analyzer
  kế thừa (mask seed20261120, NMS seed20261121), không gọi p phụ là xác nhận trong họ chính.
  Không suy thời gian component bằng trừ/cộng các median khác.
- Hai control mới `nms_adv_B`,`mask_adv_B` lặp đúng job adv tương ứng; chỉ
  để A/A và MDE từng stage. Contrast adv/clean vẫn dùng arm gốc, không chọn
  arm A/B theo tốc độ, không pool B để đổi estimand đã mô tả.
- Giữ mọi ảnh/arm đã đăng ký. Missing/corrupt schedule không được lọc ảnh để
  cứu n; raw giữ nguyên, không tính một estimate đầy đủ giả từ tập thiếu.

## 4. Điều kiện, giám sát và khôi phục

- Snapshot governor/swap topology+priority và trạng thái unit/helper trước
  mutation. Chỉ hỗ trợ zram0 hiện có hoặc swap tắt và setup tương ứng, không
  preexisting runtime/persistent override/mask, không writeback đang chạy.
- Tạm dừng writeback timer; STOP swap khi unit chưa mask; sau đó mask runtime
  một batch đúng dev-zram0.swap và writeback.service/timer. Đặt powersave;
  chỉ READY khi kernel swap tắt và readback mask/governor khớp.
- Không sửa `/etc`, nguồn/turbo, package hay dịch vụ SSH. Không blanket-mask
  sysinit/swap.target, không tắt man-db/apt/cron. Background noise phát hiện
  bằng references/gates, không sửa hệ thống để đạt kết quả.
- systemd transient service cố định, KillMode=control-group, ExecStopPost
  restore, RuntimeMaxSec21600 cho campaign, TimeoutStopSec120. Source/helper
  đã kiểm cgroup cleanup với sleep-only; chưa thử mất điện hay kernel chết.
- Operational state/status là cache atomic; lease_events append-only;
  prep/raw/terminal/restore/registration dùng output mới, không ghi đè run.
  Restore chỉ gỡ mask thuộc sở hữu, trở về governor/swap/timer và helper
  ActiveState/Result ban đầu. Restore lỗi giữ lỗi, không auto-retry receipt.
- Fastguard ngoài mỗi clockedcall, cả mẫu reference: governor, requestedclock,
  thermal_zone0 (milliC), affinity, MemAvailable, SwapTotal+/proc/swaps,
  USBblockdevices,3runtime masks, delta pswpin/pswpout/oom_kill. Vi phạm/đọc
  lỗi => abort/flush/dừng, không tự sửa rồi tiếp tục. Delta là toàn hệ thống.
- Mỗi khối và cuối phiên thêm vcgencmd actualclock/temp/throttled cùng
  reference. Guard trước/sau không quan sát peak giữa lời gọi; RSS cuối
  khối không phải peakRSS. Cổng swap được bảo vệ thêm bằng mask, không chỉ
  suy từ vài snapshot. Không khẳng định clock liên tục giữa các lần đọc.

## 5. Thiết kế hữu hạn, thứ tự và vùng bấm giờ

Một smoke riêng2ảnh×2reps, sau đó tối đa một full nếu smoke đáp ứng cổng.
Người dùng đã duyệt làm đầy đủ: tiếp tục full sau khi lưu/kiểm smoke, không
cần hỏi lại chỉ vì bước đầy đủ vốn nằm trong phạm vi. Smoke không góp số bài.
FAIL code/condition/safety hoặc có timing => đóng protocol, không retry.

Ba phiên tuần tự/freshprocess:

| Phiên | CPU/intra/inter | Arms | Full repeats |
|---|---|---|---:|
|pipeline_PI4 chính|0–3/4/1|cleanA,cleanB,adv,advcap,cleanforward,advforward|6|
|pipeline_PI1 phụ|3/1/1|như trên|4|
|stages_PI4 phụ|0–3/4/1|nmsclean,nmsadv,maskclean,maskadv,nmsadvB,maskadvB +dose|5|

Stage dose trên5ảnh đầu, K∈{1,10,30,100,300} mà ảnh có đủ detections;
không padding/resampling. Smoke dose chỉ ảnh đầu. Gốc các job stage/total
không đổi; thêm hai B job chỉ thay lịch stage, công khai trước đo.

- Seed shuffle perrep `20261114+1000*image_index+rep`; dùng số arms thực tế.
- Nạp1cặp ngoài timer, reference/counts ngoài timer; warmup3global full/1smoke,
  mỗi job1warmup/ảnh, reference1warmup+3clocked samples; pin3s đầu/cuối.
- Nghỉ60s trước mỗi phiên full/10s smoke. Refs22điểm full: start, từngảnh,end.
- perf_counter_ns/process_time_ns; GC tắt vùng clock; release result sau cả
  hai clock endpoints. NMS clones ngoài clock. Fastguards/logwrite ngoài clock
  nhưng có thể đổi cache/drift; coi đây là protocol khác, không trộn với cũ.
- Session timeout14400s; campaign21600s. Timeout giữ partial và dừng các phiên
  tiếp theo. Campaign cũng dừng sau worker nonzero hoặc gate-only nonzero.
- Trong mọi timing, trợ lý chỉ chờ live frontend handle; không đọc log,
  chạy phân tích, git, test, web hoặc lệnh khác. Sau terminal mới fetch/audit.
  Nếu frontend mất, không coi worker đã chết hay khởi động lại theo suy đoán.

## 6. Cổng chất lượng và phân tích cuối

Từng phiên full phải đủ đúng20IDs/arms/reps/order/reference/guards/pin/terminal;
source/config/input hashes khớp; governorpowersave, actualclock594–606MHz ở
mọi lần đọc, swapOFF, noUSB, pin arithmetic đầu/cuối đúng và đạt. Cả ba masks
giữ nguyên tại guard; no pswp/oomdelta; flaggedreferences≤2 ở drift>3%.
Stop nhiệt≥75C, MemAvailable<40000kB, missing/invalid readback hoặc affinity đổi.
Thiếu áp là điều kiện khai báo, không phải cớ loại ảnh hay quy về1.2GHz.

Pipeline: |meanlogA/A|≤0.02 và MDElog80%≤0.05, như cũ. MDE dùng
`(t_.975,n−1+t_.8,n−1)*SD/sqrt(n)`; t-critical sums n2/n20 tính trên laptop,
khóa trong JSON để Pi không cần scipy. Test khớp công thức chính xác; full
inferential analysis với scipy thực hiện trên laptop bằng stats đã copy.

Stage FULL bổ sung cùng hai ngưỡng cho CẢ NMS và mask A/A. Stage smoke2ảnh
chỉ kiểm đường chạy/physical gates; control noise được lưu mô tả, chưa là
chứng nhận fullstage. Quy tắc này đặt trước mọi timing stage v2, không bỏ một
cổng đã thấy FAIL. Không dùng smoke như số tách công đoạn cho bài.

Offline analyzer yêu cầu thêm restore campaign đạt, explicit reference count
fileSHA và registration khớp; summary mới exclusive. NMS/MASK/dose không có
thì báo thiếu, không lấy phiên khác thay. Phiên đủ cấu trúc nhưng FAIL quality
giữ estimates chẩn đoán trên đủ20ảnh. Phiên thiếu/corrupt chỉ audit+raw, không
giả CI toàn cohort. Không giấu failed session khi phụ dừng hoặc campaign timeout.

## 7. Lưu và giới hạn

Remote v2/runs/{smoke_01,full_01}, local
`results/pi3b_swapguard_v2_20261114/runs/`. Giữ nguyên mọi QA/campaign cũ.
Fetch nguyên thư mục phiên, SHA remote/local, source/tag/input checks,
line selectors cho mọi số; báo cáo `docs/reports/PI3B_SWAPGUARD_V2_RESULTS_20261114.md`.
Xuất các bảng/plots và nguồn sang paper_en khi đủ chứng cứ, giữ main dirty
ngoài thay đổi được kiểm soát. Không chọn cutoffs/seed/cores sau khi xem timing.

Một board thiếu áp,20ảnh không độc lập với laptop/cohort cũ; một model và bộ
PGD. Không kiểm attacker thích nghi, accuracy matched của cap, camera/patch
vật lý, deadline hay service. Không tuyên bố DoS, miễn nhiễm, tương đương từ
p>0.05, hoặc tăng tốc Pi4/Pi5/A36 bằng phép quy đổi thời gian Pi3B.
