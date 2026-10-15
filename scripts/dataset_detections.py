"""Detection rate of each sensor versus range, opponent ahead vs behind (Section 4.2).

Detections are associated with the opponent if within 5 m from the ground truth,
interpolated at the acquisition time; at most one detection per message is kept.
The rate in each range bin is the number of associated detections divided by the
time spent by the opponent in that bin. The two sessions are merged.
"""
import numpy as np, pandas as pd, json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

U = 'data/'
SES = {'0726': '20260726_ontrack_TUM_', '0803': '202600803_ontrack_KINETIZ_'}
SENS = [('lid_clust', 'LiDAR Clustering', '#2ca02c'),
        ('lid_pp', 'LiDAR PointPillars', '#ff7f0e'),
        ('rad_clust', 'RaDAR', '#4fa8e0')]
GATE = 5.0
BINS = np.arange(0, 160, 10)
MIN_T = 5.0  # [s] minimum time in a bin to show the rate


def load_det(f):
    d = pd.read_csv(f); d = d[d['count'] > 0]; rows = []
    for i in range(1, 16):
        if f'sens_stamp_{i}' not in d: break
        rows.append(pd.DataFrame({'ts': d[f'sens_stamp_{i}'], 'x': d[f'x_rel_{i}'],
                                  'y': d[f'y_rel_{i}'], 'msg': d.index}))
    return pd.concat(rows).dropna(subset=['x', 'ts'])


OUT = {}
for k, lab, c in SENS:
    T = np.zeros((2, len(BINS) - 1)); N = np.zeros((2, len(BINS) - 1))
    for tag, p in SES.items():
        R = pd.read_csv(U + p + 'gt.csv').sort_values('stamp').dropna(subset=['x_rel'])
        L = load_det(U + p + k + '.csv')
        Rs = R[(R.stamp >= L.ts.min()) & (R.stamp <= L.ts.max())]
        rho = np.hypot(Rs.x_rel, Rs.y_rel)
        for j, m in enumerate([Rs.x_rel > 0, Rs.x_rel <= 0]):
            T[j] += np.histogram(rho[m], BINS)[0] / 100.0  # GT at 100 Hz
        gt = R.stamp.values
        L = L[(L.ts >= gt.min()) & (L.ts <= gt.max())].copy()
        for q in ['x_rel', 'y_rel']:
            L['g_' + q] = np.interp(L.ts, gt, R[q].values)
        L['e'] = np.hypot(L.x - L.g_x_rel, L.y - L.g_y_rel)
        A = L[L.e < GATE].sort_values('e').drop_duplicates('msg')
        r = np.hypot(A.g_x_rel, A.g_y_rel)
        for j, m in enumerate([A.g_x_rel > 0, A.g_x_rel <= 0]):
            N[j] += np.histogram(r[m], BINS)[0]
    rate = np.where(T >= MIN_T, N / np.maximum(T, 1e-9), np.nan)
    OUT[k] = {'bins': BINS.tolist(), 'ahead_hz': np.round(rate[0], 2).tolist(),
              'behind_hz': np.round(rate[1], 2).tolist()}
json.dump(OUT, open('scripts/dataset_detections.json', 'w'), indent=1)

plt.rcParams.update({'font.family': 'serif', 'font.serif': ['cmr10'], 'mathtext.fontset': 'cm',
                     'axes.formatter.use_mathtext': True, 'font.size': 9})
ctr = 0.5 * (BINS[:-1] + BINS[1:])
fig, axs = plt.subplots(1, 3, figsize=(6.3, 2.4), sharey=True)
for ax, (k, lab, c) in zip(axs, SENS):
    ax.plot(ctr, OUT[k]['ahead_hz'], '-o', color=c, ms=3, lw=1.3, label='Opponent ahead')
    ax.plot(ctr, OUT[k]['behind_hz'], '--s', color=c, ms=3, lw=1.3, mfc='white', label='Opponent behind')
    ax.set_title(lab, fontsize=9); ax.set_xlim(0, 150); ax.set_ylim(0, 15)
    ax.set_xlabel(r'Range $\rho$ [m]'); ax.grid(alpha=0.3, lw=0.4)
axs[0].set_ylabel('Detection rate [Hz]')
h = [plt.Line2D([], [], color='k', ls='-', marker='o', ms=3, label='Opponent ahead'),
     plt.Line2D([], [], color='k', ls='--', marker='s', ms=3, mfc='white', label='Opponent behind')]
fig.legend(handles=h, loc='lower center', ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.02))
fig.tight_layout(rect=(0, 0.08, 1, 0.94))
fig.suptitle('Sessions 07/26_TUM and 08/03_Kinetiz', fontsize=9, y=0.975)
fig.savefig('figures/ch4/detection_rate_range.pdf', bbox_inches='tight')
fig.savefig('/tmp/claude-0/-home-claude--t05--tesi/fe9c22f3-a0f7-524e-88e2-f943c23ad6f5/scratchpad/diag/rate.png',
            dpi=130, bbox_inches='tight')
