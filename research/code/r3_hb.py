"""H-B: month-end equity-hedge rebalancing flow (Melvin & Prins 2015). Pre-registered, no tuning.
FX business days = weekdays except Dec 25 and Jan 1. T = last FX business day of the month. Entry date E = T (variant a)
or the FX business day two before T (variant b). Signal = MTD log return SPX - foreign index, using index D1 closes with
close date < E (i.e. up to the previous 17:00 EST close); MTD base = last index close dated in the previous month.
diff > 0 -> buy foreign ccy vs USD (EURUSD/GBPUSD/AUDUSD long, USDJPY short); diff <= 0 -> the opposite.
Entry: 08:00 EST H1 open on E. Exit: H1 open at the London 16:00 fix on T (16:00 Europe/London -> UTC -> UTC-5).
Missing H1 bar -> close of last H1 bar within 6h (price_at); if no price, the trade is skipped (logged).
R unit = 0.5 * ATR14(D1) from D1 bars with close date < E. Net of COST_PIPS * cost multiplier.
EURUSD trades whose GRXEUR base or signal close lies in the non-DAX segment 2020-06-15..2023-12-01 are excluded (primary);
the 'proxy' run keeps them (Euro Stoxx 50 used as euro-area equity proxy) as a sensitivity only."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r3_common import *
MAP = {'EURUSD': ('GRXEUR', 1), 'GBPUSD': ('UKXGBP', 1), 'USDJPY': ('JPXJPY', -1), 'AUDUSD': ('AUXAUD', 1)}

def fx_bdays():
    d = pd.bdate_range('2011-09-01', '2024-12-31')
    return d[~(((d.month == 12) & (d.day == 25)) | ((d.month == 1) & (d.day == 1)))]

def last_close_before(s, when):
    pos = s.index.searchsorted(when, side='left') - 1
    return (s.index[pos], s.values[pos]) if pos >= 0 else (pd.NaT, np.nan)

def base_close(s, when):
    """last close dated in the month before `when`'s month"""
    m0 = pd.Timestamp(when.year, when.month, 1)
    return last_close_before(s, m0)

def run(variant, cmult=1.0, keep_proxy=False):
    bd = fx_bdays(); ser = pd.Series(bd, index=bd)
    T = ser.groupby(bd.to_period('M')).max()
    T = T[(T >= START) & (T < END)]
    spx = idx_d1('SPXUSD').close
    rows = []; skipped = []
    for pair, (isym, sgn) in MAP.items():
        h1 = fx_h1(pair); d1 = fx_d1(pair)
        a14 = pd.Series(atr(d1.high.values, d1.low.values, d1.close.values, 14), index=d1.index)
        fi = idx_d1(isym).close
        for t in T.values:
            t = pd.Timestamp(t); i = bd.get_loc(t); E = t if variant == 'a' else bd[i - 2]
            bU, cU0 = base_close(spx, E); sU, cU1 = last_close_before(spx, E)
            bF, cF0 = base_close(fi, E); sF, cF1 = last_close_before(fi, E)
            if sU < pd.Timestamp(E.year, E.month, 1) or sF < pd.Timestamp(E.year, E.month, 1):
                skipped.append((pair, t, 'no index close in month before entry')); continue
            bad = isym == 'GRXEUR' and any(BAD_GRX[0] <= x <= BAD_GRX[1] for x in (bF, sF))
            if bad and not keep_proxy: skipped.append((pair, t, 'GRXEUR non-DAX segment')); continue
            diff = (np.log(cU1) - np.log(cU0)) - (np.log(cF1) - np.log(cF0))
            dirn = sgn * (1 if diff > 0 else -1)          # +1 = long the pair
            ent_t = E + pd.Timedelta('8h'); ex_t = london_fix_est([t])[0]
            pe = price_at(h1, [ent_t]).iloc[0]; px = price_at(h1, [ex_t]).iloc[0]
            if np.isnan(pe) or np.isnan(px): skipped.append((pair, t, 'missing FX price')); continue
            _, A = last_close_before(a14, E)
            Ru = 0.5 * A; cost = COST_PIPS[pair] * PIP[pair] * cmult
            pnl = dirn * (px - pe) - cost
            rows.append(dict(pair=pair, T=t, entry_date=E, entry_time=ent_t, exit_time=ex_t, diff=diff, dir=dirn,
                             entry=pe, exit=px, R_unit=Ru, pips=pnl / PIP[pair], R=pnl / Ru, gross_R=dirn * (px - pe) / Ru,
                             proxy=bad))
    tr = pd.DataFrame(rows).sort_values(['exit_time', 'pair']).reset_index(drop=True)
    return tr, pd.DataFrame(skipped, columns=['pair', 'T', 'reason'])

if __name__ == '__main__':
    for v in ('a', 'b'):
        for cm in (1.0, 1.5, 2.0):
            tr, sk = run(v, cm); tr.to_parquet(os.path.join(OUT, f'r3_hb_trades_{v}_c{cm}.parquet'))
            if cm == 1.0:
                print(v, 'N', len(tr), 'skipped', len(sk)); print(sk.groupby(['pair', 'reason']).size().to_string())
                print(sk[sk.reason != 'GRXEUR non-DAX segment'].to_string())
        tp, _ = run(v, 1.0, keep_proxy=True); tp.to_parquet(os.path.join(OUT, f'r3_hb_trades_{v}_proxy.parquet'))
        tp, _ = run(v, 1.5, keep_proxy=True); tp.to_parquet(os.path.join(OUT, f'r3_hb_trades_{v}_proxy_c1.5.parquet'))
