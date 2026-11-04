"""Round 15 O4: method 2 with a lower-TF trigger (pre-registered in research/round15/r15_prereg.md).
On Gotobi days, from 09:55 to 10:55 JST wait on M5 for fractal high H1 -> low L -> high H2 (H2 <= H1 + 0.1R) -> close below L; sell at the
next M5 open; stop entry + 1R; exit 15:00 JST. No trigger -> no trade (0 R). Compared per Gotobi day with method 2 (immediate sell, 1R stop).
Usage: python3 -I r15_o4.py <REPO> <WORK> <PRE_ZIP_DIR>"""
import os, sys, glob, zipfile, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sig import atr
REPO, WORK, PRE = sys.argv[1:4]; COST = 0.005
agg = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'}
fr = []
for z in sorted(glob.glob(os.path.join(PRE, 'DAT_ASCII_USDJPY_M1_200*.zip'))):
    with zipfile.ZipFile(z) as f:
        n = [x for x in f.namelist() if x.endswith('.csv')][0]
        d = pd.read_csv(f.open(n), sep=';', header=None, names=['ts', 'open', 'high', 'low', 'close', 'v'])
    d['ts'] = pd.to_datetime(d.ts, format='%Y%m%d %H%M%S'); fr.append(d.drop(columns='v'))
m1 = pd.concat(fr).drop_duplicates('ts').set_index('ts').sort_index()
med = m1.close.rolling(61, center=True, min_periods=11).median(); m1 = m1[~(np.log(m1[['open', 'high', 'low', 'close']].div(med, axis=0)).abs().max(axis=1) > 0.10)]
M5 = pd.concat([m1.resample('5min', label='left', closed='left').agg(agg).dropna(), pd.read_parquet(os.path.join(WORK, 'bars_m5', 'USDJPY_M5.parquet'))]).sort_index()
M5 = M5[~M5.index.duplicated()]
d1p = m1.shift(freq='7h').resample('1D').agg(agg).dropna(); d1p.index = d1p.index - pd.Timedelta('7h')
D1 = pd.concat([d1p, pd.read_parquet(os.path.join(WORK, 'bars_full', 'USDJPY_D1.parquet'))]).sort_index(); D1 = D1[~D1.index.duplicated()]
ATR = pd.Series(atr(D1.high.values, D1.low.values, D1.close.values, 14), index=D1.index + pd.Timedelta('24h'))
o, h, l, c = [M5[k].values.astype(float) for k in ('open', 'high', 'low', 'close')]; idx = M5.index
fh = np.zeros(len(h), bool); fl = np.zeros(len(l), bool)
fh[2:-2] = (h[2:-2] > h[1:-3]) & (h[2:-2] > h[:-4]) & (h[2:-2] >= h[3:-1]) & (h[2:-2] >= h[4:])
fl[2:-2] = (l[2:-2] < l[1:-3]) & (l[2:-2] < l[:-4]) & (l[2:-2] <= l[3:-1]) & (l[2:-2] <= l[4:])
def gotobi(y0, y1):
    G = set()
    for y in range(y0, y1 + 1):
        for mo in range(1, 13):
            last = pd.Timestamp(y, mo, 1) + pd.offsets.MonthEnd(0)
            for g in [pd.Timestamp(y, mo, k) for k in (5, 10, 15, 20, 25, 30) if k <= last.day] + [last]:
                while g.dayofweek >= 5: g -= pd.Timedelta(days=1)
                G.add(g)
    return sorted(G)
def short(e, i_exit, R):
    sl = o[e] + R
    for j in range(e, i_exit):
        if j > e and o[j] >= sl: return o[e] - o[j] - COST
        if h[j] >= sl: return o[e] - sl - COST
    return o[e] - o[i_exit] - COST
rows = []
for g in gotobi(2000, 2024):
    t0 = g - pd.Timedelta(days=1) + pd.Timedelta(hours=19, minutes=55); tx = g + pd.Timedelta(hours=1)
    if t0 < pd.Timestamp('2000-06-01'): continue
    i0 = idx.searchsorted(t0); ix = idx.searchsorted(tx)
    if ix >= len(idx) or idx[i0] - t0 > pd.Timedelta('15min') or idx[ix] - tx > pd.Timedelta('15min'): continue
    k = ATR.index.searchsorted(t0, side='right') - 1
    if k < 14: continue
    R = 0.25 * ATR.iloc[k]
    base = short(i0, ix, R) / R
    # trigger scan 09:55-10:55 JST
    kend = idx.searchsorted(t0 + pd.Timedelta('60min')); H1 = Lw = H2 = None; ent = None
    for kk in range(i0 + 2, min(kend, ix)):
        j = kk - 2
        if j < i0: continue
        if fh[j]:
            if H1 is None or (Lw is None and h[j] > H1): H1 = h[j]
            elif Lw is not None:
                if h[j] <= H1 + 0.1 * R: H2 = h[j] if H2 is None or h[j] > H2 else H2
                else: H1, Lw, H2 = h[j], None, None
        if fl[j] and H1 is not None and H2 is None: Lw = l[j] if Lw is None or l[j] < Lw else Lw
        if H2 is not None and Lw is not None and c[kk] < Lw: ent = kk + 1; break
    o4 = short(ent, ix, R) / R if ent is not None and ent < ix else 0.0
    rows.append(dict(G=g, base=base, o4=o4, traded=ent is not None and ent < ix))
T = pd.DataFrame(rows); T['per'] = np.select([T.G < '2005', T.G < '2017', T.G < '2022'], ['2000-04', '2005-16', '2017-21'], '2022-24')
S = T.groupby('per').agg(N=('base', 'size'), base=('base', 'mean'), o4=('o4', 'mean'), traded=('traded', 'mean'),
                         o4_when_traded=('o4', lambda x: x[T.loc[x.index, 'traded']].mean()), base_when_traded=('base', lambda x: x[T.loc[x.index, 'traded']].mean()),
                         base_when_skipped=('base', lambda x: x[~T.loc[x.index, 'traded']].mean()))
print(S.round(3).to_string())
ok = all(S.loc[p, 'o4'] > S.loc[p, 'base'] for p in ('2005-16', '2017-21', '2000-04'))
print('O4 ADOPT =', ok)
T.to_csv(os.path.join(WORK, 'out', 'r15_o4.csv'), index=False)
