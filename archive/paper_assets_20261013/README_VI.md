# Kho ảnh ứng viên cho bản thảo — 13/10/2026

Đã rà soát 830 mục nguồn (803 ảnh/vector trên đĩa và 27 media nhúng từ bản Word trước sửa); loại trùng SHA-256 còn **476 tệp ảnh/vector khác nội dung**. Tất cả 27 media nhúng đã có bản giống byte trên đĩa. Giữ nguyên ảnh gốc, không tạo ảnh bằng AI và không chạy thực nghiệm mới.

## Cách đọc

- `RECOMMENDED/`: 11 hình gốc có caption, cộng ba hình dựng mới từ scalar đã kiểm chứng và phạm vi rõ bên dưới; 8 hình Sponge được đối chiếu hash manifest, 1 hình fullscale, 2 sơ đồ local tùy chọn. Không cần đưa cả 11 hình vào thân bài.
- `inventory.csv` / `inventory.json`: ID, đường dẫn nguồn, bản sao, SHA-256, kích thước, nhóm, phạm vi, trùng lặp.
- `CONTACT_SHEETS/`: 15 sheet; đã xem toàn bộ 15 sheet của ảnh raster khác nội dung. Vector SVG/source.svg được bảo toàn, bản PNG tương ứng đã xem.
- `excluded.json`: 263 ảnh dataset, vendor, weights và ảnh QA bị loại khỏi kho manuscript; đây không phải danh mục dữ liệu raw toàn dự án.

Các ảnh val_batch được giữ để minh họa dữ liệu/định tính lịch sử. Không gọi chúng là prediction của fullscale vì đường dẫn nằm ở benchmark trước fullscale; không suy từ hình có người mặc áo patch thành bằng chứng chống patch/DoS.

## 11 hình có thể cân nhắc

| STT | Hình | Resolution | Vai trò |
|---|---|---|---|
| 1 | [RECOMMENDED/01_ty_so_ung_vien.png](RECOMMENDED/01_ty_so_ung_vien.png) | 1581×779 | SPONGE_VALIDATED |
| 2 | [RECOMMENDED/02_ngan_sach_truy_van.png](RECOMMENDED/02_ngan_sach_truy_van.png) | 1581×780 | SPONGE_VALIDATED |
| 3 | [RECOMMENDED/03_dien_tich_mieng_dan.png](RECOMMENDED/03_dien_tich_mieng_dan.png) | 1581×779 | SPONGE_VALIDATED |
| 4 | [RECOMMENDED/04_loai_bo_eot.png](RECOMMENDED/04_loai_bo_eot.png) | 2380×780 | SPONGE_VALIDATED |
| 5 | [RECOMMENDED/05_chuyen_giao.png](RECOMMENDED/05_chuyen_giao.png) | 1782×778 | SPONGE_VALIDATED |
| 6 | [RECOMMENDED/06_danh_doi_phong_thu.png](RECOMMENDED/06_danh_doi_phong_thu.png) | 2172×776 | SPONGE_VALIDATED |
| 7 | [RECOMMENDED/07_ngan_sach_xu_ly.png](RECOMMENDED/07_ngan_sach_xu_ly.png) | 1578×779 | SPONGE_VALIDATED |
| 8 | [RECOMMENDED/08_bien_the_tham_chieu.png](RECOMMENDED/08_bien_the_tham_chieu.png) | 1570×780 | SPONGE_VALIDATED |
| 9 | [RECOMMENDED/09_fullscale_mAP_growth.png](RECOMMENDED/09_fullscale_mAP_growth.png) | 1980×936 | MAIN_CURRENT_YOLO |
| 10 | [RECOMMENDED/10_luu_do_ga_vi.png](RECOMMENDED/10_luu_do_ga_vi.png) | 3000×2694 | ILLUSTRATIVE_SCHEMES |
| 11 | [RECOMMENDED/11_quy_trinh_kiem_chung_vi.png](RECOMMENDED/11_quy_trinh_kiem_chung_vi.png) | 2667×1533 | ILLUSTRATIVE_SCHEMES |

