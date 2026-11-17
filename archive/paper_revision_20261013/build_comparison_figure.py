from pathlib import Path
import json, statistics, hashlib, shutil
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r'D:\Physical-Visual-DoS-EdgeAI-main')
WORK = ROOT / '_paper_revision_20261013'
OUT = ROOT / 'paper_assets_20261013' / 'COMPARISON'
OUT.mkdir(exist_ok=True)
source = json.loads((WORK / 'published_comparison.json').read_text(encoding='utf-8'))
lat = json.loads((ROOT / 'project_yolov13/results/fullscale_experiments/latency_records.json').read_text(encoding='utf-8'))
print('LATENCY KEYS',list(lat) if isinstance(lat,dict) else 'list')

def collect_entries(value):
    if isinstance(value, list):
        for item in value: yield from collect_entries(item)
    elif isinstance(value, dict):
        if 'latency_median_ms_per_frame' in value: yield value
        else:
            for item in value.values(): yield from collect_entries(item)

entries = list(collect_entries(lat))
local = []
for key,label in [('yolo11n','YOLO11n'),('yolov12n','YOLOv12n'),('yolov13n','YOLOv13n'),('yolov13s','YOLOv13s')]:
    es=[x for x in entries if x['model_key']==key]
    budget=es[0]['sweet_spot_minutes'];maps=[]
    for path in sorted((ROOT / 'project_yolov13/results/fullscale_experiments/records' / key).glob('*.json')):
        d=json.loads(path.read_text(encoding='utf-8'))
        row=next(x for x in d['milestones'] if x['budget_minutes']==budget)
        metrics=row['test'] if 'test' in row else row['test_metrics']
        maps.append(metrics['map50_95']*100)
    local.append({'model':label,'map_mean':statistics.mean(maps),'map_sd':statistics.stdev(maps),
                  'latency_ms':statistics.mean(x['latency_median_ms_per_frame'] for x in es),'budget':budget})

W,H=3000,1720
im=Image.new('RGB',(W,H),'white');draw=ImageDraw.Draw(im)
fontpath=Path(r'C:\Windows\Fonts\arial.ttf');boldpath=Path(r'C:\Windows\Fonts\arialbd.ttf')
def font(n,bold=False):return ImageFont.truetype(str(boldpath if bold else fontpath),n)
def text(x,y,s,n=32,bold=False,fill='#202A34',anchor=None):draw.text((x,y),s,font=font(n,bold),fill=fill,anchor=anchor)
text(W//2,45,'ĐỐI CHIẾU SỐ LIỆU CÔNG BỐ VÀ THỰC NGHIỆM',54,True,anchor='mt')
text(W//2,118,'Hai giao thức riêng biệt — chỉ so sánh mô hình bên trong từng panel',34,False,anchor='mt')
colors=['#2478B4','#E58932','#239E80','#8F58B5']

for pi in range(2):
    px=95+pi*1480
    title='A  Công bố YOLOv13 năm 2025' if pi==0 else 'B  Thực nghiệm của nhóm'
    text(px,215,title,43,True)
    lines=['COCO val2017 · 80 lớp · 640 px','Tesla T4 · TensorRT FP16','AP50:95 công bố trong Bảng I'] if pi==0 else ['COCO + AdvT-shirt · 1 lớp person · 416 px','RTX 5060 · PyTorch FP32 · batch 1','Test mAP50:95 tại mốc chọn theo validation']
    for j,line in enumerate(lines):text(px,278+46*j,line,31)
    left,right,top,bottom=px+80,px+1290,470,1120
    for tick in range(0,56,10):
        y=bottom-tick/55*(bottom-top)
        draw.line((left,y,right,y),fill='#DDE2E5',width=2)
        text(left-20,y,str(tick),27,anchor='rm')
    draw.line((left,top,left,bottom),fill='#263238',width=3)
    text(px,425,'AP50:95 (%)',29,True)
    for j in range(4):
        x=left+65+j*295
        value=source['published_rows'][j]['ap50_95_pct'] if pi==0 else local[j]['map_mean']
        y=bottom-value/55*(bottom-top)
        draw.rectangle((x,y,x+175,bottom),fill=colors[j])
        if pi==1:
            sd=local[j]['map_sd'];dy=sd/55*(bottom-top)
            draw.line((x+87,y-dy,x+87,y+dy),fill='black',width=4)
            draw.line((x+65,y-dy,x+110,y-dy),fill='black',width=4)
            draw.line((x+65,y+dy,x+110,y+dy),fill='black',width=4)
        valtext=f'{value:.2f}' if pi else f'{value:.1f}'
        text(x+87,y-38,valtext,34,True,anchor='mb')
        text(x+87,bottom+20,local[j]['model'],31,True,anchor='mt')
    label='Latency inference công bố (ms)' if pi==0 else 'Latency pipeline trung bình (ms)'
    text(px,1230,label,33,True)
    vals=[x['latency_ms'] for x in source['published_rows']] if pi==0 else [x['latency_ms'] for x in local]
    for j,v in enumerate(vals):text(left+152+j*295,1290,f'{v:.2f}',34,True,anchor='mt')
    detail='Không có SD trong bảng công bố.' if pi==0 else 'Thanh sai số mAP: SD giữa 5 seed; mốc 120/120/5/10 phút.'
    text(px,1380,detail,28)

draw.line((65,1480,W-65,1480),fill='#C7CDD2',width=2)
text(W//2,1510,'Khác dataset, số lớp, pretrained, input, phần cứng, backend và precision.',31,True,anchor='mt')
text(W//2,1558,'Không lấy chênh lệch giữa hai panel để kết luận phương pháp nhóm tốt hơn bài công bố.',30,False,anchor='mt')
text(W//2,1610,'Nguồn A: Lei và cộng sự, arXiv 2506.17733v2, Bảng I. Nguồn B: 20 records và latency_records.json.',27,False,anchor='mt')
png=OUT/'so_sanh_cong_bo_va_thuc_nghiem.png';im.save(png,dpi=(300,300))
recommended=ROOT/'paper_assets_20261013/RECOMMENDED/12_so_sanh_cong_bo_va_thuc_nghiem.png'
shutil.copy2(png,recommended)
receipt={'source':source['source'],'published_rows':source['published_rows'],'local_rows':local,
         'scope':'Separate published COCO80/T4TensorRTFP16 inference and local person/RTX5060FP32 pipeline protocols; not cross-study superiority.',
         'image':str(png),'sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'errorbars':'Local mAP sample SD across5seeds only; no published uncertainty invented.'}
(OUT/'comparison_sources.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(local,ensure_ascii=False,indent=2))
print('FIGURE',recommended)
