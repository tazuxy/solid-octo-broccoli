"""Round 7 library v2: per-bar condition table for H1 and H4 (+ sparse M15 table for the T family).
All conditions use closed bars only (value at bar i uses data up to and including bar i's close; swing points are
confirmed only after their 2 right-hand bars closed). Entry = open of bar i+1 (bars must be contiguous).
Condition columns are int8 orientations (+1 bullish / -1 bearish / 0 none); 'follow' trades the orientation.
ROLLOVER VALIDITY RULE (added after library v1 exposed a bid-only artifact): no entry or exit price is taken at a bar that
opens in [16:55, 17:30) EST; such entry/exit stamps move to the next bar outside the window, and those bars' high/low are
ignored for TP/SL checks.
Outcomes (long side for holds; both sides for brackets):
  h4/h12/h24 = exit at the open of bar i+1+H;  br = bracket TP 1.5 ATR14(tf), SL 1 ATR14(tf), 24-bar time stop
  T family only: tb = SL pullback extreme -/+ 0.25 ATR, TP 2 x risk, 48-bar time stop; tt = TP at the trend high/low, same SL."""
import os, sys, warnings, numpy as np, pandas as pd
warnings.filterwarnings("ignore")
from collections import deque
from numpy.lib.stride_tricks import sliding_window_view as swv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r7_lib as L
from bt import PIP
from sig import atr, rsi, bbands

TFD = {'M15': pd.Timedelta('15min'), 'H1': pd.Timedelta('1h'), 'H4': pd.Timedelta('4h'), 'D1': pd.Timedelta('1D')}
ZONES_H1 = ['PDH', 'PDL', 'PWH', 'PWL', 'ASH', 'ASL', 'PP', 'R1', 'S1', 'SWH', 'SWL']
ZONES_H4 = ['PDH', 'PDL', 'PWH', 'PWL', 'PP', 'R1', 'S1', 'SWH', 'SWL']
ZEV = ['at', 'rej', 'brk', 'ret']
CANDLES = ['C_pin', 'C_engulf', 'C_inside', 'C_outside', 'C_doji', 'C_maru', 'C_3bar']
IND = ['I_rsi_lt30', 'I_rsi_30_50', 'I_rsi_50_70', 'I_rsi_gt70', 'I_stoch', 'I_macdx', 'I_macdh', 'I_emax', 'I_ema200',
       'I_bb_above', 'I_bb_uh', 'I_bb_lh', 'I_bb_below', 'I_bbsq', 'I_adx_gt25', 'I_adx_lt20', 'I_cci', 'I_cloud', 'I_tk', 'I_psar']
TCOLS = [f'T_{v}_{c}' for v in ('a', 'b') for c in ('dh4', 'dd1', 'e4', 'any')]
DCOLS_H4 = ['D_h4_cont', 'D_h4_choch', 'D_h4_pb', 'D_d1_cont', 'D_d1_choch', 'D_d1_pb']

def ema(x, n): return pd.Series(x).ewm(span=n, adjust=False).mean().to_numpy(copy=True)
def i8(x): return np.nan_to_num(np.asarray(x, float)).astype(np.int8)
def roll_mask(t):
    m = t.hour * 60 + t.minute; return np.asarray((m >= 16 * 60 + 55) & (m < 17 * 60 + 30))

def fractals(h, l):
    n = len(h); fh = np.zeros(n, bool); fl = np.zeros(n, bool)
    if n > 5:
        fh[2:-2] = (h[2:-2] > h[1:-3]) & (h[2:-2] > h[:-4]) & (h[2:-2] >= h[3:-1]) & (h[2:-2] >= h[4:])
        fl[2:-2] = (l[2:-2] < l[1:-3]) & (l[2:-2] < l[:-4]) & (l[2:-2] <= l[3:-1]) & (l[2:-2] <= l[4:])
    return fh, fl

