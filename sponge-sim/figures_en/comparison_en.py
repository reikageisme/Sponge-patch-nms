# English re-render of COMPARISON figures (fig14, fig12). Số từ paper_assets_20261013/COMPARISON/*.json
# Chỉ dịch nhãn; KHÔNG đổi số; thanh sai số = SD trong file nguồn.
import json
from pathlib import Path
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, numpy as np
REPO=Path(__file__).resolve().parents[2]
SRC=REPO/'archive/paper_assets_20261013/COMPARISON'
OUT=REPO/'sponge-sim/figures_en/out'; OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
C=['#1f77b4','#ff7f0e','#2ca02c','#9467bd','#7f7f7f']; GRAY='#666666'

def vlabels(ax,xs,vals,fmt):
    for x,v in zip(xs,vals):
        ax.annotate(fmt(v),(x,v),textcoords='offset points',xytext=(0,4),ha='center',fontweight='bold',fontsize=10)

def panel_header(fig,ax,title,infos,y_title,dy=0.026):
    x0=ax.get_position().x0
    fig.text(x0,y_title,title,fontweight='bold',fontsize=12,va='top')
    for i,t in enumerate(infos):
        fig.text(x0,y_title-0.030-dy*i,t,fontsize=8.5,color=GRAY,va='top')

def panel_note(fig,ax,lines,y0,dy=0.025):
    x0=ax.get_position().x0
    for i,t in enumerate(lines):
        fig.text(x0,y0-dy*i,t,fontsize=8.5,color='#333333',va='top')

def barx(ax,i,n):
    p=ax.get_position(); return p.x0+((i+0.5)/n)*p.width

# ================= FIG 14 =================
f=json.load(open(SRC/'foundation_sources.json'))
fig,axes=plt.subplots(1,3,figsize=(15,6.6),gridspec_kw={'width_ratios':[4,5,2.4]})
fig.subplots_adjust(top=0.62,bottom=0.30,wspace=0.32,left=0.055,right=0.985)
fig.text(0.5,0.965,'MEASUREMENTS FROM FOUNDATION WORKS AND SPONGE PATCH',ha='center',fontweight='bold',fontsize=15,va='top')
fig.text(0.5,0.915,'Three separate protocols and units · no cross-panel ranking',ha='center',fontsize=10.5,color=GRAY,va='top')
# A
ax=axes[0]; vals=[r[1] for r in f['underload']['rows']]; xs=np.arange(len(vals))
ax.bar(xs,vals,color=C[:len(vals)],alpha=.9); vlabels(ax,xs,vals,lambda v:f'{v:.1f}')
ax.set_xticks(xs,['Standard\nclean','Standard\nOverload','Underload\nclean','Underload\nOverload'],fontsize=9)
ax.set_ylim(0,66); ax.grid(axis='y',alpha=.2); ax.set_axisbelow(True)
# B
ax=axes[1]; vals=[r[1] for r in f['evade']['rows']]; xs=np.arange(len(vals))
ax.bar(xs,vals,color=C[:len(vals)],alpha=.9); vlabels(ax,xs,vals,lambda v:f'{v:.0f}')
ax.set_xticks(xs,['Clean','Dae.','Over.','Phan.','Beyond'],fontsize=9)
ax.set_ylim(0,330); ax.grid(axis='y',alpha=.2); ax.set_axisbelow(True)
# C
ax=axes[2]; vals=[r[1] for r in f['local']['rows']]; xs=np.arange(len(vals))
sd=float(f['local']['note'].split('SD')[1].split('pp')[0].strip())
ax.bar(xs,vals,color=[C[0],C[1]],alpha=.9); ax.errorbar(xs,vals,yerr=[0,sd],fmt='none',ecolor='#333',capsize=4)
vlabels(ax,xs,vals,lambda v:f'{v:.2f}')
ax.set_xticks(xs,['Clean','SG-GA\n2,500 queries'],fontsize=9)
ax.set_ylim(0,42); ax.grid(axis='y',alpha=.2); ax.set_axisbelow(True)
fig.canvas.draw()
panel_header(fig,axes[0],'A  Underload 2025',['YOLOv8s · COCO','mAP50 (%) · Table 1'],0.885)
panel_header(fig,axes[1],'B  EVADE 2025',['YOLOv8n · COCO val2017','Boxes AFTER NMS · Table 3'],0.885)
panel_header(fig,axes[2],'C  This work',['YOLOv8n · 128 images · patch 4%','AP50:95 (%) · 10 seeds'],0.885)
panel_note(fig,axes[0],['Underload: adversarially trained','model. Not ordinary fine-tuning.'],0.22)
panel_note(fig,axes[1],['Dae./Over./Phan./Beyond: 4 attacks.','Box count, not NMS time.'],0.22)
panel_note(fig,axes[2],['Patch only, no model update.','Patch error bar: SD across seeds.'],0.22)
fig.text(0.5,0.075,'AP50 vs AP50:95 · different image sets, access and intervention.  '
         'Sources and traceable scalars: foundation_sources.json · no cross-panel differencing.',
         ha='center',fontsize=9,color='#333333',va='top')
