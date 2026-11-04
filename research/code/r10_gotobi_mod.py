"""Method 1 modifications (pre-registered in research/round10/r10_gotobi_mod_prereg.md):
  base = method 1 (Gotobi-eve USDJPY, month-end-business-day G skipped); A1 skip holiday G; A2 move holiday G to the previous JP business day;
  B1 skip Monday G; B2 Monday G: buy Monday 08:00 JST (Sunday 18:00 EST) instead of Friday 22:00 JST.
Data sets: 'pre' = histdata 2000-05-30..2004-12-31 (unused), 'main' = histdata 2005-2024 (used), 'fxcm' = FXCM bid/ask 2025-2026 (used).
Usage: python3 -I r10_gotobi_mod.py <REPO> <WORK> <PRE_ZIP_DIR> <FXCM_DIR>   -> prints tables, writes <WORK>/out/r10_gotobi_mod_*.csv"""
import os, sys, glob, zipfile, numpy as np, pandas as pd
REPO, WORK, PRE, FX = sys.argv[1:5]
COST = 0.5
# ---------------- calendars
hol = pd.read_csv(os.path.join(REPO, 'research', 'round10', 'jp_holidays_cao.csv'))
HOL = set(pd.to_datetime(hol.iloc[:, 0], format='%Y/%m/%d'))
for y in range(1999, 2028):
    HOL |= {pd.Timestamp(y, 12, 31), pd.Timestamp(y, 1, 2), pd.Timestamp(y, 1, 3)}
def prev_wd(d):
    d = d - pd.Timedelta(days=1)
    while d.dayofweek >= 5: d -= pd.Timedelta(days=1)
    return d
def base_G(y0, y1):
    G = set()
    for y in range(y0, y1 + 1):
        for mo in range(1, 13):
            last = pd.Timestamp(y, mo, 1) + pd.offsets.MonthEnd(0)
            for g in [pd.Timestamp(y, mo, k) for k in (5, 10, 15, 20, 25, 30) if k <= last.day] + [last]:
                while g.dayofweek >= 5: g -= pd.Timedelta(days=1)
                G.add(g)
    bd = pd.bdate_range(f'{y0}-01-01', f'{y1}-12-31')
    lastbd = set(pd.Series(bd, index=bd).groupby([bd.year, bd.month]).max())
    return sorted(g for g in G if g not in lastbd)
def schedule(variant, y0, y1):
    """list of dicts: G, t_in (EST), t_out (EST), tag in {'base','new'}; 'aff' marks base trades affected by the variant"""
    out = []; Gs = base_G(y0, y1); Gset = set(Gs)
    for g in Gs:
        t_in = prev_wd(g) + pd.Timedelta(hours=8); t_out = g - pd.Timedelta(days=1) + pd.Timedelta(hours=19, minutes=55)
        isH, isM = g in HOL, g.dayofweek == 0
        if variant == 'base': out.append(dict(G=g, t_in=t_in, t_out=t_out, kind='keep'))
        elif variant == 'A1': out.append(dict(G=g, t_in=t_in, t_out=t_out, kind='drop' if isH else 'keep'))
        elif variant == 'A2':
            if not isH: out.append(dict(G=g, t_in=t_in, t_out=t_out, kind='keep')); continue
            out.append(dict(G=g, t_in=t_in, t_out=t_out, kind='drop'))
            g2 = g - pd.Timedelta(days=1)
            while g2.dayofweek >= 5 or g2 in HOL: g2 -= pd.Timedelta(days=1)
            if g2 in Gset: continue
            out.append(dict(G=g2, t_in=prev_wd(g2) + pd.Timedelta(hours=8), t_out=g2 - pd.Timedelta(days=1) + pd.Timedelta(hours=19, minutes=55), kind='new'))
        elif variant == 'B1': out.append(dict(G=g, t_in=t_in, t_out=t_out, kind='drop' if isM else 'keep'))
        elif variant == 'B2':
            if not isM: out.append(dict(G=g, t_in=t_in, t_out=t_out, kind='keep')); continue
            out.append(dict(G=g, t_in=t_in, t_out=t_out, kind='drop'))
            out.append(dict(G=g, t_in=g - pd.Timedelta(days=1) + pd.Timedelta(hours=18), t_out=t_out, kind='new'))
    return out
# ---------------- prices
def m5_pre():
    fr = []
    for z in sorted(glob.glob(os.path.join(PRE, 'DAT_ASCII_USDJPY_M1_200*.zip'))):
        with zipfile.ZipFile(z) as f:
            n = [x for x in f.namelist() if x.endswith('.csv')][0]
            d = pd.read_csv(f.open(n), sep=';', header=None, names=['ts', 'open', 'high', 'low', 'close', 'v'])
        d['ts'] = pd.to_datetime(d.ts, format='%Y%m%d %H%M%S'); fr.append(d.drop(columns='v'))
    m = pd.concat(fr).drop_duplicates('ts').set_index('ts').sort_index()
    med = m.close.rolling(61, center=True, min_periods=11).median()            # same spike cleaning as r2/r4
    dev = np.log(m[['open', 'high', 'low', 'close']].div(med, axis=0)).abs().max(axis=1); m = m[~(dev > 0.10)]
    return m.resample('5min', label='left', closed='left').agg({'open': 'first'}).dropna()
