"""Forward check of method 1 (Gotobi-eve USDJPY, month-end G skipped) on FXCM public M1 bid/ask, 2025-01-01 onward
(pre-registered in research/round10/r10_m1_forward_prereg.md). Buy at ASK open of the first M1 bar >= 08:00 EST on D, sell at BID open
of the first M1 bar >= 19:55 EST on G-1 (both within 15 minutes, else skipped). Reference distribution: method-1 trades 2005-2024
from histdata (0.5 pips cost), bootstrap of the mean with the same N (20,000 draws, seed 10).
Usage (from the work dir): python3 -I code/r10_m1_forward.py <FXCM_DIR>"""
import os, sys, glob, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r10_hyp as H
SRC = sys.argv[1]
fr = []
for f in sorted(glob.glob(os.path.join(SRC, 'USDJPY_202[56]_*.csv.gz'))):
    d = pd.read_csv(f); d['ts'] = pd.to_datetime(d.DateTime, format='%m/%d/%Y %H:%M:%S.%f') - pd.Timedelta('5h'); fr.append(d)
m = pd.concat(fr).drop_duplicates('ts').set_index('ts').sort_index()
m = m[m.index >= '2025-01-01']
weeks = sorted({(t.isocalendar().year, t.isocalendar().week) for t in m.index})
def at(ts):
    i = m.index.searchsorted(ts)
    if i >= len(m) or m.index[i] - ts > pd.Timedelta('15min'): return None
    return m.iloc[i]
def gotobi(y0, y1):
    G = set()
    for y in range(y0, y1 + 1):
        for mo in range(1, 13):
            last = pd.Timestamp(y, mo, 1) + pd.offsets.MonthEnd(0)
            for g in [pd.Timestamp(y, mo, k) for k in (5, 10, 15, 20, 25, 30) if k <= last.day] + [last]:
                while g.dayofweek >= 5: g -= pd.Timedelta(days=1)
                G.add(g)
    bd = pd.bdate_range(f'{y0}-01-01', f'{y1}-12-31')
    lastbd = set(pd.Series(bd, index=bd).groupby([bd.year, bd.month]).max())
    return sorted(g for g in G if g not in lastbd)
rows = []; skipped = 0
for g in gotobi(2025, 2026):
    D = H.prev_bd(g); t_in = D + pd.Timedelta(hours=8); t_out = g - pd.Timedelta(days=1) + pd.Timedelta(hours=19, minutes=55)
    if t_in < pd.Timestamp('2025-01-01') or t_out > m.index.max(): continue
    a, b = at(t_in), at(t_out)
    if a is None or b is None: skipped += 1; continue
    real = (b.BidOpen - a.AskOpen) / 0.01
    mid = ((b.BidOpen + b.AskOpen) / 2 - (a.BidOpen + a.AskOpen) / 2) / 0.01
    rows.append(dict(G=g, t_in=t_in, real=real, mid=mid, sp_in=(a.AskOpen - a.BidOpen) / 0.01, sp_out=(b.AskOpen - b.BidOpen) / 0.01))
F = pd.DataFrame(rows)
# reference: histdata 2005-2024, same rule, 0.5 pips
ref = []
for g in gotobi(2005, 2024):
    D = H.prev_bd(g)
    ref += H.timed('M1', [('USDJPY', 1)], D + pd.Timedelta(hours=8), g - pd.Timedelta(days=1) + pd.Timedelta(hours=19, minutes=55), 0)
Rf = pd.DataFrame(ref); r = Rf.gross_pips.values - 0.5
rng = np.random.default_rng(10); n = len(F)
boot = rng.choice(r, size=(20000, n), replace=True).mean(axis=1)
mu = F.real.mean(); pct = (boot < mu).mean()
t = mu / (F.real.std(ddof=1) / np.sqrt(n))
print(f'FXCM coverage: {m.index.min()} .. {m.index.max()}, ISO weeks with data: {len(weeks)}; Gotobi trades skipped for missing data: {skipped}')
print(f'forward N={n}  real mean {mu:+.2f} pips  t {t:.2f}  win {(F.real > 0).mean():.0%}  sum {F.real.sum():+.1f}  '
      f'maxDD {(F.real.cumsum() - F.real.cumsum().cummax().clip(lower=0)).min():.1f} pips')
print(f'mid-0.5: {(F.mid - 0.5).mean():+.2f} pips; paid spread mean {(F.mid - F.real).mean():.2f}; entry spread median {F.sp_in.median():.2f}, exit median {F.sp_out.median():.2f}')
print(f'reference 2005-2024 histdata: N={len(r)} mean {r.mean():+.2f}; bootstrap mean (N={n}) 5% {np.percentile(boot, 5):+.2f} 25% {np.percentile(boot, 25):+.2f} '
      f'50% {np.percentile(boot, 50):+.2f}; forward mean percentile = {pct:.1%}')
print('by year:', F.groupby(F.G.dt.year).real.agg(['size', 'mean', 'sum']).round(2).to_dict('index'))
F.to_csv(os.path.join(H.OUT, 'r10_m1_forward_trades.csv'), index=False)
