# Gói lưu trữ: "Tấn công cạn kiệt tài nguyên qua NMS có thực sự làm chậm bộ phát hiện? Một nghiên cứu đo lường trên CPU ghim lõi"

Gói này đi kèm bản thảo `paper_vi/main_vi.tex` và tài liệu bổ sung `paper_vi/supplement_vi.tex`.

## Nội dung
- `sponge-sim/prereg/`: các tệp đăng ký trước. Tag git tương ứng (tag `prereg-*`) và commit được ghi trong `MANIFEST.json`.
- `sponge-sim/DEVIATIONS.md`: mọi sai lệch, lần đo lại và lỗi phát hiện ra. Các lần đo lỗi vẫn được giữ.
- `sponge-sim/src`, `sponge-sim/studies`, `sponge-sim/tests`: bộ công cụ đo, script chạy, script phân tích, kiểm thử.
- `sponge-sim/results/<run>/*.json`: tệp tóm tắt và manifest của từng lần chạy dùng trong bài.
- `paper_vi/tables/`: script sinh bảng (`make_tables.py`), script kiểm số (`check_numbers.py`) và các bảng đã sinh.
- `MANIFEST.json`: SHA-256 và kích thước của mọi tệp trong gói. Mục `raw_not_copied` liệt kê các bản ghi thô (`raw_*.jsonl`) kèm SHA-256; các tệp này chưa được chép vào gói vì dung lượng lớn.

## Tái tạo bảng từ tệp tóm tắt
```bash
python -X utf8 paper_vi/tables/make_tables.py          # ghi paper_vi/tables/tab_*.tex
python -X utf8 paper_vi/tables/check_numbers.py --all  # phải in "KẾT QUẢ: ĐẠT"
```

## Tái tạo tệp tóm tắt từ bản ghi thô
Cần các tệp `raw_*.jsonl`. Ví dụ:
```bash
python -X utf8 sponge-sim/studies/e11_patch_remeasure/analyze.py sponge-sim/results/e11/<run>
python -X utf8 sponge-sim/studies/e10_reference/analyze.py ...
```
Lệnh đầy đủ của từng lần chạy nằm trong `sponge-sim/PROGRESS.md` của kho mã.

## Phạm vi
Mọi phép đo thời gian chạy trên một CPU laptop (Intel i5-1335U, Windows, chế độ nguồn Balanced, tần số không khoá), với một lõi logic được ghim. Gói không chứa patch đã tối ưu ở dạng công cụ tấn công.
