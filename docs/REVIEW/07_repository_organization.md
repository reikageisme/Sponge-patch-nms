# 07 — Tổ chức repository: receipt và đề xuất tên

Ngày21/10/2026. Branch `codex/repository-organization`. Scope: presentation/documentation và self-contained manuscript package; không chạy research experiments, không di chuyển/xóa raw/source cũ, không commit/push hoặc đổi tên GitHub.

## Yêu cầu và kết quả triển khai

| Yêu cầu | Kết quả cụ thể | Bằng chứng |
|---|---|---|
| Repo có lối đọc gọn, khoa học | README Anh/Việt ngắn, cùng phạm vi khoa học; entry docs phân biệt current/historical | README.md,README.vi.md,START_HERE_VI.md,docs/README.md |
| Tách paper khỏi workspace dữ liệu lớn | paper/main.tex +figures+CAS+thumbnails+source manifest | paper/source_manifest.json và paper/README.md |
| Không trộn cohort/metric | Danh mục OLD128/X1/X2/X5/B, raw vs derived, data availability | docs/results.md và experiments/README.md |
| Đề xuất tên folder/GitHub | sponge-patch-study; hai phương án thay thế, About/topics, mapping thư mục | docs/repository-organization.md |
| Giữ lineage và thay đổi dirty có trước | Snapshot sáu file presentation trước sửa; baseline hashes cho1769file khác | _provenance/documentation_before_organization_20261021/snapshot.json |
| Giữ scope remote | origin=forksudo-baoz;upstream=reikageisme; chỉ đề xuất, chưa rename | git remote -v; docs/repository-organization.md |

## Evidence → finding → action

- Evidence: README public gọi physical DoS/EdgeAI, trong khi REVIEW và saved results chỉ hỗ trợ laptop/software evaluation. Finding: tên/mô tả public mạnh hơn bằng chứng. Action: thay lời giới thiệu cục bộ, đề xuất slug trung tính và About phản ánh study. Nguồn public: https://github.com/reikageisme/Physical-Visual-DoS-EdgeAI (đọc21/10/2026).
- Evidence:235kfiles/45.4GiB trong kiểm kê trước, nhiều data/runtime và reviewer builds; compiler từ chối root quá lớn. Finding: manuscript cần package riêng. Action: paper/ chỉ đóng gói các includegraphics và CAS cần thiết, không copy dataset/venv.
- Evidence: `.gitignore` bỏ mọiPNG nên paper figures sẽ mất trong clone nếu không có exception. Finding: đủ file local chưa đủ publishability. Action: thêm exception chỉ paper/figures; không unignore datasets/raw runs.
- Evidence: core/experiments và manifests chứa đường dẫn lịch sử, X5 còn đọc weights nhánhB. Finding: đổi tên code/data ngay sẽ phá replay. Action: giữ path, cung cấp mapping di chuyển để duyệt; không gán plan thành implementation.

## Cách áp dụng skill

Dùng docs-generator cho task-oriented README/index. Tool-index ở vị trí sibling mặc định thiếu, đã tìm và đọc bản reverse-skill/tool-index.md; task này không cần tool reverse/security hoặc bootstrap. Quy tắc viết của phiên được ưu tiên; không giả lập skill ce:writer chưa có trong catalog. ARS evidence discipline được giữ cho số liệu và các giới hạn.

## Kiểm chứng cuối

Đã kiểm trực tiếp, không chạy inference/training hoặc test suite có ghi outputs:

