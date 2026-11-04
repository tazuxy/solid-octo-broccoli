"""Round 7 edge-discovery loop, LIBRARY v2 (resumable). Run: python3 -I r7_v2loop.py
Library v2 = v1 (F1-F9, with the rollover validity rule) + C candles, I indicators, Z zones, D Dow structure, T counter-
trendline breaks (H1/H4; T also M15) + X combinations (trigger x context x location x indicator, <=3 conditions, 4 if the
4th is a context), per instrument and POOLED over the 17 FX pairs. Top 20 per month; confirmation t>=3.5.
State: out/r7_state.json (v1 state archived in out/r7_v1_state.json); log: out/r7_loop_log.md."""
import os, sys, json, warnings, numpy as np, pandas as pd
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r7_lib as L, r7_dev as D, r7_v2feat as V
from r7_lib import logmd
import r7_loop as V1

T_MIN = 3.5; N_MIN = 8; TOPK = 20; MAX_MONTHS = 12; TARGET = 2; POOL_FRAC = 0.60
GEN = ['h4', 'h12', 'h24', 'br']; TOUT = ['h12', 'h24', 'tb', 'tt']
CTXV = ['a_dh4', 'a_dd1', 'a_e200']; INDV = ['a_rsiz', 'a_rsi50', 'a_stz', 'a_macdh', 'a_macdt']
VALS = [f'v{j}{x}' for j in range(4) for x in 'fx']
FAMS = [('c',), ('loc',), ('u',), ('c', 'loc'), ('c', 'u'), ('loc', 'u'), ('c', 'loc', 'u'), ('c', 'c2', 'loc'), ('c', 'c2', 'u')]
FAMILY = {'F1': 'time', 'F2': 'time', 'F7': 'time', 'F8': 'calendar', 'F3': 'calendar', 'F4': 'price-reaction', 'F5': 'indicator',
          'F6': 'price-reaction', 'F9': 'candle', 'C_': 'candle', 'I_': 'indicator', 'Z_': 'zone', 'D_': 'Dow', 'T_': 'trendline'}

# ---------------- v1 features under the rollover validity rule ----------------
def v1_filter(U):
    """drop v1 units whose entry or exit price is stamped in the 16:55-17:30 EST rollover window (bid-only artifact)."""
    fx = U.inst != 'XAUUSD'
    bad = U.param.isin(['F1_h16', 'F1_h17']) | U.param.str.endswith('_NY') | ((U.param == 'F8_sun4') & fx)
    bad |= (U.param == 'F7_follow') & U.t.dt.hour.isin([16, 17])
    trig = U.param.str[:2].isin(['F4', 'F5', 'F9'])
    bad |= trig & ((U.t.dt.hour == 17) | (U.te.dt.hour == 17))
    return U[~bad].reset_index(drop=True)

# ---------------- outcomes ----------------
def outcome(B, s, out, d):
    """gross pips (oriented by trigger orientation s and direction d), exit time, stop distance (pips, NaN=none), market side."""
    s = np.asarray(s, float); m = s * d
    if out.startswith('h'):
        g = m * B[f'g_{out}'].values; x = B[f'x_{out}'].values; k = np.full(len(B), np.nan)
    elif out == 'br':
        g = np.where(m > 0, B.g_brL.values, B.g_brS.values); x = np.where(m > 0, B.x_brL.values, B.x_brS.values); k = B.k_br.values
    else:
        f = 'F' if d > 0 else 'X'; g = B[f'g_{out}{f}'].values; x = B[f'x_{out}{f}'].values; k = B[f'k_{out}'].values
    return g.astype(float), x, k.astype(float), m

def outs_for(trig): return TOUT if trig.startswith('T_') else GEN

def vals_frame(B, s, trig):
    cost = B.inst.map(L.COST).values; R = B.R.values.astype(float); v = {}
    for j, o in enumerate(outs_for(trig)):
        for x, d in (('f', 1), ('x', -1)):
            g, _, _, _ = outcome(B, s, o, d); v[f'v{j}{x}'] = (g - cost) / R
    v = pd.DataFrame(v, index=B.index); v['day'] = B.t_ent.values.astype('datetime64[D]').astype(np.int64)
    return v