# ---------------- indicators ----------------
def adx_di(h, l, c, n=14):
    up = np.diff(h, prepend=np.nan); dn = -np.diff(l, prepend=np.nan)
    pdm = np.where((up > dn) & (up > 0), up, 0.0); mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    pc = np.roll(c, 1); pc[0] = c[0]; tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    a = 1.0 / n
    def rma(x): return pd.Series(x).ewm(alpha=a, adjust=False).mean().values
    at = rma(tr); pdi = 100 * rma(pdm) / at; mdi = 100 * rma(mdm) / at
    dx = 100 * np.abs(pdi - mdi) / np.where(pdi + mdi == 0, np.nan, pdi + mdi)
    adx = pd.Series(dx).ewm(alpha=a, adjust=False).mean().to_numpy(copy=True); adx[:2 * n] = np.nan
    return adx, pdi, mdi

def psar(h, l, step=0.02, mx=0.2):
    n = len(h); flip = np.zeros(n, np.int8)
    if n < 3: return flip
    up = True; af = step; ep = h[0]; sar = l[0]
    for i in range(1, n):
        sar = sar + af * (ep - sar)
        if up:
            sar = min(sar, l[i - 1], l[i - 2] if i > 1 else l[i - 1])
            if l[i] < sar: up = False; sar = ep; ep = l[i]; af = step; flip[i] = -1
            elif h[i] > ep: ep = h[i]; af = min(af + step, mx)
        else:
            sar = max(sar, h[i - 1], h[i - 2] if i > 1 else h[i - 1])
            if h[i] > sar: up = True; sar = ep; ep = h[i]; af = step; flip[i] = 1
            elif l[i] < ep: ep = l[i]; af = min(af + step, mx)
    return flip

def cross(a, b):
    ap, bp = np.roll(a, 1), np.roll(b, 1)
    s = np.where((ap <= bp) & (a > b), 1, np.where((ap >= bp) & (a < b), -1, 0)); s[0] = 0
    return s

def indicators(o, h, l, c, full=True):
    out = {}; n = len(c)
    r = rsi(c, 14); out['rsi'] = r
    out['I_rsi_lt30'] = i8(np.where(r < 30, -1, 0)); out['I_rsi_30_50'] = i8(np.where((r >= 30) & (r < 50), -1, 0))
    out['I_rsi_50_70'] = i8(np.where((r >= 50) & (r <= 70), 1, 0)); out['I_rsi_gt70'] = i8(np.where(r > 70, 1, 0))
    LL = pd.Series(l).rolling(14).min().values; HH = pd.Series(h).rolling(14).max().values
    fk = 100 * (c - LL) / np.where(HH - LL == 0, np.nan, HH - LL)
    K = pd.Series(fk).rolling(3).mean().values; Dd = pd.Series(K).rolling(3).mean().values
    x = cross(K, Dd); out['stochK'] = K
    out['I_stoch'] = i8(np.where((x == 1) & (K < 20) & (Dd < 20), 1, np.where((x == -1) & (K > 80) & (Dd > 80), -1, 0)))
    m = ema(c, 12) - ema(c, 26); sg = ema(m, 9); hist = m - sg
    out['I_macdx'] = i8(cross(m, sg)); out['I_macdh'] = i8(np.sign(hist)); out['macd_hist'] = hist
    e20, e50, e200 = ema(c, 20), ema(c, 50), ema(c, 200); e200[:200] = np.nan
    out['I_emax'] = i8(cross(e20, e50)); out['I_ema200'] = i8(np.sign(c - e200))
    mid, up, lo, _ = bbands(c, 20, 2.0)
    out['I_bb_above'] = i8(np.where(c > up, 1, 0)); out['I_bb_uh'] = i8(np.where((c > mid) & (c <= up), 1, 0))
    out['I_bb_lh'] = i8(np.where((c < mid) & (c >= lo), -1, 0)); out['I_bb_below'] = i8(np.where(c < lo, -1, 0))
    if not full: return out
    bw = pd.Series((up - lo) / mid); pr = bw.rolling(250, min_periods=200).rank(pct=True).values
    out['I_bbsq'] = i8(np.where(pr <= 0.10, np.sign(c - mid), 0))
    adx, pdi, mdi = adx_di(h, l, c, 14); ds = np.sign(pdi - mdi)
    out['I_adx_gt25'] = i8(np.where(adx > 25, ds, 0)); out['I_adx_lt20'] = i8(np.where(adx < 20, ds, 0))
    tp = (h + l + c) / 3; s = pd.Series(tp); sma = s.rolling(20).mean().values
    mad = s.rolling(20).apply(lambda v: np.abs(v - v.mean()).mean(), raw=True).values
    cci = (tp - sma) / (0.015 * np.where(mad == 0, np.nan, mad))
    out['I_cci'] = i8(np.where(cci > 100, 1, np.where(cci < -100, -1, 0)))
    def hl(nn): return (pd.Series(h).rolling(nn).max().values + pd.Series(l).rolling(nn).min().values) / 2
    ten, kij, sb = hl(9), hl(26), hl(52); sa = (ten + kij) / 2
    A = np.roll(sa, 26); B = np.roll(sb, 26); A[:26] = np.nan; B[:26] = np.nan
    top, bot = np.fmax(A, B), np.fmin(A, B)
    out['I_cloud'] = i8(np.where(c > top, 1, np.where(c < bot, -1, 0))); out['I_tk'] = i8(cross(ten, kij))
    out['I_psar'] = psar(h, l)
    return out

