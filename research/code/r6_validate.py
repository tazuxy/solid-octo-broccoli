"""Round 6 step 3: ONE look at the validation period (G in 2015-2024) for the frozen rule, then the full bucket table
for both periods (validation numbers NOT used for choosing)."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r6_common import *
fz = json.load(open(os.path.join(OUT, 'r6_frozen.json'))); proto = json.load(open(os.path.join(OUT, 'r6_protocol.json')))
log(f"r6_validate: start; frozen at {fz['frozen_utc']}; adopted={fz['adopted']}")
allt = pd.read_parquet(os.path.join(OUT, 'r6_trades_all.parquet')); g = allt[allt.gotobi].sort_values('t_ent').reset_index(drop=True)
def keep_mask(x): 
    m = np.ones(len(x), bool)
    for a in fz['adopted']: m &= (x[a['cond']] != a['exclude']).values
    return m
L = []
def P(*a): s = ' '.join(str(x) for x in a); print(s); L.append(s)
pd.set_option('display.width', 250)
rows = []
for per in ('SEL', 'VAL', 'ALL'):
    x = g if per == 'ALL' else g[g.period == per]
    for name, y in (('base', x), ('filtered', x[keep_mask(x)])):
        s = pstats(y); s['flat_days'] = longest_flat_days(y.t_ent, y.net.values); s['mean_1pip'] = (y.gross_pips - 1.0).mean()
        s['t_1pip'] = tstat(y.gross_pips - 1.0); rows.append(dict(period=per, rule=name, **s))
    for a in fz['adopted']:
        ex = x[x[a['cond']] == a['exclude']]; kp = x[x[a['cond']] != a['exclude']]
        rows.append(dict(period=per, rule=f"excluded bucket {a['cond']}={a['exclude']}", **pstats(ex)))
        rows.append(dict(period=per, rule=f"kept buckets {a['cond']}", **pstats(kp)))
V = pd.DataFrame(rows); P(V.round(3).to_string(index=False)); V.to_csv(os.path.join(OUT, 'r6_validation.csv'), index=False)
vb = V[(V.period == 'VAL') & (V.rule == 'base')].iloc[0]; vf = V[(V.period == 'VAL') & (V.rule == 'filtered')].iloc[0]
ok_ratio = vf.ratio > vb.ratio
ok_sign = all(V[(V.period == 'VAL') & (V.rule == f"excluded bucket {a['cond']}={a['exclude']}")].iloc[0]['mean'] <
              V[(V.period == 'VAL') & (V.rule == f"kept buckets {a['cond']}")].iloc[0]['mean'] for a in fz['adopted'])
confirmed = bool(len(fz['adopted']) and ok_ratio and ok_sign)
P(f'\nVALIDATION: ratio filtered {vf.ratio:.3f} vs base {vb.ratio:.3f} -> {ok_ratio}; excluded<kept -> {ok_sign}; CONFIRMED={confirmed}')
json.dump(dict(confirmed=confirmed, ok_ratio=bool(ok_ratio), ok_sign=bool(ok_sign)), open(os.path.join(OUT, 'r6_confirm.json'), 'w'))
log(f'r6_validate: result CONFIRMED={confirmed}')
# full table, both periods
EXC = {k: v[0] for k, v in proto['a_priori_exclusion_bucket'].items()}
T = []
for c in CONDS:
    for b in sorted(g[c].unique()):
        r = dict(cond=c, bucket=b, a_priori_excl=(EXC[c] == b))
        for per in ('SEL', 'VAL'):
            x = g[g.period == per]; y = x[x[c] == b]; s = pstats(y)
            r.update({f'{per}_N': s['N'], f'{per}_share': s['N'] / len(x), f'{per}_mean': s['mean'], f'{per}_t': s['t']})
        T.append(r)
T = pd.DataFrame(T); T.to_csv(os.path.join(OUT, 'r6_buckets_both.csv'), index=False)
P('\nALL BUCKETS (net 0.5 pip, pips/trade). VAL columns were NOT used for selection'); P(T.round(3).to_string(index=False))
# yearly for base / filtered
y = g.assign(keep=keep_mask(g)).groupby('year').apply(lambda x: pd.Series({'N_base': len(x), 'sum_base': x.net.sum(), 'N_filt': x.keep.sum(), 'sum_filt': x.net[x.keep].sum(),
      'sum_excl': x.net[~x.keep].sum()}))
P('\nyearly net pips'); P(y.round(1).to_string()); y.to_csv(os.path.join(OUT, 'r6_yearly.csv'))
open(os.path.join(OUT, 'r6_validate.log'), 'w').write('\n'.join(L))
