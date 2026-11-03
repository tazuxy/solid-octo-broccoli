"""Step 2: 'when not to trade' analysis for the closest strategies, 4-cell discipline.
A filter is ADOPTABLE only if avgR(kept) - avgR(baseline) > 0 in all four cells (design/cross x IS/OOS)
and the kept sample keeps >= 100 trades."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fam_common import *

CELLS = [('design', 'IS'), ('design', 'OOS'), ('cross', 'IS'), ('cross', 'OOS')]
def cells(x): return [x[(x.group == g) & (x.period == p)].r.mean() for g, p in CELLS]
SNB = (pd.Timestamp('2015-01-14'), pd.Timestamp('2015-01-16'))

def evaluate(name, base, kept):
    b = cells(base); k = cells(kept); s = stats(kept.r.values, kept.exit_t.values)
    d = [kk - bb for kk, bb in zip(k, b)]
    pp = kept.groupby('pair').r.sum()
    ok = all(v > 0 for v in d) and s['N'] >= 100
    return dict(filter=name, N=s['N'], avgR=s['avgR'], dIS=k[0], dOOS=k[1], cIS=k[2], cOOS=k[3],
                delta_min=min(d), delta_max=max(d), t=s['t'], sumR=s['sumR'], maxDD_R=s['maxDD_R'],
                sumR_DD=s['sumR'] / abs(s['maxDD_R']) if s['maxDD_R'] < 0 else np.inf,
                pairs_pos=int((pp > 0).sum()), consistent=ok)

def run(strat, tr):
    x = tr[tr.strat == strat].copy()
    rows = [evaluate('baseline', x, x)]
    snb = x[~((x.pair.str.contains('CHF')) & (x.entry_t <= SNB[1]) & (x.exit_t >= SNB[0]))]
    rows.append(evaluate('info: exclude trades open over SNB 2015-01-15 (CHF pairs)', x, snb))
    rows.append(evaluate('info: R capped at +10', x, x.assign(r=x.r.clip(upper=10))))
    F = {
        'skip atr_ratio > 1.5': x.atr_ratio <= 1.5,
        'skip atr_ratio < 0.8': x.atr_ratio >= 0.8,
        'only atr_ratio 0.8-1.2': (x.atr_ratio >= 0.8) & (x.atr_ratio <= 1.2),
        'skip ADX < 20': x.adx >= 20,
        'skip ADX > 40': x.adx <= 40,
        'only ADX 20-40': (x.adx >= 20) & (x.adx <= 40),
        'skip cost_r > 0.1': x.cost_r <= 0.1,
        'skip cost_r > 0.05': x.cost_r <= 0.05,
    }
    for dname in range(5):
        F[f'skip dow {["Mon","Tue","Wed","Thu","Fri"][dname]}'] = x.dow != dname
    if x.tf.iloc[0] == 'H4':
        for hh in sorted(x.hour.unique()): F[f'skip hour {hh:02d} EST'] = x.hour != hh
    for name, m in F.items():
        rows.append(evaluate(name, x, x[m.fillna(False).values]))
    P = {'max concurrent 4': dict(max_pos=4), 'max concurrent 8': dict(max_pos=8),
         'ccy cap 2 same-direction': dict(ccy_cap=2), 'ccy cap 3 same-direction': dict(ccy_cap=3),
         'month stop -5R': dict(month_stop=5), 'week stop -3R': dict(week_stop=3)}
    for name, kw in P.items():
        rows.append(evaluate('portfolio: ' + name, x, select(x, **kw)))
    out = pd.DataFrame(rows); out.insert(0, 'strat', strat); return out

if __name__ == '__main__':
    pd.set_option('display.width', 300); pd.set_option('display.max_columns', 40); pd.set_option('display.max_rows', 500)
    tr = pd.read_parquet(os.path.join(OUT, 'fam_trades.parquet'))
    strats = sys.argv[1].split(';')
    res = pd.concat([run(s, tr) for s in strats], ignore_index=True)
    res.to_csv(os.path.join(OUT, 'fam_filters.csv'), index=False)
    print(res.round(3).to_string(index=False))
