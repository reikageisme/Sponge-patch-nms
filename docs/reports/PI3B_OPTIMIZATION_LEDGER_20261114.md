# Pi — tối ưu đã làm, việc còn thiếu và khó khăn

## Đã xong

| Việc | Trạng thái và chứng cứ |
|---|---|
|Giữ swapOFF|runtime mask hẹp, stop trước mask, guard trước/sau clock; QA-c5/5 và v2smoke72guardrecords đạt. Chưa suy mọi thời điểm giữa hai lần đọc.|
|Giảm thao tác cấu hình lặp|mask/unmask theo batch, một daemonreload mỗi batch; không tuyên bố đã đo tăng FPS vì đây là setup ngoài timer.|
|Khôi phục khi tiến trình/kết nối chết|sleep-only QA main/child/timeout/disconnect đạt, cả helper zram được kiểm; không power-loss test.|
|Giảm phụ thuộc trên Pi|không cài scipy; t-critical sums khóa trên laptop, Pi gate công thức tương ứng; inferential analysis trên laptop sau phiên.|
|Giữ RAM đầu vào nhỏ|runner Pi đã nạp1cặp/ảnh từ trước, giữ nguyên; không nhận đây là tối ưu mới. Một cặp RGBFP32/640 có9.375MiB tensor,20cặp187.5MiB là phép tính kích thước, không RSS.|
|Giữ bộ dựng mask đã có chunk|giữ đúng source opsSHA828de5d2… của baseline; không đổi precision/resolution/backend/cap để tăng hiệu ứng.|
|Ghi log ngoài clock|cheapfastguard không subprocess trong timer; vcgencmd ở khối. Overhead ngoài clock vẫn có thể đổi cache/drift, được khai báo và kiểm reference/A/A.|
|Noise control chi tiết|Full20 toàn trình4luồng720timings PASS; stage705timings đủ nhưng NMScontrol FAIL, MASKcontrol riêngPASS; jointstageFAIL. Không retry/loại ảnh. Xem PI3B_FULL20_RESULTS_20261114.md.|
|RSS thực trên Pi, chốt15/11|USB-present full20/360freshprocesses PASS. Preallocated/directcopy16M so với native32M: attacked whole-process RSS ratio0.8755043265545107, CI[0.867515845345165,0.8838846368082481]; AA/MDEcảclean+advPASS. Exactoutputdigests khớp40cache. Xem PI3B_RENDERER_MEMORY_USB_FULL20_20261115.md và independent_full_audit.json. Không là renderer-only/model-residentRSS hoặc speedup.|
|NMS whole-pool/cgroup API,15/11|31hosttests vàONEserviceQA tag03999b2 PASS. Nativepool1→10TID dùTorchintraop4, allaffinity0–3; baancestor nodes giữnguyên. MemorycgfilesUNAVAILABLE, leafcpu.maxvắng; không gán0 hay suyparallelutilization/causalNMS. Raw+reportPI3B_NMS_SERVICE_POOL_QA_20261115.md. Cần stagepoolmapping/sham/matchedpredecessor trước scientifictrace.|
|Staged-pool và cấu hình kernel,15/11|45hosttests+ONE11-stageQA tag7c01949 PASS:1→4sauNumPyimport→7sauTorchsetintraop→10sauones. Temporalnotownership. Cmdlinecgroup_disable=memory; parentCPUsubtreekhôngbậtchochild, giải thíchAPIsvắng theo tài liệu kernel. Khôngenable/reboot/đổithreadđểlấyPASS. ReportPI3B_POOL_STAGES_QA_20261115.md; tiếp theoobservernhẹ/sham, không đặtfullprocfsinventoryquanhNMS.|
|Observer per-call API,15/11|25fake-clocktests+ONE2-samplenativeQA f7258a5 PASS RUSAGE_SELF/THREAD fields/delta. Nativemeasure()chưađượcgọi/chưacóoverhead. Lazyimportresourceởfirstsample làm mô tảnofilesystemquárộng: sourcegiữnguyên, futureintegrationphảibindatsetup+QA. ReportPI3B_NMS_LIGHT_API_QA_20261115.md; matchedpredecessorDRAFTchưarunnable, chưaNMScause/DoS.|
|Integrated core,15/11|51hostchecksPASS: explicitresourceinit/noimportcallpath, immediatepair/outputlifetime, scheduler3600/360, exactkernelargumentstride+offset/cap distinction andcached-tensor parity. Nms.pyhost=PiSHA322nhưngCppversionskhác; native40case/guard/supervisor/ref/sentry/chưatimingscience. Corelockv2flagsFalse, reportPI3B_NMS_PREDECESSOR_CORE_20261115.md; không lấyunitPASSlàNMScause/overhead.|

