"""Lateral error of the LiDARs after the recalibration, session 10/14_eva (Section 4.3.2).

Errors in the ego frame, e = p_det - p_gt, with the ground truth interpolated at the
acquisition time; detections within 5 m from the ground truth, one per message.
"""
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

U = 'data/'
P = '1014_yasnorth_00_eva_'
SENS = [('lid_clust', 'LiDAR Clustering', '#2ca02c'),
        ('lid_pp', 'LiDAR PointPillars', '#ff7f0e')]
GATE = 5.0


def load_det(f):
    d = pd.read_csv(f); d = d[d['count'] > 0]; rows = []
    for i in range(1, 16):
        if f'sens_stamp_{i}' not in d: break
        rows.append(pd.DataFrame({'ts': d[f'sens_stamp_{i}'], 'x': d[f'x_rel_{i}'],
                                  'y': d[f'y_rel_{i}'], 'msg': d.index}))
    return pd.concat(rows).dropna(subset=['x', 'ts'])


R = pd.read_csv(U + P + 'gt.csv').sort_values('stamp').dropna(subset=['x_rel'])
gt = R.stamp.values

plt.rcParams.update({'font.family': 'serif', 'font.serif': ['cmr10'], 'mathtext.fontset': 'cm',
                     'axes.formatter.use_mathtext': True, 'font.size': 9})
fig, axs = plt.subplots(2, 1, figsize=(6.3, 3.9), sharex=True)
for ax, (k, lab, c) in zip(axs, SENS):
    L = load_det(U + P + k + '.csv'); L = L[(L.ts >= gt.min()) & (L.ts <= gt.max())].copy()
    for q in ['x_rel', 'y_rel']:
        L['g_' + q] = np.interp(L.ts, gt, R[q].values)
    L['ex'] = L.x - L.g_x_rel; L['ey'] = L.y - L.g_y_rel; L['e'] = np.hypot(L.ex, L.ey)
    A = L[L.e < GATE].sort_values('e').drop_duplicates('msg')
    ax.scatter(A.g_x_rel, A.ey, s=2, c=c, alpha=0.35, linewidths=0, rasterized=True)
    ax.axhline(0, color='k', lw=0.5, ls=':'); ax.axvline(0, color='k', lw=0.5, ls=':')
    ax.set_xlim(-75, 150); ax.set_ylim(-1.5, 1.5)
    ax.set_ylabel(r'$e_y$ [m]'); ax.set_title(lab, fontsize=9, pad=3)
    ax.grid(alpha=0.3, lw=0.4)
axs[-1].set_xlabel(r'$x_{\mathrm{rel}}$ [m]')
fig.tight_layout(h_pad=0.6)
fig.savefig('figures/ch4/det_lat_yas.pdf', dpi=300, bbox_inches='tight')
fig.savefig('/tmp/claude-0/-home-claude/fe9c22f3-a0f7-524e-88e2-f943c23ad6f5/scratchpad/det_lat_yas.png',
            dpi=110, bbox_inches='tight')
