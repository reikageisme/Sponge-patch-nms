# CPU laptop: hai phiên phân đoạn thật đạt kiểm tra — 07/11/2026

## Đã xong

Đã đo 20 cặp tensor sạch/tấn công PGD đã lưu, YOLOv8n-seg FP32 trên i5-1335U, ghim logical CPU 2 (một luồng của P-core), 1 luồng Torch, AboveNormal và HighQoS. Ứng dụng ChatGPT của chính phiên được tạm tránh CPU 2/3 rồi khôi phục. Không thay power plan, turbo, bảo vệ nhiệt hoặc package. Máy GPU thuê đã bị xóa; không kết nối lại. Chưa chạy điện thoại.

Lượt mới dùng đúng tag `prereg-laptop-carryover-20261107` (`a57662d32d8a37f448776622bfa1941862c62634`), một smoke đạt rồi một full cố định. Full có 3.840 lần đo; mỗi ảnh/nhánh có 96 lần gọi để lấy trung vị và 48 lần mỗi nhãn để kiểm A/A. Không loại spike hoặc ảnh nào.

| Kiểm tra full | Giá trị từ artifact | Cổng đăng ký | Kết quả |
|---|---:|---:|---|
| Mốc tham chiếu bị cờ | 1/22 | Tối đa 2, lệch >3% | Đạt |
| MDE A/A ảnh sạch | 0,996621759496496% | ≤1% | Đạt, sát ngưỡng |
| MDE A/A ảnh tấn công | 0,21343183695886384% | ≤1% | Đạt |
| Ghim CPU đầu/cuối | Đạt/đạt | Cả hai đạt | Đạt |
| Khôi phục affinity | 45 khôi phục đúng; 3 đã thoát | Không lỗi hoặc bỏ qua tiến trình còn sống | Đạt |

Trung bình nhân của tỷ số trung vị theo ảnh là **4,235134263867301**, CI95% **[4,0249535047979865; 4,441712278610986]**. Chênh lệch trung vị trung bình theo ảnh là **745,4720050000001 ms**, CI95% **[696,2336961875001; 792,4382326875] ms**. Bootstrap theo 20 ảnh, 20.000 mẫu, RNG 20261107. Các lần lặp trong ảnh không được tính như ảnh độc lập.

Endpoint bắt đầu từ tensor đã chuẩn bị và kết thúc khi hàm trả mask native 640×640. Giải phóng output sau cả hai đồng hồ, trước lần gọi kế tiếp; không gồm giải mã JPEG, truyền dữ liệu, giải phóng output, hàng đợi hay serialization. Đây là tấn công số toàn ảnh, không phải universal/localized patch.

Nguồn: `sponge-sim/results/laptop_carryover_20261107/full_01/P1_cpu2/attack_summary.json` → `quality_pass`, `aa`, `contrasts.total`, `references`, `counts`; dữ liệu gốc `raw.jsonl`, SHA256 `f344e61f6f1200a1b47558d48ae51b93d7373774c9594c54070d6d3bcf567148`. `verification_receipt.json` kiểm lại lock, tag, input, lịch gọi, tham chiếu, tính toán và nhật ký khôi phục; hình `carryover_diagnostic.{png,pdf}` được dựng từ toàn bộ raw.

Phiên lặp lại đã hoàn tất theo tag mới `prereg-laptop-session-confirm-20261107` (`17f2cd6805cbfd4cc636d58aec086209bf59c4cc`), đăng ký sau khi xem kết quả phiên đầu. Production code, 20 cặp ảnh, lịch gọi, 48 lần/nhãn, các ngưỡng và môi trường giữ nguyên. Smoke có 0/4 cờ, full có 0/22 cờ. Full MDE sạch **0,8293578335047918%**, tấn công **0,16818171205488994%**: cả hai đạt ngưỡng 1%. Đủ 3.840 trials, ghim CPU và readback đạt; 45/45 tiến trình ứng dụng được khôi phục đúng, không lỗi. Không có công việc trợ lý khác trong lúc đo.

Phiên hai có tỷ số **4,222968253034303**, CI95% **[4,007657160277586; 4,433075641475105]**; chênh lệch **746,220005 ms**, CI95% **[696,3973888125; 793,6956609375] ms**. Nguồn `sponge-sim/results/laptop_session_confirm_20261107/full_01/P1_cpu2/attack_summary.json` cùng selectors; raw SHA **51ee4e3468231324be1de72a5ed62929068429140fbb979ca313095b0c7f3b24**. Receipt và hình nằm trong `full_01`. Audit xác nhận lịch/context/positions đúng, counts/prediction SHA khớp lượt trước, summary tính lại khớp. Không gộp CI hai phiên vì dùng chung ảnh, attack và lịch. Đây là bằng chứng lặp lại trên một máy trong hai tiến trình/khung thời gian, không phải hai tập ảnh độc lập.

Đã bổ sung `paper_en/segmentation_extension/laptop_cpu.tex`, bảng hai phiên, hình `laptop_sessions.{png,pdf}` và source map giá trị chính xác. Phần này được include từ extension hiện hành; không sửa/stage `paper_en/main.tex` đang dirty từ trước. Chưa build PDF toàn bài vì máy không có TeX engine; đã chạy generator và xem hình xuất ra.

## Phát hiện cần biết

Các lượt trước vẫn giữ nguyên trạng thái:

