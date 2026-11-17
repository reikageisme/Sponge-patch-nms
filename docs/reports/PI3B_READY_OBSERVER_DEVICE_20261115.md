## Đã xong

- Người dùng duyệt đúng câu hỏi về một ngoại lệ mới: “Duyệt một lượt kiểm chứng mới”. Sự kiện thật tại `sponge-sim/results/pi3b_ready_observer_host_qa_20261115/user_review_event.json`, admission tại `method_approval.json` bind outer tag `qa-pi3b-ready-observer-20261115`/`7c6b8a8a783c51a701c565015e95837c2288626a`, lock SHA và receipt failure cũ. Không suy approval từ goal continuation.
- Triển khai đúng một probe.py vào sidecar mới, không sửa23 file payload. Chạy một driver, handle50023, chỉ chờ handle trong lúc live. Cả năm case normal/mainkill/childkill/timeout/disconnect PASS, driver exit0; nguồn: `qualification_outcomes.json`, `driver_01.log`.
- Thu sau terminal đủ52 file remote-original/47.065 bytes: **44 file mới**, tám file của normal cũ giữ nguyên. SHA/bytes remote-before/local/remote-after khớp; controller23 và observer source khớp tag/source. Nguồn: `transfer_verification.json`, hai remote snapshots, `supervisor_qa_verification.json`.
- Kiểm lại live READY từng case khớp payload receipt/MainPID/InvocationID/child birth, governor powersave/swapOFF/mask và USB phase SHA. Năm InvocationID khác nhau, hai fault intent/sent có thật. Từng case restore RESTORED/errors[], child birth cũ không còn; kiểm độc lập cuối nguồn governor/swap/priority/helper/timer/setup/mask/no-owned-worker đạt. SSH/sshd giữ mở.
- Có39 query receipts, tất cả JSON_RESPONSE_RECEIVED, timeout cap≤25s và không retry. Tổng READY40s, unit-query10s, năm sleep/cap và postterminal predicate giữ như proposal. Không model, NMS, renderer hay endpoint latency/RSS mới trong qualification này.

## Phát hiện cần biết

- Lượt mới đạt **không đổi** lượt cũ CLOSED_INCOMPLETE hoặc bốn case cũ NOT_STARTED. Payload SOURCE vẫn tag925c544; qualification METHOD mới là7c6b8a8. Review `ALL_FIVE_SLEEP_CASES_PASS` ghi rõ hai lớp này, các case mới và `original_failed_verdict_replaced=false`.
- Mainkill frontend exit255 đi kèm fault đã gửi và `status=9/KILL` đúng tiêu chí, không tự quy là lỗi mạng giống sự cố RSS cũ. Case disconnect giữ một cảnh báo journal lúc07:26:00UTC: không mở được transient unit file sau deactivation. Cảnh báo giữ nguyên, chưa chứng minh gây lỗi/cause; các criterion đã đặt trước vẫn đạt.
- Không kết luận sửa observer đã giải thích nguyên nhân timeout cũ. Đây là một lượt sau thay đổi phương pháp có review riêng, không thử nghiệm nhân quả mạng/OS/NMS, không chứng minh khôi phục khi mất điện/kernel treo/arbitrary model.
- Approval mới chỉ cấp ngoại lệ năm sleeping case. Nó không phải approval full NMS hoặc cơ sở tự sinh số hiệu năng. Giai đoạn phần mềm tiếp theo phải có plan/tag riêng, actual review/source/restore này là điều kiện cần; quyền kiểm thử chức năng hữu hạn nằm ở các chỉ dẫn nghiên cứu trước đó, không suy từ PASS hoặc mở rộng câu trả lời hẹp này.

## Việc tiếp theo — chọn 1 trong các cách sau

1. Đóng và lưu qualification mới; không thêm set/QA02. Giữ nguyên mọi file cũ và dữ liệu âm. Review phần mềm thực tế đã có, không tạo receipt PASS giả.
2. Chuẩn bị một lượt material40 theo plan/tag riêng: cùng19 Python bytes, một model resident, fresh/frozen tensor/count/kernel/mask parity, no latency/RSS/AA endpoint. Phải ghi rõ qualification mới7c6b8a8 thay vì giả sử campaign cũ925c544 đạt. Không thay gate, không chọn lại ảnh, dừng không retry nếu lỗi.
3. Worker timing/provider/auditor/native sentry và scientific registration/smoke/full vẫn riêng. Không đưa sleeping QA vào bài như hiệu năng hay DoS.

## Đang chờ gì ở tôi

Không chờ lại quyết định về ngoại lệ READY: đã nhận và đã dùng đúng một lượt. Chưa hỏi duyệt full NMS; chưa có số smoke mới để review.
