# Sổ tay 28/11/2026: hai máy, một việc (máy đo AMD chạy Xubuntu live + laptop SSH vào)

Đọc file này ĐẦU TIÊN khi mở phiên Claude Code mới trên laptop. Câu mở phiên gợi ý (copy-dán):

> Đọc docs/HANDOFF_20261128_HAI_MAY.md trên nhánh amd-replication-20261124 và làm tiếp từ mục "Đang ở bước nào". Máy đo là Xubuntu live, SSH: `ssh xubuntu@<IP Tailscale>`. Tuân thủ mục "Quy tắc bắt buộc".

## 1. Hai máy là gì

| | Máy đo (desktop AMD) | Laptop |
|---|---|---|
| Phần cứng | Ryzen 5 5500, RAM 3,9 GB, ổ `D:` (NTFS, nhãn "Data") chứa repo gốc `D:\Sponge-patch-study` | máy của bạn ở trường |
| Hệ điều hành khi đo | **Xubuntu 24.04.5 live từ USB**, mọi thứ nằm trong RAM: tắt máy là MẤT hết | bất kỳ, có Claude Code + SSH |
| Vai trò | chỉ chạy đúng tiến trình đo | soạn lệnh, ra lệnh qua SSH, nhận kết quả về |
| Bình thường (không đo) | chạy Windows; đây là máy đã soạn kế hoạch 27/11 | |

Một việc duy nhất ngày 28/11: chạy đợt đo lại theo góp ý của thầy (E9-R lưới N mịn, E10-R đo lại YOLOv5s, E10-RM thăm dò),
rồi mang kết quả về. Kế hoạch tổng: `docs/KE_HOACH_SUA_PHAN_BIEN_20261127.md`. Lý do đo lại: `docs/reports/REVIEW_B_POSTHOC_20261127.md`.
PREREG nháp: `sponge-sim/prereg/DRAFT_PREREG_AMD_REVISION_20261127.md`.

## 2. Quy tắc bắt buộc (tóm tắt CLAUDE.md của repo gốc; file đó không có trên nhánh này)
1. Không xóa, di chuyển, ghi đè dữ liệu thô hay kết quả đã chạy (`outputs/**`, `sponge-sim/results/**`). Ổ `D:` chỉ mount **read-only**.
2. Không sửa code cũ (`core/`, `attack/`, `experiments/`, runner cũ trong `sponge-sim/studies/`). Runner mới đã là bản sao có ghi nguồn.
3. Mọi con số phải truy được tới dòng raw. Kết quả âm giữ nguyên. Không nói "tương đương/chứng minh" khi chỉ có p > 0,05 hoặc CI chứa 0.
4. PREREG + `git tag` TRƯỚC khi đo. Sai lệch ghi vào `sponge-sim/prereg/DEVIATIONS_AMD_REVISION_<ngày>.md`.
5. Claude không cài gói, không đổi cấu hình hệ thống: chỉ in lệnh cho người dùng tự gõ (cài SSH/Tailscale/venv, mount, khóa xung).
   Ngoại lệ: Claude được chạy `lock_env.sh` (đã có trong repo) khi người dùng bảo, vì đó là bước của giao thức.
6. **Trong lúc đo, Claude chỉ được để đúng tiến trình đo chạy.** Không SSH vào đọc log, không chạy việc khác trên máy đo,
   không poll. Chờ hết thời gian ước tính rồi mới kiểm `ALL_DONE` bằng MỘT lệnh. Người dùng không dùng máy đo.
7. Chỉ `git add` đúng file của việc đang làm. Không reset/clean/force-push. Claude không gõ mật khẩu hay mã xác thực.

## 3. Đang ở bước nào (cập nhật mục này mỗi khi xong một bước)
- [x] 27/11 Windows: kế hoạch, nhóm A (sửa bài, commit `b8968be`), nhóm B (phân tích lại), runner E9-R/E10-R, PREREG nháp, gói đầu vào.
- [ ] Đẩy nhánh `amd-replication-20261124` lên GitHub (chờ người dùng đồng ý).
- [ ] 28/11 sáng, tại nhà: khởi động live, mở đường SSH (mục 4).
- [ ] Chốt PREREG (ngưỡng gây hại), commit, tag, push (mục 5).
- [ ] Dựng môi trường đo trên live (mục 6).
- [ ] Smoke → người dùng duyệt → phiên chính (mục 7).
- [ ] Mang kết quả về, kiểm SHA-256 hai phía, rồi mới tắt máy live (mục 8).

