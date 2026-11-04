"""R5 H3 (fix flows), H4 (gold Asian long / London-NY short), H5 (JPY intraday). Time-window trades, no stop.
Prices: open of the bar starting exactly at the entry / exit time (skip the day if either bar is missing).
R = 0.25 * D1 ATR(14) of the last D1 bar closed before entry. Delay variant: entry one bar later (M5: +5 min, H4 test H1: +1 h), same exit.
H3 fixes (EST = UTC-5 fixed): Tokyo 09:55 JST = 19:55 EST previous calendar day (JST weekday);
 ECB 14:15 CET/CEST -> 08:15 EST winter / 07:15 EST summer (EU rule); London WMR 16:00 GMT/BST -> 11:00 / 10:00 EST (UK rule).
 pre = long USD fix-60min -> fix; post = short USD fix -> fix+60min. Weekdays (local) only. 7 USD pairs; EURGBP/EURJPY London fix = report only (long base ccy).
H4 XAUUSD H1: a long 19:00 EST (Sun-Thu) -> 03:00 EST next day; b short 03:00 -> 11:00 EST Mon-Fri.
H5 USDJPY M5: a long 13:45 -> 14:45 JST (= 23:45 EST prev day -> 00:45 EST) JST weekdays;
 b long 10:00 -> 15:00 JST (20:00 EST prev day -> 01:00 EST) on JST weekdays that are day 29-31 or the last weekday of the month."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r5_common import *

USD_SIGN = {'EURUSD': -1, 'GBPUSD': -1, 'AUDUSD': -1, 'NZDUSD': -1, 'USDJPY': 1, 'USDCAD': 1, 'USDCHF': 1}
DAYS = pd.bdate_range('2005-01-01', '2024-12-31')

def window_trades(pair, bars, specs, var, step):
    """specs: list of (t_entry, t_exit, dir). Entry bar open / exit bar open; delayed copy uses t_entry+step."""
    op = bars.open; first = bars.index[0] + pd.Timedelta('30D'); rows = []
    idx = op.index
    for te, tx, d in specs:
        if te < first: continue
        for mode, t0 in (('base', te), ('delay', te + step)):
            if t0 not in idx or tx not in idx: continue
            rows.append(dict(inst=pair, var=var, mode=mode, t_ent=t0, dir=d, gross_pips=d * (op[tx] - op[t0]) / PIP[pair]))
    tr = pd.DataFrame(rows)
    tr = attach_atr(tr, pair, 't_ent'); tr['R_pips'] = 0.25 * tr.d1_atr / PIP[pair]
    return tr.dropna(subset=['R_pips'])

def fix_times(fix):
    out = []
    for D in DAYS:
        if fix == 'TKY': t = D - pd.Timedelta('1D') + pd.Timedelta('19h55min')
        elif fix == 'ECB': t = D + (pd.Timedelta('7h15min') if eu_summer(D) else pd.Timedelta('8h15min'))
        else: t = D + (pd.Timedelta('10h') if eu_summer(D) else pd.Timedelta('11h'))
        out.append(t)
    return out

def h3():
    res = []; m5 = {p: load_m5(p) for p in list(USD_SIGN) + ['EURGBP', 'EURJPY']}
    for fix in ('TKY', 'ECB', 'LDN'):
        ft = fix_times(fix); H = pd.Timedelta('60min')
        for p, s in USD_SIGN.items():
            res.append(window_trades(p, m5[p], [(t - H, t, s) for t in ft], f'H3_{fix}_pre', pd.Timedelta('5min')))
            res.append(window_trades(p, m5[p], [(t, t + H, -s) for t in ft], f'H3_{fix}_post', pd.Timedelta('5min')))
        if fix == 'LDN':
            for p in ('EURGBP', 'EURJPY'):
                res.append(window_trades(p, m5[p], [(t - H, t, 1) for t in ft], 'X_LDN_pre_longbase', pd.Timedelta('5min')))
                res.append(window_trades(p, m5[p], [(t, t + H, 1) for t in ft], 'X_LDN_post_longbase', pd.Timedelta('5min')))
    return pd.concat(res, ignore_index=True)

def h4():
    g = load_full('XAUUSD', 'H1'); res = []
    ev = pd.date_range('2009-03-01', '2024-12-31', freq='D')
    a = [(D + pd.Timedelta('19h'), D + pd.Timedelta('1D 3h'), 1) for D in ev if D.dayofweek in (6, 0, 1, 2, 3)]
    b = [(D + pd.Timedelta('3h'), D + pd.Timedelta('11h'), -1) for D in ev if D.dayofweek <= 4]
    res.append(window_trades('XAUUSD', g, a, 'H4a', pd.Timedelta('1h')))
    res.append(window_trades('XAUUSD', g, b, 'H4b', pd.Timedelta('1h')))
    return pd.concat(res, ignore_index=True)

def h5():
    b = load_m5('USDJPY'); res = []
    a = [(D - pd.Timedelta('15min'), D + pd.Timedelta('45min'), 1) for D in DAYS]
    s = pd.Series(DAYS, index=DAYS); last = set(s.groupby([DAYS.year, DAYS.month]).max())
    sel = [D for D in DAYS if D.day >= 29 or D in last]
    bb = [(D - pd.Timedelta('4h'), D + pd.Timedelta('1h'), 1) for D in sel]
    res.append(window_trades('USDJPY', b, a, 'H5a', pd.Timedelta('5min')))
    res.append(window_trades('USDJPY', b, bb, 'H5b', pd.Timedelta('5min')))
    return pd.concat(res, ignore_index=True)

if __name__ == '__main__':
    tr = pd.concat([h3(), h4(), h5()], ignore_index=True)
    tr['group'] = tr.inst.map(group_of)
    tr['cost_pips'] = np.where(tr.inst == 'XAUUSD', GOLD_COST, USER_COST)
    tr.to_parquet(os.path.join(OUT, 'r5_h345_trades.parquet'))
    tr['gR'] = tr.gross_pips / tr.R_pips
    print(tr.groupby(['var', 'mode']).agg(N=('gR', 'size'), g=('gross_pips', 'mean'), gR=('gR', 'mean'), R=('R_pips', 'median')).round(4))
