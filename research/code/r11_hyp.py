"""Round 11: trades for the pre-registered hypotheses K1, K2, G2, F2 (research/round11/r11_prereg.md).
Gross result in price units (index points, gold USD, USDJPY pips) in 'gross_pips'; per-trade cost (spread + K1 financing at 5%/yr) in
'cost_pips'; extra columns fin0/fin8 = cost with 0% / 8% financing. Evaluate with: python3 -I code/r10_eval.py screen r11
Usage (work dir): python3 -I code/r11_hyp.py <REPO>   -> out/r10_r11_trades.parquet"""
import os, sys, numpy as np, pandas as pd
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sig import atr
REPO = sys.argv[1]; ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, 'out')
EST = ZoneInfo('Etc/GMT+5')
IDX = {'SPXUSD': ('America/New_York', 16, 0, 0.5), 'UKXGBP': ('Europe/London', 16, 30, 1.0),
       'JPXJPY': ('Asia/Tokyo', 15, 0, 7.0), 'AUXAUD': ('Australia/Sydney', 16, 0, 1.0)}
FIN = 0.05
hol = pd.read_csv(os.path.join(REPO, 'research', 'round10', 'jp_holidays_cao.csv'))
JPH = set(pd.to_datetime(hol.iloc[:, 0], format='%Y/%m/%d'))
for y in range(2009, 2026): JPH |= {pd.Timestamp(y, 12, 31), pd.Timestamp(y, 1, 2), pd.Timestamp(y, 1, 3)}
_b = {}
def m5(sym):
    if sym not in _b:
        f = os.path.join(ROOT, 'bars_r11', f'{sym}_M5.parquet') if sym in IDX or sym == 'XAUUSD' else os.path.join(ROOT, 'bars_m5', f'{sym}_M5.parquet')
        b = pd.read_parquet(f); m = b.index.hour * 60 + b.index.minute
        _b[sym] = b[~((m >= 16 * 60 + 55) & (m < 17 * 60 + 30))]
    return _b[sym]
def px(sym, t, delay=0):
    b = m5(sym); i = b.index.searchsorted(t)
    if i >= len(b) or b.index[i] - t > pd.Timedelta('15min'): return None, np.nan
    i += delay
    if i >= len(b): return None, np.nan
    return b.index[i], float(b.open.iloc[i])
_a = {}
def R(sym, t):
    if sym not in _a:
        f = os.path.join(ROOT, 'bars_idx', f'{sym}_D1.parquet') if sym in IDX else os.path.join(ROOT, 'bars_full', f'{sym}_D1.parquet')
        d = pd.read_parquet(f); a = atr(d.high.values, d.low.values, d.close.values, 14)
        _a[sym] = pd.Series(a, index=d.index + pd.Timedelta('24h'))
    s = _a[sym]; i = s.index.searchsorted(t, side='right') - 1
    return 0.25 * s.iloc[i] if i >= 14 else np.nan
def loc2est(d, hh, mm, tz):
    t = pd.Timestamp(d.year, d.month, d.day, hh, mm).to_pydatetime().replace(tzinfo=ZoneInfo(tz))
    return pd.Timestamp(t.astimezone(EST).replace(tzinfo=None))
def tdays(sym, a='2010-11-15', z='2024-12-31'):
    d = pd.bdate_range(a, z); d = d[~((d.month == 12) & (d.day == 25)) & ~((d.month == 1) & (d.day == 1))]
    if sym == 'JPXJPY': d = d[~d.isin(JPH)]
    return d
def row(hyp, sym, te, pe, tx, pxx, dirn, cost, delay, fin0=None, fin8=None):
    r = R(sym, te)
    if not np.isfinite(r) or r <= 0: return None
    d = dict(hyp=hyp, inst=sym, t_ent=te, t_exit=tx, dir=dirn, gross_pips=dirn * (pxx - pe), R_pips=r, cost_pips=cost, delay=delay)
    if fin0 is not None: d.update(fin0=fin0, fin8=fin8)
    return d