def candles(o, h, l, c):
    out = {}; body = np.abs(c - o); rng = h - l; rng0 = np.where(rng <= 0, np.nan, rng)
    uw = h - np.maximum(o, c); lw = np.minimum(o, c) - l
    bull = (lw >= 2 * body) & (np.minimum(o, c) >= l + 2 * rng0 / 3); bear = (uw >= 2 * body) & (np.maximum(o, c) <= l + rng0 / 3)
    out['C_pin'] = i8(np.where(bull & ~bear, 1, np.where(bear & ~bull, -1, 0)))
    po, pc_ = np.roll(o, 1), np.roll(c, 1); ph, pl = np.roll(h, 1), np.roll(l, 1)
    eb = (c > o) & (pc_ < po) & (o <= pc_) & (c >= po) & (body > np.abs(pc_ - po))
    es = (c < o) & (pc_ > po) & (o >= pc_) & (c <= po) & (body > np.abs(pc_ - po))
    e = np.where(eb, 1, np.where(es, -1, 0)); e[0] = 0; out['C_engulf'] = i8(e)
    ins = (h < ph) & (l > pl); ins[0] = False; out['C_inside'] = i8(np.where(ins, np.sign(c - o), 0))
    ous = (h > ph) & (l < pl); ous[0] = False; out['C_outside'] = i8(np.where(ous, np.sign(c - o), 0))
    out['C_doji'] = i8(np.where(body <= 0.1 * rng0, np.sign(c - (h + l) / 2), 0))
    out['C_maru'] = i8(np.where(body >= 0.8 * rng0, np.sign(c - o), 0))
    o2, c2, l2, h2 = np.roll(o, 2), np.roll(c, 2), np.roll(l, 2), np.roll(h, 2)
    b3 = (c2 < o2) & (pl < l2) & (c > ph) & (c > o); s3 = (c2 > o2) & (ph > h2) & (c < pl) & (c < o)
    t3 = np.where(b3, 1, np.where(s3, -1, 0)); t3[:2] = 0; out['C_3bar'] = i8(t3)
    return out

# ---------------- zones ----------------
def swing_level(p, fr, c, a, low=False):
    n = len(c); out = np.full(n, np.nan); dq = deque()
    for i in range(n):
        k = i - 2
        if k >= 0 and fr[k]: dq.append((k, p[k]))
        while dq and dq[0][0] < i - 100: dq.popleft()
        if len(dq) >= 2 and np.isfinite(a[i]):
            arr = np.fromiter((x[1] for x in dq), float, len(dq))
            d = np.abs(arr[:, None] - arr[None, :]); np.fill_diagonal(d, np.inf)
            cl = (d <= 0.25 * a[i]).any(1)
            if cl.any():
                lv = arr[cl]; out[i] = lv[np.argmin(np.abs(lv - c[i]))]
    return out

