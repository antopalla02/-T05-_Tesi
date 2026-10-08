"""Statistics of the two sessions for Section 2.5 (Datasets)."""
import numpy as np, pandas as pd, glob, json
# Folder with the CSV exports: <session>_gt.csv and <session>_<sensor>.csv
U='data/'
SES={'0726':(U+'20260726_ontrack_TUM_gt.csv','20260726_ontrack_TUM_'),
     '0803':(U+'202600803_ontrack_KINETIZ_gt.csv','202600803_ontrack_KINETIZ_')}
SENS=['lid_clust','lid_pp','rad_clust','cam_yolo']
GATE=5.0; DT=0.1; EDGES=np.arange(0,210,10)
RB=[0,25,50,75,100,125,150,np.inf]   # range bins for the detection-rate table
import os
BANDS=[float(x) for x in os.environ.get('BANDS','0,75,100,150').split(',')]                 # range bands for the detection-rate figure
PCT=[5,25,50,75,95]
def load_det(f):
    d=pd.read_csv(f); d=d[d['count']>0]; rows=[]
    for i in range(1,16):
        if f'sens_stamp_{i}' not in d: break
        rows.append(pd.DataFrame({'ts':d[f'sens_stamp_{i}'],'t':d['stamp'],'x':d[f'x_rel_{i}'],'y':d[f'y_rel_{i}'],'msg':d.index}))
    return d,pd.concat(rows).dropna(subset=['x','ts'])
