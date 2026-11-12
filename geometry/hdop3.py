import numpy as np, itertools, json
from hdop2 import *
rng=np.random.default_rng(1)
cfgs={'A 10x20, 0deg':(10,20,1,0.0),'B 10x20, 5deg':(10,20,1,5.0),'C 20x10, 0deg':(20,10,1,0.0),'D 8x25, 0deg':(8,25,1,0.0),'E 10x20, 10deg':(10,20,1,10.0)}
res={}
for name,(P,S,F,m) in cfgs.items():
    rows=geom(P,S,F,m)
    nv=np.array([len(r[1]) for r in rows]); lat=np.abs(np.array([r[0] for r in rows]))
    H=np.full(len(rows),np.nan); Gm=np.full(len(rows),np.nan)
    for i,(l,E,N) in enumerate(rows):
        if len(E)>=3:
            try: H[i],Gm[i]=hd(E,N)
            except Exception: pass
    valid=~np.isnan(H)
    d={'valid':valid.mean(),'mean_nvis':nv.mean(),'hdop_med':np.nanmedian(H),'hdop_p99':np.nanpercentile(H,99),
       'f_hdop_gt':np.mean(H[valid]>11.7),'f_g_gt':np.mean(Gm[valid]>11.7)}
    for lo,hi,lab in ((0,30,'<30'),(30,60,'30-60'),(60,90,'>60')):
        b=valid&(lat>=lo)&(lat<hi) if hi<90 else valid&(lat>=lo)
        d['lat'+lab]=(float(b.sum()),float(np.mean(H[b]>11.7)) if b.any() else None,float(np.nanmedian(H[b])) if b.any() else None, float(np.mean(nv[(lat>=lo)&(lat<hi)] if hi<90 else nv[lat>=lo])))
    res[name]=d
    print(name,{k:(np.round(v,3) if not isinstance(v,tuple) else tuple(np.round(v,3))) for k,v in d.items()})
# adversarial dropping for config A
P,S,F,m=cfgs['A 10x20, 0deg']; rows=geom(P,S,F,m)
idx=rng.choice(len(rows),1500,replace=False)
out={}
for mm in (3,4,5,6,8):
    hit=0;tot=0
    for i in idx:
        l,E,N=rows[i]; n=len(E)
        if n<mm: continue
        tot+=1
        combos=list(itertools.combinations(range(n),mm))
        if len(combos)>3000: combos=[combos[j] for j in rng.choice(len(combos),3000,replace=False)]
        mx=0
        for cmb in combos:
            h,g=hd(E[list(cmb)],N[list(cmb)])
            if h>mx: mx=h
            if mx>11.7: break
        hit+= mx>11.7
    out[mm]=(tot,hit/tot if tot else None)
    print('keep m=',mm,'samples',tot,'frac where some m-subset has HDOP>11.7',out[mm][1])
json.dump({'cfg':{k:{kk:(list(vv) if isinstance(vv,tuple) else vv) for kk,vv in d.items()} for k,d in res.items()},'drop':out},open('hdop_results.json','w'),default=float)
