# Pi 3 Model B 1GB cho Sponge Patch phân đoạn

## Đã xong

**Đánh giá: Pi3B vẫn là phương án khả thi có điều kiện cho một trục board thật,
đặc biệt đo offline. Chưa đủ bằng chứng cam kết nguyên stack PyTorch640/K300
vừa1GB hoặc chạy thời gian thực.** Không cần Pi4 chỉ để có một thiết bị ARM
nhúng thật; câu hỏi nghiên cứu và tiêu chí chất lượng quyết định giá trị dữ liệu.

Đây là đánh giá tài liệu/source và phép tính byte, **không phải benchmark Pi**.
Ngày kiểm nguồn08/11/2026. Không truy cập điện thoại, chạy model, cài gói, đổi
nguồn/cài đặt, tải dataset hoặc thay raw trong giai đoạn này. SSH điện thoại
tiếp tục giữ mở theo chỉ dẫn hiện hành; mục tiêu ARM đang làm không bị hủy.

Theo [hãng Raspberry Pi](https://www.raspberrypi.com/products/raspberry-pi-3-model-b/),
Pi3 ModelB có4 lõi64-bit1.2GHz và1GB RAM. Không nhầm với B+1.4GHz. Chọn
[Raspberry Pi OS Lite64-bit](https://www.raspberrypi.com/documentation/computers/os.html):
Pi3 hỗ trợ64-bit, Lite bỏ desktop. [Hướng dẫn PyTorch](https://docs.pytorch.org/tutorials/intermediate/realtime_rpi.html)
yêu cầu64-bit cho wheel ARM chính thức; vẫn phải kiểm từng bản Python/torch/
torchvision và binary CPU trên A53 trước dùng, không mặc định môi trường A36
hoặc laptop cài nguyên xi được trên board.

| Việc của đề tài | Khả năng hợp lý trước khi có board |
|---|---|
| Metadata, ghim luồng, kiểm supervisor | Làm được về mặt thiết kế; phải xác minh trên board |
| NMS/MASK controls với tensor chuẩn bị | Ứng viên phù hợp để bắt đầu; chưa có latency/RSS thực |
| Replay nano-seg, batch1, từng ảnh | Có đường triển khai; phụ thuộc runtime và RAM đỉnh |
| Nguyên pipeline FP32/640/K300 hiện tại | Chưa cam kết; cần tối ưu retention/mask và smoke |
| Tối ưu PGD nhiều seed/train trên board | Không phải việc nên giao cho Pi3B; sinh ở máy khác rồi replay |
| Camera phân đoạn realtime | Chưa có bằng chứng, không hứa FPS |

## Phát hiện cần biết

### Bộ nhớ có chỗ giảm cụ thể trong code hiện tại

Đã đọc `studies/laptop_seg/run.py`: worker đang nạp toàn bộ cặp frozen inputs
vào danh sách, và phần power/QoS còn có API Windows. Không đưa nguyên runner
này lên Pi; cần adapter Linux/board và giữ các kiểm định đã có.

Đã đọc đúng `ultralytics/utils/ops.py` trên máy, SHA
`828de5d265ab91a792acae836f9380d07abda2a15a501170fc9f49d7a448688d`,
khớp lock carryover. Renderer đã chia upsample theo ngân sách32M pixel và
crop riêng hàng/cột tại chỗ. Vì vậy **không được mô tả nó đang giữ toàn bộ
K mask float640 cùng lúc** hoặc đề xuất lại hai tối ưu đó như chưa có.

| Đại lượng tính toán | Byte/MiB |
|---|---|
| Một cặp RGB FP32/640 sạch+nhiễu | 9830400byte =9.375MiB |
|20 cặp như config carryover |196608000byte =187.5MiB |
|300 mask uint8/640 |122880000byte =117.1875MiB |
|300 mask uint8/320 |30720000byte =29.296875MiB |
| Float chunk lớn nhất hiện tại ở K300/640 (78mask) |127795200byte =121.875MiB |

Nguồn công thức và hash: `pi3b_feasibility_20261108_01/memory_arithmetic.json`.
Đơn vị MiB là byte/2²⁰; mỗi RGB float có4byte, uint8 có1byte. Đây là kích
thước buffer, **không phải RSS đỉnh**: còn model, activations, runtime, OS,
workspace, allocator và các thời điểm buffer cùng tồn tại.

Hai thay đổi đáng làm trước: chỉ giữ một cặp ảnh (nạp ngoài clock), và thay
danh sách uint8+torch.cat bằng một output uint8 cấp trước rồi điền từng chunk.
Cả hai là ứng viên tối ưu, chưa triển khai/đo trong review này. Cần kiểm output
từng byte cùng crop/order và đăng ký renderer mới trước timing. Không giảm K,
thay threshold hay âm thầm đổi640→320 để coi là cùng cấu hình baseline.

### Runtime nhẹ là phương án có thật, nhưng là một điều kiện khác

[Ultralytics](https://docs.ultralytics.com/integrations/ncnn/) liệt kê export
segmentation cho NCNN. [Tencent có ví dụ C++ YOLOv8-seg](https://github.com/Tencent/ncnn/blob/master/examples/yolov8_seg.cpp).
Đây là cơ sở cho phương án standalone để giảm phụ thuộc Python/PyTorch. Tuy
nhiên ví dụ có NMS/preprocessing/resize mask riêng và vẫn upsample nhiều mask;
không copy nguyên ví dụ rồi coi tương đương pipeline đang đo. Phải khớp input,
preprocessing, threshold, class-awareness, cap và kiểm prediction/count/mask.

NCNN [lightmode](https://github.com/Tencent/ncnn/blob/master/src/option.h)
tái sử dụng intermediate theo mặc định; các cờ thread/precision vẫn phải khóa.
NCNN/framework đổi nghĩa là một backend mới. Nếu so phần cứng thuần, nên chạy
cùng bản backend đó trên A36 và Pi, đồng thời giữ riêng dữ liệu torchvision.
Không hứa INT8 chỉ bằng export NCNN của Ultralytics hoặc coi FP16 tự động nhanh
hơn trên A53; bắt đầu FP32, lượng tử hóa là nhánh accuracy/count riêng.

[Guide Raspberry Pi của Ultralytics](https://docs.ultralytics.com/guides/raspberry-pi/)
đã thử Pi4/5 và chỉ nói Pi3 kỳ vọng tương thích. Benchmark trên trang đó là
Pi5, không phải số đo YOLOv8n-seg trên Pi3B1GB. Không quy đổi FPS từ các trang
đó hoặc từ A36 thành Pi3.

### Điều kiện để dữ liệu Pi3 có giá trị

Đo từng ảnh offline vẫn có thể trả lời quan hệ N/K–latency và tác dụng cap;
không bắt buộc realtime. Nếu clean đã trượt deadline, chưa kết luận attack DoS.
Nếu có swap/page faults/OOM, tách rõ memory-pressure result với chậm do NMS/MASK.
Theo dõi RSS/availableRAM, pagefault/swap counters, nhiệt, nguồn và
[throttling/undervoltage](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/computers/os/graphics-utilities.adoc).
Nguồn/thẻ/cooling kém có thể làm phép đo trôi; không biến lỗi board thành hiệu ứng.

Một board thật bổ sung external validity, không bảo đảm Q1 hay thay các cổng
ghim/A/A/reference/MDE. Số ảnh nhiều không tự làm nhiều thiết bị.

### Cập nhật giá/phụ kiện từ người dùng08/11

Người dùng báo Facebook380000đ, Shopee450000đ, có lựa chọn lỗi Wi-Fi nhưng
dùng LAN; đang có thẻ8GB/32GB và sẽ tự chuẩn bị nguồn5V. Đây là giá người dùng
quan sát, chưa kiểm listing/người bán/bảo hành; chưa rõ lỗi Wi-Fi thuộc món nào.
Chênh lệch70000đ. Với ngân sách này Pi3B đáng cân nhắc cho board thử offline,
vẫn giữ nguyên giới hạn1GB và chưa cam kết pipeline640/K300.

Ethernet100Base của Pi3B đủ cho SSH/chuyển artifact trước đợt đo; bài này không
đòi Wi-Fi. Tuy vậy chưa chẩn đoán được nguyên nhân Wi-Fi lỗi từ lời mô tả.
Ưu tiên board boot/thẻ/LAN/USB và tải CPU ổn định, không tự reboot hoặc báo
undervoltage; không coi một board lỗi phần cứng nói chung là máy đo chuẩn.
Facebook hợp lý nếu test được trực tiếp;450k shop chỉ đáng hơn khi có cam kết
đổi trả và test rõ, không suy quyền lợi chỉ từ tên nền tảng.

Dùng thẻ32GB sẵn có. [Hãng khuyến nghị tối thiểu8GB cho OS Lite](https://www.raspberrypi.com/documentation/computers/getting-started.html),
nhưng runtime/artifact/log cần thêm chỗ. Nguồn cần đúng micro-USB và dòng/cáp
đủ tốt; [khuyến nghị Pi3 là5.1V/2.5A](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-supply),
không chỉ nhìn nhãn5V. Không cần mua thiết bị mới hay đổi hệ thống trong review.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Tiếp tục tối ưu retention/mask trên A36 theo hướng dễ chuyển Pi3B; sau đó
đo một gói nhỏ trên board khi có → gõ: "Ưu tiên gói Pi3B1GB".

B. Kiểm món cụ thể nếu có listing/video thử → gõ:
"Đây là listing hoặc thông tin bảo hành Pi3B".

Kế hoạch tối thiểu nếu mua: A0 OS/runtime/RAM/nhiệt/nguồn → kiểm output với
batch1/streamed input → smoke640 trên tập đã khóa → chỉ mở nghiên cứu latency
khi pin/memory/A/A/reference đạt. Nếu cần backend/resolution khác, đăng ký
nhánh riêng trước đo. Export/build thực hiện ở máy khác khi phù hợp; Pi dùng
artifact đã khóa. Không phải PREREG cuối và chưa có tag/benchmark cho Pi.

## Đang chờ gì ở tôi

Đã nhận giá/phụ kiện; không hỏi lại. Chỉ cần listing/chính sách đổi trả nếu muốn
đánh giá riêng người bán, không bắt buộc để làm tiếp code. Chưa mua/đo Pi.
Có thể tiếp tục tối ưu trên A36; không đổi nhãn A36 thành board giả lập Pi3.