| Kiểm tra | Kết quả / phạm vi |
|---|---|
| Biên dịch gói mới | `compile_latex_document(paper/,mainFile=main.tex)` trả **success**; compiler tích hợp. Không export PDF mới, warnings bản thảo vẫn theo REVIEW/06. |
| Bảo toàn trước sửa | **1769/1769** protected SHA-256 khớp baseline: tracked files ngoài sáu file presentation cho phép sửa, bổ sung first-party Python, manuscript và selected run manifests/analysis. Không tuyên bố đã hash toàn bộ48GB. |
| Gói paper | **18/18** file hashes khớp manifest, manifest không tự hash chính nó; file includegraphics/CAS/icons đầy đủ. Tổng package **1.237.997bytes** tại lúc kiểm. |
| Nội dung bản thảo | Đảo đúng tám path `figures/→RECOMMENDED/` khôi phục nguyên text v2 root. Root v2 và bản thảo gốc đều được baseline bảo toàn. |
| Markdown | **87** local link targets tồn tại trên12entry docs, không ký tự replacement, code fences cân bằng. |
| Git eligibility | Tất cả19file package (gồm manifest) không bị ignore. TámPNG có exception riêng; dùng `git check-ignore --stdin -z` với binary NUL-delimited input để tránh CRLF Windows. |
| Local artifacts | Review build, outputs X1 và venv vẫn được ignore; không untrack hoặc xóa file nào. |
| Lệnh đọc số | Primary X1 mean−.029335098118660065; exactp.001953125, khớp README. Chỉ đọc JSON đã lưu. |
| Remote | `git remote -v` khớp snapshot; origin=forksudo-baoz,upstream=reikageisme; chưa sửa remote/GitHub. |
| README | Anh326→60dòng;Việt276→60dòng. Nội dung trước sửa giữ snapshot, không xóa lịch sử. |

Các phép kiểm bao phủ lối đọc và package đã tổ chức, không chứng nhận research code không còn lỗi, không tái lập toàn bộ study. Di chuyển code/data chỉ có đề xuất và không bị gán nhãn đã làm.

## Phần chưa áp dụng theo thiết kế

Tên folder local/GitHub và các di chuyển legacy là **đề xuất** đúng phạm vi yêu cầu; chưa đổi tên thực tế. Nhóm G1–G4 của review trước chưa được duyệt để di chuyển/xóa. Không công bố evidence bundle/DOI, không quảng bá đã có benchmark mới hoặc DoS vật lý. Bản v2 có warnings layout/glyph đã ghi ở REVIEW/06; đóng gói không sửa kết luận hoặc che các warnings đó.

## Phạm vi thay đổi

Sáu file hiện có được sửa: README.md,README.vi.md,START_HERE_VI.md,README_REVIEW_VI.md,REPRODUCE.md,.gitignore. File mới: docs/README.md,docs/results.md,docs/repository-organization.md,experiments/README.md,outputs/README.md,paper/ package và receipt này. Backup presentation ở _provenance/documentation_before_organization_20261021. Không sửa .gitattributes/LICENSE, code thí nghiệm, raw dataset/predictions/timing/weights hoặc source manuscript root.

Không tạo goal con, automation hoặc PR; không commit/push. Tên đề xuất cho local folder và GitHub cùng là **sponge-patch-study**. About/topics và các bước đổi đúng remote đã chuẩn bị trong docs/repository-organization.md; việc chọn/áp tên mới thuộc lượt tác giả quyết định, vì yêu cầu hiện tại là gợi ý tên.

## Completion audit theo yêu cầu hiện tại

- Tổ chức lối đọc khoa học: đã có README ngắn song ngữ, danh mục evidence và hướng dẫn code có quantity/boundary/cohort; links kiểm trực tiếp.
- Tổ chức artifact thực tế: có paper/ tự chứa, figures/ chuẩn hóa, manifest và compile success; không chỉ dừng ở sơ đồ đề xuất.
- Gợi ý đổi folder/GitHub: có tên ưu tiên, alternatives, lý do, About/topics, remote mapping đúng fork/upstream và hướng dẫn GitHub chính thức.
- Bảo toàn lịch sử/giới hạn từ review: có snapshot/hashes, không di chuyển nhóm cần duyệt, không thay study code hoặc các số đã lưu.
