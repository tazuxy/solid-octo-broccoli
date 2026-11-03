"""H-B evaluation vs pre-registered criteria. Trades ordered by exit time (then pair) for the cumulative-R drawdown."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r3_common import *
def crit13(tr):
    IS = tr[tr['T'] < IS_END]; OOS = tr[tr['T'] >= IS_END]
    pp = tr.groupby('pair').R.mean()
    c1 = IS.R.mean() > 0 and OOS.R.mean() > 0 and (pp > 0).sum() >= 3
    t = tstat(tr.R); dd = maxdd_R(tr.R.values); rd = tr.R.sum() / abs(dd) if dd < 0 else np.inf
    return dict(N=len(tr), avgR=tr.R.mean(), avgR_IS=IS.R.mean(), avgR_OOS=OOS.R.mean(), pairs_pos=int((pp > 0).sum()),
                per_pair={p: round(x, 3) for p, x in pp.items()}, c1=c1, t=t, c2=t >= 2, sumR=tr.R.sum(), maxddR=dd, retdd=rd, c3=rd >= 3,
                avg_pips=tr.pips.mean(), avg_gross_R=tr.gross_R.mean(), hit=(tr.R > 0).mean())
res = []
for v in ('a', 'b'):
    tr = pd.read_parquet(os.path.join(OUT, f'r3_hb_trades_{v}_c1.0.parquet'))
    c = crit13(tr); x = crit13(pd.read_parquet(os.path.join(OUT, f'r3_hb_trades_{v}_c1.5.parquet')))
    c5 = x['c1'] and x['c2'] and x['c3']
    res.append(dict(variant=v, **c, c4=c['N'] >= 100, c5=c5, c5_detail=dict(avgR_IS=x['avgR_IS'], avgR_OOS=x['avgR_OOS'], pairs_pos=x['pairs_pos'], t=x['t'], retdd=x['retdd']),
                    PASS=c['c1'] and c['c2'] and c['c3'] and c['N'] >= 100 and c5))
    print(f'==== H-B variant {v}'); [print('  ', k, '=', (round(val, 4) if isinstance(val, float) else val)) for k, val in res[-1].items()]
    # breakdowns
    tr['year'] = tr['T'].dt.year
    print('  per pair:'); print(tr.groupby('pair').agg(N=('R', 'size'), avgR=('R', 'mean'), t=('R', tstat), sumR=('R', 'sum'), avg_pips=('pips', 'mean'), hit=('R', lambda r: (r > 0).mean())).round(3).to_string())
    print('  per pair x period:'); print(tr.assign(per=np.where(tr['T'] < IS_END, 'IS', 'OOS')).groupby(['pair', 'per']).R.agg(['size', 'mean']).unstack().round(3).to_string())
    print('  yearly sumR:'); print(tr.groupby('year').R.agg(['size', 'sum', 'mean']).round(2).T.to_string())
    # longest flat (months between new highs of cumulative R)
    cum = tr.groupby('T').R.sum().cumsum(); hi = cum.cummax(); nh = cum.index[cum >= hi]
    g = np.diff(np.r_[nh.values, np.datetime64(cum.index[-1])]).astype('timedelta64[D]').astype(int).max() / 30.44
    print('  longest flat (months):', round(g, 1))
    # direction split and |diff| distribution
    print('  by dir (+1 long pair):', tr.groupby('dir').R.agg(['size', 'mean']).round(3).to_dict())
    print('  quarter-end vs other:', tr.groupby(tr['T'].dt.month.isin([3, 6, 9, 12])).R.agg(['size', 'mean']).round(3).to_dict())
    for tag in ('proxy', 'proxy_c1.5'):
        p = crit13(pd.read_parquet(os.path.join(OUT, f'r3_hb_trades_{v}_{tag}.parquet')))
        print(f'  sensitivity {tag} (EURUSD incl. Euro Stoxx segment): N {p["N"]} avgR {p["avgR"]:.3f} IS {p["avgR_IS"]:.3f} OOS {p["avgR_OOS"]:.3f} pairs+ {p["pairs_pos"]} t {p["t"]:.2f} retdd {p["retdd"]:.2f}')
pd.DataFrame(res).to_csv(os.path.join(OUT, 'r3_hb_criteria.csv'), index=False)
