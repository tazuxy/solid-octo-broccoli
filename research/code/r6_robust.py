"""Round 6 step 4: robustness of the final rule (and the base for comparison). Final rule = frozen filter if confirmed, else base."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r6_common import *
fz = json.load(open(os.path.join(OUT, 'r6_frozen.json'))); cf = json.load(open(os.path.join(OUT, 'r6_confirm.json')))
ADOPT = fz['adopted'] if cf['confirmed'] else []
L = []
def P(*a): s = ' '.join(str(x) for x in a); print(s); L.append(s)
pd.set_option('display.width', 250)
def keep(x, adopt):
    m = np.ones(len(x), bool)
    for a in adopt: m &= (x[a['cond']] != a['exclude']).values
    return x[m]
RULES = {'base': [], 'final': ADOPT}
P('final rule filters:', ADOPT)
# 1) time grid
grid = []
for eo in (-30, -15, 0, 15, 30):
    tr = build(eo, 0) if True else None
    for xo in (-10, -5, 0, 5, 10):
        t = build(eo, xo) if xo != 0 else tr
        t = features(t) if len(ADOPT) else t.assign(period=np.where(t.year <= SEL[1], 'SEL', 'VAL'))
        t = t[t.gotobi]
        for rn, ad in RULES.items():
            y = keep(t, ad) if ad else t
            for per in ('ALL', 'SEL', 'VAL'):
                z = y if per == 'ALL' else y[y.period == per]; s = pstats(z)
                grid.append(dict(rule=rn, entry_off=eo, exit_off=xo, period=per, N=s['N'], mean=s['mean'], t=s['t'], ratio=s['ratio']))
G = pd.DataFrame(grid); G.to_csv(os.path.join(OUT, 'r6_grid.csv'), index=False)
for rn in RULES:
    for per in ('ALL', 'VAL'):
        P(f'\n grid {rn} {per}: mean net pips (rows entry offset min, cols exit offset min)')
        P(G[(G.rule == rn) & (G.period == per)].pivot(index='entry_off', columns='exit_off', values='mean').round(2).to_string())
        P(f' t-stat'); P(G[(G.rule == rn) & (G.period == per)].pivot(index='entry_off', columns='exit_off', values='t').round(2).to_string())
        P(f' ratio'); P(G[(G.rule == rn) & (G.period == per)].pivot(index='entry_off', columns='exit_off', values='ratio').round(2).to_string())
# 2) cost, top-5% drop, bootstrap, placebo
allt = pd.read_parquet(os.path.join(OUT, 'r6_trades_all.parquet'))
g = allt[allt.gotobi].sort_values('t_ent'); pool = allt[~allt.gotobi]
rng = np.random.default_rng(6); out = []
for rn, ad in RULES.items():
    y = keep(g, ad) if ad else g
    r = dict(rule=rn, N=len(y), mean05=y.net.mean(), t05=tstat(y.net), ratio05=pstats(y)['ratio'])
    n1 = y.gross_pips - 1.0; r.update(mean10=n1.mean(), t10=tstat(n1), ratio10=pstats(n1.values)['ratio'])
    for per in ('SEL', 'VAL'):
        z = y[y.period == per].gross_pips - 1.0; r[f'mean10_{per}'] = z.mean(); r[f't10_{per}'] = tstat(z); r[f'ratio10_{per}'] = pstats(z.values)['ratio']
    q = y.net.quantile(0.95); d = y[y.net < q]; r.update(drop5_N=len(d), drop5_mean=d.net.mean(), drop5_t=tstat(d.net), drop5_sum=d.net.sum())
    yrs = y.groupby('year').net.agg(['sum', 'count']); ys = yrs['sum'].values; yc = yrs['count'].values
    bs = []
    for _ in range(10000):
        i = rng.integers(0, len(ys), len(ys)); bs.append(ys[i].sum() / yc[i].sum())
    bs = np.array(bs); r.update(boot_p05=np.quantile(bs, 0.05), boot_p50=np.median(bs), boot_p_le0=(bs <= 0).mean())
    pl = np.array([pool.net.values[rng.choice(len(pool), len(y), replace=False)].mean() for _ in range(1000)])
    r.update(placebo_mean=pl.mean(), placebo_p95=np.quantile(pl, 0.95), placebo_max=pl.max(), real_pctile=100 * (pl < y.net.mean()).mean())
    out.append(r)
O = pd.DataFrame(out); O.to_csv(os.path.join(OUT, 'r6_robust.csv'), index=False); P('\n'); P(O.round(3).T.to_string())
P(f'placebo pool N={len(pool)} mean={pool.net.mean():.3f}')
open(os.path.join(OUT, 'r6_robust.log'), 'w').write('\n'.join(L))
log('r6_robust done')
