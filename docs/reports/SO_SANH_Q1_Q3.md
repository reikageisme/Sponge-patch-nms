# So sánh gói cũ `paper_Q1_submission/` và gói chốt `paper_Q3_submission_v5/` (03/11/2026)

| | Gói cũ (Q1, 21/10/2026) | Gói chốt (Q3 v5) |
|---|---|---|
| Tiêu đề | "Tấn công đối kháng Sponge Patch: Khai thác lỗ hổng cạn kiệt tài nguyên…" | "Tấn công cạn kiệt tài nguyên qua NMS có thực sự làm chậm bộ phát hiện? Một nghiên cứu đo lường trên CPU ghim lõi" (GVHD duyệt) |
| Khung | Đề xuất và kiểm chứng một tấn công | Kiểm tra giả định "N_τ cao ⇒ chậm" của dòng tấn công; Sponge Patch là đối tượng được đánh giá |
| Dữ liệu | Các nhóm lịch sử OLD128, X1-500, X2 (8 detector), luồng dịch vụ, phòng thủ, EOT, diện tích; nhánh YOLOv13 lựa chọn detector | Đối chứng dương E1, A/A, tiêm toàn pipeline E9, biến thể tấn công toàn ảnh E10 (YOLOv5s), patch E6 (N_τ, NMS đo; toàn trình dự đoán) |
| Giao thức | Phần lớn số đo chưa ghim lõi; ghim lõi chỉ là một tiểu mục | Toàn bộ dưới giao thức ghim lõi có kiểm chứng, A/A, MDE, đăng ký trước + tag |
| Bảng số | Gõ tay | Sinh tự động từ tệp tóm tắt; `check_numbers.py` ĐẠT |
| Tài liệu tham khảo | 31 mục, nhúng `thebibliography` | 40 mục BibTeX, kiểm từng mục trên web (REPORT_Q3 mục d) |
| Tác giả liên hệ | Đinh Phương Nam, dp.nam@hutech.edu.vn | Giữ như bản cũ (khớp CLAUDE.md) |

**Không chuyển nội dung nào từ bản cũ sang**, trừ thông tin tác giả liên hệ. Lý do:
- Các nhóm lịch sử đã bị GVHD yêu cầu cắt ở bước 2.
- Nhánh YOLOv13 nằm ngoài luận điểm.
- Phần lớn số đo trong bản cũ được đo khi chưa ghim lõi.

`paper_Q1_submission/` vẫn được giữ vì `build_submission.py` lấy phần preamble CAS tiếng Việt từ đây.
