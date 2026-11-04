"""Round 4b S2: Gotobi 'buy on the day BEFORE' variants (pre-registered), plus r4 a/b/c/c2 rebuilt by the same generic builder.
JST = histdata EST + 14h. G = Gotobi JST date (r4_s2.gotobi_set: 5/10/15/20/25/30 or last weekday of month; Sat/Sun -> preceding
weekday; NO JP holiday calendar). D = business (week)day before G (G Monday -> D Friday: weekend hold for E1-E3).
  E1: long 15:00 JST D -> 09:55 JST G      E2: long 22:00 JST D -> 09:55 JST G
  E3: long 09:55 JST D -> 09:55 JST G      E4 (control): long 08:00 JST D -> 09:55 JST D
  b  (r4): long 08:00 JST G -> 09:55 JST G
Splits (report): E1/E2/E3 'pre' = entry -> 08:00 JST G ; 'fix' = 08:00 -> 09:55 JST G (= b); E3 segments.
Non-Gotobi comparison (report): same windows with G = every other JST weekday (D = previous weekday).
Prices = open of M5 bar starting exactly at the time (skip if missing). R = 0.25 * D1 ATR(14) of last D1 bar closed before entry
(identical to r4_s2). No stop, no swap. year/period = year of G (JST)."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4b_common import *
from r4_s2 import gotobi_set
from sig import atr

SPEC = {  # name: (entry_ref, entry_JST_time, exit_ref, exit_JST_time, dir)
    'a':  ('G', '08:00', 'G', '09:55', 1), 'c': ('G', '09:55', 'G', '11:00', -1),
    'E1': ('D', '15:00', 'G', '09:55', 1), 'E2': ('D', '22:00', 'G', '09:55', 1),
    'E3': ('D', '09:55', 'G', '09:55', 1), 'E4': ('D', '08:00', 'D', '09:55', 1),
    'E1pre': ('D', '15:00', 'G', '08:00', 1), 'E2pre': ('D', '22:00', 'G', '08:00', 1), 'E3pre': ('D', '09:55', 'G', '08:00', 1),
    'seg_D0955_1500': ('D', '09:55', 'D', '15:00', 1), 'seg_D1500_2200': ('D', '15:00', 'D', '22:00', 1),
    'seg_D2200_G0800': ('D', '22:00', 'G', '08:00', 1),
}
def jst_to_est(day, hhmm):
    h, m = map(int, hhmm.split(':')); return day + pd.Timedelta(hours=h, minutes=m) - pd.Timedelta('14h')

def d1_atr_frame(pair):   # identical to r4_s2.run
    d1 = pd.read_parquet(os.path.join(ROOT, 'bars_full', f'{pair}_D1.parquet'))
    a = atr(d1.high.values, d1.low.values, d1.close.values, 14)
    span = pd.Series(d1.index).diff(13).dt.days.values
    return pd.DataFrame({'close_time': d1.index + pd.Timedelta('1D'), 'atr': np.where(span <= 24, a, np.nan)}).sort_values('close_time')

def build(pair):
    op = pd.read_parquet(os.path.join(ROOT, 'bars_m5', f'{pair}_M5.parquet')).open
    first = op.index[0] + pd.Timedelta('30D'); d1f = d1_atr_frame(pair)
    days = pd.bdate_range('2005-01-01', '2024-12-31'); gb = gotobi_set('2005-01-01', '2024-12-31')
    prev = dict(zip(days[1:], days[:-1])); rows = []
    for G in days[1:]:
        D = prev[G]; ref = {'G': G, 'D': D}
        for name, (er, et, xr, xt, d) in SPEC.items():
            ti, tx = jst_to_est(ref[er], et), jst_to_est(ref[xr], xt)
            if ti < first or ti not in op.index or tx not in op.index: continue
            rows.append(dict(pair=pair, var=name, G=G, D=D, t_ent=ti, t_exit=tx, dir=d, entry=op[ti], exit=op[tx], gotobi=G in gb,
                             D_gotobi=D in gb, G_dow=G.dayofweek, weekend=(G - D).days > 1))
    tr = pd.DataFrame(rows).sort_values('t_ent').reset_index(drop=True)
    m = pd.merge_asof(tr[['t_ent']], d1f, left_on='t_ent', right_on='close_time', direction='backward')
    tr['d1_atr'] = m.atr.values; tr['gross_pips'] = tr.dir * (tr.exit - tr.entry) / PIP[pair]
    tr['R_pips'] = 0.25 * tr.d1_atr / PIP[pair]; tr['year'] = tr.G.dt.year
    return tr.dropna(subset=['R_pips'])

if __name__ == '__main__':
    tr = pd.concat([build(p) for p in ('USDJPY', 'EURJPY', 'AUDJPY')], ignore_index=True)
    tr.to_parquet(os.path.join(OUT, 'r4b_s2_trades.parquet'))
    # consistency check vs r4 (b = a on Gotobi; c2 = c on Gotobi)
    r4 = pd.read_parquet(os.path.join(OUT, 'r4_s2_trades.parquet'))
    for v4, v, g in (('a', 'a', None), ('b', 'a', True), ('c', 'c', None), ('c2', 'c', True)):
        x = r4[(r4.pair == 'USDJPY') & (r4['var'] == v4)]; y = tr[(tr.pair == 'USDJPY') & (tr['var'] == v)]
        if g: y = y[y.gotobi]
        print(f'check {v4}: r4 N={len(x)} sum={x.gross_pips.sum():.1f} R={x.R_pips.mean():.3f} | r4b N={len(y)} sum={y.gross_pips.sum():.1f} R={y.R_pips.mean():.3f}')
    print(tr[tr.gotobi].groupby(['pair', 'var']).agg(N=('gross_pips', 'size'), g=('gross_pips', 'mean')).round(2).unstack(0))