# ---------------- tables ----------------
def load_tables():
    T = {tf: {} for tf in ('H1', 'H4', 'M15')}
    for inst in L.INSTS:
        for tf, df in V.pool_tables(inst).items():
            assert df.t_ent.max() < L.POOL_END
            T[tf][inst] = df
    return T

def cond_cols(df): return [c for c in df.columns if c[:2] in ('C_', 'I_', 'Z_', 'D_', 'T_')]
def trig_cols(df): return [c for c in df.columns if c.startswith('C_') or c.startswith('T_') or (c.startswith('Z_') and not c.endswith('_xx'))]
def zat_cols(df): return [c for c in df.columns if c.startswith('Z_') and c.endswith('_at')]

def gstats(df, keys, floor=None):
    """per-group stats for the 8 outcome slots. Events may overlap in time (within a pair, and across pairs for pooled
    rules), so t is computed on the candidate's DAILY P&L series in the month: sum net R per entry day, t = mean/SE over
    days (needs >= 3 days). Variance floor: the day-level SD used is at least the month-wide per-event SD of that slot."""
    x = df[keys + ['day'] + VALS]
    g1 = x.groupby(keys + ['day'], observed=True, sort=False)
    Sd = g1[VALS].sum(min_count=1); Cd = g1[VALS].count()
    Sd = Sd.reset_index(); Cd = Cd.reset_index()
    for v in VALS: Sd[v + 'q'] = Sd[v] ** 2
    g2 = Sd.groupby(keys, observed=True, sort=False)
    S = g2[VALS].sum(); D = g2[VALS].count(); Q = g2[[v + 'q' for v in VALS]].sum(); Q.columns = VALS
    Cn = Cd.groupby(keys, observed=True, sort=False)[VALS].sum()
    md = S / D; var = (Q - D * md ** 2) / (D - 1)
    if floor is not None:
        for v in VALS: var[v] = np.maximum(var[v], floor[v] ** 2)
    t = md / np.sqrt(var / D); M = S / Cn
    rows = []
    for v in VALS:
        ok = (Cn[v] >= N_MIN) & (D[v] >= 3) & (t[v] > 2.5) & np.isfinite(t[v])
        if not ok.any(): continue
        sub = pd.DataFrame({'n': Cn[v][ok], 'days': D[v][ok], 'mR': M[v][ok], 't': t[v][ok]}); sub['slot'] = v
        rows.append(sub.reset_index())
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()

def month_slice(T, tf, mon):
    parts = [df[df.month == mon] for df in T[tf].values()]
    return pd.concat([p for p in parts if len(p)], ignore_index=True)

