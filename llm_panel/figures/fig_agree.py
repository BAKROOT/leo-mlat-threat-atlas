from common import *
from matplotlib.gridspec import GridSpec
rng=np.random.default_rng(7)
Lw=L.copy()
ORD_TIER=ag.ORD_TIER; ORD_EVID=ag.ORD_EVID
Lw['tier_c']=Lw.tier.map(ORD_TIER); Lw['evid_c']=Lw.evidence.map(ORD_EVID)
for c in ['layer','stride_primary','validity']: Lw[c+'_c']=Lw[c].astype('category').cat.codes
Lw['enab_c']=Lw.is_enabler.astype(int)
dims=[('Layer','layer_c','nominal'),('STRIDE-$\\tau$ category','stride_primary_c','nominal'),('Enabler flag','enab_c','nominal'),('Validity verdict','validity_c','nominal'),
 ('Tier (ordinal)','tier_c','ordinal'),('Evidence level (ordinal)','evid_c','ordinal'),
 ('Goal: displacement','goal_Displacement','nominal'),('Goal: denial','goal_Denial','nominal'),('Goal: deception','goal_Deception','nominal'),('Goal: disclosure','goal_Disclosure','nominal'),
 ('Damage D','D','interval'),('Reproducibility R','R','interval'),('Exploitability E','E','interval'),('Affected users A','A','interval'),
 ('Discoverability, strong pass','Di_strong','interval'),('Discoverability, weak pass','Di_weak','interval'),('Total score, strong pass','S_strong','interval'),('Total score, weak pass','S_weak','interval')]
groups=[('Classification',0,4),('Adversary and evidence',4,6),('Goals',6,10),('PA-DREAD scores',10,18)]
rows=[]
for lab,col,met in dims:
    P=Lw.pivot(index='id',columns='model',values=col)[MODELS]
    a=ag.alpha(P.values,met)
    bs=[]
    ids=np.arange(len(P))
    for b in range(1000):
        s=rng.choice(ids,len(ids)); bs.append(ag.alpha(P.values[s],met))
    bs=np.array(bs,float); lo,hi=np.nanpercentile(bs,[2.5,97.5])
    # Kendall W (complete cases) for score dimensions only
    w=np.nan
    if met=='interval':
        Pc=P.dropna()
        w=ag.kendall_w(Pc.values)
        w=w[0] if isinstance(w,(tuple,list)) else w
    rows.append((lab,a,lo,hi,w,met))
D=pd.DataFrame(rows,columns=['dim','alpha','lo','hi','W','metric']); D.to_csv('out/fig2_alpha_bootstrap.csv',index=False); print(D.round(3).to_string())
