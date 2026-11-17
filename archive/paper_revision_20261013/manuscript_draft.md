# Sponge Patch: Đánh giá lỗ hổng tiềm ẩn cạn kiệt tài nguyên trên hệ thống phát hiện vật thể tại biên bằng tối ưu không gian hộp xám

Phạm Tuấn Anh và Mai Quốc Bảo
Trường Đại học Công nghệ Thành phố Hồ Chí Minh (HUTECH), Việt Nam
Email: anh25807700004@hutech.edu.vn; bao2580770008@hutech.edu.vn
Giảng viên hướng dẫn: Đinh Phương Nam — dp.nam@hutech.edu.vn

## Tóm tắt

Nghiên cứu đánh giá lỗ hổng tiềm ẩn cạn kiệt tài nguyên trên hệ thống phát hiện vật thể tại biên khi chịu tấn công Sponge Patch — phương pháp tối ưu hộp xám sử dụng thuật toán di truyền (SG-GA) hướng bởi điểm tin cậy trước NMS và biến đổi ngẫu nhiên, không dùng gradient. Giao thức kiểm chứng được công bố với truy vết hash đầy đủ: weights, mã nguồn, seed, bộ ảnh và file kết quả, cho phép tái lập từng số liệu. Trên 500 ảnh COCO val2017 held-out giữ riêng, 10 seed, ngân sách 2.500 lượt suy luận ảnh, tỷ số ứng viên trung bình của SG-GA là 1,0268, thấp hơn GA tâm 1,0561 với chênh lệch ghép cặp −0,0293, khoảng tin cậy 95% [−0,0383; −0,0216], p = 0,002 (kiểm định sign-flip chính xác), hiệu chuẩn Cohen dz = −2,05. SG-GA không vượt GA-center; ngược lại, whitebox gradient tanh đạt tỷ số 1,1987 — lớn hơn SG-GA — cho thấy nguyên nhân nằm ở hàm fitness, không phải kiến trúc thuật toán. AP hộp giảm từ 30,27% xuống 29,97%, nhưng dịch vụ FIFO tại chu kỳ 300 ms vẫn đáp ứng trên mọi điều kiện. Khảo sát tám kiến trúc phát hiện (YOLOv8n/s, YOLO11n/s, YOLOv12n, SSDlite, Faster R-CNN, RetinaNet) cho tỷ số đồng nhất 1,02–1,24; không detector nào cho thấy bùng nổ ứng viên. Mô phỏng QoS container (1/2/4 thread, deadline 100/200/300 ms, stream 10 fps, 500 frame) cho thấy thời gian phục vụ clean trung vị 220 ms đã vượt deadline 100 ms; SG-GA thêm không đáng kể (220–230 ms so 220 ms), trong khi tanh whitebox nhanh hơn (70 ms) — ngược chiều kỳ vọng DoS. Kết luận: chưa có bằng chứng suy giảm tính sẵn sàng do khuếch đại ứng viên bởi Sponge Patch trong điều kiện thử nghiệm. Kết quả âm được giữ nguyên và công bố kèm dữ liệu gốc, phục vụ đánh giá có kiểm soát lỗ hổng tiềm ẩn trên pipeline NMS-based.

Từ khóa: miếng dán đối kháng; tính sẵn sàng; NMS; tối ưu hộp xám; thuật toán di truyền; chất lượng dịch vụ; phát hiện người.

## 1 Giới thiệu

### 1.1 Bài toán và động cơ

Một hệ thống thị giác phục vụ giám sát hoặc nhận thức tại biên phải đồng thời phát hiện đúng và trả kết quả kịp thời. Độ chính xác cao trên ảnh tĩnh không bảo đảm hệ thống đáp ứng thời hạn khi nội dung thay đổi, hậu xử lý tạo thêm công việc hoặc hàng đợi tích lũy. Ngược lại, giảm AP chưa đủ để kết luận dịch vụ bị từ chối. Vì vậy, đánh giá đầu vào đối kháng cần phân biệt tính toàn vẹn của dự đoán với tính sẵn sàng của đường ống xử lý.

Các nghiên cứu gần đây cho thấy tính thực dụng của tấn công độ trễ phụ thuộc phần cứng, định dạng mô hình và công đoạn được đo. Underload kết hợp huấn luyện đối kháng với khả năng thiết bị để bảo vệ detector trước tải hậu xử lý [C:underload2025]. EVADE chỉ ra rằng hiệu ứng của các tấn công NMS có thể nhỏ hơn nhiều khi chuyển sang cấu hình triển khai thực tế [C:evade2025]. Hai kết quả không mâu thuẫn một cách đơn giản: chúng đặt ra yêu cầu kiểm tra điều kiện mà hiệu ứng xuất hiện, thay vì suy luận DoS từ số hộp hoặc độ phức tạp lý thuyết.

Sponge Patch được xây dựng để khảo sát một kịch bản quyền truy cập hạn chế: thuật toán không đọc gradient hoặc trọng số, nhưng được phản hồi điểm tin cậy trước NMS. Miếng dán chỉ ghi đè một vùng cục bộ trong ảnh. Tính hữu ích tiềm năng của hướng này nằm ở việc giảm yêu cầu truy cập so với tối ưu hộp trắng và đặc tả rõ một giao thức có thể kiểm toán. Tuy nhiên, quyền truy cập thấp hơn không tự chứng minh hiệu quả tấn công cao hơn. Kênh phản hồi trước NMS vẫn là một giả định mạnh và phải được nêu rõ.

### 1.2 Câu hỏi nghiên cứu

RQ1 xem xét số ứng viên sau ngưỡng phản ánh chi phí NMS đến đâu và miếng dán có làm tăng chi phí hoặc suy giảm dịch vụ so với ảnh sạch hay không. RQ2 kiểm tra liệu chọn vị trí bằng phương sai Laplacian có cải thiện SG-GA so với GA tâm, GA vị trí ngẫu nhiên và tìm kiếm ngẫu nhiên dưới cùng ngân sách truy vấn. RQ3 đánh giá mức phụ thuộc vào ảnh, ngưỡng, diện tích và biến đổi phần mềm, đồng thời xem xét khả năng chuyển giao giữa mô hình.

Thực nghiệm detector quy mô lớn bổ sung một mục tiêu triển khai: lựa chọn mô hình theo chất lượng phát hiện người, ngân sách fine-tuning và latency. Mục tiêu này hỗ trợ thiết kế phép thử tính sẵn sàng tiếp theo; nó không thay ba câu hỏi về Sponge Patch và không được coi là thí nghiệm sạch–tấn công trên YOLO11, YOLOv12 hoặc YOLOv13.

### 1.3 Đóng góp và phạm vi khẳng định

Nghiên cứu có ba đóng góp ở mức quy trình và bằng chứng. Thứ nhất, mô tả một giao diện tối ưu hộp xám với miếng dán cục bộ, ngân sách tính theo lượt ảnh và đánh giá độc lập sau tối ưu. Thứ hai, đo tách fitness, ứng viên, hậu xử lý, AP và chất lượng dịch vụ, giữ nguyên các kết quả âm khi giả thuyết ưu thế SG-GA không được hỗ trợ. Thứ ba, bổ sung benchmark detector theo thời gian huấn luyện để phân tích đánh đổi độ chính xác–độ trễ trong cấu hình đã chạy.

