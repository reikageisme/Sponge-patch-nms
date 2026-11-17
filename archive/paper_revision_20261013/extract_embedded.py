from pathlib import Path
import zipfile,hashlib,json,csv,io
from PIL import Image,ImageDraw,ImageFont
root=Path(r'D:\Physical-Visual-DoS-EdgeAI-main');out=root/'paper_assets_20261013';rows=json.loads((out/'inventory.json').read_text(encoding='utf-8')); hashes={r['sha256']:r for r in rows if not r['duplicate_of']};added=[]
p=root/'_paper_revision_20261013/BaoCaoKhoaHocAdversarialAttacks_NangCap_VI.before_rewrite.docx'
with zipfile.ZipFile(p) as z:
 for n in z.namelist():
  if not n.startswith('word/media/') or Path(n).suffix.lower() not in ['.png','.jpg','.jpeg','.svg']:continue
  data=z.read(n);h=hashlib.sha256(data).hexdigest();w=height=None
  try:
   with Image.open(io.BytesIO(data)) as im:w,height=im.size
  except:pass
  dup=hashes.get(h)
  if dup:copy=dup['copy'];did=dup['id']
  else:
   target=out/'EMBEDDED_ORIGINAL_MANUSCRIPT'/Path(n).name;target.parent.mkdir(exist_ok=True);target.write_bytes(data);copy=target.relative_to(out).as_posix();did=''
  r={'id':f'IMG{len(rows)+1:04d}','source':p.name+'::'+n,'copy':copy,'sha256':h,'width':w,'height':height,'group':'EMBEDDED_ORIGINAL_MANUSCRIPT','scope':'Original manuscript media, must inspect caption/provenance before retaining','status':'review','duplicate_of':did};rows.append(r)
  if not dup:hashes[h]=r;added.append(r)
(out/'inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
with (out/'inventory.csv').open('w',encoding='utf-8-sig',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
if added:
 sheet=Image.new('RGB',(1600,((len(added)+4)//5)*260),'#ddd');draw=ImageDraw.Draw(sheet);font=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',15)
 for k,r in enumerate(added):
  if not r['width']:continue
  im=Image.open(out/r['copy']).convert('RGB');im.thumbnail((310,220));x=k%5*320;y=k//5*260;sheet.paste(im,(x,y));draw.text((x,y+224),r['id']+' '+Path(r['copy']).name,fill='black',font=font)
 sheet.save(out/'CONTACT_SHEETS/EMBEDDED_ORIGINAL_01.jpg')
print(json.dumps({'embedded_media':sum(r['group']=='EMBEDDED_ORIGINAL_MANUSCRIPT' for r in rows),'new_unique':len(added),'total_candidates':len(rows),'unique':len(hashes),'new':added},ensure_ascii=False,indent=2))
