import sys, os, pickle; sys.path.insert(0, os.path.dirname(__file__))
from bt import *
from multiprocessing import Pool
PAIRS = ['EURUSD','GBPUSD','USDJPY','AUDUSD','USDCAD','USDCHF','NZDUSD','XAUUSD']
def job(args):
    pair, tf = args
    df = build(pair, tf, L=40, gap=3, touch='low')
    df.to_parquet(os.path.join(ROOT, 'out', f'feat_{pair}_{tf}.parquet'))
    idx = np.where(df.buy.values | df.sell.values)[0]; d = np.where(df.buy.values[idx], 1, -1)
    res = {}
    for name, kw in {'mid_sl1.0_32': dict(sl_atr=1.0, tp_mode='mid', max_bars=32),
                     'midtrail_sl1.0_32': dict(sl_atr=1.0, tp_mode='midtrail', max_bars=32),
                     'fixed1.5_sl1.0_32': dict(sl_atr=1.0, tp_mode='fixed', tp_atr=1.5, max_bars=32),
                     'mid_sl0.5_16': dict(sl_atr=0.5, tp_mode='mid', max_bars=16)}.items():
        tr = simulate(df, pair, idx, d, **kw); tr['pair'] = pair; tr['tf'] = tf; tr['model'] = name
        res[name] = tr
    return pair, tf, res
if __name__ == '__main__':
    tfs = sys.argv[1:] or ['M15','H1']
    with Pool(4) as p: out = p.map(job, [(pr, tf) for pr in PAIRS for tf in tfs])
    allt = pd.concat([tr for _,_,res in out for tr in res.values()])
    allt.to_parquet(os.path.join(ROOT, 'out', 'trades_bt1.parquet'))
    pd.set_option('display.width', 250)
    for tf in tfs:
        print(f'\n===== {tf} =====')
        sub = allt[allt.tf == tf]
        print(sub.groupby(['model','dir']).apply(lambda x: pd.Series(summary(x)), include_groups=False).round(3))
        print(sub[sub.model=='mid_sl1.0_32'].groupby(['pair','dir']).apply(lambda x: pd.Series(summary(x)), include_groups=False).round(3))
