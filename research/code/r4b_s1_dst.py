"""Round 4b S1 diagnostic (report only): early-bucket (17:30-17:55 EST) gross edge split by US DST status.
US winter: NY 17:00 rollover = 17:00 EST -> bucket is 30-55 min after rollover. US summer: rollover = 16:00 EST -> 90-115 min after.
If the early edge is mostly a rollover-spread (bid-only) artefact it should be larger in US winter."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4b_common import *
def us_dst(ts):
    ts = pd.to_datetime(ts); y = ts.dt.year; out = np.zeros(len(ts), bool)
    for yy in np.unique(y):
        if yy >= 2007:
            a = pd.Timestamp(f'{yy}-03-01'); a += pd.Timedelta(days=(6 - a.dayofweek) % 7 + 7)
            b = pd.Timestamp(f'{yy}-11-01'); b += pd.Timedelta(days=(6 - b.dayofweek) % 7)
        else:
            a = pd.Timestamp(f'{yy}-04-01'); a += pd.Timedelta(days=(6 - a.dayofweek) % 7)
            b = pd.Timestamp(f'{yy}-10-31'); b -= pd.Timedelta(days=(b.dayofweek + 1) % 7)
        m = (y == yy).values; out[m] = ((ts[m] >= a) & (ts[m] < b)).values
    return out
tr = pd.read_parquet(os.path.join(OUT, 'r4_s1_trades_eval.parquet')); tr = tr[tr.win == 'night'].copy()
tr['us_summer'] = us_dst(tr.t_ent); tr['b2'] = np.where(tr.bucket == '17:30-17:55', 'early', 'late')
tr['r05'] = (tr.gross_pips - BASE) / tr.risk_pips
g = tr.groupby(['sig','ex','b2','us_summer']).agg(N=('gross_pips','size'), g_pips=('gross_pips','mean'), avgR_05=('r05','mean')).round(3)
pd.set_option('display.width', 200); print(g.to_string()); g.to_csv(os.path.join(OUT, 'r4b_s1_dst.csv'))
