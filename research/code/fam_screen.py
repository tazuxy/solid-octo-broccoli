"""Step 1: screen strategy families on 18 instruments. Writes out/fam_trades.parquet, fam_screen.csv, fam_criteria.csv."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fam_common import *
from fam_sim import simulate
from multiprocessing import Pool

def prep(pair, tf):
    df = load(pair, tf, start='2011-01-01')
    o, h, l, c = [df[k].values.astype(float) for k in ('open', 'high', 'low', 'close')]
    a = atr(h, l, c, 14)
    ts = df.index
    feats = dict(atr_ratio=a / sma(a, 200), adx=adx(h, l, c, 14),
                 hour=np.asarray(ts.hour), dow=np.asarray((ts + pd.Timedelta(hours=7)).dayofweek))
    return dict(df=df, ts=ts, o=o, h=h, l=l, c=c, a=a, feats=feats, td=pd.Timedelta(minutes=TF_MIN[tf]))

def run(P, pair, buy, sell, **kw):
    buy = np.nan_to_num(buy).astype(bool); sell = np.nan_to_num(sell).astype(bool)
    idx = np.concatenate([np.where(buy)[0], np.where(sell)[0]])
    dr = np.concatenate([np.ones(buy.sum(), int), -np.ones(sell.sum(), int)])
    cost = COST_PIPS[pair] * PIP[pair]
    return simulate(P['ts'], P['o'], P['h'], P['l'], P['c'], P['a'], idx, dr, cost, feats=P['feats'], bar_td=P['td'], **kw)

def b(x): return np.nan_to_num(x, nan=0).astype(bool)

def htf_align(P_lo, P_hi, cols):
    hi = pd.DataFrame(cols, index=P_hi['ts']); hi['close_time'] = hi.index + P_hi['td']
    lo = pd.DataFrame({'close_time': P_lo['ts'] + P_lo['td']})
    m = pd.merge_asof(lo, hi.sort_values('close_time'), on='close_time', direction='backward')
    return {k: m[k].values for k in cols}

def worker(pair):
    out = []
    def add(tr, fam, var, tf):
        if len(tr): tr = tr.assign(fam=fam, var=var, tf=tf, pair=pair); out.append(tr)
    Ps = {tf: prep(pair, tf) for tf in ('H1', 'H4', 'D1')}
    # 1 Donchian
    for tf, Ns in (('D1', (20, 55)), ('H4', (50, 100))):
        P = Ps[tf]; h, l, c = pd.Series(P['h']), pd.Series(P['l']), P['c']
        for N in Ns:
            hiN = h.rolling(N).max().shift(1).values; loN = l.rolling(N).min().shift(1).values
            hx = h.rolling(N // 2).max().shift(1).values; lx = l.rolling(N // 2).min().shift(1).values
            buy, sell = c > hiN, c < loN
            add(run(P, pair, buy, sell, sl_atr=2, exit_long=b(c < lx), exit_short=b(c > hx), max_bars=2000), 'F1 Donchian', f'N{N} exit chan{N//2}', tf)
            add(run(P, pair, buy, sell, sl_atr=2, trail_atr=3, max_bars=2000), 'F1 Donchian', f'N{N} exit trail3', tf)
    # 2 MA cross
    for tf, pairs_ in (('D1', ((20, 50), (50, 200))), ('H4', ((50, 200),))):
        P = Ps[tf]; c = P['c']
        for f, s in pairs_:
            ef, es = ema(c, f), ema(c, s)
            up = b(ef > es); dn = b(ef < es)
            buy = up & ~np.roll(up, 1); sell = dn & ~np.roll(dn, 1); buy[0] = sell[0] = False
            add(run(P, pair, buy, sell, sl_atr=2, exit_long=dn, exit_short=up, max_bars=3000), 'F2 EMA cross', f'{f}/{s} exit cross', tf)
            add(run(P, pair, buy, sell, sl_atr=2, trail_atr=3, max_bars=3000), 'F2 EMA cross', f'{f}/{s} exit trail3', tf)
    # 3 TSMOM (D1)
    P = Ps['D1']; c = P['c']
    for L in (60, 120):
        mom = c - np.roll(c, L); mom[:L] = np.nan
        add(run(P, pair, b(mom > 0), b(mom < 0), sl_atr=3, exit_long=b(mom < 0), exit_short=b(mom > 0), max_bars=3000), 'F3 TSMOM', f'L{L} SL3', 'D1')
    # 4 RSI(2) Connors (D1)
    P = Ps['D1']; c = P['c']; r2 = rsi(c, 2); s5 = sma(c, 5); s200 = sma(c, 200)
    buy, sell = b(r2 < 10), b(r2 > 90)
    add(run(P, pair, buy, sell, sl_atr=2, exit_long=b(c > s5), exit_short=b(c < s5), max_bars=5), 'F4 RSI2 MR', 'no filter', 'D1')
    add(run(P, pair, buy & b(c > s200), sell & b(c < s200), sl_atr=2, exit_long=b(c > s5), exit_short=b(c < s5), max_bars=5), 'F4 RSI2 MR', 'SMA200 filter', 'D1')
    # 5 Squeeze breakout
    for tf in ('H4', 'D1'):
        P = Ps[tf]; c = P['c']; mid, upb, lob, _ = bbands(c, 20, 2.0)
        bw = (upb - lob) / mid
        bwp = pd.Series(bw).rolling(100).rank(pct=True)
        armed = b(bwp.rolling(10).min().shift(1).values <= 0.10)
        buy, sell = armed & b(c > upb), armed & b(c < lob)
        add(run(P, pair, buy, sell, sl_atr=1.5, trail_atr=3, max_bars=2000), 'F5 Squeeze', 'exit trail3', tf)
        add(run(P, pair, buy, sell, sl_atr=1.5, max_bars=30), 'F5 Squeeze', 'exit time30', tf)
    # 6 Pullback in D1 trend (H4 entries)
    P, D = Ps['H4'], Ps['D1']
    dal = htf_align(P, D, {'e50': ema(D['c'], 50), 'e200': ema(D['c'], 200)})
    upT, dnT = b(dal['e50'] > dal['e200']), b(dal['e50'] < dal['e200'])
    r14 = rsi(P['c'], 14)
    buy, sell = upT & b(r14 < 40), dnT & b(r14 > 60)
    add(run(P, pair, buy, sell, sl_atr=2, exit_long=b(r14 > 60), exit_short=b(r14 < 40), max_bars=1000), 'F6 Pullback', 'exit RSI', 'H4')
    add(run(P, pair, buy, sell, sl_atr=2, trail_atr=3, max_bars=1000), 'F6 Pullback', 'exit trail3', 'H4')
    # 7 Session (Tokyo range 19:00-02:00 EST, breakout 02:00-08:00 EST, flat 17:00 EST)
    P = Ps['H1']; ts = P['ts']; hr = np.asarray(ts.hour)
    sday = np.asarray((ts + pd.Timedelta(hours=5)).normalize())
    inrng = (hr >= 19) | (hr <= 1)
    g = pd.DataFrame({'d': sday, 'h': P['h'], 'l': P['l'], 'in': inrng})
    rg = g[g['in']].groupby('d').agg(rh=('h', 'max'), rl=('l', 'min'), n=('h', 'size'))
    rh = pd.Series(sday).map(rg.rh).values; rl = pd.Series(sday).map(rg.rl).values; rn = pd.Series(sday).map(rg.n).fillna(0).values
    win = (hr >= 2) & (hr <= 7) & (rn >= 6)
    c = P['c']; up = win & b(c > rh); dn = win & b(c < rl)
    ev = pd.DataFrame({'d': sday, 'up': up, 'dn': dn, 'k': np.arange(len(c))})
    first = ev[ev.up | ev.dn].groupby('d').k.first().values
    idx = first; dr = np.where(up[idx], 1, -1); slp = np.where(dr == 1, rl[idx], rh[idx])
    fx = hr == 16
    cost = COST_PIPS[pair] * PIP[pair]
    for tpR in (1, 2):
        tr = simulate(ts, P['o'], P['h'], P['l'], c, P['a'], idx, dr, cost, sl_price=slp, tp_R=tpR, force_exit=fx,
                      max_bars=20, feats=P['feats'], bar_td=P['td'])
        add(tr, 'F7 Session', f'Tokyo range TP{tpR}R', 'H1')
    return pd.concat(out, ignore_index=True)

def ref_rows():
    fs = [os.path.join(OUT, f) for f in ('trades_ruleC_design.parquet', 'trades_ruleC_cross.parquet')]
    xs = [pd.read_parquet(f) for f in fs if os.path.exists(f)]
    if not xs: return None
    x = pd.concat(xs, ignore_index=True).sort_values('t')
    keep = []; busy = {}
    for k, row in x.iterrows():
        if row.pair in busy and row.t < busy[row.pair]: continue
        keep.append(k); busy[row.pair] = row.exit_t
    x = x.loc[keep]
    x['dow'] = (x.t + pd.Timedelta(hours=7)).dt.dayofweek
    cols = ['t', 'exit_t', 'dir', 'r', 'cost_r', 'risk_atr', 'bars', 'reason', 'pair', 'atr_ratio', 'adx', 'hour', 'dow']
    x = x[cols].assign(fam='F8 REF divergence H4', var='2nd div/12 bars', tf='H4', entry_t=x.t + pd.Timedelta(hours=4))
    return x

if __name__ == '__main__':
    t0 = time.time()
    with Pool(4) as p: res = p.map(worker, ALL)
    tr = pd.concat(res, ignore_index=True)
    ref = ref_rows()
    if ref is not None: tr = pd.concat([tr, ref], ignore_index=True)
    tr = tag(tr); tr = tr[tr.t >= '2012-01-01']
    tr['strat'] = tr.fam + ' | ' + tr['var'] + ' | ' + tr.tf
    tr.to_parquet(os.path.join(OUT, 'fam_trades.parquet'))
    print('trades', len(tr), 'time %.0fs' % (time.time() - t0), flush=True)
