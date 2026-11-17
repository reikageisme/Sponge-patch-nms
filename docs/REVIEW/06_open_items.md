# 06 — Các điểm còn mở

## Quyết định tác giả

1. Nhánh B đang mặc định TẮT bằng `\branchBfalse`, nội dung vẫn trong source. Duyệt giữ tắt, đưa thành phụ lục hay bật lại? Không xóa dữ liệu hoặc source B.
2. Hình giao diện camera lịch sử đã bỏ khỏi thân bài; có đưa vào phụ lục lịch sử khi truy được provenance không? Chưa xác định ảnh dùng SG-GA hay nhiễu ngẫu nhiên; ảnh gốc vẫn nguyên.
3. Tóm tắt đang trình bày OLD128 trước, X1-500 sau. Hai cohort lồng nhau; X1 là mở rộng sau quan sát, không xác nhận độc lập. Có giữ thứ tự này không?
4. Tác giả liên hệ đã ghi Đinh Phương Nam trong cortext/email, bỏ cormark gắn Anh; giữ nguyên danh sách hai tác giả Anh/Bảo, không tự thêm đồng tác giả. Nếu quy định venue đòi corresponding author nằm trong author list, cần tác giả xác nhận danh sách/tư cách tác giả và vị trí tên Nam.

## Số và khẳng định chưa có nguồn đủ

- Không tìm thấy prospective power calculation bảo đảm 500 ảnh đủ công suất; bản v2 chỉ nói mục tiêu tăng thông tin/precision, vẫn10seed.
- OLD Δ−.0051 và X1 Δ−.0293 cùng âm; không dùng gợi ý “đổi dấu” trong yêu cầu vì trái số liệu.
- Không điền CI mới cho đồ thị X2 chưa được tính/kiểm trong scope; figure ghi rõ không có CI. Nhiều weights_sha256 X2=null; không bịa hash thay thế.
- Không có thiết bị ARM/edge hoặc calibration; không báo resource-NMS end-to-end từ X5v2. Condition map đầy đủ là việc tiếp theo, không kết quả hiện có.
- Historical synthetic benchmark thiếu raw repeats/seed/geometry/hardware/hash; không dùng fit endpoint làm bằng chứng complexity.
- Không có số đo inference/training/timing/COCOeval mới. Mọi số X1 bổ sung đều từ raw/analysis đã lưu và ghi selectors trong changelog; không cần điền placeholder số đo mới.

## Biên dịch và layout

V2 đã compile SUCCESS bằng compiler tích hợp (Tectonic/XeTeX), staging `REVIEW/06_latex_build/after/`. Cùng engine/font compatibility: trước14trang → sau13trang; counter kiểm sau pass2 trên bản probe riêng, cố ý dừng bằng thông báo counter. Bản giao không có probe.

Chưa xuất được PDF local: tool chỉ compile/preview, không export; không TeXCLI trongPATH, Dockerdaemon chưa chạy, DocumentControl không có connected session. Không upload manuscript ra bên ngoài. Preview project đã được yêu cầu mở trong Codex; chưa visual QA từng trang.

Warnings cần kiểm trước nộp: Overfull123.63pt tại maketitle (cũng có trong bản trước), các tràn còn lại10.29/5.76/8.08/16.98pt, glyphU+009D và Underfull ở bảng. Diagnostic pass2 không thấy undefined references/citations; static targets/citationkeys đầy đủ. Không coi compilation success là hết lỗi layout/font. Chỉ nhánh XeTeX thêm fontspec/TU để giữ tiếng Việt; pdfLaTeX vẫn giữ T5/babel gốc.

Dừng ở bản thảo và hai báo cáo; không tự sửa harness, thí nghiệm hoặc dọn repo.

## Cập nhật 04/11/2026: thay đổi có chủ đích, không phải sai lệch
Theo yêu cầu trực tiếp của Tanh (ưu tiên hơn mục 4 ở trên): Đinh Phương Nam được thêm vào danh sách tác giả, là đồng tác giả thứ ba và tác giả liên hệ (`\cormark`/`\cortext`), ORCID 0009-0006-1239-1266. Chỉ tác giả liên hệ có ORCID. Áp dụng trong `paper_en/main.tex` (bản chính thức).
