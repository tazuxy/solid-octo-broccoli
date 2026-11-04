"""r9c pseudo-holdout check (no 2022+ data anywhere).
Re-make the confirmation decision of every round-7 (v2) / round-8 candidate using ONLY 2005-2016 (discovery window excluded),
under strict and relaxed criteria, then score the decision on 2017-2021 (discovery window excluded), which the new
decisions never used. Also: hypothesis-driven rules of rounds 0/4b/5 (trade files filtered to < 2022).
Outputs: out/r9c_pseudo_cands.csv, out/r9c_pseudo_hyp.csv, out/r9c_pseudo.log
Run: python3 -I r9c_pseudo.py"""
import os, sys, numpy as np, pandas as pd
from math import erf, sqrt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, 'out')
CUT = pd.Timestamp('2022-01-01'); SPLIT = 2017
LOG = None
def P(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True)
    if LOG is not None: LOG.write(s + '\n'); LOG.flush()

def tstat(x):
    x = np.asarray(x, float)
    return x.mean() / (x.std(ddof=1) / np.sqrt(len(x))) if len(x) > 2 and x.std() > 0 else np.nan

def maxdd(r):
    c = np.cumsum(r); pk = np.maximum.accumulate(np.concatenate([[0.0], c]))[1:]
    return float((c - pk).min()) if len(c) else 0.0

def pval(t): return 0.5 * (1 - erf(t / sqrt(2))) if np.isfinite(t) else 1.0

BLK_S = [(2005, 2007), (2008, 2010), (2011, 2013), (2014, 2016)]
ROLL = (16, 17, 18)

def hour_ok(T):
    """round-8 rollover-hour check (data validity gate)."""
    if len(T) < 3: return False
    eh = T.t_ent.dt.hour.values; xh = T.t_exit.dt.hour.values; r = T.netR.values; tot = r.sum()
    if tot > 0:
        pe = pd.Series(r).groupby(eh).sum(); px = pd.Series(r).groupby(xh).sum()
        share = max(max(pe.get(h, 0.0), px.get(h, 0.0)) / tot for h in ROLL)
        if share >= 0.5: return False
    adj = np.isin(eh, ROLL) | np.isin(xh, ROLL); ex = r[~adj]
    return len(ex) >= 30 and ex.mean() > 0

def stats(T, pooled, blocks=BLK_S, rollcheck=True):
    s = dict(N=len(T))
    if len(T) < 10:
        return dict(N=len(T), mean_R=np.nan, mean_pips=np.nan, t=np.nan, t_used=np.nan, nblk=0, nblkn=0, x2=np.nan, x15=np.nan,
                    pairs=np.nan, roll=False, ratio=np.nan)
    r = T.netR.values; s['mean_R'] = r.mean(); s['mean_pips'] = T.net.mean(); s['t'] = tstat(r)
    dsum = T.groupby(T.t_ent.dt.normalize()).netR.sum().values; s['t_day'] = tstat(dsum)
    s['t_used'] = np.nanmin([s['t'], s['t_day']])
    y = T.t_ent.dt.year.values; nb = 0; nbn = 0
    for a, b in blocks:
        m = (y >= a) & (y <= b)
        if m.sum() >= 5: nbn += 1; nb += int(r[m].mean() > 0)
    s['nblk'] = nb; s['nblkn'] = nbn
    s['x2'] = T.netR2.mean(); s['x15'] = (0.5 * (T.netR + T.netR2)).mean()
    if pooled:
        per = T.groupby('inst').netR.agg(['mean', 'size']); per = per[per['size'] >= 20]
        s['pairs'] = float((per['mean'] > 0).mean()) if len(per) else 0.0
    else: s['pairs'] = np.nan
    s['roll'] = hour_ok(T) if rollcheck else True
    dd = maxdd(r); s['ratio'] = r.sum() / abs(dd) if dd < 0 else np.inf
    return s

def decide(s, pooled, tmin, blk_need, cost='x2', pairs_min=0.6):
    if not np.isfinite(s.get('t_used', np.nan)): return False
    ok = s['mean_R'] > 0 and s['mean_pips'] > 0 and s['t_used'] >= tmin and s['nblk'] >= min(blk_need, s['nblkn']) and s['roll']
    if cost == 'x2': ok = ok and s['x2'] > 0
    if cost == 'x1.5': ok = ok and s['x15'] > 0
    if pooled: ok = ok and s['pairs'] >= pairs_min
    return bool(ok)

RULES = {'strict (t>=3.4, 3/4 blk, x2, 60% pairs)': (3.4, 3, 'x2'),
         'relaxed t>=2.5 (2/4 blk, x1)': (2.5, 2, 'x1'),
         'relaxed t>=2.0 (2/4 blk, x1)': (2.0, 2, 'x1'),
         'proposal screen t>=2.5 (2/4 blk, x1.5)': (2.5, 2, 'x1.5')}

