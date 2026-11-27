# Nhóm B (27/11/2026): phân tích lại dữ liệu AMD đã lưu — POST HOC, không đo mới

Script: `sponge-sim/studies/review_20261127/diag_posthoc.py` (chỉ thư viện chuẩn, bootstrap 20 000 lần, seed 20261127).
Kết quả đầy đủ: `sponge-sim/results/review_20261127/diag_posthoc.json` (selector ghi trong ngoặc vuông dưới đây).
Nguồn: raw của `results/amd_20261124/full-01/{e9,e10,e12}` và `results/aa_linux_20261124/.../aa_{320,640}`.
Mọi kết quả ở đây là THĂM DÒ, sau khi đã thấy dữ liệu; chỉ dùng để thiết kế lần đo lại, không thay endpoint đã đăng ký.

## B1. Thời gian sạch có hai mức

Phân cụm 1 chiều (2-means) trên thời gian toàn trình của nhánh sạch; cờ "hai mức" khi chênh > 3%, tách > 5 SD trong cụm,
cụm nhỏ ≥ 5% [`B1_streams.<luồng>`].

| Phiên | Mức nhanh (ms) | Mức chậm (ms) | Chênh | Tỷ lệ chậm | Hai mức? |
|---|---|---|---|---|---|
| E10 YOLOv5s 640, tv_nms | 270,26 | 298,64 | 10,5% | 0,49 | có |
| E9 YOLOv8n 320, N=0, tv_nms | 38,24 | 42,15 | 10,2% | 0,40 | có |
| E9 YOLOv8n 640, N=0, tv_nms | 140,19 | 150,39 | 7,3% | 0,10 | có |
| E12 YOLOv8n 320, sạch, tv_nms | 39,28 | 39,72 | 1,1% | 0,43 | không |
| A/A 320, toàn trình | 46,19 | 50,30 | 8,9% | 0,25 | không (tách 3,0 SD) |
| A/A 640, toàn trình | 154,51 | 165,25 | 7,0% | 0,88 | không (tách 3,2 SD) |

Điểm khác nhau quyết định:
- **E9: mức nhanh/chậm cố định theo ảnh.** 8/20 ảnh ở 320 px và 2/20 ảnh ở 640 px chậm ở mọi lần đo, không ảnh nào lẫn hai mức
  (kiểm thêm trong phiên làm việc, cùng raw). Vì N* và tỷ số E9 so sánh trong cùng một ảnh, hai mức không làm tăng nhiễu của
  phép so sánh; sàn nhiễu trong phiên E9 vẫn 0,07-0,08% ở 320 px như bài đã viết.
- **E10: mức nhảy giữa các đơn vị ngay trong cùng một ảnh.** Hai nhánh sạch clean_a và clean_b dùng CHÍNH MỘT tensor
  (`studies/e10_reference/run.py:85`) nhưng chỉ cùng mức ở 29/50 ảnh; giữa hai đơn vị liền nhau của cùng ảnh, mức đổi 259/550 lần.
  Đây là nguồn của MDE trong phiên 2,8%. Trong một đơn vị (9 lần gọi liên tiếp) mức gần như không đổi (hệ số biến thiên trung vị 0,16%).
- Vì cùng tensor mà khác mức, nội dung ảnh (ví dụ số denormal) không giải thích được E10. Đơn vị đứng sau một đơn vị bị tấn công
  chậm nhiều hơn một chút (P(chậm) 0,348 so với 0,242 sau đơn vị sạch), nhưng tương quan hạng giữa N của đơn vị trước và thời gian
  nền của đơn vị sau chỉ 0,066 [`B1_e10_mechanism`]. Giả thuyết còn lại: trạng thái bộ cấp phát/bộ nhớ (vị trí trang vật lý, page
  fault khi glibc trả bộ nhớ cho hệ điều hành). Lần đo lại sẽ ghi page fault mỗi lần gọi và có một phiên thăm dò cố định ngưỡng glibc.

## B2. Bảng 10: phần dư âm biến mất khi so cùng mức

Phần dư = (Δ toàn trình) − (Δ NMS vi mô), như `studies/e10_reference/stage_decomp.py` [`B2_e10_decomp_by_state`].
"Cùng mức" = đơn vị tấn công và cả hai nhánh sạch của ảnh đó cùng mức (22/50 ảnh có ít nhất một cặp như vậy).

