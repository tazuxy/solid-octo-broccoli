"""Step 1b: screening table + pre-registered pass/fail criteria from out/fam_trades.parquet."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fam_common import *

def screen(tr):
    rows = []
    for st, x in tr.groupby('strat', sort=False):
        for dname, dsel in (('both', None), ('buy', 1), ('sell', -1)):
            xd = x if dsel is None else x[x.dir == dsel]
            for gname in ('design', 'cross', 'all'):
                xg = xd if gname == 'all' else xd[xd.group == gname]
                for pname in ('IS', 'OOS', 'ALL'):
                    xp = xg if pname == 'ALL' else xg[xg.period == pname]
                    s = stats(xp.r.values, xp.exit_t.values)
                    rows.append(dict(strat=st, fam=x.fam.iloc[0], var=x['var'].iloc[0], tf=x.tf.iloc[0], dir=dname,
                                     group=gname, period=pname, **s))
    return pd.DataFrame(rows)

def criteria(tr):
    rows = []
    for st, x in tr.groupby('strat', sort=False):
        cell = {}
        for g in ('design', 'cross'):
            for p in ('IS', 'OOS'):
                cell[f'{g[0]}{p}'] = x[(x.group == g) & (x.period == p)].r.mean()
        s = stats(x.r.values, x.exit_t.values)
        pp = x.groupby('pair').r.sum(); npos = int((pp > 0).sum()); npairs = len(pp)
        ratio = s['sumR'] / abs(s['maxDD_R']) if s['maxDD_R'] < 0 else np.inf
        c1 = all(v > 0 for v in cell.values() if not np.isnan(v)) and not any(np.isnan(v) for v in cell.values())
        c2 = s['t'] >= 2.0; c3 = ratio >= 3; c4 = s['N'] >= 100; c5 = npos >= 12
        rows.append(dict(strat=st, N=s['N'], avgR=s['avgR'], **{f'avgR_{k}': v for k, v in cell.items()}, t=s['t'],
                         sumR=s['sumR'], maxDD_R=s['maxDD_R'], sumR_DD=ratio, pairs_pos=f'{npos}/{npairs}',
                         buy_avgR=x[x.dir == 1].r.mean(), sell_avgR=x[x.dir == -1].r.mean(),
                         C1_4cells=c1, C2_t=c2, C3_ratio=c3, C4_N=c4, C5_pairs=c5, CANDIDATE=c1 and c2 and c3 and c4 and c5))
    return pd.DataFrame(rows)

if __name__ == '__main__':
    pd.set_option('display.width', 300); pd.set_option('display.max_columns', 40); pd.set_option('display.max_rows', 500)
    tr = pd.read_parquet(os.path.join(OUT, 'fam_trades.parquet'))
    sc = screen(tr); sc.to_csv(os.path.join(OUT, 'fam_screen.csv'), index=False)
    cr = criteria(tr); cr.to_csv(os.path.join(OUT, 'fam_criteria.csv'), index=False)
    print(cr.round(3).to_string(index=False))
    print('\nbuy/sell split, all 18, by period')
    x = sc[(sc.group == 'all') & (sc.dir != 'both')].pivot_table(index=['strat', 'dir'], columns='period', values=['N', 'avgR']).round(3)
    print(x.to_string())
