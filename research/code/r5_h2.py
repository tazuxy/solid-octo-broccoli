"""R5 H2 round-number levels (Osler). Levels = multiples of 100 pips (big figure: 1.1000, 1.1100 / 110.00, 111.00).
Prices converted to pips rounded to 0.1 pip. NY day = 17:00-17:00 EST.
(a) FADE: first bar of the NY day whose [low,high] contains level L (touched-level closest to the bar open; open==L skipped);
    open < L -> touched from below -> SELL at next open; open > L -> BUY. TP 10 pips, SL = L +/- 10 pips, time stop 12 bars (close of 12th bar).
(b) BREAK: bar i closes >= 10 pips beyond L (L = nearest level with close-10p >= L for up), price was on the other side of L
    (low<L for up / high>L for down) within bars i-3..i, and close[i-1] not yet 10 pips beyond (first such close).
    Enter break direction at open i+1; TP 15 pips; SL = L -/+ 5 pips; time stop 24 bars.
Both: one position per pair at a time; entry bar must follow signal bar within 10 min; holding window cut at any data gap > 60 min
(exit at close of the last bar before the gap). Delay variant: entry at open i+2, TP re-based on the new entry, same SL, same holding length.
R = |entry - SL|. SL before TP in the same bar."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r5_common import *

PAIRS = DESIGN + ['EURJPY', 'GBPJPY', 'EURGBP', 'AUDJPY']
STEP = 100.0

def signals(b, pip):
    o = np.round(b.open.values / pip, 1); h = np.round(b.high.values / pip, 1)
    l = np.round(b.low.values / pip, 1); c = np.round(b.close.values / pip, 1)
    ts = b.index; nyday = ((ts - pd.Timedelta('17h')).normalize()).values
    # ---- fade
    klo = np.ceil(l / STEP); khi = np.floor(h / STEP)
    touched = klo <= khi
    below = np.ceil(o / STEP) * STEP; above = np.floor(o / STEP) * STEP   # nearest level >= open / <= open
    up_ok = touched & (below <= h); dn_ok = touched & (above >= l)
    dist_up = np.where(up_ok, below - o, np.inf); dist_dn = np.where(dn_ok, o - above, np.inf)
    L = np.where(dist_up <= dist_dn, below, above)
    side = np.where(o < L, 1, np.where(o > L, -1, 0))   # +1 approached from below
    idx = np.where(touched & (np.isfinite(dist_up) | np.isfinite(dist_dn)))[0]
    f = pd.DataFrame({'i': idx, 'day': nyday[idx], 'L': L[idx], 'side': side[idx]})
    f = f.drop_duplicates(['day', 'L'], keep='first')
    f = f[f.side != 0]
    fade = [(int(i), float(Lv), int(-s)) for i, Lv, s in zip(f.i, f.L, f.side)]   # trade dir = -side
    # ---- break
    lo4 = pd.Series(l).rolling(4, min_periods=4).min().values; hi4 = pd.Series(h).rolling(4, min_periods=4).max().values
    Lu = np.floor((c - 10) / STEP) * STEP; Ld = np.ceil((c + 10) / STEP) * STEP
    cp = np.roll(c, 1); cp[0] = np.nan
    up = (lo4 < Lu) & (cp < Lu + 10); dn = (hi4 > Ld) & (cp > Ld - 10)
    brk = [(int(i), float(Lu[i]), 1) for i in np.where(up)[0]] + [(int(i), float(Ld[i]), -1) for i in np.where(dn)[0]]
    brk.sort()
    return fade, brk, (o, h, l, c)

def run_one(pair, kind, delay):
    b = load_m5(pair); pip = PIP[pair]; ts = b.index.values
    fade, brk, (o, h, l, c) = signals(b, pip)
    gap_after = np.concatenate([np.diff(ts) > np.timedelta64(60, 'm'), [True]])   # gap after bar j
    first_ok = b.index[0] + pd.Timedelta('30D'); sigs = fade if kind == 'a' else brk
    hold = 12 if kind == 'a' else 24; busy_until = -1; rows = []
    n = len(o)
    for i, Lv, d in sigs:
        if i <= busy_until or b.index[i] < first_ok: continue
        i0 = i + 1 + delay
        if i0 + 1 >= n or (ts[i0] - ts[i]) > np.timedelta64(10 + 5 * delay, 'm') or gap_after[i:i0].any(): continue
        e = o[i0]
        if kind == 'a': tp = e + d * 10; sl = Lv - d * 10
        else: tp = e + d * 15; sl = Lv - d * 5
        if (d > 0 and e <= sl) or (d < 0 and e >= sl): continue
        i1 = min(i0 + hold - 1, n - 1)
        g = np.where(gap_after[i0:i1 + 1])[0]
        if len(g): i1 = i0 + int(g[0])
        px, why, j = sim_path(o, h, l, i0, i1, d, tp, sl)
        if px is None: px, j = c[i1], i1
        busy_until = j
        rows.append(dict(inst=pair, t_ent=b.index[i0], dir=d, level=Lv, entry=e, gross_pips=d * (px - e), R_pips=abs(e - sl), why=why))
    return pd.DataFrame(rows)

if __name__ == '__main__':
    from multiprocessing import Pool
    jobs = [(p, k, dl) for p in PAIRS for k in ('a', 'b') for dl in (0, 1)]
    with Pool(4) as pool: res = pool.starmap(run_one, jobs)
    out = []
    for (p, k, dl), df in zip(jobs, res):
        df['var'] = 'H2' + k; df['mode'] = 'delay' if dl else 'base'; out.append(df)
    tr = pd.concat(out, ignore_index=True); tr['group'] = tr.inst.map(group_of); tr['cost_pips'] = USER_COST
    tr.to_parquet(os.path.join(OUT, 'r5_h2_trades.parquet'))
    tr['gR'] = tr.gross_pips / tr.R_pips
    print(tr.groupby(['var', 'mode']).agg(N=('gR', 'size'), g=('gross_pips', 'mean'), gR=('gR', 'mean'), R=('R_pips', 'median')).round(3))
    print(tr.groupby(['var', 'mode', 'why']).size())
