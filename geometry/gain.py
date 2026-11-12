"""Per-satellite gain, leverage and actual-error analysis for the Walker-Star variants (illustrative, assumed geometry).
For one bias eps on satellite i: horizontal error e_h = g_i*eps (g_i = horizontal norm of column i of K=(G'G)^-1 G').
RAIM-style residual test (n-3 dof): expected residual norm of that bias = eps*sqrt(1-h_ii), h_ii = leverage of G.
Detected if residual norm >= T = sigma*sqrt(chi2.ppf(1-Pfa, n-3)).  n=3: no redundancy -> undetectable by residuals.
Outputs gain_results.json"""
import numpy as np, json, itertools
from scipy.stats import chi2
from hdop2 import geom
EREQ=350.0; STEP=30.0   # m; the covert 100 ns step is ~30 m
SIG=(10.0,30.0,100.0); PFA=1e-3
cfgs={'A 10x20, 0deg':(10,20,1,0.0),'B 10x20, 5deg':(10,20,1,5.0),'C 20x10, 0deg':(20,10,1,0.0),'D 8x25, 0deg':(8,25,1,0.0)}
def analyse(E,N):
    G=np.column_stack([-E,-N,np.ones(len(E))]); K=np.linalg.pinv(G)
    g=np.sqrt((K[:2]**2).sum(0)); H=G@K; hii=np.clip(np.diag(H),0,1)
    return g,hii
res={}
for name,(P,S,F,m) in cfgs.items():
    rows=geom(P,S,F,m)
    tot=len(rows); n3=0; recs=[]
    for l,E,N in rows:
        n=len(E)
        if n<3: continue
        g,hii=analyse(E,N); recs.append((n,g,hii))
    ok=len(recs)
    gmax=np.array([r[1].max() for r in recs]); hdop=np.array([np.sqrt((r[1]**2).sum()) for r in recs])
    nn=np.array([r[0] for r in recs])
    d={'samples':tot,'ge3':ok/tot,'n_med':float(np.median(nn)),
       'hdop_med':float(np.median(hdop)),'hdop_p99':float(np.percentile(hdop,99)),
       'gmax_med':float(np.median(gmax)),'gmax_p99':float(np.percentile(gmax,99)),'gmax_max':float(gmax.max()),
       'share_hdop_gt_h*':float(np.mean(hdop>EREQ/STEP)),'share_gmax_gt_h*':float(np.mean(gmax>EREQ/STEP)),
       'ratio_gmax_over_hdop_med':float(np.median(gmax/hdop)),
       # actual worst-case horizontal error of one 30 m step on the best-placed satellite
       'err30_med':float(np.median(gmax*STEP)),'err30_p99':float(np.percentile(gmax*STEP,99)),
       # smallest single-satellite bias that breaches 350 m (m)
       'eps_breach_med_m':float(np.median(EREQ/gmax)),'eps_breach_p01_m':float(np.percentile(EREQ/gmax,1))}
    # detectability
    for s in SIG:
        stealth_any=0; step_breach_undet=0; step_breach=0; nonred=0
        for n,g,hii in recs:
            sq=np.sqrt(np.clip(1-hii,1e-12,1))
            T=s*np.sqrt(chi2.ppf(1-PFA,n-3)) if n>3 else np.inf
            eps_req=EREQ/np.maximum(g,1e-9); eps_det=T/sq
            if np.any(eps_req<eps_det): stealth_any+=1
            if n==3: nonred+=1
            # the 30 m step
            br=g*STEP>=EREQ; 
            if br.any(): step_breach+=1
            if np.any(br & (STEP*sq<T)): step_breach_undet+=1
        d[f'sig{int(s)}']={'share_samples_with_open_window':stealth_any/ok,'share_30m_step_breaches':step_breach/ok,
                           'share_30m_step_breaches_undetected':step_breach_undet/ok,'share_n3_no_redundancy':nonred/ok}
    res[name]=d
    print(name,json.dumps({k:(round(v,3) if isinstance(v,float) else v) for k,v in d.items() if not isinstance(v,dict)}))
    for s in SIG: print('   sigma',s,{k:round(v,4) for k,v in d[f'sig{int(s)}'].items()})
json.dump(res,open('gain_results.json','w'),indent=1)
