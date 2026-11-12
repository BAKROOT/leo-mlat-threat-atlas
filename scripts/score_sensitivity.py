"""One-point sensitivity of the PA-DREAD totals and bands (each dimension perturbed by +/-1, random direction, 3000 replications, seed 7).
Usage: python scripts/score_sensitivity.py [catalogue.xlsx]   -> sens_results.json"""
import openpyxl, numpy as np, json, sys
from scipy.stats import spearmanr
wb=openpyxl.load_workbook(sys.argv[1] if len(sys.argv)>1 else 'data/catalogue/LEO_MLAT_Threat_Catalogue.xlsx',data_only=True)
ws=wb['Catalogue']; rows=list(ws.iter_rows(min_row=4,values_only=True)); hdr=rows[0]
ix={h:i for i,h in enumerate(hdr) if h}
need=['ID','D','R','E','A','Di strong','Di weak','S strong','S weak','Band strong','Band weak','Role']
print({k:ix.get(k) for k in need})
data=[r for r in rows[1:] if r[0] and str(r[0]).startswith('T')]
print(len(data))
ids=[r[ix['ID']] for r in data]
def num(x):
    try: return float(x)
    except: return np.nan
cat={k:np.array([num(r[ix[k]]) for r in data]) for k in ['D','R','E','A','Di strong','Di weak','S strong','S weak']}
role=[r[ix['Role']] for r in data]
sc=~np.isnan(cat['S strong'])
print('scored',sc.sum(),'enablers',[i for i,r in zip(ids,role) if r!='Leaf'][:10])
def band(s): return np.where(s>=20,3,np.where(s>=15,2,np.where(s>=10,1,0)))
dims=['D','R','E','A']
def total(c,di): return c['D']+c['R']+c['E']+c['A']+c[di]
# check recompute equals S strong
t=total(cat,'Di strong'); print('recompute ok',np.nanmax(np.abs(t-cat['S strong'])))
# sensitivity: each dimension moved by +/-1 with prob 0.5 (direction random), clipped 1..5
rng=np.random.default_rng(7)
def sens(di,nrep=3000,p=0.5):
    base=total(cat,di)[sc]; top=set(np.argsort(-base,kind='stable')[:10]); rs=[];ov=[];bc=[];
    for _ in range(nrep):
        s=np.zeros(sc.sum())
        for k in ['D','R','E','A',di]:
            v=cat[k][sc].copy(); m=rng.random(len(v))<p; d=rng.choice([-1,1],len(v)); v=np.clip(v+np.where(m,d,0),1,5); s+=v
        rs.append(spearmanr(base,s)[0]); ov.append(len(top&set(np.argsort(-s,kind='stable')[:10]))/10); bc.append((band(s)!=band(base)).mean())
    return dict(rho_mean=float(np.mean(rs)),rho_p5=float(np.percentile(rs,5)),top10=float(np.mean(ov)),band_change=float(np.mean(bc)))
S1=sens('Di strong'); S2=sens('Di weak'); print('sens strong',S1); print('sens weak',S2)
# panel median rescoring
wb2=openpyxl.load_workbook('/mnt/user-data/outputs/Panel_Review_4models.xlsx',data_only=True)
L=list(wb2['Long'].iter_rows(values_only=True)); lh=L[0]; li={h:i for i,h in enumerate(lh)}
from collections import defaultdict
pm=defaultdict(lambda: defaultdict(list))
for r in L[1:]:
    if not r[0]: continue
    for k,col in [('D','D'),('R','R'),('E','E'),('A','A'),('Di strong','Di_strong'),('Di weak','Di_weak')]:
        v=num(r[li[col]]); 
        if not np.isnan(v): pm[r[li['id']]][k].append(v)
pan={k:np.array([np.median(pm[i][k]) if pm[i][k] else np.nan for i in ids]) for k in cat if k in ['D','R','E','A','Di strong','Di weak']}
def rnd(x): return np.floor(x+0.5)
res={}
for di,sname in (('Di strong','strong'),('Di weak','weak')):
    cs={k:cat[k] for k in cat}; ps={k:rnd(pan[k]) for k in pan}
    base=total(cs,di); alt=np.where(np.isnan(base),np.nan,ps['D']+ps['R']+ps['E']+ps['A']+ps[di])
    m=sc&~np.isnan(alt)
    rho=spearmanr(base[m],alt[m])[0]
    top=set(np.argsort(-np.nan_to_num(base,nan=-1))[:10]); top2=set(np.argsort(-np.nan_to_num(alt,nan=-1))[:10])
    res[sname]=dict(n=int(m.sum()),rho=float(rho),band_change=float((band(base[m])!=band(alt[m])).mean()),top10=len(top&top2)/10,mean_cat=float(np.nanmean(base[m])),mean_pan=float(np.nanmean(alt[m])))
print('panel-median rescoring',res)
for k in ['T1.11','T2.06','T2.04','T2.07','T3.06','T4.12','T2.02','T2.09','T3.07','T3.08']:
    i=ids.index(k); print(k,'cat',[cat[x][i] for x in ['D','R','E','A','Di strong','Di weak']],'S',cat['S strong'][i],cat['S weak'][i],'| panel med',[pan[x][i] for x in ['D','R','E','A','Di strong','Di weak']])
json.dump(dict(sens_strong=S1,sens_weak=S2,resc=res),open('sens_results.json','w'))