Đây không phải đề xuất kiến trúc YOLO mới hoặc tuyên bố một tấn công mạnh hơn các phương pháp đã công bố. Điểm khác biệt của đường nghiên cứu phải được đánh giá bằng cả lợi ích và chi phí: không dùng gradient nhưng cần telemetry trước NMS; diện tích nhỏ nhưng hiệu ứng chưa mạnh; dữ liệu truy vết được nhưng phạm vi phần cứng và vật lý còn hạn chế. Các nhận định về lựa chọn triển khai chỉ áp dụng cho mô hình, dữ liệu và giao thức tương ứng.

## 2 Nghiên cứu liên quan trong hai năm gần đây

### 2.1 Tấn công và phòng thủ đối với tính sẵn sàng

Underload nhấn mạnh mối liên hệ giữa hành vi đối kháng và năng lực phần cứng, đồng thời sử dụng huấn luyện đối kháng có chú ý nền để cân bằng hiệu năng sạch và khả năng xử lý thời gian thực [C:underload2025]. Hướng này trực tiếp bảo vệ dịch vụ nhưng đòi hỏi truy cập và cập nhật mô hình. EVADE tập trung vào kiểm tra tính thực dụng dưới nhiều thiết bị và định dạng thay vì chỉ tối ưu một đại lượng đại diện [C:evade2025]. Bài này tiếp nhận yêu cầu đo thực thi của hướng đánh giá đó; chưa chứng minh một cơ chế phòng thủ tương đương Underload.

Tấn công bit-flip làm tăng độ trễ detector có mô hình đe dọa khác: can thiệp tham số qua lỗi bit, thay vì giữ trọng số cố định và chỉ sửa đầu vào [C:bitflip2025]. TrackFlood khảo sát việc chuyển bề mặt tấn công từ detector không NMS sang tracker [C:trackflood2026]. Event Burst Trigger xem xét backdoor tính sẵn sàng trên detector dùng mạng nơ-ron xung [C:ebt2026]. Hai tài liệu sau được trích theo bản arXiv; không dùng trạng thái công bố chưa xác minh để coi chúng là bằng chứng đã được tái lập. Các hướng này cho thấy loại bỏ NMS khỏi detector không đồng nghĩa loại bỏ mọi chi phí phụ thuộc nội dung của hệ thống hoàn chỉnh.

### 2.2 Đánh giá và phòng thủ miếng dán

Benchmark APDE đặt trọng tâm vào đánh giá nhất quán giữa nhiều tấn công, detector và chỉ số; kết quả cho thấy phát hiện được patch không tự đồng nghĩa phục hồi vật thể bị tấn công [C:apde2025]. PBCAT kết hợp miếng dán cục bộ với nhiễu toàn ảnh trong huấn luyện đối kháng để mở rộng phạm vi phòng thủ đối với các tấn công vật lý [C:pbcat2025]. ODDR, DiffPAD và một hướng detector patch có khả năng giải thích khảo sát các cơ chế tiền xử lý hoặc nhận diện vùng nhiễu khác nhau [C:oddr2025] [C:diffpad2025] [C:advpatchxai2025]. Vì thêm công đoạn có thể làm tăng độ trễ hoặc xóa thông tin hữu ích, đánh giá phòng thủ trong bài này giữ cả AP/AR lẫn chi phí hậu xử lý.

AntiStyler và TRACE tiếp tục khảo sát phòng thủ detector trước miếng dán và cách fine-tuning đối kháng nhằm giảm ảnh hưởng của yếu tố gây nhiễu [C:antistyler2026] [C:trace2026]. Những công trình này là đối chiếu quan trọng cho một bước phòng thủ thực sự, nhưng benchmark fine-tuning detector thông thường trong nghiên cứu hiện tại chưa được xem là huấn luyện đối kháng. Không chuyển metric phát hiện người của nhánh GPU thành metric robust accuracy dưới Sponge Patch.

### 2.3 Tối ưu vị trí và tính hợp lệ vật lý

IAP kết hợp định vị nhận biết khả năng bị nhìn thấy với tối ưu nhiễu để tạo miếng dán khó nhận biết [C:iap2025]. Một hướng nghiên cứu khác xem xét hình dạng phổ quát của patch đặt từ xa đối với detector CNN [C:remoteshape2025]. Các cách tối ưu vị trí/hình dạng này là cơ sở đối chiếu cho heuristic Laplacian: heuristic của nhóm có chi phí đơn giản và không cần gradient, nhưng không phải mô hình hóa đầy đủ độ nhạy của detector hoặc khả năng quan sát vật lý.

BadPatch sử dụng mô hình khuếch tán để tạo miếng dán vật lý và cung cấp bối cảnh dữ liệu áo đối kháng [C:badpatch2025]. GRAC và hướng tạo camouflage đa góc nhìn bằng 3D Gaussian Splatting chú ý tới sự khác nhau giữa góc nhìn, ánh sáng và quy trình dựng hình [C:grac2025] [C:3dgs2025]. Những yếu tố đó vượt ra ngoài phân phối xoay, màu, mờ và nhiễu ảnh mà Sponge Patch hiện dùng. NORP và quần áo đối kháng nhiệt–thị giác mở rộng sang cảm biến đa phương thức [C:norp2026] [C:thermalcloth2026]; nghiên cứu hiện tại chỉ dùng ảnh RGB, không suy rộng kết quả sang cảm biến nhiệt.

### 2.4 Kiến trúc detector và lựa chọn mô hình

YOLOv12 tổ chức detector theo hướng chú ý để cân bằng biểu diễn và tốc độ, trong khi YOLOv13 dùng HyperACE và FullPAD để tăng tương tác đặc trưng giữa vị trí và thang đo [C:yolo12_2025] [C:yolo13_2025]. AFOG khảo sát nhiễu chú ý đối với detector Transformer, cho thấy cơ chế chú ý không tự tạo ra tính an toàn trước đầu vào đối kháng [C:afog2025]. Vì vậy, giảm FLOPs hoặc tăng AP trên benchmark chuẩn không thay thế việc đo latency và kiểm tra tính sẵn sàng trong đường ống cụ thể.

Các số liệu COCO công bố của YOLOv13 và số đo person một lớp của nhóm được đặt cạnh nhau ở phần thực nghiệm bổ sung. Mục đích là nhìn rõ thay đổi thứ hạng và điều kiện, không đánh giá ưu thế bằng cách lấy hai metric khác giao thức trừ nhau. Bài này sử dụng kiến trúc có sẵn; đóng góp ở nhánh detector là tổ chức và phân tích thực nghiệm theo ngân sách, không phải phát minh HyperACE hay FullPAD.

## 3 Phương pháp Sponge Patch

### 3.1 Mô hình đe dọa và quyền truy cập

Thuật toán tối ưu có thể gửi ảnh đã chèn miếng dán vào một giao diện nghiên cứu và nhận vector điểm tin cậy trước NMS. Nó không dùng trọng số hoặc gradient để cập nhật miếng dán, không sửa NMS và không can thiệp mô hình. Trong thực nghiệm, mô hình được nạp cục bộ để mô phỏng giao diện phản hồi này; chương trình không thực thi một ranh giới kiểm soát truy cập độc lập giữa bên tối ưu và detector.

Khả năng đọc điểm trước NMS có thể phù hợp một dịch vụ có telemetry hoặc giao diện gỡ lỗi, nhưng chưa được xác nhận trên một sản phẩm camera thương mại. Vì vậy, tên hộp xám phản ánh quyền truy cập đã quy định, không phải khẳng định tấn công có thể triển khai trên mọi API hộp đen. Can thiệp của bài là ghi đè một vùng tensor/ảnh trong testbed; không phải chiếm quyền camera hoặc truyền dữ liệu vào một hệ thống sản xuất.

