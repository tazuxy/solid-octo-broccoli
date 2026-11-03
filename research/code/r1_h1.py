"""H1: cross-sectional currency momentum (a) and 1-week reversal (b).
Implementation D: 8 currencies, traded with the 7 USD pairs (no XAU).  Implementation C: 7 non-USD currencies,
ranked from crosses only (JPY anchor) and traded with the 10 crosses (min-cost LP decomposition of the exposure).
Weights: long side and short side each gross 1 (dollar-neutral), inverse 20-day vol of the currency-vs-basket
return within each side.  Decision at Friday close, execution at next D1 open, hold 1 week."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_common import *
from scipy.optimize import linprog

CCY_D = ['USD','EUR','GBP','JPY','AUD','CAD','CHF','NZD']
CCY_C = ['EUR','GBP','JPY','AUD','CAD','CHF','NZD']
USDP = {'EUR':('EURUSD',1),'GBP':('GBPUSD',1),'AUD':('AUDUSD',1),'NZD':('NZDUSD',1),
        'JPY':('USDJPY',-1),'CAD':('USDCAD',-1),'CHF':('USDCHF',-1)}

def ccy_logidx(P, impl):
    """log value of each currency vs the anchor (USD for D, JPY for C), from a price panel P."""
    L = np.log(P)
    if impl == 'D':
        out = {'USD': pd.Series(0.0, index=P.index)}
        for c, (p, s) in USDP.items(): out[c] = s * L[p]
        return pd.DataFrame(out)[CCY_D]
    aud = L['AUDJPY'].where(L['AUDJPY'].notna(), L['EURJPY'] - L['EURAUD'])
    out = {'JPY': pd.Series(0.0, index=P.index), 'EUR': L['EURJPY'], 'GBP': L['GBPJPY'], 'AUD': aud,
           'CAD': L['CADJPY'], 'NZD': L['NZDJPY'], 'CHF': L['EURJPY'] - L['EURCHF']}
    return pd.DataFrame(out)[CCY_C]

def run(impl, variant, cost_mult=1.0, k=2):
    C, Cf, X = panels()
    ccys = CCY_D if impl == 'D' else CCY_C
    pairs = [USDP[c][0] for c in CCY_D if c != 'USD'] if impl == 'D' else CROSS
    Lc = ccy_logidx(Cf, impl)                 # close-based (signals)
    Lx = ccy_logidx(X.ffill(), impl)          # exec-price based (attribution)
    Xb = Lc.sub(Lc.mean(axis=1), axis=0)      # vs equal-weight basket (log index)
    Xe = Lx.sub(Lx.mean(axis=1), axis=0)
    vol20 = Xb.diff().rolling(20).std()
    sch = weekly_schedule(C.index)
    # incidence matrix for crosses
    A = np.array([[1 if p[:3] == c else (-1 if p[3:] == c else 0) for p in CROSS] for c in CCY_C], float)
    rows = []; prev_q = pd.Series(0.0, index=pairs); prev_e = pd.Series(0.0, index=ccys)
    for k_ in range(len(sch) - 1):
        d, ex, ex1 = sch.dec[k_], sch['exec'][k_], sch['exec'][k_ + 1]
        i = Xb.index.get_loc(d)
        if i < 65: continue
        if variant == 'a':      # 12-week momentum skipping the last week: I(t-1w) - I(t-12w)
            d1w = sch.dec[k_ - 1] if k_ >= 1 else None; d12 = sch.dec[k_ - 12] if k_ >= 12 else None
            if d12 is None: continue
            score = Xb.loc[d1w] - Xb.loc[d12]; sign = 1
        else:                   # 1-week reversal
            score = Xb.loc[d] - Xb.loc[sch.dec[k_ - 1]]; sign = -1
        v = vol20.loc[d]
        if score.isna().any() or v.isna().any(): continue
        order = score.sort_values()
        top, bot = list(order.index[-k:]), list(order.index[:k])
        lng, sht = (top, bot) if sign == 1 else (bot, top)
        e = pd.Series(0.0, index=ccys)
        il = 1 / v[lng]; e[lng] = il / il.sum()
        is_ = 1 / v[sht]; e[sht] = -is_ / is_.sum()
        # pair positions
        px = X.loc[ex, pairs]
        cf = pd.Series({p: cost_frac(p, px[p]) for p in pairs}) * cost_mult
        if impl == 'D':
            q = pd.Series({USDP[c][0]: USDP[c][1] * e[c] for c in ccys if c != 'USD'})[pairs]
        else:
            avail = [j for j, p in enumerate(CROSS) if not np.isnan(px[p])]
            Aa = A[:, avail]; ca = cf.values[avail]
            res = linprog(np.r_[ca, ca], A_eq=np.c_[Aa, -Aa], b_eq=e[CCY_C].values, bounds=(0, None), method='highs')
            qa = res.x[:len(avail)] - res.x[len(avail):]
            q = pd.Series(0.0, index=pairs); q.iloc[avail] = qa
        dq = (q - prev_q).abs()
        cost_p = dq * cf / 2
        r_p = (X.loc[ex1, pairs] / X.loc[ex, pairs] - 1).fillna(0.0)
        gross_p = q * r_p
        # currency attribution (basket space, open-to-open), cost allocated by |de|
        xr = Xe.loc[ex1] - Xe.loc[ex]
        de = (e - prev_e).abs(); tot_cost = cost_p.sum()
        ccy_net = e * xr - (de / de.sum() * tot_cost if de.sum() > 0 else 0.0)
        rows.append(dict(dec=d, t=ex1, gross=gross_p.sum(), cost=tot_cost, net=gross_p.sum() - tot_cost,
                         turnover=dq.sum(), **{f'p_{p}': gross_p[p] - cost_p[p] for p in pairs},
                         **{f'c_{c}': ccy_net[c] for c in ccys}, long=','.join(lng), short=','.join(sht)))
        prev_q, prev_e = q, e
    w = pd.DataFrame(rows).set_index('t')
    return w

if __name__ == '__main__':
    res = {}
    for var in ('a', 'b'):
        for impl in ('D', 'C'):
            for cm in (1.0, 1.5, 2.0):
                w = run(impl, var, cm)
                w.to_parquet(os.path.join(OUT, f'r1_h1{var}_{impl}_c{cm}.parquet'))
                print(var, impl, cm, len(w), 'ann gross %.4f net %.4f t %.2f turnover/wk %.2f' %
                      (ann_ret(w.gross), ann_ret(w.net), tstat(w.net), w.turnover.mean()))
