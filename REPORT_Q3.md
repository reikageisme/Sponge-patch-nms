# REPORT_Q3 — hoàn thiện bản nộp Q3 theo yêu cầu GVHD (03/11/2026)

Tên bài (đổi 03/11/2026, xem REFRAME_REPORT.md): "Tấn công cạn kiệt tài nguyên qua NMS có thực sự làm chậm bộ phát hiện? Một nghiên cứu đo lường trên CPU ghim lõi".

Bản thảo: `paper_vi/main_vi.tex` (tiếng Việt, không dịch). Tài liệu bổ sung: `paper_vi/supplement_vi.tex`. Gói nộp: `paper_Q3_submission_v4/`.
Kiểm số: `python -X utf8 paper_vi/tables/check_numbers.py --all` → **KẾT QUẢ: ĐẠT**. Kết quả này chưa gồm các ô E11, vì E11 chưa đo.
Không biên dịch được LaTeX trên máy: không có TeX, và quy tắc dự án cấm cài gói. Đã kiểm tĩnh: ngoặc cân, môi trường cân, không có `\ref` hỏng, không có nhãn trùng, đủ 40 trích dẫn. **Cần biên dịch trên Overleaf** để xác nhận không còn "??".

## (a) Việc đã làm / chưa làm

| Việc | Trạng thái | Ghi chú |
|---|---|---|
| 1a Sửa mã đo | Xong | `sponge-sim/studies/e11_patch_remeasure/run.py`: ảnh đầu vào dựng ngoài vùng bấm giờ, mọi nhánh dùng chung `pipeline_fn`. Chọn "đưa ra ngoài" vì bước chèn là thao tác dựng kịch bản, không thuộc pipeline bộ phát hiện. |
| 1b Test hồi quy | Xong | `sponge-sim/tests/test_e11_symmetry.py`: 3 test đạt (cùng chuỗi thao tác trong vùng đo; hàm đo không tham chiếu insert; ảnh patch chỉ khác ảnh gốc ở vùng patch). |
| 1c Kiểm phép đo khác | Xong | 640 px của patch (`e6_remeasure/run.py:199`, cùng hàm `full()`): **cùng lỗi**. Tiêm toàn pipeline (`e9_pipeline/run.py:102,116-122`): không lỗi, ảnh và ứng viên tiêm dựng trước. Tấn công toàn ảnh (`e10_reference/run.py:84,103-108`): không lỗi, nhiễu loạn cộng trước khi đo. E1/E5: không có bước chèn. |
| 1d PREREG + đo lại | **Chờ duyệt** | `prereg/PREREG_E11.md` đã commit (d1b77dd), **chưa tag, chưa đo**. Smoke 2 ảnh chạy được (không dùng số). |
| 1e Thiết kế cân | Xong (trong PREREG) | Mọi nhánh trên cùng 100 ảnh và seed 0–4. Bằng chứng seed chọn trước: `PREREG_E6.md:20` trong tag `prereg-e6-20261101` (01/11 18:11 +0700); lần đo E6 đầu bắt đầu 16:41Z cùng ngày, sau tag. Vì chứng minh được nên không cần đo 10 seed. |
| 1f Số hiệu chỉnh cũ | Xong | Chuyển sang tài liệu bổ sung (`tab_supp_corrected`), nhãn "Kiểm tra chéo, post hoc". |
| 1g Cập nhật bản thảo | Một phần | Đã bỏ mọi chỗ dùng "1,1–1,5%" và số hiệu chỉnh. Chỗ cần số E11 để `\todo` (xem mục c). |
| 2a t_total cùng phiên | Xong | Giải thích mâu thuẫn trong Kết quả: 53,5/180 ms là toàn trình A/A (gồm đổi kích thước 5,60 ms); 46,3–46,5/171–173 ms là phiên tiêm; 50,8/165,7 ms là phiên patch E6 (tensor đã chuẩn bị); 0,28/0,29 ms là hai backend khác nhau. Ngưỡng mới chỉ dùng t_total và MDE trong cùng phiên E11. |
| 2b Tính lại mục ngưỡng | Chờ E11 | `tab_threshold` sinh từ E11 (MDE trong phiên, t_total trong phiên, Δt_NMS của B4, R dự đoán/đo). |
| 2c Bảng Amdahl | Xong | `tab_amdahl` gộp phần A tiêm (nhãn **post hoc** trong chú thích) và phần B tấn công đủ 6 ô (3 "không đạt" in đậm, kèm lý do). Đã bỏ từ "kiểm chứng/xác nhận" cho kết quả 3/6. |
| 2d N* dự đoán | Xong | Cột "Dự đoán†" (post hoc, đầu 2100/8400 anchor, không dùng đầu 10 000) trong `tab_nstar`. |
| 3a top-300 | Xong | `tab_cap` có hệ số giảm cho đủ 12 ô: 3,66 (PyTorch, cụm dày đặc) đến 653 (torchvision nms, rời nhau). Câu cũ "72 đến 650" đã sửa. |
| 3b Bảng 2 đủ 4×3 | Xong | `tab_dose`: 12 ô có KTC; cả 12 vượt MDE nên giữ câu "phát hiện được ở mọi cài đặt và hình học". |
| 3c Câu 0,44/0,35/0,93/0,76 | Xong | Thứ tự đúng với nguồn (Ultralytics 0,44; theo lô 0,35; nms 0,93; PyTorch 0,76). Câu viết lại, gọi tên từng cài đặt. |
| 3d Đánh số bảng/hình | Xong (tĩnh) | Phần Kết quả xếp theo khung bài: Q3 gồm N* → patch → tấn công; Q4 gồm dự đoán → Bảng 7 (`tab:nk`) → Bảng 8 (`tab:amdahl`). Chưa biên dịch để xem số cuối cùng (xem mục e). |
| 3e Overload/Phantom | Xong | Gọi là "biến thể thích nghi theo …" ở phương pháp, kết quả, bảng, thảo luận, hạn chế. Mọi câu về mức tăng đều kèm điều kiện (YOLOv5s, 640 px, một lõi CPU). |
| 4a Bảng tự động | Xong | `paper_vi/tables/make_tables.py` sinh 14 bảng `tab_*.tex` (gồm bảng bổ sung) và `numbers.json` (754 ô số kèm nguồn). |
| 4b Script kiểm | Xong | `paper_vi/tables/check_numbers.py` và `paper_vi/Makefile` (`make check`). Không thêm pre-commit hook vì quy tắc dự án cấm đụng `.git`. |
| 4c Bảng thiết lập | Xong | `tab_spec` sinh từ đặc tả lưu trong checkpoint E7. Khớp bản thảo cũ (8 dòng); thêm cột số ảnh tối ưu (100); seed 0–9 đọc từ thư mục. |
| 5a Ultralytics | Xong | `max_nms = 30000` (mặc định, lớn hơn mọi N đã đo: tối đa 10⁴ khi tiêm, 8178 đầu vào NMS ở E10), `time_limit = 2,05 s`. Thời gian NMS Ultralytics lớn nhất trong bản ghi thô: E1 183 ms, E9 139 ms, E10 92,6 ms. Ô vượt giới hạn: 0. Không có log cảnh báo, nhưng giới hạn được so với chính thời gian trôi trong hàm, nên không thể đã kích hoạt. **Không cần đo lại.** |
| 5b SMT | Xong | Từ mã và manifest: lõi gồm CPU 2 và CPU 3; chỉ tiến trình đo bị đặt affinity vào CPU 2; không có cơ chế dành riêng CPU 3. |
| 5c Độ nhạy N* | Xong | Cột "Bỏ khối cờ§" trong `tab_nstar` (12/21 điểm bị cờ; còn 14 ảnh). |
| 5d Hai MDE 640 px | Xong | Cột "Đo" (MDE 1,88%) và cột "MDE 0,69%" đặt cạnh nhau; khác nhau ở 1/12 ô không giới hạn. |
| 5e Công thức | Xong | Bỏ `\text{cài đặt}` trong công thức; chỉ số dưới dùng `\mathrm{meas}`/`\mathrm{pred}`. |
| 5f Tóm tắt | Xong | 248 từ (tách theo khoảng trắng); có câu hỏi, giao thức, 3 phát hiện, 1 câu hạn chế CPU một lõi; không còn số. |
| 5g Hạn chế 4 nhóm | Xong | Phạm vi (nói thẳng: một lõi, lan truyền thuận chiếm ưu thế nên thiên về "không có tác động"), nội tại, cấu trúc, bên ngoài, kết luận. Điện thoại còn đúng 1 câu. |
| 5h Trích dẫn | Xong | Xem mục (d). TrackFlood **có thật** (arXiv:2609.33948), giữ nguyên. |
| 5i Tác giả | `\todo` | Tác giả liên hệ, email, ORCID. Đã bỏ dòng ghi thầy Nam là tác giả liên hệ, cả trong bản thảo lẫn gói nộp. |
| 5j Gói Zenodo | Xong (chưa tải) | `python -X utf8 paper_vi/zenodo/make_bundle.py` tạo `zenodo_bundle/` (113 tệp, 1,5 MB), gồm MANIFEST có SHA-256 và danh sách 9 bản ghi thô (193 MB, chưa chép). **Chạy lại sau E11.** |
| 5k CRediT | `\todo` | Mục mới trước "Tuyên bố sử dụng AI". |
| 5l Đổi tên gói | Xong | `paper_Q3_submission_v4/`; `build_submission.py` đã trỏ tới gói mới. Gói cũ `paper_Q1_submission_v3/` giữ nguyên vì quy tắc không xoá; nếu muốn xoá thì duyệt. |
| 6 Profile Fedora | Chuẩn bị xong | `sponge-sim/studies/linux_profile/README.md` và `topology_fedora.py` (chỉ đọc). Chưa chạy, chưa đưa vào bài. |

