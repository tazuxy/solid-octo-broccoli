"""Round 2: build continuous 2005-2024 bars in bars_full/ = CLEANED 2005-2011 (from data_early M1) + bars/ (2012-2024, unchanged).
Data-quality cleaning of the early M1 data (defined from data errors only, before any strategy result was looked at):
  (1) AUDJPY 2005-05-01 17:00 .. 2005-05-15 18:34: the file mixes prices of other instruments (values 0.67 .. 136) -> dropped.
  (2) isolated bad ticks: an M1 row is dropped if any of O/H/L/C deviates > 10% from the centred 61-minute rolling
      median of M1 closes (found: single spikes in AUDUSD 2005-11-21, USDCHF 2005-01-11, NZDUSD 2008-12-23, GBPCHF 2007-08-06).
Resampling is identical to prep.py (left-labelled M15/H1/H4, D1 17:00->17:00 EST)."""
import os, sys, glob, zipfile, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prep
ROOT = prep.ROOT
prep.DATA = os.path.join(ROOT, 'data_early')
PAIRS = ['EURUSD','GBPUSD','USDJPY','AUDUSD','USDCAD','USDCHF','NZDUSD','XAUUSD',
         'EURJPY','GBPJPY','EURGBP','AUDJPY','EURAUD','EURCHF','CADJPY','AUDNZD','NZDJPY','GBPCHF']
os.makedirs(os.path.join(ROOT, 'bars_full'), exist_ok=True)

def clean(p, m1):
    n0 = len(m1)
    if p == 'AUDJPY':
        m1 = m1[~((m1.index >= '2005-05-01 17:00') & (m1.index <= '2005-05-15 18:34'))]
    n1 = len(m1)
    med = m1.close.rolling(61, center=True, min_periods=11).median()
    dev = np.log(m1[['open', 'high', 'low', 'close']].div(med, axis=0)).abs().max(axis=1)
    m1 = m1[~(dev > 0.10)]
    return m1, n0 - n1, n1 - len(m1)

def bars_from_m1(m1):
    out = {}
    for rule, tag in [('15min', 'M15'), ('1h', 'H1'), ('4h', 'H4')]: out[tag] = prep.resample(m1, rule)
    d = prep.resample(m1.shift(freq='7h'), '1D'); d.index = d.index - pd.Timedelta('7h'); out['D1'] = d
    return out

if __name__ == '__main__':
    rows = []
    for p in PAIRS:
        m1, nwin, nspk = clean(p, prep.load_pair(p))
        eb = bars_from_m1(m1)
        for tf in ('M15', 'H1', 'H4', 'D1'):
            a = eb[tf]; orig = pd.read_parquet(os.path.join(ROOT, 'bars_early', f'{p}_{tf}.parquet'))
            b = pd.read_parquet(os.path.join(ROOT, 'bars', f'{p}_{tf}.parquet'))
            common = a.index.intersection(orig.index)
            changed = int((a.loc[common] != orig.loc[common]).any(axis=1).sum()) + len(orig.index.difference(a.index))
            m = pd.concat([a[~a.index.isin(b.index)], b]).sort_index()
            assert m.index.is_unique and m.index.is_monotonic_increasing
            m.to_parquet(os.path.join(ROOT, 'bars_full', f'{p}_{tf}.parquet'))
            if tf in ('H4', 'D1'): rows.append(dict(pair=p, tf=tf, early_from=a.index.min(), early_to=a.index.max(), main_from=b.index.min(),
                                       m1_dropped_window=nwin, m1_dropped_spikes=nspk, bars_changed_vs_bars_early=changed, n=len(m)))
        print(p, nwin, nspk, flush=True)
    cov = pd.DataFrame(rows); cov.to_csv(os.path.join(ROOT, 'out', 'r2_coverage.csv'), index=False); print(cov.to_string(index=False))
