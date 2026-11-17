#!/usr/bin/env bash
# B5. Khoá môi trường đo trên Linux cho MỘT CPU được ghim. Cần quyền root. Đọc kỹ trước khi chạy: script đổi cấu hình nguồn của máy.
# Hoàn tác: chạy lại với "unlock" hoặc khởi động lại máy.
#   sudo bash b5_linux_lock_env.sh lock   <cpu> <tan_so_kHz>     vd: sudo bash b5_linux_lock_env.sh lock 2 2400000
#   sudo bash b5_linux_lock_env.sh unlock <cpu>
# Chọn tần số không vượt tần số cơ sở (không turbo). Sau khi lock: python b5_check_env.py <cpu> phải in "ready": true.
set -euo pipefail
mode="${1:?lock|unlock}"; cpu="${2:?cpu}"; freq="${3:-}"
sysc=/sys/devices/system/cpu
sibs=$(tr ',-' '  ' < "$sysc/cpu$cpu/topology/thread_siblings_list")

if [ "$mode" = lock ]; then
  [ -n "$freq" ] || { echo "thiếu tần số kHz"; exit 2; }
  # 1. tắt turbo (Intel) hoặc boost (AMD / acpi-cpufreq)
  [ -w "$sysc/intel_pstate/no_turbo" ] && echo 1 > "$sysc/intel_pstate/no_turbo"
  [ -w "$sysc/cpufreq/boost" ] && echo 0 > "$sysc/cpufreq/boost"
  # 2. governor performance, min = max = freq trên CPU được ghim
  echo performance > "$sysc/cpu$cpu/cpufreq/scaling_governor"
  echo "$freq" > "$sysc/cpu$cpu/cpufreq/scaling_max_freq"
  echo "$freq" > "$sysc/cpu$cpu/cpufreq/scaling_min_freq"
  # 3. đưa CPU anh em SMT của lõi này offline (để lõi vật lý chỉ chạy một luồng)
  for s in $sibs; do
    [ "$s" = "$cpu" ] || echo 0 > "$sysc/cpu$s/online"
  done
  echo "đã khoá cpu $cpu ở $freq kHz; anh em SMT offline: $(for s in $sibs; do [ "$s" = "$cpu" ] || printf '%s ' "$s"; done)"
  echo "nên thêm vào dòng lệnh kernel: isolcpus=$cpu nohz_full=$cpu rcu_nocbs=$cpu (cần khởi động lại)"
else
  for s in $sibs; do
    [ "$s" = "$cpu" ] || echo 1 > "$sysc/cpu$s/online"
  done
  cat "$sysc/cpu$cpu/cpufreq/cpuinfo_min_freq" > "$sysc/cpu$cpu/cpufreq/scaling_min_freq"
  cat "$sysc/cpu$cpu/cpufreq/cpuinfo_max_freq" > "$sysc/cpu$cpu/cpufreq/scaling_max_freq"
  [ -w "$sysc/intel_pstate/no_turbo" ] && echo 0 > "$sysc/intel_pstate/no_turbo"
  [ -w "$sysc/cpufreq/boost" ] && echo 1 > "$sysc/cpufreq/boost"
  echo "đã mở khoá cpu $cpu"
fi
