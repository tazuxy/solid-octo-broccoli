"""Round 4 S1: early-morning JST (17:30-18:45 EST) M5 mean-reversion scalping, 17 FX pairs, 2005-2024.
Pre-registered rules (fixed before any result):
  signal bar = M5 bar whose CLOSE is in [17:30, 18:45] EST, EST weekday Mon-Thu; entry = next M5 bar open (must be < 19:00).
  signals: 'rsi' RSI14<30 buy / >70 sell ; 'bb' close < BB(20,2) lower buy / > upper sell.
  exits:   'mid' TP = BB20 middle at signal, SL = entry -/+ 2*ATR14 ; 'atr' TP = 1*ATR, SL = 3*ATR. R unit = SL distance.
           forced exit at open of the first bar >= 19:00 EST (or last close before it if missing).
  one position per pair; max 1 trade per pair per night per direction; 'mid' signal skipped if TP not beyond entry.
  intrabar: SL checked before TP (conservative); a bar opening beyond SL/TP fills at its open.
  data guard: skip signal if bars i-50..i span > 1 day (data gaps, AUDJPY 2012); first 30 days of each pair not traded.
Placebo (reported only): same rules, signal-bar closes 08:00-10:45 EST, forced exit 11:00, Mon-Fri.
Output: out/r4_s1_trades.parquet (gross pnl in price + pips; cost applied in eval)."""
import os, sys, numpy as np, pandas as pd
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sig import rsi, atr, bbands
from r4_common import ROOT, OUT, DESIGN, CROSS, PIP

WINDOWS = {'night': (17*60+30, 18*60+45, 19*60, (0, 1, 2, 3)),
           'placebo': (8*60, 10*60+45, 11*60, (0, 1, 2, 3, 4))}

def run_pair(p):
    b = pd.read_parquet(os.path.join(ROOT, 'bars_m5', f'{p}_M5.parquet'))
    o, h, l, c = [b[k].values.astype(float) for k in ('open', 'high', 'low', 'close')]
    R = rsi(c, 14); A = atr(h, l, c, 14); mid, up, lo, _ = bbands(c, 20, 2.0)
    ts = b.index.values; n = len(b)
    closemin = ((b.index + pd.Timedelta('5min')).hour * 60 + (b.index + pd.Timedelta('5min')).minute).values
    openmin = (b.index.hour * 60 + b.index.minute).values
    day = b.index.normalize().values; dow = b.index.dayofweek.values
    span_ok = np.zeros(n, bool); span_ok[50:] = (ts[50:] - ts[:-50]) <= np.timedelta64(1, 'D')
    start_ok = ts >= ts[0] + np.timedelta64(30, 'D')
    rows = []
    for wname, (c0, c1, fx, dows) in WINDOWS.items():
        # signal bars in window; group by day
        cand = np.where((closemin >= c0) & (closemin <= c1) & np.isin(dow, dows) & span_ok & start_ok & (openmin < fx))[0]
        days = day[cand]
        for d0 in np.unique(days):
            ib = cand[days == d0]
            # forced-exit bar: first bar index with same day and openmin >= fx (else last bar before fx)
            last = ib[-1]; k = last + 1
            while k < n and day[k] == d0 and openmin[k] < fx: k += 1
            if k < n and day[k] == d0: fx_i, fx_px, fx_use_open = k, o[k], True
            else: fx_i, fx_px, fx_use_open = k - 1, c[k - 1], False
            for sig in ('rsi', 'bb'):
                for ex in ('mid', 'atr'):
                    used = set(); free_from = -1
                    for i in ib:
                        if i < free_from: continue
                        if sig == 'rsi': dirn = 1 if R[i] < 30 else (-1 if R[i] > 70 else 0)
                        else: dirn = 1 if c[i] < lo[i] else (-1 if c[i] > up[i] else 0)
                        if dirn == 0 or dirn in used or np.isnan(A[i]) or A[i] <= 0: continue
                        e = i + 1
                        if e >= fx_i + (0 if fx_use_open else 1) or day[e] != d0: continue
                        ent = o[e]
                        if ex == 'mid':
                            tp = mid[i]; sl = ent - dirn * 2 * A[i]
                            if dirn * (tp - ent) <= 0: continue
                        else:
                            tp = ent + dirn * A[i]; sl = ent - dirn * 3 * A[i]
                        risk = abs(ent - sl); px = None; why = ''
                        endj = fx_i if fx_use_open else fx_i + 1
                        for j in range(e, endj):
                            if j > e:   # gap at bar open
                                if dirn * (o[j] - sl) <= 0: px, why = o[j], 'sl'; break
                                if dirn * (o[j] - tp) >= 0: px, why = o[j], 'tp'; break
                            lowx = l[j] if dirn == 1 else -h[j]; hix = h[j] if dirn == 1 else -l[j]
                            if lowx <= dirn * sl: px, why = sl, 'sl'; break
                            if hix >= dirn * tp: px, why = tp, 'tp'; break
                        if px is None: px, why, j = fx_px, 'time', fx_i
                        both = int(why == 'sl' and (h[j] >= tp if dirn == 1 else l[j] <= tp)) if why == 'sl' else 0
                        gross = dirn * (px - ent)
                        rows.append(dict(pair=p, win=wname, sig=sig, ex=ex, t_sig=ts[i], t_ent=ts[e], dir=dirn, entry=ent, exit=px,
                                         reason=why, bars=j - e + 1, risk=risk, atr=A[i], gross_pips=gross / PIP[p],
                                         risk_pips=risk / PIP[p], r_gross=gross / risk, both=both,
                                         bar_rng_atr=(h[i] - l[i]) / A[i]))
                        used.add(dirn); free_from = j
    return pd.DataFrame(rows)

if __name__ == '__main__':
    with Pool(4) as pool: dfs = pool.map(run_pair, DESIGN + CROSS)
    tr = pd.concat(dfs, ignore_index=True)
    tr.to_parquet(os.path.join(OUT, 'r4_s1_trades.parquet'))
    print(tr.groupby(['win', 'sig', 'ex']).agg(N=('r_gross', 'size'), avgRg=('r_gross', 'mean'), gpips=('gross_pips', 'mean'),
                                                  riskp=('risk_pips', 'median'), both=('both', 'mean')).round(4))
