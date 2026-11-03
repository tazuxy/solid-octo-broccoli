"""Round 2, candidates P1/P2 (cross-sectional currency reversal), weekly series.
Exact round-1 H1 logic (r1_h1.run) with two parametrisations only:
  * data directory (bars/ or bars_full/) -> r1_common.BARS is patched, panels() unchanged;
  * execution: 'd1open' = round-1 (next D1 open, Sunday 17:00 EST) or 'mon08' = open of the first H1 bar at/after
    08:00 EST on the next trading day after the Friday-close decision (normally Monday 08:00 EST); if no H1 bar
    between 08:00 and 17:00 that day, the last H1 close before 08:00 is used. Holding return = exec[k+1]/exec[k]-1.
Variant 'arev' = H1a with the sign flipped (long the 2 lowest 12-week (skip last week) basket returns, short the 2 highest).
Warm-up (bars_full only): a pair is not tradable in the C-implementation LP during its first 6 months of data
(matters only for AUDNZD 2007-09..2008-03); weeks are scored later from a start date set in r2_eval_port.py.
usage: python -I code/r2_xs.py"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_common
from r1_common import *
from r1_h1 import CCY_D, CCY_C, USDP, ccy_logidx
from scipy.optimize import linprog
from multiprocessing import Pool

def set_bars(d):
    r1_common.BARS = os.path.join(ROOT, d); r1_common._cache.clear()

def mon08_panel(pairs, idx, bars):
    out = {}
    for p in pairs:
        h = pd.read_parquet(os.path.join(ROOT, bars, f'{p}_H1.parquet'))
        ts = h.index.values; o = h.open.values; c = h.close.values
        T = (idx + pd.Timedelta(hours=8)).values; T17 = (idx + pd.Timedelta(hours=17)).values
        j = np.searchsorted(ts, T, side='left')
        px = np.full(len(idx), np.nan)
        ok = (j < len(ts)) & (ts[np.clip(j, 0, len(ts) - 1)] < T17)
        px[ok] = o[j[ok]]
        jb = j - 1; okb = (~ok) & (jb >= 0)
        px[okb] = c[jb[okb]]
        px[T < ts[0]] = np.nan
        out[p] = px
    return pd.DataFrame(out, index=idx)

def run(impl, variant, cost_mult=1.0, k=2, execm='d1open', bars='bars', warm=False):
    set_bars(bars)
    C, Cf, X = panels()
    if execm == 'mon08': X = mon08_panel(list(C.columns), C.index, bars)
    gap = None
    if warm:   # bars_full only: a pair with no D1 bar for > 10 calendar days is treated as unavailable inside that gap
        gap = pd.DataFrame(False, index=C.index, columns=C.columns)   # (AUDJPY 2005-05, 2012-01..09, 2012-11..12)
        for p_ in C.columns:
            have = C[p_].dropna().index
            for a_, b_ in zip(have[:-1], have[1:]):
                if (b_ - a_).days > 10: gap.loc[(gap.index > a_) & (gap.index < b_), p_] = True
        Cf = Cf.mask(gap); X = X.mask(gap)
    ccys = CCY_D if impl == 'D' else CCY_C
    pairs = [USDP[c][0] for c in CCY_D if c != 'USD'] if impl == 'D' else CROSS
    first = {p: C[p].first_valid_index() for p in pairs}
    Lc = ccy_logidx(Cf, impl)
    Lx = ccy_logidx(X.ffill() if gap is None else X.ffill().mask(gap), impl)
    Xb = Lc.sub(Lc.mean(axis=1), axis=0)
    Xe = Lx.sub(Lx.mean(axis=1), axis=0)
    vol20 = Xb.diff().rolling(20).std()
    sch = weekly_schedule(C.index)
    A = np.array([[1 if p[:3] == c else (-1 if p[3:] == c else 0) for p in CROSS] for c in CCY_C], float)
    rows = []; prev_q = pd.Series(0.0, index=pairs); prev_e = pd.Series(0.0, index=ccys)
    for k_ in range(len(sch) - 1):
        d, ex, ex1 = sch.dec[k_], sch['exec'][k_], sch['exec'][k_ + 1]
        i = Xb.index.get_loc(d)
        if i < 65: continue
        if variant in ('a', 'arev'):
            d1w = sch.dec[k_ - 1] if k_ >= 1 else None; d12 = sch.dec[k_ - 12] if k_ >= 12 else None
            if d12 is None: continue
            score = Xb.loc[d1w] - Xb.loc[d12]; sign = 1 if variant == 'a' else -1
        else:
            score = Xb.loc[d] - Xb.loc[sch.dec[k_ - 1]]; sign = -1
        v = vol20.loc[d]
        if score.isna().any() or v.isna().any(): continue
        order = score.sort_values()
        top, bot = list(order.index[-k:]), list(order.index[:k])
        lng, sht = (top, bot) if sign == 1 else (bot, top)
        e = pd.Series(0.0, index=ccys)
        il = 1 / v[lng]; e[lng] = il / il.sum()
        is_ = 1 / v[sht]; e[sht] = -is_ / is_.sum()
        px = X.loc[ex, pairs]
        cf = pd.Series({p: cost_frac(p, px[p]) for p in pairs}) * cost_mult
        if impl == 'D':
            q = pd.Series({USDP[c][0]: USDP[c][1] * e[c] for c in ccys if c != 'USD'})[pairs]
        else:
            avail = [j for j, p in enumerate(CROSS) if not np.isnan(px[p]) and
                     (not warm or ex >= first[p] + pd.DateOffset(months=6))]
            Aa = A[:, avail]; ca = cf.values[avail]
            res = linprog(np.r_[ca, ca], A_eq=np.c_[Aa, -Aa], b_eq=e[CCY_C].values, bounds=(0, None), method='highs')
            if res.x is None:          # exposure not representable (only while a cross is still in warm-up)
                print(f'LP infeasible {impl} {variant} {ex.date()} -> week skipped', flush=True); continue
            qa = res.x[:len(avail)] - res.x[len(avail):]
            q = pd.Series(0.0, index=pairs); q.iloc[avail] = qa
        dq = (q - prev_q).abs()
        cost_p = dq * cf / 2
        r_p = (X.loc[ex1, pairs] / X.loc[ex, pairs] - 1).fillna(0.0)
        gross_p = q * r_p
        xr = Xe.loc[ex1] - Xe.loc[ex]
        de = (e - prev_e).abs(); tot_cost = cost_p.sum()
        ccy_net = e * xr - (de / de.sum() * tot_cost if de.sum() > 0 else 0.0)
        rows.append(dict(dec=d, t=ex1, gross=gross_p.sum(), cost=tot_cost, net=gross_p.sum() - tot_cost,
                         turnover=dq.sum(), **{f'p_{p}': gross_p[p] - cost_p[p] for p in pairs},
                         **{f'c_{c}': ccy_net[c] for c in ccys}, long=','.join(lng), short=','.join(sht),
                         **{f'q_{p}': q[p] for p in pairs}))
        prev_q, prev_e = q, e
    return pd.DataFrame(rows).set_index('t')

JOBS = []
ONLY = sys.argv[1] if len(sys.argv) > 1 else None
for var in ('a', 'b'):                              # reproduction of round 1 (bars, Sunday-open execution)
    for impl in ('D', 'C'): JOBS.append(('rep', var, impl, 1.0, 'd1open', 'bars', False))
for var in ('arev', 'b'):
    for impl in ('D', 'C'):
        for cm in (1.0, 1.5, 2.0):
            JOBS.append(('bars_mon', var, impl, cm, 'mon08', 'bars', False))      # 2012-2024, new execution
            JOBS.append(('full_mon', var, impl, cm, 'mon08', 'bars_full', True))  # 2005-2024, new execution
        JOBS.append(('bars_d1', var, impl, 1.0, 'd1open', 'bars', False))          # 2012-2024 round-1 execution (arev ref)
        JOBS.append(('full_d1', var, impl, 1.0, 'd1open', 'bars_full', True))      # 2005-2024 round-1 execution (reference only)

def job(j):
    tag, var, impl, cm, execm, bars, warm = j
    w = run(impl, var, cm, execm=execm, bars=bars, warm=warm)
    f = os.path.join(OUT, f'r2_xs_{tag}_{var}_{impl}_c{cm}.parquet'); w.to_parquet(f)
    return f'{tag} {var} {impl} c{cm}: N={len(w)} {w.index.min().date()}..{w.index.max().date()} ann net {ann_ret(w.net)*100:.2f}% t {tstat(w.net):.2f}'

if __name__ == '__main__':
    jobs = [j for j in JOBS if ONLY is None or j[0].startswith(ONLY)]
    with Pool(4) as p:
        for s in p.imap(job, jobs): print(s, flush=True)
    # reproduction check vs round-1 files
    for var in ('a', 'b'):
        for impl in ('D', 'C'):
            a = pd.read_parquet(os.path.join(OUT, f'r2_xs_rep_{var}_{impl}_c1.0.parquet'))
            b = pd.read_parquet(os.path.join(OUT, f'r1_h1{var}_{impl}_c1.0.parquet'))
            same = a.index.equals(b.index) and np.allclose(a.net.values, b.net.values, atol=1e-13, rtol=0)
            print(f'REPRO r1 h1{var} {impl}: identical={same} max|diff|={np.abs(a.net.values - b.net.values).max() if a.index.equals(b.index) else "index differs"}')
