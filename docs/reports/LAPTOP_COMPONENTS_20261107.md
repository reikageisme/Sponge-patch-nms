# Kiểm tra riêng NMS và MASK trên CPU laptop — protocol đã đóng

## Đã xong

Đã chạy đúng thứ tự đăng ký: NMS smoke hai ảnh, NMS full 20 ảnh, rồi MASK smoke hai ảnh. Mỗi ảnh dùng cùng tensor sạch và tensor PGD đã khóa từ trước. Tổng cộng 4.608 lượt timing đã hoàn tất; đây không phải 4.608 ảnh độc lập. Không chạy lại lượt nào để tìm PASS.

| Lượt | Timing | Cờ tham chiếu | Kết luận theo đăng ký |
|---|---:|---:|---|
| NMS smoke, hai ảnh | 384 | 0/4 | Đủ điều kiện chạy full |
| NMS full, 20 ảnh | 3.840 | 20/22; cho phép tối đa 2 | FAIL |
| MASK smoke, hai ảnh | 384 | 1/4; không cho phép cờ nào | FAIL; hủy full |

Nguồn: `sponge-sim/results/laptop_components_20261107/{nms_kernel/smoke_01,nms_kernel/full_01,mask_native/smoke_01}/verification_receipt.json:n_trials`, `P1_cpu2/stage_summary.json:flags,n_references,feasibility_pass,quality_pass`. Tổng timing là phép cộng ba `n_trials`. Protocol `sponge-sim/prereg/PREREG_LAPTOP_COMPONENTS_20261107.md`, tag `prereg-laptop-components-20261107`, commit `0b468db6130714be0521bc3d8bf547b206dbfcef` đều có trước phép đo.

Cả ba lượt có dữ liệu đầy đủ, đầu vào không thay đổi, số đếm và hash prediction khớp lượt CPU trước, kiểm tra ghim lõi đạt. Sau từng lượt đã kiểm tra khôi phục đúng affinity cho 45/45 tiến trình ứng dụng trước khi phân tích. Đây là kiểm tra tính toàn vẹn, không thay thế cổng ổn định thời gian.

Đã lưu bảng tra nguồn có số dòng JSONL tại `paper_en/segmentation_extension/laptop_components_sources.json`, bảng tổng hợp `sponge-sim/results/laptop_components_20261107/family_analysis.json`, hình PNG/PDF và đoạn bổ sung bài tiếng Anh `paper_en/segmentation_extension/laptop_components.tex`. Hình PNG đã xem trực quan; chưa build PDF toàn bài vì chưa có TeX engine. Không sửa `paper_en/main.tex` đang có thay đổi ngoài phạm vi.

## Phát hiện cần biết

Rà offline sau đó phát hiện bảng PDH theo tên công đoạn bị bỏ sót ở bộ tổng hợp cũ. Counter vẫn có trong raw; đã tạo bản chẩn đoán riêng, không sửa summary hoặc cổng FAIL. Xem `docs/reports/LAPTOP_COMPONENT_DRIFT_20261107.md`.

NMS full có A/A MDE sạch **0,3407300540545993%**, bị tấn công **0,09585090875208305%**, đều dưới ngưỡng 1%. Tuy nhiên 20/22 cờ tham chiếu vẫn khiến lượt này FAIL theo đúng quy tắc đã khóa. Không đổi ngưỡng hoặc bỏ tham chiếu sau khi thấy số liệu.

Trong 20 cờ đó, **19 khối nhanh hơn mốc đầu**, một khối chậm hơn. Trung vị forward tham chiếu đầu là 225,8709 ms, cuối là 210,5462 ms; tỷ số cuối/đầu 0,9321528359784284. Đây là quan sát drift hai chiều; chưa xác định nguyên nhân vật lý. Không đủ căn cứ gọi là quá nhiệt, lỗi turbo, tác động hypervisor hay tiến trình cụ thể. Nguồn: `nms_kernel/full_01/P1_cpu2/raw.jsonl:kind=reference`, trung vị `samples_ns` chia 1e6 và trường `ratio,flagged`; bảng tổng hợp giữ các selector tương ứng.

MASK smoke bị cờ ở tham chiếu cuối, tỷ số **1,0328367896175703**, vượt giới hạn 3%. MDE hai ảnh chỉ là chẩn đoán; không dùng để suy độ ổn định của 20 ảnh. Lượt full không được khởi chạy. Nguồn: `mask_native/smoke_01/P1_cpu2/stage_summary.json:references[-1],aa`.

Các tỷ số công đoạn đã tính được giữ trong `diagnostic_only_contrast` của bảng tổng hợp; **không có contrast công đoạn nào đủ điều kiện suy luận chính**. Hai giá trị p=1 trong bảng là placeholder giữ nguyên họ hai so sánh, không phải kiểm định cho thấy không có hiệu ứng. Không thực hiện sign-flip cho contrast không đủ điều kiện.

NMS đo khối 64 lần gọi cùng torchvision facade trên boxes/scores đã chuẩn bị, tính mỗi lần bằng thời gian khối chia 64; gồm vòng Python và giải phóng indices. MASK đo một lần dựng mask từ prototype/detection đã chuẩn bị, giải phóng output sau đồng hồ. Khác trạng thái cache và vòng đời tensor nên không cộng trung vị hai phần hoặc trừ khỏi tổng cũ để quy phần trăm trách nhiệm. Các lượt CPU toàn trình/phòng thủ đạt trước đây vẫn giữ nguyên kết luận trong phạm vi riêng; lượt mới không bổ sung chứng cứ DoS hay ARM.

SHA256 raw được giữ nguyên:

- NMS smoke: `10c89e8aadbbb94f0b6bfb2a7a85150d91a0913f19bebc02fe2f51c603627c90`.
- NMS full: `9a0e61f462cf7e054993e70783c32f8c6a29401bc97be8489cf4d89a29311ba8`.
- MASK smoke: `9b1e76ffad18100c6b722b03dcb17035029dc1d643a3e771609f18aefe72bc98`.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Rà nguyên nhân drift từ dữ liệu đã lưu, đề xuất kiểm chứng có giới hạn trước khi đăng ký lượt mới → gõ: "Rà drift offline, giữ nguyên mọi lượt FAIL".

B. Hoàn thiện điều kiện pin/nhiệt và nguồn pin/sạc của A36 trước bất kỳ tải nào → gõ: "Tiếp tục gỡ điều kiện đo A36, chưa chạy tải khi thiếu cảm biến".

## Đang chờ gì ở tôi

Không cần duyệt lại các kết quả đã lưu. Protocol công đoạn đã đóng và không tự chạy lại. Điện thoại chưa có nguồn SOC/sạc live và registry nhiệt hợp lệ; SSH đã đóng sau giai đoạn metadata. Muốn chạy tải A36 cần giải quyết các điều kiện này và xác nhận trạng thái máy theo protocol riêng; việc đã bật sshd chỉ cho phép truy cập, không chứng nhận điều kiện đo.
