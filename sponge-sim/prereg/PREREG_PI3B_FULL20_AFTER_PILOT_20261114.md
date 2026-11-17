# PREREG — Pi 3B full20 sau pilot, giữ nguyên cổng full

Ngày14/11/2026. Tag `prereg-pi3b-full20-after-pilot-20261114`.
Đăng ký trước mọi timing của full20 này, SAU khi đã xem oldfull01 và pilotv2.
Người dùng chấp thuận proposal khi được hỏi cụ thể về full20 mới/giữ cổng/
không lặp pilot, đồng thời yêu cầu làm đầy đủ/tối ưu/ghi mọi khó khăn. Quyền
này không biến một phiên FAIL thành PASS hoặc cho phép lặp full tới khi đạt.

## 1. Lịch sử quan sát, quyết định sau pilot

- Oldfull20 (tagc80cf816): main hoàn tất nhưng swap bật lại giữa phiên;
  số chỉ chẩn đoán. Hai phụ bị từ chối precondition; không retry.
- Swapguard v2(tag560b3aaf): một pilot2ảnh,24timing/72guards hoàn tất, swap/
  pin/clock/reference/AAbias đạt nhưng MDElog0.1335119103548224>0.05. V2 đã
  đóng, full và phụ hủy. Mọi raw/source/âm tính giữ nguyên, không đổi nhãn.
- SDlogAA trên2ảnh0.01340764725726188; phép tính giả định giữ SD tại n20 cho
  MDE0.008856137180298611. Đây chỉ là planning, không số đo hay bảo đảm PASS;
  SDn2 bất định. n20 là mục tiêu có từ trước pilot, không chọn n3/n5 vừa đủ
  qua đường giả định. Không gọi full này là cohort hoặc tái lập độc lập.
- Người dùng đã duyệt thay quyết định mở full: dùng pilot hiện có làm chứng
  cứ đường chạy, KHÔNG chạy thêm smoke. Source mới machine-reject mode smoke
  ở launcher/payload/worker. Đây là ngoại lệ được duyệt so với việc yêu cầu
  một smoke mới, không bỏ cổng full và không mở full dưới tag v2.
- QA workspace mới5case sleeping-payload ở tag7a63da73 đạt,39file SHA khớp.
  Source đo sau QA chỉ ưu tiên thứ tự full; lease/guards/computation giữ nguyên,
  final61hostcontracts đạt3.44s. Không Torch/matmul/pin benchmark trong QA.

## 2. Vật liệu, source và thiết bị khóa

- `studies/pi3b_full20_20261114/lock.json` bind7source/helper/builder,20input
  và weights. Source có header file/dòng/SHA từ v2; v2 không bị sửa.
  Lock SHA tại đăng ký:
  `1cd1789d4f30c0a6b708fad907729999f6e6e53d4ba373ce487bc8037d10be0e`.
- Đúng20 `lock.inputs`/thứ tự đã dùng ở laptop và Pi, cùng byte PGD tensors
  budget16/255, cùng yolov8n-seg.pt. Không sinh/chọn lại seed/ảnh/trajectory.
  Link chỉ đọc tới vật liệu cũ; SHA trước/sau. Không pool các protocol.
- Pi3B Rev1.2,4×Cortex-A53,1GB,OSLite64-bit trixie; nguồn có thiếu áp khai báo,
  governorpowersave/điểm600MHz. Lưu flags cả hiện tại/lịch sử, không nói luôn
  đang undervolted khi chỉ có bit lịch sử. Không quy đổi sang1.2GHz/board khác.
- torch2.15.0+cpu/torchvision0.29.2+cpu/Ultra8.4.90/numpy2.5.4/Python3.13.5;
  fixed NMS/ops Python source hashes như v2. Không package/network ngoài SSH,
  không đổi nguồn/turbo. Torchvision import trước Ultra; FP32/batch1/640²,
  conf0.25/IoU0.45/nc80/max_det300/baseline max_nms30000.
- Full pipeline net→decode→locked NMS wrapper→native full-resolution mask.
  Cap max_nms300/max_det300 trên cùng ảnh nhiễu. Không đổi renderer/precision/
  resolution, không áp dụng ứng viên preallocation vào baseline này.
