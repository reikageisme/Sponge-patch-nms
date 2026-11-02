# Review của GVHD (thầy Đinh Phương Nam) — tệp tham chiếu cố định

**Nguồn:** phần "Nguyên văn" bên dưới do người dùng dán ngày 01/11/2026 (thông điệp thầy gửi nhóm). Phần "bản review chi tiết kèm vị trí
từng lỗi" mà thầy nhắc tới CHƯA có trong repo; khi có thì thêm vào cuối tệp này, không sửa phần nguyên văn.

## Nguyên văn
Thầy đã đọc kỹ bản thảo Sponge Patch. Nhóm làm tốt ở phần quy trình đánh giá: khóa patch trước khi kiểm tra, giữ nguyên kết quả âm, thống kê cẩn thận (bootstrap hai tầng, kiểm định đảo dấu, Holm), và giao thức ghim core có hiệu chỉnh A/A. Đây là điểm cộng thật sự. Tuy vậy, ở dạng hiện tại bài chưa đủ để nộp tạp chí Q1-Q2, vì năm vấn đề chính.

(1) Tên bài hứa “khai thác lỗ hổng cạn kiệt tài nguyên”, nhưng số ứng viên chỉ tăng khoảng 3% và không có DoS. Câu chuyện của bài đang mâu thuẫn với bằng chứng.

(2) SG-GA không hơn tìm kiếm ngẫu nhiên, còn thua GA vị trí ngẫu nhiên và baseline gradient. Ngoài ra fitness không gắn với độ trễ.

(3) Quy mô quá nhỏ: chỉ 4 ảnh để tối ưu, 1 detector, 1 CPU laptop. Bài chưa có thiết bị edge, dù đó chính là động cơ của bài.

(4) Phát hiện đáng giá nhất là “số ứng viên tăng khoảng 300 lần nhưng độ trễ toàn trình chỉ tăng 2-6%”. Phát hiện này lại dựa trên dữ liệu lịch sử của YOLOv5s, chưa ghim core và chưa có đối chứng dương. Nó cũng khá gần với kết luận của EVADE (NeurIPS 2025).

(5) Văn bản còn nhiều nhãn nội bộ (OLD128, X1-500, R3, E5, đường dẫn outputs/), câu rào đón dày đặc, số liệu để quá nhiều chữ số. Tài liệu tham khảo còn dùng bài arXiv và workshop, lại thiếu các bài nền (Sponge Examples, Brown et al., EOT, tấn công black-box dựa trên truy vấn).

Thầy đề nghị nhóm chuyển trục bài thành một nghiên cứu đo lường: “số ứng viên có dự đoán được độ trễ hay không”, còn SG-GA chỉ là một case study. Theo hướng đó, nhóm cần làm các việc sau:

Bổ sung đối chứng dương bằng cách tiêm N hộp tổng hợp (từ 10² đến 10⁴) vào cùng pipeline, đo trên laptop và ít nhất một board ARM.
Chạy lại giao thức ghim core trên các patch thật.
Tăng tập tối ưu lên tối thiểu 100 ảnh, thêm thử nghiệm ở ngưỡng 0,25 và ảnh 640 px.
Viết lại bằng tiếng Anh, gom các giới hạn vào mục Threats to validity.

Nếu làm đủ các việc này, bài có thể nhắm Q2, và có cơ hội Q1 nếu kết quả trên thiết bị edge rõ ràng. Còn nếu chỉ dịch và sửa trình bày, bài chỉ ở mức Q3-Q4. Bản review chi tiết kèm vị trí từng lỗi thầy gửi kèm theo.

## Bốn yêu cầu thi công (người dùng chuyển thành lệnh làm việc, 01/11/2026)
1. A/A P1_cpu2 hợp lệ trên laptop → điền MDE vào PREREG_E1 → tag → E1 (tiêm N = 10²–10⁴ hộp giả) trên laptop VÀ trên điện thoại (dùng PREREG_E5_phone).
2. Đo lại patch SG-GA thật bằng giao thức ghim core đã kiểm chứng (không dùng OLD128/X1-500 cũ cho kết luận chính nữa, chỉ dùng tham khảo).
3. Mở tập tối ưu lên tối thiểu 100 ảnh, thêm thử nghiệm ngưỡng 0,25 và ảnh 640 px.
4. Đổi khung bài: trục chính là "N có dự đoán được độ trễ không", SG-GA chỉ là case study minh họa. Sửa tên bài, bỏ "khai thác lỗ hổng/cạn kiệt tài nguyên".
   Viết lại toàn bộ bằng tiếng Anh. Dồn mọi giới hạn, cảnh báo, phạm vi hẹp vào một mục Threats to Validity duy nhất, không rải rào đón khắp bài.
   Bỏ hết nhãn nội bộ (OLD128, X1-500, R1/R2/R3, đường dẫn outputs/). Giảm số chữ số có nghĩa cho hợp lý.
   Bổ sung trích dẫn nền: Sponge Examples, Brown et al. (patch gốc), EOT, một bài tấn công black-box dựa trên truy vấn,
   và so sánh rõ với EVADE (NeurIPS 2025) ở phần Related Work.