fig.savefig(OUT/'so_sanh_bai_nen_va_sponge.png',dpi=200,bbox_inches='tight'); plt.close(fig)
print('fig14 ok, sd_C=',sd)

# ================= FIG 12 =================
c=json.load(open(SRC/'comparison_sources.json'))
pub=c['published_rows']; loc=c['local_rows']; models=[r['model'] for r in pub]; xs=np.arange(len(models))
fig,axes=plt.subplots(1,2,figsize=(14,6.8))
fig.subplots_adjust(top=0.60,bottom=0.34,wspace=0.20,left=0.07,right=0.975)
fig.text(0.5,0.965,'PUBLISHED FIGURES VS OUR MEASUREMENTS',ha='center',fontweight='bold',fontsize=15,va='top')
fig.text(0.5,0.915,'Two separate protocols — compare models only within each panel',ha='center',fontsize=10.5,color=GRAY,va='top')
# A
ax=axes[0]; vals=[r['ap50_95_pct'] for r in pub]
ax.bar(xs,vals,color=C[:4],alpha=.9); vlabels(ax,xs,vals,lambda v:f'{v:.1f}')
ax.set_xticks(xs,models,fontsize=9.5); ax.set_ylim(0,55); ax.grid(axis='y',alpha=.2); ax.set_axisbelow(True); ax.set_ylabel('AP50:95 (%)')
# B
ax=axes[1]; vals=[r['map_mean'] for r in loc]; sd=[r['map_sd'] for r in loc]
ax.bar(xs,vals,color=C[:4],alpha=.9); ax.errorbar(xs,vals,yerr=sd,fmt='none',ecolor='#333',capsize=4); vlabels(ax,xs,vals,lambda v:f'{v:.2f}')
ax.set_xticks(xs,models,fontsize=9.5); ax.set_ylim(0,55); ax.grid(axis='y',alpha=.2); ax.set_axisbelow(True); ax.set_ylabel('AP50:95 (%)')
fig.canvas.draw()
panel_header(fig,axes[0],'A  Published YOLOv13 (2025)',['COCO val2017 · 80 classes · 640 px','Tesla T4 · TensorRT FP16','AP50:95 published in Table I'],0.885)
panel_header(fig,axes[1],'B  Our experiments',['COCO + AdvT-shirt · 1 person class · 416 px','RTX 5060 · PyTorch FP32 · batch 1','Test mAP50:95 at validation-selected checkpoint'],0.885)
# latency rows + notes
for ax,rows,lab,noteline in [(axes[0],pub,'Published inference latency (ms)','No SD in the published table.'),
                              (axes[1],loc,'Mean pipeline latency (ms)','mAP error bar: SD across 5 seeds; checkpoints 120/120/5/10 min.')]:
    x0=ax.get_position().x0
    fig.text(x0,0.255,lab,fontsize=9,color='#333333',fontweight='bold',va='top')
    for i,r in enumerate(rows):
        fig.text(barx(ax,i,4),0.215,f"{r['latency_ms']:.2f}",ha='center',fontsize=9.5,fontweight='bold',va='top')
    fig.text(x0,0.165,noteline,fontsize=8.5,color='#333333',va='top')
fig.text(0.5,0.085,'Different dataset, class count, pretrained, input, hardware, backend and precision. '
         'Do not difference the two panels to claim superiority.',ha='center',fontsize=9,color='#333333',va='top')
fig.text(0.5,0.055,'Source A: Lei et al., arXiv 2506.17733v2, Table I. Source B: 20 records and latency_records.json.',
         ha='center',fontsize=8.5,color=GRAY,va='top')
fig.savefig(OUT/'so_sanh_cong_bo_va_thuc_nghiem.png',dpi=200,bbox_inches='tight'); plt.close(fig)
print('fig12 ok')