- Mỗi manifest ghi tag/commit/lock/runner/weightsSHA,config,version/parallel_info,
  CPUaffinity/threads/firmware/kernel/model và readbacks. Campaign registration
  phải khớp. Tag và source đang deploy được kiểm trước/sau, không build_lock
  sau tag. Referencecounts file cho laptopanalysis là bản đã khóa theo SHA.

## 3. Câu hỏi/đơn vị/endpoint

- H1 chính PI4: geomean pairedratio adv_total/clean_total theo20ảnh.
- H2 chính PI4: advcap_total/adv_total; Holm chỉ {H1,H2}.
- Clean_total là median gộp A+B trên mỗi ảnh(12mẫu PI4,8mẫu PI1); mỗi arm
  khác lấy median lặp. Logratios theoảnh→mean→exp, không chia globalmedians.
- Bootstrap percentile20k theoảnh, RNG20261115/16; exact signflip2^20 two-sided,
  tolerance1e-12/p nhỏ nhất2/2^20; d_z mean/SD(ddof1). n=20ảnh, không sốtrial;
  CI không phủ perturbationseed/board/nguồn/model.
- AA seed20261117, cap/clean20261118, forwardadv/clean20261119; phụ PI1 không
  được dùng cho kiểm speedup nhân quả/interaction xuyênprofile. Tỷ trọng
  forward là median tỷ số perimage, không trừ/cộng các median để suy component.
- NMS/maskadv/clean: phụ/mô tả, bootstrapảnh như v2; mask seed20261120,
  NMS20261121. Không suy O(N²)/O(K) từ fit. NMS endpoint là toàn bộ wrapper
  lọc/sắp xếp/chuẩn bị+fixedkernel, KHÔNG bare-C++kernel time.
- StageAA dùng nmsadv/nmsadvB và maskadv/maskadvB, median/ảnh. Đây là control
  tại attacked workload, không chứng nhận noise mọi clean/zero-mask microcall.
  Hai B chỉ phục vụ precisiongate, không pool B để sửa efficacyestimand.

## 4. Một full duy nhất, thứ tự tối ưu việc thu dữ liệu

Chỉ một campaign `full_01`, freshprocess mỗi phiên, thứ tự khóa:

| Thứ tự | Phiên | CPU/intra/inter | Arms/lặp mỗi ảnh |
|---:|---|---|---|
|1|pipeline_PI4 chính|0–3/4/1|cleanA,cleanB,adv,advcap,cleanforward,advforward;6|
|2|stages_PI4 phụ|0–3/4/1|nmsclean,nmsadv,maskclean,maskadv,nmsadvB,maskadvB+dose;5|
|3|pipeline_PI1 phụ|3/1/1|6arms như chính;4|

Đổi thứ tự trước full để cơ chế NMS/MASK không phải đợi phiên1luồng dài;
không thay theo kết quả giữa chừng, không so tuyệt đối xuyênprofile như một
causal treatment. Nếu gate/worker fail, dừng các phiên chưa bắt đầu và ghi hủy.

- Mỗi khối nạp1cặp ngoài timer, reference/counts ngoài timer; globalwarmup3,
  warmup1/job/ảnh, reference1warmup+3clockedsamples; start/perimage/end22refs;
  pin3sđầu/cuối; settle60strước mỗi phiên. Không tăngwarmup sau khi thấy drift.
- Thứ tự arm shuffle seed20261114+1000*image_index+rep, theo số arm thực tế.
  Dose trên5ảnhđầu, K∈1/10/30/100/300 mà ảnh có đủ detections; không padding.
- PI4pipeline720timing,PI1pipeline480; stage600base+5*Σ(levelsavailable của
  5ảnhđầu), không giả đủ5levels cho mọiảnh. Giữ allIDs/allarms/allreps.
- perf_counter_ns/process_time_ns,GCoff trongclock; releaseoutput sau cả hai
  clockends, NMSclone ngoài clock. Guards/log/IO ngoài clock nhưng có thể đổi
  cache/drift; không gọi đây là overheadzero hoặc so trực tiếp các protocol.
- Sessiontimeout14400s, campaign21600s, supervisorstop120s. Chỉ chờ liveSSH
  handle trong đo; không logpoll/git/test/paper/analysis/song song. SSHkeepalive
  transport30s/Max10 là giữkếtnối, không dataquery. Mấtfrontend không là chứng
  cứ worker chết; không restart theo timeout quan sát.

