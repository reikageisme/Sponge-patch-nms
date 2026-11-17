# Rà cổng còn thiếu của nghiên cứu — 07/11/2026

## Đã xong

Đã đối chiếu các ưu tiên bàn giao, review của GVHD, summary/receipt hiện có và bản tiếng Anh đang làm. Không chạy model hoặc benchmark mới. Bảng kiểm 11 yêu cầu cùng SHA và selector nguồn nằm tại `research_readiness_20261107_01/evidence_matrix.json`; trạng thái chung **chưa chứng minh hoàn tất nghiên cứu**.

Đã sửa generator phụ lục để giữ bắt buộc cả năm phần: nghiên cứu số đếm mở rộng, CPU toàn trình, phòng thủ, công đoạn thất bại và trace forward. Thiếu bất kỳ phần nào sẽ dừng trước khi ghi bản phụ lục, thay vì âm thầm bỏ kết quả. Dựng thử trong thư mục tạm tạo lại đúng byte `extension.tex` hiện hành; raw và biểu đồ cũ không bị ghi lại. Bảng `sources.json` đã thêm hai phần mới.

Đã bổ sung lệnh kiểm số tiếng Anh trước đây bị thiếu:

```powershell
python paper_en/tables_q3/check_numbers_en.py
```

Lệnh xác nhận **12 bảng và 815 mục số/nguồn** khớp một lần sinh lại trong bộ nhớ từ các summary đã lưu. Nó kiểm cả registry nguồn, nên phát hiện được trường hợp sửa sai nguồn dù chữ số và bảng trông vẫn giống nhau. Phạm vi này chưa chứng nhận mọi câu diễn giải, tính đúng của nghiên cứu hay layout PDF.

41 tests CPU/phụ lục đạt trong 5,02 giây. Ba tests bổ sung kiểm việc giữ kết quả âm, dừng khi thiếu phần âm và phát hiện sai registry. Checker cấu trúc hiện có tìm thấy 31 citation dùng và 31 mục bibliography, không thiếu citation/label, không trùng label, môi trường cân bằng. Kiểm phụ thuộc tìm đủ các input và 13 hình của bản đang làm. Nguồn và stdout: `research_readiness_20261107_01/paper_artifacts.json`.

## Phát hiện cần biết

### Dữ liệu nhiều hơn chưa đồng nghĩa mọi cổng đã đóng

| Hạng mục | Bằng chứng hiện tại | Phần còn thiếu |
|---|---|---|
| NMS biến động | Đã xác định dispatch phụ thuộc import; backend mới được cố định | Tách công đoạn mới chưa đạt chất lượng: NMS full FAIL, MASK smoke FAIL |
| Timing tấn công CPU | Hai phiên toàn trình đạt trên cùng 20 cặp ảnh PGD | Không phải 1.500 ảnh timing, patch nhỏ, nhiều thiết bị hay kiểm chứng đuôi dịch vụ |
| CPU nhiều core/GPU | Đối chứng mask tổng hợp CPU4 và GPU đạt | Chưa có timing tấn công phân đoạn thật đạt trên CPU nhiều core; xác nhận GPU thật đã lưu vẫn không ổn định |
| Phòng thủ | Pre-NMS cap 300 có timing CPU ghép cặp đạt | Output cap 50 trượt smoke; chưa attacker thích ứng hoặc accuracy–latency cùng preprocessing/ngưỡng |
| COCO đầy đủ | Tám cấu hình đều ghi 5.000 ảnh; metric replay khớp | Metric Ultralytics từ polygon label; không tự gọi là COCO API đánh giá lại độc lập |
| YOLO26 native | Hoàn tất 1.500 ảnh × năm khởi tạo × bốn hướng số đếm | Zero transfer không phải miễn nhiễm; số đếm không chứng minh DoS |
| Patch thật | Manifest patch cũ đã có 100 ảnh tối ưu; phần này không còn “chỉ bốn ảnh” | Đo lại timing patch E11 vẫn trượt; PGD toàn ảnh phân đoạn không thay cho timing patch nhỏ/universal/physical |
| A36/Pi | Có metadata A36 và code guard/sampler kiểm offline | Chưa SOC/sạc live, registry nhiệt, runtime import và QA supervisor thực trên máy; chưa có đo Pi |
| DoS | Có timing tensor và số đếm trong phạm vi đã nêu | Chưa thử dịch vụ phân đoạn có lịch phát/deadline được kiểm chứng |

Các trạng thái trên được đọc từ gate hiện hành: hai `attack_summary.json` của CPU đạt; hai `summary_verified.json` của mask CPU4/GPU đạt; `stability_full_20261106/confirmation_summary.json:stable=false`; nhánh phòng thủ và công đoạn giữ nguyên FAIL. Không đánh giá lại các gate bằng bộ tiêu chí mới.

