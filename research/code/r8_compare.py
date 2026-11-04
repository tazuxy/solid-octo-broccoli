"""Round 8 final comparison of method 1 (r6) and the methods ACCEPTED in round 8 (r7_compare.py logic, round-8 files).
Risk per trade: equity fraction lost when the trade loses its stop distance (kR column: 1R for no-stop rules, k for kR stops,
per-trade bracket distance for intrinsic brackets). Outputs out/r8_compare.json, out/r8_compare.png."""
import os, sys, json, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r7_lib as L, r7_dev as D
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
L.STATE = os.path.join(L.OUT, 'r8_state.json')

st = L.load_state(); assert st['phase'] == 'done'
M = {1: dict(T=D.method1_trades(L.HOLD_END), inst='USDJPY', stop='none',
             rule='USDJPY long 22:00 JST on the business day before a Gotobi day -> 09:55 JST on the Gotobi day; skip month-end Gotobi',
             clean_holdout=False)}
for N in st['accepted']:
    fz = json.load(open(os.path.join(L.OUT, f'r8_method{N}_frozen.json')))
    T = pd.read_parquet(os.path.join(L.OUT, f'r8_method{N}_full_trades.parquet'))
    M[N] = dict(T=T, inst=fz['instrument'], stop=str(fz['stop']), clean_holdout=True,
                rule=fz['rule'] + (f"; refinement: skip {fz['refinement']}" if fz['refinement'] else ''))

def frac(T, risk):
    k = T['kR'].values.astype(float) if 'kR' in T else np.ones(len(T))
    k = np.where(np.isfinite(k) & (k > 0), k, 1.0); return risk / k

def equity(T, risk):
    T = T.sort_values('t_exit'); eq = np.cumprod(1 + frac(T, risk) * T.netR.values)
    return pd.Series(eq, index=pd.to_datetime(T.t_exit.values))

def cagr_dd(eq, t0, t1):
    yrs = (t1 - t0).days / 365.25; c = eq.iloc[-1] ** (1 / yrs) - 1
    dd = float((eq / np.maximum.accumulate(np.concatenate([[1.0], eq.values]))[1:] - 1).min())
    return c, dd

def flat_days(eq):
    v = np.concatenate([[1.0], eq.values]); t = np.concatenate([[eq.index[0]], eq.index.values]); hi = v[0]; lt = t[0]; best = 0
    for ti, vi in zip(t, v):
        if vi > hi: best = max(best, (ti - lt) / np.timedelta64(1, 'D')); hi = vi; lt = ti
    return max(best, (t[-1] - lt) / np.timedelta64(1, 'D'))

def mc_dd(rets, n=10000, seed=7):
    rng = np.random.default_rng(seed); r = np.asarray(rets); out = np.empty(n)
    for i in range(n):
        x = np.cumprod(1 + rng.choice(r, len(r), replace=True)); pk = np.maximum.accumulate(np.concatenate([[1.0], x]))[1:]
        out[i] = (x / pk - 1).min()
    return float(np.percentile(out, 5))

t0, t1 = pd.Timestamp('2005-01-01'), pd.Timestamp('2025-01-01'); rows = []; curves = {}
for N, m in M.items():
    T = m['T'].sort_values('t_ent').reset_index(drop=True); fs = D.full_stats(T)
    H = T[T.t_ent >= L.POOL_END]; hs = D.full_stats(H); P = T[T.t_ent < L.POOL_END]; ps = D.full_stats(P)
    r = dict(method=N, rule=m['rule'], inst=m['inst'], stop=m['stop'], N=fs['N'], per_year=fs['per_year'],
             mean_pips=fs['mean_pips'], mean_R=fs['mean_R'], win=fs['win'], t=fs['t'], maxDD_R=fs['maxDD'], ratio=fs['ratio'],
             flat_days=fs['flat_days'], mean_R_2x=fs['mean_R_2x'], t_2x=L.tstats(T.netR2)['t'], pool_mean_R=ps['mean_R'], pool_t=ps['t'],
             hold_N=hs['N'], hold_mean_R=hs['mean_R'], hold_mean_pips=hs['mean_pips'], hold_t=hs['t'], hold_sum=hs['sum'],
             clean_holdout=m['clean_holdout'])
    for risk in (0.0025, 0.005):
        eq = equity(T, risk); c, dd = cagr_dd(eq, t0, t1)
        r[f'cagr_{risk}'] = c; r[f'dd_{risk}'] = dd; r[f'cagr_dd_{risk}'] = c / abs(dd) if dd < 0 else np.inf
        r[f'flat_{risk}'] = flat_days(eq); r[f'mcdd_{risk}'] = mc_dd(frac(T, risk) * T.netR.values)
        if risk == 0.005: curves[N] = eq
    rows.append(r)
C = pd.DataFrame(rows)
mon = pd.DataFrame({N: m['T'].groupby(pd.to_datetime(m['T'].t_exit).dt.to_period('M')).netR.sum() for N, m in M.items()}).fillna(0.0)
mon = mon.reindex(pd.period_range('2005-01', '2024-12', freq='M'), fill_value=0.0)
corr = mon.corr()
port = {}
if len(M) > 1:
    for risk in (0.0025, 0.005):
        d = pd.concat([pd.Series(frac(m['T'], risk) * m['T'].netR.values, index=pd.to_datetime(m['T'].t_exit).dt.normalize().values).groupby(level=0).sum()
                       for m in M.values()], axis=1).fillna(0.0).sum(axis=1).sort_index()
        days = pd.bdate_range(t0, t1 - pd.Timedelta('1D')); d = d.reindex(days, fill_value=0.0)
        eq = pd.Series(np.cumprod(1 + d.values), index=days); c, dd = cagr_dd(eq, t0, t1)
        port[risk] = dict(cagr=c, maxDD=dd, cagr_dd=c / abs(dd), flat_days=flat_days(eq), mcdd95=mc_dd(d.values, n=2000),
                          hold_ret=float(eq[eq.index >= L.POOL_END].iloc[-1] / eq[eq.index < L.POOL_END].iloc[-1] - 1))
        if risk == 0.005: curves['combined'] = eq
json.dump(dict(table=C.to_dict(orient='records'), corr={str(k): {str(a): b for a, b in v.items()} for k, v in corr.round(3).to_dict().items()},
               portfolio={str(k): v for k, v in port.items()}), open(os.path.join(L.OUT, 'r8_compare.json'), 'w'), indent=1, default=float)
fig, ax = plt.subplots(figsize=(11, 5.5))
for N, eq in curves.items():
    ax.plot(eq.index, 100 * (eq.values - 1), label=f'method {N}' if N != 'combined' else 'combined (equal risk)', lw=1.6 if N == 'combined' else 1.1)
ax.axvspan(L.POOL_END, t1, color='grey', alpha=0.15, label='final holdout 2022-24')
ax.set_ylabel('equity change % (0.5% risk per trade, compounded, 0.5 pip cost)')
ax.set_title('Round 8: method comparison' + ('' if len(M) > 1 else ' (no new method accepted: method 1 only)'))
ax.grid(alpha=0.3); ax.legend(); fig.tight_layout(); fig.savefig(os.path.join(L.OUT, 'r8_compare.png'), dpi=120)
pd.set_option('display.width', 250); print(C.T.to_string()); print(corr.round(2)); print(port)