def zone_events(Lv, h, l, c, a, only_at=False):
    cp = np.roll(c, 1); cp[0] = np.nan
    sp = np.nan_to_num(np.sign(cp - Lv)); sc = np.nan_to_num(np.sign(c - Lv))
    near = np.abs(c - Lv) <= 0.25 * a
    at = np.where(near, np.where(sp != 0, sp, sc), 0)
    if only_at: return {'at': i8(at)}
    rej = np.where((l <= Lv) & (h >= Lv) & (sc == sp) & (sp != 0), sp, 0)
    brk = np.where((sp != 0) & ((c - Lv) * (-sp) >= 0.25 * a), -sp, 0)
    ret = np.zeros(len(c)); last = None
    for i in range(len(c)):
        if last is not None:
            s, Lb, j = last
            if i - j > 24: last = None
            elif s > 0 and l[i] <= Lb + 0.25 * a[i] and c[i] > Lb: ret[i] = 1; last = None
            elif s < 0 and h[i] >= Lb - 0.25 * a[i] and c[i] < Lb: ret[i] = -1; last = None
            elif (s > 0 and c[i] < Lb - 0.25 * a[i]) or (s < 0 and c[i] > Lb + 0.25 * a[i]): last = None
        if brk[i] != 0: last = (brk[i], Lv[i], i)
    return {'at': i8(at), 'rej': i8(rej), 'brk': i8(brk), 'ret': i8(ret)}

def day_week_levels(inst, end):
    d1 = L.load(inst, 'D1', end)
    f = pd.DataFrame({'close_time': d1.index + pd.Timedelta('1D'), 'PDH': d1.high.values, 'PDL': d1.low.values})
    pp = (d1.high.values + d1.low.values + d1.close.values) / 3
    f['PP'] = pp; f['R1'] = 2 * pp - d1.low.values; f['S1'] = 2 * pp - d1.high.values
    wk = f.close_time.dt.to_period('W-SAT')
    w = f.groupby(wk).agg(avail=('close_time', 'max'), PWH=('PDH', 'max'), PWL=('PDL', 'min')).reset_index(drop=True)
    return f.sort_values('close_time'), w.sort_values('avail')

def asia_levels(inst, end):
    h1 = L.load(inst, 'H1', end); hr = h1.index.hour
    m = (hr >= 19) | (hr < 2); fxd = (h1.index + pd.Timedelta('7h')).normalize()
    A = pd.DataFrame({'d': fxd[m], 'h': h1.high.values[m], 'l': h1.low.values[m]}).groupby('d').agg(ASH=('h', 'max'), ASL=('l', 'min'), n=('h', 'size'))
    A = A[A.n >= 4].reset_index(); A['avail'] = A.d + pd.Timedelta('2h')
    return A[['avail', 'ASH', 'ASL']].sort_values('avail')

def asof_cols(ct, frame, key, cols, exact=True):
    x = pd.DataFrame({'ct': ct}); m = pd.merge_asof(x, frame, left_on='ct', right_on=key, direction='backward', allow_exact_matches=exact)
    return {c: m[c].values for c in cols}

