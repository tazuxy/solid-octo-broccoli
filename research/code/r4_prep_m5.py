"""Round 4: build M5 bars 2005-2024 from histdata M1 (data_early + data), fixed EST (UTC-5).
Data-quality fixes reused from r2_prep_full.clean(): AUDJPY 2005-05-01..05-15 contamination dropped; isolated M1 rows
deviating >10% from the centred 61-min rolling median dropped. Applied to ALL years (2012+ spike count reported; r2 left 2012+ untouched).
Resampling identical to prep.resample (left-labelled). Output bars_m5/<PAIR>_M5.parquet."""
import os, sys, glob, zipfile, numpy as np, pandas as pd
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prep, r2_prep_full
ROOT = prep.ROOT
PAIRS = ['EURUSD','GBPUSD','USDJPY','AUDUSD','USDCAD','USDCHF','NZDUSD',
         'EURJPY','GBPJPY','EURGBP','AUDJPY','EURAUD','EURCHF','CADJPY','AUDNZD','NZDJPY','GBPCHF']

def load(pair):
    fr = []
    for d in ('data_early', 'data'):
        for zp in sorted(glob.glob(os.path.join(ROOT, d, f'DAT_ASCII_{pair}_M1_*.zip'))):
            with zipfile.ZipFile(zp) as z:
                name = [n for n in z.namelist() if n.endswith('.csv')][0]
                with z.open(name) as f:
                    df = pd.read_csv(f, sep=';', header=None, names=['ts','open','high','low','close','vol'])
            df['ts'] = pd.to_datetime(df['ts'], format='%Y%m%d %H%M%S'); fr.append(df.drop(columns='vol'))
    return pd.concat(fr).drop_duplicates('ts').set_index('ts').sort_index()

def run(p):
    m1, nwin, nspk = r2_prep_full.clean(p, load(p))
    b = prep.resample(m1, '5min'); b.to_parquet(os.path.join(ROOT, 'bars_m5', f'{p}_M5.parquet'))
    return dict(pair=p, m1=len(m1), dropped_window=nwin, dropped_spikes=nspk, m5=len(b), first=b.index.min(), last=b.index.max())

if __name__ == '__main__':
    with Pool(4) as pool: rows = pool.map(run, PAIRS)
    cov = pd.DataFrame(rows); cov.to_csv(os.path.join(ROOT, 'out', 'r4_m5_coverage.csv'), index=False); print(cov.to_string(index=False))
