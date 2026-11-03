"""H4 deep-dive: stability around the best region, divergence-vs-no-divergence, features for filter analysis."""
import sys, os, itertools; sys.path.insert(0, os.path.dirname(__file__))
from bt import *
from multiprocessing import Pool
PAIRS = ['EURUSD','GBPUSD','USDJPY','AUDUSD','USDCAD','USDCHF','NZDUSD','XAUUSD']
def pooled(R, keys):
    return R.groupby(keys).apply(lambda x: pd.Series({'N': x.N.sum(), 'net': np.average(x.r, weights=x.N), 'gross': np.average(x.g, weights=x.N),
              'IS': np.average(x.r_is.fillna(0), weights=x.N), 'OOS': np.average(x.r_oos.fillna(0), weights=x.N), 'win': np.average(x.win, weights=x.N),
              'pairs_pos': (x.r > 0).sum()}), include_groups=False).reset_index()
def stats(tr, pair, df, **meta):
    tr['cost_r'] = COST_PIPS[pair] * PIP[pair] / (tr.risk_atr * df['atr'].values[tr.i.values]); tr['is'] = tr.t < '2019-01-01'
    return dict(pair=pair, N=len(tr), r=tr.r.mean(), g=(tr.r + tr.cost_r).mean(), r_is=tr[tr['is']].r.mean(), r_oos=tr[~tr['is']].r.mean(), win=(tr.r>0).mean(), **meta)
def job(pair):
    tf = 'H4'; base = add_indicators(load(pair, tf, start='2011-10-01')); rows = []; rows2 = []
    # 1) stability grid
    for L, mg in itertools.product((60,100,150), (3,5,8,10)):
        buy, sell, *_ = signals(base, touch='close', L=L, gap=3, rsi_margin=mg)
        df = base.copy(); idx = np.where(buy | sell)[0]; d = np.where(buy[idx], 1, -1)
        for sl, mb in itertools.product((0.75,1.0,1.5), (24,32,48)):
            tr = simulate(df, pair, idx, d, sl_atr=sl, tp_mode='mid', max_bars=mb)
            if len(tr): rows.append(stats(tr, pair, df, L=L, mg=mg, sl=sl, mb=mb))
    # 2) does divergence matter? same exit, variants of the entry condition
    buy, sell, tb, ts, jmin, jmax = signals(base, touch='close', L=100, gap=3, rsi_margin=5)
    r = base['rsi'].values; c = base['close'].values
    n = len(base); refl = r[np.clip(jmin,0,n-1)]; refh = r[np.clip(jmax,0,n-1)]
    newlow = (base['low'].values < base['low'].values[np.clip(jmin,0,n-1)]) & (jmin>=0)
    newhigh = (base['high'].values > base['high'].values[np.clip(jmax,0,n-1)]) & (jmax>=0)
    variants = {'A close-out + div(5)': (buy, sell),
                'B close-out only': (tb, ts),
                'C close-out + new low/high, NO div': (tb & newlow & (r <= refl + 5), ts & newhigh & (r >= refh - 5)),
                'D close-out + rsi<30/>70': (tb & (r < 30), ts & (r > 70)),
                'E close-out + new low/high (any rsi)': (tb & newlow, ts & newhigh),
                'F low/high-touch + div(5)': signals(base, touch='low', L=100, gap=3, rsi_margin=5)[:2]}
    for name, (b, s) in variants.items():
        idx = np.where(b | s)[0]; d = np.where(b[idx], 1, -1)
        tr = simulate(base, pair, idx, d, sl_atr=1.0, tp_mode='mid', max_bars=32)
        if len(tr): rows2.append(stats(tr, pair, base, variant=name))
    # 3) features + trades for filter analysis, base config
    df = build(pair, tf, touch='close', L=100, gap=3, rsi_margin=5)
    df.to_parquet(os.path.join(ROOT,'out',f'feat_{pair}_H4.parquet'))
    idx = np.where(df.buy.values | df.sell.values)[0]; d = np.where(df.buy.values[idx], 1, -1)
    tr = simulate(df, pair, idx, d, sl_atr=1.0, tp_mode='mid', max_bars=32); tr['pair'] = pair; tr['tf'] = tf; tr['model'] = 'mid_sl1.0_32'
    return rows, rows2, tr
if __name__ == '__main__':
    with Pool(4) as p: out = p.map(job, PAIRS)
    pd.set_option('display.width', 250); pd.set_option('display.max_rows', 500)
    R = pd.DataFrame([r for o in out for r in o[0]]); R.to_csv(os.path.join(ROOT,'out','h4_grid.csv'), index=False)
    g = pooled(R, ['L','mg','sl','mb'])
    print('=== stability grid (H4, touch=close, TP=mid) ===')
    print(g.round(3).to_string(index=False))
    print('\nmarginals:')
    for k in ['L','mg','sl','mb']: print(pooled(R, [k]).round(3).to_string(index=False))
    R2 = pd.DataFrame([r for o in out for r in o[1]])
    print('\n=== entry variants (H4, mid_sl1_32) ===')
    print(pooled(R2, ['variant']).round(3).to_string(index=False))
    print(R2.pivot(index='pair', columns='variant', values='r').round(3).to_string())
    T = pd.concat([o[2] for o in out]); T.to_parquet(os.path.join(ROOT,'out','trades_h4.parquet'))
