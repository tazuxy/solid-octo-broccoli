"""Round 6 shared code: E2 trade builder (identical conventions to r4b_s2.py) + entry-time features (closed bars only).
Clock: histdata fixed EST (UTC-5); JST = EST + 14h. D1 bars: open 17:00 EST, close +1 day. H4 bars: left-labelled 00/04/.. EST."""
import os, sys, json, datetime as dt, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4_common import ROOT, OUT, PIP, tstat, maxdd, longest_flat_days
from r4_s2 import gotobi_set
from sig import atr, rsi, bbands
COST = 0.5
SEL = (2005, 2014); VAL = (2015, 2024)
_M5 = None
def m5():
    global _M5
    if _M5 is None: _M5 = pd.read_parquet(os.path.join(ROOT, 'bars_m5', 'USDJPY_M5.parquet'))
    return _M5
def log(msg):
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
    open(os.path.join(OUT, 'r6_timeline.log'), 'a').write(f'{now} {msg}\n'); return now

def build(entry_off=0, exit_off=0):
    """All business days G (weekdays, 2005-2024) with D = previous weekday. Long 22:00 JST D (+entry_off min) -> 09:55 JST G (+exit_off)."""
    op = m5().open; first = op.index[0] + pd.Timedelta('30D')
    days = pd.bdate_range('2005-01-01', '2024-12-31'); gb = gotobi_set('2005-01-01', '2024-12-31')
    G = days[1:]; D = days[:-1]
    ti = D + pd.Timedelta(hours=8, minutes=entry_off); tx = G - pd.Timedelta('1D') + pd.Timedelta(hours=19, minutes=55 + exit_off)
    tr = pd.DataFrame({'G': G, 'D': D, 't_ent': ti, 't_exit': tx})
    tr = tr[(tr.t_ent >= first) & tr.t_ent.isin(op.index) & tr.t_exit.isin(op.index)].copy()
    tr['entry'] = op.reindex(tr.t_ent).values; tr['exit'] = op.reindex(tr.t_exit).values
    tr['gotobi'] = tr.G.isin(gb); tr['G_dow'] = tr.G.dt.dayofweek; tr['year'] = tr.G.dt.year
    d1 = d1_frame()
    m = pd.merge_asof(tr[['t_ent']].reset_index(), d1[['close_time', 'atr']], left_on='t_ent', right_on='close_time', direction='backward').set_index('index')
    tr['d1_atr'] = m.atr; tr['gross_pips'] = (tr.exit - tr.entry) / PIP['USDJPY']; tr['R_pips'] = 0.25 * tr.d1_atr / PIP['USDJPY']
    tr = tr.dropna(subset=['R_pips']).sort_values('t_ent').reset_index(drop=True)
    tr['net'] = tr.gross_pips - COST
    return tr

def adx_wilder(h, l, c, n=14):
    up = np.diff(h, prepend=np.nan); dn = -np.diff(l, prepend=np.nan)
    pdm = np.where((up > dn) & (up > 0), up, 0.0); mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    pc = np.roll(c, 1); pc[0] = np.nan
    trr = np.nanmax(np.vstack([h - l, np.abs(h - pc), np.abs(l - pc)]), axis=0)
    def rma(x, start):
        o = np.full(len(x), np.nan); o[start] = np.nanmean(x[start - n + 1:start + 1])
        for i in range(start + 1, len(x)): o[i] = o[i - 1] + (x[i] - o[i - 1]) / n
        return o
    atr_ = rma(trr, n); pdi = 100 * rma(pdm, n) / atr_; mdi = 100 * rma(mdm, n) / atr_
    dx = 100 * np.abs(pdi - mdi) / (pdi + mdi)
    adx = np.full(len(c), np.nan); s = 2 * n - 1; adx[s] = np.nanmean(dx[n:s + 1])
    for i in range(s + 1, len(c)): adx[i] = adx[i - 1] + (dx[i] - adx[i - 1]) / n
    return adx

_D1 = None
def d1_frame():
    global _D1
    if _D1 is not None: return _D1
    d1 = pd.read_parquet(os.path.join(ROOT, 'bars_full', 'USDJPY_D1.parquet'))
    h, l, c = d1.high.values, d1.low.values, d1.close.values
    a = atr(h, l, c, 14); span = pd.Series(d1.index).diff(13).dt.days.values
    f = pd.DataFrame({'close_time': d1.index + pd.Timedelta('1D'), 'close': c, 'high': h,
                      'atr': np.where(span <= 24, a, np.nan)})       # identical ATR to r4b_s2
    cs = pd.Series(c)
    f['sma200'] = cs.rolling(200).mean().values; s50 = cs.rolling(50).mean(); f['sma50_slope'] = (s50 - s50.shift(10)).values
    av = pd.Series(a)
    f['atr_pct'] = av.rolling(250).apply(lambda x: 100.0 * (x <= x[-1]).mean(), raw=True).values
    f['ret5'] = (cs / cs.shift(5) - 1).values; f['ret20'] = (cs / cs.shift(20) - 1).values
    f['adx'] = adx_wilder(h, l, c, 14)
    _D1 = f.sort_values('close_time').reset_index(drop=True); return _D1

def weekly_frame():
    f = d1_frame()
    wk = f.close_time.dt.to_period('W-SAT')        # Sun..Sat by D1 close time
    w = f.groupby(wk).agg(close=('close', 'last')).reset_index()
    w['avail'] = w.close_time.dt.end_time if hasattr(w, 'close_time') else None
    w['avail'] = w['close_time'].apply(lambda p: p.end_time) if 'close_time' in w else w.iloc[:, 0].apply(lambda p: p.end_time)
    w['sma26'] = w.close.rolling(26).mean()
    return w[['avail', 'close', 'sma26']].rename(columns={'close': 'wclose'}).sort_values('avail')