def discover_v2(T, mon):
    recs = []
    for tf in ('H1', 'H4', 'M15'):
        M = month_slice(T, tf, mon)
        if not len(M): continue
        fxm = M.inst != 'XAUUSD'
        # singles: every condition column (orientation = column sign)
        occ = []
        cols = cond_cols(M) if tf != 'M15' else [c for c in M.columns if c.startswith('T_')]
        for c in cols:
            sub = M[M[c] != 0]
            if len(sub) < N_MIN: continue
            vf = vals_frame(sub, sub[c].values, c); vf['inst'] = sub.inst.values; vf['trig'] = c; occ.append(vf)
        if occ:
            O = pd.concat(occ, ignore_index=True); fl = {v: float(np.nanstd(O[v].values)) for v in VALS}
            for pooled in (False, True):
                X = O[O.inst != 'XAUUSD'].assign(inst='POOL') if pooled else O
                r = gstats(X, ['inst', 'trig'], fl)
                if len(r): r['tf'] = tf; r['fam'] = 'single'; recs.append(r)
        # combinations: triggers = candles, zone events, T lines
        trigs = [c for c in M.columns if c.startswith('C_') or c.startswith('T_') or (c.startswith('Z_') and tf != 'M15')]
        if tf == 'M15': trigs = [c for c in M.columns if c.startswith('T_')]
        za = zat_cols(M); zat = (M[za] != 0).values; znames = [c[2:-3] for c in za]
        occ = []
        for c in trigs:
            sub = M[M[c] != 0]
            if len(sub) < N_MIN: continue
            vf = vals_frame(sub, sub[c].values, c); vf['inst'] = sub.inst.values; vf['trig'] = c; vf['row'] = sub.index.values
            for a in CTXV + INDV: vf[a] = sub[a].values
            occ.append(vf)
        if not occ: continue
        O = pd.concat(occ, ignore_index=True); fl = {v: float(np.nanstd(O[v].values)) for v in VALS}
        # exploded location: one row per zone type the close is at, or 'none'
        zr = zat[O.row.values]; li, lj = np.nonzero(zr)
        none = ~zr.any(1)
        E = pd.concat([O.iloc[li].assign(loc=np.array(znames)[lj]), O[none].assign(loc='none')], ignore_index=True)
        for fam in FAMS:
            src = E if 'loc' in fam else O
            keysets = []
            cvars = CTXV
            if fam == ('c',): keysets = [[c] for c in cvars]
            elif fam == ('loc',): keysets = [['loc']]
            elif fam == ('u',): keysets = [[u] for u in INDV]
            elif fam == ('c', 'loc'): keysets = [[c, 'loc'] for c in cvars]
            elif fam == ('c', 'u'): keysets = [[c, u] for c in cvars for u in INDV]
            elif fam == ('loc', 'u'): keysets = [['loc', u] for u in INDV]
            elif fam == ('c', 'loc', 'u'): keysets = [[c, 'loc', u] for c in cvars for u in INDV]
            elif fam == ('c', 'c2', 'loc'): keysets = [[a, b, 'loc'] for i, a in enumerate(cvars) for b in cvars[i + 1:]]
            elif fam == ('c', 'c2', 'u'): keysets = [[a, b, u] for i, a in enumerate(cvars) for b in cvars[i + 1:] for u in INDV]
            for ks in keysets:
                for pooled in (False, True):
                    X = src[src.inst != 'XAUUSD'].assign(inst='POOL') if pooled else src
                    r = gstats(X, ['inst', 'trig'] + ks, fl)
                    if not len(r): continue
                    r['tf'] = tf; r['fam'] = 'x:' + '+'.join(ks)
                    r['conds'] = [json.dumps({k: (v if isinstance(v, str) else int(v)) for k, v in zip(ks, vals)}) for vals in r[ks].values]
                    recs.append(r.drop(columns=ks))
    R = pd.concat(recs, ignore_index=True)
    if 'conds' not in R: R['conds'] = None
    R['conds'] = R.conds.where(R.conds.notna(), '{}')
    R = R.sort_values('t', ascending=False)
    R = R.drop_duplicates(subset=['tf', 'inst', 'trig', 'conds', 'slot'])
    # identical in-month event sets under different (redundant) conditions: keep the rule with the fewest conditions
    R['ncond'] = R.conds.str.count(':'); R['mkey'] = R.mR.round(6)
    R = R.sort_values(['t', 'ncond'], ascending=[False, True]).drop_duplicates(subset=['tf', 'inst', 'trig', 'slot', 'n', 'mkey'])
    cands = []
    for r in R.head(TOPK * 3).itertuples():
        j = int(r.slot[1]); d = 1 if r.slot[2] == 'f' else -1
        cands.append(dict(kind='v2', tf=r.tf, inst=r.inst, trig=r.trig, conds=json.loads(r.conds), out=outs_for(r.trig)[j], d=d,
                          n=int(r.n), t=float(r.t), mean_R=float(r.mR)))
    return cands, len(R)

def discover_all(T, U, mon):
    c2, n2 = discover_v2(T, mon)
    c1, n1 = V1.discover(U, mon)
    for c in c1:
        c.update(kind='v1', tf='H1' if c['param'][:2] != 'F6' else 'M5', trig=c['param'], conds={}, out='-', n=c['n_units'])
    allc = sorted(c1 + c2, key=lambda z: -z['t'])[:TOPK]
    for k, c in enumerate(allc): c['rank'] = k + 1
    return allc, n1 + n2

def cand_str(c):
    if c['kind'] == 'v1': return f"{c['inst']} {c['param']} {'long/follow' if c['d'] > 0 else 'short/fade'}"
    cs = ' & '.join(f'{k[2:] if k.startswith("a_") else k}={v}' for k, v in c['conds'].items())
    return f"{c['tf']} {c['inst']} {c['trig']}{(' & ' + cs) if cs else ''} → {c['out']} {'follow' if c['d'] > 0 else 'fade'}"

