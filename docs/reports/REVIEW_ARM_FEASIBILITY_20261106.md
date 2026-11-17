# Rà điểm còn yếu và khả năng dùng Galaxy A36 cho trục ARM

Ngày: 06/11/2026. Phạm vi: bản thảo chính, extension phân đoạn, dữ liệu nested1500 và harness điện thoại hiện có. Đây là review và thiết kế; không có phép đo mới trên điện thoại, không truy cập máy thuê đã xóa.

## Đã xong

**Kết luận thực dụng:** dùng Galaxy A36 làm **thiết bị ARM thật** là hướng có giá trị. Hạn chế tài nguyên trên điện thoại chỉ tạo thêm cấu hình của chính điện thoại; chưa tạo ra số đo Raspberry Pi 4/Pi 5. Không cần biến nó thành Pi để bổ sung external validity.

**Material Passport:** academic-research-suite / experiment-agent, plan; nguồn chính là artifact cục bộ và tài liệu hãng; ngày nguồn 06/11/2026; trạng thái `ANALYZED`, thiết kế ARM `DRAFT/UNRUN`. Skill dự án `sponge-research` áp dụng cho mọi bước đo sau này.

Đã rà các nguồn sau:

- `paper_en/main.tex`, `paper_en/segmentation_extension/{extension,nested1500}.tex` và source maps.
- `docs/reports/{FULL_SEGMENTATION,STABILITY,NESTED1500}_CODEX_20261106.md`.
- `sponge-sim/results/large_seed_20261106/export/{summary1000,summary1500,bootstrap_sensitivity}.json` và các receipt.
- `sponge-sim/results/phone_a36/pin_20261101/{pin_verify,profiles}.json`, `studies/e5_phone/{pin_verify,run}.py`, `src/sponge_sim/hw_linux.py`, `prereg/PREREG_E5_phone.md`.

Những phần đã đóng tốt: 30.000 trường hợp có coverage, archive và hash kiểm được; 1.280 auditcases có 12.800 so sánh K khớp; phân biệt transfer âm với tối ưu trực tiếp YOLO26; các phiên timing thất bại được giữ nguyên. Không cần mở lại các kết quả này để tìm số đẹp.

## Phát hiện cần biết

### 1. Sổ việc còn mở, theo mức ưu tiên

