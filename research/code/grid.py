"""Grid over signal definitions x exit models x timeframes. Pooled net/gross avg R, IS/OOS."""
import sys, os, itertools; sys.path.insert(0, os.path.dirname(__file__))
from bt import *
from multiprocessing import Pool
PAIRS = ['EURUSD','GBPUSD','USDJPY','AUDUSD','USDCAD','USDCHF','NZDUSD','XAUUSD']
SIGS = [dict(touch=t, L=L, gap=3, ref_rsi_max=rr, rsi_margin=mg) for t in ('low','close') for L in (40,100) for rr in (None,30) for mg in (0,5)]
EXITS = {'mid_sl1_32': dict(sl_atr=1.0, tp_mode='mid', max_bars=32),
         'midtrail_sl1.5_64': dict(sl_atr=1.5, tp_mode='midtrail', max_bars=64),
         'fix2_sl1_64': dict(sl_atr=1.0, tp_mode='fixed', tp_atr=2.0, max_bars=64),
         'fix1_sl1_32': dict(sl_atr=1.0, tp_mode='fixed', tp_atr=1.0, max_bars=32)}
def job(args):
    pair, tf = args
    base = add_indicators(load(pair, tf, start='2011-10-01'))
    rows = []
    for si, sk in enumerate(SIGS):
        buy, sell, *_ = signals(base, **sk)
        df = base.copy(); df['buy'] = buy; df['sell'] = sell
        idx = np.where(buy | sell)[0]; d = np.where(buy[idx], 1, -1)
        for en, ek in EXITS.items():
            tr = simulate(df, pair, idx, d, **ek)
            if len(tr) == 0: continue
            tr['cost_r'] = COST_PIPS[pair] * PIP[pair] / (tr.risk_atr * df['atr'].values[tr.i.values])
            tr['is'] = tr.t < '2019-01-01'
            rows.append(dict(pair=pair, tf=tf, sig=si, exit=en, N=len(tr), r=tr.r.mean(), g=(tr.r + tr.cost_r).mean(),
                             r_is=tr[tr['is']].r.mean(), r_oos=tr[~tr['is']].r.mean(), win=(tr.r>0).mean(), sumr=tr.r.sum()))
    return rows
if __name__ == '__main__':
    tfs = sys.argv[1:] or ['H1','H4']
    with Pool(4) as p: out = p.map(job, [(pr, tf) for pr in PAIRS for tf in tfs])
    R = pd.DataFrame([r for rr in out for r in rr]); R.to_csv(os.path.join(ROOT,'out','grid.csv'), index=False)
    pd.set_option('display.width', 250); pd.set_option('display.max_rows', 500)
    for tf in tfs:
        s = R[R.tf==tf]
        g = s.groupby(['sig','exit']).apply(lambda x: pd.Series({'N': x.N.sum(), 'net': np.average(x.r, weights=x.N), 'gross': np.average(x.g, weights=x.N),
              'IS': np.average(x.r_is, weights=x.N), 'OOS': np.average(x.r_oos, weights=x.N), 'win': np.average(x.win, weights=x.N),
              'pairs_pos': (x.r > 0).sum()}), include_groups=False).reset_index()
        g['sigdesc'] = g.sig.map(lambda i: str({k:v for k,v in SIGS[i].items() if k!='gap'}))
        print(f'\n===== {tf} ====='); print(g.sort_values('net', ascending=False).round(3).to_string(index=False))