def h4_frame():
    h4 = pd.read_parquet(os.path.join(ROOT, 'bars_full', 'USDJPY_H4.parquet')); c = h4.close.values
    mid, up, lo, _ = bbands(c, 20, 2.0)
    return pd.DataFrame({'close_time': h4.index + pd.Timedelta('4h'), 'h4close': c, 'rsi': rsi(c, 14), 'bb_up': up, 'bb_lo': lo}).sort_values('close_time')

def gtype_cols(G):
    G = pd.DatetimeIndex(G); bd = pd.bdate_range('2004-12-01', '2025-01-31')
    lastbd = set(pd.Series(bd, index=bd).groupby([bd.year, bd.month]).max())
    typ, rolled = [], []
    for g in G:
        dim = g.days_in_month
        if g in lastbd: typ.append('month_end'); rolled.append(g.day != dim); continue
        k = next(k for k in (5, 10, 15, 20, 25, 30) if k >= g.day)
        typ.append(f'd{k}'); rolled.append(g.day != k)
    return typ, rolled

def b3(x, lo, hi, labs):
    return np.where(np.isnan(x), 'NA', np.where(x < lo, labs[0], np.where(x > hi, labs[2], labs[1])))

def features(tr):
    """Bucket labels for every candidate condition, computed at t_ent from closed bars only."""
    tr = tr.copy(); key = tr[['t_ent']].reset_index()
    d = pd.merge_asof(key, d1_frame(), left_on='t_ent', right_on='close_time', direction='backward').set_index('index')
    w = pd.merge_asof(key, weekly_frame(), left_on='t_ent', right_on='avail', direction='backward').set_index('index')
    h = pd.merge_asof(key, h4_frame(), left_on='t_ent', right_on='close_time', direction='backward').set_index('index')
    tr['HTF1'] = np.where(d.sma200.isna(), 'NA', np.where(d.close >= d.sma200, 'above', 'below'))
    tr['HTF2'] = np.where(d.sma50_slope.isna(), 'NA', np.where(d.sma50_slope > 0, 'up', 'down'))
    tr['HTF3'] = np.where(w.sma26.isna(), 'NA', np.where(w.wclose >= w.sma26, 'above', 'below'))
    tr['HTF4'] = b3(d.atr_pct.values, 20, 80, ['<20', '20-80', '>80'])
    tr['HTF5a'] = b3(100 * d.ret5.values, -1, 1, ['<-1%', '-1..+1%', '>+1%'])
    tr['HTF5b'] = b3(100 * d.ret20.values, -2, 2, ['<-2%', '-2..+2%', '>+2%'])
    tr['HTF6'] = b3(d.adx.values, 20, 30, ['<20', '20-30', '>30'])
    tr['DOW1'] = tr.G.dt.dayofweek.map({0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri'})
    typ, rolled = gtype_cols(tr.G); tr['DOW2a'] = typ; tr['DOW2b'] = np.where(rolled, 'rolled', 'not_rolled')
    tr['DOW3'] = np.where(tr.G.dt.month.isin([3, 6, 9, 12]), 'quarter_end', 'other')
    tr['IND1'] = b3(h.rsi.values, 30, 70, ['<30', '30-70', '>70'])
    op = m5().open; t0 = tr.t_ent - pd.Timedelta(hours=8) - pd.Timedelta('1D') + pd.Timedelta(hours=19, minutes=55)   # 09:55 JST on D
    p0 = op.reindex(t0).values; mv = tr.entry.values - p0
    tr['IND2'] = np.where(np.isnan(mv), 'NA', np.where(mv > 0, 'up', 'down'))
    tr['IND3'] = np.where(h.bb_up.isna(), 'NA', np.where(h.h4close > h.bb_up, 'above_upper', np.where(h.h4close < h.bb_lo, 'below_lower', 'inside')))
    dist = (d.high.values - tr.entry.values) / d.atr.values
    tr['IND4'] = b3(dist, 0.25, 1.0, ['<0.25', '0.25-1', '>1'])
    tr['period'] = np.where(tr.year <= SEL[1], 'SEL', 'VAL')
    return tr

CONDS = ['HTF1', 'HTF2', 'HTF3', 'HTF4', 'HTF5a', 'HTF5b', 'HTF6', 'DOW1', 'DOW2a', 'DOW2b', 'DOW3', 'IND1', 'IND2', 'IND3', 'IND4']

def pstats(x, col='net'):
    v = np.asarray(x[col] if isinstance(x, pd.DataFrame) else x, float)
    if len(v) == 0: return dict(N=0, mean=np.nan, t=np.nan, sum=0.0, maxDD=0.0, ratio=np.nan)
    dd = maxdd(v); s = v.sum()
    return dict(N=len(v), mean=v.mean(), t=tstat(v), sum=s, maxDD=dd, ratio=s / abs(dd) if dd < 0 else np.inf)

def stop_gross(tr, k):
    """Gross pips with a stop k*R below entry: M5 bid lows from the entry bar to the bar before exit; gap through -> bar open."""
    b = m5(); bt_ = b.index.values; lo = b.low.values; op = b.open.values; out = []
    for ti, tx, e, R, g in zip(tr.t_ent.values, tr.t_exit.values, tr.entry.values, tr.R_pips.values, tr.gross_pips.values):
        i0, i1 = np.searchsorted(bt_, ti), np.searchsorted(bt_, tx); sl = e - k * R * PIP['USDJPY']; hit = None
        for j in range(i0, i1):
            if j > i0 and op[j] <= sl: hit = op[j]; break
            if lo[j] <= sl: hit = sl; break
        out.append(g if hit is None else (hit - e) / PIP['USDJPY'])
    return np.array(out)
