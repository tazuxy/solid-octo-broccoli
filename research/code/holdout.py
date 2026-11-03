"""Run the final H4 rule set on an arbitrary instrument list (hold-out test).
usage: python -I code/holdout.py TAG PAIR1 PAIR2 ...   (bars must exist in bars/)
Rules: close outside BB(20,2), new low/high vs bars 3..100, RSI gap >= 5, TP = midband, SL = extreme -/+ 1 ATR, 32 bars.
 A: all signals (one position per instrument)   B: 2nd+ signal within 12 bars   C: B + stop <= 1.5 ATR   D: C + bw_pct < 0.6"""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from bt import *
from port import no_overlap, rstats, portfolio
from multiprocessing import Pool
def job(pair):
    df = build(pair, 'H4', touch='close', L=100, gap=3, rsi_margin=5)
    df.to_parquet(os.path.join(ROOT, 'out', f'feat_{pair}_H4.parquet'))
    idx = np.where(df.buy.values | df.sell.values)[0]; d = np.where(df.buy.values[idx], 1, -1)
    tr = simulate(df, pair, idx, d, sl_atr=1.0, tp_mode='mid', max_bars=32); tr['pair'] = pair
    f = df.iloc[tr.i.values]
    for col in ['bw_pct','bw_chg','atr_ratio','mid_slope','adx','bar_range','close_pos','run_lo','run_hi','rsi','h4_rsi','d1_adx','d1_dist20','d1_rsi','d1_atr_ratio','sma200_dist','hour','dow','atr']:
        tr[col] = f[col].values
    k = np.array([((idx[a] - idx[:a] <= 12) & (d[:a] == d[a])).sum() for a in range(len(idx))])
    pos = {i: n for n, i in enumerate(idx)}; tr['k'] = [k[pos[i]] for i in tr.i]
    tr['exit_t'] = [t + pd.Timedelta(hours=4*int(b)) for t, b in zip(tr.t, tr.bars)]
    tr['cost_r'] = COST_PIPS[pair] * PIP[pair] / (tr.risk_atr * tr.atr); tr['is'] = tr.t < '2019-01-01'
    return tr
RULES = {'A: all signals (1st entry only)': lambda x: np.ones(len(x), bool),
         'B: 2nd+ signal within 12 bars': lambda x: x.k >= 1,
         'C: B + stop<=1.5ATR': lambda x: (x.k >= 1) & (x.risk_atr <= 1.5),
         'D: C + bw_pct<0.6': lambda x: (x.k >= 1) & (x.risk_atr <= 1.5) & (x.bw_pct < 0.6)}
def report(m, tag):
    pd.set_option('display.width', 250); rows = []
    for name, f in RULES.items():
        x = no_overlap(m[f(m)].sort_values('t')); st = rstats(x)
        p = portfolio(x, risk=0.01, max_pos=4); st['cagr1%'] = p['cagr']; st['maxdd1%'] = p['maxdd']
        rows.append(dict(rule=name, **st))
        if name.startswith('C'):
            print(f'[{tag}] rule C by pair:'); print(x.groupby('pair').r.agg(['count','mean','sum']).round(2).T.to_string())
            print(f'[{tag}] rule C by year:'); print(x.groupby(x.t.dt.year).r.agg(['count','mean','sum']).round(2).T.to_string())
            print(f'[{tag}] rule C by dir:'); print(x.groupby('dir').r.agg(['count','mean','sum']).round(2).T.to_string())
            x.to_parquet(os.path.join(ROOT, 'out', f'trades_ruleC_{tag}.parquet'))
    print(f'[{tag}] summary:'); print(pd.DataFrame(rows).round(3).to_string(index=False))
if __name__ == '__main__':
    tag, pairs = sys.argv[1], sys.argv[2:]
    with Pool(4) as p: out = p.map(job, pairs)
    m = pd.concat(out).sort_values('t').reset_index(drop=True)
    m.to_parquet(os.path.join(ROOT, 'out', f'signals_{tag}.parquet'))
    report(m, tag)