| Mức | Điểm chưa ổn | Bằng chứng hiện có | Việc cần làm / tiêu chí đóng |
|---|---|---|---|
| P0 | **Chưa có timing tấn công phân đoạn thật đạt cổng ổn định trên máy thuê.** | `stability_full_20261106/confirmation_summary.json:stable=false`; M6 có 14/14/10 reference flags. M4/M4B cũng không đạt. | Giữ nhãn diagnostic. ARM có thể là testbed mới nếu qua A/A; không lấy count study thay cho latency hoặc chạy lại cùng host để săn phiên pass. |
| P0 | Một phần lập luận N* của thân bài vẫn dựa trên injection có drift lớn. | `paper_en/main.tex:284` nêu 12/21 reference points bị cờ. Đây là thí nghiệm NMS cũ, khác extension MASK. | Rà lại vị trí headline và độ nhạy của kết luận. Kết quả MASK tổng hợp CPU4/GPU đạt cổng không hợp thức hóa ngược mọi run cũ. |
| P0 | **Điện thoại chưa có cấu hình ghim lõi hợp lệ trong artifact cũ.** | `pin_verify.json:profiles_passed={}`, `conclusion=KHONG_CO_PROFILE_DAT`; `profiles.json={}`. | Sửa và xác minh quy trình theo từng luồng, tiến trình mới. Không gọi dữ liệu cũ là 1/4 lõi hoặc Pi-like. |
| P0 | Bộ chạy điện thoại chưa thực hiện đủ các điều kiện dừng đã đăng ký. | `e5_phone/run.py:160` chờ hết worker; kiểm nhiệt tại `:178` sau đợt. Chưa có nhánh pin >=40°C, đếm ba lần dừng liên tiếp, hay chặn kịp thời trong worker như protocol yêu cầu. | Hoàn thiện supervisor và đối chiếu đúng protocol trước tải kéo dài. Không chạy nguyên runner này trên điện thoại dùng hằng ngày. |
| P1 | Cần thống nhất câu chuyện của bản thảo. | Abstract tập trung YOLOv8n/v5s, NMS và một CPU; appendix mới có segmentation, mask workload, YOLO11/26 và GPU. | Chọn rõ đóng góp chính và vai trò appendix. Tách Sponge Patch cục bộ hộp xám, whole-image PGD và adapted reference attacks; không xếp hạng như cùng quyền truy cập/ngân sách. |
| P1 | CI trung vị bootstrap hai tầng có dịch chuyển đáng kể. | N1500: median26-many=287.8, CI đã đăng ký=[288.4,292.0]; sensitivity tái tạo đúng, không phải lỗi đọc số. | Giữ nguyên; nêu hạn chế của median phi tuyến và các endpoint biên. Dùng paired mean-gain/reach đã đăng ký khi bàn hiệu ứng; nghiên cứu coverage trước khi chọn phương pháp cho nghiên cứu mới. Không đổi CI hậu nghiệm. |
| P1 | Phòng thủ chưa có đường cong accuracy–latency cùng điều kiện. | Accuracy 5.000 ảnh dùng letterbox/conf0.001; count/attack dùng resize vuông/conf0.25. | Ghi giới hạn; thiết kế đánh giá cùng preprocessing/runtime, đo sạch và nhiễu với từng cap. Chưa có chứng cứ phòng thủ giữ QoS chỉ từ K/mAP riêng lẻ. |
| P1 | Chưa có đánh giá availability trực tiếp cho YOLO26 native. | Tối ưu trực tiếp làm K cao; K>=50 là cutoff đếm, chưa được hiệu chuẩn thành ngưỡng chậm của model này. | Nếu cần claim availability: đo pipeline native gồm mask, rồi kiểm deadline với workload sạch khả thi. Không suy DoS từ K. |
| P1 | Số ảnh lớn chưa thay thế được số thiết bị/phiên độc lập. | 1.000 nằm trong 1.500; năm starts có một zero và bốn random; hiện chỉ một host thuê trong extension. | Báo rõ đơn vị ảnh/start/session/device; thêm ARM thật và nhiều phiên, không gọi hai prefix là hai tái lập độc lập hoặc gọi nhiều profile là nhiều board. |
| P2 | Portability và artifact release cần hoàn thiện. | Exact inputs chỉ có 64 audit IDs cho mọi task/start; ZIP lớn ở local; main.tex còn dirty từ trước; chưa build PDF toàn bài. | Công bố manifest/receipt và hướng dẫn lấy archive được phép chia sẻ; nói đúng coverage replay; review bản thảo và build PDF ở môi trường có TeX. Không sửa raw để thuận công bố. |

### 2. Bằng chứng điện thoại cũ: điểm chặn nằm ở đâu?

Nguồn: `sponge-sim/results/phone_a36/pin_20261101/pin_verify.json:verify.<profile>`. Các số sau là **lịch sử 01/11**, không mô tả cấu hình hiện tại.

| Profile cũ | CPU đề nghị | CPU hiệu dụng | Tỷ lệ mẫu CPU cuối nằm trong tập | Đạt cổng cũ? |
|---|---|---:|---:|---|
| big1 | [5] | 0.906282 | 0.400000 | Không |
| big4 | [4,5,6,7] | 3.402703 | 0.874126 | Không |
| little1 | [1] | 1.758106 | 0.300000 | Không, cả giới hạn CPU hiệu dụng |
| little4 | [0,1,2,3] | 3.129678 | 0.619048 | Không |

