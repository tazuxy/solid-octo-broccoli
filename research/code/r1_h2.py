"""H2: diversified vol-targeted time-series momentum (managed-futures style).
signal_i = sign(mean(r_1m, r_3m, r_12m)) with 21/63/252-day close-to-close returns at the decision close;
raw weight = signal / sigma_i(60d, annualised); portfolio scaled so ex-ante vol (60-day covariance) = 8%;
weekly rebalance at the next D1 open; cost = |dw| * COST/2 per instrument per rebalance.
Variant a: all instruments of the (sub-)portfolio. Variant b: excluding JPY crosses and XAU."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_common import *

def run(insts, cost_mult=1.0, target=0.08, start_week=None, extra=None):
    C, Cf, X = panels()
    Cf = Cf[insts]; Xs = X[insts]
    lr = np.log(Cf).diff()
    sch = weekly_schedule(Cf.index)
    rows = []; prev = pd.Series(0.0, index=insts)
    for k in range(len(sch) - 1):
        d, ex, ex1 = sch.dec[k], sch['exec'][k], sch['exec'][k + 1]
        i = Cf.index.get_loc(d)
        if i < 252: continue
        p = Cf.iloc[i]
        sig = np.sign(((p / Cf.iloc[i - 21] - 1) + (p / Cf.iloc[i - 63] - 1) + (p / Cf.iloc[i - 252] - 1)) / 3)
        win = lr.iloc[i - 59:i + 1]
        ok = sig.notna() & (win.notna().sum() >= 55) & Cf.iloc[i - 252].notna()
        w = pd.Series(0.0, index=insts)
        if ok.sum() > 0:
            o = ok[ok].index
            vol = win[o].std() * np.sqrt(252)
            raw = sig[o] / vol
            cov = win[o].cov() * 252
            pv = np.sqrt(raw.values @ cov.values @ raw.values)
            w[o] = raw * target / pv
        cf = pd.Series({q: cost_frac(q, Xs.loc[ex, q]) if not np.isnan(Xs.loc[ex, q]) else 0 for q in insts}) * cost_mult
        dw = (w - prev).abs(); cost_i = dw * cf / 2
        r = (Xs.loc[ex1] / Xs.loc[ex] - 1).fillna(0.0)
        g = w * r
        rows.append(dict(dec=d, t=ex1, gross=g.sum(), cost=cost_i.sum(), net=g.sum() - cost_i.sum(),
                         turnover=dw.sum(), gross_lev=w.abs().sum(), n=int(ok.sum()),
                         **{f'p_{q}': g[q] - cost_i[q] for q in insts}, **{f'w_{q}': w[q] for q in insts}))
        prev = w
    return pd.DataFrame(rows).set_index('t')

GROUPS = {
    'a': {'D': DESIGN, 'C': CROSS, 'ALL': ALL},
    'b': {'D': [p for p in DESIGN if p != 'XAUUSD'], 'C': [p for p in CROSS if p not in JPYX],
          'ALL': [p for p in ALL if p != 'XAUUSD' and p not in JPYX]},
}
if __name__ == '__main__':
    for var, gs in GROUPS.items():
        for g, insts in gs.items():
            for cm in (1.0, 1.5, 2.0):
                w = run(insts, cm)
                w.to_parquet(os.path.join(OUT, f'r1_h2{var}_{g}_c{cm}.parquet'))
                print(var, g, cm, len(w), 'ann gross %.4f net %.4f t %.2f realised vol %.3f turnover/wk %.2f lev %.2f' %
                      (ann_ret(w.gross), ann_ret(w.net), tstat(w.net), w.net.std() * np.sqrt(52), w.turnover.mean(), w.gross_lev.mean()))
