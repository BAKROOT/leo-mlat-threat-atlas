"""Asset dependency graph: edge register with provenance, reach statistics, and edge-set sensitivity.
Inputs: SATERA_Extended_Threat_Catalogue.xlsx (sheets 'Asset Connections', 'Threat Propagation').
Outputs: graph_edges.csv, graph_results.json
Reach: radius = number of other assets reachable; fan-in = number from which reachable;
rho_det / rho_root = least number of layer boundaries crossed (each edge counts |layer difference|)
on any path to the nearer of A3.4/A3.5, and to A4.6."""
import openpyxl,re,collections,heapq,json,csv,sys,itertools
XLSX=sys.argv[1] if len(sys.argv)>1 else 'data/catalogue/LEO_MLAT_Threat_Catalogue.xlsx'
wb=openpyxl.load_workbook(XLSX,data_only=True)
ws=wb['Asset Connections']
E=[];names={};layer={}
for r in ws.iter_rows(min_row=5,values_only=True):
    if not r[0] or not re.match(r'^A\d\.\d$',str(r[0])): continue
    names[r[0]]=r[1]; layer[r[0]]=int(r[0][1])
    for line in str(r[4] or '').split('\n'):
        m=re.match(r'(A\d\.\d) .*\((\w+)\)\s*$',line.strip())
        if m: E.append((r[0],m.group(1),m.group(2)))
A=list(names)
# threats -> assets (all roles) from the Threat Propagation sheet
T=collections.defaultdict(set); main={}
ws=wb['Threat Propagation']
for r in ws.iter_rows(min_row=5,values_only=True):
    if r[0] and re.match(r'^T\d\.\d\d$',str(r[0])):
        a=str(r[2]).split()[0]
        T[r[0]].add(a)
        if r[3]=='Main': main[r[0]]=a
THREATS=sorted(T)
EFF={'A1.7':2}   # A1.7 sits on TB2: as an intermediate hop of the ground segment it adds no crossing of its own; as an origin it counts at its own layer L1
INFERRED={('A1.6','A1.4'),('A1.6','A1.5'),('A4.1','A2.3')}   # readings S1 (two edges) and S2
def adj(E):
    d=collections.defaultdict(set)
    for a,b,k in E: d[a].add(b)
    return d
def reach(d,s):
    seen={s};st=[s]
    while st:
        x=st.pop()
        for y in d[x]:
            if y not in seen: seen.add(y);st.append(y)
    return seen-{s}
def dist(d,s,targets):
    D={s:0};pq=[(0,s)]
    while pq:
        c,x=heapq.heappop(pq)
        if c>D[x]:continue
        for y in d[x]:
            nc=c+abs((layer[x] if x==s else EFF.get(x,layer[x]))-EFF.get(y,layer[y]))
            if nc<D.get(y,99): D[y]=nc;heapq.heappush(pq,(nc,y))
    ds=[D[t] for t in targets if t in D]
    return min(ds) if ds else None
