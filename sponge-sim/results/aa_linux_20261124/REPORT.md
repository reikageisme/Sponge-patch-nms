# A/A trên Ryzen 5 5500 khóa xung

Ngày đo 24/11/2026. Xubuntu Live 24.04.5 LTS, kernel 7.0.0-31-generic, CPU logic 2, CPU 8 offline, boost toàn máy tắt và giới hạn CPUFreq 3,600 GHz. Kiểm xung trước và sau mỗi phiên bằng 10 mẫu Bzy_MHz dưới tải ghim.

Hai phiên dùng cùng 100 ảnh COCO val2017, YOLOv8n FP32, một luồng và đúng SHA-256 trọng số của E5 Windows. Mỗi ảnh có 10 lượt A và 10 lượt B với hai nhãn cùng đầu vào, theo ABBA hoặc BAAB. Toàn trình gồm nạp và resize ảnh, forward, decode, lọc điểm và NMS pure PyTorch.

| Kích thước | Công đoạn | Tỷ số A/B | CI 95% theo ảnh | MDE (%) | CI 95% theo khối (hậu kiểm) |
|---|---|---:|---:|---:|---:|
| 320 px | forward | 1.00010 | 0.99997–1.00025 | 0.0201 | 0.99997–1.00028 |
| 320 px | total | 0.99988 | 0.99953–1.00017 | 0.0463 | 0.99943–1.00020 |
| 640 px | forward | 0.99997 | 0.99987–1.00008 | 0.0149 | 0.99988–1.00006 |
| 640 px | total | 1.00004 | 0.99990–1.00018 | 0.0199 | 0.99997–1.00011 |

Tỷ số là trung bình hình học của các tỷ số trung vị A/B theo ảnh. MDE dùng công suất 80% và alpha 0,05. Kết quả chính dùng bootstrap theo ảnh đăng ký trước. Bootstrap 10 khối là hậu kiểm với 20.000 lượt và seed 20261124.

| Kích thước | Dòng đo | Ghim trước/sau (lõi hiệu dụng) | Drift bị cờ | Drift lớn nhất | Bzy_MHz trước/sau |
|---|---:|---:|---:|---:|---:|
| 320 px | 2.000 | 0.999 / 0.999 | 0/11 | 0.046% | 3575–3575 / 3575–3575 |
| 640 px | 2.000 | 0.999 / 0.999 | 0/11 | 0.178% | 3575–3575 / 3575–3575 |

| Công đoạn | 320 px, trung vị (ms) | 320 px, MDE (%) | 640 px, trung vị (ms) | 640 px, MDE (%) |
|---|---:|---:|---:|---:|
| pre | 5.221 | 0.3161 | 7.556 | 0.2124 |
| forward | 42.86 | 0.0201 | 143 | 0.0149 |
| decode | 0.3395 | 0.2564 | 1.022 | 0.1137 |
| tau | 0.05035 | 0.1807 | 0.06761 | 0.2146 |
| nms_torch_pure | 0.963 | 0.1422 | 1.159 | 0.1693 |
| nms_tv_nms | 0.09118 | 0.1820 | 0.09673 | 0.1503 |
| total | 46.47 | 0.0463 | 164 | 0.0199 |

MDE toàn trình Windows đã lưu là 0,552% ở 320 px. Ở 640 px, phiên đầu là 1,882% và phiên lặp là 0,685%. So sánh giữa Windows và Linux mang tính mô tả vì CPU, hệ điều hành và bản dựng Python khác nhau.

MDE Linux áp dụng cho định nghĩa toàn trình và môi trường đo ở đây. Hiệu chuẩn ảnh sạch không cung cấp phép đo toàn trình của bảng patch. CI bao gồm 1 không phải bằng chứng tương đương.

Cả bốn CI 95% chính và bốn CI hậu kiểm theo khối đều bao gồm 1. Không có điểm drift nào bị cờ trong hai phiên chính.

## Hồ sơ tái lập

Tag prereg-aa-linux-20261124 trỏ đến 6de50aa2c5fab3e7be451f43e3bad0f2369928f0 và nằm trong aa_prereg_source.bundle. Đã đối chiếu SHA-256 của 35 tệp. Số dòng, tỷ số chính và độ lệch chuẩn theo ảnh cũng đã được tính lại từ raw. Các thư mục full-01 và smoke-01 lưu raw, manifest, log xung và kết quả phân tích.

Chạy lại bộ phân tích từ tag trên raw của cả hai phiên cho JSON khớp chính xác toàn bộ trường thống kê và kiểm chất lượng. Trường run_dir ghi đường dẫn riêng của lần chạy lại. SHA-256 của hai summary đã lưu trên Windows cũng khớp bản gốc trên máy đo.

## Đoạn đề xuất để duyệt trước khi chèn vào bài

Vị trí đề xuất là cuối mục hiệu chuẩn A/A, sau phần Windows. Bảng A/A hiện tại ghi số từ laptop Windows. Các ngưỡng dùng trong những phép đo Windows được giữ theo phiên và định nghĩa độ trễ đã dùng ở đó.

**Bản tiếng Anh**

> We repeated the clean-image A/A calibration on a frequency-locked Ryzen 5 5500 running Xubuntu Live. At each input size, we used the same 100 COCO validation images and the same YOLOv8n FP32 weights as in the Windows calibration, with one CPU thread and 10 repetitions per label per image. The CPU frequency limit was set to 3.600 GHz with boost disabled. In all 40 checks of effective frequency under load, taken before and after the two sessions, turbostat reported 3.575 GHz. The end-to-end A/B ratios were 0.99988 at 320 px (95% CI 0.99953 to 1.00017) and 1.00004 at 640 px (95% CI 0.99990 to 1.00018). The end-to-end MDEs were 0.0463% and 0.0199%, respectively. Neither session flagged a reference point (0 of 11 at each size). The maximum absolute drift was 0.046% at 320 px and 0.178% at 640 px. These estimates characterize the clean-image measurement noise on this Linux configuration. The separate Windows runs retain their original calibration.

**Bản tiếng Việt**

> Chúng tôi lặp lại hiệu chuẩn A/A ảnh sạch trên Ryzen 5 5500 chạy Xubuntu Live và khóa xung. Ở mỗi kích thước đầu vào, chúng tôi dùng cùng 100 ảnh kiểm định COCO và cùng trọng số YOLOv8n FP32 như trong hiệu chuẩn Windows, với một luồng CPU và 10 lượt đo cho mỗi nhãn trên mỗi ảnh. Giới hạn xung được đặt ở 3,600 GHz và boost được tắt. Trong cả 40 mẫu kiểm xung hiệu dụng dưới tải trước và sau hai phiên, turbostat ghi 3,575 GHz. Tỷ số A/B toàn trình là 0,99988 ở 320 px (CI 95% từ 0,99953 đến 1,00017) và 1,00004 ở 640 px (CI 95% từ 0,99990 đến 1,00018). MDE toàn trình lần lượt là 0,0463% và 0,0199%. Cả hai phiên đều có 0/11 điểm tham chiếu bị gắn cờ. Độ trôi tuyệt đối lớn nhất là 0,046% ở 320 px và 0,178% ở 640 px. Các ước lượng này mô tả nhiễu đo ảnh sạch trên cấu hình Linux đã khảo sát. Các phiên Windows giữ hiệu chuẩn ban đầu.
