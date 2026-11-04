"""Round 10: build trades for pre-registered hypotheses H1-H5 (research/round10/r10_prereg.md). Gross only; cost applied in r10_eval.py.
Data: histdata BID, fixed EST. Run from the work-dir copy of code/:  python3 -I code/r10_hyp.py
Output: out/r10_trades.parquet with columns hyp, inst, t_ent, t_exit, dir, gross_pips, R_pips, delay (0 = rule, 1 = one-bar-late entry).
Trades for all years are built here; r10_eval.py reads only < 2022 in screen mode."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sig import rsi, atr, bbands
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.environ.get('REPO', '/home/user/solid-octo-broccoli')
OUT = os.path.join(ROOT, 'out')
XP = {'AUDCAD', 'NZDCAD', 'CHFJPY', 'CADCHF', 'GBPCAD', 'EURCAD', 'AUDCHF', 'NZDCHF', 'GBPAUD', 'GBPNZD', 'EURNZD'}
def pip(p): return 0.01 if p.endswith('JPY') else 0.0001
_c = {}
def bars(p, tf):
    k = (p, tf)
    if k not in _c:
        if p in XP: f = os.path.join(ROOT, 'bars_x', f'{p}_{tf}.parquet')
        elif tf == 'M5': f = os.path.join(ROOT, 'bars_m5', f'{p}_M5.parquet')
        else: f = os.path.join(ROOT, 'bars_full', f'{p}_{tf}.parquet')
        _c[k] = pd.read_parquet(f)
    return _c[k]
def in_roll(ts):  # 16:55 <= t < 17:30 EST
    m = ts.hour * 60 + ts.minute
    return (m >= 16 * 60 + 55) & (m < 17 * 60 + 30)
def price_at(p, ts, delay=0, tf='M5', within='15min'):
    """open of the first bar at/after ts (outside the rollover window), within 15 min; delay = extra bars. Returns (time, price)."""
    b = bars(p, tf); idx = b.index; i = idx.searchsorted(ts)
    while i < len(idx) and in_roll(idx[i]): i += 1
    if i >= len(idx) or idx[i] - ts > pd.Timedelta(within): return None, np.nan
    i += delay
    while i < len(idx) and in_roll(idx[i]): i += 1
    if i >= len(idx): return None, np.nan
    return idx[i], float(b.open.iloc[i])
_atr = {}
def R_pips(p, t):
    """0.25 x ATR14 of the last D1 bar that closed before t (D1 bar label = 17:00 start, closes 24h later), in pips."""
    if p not in _atr:
        d = bars(p, 'D1'); a = atr(d.high.values, d.low.values, d.close.values, 14)
        _atr[p] = pd.Series(a, index=d.index + pd.Timedelta('24h'))
    s = _atr[p]; i = s.index.searchsorted(t, side='right') - 1
    if i < 14: return np.nan
    return 0.25 * s.iloc[i] / pip(p)

def fomc_dates():
    f = pd.read_csv(os.path.join(REPO, 'research', 'round10', 'fomc_dates.tsv'), sep='\t')
    return [pd.Timestamp(x) for x in f.date]
def prev_bd(d):
    d = d - pd.Timedelta(days=1)
    while d.dayofweek >= 5: d -= pd.Timedelta(days=1)
    return d

def timed(hyp, pairs_dirs, t_in, t_out, delay):
    rows = []
    for p, dirn in pairs_dirs:
        te, pe = price_at(p, t_in, delay); tx, px = price_at(p, t_out)
        if te is None or tx is None or tx <= te: continue
        r = R_pips(p, te)
        if not np.isfinite(r) or r <= 0: continue
        rows.append(dict(hyp=hyp, inst=p, t_ent=te, t_exit=tx, dir=dirn, gross_pips=dirn * (px - pe) / pip(p), R_pips=r, delay=delay))
    return rows

def h1_h2():
    rows = []
    for d in fomc_dates():
        pd_ = prev_bd(d)
        for delay in (0, 1):
            rows += timed('H1', [('EURUSD', 1), ('GBPUSD', 1), ('AUDUSD', 1), ('NZDUSD', 1), ('USDJPY', -1), ('USDCHF', -1), ('USDCAD', -1)],
                          pd_ + pd.Timedelta(hours=18), d + pd.Timedelta(hours=16), delay)
            rows += timed('H2', [('AUDJPY', 1), ('NZDJPY', 1), ('CADJPY', 1)], pd_ + pd.Timedelta(hours=11), d + pd.Timedelta(hours=11), delay)
    return rows

def gotobi():
    G = set()
    for y in range(2005, 2025):
        for m in range(1, 13):
            last = pd.Timestamp(y, m, 1) + pd.offsets.MonthEnd(0)
            for g in [pd.Timestamp(y, m, k) for k in (5, 10, 15, 20, 25, 30) if k <= last.day] + [last]:
                while g.dayofweek >= 5: g -= pd.Timedelta(days=1)
                G.add(g)
    bd = pd.bdate_range('2005-01-01', '2024-12-31')
    lastbd = set(pd.Series(bd, index=bd).groupby([bd.year, bd.month]).max())
    return sorted(g for g in G if g not in lastbd)
def h3():
    rows = []
    for g in gotobi():
        D = prev_bd(g)
        for delay in (0, 1):
            rows += timed('H3', [(p, 1) for p in ('EURJPY', 'GBPJPY', 'AUDJPY', 'NZDJPY', 'CADJPY', 'CHFJPY')],
                          D + pd.Timedelta(hours=8), g - pd.Timedelta(days=1) + pd.Timedelta(hours=19, minutes=55), delay)
    return rows

def h4_pair(p, delay):
    b = bars(p, 'M15'); o, h, l, c = [b[k].values.astype(float) for k in ('open', 'high', 'low', 'close')]
    R = rsi(c, 14); A = atr(h, l, c, 14); mid, up, lo, _ = bbands(c, 20, 2.0)
    idx = b.index; n = len(b); ts = idx.values
    close_t = idx + pd.Timedelta('15min'); cm = (close_t.hour * 60 + close_t.minute).values
    # session date = EST evening date: closes >= 19:00 belong to that date, closes <= 01:45 to the previous date
    sess = np.where(cm >= 19 * 60, close_t.normalize().values, (close_t.normalize() - pd.Timedelta(days=1)).values)
    sdow = pd.DatetimeIndex(sess).dayofweek.values
    insig = ((cm >= 19 * 60) | (cm <= 1 * 60 + 45)) & np.isin(sdow, (0, 1, 2, 3))
    span_ok = np.zeros(n, bool); span_ok[50:] = (ts[50:] - ts[:-50]) <= np.timedelta64(2, 'D')
    rows = []; i = 50
    while i < n - 2:
        if not (insig[i] and span_ok[i]) or not np.isfinite(A[i]) or A[i] <= 0 or not np.isfinite(R[i]):
            i += 1; continue
        dirn = -1 if (c[i] > up[i] and R[i] > 70) else (1 if (c[i] < lo[i] and R[i] < 30) else 0)
        if dirn == 0: i += 1; continue
        e = i + 1 + delay
        fx_t = pd.Timestamp(sess[i]) + pd.Timedelta(days=1, hours=3)       # 03:00 EST forced exit
        if e >= n or idx[e] >= fx_t or idx[e] - idx[i] > pd.Timedelta('1h'): i += 1; continue
        ent = o[e]; sl = ent - dirn * 3 * A[i]; px = None; j = e
        while j < n:
            if idx[j] >= fx_t: px = o[j]; break
            if j > e and dirn * (o[j] - sl) <= 0: px = o[j]; break
            if (dirn == 1 and l[j] <= sl) or (dirn == -1 and h[j] >= sl): px = sl; break
            if dirn * (c[j] - mid[j]) >= 0:                                 # close back at/through SMA20 -> next open
                if j + 1 < n: px = o[j + 1]; j += 1
                else: px = c[j]
                break
            j += 1
        if px is None: break
        r = R_pips(p, idx[e])
        if np.isfinite(r) and r > 0:
            rows.append(dict(hyp='H4', inst=p, t_ent=idx[e], t_exit=idx[min(j, n - 1)], dir=dirn, gross_pips=dirn * (px - ent) / pip(p), R_pips=r, delay=delay))
        i = max(j, i + 1)
    return rows

def h5_pair(p, delay):
    d = bars(p, 'D1'); c = d.close.values.astype(float); n = len(d)
    sma = pd.Series(c).rolling(20).mean().values; sd = pd.Series(c).rolling(20).std().values
    z = (c - sma) / sd; close_t = d.index + pd.Timedelta('24h')
    rows = []; i = 20
    while i < n - 1:
        if not np.isfinite(z[i]) or abs(z[i]) <= 2: i += 1; continue
        dirn = -1 if z[i] > 2 else 1
        te, pe = price_at(p, close_t[i] + pd.Timedelta('1h'), 0, 'M5', within='3D')
        if delay: te, pe = price_at(p, close_t[i] + pd.Timedelta('2h'), 0, 'M5', within='3D')
        if te is None: i += 1; continue
        k = i + 1
        while k < n and k - i < 10 and not (dirn * (c[k] - sma[k]) >= 0): k += 1
        if k >= n: break
        tx, px = price_at(p, close_t[k] + pd.Timedelta('1h'), 0, 'M5', within='3D')
        if tx is None or tx <= te: i = k + 1; continue
        r = R_pips(p, te)
        if np.isfinite(r) and r > 0:
            rows.append(dict(hyp='H5', inst=p, t_ent=te, t_exit=tx, dir=dirn, gross_pips=dirn * (px - pe) / pip(p), R_pips=r, delay=delay))
        i = k + 1          # flat after the exit close; next signal from the following close
    return rows

if __name__ == '__main__':
    rows = h1_h2() + h3()
    for p in ('AUDCAD', 'NZDCAD', 'AUDNZD'):
        for delay in (0, 1): rows += h4_pair(p, delay) + h5_pair(p, delay)
    T = pd.DataFrame(rows); T.to_parquet(os.path.join(OUT, 'r10_trades.parquet'))
    print(T.groupby(['hyp', 'delay']).size().unstack())