def family_of(c):
    if c['kind'] == 'v1': return FAMILY[c['param'][:2]]
    base = FAMILY[c['trig'][:2]]
    return base if not c['conds'] else f"combination ({base} trigger)"

# ---------------- trades of a v2 candidate ----------------
def v2_trades(tables, c, insts):
    rows = []
    for inst in insts:
        B = tables[c['tf']].get(inst)
        if B is None or not len(B): continue
        m = B[c['trig']] != 0
        for k, v in c['conds'].items():
            if k == 'loc':
                m &= (B[f'Z_{v}_at'] != 0) if v != 'none' else (B[zat_cols(B)] == 0).all(axis=1)
            else: m &= B[k] == v
        S = B[m]
        if not len(S): continue
        g, x, kp, side = outcome(S, S[c['trig']].values, c['out'], c['d'])
        Tt = pd.DataFrame({'inst': inst, 't_ent': S.t_ent.values, 't_exit': pd.to_datetime(x), 'gross': g, 'cost': L.COST[inst],
                           'R': S.R.values.astype(float), 'px': S.px.values, 'side': side.astype(int), 'kpips': kp, 'month': S.month.values})
        Tt = Tt.dropna(subset=['gross', 't_exit']).sort_values('t_ent')
        keep = np.zeros(len(Tt), bool); last = np.datetime64('1900-01-01')
        te, tx = Tt.t_ent.values, Tt.t_exit.values
        for i in range(len(Tt)):
            if te[i] >= last: keep[i] = True; last = tx[i]
        rows.append(Tt[keep])
    if not rows: return pd.DataFrame(columns=['inst', 't_ent', 't_exit', 'gross', 'cost', 'R', 'px', 'side', 'kpips', 'month'])
    T = pd.concat(rows, ignore_index=True).sort_values('t_ent').reset_index(drop=True)
    T['d'] = c['d']; T['net'] = T.gross - T.cost; T['netR'] = T.net / T.R; T['netR2'] = (T.gross - 2 * T.cost) / T.R
    return T

def insts_of(c): return [i for i in L.FX] if c['inst'] == 'POOL' else [c['inst']]

def confirm_v2(tables, c, mon):
    T = v2_trades(tables, c, insts_of(c)); T = T[T.month != mon]
    s = V1_stats(T)
    if c['inst'] == 'POOL':
        per = T.groupby('inst').netR.agg(['mean', 'size']); per = per[per['size'] >= 20]
        frac = float((per['mean'] > 0).mean()) if len(per) else 0.0
        s['pairs_pos'] = f"{int((per['mean'] > 0).sum())}/{len(per)}"; s['crit']['pairs60'] = bool(frac >= POOL_FRAC)
        s['nb'] = [f"{i} {m:+.3f}R" for i, m in per['mean'].sort_values(ascending=False).head(4).items()]
    else:
        c2 = dict(c, inst='POOL'); Tp = v2_trades(tables, c2, [i for i in L.FX if i != c['inst']]); Tp = Tp[Tp.month != mon]
        per = Tp.groupby('inst').netR.mean()
        s['pairs_pos'] = f"other pairs {int((per > 0).sum())}/{len(per)}"
        q = L.tstats(Tp.netR); s['nb'] = [f"same rule other 16 pairs pooled {q['mean']:+.3f}R t{q['t']:.1f}"] if len(Tp) > 2 else []
    s['verdict'] = 'CONFIRMED' if all(s['crit'].values()) else 'limited'
    return s

