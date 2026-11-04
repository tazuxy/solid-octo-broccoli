"""Method 2: conditional exit at +1R vs hold to 15:00 JST (pre-registered in research/round11/r11_m2_cond_exit_prereg.md).
Usage (work dir): python3 -I code/r11_m2_cond_exit.py <FXCM_PQ_DIR>"""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sig import rsi
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, 'out'); PQ = sys.argv[1]
T = pd.read_parquet(os.path.join(OUT, 'r10_r11_trades.parquet')); T = T[(T.hyp == 'F2') & (T.delay == 0)].sort_values('t_ent')
d1 = pd.read_parquet(os.path.join(ROOT, 'bars_full', 'USDJPY_D1.parquet')); d1['sma'] = d1.close.rolling(20).mean(); d1['tclose'] = d1.index + pd.Timedelta('24h')
h4 = pd.read_parquet(os.path.join(ROOT, 'bars_full', 'USDJPY_H4.parquet')); h4['sma'] = h4.close.rolling(20).mean(); h4['tclose'] = h4.index + pd.Timedelta('4h')
m15 = pd.read_parquet(os.path.join(ROOT, 'bars_full', 'USDJPY_M15.parquet')); m15['rsi'] = rsi(m15.close.values.astype(float), 14); m15['tclose'] = m15.index + pd.Timedelta('15min')
COST = 0.005
def last_closed(df, t):
    i = df.tclose.searchsorted(t, side='right') - 1
    return df.iloc[i] if i >= 0 else None
def run(src):
    if src == 'hist':
        b = pd.read_parquet(os.path.join(ROOT, 'bars_m5', 'USDJPY_M5.parquet')); E = O = b.open.values; Hh, Ll = b.high.values, b.low.values; c = COST
    else:
        b = pd.read_parquet(os.path.join(PQ, 'USDJPY_M1BA.parquet')); E = b.bo.values; O, Hh, Ll = b.ao.values, b.ah.values, b.al.values; c = 0.0
    idx = b.index; rows = []
    for _, t in T.iterrows():
        if src == 'fxcm' and t.t_ent < pd.Timestamp('2012-01-02'): continue
        i0 = idx.searchsorted(t.t_ent); i1 = idx.searchsorted(t.t_exit)
        if i1 >= len(idx) or idx[i0] - t.t_ent > pd.Timedelta('15min') or idx[i1] - t.t_exit > pd.Timedelta('15min'): continue
        e = E[i0]; R = t.R_pips; sl = e + R; tp = e - R; hold = None; touch = None; exitv = None
        for j in range(i0, i1):
            if j > i0 and O[j] >= sl: hold = e - O[j]; break
            if Hh[j] >= sl: hold = e - sl; break                          # stop first if both in one bar
            if touch is None:
                if j > i0 and O[j] <= tp: touch, exitv = j, e - O[j]
                elif Ll[j] <= tp: touch, exitv = j, e - tp
        if hold is None: hold = e - O[i1]
        if touch is None: continue
        tt = idx[touch]; tpx = tp if exitv == e - tp else O[touch]
        D = last_closed(d1, tt); H = last_closed(h4, tt); M = last_closed(m15, tt)
        f = dict(f1_d1_up=bool(D is not None and D.close > D.sma), f2_h4_up=bool(H is not None and H.close > H.sma),
                 f3_pdl_near=bool(D is not None and tpx - 0.5 * R <= D.low <= tpx), f5_rsi_os=bool(M is not None and M.rsi < 30),
                 f6_late=bool((tt + pd.Timedelta(hours=14)).hour * 60 + (tt + pd.Timedelta(hours=14)).minute >= 10 * 60 + 30))
        lv = np.floor(tpx / 0.5) * 0.5; f['f4_round_near'] = bool(tpx - 0.5 * R <= lv <= tpx)
        rows.append(dict(src=src, t=t.t_ent, exitR=(exitv - c) / R, holdR=(hold - c) / R, **f))
    return pd.DataFrame(rows)
A = pd.concat([run('hist'), run('fxcm')]); A['impr'] = A.exitR - A.holdR; A.to_csv(os.path.join(OUT, 'r11_m2_cond_exit.csv'), index=False)
FS = ['f1_d1_up', 'f2_h4_up', 'f3_pdl_near', 'f4_round_near', 'f5_rsi_os', 'f6_late']
def st(x):
    x = np.asarray(x, float); return (len(x), x.mean() if len(x) else np.nan, x.mean() / x.std(ddof=1) * np.sqrt(len(x)) if len(x) > 2 else np.nan)
P = {'2005-14': ('hist', '2005', '2015'), '2015-21': ('hist', '2015', '2022'), '2022-24': ('hist', '2022', '2025'), 'FXCM 2022-24 (ref)': ('fxcm', '2022', '2025')}
for nm, (s, a, z) in P.items():
    g = A[(A.src == s) & (A.t >= a) & (A.t < z)]; n, m, tt = st(g.impr)
    print(f'{nm}: trades touching +1R N={len(g)}; always-exit vs hold improvement mean {m:+.3f}R (t {tt:.2f})')
out = []
for fcol in FS:
    r = {'feature': fcol}
    for nm, (s, a, z) in P.items():
        g = A[(A.src == s) & (A.t >= a) & (A.t < z)]
        n1, m1, t1 = st(g[g[fcol]].impr); n0, m0, t0 = st(g[~g[fcol]].impr)
        r[f'{nm} flag N'] = n1; r[f'{nm} flag impr'] = m1; r[f'{nm} flag t'] = t1; r[f'{nm} noflag impr'] = m0
    r['ADOPT'] = bool(r['2005-14 flag N'] >= 30 and r['2005-14 flag impr'] > 0 and r['2005-14 flag t'] >= 2.0 and r['2015-21 flag impr'] > 0 and r['2022-24 flag impr'] > 0)
    out.append(r)
O_ = pd.DataFrame(out); O_.to_csv(os.path.join(OUT, 'r11_m2_cond_exit_summary.csv'), index=False)
pd.set_option('display.width', 250); print(O_.round(3).T.to_string())
