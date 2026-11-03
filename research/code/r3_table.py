"""One pass/fail table for the 4 pre-registered variants -> out/r3_pass_table.md (+csv)."""
import os, sys, ast, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r3_common import *
S = pd.read_csv(os.path.join(OUT, 'r3_ha_stats.csv')).set_index(['variant', 'cost', 'group'])
HB = pd.read_csv(os.path.join(OUT, 'r3_hb_criteria.csv')).set_index('variant')
yn = lambda b: 'PASS' if b else 'FAIL'
L = ['| Variant | Criterion | Value | Threshold | Result |', '|---|---|---|---|---|']
rows = []
for v in ('a', 'b'):
    def cells(cm): return {f'{g}-{p}': S.loc[(v, cm, g), f'{p}_ann_8v'] for g in ('A', 'B') for p in ('IS', 'OOS')}
    c = cells(1.0); c1 = all(x > 0 for x in c.values())
    t = S.loc[(v, 1.0, 'AB'), 't_8v']; rd = S.loc[(v, 1.0, 'AB'), 'ret_dd_8v']
    c4 = {g: (S.loc[(v, 1.0, g), 'sharpe_8v'], S.loc[('bh', 1.0, g), 'sharpe_8v'], S.loc[(v, 1.0, g), 'maxdd_8v'], S.loc[('bh', 1.0, g), 'maxdd_8v']) for g in ('A', 'B')}
    p4 = all(x[0] > x[1] and x[2] > x[3] for x in c4.values())
    cx = cells(2.0); tx = S.loc[(v, 2.0, 'AB'), 't_8v']; rdx = S.loc[(v, 2.0, 'AB'), 'ret_dd_8v']; p5 = all(x > 0 for x in cx.values()) and tx >= 2 and rdx >= 3
    nm = f'H-A {v}'
    rows += [(nm, '(1) ann. net return, 4 cells (8% vol)', ', '.join(f'{k} {x*100:+.2f}%' for k, x in c.items()), 'all > 0', yn(c1)),
             (nm, '(2) t weekly, A+B', f'{t:.2f}', '>= 2.0', yn(t >= 2)),
             (nm, '(3) cum / maxDD, A+B @8%', f'{S.loc[(v,1.0,"AB"),"cum_8v"]*100:+.1f}% / {S.loc[(v,1.0,"AB"),"maxdd_8v"]*100:.1f}% = {rd:.2f}', '>= 3', yn(rd >= 3)),
             (nm, '(4) vs buy&hold: Sharpe, maxDD', '; '.join(f'{g}: SR {x[0]:.2f} vs {x[1]:.2f}, DD {x[2]*100:.1f}% vs {x[3]*100:.1f}%' for g, x in c4.items()), 'better on both, both groups', yn(p4)),
             (nm, '(5) costs x2: (1)-(3)', ', '.join(f'{k} {x*100:+.2f}%' for k, x in cx.items()) + f'; t {tx:.2f}; ratio {rdx:.2f}', '(1)-(3) hold', yn(p5)),
             (nm, 'OVERALL', '', '', yn(c1 and t >= 2 and rd >= 3 and p4 and p5))]
for v in ('a', 'b'):
    r = HB.loc[v]; pp = ast.literal_eval(r.per_pair); c5 = ast.literal_eval(r.c5_detail.replace('np.float64(', '(')) if isinstance(r.c5_detail, str) else r.c5_detail
    nm = f'H-B {v}'
    rows += [(nm, '(1) avg net R: IS, OOS, pairs>0', f'IS {r.avgR_IS:+.3f}, OOS {r.avgR_OOS:+.3f}; ' + ', '.join(f'{k} {x:+.3f}' for k, x in pp.items()), 'IS>0, OOS>0, >=3/4 pairs', yn(r.c1)),
             (nm, '(2) pooled t', f'{r.t:.2f}', '>= 2.0', yn(r.c2)),
             (nm, '(3) sumR / abs(maxDD_R)', f'{r.sumR:+.1f} / {r.maxddR:.1f} = {r.retdd:.2f}', '>= 3', yn(r.c3)),
             (nm, '(4) N', f'{int(r.N)}', '>= 100', yn(r.c4)),
             (nm, '(5) costs x1.5: (1)-(3)', f'IS {c5["avgR_IS"]:+.3f}, OOS {c5["avgR_OOS"]:+.3f}, pairs+ {c5["pairs_pos"]}; t {c5["t"]:.2f}; ratio {c5["retdd"]:.2f}', '(1)-(3) hold', yn(r.c5)),
             (nm, 'OVERALL', '', '', yn(r.PASS))]
for x in rows: L.append('| ' + ' | '.join(x) + ' |')
open(os.path.join(OUT, 'r3_pass_table.md'), 'w').write('\n'.join(L) + '\n'); pd.DataFrame(rows, columns=['variant', 'criterion', 'value', 'threshold', 'result']).to_csv(os.path.join(OUT, 'r3_pass_table.csv'), index=False)
print('\n'.join(L))