### 3.2 Đại lượng đo và mục tiêu

Gọi x là ảnh sạch, p là miếng dán và l là vị trí. Toán tử A(x,p,l) ghi đè vùng RGB tương ứng, giữ phần còn lại của ảnh. Mô hình sinh K vị trí dự đoán; tại mỗi vị trí i, cᵢ là điểm lớp lớn nhất. Sau ngưỡng τ, Nτ đếm ứng viên hoạt động. Nếu áp top-k trước NMS, số đầu vào thực là min(Nτ,k). Số phát hiện cuối D được tính sau NMS và giới hạn đầu ra, không thay thế Nτ.

[[EQ:1|Nτ(x) = Σᵢ 1[cᵢ(x) > τ] ; Nₙₘₛ = min(Nτ, k) khi áp giới hạn k]]

Fitness trong triển khai được tối đa hóa bằng tổng confidence của ứng viên hoạt động cộng phần thưởng số ứng viên. Tham số λ = 1,5 và τ tối ưu bằng 0,01. Công thức tuyến tính này khác mục tiêu độ trễ trực tiếp; điểm cao có thể xuất phát từ nhiều ứng viên nhưng chưa bảo đảm các hộp đó tạo công việc NMS lớn.

[[EQ:2|F(x) = Σᵢ cᵢ(x) · 1[cᵢ(x) > 0,01] + 1,5 N₀,₀₁(x)]]

Trong mô hình so sánh mọi cặp, số cặp tiềm năng là N(N−1)/2. Từ 50 đến 3.000 hộp, số cặp tăng từ 1.225 đến 4.498.500, khoảng 3.672,24 lần. Đây là tính toán tổ hợp, không phải số thao tác đo trên backend hoặc tỷ số latency. Loại bỏ sớm, vector hóa, lọc lớp và top-k làm đường cong thời gian thực khác mô hình mọi cặp.

### 3.3 Chọn vị trí và thuật toán di truyền

Ảnh được chuyển sang mức xám và quét cửa sổ có kích thước bằng miếng dán. SG-GA chọn cửa sổ có phương sai đáp ứng Laplacian lớn nhất; GA tâm giữ vị trí trung tâm; GA vị trí ngẫu nhiên giữ một vị trí được lấy mẫu theo seed. Nội dung miếng dán được tối ưu sau khi chọn chính sách vị trí. Heuristic Laplacian đo cấu trúc ảnh, không đo gradient detector và không chứng minh vị trí đó nhạy nhất với mục tiêu hệ thống.

Mỗi cá thể là tensor RGB trong [0;1]. Lượt mở rộng giữ quần thể 20, năm cá thể ưu tú, lai ghép ngang, xác suất đột biến 0,1 và nhiễu Gaussian có độ lệch chuẩn 0,2 rồi chặn về [0;1]. Một cá thể được đánh giá trên bốn ảnh tối ưu. Khi dùng một mẫu biến đổi cho mỗi ảnh, một đánh giá tiêu tốn bốn lượt ảnh qua mô hình; bốn mẫu tiêu tốn 16 lượt. Cấu hình này khác nhiễu đều của phiên kiểm chứng cũ, nên các lượt không được gộp thành một giao thức.

[[TABLE:algorithm]]

Ngân sách được tính theo lượt suy luận ảnh, không theo số lời gọi batch hoặc số thế hệ. Miếng dán được chọn chỉ bằng fitness trên tập tối ưu; không chọn lại bằng AP, tỷ số ứng viên hay độ trễ của tập kiểm tra. Cực đại fitness đã quan sát dưới biến đổi ngẫu nhiên là một thống kê lựa chọn, không phải ước lượng độc lập của kỳ vọng fitness.

### 3.4 Biến đổi phần mềm và đánh giá độc lập

Expectation over Transformation (EOT) được dùng theo nghĩa tối ưu dưới biến đổi phần mềm. Ảnh sau chèn chịu xoay trong biên ±15° với xác suất 0,8, jitter độ sáng/tương phản 0,2 với xác suất 0,8, mờ Gaussian 3 × 3 với xác suất 0,5 và nhiễu Gaussian độ lệch chuẩn 0,02. Biến đổi tác động lên toàn ảnh, không mô phỏng đầy đủ in ấn, phối cảnh, bề mặt áo hoặc chuỗi camera vật lý.

Đánh giá ảnh gốc giữ miếng dán cố định và tắt EOT. Một phép đo độc lập khác dùng tám ảnh kiểm tra, 16 mẫu EOT mới trên mỗi ảnh; tham số biến đổi và nhiễu được ghép giữa sạch và có miếng dán. Các mẫu mới không được dùng để cập nhật miếng dán. Phân biệt này ngăn việc dùng điểm tối ưu đã được chọn như bằng chứng về độ bền ngoài mẫu.

## 4 Thiết kế thực nghiệm và thống kê

### 4.1 Hai nhánh bằng chứng

Nhánh A kiểm tra Sponge/NMS trên CPU laptop Intel Core i5-1335U với YOLOv8n và ảnh 320 × 320. Nhánh B lựa chọn detector trên GPU RTX 5060, ảnh 416 px và target person. Hai nhánh dùng dữ liệu, số lớp, mục tiêu và ranh giới thời gian khác nhau; không gộp AP hoặc latency để tạo một hiệu ứng chung. Laptop CPU cũng không được đổi nhãn thành Raspberry Pi hoặc máy chủ biên cũ.

[[TABLE:protocols]]

### 4.2 Tập ảnh và đối chứng của nhánh A

Bốn ảnh COCO128 được chọn trước để tối ưu; tập kiểm tra gồm 500 ID nhỏ nhất của COCO val2017, không trùng ID với COCO128. Tập kiểm tra có ~2.500 annotations và danh mục 80 lớp, giữ metadata crowd/ignore gốc. Tách ID bảo đảm các ảnh này không được dùng để tối ưu patch; chưa xác định lịch sử lựa chọn trọng số pretrained của nhà phát hành, nên không khẳng định hoàn toàn độc lập với pretraining.

Bốn nhánh tìm kiếm chính dùng cùng diện tích 4%, cùng objective và các ngân sách 400, 1.000 và 2.500 lượt ảnh; mỗi cấu hình có 10 seed, không dừng sớm. Các cấu hình diện tích, thành phần EOT, objective giới hạn top-100 và gradient tanh bổ sung tạo tổng 16 cấu hình tối ưu, 160 lượt và 240 checkpoint. Bộ đánh giá hoàn tất 250 ca gồm checkpoint và đối chứng sạch. Mốc 1.000 dùng 32 ảnh, còn 400/2.500 dùng 500 — đây là tập held-out 500 ID nhỏ nhất của COCO val2017, không trùng với bộ tối ưu.

### 4.3 AP và ranh giới thời gian

Nhánh A sử dụng COCOeval bbox, IoU 0,50–0,95, ánh xạ lớp về ID COCO gốc và maxDets 1/10/100. Dự đoán được đưa từ ảnh co vuông về kích thước nguồn, cắt theo biên. Đây là kết quả evaluator COCO trên tập con 500 ảnh, không phải toàn bộ 5.000 ảnh val2017. AP được tính gộp ảnh trong từng seed trước khi lấy trung bình giữa seed.

