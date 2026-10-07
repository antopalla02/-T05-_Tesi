"""Chapter 2 - dataset figures and statistics.
Usage: python3 make_dataset_figures.py <BAG_TAG> <det_csv_glob_prefix> [gt_csv]
Reads the <bag>_det_<sensor>.csv exports (export_detections_csv.m). The opponent
GT is taken at detection instants (union of all sensors on a 0.1 s grid), i.e.
the statistics describe the opponent WHILE it is observed by at least one sensor.
"""
import sys, glob, json, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'serif','font.serif':['cmr10','DejaVu Serif'],
    'mathtext.fontset':'cm','axes.formatter.use_mathtext':True,'font.size':9,
    'axes.grid':True,'grid.alpha':.25,'grid.linewidth':.5,'axes.spines.top':False,
    'axes.spines.right':False,'lines.linewidth':1.0,'savefig.bbox':'tight'})
TAG, PFX = sys.argv[1], sys.argv[2]
OUT='figures/ch2/'   # run from the repository root
import os; os.makedirs(OUT, exist_ok=True)
SENS={'lidar':('LiDAR clustering','#2EA12E'),'pp':('LiDAR PointPillars','#ED8C1A'),
      'radar':('Radar','#1A99D9'),'camera':('Camera','#B8A000')}
INK='#33475b'
cols=['sens_stamp','stamp','gt_vx','gt_ax','gt_rho','gt_yaw_rate','x_rel_gt','y_rel_gt']
D={}
for s in SENS:
    f=glob.glob(PFX+f'*_det_{s}.csv')
    if not f: continue
    d=pd.read_csv(f[0]).sort_values('sens_stamp')
    d=d[np.r_[True,np.diff(d.sens_stamp.values)>1e-3]]          # drop re-published scans
    D[s]=d[[c for c in cols if c in d]].dropna(subset=['gt_vx'])
A=pd.concat([d.assign(src=s) for s,d in D.items()])
A['tb']=(A.sens_stamp/0.1).round().astype(int)
G=A.groupby('tb').first().reset_index().sort_values('sens_stamp')
G['ay']=G.gt_vx*np.radians(G.gt_yaw_rate)
t0=G.sens_stamp.min(); G['t']=G.sens_stamp-t0
mov=G.gt_vx>2; M=G[mov]
st={'tag':TAG,'session_s':float(G.sens_stamp.max()-t0),'visible_s':len(G)*0.1,
    'moving_s':float(mov.sum()*0.1),'v_mean':M.gt_vx.mean(),'v_p95':M.gt_vx.quantile(.95),'v_max':M.gt_vx.max(),
    'ax_p1':M.gt_ax.quantile(.01),'ax_p99':M.gt_ax.quantile(.99),'ay_p99':abs(M.ay).quantile(.99),
    'frac_brake':float((M.gt_ax<-2).mean()),'frac_acc':float((M.gt_ax>2).mean()),
    'frac_corner':float(((abs(M.ay)>5)&(abs(M.gt_ax)<=2)).mean())}
st['frac_steady']=1-st['frac_brake']-st['frac_acc']-st['frac_corner']
st['sensors']={s:{'n':len(d),'rate_hz':1/np.median(np.diff(d.sens_stamp)),
    'lat_ms':1e3*np.median(d.stamp-d.sens_stamp) if 'stamp' in d else None,
    'rho_p50':d.gt_rho.median(),'rho_p95':d.gt_rho.quantile(.95),'front':float((d.x_rel_gt>0).mean())} for s,d in D.items()}
json.dump(st,open(f'scripts/stats_{TAG}.json','w'),indent=1,default=float)
print(json.dumps(st,indent=1,default=lambda x: round(float(x),3)))

def broken(t,y,gap=0.5):
    y=y.astype(float).copy(); y[np.r_[False,np.diff(t)>gap]]=np.nan; return y
# --- F1: opponent longitudinal dynamics over the session
fig,ax=plt.subplots(2,1,figsize=(6.1,3.6),sharex=True,gridspec_kw={'hspace':.12})
ax[0].plot(G.t,broken(G.t.values,G.gt_vx.values)*3.6,color=INK,lw=.8)
ax[0].set_ylabel(r'$v$ [km/h]')
a=broken(G.t.values,G.gt_ax.values)
ax[1].plot(G.t,a,color=INK,lw=.6)
for th in (-2,2): ax[1].axhline(th,color='0.45',ls='--',lw=.7)
ax[1].set_ylabel(r'$a_x$ [m/s$^2$]'); ax[1].set_xlabel('time [s]')
fig.savefig(OUT+f'dataset_{TAG}_timeseries.pdf'); plt.close(fig)
# --- F2: distributions of the opponent motion (moving samples)
fig,ax=plt.subplots(1,3,figsize=(6.1,2.0),gridspec_kw={'wspace':.35})
for k,(x,lab,b) in enumerate([(M.gt_vx*3.6,r'$v$ [km/h]',np.arange(0,170,5)),
                               (M.gt_ax,r'$a_x$ [m/s$^2$]',np.arange(-14,12,.5)),
                               (M.ay,r'$a_y = v\,\dot\psi$ [m/s$^2$]',np.arange(-16,16.5,.5))]):
    w=np.full(len(x),100/len(x))
    ax[k].hist(x,bins=b,weights=w,color=INK,alpha=.85,edgecolor='white',linewidth=.3)
    ax[k].set_xlabel(lab)
ax[0].set_ylabel('share of samples [%]')
fig.savefig(OUT+f'dataset_{TAG}_distributions.pdf'); plt.close(fig)
# --- F3: where each sensor sees the opponent (ego frame, x forward)
ss=[s for s in SENS if s in D]
fig,ax=plt.subplots(1,len(ss),figsize=(6.1,3.0),sharey=True,gridspec_kw={'wspace':.08})
for k,s in enumerate(ss):
    d=D[s]; ax[k].scatter(d.y_rel_gt,d.x_rel_gt,s=1.2,color=SENS[s][1],alpha=.35,lw=0,rasterized=True)
    ax[k].plot(0,0,marker='^',color='k',ms=5); ax[k].set_title(SENS[s][0],fontsize=9)
    ax[k].set_xlim(40,-40); ax[k].set_ylim(-80,150); ax[k].set_xlabel(r'$y_{rel}$ [m]')
    ax[k].text(.97,.03,f"$\\rho_{{50}}$ = {d.gt_rho.median():.0f} m\n$\\rho_{{95}}$ = {d.gt_rho.quantile(.95):.0f} m",
               transform=ax[k].transAxes,ha='right',va='bottom',fontsize=7.5,color=INK)
ax[0].set_ylabel(r'$x_{rel}$ [m]')
fig.savefig(OUT+f'dataset_{TAG}_coverage.pdf',dpi=300); plt.close(fig)
