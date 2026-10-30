import pandas as pd, json
# k -> (class, [catalogue ids]) ; C = covered, P = partly covered (related, narrower or different), N = not in catalogue
M={0:('C','T1.11'),1:('C','T1.01'),2:('C','T3.02'),3:('C','T3.12'),4:('C','T4.06'),5:('C','T4.02'),6:('C','T3.06'),7:('C','T2.01'),8:('C','T2.11'),9:('C','T4.04'),
10:('C','T1.05'),11:('C','T1.10'),12:('C','T2.06'),13:('C','T1.14'),14:('C','T1.04'),15:('C','T1.13'),16:('C','T1.15'),17:('P','T2.03'),18:('C','T3.01'),19:('C','T3.04'),
20:('N',''),21:('N',''),22:('C','T3.03'),23:('C','T3.09'),24:('C','T3.05'),25:('C','T4.01'),26:('C','T4.02'),27:('C','T4.15'),28:('C','T4.11'),29:('C','T4.12'),
30:('C','T4.15'),31:('C','T4.09'),32:('N',''),33:('C','T2.05'),34:('P','T1.16'),35:('N',''),36:('P','T2.02'),37:('N',''),38:('P','T4.14'),39:('P','T1.09'),
40:('C','T4.14'),41:('P','T3.01'),42:('C','T2.06'),43:('C','T1.11'),44:('C','T4.01'),45:('C','T2.11'),46:('C','T3.06'),47:('P','T2.04'),48:('N',''),49:('C','T3.07'),
50:('C','T1.14'),51:('C','T4.04'),52:('C','T2.01'),53:('C','T4.02'),54:('C','T3.03'),55:('C','T3.01'),56:('C','T1.02'),57:('C','T1.05'),58:('P','T3.05'),59:('C','T3.09'),
60:('C','T3.12'),61:('C','T1.15'),62:('C','T1.13'),63:('C','T4.08'),64:('C','T4.12'),65:('C','T4.13'),66:('C','T4.15'),67:('C','T1.10'),68:('P','T2.01'),69:('C','T1.08'),
70:('P','T2.03'),71:('C','T1.04'),72:('C','T1.16'),73:('C','T1.09'),74:('C','T1.03'),75:('C','T3.08'),76:('P','T3.04'),77:('C','T3.08'),78:('N',''),79:('C','T4.09'),
80:('N',''),81:('N',''),82:('C','T4.14'),83:('C','T1.15'),84:('C','T4.11'),85:('C','T2.08'),86:('P','T2.03'),87:('C','T1.01'),88:('C','T1.11'),89:('C','T1.11'),
90:('C','T2.06'),91:('C','T2.11'),92:('C','T4.04'),93:('C','T3.06'),94:('C','T4.01'),95:('C','T3.03'),96:('C','T3.01'),97:('C','T3.02'),98:('C','T3.02'),99:('C','T3.12'),
100:('C','T1.14'),101:('C','T1.13'),102:('C','T3.09'),103:('C','T4.08'),104:('C','T4.10'),105:('C','T4.12'),106:('C','T4.15'),107:('C','T2.01'),108:('C','T2.08'),109:('C','T2.05'),
110:('C','T1.15'),111:('C','T1.04'),112:('C','T3.01'),113:('C','T1.01'),114:('C','T1.11'),115:('C','T1.04'),116:('C','T1.08'),117:('C','T2.11'),118:('C','T1.16'),119:('C','T2.01'),
120:('C','T2.05'),121:('C','T2.06'),122:('P','T2.12'),123:('C','T2.11'),124:('C','T3.01'),125:('C','T3.03'),126:('C','T3.05'),127:('P','T1.11'),128:('C','T3.07'),129:('C','T3.09'),
130:('C','T3.12'),131:('C','T4.01'),132:('N',''),133:('C','T4.04'),134:('C','T4.13'),135:('P','T4.08'),136:('P','T4.10'),137:('C','T4.12'),138:('P','T4.07'),139:('C','T2.08'),
140:('C','T1.03'),141:('P','T1.11'),142:('N','')}
e=pd.ExcelFile('../results/Panel_Review.xlsx').parse('Elicited_all')
assert len(M)==len(e)==143
e['k']=range(len(e)); e['map_class']=e.k.map(lambda k:M[k][0]); e['catalogue_id']=e.k.map(lambda k:M[k][1])
cat=pd.read_csv('../results/panel_summary.csv')[['id','title']]
ids=list(cat.id)
print(e_orig.map_class.value_counts().to_dict() if 'e_orig' in dir() else '')
e_orig=e; e=pd.concat([e,pd.DataFrame([dict(model=e.loc[k,'model'],k=k,map_class='C',catalogue_id='T2.07') for k in (12,90)])],ignore_index=True)
res={}
for m,g in list(e.groupby('model'))+[('all',e)]:
    c=set(g[g.map_class=='C'].catalogue_id); p=set(g[g.map_class=='P'].catalogue_id)
    res[m]=dict(n=len(g),C=int((g.map_class=='C').sum()),P=int((g.map_class=='P').sum()),N=int((g.map_class=='N').sum()),rec_C=len(c),rec_CP=len(c|p))
print(pd.DataFrame(res).T)
# how many models named each catalogue threat (C or P)
named={i:sorted(set(e[(e.catalogue_id==i)&(e.map_class.isin(['C','P']))].model)) for i in ids}
cnt=pd.Series({i:len(v) for i,v in named.items()})
print('named by 0:',[i for i in ids if cnt[i]==0]); print('by 1:',[i for i in ids if cnt[i]==1]); print(cnt.value_counts().sort_index().to_dict())
# strict (C only)
namedC={i:sorted(set(e[(e.catalogue_id==i)&(e.map_class=='C')].model)) for i in ids}
cc=pd.Series({i:len(v) for i,v in namedC.items()}); print('strict C by 0:',[i for i in ids if cc[i]==0]); print(cc.value_counts().sort_index().to_dict())
extra=pd.DataFrame([dict(model=e.loc[k,'model'],layer=e.loc[k,'layer'],title=e.loc[k,'title']+' [second mapping]',k=k,map_class='C',catalogue_id='T2.07') for k in (12,90)])
E2=pd.concat([e,extra],ignore_index=True)
E2.drop(columns=['mechanism'],errors='ignore').to_csv('elicitation_mapping_manual.csv',index=False)
json.dump(dict(named=named,namedC=namedC),open('named.json','w'))