Nguồn: báo cáo QA/v2, code/PREREG/tag và các receipt trong
`results/pi3b_swapguard_v2*_20261114/`. Các source/estimator/tensors cũ nguyên.

## Phát hiện cần biết

- Thiếu scipy, lỗi stop sau mask, helper reset busy và recovery đều giữ log;
  không giấu các thử kỹ thuật lỗi. Builder trên laptop từng có OSError22 khi
  ghi metadata trước tag; lock cũ còn nguyên/valid, chuyển ghi atomic. Không
  biết nguyên nhân gốc lỗi Windows, không gán cho phần mềm bảo vệ.
- Smoke đủ24timing nhưng MDElog0.1335>0.05 trên2ảnh: không phải kết luận nhiễu
  runtime14%. Protocol v2 đã đóng, full không chạy. Người dùng đã duyệt thiết
  kế full20 riêng giữ ngưỡng; không đo lại smoke hoặc chọn n nhỏ vừa đủ PASS.
- Nguồn thiếu áp ghi nhận, powersave600MHz, thẻ8GB và RAM1GB là giới hạn thật.
  Đã có timing toàn trình full20 đạt; cập nhật15/11 đã có whole-process high-water RSS cache-only dưới điều kiệnUSB riêng, không bảo đảm mọi ảnh/K/pipeline sẽ vừa RAM.
- NMS stage là wrapper Ultralytics khóa backend torchvision, gồm lọc/sắp
  xếp/chuẩn bị và kernel; không tự gọi thời gian đó là bare-C++kernel time.
- Bản thảo đã có hai mục Pi bị loại. Source số/negative-section checks đạt;
  không có TeXcompiler trên PATH nên chưa build/render toàn bài. Main vốn
  dirty được giữ, hai thay đổi của việc này có patch/receipt riêng, không
  commit lẫn thay đổi người dùng. BIB/PDFcũ không ghi đè.

## Việc tiếp theo — chọn 1 trong các cách sau

**Checkpoint15/11 sau full RSS (các đoạn chuẩn bị cũ dưới đây là lịch sử):**
full đã chạy đúngmộtlần theo phê duyệt, không còn chờ mở smoke/full. Thu1814
originalfiles/30153532bytes, SHAremote/local/remote khớp; independent replay
schedule/medians/bootstrap/all2^20signpatterns/units/6238guardframes/mask
hashes đạt. Fullgiữsource70c398a, không sửa runtime để lấyPASS. SSHfrontend
ngắt255 nhưng ownedservice vẫn chạy; chỉ chờ cùnginvocationđếnterminal rồi
mới thu raw, không restart. KeepSSHOPEN, restore/readbackPASS. OldUSBabsentV1
0RSS/FAIL/fullcancel và NMSstageFAIL/PI1cancel giữ nguyên.

Việc tiếp theo thực sự: (1) kiểm workerpool/TID+actualservice/ancestorcgroup
counters vàshamobserver trước controlledNMS trace; (2) QA/tách protocol mới
cho renderer tích hợp modelresident, RSS+latencytradeoff. Hiện chưa có số
cho hai việc này. GiảmRSS không chứng minh giảmpaging/NMScarryover/DoS;
đổi chunk+assembly cùnglúc chưa định lượng riêng hai thànhphần. Thay đổi
nguồn/clock/NCNN/FP16/INT8 sẽ là điều kiện mới, không đổi nhãn kết quả hiện tại.

Candidate renderer đã code và12functionaltests đạt trên laptop; xem
`PI3B_RENDERER_PREALLOCATION_QA_20261114.md`. Phân tích tĩnh phát hiện
preallocation giữ32Mchunk có thể TĂNG max tensor sống: K300640² baseline
263.671875MiB so với candidate268.359375MiB. Chỉ khi dùng16Mchunk/directcopy
mô hình giảm đến207.421875MiB; đây không là peakRSS hay FPS. Giữ cả trường hợp
bất lợi, không dùng biến thể chưa đo để sửa kết quả full20. Draft so sánh
riêng còn cần cache/collector/deviceQA/PREREGtag; chưa có tải Pi mới.

