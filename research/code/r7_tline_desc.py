"""Descriptive (outside the loop, NOT eligible for promotion): counter-trendline break family T on the 2005-2021 pool only.
Pooled 17 FX pairs and XAUUSD separately; non-overlapping trades per pair; net of 0.5 pip (XAU 0.30 USD)."""
import sys, os, warnings; warnings.filterwarnings('ignore'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r7_v2loop as W, r7_lib as L, pandas as pd, numpy as np
T = W.load_tables(); rows = []
for tf in ('H1', 'M15'):
    for trig in ['T_a_any', 'T_a_dh4', 'T_a_dd1', 'T_a_e4', 'T_b_any']:
        for out in ['h12', 'h24', 'tb', 'tt']:
            for d in (1, -1):
                for grp, insts in (('POOL17', L.FX), ('XAUUSD', ['XAUUSD'])):
                    c = dict(kind='v2', tf=tf, inst='POOL' if grp == 'POOL17' else 'XAUUSD', trig=trig, conds={}, out=out, d=d)
                    X = W.v2_trades(T, c, insts)
                    if len(X) < 30: continue
                    s = W.V1_stats(X); per = X.groupby('inst').netR.mean()
                    rows.append(dict(tf=tf, trig=trig, out=out, dir='follow' if d > 0 else 'fade', grp=grp, N=s['N'], per_year=round(s['N'] / 17, 1),
                                     mean_pips=round(s['mean_pips'], 2), mean_R=round(s['mean_R'], 4), gross_R=round(s['gross_R'], 4),
                                     t_trades=round(s['t_R'], 2), t_daily=round(s['t_day'], 2), blocks=s['blocks_pos'],
                                     pairs_pos=f"{int((per > 0).sum())}/{len(per)}"))
R = pd.DataFrame(rows); R.to_csv(os.path.join(L.OUT, 'r7_tline_desc.csv'), index=False)
pd.set_option('display.width', 250); print(R[R.dir == 'follow'].to_string(index=False))
print('\nfade rows with t_daily>=2:'); print(R[(R.dir == 'fade') & (R.t_daily >= 2)].to_string(index=False))
print('\nn rows', len(R), 'best', R.sort_values('t_daily').tail(3).to_string(index=False))
