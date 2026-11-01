# Đề tài NCKH: Sponge Patch (nhắm Q1)

Tiêu đề: "Tấn công đối kháng Sponge Patch: Khai thác lỗ hổng cạn kiệt tài nguyên bằng thuật toán tối ưu không gian".
Nhóm: Phạm Tuấn Anh, Mai Quốc Bảo; GVHD và tác giả liên hệ: Đinh Phương Nam (HUTECH). Ngôn ngữ làm việc: tiếng Việt; thuật ngữ kỹ thuật giữ tiếng Anh.

## Luận điểm đang theo đuổi (hướng A + C)
- A: số ứng viên trước NMS (N_tau) là proxy KHÔNG dự đoán được độ trễ/suy giảm dịch vụ; chỉ ra vùng proxy đúng và vùng sai.
- C: bản đồ điều kiện (backend × class-aware/agnostic × cap top-k × tau × số core CPU × chu kỳ phát) cho biết khi nào tấn công NMS thành lỗ hổng sẵn sàng.
- Không còn dùng cụm "máy chủ biên / Edge Server". Gọi đúng: "mô phỏng hạn chế tài nguyên trên CPU laptop ghim core". Chưa có thiết bị ARM/edge thật.

## Quy tắc cứng (không thương lượng)
1. KHÔNG xóa, di chuyển, ghi đè dữ liệu thô hay kết quả đã chạy (`outputs/**`). Muốn dọn: đề xuất danh sách, chờ duyệt.
2. KHÔNG sửa code cũ (`core/`, `attack/`, `experiments/`). Cần dùng lại thì COPY sang `sponge-sim/` kèm header nguồn (file:dòng + SHA256) và test hồi quy.
3. KHÔNG đụng `project_yolov13/**` (nhánh B, ~32 GB, ngoài luận điểm), `.venv`, `.git`.
4. Mọi con số đưa vào bài phải truy được tới dòng raw (JSONL/JSON:selector). Không làm tròn cho đẹp, không bịa, không điền số khi chưa có nguồn.
5. Đặt trước giả thuyết/endpoint (PREREG) và `git tag` TRƯỚC khi đo. Sai lệch ghi vào DEVIATIONS.md.
6. Kết quả âm giữ nguyên. Không dùng "tương đương / không phụ thuộc / chứng minh" khi chỉ có p > 0,05 hoặc CI chứa 0; phải kèm MDE.
7. Không cài gói hệ thống, không dùng mạng, không đổi power plan/turbo: chỉ ĐỌC cấu hình và in checklist cho tôi tự làm.
8. Chỉ `git add` đúng file của việc đang làm. Repo đã dirty từ trước (5 file code đã sửa sau các lượt chạy cũ). Không reset/clean/force-push.

## Bản đồ repo (D:/Physical-Visual-DoS-EdgeAI-main)
- Cohort dữ liệu (tên bắt buộc dùng thống nhất):
  - OLD128 = `outputs/extended_q1_20261002` (128 ảnh con của 500 ID held-out; q1000 dùng 32 ảnh).
  - X1-500 = `outputs/x1_500img_20261018` (500 ảnh; là mở rộng SAU khi thấy p=0,1504 ở OLD128, KHÔNG phải tái lập độc lập vì 128 ⊂ 500).
  - X2 = `outputs/x2_architecture_20261020` (8 detector; Faster R-CNN/RetinaNet/SSDlite đếm `post_module_detections`, tức đã qua NMS nội bộ, KHÔNG dùng để kết luận tải NMS).
  - X5 v2 chỉ là mô hình hàng đợi nhiều server từ thời gian forward, không phải đo core, không có NMS: không dùng làm bằng chứng.
- Code tái sử dụng được (đã audit): `core/victim_model.py`, `experiments/extended_evaluation.py`, `experiments/extended_validation.py:113` (optimize), `experiments/local_q1_validation.py` (load_image).
- Bản thảo: `BaoCaoKhoaHocAdversarialAttacks_Q1_VI_v2.tex` (nhánh `paper/q1-fixes`; nhánh B đang tắt bằng cờ).
- Báo cáo review đã có: `REVIEW/01_inventory.md` … `REVIEW/06_*.md`. Đọc 03 và 04 trước khi đụng bản thảo.

## Kết quả đã xác minh (để không phải tính lại)
- OLD128: SG-GA − GA tâm = −0,00513, CI95% [−0,01118; 0,00071], p = 0,1504, d_z = −0,498.
- X1-500: −0,02934, CI95% [−0,03833; −0,02160], p = 0,001953 (giá trị nhỏ nhất có thể với 10 seed, cả 10 seed cùng dấu âm), d_z = −2,05. SG-GA kém hơn cả GA vị trí ngẫu nhiên, không khác tìm kiếm ngẫu nhiên.
- Suy luận hiện tại theo seed (10 seed), chưa phủ độ bất định của ảnh: cần bootstrap hai tầng (ảnh × seed).
- Backend NMS custom vs torchvision khớp trên mẫu hữu hạn (không phải tương đương mọi tie).

