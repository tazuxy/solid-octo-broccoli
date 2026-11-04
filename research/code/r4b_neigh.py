"""Round 4b report-only: neighbourhood of E2 (USDJPY, Gotobi only, cost 0.5): entry JST time on D varied, exit 09:55 G;
and exit time varied with entry 22:00 D. Not used for selection (shows whether 22:00 is a knife-edge)."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r4b_s2
from r4b_common import *
sp = {f'in{h}': ('D', h, 'G', '09:55', 1) for h in ('12:00', '15:00', '18:00', '20:00', '21:00', '22:00', '23:00')}
sp.update({'in00:00G': ('G', '00:00', 'G', '09:55', 1), 'in03:00G': ('G', '03:00', 'G', '09:55', 1)})
sp.update({f'out{h}': ('D', '22:00', 'G', h, 1) for h in ('08:00', '09:00', '09:30', '10:30', '11:00')})
r4b_s2.SPEC = sp
v = r4b_s2.build('USDJPY'); v = v[v.gotobi]
rows = []
for k, x in v.groupby('var'):
    s = fix_stats(x, BASE); rows.append(dict(var=k, **{c: s[c] for c in ('N', 'avg_pips', 'avgR', 't', 'ratio', '2005-2011', '2012-2018', '2019-2024', 'ok')}))
t = pd.DataFrame(rows); print(t.round(3).to_string(index=False)); t.to_csv(os.path.join(OUT, 'r4b_neigh.csv'), index=False)
