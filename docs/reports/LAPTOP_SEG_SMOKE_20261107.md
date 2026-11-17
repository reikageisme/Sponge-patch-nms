# Lượt thử CPU laptop —07/11/2026

## Đã xong

- Đã chạy đúng campaign được người dùng cho phép: hai fresh workers tuần tự,
  P1_cpu2=[2] vàP2=[0,2], hai input sạch khóa trước, mỗi ảnh8repeats mỗi label
  A/B cho forward và total. Không tấn công/PGD hoặc injectedMASK trong lượt này.
- Tag `prereg-laptop-seg-smoke-20261107`, commit
  `9cafdd8548dcd794da8c060619cf187daf45158f` có trước timing. Campaign kết thúc
  exit0, cả haiworkerexit0. Không đọc log/phân tích/test/git/web trong lúc đo;
  chỉ chờ kết thúc. Thời gian nghỉ60s đầu/giữa theo protocol.
- Đủ128timing rows,120reference samples qua8reference records,4pinchecks.
  Raw/manifest/summary mới được giữ nguyên; receipt kiểm tag-source byte/SHA
  và rawSHA tại `results/laptop_seg_20261107/smoke_01/verification_receipt.json`.

| Cấu hình | Ghim/tải đầu–cuối | Cờ drift /4 | Lệch reference lớn nhất | Gate smoke |
|---|---|---:|---:|---|
| Một P-core [2] | PASS/PASS;0.947512 /0.942185 CPU hiệu dụng | 0/4 | +2.925193% | PASS khả thi |
| Hai P-core [0,2] | PASS/PASS;1.801420 /1.900567 CPU hiệu dụng | 1/4 | −5.076463% | FAIL drift |

Nguồn: mỗi profile `raw.jsonl:kind=pin_start|pin_end,reference`, summary
`feasibility_pass,flagged_references,pin_checks`. PerCPU utilization được QA
ghi100% ở cácCPU cho phép; không chỉ tin số thread Torch tự khai.

| Cấu hình | A/A geometric ratio forward /total | MDE80 forward /total (%) |
|---|---|---|
| P1 | 0.987095 /1.010298 | 8.992809 /48.668560 |
| P2 | 1.002506 /0.991983 | 29.069786 /74.441009 |

Nguồn: `smoke_summary.json:stages.forward|total`. Hai ảnh là đơn vịn=2,
df1, MDEtheo registered t approximation; không CI/p-value population.

## Phát hiện cần biết

**P1 mới đạt khả thi ngắn, chưa xác nhận ổn định dài.** Reference lớn nhất
+2.925193% khá gần cổng3%; A/A MDE rất rộng với haiảnh. Không dùng ratio gần1
để nói tương đương hoặc nhiễu không đáng kể. Không suy P1 đủ công suất phát
hiện hiệu ứng1%, không đưa smoke thành headline latency attack hoặcDoS.

P2 thực sự dùng gần haiCPU nhưng reference cuối127.1908ms so baseline133.9929ms,
ratio0.9492353699337801: bị cờ do NHANH hơn5.076463%, không phải chậm dần.
Không kết luận nóng/throttling/clock hoặc lỗi pool là nguyên nhân. Một phiên,
hai ảnh chưa định vị được cause. Không rerun P2 để lấy phiênPASS.

K sạch haiảnh6và2 ở cả hai profile;N_tau37và18,proto[32,160,160]. Đây là cùng
hai inputclean, không phải số tấn công và không kiểm bitwise predictions khác
runtime. Runtime laptop torch2.13.0+cpu/TV.28.0+cpu/Ultralytics8.4.90 khác hostthuê.

ConfiguredACBestPerformance đã được chọn đúng như người dùng nhớ; maxAC100%,
boostmode2, maxfrequency0 trong powercfg snapshot. Reapply cùngACmode thành
công trước tag, effectiveoverlay vẫn961cc777. Cả đầu/cuối haiworker giữ cùng
configured/effectiveGUID, ACTrue. Không hề tắt bảo vệ nhiệt hoặc tăng powerlimit.
Microsoft mô tả configuredmode là user vote, có thể bị tín hiệu hệ thống khác
ghi đè; readback này chưa cho biết nguyên nhân hoặc xung CPU thực.
[Microsoft PowerSetUserConfiguredACPowerMode](https://learn.microsoft.com/en-us/windows/win32/api/powrprof/nf-powrprof-powersetuserconfiguredacpowermode)

Probe RIÊNG sau smoke đọc ProcessPowerThrottling: ControlMask0/StateMask0,
normalpriority. Không thấy opt-in EcoQoS của chính probe; không được gán
readback này cho haiworker đã thoát hoặc phủ nhận heuristicsWindows. Windows
có thể suyQoS khi process không tự khai; HighQoS có thể là biến trong protocol
sau nếu cần, không sửa QoS rồi gọi là cùng phiên cũ.
[Microsoft SetProcessInformation](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-setprocessinformation)

## Việc tiếp theo — chọn 1 trong các cách sau

A. Chạy A/A20ảnh P1 để kiểm phiên dài: đã chuẩn bị protocol
`PREREG_LAPTOP_AA20_20261107.md`, code tổng quát và `lock_aa20.json`;
**UNRUN, chưa tag full**. Một phiên cố định,22references,<=2flags3%,
MDEforward/total<=1%, không đổi power/QoS hoặc chọn kết quả tấn công.
9tests local PASS sau mở rộng; analyzer mới kiểm lại khớp summary smoke cũ,
không ghi đè. Dự kiến vài phút; chưa có runtime20ảnh được đo. → gõ:
**“Chạy A/A20ảnh trên P1 theo protocol đã chuẩn bị.”**

B. Rà thêm cơ chế quản lý năng lượng/QoS trước protocol khác → gõ:
**“Rà tiếp giới hạn hiệu năng, chưa đo thêm.”**

## Đang chờ gì ở tôi

Campaign smoke đã hoàn tất; cần review/duyệt bước đầy đủ tiếp theo.
Theo `.claude/skills/sponge-research/SKILL.md`§1.4: “Chạy smoke nhỏ trước,
ước lượng thời gian/dung lượng, dừng chờ duyệt rồi mới chạy đầy đủ.”
Không có tiến trình đo còn chạy. Không truy cập máy thuê đã xóa hoặc A36.
