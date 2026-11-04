"""r9c extra: (1) precise false-positive rates (edge 0, 20,000 reps) of every criterion set incl. proposals;
(2) power of the mass-search proposal (PROP M) on the edge grid; (3) edge needed for 50% / 80% power per set (interpolated).
Uses the simulator in r9c_power.py (2005-2021 empirical distributions only).
Outputs: out/r9c_fpr.csv, out/r9c_power_m.csv, out/r9c_power_need.csv   Run: python3 -I r9c_power_extra.py"""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r9c_power as RP
OUT = RP.OUT
RP.SETS['PROP M: t>=3.5,blk2/4,x1.5 + holdout(mean>0, full t>=3)'] = (['mean>0', 't>=3.5', 'blk>=2/4', 'x1.5>0', 'H_mean>0', 'H_full_t>=3'], False)

def sim_sets(d, N, edge, reps):
    acc = None
    for c in range(0, reps, 500):
        cr = RP.simulate(d, N, edge, min(500, reps - c))
        acc = cr if acc is None else {k: np.concatenate([acc[k], cr[k]]) for k in cr}
    return {s: float(np.all([acc[c] for c in crit], 0).mean()) for s, (crit, _) in RP.SETS.items()}

def main():
    D = RP.dists(); rows = []
    for dn in ('bracket', 'fix'):
        for N in (300, 1000, 5000):
            r = sim_sets(D[dn], N, 0.0, 20000)
            for s, v in r.items(): rows.append(dict(dist=dn, N=N, set=s, fpr=v))
            print('fpr', dn, N, flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(OUT, 'r9c_fpr.csv'), index=False)
    rows = []
    for dn in ('bracket', 'fix'):
        for N in (300, 1000, 5000):
            for e in (0.02, 0.03, 0.05, 0.07, 0.10, 0.15, 0.20, 0.30):
                r = sim_sets(D[dn], N, e, 1500)
                rows.append(dict(dist=dn, N=N, edge=e, set='PROP M: t>=3.5,blk2/4,x1.5 + holdout(mean>0, full t>=3)',
                                 pass_rate=r['PROP M: t>=3.5,blk2/4,x1.5 + holdout(mean>0, full t>=3)']))
            print('propM', dn, N, flush=True)
    M = pd.DataFrame(rows); M.to_csv(os.path.join(OUT, 'r9c_power_m.csv'), index=False)
    A = pd.concat([pd.read_csv(os.path.join(OUT, 'r9c_power.csv'))[['dist', 'N', 'edge', 'set', 'pass_rate']], M])
    need = []
    for (dn, N, s), g in A.groupby(['dist', 'N', 'set']):
        g = g[g.edge > 0].sort_values('edge'); e = g.edge.values; p = g.pass_rate.values
        r = dict(dist=dn, N=N, set=s)
        for q in (0.5, 0.8):
            k = np.nonzero(p >= q)[0]
            if not len(k): r[f'edge_{int(q * 100)}'] = np.nan; continue
            k = k[0]
            r[f'edge_{int(q * 100)}'] = e[0] if k == 0 else e[k - 1] + (q - p[k - 1]) * (e[k] - e[k - 1]) / (p[k] - p[k - 1])
        need.append(r)
    pd.DataFrame(need).to_csv(os.path.join(OUT, 'r9c_power_need.csv'), index=False)
    print('done')

if __name__ == '__main__':
    main()
