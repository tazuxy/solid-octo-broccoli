"""Round 7 edge-discovery loop: shared library.
Clock: histdata fixed EST (UTC-5, no DST); JST = EST + 14h. H1/H4/M15/M5 bars left-labelled; D1 bars open 17:00 EST.
Every candidate is stored as 'units' (one row per held H1 bar for calendar features F1/F2/F3/F8/F7, one row per trade
for trigger features F4/F5/F6/F9). A unit carries the trade id (tid) it belongs to; trade P&L = sum of its units.
gross is oriented: +1 = 'long' (calendar) or 'follow/continuation' (trigger). Direction d in {+1,-1} is applied later:
net pips = d*gross - cost_share. R = 0.25 * D1 ATR(14) of the last D1 bar closed at or before the trade entry.
HOLDOUT LOCK: data at or after 2022-01-01 can only be loaded after unlock_holdout(frozen_json) (see below)."""
import os, sys, json, datetime as dt, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bt import PIP
from sig import atr, rsi, bbands
from r4_common import tstat, maxdd, longest_flat_days

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'out'); CACHE = os.path.join(OUT, 'r7_cache'); os.makedirs(CACHE, exist_ok=True)
STATE = os.path.join(OUT, 'r7_state.json'); LOG = os.path.join(OUT, 'r7_loop_log.md')
POOL_END = pd.Timestamp('2022-01-01')     # exclusive
HOLD_END = pd.Timestamp('2025-01-01')     # exclusive
FX = ['AUDJPY', 'AUDNZD', 'AUDUSD', 'CADJPY', 'EURAUD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'GBPCHF', 'GBPJPY',
      'GBPUSD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
INSTS = FX + ['XAUUSD']
USD7 = {'EURUSD': -1, 'GBPUSD': -1, 'AUDUSD': -1, 'NZDUSD': -1, 'USDJPY': 1, 'USDCAD': 1, 'USDCHF': 1}
COST = {p: 0.5 for p in FX}; COST['XAUUSD'] = 30.0          # pips round trip (XAU pip = 0.01 USD -> 0.30 USD)
BLOCKS = [('2005-08', 2005, 2008), ('2009-12', 2009, 2012), ('2013-16', 2013, 2016), ('2017-21', 2017, 2021)]
H1 = pd.Timedelta('1h')
_UNLOCK = {'ok': False}

def now_utc(): return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')

def usd_side(p):
    if p.endswith('USD'): return -1          # XXXUSD (incl. XAUUSD): USD up -> pair down
    if p.startswith('USD'): return 1
    return 1                                 # non-USD cross: label 'follow' = long cross after USD-up hour (sign convention only)

def unlock_holdout(frozen_path):
    if not os.path.exists(frozen_path): raise RuntimeError('holdout locked: frozen file missing')
    _UNLOCK['ok'] = True

def lock_holdout(): _UNLOCK['ok'] = False

def load(inst, tf, end):
    if end > POOL_END and not _UNLOCK['ok']: raise RuntimeError('HOLDOUT LOCKED: refusing to load data >= 2022-01-01')
    if tf == 'M5':
        if inst == 'XAUUSD': tf = 'M15'
        else: df = pd.read_parquet(os.path.join(ROOT, 'bars_m5', f'{inst}_M5.parquet')); return df[df.index < end]
    df = pd.read_parquet(os.path.join(ROOT, 'bars_full', f'{inst}_{tf}.parquet'))
    return df[df.index < end]

# ---------------- state / log ----------------
def load_state():
    if os.path.exists(STATE): return json.load(open(STATE))
    return None

def save_state(st):
    tmp = STATE + '.tmp'; json.dump(st, open(tmp, 'w'), indent=1, default=float); os.replace(tmp, STATE)

def logmd(text):
    with open(LOG, 'a') as f: f.write(text.rstrip('\n') + '\n')

# ---------------- D1 frame (R, refinement features) ----------------
def d1_frame(inst, end):
    d1 = load(inst, 'D1', end)
    h, l, c = d1.high.values, d1.low.values, d1.close.values
    a = atr(h, l, c, 14); span = pd.Series(d1.index).diff(13).dt.days.values
    f = pd.DataFrame({'close_time': d1.index + pd.Timedelta('1D'), 'close': c, 'atr': np.where(span <= 24, a, np.nan)})
    f['sma200'] = pd.Series(c).rolling(200).mean().values
    av = pd.Series(f['atr'].values)
    f['atr_pct'] = av.rolling(250, min_periods=200).apply(lambda x: 100.0 * (x <= x[-1]).mean(), raw=True).values
    return f.sort_values('close_time').reset_index(drop=True)

def h4_rsi_frame(inst, end):
    h4 = load(inst, 'H4', end)
    return pd.DataFrame({'close_time': h4.index + pd.Timedelta('4h'), 'h4rsi': rsi(h4.close.values, 14)}).sort_values('close_time')

def asof(times, frame, key='close_time'):
    x = pd.DataFrame({'t': pd.to_datetime(times)}).reset_index()
    m = pd.merge_asof(x.sort_values('t'), frame, left_on='t', right_on=key, direction='backward').sort_values('index')
    return m.reset_index(drop=True)

# ---------------- unit builders ----------------
def _cal_units(idx, o, c, pip, cost, param, tid, keep):
    """calendar units: one per H1 bar; gross = long close-open; cost share = cost / units in the trade."""
    k = np.asarray(keep)
    df = pd.DataFrame({'param': np.asarray(param)[k], 't': idx[k], 'te': idx[k] + H1, 'tid': np.asarray(tid)[k],
                       'gross': ((c - o) / pip)[k], 'px': o[k], 'side': 1})
    df['cost'] = cost / df.groupby(['param', 'tid']).t.transform('size')
    return df

def _trig_units(idx, o, c, pip, cost, param, trig_i, dirs, hold_h):
    """trigger units: entry at open of bar i+1 (must be exactly 1h after bar i), exit at close of the last bar with open
    < entry + hold_h; one position at a time (a trigger is skipped while the previous trade is open)."""
    n = len(idx); rows = []; busy_until = pd.Timestamp('1900-01-01')
    for i, d in zip(trig_i, dirs):
        j = i + 1
        if j >= n or idx[j] != idx[i] + H1: continue
        if idx[j] < busy_until: continue
        k = int(np.searchsorted(idx, idx[j] + pd.Timedelta(hours=hold_h))) - 1
        if k < j: continue
        te = idx[k] + H1; busy_until = te
        rows.append((param, idx[j], te, j, d * (c[k] - o[j]) / pip, o[j], int(d)))
    df = pd.DataFrame(rows, columns=['param', 't', 'te', 'tid', 'gross', 'px', 'side']); df['cost'] = cost
    return df

def usd_basket(end):
    fp = os.path.join(CACHE, f'basket_{end.year}.parquet')
    if os.path.exists(fp): return pd.read_parquet(fp)['b']
    cols = {}
    for p, s in USD7.items():
        h = load(p, 'H1', end); cols[p] = s * 100.0 * (h.close - h.open) / h.open
    m = pd.DataFrame(cols); b = m.mean(axis=1).where(m.notna().sum(axis=1) >= 5)
    pd.DataFrame({'b': b}).to_parquet(fp); return b

def f6_units(inst, end, pip, cost):
    b = load(inst, 'M5', end); idx = b.index; o, h, l, c = (b[k].values for k in ('open', 'high', 'low', 'close'))
    step = 15 if inst == 'XAUUSD' else 5; nexp = 7 * 60 // step
    fxd = (idx + pd.Timedelta('7h')).normalize(); hr = idx.hour
    asia = (hr >= 19) | (hr < 2)
    A = pd.DataFrame({'d': fxd[asia], 'h': h[asia], 'l': l[asia]}).groupby('d').agg(hi=('h', 'max'), lo=('l', 'min'), n=('h', 'size'))
    A = A[A.n >= nexp // 2]
    win = (hr >= 2) & (hr < 6)
    W = pd.DataFrame({'d': fxd[win], 'i': np.nonzero(win)[0], 'c': c[win]})
    W = W.join(A, on='d', how='inner')
    W['br'] = np.where(W.c > W.hi, 1, np.where(W.c < W.lo, -1, 0)); W = W[W.br != 0]
    first = W.groupby('d').first()
    rows = []
    for d, r in first.iterrows():
        j = int(r.i) + 1
        if j >= len(idx) or idx[j] >= d + pd.Timedelta('11h'): continue
        k = int(np.searchsorted(idx, d + pd.Timedelta('11h')))
        if k >= len(idx) or idx[k] > d + pd.Timedelta('11h30min'): continue
        rows.append(('F6_follow', idx[j], idx[k], j, r.br * (o[k] - o[j]) / pip, o[j], int(r.br)))
    df = pd.DataFrame(rows, columns=['param', 't', 'te', 'tid', 'gross', 'px', 'side']); df['cost'] = cost
    return df

GRP = [(1, 3), (4, 7), (8, 12), (13, 17), (18, 22), (23, 27), (28, 31)]
DOWN = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']

def build_units(inst, end):
    pip = PIP[inst]; cost = COST[inst]
    h = load(inst, 'H1', end); idx = h.index; o, hi, lo, c = (h[k].values.astype(float) for k in ('open', 'high', 'low', 'close'))
    n = len(idx); hr = idx.hour.values; dow = idx.dayofweek.values; ordd = (idx.normalize() - pd.Timestamp('2000-01-01')).days.values
    parts = []
    # F1 hour-of-day
    parts.append(_cal_units(idx, o, c, pip, cost, np.array([f'F1_h{x:02d}' for x in range(24)])[hr], np.arange(n), np.ones(n, bool)))
    # F2 weekday x 4h block (EST calendar weekday Mon-Fri)
    blk = hr // 4
    par2 = np.array([f'F2_{DOWN[min(d, 4)]}_{b * 4:02d}' for d, b in zip(dow, blk)])
    parts.append(_cal_units(idx, o, c, pip, cost, par2, ordd * 10 + blk, dow <= 4))
    # F3 day-of-month group x session; FX trading date = (EST + 7h) date (day rolls 17:00 EST)
    fxd = (idx + pd.Timedelta('7h')).normalize(); fday = fxd.day.values; fdow = fxd.dayofweek.values
    sess = np.where((hr >= 19) | (hr < 2), 0, np.where((hr >= 2) & (hr < 8), 1, np.where((hr >= 8) & (hr < 17), 2, -1)))
    gi = np.zeros(n, int)
    for g, (a, b_) in enumerate(GRP): gi[(fday >= a) & (fday <= b_)] = g
    sname = np.array(['Asia', 'London', 'NY'])
    gname = np.array([f'd{a:02d}-{b_:02d}' for a, b_ in GRP])
    par3 = np.char.add(np.char.add(np.char.add('F3_', gname[gi]), '_'), sname[np.clip(sess, 0, 2)])
    fo = (fxd - pd.Timestamp('2000-01-01')).days.values
    parts.append(_cal_units(idx, o, c, pip, cost, par3, fo * 10 + sess, (sess >= 0) & (fdow <= 4)))
    # F8 week open: Sunday first 4h from the first Sunday bar (>=16:00); Monday 02:00-11:00 EST
    sun = (dow == 6) & (hr >= 16)
    s0 = pd.Series(idx[sun]).groupby(idx[sun].normalize()).transform('min').values
    k8 = np.zeros(n, bool); k8[np.nonzero(sun)[0]] = (idx[sun].values < s0 + np.timedelta64(4, 'h'))
    parts.append(_cal_units(idx, o, c, pip, cost, np.full(n, 'F8_sun4'), ordd, k8))
    parts.append(_cal_units(idx, o, c, pip, cost, np.full(n, 'F8_mon0211'), ordd, (dow == 0) & (hr >= 2) & (hr < 11)))
    # F7 lead-lag: previous-hour USD basket -> this hour. follow dir = sign(basket) * usd_side(inst)
    bsk = usd_basket(end); prev = bsk.reindex(idx - H1).values
    sg = np.sign(np.nan_to_num(prev)); k7 = sg != 0
    u7 = _cal_units(idx, o, c, pip, cost, np.full(n, 'F7_follow'), np.arange(n), k7)
    u7['side'] = (sg[k7] * usd_side(inst)).astype(int); u7['gross'] = u7['gross'].values * u7['side'].values; parts.append(u7)
    # F4 large move: |c-o| > 2*ATR14(H1, through previous bar)
    a = atr(hi, lo, c, 14); ap = np.roll(a, 1); ap[0] = np.nan; mv = c - o
    ti = np.nonzero(np.abs(mv) > 2 * np.nan_to_num(ap, nan=np.inf))[0]
    for H in (1, 4, 12): parts.append(_trig_units(idx, o, c, pip, cost, f'F4_h{H:02d}', ti, np.sign(mv[ti]), H))
    # F5 indicator states (follow orientation: RSI<30 / below BB -> short; RSI>70 / above BB -> long), next 4h
    r = rsi(c, 14); _, up, dn, _ = bbands(c, 20, 2.0)
    for nm, cond, d in (('rsiLo', r < 30, -1), ('rsiHi', r > 70, 1), ('bbLo', c < np.nan_to_num(dn, nan=-np.inf), -1),
                        ('bbHi', c > np.nan_to_num(up, nan=np.inf), 1)):
        ii = np.nonzero(np.nan_to_num(cond, nan=False).astype(bool))[0]
        parts.append(_trig_units(idx, o, c, pip, cost, f'F5_{nm}', ii, np.full(len(ii), d), 4))
    # F9 streaks of same-colour H1 candles (contiguous bars); trigger when the run reaches exactly N; follow = colour
    col = np.sign(mv); run = np.zeros(n, int)
    for i in range(n):
        if col[i] != 0 and i > 0 and col[i] == col[i - 1] and idx[i] == idx[i - 1] + H1: run[i] = run[i - 1] + 1
        else: run[i] = 1 if col[i] != 0 else 0
    for N in (4, 6):
        ii = np.nonzero(run == N)[0]; parts.append(_trig_units(idx, o, c, pip, cost, f'F9_s{N}', ii, col[ii], 4))
    # F6 Asia-range break (M5; M15 for XAUUSD)
    parts.append(f6_units(inst, end, pip, cost))
    U = pd.concat(parts, ignore_index=True)
    U = U[U.te <= end].copy()
    # trade-level entry time -> R and month
    U['t_ent'] = U.groupby(['param', 'tid']).t.transform('min')
    d1 = d1_frame(inst, end)[['close_time', 'atr']]
    te = U[['t_ent']].drop_duplicates().sort_values('t_ent')
    m = pd.merge_asof(te, d1, left_on='t_ent', right_on='close_time', direction='backward')
    U = U.merge(m[['t_ent', 'atr']], on='t_ent', how='left')
    U['R'] = 0.25 * U['atr'] / pip
    U = U.dropna(subset=['R', 'gross']); U = U[U.R > 0]
    U['month'] = U.t_ent.dt.year * 100 + U.t_ent.dt.month
    U['inst'] = inst
    return U[['inst', 'param', 't', 'te', 'tid', 't_ent', 'gross', 'cost', 'R', 'px', 'side', 'month']].reset_index(drop=True)

def pool_units(inst):
    fp = os.path.join(CACHE, f'units_pool_{inst}.parquet')
    if os.path.exists(fp): return pd.read_parquet(fp)
    U = build_units(inst, POOL_END); U.to_parquet(fp); return U

def excluded(inst, param):
    """Method-1 equivalents (Gotobi / Tokyo-fix windows in USDJPY): 08:00-10:00 JST hours, the 16-20 EST block
    (contains 09:55 JST), every Asia session of F3 (contains 09:55 JST and the Gotobi day groups)."""
    if inst != 'USDJPY': return False
    return param in ('F1_h18', 'F1_h19') or (param.startswith('F2_') and param.endswith('_16')) or \
        (param.startswith('F3_') and param.endswith('_Asia'))

# ---------------- trade level ----------------
def trades_of(U, inst, param, d):
    u = U[(U.inst == inst) & (U.param == param)]
    g = u.groupby('tid', sort=False)
    T = pd.DataFrame({'t_ent': g.t.min(), 't_exit': g.te.max(), 'gross': g.gross.sum() * d, 'cost': g.cost.sum(),
                      'R': g.R.first(), 'px': g.px.first(), 'side': g.side.first() * d, 'month': g.month.first()}).sort_values('t_ent').reset_index(drop=True)
    T['d'] = d; T['net'] = T.gross - T.cost; T['netR'] = T.net / T.R
    return T

def tstats(x):
    x = np.asarray(x, float)
    if len(x) < 3: return dict(N=len(x), mean=np.nan, t=np.nan)
    return dict(N=len(x), mean=float(x.mean()), t=float(tstat(x)))

def ratio_stats(r):
    r = np.asarray(r, float); s = r.sum(); dd = maxdd(r)
    return dict(sum=float(s), maxDD=float(dd), ratio=float(s / abs(dd)) if dd < 0 else float('inf'))
