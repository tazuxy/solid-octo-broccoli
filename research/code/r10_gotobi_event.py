"""Method 1: trades with a major US release (NFP, CPI 08:30 ET; FOMC statement) inside the holding window
(pre-registered in research/round10/r10_gotobi_event_prereg.md). Uses the base-variant trades written by r10_gotobi_mod.py.
Usage: python3 -I r10_gotobi_event.py <REPO> <WORK>"""
import os, sys, numpy as np, pandas as pd
from zoneinfo import ZoneInfo
REPO, WORK = sys.argv[1:3]; R10 = os.path.join(REPO, 'research', 'round10'); NY = ZoneInfo('America/New_York')
T = pd.read_csv(os.path.join(WORK, 'out', 'r10_gotobi_mod_trades.csv'), parse_dates=['G', 't_in'])
T = T[T.variant == 'base'].copy(); T['t_out'] = T.G - pd.Timedelta(days=1) + pd.Timedelta(hours=19, minutes=55)
def est(d, hh, mm):
    """local NY wall time on date d -> fixed EST (UTC-5) naive timestamp"""
    loc = pd.Timestamp(d.year, d.month, d.day, hh, mm).to_pydatetime().replace(tzinfo=NY)
    return pd.Timestamp(loc.astimezone(ZoneInfo('Etc/GMT+5')).replace(tzinfo=None))
ev = []
for f, nm in (('us_nfp_release_dates.csv', 'NFP'), ('us_cpi_release_dates.csv', 'CPI')):
    for d in pd.to_datetime(pd.read_csv(os.path.join(R10, f)).date): ev.append((nm, d, est(d, 8, 30)))
for d in pd.to_datetime(pd.read_csv(os.path.join(R10, 'fomc_dates_2000_2026.tsv'), sep='\t').date):
    hh, mm = (14, 15) if d.year <= 2012 else (14, 0)          # presser days 2011-12 were 12:30 ET; any of these is inside the window on D
    ev.append(('FOMC', d, est(d, hh, mm)))
E = pd.DataFrame(ev, columns=['kind', 'date', 't_est'])
def hits(r):
    m = (E.t_est > r.t_in) & (E.t_est <= r.t_out); return ','.join(sorted(E[m].kind.unique()))
T['ev'] = T.apply(hits, axis=1); T['has'] = T.ev != ''
Dd = T.t_in.dt.normalize(); T['on_D'] = Dd.isin(set(E.date))
def st(x):
    x = np.asarray(x, float); return dict(N=len(x), mean=x.mean() if len(x) else np.nan, std=x.std(ddof=1) if len(x) > 1 else np.nan)
def curve(x):
    cs = np.cumsum(x); dd = float((cs - np.maximum(np.maximum.accumulate(cs), 0)).min()); return x.sum(), dd, x.sum() / abs(dd) if dd < 0 else np.inf
rows = []; votes_skip = votes_half = 0
for src in ('pre', 'main', 'fxcm'):
    g = T[T.src == src].sort_values('t_in'); a, b = st(g[g.has].net), st(g[~g.has].net)
    cm = a['mean'] < b['mean']; cs = a['std'] > 1.2 * b['std']
    votes_skip += int(cm and cs); votes_half += int(cs)
    by = {k: st(g[g.ev.str.contains(k)].net) for k in ('NFP', 'CPI', 'FOMC')}
    sd = st(g[g.on_D].net)
    x = g.net.values; h = g.has.values; mo = g.mon.values
    var = {'base': x, 'skip_event': x[~h], 'half_event': np.where(h, 0.5 * x, x), 'half_monday': np.where(mo, 0.5 * x, x),
           'half_monday+half_event': np.where(mo | h, 0.5 * x, x), 'half_monday+skip_event': np.where(h, 0, np.where(mo, 0.5 * x, x))}
    for k, v in var.items():
        s, dd, rt = curve(v); rows.append(dict(src=src, variant=k, sum=s, maxdd=dd, ratio=rt, mean_per_trade=v[v != 0].mean() if k.startswith('skip') else v.mean()))
    print(f'{src}: with event N={a["N"]} mean {a["mean"]:+.2f} std {a["std"]:.1f} | without N={b["N"]} mean {b["mean"]:+.2f} std {b["std"]:.1f} '
          f'| mean lower={cm} std>1.2x={cs} | ' + ' '.join(f'{k}: N={v["N"]} {v["mean"]:+.1f}/{v["std"]:.0f}' for k, v in by.items())
          + f' | event on D (any time) N={sd["N"]} mean {sd["mean"]:+.2f} std {sd["std"]:.1f}')
V = pd.DataFrame(rows); print(V.round(2).to_string(index=False))
dec = 'skip' if votes_skip >= 2 else ('half lot' if votes_half >= 2 else 'no change')
print(f'votes: skip {votes_skip}/3, std-condition {votes_half}/3 -> pre-registered recommendation: {dec}')
V.to_csv(os.path.join(WORK, 'out', 'r10_gotobi_event_variants.csv'), index=False); T.to_csv(os.path.join(WORK, 'out', 'r10_gotobi_event_trades.csv'), index=False)
