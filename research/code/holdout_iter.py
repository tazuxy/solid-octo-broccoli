"""Final hold-out evaluation incl. revised rule E (rules A-D unchanged, imported from holdout.py).
Needs out/signals_design.parquet and out/signals_cross.parquet (run holdout.py first).
usage: python -I code/holdout_iter.py"""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from hx import *
from port import portfolio
import holdout
RULES = dict(holdout.RULES)
RULES['E: C + H4 ADX<30 + D1 dist20>=1ATR counter-trend'] = lambda x: (x.k >= 1) & (x.risk_atr <= 1.5) & (x.adx < 30) & (-x.dir * x.d1_dist20 >= 1)
def crit(x):
    st = rstats(x); pp = x.groupby('pair').r.mean()
    return dict(**st, pairs_pos=f'{(pp > 0).sum()}/{len(pp)}', sum_dd=st['sumR'] / abs(st['maxDD_R']) if st['maxDD_R'] < 0 else np.inf)
if __name__ == '__main__':
    pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40)
    m = load_all(); m.to_parquet(os.path.join(ROOT, 'out', 'signals_all_aug.parquet'))
    rows = []
    for grp, pairs in (('design', DESIGN), ('cross', CROSS), ('all18', DESIGN + CROSS)):
        g = m[m.pair.isin(pairs)]
        for name, f in RULES.items():
            x = no_overlap(g[f(g)].sort_values('t')); st = crit(x)
            p = portfolio(x, risk=0.01, max_pos=4)
            rows.append(dict(group=grp, rule=name[:2], **st, cagr1=p['cagr'], maxdd1=p['maxdd']))
            if name[0] in 'ABCDE' and grp in ('cross',) or (name[0] in 'CE'):
                tag = name[0]
                print(f'\n[{grp}] rule {tag} by pair (count/mean/sum):'); print(x.groupby('pair').r.agg(['count','mean','sum']).round(2).T.to_string())
                if name[0] in 'CE':
                    print(f'[{grp}] rule {tag} by year:'); print(x.groupby(x.t.dt.year).r.agg(['count','mean','sum']).round(2).T.to_string())
                    print(f'[{grp}] rule {tag} by dir:'); print(x.groupby('dir').r.agg(['count','mean','sum']).round(2).T.to_string())
            if name[0] == 'E': x.to_parquet(os.path.join(ROOT, 'out', f'trades_ruleE_{grp}.parquet'))
    t = pd.DataFrame(rows); print('\nSUMMARY'); print(t.round(3).to_string(index=False))
    t.to_csv(os.path.join(ROOT, 'out', 'holdout_iter_summary.csv'), index=False)
    # cumulative R figure, rules C and E, by group
    try:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
        for a, rk in zip(ax, ('C', 'E')):
            f = [v for k, v in RULES.items() if k[0] == rk][0]
            for grp, pairs in (('design 8', DESIGN), ('cross 10', CROSS)):
                g = m[m.pair.isin(pairs)]; x = no_overlap(g[f(g)].sort_values('t'))
                a.plot(x.exit_t.values, x.r.cumsum().values, label=f'{grp} (N={len(x)})')
            a.axhline(0, color='grey', lw=0.8); a.set_title(f'rule {rk}: cumulative R'); a.legend()
        fig.tight_layout(); fig.savefig(os.path.join(ROOT, 'out', 'holdout_cumR.png'), dpi=110)
    except Exception as e: print('plot skipped:', e)