# ---------------- Dow structure ----------------
def dow(h, l, c, a):
    n = len(c); fh, fl = fractals(h, l); st = np.zeros(n, np.int8)
    cont = np.zeros(n, np.int8); choch = np.zeros(n, np.int8); pb = np.zeros(n, np.int8); SH = []; SL = []; used = None
    for i in range(n):
        k = i - 2
        if k >= 2:
            if fh[k]:
                SH.append(h[k])
                if len(SH) >= 3 and SH[-1] < SH[-2] and SH[-2] > SH[-3]: choch[i] = -1
            if fl[k]:
                SL.append(l[k])
                if len(SL) >= 3 and SL[-1] > SL[-2] and SL[-2] < SL[-3]: choch[i] = 1
        s = 0
        if len(SH) >= 2 and len(SL) >= 2:
            if SH[-1] > SH[-2] and SL[-1] > SL[-2]: s = 1
            elif SH[-1] < SH[-2] and SL[-1] < SL[-2]: s = -1
        st[i] = s
        if i == 0 or not np.isfinite(a[i]): continue
        if s == 1:
            if c[i] > SH[-1] and c[i - 1] <= SH[-1]: cont[i] = 1
            if l[i] <= SL[-1] + 0.25 * a[i] and c[i] > SL[-1] and used != ('L', len(SL)): pb[i] = 1; used = ('L', len(SL))
        elif s == -1:
            if c[i] < SL[-1] and c[i - 1] >= SL[-1]: cont[i] = -1
            if h[i] >= SH[-1] - 0.25 * a[i] and c[i] < SH[-1] and used != ('H', len(SH)): pb[i] = -1; used = ('H', len(SH))
    return st, cont, choch, pb

def dow_frame(inst, tf, end):
    b = L.load(inst, tf, end); h, l, c = b.high.values, b.low.values, b.close.values; a = atr(h, l, c, 14)
    st, cont, choch, pb = dow(h, l, c, a)
    e200 = ema(c, 200); e200[:200] = np.nan
    return pd.DataFrame({'close_time': b.index + TFD[tf], 'state': st, 'cont': cont, 'choch': choch, 'pb': pb,
                         'e200': i8(np.sign(c - e200))}).sort_values('close_time')

# ---------------- counter-trendline (T family) ----------------
def tline(h, l, c, a):
    """returns orient (+1 up-context line break, -1 down), three-touch flag, SL level, trend-extreme target."""
    n = len(c); fh, fl = fractals(h, l)
    ori = np.zeros(n, np.int8); tt3 = np.zeros(n, bool); slv = np.full(n, np.nan); tgt = np.full(n, np.nan)
    def side(sgn):
        # sgn=+1: up context (swing highs descending after the trend high); sgn=-1 mirror on negated prices
        H = h if sgn > 0 else -l; Lw = l if sgn > 0 else -h; C = c if sgn > 0 else -c
        frH = fh if sgn > 0 else fl; frL = fl if sgn > 0 else fh
        # TH = most recent HIGHER swing high (higher than the swing high before it); P = swing highs formed after it
        TH = None; P = []; lastH = None; pl = np.inf; used = None
        for i in range(n):
            k = i - 2
            if k >= 0 and frH[k]:
                if lastH is not None and H[k] > lastH:
                    TH = (k, H[k]); P = []; pl = Lw[k:i + 1].min()
                elif TH is not None: P.append((k, H[k]))
                lastH = H[k]
            if TH is not None: pl = min(pl, Lw[i])
            if TH is None or len(P) < 2 or not np.isfinite(a[i]) or i == 0: continue
            (k1, p1), (k2, p2) = P[-2], P[-1]
            if not (p2 < p1) or i - k2 > 30 or used == (k1, k2): continue
            sl_ = (p2 - p1) / (k2 - k1); li = p2 + sl_ * (i - k2); lp = p2 + sl_ * (i - 1 - k2)
            # 'pullback not invalidated' read literally: the close is still above the pullback's lowest low
            if C[i] > li + 0.1 * a[i] and C[i - 1] <= lp + 0.1 * a[i - 1] and C[i] > pl:
                used = (k1, k2)
                if ori[i] != 0: continue
                ori[i] = sgn
                if len(P) >= 3:
                    k0, p0 = P[-3]; tt3[i] = abs(p0 - (p2 + sl_ * (k0 - k2))) <= 0.1 * a[i]
                slv[i] = sgn * (pl - 0.25 * a[i]); tgt[i] = sgn * TH[1]
    side(1); side(-1)
    return ori, tt3, slv, tgt

# ---------------- outcomes ----------------
def next_ok(rm):
    """nxt[j] = first index >= j that is not a rollover bar."""
    n = len(rm); nxt = np.full(n + 1, n, np.int64)
    for j in range(n - 1, -1, -1): nxt[j] = j if not rm[j] else nxt[j + 1]
    return nxt

