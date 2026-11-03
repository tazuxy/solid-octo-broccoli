"""H-A: equity-regime-filtered JPY carry (pre-registered, round 3). No tuning.
Signal (decided with SPX D1 closes whose close date < execution date, i.e. up to the previous 17:00 EST close):
  a: risk_on = SPX close > SMA200(SPX close)            b: a AND vol20 < rolling-252 median(vol20)  (vol20 = 20d stdev of
  SPX daily log returns * sqrt(252); median uses min 120 obs during warm-up).  Benchmark 'bh': always long.
Execution: 08:00 EST H1 open on each FX execution date (a date on which all 7 pairs have an 08:00 price; otherwise the
interval simply spans to the next date). Holding return of date d = P08(next)/P08(d) - 1.
Weights: long, inverse-60d-vol (D1 close-to-close log returns, close dates < d), normalised to gross 1 (= 'unscaled'),
weights refreshed on the first execution date of each week. Costs: |dw| * COST_PIPS*PIP/price / 2 per one-way trade.
Output: daily & weekly net returns per (group, variant, cost multiplier)."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r3_common import *
GA = ['AUDJPY', 'NZDJPY', 'CADJPY']; GB = ['EURJPY', 'GBPJPY', 'AUDUSD', 'NZDUSD']
PAIRS = GA + GB

def spx_signals():
    s = idx_d1('SPXUSD').close
    s = s[s.index < END]
    sma = s.rolling(200).mean()
    lr = np.log(s).diff(); vol = lr.rolling(20).std() * np.sqrt(252)
    med = vol.rolling(252, min_periods=120).median()
    a = (s > sma).where(sma.notna())
    b = (a.astype(float) * (vol < med).astype(float)).where(sma.notna() & med.notna())
    return pd.DataFrame({'spx': s, 'sma200': sma, 'vol20': vol, 'volmed': med, 'a': a.astype(float), 'b': b})

def unavailable(pair, days):
    """Data-gap handling (decided after the AUDJPY 2012 hole was found; same spirit as round 2): a pair is unavailable from
    the start of any D1 data gap > 10 calendar days until its 60th D1 bar after the gap (vol re-warm-up).
    Its weight is 0 and the other legs are re-normalised. Only AUDJPY 2012-01..2013-03 is affected."""
    idx = fx_d1(pair).index; idx = idx[idx >= '2010-06-01']
    m = pd.Series(False, index=days)
    gaps = np.where(np.diff(idx.values).astype('timedelta64[D]').astype(int) > 10)[0]
    for g in gaps:
        endpos = min(g + 1 + 60, len(idx) - 1)
        m[(days > idx[g]) & (days <= idx[endpos])] = True
    return m

def exec_panel():
    """08:00 EST prices; execution dates = dates on which every AVAILABLE pair has an 08:00 price."""
    days = pd.bdate_range('2010-11-15', '2024-12-31')
    P = pd.DataFrame({p: price_at(fx_h1(p), days + pd.Timedelta('8h')).values for p in PAIRS}, index=days)
    U = pd.DataFrame({p: unavailable(p, days).values for p in PAIRS}, index=days)
    ok = (P.notna() | U).all(axis=1)
    P = P[ok].where(~U[ok]); U = U[ok]
    P.attrs['unavail'] = U
    return P

def run(group, variant, cmult=1.0, sig=None, P=None, extra_off=None):
    sig = spx_signals() if sig is None else sig; P = exec_panel() if P is None else P
    pairs = GA if group == 'A' else GB
    U = P.attrs['unavail'][pairs].copy(); X = P[pairs].copy(); X.attrs = {}; U.attrs = {}
    # signal at the last SPX close strictly before date d
    if variant == 'bh': on = pd.Series(1.0, index=X.index)
    else:
        sv = sig[variant]; pos = sv.index.searchsorted(X.index, side='left') - 1
        on = pd.Series(np.where(pos >= 0, sv.values[np.clip(pos, 0, None)], np.nan), index=X.index)
    if extra_off is not None: on = on * (1 - extra_off.reindex(X.index).fillna(0))
    # inverse-vol weights, frozen weekly
    vols = {}
    for p in pairs:
        c = fx_d1(p).close; lr = np.log(c).diff(); v = lr.rolling(60).std() * np.sqrt(252)
        pos = v.index.searchsorted(X.index, side='left') - 1
        vols[p] = np.where(pos >= 0, v.values[np.clip(pos, 0, None)], np.nan)
    V = pd.DataFrame(vols, index=X.index)
    wk = X.index.to_period('W-FRI'); first = ~pd.Series(wk).duplicated().values
    Vf = V.where(np.repeat(first[:, None], V.shape[1], axis=1)).ffill()
    iv = (1 / Vf).where(~U, 0.0); W = iv.div(iv.sum(axis=1), axis=0)
    W = W.mul(on, axis=0)
    W = W.where(W.notna().all(axis=1) & on.notna(), np.nan)
    ret = (X.shift(-1) / X - 1).where(~(U | U.shift(-1, fill_value=False)), 0.0)
    cf = pd.DataFrame({p: COST_PIPS[p] * PIP[p] / X[p].ffill() for p in pairs}) * cmult
    Wz = W.fillna(0)
    cost = (Wz.diff().abs().fillna(Wz.abs()) * cf / 2).sum(axis=1)
    gross = (Wz * ret).sum(axis=1)
    net = (gross - cost)
    net = net[(net.index >= START) & ret.notna().all(axis=1)]
    assert len(net) > 3200, len(net)
    exposure = (Wz.abs().sum(axis=1) > 0).reindex(net.index)
    # contributions per pair (net of own costs)
    contrib = (Wz * ret - Wz.diff().abs().fillna(Wz.abs()) * cf / 2).reindex(net.index)
    return net, exposure, contrib, W.reindex(net.index)

def weekly(daily):
    """compound daily -> Mon-Fri weeks, labelled by the last execution date in the week"""
    k = daily.index.to_period('W-FRI'); lab = pd.Series(daily.index, index=daily.index).groupby(k).max()
    w = (1 + daily).groupby(k).prod() - 1
    return w.set_axis(pd.DatetimeIndex(lab.reindex(w.index).values))

if __name__ == '__main__':
    sig = spx_signals(); P = exec_panel()
    print('exec dates', len(P), P.index.min(), P.index.max())
    print('signal coverage: a from', sig.a.first_valid_index(), ' b from', sig.b.first_valid_index())
    sc = sig[(sig.index >= START)]
    print('share risk_on 2011-10..2024: a %.3f  b %.3f' % (sc.a.mean(), sc.b.mean()))
    sig.to_parquet(os.path.join(OUT, 'r3_ha_signals.parquet'))
    rows = {}
    for g in ('A', 'B'):
        for v in ('a', 'b', 'bh'):
            for cm in (1.0, 1.5, 2.0):
                net, ex, con, W = run(g, v, cm, sig, P)
                rows[(g, v, cm)] = net
                if cm == 1.0:
                    con.to_parquet(os.path.join(OUT, f'r3_ha_contrib_{g}_{v}.parquet'))
                    print(g, v, 'days', len(net), 'exposure %.3f' % ex.mean(), 'switches', int((W.fillna(0).abs().sum(axis=1) > 0).astype(int).diff().abs().sum()))
    D = pd.DataFrame({f'{g}_{v}_c{cm}': s for (g, v, cm), s in rows.items()})
    D.to_parquet(os.path.join(OUT, 'r3_ha_daily.parquet'))
    Wk = D.apply(weekly); Wk.to_parquet(os.path.join(OUT, 'r3_ha_weekly.parquet'))
    print(Wk.shape, Wk.index.min(), Wk.index.max())
