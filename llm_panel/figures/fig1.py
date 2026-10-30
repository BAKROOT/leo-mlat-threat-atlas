from common import *
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
fig=plt.figure(figsize=(7.16,2.55)); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,100); ax.set_ylim(0,36); ax.axis('off')
def box(x,y,w,h,fc,ec,txt_title,txt_body=None,tc=INK,fs=6.8,bold=True,lw=0.8):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.0,rounding_size=0.9',fc=fc,ec=ec,lw=lw,zorder=2))
    ax.text(x+w/2,y+h-1.6,txt_title,ha='center',va='top',fontsize=fs+0.4,color=tc,fontweight='bold' if bold else 'normal',zorder=3)
    if txt_body: ax.text(x+w/2,y+h-4.4,txt_body,ha='center',va='top',fontsize=fs-0.6,color=MUTE if tc==INK else tc,zorder=3,linespacing=1.25)
def arrow(x1,y1,x2,y2,c=MUTE):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=7,lw=0.8,color=c,zorder=1,shrinkA=0,shrinkB=0))
# stage headers
for x,t in [(9.5,'1  Material'),(33.5,'2  Prompts'),(57,'3  Four vendors'),(84,'4  Outputs')]:
    ax.text(x,34.2,t,fontsize=7.6,fontweight='bold',color=INK,ha='center',va='center')
box(1,11,17,19.5,'#f4f6fa','#9aa6b8','Extended catalogue','55 threats\n4 layers, 27 assets\n78 atlas sources\n\nauthors\' category, goals,\ntier, evidence and\nscores withheld')
box(23,19,21.5,11.5,'#eaf1fb',BLUE,'Prompt A: elicitation','architecture, vocabulary and rubric;\nno threat shown. The model lists the\nthreats it expects.')
box(23,5,21.5,12.5,'#eaf1fb',BLUE,'Prompts B1 to B4: rating','16 + 12 + 12 + 15 threat cards.\nOne JSON object per prompt: STRIDE-$\\tau$,\ngoals, tier, evidence, PA-DREAD\nscores, validity, issues.')
ax.text(33.75,2.4,'identical text for every model (hash-checked)\nfresh chat, closed book, no tools, no memory',ha='center',va='center',fontsize=6.2,color=MUTE,linespacing=1.25)
models=[('Anthropic','Claude Sonnet 5.5'),('OpenAI','ChatGPT, GPT-6'),('DeepSeek','DeepSeek, DeepThink'),('Google','Gemini 3.1 Pro')]
for i,(v,m) in enumerate(models):
    y=24.6-i*6.6
    ax.add_patch(FancyBboxPatch((50,y),14.5,5.3,boxstyle='round,pad=0.0,rounding_size=0.9',fc='white',ec=INK,lw=0.8,zorder=2))
    ax.text(57.25,y+3.55,v,ha='center',va='center',fontsize=7,fontweight='bold',color=INK,zorder=3); ax.text(57.25,y+1.55,m,ha='center',va='center',fontsize=6.4,color=MUTE,zorder=3)
arrow(18.2,20.5,22.8,24.5); arrow(18.2,19,22.8,11.5)
ax.plot([46.2,46.2],[7.0,30.3],color=MUTE,lw=1.4,zorder=1,solid_capstyle='round')
ax.plot([44.7,46.2],[24.8,24.8],color=MUTE,lw=0.8,zorder=1); ax.plot([44.7,46.2],[11.5,11.5],color=MUTE,lw=0.8,zorder=1)
for i in range(4):
    y=24.6-i*6.6+2.65; arrow(46.2,y,49.8,y)
ax.plot([67.2,67.2],[7.0,30.3],color=MUTE,lw=1.4,zorder=1,solid_capstyle='round')
for i in range(4):
    y=24.6-i*6.6+2.65; ax.plot([64.7,67.2],[y,y],color=MUTE,lw=0.8,zorder=1)
arrow(67.2,17.5,68.8,17.5)
ax.text(65.8,31.2,'one reply per\nprompt, 5 each',ha='center',va='bottom',fontsize=6,color=MUTE,linespacing=1.2)
box(69.3,10,9.6,15,'#f4f4f1','#9aa6b8','Check','220 ratings\nall valid JSON\n0 repairs',fs=6.4)
for k,(t,b,y) in enumerate([('Agreement','Krippendorff $\\alpha$,\nKendall $W$, repeat',24.5),('Disagreement map','models vs catalogue,\nmodels vs models',15.2),('Completeness','what the models\nlist unprompted',5.9)]):
    box(82,y,17,8.4,'#eaf1fb',BLUE,t,b,fs=6.4)
    arrow(79,17.5,81.8,y+4.2)
for y,t in [(24.5,'Fig. 2'),(15.2,'Fig. 3'),(5.9,'Fig. 4')]: ax.text(98.5,y+7.5,t,fontsize=5.6,color=BLUE,ha='right',va='top')
fig.savefig('out/Fig_panel_protocol.pdf'); fig.savefig('out/Fig_panel_protocol.png',dpi=170)