def V1_stats(T):
    q = L.tstats(T.netR); qp = L.tstats(T.net)
    blk = V1.block_of(T.t_ent) if len(T) else np.array([])
    bl = T.assign(blk=blk).groupby('blk').netR.agg(['mean', 'size']) if len(T) else pd.DataFrame(columns=['mean', 'size'])
    nblk = len(bl); npos = int((bl['mean'] > 0).sum()); need = 3 if nblk >= 3 else max(nblk, 1)
    s = dict(N=q['N'], mean_R=q['mean'], t_R=q['t'], mean_pips=qp['mean'], gross_R=float((T.gross / T.R).mean()) if len(T) else np.nan,
             mean_R_2x=float(T.netR2.mean()) if len(T) else np.nan, blocks_pos=f'{npos}/{nblk}')
    dsum = T.groupby(pd.to_datetime(T.t_ent).dt.normalize()).netR.sum() if len(T) else pd.Series(dtype=float)
    s['t_day'] = L.tstats(dsum.values)['t']        # t on the daily P&L series (handles same-day trades across pairs)
    tc = np.nanmin([q['t'], s['t_day']]) if len(T) > 2 else np.nan
    s['t_used'] = float(tc)
    s['crit'] = dict(mean_pos=bool(q['mean'] > 0 and qp['mean'] > 0), t=bool(tc >= T_MIN), blocks=bool(npos >= need),
                     cost2x=bool(s['mean_R_2x'] > 0))
    return s

def confirm_any(tables, U, c, mon):
    if c['kind'] == 'v2': return confirm_v2(tables, c, mon)
    r = V1.confirm(U, c, mon)
    T = L.trades_of(U, c['inst'], c['param'], c['d']); T = T[T.month != mon]
    r['t_day'] = L.tstats(T.groupby(T.t_ent.dt.normalize()).netR.sum().values)['t']; r['t_used'] = float(np.nanmin([r['t_R'], r['t_day']]))
    r['crit']['t'] = bool(r['t_used'] >= T_MIN); r['verdict'] = 'CONFIRMED' if all(r['crit'].values()) else 'limited'
    r['pairs_pos'] = r['nb_other_inst_pos']; r['nb'] = r['nb_other_inst_t>=2'][:3] + r.get('nb_adjacent_hours', [])
    return r

# ---------------- development ----------------
def cand_trades(c, tables, U, end):
    """full trade list of the candidate's base rule (all months up to end)."""
    if c['kind'] == 'v2':
        return v2_trades(tables, c, insts_of(c))
    T = L.trades_of(U, c['inst'], c['param'], c['d']); T['inst'] = c['inst']; T['kpips'] = np.nan
    T['netR2'] = (T.gross - 2 * T.cost) / T.R
    return T

def stop_and_features(T, c, k, end):
    parts = []
    for inst, Ti in T.groupby('inst'):
        if c.get('out') in ('br', 'tb', 'tt'):
            Tk = D.apply_stop(Ti, inst, None, end); Tk['kR'] = Ti.kpips.values / Ti.R.values
        else:
            Tk = D.apply_stop(Ti, inst, k, end); Tk['kR'] = float(k) if k else 1.0
        Tk = D.add_features(Tk, inst, end); Tk['inst'] = inst; parts.append(Tk)
    return pd.concat(parts, ignore_index=True).sort_values('t_ent').reset_index(drop=True)

def rule_text(c):
    if c['kind'] == 'v1': return V1.rule_text(c)
    o = {'h4': 'exit at the open 4 bars after entry', 'h12': 'exit at the open 12 bars after entry', 'h24': 'exit at the open 24 bars after entry',
         'br': 'bracket: TP 1.5 x ATR14(tf), SL 1 x ATR14(tf), time stop 24 bars',
         'tb': 'bracket: SL = pullback extreme -/+ 0.25 ATR14, TP = 2 x risk, time stop 48 bars',
         'tt': 'TP = prior trend extreme, SL = pullback extreme -/+ 0.25 ATR14, time stop 48 bars'}[c['out']]
    who = 'each of the 17 FX pairs (one position per pair)' if c['inst'] == 'POOL' else c['inst']
    return (f"{who}, {c['tf']} bars: when [{cand_str(c).split('→')[0].split(' ', 2)[2].strip()}] at a closed bar, enter at the next bar open "
            f"in the {'signal' if c['d'] > 0 else 'opposite-to-signal'} direction; {o}; no entry/exit stamped 16:55-17:30 EST")

