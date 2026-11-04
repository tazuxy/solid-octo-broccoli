"""Round 8 diagnostics (after r8_loop.py): hit-rate of the 20 discovery winners per window vs round 7 (1-month windows,
library v2, from out/r7_state.json), family breakdown, full candidate list. Outputs out/r8_diag.json, out/r8_diag.md,
out/r8_candidates.csv; the tables are also appended to out/r8_loop_log.md."""
import os, sys, json, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r7_lib as L, r7_v2loop as VL
L.STATE = os.path.join(L.OUT, 'r8_state.json'); L.LOG = os.path.join(L.OUT, 'r8_loop_log.md')
T_MIN = 3.4

st8 = json.load(open(L.STATE)); st7 = json.load(open(os.path.join(L.OUT, 'r7_state.json')))

def fam8(c):
    """user's family names: time, calendar, candle, indicator, zone, Dow, trendline, combination (+ price-reaction for v1 F4/F6)."""
    if c['kind'] == 'v2' and c['conds']: return 'combination'
    return VL.family_of(c)

def dist(ts):
    t = np.array(ts, float)
    return dict(n=len(t), median=float(np.nanmedian(t)), gt0=int((t > 0).sum()), gt2=int((t > 2).sum()), ge34=int((t >= T_MIN).sum()),
                ge35=int((t >= 3.5).sum()))

rows = []; win = []
for y, ws in st8['windows'].items():
    if 'confirmation' not in ws: continue
    ts = []
    for c, r in zip(ws['discovery'], ws['confirmation']):
        ts.append(r['t_used'])
        rows.append(dict(round=8, window=int(y), rank=c['rank'], candidate=VL.cand_str(c), kind=c['kind'], family=fam8(c),
                         trigger_family=VL.family_of(c), pooled=c['inst'] == 'POOL', tf=c['tf'], events_window=c['n'], t_window=c['t'],
                         N=r['N'], mean_pips=r['mean_pips'], mean_R=r['mean_R'], t_trades=r['t_R'], t_daily=r['t_day'], t_used=r['t_used'],
                         mean_R_2x=r['mean_R_2x'], blocks_pos=r['blocks_pos'], pairs_pos=r.get('pairs_pos', ''), rollover_ok=r['hours']['ok'],
                         hours=r['hours']['txt'], verdict=r['verdict'], fails=','.join(k for k, v in r['crit'].items() if not v)))
    win.append(dict(round=8, window=str(y), k=ws['k'], **dist(ts), confirmed=sum(r['verdict'] == 'CONFIRMED' for r in ws['confirmation'])))
r7rows = []
for m, ms in st7['months'].items():
    if 'confirmation' not in ms: continue
    ts = [r['t_used'] for r in ms['confirmation']]
    win.append(dict(round=7, window=f'{m[:4]}-{m[4:]}', k=ms['k'], **dist(ts), confirmed=sum(r['verdict'] == 'CONFIRMED' for r in ms['confirmation'])))
    for c, r in zip(ms['discovery'], ms['confirmation']):
        r7rows.append(dict(family=fam8(c), t_used=r['t_used'], mean_R=r['mean_R']))
C = pd.DataFrame(rows); W = pd.DataFrame(win); R7 = pd.DataFrame(r7rows)
C.to_csv(os.path.join(L.OUT, 'r8_candidates.csv'), index=False)
agg = {}
for rd, sub in (('round 7 (1-month, v2, 12 months, 240 tests)', R7.t_used), ('round 8 (12-month, 8 windows max)', C.t_used if len(C) else pd.Series(dtype=float))):
    agg[rd] = dist(sub.values) | dict(pos_mean_share=float((sub > 0).mean()) if len(sub) else np.nan)
fam = C.groupby('family').agg(n=('t_used', 'size'), confirmed=('verdict', lambda v: int((v == 'CONFIRMED').sum())),
                              pos=('mean_R', lambda v: int((v > 0).sum())), t_gt2=('t_used', lambda v: int((v > 2).sum())),
                              median_t=('t_used', 'median'), best_t=('t_used', 'max')).reset_index() if len(C) else pd.DataFrame()
fam7 = R7.groupby('family').agg(n7=('t_used', 'size'), pos7=('mean_R', lambda v: int((v > 0).sum())), t_gt2_7=('t_used', lambda v: int((v > 2).sum())),
                                median_t7=('t_used', 'median')).reset_index()
fam = fam.merge(fam7, on='family', how='outer').fillna({'n': 0, 'n7': 0})
fails = C.fails.str.split(',').explode().value_counts().to_dict() if len(C) else {}
json.dump(dict(windows=W.to_dict(orient='records'), aggregate=agg, family=fam.to_dict(orient='records'), fail_reasons=fails),
          open(os.path.join(L.OUT, 'r8_diag.json'), 'w'), indent=1, default=float)

def md(df):
    def fm(v): return f'{v:.2f}' if isinstance(v, (float, np.floating)) else str(v)
    cols = list(df.columns); out = ['| ' + ' | '.join(map(str, cols)) + ' |', '|' + '---|' * len(cols)]
    for r in df.itertuples(index=False): out.append('| ' + ' | '.join(fm(v) for v in r) + ' |')
    return '\n'.join(out)
txt = ["\n# Diagnostics (r8_diag.py)\n", "## Confirmation t of the 20 discovery winners per window (t used = min(trade t, daily t))\n", md(W),
       "\n## Aggregate: round 8 (12-month windows) vs round 7 (1-month windows, library v2)\n",
       md(pd.DataFrame(agg).T.reset_index().rename(columns={'index': 'round'})),
       "\n## Family breakdown (round 8 n/confirmed/positive/t>2; round 7 v2 columns with suffix 7)\n", md(fam),
       f"\n## Failed criteria count (round 8, a candidate can fail several)\n\n{fails}\n"]
open(os.path.join(L.OUT, 'r8_diag.md'), 'w').write('\n'.join(txt))
L.logmd('\n'.join(txt))
print('\n'.join(txt))
