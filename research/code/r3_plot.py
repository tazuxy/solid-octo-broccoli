"""Diagnostic equity chart (no variant passed): H-A A+B at 8% vol (a, b, buy&hold) and H-B cumulative net R (a, b)."""
import os, sys, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r3_common import *
W = pd.read_parquet(os.path.join(OUT, 'r3_ha_weekly.parquet'))
C1, C2, GR, INK, INK2 = '#2a78d6', '#eb6834', '#8a8984', '#0b0b0b', '#52514e'
plt.rcParams.update({'font.size': 9, 'axes.edgecolor': '#d6d5d0', 'axes.labelcolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2})
fig, ax = plt.subplots(1, 2, figsize=(12, 4.2), dpi=130)
for v, col, lab in (('a', C1, 'H-A a: SPX > SMA200'), ('b', C2, 'H-A b: + low SPX vol'), ('bh', GR, 'Buy & hold (benchmark)')):
    r = scale_to((scale_to(W[f'A_{v}_c1.0']) + scale_to(W[f'B_{v}_c1.0'])) / 2); eq = (1 + r).cumprod()
    ax[0].plot(eq.index, (eq - 1) * 100, color=col, lw=2 if v != 'bh' else 1.6, ls='-' if v != 'bh' else '--', label=lab)
ax[0].set_title('H-A: groups A+B, net, scaled to 8% vol (cumulative %)', loc='left', color=INK)
for v, col, lab in (('a', C1, 'H-B a: last day 08:00 -> fix'), ('b', C2, 'H-B b: T-2 08:00 -> fix')):
    tr = pd.read_parquet(os.path.join(OUT, f'r3_hb_trades_{v}_c1.0.parquet')); c = tr.groupby('T').R.sum().cumsum()
    ax[1].plot(c.index, c.values, color=col, lw=2, label=lab)
ax[1].set_title('H-B: 4 pairs pooled, cumulative net R', loc='left', color=INK)
for a in ax:
    a.axhline(0, color='#bdbcb6', lw=0.8); a.axvline(IS_END, color='#bdbcb6', lw=0.8, ls=':')
    a.text(IS_END, a.get_ylim()[1], ' OOS ->', va='top', color=INK2, fontsize=8)
    a.grid(axis='y', color='#ecebe7', lw=0.6); a.spines[['top', 'right']].set_visible(False); a.legend(frameon=False, fontsize=8, loc='lower left')
fig.tight_layout(); fig.savefig(os.path.join(OUT, 'r3_diag_equity.png')); print('ok')