def loop_part():
    C = pd.read_csv(os.path.join(OUT, 'r9c_cands.csv')); T = pd.read_parquet(os.path.join(OUT, 'r9c_cand_trades.parquet'))
    assert T.t_ent.max() < CUT and T.t_exit.max() <= CUT
    T = T[~T.inwin]; rows = []
    for cid, g in T.groupby('cid'):
        c = C.loc[C.cid == cid].iloc[0]; pooled = bool(c.pooled)
        g = g.sort_values('t_ent')
        S = g[g.t_ent.dt.year < SPLIT]; H = g[g.t_ent.dt.year >= SPLIT]
        ss = stats(S, pooled); hs = stats(H, pooled, blocks=[(2017, 2021)], rollcheck=False)
        r = dict(cid=cid, round=c['round'], window=c.window, cand=c.cand, family=c.family, out=c.out, pooled=pooled,
                 orig_t_used=c.orig_t_used, orig_verdict=c.orig_verdict)
        r.update({f'S_{k}': v for k, v in ss.items()}); r.update({f'H_{k}': v for k, v in hs.items()})
        for nm, (tm, bn, co) in RULES.items(): r[nm] = decide(ss, pooled, tm, bn, co)
        r['S_p'] = pval(ss['t_used']) if np.isfinite(ss.get('t_used', np.nan)) else 1.0
        rows.append(r)
    R = pd.DataFrame(rows)
    # BH-FDR on the 2005-16 one-sided p of all 400 candidates (+ other gates)
    m = len(R); p = R.S_p.values; o = np.argsort(p); thr = 0.10 * np.arange(1, m + 1) / m
    k = np.nonzero(p[o] <= thr)[0]; cut = p[o][k.max()] if len(k) else -1
    R['BH q=0.10 (2005-16)'] = (R.S_p <= cut)
    R['BH q=0.10 + gates'] = R['BH q=0.10 (2005-16)'] & R['relaxed t>=2.0 (2/4 blk, x1)']
    R.to_csv(os.path.join(OUT, 'r9c_pseudo_cands.csv'), index=False)
    P(f"loop candidates: {m}; BH(q=0.10) p cut {cut:.4g} -> {int(R['BH q=0.10 (2005-16)'].sum())} rejections")
    P('Spearman(S t_used, H t_used) =', round(R[['S_t_used', 'H_t_used']].corr('spearman').iloc[0, 1], 3),
      '| Pearson =', round(R[['S_t_used', 'H_t_used']].corr().iloc[0, 1], 3))
    P('S t_used: median', round(R.S_t_used.median(), 2), ' share >0', round((R.S_t_used > 0).mean(), 3), ' >2', int((R.S_t_used > 2).sum()),
      ' >2.5', int((R.S_t_used > 2.5).sum()), ' >3.4', int((R.S_t_used >= 3.4).sum()))
    # Storey pi0 from 2005-16 p values
    for lam in (0.5, 0.7):
        P(f'Storey pi0 (lambda {lam}) = {min(1, (R.S_p > lam).mean() / (1 - lam)):.2f}')
    return R

def summarize(R, label):
    grp = {}
    s = R['strict (t>=3.4, 3/4 blk, x2, 60% pairs)']; r25 = R['relaxed t>=2.5 (2/4 blk, x1)']; r20 = R['relaxed t>=2.0 (2/4 blk, x1)']
    grp['strict pass'] = s
    grp['relaxed t>=2.5 only (not strict)'] = r25 & ~s
    grp['relaxed t>=2.0 only (not t>=2.5)'] = r20 & ~r25 & ~s
    grp['rejected by all'] = ~r20 & ~s & ~r25
    grp['proposal screen (t>=2.5, x1.5)'] = R['proposal screen t>=2.5 (2/4 blk, x1.5)']
    if 'BH q=0.10 + gates' in R: grp['BH q=0.10 + gates'] = R['BH q=0.10 + gates']
    grp['all'] = pd.Series(True, index=R.index)
    rows = []
    for k, m in grp.items():
        x = R[m]
        rows.append(dict(set=label, group=k, n=int(m.sum()), S_t_med=x.S_t_used.median(), S_meanR_med=x.S_mean_R.median(),
                         H_N_med=x.H_N.median(), H_meanR_avg=x.H_mean_R.mean(), H_meanR_med=x.H_mean_R.median(),
                         H_pos=(x.H_mean_R > 0).mean(), H_t_med=x.H_t_used.median(), H_t_ge2=(x.H_t_used >= 2).mean(),
                         H_x2_pos=(x.H_x2 > 0).mean()))
    return pd.DataFrame(rows)