## Việc đang làm
Bước 1: harness mới `sponge-sim/` + thí nghiệm E1 (đối chứng dương, dose-response), E2 (proxy), E5 (giao thức đo). Chi tiết: `docs/PROMPT_STEP1.md`. Tiến độ ghi ở `sponge-sim/PROGRESS.md`.

## Làm việc tiết kiệm token (quan trọng: lần trước hết token giữa chừng)
- Cập nhật `sponge-sim/PROGRESS.md` sau mỗi giai đoạn nhỏ (đã xong gì, đang dở gì, lệnh để chạy tiếp, quyết định chờ tôi). Phiên mới đọc file này đầu tiên.
- Commit nhỏ, thường xuyên trên nhánh `harness/step1`.
- Việc dài (đo, build): chạy nền, ghi log ra file, chỉ đọc phần cuối log. Không in JSON lớn ra màn hình; dùng `head`, `jq`, hoặc script tóm tắt.
- Không Glob/Grep toàn repo (235k file, 45 GB). Luôn chỉ rõ thư mục con.
- Dùng skill `sponge-research` cho mọi việc về thí nghiệm, thống kê, báo số, sửa bài.

## Thiết bị ARM: điện thoại Samsung Galaxy A36 (Snapdragon 6 Gen 3), qua SSH
- Host `192.168.1.139`, cổng `8022`, user `u0_a445`, khóa riêng `$env:USERPROFILE\.ssh\phone_a36` (Git Bash: `~/.ssh/phone_a36`).
- Môi trường chạy: bên trong Termux, dùng proot-distro Ubuntu. Lệnh mẫu: `ssh -p 8022 -i ~/.ssh/phone_a36 u0_a445@192.168.1.139 "<lệnh>"`.
- Đây là điện thoại dùng hàng ngày của người dùng, KHÔNG phải máy thí nghiệm. Phạm vi cho phép TRÊN ĐIỆN THOẠI: chỉ đọc/ghi trong `~/sponge-sim` (hoặc thư mục tương ứng trong proot Ubuntu). Không đụng gì khác trên Termux hay Android.
- Ngoại lệ mạng (đã được người dùng cho phép): cài proot-distro + Ubuntu trong Termux, rồi cài python3, pip, git, torch trong Ubuntu. Ngoại lệ này CHỈ áp dụng trong lúc CÀI ĐẶT. Sau khi cài xong, quy tắc cứng số 7 "không dùng mạng" áp dụng cho cả điện thoại: không tải thêm gói hay dữ liệu.
- Khi ĐO thật (A/A, E5, smoke có ghi thời gian): người dùng tắt mạng di động trên điện thoại, giữ Wi-Fi ở mức tối thiểu hoặc tắt hẳn nếu SSH không cần giữ liên tục. Nếu phải tắt Wi-Fi, chạy phép đo nền trên điện thoại (log ra file trong `~/sponge-sim`), rồi lấy kết quả sau khi Wi-Fi bật lại. Không đo khi mạng di động đang bật. PREREG_E5_phone phải ghi trạng thái mạng của từng lần đo, và Claude chờ người dùng xác nhận trước khi bắt đầu.
- Cấm: `rm`/`rmdir` ngoài thư mục `sponge-sim` qua SSH; tắt/khởi động lại máy; đổi cài đặt hệ thống Android.
- Kết thúc việc: tắt sshd trên điện thoại bằng `ssh ... "pkill sshd"` để không để cổng mở.
- Kết quả đo lấy về `sponge-sim/results/phone_a36/`. Mọi lần đo trên điện thoại phải có PREREG riêng (PREREG_E5_phone.md) và chờ người dùng xác nhận máy rảnh (sạc, không dùng tay, Không làm phiền, tắt tiết kiệm pin) trước khi chạy đầy đủ.

## Quy ước báo cáo (bắt buộc cho mọi phiên, mọi báo cáo cuối việc)
Viết cho người không rành kỹ thuật đọc hiểu ngay, không cần hỏi lại ai. Dùng đúng khuôn 4 mục sau, theo thứ tự:

```
## Đã xong
(mỗi dòng 1 việc, không thuật ngữ nội bộ khó hiểu)

## Phát hiện cần biết
(bất thường/rủi ro nói bằng câu thường, không chỉ trích dòng code)

## Việc tiếp theo — chọn 1 trong các cách sau
A. [mô tả] → gõ: "[tin nhắn mẫu để copy-dán]"
B. [mô tả] → gõ: "[tin nhắn mẫu để copy-dán]"
(tối đa 3 lựa chọn, luôn kèm sẵn câu để copy-dán, không bắt người dùng tự nghĩ câu lệnh)

## Đang chờ gì ở tôi
(nếu không có: "Không có — có thể làm tiếp việc A/B ở trên")
```
Số liệu vẫn phải truy được tới nguồn (quy tắc cứng số 4); nguồn đưa vào mục "Đã xong" hoặc phụ lục ngắn cuối báo cáo, không làm rối thân báo cáo.
