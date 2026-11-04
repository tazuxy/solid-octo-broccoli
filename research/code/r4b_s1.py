"""Round 4b S1 re-evaluation at the user's 0.5-pip round-trip cost (all 17 pairs), sensitivity 0/0.3/0.7/1.0.
Re-uses r4 trades (out/r4_s1_trades_eval.parquet, produced by r4_s1.py + r4_eval_s1.py, rules unchanged).
Criteria (r4 S1, baseline now 0.5 pip): (1) 6 cells avgR>0, (2) t>=3, (3) sumR/|maxDD|>=3, (4) >=60% pairs sumR>0,
(5) avgR>0 at 2x cost (1.0 pip).  Robustness view (NOT a pass filter): drop trades entered 17:30-17:55 EST.
Edge location: gross pips by entry bucket 17:30-17:55 vs 18:00-18:45."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4b_common import *
tr = pd.read_parquet(os.path.join(OUT, 'r4_s1_trades_eval.parquet')).sort_values('t_ent').reset_index(drop=True)
tr = tr[tr.win == 'night'].copy()
tr['late'] = tr.bucket != '17:30-17:55'
L = []
def P(*a): s = ' '.join(str(x) for x in a); print(s); L.append(s)
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 60)
rows = []
for view, sub in (('all', tr), ('excl_1730_1755', tr[tr.late])):
    for (sig, ex), v in sub.groupby(['sig', 'ex']):
        row = dict(view=view, variant=f'{sig}/{ex}', N=len(v), gross_pips=v.gross_pips.mean(), risk_med=v.risk_pips.median())
        for c in COSTS:
            r = (v.gross_pips - c) / v.risk_pips; s = stats(pd.DataFrame({'r': r.values}))
            row.update({f'avgR_{c}': s['avgR'], f't_{c}': s['t'], f'sumR_{c}': s['sumR'], f'maxDD_{c}': s['maxDD'], f'ratio_{c}': s['ratio']})
        r = (v.gross_pips - BASE) / v.risk_pips
        cells = r.groupby([v.grp, v.period]).mean()
        for (g, pp), x in cells.items(): row[f'cell_{g}_{pp}'] = x
        pr = r.groupby(v.pair).sum(); row['pairs_pos'] = int((pr > 0).sum()); row['pairs_n'] = len(pr)
        row['flat_days'] = longest_flat_days(v.t_ent, r.values)
        crit = dict(c1=bool((cells > 0).all() and len(cells) == 6), c2=bool(row[f't_{BASE}'] >= 3), c3=bool(row[f'ratio_{BASE}'] >= 3),
                    c4=bool(row['pairs_pos'] >= 0.6 * row['pairs_n']), c5=bool(row['avgR_1.0'] > 0))
        row.update(crit); row['PASS'] = all(crit.values()); rows.append(row)
t = pd.DataFrame(rows); t.to_csv(os.path.join(OUT, 'r4b_s1_pass.csv'), index=False)
P('=== S1 at absolute round-trip costs (pips), baseline 0.5 ===')
P(t[['view','variant','N','gross_pips','risk_med'] + [f'avgR_{c}' for c in COSTS] + [f't_{c}' for c in COSTS]].round(3).to_string(index=False))
P(t[['view','variant',f'sumR_{BASE}',f'maxDD_{BASE}',f'ratio_{BASE}','ratio_1.0'] + [c for c in t.columns if c.startswith('cell_')] + ['pairs_pos','pairs_n','flat_days','c1','c2','c3','c4','c5','PASS']].round(3).to_string(index=False))
P('\n=== edge location: gross pips by entry bucket ===')
b = tr.assign(b2=np.where(tr.late, '18:00-18:45', '17:30-17:55')).groupby(['sig','ex','b2']).agg(N=('gross_pips','size'), g_pips=('gross_pips','mean'), sum_g=('gross_pips','sum'),
     sumR0=('r0','sum'), avgR_05=('gross_pips', 'size'))
b['avgR_05'] = tr.assign(b2=np.where(tr.late, '18:00-18:45', '17:30-17:55'), r05=(tr.gross_pips - BASE) / tr.risk_pips).groupby(['sig','ex','b2']).r05.mean()
b['share_gross_pips'] = b.sum_g / b.groupby(level=[0, 1]).sum_g.transform('sum'); b['share_N'] = b.N / b.groupby(level=[0, 1]).N.transform('sum')
b['share_sumR0'] = b.sumR0 / b.groupby(level=[0, 1]).sumR0.transform('sum')
b.to_csv(os.path.join(OUT, 'r4b_s1_buckets.csv')); P(b.round(3).to_string())
P('\n=== by direction x bucket, gross pips ===')
P(tr.assign(b2=np.where(tr.late, 'late', 'early')).groupby(['sig','ex','b2','dir']).gross_pips.mean().round(2).unstack([2,3]).to_string())
P('\n=== cell avgR at 0.5 by group/period, excl early (robustness) shown above; yearly sumR at 0.5 (all) ===')
yr = tr.assign(r05=(tr.gross_pips - BASE) / tr.risk_pips).pivot_table(index='year', columns=['sig','ex'], values='r05', aggfunc='sum').round(1)
yr.to_csv(os.path.join(OUT, 'r4b_s1_yearly_05.csv')); P(yr.to_string())
open(os.path.join(OUT, 'r4b_s1.log'), 'w').write('\n'.join(L))
