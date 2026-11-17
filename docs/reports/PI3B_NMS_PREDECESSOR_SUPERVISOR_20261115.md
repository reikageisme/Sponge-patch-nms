## Đã xong

- Khóa bộ giám sát mới dưới tag `qa-pi3b-nms-predecessor-supervisor-20261115`, commit `925c544f618491e5b21a3621d77804a10686d111`, trước khi thử triển khai. Gói có 19 file Python, ba tài liệu tham chiếu và controller lock; 23 file khớp byte giữa source, bản lưu và Git tag. Nguồn: `sponge-sim/results/pi3b_predecessor_supervisor_qa_20261115/source_preparation.json`, `offline_final_verification.json`.
- Có 64 kiểm thử host đạt trước tag; bổ sung năm kiểm thử lỗi watchdog sau tag, tổng 69 đạt. Năm trường hợp bổ sung kiểm kết thúc bình thường, mã lỗi con, timeout, guard dừng và terminate phải nâng lên kill; kiểm receipt và thu hồi con. Chỉ dùng tiến trình/đồng hồ giả, không phải kiểm chứng tải thật trên Pi. Log nguyên: `host_checks_01.log`, `host_checks_02.log`; test mới `sponge-sim/tests/test_pi3b_predecessor_campaign.py`. Không đổi source đã khóa sau tag.
- Giữ nguyên AST của System/Lease/guard/USB từ bộ giám sát đã kiểm trước. Entrypoint mới chỉ có sleeping QA và functional; chưa có scientific timing mode. Activation functional chưa tồn tại, cờ scientific/empirical đều false.
- Chuẩn bị script triển khai một lần vào workspace mới, driver năm tình huống sleeping và collector sau terminal. Chuẩn bị riêng bản nháp kiểm 40 bộ tensor trước phép đo NMS; chưa kích hoạt hay gắn tag cho bước này.
- Kiểm lại đủ 1.814 file gốc của RSS full trước: kích thước và SHA vẫn khớp manifest; bibliography vẫn nguyên SHA đã bảo vệ. Script tái kiểm chỉ đọc: `verify_offline.py`. Không chạy lại full RSS đã hoàn tất.

## Phát hiện cần biết

- **Chưa chạy được QA native mới.** Một lần gọi `prepare_device.py` dừng với `ssh: connect to host 192.168.10.11 port 22: Connection timed out`, trước khi mở phiên SSH thực thi. Không có receipt triển khai hay case native mới; không tuyên bố đã đọc lại trạng thái Pi. Lỗi và vị trí transcript lưu trong `connectivity_failure.json`.
- Kiểm Tailscale cục bộ thấy không có peer; snapshot lưu sau timeout có `BackendState=NoState`, `Self.Online=false`. Trạng thái tức thời trước đó khác; chưa xác định nguyên nhân mất tuyến. Không đổi cấu hình mạng hay tắt sshd.
- Sleeping QA chưa được thực hiện, nên bộ giám sát mới chưa đủ điều kiện mở tải model. Kiểm host không thay thế việc xác minh khôi phục governor/swap/timer/helper/mask trên Pi thật. Không tạo receipt PASS hoặc activation để đi vòng.
- Bộ sao chép tensor mới khởi tạo phần đệm storage bằng zero trước khi xuất view có stride; tránh đưa byte heap chưa khởi tạo vào file. Giá trị logic, stride và offset giữ nguyên; đây không phải số đo tối ưu hiệu năng. Thay đổi có trước native material/timing mới; nguồn cũ không sửa.
- Lần kiểm offline đầu dùng thiếu thư mục `original` trong đường dẫn RSS, gặp FileNotFoundError. Sửa đường dẫn ở script kiểm mới, không sửa raw hay phương pháp; lưu `offline_audit_path_correction.json`. Lần kiểm đúng đường dẫn đạt đủ 1.814 file.
- Kết quả NMS A/A/MDE FAIL và PI1 chưa chạy của protocol full20 cũ giữ nguyên. RSS full đã đạt chỉ hỗ trợ kết luận bộ nhớ trong điều kiện đã đăng ký; không chứng minh cơ chế NMS, độ trễ hay DoS. Không có số hiệu năng mới từ phiên chuẩn bị này.

## Việc tiếp theo — chọn 1 trong các cách sau

1. Khi tuyến tới Pi hoạt động lại, kiểm workspace/unit/context bằng thao tác chỉ đọc trước. Timeout kết nối hiện tại chưa mở case hay triển khai file, không phải căn cứ tạo lần đo thứ hai. Nếu có trạng thái từ nguồn khác, dừng đối chiếu trước khi triển khai.
2. Triển khai đúng 23 file tag `925c544`, chạy đúng một driver năm sleeping case theo `QA_PI3B_NMS_PREDECESSOR_SUPERVISOR_20261115.md`. Chỉ chờ driver khi live; không đọc raw/git/test song song. Dừng ở lỗi đầu tiên, giữ partial, không retry/QA02. Sau terminal mới lấy nguyên bản và kiểm SHA/restore độc lập.
3. Chỉ sau bằng chứng thực tế đạt mới chốt kế hoạch/tag functional 40 case và activation. Bản nháp: `sponge-sim/prereg/DRAFT_QA_PI3B_NMS_PREDECESSOR_MATERIAL_20261115.md`. Sau functional còn thiếu worker timing, warmup/reference/pool sentry, analyzer, scientific PREREG/tag và smoke thực tế trước bước full cần duyệt riêng.

## Đang chờ gì ở tôi

Khôi phục đường kết nối tới Pi: kiểm nguồn, LAN và tuyến Tailscale rồi báo khi SSH truy cập được. Câu hỏi đã gửi trong phiên. Không cần duyệt lại RSS full đã chạy; chưa đề nghị duyệt full NMS mới khi chưa có smoke.
