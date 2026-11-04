"""Round 4 S2 control (reported only): mean gross pips of a LONG 115-min USDJPY hold started at each full hour (EST),
all weekdays, by period -> shows how much of S2a/b is general drift vs the 08:00-09:55 JST window. Also goto-bi vs other days."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4_common import *
from r4_s2 import gotobi_set
b = pd.read_parquet(os.path.join(ROOT, 'bars_m5', 'USDJPY_M5.parquet')).open
b = b[b.index >= '2005-02-01']
gb = gotobi_set('2005-01-01', '2025-01-10')
rows = []
for hh in range(24):
    st = b[(b.index.hour == hh) & (b.index.minute == 0)]
    ex = b.reindex(st.index + pd.Timedelta('115min'))
    g = (ex.values - st.values) / 0.01
    jst = (st.index + pd.Timedelta('14h')).normalize()
    df = pd.DataFrame({'g': g, 'jdow': jst.dayofweek, 'year': jst.year, 'gb': [d in gb for d in jst]}).dropna()
    df = df[df.jdow < 5]; df['period'] = period_of(df.year)
    r = dict(start_est=f'{hh:02d}:00', start_jst=f'{(hh+14)%24:02d}:00', N=len(df), all=df.g.mean(), gotobi=df[df.gb].g.mean(), other=df[~df.gb].g.mean())
    for pp, x in df.groupby('period').g.mean().items(): r[pp] = x
    rows.append(r)
t = pd.DataFrame(rows); t.to_csv(os.path.join(OUT, 'r4_s2_control.csv'), index=False)
pd.set_option('display.width', 200); print(t.round(2).to_string(index=False))
print('mean over all 24 start hours:', t[['all','gotobi','other','2005-2011','2012-2018','2019-2024']].mean().round(3).to_dict())
