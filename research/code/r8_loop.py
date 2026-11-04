"""Round 8 edge-discovery loop: the round-7 library-v2 loop (r7_v2loop.py + r7_lib.py + r7_dev.py + r7_v2feat.py, reused by
import) with a 12-month DISCOVERY WINDOW (one calendar year) instead of one month. Resumable. Run: python3 -I r8_loop.py
Changes vs round 7 (everything else is the round-7 code):
  * window = calendar year drawn from 2005..2021 with numpy default_rng(8), without replacement, at most 8 windows
  * >= 30 events in the window; top 20 by window t (daily P&L t with variance floor, net 0.5 pip / gold 0.30)
  * v1 features (F1-F9) are ranked on the same daily-P&L t with a variance floor (round 7 ranked v1 on unit t) and need
    >= 30 TRADES in the window (round 7 counted held H1 bars for calendar features because a month had too few trades)
  * confirmation on the other 16 pool years: min(trade t, daily t) >= 3.4; >= 3/4 blocks positive (the discovery year is
    simply absent from its block); 2x cost > 0; pooled >= 60% of pairs positive; NEW rollover-hour check (see hour_check)
  * duplicate check before freezing: daily-return corr <= 0.5 vs method 1 and every earlier round-8 promoted method
State: out/r8_state.json; log: out/r8_loop_log.md; holdout timeline: out/r8_holdout_timeline.log."""
import os, sys, json, warnings, numpy as np, pandas as pd
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r7_lib as L, r7_dev as D, r7_v2feat as V, r7_v2loop as VL, r7_loop as V1
from r7_lib import logmd

# ---- parametrise the round-7 modules for round 8 ----
L.STATE = os.path.join(L.OUT, 'r8_state.json'); L.LOG = os.path.join(L.OUT, 'r8_loop_log.md')
N_MIN = 30; T_MIN = 3.4; TOPK = 20; MAX_WIN = 8; TARGET = 2; SEED = 8
VL.N_MIN = N_MIN; VL.T_MIN = T_MIN; VL.TOPK = TOPK
POOL_YEARS = list(range(2005, 2022))
ROLL_ADJ = (16, 17, 18)          # EST hours adjacent to the 17:00 EST rollover
f = V1.f

