"""Round 14: Gotobi brush-up (pre-registered in research/round14/r14_prereg.md).
GB0 method 2 on unused 2000-05-30..2004 (histdata), GB1 skip JP-holiday G, GB2 skip BoJ statement days, GB3 method-1 stop grid.
Usage: python3 -I r14_gotobi_brushup.py <REPO> <WORK> <PRE_ZIP_DIR> <FXCM_DIR>"""
import os, sys, glob, zipfile, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sig import atr
REPO, WORK, PRE, FX = sys.argv[1:5]
COST = 0.005
hol = pd.read_csv(os.path.join(REPO, 'research', 'round10', 'jp_holidays_cao.csv'))
HOL = set(pd.to_datetime(hol.iloc[:, 0], format='%Y/%m/%d'))
for y in range(1999, 2028): HOL |= {pd.Timestamp(y, 12, 31), pd.Timestamp(y, 1, 2), pd.Timestamp(y, 1, 3)}
BOJ = set(pd.to_datetime(pd.read_csv(os.path.join(REPO, 'research', 'round14', 'boj_statement_dates.csv')).date))
# ---------------- prices (bid-only histdata M5 + D1; FXCM bid/ask M1)
def pre_m1():
    fr = []
    for z in sorted(glob.glob(os.path.join(PRE, 'DAT_ASCII_USDJPY_M1_200*.zip'))):
        with zipfile.ZipFile(z) as f:
            n = [x for x in f.namelist() if x.endswith('.csv')][0]
            d = pd.read_csv(f.open(n), sep=';', header=None, names=['ts', 'open', 'high', 'low', 'close', 'v'])
        d['ts'] = pd.to_datetime(d.ts, format='%Y%m%d %H%M%S'); fr.append(d.drop(columns='v'))
    m = pd.concat(fr).drop_duplicates('ts').set_index('ts').sort_index()
    med = m.close.rolling(61, center=True, min_periods=11).median()
    dev = np.log(m[['open', 'high', 'low', 'close']].div(med, axis=0)).abs().max(axis=1); return m[~(dev > 0.10)]
agg = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'}
m1p = pre_m1()
M5 = pd.concat([m1p.resample('5min', label='left', closed='left').agg(agg).dropna(),
                pd.read_parquet(os.path.join(WORK, 'bars_m5', 'USDJPY_M5.parquet'))]).sort_index()
M5 = M5[~M5.index.duplicated()]
d1p = m1p.shift(freq='7h').resample('1D').agg(agg).dropna(); d1p.index = d1p.index - pd.Timedelta('7h')
D1 = pd.concat([d1p, pd.read_parquet(os.path.join(WORK, 'bars_full', 'USDJPY_D1.parquet'))]).sort_index(); D1 = D1[~D1.index.duplicated()]
ATR = pd.Series(atr(D1.high.values, D1.low.values, D1.close.values, 14), index=D1.index + pd.Timedelta('24h'))
def Rv(t):
    i = ATR.index.searchsorted(t, side='right') - 1; return 0.25 * ATR.iloc[i] if i >= 14 else np.nan
fr = []
for f in sorted(glob.glob(os.path.join(FX, 'USDJPY_202[56]_*.csv.gz'))):
    d = pd.read_csv(f); d['ts'] = pd.to_datetime(d.DateTime, format='%m/%d/%Y %H:%M:%S.%f') - pd.Timedelta('5h'); fr.append(d)
FXC = pd.concat(fr).drop_duplicates('ts').set_index('ts').sort_index(); FXC = FXC[FXC.index >= '2025-01-01']
# ---------------- calendar
def prev_wd(d):
    d = d - pd.Timedelta(days=1)
    while d.dayofweek >= 5: d -= pd.Timedelta(days=1)
    return d
def gotobi(y0, y1, skip_month_end):
    G = set()
    for y in range(y0, y1 + 1):
        for mo in range(1, 13):
            last = pd.Timestamp(y, mo, 1) + pd.offsets.MonthEnd(0)
            for g in [pd.Timestamp(y, mo, k) for k in (5, 10, 15, 20, 25, 30) if k <= last.day] + [last]:
                while g.dayofweek >= 5: g -= pd.Timedelta(days=1)
                G.add(g)
    bd = pd.bdate_range(f'{y0}-01-01', f'{y1}-12-31'); lastbd = set(pd.Series(bd, index=bd).groupby([bd.year, bd.month]).max())
    return sorted(g for g in G if not (skip_month_end and g in lastbd))
def path(src, t_in, t_out, d, stop_k, R):
    """direction d (+1 long/-1 short); returns net in yen (histdata: minus 0.5 pip), or None if prices missing"""
    if src == 'fx':
        b = FXC; i0 = b.index.searchsorted(t_in); i1 = b.index.searchsorted(t_out)
        if i1 >= len(b) or b.index[i0] - t_in > pd.Timedelta('15min') or b.index[i1] - t_out > pd.Timedelta('15min'): return None
        if d == 1: e, xo, xh, xl, ex = b.AskOpen.iloc[i0], b.BidOpen.values, b.BidHigh.values, b.BidLow.values, b.BidOpen.iloc[i1]
        else: e, xo, xh, xl, ex = b.BidOpen.iloc[i0], b.AskOpen.values, b.AskHigh.values, b.AskLow.values, b.AskOpen.iloc[i1]
        c = 0.0
    else:
        b = M5; i0 = b.index.searchsorted(t_in); i1 = b.index.searchsorted(t_out)
        if i1 >= len(b) or b.index[i0] - t_in > pd.Timedelta('15min') or b.index[i1] - t_out > pd.Timedelta('15min'): return None
        e, xo, xh, xl, ex = b.open.iloc[i0], b.open.values, b.high.values, b.low.values, b.open.iloc[i1]; c = COST
    px = ex
    if stop_k:
        sl = e - d * stop_k * R
        for j in range(i0, i1):
            if j > i0 and d * (xo[j] - sl) <= 0: px = xo[j]; break
            if (d == 1 and xl[j] <= sl) or (d == -1 and xh[j] >= sl): px = sl; break
    return d * (px - e) - c
