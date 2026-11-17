from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,shutil
R=Path(r'D:\Physical-Visual-DoS-EdgeAI-main');p=R/'outputs/extended_q1_20261002/analysis.json';a=json.loads(p.read_text(encoding='utf-8'))
rows=[]
for name,side in [('area_1',32),('area_2',45),('sg_ga',64),('area_8',90),('area_16',128)]:
 m=next(x for x in a['methods'] if x['name']==name and x['budget']==400)
 rows.append({'name':name,'side':side,'area_pct':100*side*side/320**2,**m['candidate_ratio']})
o=R/'paper_assets_20261013/COMPARISON';(o/'area_replot_sources.json').write_text(json.dumps({'source_path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rows':rows,'reason':'Regenerated from scalar/CI: original plot title mislabeled area as component ablation; original image retained.'},ensure_ascii=False,indent=2),encoding='utf-8')
im=Image.new('RGB',(2500,1230),'white');d=ImageDraw.Draw(im)
def tx(x,y,t,n=35,b=False,anchor=None):d.text((x,y),t,font=ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf' if b else r'C:\Windows\Fonts\arial.ttf',n),fill='#202A34',anchor=anchor)
tx(1250,30,'DIỆN TÍCH MIẾNG DÁN VÀ TỶ SỐ ỨNG VIÊN',46,True,'mt');tx(1250,98,'400 lượt ảnh · 128 ảnh kiểm tra · 10 seed · ngưỡng 0,01 · không cap',33,False,'mt')
left,right,top,bottom=230,2350,235,930
tx(65,180,'Tỷ số ứng viên so với ảnh sạch',32,True)
for i in range(6):
 tick=i*.2;y=bottom-tick/1.12*(bottom-top);d.line((left,y,right,y),fill='#DDE2E5',width=2);tx(left-25,y,f'{tick:.1f}',31,False,'rm')
y=bottom-1/1.12*(bottom-top)
for x in range(left,right,24):d.line((x,y,min(x+12,right),y),fill='#555555',width=3)
colors=['#2478B4','#E58932','#239E80','#8F58B5','#B77DA4']
for i,row in enumerate(rows):
 cx=left+(right-left)*(i+.5)/5;v=row['mean'];y=bottom-v/1.12*(bottom-top);d.rectangle((cx-130,y,cx+130,bottom),fill=colors[i]);lo,hi=row['conditional_paired_seed_bootstrap_95ci'];yl=bottom-lo/1.12*(bottom-top);yh=bottom-hi/1.12*(bottom-top);d.line((cx,yl,cx,yh),fill='black',width=4)
 for yy in [yl,yh]:d.line((cx-20,yy,cx+20,yy),fill='black',width=4)
 tx(cx,yh-18,f'{v:.4f}',34,True,'mb');tx(cx,950,f"{row['area_pct']:.2f}%",34,True,'mt');tx(cx,1000,f"{row['side']} × {row['side']} px",31,False,'mt')
tx(1250,1090,'Thanh sai số: bootstrap 95% theo seed trên bộ ảnh cố định; đường đứt: sạch = 1',30,False,'mt')
tx(1250,1140,'Nguồn: analysis.json · Diện tích đổi cả vùng che và số chiều tìm kiếm',30,False,'mt')
out=o/'dien_tich_kiem_chung.png';im.save(out,dpi=(300,300));shutil.copy2(out,R/'paper_assets_20261013/RECOMMENDED/13_dien_tich_kiem_chung.png');print('Area scalar/CI replot ready')