| Biến thể, backend | Phần dư, mọi cặp (ms) | Phần dư, chỉ cặp cùng mức (ms) |
|---|---|---|
| Overload, tv_nms | −3,65 [−8,42; 1,37] | 0,11 [−1,63; 1,58] |
| Overload, tv_batched | −3,51 [−8,27; 1,44] | 0,28 [−1,29; 1,60] |
| Overload, Ultralytics | −3,24 [−7,96; 1,72] | 0,69 [−1,01; 2,00] |
| Phantom Sponges, tv_nms | −4,74 [−9,79; 0,65] | 1,10 [−0,32; 3,14] |
| Phantom Sponges, tv_batched | −4,63 [−9,65; 0,74] | 1,22 [−0,18; 3,29] |
| Phantom Sponges, Ultralytics | −4,35 [−9,36; 1,02] | 1,48 [0,04; 3,64] |

Cột thứ nhất tái lập đúng Bảng 10 của bài. Khi chỉ giữ cặp cùng mức, phần dư dương nhỏ, khoảng tin cậy hẹp hơn khoảng ba lần và chứa 0
ở 5/6 ô. Nghĩa là "toàn trình tăng ít hơn NMS đo riêng" nhiều khả năng là do các nhánh rơi ngẫu nhiên vào mức nhanh/chậm, không phải
hai cách đo NMS khác nhau. Kiểm tra thật sự cần mốc thời gian NMS bên trong lần gọi toàn trình (có trong runner E10-R).
Hạn chế: chọn cặp theo mức là lọc sau khi thấy dữ liệu, mẫu còn 22 ảnh và không cân bằng theo seed.

## B3. Ngưỡng "gây hại" (đề xuất, chưa chốt)

Δt_harm = 5% của khung 33,33 ms ở 30 FPS = 1,667 ms; độ nhạy 10% = 3,333 ms [`harm_thresholds_ms`].
Trên một lõi, thời gian sạch đã vượt 33 ms (YOLOv8n 320 px khoảng 38-46 ms), nên đây là ngưỡng tuyệt đối "thêm bao nhiêu ms
mỗi khung", không phải "lỡ khung 30 FPS".

**E9, N_harm** (mức lưới nhỏ nhất có cận dưới KTC 95% của Δt_total trung bình > ngưỡng; không cap) [`B3_e9_n_harm.<cv>|<backend>|<hình học>|capNone`]:

| Backend | 320 px, rời nhau / trộn / cụm (5%) | 640 px, rời nhau / trộn / cụm (5%) |
|---|---|---|
| PyTorch thuần | 100 / 100 / >2100 | 300 / 300 / 8400 |
| torchvision `nms` | 1000 / 2100 / >2100 | 3000 / 3000 / 8400 |
| torchvision batched | 2100 / 2100 / 2100 | 1000 / 1000 / 3000 |
| Ultralytics | 1000 / 1000 / 2100 | 1000 / 1000 / 3000 |

So với N* "phát hiện được" (100 ở 320 px, 300 ở 640 px ở gần như mọi ô) của các kernel thư viện,
ngưỡng gây hại cao hơn N* khoảng 3-28 lần tùy ô nên phân biệt được các cài đặt, đúng điều thầy hỏi. Với PyTorch thuần N_harm vẫn rơi vào mức thấp nhất của lưới (cần lưới mịn E9-R).

**Patch (E12)** [`B3_e12_delta_total`]: không nhánh nào vượt 1,667 ms. Lớn nhất là gradient B4 với PyTorch thuần,
+0,820 ms [0,706; 0,929], tức 2,46% khung 30 FPS; các nhánh GA dưới 0,04 ms.

**Tấn công toàn ảnh (E10)** [`B3_e10_delta_total`]: Δt_total trung bình 3,13-5,23 ms (9,4-15,7% khung), nhưng mọi KTC chứa 0
(cận dưới từ −2,46 đến −0,09 ms), nên không kết luận được gây hại hay không ở độ nhiễu của phiên này. Đây là lý do chính để đo lại E10.

## Hệ quả cho bài (đề xuất, chưa sửa bài)
1. Câu "chưa rõ vì sao MDE phiên YOLOv5s lớn" có thể thay bằng mô tả hiện tượng hai mức (đã đo được, chưa rõ cơ chế), gắn nhãn post hoc.
2. Bảng 10 cần đọc lại sau E10-R; tạm thời ghi rằng phần dư âm không còn khi so cùng mức (post hoc).
3. Thêm cột N_harm vào Bảng 6 và một câu về ngưỡng gây hại, khi tác giả đã chốt ngưỡng.