def bracket(o, h, l, ei, e, sl, tp, side, W, rm, nxt):
    """vectorised bracket: path bars ei..ei+W-1 (rollover bars ignored), SL first if both in one bar, gap -> open.
    returns exit price and exit bar index (time stop -> open of the first valid bar at/after ei+W)."""
    n = len(o); N = len(ei); px = np.full(N, np.nan); xi = np.full(N, -1, np.int64)
    ok = ei + W < n
    if not ok.any(): return px, xi
    idx = np.where(ok)[0]; E = ei[idx]
    Hm = swv(h, W)[E]; Lm = swv(l, W)[E]; Om = swv(o, W)[E]; Rm = swv(rm, W)[E]
    s = side[idx][:, None]; SL = sl[idx][:, None]; TP = tp[idx][:, None]
    hs = np.where(s > 0, Lm <= SL, Hm >= SL) & ~Rm; ht = np.where(s > 0, Hm >= TP, Lm <= TP) & ~Rm
    any_ = hs | ht; j = np.argmax(any_, axis=1); hit = any_[np.arange(len(idx)), j]
    oj = Om[np.arange(len(idx)), j]; slv = SL[:, 0]; tpv = TP[:, 0]; sv = s[:, 0]
    gap_sl = (j > 0) & np.where(sv > 0, oj <= slv, oj >= slv); gap_tp = (j > 0) & np.where(sv > 0, oj >= tpv, oj <= tpv)
    hsj = hs[np.arange(len(idx)), j]
    p = np.where(gap_sl, oj, np.where(gap_tp, oj, np.where(hsj, slv, tpv)))
    ts = nxt[np.minimum(E + W, n)]; tsok = ts < n
    p = np.where(hit, p, np.where(tsok, o[np.minimum(ts, n - 1)], np.nan))
    x = np.where(hit, E + j, np.where(tsok, ts, -1))
    px[idx] = p; xi[idx] = x
    return px, xi

