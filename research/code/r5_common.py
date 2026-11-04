"""Round 5 shared helpers. Data clock = fixed EST (UTC-5, no DST); JST = EST + 14h.
Trades are stored with gross_pips (bid-only), R_pips (risk unit) and cost_pips (1x user cost); net R at cost multiple m
= (gross_pips - m*cost_pips) / R_pips."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sig import atr
from r4_common import ROOT, OUT, DESIGN, CROSS, PIP, tstat, maxdd, longest_flat_days

USER_COST = 0.5            # pips round trip, every FX pair (user assumption)
GOLD_COST = 30.0           # XAUUSD 0.30 USD round trip (PIP=0.01) = bt.COST_PIPS
GOLD_COST_ALT = 20.0       # 0.20 USD

def load_m5(pair):
    return pd.read_parquet(os.path.join(ROOT, 'bars_m5', f'{pair}_M5.parquet'))

def load_full(pair, tf):
    return pd.read_parquet(os.path.join(ROOT, 'bars_full', f'{pair}_{tf}.parquet'))

def d1_atr_table(pair):
    """D1 ATR(14) indexed by bar close time (D1 bars start 17:00 EST). Guard: 14-bar window must span <= 24 days."""
    d1 = load_full(pair, 'D1')
    a = atr(d1.high.values, d1.low.values, d1.close.values, 14)
    span = pd.Series(d1.index).diff(13).dt.days.values
    return pd.DataFrame({'close_time': d1.index + pd.Timedelta('1D'), 'atr': np.where(span <= 24, a, np.nan)}).sort_values('close_time')

def attach_atr(tr, pair, col='t_ent'):
    """ATR of the last D1 bar closed at or before the entry time (no look-ahead)."""
    if len(tr) == 0: tr['d1_atr'] = []; return tr
    tab = d1_atr_table(pair)
    x = tr[[col]].reset_index().sort_values(col)
    m = pd.merge_asof(x, tab, left_on=col, right_on='close_time', direction='backward').sort_values('index')
    tr = tr.copy(); tr['d1_atr'] = m['atr'].values
    return tr

# ---------- DST helpers (date level) ----------
def _last_sunday(y, m):
    d = pd.Timestamp(year=y, month=m, day=1) + pd.offsets.MonthEnd(0)
    return d - pd.Timedelta(days=(d.dayofweek + 1) % 7)

def _nth_sunday(y, m, n):
    d = pd.Timestamp(year=y, month=m, day=1)
    first = d + pd.Timedelta(days=(6 - d.dayofweek) % 7)
    return first + pd.Timedelta(weeks=n - 1)

def eu_summer(date):
    """EU/UK summer time (CEST/BST) on local calendar date: last Sun Mar <= date < last Sun Oct."""
    y = date.year
    return _last_sunday(y, 3) <= date.normalize() < _last_sunday(y, 10)

def us_summer(date):
    y = date.year
    if y >= 2007: a, b = _nth_sunday(y, 3, 2), _nth_sunday(y, 11, 1)
    else: a, b = _nth_sunday(y, 4, 1), _last_sunday(y, 10)
    return a <= date.normalize() < b

# ---------- path simulation ----------
def sim_path(o, h, l, i0, i1, d, tp, sl):
    """Entry at o[i0]; bars i0..i1 inclusive checked. Returns (exit_price, reason, exit_idx) or (None,'time',i1).
    Conservative: SL before TP inside a bar; a gap through a level at a later bar's open fills at that open."""
    hh = h[i0:i1 + 1]; ll = l[i0:i1 + 1]; oo = o[i0:i1 + 1]
    if d > 0: hs = ll <= sl; ht = hh >= tp
    else:     hs = hh >= sl; ht = ll <= tp
    any_ = hs | ht
    if not any_.any(): return None, 'time', i1
    j = int(np.argmax(any_))
    if j > 0:
        op = oo[j]
        if (d > 0 and op <= sl) or (d < 0 and op >= sl): return op, 'sl', i0 + j
        if (d > 0 and op >= tp) or (d < 0 and op <= tp): return op, 'tp', i0 + j
    if hs[j]: return sl, 'sl', i0 + j
    return tp, 'tp', i0 + j

def period3(year, gold=False):
    y = np.asarray(year)
    a = '2009-2011' if gold else '2005-2011'
    return np.where(y <= 2011, a, np.where(y <= 2018, '2012-2018', '2019-2024'))

def group_of(p):
    return 'design' if p in DESIGN else ('cross' if p in CROSS else 'gold' if p == 'XAUUSD' else 'other')

def netR(tr, m=1.0, cost_col='cost_pips'):
    return ((tr.gross_pips - m * tr[cost_col]) / tr.R_pips).values

def evaluate(tr, trd, gold=False, extra_cost=None):
    """tr: base trades, trd: one-bar-delayed trades. Returns dict of all criteria."""
    tr = tr.sort_values(['t_ent', 'inst']).reset_index(drop=True)
    r1 = netR(tr, 1); r0 = netR(tr, 0); r2 = netR(tr, 2); r4 = netR(tr, 4)
    per = period3(tr.t_ent.dt.year, gold)
    cells = {}
    for g in sorted(tr.group.unique()):
        for p in sorted(set(per)):
            mk = (tr.group.values == g) & (per == p)
            cells[f'{g}|{p}'] = (r1[mk].mean() if mk.any() else np.nan, int(mk.sum()))
    c1 = all(v[0] > 0 for v in cells.values())
    t1 = tstat(r1); s = r1.sum(); dd = maxdd(r1); ratio = s / abs(dd) if dd < 0 else np.inf
    insts = tr.inst.unique(); pos = tr.assign(r=r1).groupby('inst').r.sum()
    frac = (pos > 0).mean(); c4 = True if len(insts) <= 1 else frac >= 0.6
    k = int(np.ceil(0.05 * len(r1))); rs = np.sort(r1)[::-1]; drop5 = rs[k:].mean()
    rd = netR(trd, 1) if len(trd) else np.array([np.nan])
    out = dict(N=len(r1), gross_avgR=r0.mean(), gross_pips=tr.gross_pips.mean(), avgR=r1.mean(), t=t1, sumR=s, maxDD=dd,
               ratio=ratio, avgR_x2=r2.mean(), avgR_x4=r4.mean(), drop5=drop5, delay_avgR=np.nanmean(rd), delay_N=len(trd),
               inst_pos=f'{int((pos > 0).sum())}/{len(pos)}', frac=frac, cells=cells,
               flat_days=longest_flat_days(tr.t_ent, r1), med_R_pips=tr.R_pips.median(), win=(r1 > 0).mean())
    if extra_cost is not None:
        out['avgR_alt'] = ((tr.gross_pips - extra_cost) / tr.R_pips).mean()
    out['c1'] = c1; out['c2'] = t1 >= 3.0; out['c3'] = ratio >= 3; out['c4'] = c4
    out['c5'] = out['avgR_x2'] > 0; out['c6'] = (drop5 > 0) and (out['delay_avgR'] > 0)
    out['PASS'] = all(out[c] for c in ('c1', 'c2', 'c3', 'c4', 'c5', 'c6'))
    return out
