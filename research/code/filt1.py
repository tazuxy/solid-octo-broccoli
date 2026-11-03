"""Conditional analysis: avg R of signal trades bucketed by candidate filter features (IS 2012-2018 / OOS 2019-2024)."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from bt import *
PAIRS = ['EURUSD','GBPUSD','USDJPY','AUDUSD','USDCAD','USDCHF','NZDUSD','XAUUSD']
tf = sys.argv[1]; model = sys.argv[2] if len(sys.argv) > 2 else 'mid_sl1.0_32'
tr = pd.read_parquet(os.path.join(ROOT,'out', sys.argv[3] if len(sys.argv)>3 else 'trades_bt1.parquet')); tr = tr[(tr.tf==tf)&(tr.model==model)]
feats = []
for p in PAIRS:
    f = pd.read_parquet(os.path.join(ROOT,'out',f'feat_{p}_{tf}.parquet')).reset_index(drop=True)
    f['i'] = np.arange(len(f)); f['pair'] = p; feats.append(f)
F = pd.concat(feats)
m = tr.merge(F, on=['pair','i'], how='left', suffixes=('','_f'))
d = m['dir'].values
m['al_mid_slope'] = d*m.mid_slope; m['al_h4_dist50'] = d*m.h4_dist50; m['al_h4_slope50'] = d*m.h4_slope50
m['al_d1_dist20'] = d*m.d1_dist20; m['al_sma200'] = d*m.sma200_dist; m['al_h4_rsi'] = d*(m.h4_rsi-50); m['al_d1_rsi'] = d*(m.d1_rsi-50)
m['rej'] = np.where(d==1, m.close_pos, 1-m.close_pos)
m['run_out'] = np.where(d==1, m.run_lo, m.run_hi)
m['rsi_gap'] = np.where(d==1, m.rsi_gap_b, m.rsi_gap_s); m['ref_rsi'] = np.where(d==1, m.ref_rsi_b, 100-m.ref_rsi_s)
m['ref_dist'] = np.where(d==1, m.ref_dist_b, m.ref_dist_s)
m['cur_rsi'] = np.where(d==1, m.rsi, 100-m.rsi)
m['is'] = m.t < '2019-01-01'
pd.set_option('display.width', 250)
print(f'== {tf} {model}: all trades: N={len(m)} avgR={m.r.mean():.3f} IS={m[m["is"]].r.mean():.3f} OOS={m[~m["is"]].r.mean():.3f}')
def table(col, q=int(os.environ.get('Q','5')), cats=None):
    x = m[col]
    if cats is not None: b = x
    else:
        try: b = pd.qcut(x, q, duplicates='drop')
        except Exception: b = x
    g = m.groupby(b, observed=True).apply(lambda s: pd.Series({'N': len(s), 'avgR': s.r.mean(), 'win': (s.r>0).mean(),
            'R_IS': s[s['is']].r.mean(), 'R_OOS': s[~s['is']].r.mean(), 'N_OOS': (~s['is']).sum()}), include_groups=False)
    print(f'\n--- {col} ---'); print(g.round(3).to_string())
for col in ['bw_pct','bw_chg','atr_ratio','al_mid_slope','adx','h4_adx','d1_adx','al_h4_dist50','al_h4_slope50','al_d1_dist20','al_sma200',
            'al_h4_rsi','al_d1_rsi','rej','bar_range','rsi_gap','ref_rsi','ref_dist','cur_rsi','risk_atr','d1_atr_ratio','dist_mid']:
    table(col)
for col in ['close_in','run_out','hour','dow']:
    table(col, cats=True)
print('\n--- by year ---')
print(m.groupby(m.t.dt.year).apply(lambda s: pd.Series({'N': len(s), 'avgR': s.r.mean(), 'win': (s.r>0).mean(), 'sumR': s.r.sum()}), include_groups=False).round(3).to_string())
print('\n--- by pair x dir ---')
print(m.groupby(['pair','dir']).apply(lambda s: pd.Series({'N': len(s), 'avgR': s.r.mean(), 'win': (s.r>0).mean(), 'sumR': s.r.sum(), 'IS': s[s['is']].r.mean(), 'OOS': s[~s['is']].r.mean()}), include_groups=False).round(3).to_string())
print('\n--- by exit reason ---'); print(m.groupby('reason').r.agg(['count','mean']).round(3))
m.to_parquet(os.path.join(ROOT,'out',f'merged_{tf}.parquet'))