### 1. ty_so_ung_vien.png

Bốn phương pháp, 10 seed, 128 ảnh kiểm tra; đường đứt tại 1 là ảnh sạch. Không phải tỷ số độ trễ hay xác nhận DoS. 95% bootstrap ghép cặp theo 10 seed, điều kiện trên bộ ảnh cố định; không gộp ảnh/lượt đo thành seed

Nguồn: `outputs/extended_q1_20261002/figures/ty_so_ung_vien.png`. SHA-256: `29e040db94139c6744ff3a66fd885b08134a4b5a6c121f4917f6b21e36b769b7`.

### 2. ngan_sach_truy_van.png

Mọi điểm dùng đúng 32 ID ảnh chung; vùng mờ là khoảng tin cậy theo seed, không phải độ lệch chuẩn. 95% bootstrap ghép cặp theo 10 seed, điều kiện trên bộ ảnh cố định; không gộp ảnh/lượt đo thành seed

Nguồn: `outputs/extended_q1_20261002/figures/ngan_sach_truy_van.png`. SHA-256: `96947525fd7907cab9ae25b0c118c29532264b932033a0a5c53424e0f7196521`.

### 3. dien_tich_mieng_dan.png

Diện tích 1/1,98/4/7,91/16%, cùng ảnh tối ưu/kiểm tra và ngân sách; mức 4% dùng checkpoint SG-GA tại 400. 95% bootstrap ghép cặp theo 10 seed, điều kiện trên bộ ảnh cố định; không gộp ảnh/lượt đo thành seed

Nguồn: `outputs/extended_q1_20261002/figures/dien_tich_mieng_dan.png`. SHA-256: `f8457f0cbda2ea8db14d539f2fd24fa25ae1ce70793f15b261d89dee868ffa3a`.

### 4. loai_bo_eot.png

Bảy cấu hình cùng 400 lượt ảnh qua mô hình; bốn mẫu EOT có ít cá thể hơn. Kiểm tra độc lập dùng tám ảnh, 16 mẫu ghép cặp mới/ảnh, không chọn lại miếng dán. 95% bootstrap ghép cặp theo 10 seed, điều kiện trên bộ ảnh cố định; không gộp ảnh/lượt đo thành seed

Nguồn: `outputs/extended_q1_20261002/figures/loai_bo_eot.png`. SHA-256: `f81633087e0997415a7f820810e7c6376c5322150326e75aba0745b51822387d`.

### 5. chuyen_giao.png

Cùng 16 ảnh và 10 miếng dán nguồn; bao gồm chuẩn hóa/hậu xử lý riêng của mô hình. Không so sánh độ trễ tuyệt đối giữa các kiến trúc; DETR không có NMS. 95% bootstrap ghép cặp theo 10 seed, điều kiện trên bộ ảnh cố định; không gộp ảnh/lượt đo thành seed

Nguồn: `outputs/extended_q1_20261002/figures/chuyen_giao.png`. SHA-256: `ee7272a698179f00a37b940739ea91ce99db806f275772cc852d20d1cf3fd147`.

### 6. danh_doi_phong_thu.png

AP được tính gộp ảnh bằng COCOeval, sau đó trung bình theo miếng dán/seed. Chỉ so sánh thích nghi với SG-GA cùng 400 truy vấn; đồ thị mô tả, không mang thanh sai số. Đồ thị mô tả trung bình theo seed; không có thanh sai số. Khoảng tin cậy chênh lệch AP/AR có trong analysis.json.

Nguồn: `outputs/extended_q1_20261002/figures/danh_doi_phong_thu.png`. SHA-256: `64ed15b11e51050a750738260ee691625bc857b939c833f55aafbe78232dce21`.

### 7. ngan_sach_xu_ly.png

Một máy vật lý, 10 khối ghép cặp, 16 ảnh, ba lượt đo. Suy luận + giải mã dự đoán + lọc + NMS được đo chung; không phải thời hạn hay tuổi khung camera. 95% bootstrap ghép cặp theo 10 seed, điều kiện trên bộ ảnh cố định; không gộp ảnh/lượt đo thành seed

