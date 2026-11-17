from pathlib import Path
import json,hashlib,shutil
from PIL import Image,ImageDraw,ImageFont
R=Path(r'D:\Physical-Visual-DoS-EdgeAI-main');O=R/'paper_assets_20261013'/'COMPARISON'
sources={'underload':{'url':'https://arxiv.org/html/2412.02171v2','version':'13 March 2025','table':'Table 1, YOLOv8s COCO columns','metric':'mAP50 percent','rows':[['Standard clean',57.7],['Standard Overload',20.1],['Underload clean',45.7],['Underload Overload',42.0]],'note':'Published adversarial-training comparison, not our graybox patch protocol.'},'evade':{'url':'https://proceedings.neurips.cc/paper_files/paper/2025/file/371713c3e5314dff9483c62c5abb98a8-Paper-Conference.pdf','table':'Table 3, PDF page 7, YOLOv8n same-source/same-target entries','metric':'Rounded-up average output boxes after NMS','rows':[['Genuine',6],['Daedalus',247],['Overload',300],['Phantom Sponge',228],['Beyond Phantom Sponge',151]],'note':'COCO2017 validation. Counts after NMS are not our before-NMS candidates; counts are not latency.'},'local':{'path':'outputs/extended_q1_20261002/analysis.json','metric':'COCO AP50:95 bbox percent','rows':[['Clean',34.079449954282426],['SG-GA q2500',29.967882466988266]],'note':'128-image COCO val2017 subset, YOLOv8n 320 px, patch4%,10seeds; patch AP SD0.468259pp. Different objective/data/metric from published panels.'}}
sources['local']['sha256']=hashlib.sha256((R/sources['local']['path']).read_bytes()).hexdigest()
(O/'foundation_sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
W,H=3000,1500;im=Image.new('RGB',(W,H),'white');d=ImageDraw.Draw(im)
def font(n,b=False):return ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf' if b else r'C:\Windows\Fonts\arial.ttf',n)
def tx(x,y,t,n=40,b=False,anchor=None):d.text((x,y),t,font=font(n,b),fill='#202A34',anchor=anchor)
tx(1500,40,'CÁC PHÉP ĐO TỪ BÀI NỀN VÀ SPONGE PATCH',58,True,'mt')
tx(1500,120,'Ba giao thức và đơn vị riêng biệt · không xếp hạng xuyên panel',40,False,'mt')
configs=[('A  Underload 2025',['YOLOv8s · COCO','mAP50 (%) · Bảng 1'],[57.7,20.1,45.7,42.0],['Gốc\nsạch','Gốc\nOverload','AT\nsạch','AT\nOverload'],60,10),('B  EVADE 2025',['YOLOv8n · COCO val2017','Hộp SAU NMS · Bảng 3'],[6,247,300,228,151],['Sạch','Dae.','Over.','Phan.','Beyond'],320,100),('C  Nhóm nghiên cứu',['YOLOv8n · 128 ảnh · patch 4%','AP50:95 (%) · 10 seed'],[34.07945,29.96788],['Sạch','SG-GA\n2.500 lượt'],40,10)]
colors=['#2478B4','#E58932','#239E80','#8F58B5','#89939D']
for i,(title,lines,values,labels,maximum,step) in enumerate(configs):
 x=55+i*1000;tx(x,235,title,45,True)
 for j,line in enumerate(lines):tx(x,305+j*58,line,37)
 left,right,top,bottom=x+75,x+875,455,1050
 for tick in range(0,maximum+1,step):
  y=bottom-tick/maximum*(bottom-top);d.line((left,y,right,y),fill='#DDE2E5',width=2);tx(left-15,y,str(tick),33,False,'rm')
 d.line((left,top,left,bottom),fill='#263238',width=3)
 slot=(right-left)/len(values)
 for j,v in enumerate(values):
  cx=left+slot*(j+.5);bw=slot*.62;y=bottom-v/maximum*(bottom-top);d.rectangle((cx-bw/2,y,cx+bw/2,bottom),fill=colors[j]);tx(cx,y-18,str(round(v,2)) if i==2 else str(v),40,True,'mb')
  if i==2 and j==1:
   dy=.468259/maximum*(bottom-top);d.line((cx,y-dy,cx,y+dy),fill='black',width=4);d.line((cx-15,y-dy,cx+15,y-dy),fill='black',width=4)
  for k,line in enumerate(labels[j].split('\n')):tx(cx,bottom+20+k*47,line,34,False,'mt')
 notes=[['AT: model được huấn luyện đối kháng.','Không thay bằng fine-tuning thường.'],['Dae./Over./Phan./Beyond: 4 tấn công.','Số hộp không phải thời gian NMS.'],['Chỉ sửa patch, không cập nhật model.','Thanh sai số patch: SD giữa seed.']][i]
 for k,line in enumerate(notes):tx(x,1190+k*53,line,35)
d.line((55,1340,2945,1340),fill='#CDD3D8',width=2)
tx(1500,1375,'Khác AP50 và AP50:95 · khác tập ảnh, quyền truy cập và phép can thiệp',38,True,'mt')
tx(1500,1430,'Nguồn và scalar truy vết: foundation_sources.json · Không tính chênh lệch xuyên panel',34,False,'mt')
p=O/'so_sanh_bai_nen_va_sponge.png';im.save(p,dpi=(300,300));shutil.copy2(p,R/'paper_assets_20261013'/'RECOMMENDED'/'14_so_sanh_bai_nen_va_sponge.png')
print('Foundation comparison created from primary-table scalars')