def k1():
    rows = []
    for sym, (tz, hh, mm, sp) in IDX.items():
        D = tdays(sym); s = pd.Series(D, index=D); g = s.groupby([D.year, D.month])
        months = sorted(g.groups.keys())
        for (y, m), (y2, m2) in zip(months[:-1], months[1:]):
            cur = list(g.get_group((y, m))); nxt = list(g.get_group((y2, m2)))
            if len(cur) < 2 or len(nxt) < 3: continue
            d_in, d_out = cur[-2], nxt[2]
            for delay in (0, 1):
                te, pe = px(sym, loc2est(d_in, hh, mm, tz), delay); tx, pxx = px(sym, loc2est(d_out, hh, mm, tz))
                if te is None or tx is None: continue
                nights = (d_out - d_in).days
                f = lambda rate: sp + rate * pe * nights / 365
                r = row('K1', sym, te, pe, tx, pxx, 1, f(FIN), delay, f(0.0), f(0.08))
                if r: rows.append(r)
    return rows
def k2():
    rows = []
    for sym, (tz, hh, mm, sp) in IDX.items():
        D = tdays(sym)
        for p, d in zip(D[:-1], D[1:]):
            _, p0 = px(sym, loc2est(p, hh, mm, tz)); tsig = loc2est(d, hh, mm, tz) - pd.Timedelta('30min')
            for delay in (0, 1):
                te, pe = px(sym, tsig, delay); tx, pxx = px(sym, loc2est(d, hh, mm, tz))
                _, ps = px(sym, tsig)
                if te is None or tx is None or not np.isfinite(p0) or tx <= te or ps == p0: continue
                r = row('K2', sym, te, pe, tx, pxx, 1 if ps > p0 else -1, sp, delay)
                if r: rows.append(r)
    return rows
def g2():
    rows = []; D = tdays('XAUUSD', '2009-03-16', '2024-12-31')
    for p, d in zip(D[:-1], D[1:]):
        _, p0 = px('XAUUSD', loc2est(p, 13, 30, 'America/New_York')); tsig = loc2est(d, 13, 0, 'America/New_York')
        _, ps = px('XAUUSD', tsig)
        for delay in (0, 1):
            te, pe = px('XAUUSD', tsig, delay); tx, pxx = px('XAUUSD', loc2est(d, 13, 30, 'America/New_York'))
            if te is None or tx is None or not np.isfinite(p0) or tx <= te or ps == p0: continue
            r = row('G2', 'XAUUSD', te, pe, tx, pxx, 1 if ps > p0 else -1, 0.30, delay)
            if r: rows.append(r)
    return rows
def f2():
    rows = []; G = set()
    for y in range(2005, 2025):
        for mo in range(1, 13):
            last = pd.Timestamp(y, mo, 1) + pd.offsets.MonthEnd(0)
            for g in [pd.Timestamp(y, mo, k) for k in (5, 10, 15, 20, 25, 30) if k <= last.day] + [last]:
                while g.dayofweek >= 5: g -= pd.Timedelta(days=1)
                G.add(g)
    for g in sorted(G):
        for delay in (0, 1):
            te, pe = px('USDJPY', g - pd.Timedelta(days=1) + pd.Timedelta(hours=19, minutes=55), delay); tx, pxx = px('USDJPY', g + pd.Timedelta(hours=1))
            if te is None or tx is None or tx <= te: continue
            r = row('F2', 'USDJPY', te, pe, tx, pxx, -1, 0.005, delay)      # price units: 0.005 yen = 0.5 pips
            if r: rows.append(r)
    return rows
if __name__ == '__main__':
    T = pd.DataFrame(k1() + k2() + g2() + f2())
    T.to_parquet(os.path.join(OUT, 'r10_r11_trades.parquet'))
    print(T.groupby(['hyp', 'delay']).size().unstack()); print(T[T.delay == 0].groupby(['hyp', 'inst']).size().unstack(0))
