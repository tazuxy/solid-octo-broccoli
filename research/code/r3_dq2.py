"""Round 3 DQ part 2: is any index D1 CLOSE (the only index price the strategies use) a bad print?
Compare each D1 close with the median of the last 31 M1 closes of that D1 bar; also report the time of the last M1 print."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prep
prep.DATA = os.path.join(prep.ROOT, 'data_idx')
for s in ['SPXUSD', 'GRXEUR', 'UKXGBP', 'JPXJPY', 'AUXAUD']:
    m1 = prep.load_pair(s)
    key = (m1.index + pd.Timedelta('7h')).normalize()          # D1 bar (17:00->17:00) open date + 7h trick
    g = m1.close.groupby(key)
    last = g.last(); med = g.apply(lambda x: x.iloc[-31:].median()); lt = m1.index.to_series().groupby(key).last()
    dev = np.log(last / med).abs()
    print(s, 'D1 closes deviating >1% from median of last 31 M1:', [(str(k.date()), round(v, 4), str(lt[k].time())) for k, v in dev[dev > 0.01].items()])
    print('   last-print time distribution (EST hour):', lt.dt.hour.value_counts().sort_index().to_dict())
