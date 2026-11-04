"""Round 4 shared helpers: metrics on trade lists (R units)."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bt import COST_PIPS, PIP
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'out')
DESIGN = ['EURUSD','GBPUSD','USDJPY','AUDUSD','USDCAD','USDCHF','NZDUSD']
CROSS = ['EURJPY','GBPJPY','EURGBP','AUDJPY','EURAUD','EURCHF','CADJPY','AUDNZD','NZDJPY','GBPCHF']
PERIODS = [('2005-2011', 2005, 2011), ('2012-2018', 2012, 2018), ('2019-2024', 2019, 2024)]

def period_of(year):
    y = np.asarray(year)
    return np.where(y <= 2011, '2005-2011', np.where(y <= 2018, '2012-2018', '2019-2024'))

def tstat(r):
    r = np.asarray(r, float)
    return r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 2 and r.std() > 0 else np.nan

def maxdd(r):
    c = np.cumsum(np.asarray(r, float)); peak = np.maximum.accumulate(np.concatenate([[0.0], c]))[1:]
    return float((c - peak).min()) if len(c) else 0.0

def longest_flat_days(t, r):
    """Longest time (days) between successive new highs of cumulative R (incl. the open stretch at the end)."""
    t = pd.to_datetime(pd.Series(t)).values; c = np.cumsum(np.asarray(r, float))
    if len(c) == 0: return 0.0
    best, last_hi_t, hi = 0.0, t[0], 0.0
    for ti, ci in zip(t, c):
        if ci > hi: best = max(best, (ti - last_hi_t) / np.timedelta64(1, 'D')); hi = ci; last_hi_t = ti
    best = max(best, (t[-1] - last_hi_t) / np.timedelta64(1, 'D'))
    return float(best)

def stats(tr, col='r'):
    r = tr[col].values
    if len(r) == 0: return dict(N=0, avgR=np.nan, t=np.nan, sumR=0, maxDD=0, ratio=np.nan, win=np.nan)
    s = r.sum(); dd = maxdd(r)
    return dict(N=len(r), avgR=r.mean(), t=tstat(r), sumR=s, maxDD=dd, ratio=s / abs(dd) if dd < 0 else np.inf, win=(r > 0).mean())
