"""Round 4b diagnostics for the passing Gotobi variants E1/E2 (USDJPY, report only): outliers, Gotobi type, G weekday."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4b_common import *
tr = pd.read_parquet(os.path.join(OUT, 'r4b_s2_trades.parquet')); u = tr[(tr.pair == 'USDJPY') & tr.gotobi].copy()
u['r05'] = (u.gross_pips - BASE) / u.R_pips
lastbd = u.G.groupby([u.G.dt.year, u.G.dt.month]).transform('max')  # not used: need calendar last weekday
bd = pd.bdate_range('2004-12-01', '2025-01-31'); lb = set(pd.Series(bd, index=bd).groupby([bd.year, bd.month]).max())
def gtype(G):
    if G in lb: return 'month_end'
    d = G.day
    for n in (30, 25, 20, 15, 10, 5):
        if d <= n and d > n - 5: return f'd{n}'
    return 'other'
u['gtype'] = u.G.map(gtype)
pd.set_option('display.width', 200)
for var in ('E1', 'E2', 'b', 'E3'):
    v = u[u['var'] == ('a' if var == 'b' else var)]
    q = v.r05.quantile([0.01, 0.99]); tv = v[(v.r05 > q.iloc[0]) & (v.r05 < q.iloc[1])]
    print(f'{var}: N={len(v)} mean={v.r05.mean():.3f} median={v.r05.median():.3f} win={(v.r05>0).mean():.3f} trimmed1%={tv.r05.mean():.3f} t_trim={tstat(tv.r05):.2f} '
          f'top10 trades sumR={v.r05.nlargest(10).sum():.1f} bottom10={v.r05.nsmallest(10).sum():.1f} total={v.r05.sum():.1f}')
    print(v.groupby('gtype').agg(N=('r05', 'size'), g=('gross_pips', 'mean'), r=('r05', 'mean'), t=('r05', tstat)).round(2).T.to_string())
    print(v.groupby('G_dow').agg(N=('r05', 'size'), g=('gross_pips', 'mean'), r=('r05', 'mean'), t=('r05', tstat)).round(2).T.to_string())