Nguồn: `outputs/extended_q1_20261002/figures/ngan_sach_xu_ly.png`. SHA-256: `acceb7a50f368514d943063d224247a90b34275aa075531686c88922d8b690b5`.

### 8. bien_the_tham_chieu.png

Chạy hàm nguyên trạng từ kho Underload, chuyển môi trường sang CPU/runtime hiện tại; UAP cộng toàn ảnh, mô hình/kích thước/tập tối ưu/ngân sách khác nhóm miếng dán cục bộ. Không tái lập toàn bộ thí nghiệm bài gốc; không xếp hạng hai đe dọa như cùng điều kiện. 95% bootstrap ghép cặp theo 10 seed, điều kiện trên bộ ảnh cố định; không gộp ảnh/lượt đo thành seed

Nguồn: `outputs/extended_q1_20261002/figures/bien_the_tham_chieu.png`. SHA-256: `d89514d042293a95169abbe2b92d89e692e3cf6d2c61cf2e6c4d80319a06ef6c`.

### 9. fullscale_mAP_growth.png

Độ chính xác validation theo ngân sách wall-clock của bốn mô hình qua năm seed. Trái: checkpoint tốt nhất theo validation trong ngân sách; phải: epoch cuối đã hoàn tất. Đây là person benchmark bổ sung trên GPU, không phải đo Visual DoS; mô tả riêng khoảng bất định theo báo cáo fullscale.

Nguồn: `project_yolov13/results/fullscale_mAP_growth.png`. SHA-256: `f99f1900fee2b92f2307388c0e79277f312c8c4e675c4ce8ebb9c9e0353d5fba`.

### 10. luu_do_ga_vi.png

Lưu đồ tối ưu SG-GA/GA trong giao thức local validation 400 truy vấn ảnh, ảnh bus 320×320. Hình minh họa phương pháp cũ; không thay thế giao thức extended Q1 với 2.500 lượt ảnh.

Nguồn: `figures/luu_do_ga_vi.png`. SHA-256: `75d8e5c16d39f06111656ce8ffe39624ecac4cef3fd9e754ad49ee4f3596b202`.

### 11. quy_trinh_kiem_chung_vi.png

Giao thức kiểm chứng local trên YOLOv8n CPU: tối ưu trên ảnh bus rồi đánh giá trên bus, Zidane và COCO128. Chỉ minh họa giai đoạn local trước extended Q1; không xác nhận DoS hay thử nghiệm vật lý.

Nguồn: `figures/quy_trinh_kiem_chung_vi.png`. SHA-256: `b2b9b5b14d05da2f0a5cb3d9c7765e4f6007b4e0c2ee50ee9b6a174297fa175c`.

## Những nhóm không đưa vào kết quả mới

- `SUPPLEMENTARY_HISTORICAL`: ảnh camera/giao diện, plot CPU/FPS mô phỏng, convergence/defense cũ, patch simulated, ảnh val_batch và time_budget/map_growth trước fullscale. Giữ vì có giá trị lịch sử; không có provenance đủ để dùng thay kết quả mới. Không dùng số CPU/FPS trên ảnh giao diện như số đo có đối chứng.
- `SUPPLEMENTARY_LOCAL_VALIDATION`: local precursor trên bus/Zidane, synthetic-box NMS và texture 64×64. Có thể đưa phụ lục nếu giải thích local protocol; không gộp với extended Q1 hay fullscale.
- `SPONGE_PATCH_LIBRARY`: 279 texture/checkpoint/UAP, phần lớn 64×64. Không chọn vài texture rồi suy ra hiệu quả thống kê; ảnh gần đen của reference UAP là đặc tính biểu diễn, không tự động coi là file hỏng. Không phóng lớn texture 64×64 rồi gọi ảnh print A4 chứng minh đánh giá vật lý.
- `ILLUSTRATIVE_SCHEMES`: vector/PNG sơ đồ local 400 truy vấn. Bản SVG là nguồn chỉnh sửa; PNG sẵn dùng. Caption cần khóa phạm vi.

## Kiểm tra đã thực hiện