## (b) Số đã thay đổi (cũ → mới, nguồn)

| Chỗ | Cũ | Mới | Nguồn |
|---|---|---|---|
| Tỷ số liều, torchvision rời nhau | 1360 (1250–1410) | 1356 (1247–1414) | `e1/E1_P1cpu2_20261101/summary.json:dose_1e2_to_1e4.P1_cpu2\|tv_nms\|disjoint` |
| Tỷ số liều, PyTorch cụm dày đặc | 4,0 | 4,04 | cùng tệp, `…\|torch_pure\|dense_cluster` |
| Hệ số giảm top-300 | "72 đến 650 lần" | 3,66 đến 653 lần (12 ô) | `e1/…/summary.json:contrasts.cap300_over_capNone.*\|10000` (nghịch đảo) |
| Lọc điểm khi có giới hạn | 0,39 ms | **0,46 ms** (số cũ sai) | `e1/…:curves.P1_cpu2\|10000\|torch_pure\|disjoint\|80\|300\|10000.tau_median_ms` |
| MDE NMS torchvision 320 px | 1,1% | 1,09% | `e5/AA_P1cpu2_20261101/summary.json:profiles.P1_cpu2.stages.nms_tv_nms.mde_ratio_pct` |
| MDE A/A 640 px lần đầu | 1,9% | 1,88% | `e5/AA640_P1cpu2_20261102/summary.json:…stages.total.mde_ratio_pct` |
| Amdahl 640 px R đo, torchvision nms | 1,58 | 1,57 | `amdahl/amdahl_vs_e9_posthoc.json:cells.640\|tv_nms\|disjoint\|capNone.rows[8400].r_meas` |
| Amdahl 640 px R đo, Ultralytics | 1,59 | 1,58 | cùng tệp, `640\|ultra_native…` |
| M_N, PyTorch 640 px | 0,90 | 0,89 | `e9/E9_P1cpu2_20261102/summary_part_b.json:test2_e6a1_640_confirmatory.torch_pure.median_abs_log_err_M_N` |
| Δ, theo lô 640 px, cận trên | −1,06 | −1,05 | cùng tệp, `tv_batched.delta_ci95[1]` |
| NMS sau tấn công, nhân thư viện | 4,6–7,8 ms | 4,5–7,8 ms | `e10/E10_P1cpu2_20261102/stage_medians_posthoc.json` (script mới, post hoc, mô tả) |
| NMS PyTorch, ảnh sạch E10 | 0,52 ms | 0,51 ms | cùng tệp, `nms_ms.clean\|torch_pure` |
| Tương quan trong cùng ảnh | 0,36–0,73 | 0,27–0,73 | `e6/E6_P1cpu2_20261102/summary.json:arms[C1,C3,B1–B4].nms_tau0.01_*.rho_dN_dt` |
| Tỷ số N của tấn công | "khoảng 350 lần" | 340 đến 389 lần | `e10/…/summary.json:n_ratio.*\|tau0.25.mean` |
| N của tấn công | "khoảng 5000" | 4811,5 đến 5578,5 (trung vị) | `e10/…:n_median.*\|tau0.25.patched` |
| Toàn trình khi bị tấn công | "+3%" | 2,9 đến 3,4% | `e10/…:total_ratio[*].mean` |
| Mọi số của bảng patch, ngưỡng, cài đặt | số E6 / số hiệu chỉnh | `\todo` chờ E11 | – |
| Mới công bố | – | N* đo trong bảng Amdahl khác bảng N* ở 3/48 ô (khác cách gộp: log-tỷ số so với tỷ số) | `amdahl/…:n_star` so với `e9/…summary_part_a.json:n_star` |

