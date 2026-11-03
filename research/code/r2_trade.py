"""Round 2, per-trade candidates P4 (Donchian H4 N50, channel-25 exit, SL 2 ATR, skip ATR ratio < 0.8, monthly -5R stop)
and P5 (divergence rules C and E). Exact round-0 code is reused:
  * Donchian: fam_screen.prep / fam_screen.run with the 'F1 Donchian N50 exit chan25 H4' lines copied verbatim;
    filters + month stop = fam_combo.final_rules(atr_skip=True, hour_skip=False, month=True)  (= fam_portfolio.rules, no max_pos).
  * Divergence: holdout.job (bt.build + bt.simulate) without its feature-file side effect; rules from holdout_iter.RULES.
Parametrisation only: data directory (sig.BARS) and first bar (load start, bt.BUILD_FROM).
Modes: 'rep' = bars/, original starts (must reproduce rounds 0 exactly);  'full' = bars_full/, start 2004 (continuous 2005-2024).
usage: python -I code/r2_trade.py"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import sig, bt, fam_screen
from fam_common import tag, DESIGN, CROSS, ALL, OUT, stats, select
from fam_screen import b as _b
import holdout, holdout_iter
from port import no_overlap
from multiprocessing import Pool
_orig_load = sig.load

def configure(mode):
    if mode == 'full':
        sig.BARS = os.path.join(sig.ROOT, 'bars_full')
        f = lambda pair, tf, start=None: _orig_load(pair, tf, start='2004-01-01')
        bt.load = f; fam_screen.load = f; bt.BUILD_FROM = '2004-01-01'

def donch(args):
    mode, pair = args; configure(mode)
    P = fam_screen.prep(pair, 'H4'); h, l, c = pd.Series(P['h']), pd.Series(P['l']), P['c']
    N = 50          # --- verbatim from fam_screen.worker (F1 Donchian, H4, N=50, exit chan N//2) ---
    hiN = h.rolling(N).max().shift(1).values; loN = l.rolling(N).min().shift(1).values
    hx = h.rolling(N // 2).max().shift(1).values; lx = l.rolling(N // 2).min().shift(1).values
    buy, sell = c > hiN, c < loN
    tr = fam_screen.run(P, pair, buy, sell, sl_atr=2, exit_long=_b(c < lx), exit_short=_b(c > hx), max_bars=2000)
    return tr.assign(fam='F1 Donchian', var=f'N{N} exit chan{N//2}', tf='H4', pair=pair)

def div(args):
    mode, pair = args; configure(mode)
    df = bt.build(pair, 'H4', touch='close', L=100, gap=3, rsi_margin=5)   # --- holdout.job without the to_parquet ---
    idx = np.where(df.buy.values | df.sell.values)[0]; d = np.where(df.buy.values[idx], 1, -1)
    tr = bt.simulate(df, pair, idx, d, sl_atr=1.0, tp_mode='mid', max_bars=32); tr['pair'] = pair
    f = df.iloc[tr.i.values]
    for col in ['bw_pct','bw_chg','atr_ratio','mid_slope','adx','bar_range','close_pos','run_lo','run_hi','rsi','h4_rsi','d1_adx','d1_dist20','d1_rsi','d1_atr_ratio','sma200_dist','hour','dow','atr']:
        tr[col] = f[col].values
    k = np.array([((idx[a] - idx[:a] <= 12) & (d[:a] == d[a])).sum() for a in range(len(idx))])
    pos = {i: n for n, i in enumerate(idx)}; tr['k'] = [k[pos[i]] for i in tr.i]
    tr['exit_t'] = [t + pd.Timedelta(hours=4*int(bb)) for t, bb in zip(tr.t, tr.bars)]
    tr['cost_r'] = bt.COST_PIPS[pair] * bt.PIP[pair] / (tr.risk_atr * tr.atr); tr['is'] = tr.t < '2019-01-01'
    return tr

RULE_C = [v for k, v in holdout_iter.RULES.items() if k[0] == 'C'][0]
RULE_E = [v for k, v in holdout_iter.RULES.items() if k[0] == 'E'][0]

if __name__ == '__main__':
    from fam_combo import final_rules
    pd.set_option('display.width', 250)
    with Pool(4) as p:
        for mode in ('rep', 'full'):
            dn = pd.concat(p.map(donch, [(mode, x) for x in ALL]), ignore_index=True)
            dn = tag(dn); dn['strat'] = dn.fam + ' | ' + dn['var'] + ' | ' + dn.tf
            if mode == 'rep': dn = dn[dn.t >= '2012-01-01']
            dn.to_parquet(os.path.join(OUT, f'r2_donch_raw_{mode}.parquet'))
            for cm in (1.0, 1.5, 2.0):
                x = final_rules(dn, atr_skip=True, hour_skip=False, month=True, cost_mult=cm)
                x.to_parquet(os.path.join(OUT, f'r2_P4_{mode}_c{cm}.parquet'))
            dv = pd.concat(p.map(div, [(mode, x) for x in ALL]), ignore_index=True).sort_values('t').reset_index(drop=True)
            dv.to_parquet(os.path.join(OUT, f'r2_div_signals_{mode}.parquet'))
            for rn, rf in (('C', RULE_C), ('E', RULE_E)):
                x = no_overlap(dv[rf(dv)].sort_values('t'))
                x.to_parquet(os.path.join(OUT, f'r2_P5{rn}_{mode}.parquet'))
            print(mode, 'done', len(dn), len(dv), flush=True)
    # ---- reproduction checks (round 0) ----
    old = pd.read_parquet(os.path.join(OUT, 'fam_trades.parquet'))
    old = old[old.strat == 'F1 Donchian | N50 exit chan25 | H4'].sort_values(['pair', 't'])
    new = pd.read_parquet(os.path.join(OUT, 'r2_donch_raw_rep.parquet')).sort_values(['pair', 't'])
    print('REPRO Donchian raw trades: N old/new', len(old), len(new), 'identical r:',
          len(old) == len(new) and np.allclose(old.r.values, new.r.values, atol=1e-12))
    x = pd.read_parquet(os.path.join(OUT, 'r2_P4_rep_c1.0.parquet')); s = stats(x.r.values, x.exit_t.values)
    print('REPRO P4 (round-0 report: t 1.64, sumR/DD 2.50):', {k: round(v, 3) for k, v in s.items()}, 'ratio', round(s['sumR'] / abs(s['maxDD_R']), 2))
    for rn in ('C', 'E'):
        for g in ('design', 'cross'):
            f = os.path.join(OUT, f'trades_rule{rn}_{g}.parquet')
            if not os.path.exists(f): continue
            o = pd.read_parquet(f); n = pd.read_parquet(os.path.join(OUT, f'r2_P5{rn}_rep.parquet'))
            n = n[n.pair.isin(DESIGN if g == 'design' else CROSS)]
            print(f'REPRO rule {rn} {g}: N old/new {len(o)}/{len(n)} avgR old/new {o.r.mean():.4f}/{n.r.mean():.4f}',
                  'identical' if len(o) == len(n) and np.allclose(np.sort(o.r.values), np.sort(n.r.values)) else 'DIFFERENT')
