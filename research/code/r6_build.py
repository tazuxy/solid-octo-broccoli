"""Round 6 step 1: build E2 (Gotobi) + all non-Gotobi business days (placebo pool) with features; check vs r4b."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r6_common import *
tr = features(build())
tr.to_parquet(os.path.join(OUT, 'r6_trades_all.parquet'))
g = tr[tr.gotobi]
r4 = pd.read_parquet(os.path.join(OUT, 'r4b_s2_trades.parquet')); r4 = r4[(r4.pair == 'USDJPY') & (r4['var'] == 'E2') & r4.gotobi]
print('r6 E2 N', len(g), 'gross sum', round(g.gross_pips.sum(), 2), 'R mean', round(g.R_pips.mean(), 4))
print('r4b E2 N', len(r4), 'gross sum', round(r4.gross_pips.sum(), 2), 'R mean', round(r4.R_pips.mean(), 4))
print('non-gotobi pool N', (~tr.gotobi).sum())
print('N by period', g.period.value_counts().to_dict())
for c in CONDS: print(c, g[c].value_counts().to_dict())
log(f'r6_build: trades built (features only, no bucket statistics). E2 N={len(g)}')
