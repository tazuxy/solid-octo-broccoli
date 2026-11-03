"""Hold-out iteration helpers: augment the overlapping-signal files with extra (look-ahead-free) features
and evaluate rule + filter combinations per instrument group x period."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from bt import *
from port import no_overlap, rstats
DESIGN = ['EURUSD','GBPUSD','USDJPY','AUDUSD','USDCAD','USDCHF','NZDUSD','XAUUSD']
CROSS = ['EURJPY','GBPJPY','EURGBP','AUDJPY','EURAUD','EURCHF','CADJPY','AUDNZD','NZDJPY','GBPCHF']

def d1_move(hi):
    c, o = hi['close'].values, hi['open'].values
    a = atr(hi['high'].values, hi['low'].values, c, 14)
    out = pd.DataFrame(index=hi.index)
    out['d1_body'] = (c - o) / a                      # last completed D1 bar body in D1-ATR (signed)
    out['d1_ret3'] = (c - np.roll(c, 3)) / a          # 3-day move in D1-ATR
    return out

def augment(m):
    parts = []
    for pair, g in m.groupby('pair'):
        f = pd.read_parquet(os.path.join(ROOT, 'out', f'feat_{pair}_H4.parquet'))
        df = f.copy(); df.attrs['tf'] = 'H4'
        dm = htf_feature(df, pair, 'D1', d1_move)
        i = g.i.values; d = g.dir.values
        low, high, mid, a = f.low.values, f.high.values, f.mid.values, f.atr.values
        g = g.copy()
        g['tp_atr'] = d * (mid[i] - g.entry.values) / a[i]                 # distance entry -> fixed TP (midband)
        g['rsi_dir'] = np.where(d == 1, f.rsi.values[i], 100 - f.rsi.values[i])   # buy view: low = oversold
        g['ref_rsi_dir'] = np.where(d == 1, f.ref_rsi_b.values[i], 100 - f.ref_rsi_s.values[i])
        g['rsi_gap'] = np.where(d == 1, f.rsi_gap_b.values[i], f.rsi_gap_s.values[i])
        g['close_pos_dir'] = np.where(d == 1, f.close_pos.values[i], 1 - f.close_pos.values[i])  # 0 = close at the extreme
        g['run_dir'] = np.where(d == 1, f.run_lo.values[i], f.run_hi.values[i])
        refd = np.where(d == 1, f.ref_dist_b.values[i], f.ref_dist_s.values[i])
        j = i - refd
        g['ref_gap_atr'] = np.where(d == 1, low[j] - low[i], high[i] - high[j]) / a[i]   # new extreme beyond ref, ATR
        # previous same-direction signal within 12 bars (any signal, traded or not)
        sb = np.where(f.buy.values)[0]; ss = np.where(f.sell.values)[0]
        prev = []
        for ii, dd in zip(i, d):
            s = sb if dd == 1 else ss; p = s[(s < ii) & (s >= ii - 12)]
            prev.append(p[-1] if len(p) else -1)
        prev = np.array(prev)
        ext_now = np.where(d == 1, low[i], high[i]); ext_prev = np.where(d == 1, low[np.clip(prev, 0, None)], high[np.clip(prev, 0, None)])
        g['gap_prev_atr'] = np.where(prev >= 0, d * (ext_prev - ext_now) / a[i], np.nan)  # how far 2nd extreme beyond 1st
        g['bars_prev'] = np.where(prev >= 0, i - prev, np.nan)
        g['d1_body_dir'] = d * dm['d1_body'].values[i]       # >0: last day moved in trade direction; <0: against
        g['d1_body_abs'] = np.abs(dm['d1_body'].values[i])
        g['d1_ret3_dir'] = d * dm['d1_ret3'].values[i]
        g['gross_r'] = g.r + g.cost_r
        g['jpy'] = g.pair.str.endswith('JPY')
        parts.append(g)
    return pd.concat(parts).sort_values('t').reset_index(drop=True)

def load_all():
    d = pd.read_parquet(os.path.join(ROOT, 'out', 'signals_design.parquet')); d['grp'] = 'design'
    c = pd.read_parquet(os.path.join(ROOT, 'out', 'signals_cross.parquet')); c['grp'] = 'cross'
    return augment(pd.concat([d, c]))

BASE_C = lambda x: (x.k >= 1) & (x.risk_atr <= 1.5)
def cells(x):
    """avgR / N per group x period after one-position-per-instrument."""
    out = {}
    for grp in ('design', 'cross'):
        for per, isf in (('IS', True), ('OOS', False)):
            y = x[(x.grp == grp) & (x['is'] == isf)]
            out[f'{grp[:3]}_{per}'] = (len(y), y.r.mean() if len(y) else np.nan)
    return out
def evalrule(m, mask):
    x = no_overlap(m[mask].sort_values('t'))
    return x
