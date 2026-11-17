# A1. Tiêu chí, mô hình rỗng và cách tóm tắt N_tau

Nguồn: `..\sponge-sim\results` (E10, E11).

## 1. Tiêu chí hiển thị end-to-end (E10: YOLOv5s, 640 px)

| Tấn công | NMS | MDE trong phiên | Ngưỡng Δt* (ms) | Δt_NMS (ms) | Δt_total (ms) | Bảng ghi "vượt MDE" | Δt_NMS > Δt* | Δt_total > Δt* |
|---|---|---|---|---|---|---|---|---|
| overload | tv_batched | 1.97% | 6.2 | 4.9 | 9.1 | không | không | có |
| overload | tv_nms | 1.98% | 6.2 | 5.2 | 10.5 | có | không | có |
| overload | ultra_native | 2.44% | 7.7 | 7.0 | 10.7 | không | không | có |
| phantom_sponges | tv_batched | 1.97% | 6.2 | 6.0 | 9.8 | không | không | có |
| phantom_sponges | tv_nms | 1.98% | 6.2 | 5.4 | 10.0 | có | không | có |
| phantom_sponges | ultra_native | 2.44% | 7.7 | 6.9 | 10.2 | không | không | có |

- Số ô phản ví dụ cho câu "chỉ thấy được **khi** Δt_NMS > MDE × t_total": **2/6** (bảng ghi vượt MDE trong khi Δt_NMS dưới ngưỡng).
- Viết theo Δt_total thì điều kiện cần đúng ở 6/6 ô: phần tăng ngoài NMS (lọc điểm, forward) cũng góp vào.
- Lưu ý: cột "vượt MDE" của bảng dùng cận dưới khoảng tin cậy của tỉ số, còn hai cột cuối so trung bình với ngưỡng. Hai phép này khác nhau, nên bài phải nói rõ dùng phép nào.

## 2. Cùng dữ liệu, ba luật quyết định

| Tấn công | NMS | Tỉ số (CI 95%) | CI loại 1 | cận dưới > 1 + MDE | cận dưới > 1,01 | cận dưới > 1,05 |
|---|---|---|---|---|---|---|
| overload | tv_batched | 1.029 (1.017 đến 1.041) | có | không | có | không |
| overload | tv_nms | 1.034 (1.022 đến 1.045) | có | có | có | không |
| overload | ultra_native | 1.034 (1.022 đến 1.047) | có | không | có | không |
| phantom_sponges | tv_batched | 1.031 (1.019 đến 1.045) | có | không | có | không |
| phantom_sponges | tv_nms | 1.032 (1.021 đến 1.043) | có | có | có | không |
| phantom_sponges | ultra_native | 1.033 (1.020 đến 1.046) | có | không | có | không |

- Mọi ô đều có khoảng tin cậy loại 1: hiệu ứng có thật và vào khoảng 3%. Câu đúng là "tăng khoảng 3%, dưới ngưỡng 5%", không phải "không thấy được".
- MDE là đại lượng thiết kế, đổi theo cỡ mẫu và phiên đo; nên báo thêm một ngưỡng hiệu ứng cố định có ý nghĩa vận hành.

## 3. Luật pass của mô hình ngân sách so với mô hình rỗng R_pred = 1

| Tấn công | NMS | R đo | R dự đoán | sai số mô hình (trung vị, cận trên CI) | pass | sai số mô hình rỗng (xấp xỉ) | mô hình rỗng dưới 0,05 |
|---|---|---|---|---|---|---|---|
| overload | tv_batched | 1.029 | 1.027 | 0.022 (≤ 0.028) | có | 0.029 | có |
| overload | tv_nms | 1.034 | 1.067 | 0.046 (≤ 0.058) | không | 0.033 | có |
| overload | ultra_native | 1.034 | 1.098 | 0.067 (≤ 0.088) | không | 0.034 | có |
| phantom_sponges | tv_batched | 1.031 | 1.023 | 0.024 (≤ 0.030) | có | 0.031 | có |
| phantom_sponges | tv_nms | 1.032 | 1.042 | 0.031 (≤ 0.038) | có | 0.032 | có |
| phantom_sponges | ultra_native | 1.033 | 1.065 | 0.044 (≤ 0.054) | không | 0.032 | có |

