"""Round 4 S1 evaluation: costs x0/x1/x2(baseline)/x3, 6 cells, pass table, pairs, hour buckets, yearly, placebo."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4_common import *
tr = pd.read_parquet(os.path.join(OUT, 'r4_s1_trades.parquet')).sort_values('t_ent').reset_index(drop=True)
tr['cost_pips'] = tr.pair.map(COST_PIPS); tr['grp'] = np.where(tr.pair.isin(DESIGN), 'design', 'cross')
tr['year'] = pd.to_datetime(tr.t_ent).dt.year; tr['period'] = period_of(tr.year)
for m in (0, 1, 2, 3): tr[f'r{m}'] = (tr.gross_pips - m * tr.cost_pips) / tr.risk_pips
tm = pd.to_datetime(tr.t_ent); hm = tm.dt.hour * 60 + tm.dt.minute
tr['bucket'] = np.where(tr.win == 'night', np.where(hm < 18*60, '17:30-17:55', np.where(hm < 18*60+30, '18:00-18:25', '18:30-18:45')),
                        np.where(hm < 9*60, '08:00-08:55', np.where(hm < 10*60, '09:00-09:55', '10:00-10:45')))
tr.to_parquet(os.path.join(OUT, 'r4_s1_trades_eval.parquet'))
L = []
def P(*a): s = ' '.join(str(x) for x in a); print(s); L.append(s)
pass_rows = []; detail = []
for win in ('night', 'placebo'):
    for sig in ('rsi', 'bb'):
        for ex in ('mid', 'atr'):
            v = tr[(tr.win == win) & (tr.sig == sig) & (tr.ex == ex)]; name = f'{sig}/{ex}'
            row = dict(win=win, variant=name, N=len(v))
            for m in (0, 1, 2, 3):
                s = stats(v, f'r{m}'); row.update({f'avgR_x{m}': s['avgR'], f't_x{m}': s['t'], f'sumR_x{m}': s['sumR'], f'maxDD_x{m}': s['maxDD'], f'ratio_x{m}': s['ratio']})
            row['avg_gross_pips'] = v.gross_pips.mean(); row['avg_cost_pips_x1'] = v.cost_pips.mean(); row['median_risk_pips'] = v.risk_pips.median()
            row['win_x2'] = (v.r2 > 0).mean(); row['tp_share'] = (v.reason == 'tp').mean(); row['sl_share'] = (v.reason == 'sl').mean()
            cells = v.groupby(['grp', 'period']).r2.mean()
            for (g, pp), x in cells.items(): row[f'cell_{g}_{pp}'] = x
            pr = v.groupby('pair').r2.sum(); row['pairs_pos'] = int((pr > 0).sum()); row['pairs_n'] = len(pr)
            row['flat_days_x2'] = longest_flat_days(v.t_ent, v.r2)
            crit = dict(c1_cells=bool((cells > 0).all() and len(cells) == 6), c2_t3=bool(row['t_x2'] >= 3.0), c3_ratio3=bool(row['ratio_x2'] >= 3),
                        c4_pairs60=bool(row['pairs_pos'] >= 0.6 * row['pairs_n']), c5_x3pos=bool(row['avgR_x3'] > 0))
            row.update(crit); row['PASS'] = all(crit.values())
            pass_rows.append(row)
pr = pd.DataFrame(pass_rows); pr.to_csv(os.path.join(OUT, 'r4_s1_pass.csv'), index=False)
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 60)
P('=== S1 summary (r_x = net R at cost multiple x; baseline x2 for night) ===')
P(pr[['win','variant','N','avg_gross_pips','avg_cost_pips_x1','median_risk_pips','avgR_x0','avgR_x1','avgR_x2','avgR_x3','t_x0','t_x2','sumR_x2','maxDD_x2','ratio_x2','win_x2','tp_share','sl_share']].round(3).to_string(index=False))
P(pr[['win','variant'] + [c for c in pr.columns if c.startswith('cell_')] + ['pairs_pos','pairs_n','flat_days_x2','c1_cells','c2_t3','c3_ratio3','c4_pairs60','c5_x3pos','PASS']].round(3).to_string(index=False))
nt = tr[tr.win == 'night']
P('\n=== by pair, night, avgR gross / x1 / x2, N ===')
bp = nt.groupby(['sig','ex','pair']).agg(N=('r0','size'), g_pips=('gross_pips','mean'), cost=('cost_pips','first'), risk=('risk_pips','median'),
                                           r0=('r0','mean'), r1=('r1','mean'), r2=('r2','mean'), sum2=('r2','sum')).round(3)
bp.to_csv(os.path.join(OUT, 'r4_s1_pairs.csv')); P(bp.to_string())
P('\n=== by hour bucket (entry time) avgR x0 / x2, N ===')
hb = tr.groupby(['win','sig','ex','bucket']).agg(N=('r0','size'), g_pips=('gross_pips','mean'), r0=('r0','mean'), r1=('r1','mean'), r2=('r2','mean')).round(3)
hb.to_csv(os.path.join(OUT, 'r4_s1_buckets.csv')); P(hb.to_string())
P('\n=== yearly sum R at x2 (night) ===')
yr = nt.pivot_table(index='year', columns=['sig','ex'], values='r2', aggfunc='sum').round(1)
yr0 = nt.pivot_table(index='year', columns=['sig','ex'], values='r0', aggfunc='sum').round(1)
yr.to_csv(os.path.join(OUT, 'r4_s1_yearly_x2.csv')); yr0.to_csv(os.path.join(OUT, 'r4_s1_yearly_x0.csv'))
P(yr.to_string()); P('gross:'); P(yr0.to_string())
P('\n=== gross avg pips by group/period (night) ===')
P(nt.groupby(['sig','ex','grp','period']).agg(N=('r0','size'), g_pips=('gross_pips','mean'), cost=('cost_pips','mean'), r0=('r0','mean'), r2=('r2','mean')).round(3).to_string())
P('\nambiguous SL+TP same bar share:', nt.both.mean().round(4))
open(os.path.join(OUT, 'r4_s1_eval.log'), 'w').write('\n'.join(L))
