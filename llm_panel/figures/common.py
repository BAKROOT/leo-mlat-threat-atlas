import sys, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
R='../results/'
sys.path.insert(0,'../tools')
import importlib.util
sp=importlib.util.spec_from_file_location('ag','../tools/agreement.py'); ag=importlib.util.module_from_spec(sp); sp.loader.exec_module(ag)
plt.rcParams.update({'font.family':'STIXGeneral','mathtext.fontset':'stix','font.size':7.5,'axes.labelsize':7.5,'axes.titlesize':8,
 'xtick.labelsize':7,'ytick.labelsize':7,'legend.fontsize':7,'axes.linewidth':0.6,'xtick.major.width':0.5,'ytick.major.width':0.5,
 'xtick.major.size':2.5,'ytick.major.size':2.5,'pdf.fonttype':42,'ps.fonttype':42,'savefig.dpi':300,'axes.spines.top':False,'axes.spines.right':False})
INK='#1b1b1b'; MUTE='#5b5b58'; GRID='#d9d8d3'; BLUE='#2a78d6'; ORANGE='#eb6834'; VIOLET='#6250d6'; LIGHT='#e9eef7'
MODELS=['claude','chatgpt','deepseek','gemini']
NAMES={'claude':'Claude','chatgpt':'ChatGPT','deepseek':'DeepSeek','gemini':'Gemini'}
L=pd.read_csv(R+'panel_long.csv')
S=pd.read_csv(R+'panel_summary.csv')
