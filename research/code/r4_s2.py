"""Round 4 S2: Tokyo fix (09:55 JST) anomaly. JST = histdata EST + 14h (no DST on either side).
 a : buy  at 08:00 JST (18:00 EST prev. calendar day), exit 09:55 JST (19:55 EST), every JST business day (Mon-Fri).
 b : same, goto-bi only (JST date 5/10/15/20/25/30 or last weekday of month; weekend -> preceding weekday; NO JP holiday calendar).
 c : sell at 09:55 JST, exit 11:00 JST (21:00 EST), every business day; c2 goto-bi only.
Prices = open of the M5 bar starting exactly at the time (skip day if that bar is missing).
R unit = 0.25 * D1 ATR(14) (bars_full D1, 17:00 EST days) of the last D1 bar CLOSED before entry. No stop.
USDJPY = verdict; EURJPY, AUDJPY = cross-check. Data guard: skip if D1 ATR window spans a >10-day gap; first 30 days skipped."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sig import atr
from r4_common import *

def gotobi_set(start, end):
    days = pd.bdate_range(start, end)  # weekdays
    s = set(); dset = set(days)
    for (y, m), g in pd.Series(days, index=days).groupby([days.year, days.month]):
        s.add(g.index.max())
        for d in (5, 10, 15, 20, 25, 30):
            try: t = pd.Timestamp(year=y, month=m, day=d)
            except ValueError: continue
            while t not in dset and t.month == m: t -= pd.Timedelta('1D')
            if t in dset: s.add(t)
    return s

def run(pair):
    b = pd.read_parquet(os.path.join(ROOT, 'bars_m5', f'{pair}_M5.parquet')); op = b.open
    d1 = pd.read_parquet(os.path.join(ROOT, 'bars_full', f'{pair}_D1.parquet'))
    a = atr(d1.high.values, d1.low.values, d1.close.values, 14)
    span = pd.Series(d1.index).diff(13).dt.days.values  # days covered by last 14 bars
    d1f = pd.DataFrame({'close_time': d1.index + pd.Timedelta('1D'), 'atr': np.where(span <= 24, a, np.nan)})
    jst_days = pd.bdate_range('2005-01-01', '2024-12-31'); gb = gotobi_set('2005-01-01', '2024-12-31')
    first = b.index[0] + pd.Timedelta('30D'); rows = []
    for D in jst_days:
        e0 = D - pd.Timedelta('1D')  # EST calendar day of the JST morning
        t18, t1955, t21 = e0 + pd.Timedelta('18h'), e0 + pd.Timedelta('19h55min'), e0 + pd.Timedelta('21h')
        if t18 < first: continue
        for var, (ti, tx, d) in {'a': (t18, t1955, 1), 'c': (t1955, t21, -1)}.items():
            if ti not in op.index or tx not in op.index: continue
            rows.append(dict(pair=pair, jst_date=D, var=var, t_ent=ti, dir=d, entry=op[ti], exit=op[tx], gotobi=D in gb, dow_jst=D.dayofweek))
    tr = pd.DataFrame(rows)
    m = pd.merge_asof(tr[['t_ent']].reset_index(), d1f.sort_values('close_time'), left_on='t_ent', right_on='close_time', direction='backward')
    tr['d1_atr'] = m.sort_values('index').atr.values
    tr['gross_pips'] = tr.dir * (tr.exit - tr.entry) / PIP[pair]; tr['R_pips'] = 0.25 * tr.d1_atr / PIP[pair]
    return tr.dropna(subset=['R_pips'])

if __name__ == '__main__':
    tr = pd.concat([run(p) for p in ('USDJPY', 'EURJPY', 'AUDJPY')], ignore_index=True)
    b2 = tr[tr.gotobi].copy(); b2['var'] = b2['var'].map({'a': 'b', 'c': 'c2'})
    tr = pd.concat([tr, b2], ignore_index=True).sort_values(['pair', 'var', 't_ent']).reset_index(drop=True)
    tr.to_parquet(os.path.join(OUT, 'r4_s2_trades.parquet'))
    print(tr.groupby(['pair', 'var']).agg(N=('gross_pips', 'size'), g=('gross_pips', 'mean'), R=('R_pips', 'median')).round(3))
