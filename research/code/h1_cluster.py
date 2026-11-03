"""Does the '2nd signal' rule work on H1 / M15 too? touch=close, L=100, margin 5, TP mid, SL 1 ATR, 32 bars."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from bt import *
from port import rstats
from multiprocessing import Pool
PAIRS = ['EURUSD','GBPUSD','USDJPY','AUDUSD','USDCAD','USDCHF','NZDUSD','XAUUSD']
def job(args):
    pair, tf = args
    df = add_indicators(load(pair, tf, start='2011-10-01'))
    buy, sell, *_ = signals(df, touch='close', L=100, gap=3, rsi_margin=5)
    idx = np.where(buy | sell)[0]; d = np.where(buy[idx], 1, -1)
    k = np.array([((idx[a] - idx[:a] <= 12) & (d[:a] == d[a])).sum() for a in range(len(idx))])
    tr = simulate(df, pair, idx, d, sl_atr=1.0, tp_mode='mid', max_bars=32)
    tr['k'] = k[[list(idx).index(i) for i in tr.i]]; tr['pair'] = pair; tr['tf'] = tf; tr['is'] = tr.t < '2019-01-01'
    return tr
if __name__ == '__main__':
    with Pool(4) as p: out = p.map(job, [(pr, tf) for pr in PAIRS for tf in ('H1','M15')])
    T = pd.concat(out); pd.set_option('display.width', 250)
    for tf in ('H1','M15'):
        s = T[T.tf == tf]; s = s.assign(k=np.minimum(s.k, 2))
        print(f'== {tf} by k (overlap allowed) =='); print(s.groupby('k').apply(lambda g: pd.Series(rstats(g)), include_groups=False).round(3).to_string())