def build_tf(inst, tf, end, ctx):
    """ctx: dict with dow H4/D1 frames and EMA200 H4 (used as context columns)."""
    pip = PIP[inst]; b = L.load(inst, tf, end); t = b.index; n = len(t)
    o, h, l, c = (b[k].values.astype(float) for k in ('open', 'high', 'low', 'close'))
    a = atr(h, l, c, 14); ct = t + TFD[tf]
    cols = {}
    full = tf in ('H1', 'H4')
    if full:
        cols.update(candles(o, h, l, c))
    ind = indicators(o, h, l, c, full=full)
    cols.update({k: v for k, v in ind.items() if k.startswith('I_')})
    # attribute columns for combinations
    r = ind['rsi']
    cols['a_rsiz'] = i8(np.select([r < 30, r < 50, r <= 70, r > 70], [0, 1, 2, 3], -1))
    cols['a_rsi50'] = i8(np.where(r > 50, 1, np.where(r < 50, -1, 0)))
    K = ind['stochK']; cols['a_stz'] = i8(np.where(K < 20, -1, np.where(K > 80, 1, 0)))
    hist = ind['macd_hist']; cols['a_macdh'] = i8(np.sign(hist)); cols['a_macdt'] = i8(np.sign(hist - np.roll(hist, 1)))
    cols['a_e200'] = cols['I_ema200']
    for nm, fr in (('dh4', ctx['H4']), ('dd1', ctx['D1'])):
        m = asof_cols(ct, fr, 'close_time', ['state', 'e200']); cols[f'a_{nm}'] = i8(m['state'])
        if nm == 'dh4': cols['a_e4'] = i8(m['e200'])
    # zones
    D, W = day_week_levels(inst, end); lv = asof_cols(ct, D, 'close_time', ['PDH', 'PDL', 'PP', 'R1', 'S1'], exact=False)
    lv.update(asof_cols(ct, W, 'avail', ['PWH', 'PWL'], exact=False))
    zones = ZONES_H4 if tf == 'H4' else ZONES_H1
    if tf != 'H4': lv.update(asof_cols(ct, asia_levels(inst, end), 'avail', ['ASH', 'ASL'], exact=False))
    fh, fl = fractals(h, l)
    lv['SWH'] = swing_level(h, fh, c, a); lv['SWL'] = swing_level(l, fl, c, a, low=True)
    for z in zones:
        ev = zone_events(lv[z], h, l, c, a, only_at=not full)
        for e_, v in ev.items(): cols[f'Z_{z}_{e_}'] = v
    # Dow events (H4 table: own H4 events + D1 events mapped forward to the first H4 bar closing at/after the D1 close)
    if tf == 'H4':
        st, cont, choch, pb = dow(h, l, c, a)
        cols['D_h4_cont'], cols['D_h4_choch'], cols['D_h4_pb'] = cont, choch, pb
        d1 = ctx['D1']; ev = d1[(d1.cont != 0) | (d1.choch != 0) | (d1.pb != 0)]
        pos = np.searchsorted(ct.values, ev.close_time.values)
        for nm in ('cont', 'choch', 'pb'):
            arr = np.zeros(n, np.int8); ok = pos < n; arr[pos[ok]] = ev[nm].values[ok]; cols[f'D_d1_{nm}'] = arr
    # T family (H1 and M15)
    if tf in ('H1', 'M15'):
        ori, t3, slv, tgt = tline(h, l, c, a)
        cx = {'dh4': cols['a_dh4'], 'dd1': cols['a_dd1'], 'e4': cols['a_e4']}
        cx['any'] = np.where((cx['dh4'] == ori) | (cx['dd1'] == ori) | (cx['e4'] == ori), ori, 0)
        for v in ('a', 'b'):
            base = ori if v == 'a' else np.where(t3, ori, 0)
            for cn in ('dh4', 'dd1', 'e4', 'any'):
                cols[f'T_{v}_{cn}'] = i8(np.where((base != 0) & (cx[cn] == base), base, 0))
    # ---------- outcomes ----------
    rm = roll_mask(t) if tf != 'H4' else np.zeros(n, bool)
    nxt = next_ok(rm)
    contig = np.zeros(n, bool); contig[:-1] = (t[1:] - t[:-1]) == TFD[tf]
    ei = nxt[np.minimum(np.arange(n) + 1, n)]; valid = contig & (ei < n)
    eic = np.minimum(ei, n - 1); e = o[eic]
    out = pd.DataFrame({'t_sig': t, 't_ent': t[eic], 'px': e})
    for H in (4, 12, 24):
        xi = nxt[np.minimum(np.arange(n) + 1 + H, n)]; okx = valid & (xi < n)
        out[f'g_h{H}'] = np.where(okx, (o[np.minimum(xi, n - 1)] - e) / pip, np.nan).astype(np.float32)
        out[f'x_h{H}'] = np.where(okx, t[np.minimum(xi, n - 1)].values, np.datetime64('NaT'))
    if tf == 'M15':
        anyT0 = np.zeros(n, bool)
        for cname in TCOLS: anyT0 |= cols[cname] != 0
        sel = np.where(anyT0)[0]
    else: sel = np.arange(n)
    for s, nm in ((1, 'L'), (-1, 'S')):
        side = np.full(len(sel), s); sl = e[sel] - s * a[sel]; tp = e[sel] + s * 1.5 * a[sel]
        p, xi = bracket(o, h, l, eic[sel], e[sel], sl, tp, side, 24, rm, nxt); okx = valid[sel] & (xi >= 0)
        g = np.full(n, np.nan, np.float32); g[sel] = np.where(okx, s * (p - e[sel]) / pip, np.nan)
        x = np.full(n, np.datetime64('NaT'), 'datetime64[ns]')
        x[sel] = np.where(okx, t[np.clip(xi, 0, n - 1)].values + np.timedelta64(int(TFD[tf].total_seconds()), 's'), np.datetime64('NaT'))
        out[f'g_br{nm}'] = g; out[f'x_br{nm}'] = x
    out['k_br'] = (a / pip).astype(np.float32)          # bracket SL distance in pips (converted to R later)
    if tf in ('H1', 'M15'):
        anyT = np.zeros(n, bool)
        for cname in TCOLS: anyT |= cols[cname] != 0
        tsig = np.where(anyT)[0]
        for nm in ('tbF', 'tbX', 'ttF', 'ttX'):
            out[f'g_{nm}'] = np.full(n, np.nan, np.float32); out[f'x_{nm}'] = np.full(n, np.datetime64('NaT'), 'datetime64[ns]')
        out['k_tb'] = np.full(n, np.nan, np.float32); out['k_tt'] = np.full(n, np.nan, np.float32)
        if len(tsig):
            s_ = ori[tsig].astype(float); E = e[tsig]; risk = np.abs(E - slv[tsig]); eiT = eic[tsig]
            okr = (risk > 0) & np.isfinite(risk)
            for kind in ('tb', 'tt'):
                if kind == 'tb': dist_tp = 2 * risk
                else: dist_tp = np.where(s_ * (tgt[tsig] - E) > 0, np.abs(tgt[tsig] - E), np.nan)
                for fx, sgn in (('F', 1.0), ('X', -1.0)):
                    side = sgn * s_; slp = E - side * risk; tpp = E + side * dist_tp
                    p, xi = bracket(o, h, l, eiT, E, slp, tpp, side.astype(int), 48, rm, nxt)
                    okx = valid[tsig] & (xi >= 0) & okr & np.isfinite(dist_tp)
                    g = np.where(okx, side * (p - E) / pip, np.nan)
                    out.loc[tsig, f'g_{kind}{fx}'] = g.astype(np.float32)
                    xt = np.where(okx, t[np.clip(xi, 0, n - 1)].values + np.timedelta64(int(TFD[tf].total_seconds()), 's'), np.datetime64('NaT'))
                    out.loc[tsig, f'x_{kind}{fx}'] = xt
                out.loc[tsig, f'k_{kind}'] = np.where(okr, risk / pip, np.nan).astype(np.float32)
    for k_, v in cols.items(): out[k_] = v
    out = out[valid].copy()
    # R and month
    d1 = L.d1_frame(inst, end)[['close_time', 'atr']]
    m = pd.merge_asof(out[['t_ent']].reset_index(), d1, left_on='t_ent', right_on='close_time', direction='backward').set_index('index')
    out['R'] = (0.25 * m['atr'] / pip).astype(np.float32)
    out = out[out.R > 0]
    out['month'] = (out.t_ent.dt.year * 100 + out.t_ent.dt.month).astype(np.int32)
    out['inst'] = inst; out['tf'] = tf
    if tf == 'M15':
        tc = [cn for cn in TCOLS]; out = out[(out[tc] != 0).any(axis=1)]
        keep = [k for k in out.columns if not k.startswith('I_') or k in ('I_ema200',)]
        out = out[keep]
    return out.reset_index(drop=True)

def build_inst(inst, end):
    ctx = {'H4': dow_frame(inst, 'H4', end), 'D1': dow_frame(inst, 'D1', end)}
    return {tf: build_tf(inst, tf, end, ctx) for tf in ('H1', 'H4', 'M15')}

def pool_tables(inst):
    fps = {tf: os.path.join(L.CACHE, f'v2_{inst}_{tf}_pool.parquet') for tf in ('H1', 'H4', 'M15')}
    if all(os.path.exists(f) for f in fps.values()): return {tf: pd.read_parquet(f) for tf, f in fps.items()}
    T = build_inst(inst, L.POOL_END)
    for tf, df in T.items(): df.to_parquet(fps[tf])
    return T

if __name__ == '__main__':
    import time
    for inst in sys.argv[1:]:
        t0 = time.time(); T = pool_tables(inst)
        print(inst, {k: len(v) for k, v in T.items()}, round(time.time() - t0, 1), flush=True)
