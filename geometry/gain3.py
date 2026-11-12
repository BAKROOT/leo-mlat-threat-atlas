"""C channel: effect of relaxing the integrity threshold (T scaled by k) on the share of samples with an open stealth window."""
import numpy as np, json
from scipy.stats import chi2
from hdop2 import geom
from gain import analyse, EREQ
out={}
for name,(P,S,F,m) in {'A 10x20, 0deg':(10,20,1,0.0),'B 10x20, 5deg':(10,20,1,5.0),'D 8x25, 0deg':(8,25,1,0.0)}.items():
    rows=[r for r in geom(P,S,F,m) if len(r[1])>=3]
    recs=[(len(r[1]),)+analyse(r[1],r[2]) for r in rows]
    d={}
    for sig in (10.0,30.0,100.0):
        for k in (1.0,2.0,4.0):
            c=0
            for n,g,hii in recs:
                sq=np.sqrt(np.clip(1-hii,1e-12,1)); T=k*sig*np.sqrt(chi2.ppf(1-1e-3,n-3)) if n>3 else np.inf
                if np.any(EREQ/np.maximum(g,1e-9)<T/sq): c+=1
            d[f'sig{int(sig)}_k{int(k)}']=c/len(recs)
    out[name]=d; print(name,{k:round(v,3) for k,v in d.items()})
json.dump(out,open('gain3_results.json','w'),indent=1)
