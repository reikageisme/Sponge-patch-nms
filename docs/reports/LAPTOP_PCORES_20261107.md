# Hai P-core: ghim lõi đạt, smoke thời gian không đạt

## Đã xong

Đã chạy đúng một smoke trên CPU `[0,2]`, thuộc hai P-core vật lý khác nhau, hai intra-op và một inter-op. Giữ nguyên worker toàn trình đã sửa carryover/output lifetime, model và input; chỉ dùng hai ảnh đầu của 20 cặp PGD đã khóa. Tag `prereg-laptop-pcores-20261107`, commit `6c261995d580a8bf06d02423ff4c086c4579069f` có trước tải và timing mới.

Đủ 384 lượt timing, thứ tự và dữ liệu đầy đủ. Kiểm ghim lõi đầu/cuối đạt, lần lượt 1,9525429469479412 và 1,951560693996942 effective cores; mức sử dụng trung bình trên hai CPU được phép đều 100% trong tải kiểm ghim. Đây là tải kiểm ghim, không phải mức sử dụng của mọi lần inference. Đã tránh cả hai P-core và SMT sibling `[0,1,2,3]` cho cây tiến trình ứng dụng trợ lý, rồi khôi phục đúng affinity cho 45/45 tiến trình trước phân tích.

Audit source/tag/input/config, lịch 48 lần lặp, readback và môi trường đều khớp. 44 tests CPU/phụ lục đạt trước phép đo. Nguồn chính: `sponge-sim/results/laptop_pcores_20261107/smoke_01/P2/{raw.jsonl,manifest.json,attack_summary.json}` và `smoke_01/verification_receipt.json`. SHA256 raw: `6f7eabd0ca0b1f30aaac027f623d34c1c32ff2fd659a94214cf7f47256b4a1b0`.

## Phát hiện cần biết

**Smoke FAIL:** 2/4 khối tham chiếu bị cờ, trong khi đăng ký chỉ cho phép 0/4:

| Mốc tham chiếu | Tỷ số so với ban đầu | Trạng thái |
|---|---:|---|
| Ban đầu | 1 | Không cờ |
| Trước ảnh thứ nhất | 1,0953159727928494 | Chậm hơn trên 3% |
| Trước ảnh thứ hai | 1,0029429737996352 | Không cờ |
| Cuối | 1,0317927329528502 | Chậm hơn trên 3% |

Nguồn `attack_summary.json:references[*].block,ratio,flagged`; receipt giữ số dòng raw. Full 20 ảnh được **hủy, không khởi chạy**. Protocol đóng sau smoke này; không tăng lần lặp, đổi warmup/core hoặc chạy lại để tìm PASS.

Các ước lượng tỷ số và A/A của hai ảnh vẫn được lưu đầy đủ để chẩn đoán, không đưa thành hiệu ứng nhiều core đạt chất lượng. MDE A/A với hai ảnh rất thiếu ổn định và không phải cổng smoke; nguyên nhân hủy full là hai cờ tham chiếu. Không suy ra không có hiệu ứng hoặc CPU nhiều core nói chung không đo được.

Cả bốn hash prediction sạch/tấn công khác phiên một core trước; `N_tau` và K đều giống cho hai ảnh này. Không loại ảnh hay yêu cầu byte prediction phải giống giữa các cấu hình thread khác nhau. Nguồn `verification_receipt.json:counts_vs_historical_p1_descriptive_only`.

Process CPU time/wall trên hai core là số core hiệu dụng, có thể lớn hơn 1 hợp lệ; không gọi đó là tỷ lệ phần trăm ngân sách hai core. PDH trong worker chỉ đọc CPU0, không đại diện toàn bộ hai core. Chưa có nhiệt độ hoặc scheduler trace để nhận diện nguyên nhân vật lý. Việc ghim đạt và thời gian không ổn định là hai kết luận khác nhau.

Endpoint vẫn là tensor chuẩn bị sẵn → mask native, không phải dịch vụ/deadline, patch nhỏ hay ARM. Không dùng smoke này để so tốc độ một core với hai core hoặc đảo các FAIL cũ thành PASS. Hai phiên toàn trình một core đạt trước đây vẫn giữ nguyên phạm vi riêng.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Hoàn thiện phần launcher/điều kiện đo A36 đang thiếu, kiểm offline trước → gõ: "Tiếp tục hoàn thiện runner A36".

B. Rà bản vá phạm vi bài tiếng Anh và giữ rõ mọi kết quả không đạt → gõ: "Rà bản vá phạm vi bản thảo".

## Đang chờ gì ở tôi

Chưa cần thao tác để làm tiếp offline. Không có benchmark đang chạy, không kết nối lại máy thuê đã xóa. A36 còn thiếu nguồn SOC/sạc và registry nhiệt hợp lệ nên chưa chạy tải. Muốn đo core/thiết bị khác phải có câu hỏi và protocol mới; không tự lặp smoke này.
