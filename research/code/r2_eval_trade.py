"""Round 2: pre-registered evaluation of per-trade candidates P4 (Donchian H4 + filters) and P5 (divergence rules C, E).
Trades are scored by signal time t.  Warm-up: trades with t < max(2005-07-01, pair's first bar + 6 months) are not scored.
early = 2005-07..2011-12 (t < 2012-01-01);  combined = all scored trades 2005-07..2024-12 (continuous 2005-2024 run).
Criteria: (a) avgR > 0 net in design-8 and cross-10 (early); (b) pooled t >= 1.5 (early); (c) combined t >= 2.0 and
sumR/|maxDD_R| >= 3 (R summed in exit-time order); (d) >= 60% of instruments with trades have sumR > 0 (early);
(e) at costs x1.5: avgR > 0 in both groups (early) and pooled avgR > 0 (combined).
Costs x1.5: P4 = re-run of the selection with r - 0.5*cost_r (fam_combo.final_rules cost_mult=1.5); P5 = r - 0.5*cost_r."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fam_common import *
rd = lambda f: pd.read_parquet(os.path.join(OUT, f))
first = {p: pd.read_parquet(os.path.join(ROOT, 'bars_full', f'{p}_H4.parquet')).index.min() for p in ALL}
START = {p: max(pd.Timestamp('2005-07-01'), first[p] + pd.DateOffset(months=6)) for p in ALL}
E_END = pd.Timestamp('2012-01-01')
# re-warm-up after a data gap > 10 days (AUDJPY only: 2012-01..09 and 2012-11..12 missing in bars/): not scored for 6 months
REGAP = {}
for p_ in ALL:
    ix = pd.read_parquet(os.path.join(ROOT, 'bars_full', f'{p_}_D1.parquet')).index
    REGAP[p_] = [(a_, b_) for a_, b_ in zip(ix[:-1], ix[1:]) if (b_ - a_).days > 10 and b_ > pd.Timestamp('2006-01-01')]

def scored(x):
    x = x.copy(); x['group'] = np.where(x.pair.isin(DESIGN), 'design', 'cross')
    keep = x.t >= x.pair.map(START)
    for p_, gl in REGAP.items():
        for a_, b_ in gl:     # a_ = last bar before the gap, b_ = first bar after it
            m = x.pair == p_
            keep &= ~(m & (x.t >= b_) & (x.t < b_ + pd.DateOffset(months=6)))     # re-warm-up
            keep &= ~(m & (x.t <= a_ + pd.Timedelta(days=1)) & (x.exit_t >= b_))  # trade held across the gap
    return x[keep]

def load(cand, cm=1.0, mode='full'):
    if cand == 'P4': return rd(f'r2_P4_{mode}_c{cm}.parquet')
    x = rd(f'r2_{cand}_{mode}.parquet')
    if cm != 1.0: x = x.assign(r=x.r - (cm - 1) * x.cost_r)
    if 'entry_t' not in x: x['entry_t'] = x.t + pd.Timedelta(hours=4)
    return x

def flat_months(x):
    """longest time (months) between new highs of the cumulative-R curve (exit-time order), incl. the unfinished one."""
    x = x.sort_values('exit_t'); cs = x.r.cumsum().values; t = x.exit_t.values
    cs = np.r_[0.0, cs]; t = np.r_[np.datetime64(x.t.min()), t]
    hi = np.maximum.accumulate(cs); newhi = t[cs >= hi]
    gaps = np.diff(np.r_[newhi, t[-1]]).astype('timedelta64[D]').astype(int)
    return gaps.max() / 30.44

def block(x):
    s = stats(x.r.values, x.exit_t.values)
    return dict(N=s['N'], avgR=s['avgR'], t=s['t'], sumR=s['sumR'], maxDD_R=s['maxDD_R'],
                ratio=s['sumR'] / abs(s['maxDD_R']) if s['maxDD_R'] < 0 else np.inf)

def evaluate(cand):
    x = scored(load(cand)); x15 = scored(load(cand, 1.5)); x2 = scored(load(cand, 2.0))
    e = x[x.t < E_END]; e15 = x15[x15.t < E_END]
    r = dict(cand=cand)
    for g in ('design', 'cross'):
        eg = e[e.group == g]; r[f'early_{g}_N'] = len(eg); r[f'early_{g}_avgR'] = eg.r.mean(); r[f'early_{g}_t'] = block(eg)['t']
        r[f'early15_{g}_avgR'] = e15[e15.group == g].r.mean()
    be = block(e); r.update({f'early_{k}': v for k, v in be.items()})
    pp = e.groupby('pair').r.sum(); r['early_pairs_pos'] = int((pp > 0).sum()); r['early_pairs_n'] = len(pp)
    r['early_pairs'] = '; '.join(f'{k} {v:+.1f}' for k, v in pp.items())
    ba = block(x); r.update({f'all_{k}': v for k, v in ba.items()}); r['all_flat_m'] = flat_months(x)
    b15 = block(x15); r['all15_avgR'] = b15['avgR']; r['all15_t'] = b15['t']; r['all15_ratio'] = b15['ratio']
    r['all2_avgR'] = x2.r.mean()
    late = x[x.t >= E_END]; bl = block(late); r.update({f'late_{k}': v for k, v in bl.items()})
    rep = load(cand, mode='rep'); br = block(rep); r.update({f'rep_{k}': v for k, v in br.items()})
    # criteria
    a = r['early_design_avgR'] > 0 and r['early_cross_avgR'] > 0
    b = r['early_t'] >= 1.5
    c = r['all_t'] >= 2.0 and r['all_ratio'] >= 3
    d = r['early_pairs_pos'] / r['early_pairs_n'] >= 0.6
    e_ = r['early15_design_avgR'] > 0 and r['early15_cross_avgR'] > 0 and r['all15_avgR'] > 0
    r.update(dict(c_a=a, c_b=b, c_c=c, c_d=d, c_e=e_, PASS=a and b and c and d and e_))
    yr = x.groupby(x.t.dt.year).r.agg(['count', 'mean', 'sum'])
    return r, yr

if __name__ == '__main__':
    pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 300)
    rows = []; yrs = {}
    for cand in ('P4', 'P5C', 'P5E'):
        r, yr = evaluate(cand); rows.append(r); yrs[cand] = yr
        print(cand); print(yr.round(3).T.to_string())
    t = pd.DataFrame(rows); t.to_csv(os.path.join(OUT, 'r2_trade_criteria.csv'), index=False)
    print(t.T.to_string())
    y = pd.concat({k: v for k, v in yrs.items()}, axis=1); y.to_csv(os.path.join(OUT, 'r2_trade_yearly.csv'))
    # P4 fixed-fractional equity (0.5% risk per trade, as round 0) for the yearly % table / maxDD
    x = scored(load('P4')); c = equity(x, 0.005); cs, yrp = curve_stats(c, start='2005-07-01')
    print('P4 0.5% risk:', {k: round(v, 3) for k, v in cs.items()}); print((yrp * 100).round(1).to_string())
    pd.DataFrame({'P4_ret_0.5risk': yrp.values}, index=yrp.index.year).to_csv(os.path.join(OUT, 'r2_P4_yearly_pct.csv'))