Tất cả tám lần đọc lại mask cho luồng gọi đều thành công. Điều này **không** xác minh toàn bộ thread pool. Trên Linux, affinity là thuộc tính từng luồng; pid=0 chỉ áp dụng cho luồng gọi. `hw_linux.py:56` dùng đúng lời gọi này; `pin_verify.py:31,51,74` nhập torch, chạy benchmark, rồi đổi profile trong cùng tiến trình. Thread pool đã tồn tại là một giả thuyết cần kiểm tra, chưa phải nguyên nhân được xác nhận trên thiết bị. [Linux sched_setaffinity](https://man7.org/linux/man-pages/man2/sched_setaffinity.2.html)

Tag lịch sử `prereg-e5phone-20261101` có source harness để đối chiếu. Tuy nhiên `pin_verify.json` không tự ghi SHA mã đang chạy, nên phân tích source hiện có chưa thay cho việc tái xác minh thiết bị; không khẳng định đã xác định nguyên nhân duy nhất của lần FAIL.

`hw_linux.py:64–110` lấy trường CPU cuối của mọi TID, không phân biệt luồng đang ngủ hay có tiêu thụ CPU trong cửa sổ lấy mẫu. Trường này biểu thị CPU mà luồng chạy **lần gần nhất**. Vì vậy mẫu có thể bị nhiễm thông tin cũ từ luồng ngủ. Đây là rủi ro sai phân loại của phép kiểm; không đủ để tự đổi bốn kết quả FAIL thành PASS. Đặc biệt little1 còn vượt giới hạn CPU hiệu dụng, nên chưa thể quy toàn bộ thất bại cho sampler. [Linux proc_pid_stat](https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html)

Cách kiểm mới cần: tiến trình riêng cho từng tập CPU; đặt mask trước khi nhập torch; đọc mask của từng TID sau khởi tạo/warmup và trong tải; đối chiếu residency của các luồng có tăng CPU-time; kiểm CPU-time/wall-time; ghi mọi lỗi quyền truy cập. Giữ nguyên artifact cũ. Nếu cần đổi phép kiểm đã đăng ký, viết amendment mới trước khi chạy, không sửa cổng cũ để lấy PASS.

Runner cũ còn là detector YOLOv8n ở conf0.01, không phải segmentation conf0.25. `total()` dùng `torch_pure`; stage `nms_tv_nms` được đo riêng, nên không được gọi total cũ là pipeline torchvision. Hai backend cũ này đều agnostic; việc thiếu `prepare()` trong total **không tạo lỗi class-aware trong phiên bản hiện tại**, vì `TorchPure.run()` chỉ dùng boxes/scores. Khi chuyển sang segmentation/fixed-TV phải khai rõ backend và class semantics (`e5_phone/run.py:57–85`, `backends.py:35–52`).

### 3. Snapdragon có thể thay Pi ở mức nào?

| Nền tảng / cách chạy | Điều xác minh được | Giá trị số liệu cho bài |
|---|---|---|
| Galaxy A36 chạy CPU thật, qua Termux/proot | Runtime thật của điện thoại; cần qua pin/A/A/nhiệt | Trục ARM bổ sung, đúng tên thiết bị và software stack |
| Chọn 1/2/4 CPU được xác minh trên điện thoại | Thí nghiệm hạn chế tài nguyên trên một SoC | So ảnh hưởng resource profile; không thành Pi4/Pi5 hoặc thêm thiết bị độc lập |
| Chạy rootfs Ubuntu/Raspberry Pi OS, đổi uname, Docker/proot | Thay userland hoặc giao diện phần mềm | Không thay CPU, cache, RAM controller hay hệ thống nhiệt |
| QEMU raspi4b trên điện thoại | Kiểm tương thích chức năng trong emulator | Thời gian host/emulator, chưa là latency của Pi thật |
| Pi4/Pi5 thật chạy cùng fixtures | Đo đúng board, revision, runtime và điều kiện nhiệt cụ thể | Mới có cơ sở ghi số đo Pi4/Pi5 |

Samsung xác nhận A36 dùng Snapdragon 6 Gen 3. Qualcomm công bố CPU 64-bit gồm bốn performance cores tối đa2.4GHz và bốn efficiency cores tối đa1.8GHz. Brief không đủ để tự gán tên Cortex cho từng cụm trên máy của người dùng. [Samsung](https://samsungmobilepress.com/articles/samsung-marks-a-step-forward-with-ai-for-everyone-by-introducing-new-galaxy-a56-5g-galaxy-a36-5g-and-galaxy-a26-5g), [Qualcomm product brief](https://www.qualcomm.com/content/dam/qcomm-martech/dm-assets/documents/Snapdragon-6-Gen-3-Product-Brief.pdf)

Trang hãng hiện ghi Pi4 là BCM2711, bốn Cortex-A72 @1.8GHz; Pi5 là BCM2712, bốn Cortex-A76 @2.4GHz. Nếu mượn board phải ghi revision và xung thực tế, không dựa trên tên thương mại. **Suy luận kỹ thuật:** cùng ISA/số lõi/GHz không làm cache, memory bandwidth, thư viện toán, scheduler hoặc thermal envelope tương đương. Không có hệ số quy đổi ms hợp lệ chỉ từ các thông số này. [Pi4](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/), [Pi5](https://www.raspberrypi.com/products/raspberry-pi-5/)

PRoot dùng ptrace cho system calls, không đem lại real root hoặc cgroups/namespaces thực. Vì thế không mặc định áp dụng được Docker CPU/RAM quota trong Ubuntu proot. Ngay trên Linux có cgroup thực, `cpu.max` là ngân sách CPU theo khoảng thời gian, không phải lệnh biến vi kiến trúc thành A72/A76. [PRoot-Distro limitations](https://github.com/termux/proot-distro#proot-limitations), [Linux cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)

Tài liệu QEMU đã kiểm có raspi4b; danh sách đó không có Pi5. Quan trọng hơn, ngay chế độ icount cũng không mô phỏng chính xác theo chu kỳ CPU. Vì vậy không dùng thời gian QEMU làm số latency Pi4/Pi5. Tính năng của bản QEMU cụ thể vẫn phải kiểm nếu sau này chỉ thử tương thích. [QEMU raspi boards](https://www.qemu.org/docs/master/system/arm/raspi.html), [QEMU icount](https://www.qemu.org/docs/master/system/invocation.html)

Không đổi governor, tắt bảo vệ nhiệt, root máy hoặc dùng sleep/busy-wait để tạo ra “Pi4 chậm/Pi5 nhanh”. Không dùng điểm Geekbench làm hệ số quy đổi forward/NMS/mask. Đây là khuyến nghị phương pháp, không phải benchmark so sánh đã thực hiện.

### 4. Thiết kế ARM nên ưu tiên cho đóng góp nghiên cứu

**Câu hỏi tốt hơn:** quan hệ N/K → độ trễ, và tác dụng chặn trước NMS/chặn đầu ra, có giữ khi chuyển từ x86/GPU sang CPU ARM thật không? Có thêm MASK vào mô hình ngân sách có cải thiện dự báo trên ảnh chưa dùng hiệu chuẩn không?

Thứ tự ít tốn công nhất:

1. **A0 — sửa phép xác minh và kiểm môi trường.** Khởi đầu với hai profile 1 CPU nhanh và 4 CPU cùng cụm đã xác minh. 2 CPU hoặc cụm chậm chỉ thêm khi có lý do và ghi trước. Nếu không ghim được, một nghiên cứu ARM không ghim vẫn có thể thiết kế riêng, nhưng không giữ nhãn 1/4 lõi.
2. **A1 — A/A và workload MASK có kiểm soát.** Cùng v8n-seg, FP32, batch1, resize640, fixed torchvision NMS. Khảo sát K=10/50/100/300 và hai mức mask resolution, đo trực tiếp total cùng các stage; vẫn là positive control tổng hợp. Chọn warmup/thời lượng đợt bằng controls-only rồi khóa, không chọn bằng slowdown.
3. **A2 — replay tấn công thật trên 64 audit images.** Đủ exact float32 inputs đã có, không phải tái tạo gần đúng 1.500 ảnh. Khởi tạo0 khóa trước; sạch/nhiễu tại baseline, output cap50 và pre-NMS cap300, tức ba phép so sánh sạch–nhiễu. Primary là baseline; defense là secondary. Ba phiên tách biệt cho hai profile là **đề xuất chưa chạy**, không phải power đã chứng minh. Counts được đếm lại trên ARM; không ép bằng GPU vì batch/runtime khác.
4. **A3 — dự báo và deadline, nếu chất lượng cho phép.** Hiệu chuẩn chỉ bằng controls; khóa tập calibration/test và kỳ phát trước khi xem attacked timing. Nếu cần availability, dùng worker xử lý thật với scheduled release/start/finish và queue bound, chứng minh sạch còn khả thi. Replay hàng đợi từ service times chỉ được gọi là mô hình. Camera/đường truyền vẫn ngoài phạm vi nếu chưa đo.
5. **A4 — native26 chỉ thêm sau kiểm tương thích.** Version trên điện thoại phải kiểm lại; không giả định checkpoint `.203` tải được trên runtime cũ `.197`. Nếu dùng native, bật và kiểm đầu one-to-one, đếm score column4, không NMS, đo cả mask. Không tự cập nhật gói hoặc đổi backend để làm nó chạy rồi gọi là cùng thí nghiệm.

Ghim lõi, nhiệt, A/A và provenance có giá trị hơn tăng ngay số ảnh lên 1.000 trên điện thoại. Điện thoại là một mẫu thiết bị; nhiều phiên giúp đánh giá độ ổn định trong thiết bị, không đại diện mọi ARM. Không thể cam kết Q1 từ số board/ảnh. Giá trị tăng thêm nằm ở đo đúng cơ chế, kiểm dự báo ngoài hiệu chuẩn và giữ kết quả âm.

Nếu sau này mượn được Pi4/Pi5, dùng chính gói64 frozen inputs trên board thật. Chỉ cần subset có protocol phù hợp để kiểm external validity; không cần tối ưu lại 30.000 trường hợp. Không có board đo chuẩn thì mọi dự phóng sang Pi phải để dạng kịch bản mô hình, có nhãn chưa kiểm chứng, không nằm trong bảng measured hardware.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Sửa bộ xác minh điện thoại và chuẩn bị preflight, chưa đo full → gõ: **“Sửa preflight ARM và chuẩn bị gói cho Galaxy A36.”**

B. Chốt lại luận điểm bản thảo và danh sách claim đủ bằng chứng → gõ: **“Rà và hợp nhất paper_en theo review ARM mới.”**

Draft thiết kế cụ thể: `sponge-sim/prereg/DRAFT_ARM_A36_SEGMENTATION_20261106.md`. Chưa có PREREG tag cho phép đo mới vì còn gate/lock phải hoàn thiện.

## Đang chờ gì ở tôi

Hiện không cần bật SSH, mua board hay cho chạy tải trên điện thoại. Chưa có bước đo được khởi động. Khi chuyển sang chạy thật, phải có phiên bản runner đã sửa, khóa protocol/tag, và xác nhận điều kiện rảnh/mạng/nhiệt theo quy tắc của dự án. Máy thuê đã được người dùng xóa; không truy cập lại IP cũ.

Nguồn web là tài liệu chính thức được kiểm ngày06/11/2026, không phải dữ liệu đo trên điện thoại của người dùng. Manifest nguồn/hash cục bộ: `review_arm_20261106_sources.json`.
