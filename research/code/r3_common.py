"""Round 3 shared helpers (index + FX loaders, execution prices, London-fix time, metrics).
Conventions: histdata EST = UTC-5 fixed. D1 bar = 17:00 -> 17:00 EST, indexed here by its CLOSE date (dow-5 fragments dropped).
Index data: bars_idx/ unchanged; GRXEUR close dates 2020-06-15 .. 2023-12-01 are NOT DAX (Euro Stoxx 50 levels and session,
see out/r3_dq.log) -> flagged BAD_GRX and handled by exclusion (H-B EURUSD), decided before any strategy result."""
import os, sys, numpy as np, pandas as pd
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bt import PIP, COST_PIPS
from r1_common import tstat, sharpe, scale_to, curve_metrics, yearly, block_bootstrap_dd
from sig import atr
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'out'); BF = os.path.join(ROOT, 'bars_full'); BI = os.path.join(ROOT, 'bars_idx')
START = pd.Timestamp('2011-10-01'); IS_END = pd.Timestamp('2018-01-01'); END = pd.Timestamp('2025-01-01')
BAD_GRX = (pd.Timestamp('2020-06-15'), pd.Timestamp('2023-12-01'))

def _d1(path):
    df = pd.read_parquet(path)
    df = df[df.index.dayofweek != 5]
    df.index = (df.index + pd.Timedelta(days=1)).normalize()
    return df[~df.index.duplicated(keep='last')]

def idx_d1(sym): return _d1(os.path.join(BI, f'{sym}_D1.parquet'))
def fx_d1(pair): return _d1(os.path.join(BF, f'{pair}_D1.parquet'))
def fx_h1(pair): return pd.read_parquet(os.path.join(BF, f'{pair}_H1.parquet'))

def price_at(h1, when):
    """Execution price at timestamp `when` (EST): open of the H1 bar starting at `when`; if that bar is missing, the close of
    the last H1 bar that started within the previous 6 hours; else NaN."""
    when = pd.DatetimeIndex(when)
    o = h1['open'].reindex(when)
    miss = o.isna()
    if miss.any():
        c = h1['close']; pos = c.index.searchsorted(when[miss], side='left') - 1
        val = np.full(miss.sum(), np.nan)
        ok = pos >= 0
        ts = c.index[np.clip(pos, 0, None)]
        ok &= (when[miss] - ts) <= pd.Timedelta('6h')
        val[ok] = c.values[pos[ok]]
        o[miss] = val
    return o

def london_fix_est(dates):
    """16:00 Europe/London on each calendar date -> UTC -> EST (UTC-5). Returns DatetimeIndex (11:00 in GMT, 10:00 in BST)."""
    out = []
    for d in pd.DatetimeIndex(dates):
        t = pd.Timestamp(d.year, d.month, d.day, 16, 0, tz=ZoneInfo('Europe/London')).tz_convert('UTC').tz_localize(None)
        out.append(t - pd.Timedelta(hours=5))
    return pd.DatetimeIndex(out)

def maxdd_R(x):
    c = np.cumsum(np.asarray(x, float)); peak = np.maximum.accumulate(np.r_[0, c])[1:]
    return (c - peak).min()
