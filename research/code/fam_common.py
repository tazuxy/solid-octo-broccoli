"""Shared helpers for fam_* scripts."""
import sys, os, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sig import rsi, atr, bbands, load, ROOT
from bt import PIP, COST_PIPS, TF_MIN, adx
OUT = os.path.join(ROOT, 'out')
DESIGN = ['EURUSD','GBPUSD','USDJPY','AUDUSD','USDCAD','USDCHF','NZDUSD','XAUUSD']
CROSS = ['EURJPY','GBPJPY','EURGBP','AUDJPY','EURAUD','EURCHF','CADJPY','AUDNZD','NZDJPY','GBPCHF']
ALL = DESIGN + CROSS
IS_END = pd.Timestamp('2019-01-01')

def ema(x, n):
    e = pd.Series(x).ewm(span=n, adjust=False).mean().values.copy(); e[:n] = np.nan; return e

def sma(x, n): return pd.Series(x).rolling(n).mean().values

def stats(r, exit_t=None):
    r = np.asarray(r, float); N = len(r)
    if N == 0: return dict(N=0, avgR=np.nan, win=np.nan, sumR=0.0, t=np.nan, maxDD_R=0.0)
    rr = r if exit_t is None else r[np.argsort(np.asarray(exit_t), kind='stable')]
    cs = np.cumsum(rr); dd = (cs - np.maximum.accumulate(np.maximum(cs, 0))).min()
    sd = r.std(ddof=1) if N > 2 else np.nan
    return dict(N=N, avgR=r.mean(), win=(r > 0).mean(), sumR=r.sum(),
                t=r.mean() / (sd / np.sqrt(N)) if N > 2 and sd > 0 else np.nan, maxDD_R=min(dd, 0.0))

def tag(tr):
    tr = tr.copy(); tr['group'] = np.where(tr.pair.isin(DESIGN), 'design', 'cross')
    tr['period'] = np.where(tr.t < IS_END, 'IS', 'OOS'); return tr

def ccy_exposure(pair, d):
    if pair == 'XAUUSD': return {'XAU': d, 'USD': -d}
    return {pair[:3]: d, pair[3:]: -d}

def select(tr, max_pos=None, ccy_cap=None, month_stop=None, week_stop=None):
    """Portfolio-level selection in time order (one position per pair is already enforced).
    max_pos: cap on concurrent positions; ccy_cap: max open positions with the same currency in the same direction;
    month_stop/week_stop: no new entries for the rest of the calendar month/week once realised R in it <= -X."""
    x = tr.sort_values(['entry_t', 'pair']).reset_index(drop=True)
    ent = x.entry_t.values; ext = x.exit_t.values; r = x.r.values
    keep = np.zeros(len(x), bool); open_ = []  # (exit_t, r, exposure dict)
    realised = []  # (exit_t, r) of closed taken trades
    for k in range(len(x)):
        t = ent[k]
        still = []
        for e in open_:
            if e[0] <= t: realised.append((e[0], e[1]))
            else: still.append(e)
        open_ = still
        if max_pos is not None and len(open_) >= max_pos: continue
        ex = ccy_exposure(x.pair.iat[k], int(x.dir.iat[k]))
        if ccy_cap is not None:
            bad = False
            for cc, sgn in ex.items():
                if sum(1 for e in open_ if e[2].get(cc) == sgn) >= ccy_cap: bad = True; break
            if bad: continue
        if month_stop is not None or week_stop is not None:
            ts = pd.Timestamp(t)
            if month_stop is not None:
                m0 = ts.to_period('M').start_time
                if sum(v for et, v in realised if pd.Timestamp(et) >= m0) <= -month_stop: continue
            if week_stop is not None:
                t7 = ts + pd.Timedelta(hours=7); w0 = (t7 - pd.Timedelta(days=t7.dayofweek)).normalize() - pd.Timedelta(hours=7)
                if sum(v for et, v in realised if pd.Timestamp(et) >= w0) <= -week_stop: continue
        keep[k] = True; open_.append((ext[k], r[k], ex))
    return x[keep]

def equity(x, risk=0.005, rcol='r'):
    """Fixed-fractional equity, P/L realised at exit, position risk = risk * equity at entry."""
    ev = [(t, 1, k) for k, t in enumerate(x.exit_t.values)] + [(t, 0, k) for k, t in enumerate(x.entry_t.values)]
    ev.sort(key=lambda e: (e[0], -e[1]))  # exits before entries at the same time
    eq = 1.0; amt = {}; pts = []
    r = x[rcol].values
    for t, typ, k in ev:
        if typ == 0: amt[k] = risk * eq
        else: eq += amt.pop(k) * r[k]; pts.append((t, eq))
    c = pd.Series([v for _, v in pts], index=pd.DatetimeIndex([t for t, _ in pts])).groupby(level=0).last()
    return c

def curve_stats(c, start='2012-01-01', end='2025-01-01'):
    c0 = pd.concat([pd.Series([1.0], index=[pd.Timestamp(start)]), c]).groupby(level=0).last()
    dd = (c0 / c0.cummax() - 1).min()
    yrs = (pd.Timestamp(end) - pd.Timestamp(start)).days / 365.25
    cagr = c0.iloc[-1] ** (1 / yrs) - 1
    d = c0.resample('D').last().ffill()
    mon = d.resample('ME').last().pct_change().dropna()
    sharpe = mon.mean() / mon.std() * np.sqrt(12) if mon.std() > 0 else np.nan
    hi = d.cummax(); newhi = d.index[d >= hi]
    gaps = np.diff(np.r_[newhi.values, np.datetime64(d.index[-1])]).astype('timedelta64[D]').astype(int)
    flat = gaps.max() / 30.44 if len(gaps) else np.nan
    yearly = d.resample('YE').last().pct_change()
    yearly.iloc[0] = d.resample('YE').last().iloc[0] / 1.0 - 1
    return dict(final=c0.iloc[-1], cagr=cagr, maxdd=dd, sharpe=sharpe, flat_months=flat), yearly
