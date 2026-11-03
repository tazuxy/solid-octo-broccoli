"""Unzip histdata M1 csv files, build M15/H1/H4/D1 bars, save parquet per instrument.
Timestamps are histdata EST (UTC-5, no DST)."""
import sys, zipfile, io, glob, os
import pandas as pd, numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, os.environ.get('DATA_DIR', 'data')); OUT = os.path.join(ROOT, os.environ.get('BARS_DIR', 'bars'))

def load_pair(pair):
    frames = []
    for zp in sorted(glob.glob(os.path.join(DATA, f'DAT_ASCII_{pair.upper()}_M1_*.zip'))):
        with zipfile.ZipFile(zp) as z:
            name = [n for n in z.namelist() if n.endswith('.csv')][0]
            with z.open(name) as f:
                df = pd.read_csv(f, sep=';', header=None, names=['ts','open','high','low','close','vol'])
        df['ts'] = pd.to_datetime(df['ts'], format='%Y%m%d %H%M%S')
        frames.append(df.drop(columns='vol'))
    m1 = pd.concat(frames).drop_duplicates('ts').set_index('ts').sort_index()
    return m1

def resample(m1, rule, offset=None):
    o = m1.resample(rule, label='left', closed='left', offset=offset).agg(
        {'open':'first','high':'max','low':'min','close':'last'})
    return o.dropna()

if __name__ == '__main__':
    pairs = sys.argv[1:]
    for p in pairs:
        m1 = load_pair(p)
        print(p, 'M1 rows', len(m1), m1.index.min(), m1.index.max())
        for rule, tag in [('15min','M15'), ('1h','H1'), ('4h','H4')]:
            b = resample(m1, rule)
            b.to_parquet(os.path.join(OUT, f'{p.upper()}_{tag}.parquet'))
            print('  ', tag, len(b))
        # daily bars aligned to NY close 17:00 EST: shift so the day starts at 17:00
        d = resample(m1.shift(freq='7h'), '1D'); d.index = d.index - pd.Timedelta('7h')
        d.to_parquet(os.path.join(OUT, f'{p.upper()}_D1.parquet'))
        print('   D1', len(d))
