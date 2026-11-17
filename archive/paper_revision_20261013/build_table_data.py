import json
import pathlib
import statistics as st

ROOT = pathlib.Path(__file__).resolve().parent.parent
P = ROOT / 'outputs/extended_q1_20261002'
A = json.loads((P / 'analysis.json').read_text())
TABLES = {}

def fmt(x, digits=2):
    return f'{x:.{digits}f}'.replace('.', ',')

def ms(values, digits=2):
    return fmt(st.mean(values), digits) + ' ± ' + fmt(st.stdev(values), digits)

def add(key, number, title, headers, rows, note):
    assert all(len(r) == len(headers) for r in rows), key
    TABLES[key] = dict(caption=f'Bảng {number}. {title}', headers=headers, rows=rows, note=note)

add('algorithm', 1, 'Quy trình tối ưu và đánh giá miếng dán.',
    ['Bước', 'Thao tác'], [
        ['1', 'Khởi tạo 20 tensor RGB; chọn vị trí theo chính sách.'],
        ['2', 'Chèn từng cá thể vào bốn ảnh tối ưu.'],
        ['3', 'Lấy mẫu biến đổi; suy luận và đọc confidence trước NMS.'],
        ['4', 'Tính fitness; ghi số lượt ảnh và cá thể tốt nhất.'],
        ['5', 'Giữ năm cá thể ưu tú; lai ghép ngang và đột biến.'],
        ['6', 'Dừng khi hết ngân sách lượt ảnh; khóa miếng dán.'],
        ['7', 'Đánh giá độc lập ứng viên, AP, latency và QoS.']],
    'Một đánh giá cá thể dùng bốn lượt ảnh với một mẫu EOT/ảnh, 16 lượt với bốn mẫu. Tập kiểm tra không chọn miếng dán. Đột biến ở nhánh mở rộng dùng Gaussian σ=0,2, xác suất 0,1, chặn RGB về [0;1].')

add('protocols', 2, 'Phân biệt giao thức Sponge và benchmark detector bổ sung.',
    ['Thuộc tính', 'Nhánh A: Sponge/NMS', 'Nhánh B: phát hiện người'], [
        ['Mục tiêu', 'Ứng viên, AP, chi phí và QoS sạch–patch', 'Chất lượng, ngân sách học và latency detector'],
        ['Mô hình', 'YOLOv8n; chuyển giao sáu detector', 'YOLO11n, YOLOv12n, YOLOv13n/s'],
        ['Dữ liệu', 'Bốn ảnh tối ưu; 128 ảnh COCO val2017 kiểm tra', '11.123 ảnh COCO + AdvT-shirt'],
        ['Đầu vào', '320 × 320; patch cơ sở 64 × 64', '416 px; target một lớp person'],
        ['Lặp', '10 seed miếng dán', '5 seed mỗi model; 20 quỹ đạo'],
        ['Thiết bị', 'CPU laptop i5-1335U', 'RTX 5060, 7,96 GiB VRAM'],
        ['Ngân sách', '400/1.000/2.500 lượt ảnh', '5/10/20/30/60/120 phút theo CSV'],
        ['Đánh giá', 'COCO AP hộp; thresholds/cap công bố riêng', 'Test 1.668 ảnh; latency batch 1 FP32']],
    'Nhánh B dùng split cố định 7.786/1.669/1.668; holdout đối với fine-tuning, chưa bảo đảm độc lập với pretraining. Không gộp AP hai nhánh hoặc coi benchmark person là thử nghiệm DoS.')

names = {'sg_ga': 'SG-GA', 'ga_center': 'GA tâm', 'ga_random_location': 'GA vị trí ngẫu nhiên', 'random_search': 'Tìm kiếm ngẫu nhiên'}
clean = json.loads((P / 'evaluation/clean_seed0_q0.json').read_text())
cm = next(x for x in clean['metrics'] if x['threshold'] == .01 and x['pre_nms_cap'] is None)
rows = [['Sạch', '1,0000', fmt(cm['coco_subset_bbox']['AP'] * 100), '0']]
for x in A['methods']:
    if x['budget'] == 2500:
        r = x['candidate_ratio']
        rows.append([names[x['name']], fmt(r['mean'], 4) + ' ± ' + fmt(r['sample_std'], 4), fmt(x['AP_mean_over_patch_seeds'] * 100) + ' ± ' + fmt(x['AP_sample_std_over_patch_seeds'] * 100), '2.500'])
