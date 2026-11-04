"""Code test of the development functions on pool data only (no state, no freeze, no holdout)."""
import sys, os, time; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r7_lib as L, r7_dev as D, pandas as pd
U = L.pool_units('EURUSD')
T0 = L.trades_of(U, 'EURUSD', 'F4_h12', 1); print(len(T0), T0.head(3))
t = time.time(); T2 = D.apply_stop(T0, 'EURUSD', 2, L.POOL_END); print('stop2 secs', round(time.time() - t, 1), 'stopped', T2.stopped.mean())
T = D.add_features(T2, 'EURUSD', L.POOL_END); print(T[D.CONDS].apply(lambda s: s.value_counts().to_dict()))
ch, tab, base = D.select_refinement(T); print(ch, base); print(tab.head(12))
M1 = D.method1_trades(L.POOL_END); print('m1', len(M1), M1.netR.mean(), 'corr', D.daily_corr(T, M1))
print(D.full_stats(T))
try:
    L.load('EURUSD', 'H1', L.HOLD_END); print('LOCK FAILED')
except RuntimeError as e: print('lock ok:', e)
