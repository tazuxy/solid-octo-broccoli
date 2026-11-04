"""Round 7 automated edge-discovery loop (resumable). Run: python3 -I r7_loop.py
State: out/r7_state.json; log: out/r7_loop_log.md. Every step is skipped if its result is already in the state."""
import os, sys, json, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r7_lib as L, r7_dev as D
from r7_lib import logmd

T_MIN = 3.2; N_MIN = 8; MAX_MONTHS = 12; TARGET = 2
CAL = ('F1', 'F2', 'F3', 'F7', 'F8')

def f(x, p=2):
    return 'nan' if x is None or (isinstance(x, float) and not np.isfinite(x)) else f'{x:+.{p}f}'

def load_pool():
    parts = []
    for inst in L.INSTS:
        U = L.pool_units(inst); parts.append(U)
    U = pd.concat(parts, ignore_index=True)
    assert U.te.max() <= L.POOL_END and U.t.max() < L.POOL_END
    return U

def discover(U, mon):
    m = U[U.month == mon]
    rows = []
    for d in (1, -1):
        net = d * m.gross.values - m.cost.values
        x = pd.DataFrame({'inst': m.inst.values, 'param': m.param.values, 'tid': m.tid.values, 'net': net, 'netR': net / m.R.values})
        g = x.groupby(['inst', 'param'], observed=True)
        a = g.agg(n=('netR', 'size'), ntr=('tid', 'nunique'), mR=('netR', 'mean'), sR=('netR', 'std'), sumP=('net', 'sum'), sumR=('netR', 'sum')).reset_index()
        a['d'] = d; rows.append(a)
    A = pd.concat(rows, ignore_index=True)
    A['t'] = A.mR / (A.sR / np.sqrt(A.n)); A['trade_mean_pips'] = A.sumP / A.ntr; A['trade_mean_R'] = A.sumR / A.ntr
    fam = A.param.str[:2]
    ok = (A.n >= N_MIN) & np.where(fam.isin(CAL), A.ntr >= 3, True)
    ok &= ~np.array([L.excluded(i, p) for i, p in zip(A.inst, A.param)])
    A = A[ok & np.isfinite(A.t)].sort_values('t', ascending=False)
    n_scanned = int(len(A))
    top = A.head(10)
    cands = [dict(rank=k + 1, inst=r.inst, param=r.param, d=int(r.d), n_units=int(r.n), n_trades=int(r.ntr), t=float(r.t),
                  mean_pips=float(r.trade_mean_pips), mean_R=float(r.trade_mean_R)) for k, r in enumerate(top.itertuples())]
    return cands, n_scanned

def block_of(ts):
    y = pd.to_datetime(ts).dt.year.values
    return np.select([y <= 2008, y <= 2012, y <= 2016], ['2005-08', '2009-12', '2013-16'], '2017-21')

