"""R5 H1 weekend-gap fade (pre-registered). 17 pairs, M5, fixed EST.
Weekend = last bar Friday >= 12:00 EST followed by first bar Sunday 15:00..17:55 EST (holiday weekends with Thu last bar skipped).
gap = first Sunday bar open - Friday last close; trade if |gap| >= k * D1 ATR(14) (last D1 closed before Sunday open), k=0.3 (a), 0.5 (b).
Entry: open of the first bar with ts >= Sun 18:00 (must be <= 18:30) [base]; 'first' = first Sunday bar open (reference);
delay = next bar after base entry. Fade toward Friday close: TP = Friday close, SL = entry -/+ |gap|. Skip if gap already filled at entry.
Time stop: open of first bar >= Mon 17:00 EST. R = |gap|. SL before TP in the same bar."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r5_common import *

PAIRS = DESIGN + CROSS

def run(pair):
    b = load_m5(pair); ts = b.index; o, h, l, c = (b[k].values for k in ('open', 'high', 'low', 'close'))
    gaps = np.where(np.diff(ts.values) > np.timedelta64(30, 'h'))[0]
    first_ok = ts[0] + pd.Timedelta('30D'); rows = []
    for g in gaps:
        tf, ts1 = ts[g], ts[g + 1]
        if tf.dayofweek != 4 or tf.hour < 12 or ts1.dayofweek != 6 or not (15 <= ts1.hour <= 17) or ts1 < first_ok: continue
        fri = c[g]; sun0 = o[g + 1]; gap = sun0 - fri
        sunday = ts1.normalize(); t18 = sunday + pd.Timedelta('18h'); tmon = sunday + pd.Timedelta('1D 17h')
        i18 = ts.searchsorted(t18); ix = ts.searchsorted(tmon)
        if i18 >= len(ts) or ts[i18] > t18 + pd.Timedelta('30min') or ix >= len(ts) or ts[ix] > tmon + pd.Timedelta('2h'): continue
        for mode, i0 in (('base', i18), ('first', g + 1), ('delay', i18 + 1)):
            e = o[i0]; d = -np.sign(gap)
            if d == 0: continue
            if (d > 0 and e >= fri) or (d < 0 and e <= fri): continue    # already filled at entry
            tp = fri; sl = e - d * abs(gap)
            px, why, j = sim_path(o, h, l, i0, ix - 1, d, tp, sl)
            if px is None: px = o[ix]
            rows.append(dict(inst=pair, mode=mode, t_ent=ts[i0], t_sun=ts1, dir=d, gap_pips=gap / PIP[pair], entry=e,
                             gross_pips=d * (px - e) / PIP[pair], R_pips=abs(gap) / PIP[pair], why=why))
    tr = pd.DataFrame(rows)
    tr = attach_atr(tr, pair, 't_sun')
    tr['gap_atr'] = abs(tr.gap_pips * PIP[pair]) / tr.d1_atr
    return tr.dropna(subset=['gap_atr'])

if __name__ == '__main__':
    tr = pd.concat([run(p) for p in PAIRS], ignore_index=True)
    tr['group'] = tr.inst.map(group_of); tr['cost_pips'] = USER_COST
    out = []
    for v, k in (('H1a', 0.3), ('H1b', 0.5)):
        x = tr[tr.gap_atr >= k].copy(); x['var'] = v; out.append(x)
    tr = pd.concat(out, ignore_index=True)
    tr.to_parquet(os.path.join(OUT, 'r5_h1_trades.parquet'))
    print(tr.groupby(['var', 'mode']).agg(N=('gross_pips', 'size'), g=('gross_pips', 'mean'), R=('R_pips', 'median'),
          gR=('gross_pips', lambda s: (s / tr.loc[s.index, 'R_pips']).mean())).round(3))