OUT={}
for tag,(gf,pfx) in SES.items():
    G=pd.read_csv(gf).sort_values('stamp'); R=G.dropna(subset=['x_rel'])
    t0,t1=R.stamp.min(),R.stamp.max(); W=G[(G.stamp>=t0)&(G.stamp<=t1)]
    mov=W.vx>2; M=W[mov]; ay=M.vx*np.radians(M.yaw_rate)
    s=np.sign(R.x_rel.values); swaps=int(((s[1:]!=s[:-1])&(R.rho.values[1:]<30)).sum())
    S=dict(duration=t1-t0, gt_rate=1/np.median(np.diff(G.stamp)), dist_km=np.trapezoid(W.vx,W.stamp)/1e3,
           moving=mov.mean(), stopped_s=float((~mov).sum()*np.median(np.diff(W.stamp))), vmax=W.vx.max()*3.6, vmean=M.vx.mean()*3.6, ax_p1=M.ax.quantile(.01), ax_p99=M.ax.quantile(.99),
           ay_p99=abs(ay).quantile(.99), laps=np.trapezoid(W.vx,W.stamp)/4909.0,
           rho50=R.rho.median(), rho90=R.rho.quantile(.9), within50=(R.rho<50).mean(), ahead=(R.x_rel>0).mean(),
           rd5=R.rho_dot.quantile(.05), rd95=R.rho_dot.quantile(.95), swaps=swaps)
    gt=R.stamp.values; bins=np.arange(gt.min(),gt.max(),DT); gr=np.interp(bins,gt,R.rho.values)
    gxb=np.interp(bins,gt,R.x_rel.values); grd=np.abs(np.interp(bins,gt,R.rho_dot.values))
    anyhit=np.zeros(len(bins),bool); sens={}
    for k in SENS:
        d,L=load_det(glob.glob(U+pfx+k+'.csv')[0])
        L=L[(L.ts>=gt.min())&(L.ts<=gt.max())].copy()
        L['gx']=np.interp(L.ts,gt,R.x_rel.values); L['gy']=np.interp(L.ts,gt,R.y_rel.values); L['gr']=np.interp(L.ts,gt,R.rho.values)
        L['e']=np.hypot(L.x-L.gx,L.y-L.gy)
        A=L[L.e<GATE].sort_values('e').drop_duplicates('msg')
        hit=np.zeros(len(bins),bool); hit[np.clip(np.searchsorted(bins,A.ts.values)-1,0,len(bins)-1)]=True; anyhit|=hit
        sens_pdb=[float(hit[(gr>=a)&(gr<b)].mean()) for a,b in zip(RB[:-1],RB[1:])]
        front=(gxb>0) if k=='cam_yolo' else np.ones(len(bins),bool)   # camera pipeline: front cameras only
        sens_band=[float(hit[front&(gr>=a)&(gr<b)].mean()) for a,b in zip(BANDS[:-1],BANDS[1:])]
        inb=[(gr>=a)&(gr<b) for a,b in zip(BANDS[:-1],BANDS[1:])]
        sens_band_ahead=[float(hit[m&(gxb>0)].mean()) for m in inb]    # detection rate with the opponent ahead
        sens_band_behind=[float(hit[m&(gxb<=0)].mean()) for m in inb]  # detection rate with the opponent behind
        pdr=[float(hit[(gr>=a)&(gr<b)].mean()) if ((gr>=a)&(gr<b)).sum()*DT>20 else None for a,b in zip(EDGES[:-1],EDGES[1:])]
        ss=np.sort(d.sens_stamp_1.unique())
        sens[k]=dict(dets=len(L),assoc=len(A),other=1-len(A)/len(L),rate=1/np.median(np.diff(ss)),lat_ms=float(np.median(d.stamp-d.sens_stamp_1)*1e3),
                     rho50=A.gr.median(),rho95=A.gr.quantile(.95),rhomax=A.gr.max(),ahead=(A.gx>0).mean(),cover=hit.mean(),
                     active=(float(ss.min()),float(ss.max())),pd=pdr,pd_bins=sens_pdb,pd_bands=sens_band,
                     pd_bands_ahead=sens_band_ahead,pd_bands_behind=sens_band_behind)
    S['cover_any']=anyhit.mean()
    S['geom_detected']={'rho':np.percentile(gr[anyhit],[50,95,99]).tolist(),'rho_dot_abs':np.percentile(grd[anyhit],[50,95,99]).tolist()}
    S['pd_any_bands']=[float(anyhit[(gr>=a)&(gr<b)].mean()) for a,b in zip(BANDS[:-1],BANDS[1:])]
    S['pd_any_bins']=[float(anyhit[(gr>=a)&(gr<b)].mean()) for a,b in zip(RB[:-1],RB[1:])]
    S['time_bins']=[float(((gr>=a)&(gr<b)).mean()) for a,b in zip(RB[:-1],RB[1:])]
    S['pd_any']=[float(anyhit[(gr>=a)&(gr<b)].mean()) if ((gr>=a)&(gr<b)).sum()*DT>20 else None for a,b in zip(EDGES[:-1],EDGES[1:])]
    S['time_by_range']={f'{a}-{b}':float(((gr>=a)&(gr<b)).mean()) for a,b in [(0,50),(50,100),(100,150),(150,1e4)]}
    br=-M.ax[M.ax<0]; tr=M.ax[M.ax>0]
    S['dyn_p95_p99']={'v':np.percentile(M.vx*3.6,[50,95,99]).tolist(),'brake':np.percentile(br,[95,99]).tolist(),
                      'traction':np.percentile(tr,[95,99]).tolist(),'ay_abs':np.percentile(np.abs(ay),[95,99]).tolist()}
    S['geom_p50_95_99']={'rho':np.percentile(R.rho,[50,95,99]).tolist(),'rho_dot_abs':np.percentile(R.rho_dot.abs(),[50,95,99]).tolist()}
    S['pct']={'v':np.percentile(M.vx*3.6,PCT).tolist(),'ax':np.percentile(M.ax,PCT).tolist(),'ay':np.percentile(ay,PCT).tolist(),
              'rho':np.percentile(R.rho,PCT).tolist(),'rho_dot':np.percentile(R.rho_dot,PCT).tolist()}
    S['pd_bins']={}
    S['sens']=sens; OUT[tag]=S
json.dump(OUT,open('scripts/datasets_stats.json','w'),indent=1,default=float)
for tag,S in OUT.items():
    print(f"=== {tag}: dur {S['duration']:.0f}s dist {S['dist_km']:.1f}km moving {S['moving']:.0%} vmax {S['vmax']:.0f} vmean {S['vmean']:.0f} ax {S['ax_p1']:.1f}/{S['ax_p99']:.1f} ay99 {S['ay_p99']:.1f}")
    print(f"   rho50 {S['rho50']:.0f} rho90 {S['rho90']:.0f} <50m {S['within50']:.0%} ahead {S['ahead']:.0%} rd {S['rd5']:.1f}/{S['rd95']:.1f} swaps {S['swaps']} cover_any {S['cover_any']:.0%}")
    print('   time by range',{k:round(v,2) for k,v in S['time_by_range'].items()})
    for k,v in S['sens'].items():
        print(f"   {k:10s} assoc {v['assoc']:5d} other {v['other']:5.1%} rate {v['rate']:5.1f} lat {v['lat_ms']:4.0f} rho {v['rho50']:.0f}/{v['rho95']:.0f}/{v['rhomax']:.0f} ahead {v['ahead']:.0%} cover {v['cover']:.0%} active {v['active'][0]:.0f}-{v['active'][1]:.0f}")
