"""Figure for Section 2.5 (Datasets): detection rate per sensor in three range bands,
computed separately for the intervals with the opponent ahead of and behind the ego
vehicle. Run from the repository root after dataset_stats.py."""
import json, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'serif','font.serif':['cmr10','DejaVu Serif'],'mathtext.fontset':'cm',
    'axes.formatter.use_mathtext':True,'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'savefig.bbox':'tight'})
S=json.load(open('scripts/datasets_stats.json'))
SENS=[('lid_clust','LiDAR clustering','#2EA12E'),('lid_pp','LiDAR PointPillars','#ED8C1A'),
      ('rad_clust','RaDAR','#1A99D9'),('cam_yolo','Camera','#B8A000')]
x=np.arange(3); w=0.2
fig,ax=plt.subplots(2,2,figsize=(6.1,4.4),sharey=True,sharex=True,gridspec_kw={'wspace':.06,'hspace':.25})
for r,(side,key) in enumerate([('ahead','pd_bands_ahead'),('behind','pd_bands_behind')]):
    for c,ses in enumerate(['0726','0803']):
        a=ax[r,c]
        for i,(k,lab,col) in enumerate(SENS):
            if k=='cam_yolo' and side=='behind': continue   # front cameras only in these sessions
            a.bar(x+(i-1.5)*w,100*np.array(S[ses]['sens'][k][key]),width=w*0.88,color=col,label=lab,zorder=3)
        a.set_xticks(x); a.set_xticklabels([r'0$-$75 m',r'75$-$100 m',r'100$-$150 m'])
        a.set_title(f'Session {ses}, opponent {side}',fontsize=9)
        a.set_ylim(0,100); a.grid(axis='y',color='0.9',lw=.6,zorder=0); a.tick_params(length=2)
    ax[r,0].set_ylabel('detection rate [%]')
h,l=ax[0,0].get_legend_handles_labels()
fig.legend(h,l,loc='lower center',bbox_to_anchor=(.5,-.01),ncol=4,frameon=False,fontsize=8,handlelength=1.2)
fig.savefig('figures/ch2/dataset_detection_rate.pdf')
print('ok')
