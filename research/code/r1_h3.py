"""H3: intraday seasonality, 'a currency depreciates during its own trading hours' (Breedon & Ranaldo 2013).
H1 bars, EST. Windows: Asia 19:00-02:00 (bars 19..01), Europe 03:00-08:00 (bars 03..07), US 08:00-16:00 (bars 08..15).
Entry = open of the first bar of the window, exit = close of its last bar (calendar rule, no look-ahead).
Half W = short the WESTERN currency of the pair during its home hours (for USD pairs: long the foreign
currency during US hours); half E = short the EASTERN currency during its home hours.  Variant a = both halves.
Equal risk per pair: notional 1/sigma_20d (daily closes up to the previous NY close).  Cost: COST_PIPS round trip
per trade.  Pairs whose two currencies share a region are skipped (USDCAD, EURGBP, EURCHF, GBPCHF, AUDNZD, AUDJPY,
NZDJPY); XAUUSD is not a currency and is skipped."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_common import *
from sig import load

WIN = {'ASIA': (19, 1), 'EUR': (3, 7), 'US': (8, 15)}   # first and last H1 bar (open hours)
REG = {'USD': 'US', 'CAD': 'US', 'EUR': 'EUR', 'GBP': 'EUR', 'CHF': 'EUR', 'JPY': 'ASIA', 'AUD': 'ASIA', 'NZD': 'ASIA'}
ORDER = {'US': 0, 'EUR': 1, 'ASIA': 2}  # west -> east

def legs(pair):
    """Return list of (half, window, direction of the pair) or [] if skipped."""
    b, q = pair[:3], pair[3:]
    if b not in REG or q not in REG or REG[b] == REG[q]: return []
    west, east = (b, q) if ORDER[REG[b]] < ORDER[REG[q]] else (q, b)
    out = []
    for half, ccy in (('W', west), ('E', east)):
        d = -1 if ccy == b else 1          # the currency is expected to depreciate: short it
        out.append((half, REG[ccy], d))
    return out

D_PAIRS = [p for p in DESIGN if legs(p)]
C_PAIRS = [p for p in CROSS if legs(p)]

def window_returns(pair, win):
    h = load(pair, 'H1', start='2012-01-01')
    f, l = WIN[win]
    key = (h.index + pd.Timedelta(hours=7)).normalize()
    hr = h.index.hour
    a = pd.Series(h.open.values[hr == f], index=key[hr == f]); a = a[~a.index.duplicated()]
    z = pd.Series(h.close.values[hr == l], index=key[hr == l]); z = z[~z.index.duplicated()]
    df = pd.concat({'entry': a, 'exit': z}, axis=1, sort=True).dropna()
    df = df[df.index.dayofweek < 5]
    return df

def run(pairs, halves=('W', 'E'), cost_mult=1.0):
    C, Cf, X = panels()
    daily = {}
    for p in pairs:
        vol = np.log(Cf[p]).diff().rolling(20).std().shift(1) * np.sqrt(252)   # known before the trading day
        cf = COST_PIPS[p] * PIP[p] * cost_mult
        tot = None
        for half, win, d in legs(p):
            if half not in halves: continue
            wr = window_returns(p, win)
            v = vol.reindex(wr.index)
            r = (d * (wr.exit - wr.entry) - cf) / wr.entry * (0.10 / v)
            tot = r if tot is None else tot.add(r, fill_value=0.0)
        daily[p] = tot
    D = pd.DataFrame(daily).sort_index()
    D = D[(D.index >= '2012-01-01') & (D.index < END)]
    port = D.mean(axis=1, skipna=True)        # equal risk per pair
    per = D.index.to_period('W-FRI')
    lab = pd.Series(D.index, index=D.index).groupby(per).transform('max').values   # last trading day of the week
    weekly = port.groupby(lab).sum()
    per_pair = D.groupby(lab).sum()
    ntr = pd.Series(0, index=weekly.index)
    for p in pairs:
        for half, win, d in legs(p):
            if half in halves: ntr = ntr.add(window_returns(p, win).groupby(pd.Series(lab, index=D.index).reindex(window_returns(p, win).index).values).size(), fill_value=0)
    per_pair['ntrades'] = ntr
    return weekly, per_pair, D

if __name__ == '__main__':
    print('design pairs', D_PAIRS, 'cross pairs', C_PAIRS)
    for p in D_PAIRS + C_PAIRS: print(p, legs(p))
    for var, halves in (('a', ('W', 'E')), ('bW', ('W',)), ('bE', ('E',))):
        for g, pairs in (('D', D_PAIRS), ('C', C_PAIRS)):
            for cm in (0.0, 1.0, 1.5, 2.0):
                wk, pp, D = run(pairs, halves, cm)
                pd.concat({'net': wk}, axis=1).join(pp.drop(columns='ntrades').add_prefix('p_')).join(pp[['ntrades']]).to_parquet(os.path.join(OUT, f'r1_h3{var}_{g}_c{cm}.parquet'))
                print(var, g, cm, len(wk), 'ann %.4f t %.2f' % (ann_ret(wk), tstat(wk)))
