"""r9c power / false-positive simulation of the decision rules used in rounds 0-8 (and proposed revisions).
Bootstrap from REAL 2005-2021 trade-return distributions (never 2022+), de-meaned, then shifted by a true edge
(R per trade, net of 1x cost). Trades are iid draws in time order; instruments assigned uniformly at random.
Output: out/r9c_power.csv (pass rates per criterion set), out/r9c_power_marg.csv (single-criterion pass rates),
        out/r9c_power_loo.csv (pass rate of each set with one criterion removed), out/r9c_power.log.
Run: python3 -I r9c_power.py"""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, 'out')
CUT = pd.Timestamp('2022-01-01')
rng = np.random.default_rng(9)
LOG = None
def P(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True)
    if LOG is not None: LOG.write(s + '\n'); LOG.flush()

# ---------------- empirical distributions (2005-2021 only) ----------------
def dists():
    D = {}
    T = pd.read_parquet(os.path.join(OUT, 'r9c_cand_trades.parquet')); C = pd.read_csv(os.path.join(OUT, 'r9c_cands.csv'))
    T = T[(~T.inwin) & (T.t_ent < CUT)].merge(C[['cid', 'out']], on='cid')
    br = T[T.out == 'br']; D['bracket'] = dict(x=br.netR.values, cost=float(((br.netR - br.netR2)).mean()), rho=0.79,
                                              src='r7/r8 candidates, bracket exits (TP1.5/SL1 ATR), 2005-21')
    r6 = pd.read_parquet(os.path.join(OUT, 'r6_trades_all.parquet')); g = r6[(r6.gotobi) & (r6.t_ent < CUT)]
    D['fix'] = dict(x=(g.net / g.R_pips).values, cost=float((0.5 / g.R_pips).mean()), rho=0.95,
                    src='method-1 type: USDJPY Gotobi-eve 22:00->09:55 JST trades, 2005-21')
    h = T[T.out == 'h24']; D['h24'] = dict(x=h.netR.values, cost=float((h.netR - h.netR2).mean()), rho=0.9,
                                          src='r7/r8 candidates, 24-bar fixed holding, 2005-21')
    f = pd.read_parquet(os.path.join(OUT, 'fam_trades.parquet'))
    f = f[(f.strat == 'F1 Donchian | N50 exit chan25 | H4') & (f.t < CUT)]
    D['trend'] = dict(x=f.r.values, cost=0.01, rho=0.95, src='Donchian N50 H4 (round 0), 2012-21, trend-following fat right tail')
    D['normal'] = dict(x=rng.standard_normal(200000), cost=0.02, rho=0.9, src='Gaussian sd 1 (reference)')
    for k, v in D.items():
        x = v['x'] - v['x'].mean(); v['x0'] = x; v['sd'] = float(x.std())
        q = np.sort(x)[::-1]; v['top5_share'] = float(q[:int(np.ceil(0.05 * len(q)))].mean() * 0.05)   # mean lost by dropping top 5%
        P(f"dist {k}: n {len(x)} sd {x.std():.3f} skew {pd.Series(x).skew():.2f} kurt {pd.Series(x).kurt():.1f} "
          f"cost/trade(R) {v['cost']:.4f} drop-top5% shifts mean by -{v['top5_share']:.3f}R | {v['src']}")
    return D

# ---------------- statistics on a (reps x N) matrix ----------------
def tst(x):
    n = x.shape[1]; return x.mean(1) / (x.std(1, ddof=1) / np.sqrt(n))

def ratio(x):
    c = np.cumsum(x, 1); pk = np.maximum.accumulate(np.concatenate([np.zeros((len(x), 1)), c], 1), 1)[:, 1:]
    dd = (c - pk).min(1); s = c[:, -1]
    return np.where(dd < 0, s / np.maximum(-dd, 1e-12), np.inf)

def seg_means(x, edges):
    """means of consecutive segments (fractions of N)"""
    n = x.shape[1]; b = np.round(np.array(edges) * n).astype(int); out = []
    for a, z in zip(b[:-1], b[1:]): out.append(x[:, a:z].mean(1))
    return np.stack(out, 1)

def cell_means(x, inst, edges, ngrp):
    """2 groups (inst < ngrp = 'design') x periods"""
    n = x.shape[1]; b = np.round(np.array(edges) * n).astype(int); out = []
    for a, z in zip(b[:-1], b[1:]):
        xs = x[:, a:z]; gs = inst[:, a:z] < ngrp
        for g in (True, False):
            m = gs == g; out.append(np.where(m.sum(1) > 0, (xs * m).sum(1) / np.maximum(m.sum(1), 1), np.nan))
    return np.stack(out, 1)

def inst_frac(x, inst, K):
    reps = len(x); idx = (np.arange(reps)[:, None] * K + inst).ravel()
    s = np.bincount(idx, weights=x.ravel(), minlength=reps * K).reshape(reps, K)
    return (s > 0).mean(1)

