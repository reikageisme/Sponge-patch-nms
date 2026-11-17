from pathlib import Path
import hashlib,json,csv,shutil,os
from PIL import Image,ImageOps,ImageDraw,ImageFont
root=Path(r'D:\Physical-Visual-DoS-EdgeAI-main'); out=root/'paper_assets_20261013'; out.mkdir(exist_ok=True)
manifest=json.loads((root/'outputs/extended_q1_20261002/figures/manifest.json').read_text(encoding="utf-8"))['figures']
rows=[]; hashes={}; excluded=[]
for folder in ['figures','docs/media','media','outputs','project_yolov13/results']:
 for p in sorted((root/folder).rglob('*')):
  if not p.is_file() or p.suffix.lower() not in ['.png','.jpg','.jpeg','.svg']:continue
  rel=p.relative_to(root).as_posix()
  if any(x in rel for x in ['/datasets/','/weights/','/vendor_underload/','/docx_qa','__pycache__']):
   excluded.append({'source':rel,'reason':'dataset / weights / vendor assets / document QA; not manuscript evidence'}); continue
  if rel.startswith('outputs/extended_q1_20261002/figures/'):
   group='SPONGE_VALIDATED'; scope=manifest.get(p.name,{}).get('description_vi',''); status='recommended'
  elif rel=='project_yolov13/results/fullscale_mAP_growth.png':
   group='MAIN_CURRENT_YOLO';scope='Fullscale person detection, 4 models x 5 seeds; accuracy versus wall-clock budget, not Visual DoS';status='recommended'
  elif rel.startswith('figures/') and 'camera' not in p.name:
   group='ILLUSTRATIVE_SCHEMES';scope='Method schematic, not measured result';status='recommended'
  elif '/benchmark/' in rel and rel.startswith('project_yolov13/'):
   group='SUPPLEMENTARY_HISTORICAL';scope='Prior benchmark qualitative batches; cannot establish fullscale accuracy or availability';status='historical'
  elif 'extended_q1_20261002' in rel:
   group='SPONGE_PATCH_LIBRARY';scope='Saved optimized patch, checkpoint or rendering from local Sponge study; candidate texture only, not outcome chart';status='supplement'
  elif 'local_q1_20261002_v2' in rel:
   group='SUPPLEMENTARY_LOCAL_VALIDATION';scope='Local validation precursor, separate from fullscale and extended Q1';status='supplement'
  else:
   group='SUPPLEMENTARY_HISTORICAL';scope='Historical/media/pilot figure; provenance insufficient for new quantitative claims';status='historical'
  h=hashlib.sha256(p.read_bytes()).hexdigest(); w=height=None
  try:
   with Image.open(p) as im:w,height=im.size
  except: pass
  if h in hashes:
   copied=hashes[h]['copy']; duplicate=hashes[h]['id']
  else:
   target=out/group/p.relative_to(root);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);copied=target.relative_to(out).as_posix();duplicate=''
  row={'id':f'IMG{len(rows)+1:04d}','source':rel,'copy':copied,'sha256':h,'width':w,'height':height,'group':group,'scope':scope,'status':status,'duplicate_of':duplicate}
  rows.append(row)
  if not duplicate:hashes[h]=row
(out/'inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'excluded.json').write_text(json.dumps(excluded,ensure_ascii=False,indent=2),encoding='utf-8')
with (out/'inventory.csv').open('w',encoding='utf-8-sig',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
sheets=out/'CONTACT_SHEETS';sheets.mkdir(exist_ok=True)
font=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',15)
for group in sorted({r['group'] for r in rows}):
 unique=[r for r in rows if r['group']==group and not r['duplicate_of'] and r['width']]
 for n in range(0,len(unique),40):
  chunk=unique[n:n+40]; sheet=Image.new('RGB',(1600,((len(chunk)+4)//5)*230),'#dddddd');draw=ImageDraw.Draw(sheet)
  for k,r in enumerate(chunk):
   im=Image.open(out/r['copy']).convert('RGB');im.thumbnail((308,190));x=(k%5)*320;y=(k//5)*230
   sheet.paste(im,(x+(320-im.width)//2,y));draw.text((x+5,y+193),r['id']+' '+Path(r['source']).name[:25],fill='black',font=font);draw.text((x+5,y+211),str(r['width'])+'x'+str(r['height']),fill='black',font=font)
  sheet.save(sheets/f'{group}_{n//40+1:02d}.jpg',quality=88)
print(json.dumps({'candidates':len(rows),'unique':len(hashes),'excluded':len(excluded),'groups':{g:sum(r['group']==g and not r['duplicate_of'] for r in rows) for g in sorted({r['group'] for r in rows})},'sheets':[p.name for p in sheets.glob('*.jpg')]},indent=2))

