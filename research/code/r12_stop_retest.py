"""Round 12: apply the method-2 stop (1R, no take-profit) to round-10 H1/H2/H3 trades (pre-registered in research/round12/r12_prereg.md).
Reads out/r10_trades.parquet, re-prices every trade on M5 bars with a 1R stop, writes out/r10_r12_trades.parquet
(evaluate with: TMIN=3.0 python3 -I code/r10_eval.py screen r12)."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r10_hyp as H
T = pd.read_parquet(os.path.join(H.OUT, 'r10_trades.parquet')); T = T[T.hyp.isin(['H1', 'H2', 'H3'])].copy()
rows = []
for p, g in T.groupby('inst'):
    b = H.bars(p, 'M5'); idx = b.index; o, h, l = b.open.values, b.high.values, b.low.values; P = H.pip(p)
    for _, t in g.iterrows():
        i0 = idx.get_loc(t.t_ent); i1 = idx.get_loc(t.t_exit); e = o[i0]; R = t.R_pips * P; d = t.dir
        sl = e - d * R; px = o[i1]; hit = 0
        for j in range(i0, i1):
            if j > i0 and d * (o[j] - sl) <= 0: px, hit = o[j], 2; break
            if (d == 1 and l[j] <= sl) or (d == -1 and h[j] >= sl): px, hit = sl, 1; break
        r = t.to_dict(); r['gross_pips'] = d * (px - e) / P; r['stopped'] = hit; r['hyp'] = t.hyp + 's'
        assert abs(d * (o[i1] - e) / P - t.gross_pips) < 1e-6        # same entry/exit prices as round 10
        rows.append(r)
S = pd.DataFrame(rows); S.to_parquet(os.path.join(H.OUT, 'r10_r12_trades.parquet'))
print(S[S.delay == 0].groupby('hyp').stopped.apply(lambda x: (x > 0).mean()).round(3).to_dict())
