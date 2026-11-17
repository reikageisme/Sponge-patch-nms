# Sponge Patch: nghiên cứu tải NMS và tính sẵn sàng

Mã nghiên cứu và bằng chứng về tác động của miếng dán đối kháng cục bộ lên số ứng viên, chi phí NMS, chất lượng phát hiện và thời hạn dịch vụ.

[English](README.md) · [Bản thảo](paper/README.md) · [Danh mục bằng chứng](docs/results.md) · [Hướng dẫn mã](experiments/README.md) · [Review](docs/REVIEW/02_code_audit.md)

## Trạng thái khoa học

Testbed đã đo là CPU laptop. Patch được chèn số, EOT là biến đổi phần mềm; chưa xác nhận hiệu lực print-and-camera hoặc hiệu chỉnh trên ARM/edge thật. Tăng số ứng viên và giảm AP chưa đủ để kết luận DoS.

| Cohort đánh giá | Ảnh / seed patch | SG-GA − GA tâm về tỷ số ứng viên | Diễn giải |
|---|---|---|---|
| OLD128 | 128 / 10 | −0,00513; p chính xác=0,15039 | Chưa hỗ trợ ưu thế SG-GA |
| X1-500 | 500 / 10 | −0,02934; p chính xác=0,001953125 | SG-GA thấp hơn GA tâm trên cohort cố định này |

OLD128 nằm trong X1-500. X1-500 là mở rộng cohort sau quan sát, không phải tái lập độc lập. Hai chênh lệch cùng âm; xem [nguồn số và khoảng tin cậy](docs/results.md).

Hai phép chuyển giao cũng tách riêng: OLD128 đo latency tensor đã chuẩn bị trong sáu detector; X2 đo số lượng tại boundary của tám adapter. Faster R-CNN/RetinaNet/SSDlite trong X2 đã qua NMS nội bộ, nên không được gộp thành một chỉ số tải trước NMS.

## Đọc theo việc cần làm

| Bạn muốn làm gì? | Mở ở đâu? |
|---|---|
| Đọc hoặc biên dịch bản thảo hiện tại | [Gói paper nhỏ, tự chứa](paper/README.md) |
| Truy một con số về artifact gốc | [Danh mục bằng chứng](docs/results.md), [changelog bản thảo](docs/REVIEW/06_paper_changelog.md) |
| Hiểu script nào sinh kết quả nào | [Hướng dẫn experiments](experiments/README.md) |
| Xem lỗi mã và khoảng trống khoa học | [Audit code](docs/REVIEW/02_code_audit.md), [gap analysis](docs/REVIEW/04_q1_gap_analysis.md) |
| Đọc benchmark GPU/person cũ | [Review nhánh B riêng](docs/reports/README_REVIEW_VI.md) |
| Xem cấu trúc và đề xuất tên mới | [Tổ chức repository](docs/repository-organization.md) |

## Kiểm nhanh số liệu đã lưu

Từ thư mục gốc, khi đã có evidence bundle cục bộ:

```powershell
python -B -c "import json; from pathlib import Path; d=json.loads(Path('outputs/x1_500img_20261018/analysis.json').read_text(encoding='utf-8')); print(d['primary']['mean'], d['primary']['exact_two_sided_sign_flip_p'])"
```

Kết quả xấp xỉ `-0.0293350981` và `0.001953125`. Lệnh chỉ đọc tổng hợp, không chạy inference hoặc tái đo timing.

Dataset, weights, raw runs, vendor và môi trường phần lớn là artifact cục bộ được Git bỏ qua. Clone GitHub không đồng nghĩa có đủ bằng chứng. Xem [khả năng tái lập](docs/results.md#availability-and-reproduction) trước khi chạy. [REPRODUCE.md](docs/reports/REPRODUCE.md) là ghi chú môi trường lịch sử; khớp package chưa bảo đảm source đúng phiên bản đã đo.

## Cấu trúc đang dùng

```text
paper/           Bản thảo hiện tại, CAS, hình và manifest SHA-256
core/, attack/   Detector, fitness, helper patch và GA cũ
experiments/     Entry points nghiên cứu, evaluator, thống kê, tests
outputs/         Dữ liệu cục bộ, artifacts từng run và tổng hợp dẫn xuất
docs/REVIEW/     Audit bằng chứng, thay đổi bản thảo, quyết định còn mở
scripts/         Kiểm môi trường và tiện ích bảo trì
project_yolov13/  Nghiên cứu GPU/person riêng (nhánh B)
docs/            Mục lục, danh mục bằng chứng, ghi chú theo thời điểm
```

Giữ đường dẫn thí nghiệm hiện có để bảo toàn manifests và lịch sử. [Tài liệu tổ chức](docs/repository-organization.md) phân biệt phần đã thực hiện với các di chuyển còn là đề xuất.

## Tác giả và giấy phép

Phạm Tuấn Anh và Mai Quốc Bảo, HUTECH. Thông tin liên hệ theo bản thảo hiện tại. Mã repository theo [MIT](LICENSE); dữ liệu và tài nguyên bên thứ ba giữ điều khoản riêng. Khi trích dẫn, ghi commit hoặc bản phát hành cụ thể; không gán DOI hay trạng thái xuất bản cho working manuscript.
