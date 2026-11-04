"""Round 15: ORZ-style multi-timeframe entries (pre-registered in research/round15/r15_prereg.md).
O1 pullback H1/M5, O2 pullback H4/M15, O3 range reversal H1/M5. Axis-bar zone touch arms a setup; the lower TF must show
low L1 -> high H -> low L2 (L2 >= L1 - 0.1 ATR_axis) and a close above H (mirror for shorts) before the window ends or the zone breaks.
Stop beyond the LTF pattern, target = previous swing extreme (O1/O2) or the opposite range zone (O3); skip if reward < 2 x risk.
Output out/r10_r15_trades.parquet (evaluate: TMIN=2.5 / 3.0 python3 -I code/r10_eval.py screen r15). Usage: python3 -I code/r15_orz.py"""
import os, sys, numpy as np, pandas as pd
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sig import atr
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, 'out')
FX = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF', 'NZDUSD', 'EURJPY', 'GBPJPY', 'EURGBP', 'AUDJPY', 'EURAUD',
      'EURCHF', 'CADJPY', 'AUDNZD', 'NZDJPY', 'GBPCHF']
SYMS = FX + ['XAUUSD']
def pip(s): return 1.0 if s == 'XAUUSD' else (0.01 if s.endswith('JPY') else 0.0001)
def cost(s): return 0.30 if s == 'XAUUSD' else 0.5 * pip(s)
AGG = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'}
def m5(sym):
    f = os.path.join(ROOT, 'bars_r11', 'XAUUSD_M5.parquet') if sym == 'XAUUSD' else os.path.join(ROOT, 'bars_m5', f'{sym}_M5.parquet')
    b = pd.read_parquet(f); m = b.index.hour * 60 + b.index.minute
    return b[~((m >= 16 * 60 + 55) & (m < 17 * 60 + 30))]
def rs(b, rule): return b.resample(rule, label='left', closed='left').agg(AGG).dropna()
def zigzag(h, l, c, A):
    """causal zigzag; returns for each bar i the list index up to which pivots are confirmed, and the pivot list (type, idx, price)"""
    piv = []; n_conf = np.zeros(len(c), int); d = 0; ev = np.nan; ei = -1
    for i in range(len(c)):
        a = A[i]
        if np.isfinite(a) and a > 0:
            if d == 0: d, ev, ei = 1, h[i], i
            elif d == 1 and h[i] > ev: ev, ei = h[i], i
            elif d == -1 and l[i] < ev: ev, ei = l[i], i
            if d == 1 and c[i] <= ev - 2 * a:
                piv.append(('H', ei, ev)); d = -1; k = ei + int(np.argmin(l[ei:i + 1])); ev, ei = l[k], k
            elif d == -1 and c[i] >= ev + 2 * a:
                piv.append(('L', ei, ev)); d = 1; k = ei + int(np.argmax(h[ei:i + 1])); ev, ei = h[k], k
        n_conf[i] = len(piv)
    return piv, n_conf
def fractals(h, l):
    n = len(h); fh = np.zeros(n, bool); fl = np.zeros(n, bool)
    fh[2:-2] = (h[2:-2] > h[1:-3]) & (h[2:-2] > h[:-4]) & (h[2:-2] >= h[3:-1]) & (h[2:-2] >= h[4:])
    fl[2:-2] = (l[2:-2] < l[1:-3]) & (l[2:-2] < l[:-4]) & (l[2:-2] <= l[3:-1]) & (l[2:-2] <= l[4:])
    return fh, fl
def ltf_trigger(L, k0, k1, d, A, zone_break):
    """scan lower-TF bars k0..k1 (inclusive). d=+1 long: L1 -> H -> L2 (>= L1 - 0.1A) -> close > H. Returns (entry bar, stop) or None."""
    o, h, l, c, fh, fl = L
    L1 = H = L2 = None
    for k in range(k0 + 2, k1 + 1):
        j = k - 2                                  # fractal at j is confirmed at the close of k
        if d == 1:
            if c[k] < zone_break: return None
            if fl[j] and j >= k0:
                if L1 is None or (H is None and l[j] < L1[1]): L1 = (j, l[j])
                elif H is not None:
                    if l[j] >= L1[1] - 0.1 * A: L2 = (j, l[j]) if L2 is None or l[j] < L2[1] else L2
                    else: L1, H, L2 = (j, l[j]), None, None
            if fh[j] and j >= k0 and L1 is not None and j > L1[0] and L2 is None:
                H = (j, h[j]) if H is None or h[j] > H[1] else H
            if L2 is not None and H is not None and c[k] > H[1] and k + 1 <= k1 + 1:
                return k + 1, min(L1[1], L2[1]) - 0.1 * A
        else:
            if c[k] > zone_break: return None
            if fh[j] and j >= k0:
                if L1 is None or (H is None and h[j] > L1[1]): L1 = (j, h[j])
                elif H is not None:
                    if h[j] <= L1[1] + 0.1 * A: L2 = (j, h[j]) if L2 is None or h[j] > L2[1] else L2
                    else: L1, H, L2 = (j, h[j]), None, None
            if fl[j] and j >= k0 and L1 is not None and j > L1[0] and L2 is None:
                H = (j, l[j]) if H is None or l[j] < H[1] else H
            if L2 is not None and H is not None and c[k] < H[1]:
                return k + 1, max(L1[1], L2[1]) + 0.1 * A
    return None
