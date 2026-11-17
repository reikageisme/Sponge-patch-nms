# Prompt bàn giao cho Codex — PI3B-600MHZ (14/11/2026)

Dán nguyên phần dưới đây cho Codex.

---

Bạn tiếp quản thí nghiệm PI3B-600MHZ của đề tài Sponge Patch trong repo `D:\Sponge-patch-study`
(nhánh `harness/step1`). Đọc `CLAUDE.md`, mục cuối `sponge-sim/PROGRESS.md` và
`sponge-sim/prereg/PREREG_PI3B_600MHZ_20261114.md` trước khi làm gì. Mọi quy tắc cứng trong
`CLAUDE.md` vẫn áp dụng, đặc biệt: không sửa/xóa raw, không đổi cấu hình sau tag, kết quả âm giữ
nguyên, mọi số phải truy được tới dòng raw, trong lúc đo trên Pi không chạy bất kỳ việc gì khác.

## Trạng thái hiện tại

- Board: Raspberry Pi 3B Rev 1.2, SSH `ssh -i ~/.ssh/pi_spongepi tanh@192.168.10.11` (đi qua
  Tailscale subnet; laptop phải bật Tailscale). venv `~/sponge-venv`. sudo không mật khẩu.
- Nguồn thiếu áp (`get_throttled=0x50005`), firmware ép xung 600 MHz. Đây là điều kiện đã khai báo.
- PREREG đã commit và tag: `prereg-pi3b-600mhz-20261114` = commit
  `c80cf8163e71e643acd2708f368f06ba6f349168`. lock.json SHA256
  `c645656a96a8faea160143159fcad7db253f93d6664c3c19baa78ed74e117099`.
- Code: `sponge-sim/studies/pi3b_600mhz/{run.py,campaign.sh,lock.json,analyze.py,parity_ref.py,build_lock.py}`,
  test `sponge-sim/tests/test_pi3b_600mhz.py` (8 PASS). Tham chiếu số đếm laptop (không đo giờ):
  `sponge-sim/results/pi3b_600mhz_20261114/laptop_reference_counts.json`.
- Trên Pi, thư mục `~/sponge-sim/pi3b_600mhz/runs/`:
  - `smoke_01`: 3 phiên đều returncode 0 (chỉ kiểm đường chạy, không gộp vào kết quả).
  - `full_01` (start 03:44Z, end 05:13Z):
    - `pipeline_PI4` returncode 0, raw 806 dòng — phiên CHÍNH, có vẻ hoàn tất.
    - `pipeline_PI1` returncode 1 (thoát sau ~2 phút), `stages_PI4` returncode 1 (~2 phút).
      **Nguyên nhân chưa đọc.** Đọc `runs/full_01/pipeline_PI1.log`, `stages_PI4.log` và dòng
      `aborted` trong raw nếu có.
  - Lưu ý: campaign.sh khôi phục governor `ondemand` nhưng log ghi `swap_total_kb=926716` lúc kết
    thúc (swap đã bật lại, đúng thiết kế).

## Việc cần làm, theo thứ tự

1. Chép NGUYÊN thư mục `~/sponge-sim/pi3b_600mhz/runs/` về
   `sponge-sim/results/pi3b_600mhz_20261114/runs/` (scp -r). Kiểm số dòng/SHA từng raw.jsonl khớp
   hai phía. Không sửa gì trên Pi.
2. Đọc nguyên nhân hai phiên thoát lỗi. Theo PREREG mục 7: chỉ được khởi động lại MỘT lần nếu phiên
   chết TRƯỚC dòng `timing` đầu tiên vì lý do hạ tầng (mất SSH, hết đĩa, lỗi tương tự). Nếu đúng như
   vậy: ghi `sponge-sim/DEVIATIONS.md` (lý do, thời điểm, đã thấy dữ liệu phiên chính chưa), sửa
   nguyên nhân hạ tầng mà KHÔNG đổi run.py/lock.json, rồi chạy lại riêng phiên đó vào thư mục mới
   (ví dụ `full_02`, giữ `full_01`). Nếu lỗi do code/cổng an toàn (nhiệt, bộ nhớ, governor, USB) hoặc
   đã có dòng timing: KHÔNG chạy lại, giữ nguyên là kết quả âm/không đạt và báo.
   Muốn sửa run.py thì đó là thay đổi sau tag: phải dừng lại hỏi người dùng.
3. Chạy `python sponge-sim/studies/pi3b_600mhz/analyze.py sponge-sim/results/pi3b_600mhz_20261114/runs/full_01`
   (phiên chạy lại, nếu có, phân tích riêng). Kiểm `quality_pass` và từng cổng trong `summary.json`.
4. Báo cáo `docs/reports/PI3B_600MHZ_RESULTS_20261114.md` theo khuôn 4 mục của CLAUDE.md:
   H1 (adv/clean toàn trình), H2 (cap/adv), A/A + MDE, tỷ trọng forward, tách NMS/mask, liều K, parity
   với laptop, cổng chất lượng. Mọi số kèm `file:selector`. Ghi rõ "Pi 3B bị firmware ép 600 MHz do
   thiếu áp", không quy đổi sang 1,2 GHz, không so tuyệt đối với laptop/A36, không kết luận DoS.
5. Cập nhật `sponge-sim/PROGRESS.md`, commit nhỏ chỉ các file của việc này (raw kết quả, summary,
   báo cáo, DEVIATIONS nếu có). Không add file ngoài phạm vi, không push.

## Số smoke để đối chiếu (KHÔNG dùng trong bài)

pipeline_PI4 trung vị: sạch 4,37 s, nhiễu 7,46 s, nhiễu+cap 5,69 s, forward 4,28 s.
stages_PI4: mask_adv 3,03 s, mask_clean 0,06 s, nms_adv 0,06 s.

## Dừng và hỏi người dùng khi

Cần sửa code sau tag; hai phía raw không khớp; số liệu mâu thuẫn; cần chạy lại phiên đã có dữ liệu;
Pi không truy cập được.