SRC = {}
SRC['pre'] = ('bid', m5_pre())
SRC['main'] = ('bid', pd.read_parquet(os.path.join(WORK, 'bars_m5', 'USDJPY_M5.parquet'))[['open']])
fr = []
for f in sorted(glob.glob(os.path.join(FX, 'USDJPY_202[56]_*.csv.gz'))):
    d = pd.read_csv(f); d['ts'] = pd.to_datetime(d.DateTime, format='%m/%d/%Y %H:%M:%S.%f') - pd.Timedelta('5h'); fr.append(d)
fx = pd.concat(fr).drop_duplicates('ts').set_index('ts').sort_index(); fx = fx[fx.index >= '2025-01-01']
SRC['fxcm'] = ('ba', fx[['BidOpen', 'AskOpen']])
RANGE = {'pre': (2000, 2004, '2000-05-30', '2004-12-31'), 'main': (2005, 2024, '2005-01-01', '2024-12-31'), 'fxcm': (2025, 2026, '2025-01-01', str(fx.index.max()))}
def px(src, t):
    kind, b = SRC[src]; i = b.index.searchsorted(t)
    if i >= len(b) or b.index[i] - t > pd.Timedelta('15min'): return None
    return b.iloc[i]
def trades(src, variant):
    y0, y1, a, z = RANGE[src]; rows = []
    for s in schedule(variant, y0, y1):
        if s['t_in'] < pd.Timestamp(a) or s['t_out'] > pd.Timestamp(z): continue
        p_in, p_out = px(src, s['t_in']), px(src, s['t_out'])
        if p_in is None or p_out is None: continue
        if SRC[src][0] == 'bid': net = (p_out.open - p_in.open) / 0.01 - COST
        else: net = (p_out.BidOpen - p_in.AskOpen) / 0.01                     # real bid/ask, no fixed cost
        rows.append(dict(src=src, variant=variant, G=s['G'], t_in=s['t_in'], kind=s['kind'], net=net,
                         hol=s['G'] in HOL, mon=s['G'].dayofweek == 0))
    return pd.DataFrame(rows)
def summ(x):
    x = np.asarray(x, float)
    if len(x) == 0: return dict(N=0, mean=np.nan, t=np.nan, sum=0.0, maxdd=0.0, ratio=np.nan)
    cs = np.cumsum(x); dd = float((cs - np.maximum(np.maximum.accumulate(cs), 0)).min())
    t = x.mean() / (x.std(ddof=1) / np.sqrt(len(x))) if len(x) > 2 else np.nan
    return dict(N=len(x), mean=x.mean(), t=t, sum=x.sum(), maxdd=dd, ratio=x.sum() / abs(dd) if dd < 0 else np.inf)
if __name__ == '__main__':
    pd.set_option('display.width', 220)
    rows = []; aff = []; allT = []
    rng = np.random.default_rng(10)
    for src in ('main', 'pre', 'fxcm'):
        base = trades(src, 'base'); allT.append(base)
        sb = summ(base.sort_values('t_in').net); rows.append(dict(src=src, variant='base', **sb, mean_x2=(base.net - (COST if src != 'fxcm' else 0) * 1).mean()))
        for v in ('A1', 'A2', 'B1', 'B2'):
            T = trades(src, v); allT.append(T)
            kept = T[T.kind != 'drop'].sort_values('t_in')
            s = summ(kept.net); rows.append(dict(src=src, variant=v, **s, mean_x2=(kept.net - (COST if src != 'fxcm' else 0)).mean()))
            dr = T[T.kind == 'drop'].net.values; nw = T[T.kind == 'new'].net.values
            k = len(dr); rk = np.nan
            if k > 0: rk = float((np.array([rng.choice(base.net.values, k, replace=False).mean() for _ in range(20000)]) < dr.mean()).mean())
            aff.append(dict(src=src, variant=v, n_drop=k, drop_mean=dr.mean() if k else np.nan, n_new=len(nw), new_mean=nw.mean() if len(nw) else np.nan,
                            rank_drop_among_random=rk))
    S = pd.DataFrame(rows); A = pd.DataFrame(aff)
    S.to_csv(os.path.join(WORK, 'out', 'r10_gotobi_mod_summary.csv'), index=False); A.to_csv(os.path.join(WORK, 'out', 'r10_gotobi_mod_affected.csv'), index=False)
    pd.concat(allT).to_csv(os.path.join(WORK, 'out', 'r10_gotobi_mod_trades.csv'), index=False)
    print(S.round(2).to_string(index=False)); print(A.round(3).to_string(index=False))
    # pre-registered decision
    for v in ('A1', 'A2', 'B1', 'B2'):
        b = S[(S.src == 'main') & (S.variant == 'base')].iloc[0]; m = S[(S.src == 'main') & (S.variant == v)].iloc[0]
        c1 = bool(m['mean'] > b['mean'] and m['ratio'] > b['ratio'])
        a = A[(A.src == 'pre') & (A.variant == v)].iloc[0]
        c2 = bool(a.drop_mean < 0) if v in ('A1', 'B1') else bool(a.new_mean > a.drop_mean)
        print(f'{v}: cond1 (2005-24 better mean and sum/DD) = {c1}; cond2 (2000-04 same direction) = {c2}; ADOPT = {c1 and c2}')
