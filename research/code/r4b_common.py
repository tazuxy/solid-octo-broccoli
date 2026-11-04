"""Round 4b shared helpers. User assumption: round-trip cost = 0.5 pip for EVERY FX pair (bid-only data:
buy at ask = bid + spread, exit at bid -> net = gross - spread for both directions). Re-uses r4_common metrics."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4_common import *          # ROOT, OUT, PIP, PERIODS, period_of, tstat, maxdd, longest_flat_days, stats
from math import erf, sqrt
BASE = 0.5                       # user's spread assumption (pips, round trip)
COSTS = (0.0, 0.3, 0.5, 0.7, 1.0)   # 1.0 = 2x baseline

def p_one_sided(t):
    return 0.5 * (1 - erf(t / sqrt(2))) if np.isfinite(t) else np.nan

def fix_stats(v, cost, rcol_pips='gross_pips', R='R_pips'):
    """Stats for a fix/Gotobi family trade list at an absolute round-trip cost (pips). Criteria as r4 S2."""
    v = v.sort_values('t_ent'); r = (v[rcol_pips] - cost) / v[R]
    s = stats(pd.DataFrame({'r': r.values})); per = r.groupby(period_of(v.year.values)).mean()   # year = JST date year (as r4)
    out = dict(cost=cost, N=len(v), avg_pips=(v[rcol_pips] - cost).mean(), avgR=s['avgR'], t=s['t'], sumR=s['sumR'], maxDD=s['maxDD'],
               ratio=s['ratio'], win=s['win'])
    for pp, _, _ in PERIODS: out[pp] = per.get(pp, np.nan)
    out['ok'] = bool(all(out[pp] > 0 for pp, _, _ in PERIODS) and s['t'] >= 2.0 and s['ratio'] >= 3)
    out['flat_days'] = longest_flat_days(v.t_ent, r.values)
    return out
