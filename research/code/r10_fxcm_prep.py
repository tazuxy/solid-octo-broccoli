"""Round 10: parse FXCM public M1 bid/ask weekly files (UTC) into one parquet per pair, index = fixed EST (UTC-5).
Usage: python3 -I r10_fxcm_prep.py <FXCM_DIR> <OUT_DIR>   (files <PAIR>_<YEAR>_<WEEK>.csv.gz from candledata.fxcorporate.com/m1/<PAIR>/<YEAR>/<WEEK>.csv.gz)
Crossed minute quotes (ask < bid at open or close, ~1-4% of rows, usually -0.1 pip: last bid and last ask come from different ticks) are KEPT; their count is printed."""
import os, sys, glob, pandas as pd
from multiprocessing import Pool
SRC, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
PAIRS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF', 'NZDUSD', 'AUDCAD', 'NZDCAD', 'AUDNZD']
def run(p):
    fr = []
    for f in sorted(glob.glob(os.path.join(SRC, f'{p}_*.csv.gz'))):
        try: d = pd.read_csv(f)
        except Exception as e: print("skip", f, e); continue
        d['ts'] = pd.to_datetime(d.DateTime, format='%m/%d/%Y %H:%M:%S.%f') - pd.Timedelta('5h'); fr.append(d.drop(columns='DateTime'))
    m = pd.concat(fr).drop_duplicates('ts').set_index('ts').sort_index()
    m.columns = ['bo', 'bh', 'bl', 'bc', 'ao', 'ah', 'al', 'ac']
    bad = (m.ac < m.bc) | (m.ao < m.bo)
    m.to_parquet(os.path.join(OUT, f'{p}_M1BA.parquet'))
    return p, len(m), int(bad.sum()), m.index.min(), m.index.max()
if __name__ == '__main__':
    with Pool(4) as pool:
        for r in pool.map(run, PAIRS): print(*r)
