"""Equity curves (net, scaled ex post to 8% annual vol) of all round-1 variants -> out/r1_equity_all.png.
(No variant passed, so the pass-only file r1_equity.png is not produced.)"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_common import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
rd = lambda f: pd.read_parquet(os.path.join(OUT, f))
def pooled(d, c): return pd.concat([scale_to(d), scale_to(c)], axis=1).fillna(0.0).mean(axis=1)
S = {'H1': {'H1a 12w momentum': pooled(rd('r1_h1a_D_c1.0.parquet').net, rd('r1_h1a_C_c1.0.parquet').net),
            'H1b 1w reversal': pooled(rd('r1_h1b_D_c1.0.parquet').net, rd('r1_h1b_C_c1.0.parquet').net)},
     'H2': {'H2a TSMOM 18': rd('r1_h2a_ALL_c1.0.parquet').net, 'H2b TSMOM ex JPY-x/XAU': rd('r1_h2b_ALL_c1.0.parquet').net},
     'H3': {'H3a both halves': pooled(rd('r1_h3a_D_c1.0.parquet').net, rd('r1_h3a_C_c1.0.parquet').net),
            'H3b-W western half': pooled(rd('r1_h3bW_D_c1.0.parquet').net, rd('r1_h3bW_C_c1.0.parquet').net),
            'H3b-E eastern half': pooled(rd('r1_h3bE_D_c1.0.parquet').net, rd('r1_h3bE_C_c1.0.parquet').net)}}
COL = ['#2a78d6', '#eb6834', '#1baf7a']
plt.rcParams.update({'font.size': 9, 'axes.edgecolor': '#c3c2b7', 'axes.labelcolor': '#52514e', 'xtick.color': '#52514e', 'ytick.color': '#52514e'})
fig, axs = plt.subplots(3, 1, figsize=(11, 9), sharex=True, facecolor='#fcfcfb')
for ax, (h, d) in zip(axs, S.items()):
    ax.set_facecolor('#fcfcfb'); ax.grid(axis='y', color='#e6e5e0', lw=0.6); ax.axhline(1, color='#8a8984', lw=0.8)
    for k, (n, r) in enumerate(d.items()):
        eq = (1 + scale_to(r)).cumprod(); ax.plot(eq.index, eq.values, color=COL[k], lw=2, label=n)
        ax.annotate(f'{eq.iloc[-1]:.2f}', (eq.index[-1], eq.iloc[-1]), xytext=(4, 9 * (k - 1)), textcoords='offset points', fontsize=8, color='#0b0b0b', va='center')
    ax.axvline(IS_END, color='#8a8984', lw=0.8, ls='--')
    ax.set_title(f'{h}: net equity, scaled to 8% annual vol (dashed line = IS/OOS split 2019-01-01)', loc='left', fontsize=9, color='#0b0b0b')
    ax.legend(frameon=False, loc='upper left', bbox_to_anchor=(1.04, 1), fontsize=8); ax.set_ylabel('equity (start = 1)')
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(OUT, 'r1_equity_all.png'), dpi=130, facecolor='#fcfcfb')