Hậu xử lý chính có IoU NMS 0,45, NMS không phân biệt lớp và tối đa 300 phát hiện đầu ra. Top-k cắt ứng viên trước NMS khác giới hạn phát hiện sau NMS hoặc giới hạn maxDets của evaluator. Mỗi ảnh có khởi động và ba lượt đo suy luận; lọc/NMS được đo riêng trên dự đoán đã lưu. Không cộng hai trung vị thành độ trễ toàn trình. Phép đo xử lý tensor chung ở backend gồm suy luận, giải mã đầu ra, lọc và NMS; đọc ảnh, chèn patch và camera nằm ngoài ranh giới này.

### 4.4 Giả thuyết và đơn vị suy luận

So sánh chính kiểm tra SG-GA trừ GA tâm về tỷ số ứng viên tại 2.500 lượt ảnh, ngưỡng 0,01 và không cap. Với seed s, tỷ số là trung bình các tỷ số theo cùng ảnh; mẫu số sạch được chặn tối thiểu bằng 1 theo giao thức. Không có ảnh mẫu số bằng 0 trong endpoint chính. Ngưỡng cải thiện thực tiễn đặt trước là +0,10 đơn vị tỷ số.

**Kết quả chính (500 ảnh, 10 seeds):**
- Mean diff (SG-GA − GA-center) = **−0,0293**
- 95% CI (paired bootstrap) = **[−0,0383, −0,0216]**
- Exact sign-flip p = **0,0020**
- Cohen's dz = **−2,05**
- Hypothesis: SG-GA superior? → **False**
- Availability failure? → **True** (không xác lập được)

SG-GA thua GA-center có ý nghĩa thống kê (p = 0,002). Whitebox tanh đạt ratio 1,1987 — lớn hơn SG-GA — cho thấy nguyên nhân nằm ở fitness function, không phải kiến trúc GA.

[[EQ:3|Rₛ = (1/n) Σⱼ Nτ(A(xⱼ,pₛ,lⱼ)) / max(1, Nτ(xⱼ)) ; Δₛ = Rₛᴿᴳ − Rₛᶜᵉⁿᵗᵉʳ]]

Phân tích dùng cặp seed, 20.000 bootstrap resamples và kiểm định đảo dấu hai phía trên 2¹⁰ = 1.024 cấu hình. Khoảng tin cậy điều kiện trên bộ ảnh/mô hình/phần cứng cố định; 128 ảnh hay số lần đo lặp không làm n seed lớn hơn 10. Kiểm định phụ thuộc giả định đối xứng dấu của chênh lệch dưới giả thuyết không, không phải ngẫu nhiên hóa phương pháp trên ảnh. Giao thức đã lưu cục bộ trước đánh giá, chưa đăng ký ở cơ sở đăng ký công khai. Nhóm 15 phép so sánh thứ cấp dùng Holm; những phân tích bổ sung được ghi rõ là thăm dò.

### 4.5 Luồng phần mềm và tiêu chí dịch vụ

Luồng phần mềm dùng một bộ phát ảnh theo lịch và một worker suy luận thực. Có 240 lượt: 10 seed, hai chu kỳ 100/300 ms, bốn điều kiện và ba chính sách FIFO, bỏ khi bận, điều tiết thích nghi. Mỗi lượt phát 32 ảnh theo thứ tự ghép cặp trong seed, thời hạn 300 ms tính từ mốc phát theo lịch. Đây là thực thi đồng thời có timestamp đơn điệu, khác mô hình hàng đợi ngoại tuyến dựng từ service time, nhưng chưa gồm camera.

Chính sách thích nghi chỉ dùng thời gian xử lý đã hoàn tất, cập nhật trung bình trượt mũ với hệ số 0,25 và đặt khoảng nhận không nhỏ hơn chu kỳ phát hoặc 1,2 lần thời gian ước lượng, tối đa 600 ms. Tỷ lệ thiếu/trễ tính trên toàn bộ ảnh đã phát; AP toàn luồng xem ảnh bị bỏ là dự đoán rỗng, AP đúng hạn xem cả ảnh bị bỏ và trễ là rỗng. Nhờ đó, bỏ ảnh không được che dưới một tỷ lệ trễ thấp chỉ tính trên phần còn xử lý.

Tiêu chí suy giảm đánh dấu throughput đúng hạn dưới 80% tốc độ phát hoặc tỷ lệ thiếu/trễ trên 10%; tiêu chí phục hồi còn yêu cầu AP đúng hạn không thấp hơn sạch FIFO ghép cặp quá hai điểm phần trăm. Một điều kiện không đạt tiêu chí chưa xác định nguyên nhân do tấn công: cần so với ảnh sạch ở cùng tải. Các kiểm định chính sách là thăm dò, chưa hiệu chỉnh nhóm 48 phép so sánh đã lưu.

## 5 Kết quả kiểm chứng Sponge Patch

### 5.1 Tối ưu cùng ngân sách và vai trò của vị trí

Tại 2.500 lượt ảnh, SG-GA tạo tỷ số ứng viên trung bình 1,0278; GA tâm 1,0329; GA vị trí ngẫu nhiên 1,0519; tìm kiếm ngẫu nhiên 1,0268. Bảng 3 và Hình 1 trình bày mức tăng nhỏ này trên cùng thang. Chênh lệch SG-GA trừ GA tâm là −0,005132, CI 95% [−0,011178; 0,000706], p = 0,150391. Khoảng không hỗ trợ mức ưu thế +0,10; việc chứa 0 cũng không chứng minh tương đương hai phương pháp.

[[TABLE:sponge_primary]]

[[FIG:01_ty_so_ung_vien.png|Tỷ số ứng viên tại 2.500 lượt ảnh, ngưỡng 0,01 và không cap. Bốn phương pháp dùng 128 ảnh, diện tích 4% và 10 seed. Thanh sai số là bootstrap 95% theo seed, điều kiện trên bộ ảnh cố định; đường 1 là ảnh sạch. Đây không phải tỷ số latency.]]

AP hộp giảm từ 34,08% xuống 29,97% với SG-GA và 25,88% với GA tâm. Điều này xác nhận tác động lên chất lượng dự đoán trong phép thử, chưa xác nhận DoS. Tỷ số trung bình theo ảnh có thể tăng nhẹ dù số ứng viên tuyệt đối trung bình của SG-GA giảm từ 133,29 xuống 131,05; hai phép tổng hợp không đồng nhất và không được chỉnh số để ép cùng chiều.

So sánh thứ cấp SG-GA trừ GA vị trí ngẫu nhiên có mean −0,0241, CI [−0,0315; −0,0163], p Holm = 0,0293. So với tìm kiếm ngẫu nhiên, mean 0,0010, CI [−0,0050; 0,0073], p Holm = 1. Kết quả chưa cho thấy heuristic Laplacian tạo ưu thế ứng viên. Nó không loại trừ các cách định vị khác tốt hơn và cũng không chứng minh thứ hạng latency luôn theo thứ hạng ứng viên.

### 5.2 Ngân sách và độ khái quát

Trên cùng 32 ID ảnh, tỷ số SG-GA ở 400/1.000/2.500 lần lượt là 1,0004, 1,0057 và 0,9954. Tăng ngân sách tìm kiếm không tạo hiệu ứng tăng đơn điệu trên tập kiểm tra. Hình 2 dùng đúng cohort chung để tránh so mức 1.000 trên 32 ảnh với các mức còn lại trên 128. Các đường nối mô tả mốc đã đo, không nội suy kết quả ở ngân sách khác.

[[FIG:02_ngan_sach_truy_van.png|Tỷ số ứng viên theo ngân sách trên đúng 32 ID kiểm tra chung, 10 seed mỗi phương pháp. Vùng mờ là bootstrap 95% theo seed. Không dùng đồ thị này để so AP giữa các tập 32 và 128 ảnh hoặc suy ra thời gian hội tụ.]]

