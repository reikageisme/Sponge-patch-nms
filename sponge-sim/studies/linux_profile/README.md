# Chuẩn bị profile CPU trên Linux

Dùng `lscpu -e=CPU,CORE,ONLINE` và `cpupower -c CPU frequency-info` để chọn CPU logic,
luồng SMT anh em và tần số trong dải non-boost. Chạy các lệnh dưới đây từ thư mục `sponge-sim`.
Script cần Python 3, `taskset`, `sha256sum` và `turbostat` có cột `Bzy_MHz`.

```bash
sudo bash studies/linux_profile/lock_env.sh lock CPU FREQUENCY_KHZ
sudo bash studies/linux_profile/lock_env.sh verify CPU --seconds 30
python3 studies/linux_profile/check_env.py CPU
sudo bash studies/linux_profile/lock_env.sh unlock CPU
```

`lock` lưu cấu hình trong `/run/sponge-cpu-lock/original.json`, tắt boost, đưa luồng SMT anh em
offline rồi đặt governor và hai giới hạn tần số. Để báo thành công, mọi mẫu `Bzy_MHz` phải nằm
trong ±1% mục tiêu và CPU bận ít nhất 95% trong từng mẫu. Mặc định lấy 20 mẫu, mỗi mẫu một giây.
Khi thiết lập hoặc phép kiểm lỗi, script thử hoàn tác ngay. Nếu hoàn tác gặp lỗi, file trạng thái
được giữ để chạy lại `unlock`. `check_env.py` chỉ đọc cấu hình sysfs, còn `verify` đo xung dưới tải.

Trên AMD, mặc định script ưu tiên tắt boost ở policy. Nếu phép kiểm dưới tải cho thấy cần tắt boost
toàn máy, dùng `--global-boost`. Cấu hình cho Ryzen 5 5500 dùng `amd-pstate-epp` ở chế độ active:

```bash
sudo bash studies/linux_profile/lock_env.sh lock 2 3600000 --global-boost --seconds 35
```

Trên máy Ryzen này, CPU 8 là luồng SMT anh em của CPU 2. Với thiết lập trên, lượt kiểm đầu đo
`Bzy_MHz` 3574 MHz trong 35/35 mẫu và CPU bận 100%.
Ghi topology trước khi khóa vì Linux có thể
bỏ CPU đã offline khỏi `thread_siblings_list`. Trước phiên đo, ghi CPU, kernel, driver, xung yêu cầu,
dải `Bzy_MHz` quan sát được và trạng thái SMT vào hồ sơ. Hoàn thiện đăng ký trước riêng cho dữ liệu
dùng trong bài. Chuẩn bị môi trường, trọng số đã kiểm SHA-256 và ảnh đầu vào theo giao thức.

## Profile

`hw_linux.profiles()` đọc danh sách CPU từ `SPONGE_PROFILES`. Ví dụ cho máy Ryzen ở trên:

```bash
export SPONGE_PROFILES='{"P1_cpu2": [2]}'
```

Kiểm ghim dưới tải bằng `verify_pin` trước phiên đo. Chạy A/A và kiểm drift theo giao thức đã đăng ký.

## 2. Lệnh đo (sau tag; mỗi lệnh chạy một mình, không chạy song song)
```bash
python3 -X utf8 studies/e5_protocol/run.py --profiles P1_cpu2 --run-dir results/e12/AA_fedora_<ngày>
python3 -X utf8 studies/e5_protocol/run.py --profiles P1_cpu2 --canvas 640 --run-dir results/e12/AA640_fedora_<ngày>
python3 -X utf8 studies/e9_pipeline/run.py --run-dir results/e12/E9_fedora_<ngày>
```
Ước tính thời gian: tương tự laptop (A/A 320 px khoảng 30–40 phút, 640 px khoảng 1 giờ, E9 vài giờ); chạy smoke (`--smoke`) trước để đo thực tế.

## 3. Phân tích
Dùng đúng script của laptop (`studies/e5_protocol/analyze.py`, `studies/e9_pipeline/analyze.py`, `studies/amdahl/analyze.py`),
với MDE của A/A Fedora. Bảng của bài chỉ thêm cột Fedora sau khi có dữ liệu, qua `paper_vi/tables/make_tables.py`.

## Giới hạn

Khóa xung và tắt luồng SMT anh em vẫn cho phép scheduler dùng CPU đo. Xung hiệu dụng đo với tải
kiểm tra có thể thay đổi với tải khác hoặc khi nhiệt độ tăng. Kiểm ghim, A/A và drift trong phiên đo.