def confirm(U, c, mon):
    T = L.trades_of(U, c['inst'], c['param'], c['d']); T = T[T.month != mon]
    T['netR2'] = (T.gross - 2 * T.cost) / T.R
    s = L.tstats(T.netR); sp = L.tstats(T.net)
    T['blk'] = block_of(T.t_ent); bl = T.groupby('blk').netR.agg(['mean', 'size'])
    nblk = len(bl); npos = int((bl['mean'] > 0).sum())
    need = 3 if nblk >= 3 else nblk
    res = dict(N=s['N'], mean_R=s['mean'], t_R=s['t'], mean_pips=sp['mean'], t_pips=sp['t'], gross_R=float((T.gross / T.R).mean()),
               mean_R_2x=float(T.netR2.mean()), blocks={k: [float(v['mean']), int(v['size'])] for k, v in bl.iterrows()},
               blocks_pos=f'{npos}/{nblk}')
    res['crit'] = dict(mean_pos=bool(s['mean'] > 0 and sp['mean'] > 0), t=bool(s['t'] >= T_MIN), blocks=bool(npos >= need),
                       cost2x=bool(res['mean_R_2x'] > 0))
    res['verdict'] = 'CONFIRMED' if all(res['crit'].values()) else 'limited'
    # neighbours: same feature bucket & direction on the other instruments; adjacent hours for F1
    nb = []
    for inst in L.INSTS:
        if inst == c['inst']: continue
        Tn = L.trades_of(U, inst, c['param'], c['d']); Tn = Tn[Tn.month != mon]
        if len(Tn) < 30: continue
        q = L.tstats(Tn.netR); nb.append((inst, q['mean'], q['t']))
    res['nb_other_inst_pos'] = f"{sum(1 for x in nb if x[1] > 0)}/{len(nb)}"
    res['nb_other_inst_t>=2'] = [f'{i} {f(m, 3)}R t{t:.1f}' for i, m, t in sorted(nb, key=lambda z: -z[2]) if t >= 2][:6]
    if c['param'].startswith('F1_h'):
        h = int(c['param'][4:]); adj = []
        for hh in ((h - 1) % 24, (h + 1) % 24):
            Tn = L.trades_of(U, c['inst'], f'F1_h{hh:02d}', c['d']); Tn = Tn[Tn.month != mon]; q = L.tstats(Tn.netR)
            adj.append(f'h{hh:02d} {f(q["mean"], 3)}R t{q["t"]:.1f}')
        res['nb_adjacent_hours'] = adj
    return res

def cand_key(c): return f"{c['inst']}|{c['param']}|{'L' if c['d'] > 0 else 'S'}"

def rule_text(c):
    p = c['param']; side = 'long' if c['d'] > 0 else 'short'
    fol = 'follow' if c['d'] > 0 else 'fade'
    if p.startswith('F1_h'): return f"{side} {c['inst']} from {p[4:]}:00 to {int(p[4:]) + 1:02d}:00 EST every day (H1 bar open->close)"
    if p.startswith('F2_'):
        _, dw, b = p.split('_'); return f"{side} {c['inst']} on {dw} (EST date) from {b}:00 to {int(b) + 4:02d}:00 EST"
    if p.startswith('F3_'):
        _, g, s = p.split('_'); hrs = {'Asia': '19:00-02:00', 'London': '02:00-08:00', 'NY': '08:00-17:00'}[s]
        return f"{side} {c['inst']} through the {s} session ({hrs} EST) on FX trading dates (day rolls 17:00 EST) with day-of-month {g[1:]}"
    if p == 'F8_sun4': return f"{side} {c['inst']} for the first 4 hours after the Sunday open"
    if p == 'F8_mon0211': return f"{side} {c['inst']} Monday 02:00-11:00 EST"
    if p == 'F7_follow':
        return f"{c['inst']} next H1 bar in the {'same' if c['d'] > 0 else 'opposite'} direction as the previous-hour USD basket implies (usd_side={L.usd_side(c['inst'])})"
    if p.startswith('F4_h'): return f"{c['inst']} after an H1 bar with |close-open| > 2xATR14(prev): {'continuation' if c['d'] > 0 else 'reversal'}, enter next bar open, hold {int(p[4:])}h"
    if p.startswith('F5_'): return f"{c['inst']} H1 state {p[3:]} at bar close -> {fol} for 4h from next bar open (one position at a time)"
    if p.startswith('F9_s'): return f"{c['inst']} after exactly {p[4:]} same-colour H1 candles -> {fol} for 4h"
    if p == 'F6_follow': return f"{c['inst']} first M5 close beyond the 19:00-02:00 EST Asia range during 02:00-06:00 -> {fol} at next bar open, exit 11:00 EST"
    return p

def promoted_trades(st):
    """trade lists (pool) of method 1 and of every promoted method (accepted or not) for the duplicate check."""
    out = {'method1': D.method1_trades(L.POOL_END)}
    for k, v in st['promotions'].items():
        fp = os.path.join(L.OUT, f"r7_method{v['N']}_pool_trades.parquet")
        if os.path.exists(fp): out[f"method{v['N']}"] = pd.read_parquet(fp)
    return out