## Quy tắc vận hành đi kèm (cũng từ tin nhắn đó)
Tự quyết và tự làm tiếp, không hỏi, TRỪ các điểm sau: DỪNG, ghi lý do vào PROGRESS.md theo khuôn "Quy ước báo cáo" trong CLAUDE.md, rồi chờ:
- Trước khi gắn bất kỳ git tag PREREG nào.
- Khi cần máy (laptop hoặc điện thoại) ở trạng thái rảnh thật để đo.
- Việc không đảo ngược được: xóa, push, reset, đổi tên/tác giả/tiêu đề bài ở bản chính thức.
- Mâu thuẫn số liệu không tự giải quyết được.
- Bị bộ lọc an toàn chặn: không đổi cách diễn đạt để né; bỏ qua phần đó, ghi vào PROGRESS.md, làm việc khác trước.

## Bản review chi tiết của thầy (người dùng dán ngày 02/11/2026, tóm lược đủ ý, giữ nguyên các yêu cầu)
1. Bệ thử nghiệm thiên về "không có tác động" (định luật Amdahl: NMS 0,16% thời gian trên CPU một lõi float32, forward 46 ms). Khẳng định của Phantom Sponges/Overload đến từ GPU/thiết bị biên có bộ tăng tốc, nơi tỷ phần NMS lớn hơn. BẮT BUỘC có ít nhất một profile GPU (forward trên GPU, NMS theo từng backend); tốt hơn thêm thiết bị biên thật (Jetson hoặc Raspberry Pi 5).
2. Nghiên cứu tình huống không kiểm được proxy vì patch GA cho N ≈ 90 như ảnh sạch; cần tập ứng viên thật ở vùng 10^3–10^4: đo lại biến thể Phantom/Overload lịch sử (N khoảng 5000) dưới giao thức ghim lõi và kiểm bộ dự đoán trên đó ("thí nghiệm giá trị nhất còn thiếu").
3. Bài là hai bài dán vào nhau: cắt phần cohort lịch sử khỏi thân bài (chỉ giữ một đoạn SG-GA không vượt baseline, kèm số đã truy lại); chuyển phần còn lại sang tài liệu bổ sung hoặc bỏ; bỏ hoặc gộp Q5–Q6. Thầy không cho nộp số chưa truy được. Lưu ý cấu hình 2 luồng chậm hơn 1 luồng (78,7 so với 51,1 ms) là dấu hiệu lập lịch lên lõi E.
4. Tính mới so với EVADE: EVADE đánh giá tấn công, bài này kiểm trực tiếp đại lượng N; xây mô hình kiểu Amdahl: tỷ số toàn trình ≈ 1 + Δt_NMS(N, cài đặt, hình học)/t_total; dùng đường đáp ứng liều + tỷ phần NMS trên ảnh sạch để dự đoán N* (Bảng N*), rồi kiểm trên GPU/thiết bị khác -> kết quả dương, dùng được.
5. Giao thức: drift cao ở phép tiêm toàn pipeline (12/21, 30%) mà MDE lấy từ phiên khác -> đo lại hoặc ước lượng sàn nhiễu trong phiên (nhánh N=0 lặp lại) và báo độ nhạy loại khối bị cờ; Windows Balanced, turbo bật -> khóa tần số/High Performance tắt turbo hoặc Linux governor performance (Surface Pro 4 chạy Fedora có thể làm profile thứ hai); nói rõ xử lý lõi SMT anh em; đặt hai MDE 640 px (1,9% và 0,69%) cạnh nhau trong bảng; Bảng patch không cân (100 ảnh × 5 seed so với 50 ảnh × 5 seed) và phải nói 5 seed nào, chọn trước khi xem kết quả; báo rõ time_limit/max_nms của Ultralytics có kích hoạt ở N = 10^4 không.
6. Điện thoại: bỏ khỏi bài (chỉ một câu trong hạn chế) hoặc đổi sang Pi 5/Jetson; proot Android gần như không ghim tin cậy được, đừng tốn thêm thời gian.
Lỗi cụ thể: công thức |ln(t_đo/t_dự đoán)| vỡ font (dùng t_meas, t_pred); tham chiếu chéo "Mục 5.1" phải là 5.5 (hai chỗ); mâu thuẫn tác giả liên hệ (đưa GVHD vào danh sách tác giả, hoặc một em làm tác giả liên hệ), ORCID trống; tỷ số 3,5–3,6 (640/320) không khớp Bảng 6 (180/53,5 ≈ 3,4); tóm tắt ~400 từ, cần 200–250 từ (câu hỏi, giao thức, ba phát hiện, một câu hạn chế); bỏ đóng góp (v) "giữ kết quả âm"; đóng băng đăng ký trước trên OSF/Zenodo (DOI, dấu thời gian); kiểm từng tài liệu tham khảo (đặc biệt EVADE, [13], [14], các bài CVPR/WACV 2026); văn phong quá phòng thủ; nộp Q1 phải bằng tiếng Anh, viết lại theo cấu trúc mới, không dịch máy.
Thứ tự thầy muốn: (1) truy lại hoặc cắt phần B; (2) thêm profile GPU (+ thiết bị biên nếu được), lặp A/A, đối chứng dương, tiêm toàn pipeline; (3) đo lại Phantom/Overload (N ~ 5000) dưới ghim lõi và kiểm bộ dự đoán; (4) xây và kiểm chứng mô hình Amdahl cho N* (đóng góp chính mới); (5) đo lại tiêm toàn pipeline với drift thấp, khóa tần số; (6) viết lại tiếng Anh: giao thức -> đối chứng dương -> mô hình dự đoán -> kiểm chứng trên tấn công thật -> SG-GA một đoạn ngắn.
Người dùng: "đại phẫu thuật, máy rảnh, làm tới khi hoàn thiện đầy đủ số liệu".
