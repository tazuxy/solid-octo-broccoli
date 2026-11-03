"""Apply the pre-registered round-1 criteria to all variants and write r1_criteria.csv / r1_yearly.csv / r1_contrib.csv."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_common import *
rd = lambda f: pd.read_parquet(os.path.join(OUT, f))

def pooled(d, c):
    """equal-risk pool of two group series, each scaled to 8% ex post (scale only; t-stat of each unaffected)."""
    j = pd.concat([scale_to(d), scale_to(c)], axis=1).fillna(0.0); return j.mean(axis=1)

VARS = {
 'H1a 12w currency momentum': ('h1', 'h1a'), 'H1b 1w currency reversal': ('h1', 'h1b'),
 'H2a TSMOM 18 instruments': ('h2', 'h2a'), 'H2b TSMOM ex JPY-crosses & XAU': ('h2', 'h2b'),
 'H3a intraday both halves': ('h3', 'h3a'), 'H3b-W western-ccy half': ('h3', 'h3bW'), 'H3b-E eastern-ccy half': ('h3', 'h3bE'),
}
def series(kind, tag, cm):
    if kind == 'h1':
        D = rd(f'r1_{tag}_D_c{cm}.parquet'); C = rd(f'r1_{tag}_C_c{cm}.parquet')
        return D, C, None
    if kind == 'h2':
        return rd(f'r1_{tag}_D_c{cm}.parquet'), rd(f'r1_{tag}_C_c{cm}.parquet'), rd(f'r1_{tag}_ALL_c{cm}.parquet')
    return rd(f'r1_{tag}_D_c{cm}.parquet'), rd(f'r1_{tag}_C_c{cm}.parquet'), None

rows = []; yearly_rows = {}; contrib_rows = []
for name, (kind, tag) in VARS.items():
    D, C, A = series(kind, tag, 1.0)
    P = A.net if A is not None else pooled(D.net, C.net)
    cl = cells(scale_to(D.net), scale_to(C.net))   # each group scaled to 8% ex post
    t = tstat(P); sh = sharpe(P)
    k8 = 0.08 / (P.std() * np.sqrt(52))
    cm8 = curve_metrics(P * k8)
    # N
    if kind == 'h3':
        N = int(D.ntrades.sum() + C.ntrades.sum())   # number of pair-window trades
    else:
        N = len(P)
    # contributions
    if kind == 'h1':
        con = pd.concat([D.filter(like='c_').sum().rename(lambda s: 'D:' + s[2:]), C.filter(like='c_').sum().rename(lambda s: 'C:' + s[2:])])
    elif kind == 'h2':
        con = A.filter(like='p_').sum().rename(lambda s: s[2:])
    else:
        con = pd.concat([D.filter(like='p_').sum(), C.filter(like='p_').sum()]).rename(lambda s: s[2:])
    frac_pos = (con > 0).mean()
    for k_, v in con.items(): contrib_rows.append(dict(variant=name, unit=k_, net_contrib=v))
    # cost sensitivity (same leverage k8)
    cs = {}
    for cm in (1.5, 2.0):
        D2, C2, A2 = series(kind, tag, cm)
        if A2 is not None: P2 = A2.net
        else:
            sd, sc = 0.08 / (D.net.std() * np.sqrt(52)), 0.08 / (C.net.std() * np.sqrt(52))
            P2 = pd.concat([D2.net * sd, C2.net * sc], axis=1).fillna(0).mean(axis=1)
        cs[cm] = (ann_ret(P2 * k8), tstat(P2), cells(D2.net * 0.08 / (D.net.std() * np.sqrt(52)), C2.net * 0.08 / (C.net.std() * np.sqrt(52))))
    pass1 = all(v > 0 for v in cl.values()); pass2 = t >= 2.0; pass3 = cm8['ret_dd'] >= 3; pass4 = N >= 100; pass5 = frac_pos >= 0.6
    row = dict(variant=name, **{k: round(v * 100, 2) for k, v in cl.items()}, c1_4cells=pass1, t_weekly=round(t, 2), c2_t=pass2,
               ret_dd_8vol=round(cm8['ret_dd'], 2), c3=pass3, N=N, c4=pass4, contrib_pos=f'{(con > 0).sum()}/{len(con)}', c5=pass5,
               PASS=pass1 and pass2 and pass3 and pass4 and pass5,
               ann_ret_8vol=round(ann_ret(P * k8) * 100, 2), sharpe=round(sh, 2), maxdd_8vol=round(cm8['maxdd'] * 100, 1),
               flat_months=round(cm8['flat_m'], 1), cum_8vol=round(cm8['cum'] * 100, 1),
               ann_x15=round(cs[1.5][0] * 100, 2), t_x15=round(cs[1.5][1], 2), ann_x2=round(cs[2.0][0] * 100, 2), t_x2=round(cs[2.0][1], 2), cells_x2=' / '.join(f'{v*100:.1f}' for v in cs[2.0][2].values()),
               gross_ann_D=round(ann_ret(D.gross) * 100, 2) if 'gross' in D else np.nan,
               gross_ann_C=round(ann_ret(C.gross) * 100, 2) if 'gross' in C else np.nan)
    if kind == 'h3':
        D0, C0, _ = series(kind, tag, 0.0)
        row['gross_ann_D'] = round(ann_ret(D0.net) * 100, 2); row['gross_ann_C'] = round(ann_ret(C0.net) * 100, 2)
        row['t_gross_pooled'] = round(tstat(pooled(D0.net, C0.net)), 2)
    if kind == 'h2':
        x = P[~((P.index >= '2015-01-15') & (P.index < '2015-01-22'))]
        row['t_ex_SNB_week'] = round(tstat(x), 2); row['ann_ex_SNB_8vol'] = round(ann_ret(x * k8) * 100, 2)
        row['SNB_week_ret_8vol'] = round(float((P * k8)[(P.index >= '2015-01-15') & (P.index < '2015-01-22')].sum()) * 100, 2)
        row['realised_vol_ALL'] = round(P.std() * np.sqrt(52) * 100, 1)
        row['t_D'] = round(tstat(D.net), 2); row['t_C'] = round(tstat(C.net), 2)
    else:
        row['t_D'] = round(tstat(D.net), 2); row['t_C'] = round(tstat(C.net), 2)
    rows.append(row)
    yearly_rows[name] = (yearly(P * k8) * 100).round(1)
crit = pd.DataFrame(rows)
crit.to_csv(os.path.join(OUT, 'r1_criteria.csv'), index=False)
pd.DataFrame(yearly_rows).to_csv(os.path.join(OUT, 'r1_yearly.csv'))
pd.DataFrame(contrib_rows).to_csv(os.path.join(OUT, 'r1_contrib.csv'), index=False)
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 50)
print(crit.T.to_string())
print(pd.DataFrame(yearly_rows).to_string())
cc = pd.DataFrame(contrib_rows); cc['net_contrib'] = (cc.net_contrib * 100).round(2)
for v, g in cc.groupby('variant', sort=False): print(v, dict(zip(g.unit, g.net_contrib)))
