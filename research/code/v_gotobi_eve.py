"""Independent re-implementation of Gotobi day-before (E2): buy USDJPY 22:00 JST on D, sell 09:55 JST on G.
histdata time = fixed EST (UTC-5); JST = EST + 14h. Written from scratch (does not import r4/r4b code)."""
import sys, numpy as np, pandas as pd
S = sys.argv[1]
m5 = pd.read_parquet(f'{S}/bars_m5/USDJPY_M5.parquet')
op = m5['open']
def price_at(ts):  # open of the first M5 bar at or after ts, within 15 minutes
    i = op.index.searchsorted(ts)
    if i >= len(op) or op.index[i] - ts > pd.Timedelta('15min'): return np.nan
    return op.iloc[i]
days = pd.date_range('2005-01-01', '2024-12-31', freq='D')
wd = days[days.dayofweek < 5]
def prev_bd(d):
    d = d - pd.Timedelta(days=1)
    while d.dayofweek >= 5: d -= pd.Timedelta(days=1)
    return d
G = set()
for y in range(2005, 2025):
    for mth in range(1, 13):
        last = pd.Timestamp(y, mth, 1) + pd.offsets.MonthEnd(0)
        cand = [pd.Timestamp(y, mth, k) for k in (5, 10, 15, 20, 25, 30) if k <= last.day] + [last]
        for g in cand:
            while g.dayofweek >= 5: g -= pd.Timedelta(days=1)   # weekend -> preceding Friday
            G.add(g)
G = sorted(G)
def trade(D, Gd, h_in=8, m_in=0, h_out=19, m_out=55):
    t_in = D + pd.Timedelta(hours=h_in, minutes=m_in)                       # EST, = 22:00 JST on D
    t_out = Gd - pd.Timedelta(days=1) + pd.Timedelta(hours=h_out, minutes=m_out)  # EST, = 09:55 JST on G
    return price_at(t_in), price_at(t_out), t_in
rows = []
for g in G:
    D = prev_bd(g); pin, pout, t = trade(D, g)
    rows.append(dict(t=t, G=g, D=D, gdow=g.dayofweek, gday=g.day, pips=(pout - pin) / 0.01))
T = pd.DataFrame(rows).dropna()
# control: same clock window on business days whose NEXT business day is not a Gotobi day
Gs = set(G); ctrl = []
for d in wd:
    nd = d + pd.Timedelta(days=1)
    while nd.dayofweek >= 5: nd += pd.Timedelta(days=1)
    if nd in Gs: continue
    pin, pout, t = trade(d, nd); ctrl.append(dict(t=t, pips=(pout - pin) / 0.01))
C = pd.DataFrame(ctrl).dropna()
def st(x): return f'N={len(x)} mean={x.mean():.2f} t={x.mean()/(x.std()/np.sqrt(len(x))):.2f}'
for name, X in (('E2 gotobi-eve', T), ('control (non-gotobi eve)', C)):
    print(f'== {name}: gross pips {st(X.pips)} | net(0.5) {st(X.pips-0.5)}')
    for a, b in (('2005','2011'), ('2012','2018'), ('2019','2024')):
        s = X[(X.t >= a) & (X.t < str(int(b)+1))].pips - 0.5; print(f'   {a}-{b}: {st(s)}')
T['net'] = T.pips - 0.5
print('by G weekday (0=Mon):', T.groupby('gdow').net.agg(['count','mean']).round(2).T.to_string())
print('by G day:', T.assign(k=np.where(T.G.dt.is_month_end | (T.gday > 30), 'eom', T.gday)).groupby('k').net.agg(['count','mean']).round(2).T.to_string())
cs = T.net.cumsum(); print('sum pips', round(T.net.sum(),1), 'maxDD pips', round((cs - cs.cummax()).min(),1))
print('yearly net pips:', T.groupby(T.t.dt.year).net.sum().round(0).to_dict())