def develop(U, st, c, mon):
    key = cand_key(c); P = st['promotions'].setdefault(key, {'cand': c, 'month': mon, 'steps': {}})
    sp = P['steps']; inst = c['inst']
    if 'N' not in P:
        P['N'] = 2 + sum(1 for k, v in st['promotions'].items() if 'N' in v); L.save_state(st)
    N = P['N']; tfp = os.path.join(L.OUT, f'r7_method{N}_pool_trades.parquet')
    # step 1: base trades + stop choice (2005-2021)
    if 'stop' not in sp:
        T0 = L.trades_of(U, inst, c['param'], c['d'])
        res = {}
        for k in (None, 2, 3):
            Tk = D.apply_stop(T0, inst, k, L.POOL_END); res[str(k)] = D.full_stats(Tk)
        best = max((None, 2, 3), key=lambda k: res[str(k)]['ratio'])
        choice = best if (best is not None and res[str(best)]['ratio'] >= 1.1 * res['None']['ratio']) else None
        sp['stop'] = dict(choice=choice, table=res); L.save_state(st)
        logmd(f"- [{L.now_utc()}] DEV method{N} {key}: stop table (2005-2021, netR) " +
              '; '.join(f"{k}: mean {f(v['mean_R'], 3)} t {v['t']:.2f} ratio {v['ratio']:.2f}" for k, v in res.items()) + f" -> stop = {choice}")
    k = sp['stop']['choice']
    T = D.add_features(D.apply_stop(L.trades_of(U, inst, c['param'], c['d']), inst, k, L.POOL_END), inst, L.POOL_END)
    # step 2: refinement chosen on 2005-2014, frozen, then confirmed on 2015-2021
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
        if choice is None: ok, info = False, {}
        else: ok, info = D.confirm_refinement(T, choice)
        sp['refine_confirm'] = dict(ok=ok, info=info, adopted=choice if ok else None); L.save_state(st)
        logmd(f"- [{L.now_utc()}] DEV method{N}: refinement confirmation 2015-2021: {'CONFIRMED' if ok else 'not adopted'} {info}")
    adopted = sp['refine_confirm']['adopted']
    TF = D.apply_refinement(T, adopted); TF.to_parquet(tfp)
    # step 3: duplicate check vs method 1 and every earlier promoted method (daily returns, 2005-2021)
    if 'corr' not in sp:
        cors = {}
        for nm, Tb in promoted_trades(st).items():
            if nm == f'method{N}': continue
            cors[nm] = D.daily_corr(TF, Tb)
        dup = [nm for nm, v in cors.items() if v > 0.5]
        sp['corr'] = dict(corr=cors, dup=dup); L.save_state(st)
        logmd(f"- [{L.now_utc()}] DEV method{N}: daily-return correlation (2005-2021) {', '.join(f'{a} {b:+.2f}' for a, b in cors.items())}" +
              (f" -> DUPLICATE of {dup}: skipped" if dup else ''))
    if sp['corr']['dup']:
        P['verdict'] = 'skipped (duplicate)'; L.save_state(st); return P
    # step 4: freeze
    ffp = os.path.join(L.OUT, f'r7_method{N}_frozen.json')
    if 'frozen' not in sp:
        pool = D.full_stats(TF)
        fz = dict(frozen_utc=L.now_utc(), method=N, discovered_in=mon, candidate=c, rule=rule_text(c), instrument=inst,
                  cost_pips_round_trip=L.COST[inst], R='0.25 x D1 ATR(14) of the last closed D1 bar at entry',
                  stop=None if k is None else f'{k}R', refinement=adopted, pool_2005_2021=pool,
                  acceptance=dict(holdout_mean_gt0=True, holdout_ge_25pct_pool=True, full_t_ge=3.0, full_ratio_ge=3.0))
        json.dump(fz, open(ffp, 'w'), indent=1, default=float)
        sp['frozen'] = dict(ts=fz['frozen_utc'], pool=pool); L.save_state(st)
        logmd(f"- [{fz['frozen_utc']}] FROZEN method{N} -> r7_method{N}_frozen.json: {fz['rule']}; stop {fz['stop']}; refinement {adopted}; "
              f"pool N {pool['N']} mean {f(pool['mean_R'], 3)}R ({f(pool['mean_pips'])} pips) t {pool['t']:.2f} ratio {pool['ratio']:.2f}")
    # step 5: one-shot holdout
    if 'holdout' not in sp:
        ts = L.now_utc()
        if 'holdout_started' not in sp:
            sp['holdout_started'] = ts; L.save_state(st)
        logmd(f"- [{ts}] HOLDOUT EVALUATION START method{N} (2022-01..2024-12), rules frozen at {sp['frozen']['ts']}")
        open(os.path.join(L.OUT, 'r7_holdout_timeline.log'), 'a').write(f'{ts} START holdout method{N} {key} (frozen {sp["frozen"]["ts"]})\n')
        L.unlock_holdout(ffp)
        try:
            Uf = L.build_units(inst, L.HOLD_END)
            Tf = L.trades_of(Uf, inst, c['param'], c['d'])
            Tf = D.add_features(D.apply_stop(Tf, inst, k, L.HOLD_END), inst, L.HOLD_END)
            Tf = D.apply_refinement(Tf, adopted)
        finally:
            L.lock_holdout()
        Tf.to_parquet(os.path.join(L.OUT, f'r7_method{N}_full_trades.parquet'))
        H = Tf[Tf.t_ent >= L.POOL_END]; Pl = Tf[Tf.t_ent < L.POOL_END]
        hs = D.full_stats(H); ps = D.full_stats(Pl); fs = D.full_stats(Tf)
        crit = dict(holdout_mean_gt0=bool(hs['mean_R'] > 0), holdout_ge_25pct=bool(hs['mean_R'] >= 0.25 * ps['mean_R']),
                    full_t=bool(fs['t'] >= 3.0), full_ratio=bool(fs['ratio'] >= 3.0))
        acc = all(crit.values())
        sp['holdout'] = dict(ts=L.now_utc(), holdout=hs, pool=ps, full=fs, crit=crit, accepted=acc); L.save_state(st)
        json.dump(sp['holdout'], open(os.path.join(L.OUT, f'r7_method{N}_holdout.json'), 'w'), indent=1, default=float)
        open(os.path.join(L.OUT, 'r7_holdout_timeline.log'), 'a').write(f'{sp["holdout"]["ts"]} DONE holdout method{N} accepted={acc}\n')
        logmd(f"- [{sp['holdout']['ts']}] HOLDOUT method{N}: N {hs['N']} mean {f(hs['mean_R'], 3)}R ({f(hs['mean_pips'])} pips) t {hs['t']:.2f} | "
              f"pool mean {f(ps['mean_R'], 3)}R | full 2005-2024 t {fs['t']:.2f} ratio {fs['ratio']:.2f} | crit {crit} -> "
              f"{'ACCEPTED' if acc else 'failed holdout'}")
    P['verdict'] = 'ACCEPTED' if sp['holdout']['accepted'] else 'failed holdout'
    L.save_state(st); return P