# ---------------- hypothesis-driven rules (rounds 0, 4b, 5) ----------------
def hyp_rules():
    out = []
    # round 5
    for f in ('r5_h1_trades.parquet', 'r5_h2_trades.parquet', 'r5_h345_trades.parquet'):
        x = pd.read_parquet(os.path.join(OUT, f)); x = x[(x['mode'] == 'base') & (x.t_ent < CUT)]
        for v, g in x.groupby('var'):
            T = pd.DataFrame({'inst': g.inst.values, 't_ent': g.t_ent.values, 't_exit': g.t_ent.values,
                              'net': (g.gross_pips - g.cost_pips).values, 'netR': ((g.gross_pips - g.cost_pips) / g.R_pips).values,
                              'netR2': ((g.gross_pips - 2 * g.cost_pips) / g.R_pips).values})
            out.append(('r5 ' + v, T, g.inst.nunique() > 1))
    # round 4b S2 / Gotobi-eve variants (USDJPY, 0.5 pip)
    x = pd.read_parquet(os.path.join(OUT, 'r4b_s2_trades.parquet')); x = x[(x.pair == 'USDJPY') & (x.t_ent < CUT)]
    for v, g in x.groupby('var'):
        for nm, gg in ((v + ' (Gotobi only)', g[g.gotobi]), (v + ' (all days)', g)):
            if v.startswith('seg') or v.endswith('pre'): continue
            T = pd.DataFrame({'inst': 'USDJPY', 't_ent': gg.t_ent.values, 't_exit': gg.t_ent.values, 'net': (gg.gross_pips - 0.5).values,
                              'netR': ((gg.gross_pips - 0.5) / gg.R_pips).values, 'netR2': ((gg.gross_pips - 1.0) / gg.R_pips).values})
            out.append(('r4b ' + nm, T, False))
    # round 0 families (2012-2021 only)
    x = pd.read_parquet(os.path.join(OUT, 'fam_trades.parquet')); x = x[x.entry_t < CUT]
    for v, g in x.groupby('strat'):
        T = pd.DataFrame({'inst': g.pair.values, 't_ent': g.entry_t.values, 't_exit': g.exit_t.values, 'net': g.r.values,
                          'netR': g.r.values, 'netR2': (g.r - g.cost_r).values})
        out.append(('r0 ' + v, T, True))
    return out

def hyp_part():
    out = hyp_rules()
    rows = []
    for nm, T, pooled in out:
        T = T.sort_values('t_ent'); T['t_ent'] = pd.to_datetime(T.t_ent); T['t_exit'] = pd.to_datetime(T.t_exit)
        assert T.t_ent.max() < CUT
        r0 = nm.startswith('r0')
        blk = [(2012, 2013), (2014, 2014), (2015, 2015), (2016, 2016)] if r0 else BLK_S
        S = T[T.t_ent.dt.year < SPLIT]; H = T[T.t_ent.dt.year >= SPLIT]
        ss = stats(S, pooled, blocks=blk, rollcheck=False); hs = stats(H, pooled, blocks=[(2017, 2021)], rollcheck=False)
        r = dict(rule=nm, pooled=pooled, S_years='2012-16' if r0 else '2005-16')
        r.update({f'S_{k}': v for k, v in ss.items()}); r.update({f'H_{k}': v for k, v in hs.items()})
        for k, (tm, bn, co) in RULES.items(): r[k] = decide(ss, pooled, tm, bn, co)
        rows.append(r)
    R = pd.DataFrame(rows); R.to_csv(os.path.join(OUT, 'r9c_pseudo_hyp.csv'), index=False)
    return R

def main():
    global LOG
    LOG = open(os.path.join(OUT, 'r9c_pseudo.log'), 'w')
    R = loop_part(); A = summarize(R, 'loop r7v2+r8 (400)')
    for rnd in (7, 8): A = pd.concat([A, summarize(R[R['round'] == rnd], f'loop r{rnd}')])
    H = hyp_part(); B = summarize(H, 'hypothesis rules r0/r4b/r5')
    S = pd.concat([A, B]); S.to_csv(os.path.join(OUT, 'r9c_pseudo_summary.csv'), index=False)
    pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
    P(S.round(3).to_string(index=False))
    cols = ['cand', 'round', 'window', 'S_N', 'S_mean_R', 'S_t_used', 'S_nblk', 'S_x2', 'S_pairs', 'S_roll', 'H_N', 'H_mean_R', 'H_t_used', 'orig_t_used', 'orig_verdict']
    P('\nloop candidates passing any relaxed rule (2005-16):')
    P(R[R['relaxed t>=2.0 (2/4 blk, x1)'] | R['strict (t>=3.4, 3/4 blk, x2, 60% pairs)']][cols].round(3).to_string(index=False))
    P('\nhypothesis rules passing any relaxed rule (2005-16):')
    hc = ['rule', 'S_years', 'S_N', 'S_mean_R', 'S_t_used', 'S_nblk', 'S_x2', 'S_pairs', 'H_N', 'H_mean_R', 'H_t_used'] + list(RULES)
    P(H[H['relaxed t>=2.0 (2/4 blk, x1)']][hc].round(3).to_string(index=False))

if __name__ == '__main__':
    main()
