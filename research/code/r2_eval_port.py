"""Round 2: pre-registered evaluation of P1 (12w xs reversal), P2 (1w xs reversal), P3 (50/50) with Monday-08:00 execution.
Scoring windows (fixed before results): early = 2005-07..2011-12 (week end t < 2012-01-01), combined = 2005-07..2024-12.
Warm-up: a week is scored only if every pair the implementation needs is past its first 6 months of data
  (D: 7 USD pairs -> NZDUSD 2005-08-12 + 6m;  C: EURJPY GBPJPY AUDJPY CADJPY NZDJPY EURCHF -> CADJPY 2007-03-18 + 6m).
P3: each leg scaled ex ante to 8%/yr with its trailing 52-week realised vol (min 13 weeks, lagged one week), then 0.5/0.5.
D+C pooling at equal vol = round-1 pooled() (ex-post scaling over the evaluated window; costs x1.5 use the x1.0 scale).
Criteria: (a) ann net > 0 in D and C (early); (b) t(pooled early) >= 1.5; (c) combined pooled t >= 2.0 and cum/maxDD >= 3 at 8% vol;
(d) >= 60% of the 15 currency units (D 8 + C 7) with positive net contribution in early; (e) (a)-(c) still hold at costs x1.5."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_common import *
def pooled(d, c):   # = r1_eval.pooled (copied: importing r1_eval would re-run its script body)
    j = pd.concat([scale_to(d), scale_to(c)], axis=1).fillna(0.0); return j.mean(axis=1)
rd = lambda f: pd.read_parquet(os.path.join(OUT, f))
first = {p: pd.read_parquet(os.path.join(ROOT, 'bars_full', f'{p}_D1.parquet')).index.min() for p in ALL}
NEED = {'D': ['EURUSD','GBPUSD','USDJPY','AUDUSD','USDCAD','USDCHF','NZDUSD'], 'C': ['EURJPY','GBPJPY','AUDJPY','CADJPY','NZDJPY','EURCHF']}
START = {g: max(pd.Timestamp('2005-07-01'), max(first[p] for p in ps) + pd.DateOffset(months=6)) for g, ps in NEED.items()}
E_END = pd.Timestamp('2012-01-01')
TAU = 0.08 / np.sqrt(52)

def leg(tag, var, impl, cm):
    return rd(f'r2_xs_{tag}_{var}_{impl}_c{cm}.parquet')

def p3(tag, impl, cm):
    a, b = leg(tag, 'arev', impl, cm), leg(tag, 'b', impl, cm)
    a1, b1 = leg(tag, 'arev', impl, 1.0), leg(tag, 'b', impl, 1.0)          # vol estimates always from the x1.0 legs
    sa = a1.net.rolling(52, min_periods=13).std().shift(1); sb = b1.net.rolling(52, min_periods=13).std().shift(1)
    j = a.index.intersection(b.index).intersection(sa.dropna().index).intersection(sb.dropna().index)
    wa, wb = 0.5 * TAU / sa.loc[j], 0.5 * TAU / sb.loc[j]
    cols = ['gross', 'cost', 'net'] + [c for c in a.columns if c.startswith('c_')]
    out = a.loc[j, cols].mul(wa, axis=0) + b.loc[j, cols].mul(wb, axis=0)
    out['dec'] = a.loc[j, 'dec']; out['turnover'] = a.loc[j, 'turnover'] * wa + b.loc[j, 'turnover'] * wb
    return out

def series(cand, tag, impl, cm):
    if cand == 'P1': return leg(tag, 'arev', impl, cm)
    if cand == 'P2': return leg(tag, 'b', impl, cm)
    return p3(tag, impl, cm)

def window(w, impl, which):
    w = w[w.dec >= START[impl]]
    if which == 'early': return w[w.index < E_END]
    if which == 'late': return w[w.index >= E_END]
    return w

def pooled_k(d, c, d0=None, c0=None):
    """pooled at equal vol; scale factors from (d0, c0) when given (cost-sensitivity runs)."""
    d0 = d if d0 is None else d0; c0 = c if c0 is None else c0
    sd, sc = 0.08 / (d0.std() * np.sqrt(52)), 0.08 / (c0.std() * np.sqrt(52))
    return pd.concat([d * sd, c * sc], axis=1).fillna(0.0).mean(axis=1)

def longest_flat(r):
    return curve_metrics(r)['flat_m']

def evaluate(cand, tag='full_mon'):
    res = {}
    W = {(impl, cm): series(cand, tag, impl, cm) for impl in ('D', 'C') for cm in (1.0, 1.5, 2.0)}
    for cm in (1.0, 1.5, 2.0):
        e = {impl: window(W[(impl, cm)], impl, 'early') for impl in ('D', 'C')}
        a = {impl: window(W[(impl, cm)], impl, 'all') for impl in ('D', 'C')}
        e0 = {impl: window(W[(impl, 1.0)], impl, 'early').net for impl in ('D', 'C')}
        a0 = {impl: window(W[(impl, 1.0)], impl, 'all').net for impl in ('D', 'C')}
        Pe = pooled_k(e['D'].net, e['C'].net, e0['D'], e0['C'])
        Pa = pooled_k(a['D'].net, a['C'].net, a0['D'], a0['C'])
        Pa0 = pooled_k(a0['D'], a0['C']); k8 = 0.08 / (Pa0.std() * np.sqrt(52))
        cmA = curve_metrics(Pa * k8)
        Pe0 = pooled_k(e0['D'], e0['C']); ke = 0.08 / (Pe0.std() * np.sqrt(52)); cmE = curve_metrics(Pe * ke)
        r = dict(cand=cand, cost=cm,
                 D_start=str(e['D'].index.min().date()), C_start=str(e['C'].index.min().date()), N_early_D=len(e['D']), N_early_C=len(e['C']),
                 ann_early_D=ann_ret(e['D'].net * 0.08 / (e0['D'].std() * np.sqrt(52))), ann_early_C=ann_ret(e['C'].net * 0.08 / (e0['C'].std() * np.sqrt(52))),
                 ann_early_D_raw=ann_ret(e['D'].net), ann_early_C_raw=ann_ret(e['C'].net),
                 t_early_D=tstat(e['D'].net), t_early_C=tstat(e['C'].net), t_early_pooled=tstat(Pe),
                 ann_early_pooled_8=ann_ret(Pe * ke), maxdd_early_8=cmE['maxdd'],
                 t_all=tstat(Pa), ann_all_8=ann_ret(Pa * k8), cum_all_8=cmA['cum'], maxdd_all_8=cmA['maxdd'], ret_dd_all_8=cmA['ret_dd'],
                 flat_all_m=cmA['flat_m'], sharpe_all=sharpe(Pa), N_all=len(Pa))
        if cm == 1.0:
            con = pd.concat([e['D'].filter(like='c_').sum().rename(lambda s: 'D:' + s[2:]), e['C'].filter(like='c_').sum().rename(lambda s: 'C:' + s[2:])])
            r['contrib_pos'] = int((con > 0).sum()); r['contrib_n'] = len(con); r['contrib'] = '; '.join(f'{k} {v*100:+.1f}' for k, v in con.items())
            r['gross_early_D'] = ann_ret(e['D'].gross); r['gross_early_C'] = ann_ret(e['C'].gross)
            r['turnover_D'] = e['D'].turnover.mean(); r['turnover_C'] = e['C'].turnover.mean()
            res['yearly'] = (yearly(Pa * k8) * 100).round(1); res['P'] = Pa * k8
        res[cm] = r
    c1, c15 = res[1.0], res[1.5]
    def abc(r):
        return (r['ann_early_D'] > 0 and r['ann_early_C'] > 0), (r['t_early_pooled'] >= 1.5), (r['t_all'] >= 2.0 and r['ret_dd_all_8'] >= 3)
    a_, b_, c_ = abc(c1); d_ = c1['contrib_pos'] / c1['contrib_n'] >= 0.6; e_ = all(abc(c15))
    res['pass'] = dict(a=a_, b=b_, c=c_, d=d_, e=e_, PASS=a_ and b_ and c_ and d_ and e_)
    return res

def late_compare():
    """2012-2024: round-1 execution (bars, Sunday 17:00) vs new execution (bars, Monday 08:00), round-1 style metrics."""
    rows = []
    for cand in ('P1', 'P2', 'P3'):
        for tag, lab in (('bars_d1', 'Sun 17:00 (round 1)'), ('bars_mon', 'Mon 08:00 (round 2)')):
            if True:
                d, c = series(cand, tag, 'D', 1.0).net, series(cand, tag, 'C', 1.0).net
            P = pooled(d, c); k8 = 0.08 / (P.std() * np.sqrt(52)); cmx = curve_metrics(P * k8)
            cl = cells(scale_to(d), scale_to(c))
            rows.append(dict(cand=cand, execution=lab, **{k: round(v * 100, 2) for k, v in cl.items()}, t=round(tstat(P), 2),
                             t_D=round(tstat(d), 2), t_C=round(tstat(c), 2), ann_8=round(ann_ret(P * k8) * 100, 2),
                             maxdd_8=round(cmx['maxdd'] * 100, 1), ret_dd=round(cmx['ret_dd'], 2), flat_m=round(cmx['flat_m'], 1)))
    return pd.DataFrame(rows)

if __name__ == '__main__':
    pd.set_option('display.width', 250); pd.set_option('display.max_columns', 60); pd.set_option('display.max_colwidth', 200)
    print('score start', {k: str(v.date()) for k, v in START.items()})
    rows = []; yr = {}; passes = {}; curves = {}
    for cand in ('P1', 'P2', 'P3'):
        r = evaluate(cand)
        for cm in (1.0, 1.5, 2.0): rows.append(r[cm])
        yr[cand] = r['yearly']; passes[cand] = r['pass']; curves[cand] = r['P']
    t = pd.DataFrame(rows); t.to_csv(os.path.join(OUT, 'r2_port_criteria.csv'), index=False)
    print(t.T.to_string())
    print(pd.DataFrame(passes).T.to_string())
    pd.DataFrame(passes).T.to_csv(os.path.join(OUT, 'r2_port_pass.csv'))
    y = pd.DataFrame(yr); y.to_csv(os.path.join(OUT, 'r2_port_yearly.csv')); print(y.to_string())
    pd.DataFrame(curves).to_parquet(os.path.join(OUT, 'r2_port_weekly_8vol.parquet'))
    lc = late_compare(); lc.to_csv(os.path.join(OUT, 'r2_port_2012_2024_exec.csv'), index=False); print(lc.to_string(index=False))
