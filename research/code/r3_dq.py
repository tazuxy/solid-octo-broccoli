"""Round 3 data-quality scan of the equity-index M1 data (data_idx/). Diagnostics only (no strategy results looked at).
Prints: per-year M1 rows / D1 bars, missing weekdays vs the SPX calendar, M1 spikes (> THR from centred 61-min median),
large daily moves, level breaks."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prep
ROOT = prep.ROOT; prep.DATA = os.path.join(ROOT, 'data_idx')
SYMS = ['SPXUSD', 'GRXEUR', 'UKXGBP', 'JPXJPY', 'AUXAUD']
THR = float(sys.argv[1]) if len(sys.argv) > 1 else 0.02
if __name__ == '__main__':
    d1s = {}
    for s in SYMS:
        m1 = prep.load_pair(s)
        print(f'===== {s}: M1 rows {len(m1)} {m1.index.min()} .. {m1.index.max()}')
        print('rows/year:', m1.groupby(m1.index.year).size().to_dict())
        bad = (m1.high < m1.low) | (m1[['open', 'close']].max(axis=1) > m1.high + 1e-9) | (m1[['open', 'close']].min(axis=1) < m1.low - 1e-9)
        print('OHLC-inconsistent rows:', int(bad.sum()))
        med = m1.close.rolling(61, center=True, min_periods=11).median()
        dev = np.log(m1[['open', 'high', 'low', 'close']].div(med, axis=0)).abs().max(axis=1)
        sp = dev[dev > THR]
        print(f'M1 rows deviating > {THR:.0%} from centred 61-min median: {len(sp)}')
        if len(sp):
            g = (sp.index.to_series().diff() > pd.Timedelta('10min')).cumsum()
            for _, x in sp.groupby(g.values):
                print('   ', x.index[0], '..', x.index[-1], 'n', len(x), 'maxdev %.3f' % x.max())
        d = prep.resample(m1.shift(freq='7h'), '1D'); d.index = d.index - pd.Timedelta('7h')
        d = d[d.index.dayofweek != 5]; d.index = (d.index + pd.Timedelta(days=1)).normalize(); d = d[~d.index.duplicated(keep='last')]
        d1s[s] = d
        r = np.log(d.close).diff()
        print('|daily log ret| > 7%:', [(str(t.date()), round(v, 3)) for t, v in r[r.abs() > 0.07].items()])
    cal = d1s['SPXUSD'].index
    for s in SYMS:
        idx = d1s[s].index
        allwd = pd.bdate_range('2010-11-16', '2024-12-31')
        miss = allwd.difference(idx)
        # missing runs > 3 weekdays
        runs = []
        if len(miss):
            g = (pd.Series(miss).diff() > pd.Timedelta('4D')).cumsum()
            for _, x in pd.Series(miss).groupby(g.values):
                if len(x) >= 3: runs.append((str(x.iloc[0].date()), str(x.iloc[-1].date()), len(x)))
        print(s, 'weekdays without D1 bar:', len(miss), ' runs>=3:', runs)