add('sponge_primary', 3, 'Tỷ số ứng viên và AP trên 128 ảnh ở ngân sách 2.500 lượt ảnh.',
    ['Điều kiện', 'Tỷ số ứng viên μ ± SD', 'AP hộp (%) μ ± SD', 'Lượt ảnh'], rows,
    '10 seed; τ=0,01, không cap. Ratio là mean theo ảnh của ứng viên patch/ứng viên sạch rồi tổng hợp theo seed. AP gộp ảnh trước khi tổng hợp seed. Baseline sạch không tạo SD nhân tạo. Primary SG-GA−GA tâm: −0,005132; CI bootstrap 95% [−0,011178; 0,000706]; p đảo dấu=0,150391.')

rows = []
for size, key in [(32, 'area_1'), (45, 'area_2'), (64, 'sg_ga'), (90, 'area_8'), (128, 'area_16')]:
    x = next(x for x in A['methods'] if x['name'] == key and x['budget'] == 400)
    r = x['candidate_ratio']
    rows.append([f'{size} × {size}', fmt(size * size / (320 * 320) * 100), fmt(r['mean'], 4) + ' ± ' + fmt(r['sample_std'], 4), fmt(x['AP_mean_over_patch_seeds'] * 100) + ' ± ' + fmt(x['AP_sample_std_over_patch_seeds'] * 100)])
add('area', 4, 'Đánh giá diện tích miếng dán trên ảnh kiểm tra.',
    ['Patch (px)', 'Diện tích (%)', 'Tỷ số ứng viên μ ± SD', 'AP hộp (%) μ ± SD'], rows,
    '128 ảnh, 10 seed, 400 lượt ảnh; τ=0,01, không cap. Mức 4% là SG-GA cơ sở. Diện tích đổi cả vùng che và số chiều tìm kiếm; không suy luận tác động đơn lẻ hoặc DoS từ giảm AP.')

rows = []
for threads in [1, 2, 4]:
    for condition in ['clean', 'sg_ga']:
        x = next(x for x in A['processing_budget_exploratory'] if x['cpu_threads'] == threads and x['condition'] == condition)
        rows.append([str(threads), 'Sạch' if condition == 'clean' else 'SG-GA', fmt(x['median_ms_mean_over_seeds']), fmt(x['p95_ms_mean_over_seeds']), fmt(x['late_fraction']['mean'] * 100)])
add('processing', 5, 'Thời gian đường xử lý tensor đã chuẩn bị và ngân sách 300 ms.',
    ['Luồng CPU', 'Điều kiện', 'Mean median (ms)', 'Mean p95 (ms)', 'Trễ (%)'], rows,
    'Mỗi dòng tổng hợp 10 block seed, 16 ảnh/block và ba lượt đo/ảnh. Mean của median/p95 từng block, không phải quantile gộp. SG-GA là patch nguồn của nhánh backend, giữ đúng manifest; đổi luồng CPU vẫn trên một thiết bị. Không gồm camera/hàng đợi.')

rows = []
policy_names = {'fifo': 'FIFO', 'drop_if_busy': 'Bỏ khi bận', 'adaptive_throttle': 'Điều tiết'}
for period in [100, 300]:
    for policy in ['fifo', 'drop_if_busy', 'adaptive_throttle']:
        for condition in ['clean', 'sg_ga']:
            stream_key = 'clean' if condition == 'clean' else 'sg_ga_q2500'
            files = list((P / 'stream_qos').glob(f'{stream_key}_seed*_period{period}_{policy}.json'))
            records = [json.loads(f.read_text()) for f in files]
            assert len(records) == 10, (condition, period, policy, len(records))
            rows.append([str(period), policy_names[policy], 'Sạch' if condition == 'clean' else 'SG-GA 2.500', fmt(st.mean(x['discarded_frames'] / x['offered_frames'] * 100 for x in records)), fmt(st.mean(x['missing_or_late_fraction'] * 100 for x in records)), fmt(st.mean(x['on_time_fps'] for x in records)), fmt(st.mean(x['deadline_delivered_coco_bbox']['AP'] * 100 for x in records))])
