"""Round-1 shared helpers: daily/weekly panels, cost fractions, performance metrics.
Conventions (no look-ahead):
  * D1 bars are indexed by their OPEN time (17:00 EST); the bar closes 24h later. We index daily data by the
    CLOSE date. Saturday-open fragments (dow 5) are dropped.
  * Weekly rebalance decision = last trading day of each Mon-Fri week (normally the Friday 17:00 NY close),
    using closes up to and including that bar.  Execution = OPEN of the next D1 bar (Sunday 17:00).
  * Holding return of week k = exec_price[k+1] / exec_price[k] - 1 (open-to-open, includes the weekend gap).
  * Costs: COST_PIPS (round trip) * PIP / price as a fraction of notional; a one-way trade of notional |dw|
    pays |dw| * cost/2.  COST_PIPS unchanged from round 0.
"""
import sys, os, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sig import ROOT, BARS
from bt import PIP, COST_PIPS
OUT = os.path.join(ROOT, 'out')
DESIGN = ['EURUSD','GBPUSD','USDJPY','AUDUSD','USDCAD','USDCHF','NZDUSD','XAUUSD']
CROSS = ['EURJPY','GBPJPY','EURGBP','AUDJPY','EURAUD','EURCHF','CADJPY','AUDNZD','NZDJPY','GBPCHF']
ALL = DESIGN + CROSS
JPYX = ['EURJPY','GBPJPY','AUDJPY','CADJPY','NZDJPY']
IS_END = pd.Timestamp('2019-01-01')
END = pd.Timestamp('2025-01-01')

def d1(pair):
    df = pd.read_parquet(os.path.join(BARS, f'{pair}_D1.parquet'))
    df = df[df.index.dayofweek != 5]
    df.index = (df.index + pd.Timedelta(days=1)).normalize()      # close date
    df = df[~df.index.duplicated(keep='last')]
    return df

_cache = {}
def panels(pairs=ALL):
    key = tuple(pairs)
    if key in _cache: return _cache[key]
    dd = {p: d1(p) for p in pairs}
    idx = sorted(set().union(*[d.index for d in dd.values()]))
    idx = pd.DatetimeIndex([t for t in idx if t.dayofweek < 5 and t < END])
    C = pd.DataFrame({p: dd[p].close.reindex(idx) for p in pairs})
    O = pd.DataFrame({p: dd[p].open.reindex(idx) for p in pairs})
    Cf = C.ffill()
    # execution price: the open of that day's bar, or the last close if the bar is missing (holiday)
    X = O.fillna(Cf.shift(1))
    X[C.isna() & C.ffill().isna()] = np.nan      # before an instrument's first bar
    _cache[key] = (C, Cf, X)
    return _cache[key]

def weekly_schedule(idx):
    """Return DataFrame with decision date (last trading day of week) and exec date (next trading day)."""
    s = pd.Series(idx, index=idx)
    wk = s.groupby(idx.to_period('W-FRI')).max()
    dec = pd.DatetimeIndex(wk.values)
    pos = idx.get_indexer(dec)
    ok = pos + 1 < len(idx)
    dec = dec[ok]; ex = idx[pos[ok] + 1]
    return pd.DataFrame({'dec': dec, 'exec': ex})

def cost_frac(pair, price):
    return COST_PIPS[pair] * PIP[pair] / price

# ------------------------------------------------------------------ metrics
def ann_ret(r, ppy=52): return np.nanmean(r) * ppy
def tstat(r):
    r = np.asarray(r, float); r = r[~np.isnan(r)]
    return r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 2 and r.std() > 0 else np.nan
def sharpe(r, ppy=52):
    r = np.asarray(r, float); r = r[~np.isnan(r)]
    return r.mean() / r.std(ddof=1) * np.sqrt(ppy) if r.std() > 0 else np.nan

def scale_to(r, target=0.08, ppy=52):
    r = pd.Series(r).dropna(); v = r.std(ddof=1) * np.sqrt(ppy)
    return r * (target / v) if v > 0 else r

def curve_metrics(r, ppy=52):
    """r: periodic returns indexed by period-end date (compounded)."""
    r = pd.Series(r).dropna()
    eq = (1 + r).cumprod(); eq0 = pd.concat([pd.Series([1.0], index=[r.index[0] - pd.Timedelta(days=7)]), eq])
    dd = (eq0 / eq0.cummax() - 1)
    hi = eq0.cummax(); newhi = eq0.index[eq0 >= hi]
    gaps = np.diff(np.r_[newhi.values, np.datetime64(eq0.index[-1])]).astype('timedelta64[D]').astype(int)
    yrs = (eq0.index[-1] - eq0.index[0]).days / 365.25
    return dict(cum=eq0.iloc[-1] - 1, cagr=eq0.iloc[-1] ** (1 / yrs) - 1, maxdd=dd.min(),
                ret_dd=(eq0.iloc[-1] - 1) / abs(dd.min()) if dd.min() < 0 else np.inf,
                flat_m=gaps.max() / 30.44, eq=eq0)

def yearly(r):
    r = pd.Series(r).dropna(); return (1 + r).groupby(r.index.year).prod() - 1

def cells(rd, rc):
    """Annualised net return in the 4 cells. rd/rc: weekly net returns (Series) of group D and C."""
    out = {}
    for g, r in (('D', rd), ('C', rc)):
        r = pd.Series(r).dropna()
        out[f'{g}_IS'] = ann_ret(r[r.index < IS_END]); out[f'{g}_OOS'] = ann_ret(r[r.index >= IS_END])
    return out

def block_bootstrap_dd(r, n=5000, block=4, seed=0):
    r = np.asarray(pd.Series(r).dropna()); N = len(r); rng = np.random.default_rng(seed); nb = int(np.ceil(N / block))
    dds = np.empty(n)
    for k in range(n):
        st = rng.integers(0, N - block + 1, nb)
        x = np.concatenate([r[s:s + block] for s in st])[:N]
        eq = np.cumprod(1 + x); dds[k] = (eq / np.maximum.accumulate(np.maximum(eq, 1.0)) - 1).min()
    return dds