def year_slice(T, tf, y):
    parts = [df[df.month // 100 == y] for df in T[tf].values()]
    return pd.concat([p for p in parts if len(p)], ignore_index=True)
VL.month_slice = year_slice      # discover_v2(T, y) now scans the calendar year y

# ---------------- v1 discovery on a year (daily-P&L t with variance floor, >= 30 trades) ----------------
def discover_v1_year(U, y):
    m = U[U.year == y]; rows = []
    for d in (1, -1):
        net = d * m.gross.values - m.cost.values
        x = pd.DataFrame({'inst': m.inst.values.astype(str), 'param': m.param.values.astype(str), 'tid': m.tid.values, 'net': net,
                          'netR': net / m.R.values, 'day': m.t_ent.values.astype('datetime64[D]')})
        tr = x.groupby(['inst', 'param', 'tid'], sort=False).agg(net=('net', 'sum'), netR=('netR', 'sum'), day=('day', 'first')).reset_index()
        tr['fam'] = tr.param.str[:2]
        floor = tr.groupby('fam').netR.std()                         # window-wide per-trade SD of each v1 family
        dy = tr.groupby(['inst', 'param', 'day'], sort=False).netR.sum().reset_index()
        g = dy.groupby(['inst', 'param']).netR.agg(days='size', md='mean', sd='std').reset_index()
        tg = tr.groupby(['inst', 'param']).agg(ntr=('tid', 'size'), sumP=('net', 'sum'), sumR=('netR', 'sum')).reset_index()
        a = g.merge(tg, on=['inst', 'param']); a['fl'] = a.param.str[:2].map(floor)
        a['t'] = a.md / (np.maximum(a.sd, a.fl) / np.sqrt(a.days)); a['d'] = d; rows.append(a)
    A = pd.concat(rows, ignore_index=True)
    ok = (A.ntr >= N_MIN) & (A.days >= 3) & np.isfinite(A.t)
    ok &= ~np.array([L.excluded(i, p) for i, p in zip(A.inst, A.param)])
    A = A[ok].sort_values('t', ascending=False)
    cands = [dict(inst=r.inst, param=r.param, d=int(r.d), n_units=int(r.ntr), n_trades=int(r.ntr), t=float(r.t),
                  mean_pips=float(r.sumP / r.ntr), mean_R=float(r.sumR / r.ntr)) for r in A.head(TOPK).itertuples()]
    return cands, int(len(A))

def discover_all(T, U, y):
    c2, n2 = VL.discover_v2(T, y)
    c1, n1 = discover_v1_year(U, y)
    for c in c1:
        c.update(kind='v1', tf='H1' if c['param'][:2] != 'F6' else 'M5', trig=c['param'], conds={}, out='-', n=c['n_trades'])
    allc = sorted(c1 + c2, key=lambda z: -z['t'])[:TOPK]
    for k, c in enumerate(allc): c['rank'] = k + 1
    return allc, n1 + n2

# ---------------- rollover-hour profile ----------------
def hour_check(T):
    """reject if the effect is concentrated in an hour adjacent to the 17:00 EST rollover: (a) one hour in 16-18 EST
    (by entry or exit hour) holds >= 50% of the total net R, or (b) the trades that neither enter nor exit in 16:00-18:59
    EST have mean net R <= 0 (or fewer than 30 trades)."""
    if len(T) < 3: return dict(ok=False, txt='no trades')
    eh = pd.to_datetime(T.t_ent).dt.hour.values; xh = pd.to_datetime(T.t_exit).dt.hour.values; r = T.netR.values; tot = r.sum()
    pe = pd.Series(r).groupby(eh).sum(); px = pd.Series(r).groupby(xh).sum()
    share = {h: (max(pe.get(h, 0.0), px.get(h, 0.0)) / tot if tot > 0 else np.nan) for h in ROLL_ADJ}
    conc = bool(tot > 0 and np.nanmax(list(share.values())) >= 0.5)
    adj = np.isin(eh, ROLL_ADJ) | np.isin(xh, ROLL_ADJ); ex = r[~adj]
    mex = float(ex.mean()) if len(ex) else np.nan
    ok = (not conc) and len(ex) >= 30 and mex > 0
    top = pe.sort_values(ascending=False).head(3)
    txt = (f"entry-hour top {', '.join(f'{int(h):02d}h {v:+.0f}R' for h, v in top.items())}; max 16-18h share "
           f"{np.nanmax(list(share.values())) if tot > 0 else float('nan'):.2f}; ex-16-18h N {len(ex)} mean {f(mex, 3)}R")
    return dict(ok=bool(ok), conc=conc, share={str(k): float(v) for k, v in share.items()}, ex_N=int(len(ex)), ex_mean=mex,
                profile_entry={str(int(k)): float(v) for k, v in pe.items()}, txt=txt)

# ---------------- confirmation on the other pool years ----------------
def confirm_v2_year(tables, c, y):
    T = VL.v2_trades(tables, c, VL.insts_of(c)); T = T[T.month // 100 != y]
    s = VL.V1_stats(T)
    if c['inst'] == 'POOL':
        per = T.groupby('inst').netR.agg(['mean', 'size']); per = per[per['size'] >= 20]
        frac = float((per['mean'] > 0).mean()) if len(per) else 0.0
        s['pairs_pos'] = f"{int((per['mean'] > 0).sum())}/{len(per)}"; s['crit']['pairs60'] = bool(frac >= VL.POOL_FRAC)
        s['nb'] = [f"{i} {m:+.3f}R" for i, m in per['mean'].sort_values(ascending=False).head(4).items()]
    else:
        c2 = dict(c, inst='POOL'); Tp = VL.v2_trades(tables, c2, [i for i in L.FX if i != c['inst']]); Tp = Tp[Tp.month // 100 != y]
        per = Tp.groupby('inst').netR.mean()
        s['pairs_pos'] = f"other pairs {int((per > 0).sum())}/{len(per)}"
        q = L.tstats(Tp.netR); s['nb'] = [f"same rule other 16 pairs pooled {q['mean']:+.3f}R t{q['t']:.1f}"] if len(Tp) > 2 else []
    return s, T

def confirm_v1_year(U, c, y):
    T = L.trades_of(U, c['inst'], c['param'], c['d']); T = T[T.month // 100 != y].copy()
    T['netR2'] = (T.gross - 2 * T.cost) / T.R
    s = VL.V1_stats(T); nb = []
    for inst in L.INSTS:
        if inst == c['inst']: continue
        Tn = L.trades_of(U, inst, c['param'], c['d']); Tn = Tn[Tn.month // 100 != y]
        if len(Tn) < 30: continue
        q = L.tstats(Tn.netR); nb.append((inst, q['mean'], q['t']))
    s['pairs_pos'] = f"other inst {sum(1 for x in nb if x[1] > 0)}/{len(nb)}"
    s['nb'] = [f'{i} {f(m, 3)}R t{t:.1f}' for i, m, t in sorted(nb, key=lambda z: -z[2]) if t >= 2][:3]
    if c['param'].startswith('F1_h'):
        h = int(c['param'][4:])
        for hh in ((h - 1) % 24, (h + 1) % 24):
            Tn = L.trades_of(U, c['inst'], f'F1_h{hh:02d}', c['d']); Tn = Tn[Tn.month // 100 != y]; q = L.tstats(Tn.netR)
            s['nb'].append(f'h{hh:02d} {f(q["mean"], 3)}R t{q["t"]:.1f}')
    return s, T

def confirm_any(tables, U, c, y):
    s, T = confirm_v2_year(tables, c, y) if c['kind'] == 'v2' else confirm_v1_year(U, c, y)
    hc = hour_check(T); s['hours'] = hc; s['crit']['not_rollover'] = hc['ok']
    s['verdict'] = 'CONFIRMED' if all(s['crit'].values()) else 'limited'
    return s

# ---------------- development (round-7 protocol, round-8 file names) ----------------
def develop(st, c, y, tables, U):
    key = VL.cand_str(c); P = st['promotions'].setdefault(key, {'cand': c, 'window': y, 'steps': {}}); sp = P['steps']
    if 'N' not in P: P['N'] = 2 + sum(1 for v in st['promotions'].values() if 'N' in v); L.save_state(st)
    N = P['N']; intrinsic = c.get('out') in ('br', 'tb', 'tt')
    T0 = VL.cand_trades(c, tables, U, L.POOL_END)
    if 'stop' not in sp:
        res = {}; opts = [None] if intrinsic else [None, 2, 3]
        for k in opts: res[str(k)] = D.full_stats(VL.stop_and_features(T0, c, k, L.POOL_END))
        best = max(opts, key=lambda k: res[str(k)]['ratio'])
        choice = best if (best is not None and res[str(best)]['ratio'] >= 1.1 * res['None']['ratio']) else None
        sp['stop'] = dict(choice=choice, table=res, intrinsic=intrinsic); L.save_state(st)
        logmd(f"- [{L.now_utc()}] DEV method{N} {key}: stop table (2005-2021, netR) " +
              '; '.join(f"{k}: mean {f(v['mean_R'], 3)} t {v['t']:.2f} ratio {v['ratio']:.2f}" for k, v in res.items()) +
              f" -> stop = {'intrinsic bracket' if intrinsic else choice}")
    k = sp['stop']['choice']
    T = VL.stop_and_features(T0, c, k, L.POOL_END)
    if 'refine_select' not in sp:
        choice, tab, base = D.select_refinement(T)
        tab.to_csv(os.path.join(L.OUT, f'r8_method{N}_refine_table.csv'), index=False)
        fr = dict(frozen_utc=L.now_utc(), method=N, cand=c, stop=k, refinement=choice, selection_base=base,
                  note='chosen on 2005-2014 only, written before any 2015-2021 statistic of the refined rule was computed')
        json.dump(fr, open(os.path.join(L.OUT, f'r8_method{N}_refine.json'), 'w'), indent=1, default=float)
        sp['refine_select'] = dict(choice=choice, ts=fr['frozen_utc']); L.save_state(st)
        logmd(f"- [{fr['frozen_utc']}] DEV method{N}: refinement selected on 2005-2014 = {choice} (frozen r8_method{N}_refine.json)")
    choice = sp['refine_select']['choice']
    if 'refine_confirm' not in sp:
        ok, info = (False, {}) if choice is None else D.confirm_refinement(T, choice)
        sp['refine_confirm'] = dict(ok=ok, info=info, adopted=choice if ok else None); L.save_state(st)
        logmd(f"- [{L.now_utc()}] DEV method{N}: refinement confirmation 2015-2021: {'CONFIRMED' if ok else 'not adopted'} {info}")
    adopted = sp['refine_confirm']['adopted']
    TF = D.apply_refinement(T, adopted); TF.to_parquet(os.path.join(L.OUT, f'r8_method{N}_pool_trades.parquet'))
    if 'corr' not in sp:
        others = {'method1': D.method1_trades(L.POOL_END)}
        for v in st['promotions'].values():
            fp = os.path.join(L.OUT, f"r8_method{v.get('N')}_pool_trades.parquet")
            if v.get('N') not in (None, N) and os.path.exists(fp): others[f"method{v['N']}"] = pd.read_parquet(fp)
        cors = {nm: D.daily_corr(TF, Tb) for nm, Tb in others.items()}
        dup = [nm for nm, v in cors.items() if v > 0.5]
        sp['corr'] = dict(corr=cors, dup=dup); L.save_state(st)
        logmd(f"- [{L.now_utc()}] DEV method{N}: daily-return correlation (2005-2021) {', '.join(f'{a} {b:+.2f}' for a, b in cors.items())}" +
              (f" -> DUPLICATE of {dup}: skipped" if dup else ''))
    if sp['corr']['dup']:
        P['verdict'] = 'skipped (duplicate)'; L.save_state(st); return P
    ffp = os.path.join(L.OUT, f'r8_method{N}_frozen.json')
    insts = VL.insts_of(c) if c['kind'] == 'v2' else [c['inst']]
    if 'frozen' not in sp:
        pool = D.full_stats(TF)
        fz = dict(frozen_utc=L.now_utc(), round=8, library='v2+T+v1', method=N, discovered_in_year=y, candidate=c, rule=VL.rule_text(c),
                  instruments=insts, instrument=insts[0] if len(insts) == 1 else 'POOL', cost_pips_round_trip={i: L.COST[i] for i in insts},
                  R='0.25 x D1 ATR(14) of the last closed D1 bar at entry',
                  stop=('intrinsic bracket' if intrinsic else (None if k is None else f'{k}R')), refinement=adopted, pool_2005_2021=pool,
                  acceptance=dict(holdout_mean_gt0=True, holdout_ge_25pct_pool=True, full_t_ge=3.0, full_ratio_ge=3.0, corr_le=0.5))
        json.dump(fz, open(ffp, 'w'), indent=1, default=float)
        sp['frozen'] = dict(ts=fz['frozen_utc'], pool=pool); L.save_state(st)
        logmd(f"- [{fz['frozen_utc']}] FROZEN method{N} -> r8_method{N}_frozen.json: {fz['rule']}; stop {fz['stop']}; refinement {adopted}; "
              f"pool N {pool['N']} mean {f(pool['mean_R'], 3)}R ({f(pool['mean_pips'])} pips) t {pool['t']:.2f} ratio {pool['ratio']:.2f}")
    if 'holdout' not in sp:
        ts = L.now_utc()
        if 'holdout_started' not in sp: sp['holdout_started'] = ts; L.save_state(st)
        logmd(f"- [{ts}] HOLDOUT EVALUATION START method{N} (2022-01..2024-12), rules frozen at {sp['frozen']['ts']}")
        open(os.path.join(L.OUT, 'r8_holdout_timeline.log'), 'a').write(f'{ts} START holdout method{N} {key} (frozen {sp["frozen"]["ts"]})\n')
        L.unlock_holdout(ffp)
        try:
            if c['kind'] == 'v2':
                full = {c['tf']: {}}
                for inst in insts: full[c['tf']][inst] = V.build_inst(inst, L.HOLD_END)[c['tf']]
                Tf = VL.v2_trades(full, c, insts)
            else:
                Uf = VL.v1_filter(L.build_units(c['inst'], L.HOLD_END)); Tf = VL.cand_trades(c, None, Uf, L.HOLD_END)
            Tf = D.apply_refinement(VL.stop_and_features(Tf, c, k, L.HOLD_END), adopted)
        finally:
            L.lock_holdout()
        Tf.to_parquet(os.path.join(L.OUT, f'r8_method{N}_full_trades.parquet'))
        H = Tf[Tf.t_ent >= L.POOL_END]; Pl = Tf[Tf.t_ent < L.POOL_END]
        hs, ps, fs = D.full_stats(H), D.full_stats(Pl), D.full_stats(Tf)
        fs['t_day'] = L.tstats(Tf.groupby(pd.to_datetime(Tf.t_ent).dt.normalize()).netR.sum().values)['t']
        crit = dict(holdout_mean_gt0=bool(hs['mean_R'] > 0 and hs['mean_pips'] > 0), holdout_ge_25pct=bool(hs['mean_R'] >= 0.25 * ps['mean_R']),
                    full_t=bool(min(fs['t'], fs['t_day']) >= 3.0), full_ratio=bool(fs['ratio'] >= 3.0))
        acc = all(crit.values())
        sp['holdout'] = dict(ts=L.now_utc(), holdout=hs, pool=ps, full=fs, crit=crit, accepted=acc); L.save_state(st)
        json.dump(sp['holdout'], open(os.path.join(L.OUT, f'r8_method{N}_holdout.json'), 'w'), indent=1, default=float)
        open(os.path.join(L.OUT, 'r8_holdout_timeline.log'), 'a').write(f'{sp["holdout"]["ts"]} DONE holdout method{N} accepted={acc}\n')
        logmd(f"- [{sp['holdout']['ts']}] HOLDOUT method{N}: N {hs['N']} mean {f(hs['mean_R'], 3)}R ({f(hs['mean_pips'])} pips) t {hs['t']:.2f} | "
              f"pool mean {f(ps['mean_R'], 3)}R | full 2005-2024 t {fs['t']:.2f} (daily {fs['t_day']:.2f}) ratio {fs['ratio']:.2f} | crit {crit} -> "
              f"{'ACCEPTED' if acc else 'failed holdout'}")
    P['verdict'] = 'ACCEPTED' if sp['holdout']['accepted'] else 'failed holdout'; L.save_state(st); return P

# ---------------- main ----------------
def main():
    st = L.load_state()
    if st is None:
        order = [int(x) for x in np.random.default_rng(SEED).choice(np.array(POOL_YEARS), size=MAX_WIN, replace=False)]
        st = dict(created=L.now_utc(), round=8, phase='loop', window='calendar year', year_order=order, windows={}, promotions={},
                  n_tests=0, accepted=[])
        L.save_state(st)
        logmd(f"# Round 8 loop log (12-month discovery windows)\n\nCreated {st['created']}. Pool years 2005..2021; final holdout 2022-01..2024-12 locked in code "
              f"(r7_lib.unlock_holdout needs the frozen file).\n"
              f"Window draw: numpy default_rng({SEED}).choice(2005..2021, {MAX_WIN}, replace=False) = {order}\n"
              f"Library: round-7 library v2 (C candles, I indicators, Z zones, D Dow, T counter-trendlines, X combinations; per pair and pooled 17 FX) "
              f"+ v1 F1-F9, exactly as in r7 (code imported from r7_v2feat/r7_v2loop/r7_lib; pool tables from out/r7_cache).\n"
              f"Discovery: >= {N_MIN} events in the year, rank by window t on DAILY net P&L with variance floor (0.5 pip; XAU 0.30 USD), duplicate event sets removed, top {TOPK}. "
              f"v1 features now also use daily-P&L t with a per-family variance floor and need >= {N_MIN} trades (round 7: unit t, >= 8 units).\n"
              f"Confirmation on the other 16 pool years: net mean > 0 (pips and R); min(trade t, daily t) >= {T_MIN} (~160 tests, one-sided 5% Bonferroni); "
              f">= 3/4 blocks positive (2005-08, 2009-12, 2013-16, 2017-21; the discovery year is excluded from its block); 2x cost > 0; pooled rules >= 60% of pairs; "
              f"NOT concentrated in a rollover-adjacent hour (no 16/17/18 EST entry-or-exit hour with >= 50% of total net R, and trades not entering/exiting 16:00-18:59 EST keep mean > 0 with >= 30 trades).\n"
              f"Rollover validity rule (r7): no entry/exit price stamped 16:55-17:30 EST; bracket checks ignore the 17:00 bar.\n"
              f"Development/holdout exactly as round 7 (one refinement chosen on 2005-2014, checked 2015-2021; freeze r8_method{{N}}_frozen.json; one holdout look 2022-2024; "
              f"accept: holdout net > 0, holdout mean >= 25% of pool mean, full 2005-2024 min(t, daily t) >= 3.0, sum/|maxDD| >= 3; daily corr <= 0.5 vs method 1 and earlier round-8 methods).\n"
              f"NOTE on the holdout: 2022-2024 was already looked at twice in round 7, for the two REJECTED rollover rules (AUDNZD short 16h, EURAUD long 17h); "
              f"it is unused for every other rule. Method 1 has also seen it in earlier rounds.\n")
    if st['phase'] == 'done': print('done already'); return
    tables = VL.load_tables()
    U = VL.v1_filter(V1.load_pool()); U['year'] = U.month // 100
    U['param'] = U.param.astype('category'); U['inst'] = U.inst.astype('category')
    for k, y in enumerate(st['year_order']):
        if len(st['accepted']) >= TARGET: break
        ws = st['windows'].setdefault(str(y), {})
        if ws.get('done'): continue
        if 'discovery' not in ws:
            cands, nsc = discover_all(tables, U, y)
            ws['discovery'] = cands; ws['n_scanned'] = nsc; ws['k'] = k + 1; L.save_state(st)
            lines = [f"\n## Window {k + 1}: {y}  (discovery {L.now_utc()}; {nsc} candidate rows with >= {N_MIN} events and window t > 2.5 [v2] / any t [v1])\n",
                     '| # | candidate | family | events | window t | window mean net R |', '|---|---|---|---|---|---|']
            for c in cands:
                lines.append(f"| {c['rank']} | {VL.cand_str(c)} | {VL.family_of(c)} | {c['n']} | {c['t']:.2f} | {f(c['mean_R'], 3)} |")
            logmd('\n'.join(lines))
        if 'confirmation' not in ws:
            conf = []
            for c in ws['discovery']:
                conf.append(confirm_any(tables, U, c, y))
            ws['confirmation'] = conf; st['n_tests'] += len(conf); L.save_state(st)
            lines = [f"\nConfirmation on the other 16 pool years ({L.now_utc()}); running test count = {st['n_tests']}\n",
                     '| # | candidate | N | mean pips | mean R | t trades | t daily | gross R | 2x-cost R | blocks + | pairs + | rollover-hour check | verdict | context |',
                     '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
            for c, r in zip(ws['discovery'], conf):
                lines.append(f"| {c['rank']} | {VL.cand_str(c)} | {r['N']} | {f(r['mean_pips'])} | {f(r['mean_R'], 3)} | {r['t_R']:.2f} | {r['t_day']:.2f} | "
                             f"{f(r['gross_R'], 3)} | {f(r['mean_R_2x'], 3)} | {r['blocks_pos']} | {r.get('pairs_pos', '')} | "
                             f"{'ok' if r['hours']['ok'] else 'FAIL'}: {r['hours']['txt']} | **{r['verdict']}** | {', '.join(r.get('nb', []))} |")
            nconf = sum(r['verdict'] == 'CONFIRMED' for r in conf)
            tt = np.array([r['t_used'] for r in conf], float)
            lines.append(f"\nWindow result: {nconf} CONFIRMED, {len(conf) - nconf} limited. Confirmation t of the 20 winners: median {np.nanmedian(tt):.2f}, "
                         f">0: {int((tt > 0).sum())}, >2: {int((tt > 2).sum())}, >={T_MIN}: {int((tt >= T_MIN).sum())}.")
            logmd('\n'.join(lines))
        for c, r in zip(ws['discovery'], ws['confirmation']):
            if r['verdict'] != 'CONFIRMED': continue
            if len(st['accepted']) >= TARGET: break
            P = develop(st, c, y, tables, U)
            if P.get('verdict') == 'ACCEPTED' and P['N'] not in st['accepted']:
                st['accepted'].append(P['N']); L.save_state(st)
        ws['done'] = True; L.save_state(st)
    st['phase'] = 'done'; st['finished'] = L.now_utc(); L.save_state(st)
    logmd(f"\n## Round 8 loop finished {st['finished']}: windows tried {len(st['windows'])}, candidate tests {st['n_tests']}, accepted methods {st['accepted']}\n")
    print('done', st['accepted'])

if __name__ == '__main__':
    main()