## 5. Cổng full giữ nguyên, không sửa sau dữ liệu

Từng phiên phải hoàn tất20đúngID/arms/reps/order/guardpairs/source/registration,
referencevàpinhaiđầu; structural audit không được PASS do tập rỗng.
Governor powersave, actualclock594–606MHz ở mọi snapshot, runtime3masks đúng,
kernelSwapTotal0+/proc/swapsrỗng, noUSBstorage, affinitykhớp, no pswpin/out/
oomdelta từ baseline. Các counters là của toàn hệ thống, không của riêng worker.

- Referenceflags≤2, thresholdabsratio−1>0.03; không bỏ flaggedimages để cứu.
- Pipeline: abs(meanlogA/A)≤0.02 VÀ MDElog80%≤0.05 trên20ảnh.
- Stage: CẢ NMSadvAA và maskadvAA phải đạt cùng hai ngưỡng trên20ảnh.
- MDE `(t_.975,n−1+t_.8,n−1)*SD/sqrt(n)` central-t approximation. Criticalsum
  n20 khóa trước trênlaptop để Pi không cần scipy; công thức/thứ tự phép tính
  khớp frozenstats trong hosttests. Offline inferentialanalysis trênlaptop.
- Safety: temp≥75C,MemAvailable<40000kB,affinity/governor/swap/mask/USB đổi,
  missing/invalid readback hoặc pswp/oomdelta =>abort/flush/dừng, không tựsửa
  rồi resume. Guard trước/sau clock không nhìn peak giữa lời gọi; RSS cuối
  block không là peakRSS. Actualclock chỉ bảo đảm tại các điểm đọc.
- Restorephảiđạt: governor/swap topology+priority/units/helperActiveState+Result
  khớpsnapshot, chỉ gỡ runtime masks sởhữu. IndependentExecStopPost và
  cgroupcleanup như QA5case; không hứa mấtđiện/kernelstall được khôi phục.
- Chỉ đạt quality của phiên sau khi các cổng trên và campaignrestore đều đạt.
  Phiên đủ cấu trúc nhưng FAIL vẫn giữ estimate20ảnh chẩnđoán. Thiếu/partial/
  corrupt thì audit+raw, không giả một CI toàncohort. Các profile độc lập về
  trạng thái đạt; một phiên phụ bị hủy không biến main đã đạt thành dữ liệu mất.

## 6. Hữu hạn, lưu và báo cáo

Không lặp smoke, không full02, không thửcore/threshold/repeatgrid, không đổi
source/backend/ảnh sautag. Một full FAIL/partial giữ nguyên và kếtthúc; không
tạo chuỗi protocol mới để tìmPASS. Nếu có vấn đề mới cần thay source/thiết kế,
ghi khókhăn/negative và đềxuất mới, không tự chấm lại kếtquả cũ.

Remote `~/sponge-sim/pi3b_full20_20261114/runs/full_01`; local
`results/pi3b_full20_20261114/runs/full_01`. Fetchnguyên/thựcSHAhaiPhía,
source/inputs trước-sau; unchangedanalyzerCLI với explicitlockedreference,
summaryexclusive. Report `docs/reports/PI3B_FULL20_RESULTS_20261114.md` theo
4mục, đủ H1/H2/AA/MDE/forwardshare/stageAA/NMS-MASK/Kdose/countparity/quality,
mọi số có file:selector và rawlinemap. Ghi mọi lỗi/hủy/cảnhbáo, cảcôngthức
lập kếhoạch không bảo đảm thànhcông. Chưa có fulltiming tại thời điểm đăngký.

Tối ưu rendererpreallocation/cácbackend khác là các condition nghiên cứu
RIÊNG sau baseline, cần outputparity/accuracy/overhead và protocol trước đo;
không âmthầm đổi baseline để số đẹp. Sổkhókhăn/tốiưu
`docs/reports/PI3B_OPTIMIZATION_LEDGER_20261114.md` tiếp tục cậpnhật.

Mộtboardthiếuáp/600MHz,20ảnh cùngbộPGD/toànảnh, mộtmodel; không physicalpatch,
camera, adaptiveattacker, accuracy-latencymatched, deadline/service/DoS,
không generalize hoặc quyđổi đếnPi4/Pi5/A36/GPU. Kếtquả không đảm bảoQ1.