Code cache/collector đã bổ sung và37hostcontrols cuối đạt; xem
`PI3B_RENDERER_CACHE_COLLECTOR_QA_20261114.md`. Parent không import Torch,
maskhash không nhân đôi outputbyte, parity thả output trước khi chạy biến thể
kế tiếp. Lịch dự kiến360freshchild gồm cả clean/adv và hai baseline A/A;
chưa có peakRSS/timing hay devicecgroup/restoreQA. Supervisor/analyzer/protocol
cụ thể vẫn cần hoàn thiện trước đo, không coi hostcontrols là qualificationPi.

Supervisor/analyzer đã bổ sung:66hosttestsPASS và5sleep-onlydevicecasesPASS
dưới tagqa-pi3b-renderer-memory-20261114,39originalSHAhaiPhía. Xem
`PI3B_RENDERER_SUPERVISOR_QA_20261114.md`. Warning transientunitfile ở case
disconnect giữ nguyên/nguyênnhânchưa rõ; actualcache/model/RSS/timing vẫn
chưa chạy. CacheflagFalse và scientificregistration chưa tồn tại; không dùng
QA ngủ để nhận đã tối ưu RAM hoặc hoàn tất qualificationworkloadTorch.

QAcache chức năng tiếp theo đã qua40/40case trên Pi và303guards,90original
filesSHAhaiPhía, tagqa-pi3b-renderer-cache-20261114/b5304d2. Xem
`PI3B_RENDERER_FUNCTIONAL_CACHE_RESULTS_20261114.md`. Input/mask/countparity
hữu hạn được kiểm, nhưng chưa có empiricalRSS/latency mới; guardMemAvailable
không là peak và không phải so sánh hiệu quả. All11Python giữsourceQA3409,
chỉ plan/engineeringflag thay và cấu hình cũ được archive. Caches đã có đủ
để khóa proposal cụ thể; không tự mở memorycampaign từ QA này.

Chẩn đoán raw NMS đã bổ sung (không chạy mới): cả200adv/Bcalls giữ nguyên,
11callsCPU<wall;10/71sau maskadv/B,0/80sau NMS,1/7lượtđầu sauwarmup.
Globalpgmajfault tăng mạnh ở các khối73/74/77, nhưng không gán được cho
process/call hoặc phân biệt paging/threadpool/scheduling. Xem
`PI3B_NMS_SAVED_DIAGNOSIS_20261114.md`. Đây là lý do cần trace process-level
và cân bằng workload trước NMS, không là bằng chứng đã giải thích xong cơ chế
hoặc cớ loại ảnh/chấm lại cổng. RSSfreshprocess là trục bổ sung, không thay
kiểm NMS dưới workload hỗn hợp và không tự suy thành speedup/DoS.

RSS-V1 đã có workspace riêng,77hosttest cuối và năm tình huống ngủ thực trên
Pi đạt dưới tagd58118f;39file gốc và14file nguồn/tham chiếu được đối chiếuSHA.
Xem `PI3B_RENDERER_MEMORY_V1_QA_20261114.md`. Cảnh báo transientunitfile ở
disconnect16:54:23UTC giữ nguyên, chưa rõ nguyên nhân; restore/readback đạt.
Draft RSS định trước smoke kỹ thuật9+30/cóK300/36children, full20/360children;
smoke AA/MDE chỉ chẩn đoán, full vẫn giữ cả hai cổngclean/adv. Chưa có
scientificregistration hoặc sốRSS/timing mới. NMS counterreader10hosttests
  chỉ chuẩn bị mã, vẫn cần actualLinux/sham/matchedpredecessor qualification.

RSS-V1 đã đăng ký dưới289c2e3 và dừng ngay guardUSB trước jobđầu:0/36RSS,
fullhủy/no retry,10file gốc đối chiếuSHAhai phía/restorePASS. Xem
`PI3B_RENDERER_MEMORY_V1_SMOKE_20261115.md`. Người dùng xác nhận SSD cắm
để thêm dung lượng; USB là cấu hình chủ đích. Metadata nhận ADATA SP900/
SupTronicsX89, workspace còn trên thẻnhớ; không tự mount/eject/tháo ổ.
Preflight thiếu USBcheck trước lease là lỗi cần sửa tương lai; không nới
cổng V1 hoặc suy0mẫu thành kết quả thuật toán. Phương án cóUSB phải tách
điều kiện/PREREG, giữ nguyên mọi âm tính và ngưỡng full.

