"""Round 11: M5 bars for equity-index CFDs (histdata, data_idx, 2010-11..2024) and XAUUSD (data_early + data, 2009-03..2024),
fixed EST, same isolated-spike cleaning as r2/r4 (M1 rows >10% from the centred 61-min rolling median dropped).
Usage: python3 -I r11_prep.py <WORK>   -> <WORK>/bars_r11/<SYM>_M5.parquet"""
import os, sys, glob, zipfile, numpy as np, pandas as pd
from multiprocessing import Pool
W = sys.argv[1]; OUT = os.path.join(W, 'bars_r11'); os.makedirs(OUT, exist_ok=True)
JOBS = {'SPXUSD': ['data_idx'], 'UKXGBP': ['data_idx'], 'JPXJPY': ['data_idx'], 'AUXAUD': ['data_idx'], 'XAUUSD': ['data_early', 'data']}
def run(sym):
    fr = []
    for d in JOBS[sym]:
        for z in sorted(glob.glob(os.path.join(W, d, f'DAT_ASCII_{sym}_M1_*.zip'))):
            with zipfile.ZipFile(z) as f:
                n = [x for x in f.namelist() if x.endswith('.csv')][0]
                x = pd.read_csv(f.open(n), sep=';', header=None, names=['ts', 'open', 'high', 'low', 'close', 'v'])
            x['ts'] = pd.to_datetime(x.ts, format='%Y%m%d %H%M%S'); fr.append(x.drop(columns='v'))
    m = pd.concat(fr).drop_duplicates('ts').set_index('ts').sort_index()
    med = m.close.rolling(61, center=True, min_periods=11).median()
    dev = np.log(m[['open', 'high', 'low', 'close']].div(med, axis=0)).abs().max(axis=1); bad = int((dev > 0.10).sum()); m = m[~(dev > 0.10)]
    b = m.resample('5min', label='left', closed='left').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'}).dropna()
    b.to_parquet(os.path.join(OUT, f'{sym}_M5.parquet'))
    return sym, len(m), bad, str(m.index.min()), str(m.index.max())
if __name__ == '__main__':
    with Pool(5) as p:
        for r in p.map(run, list(JOBS)): print(*r)
