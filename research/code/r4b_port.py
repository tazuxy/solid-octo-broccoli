"""Round 4b portfolio sim (USDJPY Gotobi-eve rule), cost 0.5 pip, compounding, one trade at a time (trades never overlap).
  main  : E2 no stop, 0.5% of equity per 1R (R = 0.25 x D1 ATR14)  -> loss can exceed 0.5% (no stop)
  stop  : E2 with SL = 2R, 0.5% of equity at the stop (1R = 0.25%)
  E1    : E1 no stop, 0.5% per 1R (alternative)
Monte Carlo: 10,000 iid bootstrap resamples of the trade R series (same N) -> maxDD % distribution. Swap not modelled."""
import os, sys, numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4b_common import *
L = []
def P(*a): s = ' '.join(str(x) for x in a); print(s); L.append(s)
pd.set_option('display.width', 220)
tr = pd.read_parquet(os.path.join(OUT, 'r4b_rules_trades.parquet'))
SIMS = {'main E2 no stop': ('E2', 'r_nostop', 0.005), 'E2 stop 2R': ('E2', 'r_stop', 0.0025), 'E1 no stop': ('E1', 'r_nostop', 0.005)}
def dd_pct(eq):
    pk = np.maximum.accumulate(np.concatenate([[1.0], eq])); return float((np.concatenate([[1.0], eq]) / pk - 1).min())
rng = np.random.default_rng(20261104); res = {}; summ = []; ytab = {}
for name, (var, col, f) in SIMS.items():
    v = tr[tr['var'] == var].sort_values('t_exit').reset_index(drop=True)
    ret = f * v[col].values; eq = np.cumprod(1 + ret); v['eq'] = eq; res[name] = v
    yrs = (v.t_exit.iloc[-1] - v.t_ent.iloc[0]).days / 365.25
    flat = longest_flat_days(v.t_exit, np.log1p(ret))
    mc = np.array([dd_pct(np.cumprod(1 + rng.choice(ret, len(ret), replace=True))) for _ in range(10000)])
    s = dict(sim=name, N=len(v), final=eq[-1], CAGR=eq[-1] ** (1 / yrs) - 1, maxDD=dd_pct(eq), worst_trade=ret.min(), best_trade=ret.max(),
             flat_days=flat, MC_DD_med=np.median(mc), MC_DD_p95=np.quantile(mc, 0.05), MC_DD_p99=np.quantile(mc, 0.01),
             pos_years=None, sd_trade=ret.std())
    y = v.groupby(v.t_exit.dt.year).apply(lambda x: pd.Series({'N': len(x), 'ret_pct': 100 * (np.prod(1 + f * x[col].values) - 1),
                                                               'maxDD_pct': 100 * dd_pct(np.cumprod(1 + f * x[col].values))}))
    s['pos_years'] = int((y.ret_pct > 0).sum()); summ.append(s); ytab[name] = y.ret_pct
    y.round(2).to_csv(os.path.join(OUT, f'r4b_port_yearly_{name.split()[0]}_{name.split()[1]}_{name.split()[-1]}.csv'))
    P(f'\n=== {name}: yearly ==='); P(y.round(2).to_string())
S_ = pd.DataFrame(summ); S_.to_csv(os.path.join(OUT, 'r4b_port_summary.csv'), index=False)
P('\n=== summary (fractions; MC_DD_p95 = 5% worst bootstrap maxDD) ==='); P(S_.round(4).to_string(index=False))
# yearly side-by-side for the report
yy = pd.DataFrame(ytab).round(2)
yy.to_csv(os.path.join(OUT, 'r4b_port_yearly.csv')); P(yy.to_string())
# chart
fig, ax = plt.subplots(figsize=(10, 5.2), dpi=130); fig.patch.set_facecolor('#fcfcfb'); ax.set_facecolor('#fcfcfb')
cols = {'main E2 no stop': '#2a78d6', 'E2 stop 2R': '#eb6834', 'E1 no stop': '#9a9994'}
lab = {'main E2 no stop': 'E2 (22:00 JST buy, no stop, 0.5%/R)', 'E2 stop 2R': 'E2 with 2R stop (0.5% at stop)', 'E1 no stop': 'E1 (15:00 JST buy, no stop, 0.5%/R)'}
for k, v in res.items():
    ax.plot(v.t_exit, 100 * v['eq'], color=cols[k], lw=2 if k.startswith('main') else 1.4, label=lab[k])
    ax.annotate(f'{100*v['eq'].iloc[-1]:.0f}', (v.t_exit.iloc[-1], 100 * v['eq'].iloc[-1]), xytext=(4, 0), textcoords='offset points',
                va='center', fontsize=9, color='#52514e')
ax.axhline(100, color='#c3c2b7', lw=0.8)
for s in ('top', 'right'): ax.spines[s].set_visible(False)
for s in ('left', 'bottom'): ax.spines[s].set_color('#c3c2b7')
ax.tick_params(colors='#52514e'); ax.grid(axis='y', color='#ecebe8', lw=0.8)
ax.set_ylabel('Equity (start = 100)', color='#52514e')
ax.set_title('USDJPY Gotobi-eve long, cost 0.5 pip round trip, swap not included, 2005-2024', loc='left', fontsize=11, color='#0b0b0b')
ax.legend(frameon=False, loc='upper left', fontsize=9, labelcolor='#0b0b0b')
fig.tight_layout(); fig.savefig(os.path.join(OUT, 'r4b_equity.png'), facecolor=fig.get_facecolor())
open(os.path.join(OUT, 'r4b_port.log'), 'w').write('\n'.join(L))
