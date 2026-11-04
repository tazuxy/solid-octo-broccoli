"""Round 4b step 4 for the passing Gotobi variant(s) (USDJPY, cost 0.5 pip).
Carried forward: E2 (highest t among passing variants; shorter hold than E1). E1 shown alongside.
'When not to trade' checks (adopt only if per-period maxDD_R improves in ALL 3 periods and no period avgR turns <= 0):
  F1 risk-off: skip if USDJPY 5-day move < -2% (last closed D1 close vs close 5 D1 bars earlier, known at entry).
  F2 BoJ/FOMC weeks: NOT tested - dates 2005-2024 cannot be listed reliably from memory.
  F3 JP year-end / Golden Week: skip if G (JST) in Dec 29-Jan 3 or Apr 29-May 5.
  F4 weekend hold (G = Monday): POST-HOC (seen in the weekend split before this check) -> reported, never adopted.
Stop test (proposed before looking): SL = 2R (= 0.5 x D1 ATR) below entry, bid M5 lows from entry bar to the bar before exit;
a bar opening below SL fills at its open. Output r4b_rules_trades.parquet (r_nostop, r_stop at 0.5 pip)."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4b_common import *
L = []
def P(*a): s = ' '.join(str(x) for x in a); print(s); L.append(s)
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40)
tr = pd.read_parquet(os.path.join(OUT, 'r4b_s2_trades.parquet'))
b = pd.read_parquet(os.path.join(ROOT, 'bars_m5', 'USDJPY_M5.parquet')); bt_ = b.index.values; lo = b.low.values; op = b.open.values
d1 = pd.read_parquet(os.path.join(ROOT, 'bars_full', 'USDJPY_D1.parquet'))
d1c = pd.DataFrame({'close_time': d1.index + pd.Timedelta('1D'), 'mv5': d1.close / d1.close.shift(5) - 1}).sort_values('close_time')
out = []
for var in ('E1', 'E2'):
    v = tr[(tr.pair == 'USDJPY') & (tr['var'] == var) & tr.gotobi].sort_values('t_ent').reset_index(drop=True)
    v['mv5'] = pd.merge_asof(v[['t_ent']], d1c, left_on='t_ent', right_on='close_time', direction='backward').mv5.values
    md = v.G.dt.month * 100 + v.G.dt.day
    v['F1'] = v.mv5 < -0.02; v['F3'] = (md >= 1229) | (md <= 103) | ((md >= 429) & (md <= 505)); v['F4'] = v.G_dow == 0
    # stop path
    sl_hit = []; px = []
    for ti, tx, e, R in zip(v.t_ent.values, v.t_exit.values, v.entry.values, v.R_pips.values):
        i0, i1 = np.searchsorted(bt_, ti), np.searchsorted(bt_, tx); sl = e - 2 * R * PIP['USDJPY']; hit = None
        for j in range(i0, i1):
            if j > i0 and op[j] <= sl: hit = op[j]; break
            if lo[j] <= sl: hit = sl; break
        sl_hit.append(hit is not None); px.append(hit if hit is not None else np.nan)
    v['sl_hit'] = sl_hit; v['stop_px'] = px
    v['gross_stop'] = np.where(v.sl_hit, (v.stop_px - v.entry) / PIP['USDJPY'], v.gross_pips)
    v['r_nostop'] = (v.gross_pips - BASE) / v.R_pips; v['r_stop'] = (v.gross_stop - BASE) / v.R_pips
    v['period'] = period_of(v.year.values); out.append(v)
    def summ(x, col='r_nostop'):
        d = dict(N=len(x), avgR=x[col].mean(), t=tstat(x[col]), sumR=x[col].sum(), maxDD=maxdd(x[col].values))
        d['ratio'] = d['sumR'] / abs(d['maxDD'])
        for pp, _, _ in PERIODS:
            y = x[x.period == pp]; d[f'avg_{pp}'] = y[col].mean(); d[f'dd_{pp}'] = maxdd(y[col].values)
        return d
    rows = [dict(rule='base', **summ(v))]
    for f in ('F1', 'F3', 'F4'): rows.append(dict(rule=f'skip {f}', skipped=int(v[f].sum()), **summ(v[~v[f]])))
    t = pd.DataFrame(rows); base = t.iloc[0]
    t['adopt'] = [False] + [bool(all(r[f'dd_{pp}'] > base[f'dd_{pp}'] for pp, _, _ in PERIODS) and all(r[f'avg_{pp}'] > 0 for pp, _, _ in PERIODS)) for _, r in t.iloc[1:].iterrows()]
    t.loc[t.rule == 'skip F4', 'adopt'] = False   # post-hoc, never adopted
    P(f'\n=== {var}: filter checks (R at 0.5 pip, no stop) ==='); P(t.round(3).to_string(index=False))
    P(f'{var} stop 2R: hit share {v.sl_hit.mean():.3f}; no-stop', {k: round(x, 3) for k, x in summ(v).items()})
    P(f'{var} stop 2R:            ', {k: round(x, 3) for k, x in summ(v, 'r_stop').items()})
    P(f'{var} stop 2R in units of stop risk (r_stop/2): avg {v.r_stop.mean()/2:.3f}  maxDD {maxdd(v.r_stop.values/2):.2f}')
    P(f'{var} 5-day move stats: share < -2% = {v.F1.mean():.3f}; F3 share {v.F3.mean():.3f}; F4 share {v.F4.mean():.3f}')
    t.to_csv(os.path.join(OUT, f'r4b_filters_{var}.csv'), index=False)
pd.concat(out).to_parquet(os.path.join(OUT, 'r4b_rules_trades.parquet'))
open(os.path.join(OUT, 'r4b_rules.log'), 'w').write('\n'.join(L))