def drop5(x):
    n = x.shape[1]; k = int(np.ceil(0.05 * n)); s = np.sort(x, 1)
    return s[:, :n - k].mean(1)

PER3 = [0, 7 / 20, 14 / 20, 1]           # 2005-11 / 2012-18 / 2019-24
HALF = [0, .5, 1]                         # IS / OOS
BLK4 = [0, 4 / 17, 8 / 17, 12 / 17, 1]    # 2005-08 / 09-12 / 13-16 / 17-21
K = 17; NG = 8

def simulate(d, N, edge, reps, K=K):
    """returns dict criterion-name -> boolean array (reps,)"""
    x0 = d['x0']; c = d['cost']; rho = d['rho']
    i = rng.integers(0, len(x0), size=(reps, N)); e = x0[i]; x = e + edge
    inst = rng.integers(0, K, size=(reps, N))
    j = rng.integers(0, len(x0), size=(reps, N)); xd = edge + rho * e + np.sqrt(1 - rho ** 2) * x0[j]   # one-bar delay
    nh = int(round(N * 3 / 17)); h = x0[rng.integers(0, len(x0), size=(reps, nh))] + edge          # 3-yr holdout
    x2 = x - c; x15 = x - 0.5 * c; x3 = x - 2 * c
    t1 = tst(x); t2 = tst(x2); r1 = ratio(x); r2 = ratio(x2)
    m1 = x.mean(1); m2 = x2.mean(1)
    cr = {}
    cr['mean>0'] = m1 > 0
    for th in (1.5, 2.0, 2.5, 3.0, 3.2, 3.4, 3.5): cr[f't>={th}'] = t1 >= th
    cr['ratio>=3'] = r1 >= 3
    cr['x1.5>0'] = x15.mean(1) > 0
    cr['x2>0'] = m2 > 0
    cr['x3>0'] = x3.mean(1) > 0
    c4 = cell_means(x, inst, HALF, NG); cr['4cells'] = (c4 > 0).all(1)
    c6 = cell_means(x, inst, PER3, NG); cr['6cells'] = (c6 > 0).all(1)
    c6x2 = cell_means(x2, inst, PER3, NG); cr['6cells_x2'] = (c6x2 > 0).all(1)
    p3 = seg_means(x, PER3); cr['3per'] = (p3 > 0).all(1)
    p3x2 = seg_means(x2, PER3); cr['3per_x2'] = (p3x2 > 0).all(1)
    b4 = seg_means(x, BLK4); nb = (b4 > 0).sum(1); cr['blk>=3/4'] = nb >= 3; cr['blk>=2/4'] = nb >= 2
    fr = inst_frac(x, inst, K); cr['inst>=12/17'] = fr >= 12 / 17 - 1e-9; cr['inst>=60%'] = fr >= 0.6; cr['inst>=50%'] = fr >= 0.5
    cr['drop5>0'] = drop5(x) > 0
    cr['delay>0'] = xd.mean(1) > 0
    cr['t_x2>=2'] = t2 >= 2.0; cr['ratio_x2>=3'] = r2 >= 3; cr['x2_t>=3'] = t2 >= 3.0
    # R2 (one-shot early period = first 35% of 2005-24 sample)
    ne = int(round(0.35 * N)); xe = x[:, :ne]; ie = inst[:, :ne]
    ce = cell_means(xe, ie, [0, 1], NG); cr['R2a'] = (ce > 0).all(1)
    cr['R2b'] = tst(xe) >= 1.5
    cr['R2d'] = inst_frac(xe, ie, K) >= 0.6
    ce15 = cell_means(xe - 0.5 * c, ie, [0, 1], NG); cr['R2e'] = (ce15 > 0).all(1) & (x15.mean(1) > 0)
    # holdout stage (r7/r8 acceptance): holdout mean > 0, >= 25% of pool mean, full t >= 3, full ratio >= 3
    hm = h.mean(1); full = np.concatenate([x, h], 1); tf = tst(full)
    cr['H_mean>0'] = hm > 0; cr['H_25pct'] = hm >= 0.25 * m1; cr['H_full_t>=3'] = tf >= 3.0; cr['H_full_ratio>=3'] = ratio(full) >= 3
    cr['H_t>=1'] = tst(h) >= 1.0; cr['H_t>=1.65'] = tst(h) >= 1.645
    cr['H_full_t>=2.5'] = tf >= 2.5
    pf = np.where(x < 0, -x, 0).sum(1); cr['_PF'] = np.where(x > 0, x, 0).sum(1) / np.maximum(pf, 1e-12)
    cr['_t'] = t1; cr['_ratio'] = r1
    return cr

