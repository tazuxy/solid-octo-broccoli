"""Trade simulation + feature construction for filter analysis."""
import sys, os, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from sig import *

PIP = {'EURUSD':1e-4,'GBPUSD':1e-4,'AUDUSD':1e-4,'NZDUSD':1e-4,'USDCAD':1e-4,'USDCHF':1e-4,'USDJPY':1e-2,'XAUUSD':0.01,
       'EURJPY':1e-2,'GBPJPY':1e-2,'AUDJPY':1e-2,'CADJPY':1e-2,'NZDJPY':1e-2,'EURGBP':1e-4,'EURAUD':1e-4,'EURCHF':1e-4,'AUDNZD':1e-4,'GBPCHF':1e-4}
# round-trip cost (spread + slippage) in pips, conservative retail ECN
COST_PIPS = {'EURUSD':1.0,'GBPUSD':1.5,'USDJPY':1.0,'AUDUSD':1.2,'USDCAD':1.8,'USDCHF':1.8,'NZDUSD':1.8,'XAUUSD':30,
             'EURJPY':1.5,'GBPJPY':2.5,'AUDJPY':1.8,'CADJPY':2.2,'NZDJPY':2.5,'EURGBP':1.3,'EURAUD':2.5,'EURCHF':1.8,'AUDNZD':2.5,'GBPCHF':2.5}
TF_MIN = {'M15':15,'H1':60,'H4':240,'D1':1440}
BUILD_FROM = '2012-01-01'   # first bar returned by build(); round-2 parametrisation (default = rounds 0-1)

def htf_feature(df, pair, tf_hi, fn):
    """Compute features on a higher timeframe and align to df without look-ahead."""
    hi = load(pair, tf_hi, start='2011-06-01')
    feat = fn(hi)  # DataFrame indexed like hi
    feat = feat.copy(); feat['close_time'] = feat.index + pd.Timedelta(minutes=TF_MIN[tf_hi])
    lo = pd.DataFrame({'close_time': df.index + pd.Timedelta(minutes=TF_MIN[df.attrs['tf']])}, index=df.index)
    m = pd.merge_asof(lo.reset_index(), feat.sort_values('close_time'), on='close_time', direction='backward')
    m.index = df.index
    return m.drop(columns=['close_time', 'ts'], errors='ignore')

def h4_feats(hi):
    c = hi['close'].values; h = hi['high'].values; l = hi['low'].values
    out = pd.DataFrame(index=hi.index)
    out['h4_rsi'] = rsi(c, 14)
    a = atr(h, l, c, 14); out['h4_atr'] = a
    sma = pd.Series(c).rolling(50).mean().values
    out['h4_dist50'] = (c - sma) / a            # distance from H4 SMA50 in H4-ATR
    out['h4_slope50'] = (sma - np.roll(sma, 5)) / a
    out['h4_adx'] = adx(h, l, c, 14)
    return out

def d1_feats(hi):
    c = hi['close'].values; h = hi['high'].values; l = hi['low'].values
    out = pd.DataFrame(index=hi.index)
    a = atr(h, l, c, 14); out['d1_atr'] = a
    sma = pd.Series(c).rolling(20).mean().values
    out['d1_dist20'] = (c - sma) / a
    out['d1_rsi'] = rsi(c, 14)
    out['d1_adx'] = adx(h, l, c, 14)
    out['d1_atr_ratio'] = a / pd.Series(a).rolling(60).mean().values
    return out

def adx(h, l, c, n=14):
    up = h - np.roll(h, 1); dn = np.roll(l, 1) - l; up[0] = dn[0] = 0
    pdm = np.where((up > dn) & (up > 0), up, 0.0); ndm = np.where((dn > up) & (dn > 0), dn, 0.0)
    pc = np.roll(c, 1); pc[0] = c[0]
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    def wild(x):
        o = np.full_like(x, np.nan); o[n-1] = x[:n].sum()
        for i in range(n, len(x)): o[i] = o[i-1] - o[i-1]/n + x[i]
        return o
    trs, ps, ns = wild(tr), wild(pdm), wild(ndm)
    pdi = 100 * ps / trs; ndi = 100 * ns / trs
    dx = 100 * abs(pdi - ndi) / (pdi + ndi)
    out = np.full_like(c, np.nan); s = 2*n - 2
    if len(c) > s + 1:
        out[s] = np.nanmean(dx[n-1:s+1])
        for i in range(s+1, len(c)): out[i] = out[i-1] + (dx[i] - out[i-1]) / n
    return out

