"""Candle Streak indicator test. Signal = bar where the same-colour streak reaches exactly N (indicator default marking).
FOLLOW = trade in the streak direction, FADE = against it. Entry next bar open. Costs from bt.COST_PIPS."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import numpy as np, pandas as pd
from sig import atr
from bt import PIP, COST_PIPS
from multiprocessing import Pool
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESIGN = ['EURUSD','GBPUSD','USDJPY','AUDUSD','USDCAD','USDCHF','NZDUSD','XAUUSD']
CROSS = ['EURJPY','GBPJPY','EURGBP','AUDJPY','EURAUD','EURCHF','CADJPY','AUDNZD','NZDJPY','GBPCHF']
TFS = ['M15','H1','H4','D1']; NS = [5, 8]; HS = [4, 16]
def streak(x):
    out = np.zeros(len(x), int); c = 0
    for i, v in enumerate(x):
        c = c + 1 if v else 0; out[i] = c
    return out
def sim(o, h, l, c, a, idx, d, cost, sl=1.5, tp=1.5, mb=16):
    """symmetric bracket trade: SL/TP in ATR of signal bar, time stop mb bars. returns net R (risk = sl*ATR)."""
    n = len(c); res = np.full(len(idx), np.nan)
    for k, (i, di) in enumerate(zip(idx, d)):
        if i + 1 >= n: continue
        e = o[i+1]; risk = sl * a[i]; s = e - di*risk; t = e + di*tp*a[i]; ex = None
        for j in range(i+1, min(n, i+1+mb)):
            if di == 1:
                if l[j] <= s: ex = s; break
                if h[j] >= t: ex = t; break
            else:
                if h[j] >= s: ex = s; break
                if l[j] <= t: ex = t; break
        if ex is None: ex = c[min(n-1, i+mb)]
        res[k] = (di*(ex - e) - cost) / risk
    return res
def job(args):
    pair, tf = args
    df = pd.read_parquet(os.path.join(ROOT, 'bars_full', f'{pair}_{tf}.parquet'))
    o, h, l, c = [df[k].values.astype(float) for k in ('open','high','low','close')]
    a = atr(h, l, c, 14); cost = COST_PIPS[pair] * PIP[pair]
    bull = streak(c > o); bear = streak(c < o)
    rows = []
    for N in NS:
        for side, m in (('bull', bull == N), ('bear', bear == N)):
            idx = np.where(m & ~np.isnan(a))[0]; idx = idx[(idx > 200) & (idx + 1 + max(HS) < len(c))]
            sdir = 1 if side == 'bull' else -1
            t = df.index[idx]
            for mode, mult in (('FOLLOW', 1), ('FADE', -1)):
                d = sdir * mult
                rec = {'pair': pair, 'tf': tf, 'N': N, 'side': side, 'mode': mode, 't': t}
                for H in HS:
                    g = d * (c[idx + 1 + H - 1] - o[idx + 1]) / a[idx]   # hold H bars: from open[i+1] to close[i+H]
                    rec[f'g{H}'] = g; rec[f'n{H}'] = g - cost / a[idx]
                rec['bracket'] = sim(o, h, l, c, a, idx, np.full(len(idx), d), cost)
                rows.append(rec)
    return rows
if __name__ == '__main__':
    jobs = [(p, tf) for tf in TFS for p in DESIGN + CROSS]
    with Pool(4) as pool: out = pool.map(job, jobs)
    recs = []
    for rr in out:
        for r in rr:
            k = len(r['t'])
            dfr = pd.DataFrame({'t': r['t'], **{x: r[x] for x in ('g4','n4','g16','n16','bracket')}})
            for x in ('pair','tf','N','side','mode'): dfr[x] = r[x]
            recs.append(dfr)
    T = pd.concat(recs, ignore_index=True)
    T['group'] = np.where(T.pair.isin(DESIGN), 'D', 'C')
    T['per'] = pd.cut(T.t.dt.year, [2004, 2011, 2018, 2024], labels=['05-11','12-18','19-24'])
    T.to_parquet(os.path.join(ROOT, 'out', 'st_signals.parquet'))
    print('saved', len(T))
