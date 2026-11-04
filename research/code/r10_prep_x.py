"""Round 10: bars for the extra crosses (histdata M1, fixed EST), 2005-2024, same cleaning as r2/r4
(isolated M1 rows deviating >10% from the centred 61-min rolling median are dropped).
Input: <ROOT>/../work2/data{,_early}/DAT_ASCII_<PAIR>_M1_<Y>.zip via env XDATA (default /home/user/work2).
Output: <ROOT>/bars_x/<PAIR>_{M5,M15,H1,D1}.parquet and out/r10_x_coverage.csv. Run from the work dir copy of code/."""
import os, sys, glob, zipfile, numpy as np, pandas as pd
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prep, r2_prep_full
ROOT = prep.ROOT; X = os.environ.get('XDATA', '/home/user/work2')
PAIRS = ['AUDCAD', 'NZDCAD', 'CHFJPY', 'CADCHF', 'GBPCAD', 'EURCAD', 'AUDCHF', 'NZDCHF', 'GBPAUD', 'GBPNZD', 'EURNZD']
os.makedirs(os.path.join(ROOT, 'bars_x'), exist_ok=True)
def load(pair):
    fr = []
    for d in ('data_early', 'data'):
        for zp in sorted(glob.glob(os.path.join(X, d, f'DAT_ASCII_{pair}_M1_*.zip'))):
            with zipfile.ZipFile(zp) as z:
                name = [n for n in z.namelist() if n.endswith('.csv')][0]
                with z.open(name) as f: df = pd.read_csv(f, sep=';', header=None, names=['ts', 'open', 'high', 'low', 'close', 'vol'])
            df['ts'] = pd.to_datetime(df['ts'], format='%Y%m%d %H%M%S'); fr.append(df.drop(columns='vol'))
    return pd.concat(fr).drop_duplicates('ts').set_index('ts').sort_index()
def run(p):
    m1, nwin, nspk = r2_prep_full.clean(p, load(p))
    for rule, tag in [('5min', 'M5'), ('15min', 'M15'), ('1h', 'H1')]:
        prep.resample(m1, rule).to_parquet(os.path.join(ROOT, 'bars_x', f'{p}_{tag}.parquet'))
    d = prep.resample(m1.shift(freq='7h'), '1D'); d.index = d.index - pd.Timedelta('7h')
    d.to_parquet(os.path.join(ROOT, 'bars_x', f'{p}_D1.parquet'))
    yrs = m1.groupby(m1.index.year).size()
    return dict(pair=p, m1=len(m1), dropped_spikes=nspk, first=m1.index.min(), last=m1.index.max(),
                min_rows_year=int(yrs.min()), min_year=int(yrs.idxmin()))
if __name__ == '__main__':
    with Pool(4) as pool: rows = pool.map(run, PAIRS)
    cov = pd.DataFrame(rows); cov.to_csv(os.path.join(ROOT, 'out', 'r10_x_coverage.csv'), index=False); print(cov.to_string(index=False))