- Mô hình ngân sách pass 3/6 ô. Mô hình rỗng (luôn đoán "không chậm đi") có sai số điểm dưới 0,05 ở 6/6 ô.
- Vậy luật pass hiện tại không chứng tỏ mô hình có sức dự đoán. Cần báo sai số mô hình rỗng bên cạnh và một skill score, tính trên từng đơn vị (ảnh, seed).
- Sai số theo đơn vị (cột 5) lớn hơn nhiều so với sai số giữa hai trung bình: nhiễu từng đơn vị chi phối, không phải độ lệch của mô hình.

## 4. "N_tau tăng bao nhiêu lần" phụ thuộc cách tóm tắt

| Tấn công | tau | Trung bình các tỉ số (CI 95%) | Trung vị sạch → bị tấn công | Tỉ số hai trung vị |
|---|---|---|---|---|
| overload | 0.01 | 66 (47 đến 89) | 253.5 → 11674.0 | 46 |
| overload | 0.25 | 389 (135 đến 753) | 45.0 → 5578.5 | 124 |
| phantom_sponges | 0.01 | 80 (56 đến 109) | 253.5 → 14487.5 | 57 |
| phantom_sponges | 0.25 | 340 (104 đến 678) | 45.0 → 4811.5 | 107 |

- Con số "340 đến 389 lần" trong abstract là trung bình các tỉ số, bị kéo bởi các ảnh có N sạch rất nhỏ. Theo trung vị chỉ khoảng 107 đến 124 lần. Bài phải ghi rõ thống kê nào, tốt nhất báo cả hai.

## 5. Bảng patch (E11): tỉ số N_tau và khoảng tin cậy

| Nhánh | tau | Tỉ số N (CI 95%) | CI chứa 1 | Hướng |
|---|---|---|---|---|
| C1 | 0.01 | 1.04 (0.99 đến 1.10) | có | không rõ |
| C1 | 0.25 | 0.94 (0.86 đến 1.03) | có | không rõ |
| C3 | 0.01 | 1.04 (0.99 đến 1.09) | có | không rõ |
| C3 | 0.25 | 0.95 (0.86 đến 1.05) | có | không rõ |
| B1 | 0.01 | 1.05 (0.99 đến 1.10) | có | không rõ |
| B1 | 0.25 | 0.90 (0.83 đến 0.99) | không | giảm |
| B2 | 0.01 | 1.06 (1.03 đến 1.10) | không | tăng |
| B2 | 0.25 | 0.93 (0.87 đến 0.97) | không | giảm |
| B3 | 0.01 | 1.03 (0.98 đến 1.08) | có | không rõ |
| B3 | 0.25 | 0.95 (0.86 đến 1.07) | có | không rõ |
| B4 | 0.01 | 2.39 (2.09 đến 2.74) | không | tăng |
| B4 | 0.25 | 6.81 (4.72 đến 9.44) | không | tăng |
| C2 | 0.01 | 1.07 (1.00 đến 1.16) | có | không rõ |
| C2 | 0.25 | 0.94 (0.89 đến 0.99) | không | giảm |
| C4 | 0.01 | 1.05 (1.02 đến 1.08) | không | tăng |
| C4 | 0.25 | 0.96 (0.92 đến 1.00) | có | không rõ |

- 4 dòng có khoảng tin cậy nằm trên 1 và 3 dòng nằm dưới 1. Câu "the intervals of the ratio contain 1" không đúng cho mọi dòng; các dòng giảm cũng cần được bàn.
