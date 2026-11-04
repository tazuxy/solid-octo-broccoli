"""r9c: which previously rejected rules would pass the PROPOSED screen, using 2005-2021 only (never 2022+).
Track H (hypothesis-driven, pre-registered, economic rationale): min(trade t, daily t) >= 2.5 on 2005-2021, >= 2/4 blocks
  positive (2005-08, 09-12, 13-16, 17-21; round 0 families 2012-21 use 2012-13, 14-15, 16-18, 19-21), mean > 0 at 1.5x cost,
  no block with t <= -2. Warnings (not gates): drop-top-5% mean, ratio, per-instrument share.
Track M (mass search loops r7v2/r8): BH-FDR q = 0.10 over all 400 confirmation tests (original 2005-2021 confirmation sample,
  discovery window excluded) + validity gates (rollover-hour check, 2/4 blocks, 1.5x cost).
Outputs: out/r9c_revive_hyp.csv, out/r9c_revive_loop.csv, out/r9c_revive.log   Run: python3 -I r9c_revive.py"""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r9c_pseudo as PS
OUT = PS.OUT; CUT = PS.CUT
LOG = open(os.path.join(OUT, 'r9c_revive.log'), 'w')
def P(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); LOG.write(s + '\n'); LOG.flush()
B4 = [(2005, 2008), (2009, 2012), (2013, 2016), (2017, 2021)]
B4F = [(2012, 2013), (2014, 2015), (2016, 2018), (2019, 2021)]

def blk_detail(T, blocks):
    y = T.t_ent.dt.year.values; r = T.netR.values; out = []
    for a, b in blocks:
        m = (y >= a) & (y <= b)
        out.append((r[m].mean() if m.sum() >= 5 else np.nan, PS.tstat(r[m]) if m.sum() >= 5 else np.nan))
    return out

def drop5(r):
    r = np.sort(np.asarray(r))[::-1]; k = int(np.ceil(0.05 * len(r))); return r[k:].mean()

def screen(s, bd):
    neg = any(np.isfinite(t) and t <= -2 for _, t in bd)
    return bool(np.isfinite(s['t_used']) and s['mean_R'] > 0 and s['mean_pips'] > 0 and s['t_used'] >= 2.5 and s['nblk'] >= 2
                and s['x15'] > 0 and not neg)

def main():
    rows = []
    for nm, T, pooled in PS.hyp_rules():
        T = T.sort_values('t_ent').copy(); T['t_ent'] = pd.to_datetime(T.t_ent); T['t_exit'] = pd.to_datetime(T.t_exit)
        assert T.t_ent.max() < CUT
        blocks = B4F if nm.startswith('r0') else B4
        s = PS.stats(T, pooled, blocks=blocks, rollcheck=False); bd = blk_detail(T, blocks)
        r = dict(rule=nm, years='2012-21' if nm.startswith('r0') else '2005-21', N=s['N'], mean_R=s['mean_R'], mean_pips=s['mean_pips'],
                 t_used=s['t_used'], blocks=f"{s['nblk']}/{s['nblkn']}", blk_means=' / '.join(f'{m:+.3f}' for m, _ in bd),
                 x15=s['x15'], x2=s['x2'], ratio=s['ratio'], pairs=s['pairs'], drop5=drop5(T.netR.values), screen_H=screen(s, bd))
        rows.append(r)
    H = pd.DataFrame(rows); H.to_csv(os.path.join(OUT, 'r9c_revive_hyp.csv'), index=False)
    pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
    P('Track H screen on 2005-2021 (r0 families 2012-2021):')
    P(H.sort_values('t_used', ascending=False).head(15).round(3).to_string(index=False))
    # loop candidates: recompute 2005-21 stats with the same functions (identical to the original confirmation sample)
    C = pd.read_csv(os.path.join(OUT, 'r9c_cands.csv')); T = pd.read_parquet(os.path.join(OUT, 'r9c_cand_trades.parquet'))
    assert T.t_ent.max() < CUT
    T = T[~T.inwin]; rows = []
    for cid, g in T.groupby('cid'):
        c = C.loc[C.cid == cid].iloc[0]; g = g.sort_values('t_ent')
        s = PS.stats(g, bool(c.pooled), blocks=B4, rollcheck=True); bd = blk_detail(g, B4)
        rows.append(dict(cid=cid, round=c['round'], window=c.window, cand=c.cand, pooled=c.pooled, N=s['N'], mean_R=s['mean_R'],
                         t_used=s['t_used'], blocks=f"{s['nblk']}/{s['nblkn']}", x15=s['x15'], roll_ok=s['roll'], pairs=s['pairs'],
                         p=PS.pval(s['t_used']), gates=screen(s, bd) and s['roll'] and (not c.pooled or s['pairs'] >= 0.6)))
    Lp = pd.DataFrame(rows); m = len(Lp); p = Lp.p.values; o = np.argsort(p); thr = 0.10 * np.arange(1, m + 1) / m
    k = np.nonzero(p[o] <= thr)[0]; cut = p[o][k.max()] if len(k) else -1
    Lp['BH10'] = Lp.p <= cut; Lp['trackM'] = Lp.BH10 & Lp.gates; Lp['trackH_if_misapplied'] = Lp.gates
    Lp.to_csv(os.path.join(OUT, 'r9c_revive_loop.csv'), index=False)
    P(f'\nTrack M: BH q=0.10 over {m} loop tests: p cut {cut:.3g}; BH rejections {int(Lp.BH10.sum())}; + gates {int(Lp.trackM.sum())}')
    P(Lp[Lp.BH10 | Lp.gates].round(3).to_string(index=False))
    P('\nTop-8 loop candidates by 2005-21 t:')
    P(Lp.sort_values('t_used', ascending=False).head(8)[['cand', 'round', 'window', 'N', 'mean_R', 't_used', 'blocks', 'x15', 'roll_ok', 'pairs', 'BH10', 'gates']].round(3).to_string(index=False))

if __name__ == '__main__':
    main()
