"""Round 4: cost sensitivity (reported only, not used for selection).
S1: break-even cost multiple per variant (night). S2: criteria vs absolute round-trip cost in pips for USDJPY a/b/c/c2."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4_common import *
L = []
def P(*a): s = ' '.join(str(x) for x in a); print(s); L.append(s)
s1 = pd.read_parquet(os.path.join(OUT, 'r4_s1_trades_eval.parquet'))
P('=== S1 break-even cost multiple (avg net R = 0), by window/variant and group ===')
for (w, sg, ex), v in s1.groupby(['win', 'sig', 'ex']):
    be = v.r0.mean() / (v.r0.mean() - v.r1.mean())
    beg = {g: x.r0.mean() / (x.r0.mean() - x.r1.mean()) for g, x in v.groupby('grp')}
    P(f'{w:8s} {sg}/{ex}: x{be:.2f}  design x{beg["design"]:.2f}  cross x{beg["cross"]:.2f}  gross pips {v.gross_pips.mean():.2f}  cost x1 {v.cost_pips.mean():.2f}')
s2 = pd.read_parquet(os.path.join(OUT, 'r4_s2_trades_eval.parquet')); u = s2[s2.pair == 'USDJPY']
P('\n=== S2 USDJPY: criteria vs round-trip cost (pips) ===')
rows = []
for var, v in u.groupby('var'):
    v = v.sort_values('t_ent')
    for c in (0.0, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0):
        r = (v.gross_pips - c) / v.R_pips; s = stats(pd.DataFrame({'r': r}))
        per = r.groupby(v.period).mean()
        rows.append(dict(var=var, cost_pips=c, avgR=s['avgR'], t=s['t'], sumR=s['sumR'], maxDD=s['maxDD'], ratio=s['ratio'],
                         p1=per.get('2005-2011'), p2=per.get('2012-2018'), p3=per.get('2019-2024'),
                         all_ok=bool((per > 0).all() and s['t'] >= 2 and s['ratio'] >= 3)))
t = pd.DataFrame(rows); t.to_csv(os.path.join(OUT, 'r4_s2_cost_sens.csv'), index=False); P(t.round(3).to_string(index=False))
open(os.path.join(OUT, 'r4_sens.log'), 'w').write('\n'.join(L))
