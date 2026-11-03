"""Step 2b: combine the filters that passed the 4-cell consistency test, re-check pre-registered criteria."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fam_common import *
from fam_filters import evaluate, SNB, cells
from fam_table import criteria

def final_rules(tr, strat='F1 Donchian | N50 exit chan25 | H4', atr_skip=True, hour_skip=True, month=True, cost_mult=1.0):
    x = tr[tr.strat == strat].copy()
    if cost_mult != 1.0: x['r'] = x.r - (cost_mult - 1) * x.cost_r
    m = np.ones(len(x), bool)
    if atr_skip: m &= (x.atr_ratio >= 0.8).values
    if hour_skip: m &= (x.hour != 4).values
    x = x[m]
    if month: x = select(x, month_stop=5)
    return x

if __name__ == '__main__':
    pd.set_option('display.width', 300); pd.set_option('display.max_columns', 40)
    tr = pd.read_parquet(os.path.join(OUT, 'fam_trades.parquet'))
    base = tr[tr.strat == 'F1 Donchian | N50 exit chan25 | H4']
    rows = []
    for name, kw in [('A: atr>=0.8', dict(hour_skip=False, month=False)), ('B: A + skip 04 bar', dict(month=False)),
                     ('C: B + month stop -5R', {}), ('D: atr>=0.8 + month stop', dict(hour_skip=False))]:
        x = final_rules(tr, **kw)
        rows.append(evaluate(name, base, x))
        xs = x[~((x.pair.str.contains('CHF')) & (x.entry_t <= SNB[1]) & (x.exit_t >= SNB[0]))]
        rows.append(evaluate(name + ' | ex-SNB', base, xs))
        rows.append(evaluate(name + ' | R cap 10', base, x.assign(r=x.r.clip(upper=10))))
        x2 = x.assign(strat=name)
        print(criteria(x2).round(3).to_string(index=False))
    out = pd.DataFrame(rows); print(out.round(3).to_string(index=False))
    out.to_csv(os.path.join(OUT, 'fam_combo.csv'), index=False)
