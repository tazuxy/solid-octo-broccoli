"""Round 2 figure: all candidates (none passed), 2005-2024. Left: P1-P3 pooled D+C at 8% vol (compounded equity).
Right: P4/P5 cumulative R (exit-time order). Shaded = untouched test period 2005-07..2011-12."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from r2_eval_trade import scored, load, OUT
W = pd.read_parquet(os.path.join(OUT, 'r2_port_weekly_8vol.parquet'))
COL = ['#2a78d6', '#eb6834', '#1baf7a']; INK = '#0b0b0b'; INK2 = '#52514e'; GRID = '#e5e5e3'
fig, ax = plt.subplots(1, 2, figsize=(13, 4.8))
for a in ax:
    a.axvspan(pd.Timestamp('2005-07-01'), pd.Timestamp('2012-01-01'), color='#f0efec', zorder=0)
    a.grid(color=GRID, lw=0.6); a.spines[['top', 'right']].set_visible(False)
    a.tick_params(colors=INK2); [s.set_color('#c3c2b7') for s in a.spines.values()]
lab = {'P1': 'P1 12-week reversal', 'P2': 'P2 1-week reversal', 'P3': 'P3 50/50'}
for k, c in zip(['P1', 'P2', 'P3'], COL):
    r = W[k].dropna(); eq = (1 + r).cumprod()
    ax[0].plot(eq.index, eq.values, color=c, lw=2, label=lab[k])
    ax[0].text(eq.index[-1] + pd.Timedelta(days=60), eq.values[-1], k, color=INK, fontsize=9, va='center')
ax[0].axhline(1, color='#c3c2b7', lw=1)
ax[0].set_title('Currency reversal portfolios, D+C pooled, 8% vol, net (Mon 08:00 exec)', fontsize=10, color=INK, loc='left')
ax[0].set_ylabel('Equity (start = 1.0)', color=INK2)
lab2 = {'P4': 'P4 Donchian H4 + filters', 'P5C': 'P5 divergence rule C', 'P5E': 'P5 divergence rule E'}
for k, c in zip(['P4', 'P5C', 'P5E'], COL):
    x = scored(load(k)).sort_values('exit_t')
    ax[1].plot(x.exit_t.values, x.r.cumsum().values, color=c, lw=2, label=lab2[k])
    ax[1].text(x.exit_t.values[-1] + np.timedelta64(60, 'D'), x.r.cumsum().values[-1], k, color=INK, fontsize=9, va='center')
ax[1].axhline(0, color='#c3c2b7', lw=1)
ax[1].set_title('Per-trade rules, 18 instruments, cumulative R, net', fontsize=10, color=INK, loc='left')
ax[1].set_ylabel('Cumulative R', color=INK2)
for a in ax:
    a.legend(frameon=False, loc='upper left', fontsize=9)
    a.text(pd.Timestamp('2005-09-01'), a.get_ylim()[0], ' untouched test 2005-07..2011-12', color=INK2, fontsize=8, va='bottom')
fig.suptitle('Round 2: no candidate passed (shaded = one-shot test period)', fontsize=11, color=INK, x=0.01, ha='left')
fig.tight_layout(); fig.savefig(os.path.join(OUT, 'r2_equity_all.png'), dpi=120, facecolor='#fcfcfb')
print('saved')
