# Sai lệch so với PREREG_AMD_REVISION_20261128.md và sổ tay HANDOFF_20261128_HAI_MAY.md

Tag: `prereg-amd-revision-20261128` (f7c9140). File này viết TRƯỚC smoke (28/11/2026, giờ UTC ở dòng cuối của lần ghi),
để ngoài commit của tag vì runner yêu cầu HEAD = tag; sẽ commit sau phiên đo, không sửa nội dung đã ghi, chỉ thêm mục mới.

## Trước smoke (môi trường, không đổi code)
1. **Đầu vào nằm trong RAM.** Venv cài đúng `pip install -r results/amd_20261124/full-01/e10/environment.txt`
   (`pip freeze` trùng khớp 40/40 dòng) nhưng chiếm 1,7 GB, chỉ còn 93 MB trên lớp ghi của USB live. Gói
   `inputs_revision_20261128.tar` (sha256 af37f48d…20d6d, khớp) được giải nén vào `/dev/shm/inputs_revision_20261128`
   (tmpfs, 245 MB) và `outputs/`, `yolov8n.pt`, `INPUTS_SHA256.txt` ở gốc repo là liên kết tượng trưng tới đó.
   `sha256sum -c INPUTS_SHA256.txt`: 1403/1403 khớp. Hệ quả: ảnh được đọc từ RAM thay vì từ lớp overlay trên USB;
   đọc ảnh nằm trong thời gian toàn trình. Đợt 24/11 đọc từ overlay (sau lần đọc đầu thì nằm trong page cache).
   Tác giả chọn cách này ngày 28/11 thay vì xóa bản đo cũ trên máy live.
2. **Clone nông, thưa.** `git clone --depth 1 --filter=blob:none --sparse --branch prereg-amd-revision-20261128`,
   sparse-checkout bỏ `sponge-sim/results/` và `figures/` (không runner nào đọc). HEAD = f7c9140 = tag; `git diff HEAD -- sponge-sim` sạch.
3. **Dọn chỗ:** xóa `~/sponge-amd-20261124/outputs` (196 MB, bản chép đầu vào của đợt 24/11, không phải kết quả), được tác giả đồng ý.
4. **Không có tmux** trên máy live: smoke và phiên chính chạy bằng `setsid nohup` thay cho tmux (cùng lệnh `run_revision.sh`).
5. **Đường SSH:** mạng LAN thay cho Tailscale. Ổ D: mount chỉ đọc để lấy gói rồi gỡ trước khi đo.

## Sau phiên chính full-01 (ghi trước khi chạy lại E10-RM)
6. **E10-RM của full-01 hỏng kỹ thuật: hết chỗ trên lớp ghi của USB.** `apt-daily-upgrade.service` (timer mặc định của Ubuntu)
   chạy lúc 06:07:47Z và ghi `/var/cache/apt/srcpkgcache.bin.*` (42 MB); lớp overlay về 0 MB, worker E10-RM dừng lúc
   06:08:19Z với `OSError: [Errno 28] No space left on device` khi ghi raw. Không có `DONE`, `xung_sau.log`, `ALL_DONE`; file
   `runs_full.exit` rỗng (không ghi được). Raw dở dang (15 226 dòng, dòng cuối cắt ngang) giữ nguyên ở `full-01/e10rm`,
   KHÔNG dùng cho phân tích. E9-R và E10-R của full-01 chạy trọn (có `DONE`, cổng xung trước/sau 3575 MHz, 100% busy).
7. **apt-daily chạy trong lúc đo E10-R.** `apt-daily.service` chạy 04:29:51–04:29:56Z (2,4 s CPU, không ghim lõi) giữa phiên
   E10-R (01:55:40–05:29:58Z). Không loại bản ghi nào vì sự kiện này; ghi lại để đối chiếu với các mốc trôi trong phân tích.
8. **Chạy lại E10-RM** theo PREREG ("chạy lại chỉ khi hỏng kỹ thuật"): cùng tag, cùng runner, `RUN_ID=full-02`, chỉ `e10rm`.
   Trước khi chạy: xóa bộ đệm apt dựng lại được (`/var/cache/apt/*pkgcache.bin*`, không phải dữ liệu) và `systemctl stop`
   (không disable, mất hiệu lực khi khởi động lại) các timer apt-daily, apt-daily-upgrade, motd-news, man-db, fstrim.
   Khóa xung từ full-01 vẫn giữ nguyên (không mở khóa giữa hai phiên); cổng kiểm xung của runner chạy lại trước/sau.
   Kết quả full-01 (49 file) đã sao về máy Windows và khớp sha256 trước bước này.
(ghi lần 2: 2026-11-28T08:09:52Z)

## Phân tích (sau phiên đo, 28/11)
9. **Bọc hàm Spearman cho E10-RM.** `analyze_new.py` dừng với `ZeroDivisionError` trên E10-RM vì `minflt` = 0 ở mọi lần đo
   nhánh sạch (Spearman không xác định khi một biến là hằng số). `runs/amd-revision/analysis/analyze_new_safe_spearman.py`
   (viết sau phiên đo) chạy nguyên `analyze_new.py`, chỉ cho `diag.spearman` trả `null` trong trường hợp đó. E10-R chạy
   bằng `analyze_new.py` gốc, không qua lớp bọc.
10. **Gọi b3_e9 trên raw E9-R.** `diag_posthoc.py` ghi cứng đường dẫn raw E9 của 24/11; `analysis/n_harm_e9r.py` nạp nguyên
    module, chỉ đổi `SRC['e9']` sang raw E9-R rồi gọi `b3_e9()` (cùng seed, cùng ngưỡng).
11. **Đầu vào phân tích từ đợt 24/11** (`amd_20261124/full-01/e1/run/{summary.json,raw_P1_cpu2.jsonl}`,
    `aa_linux_20261124/.../aa_{320,640}/summary.json`) được chép vào `/dev/shm/ana_in` từ bản trên máy Windows (sha256 khớp)
    thay vì `git sparse-checkout add`, vì lớp ghi của USB chỉ còn khoảng 140 MB.
12. **Khóa xung đã mở** sau khi sao full-02 về và khớp sha256 (`lock_env.sh unlock 2`); mọi phân tích chạy sau khi mở khóa
    (không đo thời gian).
(ghi lần 3: 2026-11-28T09:09:48Z)