## 4. Sáng 28/11 tại nhà, NGƯỜI DÙNG tự làm trên máy đo (trước khi đi học)
Trên Windows trước khi khởi động lại: tắt hẳn bằng Shift + Shut down (để ổ D: không ở trạng thái ngủ đông, mount được).
Khởi động từ USB Xubuntu, chọn "Try Xubuntu". Mở Terminal:

```bash
# 1. Không cho máy ngủ/khóa màn hình (Settings > Power Manager: Never), rồi kiểm mạng có Internet.
# 2. SSH server và mật khẩu cho user live
sudo apt update && sudo apt install -y openssh-server tmux
passwd            # tự đặt mật khẩu tạm cho user xubuntu
# 3. Đường vào từ trường: Tailscale (đăng nhập bằng tài khoản Tailscale của bạn)
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
tailscale ip -4   # GHI LẠI địa chỉ 100.x.y.z này
```

Từ laptop (có thể làm ngay ở nhà để chắc chắn): `ssh xubuntu@100.x.y.z`, gõ mật khẩu, rồi `ssh-copy-id xubuntu@100.x.y.z`
để lần sau vào bằng khóa. Mỗi lần live khởi động lại, host key đổi: xóa dòng cũ trong `known_hosts` của laptop cho IP đó
(`ssh-keygen -R 100.x.y.z`), kiểm vân tay mới in trên màn hình máy đo bằng `ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub`.

## 5. Chốt PREREG (làm trên laptop hoặc ngay trên máy đo, TRƯỚC smoke)
1. Người dùng chốt ngưỡng gây hại (đề xuất 1,667 ms = 5% khung 30 FPS; độ nhạy 3,333 ms) và kiểm các mục "CHỜ CHỐT".
2. Đổi tên `DRAFT_PREREG_AMD_REVISION_20261127.md` → `PREREG_AMD_REVISION_20261128.md`, sửa trạng thái thành có hiệu lực,
   ghi `pip freeze` của venv (mục 6) vào file.
3. `git add` đúng file đó, commit, `git tag prereg-amd-revision-20261128`, push nhánh và tag.
Nếu sau tag phải sửa runner (ví dụ smoke lỗi): ghi DEVIATIONS, commit, tag mới `-r1`, như đợt 24/11.

## 6. Dựng môi trường đo trên live (NGƯỜI DÙNG gõ các lệnh cần mạng; phần còn lại Claude có thể chạy qua SSH)
```bash
mkdir -p ~/ws && cd ~/ws
git clone -b amd-replication-20261124 https://github.com/reikageisme/Sponge-patch-nms.git repo
cd repo && git checkout prereg-amd-revision-20261128          # đúng tag đã chốt
# venv cùng phiên bản đợt 24/11 (cần mạng, người dùng tự chạy)
python3 -m venv .venv
.venv/bin/pip install --extra-index-url https://download.pytorch.org/whl/cpu -r sponge-sim/results/amd_20261124/full-01/e10/environment.txt
# đầu vào từ ổ D: (chỉ đọc). Tìm phân vùng nhãn "Data" bằng lsblk -f
sudo mkdir -p /mnt/d && sudo mount -o ro /dev/<phân-vùng-Data> /mnt/d
cp /mnt/d/Sponge-patch-study/transfer/inputs_revision_20261128.tar ~/ws/
sha256sum ~/ws/inputs_revision_20261128.tar   # phải là af37f48d36ad24a65536c089f09f2aa13f2da89295aaa39d34bdf842f5b20d6d
tar -xf ~/ws/inputs_revision_20261128.tar -C ~/ws/repo && (cd ~/ws/repo && sha256sum -c --quiet INPUTS_SHA256.txt && echo INPUTS_OK)
rm ~/ws/inputs_revision_20261128.tar          # giải phóng RAM (bản gốc vẫn ở D:)
sudo umount /mnt/d
free -m; swapon --show                        # không được có swap/zram
```
Nếu `pip install -r` lỗi vì một gói không còn trên PyPI: dừng, báo lại, ghi DEVIATIONS; không tự đổi phiên bản torch/torchvision/ultralytics.

