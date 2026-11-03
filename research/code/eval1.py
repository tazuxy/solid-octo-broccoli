"""Stage 1: does the signal have predictive value? Forward returns (ATR units) after signal vs baselines."""
import sys, os, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from sig import *
from multiprocessing import Pool

PAIRS = ['EURUSD','GBPUSD','USDJPY','AUDUSD','USDCAD','USDCHF','NZDUSD','XAUUSD']
HZ = (4, 8, 16, 32, 64)

def run(args):
    pair, tf = args
    df = add_indicators(load(pair, tf))
    buy, sell, tb, ts, jmin, jmax = signals(df, L=40, gap=3, touch='low')
    r = df['rsi'].values
    rows = []
    variants = {
        'touch+div (signal)': (buy, sell),
        'touch, no div': (tb & ~buy, ts & ~sell),
        'touch only': (tb, ts),
        'rsi<30 / >70': ((r < 30), (r > 70)),
        'touch & rsi<30/>70': (tb & (r < 30), ts & (r > 70)),
    }
    for name, (b, s) in variants.items():
        for d, m in (('buy', b), ('sell', s)):
            st = fwd_stats(df, m, 1 if d == 'buy' else -1, HZ)
            row = {'pair': pair, 'tf': tf, 'variant': name, 'dir': d, 'N': st[HZ[0]][0]}
            for hz in HZ:
                row[f'm{hz}'] = st[hz][1]; row[f'w{hz}'] = st[hz][2]; row[f't{hz}'] = st[hz][3]
            rows.append(row)
    return rows

if __name__ == '__main__':
    tfs = sys.argv[1:] or ['M15', 'H1']
    jobs = [(p, tf) for p in PAIRS for tf in tfs]
    with Pool(4) as pool:
        res = pool.map(run, jobs)
    out = pd.DataFrame([r for rr in res for r in rr])
    out.to_csv(os.path.join(ROOT, 'out', 'eval1.csv'), index=False)
    pd.set_option('display.width', 250); pd.set_option('display.max_rows', 500)
    for tf in tfs:
        print(f'\n===== {tf} =====')
        sub = out[out.tf == tf]
        # pooled summary across pairs: weighted by N
        g = sub.groupby(['variant','dir']).apply(lambda x: pd.Series({
            'N': x.N.sum(), **{f'm{h}': np.average(x[f'm{h}'], weights=x.N) for h in HZ},
            **{f'w{h}': np.average(x[f'w{h}'], weights=x.N) for h in (8, 16, 32)}}), include_groups=False)
        print(g.round(3))
        print('\nper pair, signal only, horizon 16 & 32:')
        print(sub[sub.variant.str.startswith('touch+div')][['pair','dir','N','m8','w8','t8','m16','w16','t16','m32','w32','t32']].round(3).to_string(index=False))
