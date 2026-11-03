"""Step 3: portfolio simulation of the closest rule set (Donchian H4 N50, exit 25-bar channel, SL 2ATR,
skip ATR ratio < 0.8, monthly -5R entry stop). Reference only: it did NOT pass the pre-registered criteria."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fam_common import *
from fam_filters import SNB
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

STRAT = 'F1 Donchian | N50 exit chan25 | H4'
def rules(tr, max_pos=None, cost_mult=1.0, ex_snb=False):
    x = tr[tr.strat == STRAT].copy()
    if cost_mult != 1.0: x['r'] = x.r - (cost_mult - 1) * x.cost_r
    if ex_snb: x = x[~((x.pair.str.contains('CHF')) & (x.entry_t <= SNB[1]) & (x.exit_t >= SNB[0]))]
    x = x[(x.atr_ratio >= 0.8).values]
    return select(x, max_pos=max_pos, month_stop=5)

def mc_dd(r, risk, n=2000, seed=0):
    rng = np.random.default_rng(seed); out = []
    for _ in range(n):
        c = np.cumprod(1 + risk * rng.permutation(r)); c = np.r_[1.0, c]
        out.append((c / np.maximum.accumulate(c) - 1).min())
    return np.median(out), np.percentile(out, 5)

if __name__ == '__main__':
    pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
    tr = pd.read_parquet(os.path.join(OUT, 'fam_trades.parquet'))
    rows = []; curves = {}; yearly = {}
    for ex in (False, True):
        for mp in (4, 8):
            for cm in (1.0, 1.5, 2.0):
                x = rules(tr, max_pos=mp, cost_mult=cm, ex_snb=ex)
                s = stats(x.r.values, x.exit_t.values)
                for risk in (0.005, 0.01):
                    c = equity(x, risk); cs, yr = curve_stats(c)
                    med, p5 = mc_dd(x.r.values, risk)
                    key = f"{'exSNB ' if ex else ''}max{mp} cost x{cm} risk {risk*100:.1f}%"
                    rows.append(dict(case=key, ex_snb=ex, max_pos=mp, cost_mult=cm, risk=risk, N=s['N'], avgR=s['avgR'],
                                     t=s['t'], sumR=s['sumR'], maxDD_R=s['maxDD_R'], **cs, mc_dd_median=med, mc_dd_p5=p5))
                    if cm == 1.0: curves[key] = c; yearly[key] = yr
                if cm == 1.0 and not ex:
                    print(f'\nmax{mp}: per-year R'); print(x.groupby(x.t.dt.year).r.agg(['count', 'mean', 'sum']).round(2).T.to_string())
                    pp = x.groupby('pair').r.agg(['count', 'mean', 'sum']).round(2); print(pp.T.to_string())
                    pp.to_csv(os.path.join(OUT, f'fam_port_pairs_max{mp}.csv'))
                    x.to_parquet(os.path.join(OUT, f'fam_port_trades_max{mp}.parquet'))
    res = pd.DataFrame(rows); res.to_csv(os.path.join(OUT, 'fam_portfolio.csv'), index=False)
    print(res.drop(columns=['ex_snb', 'max_pos', 'cost_mult', 'risk']).round(3).to_string(index=False))
    yt = pd.DataFrame({k: v.values for k, v in yearly.items()}, index=yearly[next(iter(yearly))].index.year)
    yt.to_csv(os.path.join(OUT, 'fam_port_yearly.csv')); print((yt * 100).round(1).to_string())
    # equity figure
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True, gridspec_kw=dict(height_ratios=[3, 1.3]))
    ser = [('max8 cost x1.0 risk 0.5%', '#2a78d6', 'max 8 positions, 0.5% risk'),
           ('max4 cost x1.0 risk 0.5%', '#eb6834', 'max 4 positions, 0.5% risk')]
    for k, col, lab in ser:
        c = curves[k]; c0 = pd.concat([pd.Series([1.0], index=[pd.Timestamp('2012-01-01')]), c])
        a1.plot(c0.index, c0.values, color=col, lw=2, label=lab)
        a2.plot(c0.index, (c0 / c0.cummax() - 1) * 100, color=col, lw=1.5)
    a1.axvline(pd.Timestamp('2019-01-01'), color='#888', lw=1, ls='--'); a2.axvline(pd.Timestamp('2019-01-01'), color='#888', lw=1, ls='--')
    a1.text(pd.Timestamp('2019-02-01'), a1.get_ylim()[1] * 0.97, 'OOS 2019-', color='#52514e', va='top', fontsize=9)
    a1.set_ylabel('Equity (start = 1.0)'); a2.set_ylabel('Drawdown %')
    a1.set_title('Donchian H4 N50 (closest variant, NOT a candidate): equity, 18 instruments, net of costs', fontsize=11)
    for a in (a1, a2):
        a.grid(color='#e5e5e3', lw=0.6); a.spines[['top', 'right']].set_visible(False)
    a1.legend(frameon=False, loc='upper left')
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fam_equity.png'), dpi=120)
    print('saved png')
