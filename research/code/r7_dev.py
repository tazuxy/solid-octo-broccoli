"""Round 7 promotion/development: stop simulation, refinement features, round-6 style selection protocol,
method-1 trade list, daily-return correlation, freeze + one-shot holdout."""
import os, sys, json, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r7_lib as L
from bt import PIP

SEL_END = pd.Timestamp('2015-01-01')     # refinement selection 2005-2014, confirmation 2015-2021

def stop_gross(T, inst, k, end):
    """gross pips (direction applied) with a stop. T.side = actual market side of each trade (+1 long / -1 short); k*R from entry. M5 bid bars (M15 for XAUUSD) from the entry bar to
    the bar before exit; a later bar opening beyond the stop fills at that open; otherwise fill at the stop."""
    if k is None: return T.gross.values.copy()
    b = L.load(inst, 'M5', end); bt_ = b.index.values; lo = b.low.values; hi = b.high.values; op = b.open.values
    pip = PIP[inst]; out = np.empty(len(T)); hit_n = 0
    for n, (ti, tx, px, R, g, d) in enumerate(zip(T.t_ent.values, T.t_exit.values, T.px.values, T.R.values, T.gross.values, T.side.values)):
        i0, i1 = np.searchsorted(bt_, ti), np.searchsorted(bt_, tx)
        sl = px - d * k * R * pip; hit = None
        if i1 > i0:
            if d > 0:
                m = lo[i0:i1] <= sl
            else:
                m = hi[i0:i1] >= sl
            if m.any():
                j = int(np.argmax(m)); oj = op[i0 + j]
                hit = oj if (j > 0 and ((d > 0 and oj <= sl) or (d < 0 and oj >= sl))) else sl
        if hit is None: out[n] = g
        else: out[n] = d * (hit - px) / pip; hit_n += 1
    return out

def apply_stop(T, inst, k, end):
    T = T.copy(); T['gross_ns'] = T.gross; T['gross'] = stop_gross(T, inst, k, end)
    T['stopped'] = T.gross != T.gross_ns if k is not None else False
    T['net'] = T.gross - T.cost; T['netR'] = T.net / T.R; T['netR2'] = (T.gross - 2 * T.cost) / T.R; T['grossR'] = T.gross / T.R
    return T

def add_features(T, inst, end):
    T = T.copy()
    d = L.asof(T.t_ent, L.d1_frame(inst, end))
    T['c_sma200'] = np.where(d.sma200.isna(), 'NA', np.where(d.close.values >= d.sma200.values, 'above', 'below'))
    ap = d.atr_pct.values
    T['c_atrpct'] = np.where(np.isnan(ap), 'NA', np.where(ap < 20, '<20', np.where(ap > 80, '>80', '20-80')))
    T['c_weekday'] = pd.to_datetime(T.t_ent).dt.dayofweek.map({0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}).values
    h = L.asof(T.t_ent, L.h4_rsi_frame(inst, end)); rv = h.h4rsi.values
    T['c_h4rsi'] = np.where(np.isnan(rv), 'NA', np.where(rv < 30, '<30', np.where(rv > 70, '>70', '30-70')))
    return T

CONDS = ['c_sma200', 'c_atrpct', 'c_weekday', 'c_h4rsi']

