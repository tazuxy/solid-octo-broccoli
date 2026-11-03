"""Filter combinations + portfolio simulation for the H4 strategy."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from bt import *
m = pd.read_parquet(os.path.join(ROOT,'out','merged_H4.parquet'))
m = m.sort_values('t').reset_index(drop=True)
m['exit_t'] = [m.t.iloc[k] + pd.Timedelta(hours=4*int(b)) for k, b in enumerate(m.bars)]
m['cost_r'] = [COST_PIPS[p]*PIP[p]/(ra*a) for p, ra, a in zip(m.pair, m.risk_atr, m.atr)]
FILTERS = {
 'none': lambda x: np.ones(len(x), bool),
 'F1 bw_pct<0.6': lambda x: x.bw_pct < 0.6,
 'F2 risk<=1.5ATR': lambda x: x.risk_atr <= 1.5,
 'F3 atr_ratio<1.5': lambda x: x.atr_ratio < 1.5,
 'F4 no 20:00 bar (Asia open)': lambda x: x.hour != 20,
 'F1+F2': lambda x: (x.bw_pct < 0.6) & (x.risk_atr <= 1.5),
 'F1+F2+F3': lambda x: (x.bw_pct < 0.6) & (x.risk_atr <= 1.5) & (x.atr_ratio < 1.5),
 'F1+F2+F3+F4': lambda x: (x.bw_pct < 0.6) & (x.risk_atr <= 1.5) & (x.atr_ratio < 1.5) & (x.hour != 20),
}
def no_overlap(x):
    keep = []; busy = {}
    for k, row in x.iterrows():
        if row.pair in busy and row.t < busy[row.pair]: continue
        keep.append(k); busy[row.pair] = row.exit_t
    return x.loc[keep]
def portfolio(x, risk=0.005, max_pos=4):
    x = x.sort_values('t'); eq = 1.0; curve = []; open_pos = []; taken = 0
    for _, row in x.iterrows():
        open_pos = [e for e in open_pos if e > row.t]
        if len(open_pos) >= max_pos: continue
        eq *= (1 + risk * row.r); open_pos.append(row.exit_t); curve.append((row.exit_t, eq)); taken += 1
    c = pd.Series([v for _, v in curve], index=[t for t, _ in curve]).sort_index()
    c = c.groupby(level=0).last()
    dd = (c / c.cummax() - 1).min()
    yrs = (c.index[-1] - c.index[0]).days / 365.25
    cagr = c.iloc[-1] ** (1 / yrs) - 1
    mon = c.resample('ME').last().pct_change().dropna()
    sharpe = mon.mean() / mon.std() * np.sqrt(12) if mon.std() > 0 else np.nan
    return dict(trades=taken, final=c.iloc[-1], cagr=cagr, maxdd=dd, sharpe=sharpe, curve=c)
def rstats(x):
    cs = x.r.cumsum(); ddR = (cs - cs.cummax()).min()
    # longest losing streak
    s = 0; mx = 0
    for v in x.r: s = s + 1 if v <= 0 else 0; mx = max(mx, s)
    return dict(N=len(x), avgR=x.r.mean(), win=(x.r>0).mean(), sumR=x.r.sum(), IS=x[x['is']].r.mean(), OOS=x[~x['is']].r.mean(),
                t=x.r.mean()/(x.r.std()/np.sqrt(len(x))), maxDD_R=ddR, streak=mx)
if __name__ == '__main__':
    pd.set_option('display.width', 250)
    rows = []; curves = {}
    for name, f in FILTERS.items():
        x = m[f(m)]; x = no_overlap(x)
        st = rstats(x); p = portfolio(x)
        rows.append(dict(filter=name, **st, cagr=p['cagr'], maxdd=p['maxdd'], sharpe=p['sharpe'])); curves[name] = p['curve']
        if name in ('none', 'F1+F2+F3'):
            print(f'\n{name}: yearly'); print(x.groupby(x.t.dt.year).r.agg(['count','mean','sum']).round(2).T.to_string())
    print(pd.DataFrame(rows).round(3).to_string(index=False))
    # cost sensitivity for the chosen filter set
    x = no_overlap(m[FILTERS['F1+F2+F3'](m)])
    for mult in (1.0, 1.5, 2.0):
        r = x.r - (mult-1)*x.cost_r
        print(f'cost x{mult}: avgR={r.mean():.3f} sumR={r.sum():.1f}')
    # Monte-Carlo drawdown: shuffle trade order 2000x, risk 0.5%
    rng = np.random.default_rng(0); dds = []
    for _ in range(2000):
        rr = rng.permutation(x.r.values); c = np.cumprod(1 + 0.005*rr); dds.append((c/np.maximum.accumulate(c)-1).min())
    print('MC maxDD (0.5%% risk): median %.1f%%, 95th %.1f%%' % (np.median(dds)*100, np.percentile(dds, 5)*100))
    pd.DataFrame(curves).to_csv(os.path.join(ROOT,'out','curves_h4.csv'))
    x.to_parquet(os.path.join(ROOT,'out','trades_h4_filtered.parquet'))
