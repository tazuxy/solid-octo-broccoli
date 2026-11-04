"""r9c: regenerate the per-trade net R of every round-7 (library v2) and round-8 confirmation candidate,
using ONLY the 2005-2021 pool tables (out/r7_cache, built with end = 2022-01-01). The 2022-2024 holdout is never loaded:
r7_lib.load() raises unless unlock_holdout() is called, and this script never calls it. Every trade is asserted < 2022.
Output: out/r9c_cand_trades.parquet (one row per trade), out/r9c_cands.csv (candidate metadata + original verdict).
Run: python3 -I r9c_trades.py"""
import os, sys, json, warnings, numpy as np, pandas as pd
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r7_lib as L, r7_v2loop as VL, r7_loop as V1

OUT = L.OUT
assert not L._UNLOCK['ok']

def main():
    st7 = json.load(open(os.path.join(OUT, 'r7_state.json')))
    st8 = json.load(open(os.path.join(OUT, 'r8_state.json')))
    tables = VL.load_tables()
    U = VL.v1_filter(V1.load_pool()); U['param'] = U.param.astype(str); U['inst'] = U.inst.astype(str)
    assert U.t.max() < L.POOL_END and U.te.max() <= L.POOL_END
    cands, parts = [], []
    jobs = [(7, mon, ms) for mon, ms in st7['months'].items()] + [(8, y, ws) for y, ws in st8['windows'].items()]
    cid = 0
    for rnd, win, ws in jobs:
        for c, r in zip(ws['discovery'], ws['confirmation']):
            if c['kind'] == 'v2':
                T = VL.v2_trades(tables, c, VL.insts_of(c))
            else:
                T = L.trades_of(U, c['inst'], c['param'], c['d']); T['inst'] = c['inst']
                T['netR2'] = (T.gross - 2 * T.cost) / T.R
            T = T.copy()
            assert len(T) == 0 or (pd.to_datetime(T.t_ent).max() < L.POOL_END)
            win_i = int(win)
            if rnd == 7: inwin = T.month.values == win_i
            else: inwin = (T.month.values // 100) == win_i
            T['inwin'] = inwin
            T['cid'] = cid
            parts.append(T[['cid', 'inst', 't_ent', 't_exit', 'net', 'netR', 'netR2', 'inwin']])
            cands.append(dict(cid=cid, round=rnd, window=win_i, rank=c['rank'], kind=c['kind'], tf=c['tf'], inst=c['inst'],
                              pooled=c['inst'] == 'POOL', out=c.get('out', '-'), cand=VL.cand_str(c), family=VL.family_of(c),
                              t_disc=c['t'], orig_N=r['N'], orig_mean_R=r['mean_R'], orig_t_used=r.get('t_used', np.nan),
                              orig_blocks=r['blocks_pos'], orig_verdict=r['verdict']))
            cid += 1
        print(rnd, win, cid, flush=True)
    TR = pd.concat(parts, ignore_index=True)
    TR['t_ent'] = pd.to_datetime(TR.t_ent); TR['t_exit'] = pd.to_datetime(TR.t_exit)
    assert TR.t_ent.max() < L.POOL_END
    TR.to_parquet(os.path.join(OUT, 'r9c_cand_trades.parquet'))
    pd.DataFrame(cands).to_csv(os.path.join(OUT, 'r9c_cands.csv'), index=False)
    print('done', len(cands), len(TR))

if __name__ == '__main__':
    main()
