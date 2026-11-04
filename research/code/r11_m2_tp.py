"""Method 2 take-profit grid (pre-registered in research/round11/r11_m2_tp_prereg.md).
Short USDJPY 09:55 -> 15:00 JST on Gotobi days; stop 1R (or none); TP = entry - m*R on M5 lows; stop first if both in one bar.
histdata (bid M5, 0.5 pip cost) and FXCM real bid/ask M1 (short: entry at bid, stop/TP/exit on ask).
Usage (work dir): python3 -I code/r11_m2_tp.py <FXCM_PQ_DIR>"""
import os, sys, numpy as np, pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, 'out'); PQ = sys.argv[1]
T = pd.read_parquet(os.path.join(OUT, 'r10_r11_trades.parquet')); T = T[(T.hyp == 'F2') & (T.delay == 0)].sort_values('t_ent')
MS = [None, 0.5, 1, 1.5, 2, 3]; STOPS = [1, None]; COST = 0.005
def path_trade(e, R, o_ex, hi, lo, op, ex, stop_k, m, cost):
    sl = e + stop_k * R if stop_k else None; tp = e - m * R if m else None
    for j in range(len(hi)):
        if j > 0:
            if sl is not None and op[j] >= sl: return e - op[j] - cost, 'sl', j
            if tp is not None and op[j] <= tp: return e - op[j] - cost, 'tp', j
        if sl is not None and hi[j] >= sl: return e - sl - cost, 'sl', j
        if tp is not None and lo[j] <= tp: return e - tp - cost, 'tp', j
    return e - ex - cost, 'time', len(hi)
def run(src):
    if src == 'hist':
        b = pd.read_parquet(os.path.join(ROOT, 'bars_m5', 'USDJPY_M5.parquet')); O, Hh, Ll = b.open.values, b.high.values, b.low.values; X = O; E = O
    else:
        b = pd.read_parquet(os.path.join(PQ, 'USDJPY_M1BA.parquet')); O, Hh, Ll = b.ao.values, b.ah.values, b.al.values; X = b.ao.values; E = b.bo.values
    idx = b.index; rows = []
    for _, t in T.iterrows():
        if src == 'fxcm' and t.t_ent < pd.Timestamp('2012-01-02'): continue
        i0 = idx.searchsorted(t.t_ent); i1 = idx.searchsorted(t.t_exit)
        if i1 >= len(idx) or idx[i0] - t.t_ent > pd.Timedelta('15min') or idx[i1] - t.t_exit > pd.Timedelta('15min'): continue
        e = E[i0]; ex = X[i1]; hi, lo, op = Hh[i0:i1], Ll[i0:i1], O[i0:i1]; R = t.R_pips; c = COST if src == 'hist' else 0.0
        mfe = (e - lo.min()) / R if len(lo) else 0.0
        for sk in STOPS:
            for m in MS:
                net, why, j = path_trade(e, R, None, hi, lo, op, ex, sk, m, c)
                rows.append(dict(src=src, t=t.t_ent, stop='1R' if sk else 'none', tp='none' if m is None else m, netR=net / R, pips=net * 100,
                                 why=why, bars=j, mfe=mfe))
    return pd.DataFrame(rows)
D = pd.concat([run('hist'), run('fxcm')]); D.to_csv(os.path.join(OUT, 'r11_m2_tp.csv'), index=False)
def summ(g):
    r = g.netR.values; cs = np.cumsum(r); dd = (cs - np.maximum.accumulate(np.maximum(cs, 0))).min()
    return dict(N=len(r), meanR=r.mean(), t=r.mean() / r.std(ddof=1) * np.sqrt(len(r)), pips=g.pips.mean(), win=(r > 0).mean(),
                tp_hit=(g.why == 'tp').mean(), sl_hit=(g.why == 'sl').mean(), maxddR=dd, worst=g.pips.min(), drop5=np.sort(r)[::-1][int(np.ceil(.05 * len(r))):].mean())
pd.set_option('display.width', 220)
sets = {'hist 2005-21': ('hist', '2005', '2022'), 'hist 2022-24': ('hist', '2022', '2025'), 'FXCM 2012-24': ('fxcm', '2012', '2025')}
res = {}
for nm, (s, a, z) in sets.items():
    G = D[(D.src == s) & (D.t >= a) & (D.t < z)]
    S = pd.DataFrame([dict(stop=k[0], tp=k[1], **summ(g)) for k, g in G.groupby(['stop', 'tp'], sort=False)]); res[nm] = S
    print('==', nm); print(S.round(3).to_string(index=False))
# pre-registered decision (stop 1R)
def mR(nm, tp): S = res[nm]; return float(S[(S.stop == '1R') & (S.tp.astype(str) == str(tp))].meanR.iloc[0])
def tt(nm, tp): S = res[nm]; return float(S[(S.stop == '1R') & (S.tp.astype(str) == str(tp))].t.iloc[0])
ok = []
for m in MS[1:]:
    c1 = mR('hist 2005-21', m) >= 1.10 * mR('hist 2005-21', 'none') and tt('hist 2005-21', m) >= 2.5
    c2 = mR('hist 2022-24', m) >= mR('hist 2022-24', 'none'); c3 = mR('FXCM 2012-24', m) >= mR('FXCM 2012-24', 'none')
    print(f'TP {m}R: cond1 {c1} cond2 {c2} cond3 {c3}'); ok += [m] if (c1 and c2 and c3) else []
print('pre-registered choice:', max(ok, key=lambda m: mR('hist 2005-21', m)) if ok else 'time exit only (no TP)')
h = D[(D.src == 'hist') & (D.stop == '1R') & (D.tp == 'none') & (D.t < '2022')]
print('MFE (R) before exit, 2005-21: median %.2f, share reaching 0.5R %.0f%%, 1R %.0f%%, 2R %.0f%%, 3R %.0f%%' % (h.mfe.median(), 100 * (h.mfe >= .5).mean(), 100 * (h.mfe >= 1).mean(), 100 * (h.mfe >= 2).mean(), 100 * (h.mfe >= 3).mean()))
for th in (1, 2):
    g = h[h.mfe >= th]; print(f'trades whose MFE reached {th}R: N {len(g)}, final result at 15:00 mean {g.netR.mean():+.2f}R, share ending below {th}R {(g.netR < th).mean():.0%}')
