"""Deterministic components of the measurement errors (Section 4.3).

Errors in the ego frame, e = p_det - p_gt, with the ground truth interpolated at the
acquisition time; detections within 5 m from the ground truth, one per message.
Outputs: figures of session 0726 and the statistics of both sessions (json).
"""
import numpy as np, pandas as pd, json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

U = 'data/'
SES = {'0726': '20260726_ontrack_TUM_', '0803': '202600803_ontrack_KINETIZ_'}
SENS = [('lid_clust', 'LiDAR Clustering', '#2ca02c'),
        ('lid_pp', 'LiDAR PointPillars', '#ff7f0e'),
        ('rad_clust', 'RaDAR', '#4fa8e0'),
        ('cam_yolo', 'Camera', '#e6b800')]
CAM_LINE = '#a68400'
GATE = 5.0
CAM_NOM = (20.0, 60.0)  # nominal range of the camera [m]
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
    L['v'] = np.interp(L.ts, gt, R.vx.values)
    L['ex'] = L.x - L.g_x_rel; L['ey'] = L.y - L.g_y_rel; L['e'] = np.hypot(L.ex, L.ey)
    return L[L.e < GATE].sort_values('e').drop_duplicates('msg').sort_values('ts')


E = {(t, k): errors(p, k) for t, p in SES.items() for k, *_ in SENS}

# ---------------- statistics ----------------
ST = {}
for t in SES:
    ST[t] = {}
    for k, *_ in SENS:
        A = E[(t, k)]; c = np.polyfit(A.g_x_rel, A.ey, 1)
        # nominal conditions: opponent ahead, 20-60 m, moving faster than 2 m/s
        nom = A[(A.g_x_rel > CAM_NOM[0]) & (A.g_x_rel < CAM_NOM[1]) & (A.v.abs() > 2.0)]
        ST[t][k] = dict(n=len(A), ex_mean=A.ex.mean(), ex_std=A.ex.std(),
                        ex_mean_nominal=nom.ex.mean(), ex_std_nominal=nom.ex.std(),
                        ey_slope_cm_per_m=100 * c[0], ey_intercept=c[1],
                        ey_angle_deg=np.degrees(np.arctan(c[0])))
    ST[t]['lidar_offset'] = 0.5 * (ST[t]['lid_clust']['ex_mean'] + ST[t]['lid_pp']['ex_mean'])
json.dump(ST, open('scripts/deterministic_components.json', 'w'), indent=1, default=float)
for t in ST:
    print(t, 'lidar offset %.3f' % ST[t]['lidar_offset'])
    for k, *_ in SENS:
        s = ST[t][k]
        print(f"  {k:9s} ex {s['ex_mean']:+.3f} std {s['ex_std']:.3f} (20-60 {s['ex_mean_nominal']:+.3f} std {s['ex_std_nominal']:.3f})  "
              f"slope {s['ey_slope_cm_per_m']:+.3f} cm/m ({s['ey_angle_deg']:+.3f} deg) icpt {s['ey_intercept']:+.3f}")

plt.rcParams.update({'font.family': 'serif', 'font.serif': ['cmr10'], 'mathtext.fontset': 'cm',
                     'axes.formatter.use_mathtext': True, 'font.size': 9})
T = '0726'

# ---------------- longitudinal error vs time (window), LiDARs ----------------
LID = SENS[:2]
W = (320, 400)
fig, axs = plt.subplots(2, 1, figsize=(6.3, 3.6), sharex=True)
for ax, (k, lab, c) in zip(axs, LID):
    A = E[(T, k)]; A = A[(A.ts >= W[0]) & (A.ts <= W[1])]
    ax.scatter(A.ts, A.ex, s=3, c=c, alpha=0.45, linewidths=0, rasterized=True)
    ax.axhline(ST[T][k]['ex_mean_nominal'], color=c, lw=1.6)
    ax.axhline(0, color='k', lw=0.5, ls=':')
    ax.set_ylim(-1.5, 1.5); ax.set_ylabel(r'$e_x$ [m]'); ax.set_title(lab, fontsize=9, pad=3)
    ax.grid(alpha=0.3, lw=0.4)
axs[-1].set_xlabel('Time [s]'); axs[-1].set_xlim(*W)
fig.tight_layout(h_pad=0.6)
fig.savefig('figures/ch4/det_long_time.pdf', dpi=300, bbox_inches='tight')
fig.savefig(SCR + 'det_long.png', dpi=110, bbox_inches='tight')

# ---------------- lateral error vs x_rel, LiDARs ----------------
fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.8), sharey=True)
for ax, (k, lab, c) in zip(axs, LID):
    A = E[(T, k)]; s_ = ST[T][k]
    ax.scatter(A.g_x_rel, A.ey, s=2, c=c, alpha=0.35, linewidths=0, rasterized=True)
    xx = np.array([A.g_x_rel.min(), A.g_x_rel.max()])
    ax.plot(xx, s_['ey_intercept'] + s_['ey_slope_cm_per_m'] / 100 * xx, color='k', lw=1.3)
    ax.axhline(0, color='k', lw=0.5, ls=':'); ax.axvline(0, color='k', lw=0.5, ls=':')
    ax.set_xlim(-50, 100); ax.set_ylim(-1.5, 1.5); ax.set_title(lab, fontsize=9, pad=3)
    ax.set_xlabel(r'$x_{\mathrm{rel}}$ [m]'); ax.grid(alpha=0.3, lw=0.4)
axs[0].set_ylabel(r'$e_y$ [m]')
fig.tight_layout()
fig.savefig('figures/ch4/det_lat_xrel.pdf', dpi=300, bbox_inches='tight')
fig.savefig(SCR + 'det_lat.png', dpi=110, bbox_inches='tight')

# ---------------- camera longitudinal error vs x_rel ----------------
off = 0.0  # errors shown before the compensation of the offset
EDG = np.array([10, 20, 25, 30, 35, 40, 45, 50, 55, 60, 70, 80, 100])
ctr = lambda A: A.groupby(pd.cut(A.g_x_rel, EDG), observed=False)
fig, ax = plt.subplots(figsize=(6.3, 3.0))
ax.axvspan(*CAM_NOM, color='0.92', zorder=0)
C = E[(T, 'cam_yolo')]; C = C[C.g_x_rel > 0]
ax.scatter(C.g_x_rel, C.ex - off, s=2, c=SENS[3][2], alpha=0.3, linewidths=0, rasterized=True)
for (k, lab, c), mk in zip(SENS[:2], ['s', 's']):
    A = E[(T, k)]; A = A[A.g_x_rel > 0]; g = ctr(A)
    ax.plot(g.g_x_rel.mean(), g.ex.mean() - off, '-' + mk, color=c, ms=3.5, lw=1.2, label=lab)
g = ctr(C)
ax.errorbar(g.g_x_rel.mean(), g.ex.mean() - off, yerr=g.ex.std(), fmt='-o', color=CAM_LINE,
            ms=4, lw=1.3, capsize=2.5, label=r'Camera (mean $\pm$ std)')
ax.axhline(0, color='k', lw=0.5, ls=':')
ax.set_xlim(10, 100); ax.set_ylim(-1.0, 2.5)
ax.set_xlabel(r'$x_{\mathrm{rel}}$ [m]'); ax.set_ylabel(r'$e_x$ [m]')
ax.grid(alpha=0.3, lw=0.4); ax.legend(loc='upper right', frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig('figures/ch4/det_cam_range.pdf', dpi=300, bbox_inches='tight')
fig.savefig(SCR + 'det_cam.png', dpi=110, bbox_inches='tight')
