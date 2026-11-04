"""R5 evaluation: one pass/fail table for 14 pre-registered variants + supporting tables -> out/r5_eval.txt, out/r5_summary.csv"""
import os, sys, math, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r5_common import *

h1 = pd.read_parquet(os.path.join(OUT, 'r5_h1_trades.parquet'))
h2 = pd.read_parquet(os.path.join(OUT, 'r5_h2_trades.parquet'))
h3 = pd.read_parquet(os.path.join(OUT, 'r5_h345_trades.parquet'))
ALL = pd.concat([h1, h2, h3], ignore_index=True)
VARS = ['H1a', 'H1b', 'H2a', 'H2b'] + [f'H3_{f}_{s}' for f in ('TKY', 'ECB', 'LDN') for s in ('pre', 'post')] + ['H4a', 'H4b', 'H5a', 'H5b']
lines = []
def P(*a): lines.append(' '.join(str(x) for x in a))

def onep(t):  # one-sided normal p
    return 0.5 * math.erfc(t / math.sqrt(2))

rows = []; res = {}
for v in VARS:
    x = ALL[ALL['var'] == v]; base = x[x['mode'] == 'base']; dl = x[x['mode'] == 'delay']
    gold = v.startswith('H4')
    e = evaluate(base, dl, gold=gold, extra_cost=GOLD_COST_ALT if gold else None); res[v] = (e, base)
    r = {k: e[k] for k in ('N', 'gross_pips', 'gross_avgR', 'avgR', 't', 'sumR', 'maxDD', 'ratio', 'avgR_x2', 'avgR_x4', 'drop5',
                          'delay_avgR', 'inst_pos', 'flat_days', 'med_R_pips', 'win', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'PASS')}
    r['var'] = v; r['cells_pos'] = f"{sum(c[0] > 0 for c in e['cells'].values())}/{len(e['cells'])}"
    r['p1'] = onep(e['t']); r['p_bonf14'] = min(1, 14 * r['p1'])
    if gold: r['avgR_gold020'] = e['avgR_alt']
    rows.append(r)
S = pd.DataFrame(rows).set_index('var'); S.to_csv(os.path.join(OUT, 'r5_summary.csv'))
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40)
P('=== PASS/FAIL (cost: FX 0.5 pip RT, gold 0.30) ===')
P(S[['N', 'gross_pips', 'gross_avgR', 'avgR', 't', 'sumR', 'maxDD', 'ratio', 'cells_pos', 'inst_pos', 'avgR_x2', 'drop5', 'delay_avgR',
     'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'PASS']].round(4).to_string())
P('\n--- extra: avgR_x4, flat_days, median R pips, win, p one-sided, Bonferroni x14')
P(S[['avgR_x4', 'flat_days', 'med_R_pips', 'win', 'p1', 'p_bonf14']].round(4).to_string())
if 'avgR_gold020' in S: P('gold @0.20:', S['avgR_gold020'].dropna().round(4).to_dict())
P('\n=== cells avgR (n) ===')
for v in VARS:
    P(v, {k: (round(a, 4), n) for k, (a, n) in res[v][0]['cells'].items()})
P('\n=== yearly sum net R (1x) ===')
Y = {}
for v in VARS:
    b = res[v][1]; Y[v] = b.assign(r=netR(b, 1), y=b.t_ent.dt.year).groupby('y').r.sum()
P(pd.DataFrame(Y).round(1).to_string())
P('\n=== per instrument: N, gross pips, net avgR, sumR ===')
for v in VARS:
    b = res[v][1].assign(r=lambda d: netR(d, 1))
    g = b.groupby('inst').agg(N=('r', 'size'), gp=('gross_pips', 'mean'), avgR=('r', 'mean'), sumR=('r', 'sum')).round(3)
    P(f'-- {v}'); P(g.T.to_string())
P('\n=== cost sensitivity avgR (0x,1x,2x,4x) and breakeven multiple ===')
for v in VARS:
    b = res[v][1]; gp = b.gross_pips.values; R = b.R_pips.values; cp = b.cost_pips.values
    be = (gp / R).mean() / (cp / R).mean()
    P(v, [round(((gp - m * cp) / R).mean(), 4) for m in (0, 1, 2, 4)], 'breakeven x', round(be, 2))
P('\n=== H1 reference: entry at first Sunday bar (bid-only, Sunday spread ignored) ===')
for v in ('H1a', 'H1b'):
    for mode in ('first', 'base', 'delay'):
        b = h1[(h1['var'] == v) & (h1['mode'] == mode)]
        P(v, mode, 'N', len(b), 'gross pips', round(b.gross_pips.mean(), 2), 'avgR 0/1/2/4x', [round(netR(b, m).mean(), 4) for m in (0, 1, 2, 4)],
          't1x', round(tstat(netR(b, 1)), 2), 'exit mix', b.why.value_counts(normalize=True).round(3).to_dict())
    b = h1[(h1['var'] == v) & (h1['mode'] == 'base')]
    P(v, 'cost (pips) needed to reach breakeven:', round(b.gross_pips.mean(), 2), ' median |gap| pips', round(b.R_pips.median(), 1))
P('\n=== H3 cross check (no USD, long base ccy, London fix) gross pips mean, t ===')
for v in ('X_LDN_pre_longbase', 'X_LDN_post_longbase'):
    for p in ('EURGBP', 'EURJPY'):
        b = h3[(h3['var'] == v) & (h3['inst'] == p) & (h3['mode'] == 'base')]
        P(v, p, len(b), round(b.gross_pips.mean(), 3), 't', round(tstat(b.gross_pips.values), 2))
P('\n=== H3 gross t by fix (pooled pairs) and by USDJPY only ===')
for v in VARS[4:10]:
    b = res[v][1]; P(v, 'gross t', round(tstat(b.gross_pips / b.R_pips), 2), 'USDJPY gross pips', round(b[b.inst == 'USDJPY'].gross_pips.mean(), 3))
P('\nTests this round: 14 variants. Best one-sided p:', S.p1.min(), S.p1.idxmin(), 'Bonferroni x14:', S.p_bonf14.min())
open(os.path.join(OUT, 'r5_eval.txt'), 'w').write('\n'.join(lines)); print('\n'.join(lines))