- Tính SHA-256 và sao chép byte nguyên trạng; deduplicate chính xác, không nhận diện gần trùng theo nội dung.
- 8/8 biểu đồ trong `SPONGE_VALIDATED` khớp hash manifest; caption kế thừa mô tả cùng phương pháp bất định của manifest.
- Xem 15 contact sheets: biểu đồ và batch ảnh hiển thị được, ảnh texture giữ đúng resolution. Không có dấu hiệu corruption nhìn thấy.
- Một số biểu đồ trục/log/CI có chữ nhỏ khi đưa Word; nên dùng rộng toàn cột và giữ caption ngay dưới ảnh.
- Việc kiểm tra ảnh không xác minh lại raw dataset/predictions/checkpoint fullscale; provenance và giới hạn khoa học vẫn theo báo cáo review ngày 13/10.

Nguồn phạm vi: `figures/NGUON_HINH_VI.txt`, `outputs/extended_q1_20261002/figures/manifest.json`, `docs/2026-10-13_research-review-report_VI.md`, `START_HERE_VI.md`.
## Hình đối chiếu bổ sung ngày 13/10/2026

`RECOMMENDED/12_so_sanh_cong_bo_va_thuc_nghiem.png` là hình mới từ Table I, trang 7 của YOLOv13 v2 và scalar thực nghiệm đã lưu. Hai panel ghi giao thức riêng; không so chênh lệch xuyên dữ liệu/phần cứng. Các giá trị và SHA-256 đầu vào ở `COMPARISON/comparison_sources.json`. Hình này được tạo sau inventory gốc, không phải ảnh đã có trong thực nghiệm.

`REFERENCES/recent_refs.md` và `.json` chứa 25 công trình để đọc/lọc tiếp, chỉ trong cửa sổ 13/10/2024–13/10/2026; đã phân biệt hội nghị và preprint. Danh sách này là thư viện ứng viên, không phải kết quả tổng quan hệ thống đầy đủ.

`RECOMMENDED/14_so_sanh_bai_nen_va_sponge.png` đối chiếu định lượng Underload/EVADE với Sponge bằng ba panel độc lập, giữ nguyên sự khác biệt AP50/AP50:95 và hộp sau/trước NMS. Scalar và nguồn ở `COMPARISON/foundation_sources.json`.

`RECOMMENDED/13_dien_tich_kiem_chung.png` dựng lại từ mean và bootstrap CI đã lưu trong analysis.json. Bản 03 gốc có tiêu đề nhầm thành loại bỏ thành phần; bảo toàn bản gốc nhưng dùng bản 13 trong Word. Nguồn/hash ở `COMPARISON/area_replot_sources.json`.

## Bản Word viết lại đã hoàn tất

File chính: `D:/Physical-Visual-DoS-EdgeAI-main/BaoCaoKhoaHocAdversarialAttacks_NangCap_VI.docx`.

Bản đọc và sửa tiếp có 24 trang, 10 bảng, 10 hình, ba công thức Word chỉnh sửa được và 22 tài liệu trích dẫn. Thư viện ứng viên có 25 công trình trong hai năm gần đây. Đã giữ tên tác giả, email và giảng viên; giữ trọng tâm Sponge Patch, tách benchmark YOLO thành phần bổ sung. Bản trước sửa bảo toàn tại `_paper_revision_20261013/BaoCaoKhoaHocAdversarialAttacks_NangCap_VI.before_rewrite.docx`.

Nên đọc phần 5 để xem số liệu Sponge nói lên gì; phần 6 để xem benchmark mới; phần 7.1 và Hình 10 để đối chiếu các hướng nghiên cứu, ưu/nhược và số liệu từ bài nền. Hình 9 là đối chiếu detector YOLO. Các hình không suy ra phương pháp nhóm tốt hơn chỉ từ khác dữ liệu/giao thức.

Giới hạn quan trọng: SG-GA chưa vượt GA tâm ở so sánh chính; giảm AP chưa xác lập DoS; benchmark person không chứng minh chống patch. Các bước thực nghiệm cần bổ sung được nêu ở kết luận.
