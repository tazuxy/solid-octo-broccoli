import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from bt import *
from port import no_overlap, rstats, FILTERS
m = pd.read_parquet(os.path.join(ROOT,'out','merged_H4.parquet')).sort_values(['pair','t']).reset_index(drop=True)
m['cost_r'] = [COST_PIPS[p]*PIP[p]/(ra*a) for p, ra, a in zip(m.pair, m.risk_atr, m.atr)]
# k-th same-direction signal within the last 12 bars (per pair)
k = np.zeros(len(m), int)
for p, g in m.groupby('pair'):
    ii = g.i.values; dd = g['dir'].values
    for a in range(len(g)):
        k[g.index[a]] = ((ii[a] - ii[:a] <= 12) & (dd[:a] == dd[a])).sum()
m['k'] = np.minimum(k, 3)
pd.set_option('display.width', 250)
print('overlap allowed, by k (0 = first signal of a cluster):')
print(m.groupby('k').apply(lambda s: pd.Series(rstats(s)), include_groups=False).round(3).to_string())
print('\nwith F1+F2+F3, by k:')
print(m[FILTERS['F1+F2+F3'](m)].groupby('k').apply(lambda s: pd.Series(rstats(s)), include_groups=False).round(3).to_string())
# alternative EA logic: shorter holding so that fewer signals are skipped
feat = {p: pd.read_parquet(os.path.join(ROOT,'out',f'feat_{p}_H4.parquet')) for p in m.pair.unique()}
rows = []
for mb in (8, 12, 16, 24, 32):
    for sl in (1.0, 1.5):
        trs = []
        for p, df in feat.items():
            idx = np.where(df.buy.values | df.sell.values)[0]; d = np.where(df.buy.values[idx], 1, -1)
            tr = simulate(df, p, idx, d, sl_atr=sl, tp_mode='mid', max_bars=mb, allow_overlap=False); tr['pair'] = p
            f = df.iloc[tr.i.values]
            tr['bw_pct'] = f.bw_pct.values; tr['atr_ratio'] = f.atr_ratio.values; tr['is'] = tr.t < '2019-01-01'
            trs.append(tr)
        T = pd.concat(trs)
        for fname, keep in (('none', np.ones(len(T), bool)), ('F1+F2+F3', (T.bw_pct < 0.6) & (T.risk_atr <= 1.5) & (T.atr_ratio < 1.5))):
            s = rstats(T[keep]); rows.append(dict(mb=mb, sl=sl, filt=fname, **s))
print('\nno-overlap, by holding limit:'); print(pd.DataFrame(rows).round(3).to_string(index=False))
