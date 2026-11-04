"""Round 6 step 0: write the analysis protocol (conditions, buckets, a-priori economic reasons, adoption rule) to
out/r6_protocol.json BEFORE any statistic of round 6 is computed. Timestamped in out/r6_timeline.log."""
import os, json, datetime as dt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, 'out')
now = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
P = dict(
  written_utc=now,
  base='E2: USDJPY long, buy 22:00 JST on D (08:00 EST), sell 09:55 JST on G (19:55 EST, calendar day before G). '
       'Prices = open of the M5 bar starting exactly then (skip if missing) as in r4b_s2.py. Cost 0.5 pip (also 1.0). No swap. '
       'R = 0.25 x D1 ATR(14) of the last closed D1 bar.',
  selection='G (JST date) in 2005-01-01..2014-12-31', validation='G in 2015-01-01..2024-12-31',
  pre_existing_knowledge='r4b already reported FULL-SAMPLE (2005-2024) splits by G weekday (Monday negative), by Gotobi type '
       '(5th and month-end weak) and the 5-day move < -2% filter (worse) and year-end/GW. Therefore DOW1, DOW2a and HTF5a are '
       'NOT clean in validation: their validation-period behaviour was partly seen before this protocol.',
  bucket_rules={
   'HTF1': 'D1 close (last closed bar) vs SMA200 of D1 closes: above (>=) / below',
   'HTF2': 'SMA50(D1) now minus SMA50 10 bars earlier: up (>0) / down (<=0)',
   'HTF3': 'last COMPLETED week close (weeks = D1 bars grouped Sun-Sat by close time, available after the week ends) vs SMA26 of weekly closes: above / below',
   'HTF4': 'percentile rank of current D1 ATR14 among last 250 D1 ATR14 values (incl. current): <20, 20-80, >80',
   'HTF5a': '5-D1-bar return: < -1%, -1..+1%, > +1%', 'HTF5b': '20-D1-bar return: < -2%, -2..+2%, > +2%',
   'HTF6': 'D1 ADX(14) Wilder: <20, 20-30, >30',
   'DOW1': 'weekday of G: Mon..Fri', 'DOW2a': 'Gotobi type: d5,d10,d15,d20,d25,d30,month_end (month_end wins ties)',
   'DOW2b': 'weekend-rolled (nominal date or calendar month end fell on Sat/Sun): yes / no',
   'DOW3': 'month of G: quarter-end (3,6,9,12) / other',
   'IND1': 'H4 RSI(14) of last closed H4 bar (closed <= 08:00 EST): <30, 30-70, >70',
   'IND2': 'USDJPY move 09:55 JST -> 22:00 JST on D (M5 opens): up (>0) / down (<=0)',
   'IND3': 'last closed H4 close vs H4 Bollinger(20,2) of that bar: below lower / inside / above upper',
   'IND4': '(high of last closed D1 bar - entry price) / D1 ATR14: <0.25, 0.25-1, >1'},
  a_priori_exclusion_bucket={   # condition (c): the ONLY bucket that may be excluded, with the economic reason
   'HTF1': ['below', 'long-term USDJPY downtrend = persistent yen-buying/risk-off flows can swamp the small settlement-driven dollar demand'],
   'HTF2': ['down', 'same as HTF1, medium-term'],
   'HTF3': ['below', 'same as HTF1, weekly'],
   'HTF4': ['>80', 'high-volatility (crisis) regimes: macro moves dwarf the Gotobi flow; repatriation/risk-off yen buying'],
   'HTF5a': ['<-1%', 'recent sharp yen appreciation = risk-off momentum that tends to persist for days'],
   'HTF5b': ['<-2%', 'same as HTF5a, monthly'],
   'HTF6': ['>30', 'strong D1 trend: macro trend flows dominate the small calendar flow'],
   'DOW1': ['Mon', 'weekend hold: weekend news/gap risk and Friday-NY position squaring (POST-HOC: seen in r4b full sample)'],
   'DOW2a': ['month_end', 'month-end has its own large flows (London 4pm fix rebalancing, often USD selling) that can offset importer demand (POST-HOC: seen in r4b)'],
   'DOW2b': [None, 'no a-priori reason to exclude either bucket -> reported only'],
   'DOW3': ['other', 'importer settlement concentrates at quarter / fiscal half-year ends -> other months weaker'],
   'IND1': ['>70', 'already overbought: the anticipated dollar buying is already priced in'],
   'IND2': ['up', 'already moved up during Tokyo on D: front-running done'],
   'IND3': ['above_upper', 'already stretched above the band: front-running done'],
   'IND4': ['<0.25', 'price already at/above the prior day high: front-running done']},
  adoption_rule=('Selection period only, net 0.5 pip, pips per trade. Excluded bucket E = the a-priori bucket of the condition, '
       'and only if its selection net mean < 0. (a) kept trades (all except E; trades with undefined feature are KEPT) have a '
       't-stat > base t-stat; (b) E holds >= 15% of the selection trades and >= 40 trades; (c) a-priori reason listed above. '
       'Rank by improvement of selection sum(net pips)/|maxDD pips| (kept minus base; must be > 0). Adopt at most 2 (greedy; the '
       'second is re-tested with (a),(b) and ratio improvement on the sample kept by the first). Thresholds fixed; nothing else tuned.'),
  validation_rule=('Once, after r6_frozen.json is written: filtered must beat base on sum/|maxDD| in 2015-2024 AND each excluded '
       "bucket's validation mean < kept mean. Else 'not confirmed' -> recommend base."),
  robustness='entry offsets -30,-15,0,+15,+30 min x exit offsets -10,-5,0,+5,+10 min; 1.0 pip; drop top 5% trades; '
       'yearly block bootstrap (10000); placebo: 1000 draws of N random non-Gotobi business days (D\'=previous business day), '
       'same clock window and same filter (if any).',
  risk='no stop / stop 2R / stop 3R (M5 bid lows, gap fills at bar open) at 0.25% and 0.5% equity per risk unit '
       '(risk unit = R without stop, = stop distance with stop); compounding; MC maxDD 95th pct (10000 iid bootstraps).')
json.dump(P, open(os.path.join(OUT, 'r6_protocol.json'), 'w'), indent=1, ensure_ascii=False)
open(os.path.join(OUT, 'r6_timeline.log'), 'a').write(f'{now} protocol written (r6_protocol.json) - no round-6 statistic computed yet\n')
print('ok', now)