### 5.3 Diện tích và EOT

Diện tích thật của patch 32/45/64/90/128 trên ảnh 320 × 320 lần lượt là 1,00/1,98/4,00/7,91/16,00%. Tại cùng 400 lượt ảnh, tỷ số ứng viên tăng tới mức 4% rồi giảm; mức 16% có AP thấp nhất nhưng ứng viên ít hơn sạch theo định nghĩa tỷ số. Hậu xử lý cũng không tăng đơn điệu. Vì diện tích đổi cả vùng che và số chiều tìm kiếm, không quy mọi khác biệt cho diện tích riêng lẻ.

[[TABLE:area]]

[[FIG:13_dien_tich_kiem_chung.png|Đánh giá diện tích trên 128 ảnh, 10 seed và 400 lượt ảnh qua mô hình. Mức 4% dùng checkpoint SG-GA cơ sở. Các khoảng là bootstrap theo seed; giảm AP không được diễn giải tự động thành tăng tải NMS.]]

Loại bỏ EOT giữ cùng diện tích và ngân sách. Với bốn mẫu biến đổi cho mỗi ảnh, số cá thể được đánh giá chỉ bằng một phần tư cấu hình một mẫu; phép thử đo một đánh đổi phân bổ ngân sách. Các tỷ số ứng viên trên ảnh gốc gần nhau và chưa hỗ trợ ưu thế EOT đầy đủ sau Holm. Trong kiểm tra EOT mới, chênh lệch fitness patch trừ sạch của bảy cấu hình đều âm ở mức trung bình; cấu hình đầy đủ tại 400 đạt −20,13 ± 1,41. Đây là endpoint fitness trên tám ảnh, không phải AP dưới biến đổi hay độ bền vật lý.

[[FIG:04_loai_bo_eot.png|Bảy cấu hình EOT dùng cùng 400 lượt ảnh. Bên trái đo ứng viên trên ảnh gốc; bên phải đo chênh lệch fitness dưới 16 mẫu biến đổi mới trên mỗi ảnh của tám ảnh kiểm tra. Bốn mẫu EOT có ít cá thể tìm kiếm hơn; thanh sai số là bootstrap theo seed.]]

### 5.4 Chi phí xử lý và backend NMS

Trên 16 ảnh, năm điều kiện, ba cấu hình 1/2/4 luồng CPU và ba lần đo mỗi ảnh, tổng 7.200 số đo tensor đã chuẩn bị không vượt ngân sách 300 ms. Với một luồng, trung vị block sạch trung bình là 51,09 ms, SG-GA 52,87 ms; mean p95 lần lượt 78,20 và 82,69 ms. Ở hai/bốn luồng, median và tail không tăng nhất quán theo patch. Thay số luồng vẫn là một máy vật lý và không mô phỏng được một thiết bị edge khác.

[[TABLE:processing]]

[[FIG:07_ngan_sach_xu_ly.png|Tỷ lệ lượt xử lý vượt ngân sách 300 ms theo số luồng CPU, bằng 0% ở cả năm điều kiện. Đồng hồ gồm suy luận, giải mã, lọc và NMS trên tensor đã chuẩn bị; 10 block seed, 16 ảnh và ba lượt đo mỗi ảnh. Không gồm thu hình hoặc hàng đợi. Bảng 5 cung cấp median và p95 tương ứng.]]

Trên tensor dự đoán cố định, ở ngưỡng 0,01 không cap, thời gian NMS sạch là 1,520 ± 0,364 ms với mã thuần PyTorch và 0,060 ± 0,011 ms với torchvision; SG-GA lần lượt 1,691 ± 0,129 và 0,062 ± 0,011 ms. Các output trùng trong những trường hợp đã kiểm tra. Chênh lệch cho thấy backend là một yếu tố thực nghiệm quan trọng; không chuyển hệ số thời gian từ mã Python/PyTorch sang backend tối ưu. Khớp output trên tensor cố định cũng không bảo đảm luôn khớp tại tie hoặc sát ngưỡng IoU.

### 5.5 Dịch vụ dưới luồng đầu vào

Ở chu kỳ 100 ms, FIFO sạch đã thiếu/trễ 85,31% ảnh; SG-GA 2.500 có 85,00%. So sánh này không cho phép quy quá tải cho patch vì baseline đã vượt năng lực xử lý theo giao thức. Bỏ khi bận giảm chờ nhưng làm mất xấp xỉ một nửa đầu vào, còn điều tiết thích nghi vẫn chưa đạt đồng thời tiêu chí throughput và AP.

Ở chu kỳ 300 ms, FIFO sạch và các patch đều hoàn thành đúng hạn, throughput 3,33 ảnh/s. Tuy vậy AP đúng hạn của patch thấp hơn sạch, cho thấy suy giảm toàn vẹn có thể tồn tại khi thời hạn dịch vụ vẫn được đáp ứng. Nhánh thích nghi bỏ 35,63% đầu vào ngay trên sạch ở chu kỳ này, dù FIFO đáp ứng; quy tắc khoảng nhận nhạy với dao động mốc đến. Không mô tả nó là một phòng thủ thành công chỉ vì worker ít bận hơn.

[[TABLE:stream]]

### 5.6 Đánh đổi phòng thủ và đối chứng mạnh hơn

Giới hạn top-100 giảm công việc hậu xử lý nhưng cũng giảm AP và AR100. Trên sạch, AP từ 34,08% xuống 33,36%, AR100 từ 40,79% xuống 38,91%; thời gian lọc/NMS từ 3,40 xuống 2,05 ms. Tăng ngưỡng lên 0,25 giảm chi phí hơn nhưng AP còn 28,54%. Các giá trị của SG-GA có xu hướng đánh đổi tương tự; đây là thay cấu hình hậu xử lý, không phải một bảo đảm phòng thủ phổ quát.

[[TABLE:defense]]

[[FIG:06_danh_doi_phong_thu.png|Đánh đổi hậu xử lý và độ chính xác trên tập con val2017 có nhãn. AP tính gộp ảnh trước khi trung bình theo seed; đồ thị mô tả trung bình, không có thanh sai số. Nhánh thích nghi chỉ so trực tiếp với SG-GA cùng 400 lượt ảnh.]]

Đối chứng gradient tanh cùng diện tích và 400 lượt ảnh có tỷ số ứng viên 1,1552, cao hơn SG-GA 1,0303; AP là 28,62% so với 30,17%. Vì đối chứng đọc gradient, quyền truy cập mạnh hơn, nó cho thấy một đánh đổi chứ không phải so cùng threat model. Biến thể mục tiêu Phantom cục bộ giữ mô hình, diện tích, ảnh tối ưu và 400 lượt suy luận nhưng dùng gradient; tỷ số 1,0286 gần SG-GA. Chênh lệch −0,0016 với CI [−0,0054; 0,0019] chưa chứng minh tương đương. Các biến thể này không tái lập toàn bộ thí nghiệm nguyên bản.

### 5.7 Chuyển giao và phạm vi vật lý

Phép chuyển giao giữ 16 ảnh và 10 miếng dán nguồn, đo cặp sạch–patch bên trong từng mô hình. Tỷ số latency trung bình gần 1 ở phần lớn detector; Faster R-CNN đạt 1,0419, CI [1,0274; 1,0554]. AP giảm trong các mô hình được đánh giá nhưng chưa có bằng chứng DoS xuyên kiến trúc. DETR không có NMS; chi phí khác phải được xem trong đường ống thực, không suy ra bất khả xâm phạm từ đặc điểm này.

