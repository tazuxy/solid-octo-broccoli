"""Round 10 H6: round-4 S1 'RSI / BB-mid' night scalp re-priced on REAL bid/ask (FXCM public M1, 2012-2024, index fixed EST).
Rule (unchanged from round 4): signal = M5 bar whose CLOSE time is 17:30-18:45 EST, EST Mon-Thu; RSI14 (bid closes) < 30 buy, > 70 sell;
  entry next M5 open (must be < 19:00); TP = BB20 middle (bid) at signal, SL = entry -/+ 2*ATR14 (bid); forced exit at the open of the
  first bar >= 19:00 EST; one position per pair; max one trade per pair per night per direction; skip if TP not beyond entry.
Fills: long buys at ASK open, exits on BID (TP/SL triggered and filled on bid); short sells at BID open, exits on ASK.
  Intrabar SL before TP; a bar opening beyond SL/TP fills at its open.
Also computes the same trade on MID prices (same entry/exit bars and levels shifted to mid) so that cost = mid result - real result.
Output: <WORK>/out/r10_h6_trades.parquet (gross_pips = mid result, cost_pips = real spread paid) and r10_spreads.csv (hourly spread table).
Usage: python3 -I code/r10_h6.py <FXCM_PQ_DIR>"""
import os, sys, numpy as np, pandas as pd
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sig import rsi, atr, bbands
import r10_hyp as H
PQ = sys.argv[1]; OUT = H.OUT
PAIRS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF', 'NZDUSD']

def m5(p):
    m = pd.read_parquet(os.path.join(PQ, f'{p}_M1BA.parquet'))
    agg = {'bo': 'first', 'bh': 'max', 'bl': 'min', 'bc': 'last', 'ao': 'first', 'ah': 'max', 'al': 'min', 'ac': 'last'}
    return m.resample('5min', label='left', closed='left').agg(agg).dropna()

def run_pair(args):
    p, delay = args
    b = m5(p); P = H.pip(p)
    bo, bh, bl, bc, ao, ah, al, ac = [b[k].values.astype(float) for k in ('bo', 'bh', 'bl', 'bc', 'ao', 'ah', 'al', 'ac')]
    R = rsi(bc, 14); A = atr(bh, bl, bc, 14); mid, up, lo, _ = bbands(bc, 20, 2.0)
    idx = b.index; ts = idx.values; n = len(b)
    cl = idx + pd.Timedelta('5min'); closemin = (cl.hour * 60 + cl.minute).values; openmin = (idx.hour * 60 + idx.minute).values
    day = idx.normalize().values; dow = idx.dayofweek.values
    span_ok = np.zeros(n, bool); span_ok[50:] = (ts[50:] - ts[:-50]) <= np.timedelta64(1, 'D')
    cand = np.where((closemin >= 17 * 60 + 30) & (closemin <= 18 * 60 + 45) & np.isin(dow, (0, 1, 2, 3)) & span_ok & (openmin < 19 * 60))[0]
    rows = []
    for d0 in np.unique(day[cand]):
        ib = cand[day[cand] == d0]; k = ib[-1] + 1
        while k < n and day[k] == d0 and openmin[k] < 19 * 60: k += 1
        if not (k < n and day[k] == d0): continue           # no bar at/after 19:00 that evening -> skip night (data gap)
        fx_i = k; used = set(); free_from = -1
        for i in ib:
            if i < free_from: continue
            dirn = 1 if R[i] < 30 else (-1 if R[i] > 70 else 0)
            if dirn == 0 or dirn in used or not np.isfinite(A[i]) or A[i] <= 0: continue
            e = i + 1 + delay
            if e >= fx_i or day[e] != d0: continue
            ent = ao[e] if dirn == 1 else bo[e]                 # real fill
            tp = mid[i]; sl = ent - dirn * 2 * A[i]
            if dirn * (tp - ent) <= 0: continue
            # exit side series: long exits on bid, short exits on ask
            xo, xh, xl = (bo, bh, bl) if dirn == 1 else (ao, ah, al)
            px = None; why = ''
            for j in range(e, fx_i):
                if j > e:
                    if dirn * (xo[j] - sl) <= 0: px, why = xo[j], 'sl'; break
                    if dirn * (xo[j] - tp) >= 0: px, why = xo[j], 'tp'; break
                lowx = xl[j] if dirn == 1 else -xh[j]; hix = xh[j] if dirn == 1 else -xl[j]
                if lowx <= dirn * sl: px, why = sl, 'sl'; break
                if hix >= dirn * tp: px, why = tp, 'tp'; break
            if px is None: j, px, why = fx_i, xo[fx_i], 'time'
            real = dirn * (px - ent)
            hs_in = (ao[e] - bo[e]) / 2; hs_out = (ao[j] - bo[j]) / 2        # half spreads at the entry / exit bar opens
            midres = real + hs_in + hs_out                                      # same trade on mid prices
            r = H.R_pips(p, idx[e])
            if not np.isfinite(r) or r <= 0: continue
            rows.append(dict(hyp='H6', inst=p, t_ent=idx[e], t_exit=idx[j], dir=dirn, reason=why, delay=delay,
                             gross_pips=midres / P, cost_pips=(midres - real) / P, real_pips=real / P, R_pips=r,
                             spread_in=2 * hs_in / P, spread_out=2 * hs_out / P))
            used.add(dirn); free_from = j
    return rows

def spreads(p):
    m = pd.read_parquet(os.path.join(PQ, f'{p}_M1BA.parquet')); P = H.pip(p)
    s = (m.ao - m.bo) / P; hh = m.index.hour + (m.index.minute >= 30) * 0.5
    per = np.where(m.index.year <= 2016, '2012-16', np.where(m.index.year <= 2021, '2017-21', '2022-24'))
    g = pd.DataFrame(dict(s=s.values, hh=hh, per=per)).groupby(['per', 'hh']).s.median().unstack(0)
    g.insert(0, 'pair', p); return g.reset_index()

if __name__ == '__main__':
    with Pool(4) as pool:
        res = pool.map(run_pair, [(p, d) for p in PAIRS for d in (0, 1)])
        sp = pool.map(spreads, PAIRS + ['AUDCAD', 'NZDCAD', 'AUDNZD'])
    T = pd.DataFrame([r for x in res for r in x]); T.to_parquet(os.path.join(OUT, 'r10_h6_trades.parquet'))
    pd.concat(sp).to_csv(os.path.join(OUT, 'r10_spreads.csv'), index=False)
    print(T.groupby(['delay']).size(), T[T.delay == 0].groupby('inst').size().to_dict())
