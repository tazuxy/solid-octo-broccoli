"""Diagnostics for the report (no new candidate rules are judged here): H-A buy&hold return split by regime state,
drawdown episodes; H-B gross vs cost decomposition."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r3_common import *
import r3_ha
D = pd.read_parquet(os.path.join(OUT, 'r3_ha_daily.parquet'))
sig = pd.read_parquet(os.path.join(OUT, 'r3_ha_signals.parquet'))
for v in ('a', 'b'):
    sv = sig[v]; pos = sv.index.searchsorted(D.index, side='left') - 1; st = pd.Series(sv.values[pos], index=D.index)
    for g in ('A', 'B'):
        bh = D[f'{g}_bh_c1.0']
        for per, m in (('IS', D.index < IS_END), ('OOS', D.index >= IS_END), ('ALL', D.index >= START)):
            on = bh[m & (st == 1)]; off = bh[m & (st == 0)]
            print(f'{v} {g} {per}: B&H ann. return (unscaled) on risk_on days {on.mean()*252*100:+.2f}% (share {len(on)/(len(on)+len(off)):.2f}),'
                  f' on risk_off days {off.mean()*252*100:+.2f}%  ann.vol on {on.std()*np.sqrt(252)*100:.1f}% off {off.std()*np.sqrt(252)*100:.1f}%')
# H-A drawdown episodes (8% vol, AB combined, variant a and bh)
W = pd.read_parquet(os.path.join(OUT, 'r3_ha_weekly.parquet'))
for v in ('a', 'bh'):
    r = scale_to((scale_to(W[f'A_{v}_c1.0']) + scale_to(W[f'B_{v}_c1.0'])) / 2); eq = (1 + r).cumprod(); dd = eq / eq.cummax() - 1
    t = dd.idxmin(); pk = eq[:t].idxmax(); print(v, 'AB maxDD %.1f%% peak %s trough %s' % (dd.min() * 100, pk.date(), t.date()))
# H-B cost share
for v in ('a', 'b'):
    tr = pd.read_parquet(os.path.join(OUT, f'r3_hb_trades_{v}_c1.0.parquet'))
    print(f'H-B {v}: avg gross R {tr.gross_R.mean():+.3f}, avg cost in R {(tr.gross_R - tr.R).mean():.3f}, avg R unit in pips',
          tr.assign(u=tr.R_unit / tr.pair.map(PIP)).groupby('pair').u.mean().round(1).to_dict(),
          ' gross t %.2f' % tstat(tr.gross_R))
    q = tr.assign(strong=tr['diff'].abs() >= 0.005)
    print('    |diff|>=0.5%:', q.groupby('strong').R.agg(['size', 'mean']).round(3).to_dict())
