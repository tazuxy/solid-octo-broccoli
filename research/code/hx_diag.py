"""Step 2 diagnosis: why does the cross set differ?"""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from hx import *
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40)
m = load_all(); m.to_parquet(os.path.join(ROOT, 'out', 'signals_all_aug.parquet'))
def agg(y): return pd.Series(dict(N=len(y), avgR=y.r.mean(), gross=y.gross_r.mean(), cost=y.cost_r.mean(), win=(y.r>0).mean(),
                                  tp=(y.reason=='tp').mean(), sl=(y.reason=='sl').mean(), time=(y.reason=='time').mean(), tp_atr=y.tp_atr.median(), risk=y.risk_atr.median()))
C = no_overlap(m[BASE_C(m)].sort_values('t')); A = no_overlap(m.sort_values('t'))
print('== overlapping signals, by group'); print(m.groupby('grp').apply(agg).round(3))
print('== rule A (no overlap) by group'); print(A.groupby('grp').apply(agg).round(3))
print('== rule C by group'); print(C.groupby('grp').apply(agg).round(3))
print('== overlapping: k==0 vs k>=1 by group'); print(m.groupby(['grp', m.k >= 1]).apply(agg).round(3))
print('== overlapping: k bucket by group'); print(m.groupby(['grp', m.k.clip(0, 3)]).r.agg(['count','mean']).round(3).unstack(0))
print('== rule C: JPY crosses vs others, IS/OOS'); print(C.groupby(['grp','jpy','is']).r.agg(['count','mean','sum']).round(2))
print('== rule C cross: year x jpy'); print(C[C.grp=='cross'].groupby([C.t.dt.year, 'jpy']).r.sum().unstack().round(2).T)
print('== rule C by group x dir'); print(C.groupby(['grp','dir']).apply(agg).round(3))
print('== rule C JPY-quote pairs (incl USDJPY) by dir'); print(C[C.pair.str.endswith('JPY')].groupby(['pair','dir']).r.agg(['count','mean']).round(2).unstack())
print('== rule C by group: d1_dist20 sign wrt trade (counter-trend depth)')
C['d1_dist_dir'] = -C.dir * C.d1_dist20
print(C.groupby(['grp', pd.cut(C.d1_dist_dir, [-99, 0, 1, 2, 99])]).r.agg(['count','mean']).round(2).unstack(0))
print('== rule C cost sensitivity (cost_r median by group)'); print(C.groupby('grp').cost_r.describe().round(3))
print('== rule C: mfe/mae'); print(C.groupby(['grp','reason']).agg(N=('r','size'), r=('r','mean'), mfe=('mfe','median')).round(2))
for g in ('design','cross'):
    y = C[C.grp == g]; print(g, 'rule C rstats', {k: round(v, 3) for k, v in rstats(y).items()})
