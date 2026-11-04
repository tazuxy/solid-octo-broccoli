"""Round 13: chart patterns on H4/D1 rebuilt from M5 without the 16:55-17:30 EST bars (pre-registered in research/round13/r13_prereg.md).
Causal zigzag (pivot confirmed when the close retraces 2*ATR14 from the running extreme). Patterns: double top/bottom (P1 H4, P2 D1),
head-and-shoulders / inverse (P3 H4, P4 D1). Entry next bar open after a close through the neckline; stop beyond the peak/shoulder
+0.2 ATR; target = measured move; time exit after 60 bars. Output out/r10_r13_trades.parquet (evaluate: python3 -I code/r10_eval.py screen r13).
Usage (work dir): python3 -I code/r13_patterns.py"""
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
def bars(sym, tf):
    f = os.path.join(ROOT, 'bars_r11', 'XAUUSD_M5.parquet') if sym == 'XAUUSD' else os.path.join(ROOT, 'bars_m5', f'{sym}_M5.parquet')
    b = pd.read_parquet(f); m = b.index.hour * 60 + b.index.minute; b = b[~((m >= 16 * 60 + 55) & (m < 17 * 60 + 30))]
    agg = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'}
    if tf == 'H4': return b.resample('4h', label='left', closed='left').agg(agg).dropna()
    d = b.shift(freq='7h').resample('1D', label='left', closed='left').agg(agg).dropna(); d.index = d.index - pd.Timedelta('7h')
    return d
def simulate(o, h, l, n, e, d, sl, tp, maxbars):
    """returns exit price, exit bar index (entry at open of bar e)"""
    end = min(n - 1, e + maxbars)
    for j in range(e, end):
        if j > e:
            if d * (o[j] - sl) <= 0: return o[j], j
            if d * (o[j] - tp) >= 0: return o[j], j
        if (d == 1 and l[j] <= sl) or (d == -1 and h[j] >= sl): return sl, j
        if (d == 1 and h[j] >= tp) or (d == -1 and l[j] <= tp): return tp, j
    return o[end], end
def run(args):
    sym, tf = args
    b = bars(sym, tf); o, h, l, c = [b[k].values.astype(float) for k in ('open', 'high', 'low', 'close')]; idx = b.index; n = len(b)
    A = atr(h, l, c, 14)
    piv = []                                   # (type 'H'/'L', bar index, price)
    dirn = 0; ext_v = np.nan; ext_i = -1
    rows = []; busy = {'dbl': -1, 'hs': -1}; used = set()
    for i in range(15, n - 2):
        a = A[i]
        if not np.isfinite(a) or a <= 0: continue
        # running extreme of the current (unconfirmed) leg, including bar i
        if dirn == 0:
            dirn, ext_v, ext_i = 1, h[i], i
        elif dirn == 1 and h[i] > ext_v: ext_v, ext_i = h[i], i
        elif dirn == -1 and l[i] < ext_v: ext_v, ext_i = l[i], i
        # ---- pattern checks on the close of bar i (pivots confirmed before bar i + current leg extreme)
        sigs = []
        if dirn == 1 and len(piv) >= 2 and piv[-1][0] == 'L':           # tops: leg up after a confirmed low
            T = piv[-1]; P1 = piv[-2]; P2 = ext_v
            if abs(P2 - P1[2]) <= 0.5 * a and P2 - T[2] >= a and c[i] < T[2] and i - T[1] <= 60:
                top = max(P1[2], P2); sigs.append(('dbl', -1, top + 0.2 * a, T[2] - (top - T[2]), ('dbl', T[1], -1)))
            if len(piv) >= 4:
                T2, Hh, T1, LS = piv[-1], piv[-2], piv[-3], piv[-4]; RS = ext_v
                if RS < Hh[2] and Hh[2] - max(LS[2], RS) >= 0.5 * a and abs(LS[2] - RS) <= a and RS - T2[2] >= a and i - T2[1] <= 60:
                    nk = lambda k: T1[2] + (T2[2] - T1[2]) * (k - T1[1]) / (T2[1] - T1[1])
                    if c[i] < nk(i): sigs.append(('hs', -1, RS + 0.2 * a, nk(i) - (Hh[2] - nk(Hh[1])), ('hs', T2[1], -1)))
        if dirn == -1 and len(piv) >= 2 and piv[-1][0] == 'H':          # bottoms: leg down after a confirmed high
            T = piv[-1]; P1 = piv[-2]; P2 = ext_v
            if abs(P2 - P1[2]) <= 0.5 * a and T[2] - P2 >= a and c[i] > T[2] and i - T[1] <= 60:
                bot = min(P1[2], P2); sigs.append(('dbl', 1, bot - 0.2 * a, T[2] + (T[2] - bot), ('dbl', T[1], 1)))
            if len(piv) >= 4:
                T2, Hh, T1, LS = piv[-1], piv[-2], piv[-3], piv[-4]; RS = ext_v
                if RS > Hh[2] and min(LS[2], RS) - Hh[2] >= 0.5 * a and abs(LS[2] - RS) <= a and T2[2] - RS >= a and i - T2[1] <= 60:
                    nk = lambda k: T1[2] + (T2[2] - T1[2]) * (k - T1[1]) / (T2[1] - T1[1])
                    if c[i] > nk(i): sigs.append(('hs', 1, RS - 0.2 * a, nk(i) + (nk(Hh[1]) - Hh[2]), ('hs', T2[1], 1)))
        for kind, d, sl, tp, key in sigs:
            if key in used: continue
            used.add(key)
            for delay in (0, 1):
                e = i + 1 + delay
                if delay == 0 and i < busy[kind]: break                 # one position per pair and pattern type
                if e >= n - 1: continue
                ent = o[e]
                if d * (ent - sl) <= 0 or d * (tp - ent) <= 0: continue  # already beyond stop or target
                px, j = simulate(o, h, l, n, e, d, sl, tp, 60)
                if delay == 0: busy[kind] = j
                hyp = {('dbl', 'H4'): 'P1', ('dbl', 'D1'): 'P2', ('hs', 'H4'): 'P3', ('hs', 'D1'): 'P4'}[(kind, tf)]
                rows.append(dict(hyp=hyp, inst=sym, t_ent=idx[e], t_exit=idx[j], dir=d, gross_pips=d * (px - ent) / pip(sym),
                                 R_pips=abs(ent - sl) / pip(sym), cost_pips=cost(sym) / pip(sym), delay=delay, bars=j - e))
        # ---- zigzag confirmation on the close of bar i
        if dirn == 1 and c[i] <= ext_v - 2 * a:
            piv.append(('H', ext_i, ext_v)); dirn = -1; k = ext_i + int(np.argmin(l[ext_i:i + 1])); ext_v, ext_i = l[k], k
        elif dirn == -1 and c[i] >= ext_v + 2 * a:
            piv.append(('L', ext_i, ext_v)); dirn = 1; k = ext_i + int(np.argmax(h[ext_i:i + 1])); ext_v, ext_i = h[k], k
    return rows
if __name__ == '__main__':
    with Pool(4) as p: res = p.map(run, [(s, tf) for s in SYMS for tf in ('H4', 'D1')])
    T = pd.DataFrame([r for x in res for r in x]); T.to_parquet(os.path.join(OUT, 'r10_r13_trades.parquet'))
    z = T[T.delay == 0]; print(z.groupby(['hyp', 'dir']).size().unstack()); print(z.groupby('hyp').bars.median())
