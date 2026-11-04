"""Round 6 step 2: SELECTION period only (G in 2005-2014). Applies the pre-registered adoption rule and freezes the choice
in out/r6_frozen.json. No validation-period statistic is computed here (trades are filtered to period == 'SEL' first)."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r6_common import *
proto = json.load(open(os.path.join(OUT, 'r6_protocol.json')))
EXC = {k: v[0] for k, v in proto['a_priori_exclusion_bucket'].items()}
allt = pd.read_parquet(os.path.join(OUT, 'r6_trades_all.parquet'))
sel = allt[allt.gotobi & (allt.period == 'SEL')].sort_values('t_ent').reset_index(drop=True)
assert sel.year.max() <= 2014
L = []
def P(*a): s = ' '.join(str(x) for x in a); print(s); L.append(s)
pd.set_option('display.width', 250)
def evaluate(sample, conds, stage):
    base = pstats(sample); rows = []; brows = []
    for c in conds:
        for b, x in sample.groupby(c):
            brows.append(dict(stage=stage, cond=c, bucket=b, **pstats(x), share=len(x) / len(sample)))
        e = EXC[c]; r = dict(stage=stage, cond=c, excl=e)
        if e is None: r.update(cand=False, why='no a-priori exclusion bucket'); rows.append(r); continue
        ex = sample[sample[c] == e]; kept = sample[sample[c] != e]; se, sk = pstats(ex), pstats(kept)
        r.update(ex_N=se['N'], ex_share=se['N'] / len(sample), ex_mean=se['mean'], kept_N=sk['N'], kept_mean=sk['mean'], kept_t=sk['t'],
                 base_t=base['t'], kept_ratio=sk['ratio'], base_ratio=base['ratio'], d_ratio=sk['ratio'] - base['ratio'])
        a1 = se['N'] > 0 and se['mean'] < 0; a2 = sk['t'] > base['t']; bb = se['N'] >= 40 and se['N'] / len(sample) >= 0.15; imp = r['d_ratio'] > 0
        r['cand'] = bool(a1 and a2 and bb and imp)
        r['why'] = ';'.join(w for w, ok in (('excl mean>=0', a1), ('kept t<=base', a2), ('excl <15% or <40', bb), ('ratio not improved', imp)) if not ok) or 'candidate'
        rows.append(r)
    return base, pd.DataFrame(rows), pd.DataFrame(brows)
base, R1, B1 = evaluate(sel, CONDS, 1)
P('SELECTION base:', {k: round(v, 3) for k, v in base.items()})
P(R1.round(3).to_string(index=False))
c1 = R1[R1.cand].sort_values('d_ratio', ascending=False)
adopted = []; R2 = pd.DataFrame(); B2 = pd.DataFrame()
if len(c1):
    first = c1.iloc[0]; adopted.append(dict(cond=first.cond, exclude=first.excl)); P('\nfirst adopted:', first.cond, first.excl)
    s2 = sel[sel[first.cond] != first.excl].reset_index(drop=True)
    base2, R2, B2 = evaluate(s2, [c for c in CONDS if c != first.cond], 2)
    P('conditional base:', {k: round(v, 3) for k, v in base2.items()}); P(R2.round(3).to_string(index=False))
    c2 = R2[R2.cand].sort_values('d_ratio', ascending=False)
    if len(c2): adopted.append(dict(cond=c2.iloc[0].cond, exclude=c2.iloc[0].excl)); P('second adopted:', c2.iloc[0].cond, c2.iloc[0].excl)
else:
    P('\nno candidate passed (a)-(c) -> no filter adopted')
pd.concat([R1, R2]).to_csv(os.path.join(OUT, 'r6_select_rules.csv'), index=False)
pd.concat([B1, B2]).to_csv(os.path.join(OUT, 'r6_select_buckets.csv'), index=False)
now = log(f'r6_select: FROZEN choice = {adopted} (selection period only; no validation statistic computed yet)')
json.dump(dict(frozen_utc=now, adopted=adopted, selection_base=base, n_buckets_stage1=int(len(B1)), n_buckets_stage2=int(len(B2)),
               note='written before any validation-period statistic of the filtered rule was computed'),
          open(os.path.join(OUT, 'r6_frozen.json'), 'w'), indent=1, default=float)
open(os.path.join(OUT, 'r6_select.log'), 'w').write('\n'.join(L))
