from common import *
import json
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
em=pd.read_csv('../completeness/elicitation_mapping_manual.csv')
emu=em.drop_duplicates('k')
named=json.load(open('../completeness/named.json'))
ids=list(S.id)
order=['claude','chatgpt','deepseek','gemini']
Pm={ 'C':set(), 'P':set()}
M=np.zeros((4,len(ids)))
for r,m in enumerate(order):
    g=em[em.model==m]
    for _,x in g.iterrows():
        pass
    for j,i in enumerate(ids):
        c=((g.catalogue_id==i)&(g.map_class=='C')).any() or (i=='T2.07' and ((g.k.isin([12,90]))).any())
        p=((g.catalogue_id==i)&(g.map_class=='P')).any()
        M[r,j]=2 if c else (1 if p else 0)
fig=plt.figure(figsize=(7.16,2.75))
ax=fig.add_axes([0.105,0.255,0.775,0.40])
ax.imshow(M,cmap=ListedColormap(['#f4f4f1','#a9c3ea',BLUE]),aspect='auto',vmin=0,vmax=2,interpolation='nearest')
ax.set_yticks(range(4)); ax.set_yticklabels([NAMES[m] for m in order],fontsize=7)
ax.set_xticks(range(len(ids))); ax.set_xticklabels([i[1:] for i in ids],rotation=90,fontsize=5.4)
ax.set_xticks(np.arange(-.5,len(ids),1),minor=True); ax.set_yticks(np.arange(-.5,4,1),minor=True); ax.grid(which='minor',color='white',lw=0.8); ax.tick_params(which='both',length=0)
for s in ax.spines.values(): s.set_visible(False)
lay=S.id.str[1].astype(int).values
for k in range(1,len(ids)):
    if lay[k]!=lay[k-1]: ax.axvline(k-0.5,color=INK,lw=1.1)
cnt=(M>0).sum(0)
axt=fig.add_axes([0.105,0.675,0.775,0.20])
axt.bar(range(len(ids)),cnt,color='#9aa6b8',width=0.78,zorder=2)
axt.plot([j for j,c in enumerate(cnt) if c==0],[0.28]*int((cnt==0).sum()),'o',ms=4.2,mfc=ORANGE,mec='white',mew=0.5,zorder=3,clip_on=False)
axt.set_xlim(-0.5,len(ids)-0.5); axt.set_ylim(0,4.4); axt.set_yticks([0,2,4]); axt.set_xticks([]); axt.tick_params(labelsize=6.2)
axt.spines['bottom'].set_visible(False); axt.yaxis.grid(True,color=GRID,lw=0.4); axt.set_axisbelow(True); axt.set_ylabel('models\nnaming it',fontsize=6.4,labelpad=2)
for L_ in range(1,5):
    idx=np.where(lay==L_)[0]; fig.text(0.105+0.775*((idx[0]+idx[-1])/2+0.5)/len(ids),0.905,f'Layer L{L_}',ha='center',va='bottom',fontsize=7.4,color=INK)
# right: stacked bars of what each model listed
axr=fig.add_axes([0.915,0.255,0.075,0.40]); 
tab={m:emu[emu.model==m].map_class.value_counts() for m in order}
tot=[len(emu[emu.model==m]) for m in order]
axr.set_ylim(3.5,-0.5); axr.set_xlim(0,48)
for r,m in enumerate(order):
    c=tab[m].get('C',0); p=tab[m].get('P',0); n=tab[m].get('N',0)
    axr.barh(r,c,color=BLUE,height=0.62); axr.barh(r,p,left=c,color='#a9c3ea',height=0.62); axr.barh(r,n,left=c+p,color=ORANGE,height=0.62)
    axr.text(c+p+n+1,r,str(tot[r]),va='center',fontsize=6.5)
axr.axis('off'); fig.text(0.915,0.665,'threats listed',fontsize=6.4,ha='left',va='bottom')
h=[Patch(fc=BLUE,label='named, matches a catalogue threat'),Patch(fc='#a9c3ea',label='named, related (narrower or different)'),Patch(fc='#f4f4f1',ec=GRID,label='not named'),Patch(fc=ORANGE,label='listed threat with no catalogue counterpart (right)')]
from matplotlib.lines import Line2D
h.append(Line2D([],[],marker='o',color='none',mfc=ORANGE,mec='white',ms=5,label='catalogue threat named by no model (top)'))
fig.legend(handles=h,loc='lower left',bbox_to_anchor=(0.02,-0.01),ncol=3,frameon=False,fontsize=6.4,handlelength=1.2,handletextpad=0.4,columnspacing=1.5)
fig.savefig('out/Fig_panel_completeness.pdf'); fig.savefig('out/Fig_panel_completeness.png',dpi=170)
print((M>0).any(0).sum(),(M==2).any(0).sum(),cnt.tolist())
