import numpy as np, itertools, sys
from hdop import *
def geom(P,S,F,mask,nlon=8,ntime=90,lats=np.arange(-85,86,10),alt=10.0):
    c=constellation(P,S,F); ts=np.linspace(0,T,ntime,endpoint=False)
    rows=[]
    for lat in lats:
        for t in ts:
            sp=sat_pos(c,t)
            for k in range(nlon):
                lon=2*np.pi*(k+0.5)/nlon; la=np.radians(lat)
                r=(Re+alt)*np.array([np.cos(la)*np.cos(lon),np.cos(la)*np.sin(lon),np.sin(la)])
                up=r/np.linalg.norm(r); east=np.array([-np.sin(lon),np.cos(lon),0.0]); north=np.cross(up,east)
                d=sp-r; rng=np.linalg.norm(d,axis=1); los=d/rng[:,None]
                el=np.degrees(np.arcsin(los@up)); vis=el>=mask
                L=los[vis]
                rows.append((lat,L@east,L@north))
    return rows
def hd(E,N):
    G=np.column_stack([-E,-N,np.ones(len(E))]); K=np.linalg.pinv(G); Kh=K[:2]
    return np.sqrt((Kh**2).sum()), np.sqrt((Kh**2).sum(0)).max()
def stats(P,S,F,mask):
    rows=geom(P,S,F,mask)
    nv=np.array([len(r[1]) for r in rows]); lat=np.array([r[0] for r in rows])
    full=[];gfull=[]
    for l,E,N in rows:
        if len(E)>=3: h,g=hd(E,N); full.append(h); gfull.append(g)
        else: full.append(np.nan); gfull.append(np.nan)
    full=np.array(full); gfull=np.array(gfull)
    out={'cfg':(P,S,F,mask),'n':len(rows),'mean_nvis':nv.mean(),'min_nvis':nv.min(),'frac_lt3':(nv<3).mean(),'frac_lt4':(nv<4).mean(),
         'hdop_med':np.nanmedian(full),'hdop_p99':np.nanpercentile(full,99),'hdop_max':np.nanmax(full),'gmax_p99':np.nanpercentile(gfull,99),
         'frac_hdop>11.7':np.nanmean(full>11.7)}
    return out,rows
if __name__=='__main__':
    P,S,F,mask=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),float(sys.argv[4])
    o,rows=stats(P,S,F,mask)
    print({k:(round(v,3) if isinstance(v,float) else v) for k,v in o.items()})
