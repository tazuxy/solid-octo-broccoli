"""Round 10: screen (2005-2021 only) and final check (2022-2024, once) for pre-registered hypotheses.
  python3 -I code/r10_eval.py screen   -> out/r10_screen.csv (never reads trades with entry >= 2022-01-01)
  python3 -I code/r10_eval.py final    -> out/r10_final.csv, only for hypotheses with pass=True in out/r10_screen.csv; refuses to run twice.
Cost: 0.5 pips round trip (x1, x1.5, x2). t_used = min(trade t, t of daily sums). Blocks 2005-08, 09-12, 13-16, 17-21."""
import os, sys, numpy as np, pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, 'out')
COST = 0.5; CUT = pd.Timestamp('2022-01-01')
B4 = [(2005, 2008), (2009, 2012), (2013, 2016), (2017, 2021)]
def tstat(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    return x.mean() / (x.std(ddof=1) / np.sqrt(len(x))) if len(x) > 2 and x.std() > 0 else np.nan
def maxdd(r):
    cs = np.cumsum(r); return float((cs - np.maximum.accumulate(np.maximum(cs, 0))).min()) if len(r) else 0.0
def prep(T, mult=1.0):
    T = T.sort_values('t_ent').copy()
    c = T.cost_pips if 'cost_pips' in T else COST          # H6: real spread paid per trade
    T['net'] = T.gross_pips - mult * c; T['netR'] = T.net / T.R_pips; return T
def stats(T0):
    T = prep(T0); r = T.netR.values; y = T.t_ent.dt.year.values
    day = T.groupby(T.t_ent.dt.normalize()).netR.sum().values
    s = dict(N=len(T), days=len(day), gross_pips=T.gross_pips.mean(), net_pips=T.net.mean(), mean_R=r.mean(), t_trade=tstat(r), t_day=tstat(day))
    s['t_used'] = np.nanmin([s['t_trade'], s['t_day']])
    blk = []
    for a, b in B4:
        m = (y >= a) & (y <= b)
        blk.append((r[m].mean(), tstat(r[m])) if m.sum() >= 5 else (np.nan, np.nan))
    s['blocks'] = ' / '.join(f'{m:+.3f}({t:+.1f})' for m, t in blk)
    s['nblk_pos'] = sum(1 for m, _ in blk if np.isfinite(m) and m > 0); s['nblk'] = sum(1 for m, _ in blk if np.isfinite(m))
    s['blk_t_le_m2'] = any(np.isfinite(t) and t <= -2 for _, t in blk)
    s['x15_R'] = prep(T0, 1.5).netR.mean(); s['x2_R'] = prep(T0, 2.0).netR.mean(); s['x2_pips'] = prep(T0, 2.0).net.mean()
    rs = np.sort(r)[::-1]; s['drop5_R'] = rs[int(np.ceil(0.05 * len(rs))):].mean(); s['drop1_R'] = rs[int(np.ceil(0.01 * len(rs))):].mean()
    dd = maxdd(day); s['sum_R'] = r.sum(); s['maxDD_R'] = dd; s['sum_over_dd'] = r.sum() / abs(dd) if dd < 0 else np.inf
    per = T.groupby('inst').netR.mean(); s['pairs_pos'] = f'{int((per > 0).sum())}/{len(per)}'
    s['breakeven_cost_pips'] = T.gross_pips.mean()
    return s
TMIN = float(os.environ.get('TMIN', '2.5'))   # round 12 re-test uses 3.0
def screen_ok(s):
    return bool(s['mean_R'] > 0 and s['t_used'] >= TMIN and s['nblk_pos'] >= 2 and not s['blk_t_le_m2'] and s['x15_R'] > 0)

if __name__ == '__main__':
    mode = sys.argv[1]; tag = sys.argv[2] if len(sys.argv) > 2 else ''   # tag 'h6' -> r10_h6_trades.parquet, r10_screen_h6.csv
    A = pd.read_parquet(os.path.join(OUT, f'r10_{tag}_trades.parquet' if tag else 'r10_trades.parquet'))
    SCR = os.path.join(OUT, f'r10_screen_{tag}.csv' if tag else 'r10_screen.csv'); FIN = os.path.join(OUT, f'r10_final_{tag}.csv' if tag else 'r10_final.csv')
    if mode == 'screen':
        A = A[A.t_ent < CUT]; assert A.t_ent.max() < CUT
        rows = []
        for h, g in A.groupby('hyp'):
            s = stats(g[g.delay == 0]); s['pass'] = screen_ok(s)
            s['delay1_R'] = stats(g[g.delay == 1])['mean_R'] if (g.delay == 1).any() else np.nan
            if 'cost_pips' in g: s['mid_minus_0.5_R'] = ((g[g.delay == 0].gross_pips - COST) / g[g.delay == 0].R_pips).mean(); s['median_cost_pips'] = g[g.delay == 0].cost_pips.median()
            rows.append(dict(hyp=h, **s))
        S = pd.DataFrame(rows); S.to_csv(SCR, index=False)
        pd.set_option('display.width', 250); print(S.round(3).T.to_string())
    elif mode == 'final':
        fl = FIN; assert not os.path.exists(fl), 'final check already run once'
        S = pd.read_csv(SCR); hs = list(S[S['pass']].hyp)
        rows = []
        for h in hs:
            g = A[(A.hyp == h) & (A.delay == 0)]
            ho = g[g.t_ent >= CUT]; sh = stats(ho); sa = stats(g)
            rows.append(dict(hyp=h, N_2224=sh['N'], net_pips_2224=sh['net_pips'], mean_R_2224=sh['mean_R'], t_2224=sh['t_used'],
                             x2_R_2224=sh['x2_R'], N_all=sa['N'], mean_R_all=sa['mean_R'], t_all=sa['t_used'], sum_over_dd_all=sa['sum_over_dd'],
                             drop5_all=sa['drop5_R'], adopt=bool(sh['mean_R'] > 0 and sa['t_used'] >= 3.0)))
        F = pd.DataFrame(rows, columns=['hyp', 'N_2224', 'net_pips_2224', 'mean_R_2224', 't_2224', 'x2_R_2224', 'N_all', 'mean_R_all', 't_all',
                                        'sum_over_dd_all', 'drop5_all', 'adopt'])
        F.to_csv(fl, index=False); print(F.round(3).T.to_string())