## 7. Khóa xung, smoke, phiên chính
```bash
cd ~/ws/repo
sudo bash sponge-sim/studies/linux_profile/lock_env.sh lock 2 3600000 --global-boost --seconds 35
# smoke (khoảng 15-25 phút): chạy trong tmux để mất SSH không giết tiến trình
tmux new -d -s smoke 'PREREG_TAG=prereg-amd-revision-20261128 RUN_ID=smoke bash sponge-sim/studies/linux_profile/run_revision.sh smoke > runs_smoke.out 2>&1'
```
Sau khoảng 30 phút, MỘT lệnh: `ls ~/ws/repo/runs/amd-revision/smoke/ALL_DONE && tail -3 ~/ws/repo/runs_smoke.out`.
Claude tóm tắt smoke (thời gian thật, số bản ghi, kiểm xung trước/sau, page fault có ghi không), DỪNG, chờ người dùng duyệt.

Phiên chính (ước lượng E9-R 0,9 h + E10-R 3,5-4 h + E10-RM 0,8 h ≈ 5,5-6 h):
```bash
tmux new -d -s full 'PREREG_TAG=prereg-amd-revision-20261128 RUN_ID=full-01 bash sponge-sim/studies/linux_profile/run_revision.sh full > runs_full.out 2>&1'
```
Không đụng máy cho tới hết thời gian ước tính. Rồi MỘT lệnh: `ls ~/ws/repo/runs/amd-revision/full-01/ALL_DONE; tail -5 ~/ws/repo/runs_full.out`.
Nếu chưa xong: chờ thêm 30-60 phút rồi kiểm lại một lần, không đọc log dở dang.

## 8. Mang kết quả về TRƯỚC khi tắt máy live
```bash
# trên máy đo
cd ~/ws/repo/runs/amd-revision && find full-01 smoke -type f -print0 | sort -z | xargs -0 sha256sum > results.sha256
sudo bash ~/ws/repo/sponge-sim/studies/linux_profile/lock_env.sh unlock 2
# trên laptop
scp -r xubuntu@100.x.y.z:~/ws/repo/runs/amd-revision ./amd_revision_20261128
cd amd_revision_20261128 && sha256sum -c --quiet results.sha256 && echo COPY_OK
```
Về nhà, chép thư mục sang Windows `sponge-sim/results/amd_revision_20261128/` (thư mục MỚI, không ghi đè), kiểm `sha256sum -c` lần nữa.
Chỉ tắt máy live khi đã có COPY_OK ở laptop.

## 9. Phân tích sau khi có dữ liệu (laptop hoặc Windows)
```bash
AA=sponge-sim/results/aa_linux_20261124/x/sponge-aa-20261124/full-01
python -X utf8 sponge-sim/studies/e9_pipeline/analyze.py --part a --run-dir <run e9r> --aa320 $AA/aa_320/summary.json --aa640 $AA/aa_640/summary.json --out <run e9r>/summary.json
python -X utf8 sponge-sim/studies/e10_reference/analyze.py <run>    # endpoint chính kiểu E10 (bản ghi E10-R tương thích)
python -X utf8 sponge-sim/studies/e10r_reference_rerun/analyze_new.py <run>   # endpoint mới: NMS trong pipeline, gây hại, page fault
```
`analyze_new.py` đã thử trên bản sao giả lập từ raw E10 cũ: tái lập đúng Δt_total, Δt_NMS của Bảng 10 và MDE 2,82/2,82/2,80%.
Bảng của bài sinh lại bằng `paper_en/tables_q3/make_tables_en.py` (cần thêm `paper/vi/tables/make_tables.py` và dữ liệu E7 từ repo gốc,
hai thứ này KHÔNG có trên nhánh GitHub).

## 10. Việc chưa thuộc đợt này
CPU đa luồng (1/2/4/6 luồng) và GPU: cần PREREG riêng; GPU chưa biết máy nào. Tài liệu tham khảo mới (Gontara 2026, survey 09/2026, …):
chờ nguồn. Phụ lục Pi: chờ quyết định giữ/bỏ.