def build(pair, tf, **sigkw):
    df = add_indicators(load(pair, tf, start='2011-10-01')); df.attrs['tf'] = tf
    o, h, l, c = [df[k].values for k in ('open','high','low','close')]
    a = df['atr'].values; mid = df['mid'].values; bw = df['bw'].values
    df['bw_pct'] = pd.Series(bw).rolling(200).rank(pct=True).values   # band width percentile vs last 200 bars
    df['bw_chg'] = bw / np.roll(bw, 5)
    df['atr_ratio'] = a / pd.Series(a).rolling(200).mean().values
    df['mid_slope'] = (mid - np.roll(mid, 5)) / a
    df['bar_range'] = (h - l) / a
    df['close_pos'] = (c - l) / np.where(h - l > 0, h - l, np.nan)   # 1 = close at high
    df['close_in'] = ((c > df['bb_lo'].values) & (c < df['bb_up'].values)).astype(int)
    df['dist_mid'] = (c - mid) / a
    df['sma200_dist'] = (c - pd.Series(c).rolling(200).mean().values) / a
    df['hour'] = df.index.hour; df['dow'] = df.index.dayofweek
    df['adx'] = adx(h, l, c, 14)
    # consecutive bars outside the band
    outl = (l <= df['bb_lo'].values); outh = (h >= df['bb_up'].values)
    def run_len(x):
        r = np.zeros(len(x), dtype=int)
        for i in range(1, len(x)): r[i] = r[i-1] + 1 if x[i] else 0
        return r
    df['run_lo'] = run_len(outl); df['run_hi'] = run_len(outh)
    buy, sell, tb, ts, jmin, jmax = signals(df, **sigkw)
    df['buy'] = buy; df['sell'] = sell; df['tb'] = tb; df['ts'] = ts
    # divergence "quality": RSI gap and price gap to reference point
    r = df['rsi'].values; n = len(df)
    df['rsi_gap_b'] = np.where(jmin >= 0, r - r[np.clip(jmin, 0, n-1)], np.nan)
    df['rsi_gap_s'] = np.where(jmax >= 0, r[np.clip(jmax, 0, n-1)] - r, np.nan)
    df['ref_rsi_b'] = np.where(jmin >= 0, r[np.clip(jmin, 0, n-1)], np.nan)
    df['ref_rsi_s'] = np.where(jmax >= 0, r[np.clip(jmax, 0, n-1)], np.nan)
    df['ref_dist_b'] = np.where(jmin >= 0, np.arange(n) - jmin, -1)
    df['ref_dist_s'] = np.where(jmax >= 0, np.arange(n) - jmax, -1)
    for tfh, fn in (('H4', h4_feats), ('D1', d1_feats)):
        f = htf_feature(df, pair, tfh, fn)
        for col in f.columns: df[col] = f[col].values
    df['pair'] = pair
    return df[df.index >= BUILD_FROM]

def simulate(df, pair, idx, direction, sl_atr=1.0, tp_mode='mid', tp_atr=1.5, max_bars=32, cost_pips=None,
             allow_overlap=True, be_trigger=None):
    """Enter at next bar open. SL = signal-bar extreme -/+ sl_atr*ATR. TP: 'mid' = midband at signal (fixed),
    'midtrail' = exit when close crosses current midband, 'fixed' = tp_atr*ATR from entry. Time stop at max_bars.
    Returns trades DataFrame; r = (pnl - cost)/risk, risk = entry - SL distance."""
    o, h, l, c, a, mid = [df[k].values for k in ('open','high','low','close','atr','mid')]
    n = len(df); cost = (COST_PIPS[pair] if cost_pips is None else cost_pips) * PIP[pair]
    rows = []; busy_until = -1
    for i, d in zip(idx, direction):
        if i + 1 >= n: continue
        if not allow_overlap and i < busy_until: continue
        ent = o[i+1]
        if d == 1:
            sl = l[i] - sl_atr * a[i]; risk = ent - sl
            tp = mid[i] if tp_mode == 'mid' else ent + tp_atr * a[i]
        else:
            sl = h[i] + sl_atr * a[i]; risk = sl - ent
            tp = mid[i] if tp_mode == 'mid' else ent - tp_atr * a[i]
        if risk <= 0 or np.isnan(risk): continue
        if tp_mode == 'mid' and (d * (tp - ent) <= cost): continue   # target already (almost) reached
        ex = None; exi = None; reason = ''; mfe = 0; mae = 0; slc = sl
        for j in range(i+1, min(n, i+1+max_bars)):
            if d == 1:
                mfe = max(mfe, h[j] - ent); mae = max(mae, ent - l[j])
                if l[j] <= slc: ex, exi, reason = slc, j, 'sl'; break
                if tp_mode == 'midtrail':
                    if c[j] >= mid[j]: ex, exi, reason = c[j], j, 'tp'; break
                elif h[j] >= tp: ex, exi, reason = tp, j, 'tp'; break
                if be_trigger and h[j] - ent >= be_trigger * risk: slc = max(slc, ent)
            else:
                mfe = max(mfe, ent - l[j]); mae = max(mae, h[j] - ent)
                if h[j] >= slc: ex, exi, reason = slc, j, 'sl'; break
                if tp_mode == 'midtrail':
                    if c[j] <= mid[j]: ex, exi, reason = c[j], j, 'tp'; break
                elif l[j] <= tp: ex, exi, reason = tp, j, 'tp'; break
                if be_trigger and ent - l[j] >= be_trigger * risk: slc = min(slc, ent)
        if ex is None:
            exi = min(n-1, i + max_bars); ex = c[exi]; reason = 'time'
        pnl = d * (ex - ent) - cost
        rows.append(dict(i=i, t=df.index[i], dir=d, entry=ent, exit=ex, bars=exi - i, reason=reason,
                         pnl=pnl, r=pnl / risk, risk_atr=risk / a[i], mfe=mfe / risk, mae=mae / risk))
        busy_until = exi + 1
    return pd.DataFrame(rows)

def summary(tr):
    if len(tr) == 0: return dict(N=0)
    g = tr.r[tr.r > 0].sum(); L = -tr.r[tr.r <= 0].sum()
    return dict(N=len(tr), win=(tr.r > 0).mean(), avgR=tr.r.mean(), pf=g / L if L > 0 else np.inf,
                tstat=tr.r.mean() / (tr.r.std() / np.sqrt(len(tr))) if len(tr) > 2 else np.nan,
                tp=(tr.reason == 'tp').mean(), sl=(tr.reason == 'sl').mean())