NMS counter API đã qua một lần QA chỉ đọc trên Linux/aarch64 dưới
qatag2703f88: process/thread identity, affinity, fault/context-switch và CPU
cgroup counters đọc được; rawSHAhai phía khớp, cấu hình không đổi. Xem
`PI3B_NMS_COUNTER_METADATA_QA_20261115.md`. memory.events/pressure thiếu
ở scopeSSH được giữUNAVAILABLE; chưa đo trong servicecgroup/Torchpool,
chưa có sham/matchedpredecessor nên không kết luận cơ chế NMS. Phương án
USBnhàn đã soạn riêng, chưa có scienceendpoint mới hoặc retryV1.

USBguard standalone mới đã có41hostregressions và một lần metadataQA thật
trên Pi dưới465f6e5: hai frame/6USBdevices/sda+sdb/17statfields mỗi disk
khớp; SD179:2, source/rawSHAhai phía và cấu hình trước–sau khớp. Xem
`PI3B_USB_GUARD_METADATA_QA_20261115.md`. Chỉ APIhelper, frontend-before-lease/
runtime sampler/child baseline/auditor/supervisor mới CHƯA tích hợp/qualify;
không suy thành RSSbenefit/USBkhôngảnhhưởng hay mởscience. SSDuse ngoài
phaseđược phép; counter/generationbaseline bindriêng mỗi phase, static
identityregistered. RSS-V1zero/FAIL/fullcancel và NMSFAIL vẫn nguyên.

USBpresent runtime đã tích hợp trướclease/parent/child/auditor;130hosttests
và nămcase ngủ thật dưới c6a9747PASS,44rawSHAmatch/restorePASS. Xem
`PI3B_RENDERER_USB_INTEGRATION_QA_20261115.md`.16filegói+metadataold47ee
giữ nguyên. Cảnh báo transientunitfile17:58:31UTCdisconnect giữ lại/unknown.
KhôngRSS/timing/modelendpoint; bước tiếp là đăng ký khoa học trước một
technicalsmoke, review sau kết quả cụ thể, không tự mởfull hay V1retry.

USBpresent smoke70c398a đã36/36RSS/2ảnh/194rawSHAs/physical-mask-USB-restore
PASS; độc lập replay median/AA/units khớp. Xem
`PI3B_RENDERER_MEMORY_USB_SMOKE_20261115.md`. Chỉ mô tả2ảnh, không efficacyCI;
fullqualityflag vẫnFalse theo thiết kế. Sau budgetreview người dùng đã DUYỆT
full20/360 (~2h21 ngoại suy, cap6h, SSDnhàn, mọi gate nguyên). Phê duyệt
đã lưu; không hỏi lại. Full dùng đúng tag/runtime, không phải V1retry; mọi
kết quả âm và NMSFAIL vẫn giữ. Theo dõi full ởPROGRESS/riêngoriginals.

A. Baseline full20 đã đóng: mainPASS, stageFAIL, PI1hủy; audit/plots/source map
giữ đủ âm tính → gõ: "Check báo cáo Pi full20".

B. Sau baseline, đánh giá tối ưu renderer thành một nhánh riêng có output
parity và đăng ký trước timing → gõ: "So sánh renderer tối ưu sau baseline".

Ứng viên hợp lý là preallocate đầu ra uint8 thay list+cat, giữ phép tính từng
chunk/crop/interpolation nguyên. Tại K300/640, một outputuint8 là117.1875MiB;
tránh thêm một bản output ở bước concat có thể giảm lượng tensor sống theo
phân tích tĩnh, **chưa phải peakRSS tiết kiệm hay tốc độ đã đo**. Cần copyops
cóSHA, test exactoutputs/edgecases, rồi cohort/tag/contrasts mới; không đổi
baseline giữa một protocol hoặc dùng timing cũ như baseline ghép cặp mới.

NCNN/FP16/INT8 hay đổi ảnh/threads là điều kiện khác, không tự thay cho baseline
đang khóa; hiện không cài thêm gói hoặc đánh đổi chất lượng đầu ra để lấy số
đẹp. Bất kỳ biến thể nào cũng phải báo cả overhead/accuracy/parity/âm tính.

## Đang chờ gì ở tôi

Không cần duyệt lại code/QA/full20 đã cho phép. Các khó khăn và việc chưa có
bằng chứng sẽ tiếp tục ghi ở đây; mọi estimate phải có raw. Một board và20ảnh
không bảo đảm kết luận tổng quát hoặc khả năng được nhận ở tạp chí Q1.
