from common import *
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
rows=[('Layer','layer'),('STRIDE-$\\tau$ category','stride_primary'),('Goals','goals'),('Tier','tier'),('Evidence level','evidence'),('Enabler flag','is_enabler'),('Validity','validity'),
 ('Damage D','D'),('Reproducibility R','R'),('Exploitability E','E'),('Affected users A','A'),('Discoverability, strong','Di_strong'),('Discoverability, weak','Di_weak')]
code={'agree':0,'panel_vs_catalogue':1,'split':2}
M=np.array([[code.get(S.loc[j,'tag_'+f],3) for j in range(len(S))] for _,f in rows])
cols=['#e6ebf3',ORANGE,VIOLET,'#ffffff']
fig=plt.figure(figsize=(7.16,3.15))
ax=fig.add_axes([0.165,0.155,0.775,0.60])
ax.imshow(M,cmap=ListedColormap(cols),aspect='auto',vmin=0,vmax=3,interpolation='nearest')
ax.set_xticks(range(len(S))); ax.set_xticklabels([i.replace('T','') for i in S.id],rotation=90,fontsize=5.4)
ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows],fontsize=6.8)
ax.set_xticks(np.arange(-.5,len(S),1),minor=True); ax.set_yticks(np.arange(-.5,len(rows),1),minor=True)
ax.grid(which='minor',color='white',lw=0.8); ax.tick_params(which='both',length=0)
for s in ax.spines.values(): s.set_visible(False)
# layer separators
lay=S.id.str[1].astype(int).values
for k in range(1,len(S)):
    if lay[k]!=lay[k-1]: ax.axvline(k-0.5,color=INK,lw=1.1)
for L_ in range(1,5):
    idx=np.where(lay==L_)[0]; fig.text(0.165+0.775*((idx[0]+idx[-1])/2+0.5)/len(S),0.935,f'Layer L{L_}',ha='center',va='bottom',fontsize=7.4,color=INK)
# top bars: number of fields not 'agree'
nd=((M==1)|(M==2)).sum(0)
axt=fig.add_axes([0.165,0.775,0.775,0.14]); axt.bar(range(len(S)),nd,color=[('#9aa6b8') if v<4 else ORANGE for v in nd],width=0.78,zorder=2); axt.set_xlim(-0.5,len(S)-0.5)
axt.set_yticks([0,5,10]); axt.set_ylabel('fields\nflagged',fontsize=6.4,labelpad=2); axt.set_xticks([]); axt.tick_params(labelsize=6.2)
axt.spines['bottom'].set_visible(False); axt.yaxis.grid(True,color=GRID,lw=0.4); axt.set_axisbelow(True)
# right counts
axr=fig.add_axes([0.945,0.155,0.045,0.60]); 
cnt=np.array([[ (M[i]==k).sum() for k in range(4)] for i in range(len(rows))])
axr.set_ylim(len(rows)-0.5,-0.5); axr.set_xlim(0,55); axr.axis('off')
for i in range(len(rows)):
    axr.text(0,i,f'{cnt[i,1]}',color=ORANGE,fontsize=6.6,va='center',ha='left',fontweight='bold'); axr.text(26,i,f'{cnt[i,2]}',color=VIOLET,fontsize=6.6,va='center',ha='left',fontweight='bold')
fig.text(0.944,0.762,'$\\neq$cat.',fontsize=6,color=ORANGE,ha='left',va='bottom'); fig.text(0.9785,0.762,'split',fontsize=6,color=VIOLET,ha='left',va='bottom')
h=[Patch(fc=cols[0],label='models and catalogue agree'),Patch(fc=cols[1],label='models agree, catalogue differs'),Patch(fc=cols[2],label='models split')]
h.append(Patch(fc='white',ec=GRID,label='not scored (enabler)'))
fig.legend(handles=h,loc='lower left',bbox_to_anchor=(0.165,-0.005),ncol=4,frameon=False,fontsize=6.6,handlelength=1.2,handletextpad=0.4,columnspacing=1.2)
fig.savefig('out/Fig_panel_disagreement.pdf'); fig.savefig('out/Fig_panel_disagreement.png',dpi=170)
print(cnt.tolist())
