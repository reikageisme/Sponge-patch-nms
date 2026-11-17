# Pi 3B (600 MHz) — tổng hợp kết quả đã kiểm chứng (15/11/2026)

Bản này gộp các kết quả Pi 3B đã ĐẠT cổng chất lượng và tôi (Claude) đã tự tính lại từ dòng raw,
độc lập với báo cáo của Codex. Điều kiện board: Raspberry Pi 3B Rev 1.2, bị firmware ép 600 MHz do
thiếu áp nguồn (`get_throttled=0x50005`), 4×Cortex-A53, Pi OS Lite 64-bit. KHÔNG quy đổi sang 1,2 GHz,
KHÔNG so tuyệt đối với laptop/A36, KHÔNG kết luận DoS. Đơn vị suy luận: ảnh (n = 20 cặp PGD đã khóa).

## Đã xong (số nào cũng truy được tới raw)

**1. Toàn trình: ảnh nhiễu chậm hơn ảnh sạch 1,80 lần.** Tự tính lại khớp từng chữ số với Codex.
- H1 geomean = 1,798077; cả 20/20 ảnh cùng chiều dương (mỗi ảnh 1,58–1,94); CI95% [1,747; 1,848];
  p đảo dấu = 1,9×10⁻⁶. A/A rất ổn định (|log| = 0,00097), MDE ≈ 1,003.
- Nguồn: `sponge-sim/results/pi3b_full20_20261114/runs/full_01/pipeline_PI4/raw.jsonl`
  (kind=timing, arm ∈ {clean_total_A/B, adv_total}); tổng hợp ở `…/summary.json:pipeline_PI4`.

**2. Phòng thủ: chặn ứng viên trước NMS kéo thời gian ảnh nhiễu còn 0,73 lần.**
- H2 cap/adv geomean = 0,728911; 20/20 ảnh; CI95% [0,713; 0,746]. (max_det=300, max_nms=300.)
- Cùng raw như trên, arm=advcap_total.

**3. Cơ chế — chi phí dựng mask tuyến tính theo số vật thể K.** Đây là bằng chứng gốc cho luận điểm.
- Trong cùng một ảnh, quét K ∈ {1,10,30,100,300}: thời gian mask ≈ 13,7 ms mỗi vật thể, rất đều giữa
  các ảnh (13,72 / 13,70 / 12,90 / 13,76 / 13,64), R² ≈ 0,999.
- Trên 20 ảnh (K thật 177–300): tương quan Pearson(mask_ms, K) = 0,933; dốc 13,2 ms/vật thể.
- Khâu mask: ảnh sạch 48 ms (K≈1–9) → ảnh nhiễu 3636 ms (K≈300), tức ×68.
- Nguồn: `…/runs/full_01/stages_PI4/raw.jsonl` (arm mask_clean/mask_adv/maskdose_K; counts.adv.k).
- Hình: `sponge-sim/results/pi3b_full20_20261114/pi3b_mask_mechanism.png`
  (dựng bằng `sponge-sim/studies/pi3b_600mhz/figure_mechanism.py` từ chính raw này).

**4. Vì sao toàn trình "chỉ" 1,8× dù mask tăng 68×:** forward chiếm ~98,6% thời gian ảnh sạch, là chi
phí cố định lớn. Attack chỉ bơm phồng phần mask, nên tỷ số toàn trình bị forward pha loãng. Đây là ví
dụ Amdahl, không phải mâu thuẫn.

**5. Số đếm khớp laptop:** K giữ lại trên Pi trùng y hệt laptop cho cả 20 ảnh (202,250,300,177,…), xác
nhận pipeline trên Pi cho cùng kết quả đếm dù torch khác bản (2.15 vs 2.13).

**6. Tối ưu bộ nhớ (Codex, 15/11, đã đạt cổng):** cấp phát trước bộ đệm mask làm đỉnh RSS ảnh nhiễu còn
0,8755 lần (−12%); CI95% [0,8675; 0,8838]; A/A và MDE đều đạt. Đây là RSS toàn tiến trình, cache-only,
KHÔNG phải đỉnh riêng renderer / độ trễ / DoS. Tag `prereg-pi3b-renderer-memory-usb-20261115`;
báo cáo `docs/reports/PI3B_RENDERER_MEMORY_USB_FULL20_20261115.md`.

## Phát hiện cần biết (giữ nguyên, không tô hồng)

- **Phần tách công đoạn "không đạt cổng" chỉ vì NMS, không phải vì mask.** Cổng A/A và MDE của NMS trượt
  do thời gian NMS rất nhỏ (~10 ms sạch, ~87 ms nhiễu) và nhiễu động trên board thiếu áp. Phần mask và
  liều K — cái quan trọng cho bài — thì sạch (R² 0,999). Nên khi trích dẫn: cơ chế mask là kết quả vững;
  con số NMS tuyệt đối chỉ để mô tả, không khẳng định độ ổn định.
- **Mọi số là ở 600 MHz do thiếu áp.** Một Pi 3B nguồn đủ (1,2 GHz) sẽ nhanh hơn; tỷ số có thể đổi. Chưa
  đo được vì chưa có nguồn 5,1 V.
- **Protocol đầu (`prereg-pi3b-600mhz-20261114`) hỏng do swap tự bật lại giữa chừng → chỉ chẩn đoán.**
  Kết quả dùng được đến từ protocol sau pilot (`prereg-pi3b-full20-after-pilot-20261114`). Hai protocol
  giữ riêng, không trộn.
- **Phiên 1 luồng (PI1) bị hủy**, chưa có số 1 luồng trên Pi.
- Nhánh "quan sát cơ chế NMS" (NMS-predecessor/observer) mà Codex chuẩn bị ngày 15/11 vẫn đang ở mức QA
  chức năng, CHƯA thành phép đo khoa học; cần duyệt phương pháp + PREREG riêng trước khi mở endpoint.

## Việc tiếp theo — chọn 1

A. Đưa ba kết quả Pi này (1,80× / 0,73× / mask 13,7 ms/vật thể) + hình vào bản thảo tiếng Anh như trục
   thiết bị ARM và phần cơ chế → gõ: "Đưa kết quả Pi vào paper".
B. Nếu sau này có nguồn 5,1 V: đăng ký protocol 1,2 GHz để có thêm một mức xung so sánh → gõ:
   "Chuẩn bị PREREG Pi 1200 MHz".
C. Dừng nhánh tối ưu/quan sát NMS đang dở của Codex (đang tiêu tài nguyên mà chưa ra số) → gõ:
   "Chốt dừng nhánh observer".

## Đang chờ gì ở tôi

Không có — ba kết quả chính của Pi đã kiểm khớp raw và có hình. Chọn A/B/C để đi tiếp.
