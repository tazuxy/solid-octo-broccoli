"""Method 2 stop-loss grid (pre-registered in research/round11/r11_m2_stop_prereg.md).
Short USDJPY at 09:55 JST on Gotobi days (incl. month-end), exit 15:00 JST, stop = entry + k*R checked on M5 highs.
Usage (work dir): python3 -I code/r11_m2_stop.py   -> out/r11_m2_stop.csv"""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, 'out')
T = pd.read_parquet(os.path.join(OUT, 'r10_r11_trades.parquet')); T = T[(T.hyp == 'F2') & (T.delay == 0)].sort_values('t_ent')
b = pd.read_parquet(os.path.join(ROOT, 'bars_m5', 'USDJPY_M5.parquet'))
o, h = b.open.values, b.high.values; idx = b.index
KS = [None, 1, 1.5, 2, 3, 4, 6]; COST = 0.005; PIP = 0.01
rows = []
for _, t in T.iterrows():
    i0 = idx.searchsorted(t.t_ent); i1 = idx.searchsorted(t.t_exit)
    ent, xit, R = t.t_ent, None, t.R_pips
    e = o[i0]; ex = o[i1]
    for k in KS:
        px, hit = ex, 0
        if k is not None:
            sl = e + k * R
            for j in range(i0, i1):
                if j > i0 and o[j] >= sl: px, hit = o[j], 2; break      # gap through the stop
                if h[j] >= sl: px, hit = sl, 1; break
        net = (e - px) - COST
        rows.append(dict(t=t.t_ent, k='none' if k is None else k, netR=net / R, pips=net / PIP, hit=hit, R_pips=R / PIP))
D = pd.DataFrame(rows); D.to_csv(os.path.join(OUT, 'r11_m2_stop.csv'), index=False)
def summ(g, extra_slip=0.0):
    r = g.netR.values - (g.hit.values > 0) * extra_slip * PIP / (g.R_pips.values * PIP)
    p = g.pips.values - (g.hit.values > 0) * extra_slip
    cs = np.cumsum(r); dd = (cs - np.maximum.accumulate(np.maximum(cs, 0))).min()
    return dict(N=len(r), meanR=r.mean(), t=r.mean() / r.std(ddof=1) * np.sqrt(len(r)), mean_pips=p.mean(), worstR=r.min(), worst_pips=p.min(),
                p1_pips=np.percentile(p, 1), maxddR=dd, stopped=(g.hit > 0).mean(), gaps=int((g.hit == 2).sum()))
pd.set_option('display.width', 200)
for nm, (a, z) in {'2005-2021 (selection)': ('2005', '2022'), '2022-2024 (check)': ('2022', '2025')}.items():
    S = pd.DataFrame([dict(k=k, **summ(g)) for k, g in D[(D.t >= a) & (D.t < z)].groupby('k', sort=False)])
    print(nm); print(S.round(3).to_string(index=False))
    if 'selection' in nm:
        base = S[S.k == 'none'].iloc[0]
        ok = S[(S.k != 'none') & (S.meanR >= 0.9 * base.meanR) & (S.t >= 2.5)]
        print('pre-registered choice:', ok.k.min() if len(ok) else 'no stop + small lot')
    S2 = pd.DataFrame([dict(k=k, **summ(g, 1.0)) for k, g in D[(D.t >= a) & (D.t < z)].groupby('k', sort=False)])
    print(nm, 'with +1 pip slippage on stop fills:'); print(S2[['k', 'meanR', 't', 'mean_pips', 'worst_pips']].round(3).to_string(index=False))
print('median R in pips: %.1f; R pips by period:' % T.R_pips.mul(100).median(), T.groupby(T.t_ent.dt.year // 5 * 5).R_pips.median().mul(100).round(1).to_dict())