def trades(method, stop_k):
    rows = []
    for g in gotobi(2000, 2026, skip_month_end=(method == 1)):
        if method == 1: t_in, t_out, d = prev_wd(g) + pd.Timedelta(hours=8), g - pd.Timedelta(days=1) + pd.Timedelta(hours=19, minutes=55), 1
        else: t_in, t_out, d = g - pd.Timedelta(days=1) + pd.Timedelta(hours=19, minutes=55), g + pd.Timedelta(hours=1), -1
        if t_in < pd.Timestamp('2000-06-01'): continue
        src = 'fx' if t_in >= pd.Timestamp('2025-01-01') else 'h'
        R = Rv(t_in)
        if not np.isfinite(R) or R <= 0: continue
        net = path(src, t_in, t_out, d, stop_k, R)
        if net is None: continue
        rows.append(dict(G=g, t=t_in, netR=net / R, pips=net * 100, hol=g in HOL, boj=g in BOJ))
    T = pd.DataFrame(rows)
    T['per'] = np.select([T.t < '2005', T.t < '2022', T.t < '2025'], ['2000-04', '2005-21', '2022-24'], '2025-26')
    return T
def st(x):
    x = np.asarray(x, float)
    if len(x) == 0: return dict(N=0, meanR=np.nan, t=np.nan)
    return dict(N=len(x), meanR=x.mean(), t=x.mean() / x.std(ddof=1) * np.sqrt(len(x)) if len(x) > 2 else np.nan)
def dd(x):
    cs = np.cumsum(x); return float((cs - np.maximum.accumulate(np.maximum(cs, 0))).min()) if len(x) else 0.0
pd.set_option('display.width', 220)
out = {}
# GB0
T2 = trades(2, 1); T2n = trades(2, None); out['m2_stop1R'] = T2; out['m2_nostop'] = T2n
ref = T2[T2.per.isin(['2005-21', '2022-24'])].netR.values; pre = T2[T2.per == '2000-04']
b = np.random.default_rng(10).choice(ref, size=(20000, len(pre))).mean(1); pct = (b < pre.netR.mean()).mean()
cls = 'strong decay suspected' if pct < 0.05 else ('somewhat weak' if pct < 0.25 else 'consistent')
print('GB0 method 2 (1R stop) by period:'); print(pd.DataFrame({p: {**st(g.netR), 'pips': g.pips.mean(), 'maxddR': dd(g.netR.values)} for p, g in T2.groupby('per')}).T.round(3))
print('    no stop:'); print(pd.DataFrame({p: {**st(g.netR), 'pips': g.pips.mean()} for p, g in T2n.groupby('per')}).T.round(3))
print(f'GB0: 2000-04 mean {pre.netR.mean():+.3f}R is at percentile {pct:.1%} of the 2005-24 bootstrap -> {cls}')
# GB1 / GB2
for nm, col in (('GB1 holiday G', 'hol'), ('GB2 BoJ statement day', 'boj')):
    r = {p: {'skip ' + k: v for k, v in st(g[g[col]].netR).items()} | {'keep meanR': g[~g[col]].netR.mean()} for p, g in T2.groupby('per')}
    print(nm); print(pd.DataFrame(r).T.round(3))
    s1 = T2[(T2.per == '2005-21') & T2[col]].netR.mean(); s0 = T2[(T2.per == '2000-04') & T2[col]].netR.mean()
    print(f'  {nm}: skipped mean 2005-21 {s1:+.3f}, 2000-04 {s0:+.3f} -> ADOPT = {bool(s1 < 0 and s0 < 0)}')
# GB3
rows = []
for k in (None, 2, 3, 4, 6, 8):
    T1 = trades(1, k); out[f'm1_k{k}'] = T1
    for p, g in T1.groupby('per'):
        rows.append(dict(k='none' if k is None else k, per=p, **st(g.netR), pips=g.pips.mean(), worst=g.pips.min(), maxddR=dd(g.netR.values)))
S = pd.DataFrame(rows); print('GB3 method 1 stop grid:'); print(S.round(3).to_string(index=False))
sel = S[S.per == '2005-21']; base = sel[sel.k == 'none'].iloc[0]
ok = sel[(sel.k != 'none') & (sel.meanR >= 0.9 * base.meanR) & (sel.t >= 2.5)]
print('GB3 pre-registered choice:', ok.k.min() if len(ok) else 'no stop')
pd.concat([v.assign(set=k) for k, v in out.items()]).to_csv(os.path.join(WORK, 'out', 'r14_trades.csv'), index=False)
S.to_csv(os.path.join(WORK, 'out', 'r14_m1_stop.csv'), index=False)
