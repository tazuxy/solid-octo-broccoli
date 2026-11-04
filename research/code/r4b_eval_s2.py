"""Round 4b S2 evaluation at the user's 0.5-pip round-trip cost (all pairs), 2x = 1.0 pip, sensitivity 0/0.3/0.7.
Verdict variants (USDJPY): a, b, c, c2 (r4) and E1-E4 (new). Criteria (r4 S2, baseline 0.5): (1) avgR>0 in 3 periods,
(2) t>=2, (3) sumR/|maxDD|>=3, (4) (1)-(3) also at 1.0 pip. Multiple testing: Bonferroni over the 8 fix/Gotobi variants."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4b_common import *
tr = pd.read_parquet(os.path.join(OUT, 'r4b_s2_trades.parquet'))
L = []
def P(*a): s = ' '.join(str(x) for x in a); print(s); L.append(s)
pd.set_option('display.width', 260); pd.set_option('display.max_columns', 80)
def sel(pair, var, gotobi=True):
    base = {'b': 'a', 'c2': 'c'}.get(var, var); v = tr[(tr.pair == pair) & (tr['var'] == base)]
    if var in ('a', 'c'): return v
    return v[v.gotobi] if gotobi else v[~v.gotobi]
VERD = ['a', 'b', 'c', 'c2', 'E1', 'E2', 'E3', 'E4']
rows = []
for pair in ('USDJPY', 'EURJPY', 'AUDJPY'):
    for var in VERD + ['E1pre', 'E2pre', 'E3pre', 'seg_D0955_1500', 'seg_D1500_2200', 'seg_D2200_G0800']:
        for gset in ((True, False) if var not in ('a', 'c') else (True,)):
            v = sel(pair, var, gset)
            for c in COSTS:
                s = fix_stats(v, c); s.update(pair=pair, var=var, days='gotobi' if gset and var not in ('a', 'c') else ('all' if gset else 'non-gotobi'),
                                          gross_pips=v.gross_pips.mean(), sd_pips=v.gross_pips.std(), R_med=v.R_pips.median()); rows.append(s)
t = pd.DataFrame(rows); t.to_csv(os.path.join(OUT, 'r4b_s2_all.csv'), index=False)
# pass table
pt = []
for pair in ('USDJPY', 'EURJPY', 'AUDJPY'):
    for var in VERD:
        x = t[(t.pair == pair) & (t['var'] == var) & (t.days != 'non-gotobi')].set_index('cost')
        b, d = x.loc[BASE], x.loc[1.0]
        pt.append(dict(pair=pair, var=var, N=b.N, gross_pips=b.gross_pips, sd_pips=b.sd_pips, net_pips=b.avg_pips, avgR=b.avgR, t=b.t, sumR=b.sumR, maxDD=b.maxDD,
                       ratio=b.ratio, p1=b['2005-2011'], p2=b['2012-2018'], p3=b['2019-2024'], flat_days=b.flat_days,
                       avgR_2x=d.avgR, t_2x=d.t, ratio_2x=d.ratio, c1=all(b[pp] > 0 for pp, _, _ in PERIODS), c2=b.t >= 2, c3=b.ratio >= 3, c4=bool(d.ok),
                       p_one=p_one_sided(b.t)))
pt = pd.DataFrame(pt); pt['PASS'] = pt.c1 & pt.c2 & pt.c3 & pt.c4
pt['p_bonf8'] = np.minimum(1, pt.p_one * len(VERD)); pt.to_csv(os.path.join(OUT, 'r4b_s2_pass.csv'), index=False)
P('=== pass table at 0.5 pip (2x = 1.0) ==='); P(pt.round(3).to_string(index=False))
P('\n=== USDJPY cost sensitivity (verdict variants) ===')
u = t[(t.pair == 'USDJPY') & t['var'].isin(VERD) & (t.days != 'non-gotobi')]
P(u[['var','cost','avgR','t','ratio','2005-2011','2012-2018','2019-2024','ok']].round(3).to_string(index=False))
P('\n=== where does the return come from (gross pips mean, Gotobi vs non-Gotobi, all pairs) ===')
w = t[(t.cost == 0) & ~t['var'].isin(['a', 'c'])].pivot_table(index=['pair', 'var'], columns='days', values=['gross_pips', 't', 'N'])
P(w.round(2).to_string())
P('\n=== period gross pips (Gotobi) ===')
P(t[(t.cost == 0) & (t.days == 'gotobi')].set_index(['pair','var'])[['2005-2011','2012-2018','2019-2024']].mul(
    t[(t.cost == 0) & (t.days == 'gotobi')].set_index(['pair','var']).R_med, axis=0).round(2).to_string())
# weekend vs weekday holds for E1-E3 USDJPY
P('\n=== USDJPY E1-E3: G=Monday (weekend hold) vs other, gross pips / avgR@0.5 ===')
for var in ('E1', 'E2', 'E3', 'E1pre', 'E2pre'):
    v = sel('USDJPY', var)
    P(var, v.groupby('weekend').apply(lambda x: pd.Series({'N': len(x), 'g': x.gross_pips.mean(), 'r05': ((x.gross_pips - BASE) / x.R_pips).mean(),
                                                           't': tstat((x.gross_pips - BASE) / x.R_pips)})).round(3).to_dict('index'))
# yearly USDJPY at 0.5
yr = pd.DataFrame({var: sel('USDJPY', var).assign(r=lambda x: (x.gross_pips - BASE) / x.R_pips).groupby('year').r.sum() for var in VERD}).round(1)
yr.to_csv(os.path.join(OUT, 'r4b_s2_yearly_usdjpy_05.csv')); P('\n=== USDJPY yearly sumR @0.5 ==='); P(yr.to_string())
best = pt[pt.pair == 'USDJPY'].sort_values('t', ascending=False).iloc[0]
P(f'\nBonferroni (8 variants): best={best["var"]} t={best.t:.2f} p_one={best.p_one:.2e} p_bonf={best.p_bonf8:.2e}; '
  f'Bonferroni critical t (one-sided 5%/8) = 2.50; two-sided 5%/8 = 2.73')
open(os.path.join(OUT, 'r4b_s2_eval.log'), 'w').write('\n'.join(L))