def develop(st, c, mon, tables, U):
    key = cand_str(c); P = st['promotions'].setdefault(key, {'cand': c, 'month': mon, 'steps': {}}); sp = P['steps']
    if 'N' not in P: P['N'] = 2 + sum(1 for v in st['promotions'].values() if 'N' in v); L.save_state(st)
    N = P['N']; intrinsic = c.get('out') in ('br', 'tb', 'tt')
    T0 = cand_trades(c, tables, U, L.POOL_END)
    if 'stop' not in sp:
        res = {}
        opts = [None] if intrinsic else [None, 2, 3]
        for k in opts: res[str(k)] = D.full_stats(stop_and_features(T0, c, k, L.POOL_END))
        best = max(opts, key=lambda k: res[str(k)]['ratio'])
        choice = best if (best is not None and res[str(best)]['ratio'] >= 1.1 * res['None']['ratio']) else None
        sp['stop'] = dict(choice=choice, table=res, intrinsic=intrinsic); L.save_state(st)
        logmd(f"- [{L.now_utc()}] DEV method{N} {key}: stop table (2005-2021, netR) " +
              '; '.join(f"{k}: mean {V1.f(v['mean_R'], 3)} t {v['t']:.2f} ratio {v['ratio']:.2f}" for k, v in res.items()) +
              f" -> stop = {'intrinsic bracket' if intrinsic else choice}")
    k = sp['stop']['choice']
    T = stop_and_features(T0, c, k, L.POOL_END)
    if 'refine_select' not in sp:
        choice, tab, base = D.select_refinement(T)
        tab.to_csv(os.path.join(L.OUT, f'r7_method{N}_refine_table.csv'), index=False)
        fr = dict(frozen_utc=L.now_utc(), method=N, cand=c, stop=k, refinement=choice, selection_base=base,
                  note='chosen on 2005-2014 only, written before any 2015-2021 statistic of the refined rule was computed')
        json.dump(fr, open(os.path.join(L.OUT, f'r7_method{N}_refine.json'), 'w'), indent=1, default=float)
        sp['refine_select'] = dict(choice=choice, ts=fr['frozen_utc']); L.save_state(st)
        logmd(f"- [{fr['frozen_utc']}] DEV method{N}: refinement selected on 2005-2014 = {choice} (frozen r7_method{N}_refine.json)")
    choice = sp['refine_select']['choice']
    if 'refine_confirm' not in sp:
        ok, info = (False, {}) if choice is None else D.confirm_refinement(T, choice)
        sp['refine_confirm'] = dict(ok=ok, info=info, adopted=choice if ok else None); L.save_state(st)
        logmd(f"- [{L.now_utc()}] DEV method{N}: refinement confirmation 2015-2021: {'CONFIRMED' if ok else 'not adopted'} {info}")
    adopted = sp['refine_confirm']['adopted']
    TF = D.apply_refinement(T, adopted); TF.to_parquet(os.path.join(L.OUT, f'r7_method{N}_pool_trades.parquet'))
    if 'corr' not in sp:
        others = {'method1': D.method1_trades(L.POOL_END)}
        for f_ in sorted(os.listdir(L.OUT)):
            if f_.endswith('_pool_trades.parquet') and f_ != f'r7_method{N}_pool_trades.parquet':
                others[f_.replace('r7_', '').replace('_pool_trades.parquet', '')] = pd.read_parquet(os.path.join(L.OUT, f_))
        cors = {nm: D.daily_corr(TF, Tb) for nm, Tb in others.items()}
        dup = [nm for nm, v in cors.items() if v > 0.5]
        sp['corr'] = dict(corr=cors, dup=dup); L.save_state(st)
        logmd(f"- [{L.now_utc()}] DEV method{N}: daily-return correlation (2005-2021) {', '.join(f'{a} {b:+.2f}' for a, b in cors.items())}" +
              (f" -> DUPLICATE of {dup}: skipped" if dup else ''))
    if sp['corr']['dup']:
        P['verdict'] = 'skipped (duplicate)'; L.save_state(st); return P
    ffp = os.path.join(L.OUT, f'r7_method{N}_frozen.json')
    if 'frozen' not in sp:
        pool = D.full_stats(TF)
        fz = dict(frozen_utc=L.now_utc(), library='v2', method=N, discovered_in=mon, candidate=c, rule=rule_text(c),
                  instruments=insts_of(c) if c['kind'] == 'v2' else [c['inst']], cost_pips_round_trip={i: L.COST[i] for i in (insts_of(c) if c['kind'] == 'v2' else [c['inst']])},
                  R='0.25 x D1 ATR(14) of the last closed D1 bar at entry',
                  stop=('intrinsic bracket' if intrinsic else (None if k is None else f'{k}R')), refinement=adopted, pool_2005_2021=pool,
                  acceptance=dict(holdout_mean_gt0=True, holdout_ge_25pct_pool=True, full_t_ge=3.0, full_ratio_ge=3.0))
        json.dump(fz, open(ffp, 'w'), indent=1, default=float)
        sp['frozen'] = dict(ts=fz['frozen_utc'], pool=pool); L.save_state(st)
        logmd(f"- [{fz['frozen_utc']}] FROZEN method{N} -> r7_method{N}_frozen.json: {fz['rule']}; stop {fz['stop']}; refinement {adopted}; "
              f"pool N {pool['N']} mean {V1.f(pool['mean_R'], 3)}R ({V1.f(pool['mean_pips'])} pips) t {pool['t']:.2f} ratio {pool['ratio']:.2f}")
    if 'holdout' not in sp:
        ts = L.now_utc()
        if 'holdout_started' not in sp: sp['holdout_started'] = ts; L.save_state(st)
        logmd(f"- [{ts}] HOLDOUT EVALUATION START method{N} (2022-01..2024-12), rules frozen at {sp['frozen']['ts']}")
        open(os.path.join(L.OUT, 'r7_holdout_timeline.log'), 'a').write(f'{ts} START holdout method{N} (v2) {key} (frozen {sp["frozen"]["ts"]})\n')
        L.unlock_holdout(ffp)
        try:
            if c['kind'] == 'v2':
                full = {c['tf']: {}}
                for inst in insts_of(c): full[c['tf']][inst] = V.build_inst(inst, L.HOLD_END)[c['tf']]
                Tf = v2_trades(full, c, insts_of(c))
            else:
                Uf = v1_filter(L.build_units(c['inst'], L.HOLD_END)); Tf = cand_trades(c, None, Uf, L.HOLD_END)
            Tf = D.apply_refinement(stop_and_features(Tf, c, k, L.HOLD_END), adopted)
        finally:
            L.lock_holdout()
        Tf.to_parquet(os.path.join(L.OUT, f'r7_method{N}_full_trades.parquet'))
        H = Tf[Tf.t_ent >= L.POOL_END]; Pl = Tf[Tf.t_ent < L.POOL_END]
        hs, ps, fs = D.full_stats(H), D.full_stats(Pl), D.full_stats(Tf)
        fs['t_day'] = L.tstats(Tf.groupby(pd.to_datetime(Tf.t_ent).dt.normalize()).netR.sum().values)['t']
        crit = dict(holdout_mean_gt0=bool(hs['mean_R'] > 0), holdout_ge_25pct=bool(hs['mean_R'] >= 0.25 * ps['mean_R']),
                    full_t=bool(min(fs['t'], fs['t_day']) >= 3.0), full_ratio=bool(fs['ratio'] >= 3.0))
        acc = all(crit.values())
        sp['holdout'] = dict(ts=L.now_utc(), holdout=hs, pool=ps, full=fs, crit=crit, accepted=acc); L.save_state(st)
        json.dump(sp['holdout'], open(os.path.join(L.OUT, f'r7_method{N}_holdout.json'), 'w'), indent=1, default=float)
        open(os.path.join(L.OUT, 'r7_holdout_timeline.log'), 'a').write(f'{sp["holdout"]["ts"]} DONE holdout method{N} accepted={acc}\n')
        logmd(f"- [{sp['holdout']['ts']}] HOLDOUT method{N}: N {hs['N']} mean {V1.f(hs['mean_R'], 3)}R ({V1.f(hs['mean_pips'])} pips) t {hs['t']:.2f} | "
              f"pool mean {V1.f(ps['mean_R'], 3)}R | full 2005-2024 t {fs['t']:.2f} ratio {fs['ratio']:.2f} | crit {crit} -> {'ACCEPTED' if acc else 'failed holdout'}")
    P['verdict'] = 'ACCEPTED' if sp['holdout']['accepted'] else 'failed holdout'; L.save_state(st); return P

