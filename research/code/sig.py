"""Indicators and the BB-touch + RSI-divergence signal (vectorised, no look-ahead).
All indicator values at bar i use data up to and including bar i's close."""
import numpy as np, pandas as pd, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BARS = os.path.join(ROOT, 'bars')

def load(pair, tf, start='2012-01-01'):
    df = pd.read_parquet(os.path.join(BARS, f'{pair}_{tf}.parquet'))
    return df[df.index >= start]

def rsi(close, n=14):
    d = np.diff(close, prepend=close[0])
    up = np.where(d > 0, d, 0.0); dn = np.where(d < 0, -d, 0.0)
    au = np.full_like(close, np.nan); ad = np.full_like(close, np.nan)
    if len(close) <= n: return np.full_like(close, np.nan)
    au[n] = up[1:n+1].mean(); ad[n] = dn[1:n+1].mean()
    a = 1.0 / n
    for i in range(n+1, len(close)):
        au[i] = au[i-1] + a * (up[i] - au[i-1]); ad[i] = ad[i-1] + a * (dn[i] - ad[i-1])
    rs = au / np.where(ad == 0, np.nan, ad)
    out = 100 - 100 / (1 + rs)
    out[(ad == 0) & (au > 0)] = 100.0
    return out

def atr(h, l, c, n=14):
    pc = np.roll(c, 1); pc[0] = c[0]
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    out = np.full_like(c, np.nan); out[n-1] = tr[:n].mean()
    a = 1.0 / n
    for i in range(n, len(c)): out[i] = out[i-1] + a * (tr[i] - out[i-1])
    return out

def bbands(close, n=20, k=2.0):
    s = pd.Series(close)
    mid = s.rolling(n).mean().values; sd = s.rolling(n).std(ddof=0).values
    return mid, mid + k*sd, mid - k*sd, sd

def rolling_min_idx(x, L, gap):
    """For each i: index of the minimum of x over [i-L, i-gap] (inclusive). nan-safe."""
    n = len(x); out = np.full(n, -1, dtype=np.int64)
    xs = pd.Series(x)
    # rolling over window L-gap+1 ending at i-gap
    w = L - gap + 1
    rm = xs.rolling(w).apply(lambda a: np.argmin(a), raw=True)  # position within window
    pos = rm.values
    for i in range(L, n):
        p = pos[i-gap]
        if not np.isnan(p): out[i] = i - gap - (w - 1) + int(p)
    return out

def rolling_max_idx(x, L, gap):
    return rolling_min_idx(-x, L, gap)

def add_indicators(df, bb_n=20, bb_k=2.0, rsi_n=14, atr_n=14):
    o, h, l, c = [df[k].values.astype(float) for k in ('open','high','low','close')]
    mid, up, lo, sd = bbands(c, bb_n, bb_k)
    df = df.copy()
    df['mid'], df['bb_up'], df['bb_lo'], df['bb_sd'] = mid, up, lo, sd
    df['rsi'] = rsi(c, rsi_n); df['atr'] = atr(h, l, c, atr_n)
    df['bw'] = (up - lo) / mid           # band width
    return df

def signals(df, L=40, gap=3, touch='low', rsi_margin=0.0, ref_rsi_max=None, cur_rsi_max=None):
    """Return boolean arrays (buy, sell) at bar i, plus reference index arrays.
    buy: bar touches lower band AND low[i] < min low over [i-L, i-gap] AND rsi[i] > rsi[argmin]+margin.
    sell: mirror. touch='low' uses the bar's low/high; 'close' uses the close."""
    h, l, c = df['high'].values, df['low'].values, df['close'].values
    r = df['rsi'].values; up = df['bb_up'].values; lo = df['bb_lo'].values
    n = len(df)
    jmin = rolling_min_idx(l, L, gap); jmax = rolling_max_idx(h, L, gap)
    ok = jmin >= 0
    idx = np.arange(n)
    refl = np.where(ok, l[np.clip(jmin, 0, n-1)], np.nan); refr_l = np.where(ok, r[np.clip(jmin, 0, n-1)], np.nan)
    refh = np.where(ok, h[np.clip(jmax, 0, n-1)], np.nan); refr_h = np.where(ok, r[np.clip(jmax, 0, n-1)], np.nan)
    if touch == 'low':
        tb = l <= lo; ts = h >= up
    else:
        tb = c <= lo; ts = c >= up
    buy = ok & tb & (l < refl) & (r > refr_l + rsi_margin)
    sell = ok & ts & (h > refh) & (r < refr_h - rsi_margin)
    if ref_rsi_max is not None:
        buy &= refr_l < ref_rsi_max; sell &= refr_h > 100 - ref_rsi_max
    if cur_rsi_max is not None:
        buy &= r < cur_rsi_max; sell &= r > 100 - cur_rsi_max
    buy &= ~np.isnan(r); sell &= ~np.isnan(r)
    return buy, sell, tb & ok, ts & ok, jmin, jmax

def fwd_stats(df, mask, direction, horizons=(4, 8, 16, 32, 64)):
    """Forward return from next bar open, in ATR units, signed by direction (+1 buy, -1 sell)."""
    o, c, a = df['open'].values, df['close'].values, df['atr'].values
    n = len(df); idx = np.where(mask)[0]; idx = idx[idx + 1 + max(horizons) < n]
    ent = o[idx + 1]; res = {}
    for hz in horizons:
        ret = direction * (c[idx + 1 + hz] - ent) / a[idx]
        ret = ret[~np.isnan(ret)]
        res[hz] = (len(ret), ret.mean(), (ret > 0).mean(), ret.mean() / (ret.std() / np.sqrt(len(ret))) if len(ret) > 2 else np.nan)
    return res