| Lượt đã đăng ký | Tham chiếu bị cờ | MDE A/A cần biết | Kết luận |
|---|---:|---:|---|
| Clean A/A20 ban đầu | 3/22 | Forward 2,359771%; total 3,089161% | Không đạt |
| HighQoS smoke | 2/4 | n=2, chỉ chẩn đoán | Không đạt; không chạy full |
| AboveNormal smoke | 3/4 | n=2, chỉ chẩn đoán | Không đạt; không chạy full |
| Clean A/A20, tách affinity ứng dụng | 1/22 | Forward 0,596518%; total 0,507288% | Đạt cho clean control |
| Attack, xen đo từng công đoạn | 2/22 | Sạch 1,888700%; tấn công 0,734110% | Không đạt |
| Attack, chỉ tổng, 48 lần/nhãn | 3/22 | Sạch 1,925799%; tấn công 0,435005% | Không đạt |
| Attack, sửa carryover/output lifetime | 1/22 | Sạch 0,996622%; tấn công 0,213432% | Một phiên đạt |
| Lặp lại cùng cấu hình đã sửa | 0/22 | Sạch 0,829358%; tấn công 0,168182% | Phiên thứ hai đạt |

Các source tương ứng nằm trong `laptop_session_sources_20261107.json`. Không gộp các lượt không đạt vào ước lượng đã đạt. Các protocol được sửa sau khi đã thấy dữ liệu cũ; đây là quá trình phát triển harness có công bố lịch sử, không phải thí nghiệm xác nhận toàn bộ từ đầu.

Lịch cũ cân bằng vị trí nhưng nhãn A/B không nhận cùng số lần đứng sau nhánh mask lớn. Đồng thời caller còn giữ output trước trong lúc tính output kế tiếp. Lượt mới cân bằng chính xác theo nhánh trước × vị trí cặp và bỏ giữ output sau vùng đo. Raw xác nhận đúng lịch cả 20 ảnh; counts và hash prediction khớp lượt trước. Vì sửa theo gói, chưa thể quy nguyên nhân riêng cho allocator, cache, thứ tự hoặc lifetime. Phân tích đổi nhãn giả định trên raw cũ chỉ là chẩn đoán hậu nghiệm; không đổi raw hoặc nâng lượt cũ thành đạt.

Đuôi vẫn nhiễu: 24/1.920 lần sạch và 42/1.920 lần tấn công vượt 1,5 lần trung vị cùng ảnh/công đoạn. Tất cả các spike đó có process-CPU/wall <0,75; wall lớn nhất 1.781,5094 ms và 2.668,2196 ms. Không loại các điểm này, không gọi toàn bộ đuôi ổn định, chưa xác định tiến trình gây chờ. PDH báo tần số danh nghĩa 1.300 MHz nhưng performance khoảng 247%; không diễn giải là CPU bị khóa ở 1.300 MHz.

Phiên hai vẫn có 14/1.920 spike sạch, 52/1.920 spike tấn công cùng định nghĩa; tất cả process-CPU/wall <0,75. Wall lớn nhất 2.057,0417 và 3.011,9318 ms. Hai lần đạt cổng cho trung vị không bảo đảm deadline hoặc đuôi dịch vụ. Lệnh khởi động smoke đầu tiên thiếu thư mục cha và dừng trước journal/worker/đổi affinity; lỗi được lưu, chỉ tạo thư mục rồi gọi lại cùng lệnh, không phải chạy lại một smoke đã đo nhưng không đạt.

Renderer cài sẵn chia khối tối đa 32 triệu float pixel rồi trả uint8; đã khớp wheel RECORD. Không dùng giả định mọi mask được materialize đồng thời dưới dạng float để kết luận RAM/OOM. NMS dùng backend torchvision cố định. Lượt total-only này không tách thời gian MASK và NMS; các phép tách công đoạn cũ không đạt cổng tổng thể, chỉ mang tính chẩn đoán.

Một file dùng chung `sponge-sim/src/sponge_sim/hw.py` có CRLF ở working tree, LF trong Git tag do quy tắc Git đã có. Lock trước phép đo ghi SHA chính xác của byte đã thực thi; audit xác nhận khác biệt chỉ xuống dòng và ghi hai SHA trong receipt. Mọi source mới, protocol và lock đều khớp byte tag; không tuyên bố toàn bộ cây nguồn khớp byte nếu bỏ qua ngoại lệ này.

Chưa có bằng chứng về DoS, deadline miss, camera, Pi4/Pi5 hoặc độ ổn định ngoài hai phiên cùng ngày/cùng máy này. 1.500 ảnh trước đó xác nhận số đếm, không nâng cỡ mẫu timing này thành 1.500. A/A sạch phiên đầu rất sát cổng; không làm tròn trước khi xét đạt.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Tiếp tục kiểm cơ chế và CPU nhiều luồng → gõ: “Tiếp tục kiểm cơ chế và nhiều luồng”. Phòng thủ đã hoàn tất theo protocol riêng: pre300 full đạt, out50 smoke không đạt/full hủy; xem `LAPTOP_DEFENSE_20261107.md`.

B. Chuyển sang hoàn thiện supervisor nhiệt/pin và kiểm thread pool điện thoại, chưa chạy tải → gõ: “Tiếp tục hoàn thiện runner A36”.

## Đang chờ gì ở tôi

Không có. Đang tiếp tục theo ủy quyền đã có; điện thoại vẫn cần xác nhận trạng thái thực tế trước phép đo riêng.
