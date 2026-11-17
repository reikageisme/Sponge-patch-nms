> **Ghi chú môi trường lịch sử, chưa bảo đảm exact-source replay.** Current source có các hash khác lượt OLD128; xem [data availability và giới hạn tái lập](docs/results.md#availability-and-reproduction). Các lệnh dưới đây có thể tạo report/chạy tests hoặc cài môi trường; để chỉ đọc nghiên cứu, bắt đầu từ [README](README.vi.md). Source/package khớp không tự chứng minh mọi inference/timing đã được tái lập.

# REPRODUCE.md — GĐ1 môi trường chuẩn cho Physical-Visual-DoS-EdgeAI

> Mục tiêu: môi trường **giống hệt bản đã đo** (lượt `extended_q1_20261002`) —
> Python 3.14.6, torch 2.13.0+cpu, ultralytics 8.4.90 — để mọi số liệu sinh sau
> này có cùng nền với `outputs/extended_q1_20261002/manifest.json`.

## 1. Kiểm chứng nhanh trên máy có sẵn môi trường

```powershell
python scripts/verify_env.py
```

Kết quả mong đợi: `status=PASS` (hoặc `PASS_WITH_SOURCE_CHANGES` nếu mã nguồn
đã được sửa hợp lệ sau 02/10), unittest ≥ 50 PASS,
báo cáo ghi rõ tại `outputs/env_verify/latest.json`.

## 2. Docker (khóa chặt môi trường, khuyên cho máy thuê)

```powershell
# build hình ảnh môi trường (lock theo requirements-lock.txt)
docker build -f docker/Dockerfile -t pvdos-env:gd1 .

# chạy kiểm chứng fail-closed với repo mount vào /work
docker run --rm -v "%CD%:/work" -w /work pvdos-env:gd1 python scripts/verify_env.py
```

Linux/macOS dùng `-v "$(pwd):/work"`. Image chỉ chứa môi trường; mã nguồn,
dataset và outputs là volume mount — không sao chép để tránh nhầm provenance.

## 3. Cài trực tiếp (không Docker, Windows/Linux)

```powershell
python -m pip install -r requirements-lock.txt --extra-index-url https://download.pytorch.org/whl/cpu
python scripts/verify_env.py
```

Ghi chú:
- `torch==2.13.0+cpu` buộc phải cài qua PyTorch CPU index (xem header của
  `requirements-lock.txt`).
- `torchvision` được cài tự động theo CPU-index; script sẽ ghi lại phiên bản
  thật của môi trường mới và cảnh báo nếu khác môi trường đo.
- `flask` không thuộc chuỗi thực nghiệm (chỉ `web_simulation.py`), không nằm
  trong lock để tránh sai lệch phiên bản tối thiểu.

## 4. Quy báo PAS/PASS_WITH_SOURCE_CHANGES/FAIL

| Status | Ý nghĩa |
|---|---|
| `PASS` | python/torch khớp bản đo, đủ packages, toàn unittest PASS, hash nguồn khớp manifest 02/10 |
| `PASS_WITH_SOURCE_CHANGES` | môi trường khớp, hash nguồn khác manifest 02/10 (sửa mã gravití sau 02/10 hoặc CRLF); mọi lần chạy mới phải truy cập bản báo này |
| `FAIL` | thiếu package, torch/python khác bản đo, hoặc có test FAILED; phải sửa trước khi sinh dữ liệu mới |

## 5. Chạy lại các lượt test thủ công

```powershell
Get-ChildItem experiments\test_*.py | Sort-Object Name |
  ForEach-Object { python $_.FullName; "[$($_.Name)] exit=$LASTEXITCODE" }
```

## 6. Tiếp theo sau GĐ1

GĐ2 (thí nghiệm mở rộng X1/X3/X5 trên profile edge container) sẽ đọc báo cáo
`outputs/env_verify/latest.json` và từ chối chạy nếu `status == FAIL` —
nguyên tắc fail-closed của repo (`NO RAW LOG = NO RESULT IN PAPER`).
