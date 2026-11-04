"""Round 4 S2 evaluation: costs x0/x1(baseline)/x1.5/x2, periods, pass table, yearly, weekday, cross-check pairs."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4_common import *
tr = pd.read_parquet(os.path.join(OUT, 'r4_s2_trades.parquet'))
tr['cost'] = tr.pair.map(COST_PIPS); tr['year'] = tr.jst_date.dt.year; tr['period'] = period_of(tr.year)
MS = {'x0': 0, 'x1': 1, 'x1.5': 1.5, 'x2': 2}
for k, m in MS.items():
    tr[f'p_{k}'] = tr.gross_pips - m * tr.cost; tr[f'r_{k}'] = tr[f'p_{k}'] / tr.R_pips
tr.to_parquet(os.path.join(OUT, 'r4_s2_trades_eval.parquet'))
L = []
def P(*a): s = ' '.join(str(x) for x in a); print(s); L.append(s)
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 60)
rows = []
for (pair, var), v in tr.groupby(['pair', 'var']):
    v = v.sort_values('t_ent'); row = dict(pair=pair, var=var, N=len(v), gross_pips=v.gross_pips.mean(), R_pips_med=v.R_pips.median())
    for k in MS:
        s = stats(v, f'r_{k}'); row.update({f'avgR_{k}': s['avgR'], f't_{k}': s['t'], f'sumR_{k}': s['sumR'], f'maxDD_{k}': s['maxDD'], f'ratio_{k}': s['ratio']})
        row[f'avgpips_{k}'] = v[f'p_{k}'].mean()
        per = v.groupby('period')[f'r_{k}'].mean()
        for pp, x in per.items(): row[f'per_{pp}_{k}'] = x
        row[f'ok_{k}'] = bool((per > 0).all() and len(per) == 3 and s['t'] >= 2.0 and s['ratio'] >= 3)
    row['flat_days_x1'] = longest_flat_days(v.t_ent, v.r_x1)
    row['c1_periods'] = bool(all(row[f'per_{pp}_x1'] > 0 for pp, _, _ in PERIODS)); row['c2_t2'] = bool(row['t_x1'] >= 2)
    row['c3_ratio3'] = bool(row['ratio_x1'] >= 3); row['c4_x2'] = row['ok_x2']
    row['PASS'] = row['c1_periods'] and row['c2_t2'] and row['c3_ratio3'] and row['c4_x2']
    rows.append(row)
pr = pd.DataFrame(rows); pr.to_csv(os.path.join(OUT, 'r4_s2_pass.csv'), index=False)
P('=== S2 summary ===')
P(pr[['pair','var','N','gross_pips','R_pips_med','avgpips_x1','avgR_x0','avgR_x1','avgR_x1.5','avgR_x2','t_x0','t_x1','t_x2','sumR_x1','maxDD_x1','ratio_x1','flat_days_x1']].round(3).to_string(index=False))
P(pr[['pair','var'] + [f'per_{pp}_{k}' for k in ('x0','x1','x2') for pp,_,_ in PERIODS] + ['c1_periods','c2_t2','c3_ratio3','c4_x2','PASS']].round(3).to_string(index=False))
u = tr[tr.pair == 'USDJPY']
P('\n=== USDJPY yearly sum R (x1) / gross pips sum ===')
y1 = u.pivot_table(index='year', columns='var', values='r_x1', aggfunc='sum').round(1)
y0 = u.pivot_table(index='year', columns='var', values='gross_pips', aggfunc='sum').round(0)
y1.to_csv(os.path.join(OUT, 'r4_s2_yearly_usdjpy_R_x1.csv')); y0.to_csv(os.path.join(OUT, 'r4_s2_yearly_usdjpy_grosspips.csv'))
P(pd.concat({'R_x1': y1, 'gross_pips': y0}, axis=1).to_string())
P('\n=== USDJPY by JST weekday (gross pips mean, R x1 mean, N) ===')
P(u.groupby(['var', 'dow_jst']).agg(N=('gross_pips','size'), g=('gross_pips','mean'), r1=('r_x1','mean')).round(3).unstack(0).to_string())
P('\n=== all pairs by period gross pips mean ===')
P(tr.groupby(['pair','var','period']).gross_pips.mean().round(2).unstack().to_string())
open(os.path.join(OUT, 'r4_s2_eval.log'), 'w').write('\n'.join(L))