## (c) Các `\todo` còn lại
1. Bảng patch (`tab_patches`), bảng cài đặt (`tab_impl`, tài liệu bổ sung), bảng ngưỡng (`tab_threshold`): tự điền khi có `results/e11/E11_*/summary.json` và chạy lại `make_tables.py`.
2. Văn bản cần số E11: đoạn "Ngưỡng tính bằng mili giây", đoạn "Patch thật", Thảo luận "Nghiên cứu tình huống bổ sung điều gì", Thảo luận "Điều gì có thể làm đổi kết luận".
3. Hình patch (`fig6_patch_effects.pdf`): vẽ lại từ E11. `make_figs_v3.py` cần sửa để đọc E11.
4. Tác giả liên hệ và email; ORCID của từng tác giả; CRediT; DOI Zenodo.

## (d) Bảng kiểm tra trích dẫn (40 mục)

| Mục | Nguồn đã kiểm | Trạng thái |
|---|---|---|
| trackflood2026 | arxiv.org/abs/2609.33948 (Gu, Singh-Smith, Liao, Liu, Saremi; nộp 27/09/2026) | Khớp. Bản arXiv, chưa có venue. |
| eventburst2026 | arxiv.org/abs/2607.09115 (Baek, Lee, Lee) | Khớp. Bản arXiv. |
| antistyler2026 | CVPR 2026 poster 40065, CVF open access (Yankelev et al.) | Khớp |
| trace2026 | WACV 2026 poster 489 (Lee, Lee, Na, Park, Choi) | Khớp |
| rgbt2026 | CVPR 2026 poster 39343, arXiv 2605.04675 (Zhu, Zeng, Hu, Zhu, Hu) | Khớp |
| thermal2026 | CVPR 2026, tr. 34929–34939, arXiv 2511.09829 (Long, Jiang, Liu, …) | Khớp |
| underload2025 | CVPR 2025, tr. 19230–19240, arXiv 2412.02171 | Khớp |
| evade2025 | NeurIPS 2025 poster 118338 (Monteuuis, Chen, Petit) | Khớp |
| bitflip2025 | WACV 2025, tr. 6709–6718 (Sistla, Wen, …) | Khớp |
| apde2025 | ICCV 2025, tr. 23476–23486, arXiv 2508.00649 | Khớp |
| pbcat2025 | ICCV 2025, tr. 24456–24466, arXiv 2506.23581 | Khớp |
| oddr2025 | ICCV 2025, tr. 22999–23008 (Chattopadhyay, Guesmi, …) | Khớp |
| diffpad2025 | WACV 2025, tr. 6602–6611, arXiv 2410.24006 | Khớp. Lưu ý: thí nghiệm của bài là phân loại và nhận diện khuôn mặt; câu dẫn chỉ nói chung về cơ chế phòng thủ. |
| unifiedpatchdet2025 | CVPR 2025, tr. 30387–30397 (Kumar, Agarwal) | Khớp |
| iap2025 | ICCV 2025, tr. 14766–14775, arXiv 2507.06856 | Khớp |
| grac2025 | ICCV 2025, tr. 13880–13889 (Liang et al.) | Khớp |
| gs3dcamo2025 | ICCV 2025, tr. 28752–28762, arXiv 2507.01367 | Khớp |
| badpatch2025 | ICCV 2025 Workshops (Findings), tr. 6303–6313, arXiv 2412.01440 | Khớp |
| remotepatch2025 | CVPR 2025 Workshops (SAIAD), tr. 4330–4340 | Khớp |
| afog2025 | ICCV 2025, tr. 3184–3193, arXiv 2508.02987 | Khớp |
| yolov12 | arXiv 2502.12524 (Tian, Ye, Doermann) | Khớp. Bản arXiv; không thấy venue. |
| yolov13 | arXiv 2506.17733 (Lei et al.) | Khớp. Bản arXiv. |
| slowtrack2024 | AAAI 2024, 38(5): 4062–4070, DOI 10.1609/aaai.v38i5.28200 | Khớp |
| 17 mục kinh điển còn lại (shumailov2021sponge, nicgslowdown2022, phantom2023, overload2024, brown2017patch, athalye2018eot, ilyas2018blackbox, thys2019fooling, neubeck2006nms, redmon2016yolo, carion2020detr, lin2014coco, jocher2023ultralytics, paszke2019pytorch, efron1979bootstrap, cameron2008cluster, holm1979) | Đã kiểm bằng web ở phiên trước (15/17 mục của bản tiếng Anh) và có DOI hoặc venue chuẩn trong bib | Khớp. Hai mục chưa kiểm web ở phiên trước là mục kinh điển, có DOI. |

