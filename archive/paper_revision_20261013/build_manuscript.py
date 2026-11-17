from pathlib import Path
import re,json,hashlib
from docx import Document
from docx.shared import Pt,Cm,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from PIL import Image

ROOT=Path(r'D:\Physical-Visual-DoS-EdgeAI-main'); WORK=ROOT/'_paper_revision_20261013'
source=WORK/'BaoCaoKhoaHocAdversarialAttacks_NangCap_VI.before_rewrite.docx'
draft=(WORK/'manuscript_draft.md').read_text(encoding='utf-8').replace('Δₛ = Rₛᴿᴳ − Rₛᶜᵉⁿᵗᵉʳ','Δₛ = Rₛ(SG-GA) − Rₛ(GA tâm)')
refs=json.loads((WORK/'recent_refs.json').read_text(encoding='utf-8'))['references']
keys=list(dict.fromkeys(re.findall(r'\[C:([^\]]+)\]',draft)))
number={k:i+1 for i,k in enumerate(keys)}
tables=json.loads((WORK/'table_data.json').read_text(encoding='utf-8'))
if 'tables' in tables: tables=tables['tables']
tables['algorithm']={'caption':'Thông số của thuật toán di truyền mở rộng','headers':['Thông số','Giá trị'],'rows':[['Quần thể','20 tensor RGB'],['Cá thể ưu tú','5'],['Lai ghép','Ngang'],['Xác suất đột biến','0,1'],['Nhiễu đột biến','Gaussian, σ = 0,2'],['Miền RGB','[0;1] sau khi chặn'],['Ảnh tối ưu','4'],['Ngân sách','400 / 1.000 / 2.500 lượt ảnh'],['Mẫu EOT mỗi ảnh','1 ở cấu hình cơ sở; 4 ở đối chứng phân bổ']],'note':'Miếng dán khóa trước đánh giá độc lập. Một đánh giá cá thể dùng bốn lượt ảnh với một mẫu EOT/ảnh, 16 lượt với bốn mẫu. Tập kiểm tra không chọn miếng dán.'}
for k,spec in tables.items():spec['caption']=re.sub(r'^Bảng \d+\.\s*','',spec['caption'])
tables['stream']['widths']=[.11,.16,.17,.11,.16,.14,.15]
tables['yolo_metrics']['widths']=[.18,.08,.148,.148,.148,.148,.148]
tables['yolo_metrics']['headers'][1]='Mốc'
tables['yolo_metrics']['note']='Mốc tính bằng phút. '+tables['yolo_metrics']['note']
tables['processing']['widths']=[.15,.22,.23,.23,.17]
tables['routes']['widths']=[.18,.26,.26,.30]
for row in tables['routes']['rows']:
    for i,value in enumerate(row):row[i]=str(value).replace('hardware/format/quantization','phần cứng, định dạng và lượng tử hóa')
doc=Document(source)
for child in list(doc._element.body):
    if child.tag!=qn('w:sectPr'): doc._element.body.remove(child)
for name in ['Normal','Title','Heading 1','Heading 2','Caption']:
    if name not in doc.styles:doc.styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH)
    style=doc.styles[name];style.font.name='Times New Roman';style.font.color.rgb=RGBColor(0,0,0)
    style._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Times New Roman')
    pf=style.paragraph_format;pf.space_after=Pt(6);pf.line_spacing=1.1
    if name=='Normal': style.font.size=Pt(13);pf.first_line_indent=Cm(.7);pf.widow_control=True
    elif name=='Title': style.font.size=Pt(15);style.font.bold=True;pf.first_line_indent=Cm(0);pf.space_after=Pt(10)
    elif name.startswith('Heading'): style.font.size=Pt(13);style.font.bold=True;pf.first_line_indent=Cm(0);pf.space_before=Pt(10);pf.space_after=Pt(6);pf.keep_with_next=True
    else: style.font.size=Pt(11);pf.first_line_indent=Cm(0)
    borders=style._element.find('.//'+qn('w:pBdr'))
    if borders is not None: borders.getparent().remove(borders)
