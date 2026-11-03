"""H-A evaluation against the pre-registered criteria (weekly net returns).
Scaling: each weekly series is scaled ex post to 8% annual vol over 2011-10..2024-12 (scale_to). 'unscaled' = gross-1 basket.
A+B combined = mean of the two 8%-scaled groups, rescaled to 8%. Criterion (3) judged on A+B combined (as (2)); groups shown."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r3_common import *
W = pd.read_parquet(os.path.join(OUT, 'r3_ha_weekly.parquet'))
def ann(r): return r.mean() * 52
def stats(r):
    r = r.dropna(); cm = curve_metrics(r)
    return dict(ann=ann(r), vol=r.std() * np.sqrt(52), sharpe=sharpe(r), t=tstat(r), cum=cm['cum'], maxdd=cm['maxdd'],
                ret_dd=cm['ret_dd'], flat_m=cm['flat_m'])
def combo(v, cm):
    a = scale_to(W[f'A_{v}_c{cm}']); b = scale_to(W[f'B_{v}_c{cm}'])
    return scale_to((a + b) / 2)
rows = []; out = {}
for v in ('a', 'b', 'bh'):
    for cm in (1.0, 1.5, 2.0):
        for g in ('A', 'B', 'AB'):
            if g == 'AB': r8 = combo(v, cm); ru = None
            else: ru = W[f'{g}_{v}_c{cm}'].dropna(); r8 = scale_to(ru)
            st = stats(r8); out[(v, cm, g)] = r8
            d = dict(variant=v, cost=cm, group=g, **{k + '_8v': x for k, x in st.items()})
            d['IS_ann_8v'] = ann(r8[r8.index < IS_END]); d['OOS_ann_8v'] = ann(r8[r8.index >= IS_END])
            if ru is not None:
                su = stats(ru); d.update(ann_unscaled=su['ann'], vol_unscaled=su['vol'], maxdd_unscaled=su['maxdd'],
                                         IS_ann_unscaled=ann(ru[ru.index < IS_END]), OOS_ann_unscaled=ann(ru[ru.index >= IS_END]))
            rows.append(d)
T = pd.DataFrame(rows); T.to_csv(os.path.join(OUT, 'r3_ha_stats.csv'), index=False)
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
print(T.round(3).to_string(index=False))
# criteria
crit = []
for v in ('a', 'b'):
    def c13(cm):
        s = T.set_index(['variant', 'cost', 'group'])
        c1 = all(s.loc[(v, cm, g), f'{p}_ann_8v'] > 0 for g in ('A', 'B') for p in ('IS', 'OOS'))
        cells = {f'{g}_{p}': round(s.loc[(v, cm, g), f'{p}_ann_8v'] * 100, 2) for g in ('A', 'B') for p in ('IS', 'OOS')}
        t = s.loc[(v, cm, 'AB'), 't_8v']; rd = s.loc[(v, cm, 'AB'), 'ret_dd_8v']
        return c1, cells, t, rd
    c1, cells, t, rd = c13(1.0)
    s = T.set_index(['variant', 'cost', 'group'])
    c4 = {g: (s.loc[(v, 1.0, g), 'sharpe_8v'], s.loc[('bh', 1.0, g), 'sharpe_8v'], s.loc[(v, 1.0, g), 'maxdd_8v'], s.loc[('bh', 1.0, g), 'maxdd_8v']) for g in ('A', 'B')}
    p4 = all(x[0] > x[1] and x[2] > x[3] for x in c4.values())
    c1x, cellsx, tx, rdx = c13(2.0)
    p5 = c1x and tx >= 2 and rdx >= 3
    crit.append(dict(variant=v, c1=c1, cells=cells, c2_t=t, c2=t >= 2, c3_retdd=rd, c3=rd >= 3, c4=p4, c4_detail=c4,
                     c5=p5, c5_detail=(cellsx, tx, rdx), PASS=c1 and t >= 2 and rd >= 3 and p4 and p5))
for c in crit: print(c)
pd.DataFrame(crit).to_csv(os.path.join(OUT, 'r3_ha_criteria.csv'), index=False)
# yearly (8% vol, cost x1)
Y = pd.DataFrame({f'{v}_{g}': yearly(out[(v, 1.0, g)]) for v in ('a', 'b', 'bh') for g in ('A', 'B', 'AB')})
Y.to_csv(os.path.join(OUT, 'r3_ha_yearly.csv')); print((Y * 100).round(1).to_string())
# per-pair contribution (unscaled, ann., cost x1)
for v in ('a', 'b', 'bh'):
    for g in ('A', 'B'):
        c = pd.read_parquet(os.path.join(OUT, f'r3_ha_contrib_{g}_{v}.parquet'))
        print(v, g, 'per-pair ann. contrib (unscaled, %):', {p: round(c[p].mean() * 252 * 100, 2) for p in c.columns},
              ' IS:', {p: round(c[p][c.index < IS_END].mean() * 252 * 100, 2) for p in c.columns},
              ' OOS:', {p: round(c[p][c.index >= IS_END].mean() * 252 * 100, 2) for p in c.columns})
