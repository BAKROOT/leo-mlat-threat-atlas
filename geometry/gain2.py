"""(1) Monte-Carlo check that the linear gain formulas reproduce the simulated horizontal error of the least-squares solver;
(2) actual horizontal error (sigma*HDOP, and 30 m bias * g_i) under report dropping to m satellites (adversarial worst case over random m-subsets)."""
import numpy as np, json
from hdop2 import geom
from gain import analyse, EREQ, STEP
rng=np.random.default_rng(7)
rows=geom(10,20,1,0.0)
out={}
# (1) MC linearity check, 40 random geometries with n>=5
idx=[i for i in rng.permutation(len(rows)) if len(rows[i][1])>=5][:40]
dev_noise=[];dev_bias=[]
for i in idx:
    l,E,N=rows[i]; n=len(E); G=np.column_stack([-E,-N,np.ones(n)]); K=np.linalg.pinv(G)
    g,hii=analyse(E,N); hd=np.sqrt((g**2).sum())
    sig=30.0; Z=rng.normal(0,sig,(4000,n)); est=Z@K.T
    rms=np.sqrt((est[:,0]**2+est[:,1]**2).mean())
    dev_noise.append(rms/(sig*hd)-1)
    k=int(np.argmax(g)); z=np.zeros(n); z[k]=STEP; e=K@z
    dev_bias.append(np.hypot(e[0],e[1])/(g[k]*STEP)-1)
out['mc_noise_rel_dev_max']=float(np.max(np.abs(dev_noise))); out['mc_bias_rel_dev_max']=float(np.max(np.abs(dev_bias)))
print('MC rel. deviation noise/bias',out['mc_noise_rel_dev_max'],out['mc_bias_rel_dev_max'])
# (2) dropping
sel=[i for i in rng.permutation(len(rows))[:1200]]
for sig in (10.0,30.0,100.0):
    pass
res={}
for m in (3,4,6):
    E1=[];G1=[];tot=0
    for i in sel:
        l,E,N=rows[i]; n=len(E)
        if n<m: continue
        tot+=1
        worstH=0;worstG=0
        for _ in range(400):
            c=rng.choice(n,m,replace=False)
            try:
                g,hii=analyse(E[c],N[c])
            except Exception: continue
            h=np.sqrt((g**2).sum())
            worstH=max(worstH,h); worstG=max(worstG,g.max())
        E1.append(worstH);G1.append(worstG)
    E1=np.array(E1);G1=np.array(G1)
    d={'n':tot,'worst_hdop_med':float(np.median(E1)),'worst_hdop_p95':float(np.percentile(E1,95))}
    for sig in (10.0,30.0,100.0):
        d[f'share_1sigma_err_gt_350_sig{int(sig)}']=float(np.mean(E1*sig>EREQ))
    d['share_30m_step_breach']=float(np.mean(G1*STEP>=EREQ)); d['err30_worst_med']=float(np.median(G1*STEP)); d['err30_worst_p95']=float(np.percentile(G1*STEP,95))
    res[m]=d; print(m,{k:round(v,3) for k,v in d.items()})
out['drop']=res
json.dump(out,open('gain2_results.json','w'),indent=1)