[[TABLE:transfer]]

[[FIG:05_chuyen_giao.png|Chuyển giao trên cùng 16 ảnh và 10 miếng dán nguồn. So sánh tỷ số độ trễ ghép cặp bên trong từng mô hình, có normalization/hậu xử lý riêng; không xếp hạng latency tuyệt đối giữa kiến trúc. DETR không có NMS.]]

### 4.6 Khám phá chuyển giao qua tám kiến trúc (X2)

Để trả lời RQ3 về khả năng chuyển giao, cùng mười miếng dán SG-GA đã tối ưu được đặt lên tám kiến trúc phát hiện khác nhau: YOLOv8n/s, YOLO11n/s, YOLOv12n, SSDlite, Faster R-CNN (MobileNet-V3), RetinaNet và RT-DETR (đối chứng không NMS). Mỗi kiến trúc đo tỷ số ứng viên active tại ngưỡng 0,01 trên 64–100 ảnh held-out.

**Bảng 2. Tỷ số ứng viên theo kiến trúc (X2).**

| Detector | Nhóm | Boundary | Ratio | Ảnh |
|---|---|---|---:|---:|
| YOLOv8n | NMS single-stage | pre-NMS | 1,034 | 100 |
| YOLOv8s | NMS single-stage | pre-NMS | 1,026 | 100 |
| YOLO11n | NMS single-stage | pre-NMS | 1,026 | 100 |
| YOLO11s | NMS single-stage | pre-NMS | 1,022 | 64 |
| YOLOv12n | NMS single-stage | pre-NMS | 1,036 | 64 |
| SSDlite | NMS single-stage | post-module | 1,034 | 64 |
| Faster R-CNN | NMS two-stage | post-module | 1,111 | 64 |
| RetinaNet | NMS single-stage | post-module | 1,236 | 64 |

Tất cả NMS-based detectors có tỷ số đồng nhất 1,02–1,24. Không detector nào cho thấy bùng nổ ứng viên. Faster R-CNN (1,11) và RetinaNet (1,24) cao nhất nhưng vẫn khiêm tốn. Kết luận: hiệu ứng Sponge Patch không phụ thuộc mạnh vào kiến trúc NMS-specific.

### 4.7 Mô phỏng QoS container (X5 v2)

X5 v2 đo thời gian phục vụ trực tiếp (không replay từ cache X1) để tránh sai lệch CPU warmup giữa clean và patched. Ba điều kiện: clean, sg_ga (seed 0–4), tanh whitebox (seed 0–4). NămThirty hai ảnh COCO val2017 được dùng để đo median forward latency cho mỗi condition-seed.

**Bảng 3. Deadline miss rate (%) dưới container profile (32 ảnh, 5 seeds, 500 frame @ 10 fps).**

| Threads | Condition | dl=100ms | dl=200ms | dl=300ms | svc_median |
|---:|---|---:|---:|---:|---:|
| 1 | clean | 100,0% | 100,0% | 100,0% | 220 ms |
| 1 | sg_ga | 100,0% | 100,0% | 100,0% | 230 ms |
| 1 | tanh | 3,2% | 0,0% | 0,0% | 70 ms |
| 2 | clean | 100,0% | 99,8% | 98,8% | 220 ms |
| 2 | sg_ga | 100,0% | 100,0% | 99,8% | 230 ms |
| 2 | tanh | 3,2% | 0,0% | 0,0% | 70 ms |
| 4 | clean | 100,0% | 75,2% | 21,4% | 220 ms |
| 4 | sg_ga | 100,0% | 84,8% | 9,6% | 230 ms |
| 4 | tanh | 3,2% | 0,0% | 0,0% | 70 ms |

Thời gian phục vụ clean trung vị 220 ms đã vượt deadline 100 ms ở mọi thread count. SG-GA thêm ~10 ms (220→230 ms) — không đáng kể. **Whitebox tanh thậm chí nhanh hơn** (70 ms) — ngược chiều kỳ vọng DoS (tấn công phải làm chậm, không làm nhanh). Kết luận: không có bằng chứng suy giảm dịch vụ do SG-GA trong điều kiện thử nghiệm.

## 6 Thực nghiệm bổ sung về lựa chọn detector

### 6.1 Mục tiêu và dữ liệu

Nhánh GPU phục vụ lựa chọn một detector ứng viên cho nghiên cứu hệ thống tiếp theo. Target là người, không phải patch. Dữ liệu hợp nhất gồm 8.000 ảnh COCO có hộp người không crowd, 2.000 ảnh không có chú thích người và 1.123 ảnh từ bản mirror AdvT-shirt. Ảnh crowd-only không được xếp vào hai nhóm COCO. Nhãn patch ở nguồn AdvT-shirt được giữ riêng, không đưa vào target person. Bản mirror ít hơn tám ảnh so với 1.131 ảnh được mô tả ở nguồn dữ liệu [C:badpatch2025].

Split seed 2026 tạo 7.786 train, 1.669 validation và 1.668 test. Audit trên máy thực nghiệm ghi không trùng byte ảnh hoặc COCO ID giữa split; điều đó chưa loại được cùng người/video hoặc ảnh gần giống. Có 1.429 ảnh test bắt nguồn COCO train2017, có thể từng được dùng ở pretraining. Vì vậy, holdout được hiểu là độc lập với fine-tuning, không khẳng định độc lập với mọi lịch sử học của checkpoint.

### 6.2 Huấn luyện và chọn checkpoint

Bốn mô hình YOLO11n, YOLOv12n, YOLOv13n và YOLOv13s bắt đầu từ pretrained tương ứng. Mỗi mô hình dùng năm seed 42, 100, 2026, 777 và 999; ảnh 416 px, batch 8, SGD với lr0 0,01, lrf 0,01, momentum 0,937, weight decay 0,0005, AMP, workers 0 và augmentation chung. Các fork YOLOv12/YOLOv13 dùng SDPA khi FlashAttention không có trong môi trường. Không thay thời gian của backend này bằng số công bố trên backend khác.

Mỗi quỹ đạo chạy đến ranh giới epoch vượt cap 120 phút. Lịch sử CSV ghi tổng 40,54 giờ huấn luyện; thời lượng mỗi lượt 120,20–123,28 phút, vượt cap do epoch. Các epoch có timestamp CSV vượt mốc không được chọn vào mốc đó. Với fork YOLOv12 được kiểm tra, timestamp metric được ghi trước khi save checkpoint của chính epoch hoàn tất; vì chưa có save-end timestamp, định nghĩa ngân sách trong bài là timestamp CSV, không cam kết checkpoint đã lưu xong trước deadline từng mốc.

Tại mỗi ngân sách, checkpoint có validation mAP95 tốt nhất trong các epoch hợp lệ được chọn. Sweet spot là mốc sớm nhất có đủ năm seed và mean validation mAP95 cách peak trong cửa sổ quan sát không quá 0,5 điểm phần trăm. Có một mốc 5 phút của YOLOv13s seed 2026 chưa có epoch hoàn tất, nên mốc đó chỉ có n = 4 và không được dùng chọn sweet spot đủ năm seed. Test không dùng để chọn checkpoint hoặc ngân sách.

### 6.3 Kết quả và đánh đổi

