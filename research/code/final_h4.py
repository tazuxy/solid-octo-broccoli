"""Final H4 rule set: 2nd divergence signal within 12 bars (k>=1), stop cap 1.5 ATR. Portfolio + chart."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from bt import *
from port import no_overlap, rstats, portfolio
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
m = pd.read_parquet(os.path.join(ROOT,'out','merged_H4.parquet')).sort_values(['pair','t']).reset_index(drop=True)
m['exit_t'] = [t + pd.Timedelta(hours=4*int(b)) for t, b in zip(m.t, m.bars)]
m['cost_r'] = [COST_PIPS[p]*PIP[p]/(ra*a) for p, ra, a in zip(m.pair, m.risk_atr, m.atr)]
k = np.zeros(len(m), int)
for p, g in m.groupby('pair'):
    ii = g.i.values; dd = g['dir'].values
    for a in range(len(g)): k[g.index[a]] = ((ii[a] - ii[:a] <= 12) & (dd[:a] == dd[a])).sum()
m['k'] = k
pd.set_option('display.width', 250)
RULES = {'A: all signals (1st entry only)': lambda x: np.ones(len(x), bool),
         'B: 2nd+ signal within 12 bars': lambda x: x.k >= 1,
         'C: B + stop<=1.5ATR': lambda x: (x.k >= 1) & (x.risk_atr <= 1.5),
         'D: C + bw_pct<0.6': lambda x: (x.k >= 1) & (x.risk_atr <= 1.5) & (x.bw_pct < 0.6)}
rows = []; curves = {}
for name, f in RULES.items():
    x = no_overlap(m[f(m)].sort_values('t'))
    st = rstats(x)
    for risk in (0.005, 0.01):
        p = portfolio(x, risk=risk, max_pos=4)
        st[f'cagr{risk}'] = p['cagr']; st[f'maxdd{risk}'] = p['maxdd']; st[f'sharpe'] = p['sharpe']
        if risk == 0.01: curves[name] = p['curve']
    rows.append(dict(rule=name, **st))
    if name.startswith('C'):
        print('rule C yearly:'); print(x.groupby(x.t.dt.year).r.agg(['count','mean','sum']).round(2).T.to_string())
        print('rule C by pair:'); print(x.groupby('pair').r.agg(['count','mean','sum']).round(2).T.to_string())
        print('rule C by dir:'); print(x.groupby('dir').r.agg(['count','mean','sum']).round(2).T.to_string())
        print('rule C exit reasons:'); print(x.groupby('reason').r.agg(['count','mean']).round(2).T.to_string())
        for mult in (1.0, 1.5, 2.0):
            r = x.r - (mult-1)*x.cost_r; print(f'cost x{mult}: avgR={r.mean():.3f} sumR={r.sum():.1f}')
        rng = np.random.default_rng(0); dds = []; fin = []
        for _ in range(5000):
            rr = rng.permutation(x.r.values); c = np.cumprod(1 + 0.01*rr); dds.append((c/np.maximum.accumulate(c)-1).min()); fin.append(c[-1])
        print('MC (1%% risk, shuffled order): maxDD median %.1f%%, worst-5%% %.1f%%; P(final<1)=%.2f' % (np.median(dds)*100, np.percentile(dds,5)*100, np.mean(np.array(fin)<1)))
        x.to_parquet(os.path.join(ROOT,'out','trades_final_h4.parquet'))
print(pd.DataFrame(rows).round(3).to_string(index=False))
fig, ax = plt.subplots(figsize=(10,5))
for name, c in curves.items(): ax.plot(c.index, (c-1)*100, label=name)
ax.set_title('H4 BB(20,2) close-outside + RSI divergence, 8 instruments, 1% risk/trade, net of costs'); ax.set_ylabel('%'); ax.grid(alpha=.3); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(ROOT,'out','equity_h4.png'), dpi=120)