def simulate(L, idx, e, d, sl, tp, t_max):
    o, h, l, c = L[:4]; n = len(o)
    for j in range(e, n):
        t = idx[j]
        if t >= t_max or (t.dayofweek == 4 and t.hour >= 16): return o[j], j, 'time'
        if j > e:
            if d * (o[j] - sl) <= 0: return o[j], j, 'sl'
            if d * (o[j] - tp) >= 0: return o[j], j, 'tp'
        if (d == 1 and l[j] <= sl) or (d == -1 and h[j] >= sl): return sl, j, 'sl'
        if (d == 1 and h[j] >= tp) or (d == -1 and l[j] <= tp): return tp, j, 'tp'
    return c[n - 1], n - 1, 'end'
def run(args):
    sym, hyp = args
    axis_rule, ltf_rule, win_bars, tmax = {'O1': ('1h', '5min', 12, '72h'), 'O2': ('4h', '15min', 12, '240h'), 'O3': ('1h', '5min', 12, '72h')}[hyp]
    b5 = m5(sym); X = rs(b5, axis_rule); Lb = b5 if ltf_rule == '5min' else rs(b5, ltf_rule)
    xo, xh, xl, xc = [X[k].values.astype(float) for k in ('open', 'high', 'low', 'close')]; xi = X.index
    s20, s50, s100 = [pd.Series(xc).rolling(n).mean().values for n in (20, 50, 100)]; A = atr(xh, xl, xc, 14)
    piv, nconf = zigzag(xh, xl, xc, A)
    lo, lh, ll, lc = [Lb[k].values.astype(float) for k in ('open', 'high', 'low', 'close')]; li = Lb.index
    fh, fl = fractals(lh, ll); L = (lo, lh, ll, lc, fh, fl)
    step = pd.Timedelta(axis_rule)
    rows = []; armed = {1: True, -1: True}; busy_until = li[0]
    for i in range(110, len(xc) - 1):
        a = A[i]
        if not np.isfinite(a) or a <= 0: continue
        P = piv[:nconf[i - 1]]                                          # pivots confirmed by the previous axis bar
        if len(P) < 4: continue
        Hs = [p for p in P if p[0] == 'H'][-2:]; Ls = [p for p in P if p[0] == 'L'][-2:]
        if len(Hs) < 2 or len(Ls) < 2: continue
        # re-arm
        if not armed[1] and xc[i] > s20[i]: armed[1] = True
        if not armed[-1] and xc[i] < s20[i]: armed[-1] = True
        t_close = xi[i] + step
        if t_close < busy_until: continue
        setups = []
        if hyp in ('O1', 'O2'):
            up = s100[i - 1] > s100[i - 11] and np.all(xc[i - 5:i] > s100[i - 5:i]) and Hs[1][2] > Hs[0][2] and Ls[1][2] > Ls[0][2]
            dn = s100[i - 1] < s100[i - 11] and np.all(xc[i - 5:i] < s100[i - 5:i]) and Hs[1][2] < Hs[0][2] and Ls[1][2] < Ls[0][2]
            if up and armed[1] and xl[i] <= s50[i] + 0.2 * a: setups.append((1, s50[i] - 0.5 * a, Hs[1][2]))
            if dn and armed[-1] and xh[i] >= s50[i] - 0.2 * a: setups.append((-1, s50[i] + 0.5 * a, Ls[1][2]))
        else:
            flat = abs(s100[i] - s100[i - 10]) < 0.5 * a
            if flat and abs(Hs[1][2] - Hs[0][2]) <= 0.5 * a and abs(Ls[1][2] - Ls[0][2]) <= 0.5 * a:
                up_lo, up_hi = min(Hs[0][2], Hs[1][2]) - 0.3 * a, max(Hs[0][2], Hs[1][2]) + 0.2 * a
                dn_lo, dn_hi = min(Ls[0][2], Ls[1][2]) - 0.2 * a, max(Ls[0][2], Ls[1][2]) + 0.3 * a
                if dn_hi < up_lo:
                    if armed[-1] and xh[i] >= up_lo and xc[i] <= up_hi: setups.append((-1, up_hi, dn_hi))
                    if armed[1] and xl[i] <= dn_hi and xc[i] >= dn_lo: setups.append((1, dn_lo, up_lo))
        for d, zone_break, tp in setups:
            armed[d] = False
            k0 = li.searchsorted(t_close); k1 = li.searchsorted(t_close + win_bars * step) - 1
            if k1 <= k0 + 3: continue
            r = ltf_trigger(L, k0, k1, d, a, zone_break)
            if r is None: continue
            e, sl = r
            if e >= len(lo): continue
            te = li[e]
            if te.dayofweek == 4 and te.hour >= 12: continue
            ent = lo[e]; risk = d * (ent - sl)
            if risk <= 0 or d * (tp - ent) < 2 * risk: continue
            px, j, why = simulate(L, li, e, d, sl, tp, te + pd.Timedelta(tmax))
            busy_until = li[j]
            rows.append(dict(hyp=hyp, inst=sym, t_ent=te, t_exit=li[j], dir=d, gross_pips=d * (px - ent) / pip(sym),
                             R_pips=risk / pip(sym), cost_pips=cost(sym) / pip(sym), delay=0, why=why))
            break
    return rows
if __name__ == '__main__':
    with Pool(4) as p: res = p.map(run, [(s, h) for h in ('O1', 'O2', 'O3') for s in SYMS])
    T = pd.DataFrame([r for x in res for r in x]); T.to_parquet(os.path.join(OUT, 'r10_r15_trades.parquet'))
    print(T.groupby(['hyp', 'dir']).size().unstack()); print(T.groupby(['hyp', 'why']).size().unstack())
    print(T.groupby('hyp').R_pips.median())
