"""Data-validity diagnostic (pool 2005-2021 only): is the 17:00 EST (rollover) edge a bid-only spread artifact?
Average M5 bid path around 17:00 EST, relative to 16:00, in pips, for the pairs flagged by the loop + reference pairs."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r7_lib as L, numpy as np, pandas as pd
from bt import PIP
offs = ['16:00', '16:30', '16:45', '16:50', '16:55', '17:00', '17:05', '17:10', '17:15', '17:20', '17:30', '17:45', '18:00', '18:30']
rows = []
for p in ['AUDNZD', 'EURAUD', 'GBPCHF', 'EURCHF', 'EURGBP', 'EURUSD', 'USDJPY', 'GBPJPY']:
    b = L.load(p, 'M5', L.POOL_END); op = b.open
    days = pd.bdate_range('2005-02-01', '2021-12-30')
    days = days[days.dayofweek <= 3]            # Mon-Thu (Friday 17:00 = weekly close)
    base = op.reindex(days + pd.Timedelta('16h')).values
    r = {'pair': p}
    for o in offs:
        hh, mm = map(int, o.split(':')); v = op.reindex(days + pd.Timedelta(hours=hh, minutes=mm)).values
        d = (v - base) / PIP[p]; r[o] = np.nanmean(d)
    rows.append(r)
D = pd.DataFrame(rows).set_index('pair')
pd.set_option('display.width', 250)
print('Mean M5 OPEN (bid) minus 16:00 bid, pips, Mon-Thu 2005-2021:'); print(D.round(2).to_string())
# M5 high-low range per bar around rollover (spread-widening proxy)
rows = []
for p in ['AUDNZD', 'EURAUD', 'EURUSD']:
    b = L.load(p, 'M5', L.POOL_END); rng_ = (b.high - b.low) / PIP[p]
    tod = b.index.strftime('%H:%M'); m = pd.Series(rng_.values, index=tod).groupby(level=0).median()
    rows.append(m.reindex(offs).rename(p))
print('\nMedian M5 high-low (pips) by bar start time:'); print(pd.DataFrame(rows).round(1).to_string())