doc.core_properties.title='Sponge Patch và kiểm chứng tính sẵn sàng của hệ thống phát hiện vật thể'
doc.core_properties.author='Phạm Tuấn Anh; Mai Quốc Bảo'
doc.core_properties.subject='Kiểm chứng Sponge Patch và thực nghiệm bổ sung lựa chọn detector'
doc.core_properties.comments='Viết lại từ bằng chứng đã lưu; nguồn tham khảo trong cửa sổ 13/10/2024–13/10/2026.'
table_count=0;figure_count=0

def cite(text):
    def sub(m):
        if m[1] not in number: raise ValueError('Unmapped reference '+m[1])
        return '['+str(number[m[1]])+']'
    return re.sub(r'\[C:([^\]]+)\]',sub,str(text))

def setrun(run,size=13,bold=False):
    run.font.name='Times New Roman';run.font.size=Pt(size);run.font.bold=bold;run.font.color.rgb=RGBColor(0,0,0)
    run._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Times New Roman')

def para(text,style=None):
    p=doc.add_paragraph(style=style);setrun(p.add_run(cite(text)),13)
    if style is None: p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    return p

def add_table(key):
    global table_count
    spec=tables[key];table_count+=1
    cap=para(f'Bảng {table_count}. '+spec['caption'],'Caption');cap.paragraph_format.keep_with_next=True;cap.alignment=WD_ALIGN_PARAGRAPH.LEFT
    for r in cap.runs:setrun(r,11,True)
    headers=spec['headers'];rows=spec['rows'];n=len(headers)
    t=doc.add_table(rows=1,cols=n);t.style='Table Grid';t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
    fractions=spec.get('widths') or ([.30]+[.70/(n-1)]*(n-1))
    if n==2:fractions=[.38,.62]
    for i,col in enumerate(t.columns):col.width=Cm(15.8*fractions[i])
    for i,text in enumerate(headers): t.rows[0].cells[i].text=cite(text)
    repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
    for row in rows:
        cells=t.add_row().cells
        if len(row)!=n:raise ValueError((key,row))
        for i,text in enumerate(row):cells[i].text=cite(text)
    props=t._tbl.tblPr
    borders=OxmlElement('w:tblBorders')
    for edge in ['top','left','bottom','right','insideH','insideV']:
        e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
    props.append(borders)
    for ridx,row in enumerate(t.rows):
        no_split=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(no_split)
        for i,cell in enumerate(row.cells):
            cell.width=Cm(15.8*fractions[i]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tcpr=cell._tc.get_or_add_tcPr();marg=OxmlElement('w:tcMar')
            for side,val in [('top','65'),('bottom','65'),('left','85'),('right','85')]:
                el=OxmlElement('w:'+side);el.set(qn('w:w'),val);el.set(qn('w:type'),'dxa');marg.append(el)
            tcpr.append(marg)
            if ridx==0:
                shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E9EEF3');tcpr.append(shade)
            for p in cell.paragraphs:
                pf=p.paragraph_format;pf.first_line_indent=Cm(0);pf.space_before=Pt(0);pf.space_after=Pt(0);pf.line_spacing=1.05;pf.keep_with_next=False
                p.alignment=WD_ALIGN_PARAGRAPH.LEFT if i==0 or key in ['routes','protocols','algorithm'] else WD_ALIGN_PARAGRAPH.CENTER
                for r in p.runs:setrun(r,10.5,ridx==0)
    note=para('Ghi chú: '+spec['note']);note.paragraph_format.first_line_indent=Cm(0);note.paragraph_format.space_before=Pt(4)
    for r in note.runs:setrun(r,10.5);r.italic=True

def add_figure(name,caption):
    global figure_count
    figure_count+=1
    path=ROOT/'paper_assets_20261013'/'RECOMMENDED'/name
    w,h=Image.open(path).size
    width=15.8
    if h/w*width>9.2:width=9.2*w/h
    p=doc.add_paragraph();p.paragraph_format.first_line_indent=Cm(0);p.paragraph_format.keep_with_next=True;p.paragraph_format.space_before=Pt(5);p.paragraph_format.space_after=Pt(3);p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path),width=Cm(width))
    cap=para(f'Hình {figure_count}. '+caption,'Caption');cap.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY;cap.paragraph_format.keep_with_next=False
    for r in cap.runs:setrun(r,11);r.italic=True

