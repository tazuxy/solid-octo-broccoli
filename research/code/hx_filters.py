"""Step 2/3: candidate 'when NOT to trade' filters, evaluated per group (design/cross) x period (IS/OOS).
usage: python -I code/hx_filters.py BASE   (BASE = C or A or a name in BASES)"""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from hx import *
pd.set_option('display.width', 250)
BASES = {'A': lambda x: np.ones(len(x), bool), 'B': lambda x: x.k >= 1, 'C': BASE_C,
         'A15': lambda x: x.risk_atr <= 1.5}
CANDS = [
 ('F01 exhaustion: 2nd extreme < 0.5ATR beyond 1st', lambda x: x.gap_prev_atr.fillna(0) < 0.5),
 ('F02 exhaustion: 2nd extreme < 1.0ATR beyond 1st', lambda x: x.gap_prev_atr.fillna(0) < 1.0),
 ('F03 bars outside band (run) <= 2', lambda x: x.run_dir <= 2),
 ('F04 bars outside band (run) <= 3', lambda x: x.run_dir <= 3),
 ('F05 RSI at signal 25-40 (buy view)', lambda x: (x.rsi_dir >= 25) & (x.rsi_dir <= 40)),
 ('F06 RSI at signal >= 30 (not extreme)', lambda x: x.rsi_dir >= 30),
 ('F07 exclude 20:00 EST bar', lambda x: x.hour != 20),
 ('F08 band-width pct < 0.6', lambda x: x.bw_pct < 0.6),
 ('F09 band-width pct < 0.8', lambda x: x.bw_pct < 0.8),
 ('F10 bar range <= 1.5 ATR', lambda x: x.bar_range <= 1.5),
 ('F11 bar range <= 2.0 ATR', lambda x: x.bar_range <= 2.0),
 ('F12 D1 ATR ratio < 1.2', lambda x: x.d1_atr_ratio < 1.2),
 ('F13 D1 ATR ratio < 1.5', lambda x: x.d1_atr_ratio < 1.5),
 ('F14 TP distance >= 1.0 ATR', lambda x: x.tp_atr >= 1.0),
 ('F15 TP distance >= 1.5 ATR', lambda x: x.tp_atr >= 1.5),
 ('F16 TP/risk >= 1.0', lambda x: x.tp_atr / x.risk_atr >= 1.0),
 ('F17 close in extreme half of bar', lambda x: x.close_pos_dir <= 0.5),
 ('F18 close in extreme third of bar', lambda x: x.close_pos_dir <= 0.33),
 ('F19 last D1 body |.| < 1.0 D1ATR', lambda x: x.d1_body_abs < 1.0),
 ('F20 last D1 body |.| < 1.5 D1ATR', lambda x: x.d1_body_abs < 1.5),
 ('F21 3-day move against < 3 D1ATR', lambda x: x.d1_ret3_dir > -3),
 ('F22 ref-point RSI oversold (<30 buy view)', lambda x: x.ref_rsi_dir < 30),
 ('F23 ref-point RSI < 35', lambda x: x.ref_rsi_dir < 35),
 ('F24 RSI divergence gap >= 10', lambda x: x.rsi_gap >= 10),
 ('F25 new extreme < 1.0 ATR beyond ref point', lambda x: x.ref_gap_atr < 1.0),
 ('F26 H4 ADX < 30 (no strong trend)', lambda x: x.adx < 30),
 ('F27 D1 ADX < 30', lambda x: x.d1_adx < 30),
 ('F28 deep counter-trend: D1 dist20 >= 1 ATR', lambda x: -x.dir * x.d1_dist20 >= 1),
 ('F29 ATR ratio (H4) < 1.2', lambda x: x.atr_ratio < 1.2),
 ('F30 exclude JPY crosses (post-hoc, snooping)', lambda x: ~(x.jpy & (x.grp == 'cross'))),
]
def row(m, mask, name, base_cells=None):
    x = no_overlap(m[mask].sort_values('t')); c = cells(x)
    st = rstats(x)
    r = dict(filter=name, N=len(x), avgR=st['avgR'], t=st['t'], sumR=st['sumR'], maxDD=st['maxDD_R'])
    for k, (n, v) in c.items(): r[k] = v; r['n_' + k] = n
    for g in ('design', 'cross'):
        y = x[x.grp == g]; r[f'{g[:3]}_all'] = y.r.mean()
    if base_cells is not None:
        d = [r[k] - base_cells[k] for k in ('des_IS', 'des_OOS', 'cro_IS', 'cro_OOS')]
        r['n_pos_delta'] = sum(v > 0 for v in d); r['min_delta'] = min(d)
    return r
if __name__ == '__main__':
    bname = sys.argv[1] if len(sys.argv) > 1 else 'C'
    extra = sys.argv[2] if len(sys.argv) > 2 else None   # optional extra base condition, python expr on x
    m = pd.read_parquet(os.path.join(ROOT, 'out', 'signals_all_aug.parquet'))
    base = BASES[bname](m)
    if extra: base = base & eval(extra, {'np': np}, {'x': m})
    b = row(m, base, f'BASE {bname}' + (f' & {extra}' if extra else ''))
    rows = [b] + [row(m, base & f(m), n, b) for n, f in CANDS]
    t = pd.DataFrame(rows)
    cols = ['filter','N','avgR','t','sumR','maxDD','des_all','cro_all','des_IS','des_OOS','cro_IS','cro_OOS','n_des_IS','n_des_OOS','n_cro_IS','n_cro_OOS','n_pos_delta','min_delta']
    t = t[cols]; print(t.round(3).to_string(index=False))
    tag = bname + ('_x' if extra else '')
    t.to_csv(os.path.join(ROOT, 'out', f'filters_{tag}.csv'), index=False)