def main():
    st = L.load_state()
    if st is None:
        pool = [y * 100 + m for y in range(2005, 2022) for m in range(1, 13)]
        rng = np.random.default_rng(42)
        order = [int(x) for x in rng.choice(np.array(pool), size=MAX_MONTHS, replace=False)]
        st = dict(created=L.now_utc(), phase='loop', month_order=order, months={}, promotions={}, n_tests=0, accepted=[])
        L.save_state(st)
        logmd(f"# Round 7 loop log\n\nCreated {st['created']}. Pool 2005-01..2021-12 (204 months); holdout 2022-01..2024-12 locked in code.\n"
              f"Month draw: numpy default_rng(42).choice(204 pool months, 12, replace=False) = {order}\n"
              f"Confirmation: net mean>0 (0.5 pip; XAU 0.30 USD), t(netR)>=3.2, >=3/4 blocks positive, 2x cost mean>0.\n")
    if st['phase'] == 'done':
        print('loop already finished'); return
    U = load_pool()
    U['param'] = U.param.astype('category'); U['inst'] = U.inst.astype('category')
    for k, mon in enumerate(st['month_order']):
        if len(st['accepted']) >= TARGET: break
        ms = st['months'].setdefault(str(mon), {})
        if ms.get('done'): continue
        if 'discovery' not in ms:
            cands, nsc = discover(U, mon)
            ms['discovery'] = cands; ms['n_scanned'] = nsc; ms['k'] = k + 1; L.save_state(st)
            lines = [f"\n## Month {k + 1}: {str(mon)[:4]}-{str(mon)[4:]}  (discovery {L.now_utc()}; {nsc} instrument x bucket x direction candidates with >=8 events)\n",
                     '| # | inst | feature | dir | units | trades | in-month t | mean net pips/trade | mean net R/trade |', '|---|---|---|---|---|---|---|---|---|']
            for c in cands:
                lines.append(f"| {c['rank']} | {c['inst']} | {c['param']} | {'L/follow' if c['d'] > 0 else 'S/fade'} | {c['n_units']} | {c['n_trades']} | {c['t']:.2f} | {f(c['mean_pips'], 1)} | {f(c['mean_R'], 3)} |")
            logmd('\n'.join(lines))
        if 'confirmation' not in ms:
            conf = []
            for c in ms['discovery']:
                r = confirm(U, c, mon); conf.append(r)
            ms['confirmation'] = conf; st['n_tests'] += len(conf); L.save_state(st)
            lines = [f"\nConfirmation on the other 203 pool months ({L.now_utc()}); running test count = {st['n_tests']}\n",
                     '| # | inst | feature | dir | N | mean pips | mean R | t(R) | gross R | 2x-cost R | blocks + | verdict | other inst + | neighbours t>=2 |',
                     '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
            for c, r in zip(ms['discovery'], conf):
                nbs = ', '.join(r['nb_other_inst_t>=2'] + r.get('nb_adjacent_hours', []))
                lines.append(f"| {c['rank']} | {c['inst']} | {c['param']} | {'L/follow' if c['d'] > 0 else 'S/fade'} | {r['N']} | {f(r['mean_pips'])} | {f(r['mean_R'], 3)} | {r['t_R']:.2f} | "
                             f"{f(r['gross_R'], 3)} | {f(r['mean_R_2x'], 3)} | {r['blocks_pos']} | **{r['verdict']}** | {r['nb_other_inst_pos']} | {nbs} |")
            nconf = sum(r['verdict'] == 'CONFIRMED' for r in conf)
            lines.append(f"\nMonth result: {nconf} CONFIRMED, {len(conf) - nconf} limited.")
            logmd('\n'.join(lines))
        for c, r in zip(ms['discovery'], ms['confirmation']):
            if r['verdict'] != 'CONFIRMED': continue
            if len(st['accepted']) >= TARGET: break
            P = develop(U, st, c, mon)
            if P.get('verdict') == 'ACCEPTED' and P['N'] not in st['accepted']:
                st['accepted'].append(P['N']); L.save_state(st)
        ms['done'] = True; L.save_state(st)
    st['phase'] = 'done'; st['finished'] = L.now_utc(); L.save_state(st)
    nm = len(st['months']); logmd(f"\n## Loop finished {st['finished']}: months tried {nm}, candidate tests {st['n_tests']}, accepted methods {st['accepted']}\n")
    print('done', st['accepted'])

if __name__ == '__main__':
    main()