def stats(E,label):
    d=adj(E)
    rad={a:len(reach(d,a)) for a in A}
    fan={a:sum(1 for b in A if a in reach(d,b)) for a in A}
    rdet={a:dist(d,a,['A3.4','A3.5']) for a in A}
    rroot={a:dist(d,a,['A4.6']) for a in A}
    # threat level: largest value over assets (None counts as 'no first check')
    def tv(t,m):
        vals=[m[a] for a in T[t]]
        if any(v is None for v in vals): return None
        return max(vals)
    tdet={t:tv(t,rdet) for t in THREATS}
    troot={t:tv(t,rroot) for t in THREATS}
    nores=[t for t in THREATS if tdet[t] is None]
    ge2=[t for t in THREATS if tdet[t] is not None and tdet[t]>=2]
    vals=[v for v in troot.values() if v is not None]
    from collections import Counter
    # spearman radius vs threat count
    cnt={a:sum(1 for t in THREATS if a in T[t]) for a in A}
    mc=Counter({a:sum(1 for t in THREATS if main.get(t)==a) for a in A})
    def rank(x):
        s=sorted(x,key=lambda i:i[1]); r={}
        i=0
        while i<len(s):
            j=i
            while j+1<len(s) and s[j+1][1]==s[i][1]: j+=1
            for k in range(i,j+1): r[s[k][0]]=(i+j)/2+1
            i=j+1
        return r
    rr=rank([(a,rad[a]) for a in A]); rc=rank([(a,cnt[a]) for a in A])
    n=len(A); mr=sum(rr.values())/n; mcn=sum(rc.values())/n
    num=sum((rr[a]-mr)*(rc[a]-mcn) for a in A); den=(sum((rr[a]-mr)**2 for a in A)*sum((rc[a]-mcn)**2 for a in A))**.5
    sp=num/den if den else None
    return dict(label=label,n_edges=len(E),radius=rad,fanin=fan,rho_det=rdet,rho_root=rroot,
        assets_reaching_A46=sum(1 for a in A if a!='A4.6' and 'A4.6' in reach(d,a)),
        threats_no_first_check=nores,threats_ge2_before_check=len(ge2),
        mean_rho_root=round(sum(vals)/len(vals),2) if vals else None,n_threats_with_root=len(vals),
        rho_root_hist=dict(sorted(Counter(troot.values()).items(),key=lambda x:(x[0] is None,x[0]))) if False else {str(k):v for k,v in sorted(Counter(troot.values()).items(),key=lambda x:(x[0] is None,x[0] or 0))},
        spearman_radius_vs_main_threats=round(sp,2) if sp is not None else None,
        top_radius=sorted(rad.items(),key=lambda x:-x[1])[:8],
        threat_rho_root=troot,threat_rho_det=tdet)
CONFIGS={
 'C1 data+timing':lambda E:[e for e in E if e[2] in('data','timing')],
 'C2 data+timing+control':lambda E:[e for e in E if e[2] in('data','timing','control')],
 'C3 all four (register)':lambda E:list(E),
 'C4 all except inferred (S1,S2)':lambda E:[e for e in E if (e[0],e[1]) not in INFERRED],
 'C5 data+timing+control, no inferred':lambda E:[e for e in E if e[2] in('data','timing','control') and (e[0],e[1]) not in INFERRED],
 'C6 hosting only+data (no timing, no control)':lambda E:[e for e in E if e[2] in('data','hosting')],
}
res={k:stats(f(E),k) for k,f in CONFIGS.items()}
# Variant: split A4.7 into operators (A4.7a) and suppliers (A4.7b)
# operators administer the two hosts (A3.7 platform, A4.8 operations centre); suppliers supply software/updates: they reach the platform (A3.7) and the
# configuration/update system (A4.4) and the bus software (A1.6 via updates) but do not administer A4.8. (sensitivity reading, not in the register)
def split_variant():
    global A,layer,names,T,main
    A0,l0,n0,T0,m0=A[:],dict(layer),dict(names),dict(T),dict(main)
    E2=[e for e in E if e[0]!='A4.7']
    E2+= [('A4.7a','A3.7','hosting'),('A4.7a','A4.8','hosting'),('A4.7b','A3.7','hosting'),('A4.7b','A4.4','control')]
    A=[a for a in A0 if a!='A4.7']+['A4.7a','A4.7b']; layer.update({'A4.7a':4,'A4.7b':4}); names.update({'A4.7a':'Operators','A4.7b':'Suppliers'})
    T={t:{('A4.7a' if a=='A4.7' else a) for a in s} for t,s in T0.items()}; main={t:('A4.7a' if a=='A4.7' else a) for t,a in m0.items()}
    r=stats(E2,'V1 A4.7 split: operators administer hosts; suppliers reach A3.7 (hosting) and A4.4 (control)')
    A,layer,names,T,main=A0,l0,n0,T0,m0
    return r