# ---------------- main ----------------
def main():
    st = L.load_state()
    if st is None:
        v1 = json.load(open(os.path.join(L.OUT, 'r7_v1_state.json')))
        st = dict(created=L.now_utc(), library='v2', phase='loop', month_order=v1['month_order'], months={}, promotions={},
                  n_tests=v1['n_tests'], n_tests_v1=v1['n_tests'], accepted=[], holdout_looks_v1=2)
        L.save_state(st)
        logmd(f"\n# Library v2 loop (started {st['created']})\n\nSame seed-42 month sequence; months tried under v1 are re-scanned. Top {TOPK} per month; "
              f"confirmation min(t on trades, t on daily P&L) of net R >= {T_MIN}, >=3/4 blocks positive, 2x cost > 0, pooled rules also >= 60% of pairs positive. "
              f"Rollover validity rule: no entry/exit price stamped 16:55-17:30 EST. Test count continues from v1 ({v1['n_tests']}).\n")
    if st['phase'] == 'done': print('done already'); return
    tables = load_tables()
    U = v1_filter(V1.load_pool()); U['param'] = U.param.astype('category'); U['inst'] = U.inst.astype('category')
    for k, mon in enumerate(st['month_order']):
        if len(st['accepted']) >= TARGET: break
        ms = st['months'].setdefault(str(mon), {})
        if ms.get('done'): continue
        if 'discovery' not in ms:
            cands, nsc = discover_all(tables, U, mon)
            ms['discovery'] = cands; ms['n_scanned'] = nsc; ms['k'] = k + 1; L.save_state(st)
            lines = [f"\n## v2 Month {k + 1}: {str(mon)[:4]}-{str(mon)[4:]}  (discovery {L.now_utc()}; {nsc} candidate rows with >=8 events and in-month t>2.5 [v2] or any t [v1])\n",
                     '| # | candidate | family | events | in-month t | in-month mean net R |', '|---|---|---|---|---|---|']
            for c in cands:
                lines.append(f"| {c['rank']} | {cand_str(c)} | {family_of(c)} | {c['n']} | {c['t']:.2f} | {V1.f(c['mean_R'], 3)} |")
            logmd('\n'.join(lines))
        if 'confirmation' not in ms:
            conf = [confirm_any(tables, U, c, mon) for c in ms['discovery']]
            ms['confirmation'] = conf; st['n_tests'] += len(conf); L.save_state(st)
            lines = [f"\nConfirmation on the other 203 pool months ({L.now_utc()}); running test count (v1+v2) = {st['n_tests']}\n",
                     '| # | candidate | N | mean pips | mean R | t trades | t daily | gross R | 2x-cost R | blocks + | pairs + | verdict | context |',
                     '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
            for c, r in zip(ms['discovery'], conf):
                lines.append(f"| {c['rank']} | {cand_str(c)} | {r['N']} | {V1.f(r['mean_pips'])} | {V1.f(r['mean_R'], 3)} | {r['t_R']:.2f} | {r['t_day']:.2f} | "
                             f"{V1.f(r['gross_R'], 3)} | {V1.f(r['mean_R_2x'], 3)} | {r['blocks_pos']} | {r.get('pairs_pos', '')} | **{r['verdict']}** | {', '.join(r.get('nb', []))} |")
            nconf = sum(r['verdict'] == 'CONFIRMED' for r in conf)
            lines.append(f"\nMonth result: {nconf} CONFIRMED, {len(conf) - nconf} limited.")
            logmd('\n'.join(lines))
        for c, r in zip(ms['discovery'], ms['confirmation']):
            if r['verdict'] != 'CONFIRMED': continue
            if len(st['accepted']) >= TARGET: break
            P = develop(st, c, mon, tables, U)
            if P.get('verdict') == 'ACCEPTED' and P['N'] not in st['accepted']:
                st['accepted'].append(P['N']); L.save_state(st)
        ms['done'] = True; L.save_state(st)
    st['phase'] = 'done'; st['finished'] = L.now_utc(); L.save_state(st)
    logmd(f"\n## v2 loop finished {st['finished']}: months tried {len(st['months'])}, candidate tests v1+v2 {st['n_tests']}, accepted methods {st['accepted']}\n")
    print('done', st['accepted'])

if __name__ == '__main__':
    main()
