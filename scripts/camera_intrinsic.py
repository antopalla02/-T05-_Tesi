"""Longitudinal error of the camera (Section 4.4), sessions kept separate.

Errors in the ego frame, e = p_det - p_gt, ground truth interpolated at the acquisition
time, detections within 5 m from the ground truth (one per message). The longitudinal
offset of the reference of each session (Section 4.3.1), estimated as the mean
longitudinal error of LiDAR Clustering over the whole session, is removed.
Binned statistics (10 m in x_rel) are shown as mean +- standard deviation.
"""
import numpy as np, pandas as pd, json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

U = 'data/'
SES = [('0726', '20260726_ontrack_TUM_', '07/26_TUM', '#f2d675'),
       ('0803', '202600803_ontrack_KINETIZ_', '08/03_Kinetiz', '#a68400')]
GATE, NMIN = 5.0, 30
EDGES = np.arange(10, 130, 10)
SCR = '/tmp/claude-0/-home-claude/fe9c22f3-a0f7-524e-88e2-f943c23ad6f5/scratchpad/'


def load_det(f):
    d = pd.read_csv(f); d = d[d['count'] > 0]; rows = []
    for i in range(1, 16):
        if f'sens_stamp_{i}' not in d: break
        rows.append(pd.DataFrame({'ts': d[f'sens_stamp_{i}'], 'x': d[f'x_rel_{i}'],
                                  'y': d[f'y_rel_{i}'], 'msg': d.index}))
    return pd.concat(rows).dropna(subset=['x', 'ts'])


def errors(p, k):
    R = pd.read_csv(U + p + 'gt.csv').sort_values('stamp').dropna(subset=['x_rel'])
    gt = R.stamp.values
    L = load_det(U + p + k + '.csv'); L = L[(L.ts >= gt.min()) & (L.ts <= gt.max())].copy()
    for q in ['x_rel', 'y_rel']:
        L['g_' + q] = np.interp(L.ts, gt, R[q].values)
    L['ex'] = L.x - L.g_x_rel; L['ey'] = L.y - L.g_y_rel; L['e'] = np.hypot(L.ex, L.ey)
    return L[L.e < GATE].sort_values('e').drop_duplicates('msg').copy()


plt.rcParams.update({'font.family': 'serif', 'font.serif': ['cmr10'], 'mathtext.fontset': 'cm',
                     'axes.formatter.use_mathtext': True, 'font.size': 9})
fig, ax = plt.subplots(figsize=(6.3, 2.9))
OUT = {'edges': EDGES.tolist()}
for j, (t, p, lab, c) in enumerate(SES):
    off = errors(p, 'lid_clust').ex.mean()
    A = errors(p, 'cam_yolo'); A = A[A.g_x_rel > 0].copy(); A['ex0'] = A.ex - off
    g = A.groupby(pd.cut(A.g_x_rel, EDGES), observed=False)
    n = g.size().values; ctr = np.array([i.mid for i in g.size().index])
    ok = n >= NMIN
    mu, sd = g.ex0.mean().values, g.ex0.std().values
    OUT[t] = {'offset': float(off), 'n': n.tolist(), 'mean': np.round(mu, 3).tolist(),
              'std': np.round(sd, 3).tolist(),
              'slope_above_40m_cm_per_m': float(100 * np.polyfit(A[(A.g_x_rel > 40) & (A.g_x_rel < 120)].g_x_rel,
                                                               A[(A.g_x_rel > 40) & (A.g_x_rel < 120)].ex0, 1)[0])}
    ax.scatter(A.g_x_rel, A.ex0, s=2, c=c, alpha=0.25, linewidths=0, rasterized=True)
    dx = -0.8 if j == 0 else 0.8
    ax.errorbar(ctr[ok] + dx, mu[ok], yerr=sd[ok], fmt='-o', color=c, mec='k', mew=0.4, ms=3.5,
                lw=1.3, capsize=2.5, label='Session ' + lab.replace('_', r'$\_$'))
ax.axhline(0, color='k', lw=0.5, ls=':')
ax.set_xlim(0, 120); ax.set_ylim(-2, 3); ax.grid(alpha=0.3, lw=0.4)
ax.set_xlabel(r'$x_{\mathrm{rel}}$ [m]'); ax.set_ylabel(r'$e_x$ [m]')
ax.legend(loc='upper right', frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig('figures/ch4/camera_longitudinal_errors.pdf', dpi=300, bbox_inches='tight')
fig.savefig(SCR + 'camera_long.png', dpi=110, bbox_inches='tight')
json.dump(OUT, open('scripts/camera_intrinsic.json', 'w'), indent=1)