res['V1 split A4.7']=split_variant()
# edge register with provenance
PROV={
('A1.1','A1.3','data'):('3.1.3 stage 2','stated'),
('A1.3','A1.4','data'):('3.1.3 stage 2','stated'),
('A1.4','A2.1','data'):('3.1.3 stage 2','stated'),
('A1.2','A1.5','timing'):('3.1.3 stage 2; Leonardi2026SyncIntegrity (GNSS disciplines the clock)','stated'),
('A1.5','A1.4','data'):('3.1.3 stage 2 (stamps against the onboard clock)','stated'),
('A1.5','A3.2','timing'):('Timing dependency, 3.1.3 (A3.2 consumes it)','stated'),
('A2.3','A1.5','timing'):('3.1.3 stage 2 (PTP over ISLs disciplines the clock)','stated'),
('A3.2','A3.3','timing'):('Timing dependency, 3.1.3 (database into solver)','stated'),
('A4.1','A2.3','timing'):('Reading S2: synchronisation policy governs the PTP exchange; not stated in 3.1.3','inferred'),
('A1.6','A1.4','hosting'):('Reading S1: bus hosts the payload processor; not stated in 3.1.3','inferred'),
('A1.6','A1.5','hosting'):('Reading S1: bus hosts the onboard clock; not stated in 3.1.3','inferred'),
('A2.5','A1.6','control'):('3.1.3 path (c): telecommands reach the satellites through A2.5 and the bus A1.6','stated'),
('A4.1','A2.5','control'):('3.1.3 path (c): synchronisation policy via telecommand channel','stated'),
('A4.3','A2.5','control'):('3.1.3 path (c): keys via telecommand channel','stated'),
('A4.4','A2.5','control'):('3.1.3 path (c): commands and updates via telecommand channel','stated'),
('A4.2','A3.2','control'):('3.1.3 path (a): orbit determination supplies ephemerides to the database','stated'),
('A4.4','A3.4','control'):('3.1.3 path (b): configuration system sets the integrity-monitor thresholds','stated'),
('A4.7','A3.7','hosting'):('Hosting: personnel and suppliers administer the central processing platform','author reading (TB0 organisational interface)'),
('A4.7','A4.8','hosting'):('Hosting: personnel and suppliers administer the operations centre','author reading (TB0 organisational interface)'),
}
for a in ['A3.1','A3.2','A3.3','A3.4','A3.5','A3.6']: PROV[('A3.7',a,'hosting')]=('Hosting: the central processing platform runs the L3 software assets','stated (asset register: A3.7 hosting asset)')
for a in ['A4.1','A4.2','A4.3','A4.4']: PROV[('A4.8',a,'hosting')]=('Hosting: the operations centre runs the governance assets','stated (asset register: A4.8 hosting asset)')
# remaining data edges (stage list)
for e in E:
    if e[2]=='data' and (e[0],e[1],e[2]) not in PROV:
        PROV[e]=('3.1.3 stages 2-7 of the end-to-end flow','stated')
rows=[]
for e in sorted(E,key=lambda x:(x[2],x[0],x[1])):
    p=PROV.get(e,('',''))
    rows.append(dict(edge_id=f'E{len(rows)+1:02d}',src=e[0],dst=e[1],kind=e[2],rationale=p[0],status=p[1],src_name=names[e[0]],dst_name=names[e[1]],crosses_boundaries=abs(layer[e[0]]-layer[e[1]])))
with open('graph_edges.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
def slim(r): return {k:v for k,v in r.items() if k not in('threat_rho_root','threat_rho_det')}
json.dump({'n_register_edges':len(E),'kinds':dict(collections.Counter(e[2] for e in E)),'configs':{k:r for k,r in res.items()}},open('graph_results.json','w'),indent=1)
if __name__=='__main__':
    print(len(E),collections.Counter(e[2] for e in E))
    for k,r in res.items():
        print(k,'| edges',r['n_edges'],'| A4.7 radius',r['radius'].get('A4.7',r['radius'].get('A4.7a')),'| A4.8',r['radius']['A4.8'],'| reach A4.6 by',r['assets_reaching_A46'],'| mean rho_root',r['mean_rho_root'],'| >=2 before check',r['threats_ge2_before_check'],'| no first check',len(r['threats_no_first_check']),'| spearman',r['spearman_radius_vs_main_threats'])
        print('   hist',r['rho_root_hist'],'| top',r['top_radius'][:5])