SETS = {
    'R0-R1 (4cells,t>=2,ratio>=3,inst12/17)': (['4cells', 't>=2.0', 'ratio>=3', 'inst>=12/17'], True),
    'R2 one-shot (a,b,c,d,e)': (['R2a', 'R2b', 't>=2.0', 'ratio>=3', 'R2d', 'R2e'], True),
    'R4 S1 (at x2: 6cells,t>=3,ratio>=3,60%,x3>0)': (['6cells_x2', 'x2_t>=3', 'ratio_x2>=3', 'inst>=60%', 'x3>0'], True),
    'R4b/R5 pooled (6cells,t>=3,ratio>=3,60%,x2>0)': (['6cells', 't>=3.0', 'ratio>=3', 'inst>=60%', 'x2>0'], True),
    'R5 pooled (+drop5,+delay)': (['6cells', 't>=3.0', 'ratio>=3', 'inst>=60%', 'x2>0', 'drop5>0', 'delay>0'], True),
    'R5 single (3per,t>=3,ratio>=3,x2,drop5,delay)': (['3per', 't>=3.0', 'ratio>=3', 'x2>0', 'drop5>0', 'delay>0'], False),
    'R4/R4b S2 single (3per,t>=2,ratio>=3; same at x2)': (['3per', 't>=2.0', 'ratio>=3', '3per_x2', 't_x2>=2', 'ratio_x2>=3'], False),
    'R7v1 confirm (t>=3.2,blk3/4,x2)': (['mean>0', 't>=3.2', 'blk>=3/4', 'x2>0'], False),
    'R7v2 confirm single (t>=3.5,blk3/4,x2)': (['mean>0', 't>=3.5', 'blk>=3/4', 'x2>0'], False),
    'R7v2 confirm pooled (+60% pairs)': (['mean>0', 't>=3.5', 'blk>=3/4', 'x2>0', 'inst>=60%'], True),
    'R8 confirm single (t>=3.4,blk3/4,x2)': (['mean>0', 't>=3.4', 'blk>=3/4', 'x2>0'], False),
    'R8 confirm + holdout accept': (['mean>0', 't>=3.4', 'blk>=3/4', 'x2>0', 'H_mean>0', 'H_25pct', 'H_full_t>=3', 'H_full_ratio>=3'], False),
    # proposals
    'PROP screen t>=2.5 (blk2/4,x1.5)': (['mean>0', 't>=2.5', 'blk>=2/4', 'x1.5>0'], False),
    'PROP screen t>=2.0 (blk2/4,x1.5)': (['mean>0', 't>=2.0', 'blk>=2/4', 'x1.5>0'], False),
    'PROP A: screen2.5 + holdout(mean>0, full t>=3)': (['mean>0', 't>=2.5', 'blk>=2/4', 'x1.5>0', 'H_mean>0', 'H_full_t>=3'], False),
    'PROP B: screen2.0 + holdout(mean>0, full t>=3)': (['mean>0', 't>=2.0', 'blk>=2/4', 'x1.5>0', 'H_mean>0', 'H_full_t>=3'], False),
    'PROP C: screen2.0 + holdout(t_h>=1, full t>=2.5)': (['mean>0', 't>=2.0', 'blk>=2/4', 'x1.5>0', 'H_t>=1', 'H_full_t>=2.5'], False),
}

def run():
    global LOG
    LOG = open(os.path.join(OUT, 'r9c_power.log'), 'w')
    D = dists()
    rows, marg, loo = [], [], []
    EDGES = [0.0, 0.01, 0.02, 0.03, 0.05, 0.07, 0.10, 0.15, 0.20, 0.30]
    for dn in ('bracket', 'fix', 'normal', 'h24', 'trend'):
        d = D[dn]
        for N in (300, 1000, 5000):
            for edge in EDGES:
                reps = 4000 if edge == 0 else 1500
                acc = None
                for chunk in range(0, reps, 500):
                    cr = simulate(d, N, edge, min(500, reps - chunk))
                    acc = cr if acc is None else {k: np.concatenate([acc[k], cr[k]]) for k in cr}
                cr = acc
                base = dict(dist=dn, N=N, edge=edge, sd=d['sd'], edge_sd=edge / d['sd'], reps=reps,
                            PF_med=float(np.median(cr['_PF'])), t_med=float(np.median(cr['_t'])), ratio_med=float(np.median(cr['_ratio'])))
                for sname, (crit, pooled) in SETS.items():
                    ok = np.all([cr[c] for c in crit], 0); r = dict(base, set=sname, pass_rate=float(ok.mean())); rows.append(r)
                    for c in crit:
                        rest = [z for z in crit if z != c]
                        okr = np.all([cr[z] for z in rest], 0) if rest else np.ones(len(ok), bool)
                        loo.append(dict(base, set=sname, removed=c, pass_rate=float(okr.mean()), gain=float(okr.mean() - ok.mean())))
                for c in cr:
                    if c.startswith('_'): continue
                    marg.append(dict(base, crit=c, pass_rate=float(cr[c].mean())))
            P(f"done {dn} N={N}")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, 'r9c_power.csv'), index=False)
    pd.DataFrame(marg).to_csv(os.path.join(OUT, 'r9c_power_marg.csv'), index=False)
    pd.DataFrame(loo).to_csv(os.path.join(OUT, 'r9c_power_loo.csv'), index=False)

if __name__ == '__main__':
    run()