def select_refinement(T):
    """round-6 protocol on 2005-2014: exclude ONE bucket of ONE condition if (a) bucket mean netR < 0 and the rest has a
    higher t than the base, (b) bucket >= 15% of trades and >= 40 trades; rank by sum/|maxDD| improvement."""
    S = T[T.t_ent < SEL_END]; base = L.tstats(S.netR); bratio = L.ratio_stats(S.netR)['ratio']; rows = []
    for c in CONDS:
        for b in sorted(set(S[c]) - {'NA'}):
            m = S[c] == b; nb = int(m.sum()); rest = S.netR[~m]
            mb = float(S.netR[m].mean()) if nb else np.nan
            tr = L.tstats(rest)['t']; rr = L.ratio_stats(rest)['ratio']
            ok_a = (nb > 0) and (mb < 0) and (tr > base['t']); ok_b = (nb >= 0.15 * len(S)) and (nb >= 40)
            rows.append(dict(cond=c, bucket=b, n=nb, mean_b=mb, t_rest=tr, ratio_rest=rr, improve=rr - bratio, ok_a=bool(ok_a), ok_b=bool(ok_b),
                             eligible=bool(ok_a and ok_b and rr > bratio)))
    R = pd.DataFrame(rows); el = R[R.eligible].sort_values('improve', ascending=False)
    choice = None if el.empty else dict(cond=el.iloc[0].cond, exclude=el.iloc[0].bucket)
    return choice, R, dict(base=base, base_ratio=bratio, N=len(S))

def confirm_refinement(T, choice):
    V = T[(T.t_ent >= SEL_END) & (T.t_ent < L.POOL_END)]
    m = V[choice['cond']] == choice['exclude']
    rb = L.ratio_stats(V.netR)['ratio']; rf = L.ratio_stats(V.netR[~m])['ratio']
    mb = float(V.netR[m].mean()) if m.any() else np.nan; mr = float(V.netR[~m].mean())
    ok = bool((rf > rb) and (mb < mr))
    return ok, dict(N_val=len(V), ratio_base=rb, ratio_filtered=rf, mean_excl=mb, mean_rest=mr, n_excl=int(m.sum()))

def apply_refinement(T, choice):
    if choice is None: return T
    return T[T[choice['cond']] != choice['exclude']].reset_index(drop=True)

# ---------------- method 1 ----------------
def method1_trades(end=L.HOLD_END):
    t = pd.read_parquet(os.path.join(L.OUT, 'r6_trades_all.parquet'))
    t = t[t.gotobi & (t.DOW2a != 'month_end')].copy()
    t = t[t.t_ent < end]
    T = pd.DataFrame({'t_ent': t.t_ent.values, 't_exit': t.t_exit.values, 'gross': t.gross_pips.values, 'cost': 0.5, 'R': t.R_pips.values})
    T['net'] = T.gross - T.cost; T['netR'] = T.net / T.R; T['netR2'] = (T.gross - 1.0) / T.R; T['grossR'] = T.gross / T.R
    T['stopped'] = False
    return T.sort_values('t_ent').reset_index(drop=True)

def daily(T, col='netR'):
    return T.groupby(pd.to_datetime(T.t_exit).dt.normalize())[col].sum()

def daily_corr(Ta, Tb, end=L.POOL_END):
    a = daily(Ta[Ta.t_exit < end]); b = daily(Tb[Tb.t_exit < end])
    days = pd.bdate_range('2005-01-01', end - pd.Timedelta('1D'))
    x = a.reindex(days, fill_value=0.0); y = b.reindex(days, fill_value=0.0)
    return float(np.corrcoef(x.values, y.values)[0, 1])

def full_stats(T):
    r = T.netR.values; s = L.tstats(r); q = L.ratio_stats(r)
    yrs = max((pd.Timestamp(T.t_ent.max()) - pd.Timestamp(T.t_ent.min())).days / 365.25, 1e-9) if len(T) else np.nan
    return dict(N=len(T), mean_R=s['mean'], t=s['t'], mean_pips=float(T.net.mean()) if len(T) else np.nan,
                gross_R=float(T.grossR.mean()) if len(T) else np.nan, mean_R_2x=float(T.netR2.mean()) if len(T) else np.nan,
                win=float((T.netR > 0).mean()) if len(T) else np.nan, sum=q['sum'], maxDD=q['maxDD'], ratio=q['ratio'],
                flat_days=float(L.longest_flat_days(T.t_ent, r)) if len(T) else np.nan, per_year=len(T) / yrs if len(T) else 0)
