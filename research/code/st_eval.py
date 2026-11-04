import os, sys, numpy as np, pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = pd.read_parquet(os.path.join(ROOT, 'out', 'st_signals.parquet'))
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 200)
rows = []
for (tf, N, mode), g in T.groupby(['tf','N','mode'], observed=True):
    for met in ('g4','n4','g16','n16','bracket'):
        x = g[met].dropna(); gg = g.loc[x.index]
        cells = gg.groupby(['group','per'], observed=True)[met].mean()
        pp = gg.groupby('pair')[met].sum()
        rows.append(dict(tf=tf, N=N, mode=mode, met=met, N_sig=len(x), avg=x.mean(), t=x.mean()/(x.std()/np.sqrt(len(x))),
                         cell_min=cells.min(), cells_pos=f'{(cells>0).sum()}/{len(cells)}', pairs_pos=f'{(pp>0).sum()}/18',
                         bull=gg[gg.side=='bull'][met].mean(), bear=gg[gg.side=='bear'][met].mean()))
R = pd.DataFrame(rows); R.to_csv(os.path.join(ROOT, 'out', 'st_eval.csv'), index=False)
tfo = {'M15':0,'H1':1,'H4':2,'D1':3}; R['o'] = R.tf.map(tfo)
print(R.sort_values(['o','N','mode','met']).drop(columns='o').round(3).to_string(index=False))
