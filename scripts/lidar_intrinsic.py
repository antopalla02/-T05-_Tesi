"""Intrinsic errors of the LiDAR pipelines (Section 4.4), sessions kept separate.

Errors in the ego frame, e = p_det - p_gt, ground truth interpolated at the acquisition
time, detections within 5 m from the ground truth (one per message). The deterministic
components of Section 4.3 are removed per session and per pipeline: the mean longitudinal
error over the whole session and the least squares line of the lateral error.
Binned statistics (10 m in x_rel) are shown as mean +- standard deviation.
"""
import numpy as np, pandas as pd, json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

U = 'data/'
SES = [('0726', '20260726_ontrack_TUM_', '07/26_TUM'),
       ('0803', '202600803_ontrack_KINETIZ_', '08/03_Kinetiz')]
SENS = [('lid_clust', 'LiDAR Clustering', 'lidar_clustering_errors', ['#8fd18f', '#1f7a1f']),
        ('lid_pp', 'LiDAR PointPillars', 'lidar_pointpillars_errors', ['#ffbb78', '#b3540a'])]
GATE, NMIN = 5.0, 30
EDGES = np.array([-60, -50, -40, -30, -20, -10, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
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
    A = L[L.e < GATE].sort_values('e').drop_duplicates('msg').copy()
    A['ex0'] = A.ex - A.ex.mean()                                    # longitudinal offset
    A['ey0'] = A.ey - np.polyval(np.polyfit(A.g_x_rel, A.ey, 1), A.g_x_rel)  # lateral trend
    return A


plt.rcParams.update({'font.family': 'serif', 'font.serif': ['cmr10'], 'mathtext.fontset': 'cm',
                     'axes.formatter.use_mathtext': True, 'font.size': 9})
OUT = {'edges': EDGES.tolist()}
for k, name, fname, cols in SENS:
    fig, axs = plt.subplots(2, 1, figsize=(6.3, 4.6), sharex=True)
    OUT[k] = {}
    for j, (t, p, lab) in enumerate(SES):
        A = errors(p, k); c = cols[j]
        if k == 'lid_clust':   # blind spot behind the ego vehicle: coverage limit, not noise
            A = A[~((A.g_x_rel < 0) & (A.g_y_rel.abs() < 2.0))]
        g = A.groupby(pd.cut(A.g_x_rel, EDGES), observed=False)
        n = g.size().values; ctr = np.array([i.mid for i in g.size().index])
        ok = (n >= NMIN) & (np.abs(ctr) > 10)
        OUT[k][t] = {q: {'mean': g[q].mean().round(3).tolist(), 'std': g[q].std().round(3).tolist()}
                     for q in ['ex0', 'ey0']}
        OUT[k][t]['n'] = n.tolist(); OUT[k][t]['offset'] = float(A.ex.mean())
        for ax, q in zip(axs, ['ex0', 'ey0']):
            ax.scatter(A.g_x_rel, A[q], s=2, c=c, alpha=0.25, linewidths=0, rasterized=True)
            dx = -0.8 if j == 0 else 0.8
            mu, sd = g[q].mean().values, g[q].std().values
            for side in [ctr < 0, ctr > 0]:                  # do not connect behind and ahead
                m = ok & side
                ax.errorbar(ctr[m] + dx, mu[m], yerr=sd[m], fmt='-o', color=c, mec='k', mew=0.4,
                            ms=3.5, lw=1.3, capsize=2.5,
                            label=('Session ' + lab.replace('_', r'$\_$')) if side[-1] else None)
    for ax, q in zip(axs, [r'$e_x$ [m]', r'$e_y$ [m]']):
        ax.axhline(0, color='k', lw=0.5, ls=':'); ax.axvline(0, color='k', lw=0.6)
        ax.set_xlim(-60, 100); ax.set_ylim(-1.5, 1.5); ax.set_ylabel(q); ax.grid(alpha=0.3, lw=0.4)
    axs[0].set_title('Longitudinal error', fontsize=9, pad=3)
    axs[1].set_title('Lateral error', fontsize=9, pad=3)
    axs[0].legend(loc='upper right', frameon=False, fontsize=8)
    axs[1].set_xlabel(r'$x_{\mathrm{rel}}$ [m]')
    fig.tight_layout(h_pad=0.6)
    fig.savefig(f'figures/ch4/{fname}.pdf', dpi=300, bbox_inches='tight')
    fig.savefig(SCR + fname + '.png', dpi=110, bbox_inches='tight')
json.dump(OUT, open('scripts/lidar_intrinsic.json', 'w'), indent=1)