## (e) Câu hỏi cần quyết
1. **Duyệt đo lại E11** (Việc 1d): tag `prereg-e11-20261103`, rồi chạy khoảng 1,5–2,5 giờ khi máy rảnh. Lệnh ở mục "Lệnh" dưới đây.
2. Tác giả liên hệ, email, ORCID, CRediT: nhóm quyết định.
3. Tạp chí Q3 cụ thể: cần biết để chỉnh template (hiện dùng Elsevier CAS hai cột của gói cũ).
4. Có xoá gói cũ `paper_Q1_submission_v3/` và `paper_Q1_submission_v3.zip` không (giữ theo quy tắc cho đến khi được duyệt).
5. Nếu E11 làm đổi kết luận chính của Q3 (ví dụ một patch GA vượt MDE trong phiên), sẽ báo trước khi sửa văn bản.
6. Biên dịch trên Overleaf và gửi lại ảnh hoặc log nếu còn "??".

## Lệnh (chỉ chạy sau khi duyệt; không chạy gì khác trong lúc đo)
```bash
git tag prereg-e11-20261103
python -X utf8 sponge-sim/studies/e11_patch_remeasure/run.py --run-dir sponge-sim/results/e11/E11_P1cpu2_20261103 --e7-dir sponge-sim/results/e7_gpu/final/runs/e7
python -X utf8 sponge-sim/studies/e11_patch_remeasure/analyze.py sponge-sim/results/e11/E11_P1cpu2_20261103
python -X utf8 sponge-sim/studies/e11_patch_remeasure/analyze.py sponge-sim/results/e11/E11_P1cpu2_20261103 --exclude-flagged
python -X utf8 paper_vi/tables/make_tables.py && python -X utf8 paper_vi/tables/check_numbers.py --all
```
(chạy từ thư mục `sponge-sim` nếu script cần đường dẫn tương đối; các lần trước chạy từ `sponge-sim/`).
