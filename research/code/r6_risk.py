"""Round 6 step 5: risk management for base and final rule. Stops none / 2R / 3R (M5 bid lows; gap through -> bar open),
cost 0.5 pip, compounding, one position at a time. Equity risk f per risk unit (unit = R without stop, = stop distance with stop).
MC: 10,000 iid bootstraps of the per-trade returns -> maxDD 95th percentile (5% worst). Swap not modelled. Also r6_equity.png."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r6_common import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fz = json.load(open(os.path.join(OUT, 'r6_frozen.json'))); cf = json.load(open(os.path.join(OUT, 'r6_confirm.json')))
ADOPT = fz['adopted'] if cf['confirmed'] else []
L = []
def P(*a): s = ' '.join(str(x) for x in a); print(s); L.append(s)
pd.set_option('display.width', 250)
allt = pd.read_parquet(os.path.join(OUT, 'r6_trades_all.parquet')); g = allt[allt.gotobi].sort_values('t_ent').reset_index(drop=True)
for k in (2, 3): g[f'gross_s{k}'] = stop_gross(g, k)
keepm = np.ones(len(g), bool)
for a in ADOPT: keepm &= (g[a['cond']] != a['exclude']).values
RULES = {'base': g, 'final': g[keepm].reset_index(drop=True)}
def dd_pct(eq):
    e = np.concatenate([[1.0], eq]); return float((e / np.maximum.accumulate(e) - 1).min())
rng = np.random.default_rng(66); rows = []; curves = {}
for rn, v in RULES.items():
    yrs = (v.t_exit.iloc[-1] - v.t_ent.iloc[0]).days / 365.25
    for stop, col, unit in (('none', 'gross_pips', 1), ('2R', 'gross_s2', 2), ('3R', 'gross_s3', 3)):
        rR = (v[col] - COST) / v.R_pips / unit          # return in risk units
        for f in (0.0025, 0.005):
            ret = f * rR.values; eq = np.cumprod(1 + ret)
            mc = np.array([dd_pct(np.cumprod(1 + rng.choice(ret, len(ret)))) for _ in range(10000)])
            vv = v.period.values == 'VAL'; eqv = np.cumprod(1 + ret[vv]); yv = (v.t_exit[vv].iloc[-1] - v.t_ent[vv].iloc[0]).days / 365.25
            rows.append(dict(rule=rn, stop=stop, risk_pct=100 * f, N=len(v), hit=(v[col] != v.gross_pips).mean() if stop != 'none' else 0.0,
                             avgR_unit=rR.mean(), CAGR=100 * (eq[-1] ** (1 / yrs) - 1), maxDD=100 * dd_pct(eq), flat_days=longest_flat_days(v.t_exit, np.log1p(ret)),
                             worst=100 * ret.min(), MC_DD95=100 * np.quantile(mc, 0.05), VAL_CAGR=100 * (eqv[-1] ** (1 / yv) - 1), VAL_maxDD=100 * dd_pct(eqv)))
            if f == 0.005 and stop == 'none': curves[rn] = (v.t_exit, eq)
R = pd.DataFrame(rows); R.to_csv(os.path.join(OUT, 'r6_risk.csv'), index=False); P(R.round(2).to_string(index=False))
open(os.path.join(OUT, 'r6_risk.log'), 'w').write('\n'.join(L))
# chart
fig, ax = plt.subplots(figsize=(10, 5.2), dpi=130); bg = '#fcfcfb'; fig.patch.set_facecolor(bg); ax.set_facecolor(bg)
ax.axvspan(pd.Timestamp('2015-01-01'), pd.Timestamp('2024-12-31'), color='#ecebe8', lw=0, zorder=0)
ax.text(pd.Timestamp('2015-03-01'), 0.98, 'Validation 2015-2024 (not used for choosing)', transform=ax.get_xaxis_transform(), va='top', fontsize=9, color='#52514e')
ax.text(pd.Timestamp('2005-03-01'), 0.98, 'Selection 2005-2014', transform=ax.get_xaxis_transform(), va='top', fontsize=9, color='#52514e')
lab = {'base': 'Base E2 (all Gotobi days)', 'final': 'Final: E2 without month-end Gotobi' if ADOPT else 'Final = base'}
cols = {'base': '#2a78d6', 'final': '#eb6834'}
for k, (t, eq) in curves.items():
    ax.plot(t, 100 * eq, color=cols[k], lw=2, label=lab[k], zorder=3)
    ax.annotate(f'{100*eq[-1]:.0f}', (t.iloc[-1], 100 * eq[-1]), xytext=(4, 0), textcoords='offset points', va='center', fontsize=9, color='#52514e')
ax.axhline(100, color='#c3c2b7', lw=0.8)
for s in ('top', 'right'): ax.spines[s].set_visible(False)
for s in ('left', 'bottom'): ax.spines[s].set_color('#c3c2b7')
ax.tick_params(colors='#52514e'); ax.grid(axis='y', color='#ecebe8', lw=0.8); ax.set_ylabel('Equity (start = 100)', color='#52514e')
ax.set_title('USDJPY Gotobi-eve long, 0.5%/R, no stop, cost 0.5 pip, swap not included', loc='left', fontsize=11, color='#0b0b0b')
ax.legend(frameon=False, loc='upper left', bbox_to_anchor=(0, 0.93), fontsize=9, labelcolor='#0b0b0b')
fig.tight_layout(); fig.savefig(os.path.join(OUT, 'r6_equity.png'), facecolor=bg)
log('r6_risk done')
