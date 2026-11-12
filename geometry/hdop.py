import numpy as np, json, sys
Re=6371.0; h_sat=500.0; a=Re+h_sat; inc=np.radians(86.0); mu=398600.4418
T=2*np.pi*np.sqrt(a**3/mu); n=2*np.pi/T
def constellation(P,S,F):
    out=[]
    for p in range(P):
        raan=np.pi*p/P            # Walker-Star: planes spread over 180 deg
        for s in range(S):
            m0=2*np.pi*s/S+2*np.pi*F*p/(P*S)
            out.append((raan,m0))
    return np.array(out)
def sat_pos(c,t):
    raan=c[:,0]; u=c[:,1]+n*t
    x=a*np.cos(u); y=a*np.sin(u)*np.cos(inc); z=a*np.sin(u)*np.sin(inc)
    # rotate by raan about z
    X=x*np.cos(raan)-y*np.sin(raan); Y=x*np.sin(raan)+y*np.cos(raan)
    return np.stack([X,Y,z],1)
def run(P=10,S=20,F=1,mask_deg=0.0,alt=10.0,nlon=12,ntime=60,lats=np.arange(-85,86,5),seed=0):
    c=constellation(P,S,F); res=[]
    ts=np.linspace(0,T,ntime,endpoint=False)
    for lat in lats:
        hd=[];gm=[];nv=[]
        for t in ts:
            sp=sat_pos(c,t)
            for k in range(nlon):
                lon=2*np.pi*(k+0.5)/nlon
                la=np.radians(lat)
                r=(Re+alt)*np.array([np.cos(la)*np.cos(lon),np.cos(la)*np.sin(lon),np.sin(la)])
                up=r/np.linalg.norm(r); east=np.array([-np.sin(lon),np.cos(lon),0.0]); north=np.cross(up,east)
                d=sp-r; rng=np.linalg.norm(d,axis=1); los=d/rng[:,None]
                el=np.degrees(np.arcsin(los@up))
                vis=el>=mask_deg
                nvis=vis.sum(); nv.append(nvis)
                if nvis<3: hd.append(np.nan); gm.append(np.nan); continue
                L=los[vis]
                G=np.column_stack([-(L@east),-(L@north),np.ones(nvis)])   # unknowns: e,n, emission-time term
                try:
                    K=np.linalg.pinv(G)   # (GtG)^-1 Gt
                except: hd.append(np.nan); gm.append(np.nan); continue
                Kh=K[:2,:]
                hdop=np.sqrt((Kh**2).sum()); g=np.sqrt((Kh**2).sum(0))
                hd.append(hdop); gm.append(g.max())
        res.append((lat,np.array(hd),np.array(gm),np.array(nv)))
    return res
if __name__=='__main__':
    P,S,F,mask=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),float(sys.argv[4])
    res=run(P,S,F,mask)
    allh=np.concatenate([r[1] for r in res]); allg=np.concatenate([r[2] for r in res]); alln=np.concatenate([r[3] for r in res])
    ok=~np.isnan(allh)
    print('cfg',P,S,F,mask,'samples',len(allh),'valid(>=3 vis)',ok.mean().round(4),'mean nvis',alln.mean().round(2))
    for q in (50,90,99): print('HDOP pct',q,np.nanpercentile(allh,q).round(2),'gmax pct',q,np.nanpercentile(allg,q).round(2))
    print('frac HDOP>11.7 (of valid)',(allh[ok]>11.7).mean().round(4),' frac gmax>11.7',(allg[ok]>11.7).mean().round(4), 'frac invalid',1-ok.mean())
    for lat,h,g,nv in res[::3]:
        v=~np.isnan(h); print(int(lat),'nvis',nv.mean().round(1),'valid',v.mean().round(3),'HDOP med',np.nanmedian(h).round(2) if v.any() else None,'P(HDOP>11.7)',(h[v]>11.7).mean().round(3) if v.any() else None,'P(gmax>11.7)',(g[v]>11.7).mean().round(3) if v.any() else None)