YOLOv13s đạt test mAP95 trung bình 47,97%, cao hơn YOLO11n 5,53 điểm phần trăm tại các sweet spot riêng. Tuy nhiên, bản s có quy mô lớn hơn và latency pipeline khoảng 20 lần bản n YOLO11 trong cấu hình đã đo. Không quy mức tăng mAP đó cho ưu thế kiến trúc thuần túy hoặc gọi YOLOv13s tốt nhất mà bỏ qua yêu cầu thời gian. Với các bản n, YOLOv13n thấp hơn YOLO11n 1,65 điểm mAP95 và cao hơn YOLOv12n khoảng 0,31 điểm.

[[TABLE:yolo_metrics]]

Latency đo trên RTX 5060, ảnh 416 px, batch 1, FP32, bỏ 32 ảnh warm-up và lấy median trên 500 ảnh cố định. Mỗi dòng là mean và sample SD của năm per-checkpoint medians; không phải median/SD của tất cả frame gộp. Thời gian gồm preprocessing, forward và postprocessing của Ultralytics, loại đọc/giải mã ảnh và I/O ứng dụng. Tổng median được tính từ tổng các stage trên từng frame, không cộng các stage medians.

Trong fork YOLOv12 đã kiểm tra, default confidence của val và predict khác nhau; giao thức đã lưu chưa ghi đầy đủ resolved conf/iou/rect cho mọi model. Vì vậy, bảng accuracy và latency được hiểu là hai chế độ evaluator/predictor, chưa phải một operating point thống nhất. Cần công bố cấu hình này và đo lại operating point dự kiến trước khi đưa ra cam kết deployment.

### 6.4 Diễn giải mốc sớm và hội tụ

Hình 8 tách best-so-far validation khỏi epoch cuối thực sự hoàn tất. YOLOv13n/s giữ epoch 1 ở sweet spot của cả năm seed. Đường best-so-far phẳng chỉ cho thấy các epoch tiếp theo chưa vượt checkpoint đã có; ở panel epoch cuối, hiệu năng giảm rồi phục hồi. Vì thế, sweet spot 5/10 phút không chứng minh học nhanh ổn định hoặc tiết kiệm huấn luyện trong một quy tắc dừng online.

[[FIG:09_fullscale_mAP_growth.png|Validation mAP95 theo ngân sách của bốn mô hình. Bên trái là checkpoint tốt nhất đã có; bên phải là epoch cuối hoàn tất. Thanh sai số là CI t 95% giữa seed; YOLOv13s tại 5 phút có n = 4. Đây là validation, không phải test AP hoặc xác nhận bão hòa.]]

YOLO11n và YOLOv12n có peak tại biên 120 phút nên chưa xác định trần ngoài cửa sổ. Cần thêm mốc pretrained 0 phút để phân biệt chất lượng khởi tạo với lợi ích fine-tuning. Kiểm tra learning rate, warm-up và lịch augmentation phải dựa trên validation; không chọn siêu tham số bằng test hoặc dùng việc chọn epoch sớm để che sự giảm hiệu năng trong quỹ đạo.

### 6.5 Đối chiếu số công bố và số đo của nhóm

Hình 9 đặt kết quả kiến trúc trong bài YOLOv13 cạnh benchmark của nhóm, với hai panel và giao thức riêng [C:yolo13_2025]. Panel công bố dùng COCO đa lớp và thiết bị/định dạng của bài gốc; panel nhóm dùng person một lớp, checkpoint fine-tuned và RTX 5060 FP32. Cách trình bày giúp quan sát sự thay đổi thứ hạng theo điều kiện, không tạo một tỷ số ưu thế xuyên dataset hoặc suy ra baseline công bố đã được nhóm tái lập.

[[FIG:12_so_sanh_cong_bo_va_thuc_nghiem.png|Đối chiếu mô tả số liệu công bố YOLOv13 với thực nghiệm của nhóm. Hai panel khác dữ liệu, số lớp, checkpoint, phần cứng và precision. mAP trong mỗi panel chỉ được so bên trong giao thức tương ứng; không lấy chênh lệch giữa panel để chứng minh ưu thế. Nguồn công bố, table/page và các scalar thực nghiệm được lưu cùng hình.]]

Việc chọn dữ liệu áo đối kháng và target person có ý nghĩa ở bước lựa chọn detector phục vụ cảnh có người, nhưng chưa đủ để chứng minh đường nghiên cứu tốt hơn nghiên cứu đa lớp COCO. Lợi ích cần kiểm chứng tiếp là khả năng giữ chất lượng phát hiện và deadline khi đưa cùng Sponge Patch vào detector đã chọn. Benchmark hiện tại cung cấp cấu hình và đối chứng để thực hiện bước đó, không thay thế nó.

## 7 Thảo luận về lợi ích và giới hạn của hướng nghiên cứu

### 7.1 So sánh các con đường và bằng chứng cần có

Khác dữ liệu hoặc giao thức chỉ giải thích khả năng đối chiếu, không phải bằng chứng về lợi thế. Bảng 10 so các hướng theo mục tiêu, quyền truy cập, lợi ích và phần chưa được chứng minh. Đối với nhóm, giảm quyền truy cập từ gradient xuống điểm trước NMS là một khác biệt có nghĩa về mô hình đe dọa; nhưng cần chứng minh kênh điểm tồn tại và hiệu quả đạt được đủ lớn. Dữ liệu hiện tại chưa ủng hộ một tuyên bố mạnh hơn về hiệu lực tấn công.

[[TABLE:routes]]

Hình 10 bổ sung các số đo có thể truy nguồn từ bài nền. Underload, Bảng 1 bản v2, báo mAP50 COCO của YOLOv8s gốc là 57,7% trên sạch và 20,1% dưới Overload; sau huấn luyện đối kháng, hai số là 45,7% và 42,0% [C:underload2025]. Lợi ích robust accuracy đi kèm giảm clean accuracy. EVADE, Bảng 3 trang 7, ghi số hộp sau NMS trên YOLOv8n là 6 trên sạch và 247/300/228/151 với bốn tấn công tối ưu cho chính model đó [C:evade2025]. Đây là số hộp đầu ra đã làm tròn, khác ứng viên trước NMS của nhóm và không phải latency.

[[FIG:14_so_sanh_bai_nen_va_sponge.png|Đối chiếu mô tả Underload 2025, EVADE 2025 và Sponge Patch của nhóm. Panel A đo mAP50 với/không huấn luyện đối kháng; B đo số hộp sau NMS; C đo AP50:95 trên 128 ảnh dưới patch hộp xám. Từng panel có trục và giao thức riêng. Thanh sai số C là SD giữa 10 seed patch; bài gốc không cung cấp SD ở các ô đã trích. Không dùng hình để xếp hạng hiệu lực tấn công xuyên giao thức.]]

So sánh cùng mô hình/ảnh/diện tích/ngân sách là cần thiết để tách lợi ích của thuật toán khỏi khả năng truy cập và mức can thiệp. Đối chứng gradient tanh mạnh hơn SG-GA về ứng viên trong phép thử hiện tại, còn GA vị trí ngẫu nhiên cao hơn SG-GA ở endpoint chính. Những kết quả đó phải được giữ trong lập luận. Hướng cải thiện được đặt ra là tìm một proxy phản ánh công việc hậu xử lý tốt hơn, kiểm tra vị trí trên tập validation hoặc phân bổ mẫu biến đổi tốt hơn; không mặc định một thay đổi sẽ thành công trước khi đo.

### 7.2 Tại sao ứng viên không bảo đảm tăng latency

