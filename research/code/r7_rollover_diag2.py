"""Rollover diagnostic 2 (pool only): mean M5 bid change vs 15:30 EST, US summer vs winter, and M5 range."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r7_lib as L, numpy as np, pandas as pd
from bt import PIP
from r5_common import us_summer
offs = ['15:30', '15:50', '15:55', '16:00', '16:05', '16:15', '16:30', '16:50', '16:55', '17:00', '17:05', '17:15', '17:30', '18:00']
for p in ['AUDNZD', 'EURAUD', 'GBPCHF']:
    b = L.load(p, 'M5', L.POOL_END); op = b.open; rg = (b.high - b.low) / PIP[p]
    days = pd.bdate_range('2005-02-01', '2021-12-30'); days = days[days.dayofweek <= 3]
    summ = np.array([us_summer(d) for d in days])
    for nm, dd in (('summer', days[summ]), ('winter', days[~summ])):
        base = op.reindex(dd + pd.Timedelta(hours=15, minutes=30)).values; r = []; q = []
        for o in offs:
            hh, mm = map(int, o.split(':')); t = dd + pd.Timedelta(hours=hh, minutes=mm)
            r.append(np.nanmean((op.reindex(t).values - base) / PIP[p])); q.append(np.nanmedian(rg.reindex(t).values))
        print(p, nm, 'bid-15:30 :', ' '.join(f'{o}:{x:+.2f}' for o, x in zip(offs, r)))
        print(p, nm, 'M5 range  :', ' '.join(f'{o}:{x:.1f}' for o, x in zip(offs, q)))