add('stream', 6, 'Dịch vụ theo toàn bộ ảnh phát: sạch và SG-GA.',
    ['Chu kỳ (ms)', 'Chính sách', 'Điều kiện', 'Bỏ (%)', 'Thiếu/trễ (%)', 'Đúng hạn (ảnh/s)', 'AP đúng hạn (%)'], rows,
    'Mean 10 seed, mỗi block 32 ảnh; deadline 300 ms. Đây là 120 block sạch/SG-GA trong tổng 240 block của giao thức. Ảnh bỏ hoặc trễ được tính dự đoán rỗng khi đo AP đúng hạn. FIFO sạch đã quá tải ở chu kỳ 100 ms, nên không quy thất bại đó cho patch.')

rows = []
for condition, budget in [('clean', 0), ('sg_ga', 2500)]:
    records = [json.loads(f.read_text()) for f in (P / 'evaluation').glob(f'{condition}_seed*_q{budget}.json')]
    assert len(records) == 10
    for threshold, cap in [(.01, None), (.01, 100), (.25, None)]:
        metrics = [next(x for x in r['metrics'] if x['threshold'] == threshold and x['pre_nms_cap'] == cap) for r in records]
        d = next(x for x in A['defense_tradeoffs'] if x['name'] == condition and x['budget'] == budget and x['threshold'] == threshold and x['pre_nms_cap'] == cap)
        rows.append(['Sạch' if condition == 'clean' else 'SG-GA 2.500', fmt(threshold), 'Không cap' if cap is None else str(cap), fmt(st.mean(x['coco_subset_bbox']['AP'] * 100 for x in metrics)), fmt(st.mean(x['coco_subset_bbox']['AR100'] * 100 for x in metrics)), fmt(d['postprocess_mean_over_seed_ms'])])
add('defense', 7, 'Đánh đổi ngưỡng/cap với chất lượng và hậu xử lý.',
    ['Điều kiện', 'τ', 'Top-k', 'AP (%)', 'AR100 (%)', 'Lọc + NMS (ms)'], rows,
    'Mean theo 10 seed trên 128 ảnh; AP/AR gộp ảnh trước khi tổng hợp seed. Cùng patch, thay cấu hình hậu xử lý. Các ô thời gian là mean đã lưu trong analysis, không phải median. Không mặc định top-k/threshold là phòng thủ thành công với mọi ứng dụng.')

model_names = {'yolov8n': 'YOLOv8n (nguồn)', 'yolov8s': 'YOLOv8s', 'ssdlite': 'SSDLite MobileNetV3', 'fasterrcnn': 'Faster R-CNN MobileNetV3', 'retinanet': 'RetinaNet ResNet50', 'detr': 'DETR ResNet50'}
rows = []
for x in A['transfer_exploratory']:
    key = x['model']
    rec = [json.loads(f.read_text()) for f in (P / 'transfer').glob(f'{key}_seed*.json')]
    assert len(rec) == 10, key
    ratio = x['within_model_paired_latency_ratio']
    ci = ratio['conditional_paired_seed_bootstrap_95ci']
    rows.append([model_names.get(key, key), fmt(ratio['mean'], 4), '[' + fmt(ci[0], 4) + '; ' + fmt(ci[1], 4) + ']', fmt(st.mean(r['coco_subset_bbox']['clean']['AP'] * 100 for r in rec)), fmt(st.mean(r['coco_subset_bbox']['patched']['AP'] * 100 for r in rec))])
add('transfer', 8, 'Chuyển giao: tỷ số latency bên trong từng detector.',
    ['Detector', 'Tỷ số latency', 'CI bootstrap 95%', 'AP sạch (%)', 'AP patch (%)'], rows,
    '16 ảnh chung, 10 miếng dán nguồn. CI theo seed trên ảnh cố định. Mỗi model có preprocessing/hậu xử lý riêng; không so latency tuyệt đối giữa dòng. DETR không có NMS. Không kết luận DoS xuyên kiến trúc từ giảm AP.')