def equation(number,text):
    # Editable OMML rather than a bitmap equation.
    p=doc.add_paragraph();p.paragraph_format.first_line_indent=Cm(0);p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    math=OxmlElement('m:oMath');r=OxmlElement('m:r');rp=OxmlElement('w:rPr');fonts=OxmlElement('w:rFonts');fonts.set(qn('w:ascii'),'Cambria Math');fonts.set(qn('w:hAnsi'),'Cambria Math');rp.append(fonts);r.append(rp);txt=OxmlElement('m:t');txt.text=text;r.append(txt);math.append(r);p._p.append(math)
    setrun(p.add_run('   ('+number+')'),11)

def hyperlink(p,url):
    rel=p.part.relate_to(url,RT.HYPERLINK,is_external=True);h=OxmlElement('w:hyperlink');h.set(qn('r:id'),rel)
    r=OxmlElement('w:r');rp=OxmlElement('w:rPr');color=OxmlElement('w:color');color.set(qn('w:val'),'0563C1');rp.append(color);sz=OxmlElement('w:sz');sz.set(qn('w:val'),'22');rp.append(sz);r.append(rp);t=OxmlElement('w:t');t.text='Nguồn trực tuyến';r.append(t);h.append(r);p._p.append(h)

for block in re.split(r'\n\s*\n',draft.strip()):
    block=block.strip()
    if block.startswith('[[TABLE:'):add_table(block[8:-2]);continue
    if block.startswith('[[FIG:'):
        name,cap=block[6:-2].split('|',1);add_figure(name,cap);continue
    if block.startswith('[[EQ:'):
        number_eq,text=block[5:-2].split('|',1);equation(number_eq,text);continue
    if block=='[[REFERENCES]]':
        lookup={r['key']:r for r in refs}
        for k in keys:
            r=lookup[k];authors=', '.join(r['authors']);tail=r['venue']
            if r.get('pages'):tail+=', tr. '+r['pages']
            if 'preprint' in r['status']:tail+='; bản tiền công bố'
            if k=='ebt2026':tail='arXiv; tài liệu liên quan DSN 2026, loại ấn phẩm chưa xác minh; bản tiền công bố'
            end='' if r['title'].endswith(('?','!','.')) else '.'
            p=para(f"[{number[k]}] {authors}. {r['title']}{end} {tail}, {r['year']}. ")
            p.paragraph_format.first_line_indent=Cm(-.7);p.paragraph_format.left_indent=Cm(.7);p.paragraph_format.line_spacing=1.05
            for run in p.runs:setrun(run,11)
            hyperlink(p,r['url'])
        continue
    if block.startswith('# '):
        p=para(block[2:],'Title');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        for run in list(p.runs):run._element.getparent().remove(run._element)
        p.add_run('Sponge Patch và kiểm chứng tính sẵn sàng').add_break()
        p.add_run('của hệ thống phát hiện vật thể')
        for r in p.runs:setrun(r,15,True)
    elif block.startswith('### '):
        p=para(block[4:],'Heading 2')
        for r in p.runs:setrun(r,13,True)
    elif block.startswith('## '):
        p=para(block[3:],'Heading 1')
        for r in p.runs:setrun(r,13,True)
    else:
        p=para(block)
        if block.startswith(('Phạm Tuấn Anh','Trường Đại học','Email:','Giảng viên hướng dẫn:')):
            p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.first_line_indent=Cm(0);p.paragraph_format.space_after=Pt(3)
            for r in p.runs:setrun(r,11)
        if block.startswith('Từ khóa:'):
            for r in p.runs:r.italic=True
out=WORK/'candidate.docx';doc.save(out)
manifest={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'tables':table_count,'figures':figure_count,'references':len(keys),'reference_keys':keys,'equations':3,'preserved':'author identities, A4 page geometry, margins, footer page-number field, Times New Roman academic styling','rewrite_scope':'all body paragraphs, results discussion and recent-only bibliography'}
(WORK/'revision_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(manifest,ensure_ascii=False))
