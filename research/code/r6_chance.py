"""Round 6 step 6 (report only): how unusual is the month-end exclusion vs a random exclusion of the same size?
Random-exclusion test (10,000 draws) in each period + Welch t of excluded vs kept; also the gross split of month-end trades."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r6_common import *
allt = pd.read_parquet(os.path.join(OUT, 'r6_trades_all.parquet')); g = allt[allt.gotobi].sort_values('t_ent').reset_index(drop=True)
rng = np.random.default_rng(7); L = []
def P(*a): s = ' '.join(str(x) for x in a); print(s); L.append(s)
for per in ('SEL', 'VAL', 'ALL'):
    x = g if per == 'ALL' else g[g.period == per].reset_index(drop=True); ex = (x.DOW2a == 'month_end').values; n = ex.sum(); v = x.net.values
    base = pstats(v)['ratio']; real = pstats(v[~ex])['ratio'] - base; real_m = v[ex].mean()
    dr, dm = [], []
    for _ in range(10000):
        m = np.zeros(len(v), bool); m[rng.choice(len(v), n, replace=False)] = True
        dr.append(pstats(v[~m])['ratio'] - base); dm.append(v[m].mean())
    a, b = v[ex], v[~ex]; wt = (b.mean() - a.mean()) / np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    P(f'{per}: N_ex={n} ex_mean={real_m:.2f} kept_mean={b.mean():.2f} Welch t(kept-ex)={wt:.2f} | d_ratio real={real:.2f}, '
      f'share of random exclusions with d_ratio>=real: {np.mean(np.array(dr) >= real):.4f}; with ex_mean<=real: {np.mean(np.array(dm) <= real_m):.4f}')
# 7 Gotobi types: chance that the worst type in SEL is also the worst/negative in VAL is not computed (1 observation)
open(os.path.join(OUT, 'r6_chance.log'), 'w').write('\n'.join(L))