F = ROOT / 'project_yolov13/results/fullscale_experiments'
L = json.loads((F / 'latency_records.json').read_text())
rows = []
for key, info in L['sweet_spots'].items():
    budget = info['sweet_spot_minutes']
    rec = [json.loads(f.read_text()) for f in (F / 'records' / key).glob('*.json')]
    milestones = [next(x for x in r['milestones'] if x['budget_minutes'] == budget) for r in rec]
    timing = [x['latency_median_ms_per_frame'] for x in L['records'] if x['model_key'] == key]
    rows.append([info['label'], str(budget), ms([x['test']['precision'] * 100 for x in milestones]), ms([x['test']['recall'] * 100 for x in milestones]), ms([x['test']['map50'] * 100 for x in milestones]), ms([x['test']['map50_95'] * 100 for x in milestones]), ms(timing)])
add('yolo_metrics', 9, 'Benchmark person tại mốc chọn theo validation.',
    ['Model', 'Mốc (phút)', 'Precision (%)', 'Recall (%)', 'mAP50 (%)', 'mAP95 (%)', 'Pipeline (ms)'], rows,
    'μ ± sample SD giữa năm seed. Mỗi model có sweet spot riêng, không cùng ngân sách/capacity. Test một lớp person, 1.668 ảnh; RTX 5060, 416 px, batch 1 FP32, median 500 ảnh sau 32 warm-up. Chưa có raw timing để tái tính p95/p99 hoặc cùng operating point accuracy/latency.')

add('routes', 10, 'Đối chiếu hướng nghiên cứu: lợi ích, giới hạn và căn cứ của nhóm.',
    ['Hướng / nguồn', 'Ưu điểm có căn cứ', 'Chi phí / giới hạn', 'Quan hệ với nghiên cứu này'], [
        ['Underload [C:underload2025]', 'Phòng thủ có xét năng lực hardware; đo phục hồi thời gian thực.', 'Cần huấn luyện đối kháng; phụ thuộc mô hình/threat đã thử.', 'Nhóm đo workload/QoS; chưa có bảo đảm phòng thủ tương đương.'],
        ['EVADE [C:evade2025]', 'Kiểm tính thực dụng qua hardware/format/quantization và deadline.', 'Kết quả âm chỉ có phạm vi cấu hình đã đánh giá.', 'Nhóm bổ sung thử nghiệm hẹp có truy vết; chỉ một laptop và một GPU.'],
        ['APDE [C:apde2025]', 'Đánh giá nhiều patch/model/metric; đối chứng adaptive.', 'Phát hiện patch/AP không tự bảo đảm availability.', 'Nhóm tách AP/candidates/QoS; tập nhỏ, chưa so đủ SOTA.'],
        ['BadPatch / GRAC [C:badpatch2025] [C:grac2025]', 'Thử vật lý, áo/texture, nhiều điều kiện nhìn.', 'Evasion và gradient/diện tích khác; không phải QoS Sponge.', 'Nhóm giữ patch 4%, không gradient; chưa xác nhận quang học.'],
        ['SG-GA của nhóm', 'Không đọc gradient/trọng số; cùng diện tích/query; đánh giá độc lập.', 'Cần confidence trước NMS; primary chưa hơn GA tâm.', 'Giá trị hiện tại là kiểm định ranh giới surrogate; không tuyên bố tấn công mạnh hơn.'],
        ['Benchmark detector của nhóm', 'Cùng split/hardware, 20 quỹ đạo; tradeoff đo trực tiếp.', 'Khác capacity/mốc; chưa có pretrained mốc 0 hoặc DoS trên detector mới.', '13s tăng mAP, latency cao; dùng chọn cấu hình cho phép thử tiếp.']],
    'So sánh vai trò và ràng buộc, không xếp hạng sức mạnh xuyên threat model. Ưu điểm tiềm năng về quyền truy cập phải được cân cùng hạn chế hiệu quả và giả định telemetry.')

destination = ROOT / '_paper_revision_20261013/table_data.json'
destination.write_text(json.dumps(TABLES, ensure_ascii=False, indent=2), encoding='utf-8')
print('READY', destination)
print({k: len(v['rows']) for k, v in TABLES.items()})
