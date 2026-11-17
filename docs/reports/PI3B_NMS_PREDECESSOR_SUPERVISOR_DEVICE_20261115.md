## Đã xong

- Người dùng mở lại Tailscale và yêu cầu tiếp tục. Kiểm live thấy client `Running`, self online, subnet router `pve` online và quảng bá `192.168.10.0/24`. SSH strict-host-key tới Pi hoạt động lại. Trước triển khai, xác nhận shared unit inactive/MainPID0, namespace mới chưa có, governor gốc ondemand, swap/helper/timer nhất quán, không có runtime mask. Nguồn: `sponge-sim/results/pi3b_predecessor_supervisor_qa_20261115/connectivity_recovered_01.json`.
- Triển khai đúng 23 file byte-exact của tag `qa-pi3b-nms-predecessor-supervisor-20261115` / `925c544f618491e5b21a3621d77804a10686d111`; kiểm lại source/ref/lock sau upload, không load model. Log: `deploy_after_connectivity_01.log`, `deployment_verification.json`. Lần kết nối timeout trước đây chưa mở phiên thực thi hay triển khai; không phải retry case native.
- Chạy đúng một driver năm tình huống. Driver chỉ mở `qa_normal_01`, rồi dừng ở lỗi quan sát READY qua SSH; không mở bốn case còn lại. Trong thời gian live, chỉ chờ handle driver96320; không git/test/phân tích/đọc raw song song.
- Sau driver lỗi, chỉ đọc trạng thái chính shared unit: inactive/MainPID0, rồi mới thu nguyên bản. Payload normal tự kết thúc với exit0, ExecStopPost ghi RESTORED/errors[]. Đã kiểm độc lập governor, swap topology/priority, timer/helper/setup và mask trở về trạng thái gốc; child cũ không còn cùng birth. SSH/sshd giữ mở.
- Thu đủ tám file gốc, SHA/bytes remote-before/local/remote-after khớp; đủ 23 file source/ref/lock vẫn khớp local/archive/tag và hai lần đọc remote. Kiểm lại 1.814 raw RSS full trước và bibliography không đổi. Nguồn kết luận: `partial_transfer_verification.json`, `device_final_verification.json`.

## Phát hiện cần biết

- **Lượt kiểm giám sát chưa đạt, đã đóng, không retry.** Client nhận `subprocess.TimeoutExpired` sau 25 giây trong `wait_ready -> remote(READY)`. Driver không lưu được `qa_normal_01.ready_observation.json`, không có `device_qa_outcomes.json` đạt đủ năm case. Không được dùng normal exit0 hoặc receipt READY do payload ghi thay cho live observation bắt buộc của driver.
- Phải phân biệt ba điều: payload normal hoàn tất; restore đạt và đã kiểm lại; **toàn bộ qualification năm tình huống không đạt**. Bốn case mainkill, childkill, timeout, disconnect là NOT_STARTED, không phải PASS, không có fault injection ở các case đó. Không tạo QA02, tăng timeout, bổ sung case hoặc sửa source dưới tag cũ để cứu kết quả.
- Nguyên nhân timeout **chưa xác định**. Bằng chứng hiện không tách được trễ SSH/Tailscale khỏi trễ xử lý lệnh READY trên Pi. Không khẳng định do mạng, do hệ điều hành, hay do NMS. Trạng thái inactive/MainPID0 chỉ được dùng xác nhận terminal; `Result=success` của unit đã unload không thay thế frontend/restore/raw.
- Journal giữ nguyên các cảnh báo không mở được transient unit file sau deactivation. Chưa chứng minh chúng gây timeout. `activation_probe.json` có returncode1 với thông báo swap unit bị mask: đây là hành vi chặn bật swap được mong đợi, không phải lỗi renderer/model.
- Không có Torch/scipy trong receipt READY của sleeping payload, không forward/model/NMS/mask hay endpoint RSS/latency mới. Giá trị operational runtime trong frontend không phải độ trễ thuật toán. NMS component FAIL/PI1 chưa chạy/pilot FAIL và RSS full PASS cũ đều giữ nguyên.
- Không tạo `supervisor_qa_verification.json` PASS hoặc `functional_activation.json`. Base flags functional/scientific/empirical vẫn false. Bước material40 và scientific smoke/full chưa được mở.

## Việc tiếp theo — chọn 1 trong các cách sau

1. Giữ nguyên campaign đã đóng và tám raw; mọi điều tra thêm chỉ đọc dữ liệu đã có hoặc code offline. Tình trạng kết nối đã khôi phục, không yêu cầu người dùng bật lại SSH hay reset mạng.
2. Chuẩn bị thay đổi cách quan sát READY thành proposal/code/test cụ thể nếu cần; nêu rõ thiết kế sau failure và quan hệ với deadline đã khóa. Không tự tăng timeout hay chạy lại qualification dưới tên khác. Cần review phương pháp mới trước một lượt thiết bị mới nếu proposal thay quy tắc đã thất bại; không sửa phán quyết cũ.
3. Có thể tiếp tục hoàn thiện worker/reference/kiểm ghim lõi/auditor bằng mock và dữ liệu giả offline. Chúng không mở tải thiết bị khi supervisor/material còn thiếu, không biến 100 host tests PASS thành native qualification.

## Đang chờ gì ở tôi

Không cần mở lại mạng/SSH: đã truy cập được Pi. Chưa yêu cầu duyệt full NMS; cần xử lý và trình bày proposal kiểm chứng trước. Quy tắc dừng nằm trong `sponge-sim/prereg/QA_PI3B_NMS_PREDECESSOR_SUPERVISOR_20261115.md`: “Exactly one set of five sleeping cases; stop at first unexpected failure, no retry/QA02.”
