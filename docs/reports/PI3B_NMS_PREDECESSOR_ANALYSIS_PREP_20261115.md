## Đã xong

- Hoàn thiện phần **phân tích số học offline** cho thiết kế NMS predecessor đang ở bản nháp, tại `sponge-sim/studies/pi3b_nms_predecessor_analysis_20261115/`. Không sửa 19 file runtime đã khóa dưới tag `925c544`, không chạy model trên Pi và không đọc dữ liệu NMS cũ để chọn thông số mới.
- Bộ đọc yêu cầu đúng từng ô và thứ tự của lịch dự kiến: full 20 ảnh/3.600 lượt hoặc smoke hai ảnh/360 lượt, giữ chỉ số ảnh gốc 0 và 2. Từ chối thiếu/thừa/trùng/đảo thứ tự, đổi số thứ tự, trường lạ, kiểu boolean giả làm integer, thời gian âm/NaN/sai phép trừ, lượt không phải sham có thời gian zero, interval chồng nhau, đổi PID/TID và counter thiếu/sai. Partial/corrupt chỉ trả audit, không sinh khoảng tin cậy trên tập con.
- Chuẩn bị đúng 12 đối chứng A/A và sáu đối chứng instrumented/uninstrumented của bản nháp. Cả điều kiện trung bình log và MDE đều bắt buộc trong mọi ngữ cảnh full. Một đối chứng trượt làm `numerical_controls_pass=false`; không lấy đối chứng khác thay thế. Smoke chỉ có bảng theo ảnh và chẩn đoán đối chứng, không có CI/p/dz hiệu ứng hay kết luận đạt cổng full.
- Primary dùng trung vị của đủ 10 lượt gốc A+B mỗi arm mỗi ảnh. Đơn vị suy luận là ảnh, không phải 3.600 lượt. Bootstrap percentile 20.000 lần, seed 2026111501; sign-flip hai phía đủ 2^20 dấu, tolerance 1e-12; d_z dùng SD mẫu và để null khi SD zero; MDE theo xấp xỉ t trung tâm đã khai báo. Không trừ thời gian sham. Liệt kê nguồn dòng raw cho trung vị, tỷ số theo ảnh, đối chứng và mọi increment instrumented; CPU/wall lớn hơn một vẫn giữ nguyên, không suy nguyên nhân NMS duy nhất.
- Bổ sung 31 kiểm thử hoàn toàn bằng dữ liệu giả có nhãn. Kiểm độc lập bootstrap theo từng lần rút, MDE/dz, sign-flip bằng vét cạn tập nhỏ và đuôi nhị thức cho 20 đơn vị; kiểm trung vị pooled10 khác trung bình hai trung vị; kiểm FAIL MDE dù trung bình gần zero, và FAIL calibration dù 17 đối chứng khác đạt. Chạy chung với 69 kiểm thử core/supervisor/watchdog: **100 PASS**. Nguồn: `sponge-sim/results/pi3b_predecessor_analysis_host_qa_20261115/host_checks_02.log`; bản chạy đầu 30 PASS giữ nguyên tại `host_checks_01.log`.
- Lưu SHA nguồn, nguồn gốc thuật toán, phạm vi chưa đủ và log tại `source_provenance.json`, `preparation_lock.json`. Lịch và validator counter giữ nguyên AST so với source đã khóa. Kiểm lại đủ 23 file runtime/reference/lock so với Git tag, bibliography giữ nguyên SHA được bảo vệ.

## Phát hiện cần biết

- **Không có kết quả đo Pi mới.** Lần kiểm lại SSH chỉ đọc vẫn timeout tới `192.168.10.11:22`; client Tailscale báo `NoState`, không có peer và “Tailscale is starting. Please wait.” Chưa xác định nguyên nhân tuyến; không đổi cấu hình, cài gói, khởi động lại hay tắt sshd. Bằng chứng local được ghi rõ là transcript, không phải raw remote: `connectivity_recheck.json`.
- Bộ phân tích số học không thể tự xác minh nguồn/tag, cảm biến, vật liệu, reference, pool, restore hay đăng ký khoa học chỉ từ các hàng timing. Vì vậy mọi đầu ra luôn ghi `campaign_quality_assessed=false` và `confirmatory_interpretation_authorized=false`. `numerical_controls_pass=true` trên dữ liệu giả hoặc tương lai chưa đủ để coi campaign đạt chất lượng.
- Nếu đủ toàn bộ lịch nhưng cổng số học FAIL, vẫn giữ thống kê đầy đủ dưới nhãn chẩn đoán; không rescue primary. Nếu partial/corrupt, không sinh thống kê hiệu ứng. Bản nháp cũ có checkpoint trước đó nói analyzer chưa có; checkpoint này bổ sung phần số học, **chưa thay thế bộ audit toàn campaign**.
- Code chưa gắn với scientific PREREG/tag hay launcher. Không có activation functional mới. Các kết quả NMS component FAIL/PI1 chưa chạy, pilot FAIL và RSS full PASS trước đây giữ nguyên. Không đưa dữ liệu giả hoặc số thời gian chạy unit test vào bài như hiệu năng thiết bị.

## Việc tiếp theo — chọn 1 trong các cách sau

1. Khi có lại tuyến Pi, kiểm chỉ đọc namespace/unit/context rồi tiếp tục đúng gói supervisor tag `925c544`. Chưa khởi động case nào nên không tạo QA02 hoặc suy diễn việc kết nối hỏng là FAIL của cơ chế khôi phục. Nếu trạng thái ngoài dự kiến, dừng đối chiếu.
2. Chỉ sau năm sleeping case thực tế đạt và raw/source/restore được kiểm độc lập mới đăng ký/kích hoạt một lượt functional 40 case. Giữ thời hạn, cổng và quy tắc không retry đã dự kiến.
3. Còn phải hoàn thiện worker timing, warmup/reference, kiểm ghim lõi bằng tải thật, schema/logging tích hợp và auditor toàn campaign. Sau đó mới chốt scientific PREREG/tag trước smoke mới. Full mới cần review cụ thể dựa trên smoke thực tế; quyền full RSS đã dùng không mở full NMS.

## Đang chờ gì ở tôi

Tuyến SSH tới Pi hoạt động lại để kiểm chứng phần thiết bị thật. Câu hỏi kiểm nguồn/LAN/Tailscale đã gửi trước đó; không cần gửi lại quyền tối ưu hay quyền chạy RSS full đã hoàn tất.