Cập nhật sau audit: đã chạy một smoke mới trên hai P-core với worker toàn trình đã sửa; kiểm ghim đạt nhưng 2/4 tham chiếu bị cờ, full bị hủy. Xem `LAPTOP_PCORES_20261107.md`. Đã có thêm raw chẩn đoán nhiều core, còn yêu cầu timing nhiều core đạt chất lượng vẫn chưa hoàn tất. Generator hiện giữ bắt buộc thêm phần âm này, tổng cộng sáu phần phụ lục.

Manifest `sponge-sim/results/e7_gpu/final/runs/e7/manifest.json:train_images` có đúng 100 ảnh. Đó là track patch lịch sử; không nhầm với năm khởi tạo của nghiên cứu phân đoạn. Yêu cầu tăng tập tối ưu đã có bằng chứng ở track này, nên không cần chạy lại chỉ vì review cũ nói bốn ảnh.

### Đã kiểm cutoff bằng từng lượt raw

Đọc riêng các record `backend=ultra_native` có `nms_ns`:

| Tập raw lịch sử | Record | NMS lớn nhất | Số interval trên 2,05 giây | Đầu vào NMS lớn nhất |
|---|---:|---:|---:|---:|
| E1 dose-response | 3.690 | 183,0205 ms | 0 | 10.000 |
| E9 tiêm toàn pipeline | 3.540 | 139,1663 ms | 0 | 8.400 |

E9 có total lớn nhất 620,5514 ms, cũng dưới 2,05 giây. Đây là quan sát trên mọi record đã chọn, không suy từ trung vị. Manifest ghi `max_nms=30000` và công thức time limit `2.0+0.05*batch`. Nguồn SHA, bộ lọc và dòng raw của từng cực đại: `research_readiness_20261107_01/cutoff_saved_raw.json`. Không có log trực tiếp nhánh cutoff/warning bên trong thư viện, nên không tuyên bố đã quan sát trạng thái nhánh đó.

### Bản thảo và khả năng dựng lại còn việc phải làm

Bản đang làm gồm hai phạm vi: nghiên cứu NMS lịch sử và phần phân đoạn mới. Một số câu chung về “không có accelerator/NMS-free”, “không hiệu chỉnh nhiều kiểm định”, Balanced mode và kiểm mọi số trong Results cần phân biệt hai phạm vi. Đã chuẩn bị sáu chỉnh sửa nhỏ tại `research_readiness_20261107_01/manuscript_scope_proposal.patch`; `git apply --check` đạt trên bản hiện tại. **Chưa áp dụng**, chưa sửa/stage `paper_en/main.tex` hoặc bibliography đang có nhiều thay đổi từ trước. Tiêu đề, tác giả và nội dung sửa trước đó được giữ nguyên.

Snapshot ban đầu tìm thấy 14 phụ thuộc dựng bài chưa được Git theo dõi: 12 bảng, registry số và style bibliography. Các bảng/registry đã được đối chiếu nguồn trước khi đưa vào phạm vi lưu lại; không sửa nội dung của chúng. Không dùng việc “có file trong máy” làm bằng chứng rằng một checkout mới đã chứa đủ phụ thuộc. Cả 14 phụ thuộc này đã được commit nguyên byte trong `85d921c`; receipt sau commit nằm tại `research_readiness_20261107_01/tracking_followup.json`. Bản main/bibliography/hình đang sửa từ trước không được đưa vào commit này.

Chưa tìm thấy `xelatex`, `pdflatex`, `lualatex`, `tectonic` hoặc `latexmk` trên PATH; chưa build/render PDF toàn bài. Kiểm cấu trúc và xem riêng biểu đồ không thay thế bước này. Audit này cũng chưa xác minh mới toàn bộ nội dung tài liệu tham khảo, timestamp/DOI công khai hoặc khả năng được Q1 chấp nhận; không thực hiện tải/cài đặt hay xuất bản ra bên ngoài.

## Việc tiếp theo — chọn 1 trong các cách sau

A. Tiếp tục trục CPU nhiều core bằng một thiết kế hữu hạn mới, giữ mọi FAIL cũ và không chọn core theo kết quả → gõ: "Tiếp tục trục CPU nhiều core".

B. Ưu tiên điều kiện đo A36 trước tải thật → gõ: "Gỡ nguồn pin/nhiệt A36".

C. Rà bản vá sáu đoạn phạm vi và chốt bản thảo trước khi dựng PDF → gõ: "Rà bản vá phạm vi bài tiếng Anh".

## Đang chờ gì ở tôi

Chưa cần thao tác để tiếp tục code/đối chiếu offline hoặc chuẩn bị trục CPU đã được ủy quyền. Máy thuê đã xóa; A36 chưa đủ điều kiện tải. Những điểm thiếu thiết bị, cảm biến hoặc công cụ dựng PDF vẫn phải ghi là thiếu; không thể lấp bằng tăng số ảnh hay tăng số lần chạy trên cùng cấu hình.