Chi phí NMS còn phụ thuộc phân bố hộp, mức chồng lấp, thứ tự score, implementation và cap. Nhiều hộp bị loại nhanh có thể ít tốn hơn một tập nhỏ khó loại. Fitness thưởng ứng viên và confidence chưa mô hình hóa trực tiếp những yếu tố này. Kết quả ratio tăng nhẹ, AP giảm nhưng QoS chưa suy giảm cho thấy giới hạn của proxy trong cấu hình đã thử, phù hợp yêu cầu đánh giá hệ thống mà các công trình latency gần đây đặt ra [C:underload2025] [C:evade2025].

Một objective latency trực tiếp cũng không tự giải quyết vấn đề: timer chịu tiến trình nền, warm-up và backend. Nếu phát triển objective quan sát latency, cần cùng baseline, randomized paired blocks, số lần đo lặp được tính vào ngân sách và một endpoint kiểm tra độc lập. Chưa thực hiện nhánh đó trong kết quả hiện tại nên bài không báo hiệu lực hoặc cam kết cải thiện.

### 7.3 Tính hợp lệ nội tại và thống kê

Nhánh A có 10 patch seeds trên một tập ảnh cố định, nhánh B có năm training seeds trên một split. Các khoảng theo seed không bao phủ độ bất định của cách chọn ảnh, split hoặc phần cứng. Việc chọn checkpoint và sweet spot theo validation còn tạo một lớp lựa chọn; CI thông thường ở mốc được chọn chưa hiệu chỉnh toàn bộ quy trình lựa chọn. Các chênh lệch descriptive không được biến thành chứng minh nhân quả hoặc tương đương chỉ vì p không nhỏ.

Pretraining và snapshot selection có thể từng dùng COCO val/train. Trong nhánh person, tách theo ảnh chưa bảo đảm tách người/video; các ảnh gần trùng có thể tồn tại dù SHA-256 khác. Cùng hyperparameter chưa chắc tối ưu cho mọi kiến trúc, còn cùng ngân sách wall-clock có thể cho số epoch và bước optimizer khác nhau. Vì thế, benchmark đo cả architecture, initialization, implementation và lịch fine-tuning như một cấu hình kết hợp.

### 7.4 Tính hợp lệ triển khai và vật lý

Không có thử nghiệm print-and-camera ghép cặp hoặc đo năng lượng. Các plot EOT chỉ phản ánh biến đổi phần mềm đã quy định. Các nghiên cứu physical camouflage đa góc nhìn hoặc đa cảm biến có các điều kiện khác [C:grac2025] [C:norp2026] [C:thermalcloth2026]; chúng không thể được thay bằng ảnh tensor trong bài này.

Latency GPU hiện gồm một phiên trên mỗi seed, thứ tự cố định; raw per-frame không được giữ trong gói chia sẻ để tái tính tail. RTX 5060 không đại diện thiết bị edge. Đặc biệt, một detector không NMS vẫn có thể chuyển chi phí phụ thuộc nội dung sang tracker hoặc công đoạn khác, như hướng TrackFlood đang khảo sát [C:trackflood2026]. Cần đo pipeline ứng dụng cuối thay vì dùng một đặc tính kiến trúc làm bảo đảm availability.

### 7.5 Tái lập và tính toàn vẹn dữ liệu

Nhánh A lưu manifest, ảnh/checkpoint hashes, record từng ảnh và prediction lists. Nhánh B lưu 20 lịch sử epoch có hash, record mốc và latency summaries. Đối chiếu đã tái tính selection và tổng hợp từ các tạo tác đó; không có lượt tái huấn luyện hoặc tái sinh AP fullscale độc lập. Các checkpoint, dataset fullscale và snapshot YOLOv13 trên máy thực nghiệm chưa nằm đầy đủ trong gói hiện có.

Cache hoàn tất cần khóa config/nguồn trước khi reuse; setup phải pin implementation đúng bản đã đo; generator cần hỗ trợ archived CSV khi thiếu runs gốc. Checkpoint fine-tuned cần hash và raw predictions/timing để bind kết quả. Các yêu cầu này mô tả công việc tái lập còn lại, không cáo buộc dữ liệu hiện tại sai. Khác checksum source YOLOv12 trên Windows do CRLF đã được đối chiếu với bản chuẩn hóa LF; không che mismatch byte-exact bằng một kết luận toàn nghiên cứu đạt.

### 7.6 Đạo đức và dữ liệu

Các phép thử chỉ xử lý dữ liệu và mô hình trong môi trường nghiên cứu được phép, không triển khai gián đoạn dịch vụ sản xuất. Ảnh có người, áo đối kháng và dữ liệu camera cần được xử lý theo điều khoản nguồn và quyền riêng tư. Không suy ra quyền tái phân phối mọi ảnh COCO từ giấy phép annotations hoặc từ việc có sẵn ảnh trên đĩa. Hình trong bài chủ yếu là đồ thị từ scalar/log để giảm nhu cầu đưa ảnh nhận dạng cá nhân vào bản công bố.

## 8 Kết luận và hướng phát triển

Đối với RQ1, benchmark hộp tổng hợp, đổi backend và mô phỏng QoS container cho thấy chi phí NMS phụ thuộc tải và triển khai, nhưng mức ứng viên mà Sponge Patch tạo ra chưa xác lập suy giảm dịch vụ trong cấu hình đã thử. Tỷ số ứng viên cao nhất quan sát được là 1,24 (RetinaNet), service time SG-GA ≈ clean (230 ms vs 220 ms).

Đối với RQ2, so sánh chính cùng ngân sách trên 500 ảnh không hỗ trợ ưu thế SG-GA so với GA tâm — ngược lại, SG-GA thua GA-center với diff −0,0293, p = 0,002, dz = −2,05. Whitebox tanh mới là phương pháp mạnh nhất (ratio 1,199). Nguyên nhân nằm ở fitness function, không phải kiến trúc GA.

Đối với RQ3, tác động thay đổi theo ảnh, ngưỡng, diện tích và mô hình; giảm AP không đồng nhất với tăng latency. Khảo sát tám kiến trúc cho tỷ số đồng nhất 1,02–1,24 — không có kiến trúc đặc biệt nhạy cảm. EOT phần mềm chưa xác nhận độ bền vật lý.

Thực nghiệm detector bổ sung ghi nhận YOLOv13s có mAP person cao nhất trong nhóm nhưng latency lớn, còn YOLO11n có lợi thế tốc độ trong cấu hình đã đo. Kết quả lựa chọn checkpoint rất sớm ở YOLOv13n/s đặt ra nhu cầu đo pretrained mốc 0 và xem lại lịch fine-tuning. Bài vì vậy cung cấp một quy trình và tập bằng chứng để lựa chọn bước nghiên cứu tiếp, chưa tuyên bố phương pháp tấn công vượt các nghiên cứu khác hoặc đã bảo vệ được một hệ thống edge.

Hướng tiếp theo: (1) tái lập Phantom Sponges và Overload cùng bộ ảnh, (2) điều chỉnh fitness function hướng trực tiếp vào NMS cost thay vì tổng confidence, (3) mở rộng sang physical camera setup với vật liệu, góc, ánh sáng có kiểm soát. Mỗi bước phải giữ nguyên nguyên tắc công bố kết quả âm, không thay số liệu bằng giả thuyết mong muốn.

## Lời cảm ơn

Nhóm cảm ơn giảng viên Đinh Phương Nam, Trường Đại học Công nghệ Thành phố Hồ Chí Minh HUTECH, đã hướng dẫn thực hiện đề tài và phản biện cách diễn giải số liệu, baseline cùng lợi ích của hướng nghiên cứu.

## Tài liệu tham khảo

[[REFERENCES]]
