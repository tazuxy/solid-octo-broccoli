"""Markdown tables for fam_report.md (generated from fam_* csv outputs)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fam_common import *
def f(v, d=3): return '—' if pd.isna(v) else f'{v:+.{d}f}' if isinstance(v, float) else str(v)
def nm(s): return str(s).replace(' | ', ' / ')
def ok(b): return '○' if b else '×'
cr = pd.read_csv(os.path.join(OUT, 'fam_criteria.csv'))
L = ['| 戦略 | N | 平均R | 設計IS | 設計OOS | 検証IS | 検証OOS | t値 | 合計R | 最大DD(R) | 合計R/DD | 黒字銘柄 | ①4区分 | ②t≥2 | ③比≥3 | ④N≥100 | ⑤≥12銘柄 | 判定 |',
     '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:-:|:-:|:-:|:-:|:-:|:-:|']
for _, r in cr.iterrows():
    L.append(f"| {nm(r.strat)} | {r.N} | {f(r.avgR)} | {f(r.avgR_dIS)} | {f(r.avgR_dOOS)} | {f(r.avgR_cIS)} | {f(r.avgR_cOOS)} | {r.t:.2f} | {r.sumR:.0f} | {r.maxDD_R:.0f} | {r.sumR_DD:.2f} | {r.pairs_pos} | "
             f"{ok(r.C1_4cells)} | {ok(r.C2_t)} | {ok(r.C3_ratio)} | {ok(r.C4_N)} | {ok(r.C5_pairs)} | {'候補' if r.CANDIDATE else '不合格'} |")
open(os.path.join(OUT, 'fam_md_criteria.md'), 'w').write('\n'.join(L) + '\n')
sc = pd.read_csv(os.path.join(OUT, 'fam_screen.csv'))
x = sc[(sc.group == 'all') & (sc.dir != 'both')]
L = ['| 戦略 | 買い N | 買い IS | 買い OOS | 売り N | 売り IS | 売り OOS |', '|---|---:|---:|---:|---:|---:|---:|']
for st in cr.strat:
    g = x[x.strat == st].set_index(['dir', 'period'])
    L.append(f"| {nm(st)} | {int(g.loc[('buy','ALL'),'N'])} | {f(g.loc[('buy','IS'),'avgR'])} | {f(g.loc[('buy','OOS'),'avgR'])} | {int(g.loc[('sell','ALL'),'N'])} | {f(g.loc[('sell','IS'),'avgR'])} | {f(g.loc[('sell','OOS'),'avgR'])} |")
open(os.path.join(OUT, 'fam_md_buysell.md'), 'w').write('\n'.join(L) + '\n')
fl = pd.read_csv(os.path.join(OUT, 'fam_filters.csv'))
L = ['| 対象 | フィルター | N | 設計IS | 設計OOS | 検証IS | 検証OOS | 改善幅(最小) | t値 | 合計R/DD | 4区分一貫 |', '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|:-:|']
short = {'F2 EMA cross | 50/200 exit cross | D1': 'EMA50/200 D1', 'F1 Donchian | N100 exit trail3 | H4': 'Donchian100 H4 trail', 'F1 Donchian | N50 exit chan25 | H4': 'Donchian50 H4 chan'}
for _, r in fl.iterrows():
    L.append(f"| {short[r.strat]} | {nm(r['filter'])} | {r.N} | {f(r.dIS)} | {f(r.dOOS)} | {f(r.cIS)} | {f(r.cOOS)} | {f(r.delta_min)} | {r.t:.2f} | {r.sumR_DD:.2f} | {'○' if r.consistent else '×'} |")
open(os.path.join(OUT, 'fam_md_filters.md'), 'w').write('\n'.join(L) + '\n')
cb = pd.read_csv(os.path.join(OUT, 'fam_combo.csv'))
L = ['| ルール | N | 平均R | 設計IS | 設計OOS | 検証IS | 検証OOS | t値 | 合計R | 最大DD(R) | 合計R/DD | 黒字銘柄 |', '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for _, r in cb.iterrows():
    L.append(f"| {nm(r['filter'])} | {r.N} | {f(r.avgR)} | {f(r.dIS)} | {f(r.dOOS)} | {f(r.cIS)} | {f(r.cOOS)} | {r.t:.2f} | {r.sumR:.0f} | {r.maxDD_R:.0f} | {r.sumR_DD:.2f} | {r.pairs_pos}/18 |")
open(os.path.join(OUT, 'fam_md_combo.md'), 'w').write('\n'.join(L) + '\n')
pf = pd.read_csv(os.path.join(OUT, 'fam_portfolio.csv'))
L = ['| ケース | 取引数 | 平均R | t値 | 年率(CAGR) | 最大DD | 月次Sharpe | 最長横ばい(月) | MC最大DD 中央値 | MC最大DD 95%点 |', '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for _, r in pf.iterrows():
    L.append(f"| {r.case} | {r.N} | {f(r.avgR)} | {r.t:.2f} | {r.cagr*100:+.1f}% | {r.maxdd*100:.1f}% | {r.sharpe:.2f} | {r.flat_months:.0f} | {r.mc_dd_median*100:.1f}% | {r.mc_dd_p5*100:.1f}% |")
open(os.path.join(OUT, 'fam_md_portfolio.md'), 'w').write('\n'.join(L) + '\n')
yt = pd.read_csv(os.path.join(OUT, 'fam_port_yearly.csv'), index_col=0)
cols = ['max8 cost x1.0 risk 0.5%', 'max8 cost x1.0 risk 1.0%', 'max4 cost x1.0 risk 0.5%', 'max4 cost x1.0 risk 1.0%']
L = ['| 年 | 最大8・0.5% | 最大8・1% | 最大4・0.5% | 最大4・1% |', '|---|---:|---:|---:|---:|']
for y, r in yt.iterrows(): L.append(f'| {y} | ' + ' | '.join(f'{r[c]*100:+.1f}%' for c in cols) + ' |')
open(os.path.join(OUT, 'fam_md_yearly.md'), 'w').write('\n'.join(L) + '\n')
pp = pd.read_csv(os.path.join(OUT, 'fam_port_pairs_max8.csv'))
L = ['| 銘柄 | 取引数 | 平均R | 合計R |', '|---|---:|---:|---:|']
for _, r in pp.iterrows(): L.append(f'| {r.pair} | {int(r["count"])} | {r["mean"]:+.2f} | {r["sum"]:+.1f} |')
open(os.path.join(OUT, 'fam_md_pairs.md'), 'w').write('\n'.join(L) + '\n')
print('ok')
