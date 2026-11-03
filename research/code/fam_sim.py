"""Generic trade simulator for the strategy-family screen (fam_*).
Rules (no look-ahead):
  * signal evaluated on CLOSED bar i, entry at open[i+1]
  * initial SL = entry -/+ sl_atr * ATR[i]   (or an explicit price via sl_price)
  * stops are checked intrabar from the entry bar on; a gap through the stop fills at the open
  * optional Chandelier trail: stop = max(stop, highest high since entry - trail_atr*ATR[j]) updated at close j,
    effective from bar j+1 (mirror for shorts)
  * optional exit-signal arrays (exit_long / exit_short, bool at bar close j) -> exit at open[j+1]
  * optional TP in R multiples (tp_R); if SL and TP are both touched inside one bar the SL is assumed first
  * optional force_exit bool array (exit at close of that bar, e.g. flat by 17:00 EST)
  * time stop: after max_bars bars in the trade exit at the close
  * one position per instrument; a new entry signal is accepted only at bar >= the bar that decided the exit
  * cost = COST_PIPS*PIP per trade (round trip); R = (pnl - cost) / initial risk
"""
import numpy as np, pandas as pd

def simulate(ts, o, h, l, c, a, sig_idx, sig_dir, cost, sl_atr=2.0, sl_price=None, trail_atr=None,
             exit_long=None, exit_short=None, tp_R=None, force_exit=None, max_bars=500, feats=None, bar_td=None):
    n = len(c); rows = []; free_from = -1
    order = np.argsort(sig_idx, kind='stable')
    sig_idx = np.asarray(sig_idx)[order]; sig_dir = np.asarray(sig_dir)[order]
    slp = None if sl_price is None else np.asarray(sl_price)[order]
    for k in range(len(sig_idx)):
        i = int(sig_idx[k]); d = int(sig_dir[k])
        if i < free_from or i + 1 >= n: continue
        if np.isnan(a[i]): continue
        ent = o[i+1]
        sl = (ent - d * sl_atr * a[i]) if slp is None else slp[k]
        risk = d * (ent - sl)
        if not (risk > 0): continue
        tp = ent + d * tp_R * risk if tp_R else None
        stop = sl; ext = ent  # best price since entry
        ex = None; reason = ''; j = i + 1; dec = None
        while j < n:
            if d == 1:
                if o[j] <= stop: ex, reason = o[j], 'sl'; break
                if l[j] <= stop: ex, reason = stop, 'sl'; break
                if tp is not None and h[j] >= tp: ex, reason = (max(o[j], tp) if j > i+1 else tp), 'tp'; break
                ext = max(ext, h[j])
            else:
                if o[j] >= stop: ex, reason = o[j], 'sl'; break
                if h[j] >= stop: ex, reason = stop, 'sl'; break
                if tp is not None and l[j] <= tp: ex, reason = (min(o[j], tp) if j > i+1 else tp), 'tp'; break
                ext = min(ext, l[j])
            if force_exit is not None and force_exit[j]: ex, reason = c[j], 'flat'; break
            if j - i >= max_bars: ex, reason = c[j], 'time'; break
            el = exit_long if d == 1 else exit_short
            if el is not None and el[j]:
                if j + 1 < n: ex, reason, dec = o[j+1], 'sig', j; j = j + 1
                else: ex, reason = c[j], 'end'
                break
            if trail_atr is not None and not np.isnan(a[j]):
                if d == 1: stop = max(stop, ext - trail_atr * a[j])
                else: stop = min(stop, ext + trail_atr * a[j])
            j += 1
        if ex is None: j = n - 1; ex = c[j]; reason = 'end'
        pnl = d * (ex - ent) - cost
        xt = ts[j] if (reason == 'sig' or bar_td is None) else ts[j] + bar_td
        row = dict(i=i, t=ts[i], entry_t=ts[i+1], exit_t=xt, dir=d, entry=ent, exit=ex, bars=j - i,
                   reason=reason, r=pnl / risk, cost_r=cost / risk, risk_atr=risk / a[i])
        if feats is not None:
            for kf, v in feats.items(): row[kf] = v[i]
        rows.append(row)
        free_from = dec if dec is not None else j
    return pd.DataFrame(rows)
