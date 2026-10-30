from common import *
import json
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
D=pd.read_csv('out/fig2_alpha_bootstrap.csv')
MV=pd.read_csv(R+'model_vs_catalogue.csv').set_index('model')
# retest
def load(p): return {r['id']:r for r in json.load(open(p))['ratings']}
a=load('../responses/chatgpt__B3__run1.json'); b=load('../retest/responses/chatgpt__B3__run2.json')
pts=[]
for i in a:
    for k in ['D','R','E','A','Di_strong','Di_weak']:
        if a[i][k] is not None and b[i][k] is not None: pts.append((a[i][k],b[i][k]))
pts=np.array(pts); exact=(pts[:,0]==pts[:,1]).mean(); w1=(abs(pts[:,0]-pts[:,1])<=1).mean(); print('retest pooled n',len(pts),exact,w1)
fig=plt.figure(figsize=(7.16,4.9))
# (a)
axa=fig.add_axes([0.205,0.145,0.355,0.775])
n=len(D); ypos=[]; y=0; gaps={4:0.6,6:0.6,10:0.6}
for i in range(n):
    if i in gaps: y+=gaps[i]
    ypos.append(y); y+=1
ypos=np.array(ypos)
def col(v): return BLUE if v>=0.8 else ('#7a96c9' if v>=0.667 else ORANGE)
for i,r in D.iterrows():
    c=col(r.alpha)
    axa.plot([max(r.lo,-0.05),r.hi],[ypos[i]]*2,color=c,lw=1.3,solid_capstyle='round',zorder=2)
    axa.plot(r.alpha,ypos[i],'o',ms=4.6,mfc=c,mec='white',mew=0.6,zorder=3)
    if not np.isnan(r.W): axa.plot(r.W,ypos[i],'D',ms=3.6,mfc='white',mec=INK,mew=0.7,zorder=4)
    axa.text(1.035,ypos[i],f'{r.alpha:.2f}',va='center',ha='left',fontsize=6.8,color=INK)
axa.set_ylim(ypos[-1]+0.8,-1.0); axa.set_xlim(-0.05,1.13); axa.spines['bottom'].set_bounds(-0.05,1.0)
axa.set_yticks(ypos); axa.set_yticklabels(D.dim,fontsize=7)
for x,l in [(0.667,'0.667'),(0.8,'0.800')]:
    axa.axvline(x,color=MUTE,lw=0.6,ls=(0,(3,2)),zorder=1)
axa.set_xticks([0,0.2,0.4,0.6,0.8,1.0]); axa.set_xlabel("Krippendorff's $\\alpha$ (4 models, 55 threats), 95% bootstrap interval")
axa.xaxis.grid(True,color=GRID,lw=0.4); axa.set_axisbelow(True)
axa.text(0.733,-1.3,'tentative',ha='center',va='bottom',fontsize=6.3,color=MUTE); axa.text(0.9,-1.3,'reliable',ha='center',va='bottom',fontsize=6.3,color=MUTE); axa.text(0.33,-1.3,'not reliable',ha='center',va='bottom',fontsize=6.3,color=MUTE)
for lab,s,e in [('Classification',0,4),('Adversary, evidence',4,6),('Goals',6,10),('PA-DREAD scores',10,18)]:
    pass
h=[Line2D([],[],marker='o',color='none',mfc=BLUE,mec='white',ms=5,label='$\\alpha\\geq0.80$'),Line2D([],[],marker='o',color='none',mfc='#7a96c9',mec='white',ms=5,label='0.667 to 0.80'),Line2D([],[],marker='o',color='none',mfc=ORANGE,mec='white',ms=5,label='$<0.667$'),Line2D([],[],marker='D',color='none',mfc='white',mec=INK,ms=3.8,label="Kendall's $W$")]
axa.legend(handles=h,loc='lower left',bbox_to_anchor=(-0.12,-0.165),ncol=4,frameon=False,handletextpad=0.2,columnspacing=0.9,fontsize=6.6)
fig.text(0.012,0.965,'(a) Agreement among the four models',fontsize=8,va='center')
# (b) heat table
axb=fig.add_axes([0.745,0.565,0.245,0.345])
rowsb=[('Layer','layer exact match','p'),('STRIDE-$\\tau$ primary','stride_primary exact match','p'),('Tier','tier exact match','p'),('Evidence level','evidence exact match','p'),('Enabler flag','is_enabler exact match','p'),
 ('D within $\\pm1$','D within +-1','p'),('R within $\\pm1$','R within +-1','p'),('E within $\\pm1$','E within +-1','p'),('A within $\\pm1$','A within +-1','p'),('Di strong $\\pm1$','Di_strong within +-1','p'),('Di weak $\\pm1$','Di_weak within +-1','p'),
 ('Band (strong) exact','band_strong exact match','p'),('Spearman $\\rho$, total','S_strong Spearman vs catalogue','r')]
M=np.array([[MV.loc[m,c] for m in MODELS] for _,c,_ in rowsb],float)
from matplotlib.colors import LinearSegmentedColormap
cm=LinearSegmentedColormap.from_list('b',['#f3f6fb','#2a78d6'])
axb.imshow(M,cmap=cm,vmin=0.4,vmax=1.0,aspect='auto')
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        v=M[i,j]; t=f'{v:.2f}' if rowsb[i][2]=='r' else f'{round(v*100):d}'
        axb.text(j,i,t,ha='center',va='center',fontsize=6.8,color='white' if v>0.82 else INK)
axb.set_xticks(range(4)); axb.set_xticklabels([NAMES[m] for m in MODELS],fontsize=6.8); axb.xaxis.tick_top()
axb.set_yticks(range(len(rowsb))); axb.set_yticklabels([r[0] for r in rowsb],fontsize=6.8)
for s in axb.spines.values(): s.set_visible(False)
axb.tick_params(length=0)
for y in [4.5,10.5]: axb.axhline(y,color='white',lw=2)
fig.text(0.60,0.965,'(b) Each model against the catalogue (% of 55 threats)',fontsize=8,va='center')
# (c) retest
axc=fig.add_axes([0.745,0.14,0.245,0.36])
jit=np.random.default_rng(3).uniform(-0.13,0.13,size=pts.shape)
axc.plot([0.5,5.5],[0.5,5.5],color=MUTE,lw=0.6,ls=(0,(3,2)),zorder=1)
axc.scatter(pts[:,0]+jit[:,0],pts[:,1]+jit[:,1],s=9,c=BLUE,alpha=0.55,edgecolors='none',zorder=2)
axc.set_xlim(0.5,5.5); axc.set_ylim(0.5,5.5); axc.set_aspect('equal'); axc.set_xticks(range(1,6)); axc.set_yticks(range(1,6))
axc.set_xlabel('ChatGPT, run 1'); axc.set_ylabel('run 2')
axc.text(5.4,0.62,f'{len(pts)} scores, 12 threats\nidentical {exact*100:.0f}%, within $\\pm1$ {w1*100:.0f}%',va='bottom',ha='right',fontsize=6.5,color=INK)
fig.text(0.60,0.53,'(c) Test-retest: ChatGPT, Layer 3, same prompt',fontsize=8,va='center')
fig.savefig('out/Fig_panel_agreement.pdf'); fig.savefig('out/Fig_panel_agreement.png',dpi=170)
