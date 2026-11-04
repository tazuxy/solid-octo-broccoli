# Round 8 loop log (12-month discovery windows)

Created 2026-11-04T03:35:52+00:00. Pool years 2005..2021; final holdout 2022-01..2024-12 locked in code (r7_lib.unlock_holdout needs the frozen file).
Window draw: numpy default_rng(8).choice(2005..2021, 8, replace=False) = [2017, 2021, 2018, 2007, 2008, 2012, 2015, 2009]
Library: round-7 library v2 (C candles, I indicators, Z zones, D Dow, T counter-trendlines, X combinations; per pair and pooled 17 FX) + v1 F1-F9, exactly as in r7 (code imported from r7_v2feat/r7_v2loop/r7_lib; pool tables from out/r7_cache).
Discovery: >= 30 events in the year, rank by window t on DAILY net P&L with variance floor (0.5 pip; XAU 0.30 USD), duplicate event sets removed, top 20. v1 features now also use daily-P&L t with a per-family variance floor and need >= 30 trades (round 7: unit t, >= 8 units).
Confirmation on the other 16 pool years: net mean > 0 (pips and R); min(trade t, daily t) >= 3.4 (~160 tests, one-sided 5% Bonferroni); >= 3/4 blocks positive (2005-08, 2009-12, 2013-16, 2017-21; the discovery year is excluded from its block); 2x cost > 0; pooled rules >= 60% of pairs; NOT concentrated in a rollover-adjacent hour (no 16/17/18 EST entry-or-exit hour with >= 50% of total net R, and trades not entering/exiting 16:00-18:59 EST keep mean > 0 with >= 30 trades).
Rollover validity rule (r7): no entry/exit price stamped 16:55-17:30 EST; bracket checks ignore the 17:00 bar.
Development/holdout exactly as round 7 (one refinement chosen on 2005-2014, checked 2015-2021; freeze r8_method{N}_frozen.json; one holdout look 2022-2024; accept: holdout net > 0, holdout mean >= 25% of pool mean, full 2005-2024 min(t, daily t) >= 3.0, sum/|maxDD| >= 3; daily corr <= 0.5 vs method 1 and earlier round-8 methods).
NOTE on the holdout: 2022-2024 was already looked at twice in round 7, for the two REJECTED rollover rules (AUDNZD short 16h, EURAUD long 17h); it is unused for every other rule. Method 1 has also seen it in earlier rounds.

## Window 1: 2017  (discovery 2026-11-04T03:37:25+00:00; 15301 candidate rows with >= 30 events and window t > 2.5 [v2] / any t [v1])

| # | candidate | family | events | window t | window mean net R |
|---|---|---|---|---|---|
| 1 | H4 EURCHF I_rsi_30_50 → h24 fade | indicator | 633 | 5.60 | +1.902 |
| 2 | H1 EURAUD Z_PWH_rej & macdh=-1 → h4 fade | combination (zone trigger) | 53 | 5.58 | +0.557 |
| 3 | H4 EURCHF I_bb_lh → h24 fade | indicator | 618 | 5.57 | +2.011 |
| 4 | H1 EURUSD Z_PP_at & dd1=0 & macdt=1 → h24 fade | combination (zone trigger) | 83 | 5.47 | +1.276 |
| 5 | H1 EURUSD Z_PP_at & dd1=0 & e200=-1 & macdt=1 → h24 fade | combination (zone trigger) | 35 | 5.27 | +1.547 |
| 6 | H1 EURAUD Z_SWH_rej & dh4=0 & dd1=-1 & rsi50=1 → br fade | combination (zone trigger) | 34 | 5.15 | +0.538 |
| 7 | H1 EURJPY T_a_dd1 & dd1=-1 & stz=0 → h24 fade | combination (trendline trigger) | 37 | 5.02 | +1.583 |
| 8 | H4 EURGBP I_rsi_gt70 → h12 fade | indicator | 100 | 4.73 | +1.899 |
| 9 | H1 USDCHF Z_PDL_brk & dh4=-1 & stz=0 → h4 fade | combination (zone trigger) | 41 | 4.63 | +0.609 |
| 10 | H1 CADJPY Z_R1_rej & dh4=-1 & macdt=-1 → h12 follow | combination (zone trigger) | 33 | 4.62 | +1.146 |
| 11 | H4 USDJPY C_engulf & dh4=-1 & rsi50=-1 → br fade | combination (candle trigger) | 48 | 4.61 | +1.165 |
| 12 | H4 USDJPY C_engulf & dh4=-1 & rsiz=1 → br fade | combination (candle trigger) | 41 | 4.61 | +1.260 |
| 13 | H4 EURCHF I_rsi_30_50 → h12 fade | indicator | 633 | 4.51 | +0.919 |
| 14 | H1 EURJPY T_a_any & dd1=-1 & stz=0 → h24 fade | combination (trendline trigger) | 55 | 4.50 | +1.185 |
| 15 | H4 EURJPY I_rsi_lt30 → h24 fade | indicator | 53 | 4.49 | +3.129 |
| 16 | H1 USDJPY Z_ASH_rej & dh4=-1 & rsiz=1 → h12 fade | combination (zone trigger) | 43 | 4.49 | +1.125 |
| 17 | H4 EURCHF I_bb_lh → h12 fade | indicator | 618 | 4.49 | +1.048 |
| 18 | H1 GBPUSD Z_ASL_rej & loc=PDL & rsi50=-1 → h4 fade | combination (zone trigger) | 35 | 4.49 | +0.829 |
| 19 | H1 GBPUSD Z_ASL_rej & loc=PDL → h4 fade | combination (zone trigger) | 36 | 4.48 | +0.811 |
| 20 | H1 EURCHF Z_PP_rej & dh4=0 & loc=PP & rsi50=-1 → h24 fade | combination (zone trigger) | 60 | 4.48 | +1.256 |

Confirmation on the other 16 pool years (2026-11-04T03:37:29+00:00); running test count = 20

| # | candidate | N | mean pips | mean R | t trades | t daily | gross R | 2x-cost R | blocks + | pairs + | rollover-hour check | verdict | context |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H4 EURCHF I_rsi_30_50 → h24 fade | 861 | -5.56 | -0.908 | -1.30 | -1.30 | -0.862 | -0.954 | 1/4 | other pairs 5/16 | FAIL: entry-hour top 16h +16R, 04h -8R, 12h -24R; max 16-18h share nan; ex-16-18h N 704 mean -1.026R | **limited** | same rule other 16 pairs pooled -0.091R t-1.9 |
| 2 | H1 EURAUD Z_PWH_rej & macdh=-1 → h4 fade | 624 | -1.57 | -0.044 | -0.97 | -0.98 | -0.028 | -0.060 | 1/4 | other pairs 9/16 | FAIL: entry-hour top 02h +11R, 04h +9R, 13h +7R; max 16-18h share nan; ex-16-18h N 495 mean -0.106R | **limited** | same rule other 16 pairs pooled +0.027R t2.2 |
| 3 | H4 EURCHF I_bb_lh → h24 fade | 881 | -6.39 | -0.827 | -1.43 | -1.43 | -0.781 | -0.873 | 0/4 | other pairs 4/16 | FAIL: entry-hour top 04h +47R, 00h -6R, 20h -76R; max 16-18h share nan; ex-16-18h N 679 mean -0.266R | **limited** | same rule other 16 pairs pooled -0.060R t-1.3 |
| 4 | H1 EURUSD Z_PP_at & dd1=0 & macdt=1 → h24 fade | 601 | -0.74 | +0.039 | 0.35 | 0.35 | +0.061 | +0.017 | 3/4 | other pairs 7/16 | ok: entry-hour top 19h +21R, 07h +21R, 06h +19R; max 16-18h share 0.00; ex-16-18h N 514 mean +0.062R | **limited** | same rule other 16 pairs pooled -0.011R t-0.4 |
| 5 | H1 EURUSD Z_PP_at & dd1=0 & e200=-1 & macdt=1 → h24 fade | 340 | -2.25 | +0.026 | 0.18 | 0.18 | +0.049 | +0.003 | 2/4 | other pairs 8/16 | ok: entry-hour top 19h +19R, 23h +19R, 06h +18R; max 16-18h share 0.00; ex-16-18h N 283 mean +0.092R | **limited** | same rule other 16 pairs pooled -0.030R t-0.8 |
| 6 | H1 EURAUD Z_SWH_rej & dh4=0 & dd1=-1 & rsi50=1 → br fade | 545 | +0.42 | +0.025 | 0.57 | 0.54 | +0.040 | +0.010 | 2/4 | other pairs 4/16 | ok: entry-hour top 04h +9R, 19h +9R, 21h +8R; max 16-18h share 0.16; ex-16-18h N 460 mean +0.045R | **limited** | same rule other 16 pairs pooled -0.039R t-3.9 |
| 7 | H1 EURJPY T_a_dd1 & dd1=-1 & stz=0 → h24 fade | 402 | -4.40 | -0.041 | -0.28 | -0.28 | -0.024 | -0.058 | 2/4 | other pairs 8/16 | ok: entry-hour top 03h +24R, 20h +18R, 14h +16R; max 16-18h share nan; ex-16-18h N 359 mean +0.026R | **limited** | same rule other 16 pairs pooled +0.016R t0.4 |
| 8 | H4 EURGBP I_rsi_gt70 → h12 fade | 322 | +2.50 | +0.145 | 0.61 | 0.61 | +0.183 | +0.107 | 3/4 | other pairs 7/16 | FAIL: entry-hour top 04h +47R, 16h +39R, 00h +23R; max 16-18h share 0.84; ex-16-18h N 281 mean +0.114R | **limited** | same rule other 16 pairs pooled -0.051R t-0.9 |
| 9 | H1 USDCHF Z_PDL_brk & dh4=-1 & stz=0 → h4 fade | 510 | -3.47 | -0.145 | -2.44 | -2.49 | -0.120 | -0.171 | 1/4 | other pairs 6/16 | FAIL: entry-hour top 07h +11R, 03h +9R, 15h +4R; max 16-18h share nan; ex-16-18h N 422 mean -0.110R | **limited** | same rule other 16 pairs pooled -0.013R t-0.8 |
| 10 | H1 CADJPY Z_R1_rej & dh4=-1 & macdt=-1 → h12 follow | 236 | +0.43 | -0.029 | -0.24 | -0.24 | -0.006 | -0.052 | 1/4 | other pairs 6/16 | FAIL: entry-hour top 07h +14R, 05h +11R, 06h +9R; max 16-18h share nan; ex-16-18h N 179 mean -0.175R | **limited** | same rule other 16 pairs pooled -0.051R t-1.9 |
| 11 | H4 USDJPY C_engulf & dh4=-1 & rsi50=-1 → br fade | 567 | +0.22 | +0.008 | 0.09 | 0.09 | +0.034 | -0.019 | 2/4 | other pairs 5/16 | FAIL: entry-hour top 08h +20R, 20h +9R, 12h -0R; max 16-18h share 2.47; ex-16-18h N 440 mean +0.028R | **limited** | same rule other 16 pairs pooled -0.032R t-1.6 |
| 12 | H4 USDJPY C_engulf & dh4=-1 & rsiz=1 → br fade | 506 | +1.18 | +0.042 | 0.48 | 0.48 | +0.069 | +0.016 | 3/4 | other pairs 3/16 | ok: entry-hour top 00h +24R, 08h +10R, 20h +8R; max 16-18h share 0.43; ex-16-18h N 387 mean +0.076R | **limited** | same rule other 16 pairs pooled -0.031R t-1.5 |
| 13 | H4 EURCHF I_rsi_30_50 → h12 fade | 1513 | -3.59 | -0.529 | -1.44 | -1.44 | -0.482 | -0.576 | 1/4 | other pairs 3/16 | FAIL: entry-hour top 00h +29R, 16h -0R, 20h -20R; max 16-18h share nan; ex-16-18h N 1331 mean -0.585R | **limited** | same rule other 16 pairs pooled -0.071R t-2.8 |
| 14 | H1 EURJPY T_a_any & dd1=-1 & stz=0 → h24 fade | 485 | -5.55 | -0.110 | -0.86 | -0.86 | -0.092 | -0.127 | 2/4 | other pairs 8/16 | FAIL: entry-hour top 03h +22R, 20h +10R, 14h +10R; max 16-18h share nan; ex-16-18h N 432 mean -0.083R | **limited** | same rule other 16 pairs pooled +0.032R t1.0 |
| 15 | H4 EURJPY I_rsi_lt30 → h24 fade | 232 | -6.17 | -0.315 | -0.84 | -0.84 | -0.296 | -0.333 | 1/4 | other pairs 5/16 | FAIL: entry-hour top 00h +14R, 12h -13R, 04h -17R; max 16-18h share nan; ex-16-18h N 184 mean -0.233R | **limited** | same rule other 16 pairs pooled -0.205R t-2.1 |
| 16 | H1 USDJPY Z_ASH_rej & dh4=-1 & rsiz=1 → h12 fade | 282 | +3.36 | +0.090 | 0.77 | 0.77 | +0.115 | +0.065 | 3/4 | other pairs 5/16 | ok: entry-hour top 00h +11R, 04h +11R, 09h +11R; max 16-18h share 0.43; ex-16-18h N 203 mean +0.118R | **limited** | same rule other 16 pairs pooled -0.016R t-0.7 |
| 17 | H4 EURCHF I_bb_lh → h12 fade | 1560 | -3.62 | -0.572 | -1.31 | -1.31 | -0.526 | -0.619 | 0/4 | other pairs 2/16 | FAIL: entry-hour top 00h +26R, 16h -15R, 20h -48R; max 16-18h share nan; ex-16-18h N 1329 mean -0.652R | **limited** | same rule other 16 pairs pooled -0.075R t-3.0 |
| 18 | H1 GBPUSD Z_ASL_rej & loc=PDL & rsi50=-1 → h4 fade | 408 | -0.70 | -0.051 | -0.83 | -0.83 | -0.034 | -0.068 | 1/4 | other pairs 7/16 | FAIL: entry-hour top 03h +11R, 08h +11R, 18h +5R; max 16-18h share nan; ex-16-18h N 338 mean -0.072R | **limited** | same rule other 16 pairs pooled -0.024R t-1.7 |
| 19 | H1 GBPUSD Z_ASL_rej & loc=PDL → h4 fade | 413 | -0.82 | -0.057 | -0.92 | -0.92 | -0.040 | -0.073 | 1/4 | other pairs 6/16 | FAIL: entry-hour top 03h +11R, 08h +11R, 18h +5R; max 16-18h share nan; ex-16-18h N 343 mean -0.078R | **limited** | same rule other 16 pairs pooled -0.024R t-1.7 |
| 20 | H1 EURCHF Z_PP_rej & dh4=0 & loc=PP & rsi50=-1 → h24 fade | 549 | +6.48 | +1.373 | 0.98 | 0.98 | +1.425 | +1.321 | 3/4 | other pairs 6/16 | ok: entry-hour top 20h +773R, 03h +21R, 02h +17R; max 16-18h share 0.00; ex-16-18h N 476 mean +1.622R | **limited** | same rule other 16 pairs pooled -0.030R t-1.0 |

Window result: 0 CONFIRMED, 20 limited. Confirmation t of the 20 winners: median -0.55, >0: 8, >2: 0, >=3.4: 0.

## Window 2: 2021  (discovery 2026-11-04T03:38:29+00:00; 14118 candidate rows with >= 30 events and window t > 2.5 [v2] / any t [v1])

| # | candidate | family | events | window t | window mean net R |
|---|---|---|---|---|---|
| 1 | GBPCHF F1_h18 long/follow | time | 259 | 8.77 | +0.294 |
| 2 | EURCHF F1_h18 long/follow | time | 259 | 7.85 | +0.263 |
| 3 | H1 AUDNZD Z_ASH_at & dh4=-1 & loc=SWH & macdt=-1 → br follow | combination (zone trigger) | 35 | 5.66 | +0.757 |
| 4 | NZDJPY F1_h18 long/follow | time | 259 | 5.62 | +0.189 |
| 5 | H1 AUDJPY Z_SWL_at & dh4=0 & e200=1 & rsiz=2 → h12 follow | combination (zone trigger) | 80 | 5.26 | +0.732 |
| 6 | H1 AUDJPY Z_SWL_at & dh4=0 & e200=1 & rsi50=1 → h12 follow | combination (zone trigger) | 81 | 5.19 | +0.744 |
| 7 | USDCHF F1_h18 long/follow | time | 259 | 5.18 | +0.174 |
| 8 | H1 AUDJPY Z_S1_rej & dd1=1 & e200=-1 & stz=0 → br follow | combination (zone trigger) | 30 | 5.16 | +0.746 |
| 9 | H1 EURCHF C_inside & dd1=-1 & e200=1 & rsi50=1 → h24 fade | combination (candle trigger) | 58 | 5.15 | +1.235 |
| 10 | H4 POOL Z_PDL_rej & dd1=0 & e200=1 & macdh=1 → h24 fade | combination (zone trigger) | 53 | 4.97 | +2.934 |
| 11 | H1 EURCHF C_inside & dd1=-1 & e200=1 & rsiz=2 → h24 fade | combination (candle trigger) | 53 | 4.87 | +1.278 |
| 12 | H4 USDJPY I_rsi_30_50 → h24 fade | indicator | 610 | 4.83 | +1.948 |
| 13 | H1 GBPJPY Z_S1_at & e200=1 & rsiz=1 → br fade | combination (zone trigger) | 46 | 4.82 | +0.503 |
| 14 | H4 USDJPY C_pin & dh4=-1 → h12 follow | combination (candle trigger) | 54 | 4.68 | +2.142 |
| 15 | H1 USDCHF Z_PDL_rej & dh4=1 & e200=1 & stz=0 → h12 fade | combination (zone trigger) | 30 | 4.58 | +1.397 |
| 16 | H4 USDCAD Z_SWH_rej & dd1=1 & loc=SWH & macdt=1 → br follow | combination (zone trigger) | 32 | 4.50 | +1.207 |
| 17 | H1 EURCHF C_inside & dd1=-1 & e200=1 & macdt=-1 → h24 fade | combination (candle trigger) | 33 | 4.50 | +1.692 |
| 18 | GBPJPY F1_h18 long/follow | time | 259 | 4.50 | +0.151 |
| 19 | H1 EURGBP Z_S1_rej & dd1=0 & e200=-1 & macdt=1 → br fade | combination (zone trigger) | 38 | 4.50 | +0.743 |
| 20 | H1 EURCHF C_inside & dd1=-1 & e200=1 & loc=none → h24 fade | combination (candle trigger) | 35 | 4.48 | +1.983 |

Confirmation on the other 16 pool years (2026-11-04T03:38:32+00:00); running test count = 40

| # | candidate | N | mean pips | mean R | t trades | t daily | gross R | 2x-cost R | blocks + | pairs + | rollover-hour check | verdict | context |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | GBPCHF F1_h18 long/follow | 4112 | +0.47 | +0.024 | 4.70 | 4.70 | +0.040 | +0.007 | 2/4 | other inst 7/17 | FAIL: entry-hour top 18h +97R; max 16-18h share 1.00; ex-16-18h N 0 mean nanR | **limited** | GBPJPY +0.018R t2.7, CADJPY +0.015R t2.3, AUDNZD +0.022R t2.1, h17 nanR tnan, h19 -0.016R t-2.9 |
| 2 | EURCHF F1_h18 long/follow | 4127 | +0.03 | +0.001 | 0.22 | 0.22 | +0.046 | -0.044 | 1/4 | other inst 7/17 | FAIL: entry-hour top 18h +5R; max 16-18h share 1.00; ex-16-18h N 0 mean nanR | **limited** | GBPCHF +0.024R t4.7, GBPJPY +0.018R t2.7, CADJPY +0.015R t2.3, h17 nanR tnan, h19 -0.036R t-6.3 |
| 3 | H1 AUDNZD Z_ASH_at & dh4=-1 & loc=SWH & macdt=-1 → br follow | 219 | -0.19 | +0.014 | 0.19 | 0.19 | +0.039 | -0.011 | 3/4 | other pairs 3/16 | FAIL: entry-hour top 14h +5R, 03h +5R, 08h +4R; max 16-18h share 0.66; ex-16-18h N 166 mean +0.003R | **limited** | same rule other 16 pairs pooled -0.057R t-3.6 |
| 4 | NZDJPY F1_h18 long/follow | 3693 | +0.11 | +0.012 | 1.39 | 1.39 | +0.035 | -0.010 | 2/4 | other inst 7/17 | FAIL: entry-hour top 18h +46R; max 16-18h share 1.00; ex-16-18h N 0 mean nanR | **limited** | GBPCHF +0.024R t4.7, GBPJPY +0.018R t2.7, CADJPY +0.015R t2.3, h17 nanR tnan, h19 -0.045R t-5.2 |
| 5 | H1 AUDJPY Z_SWL_at & dh4=0 & e200=1 & rsiz=2 → h12 follow | 432 | -5.48 | -0.183 | -1.43 | -1.44 | -0.161 | -0.205 | 0/4 | other pairs 7/16 | FAIL: entry-hour top 05h +15R, 18h +12R, 23h +9R; max 16-18h share nan; ex-16-18h N 329 mean -0.252R | **limited** | same rule other 16 pairs pooled -0.017R t-0.8 |
| 6 | H1 AUDJPY Z_SWL_at & dh4=0 & e200=1 & rsi50=1 → h12 follow | 435 | -5.15 | -0.169 | -1.32 | -1.34 | -0.147 | -0.191 | 1/4 | other pairs 6/16 | FAIL: entry-hour top 05h +13R, 18h +11R, 15h +10R; max 16-18h share nan; ex-16-18h N 334 mean -0.226R | **limited** | same rule other 16 pairs pooled -0.018R t-0.8 |
| 7 | USDCHF F1_h18 long/follow | 4126 | -0.14 | -0.006 | -1.22 | -1.22 | +0.019 | -0.030 | 1/4 | other inst 8/17 | FAIL: entry-hour top 18h -24R; max 16-18h share nan; ex-16-18h N 0 mean nanR | **limited** | GBPCHF +0.024R t4.7, GBPJPY +0.018R t2.7, CADJPY +0.015R t2.3, h17 nanR tnan, h19 -0.005R t-0.9 |
| 8 | H1 AUDJPY Z_S1_rej & dd1=1 & e200=-1 & stz=0 → br follow | 308 | -0.03 | +0.002 | 0.04 | 0.03 | +0.026 | -0.021 | 2/4 | other pairs 1/16 | FAIL: entry-hour top 11h +12R, 06h +6R, 10h +5R; max 16-18h share 5.92; ex-16-18h N 267 mean +0.005R | **limited** | same rule other 16 pairs pooled -0.048R t-3.0 |
| 9 | H1 EURCHF C_inside & dd1=-1 & e200=1 & rsi50=1 → h24 fade | 444 | -1.29 | -0.176 | -1.28 | -1.28 | -0.129 | -0.224 | 1/4 | other pairs 8/16 | FAIL: entry-hour top 19h +35R, 15h +23R, 12h +10R; max 16-18h share nan; ex-16-18h N 387 mean -0.161R | **limited** | same rule other 16 pairs pooled -0.018R t-0.6 |
| 10 | H4 POOL Z_PDL_rej & dd1=0 & e200=1 & macdh=1 → h24 fade | 482 | -0.41 | +0.118 | 0.39 | 0.39 | +0.141 | +0.094 | 3/4 | 8/16 | ok: entry-hour top 04h +142R, 20h +45R, 12h -6R; max 16-18h share 0.22; ex-16-18h N 370 mean +0.144R | **limited** | GBPCHF +2.885R, EURJPY +1.593R, USDCHF +1.382R, AUDNZD +1.264R |
| 11 | H1 EURCHF C_inside & dd1=-1 & e200=1 & rsiz=2 → h24 fade | 418 | -4.18 | -0.315 | -1.94 | -1.94 | -0.267 | -0.364 | 0/4 | other pairs 4/16 | FAIL: entry-hour top 05h +43R, 15h +8R, 12h +7R; max 16-18h share nan; ex-16-18h N 361 mean -0.269R | **limited** | same rule other 16 pairs pooled -0.059R t-1.9 |
| 12 | H4 USDJPY I_rsi_30_50 → h24 fade | 810 | -0.27 | -0.034 | -0.18 | -0.18 | -0.010 | -0.059 | 2/4 | other pairs 3/16 | ok: entry-hour top 20h +123R, 00h -7R, 08h -13R; max 16-18h share nan; ex-16-18h N 603 mean +0.039R | **limited** | same rule other 16 pairs pooled -0.126R t-1.9 |
| 13 | H1 GBPJPY Z_S1_at & e200=1 & rsiz=1 → br fade | 470 | -2.62 | -0.071 | -1.57 | -1.59 | -0.057 | -0.084 | 0/4 | other pairs 0/16 | FAIL: entry-hour top 13h +7R, 07h +5R, 01h +4R; max 16-18h share nan; ex-16-18h N 420 mean -0.032R | **limited** | same rule other 16 pairs pooled -0.076R t-6.5 |
| 14 | H4 USDJPY C_pin & dh4=-1 → h12 follow | 509 | +1.17 | -0.055 | -0.34 | -0.34 | -0.030 | -0.081 | 1/4 | other pairs 7/16 | ok: entry-hour top 04h +57R, 00h +19R, 20h +11R; max 16-18h share nan; ex-16-18h N 383 mean +0.139R | **limited** | same rule other 16 pairs pooled +0.003R t0.1 |
| 15 | H1 USDCHF Z_PDL_rej & dh4=1 & e200=1 & stz=0 → h12 fade | 191 | -2.24 | -0.072 | -0.53 | -0.53 | -0.048 | -0.096 | 2/4 | other pairs 8/16 | FAIL: entry-hour top 09h +17R, 18h +8R, 03h +6R; max 16-18h share nan; ex-16-18h N 131 mean -0.003R | **limited** | same rule other 16 pairs pooled +0.030R t0.8 |
| 16 | H4 USDCAD Z_SWH_rej & dd1=1 & loc=SWH & macdt=1 → br follow | 243 | -2.00 | -0.067 | -0.54 | -0.53 | -0.044 | -0.091 | 2/4 | other pairs 5/16 | FAIL: entry-hour top 00h +17R, 16h +1R, 04h -2R; max 16-18h share nan; ex-16-18h N 177 mean -0.105R | **limited** | same rule other 16 pairs pooled -0.079R t-2.6 |
| 17 | H1 EURCHF C_inside & dd1=-1 & e200=1 & macdt=-1 → h24 fade | 398 | -2.93 | -0.229 | -1.54 | -1.54 | -0.182 | -0.276 | 0/4 | other pairs 7/16 | FAIL: entry-hour top 19h +33R, 15h +8R, 22h +7R; max 16-18h share nan; ex-16-18h N 327 mean -0.169R | **limited** | same rule other 16 pairs pooled -0.017R t-0.5 |
| 18 | GBPJPY F1_h18 long/follow | 4125 | +0.41 | +0.018 | 2.72 | 2.72 | +0.031 | +0.005 | 3/4 | other inst 7/17 | FAIL: entry-hour top 18h +73R; max 16-18h share 1.00; ex-16-18h N 0 mean nanR | **limited** | GBPCHF +0.024R t4.7, CADJPY +0.015R t2.3, AUDNZD +0.022R t2.1, h17 nanR tnan, h19 -0.028R t-3.7 |
| 19 | H1 EURGBP Z_S1_rej & dd1=0 & e200=-1 & macdt=1 → br fade | 274 | +0.31 | +0.026 | 0.43 | 0.41 | +0.064 | -0.012 | 2/4 | other pairs 5/16 | FAIL: entry-hour top 16h +7R, 11h +6R, 02h +5R; max 16-18h share 0.93; ex-16-18h N 239 mean +0.008R | **limited** | same rule other 16 pairs pooled -0.034R t-2.2 |
| 20 | H1 EURCHF C_inside & dd1=-1 & e200=1 & loc=none → h24 fade | 351 | +1.37 | -0.115 | -0.75 | -0.75 | -0.069 | -0.162 | 0/4 | other pairs 9/16 | FAIL: entry-hour top 15h +13R, 09h +12R, 05h +11R; max 16-18h share nan; ex-16-18h N 308 mean -0.155R | **limited** | same rule other 16 pairs pooled +0.033R t1.0 |

Window result: 0 CONFIRMED, 20 limited. Confirmation t of the 20 winners: median -0.43, >0: 8, >2: 2, >=3.4: 1.

## Window 3: 2018  (discovery 2026-11-04T03:39:33+00:00; 15530 candidate rows with >= 30 events and window t > 2.5 [v2] / any t [v1])

| # | candidate | family | events | window t | window mean net R |
|---|---|---|---|---|---|
| 1 | H1 USDCHF Z_SWL_rej & dh4=0 & dd1=-1 & rsiz=2 → h24 fade | combination (zone trigger) | 50 | 5.11 | +1.190 |
| 2 | H1 USDCHF Z_SWL_rej & dh4=0 & dd1=-1 & rsi50=1 → h24 fade | combination (zone trigger) | 52 | 4.97 | +1.113 |
| 3 | H4 EURJPY C_doji & dd1=0 & macdt=-1 → br fade | combination (candle trigger) | 33 | 4.91 | +1.505 |
| 4 | H1 EURAUD Z_PDL_at & dd1=1 & loc=SWL & rsi50=-1 → h4 follow | combination (zone trigger) | 71 | 4.80 | +0.432 |
| 5 | H1 EURAUD Z_PDL_rej & dh4=1 & e200=1 & macdt=1 → br follow | combination (zone trigger) | 35 | 4.77 | +0.784 |
| 6 | H1 EURAUD Z_PDL_at & dd1=1 & loc=SWL → h4 follow | combination (zone trigger) | 72 | 4.76 | +0.423 |
| 7 | H1 EURAUD Z_PDL_at & dd1=1 & loc=SWL & rsiz=1 → h4 follow | combination (zone trigger) | 67 | 4.70 | +0.393 |
| 8 | H1 GBPJPY Z_ASH_at & dh4=-1 & e200=-1 & loc=SWH → br follow | combination (zone trigger) | 35 | 4.68 | +0.579 |
| 9 | H1 POOL Z_PP_at & dd1=0 & loc=PWH & macdt=1 → h24 fade | combination (zone trigger) | 37 | 4.65 | +1.415 |
| 10 | H1 USDCHF Z_SWL_at & dh4=0 & loc=SWH & macdh=-1 → br follow | combination (zone trigger) | 41 | 4.60 | +0.482 |
| 11 | H1 CADJPY Z_SWL_brk & dd1=1 & e200=-1 & rsi50=-1 → h24 follow | combination (zone trigger) | 35 | 4.56 | +1.908 |
| 12 | H1 GBPJPY Z_ASH_at & dh4=-1 & loc=SWH & rsiz=2 → br follow | combination (zone trigger) | 43 | 4.51 | +0.514 |
| 13 | H1 EURAUD Z_SWL_at & dd1=1 & loc=PDL & rsi50=-1 → h4 follow | combination (zone trigger) | 71 | 4.50 | +0.357 |
| 14 | H4 EURJPY C_doji & dd1=0 & rsi50=1 → br fade | combination (candle trigger) | 31 | 4.48 | +1.411 |
| 15 | H4 POOL Z_R1_ret & dd1=1 & e200=1 & loc=none → h24 fade | combination (zone trigger) | 59 | 4.48 | +2.735 |
| 16 | H1 EURAUD Z_SWL_at & dd1=1 & loc=PDL → h4 follow | combination (zone trigger) | 72 | 4.47 | +0.349 |
| 17 | H1 EURAUD Z_PDL_rej & e200=1 & loc=SWL & macdt=1 → br follow | combination (zone trigger) | 31 | 4.45 | +0.849 |
| 18 | H1 GBPCHF C_engulf & dh4=0 & e200=1 & loc=none → h12 fade | combination (candle trigger) | 58 | 4.45 | +0.823 |
| 19 | H4 POOL Z_PWL_rej & dd1=-1 & loc=SWL & macdh=1 → h4 fade | combination (zone trigger) | 73 | 4.44 | +0.787 |
| 20 | H4 EURJPY C_doji & dd1=0 → br fade | combination (candle trigger) | 61 | 4.41 | +1.017 |

Confirmation on the other 16 pool years (2026-11-04T03:39:35+00:00); running test count = 60

| # | candidate | N | mean pips | mean R | t trades | t daily | gross R | 2x-cost R | blocks + | pairs + | rollover-hour check | verdict | context |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H1 USDCHF Z_SWL_rej & dh4=0 & dd1=-1 & rsiz=2 → h24 fade | 246 | +5.79 | +0.152 | 0.95 | 0.95 | +0.177 | +0.128 | 3/4 | other pairs 5/16 | ok: entry-hour top 18h +15R, 02h +13R, 08h +11R; max 16-18h share 0.41; ex-16-18h N 221 mean +0.070R | **limited** | same rule other 16 pairs pooled -0.211R t-1.1 |
| 2 | H1 USDCHF Z_SWL_rej & dh4=0 & dd1=-1 & rsi50=1 → h24 fade | 248 | +5.23 | +0.132 | 0.83 | 0.83 | +0.156 | +0.107 | 3/4 | other pairs 6/16 | ok: entry-hour top 02h +13R, 18h +13R, 08h +9R; max 16-18h share 0.39; ex-16-18h N 222 mean +0.060R | **limited** | same rule other 16 pairs pooled -0.212R t-1.1 |
| 3 | H4 EURJPY C_doji & dd1=0 & macdt=-1 → br fade | 398 | -4.53 | -0.092 | -1.00 | -1.01 | -0.074 | -0.110 | 0/4 | other pairs 9/16 | ok: entry-hour top 08h +17R, 20h +9R, 00h +3R; max 16-18h share nan; ex-16-18h N 294 mean +0.015R | **limited** | same rule other 16 pairs pooled -0.007R t-0.3 |
| 4 | H1 EURAUD Z_PDL_at & dd1=1 & loc=SWL & rsi50=-1 → h4 follow | 499 | +0.51 | +0.003 | 0.06 | 0.06 | +0.018 | -0.013 | 2/4 | other pairs 7/16 | FAIL: entry-hour top 01h +7R, 08h +6R, 18h +6R; max 16-18h share 4.50; ex-16-18h N 399 mean +0.006R | **limited** | same rule other 16 pairs pooled -0.010R t-0.7 |
| 5 | H1 EURAUD Z_PDL_rej & dh4=1 & e200=1 & macdt=1 → br follow | 170 | -1.61 | -0.040 | -0.45 | -0.45 | -0.024 | -0.056 | 2/4 | other pairs 6/16 | ok: entry-hour top 12h +6R, 05h +4R, 03h +4R; max 16-18h share nan; ex-16-18h N 139 mean +0.059R | **limited** | same rule other 16 pairs pooled -0.023R t-1.4 |
| 6 | H1 EURAUD Z_PDL_at & dd1=1 & loc=SWL → h4 follow | 515 | +0.60 | +0.009 | 0.21 | 0.21 | +0.025 | -0.006 | 2/4 | other pairs 7/16 | FAIL: entry-hour top 01h +7R, 08h +6R, 11h +6R; max 16-18h share 1.05; ex-16-18h N 405 mean +0.013R | **limited** | same rule other 16 pairs pooled -0.007R t-0.6 |
| 7 | H1 EURAUD Z_PDL_at & dd1=1 & loc=SWL & rsiz=1 → h4 follow | 489 | +0.31 | +0.004 | 0.10 | 0.10 | +0.020 | -0.011 | 2/4 | other pairs 7/16 | FAIL: entry-hour top 01h +7R, 08h +6R, 18h +6R; max 16-18h share 2.68; ex-16-18h N 391 mean +0.006R | **limited** | same rule other 16 pairs pooled -0.011R t-0.8 |
| 8 | H1 GBPJPY Z_ASH_at & dh4=-1 & e200=-1 & loc=SWH → br follow | 297 | -5.54 | -0.093 | -1.55 | -1.57 | -0.080 | -0.106 | 0/4 | other pairs 4/16 | FAIL: entry-hour top 07h +7R, 22h +3R, 20h +3R; max 16-18h share nan; ex-16-18h N 257 mean -0.058R | **limited** | same rule other 16 pairs pooled -0.035R t-2.5 |
| 9 | H1 POOL Z_PP_at & dd1=0 & loc=PWH & macdt=1 → h24 fade | 268 | +1.57 | +0.061 | 0.37 | 0.37 | +0.084 | +0.037 | 1/4 | 2/3 | FAIL: entry-hour top 18h +28R, 16h +17R, 13h +16R; max 16-18h share 1.70; ex-16-18h N 230 mean -0.123R | **limited** | NZDJPY +0.421R, AUDUSD +0.281R, AUDJPY -1.064R |
| 10 | H1 USDCHF Z_SWL_at & dh4=0 & loc=SWH & macdh=-1 → br follow | 344 | -0.35 | -0.039 | -0.77 | -0.76 | -0.014 | -0.064 | 2/4 | other pairs 7/16 | FAIL: entry-hour top 11h +8R, 05h +5R, 15h +4R; max 16-18h share nan; ex-16-18h N 283 mean -0.035R | **limited** | same rule other 16 pairs pooled -0.005R t-0.3 |
| 11 | H1 CADJPY Z_SWL_brk & dd1=1 & e200=-1 & rsi50=-1 → h24 follow | 284 | -1.47 | -0.123 | -0.75 | -0.75 | -0.101 | -0.145 | 1/4 | other pairs 10/16 | FAIL: entry-hour top 21h +13R, 02h +7R, 06h +6R; max 16-18h share nan; ex-16-18h N 255 mean -0.081R | **limited** | same rule other 16 pairs pooled +0.042R t1.1 |
| 12 | H1 GBPJPY Z_ASH_at & dh4=-1 & loc=SWH & rsiz=2 → br follow | 452 | -4.57 | -0.080 | -1.71 | -1.75 | -0.067 | -0.093 | 1/4 | other pairs 1/16 | FAIL: entry-hour top 11h +8R, 07h +5R, 03h +3R; max 16-18h share nan; ex-16-18h N 407 mean -0.069R | **limited** | same rule other 16 pairs pooled -0.056R t-5.0 |
| 13 | H1 EURAUD Z_SWL_at & dd1=1 & loc=PDL & rsi50=-1 → h4 follow | 499 | +0.28 | +0.002 | 0.03 | 0.03 | +0.017 | -0.014 | 2/4 | other pairs 8/16 | FAIL: entry-hour top 01h +7R, 08h +6R, 18h +5R; max 16-18h share 7.10; ex-16-18h N 399 mean +0.009R | **limited** | same rule other 16 pairs pooled -0.008R t-0.6 |
| 14 | H4 EURJPY C_doji & dd1=0 & rsi50=1 → br fade | 376 | -4.55 | -0.144 | -1.54 | -1.55 | -0.126 | -0.163 | 1/4 | other pairs 9/16 | FAIL: entry-hour top 08h +19R, 20h -2R, 04h -3R; max 16-18h share nan; ex-16-18h N 273 mean -0.107R | **limited** | same rule other 16 pairs pooled +0.006R t0.2 |
| 15 | H4 POOL Z_R1_ret & dd1=1 & e200=1 & loc=none → h24 fade | 1059 | +6.96 | +0.183 | 1.13 | 1.07 | +0.206 | +0.160 | 4/4 | 10/17 | ok: entry-hour top 00h +133R, 20h +106R, 08h +88R; max 16-18h share 0.09; ex-16-18h N 774 mean +0.282R | **limited** | EURUSD +1.358R, EURJPY +1.283R, GBPCHF +1.036R, EURGBP +0.990R |
| 16 | H1 EURAUD Z_SWL_at & dd1=1 & loc=PDL → h4 follow | 515 | +0.35 | +0.007 | 0.17 | 0.17 | +0.023 | -0.008 | 2/4 | other pairs 8/16 | FAIL: entry-hour top 01h +7R, 08h +6R, 11h +6R; max 16-18h share 1.06; ex-16-18h N 405 mean +0.016R | **limited** | same rule other 16 pairs pooled -0.007R t-0.5 |
| 17 | H1 EURAUD Z_PDL_rej & e200=1 & loc=SWL & macdt=1 → br follow | 199 | -1.86 | -0.060 | -0.82 | -0.79 | -0.044 | -0.076 | 2/4 | other pairs 7/16 | FAIL: entry-hour top 05h +5R, 12h +5R, 11h +3R; max 16-18h share nan; ex-16-18h N 168 mean -0.016R | **limited** | same rule other 16 pairs pooled -0.004R t-0.2 |
| 18 | H1 GBPCHF C_engulf & dh4=0 & e200=1 & loc=none → h12 fade | 696 | -2.08 | -0.035 | -0.54 | -0.53 | -0.018 | -0.051 | 2/4 | other pairs 10/16 | FAIL: entry-hour top 03h +20R, 01h +12R, 04h +5R; max 16-18h share nan; ex-16-18h N 525 mean -0.045R | **limited** | same rule other 16 pairs pooled +0.019R t1.1 |
| 19 | H4 POOL Z_PWL_rej & dd1=-1 & loc=SWL & macdh=1 → h4 fade | 598 | +2.31 | +0.090 | 1.06 | 1.06 | +0.116 | +0.063 | 3/4 | 11/16 | FAIL: entry-hour top 16h +44R, 00h +29R, 08h +20R; max 16-18h share 0.83; ex-16-18h N 408 mean +0.010R | **limited** | GBPCHF +0.857R, EURUSD +0.466R, NZDUSD +0.420R, USDCHF +0.383R |
| 20 | H4 EURJPY C_doji & dd1=0 → br fade | 723 | -3.15 | -0.076 | -1.10 | -1.12 | -0.058 | -0.095 | 1/4 | other pairs 6/16 | FAIL: entry-hour top 08h +44R, 04h +17R, 20h -10R; max 16-18h share nan; ex-16-18h N 522 mean -0.017R | **limited** | same rule other 16 pairs pooled -0.007R t-0.4 |

Window result: 0 CONFIRMED, 20 limited. Confirmation t of the 20 winners: median -0.21, >0: 10, >2: 0, >=3.4: 0.

## Window 4: 2007  (discovery 2026-11-04T03:40:29+00:00; 14425 candidate rows with >= 30 events and window t > 2.5 [v2] / any t [v1])

| # | candidate | family | events | window t | window mean net R |
|---|---|---|---|---|---|
| 1 | H1 AUDNZD Z_SWH_at & e200=1 & rsi50=1 → br follow | combination (zone trigger) | 37 | 7.61 | +0.740 |
| 2 | H1 AUDNZD Z_SWH_at & e200=1 & rsiz=2 → br follow | combination (zone trigger) | 35 | 7.05 | +0.686 |
| 3 | H1 AUDNZD Z_SWH_at & e200=1 & macdh=1 → br follow | combination (zone trigger) | 32 | 6.91 | +0.709 |
| 4 | EURUSD F1_h03 short/fade | time | 259 | 5.36 | +0.240 |
| 5 | H4 USDCAD I_bb_lh → h24 follow | indicator | 819 | 5.36 | +1.850 |
| 6 | H4 USDCAD I_rsi_30_50 → h24 follow | indicator | 806 | 5.33 | +1.850 |
| 7 | H1 EURCHF Z_ASL_rej & dh4=-1 & dd1=0 & macdt=-1 → h24 follow | combination (zone trigger) | 33 | 5.02 | +1.759 |
| 8 | H4 POOL Z_PDH_at & dh4=1 & rsiz=2 → br fade | combination (zone trigger) | 716 | 5.01 | +0.410 |
| 9 | H4 POOL Z_PDH_at & dh4=1 & loc=PWH & rsiz=2 → br fade | combination (zone trigger) | 196 | 4.86 | +0.718 |
| 10 | H4 AUDNZD I_bb_uh → br fade | indicator | 59 | 4.72 | +2.059 |
| 11 | H1 GBPCHF T_a_any & dd1=1 & stz=0 → h12 fade | combination (trendline trigger) | 39 | 4.68 | +1.114 |
| 12 | H4 POOL Z_PWH_at & dh4=1 & loc=PDH & rsiz=2 → br fade | combination (zone trigger) | 196 | 4.66 | +0.689 |
| 13 | H4 POOL Z_PDH_at & dh4=1 & dd1=1 & rsiz=2 → br fade | combination (zone trigger) | 269 | 4.66 | +0.561 |
| 14 | H1 POOL C_maru & dh4=-1 & loc=ASL → h24 follow | combination (candle trigger) | 195 | 4.62 | +1.006 |
| 15 | H4 POOL Z_PDH_at & dh4=1 & e200=1 & rsiz=2 → br fade | combination (zone trigger) | 574 | 4.59 | +0.415 |
| 16 | H1 USDCAD Z_SWL_at & e200=-1 & loc=PP & macdt=1 → br follow | combination (zone trigger) | 61 | 4.57 | +0.561 |
| 17 | H4 EURJPY Z_SWL_rej & dd1=0 → h24 follow | combination (zone trigger) | 44 | 4.57 | +3.208 |
| 18 | H1 GBPUSD C_outside & dh4=1 & rsiz=2 → h12 fade | combination (candle trigger) | 107 | 4.56 | +0.723 |
| 19 | H4 POOL Z_PDH_at & dh4=1 & dd1=1 & rsi50=1 → br fade | combination (zone trigger) | 367 | 4.56 | +0.490 |
| 20 | H1 POOL C_maru & dh4=-1 & loc=ASL & rsiz=1 → h24 follow | combination (candle trigger) | 171 | 4.54 | +1.017 |

Confirmation on the other 16 pool years (2026-11-04T03:40:33+00:00); running test count = 80

| # | candidate | N | mean pips | mean R | t trades | t daily | gross R | 2x-cost R | blocks + | pairs + | rollover-hour check | verdict | context |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H1 AUDNZD Z_SWH_at & e200=1 & rsi50=1 → br follow | 2980 | -0.74 | -0.037 | -1.80 | -1.75 | -0.011 | -0.064 | 1/4 | other pairs 1/16 | FAIL: entry-hour top 15h +24R, 08h +20R, 20h +9R; max 16-18h share nan; ex-16-18h N 2477 mean -0.053R | **limited** | same rule other 16 pairs pooled -0.031R t-7.1 |
| 2 | H1 AUDNZD Z_SWH_at & e200=1 & rsiz=2 → br follow | 2918 | -0.67 | -0.036 | -1.73 | -1.68 | -0.010 | -0.063 | 1/4 | other pairs 2/16 | FAIL: entry-hour top 08h +21R, 15h +21R, 20h +9R; max 16-18h share nan; ex-16-18h N 2418 mean -0.054R | **limited** | same rule other 16 pairs pooled -0.030R t-6.8 |
| 3 | H1 AUDNZD Z_SWH_at & e200=1 & macdh=1 → br follow | 2309 | -1.05 | -0.048 | -2.01 | -1.97 | -0.022 | -0.074 | 0/4 | other pairs 2/16 | FAIL: entry-hour top 08h +14R, 22h +9R, 15h +8R; max 16-18h share nan; ex-16-18h N 1909 mean -0.062R | **limited** | same rule other 16 pairs pooled -0.031R t-6.3 |
| 4 | EURUSD F1_h03 short/fade | 4138 | -0.75 | -0.043 | -3.98 | -3.98 | -0.021 | -0.065 | 0/4 | other inst 3/17 | FAIL: entry-hour top 03h -178R; max 16-18h share nan; ex-16-18h N 4138 mean -0.043R | **limited** | GBPCHF +0.026R t2.3, h02 -0.005R t-0.6, h04 -0.012R t-1.2 |
| 5 | H4 USDCAD I_bb_lh → h24 follow | 864 | -5.75 | -0.280 | -1.62 | -1.62 | -0.257 | -0.303 | 0/4 | other pairs 10/16 | FAIL: entry-hour top 00h +8R, 20h -18R, 12h -21R; max 16-18h share nan; ex-16-18h N 679 mean -0.167R | **limited** | same rule other 16 pairs pooled +0.044R t0.8 |
| 6 | H4 USDCAD I_rsi_30_50 → h24 follow | 826 | -4.48 | -0.248 | -1.43 | -1.43 | -0.225 | -0.271 | 0/4 | other pairs 10/16 | FAIL: entry-hour top 04h -0R, 20h -1R, 16h -1R; max 16-18h share nan; ex-16-18h N 669 mean -0.230R | **limited** | same rule other 16 pairs pooled +0.072R t1.1 |
| 7 | H1 EURCHF Z_ASL_rej & dh4=-1 & dd1=0 & macdt=-1 → h24 follow | 309 | -3.59 | -0.161 | -1.35 | -1.35 | -0.110 | -0.212 | 2/4 | other pairs 4/16 | FAIL: entry-hour top 12h +16R, 13h +12R, 20h +9R; max 16-18h share nan; ex-16-18h N 285 mean -0.181R | **limited** | same rule other 16 pairs pooled -0.041R t-1.0 |
| 8 | H4 POOL Z_PDH_at & dh4=1 & rsiz=2 → br fade | 7217 | +1.39 | +0.034 | 1.52 | 1.44 | +0.057 | +0.010 | 2/4 | 10/17 | ok: entry-hour top 04h +121R, 00h +111R, 08h +81R; max 16-18h share 0.34; ex-16-18h N 5262 mean +0.047R | **limited** | GBPJPY +0.223R, GBPUSD +0.193R, EURAUD +0.180R, CADJPY +0.177R |
| 9 | H4 POOL Z_PDH_at & dh4=1 & loc=PWH & rsiz=2 → br fade | 1474 | +1.30 | +0.061 | 1.25 | 1.27 | +0.085 | +0.037 | 4/4 | 12/17 | FAIL: entry-hour top 04h +59R, 16h +48R, 08h +15R; max 16-18h share 0.53; ex-16-18h N 1097 mean +0.033R | **limited** | EURAUD +0.464R, AUDJPY +0.448R, EURGBP +0.421R, AUDUSD +0.246R |
| 10 | H4 AUDNZD I_bb_uh → br fade | 2271 | +0.16 | +0.001 | 0.02 | 0.02 | +0.028 | -0.026 | 1/4 | other pairs 3/16 | ok: entry-hour top 12h +68R, 08h +14R, 04h +10R; max 16-18h share 0.00; ex-16-18h N 1784 mean +0.051R | **limited** | same rule other 16 pairs pooled -0.047R t-5.2 |
| 11 | H1 GBPCHF T_a_any & dd1=1 & stz=0 → h12 fade | 580 | -5.51 | -0.126 | -1.55 | -1.55 | -0.109 | -0.144 | 0/4 | other pairs 9/16 | FAIL: entry-hour top 13h +9R, 23h +6R, 00h +6R; max 16-18h share nan; ex-16-18h N 440 mean -0.099R | **limited** | same rule other 16 pairs pooled +0.027R t1.4 |
| 12 | H4 POOL Z_PWH_at & dh4=1 & loc=PDH & rsiz=2 → br fade | 1473 | +1.16 | +0.067 | 1.38 | 1.39 | +0.091 | +0.043 | 4/4 | 11/17 | ok: entry-hour top 04h +63R, 16h +35R, 08h +22R; max 16-18h share 0.36; ex-16-18h N 1095 mean +0.053R | **limited** | EURAUD +0.517R, EURGBP +0.380R, AUDJPY +0.346R, EURUSD +0.290R |
| 13 | H4 POOL Z_PDH_at & dh4=1 & dd1=1 & rsiz=2 → br fade | 2235 | +0.75 | +0.003 | 0.08 | 0.08 | +0.027 | -0.020 | 2/4 | 10/17 | ok: entry-hour top 04h +72R, 08h +35R, 00h +25R; max 16-18h share 0.32; ex-16-18h N 1622 mean +0.045R | **limited** | EURAUD +0.210R, CADJPY +0.182R, GBPJPY +0.161R, AUDNZD +0.147R |
| 14 | H1 POOL C_maru & dh4=-1 & loc=ASL → h24 follow | 3071 | -2.52 | -0.079 | -1.68 | -1.71 | -0.055 | -0.103 | 0/4 | 5/17 | FAIL: entry-hour top 10h +69R, 22h +22R, 02h +15R; max 16-18h share nan; ex-16-18h N 2709 mean -0.049R | **limited** | EURUSD +0.289R, GBPCHF +0.261R, NZDUSD +0.192R, USDCHF +0.097R |
| 15 | H4 POOL Z_PDH_at & dh4=1 & e200=1 & rsiz=2 → br fade | 5042 | +0.96 | +0.035 | 1.33 | 1.30 | +0.059 | +0.012 | 2/4 | 11/17 | ok: entry-hour top 04h +133R, 00h +104R, 08h +63R; max 16-18h share 0.30; ex-16-18h N 3673 mean +0.055R | **limited** | EURAUD +0.228R, GBPUSD +0.220R, CADJPY +0.188R, GBPJPY +0.173R |
| 16 | H1 USDCAD Z_SWL_at & e200=-1 & loc=PP & macdt=1 → br follow | 383 | +0.77 | +0.020 | 0.42 | 0.41 | +0.044 | -0.004 | 2/4 | other pairs 3/16 | FAIL: entry-hour top 18h +9R, 09h +6R, 03h +5R; max 16-18h share 1.19; ex-16-18h N 300 mean -0.016R | **limited** | same rule other 16 pairs pooled -0.047R t-3.7 |
| 17 | H4 EURJPY Z_SWL_rej & dd1=0 → h24 follow | 299 | -9.64 | -0.241 | -0.76 | -0.76 | -0.222 | -0.259 | 2/4 | other pairs 6/16 | FAIL: entry-hour top 08h +15R, 20h -3R, 00h -10R; max 16-18h share nan; ex-16-18h N 221 mean -0.139R | **limited** | same rule other 16 pairs pooled -0.114R t-1.5 |
| 18 | H1 GBPUSD C_outside & dh4=1 & rsiz=2 → h12 fade | 1066 | +3.61 | +0.076 | 1.29 | 1.27 | +0.093 | +0.059 | 4/4 | other pairs 5/16 | ok: entry-hour top 03h +62R, 01h +24R, 05h +22R; max 16-18h share 0.15; ex-16-18h N 843 mean +0.120R | **limited** | same rule other 16 pairs pooled +0.007R t0.4 |
| 19 | H4 POOL Z_PDH_at & dh4=1 & dd1=1 & rsi50=1 → br fade | 2785 | -0.33 | -0.025 | -0.69 | -0.69 | -0.001 | -0.048 | 1/4 | 8/17 | FAIL: entry-hour top 08h +55R, 04h +49R, 12h +11R; max 16-18h share nan; ex-16-18h N 2125 mean -0.019R | **limited** | EURAUD +0.269R, EURCHF +0.168R, GBPJPY +0.168R, USDJPY +0.085R |
| 20 | H1 POOL C_maru & dh4=-1 & loc=ASL & rsiz=1 → h24 follow | 2600 | -2.26 | -0.075 | -1.47 | -1.46 | -0.051 | -0.100 | 1/4 | 7/17 | FAIL: entry-hour top 10h +32R, 05h +22R, 06h +21R; max 16-18h share nan; ex-16-18h N 2281 mean -0.034R | **limited** | GBPCHF +0.320R, EURUSD +0.199R, NZDUSD +0.174R, USDCHF +0.098R |

Window result: 0 CONFIRMED, 20 limited. Confirmation t of the 20 winners: median -1.06, >0: 8, >2: 0, >=3.4: 0.

## Window 5: 2008  (discovery 2026-11-04T03:41:30+00:00; 18303 candidate rows with >= 30 events and window t > 2.5 [v2] / any t [v1])

| # | candidate | family | events | window t | window mean net R |
|---|---|---|---|---|---|
| 1 | H1 USDCHF Z_ASL_rej & dh4=0 & dd1=1 & stz=0 → h12 follow | combination (zone trigger) | 33 | 5.90 | +1.628 |
| 2 | H1 EURAUD Z_SWH_at & dh4=1 & e200=-1 & macdh=-1 → h12 follow | combination (zone trigger) | 96 | 5.54 | +0.838 |
| 3 | H1 USDCHF Z_SWH_at & dd1=0 & loc=SWL & macdh=-1 → h12 follow | combination (zone trigger) | 31 | 5.34 | +1.468 |
| 4 | H4 GBPCHF I_bb_uh → h24 fade | indicator | 547 | 5.06 | +2.035 |
| 5 | H4 AUDNZD Z_SWL_rej & dh4=-1 & e200=1 & macdh=-1 → h4 fade | combination (zone trigger) | 43 | 4.92 | +1.485 |
| 6 | H4 GBPCHF Z_PP_rej & dh4=0 & macdt=1 → h24 fade | combination (zone trigger) | 63 | 4.82 | +2.983 |
| 7 | H1 AUDJPY Z_ASL_rej & dd1=1 & loc=none & rsi50=-1 → br follow | combination (zone trigger) | 40 | 4.81 | +0.701 |
| 8 | H4 AUDNZD Z_SWL_rej & dh4=-1 & e200=1 & macdh=-1 → br fade | combination (zone trigger) | 43 | 4.75 | +1.326 |
| 9 | H4 EURGBP Z_R1_at & loc=PDH & rsiz=2 → h12 fade | combination (zone trigger) | 33 | 4.67 | +3.269 |
| 10 | H1 EURGBP Z_SWH_at & e200=1 & loc=ASL → h4 follow | combination (zone trigger) | 33 | 4.67 | +0.717 |
| 11 | H4 AUDNZD Z_SWL_rej & dh4=-1 & dd1=1 & macdh=-1 → br fade | combination (zone trigger) | 32 | 4.66 | +1.339 |
| 12 | H1 EURUSD Z_PDL_at & dh4=-1 & dd1=0 & loc=PDL → h24 fade | combination (zone trigger) | 31 | 4.65 | +1.222 |
| 13 | H1 EURAUD Z_PDH_at & e200=1 & stz=1 → h4 follow | combination (zone trigger) | 88 | 4.63 | +0.428 |
| 14 | H4 GBPCHF I_rsi_50_70 → h24 fade | indicator | 568 | 4.62 | +1.815 |
| 15 | H4 NZDUSD I_rsi_gt70 → h24 fade | indicator | 50 | 4.61 | +4.561 |
| 16 | H1 NZDJPY Z_PDL_brk & dh4=0 & rsiz=1 → h4 follow | combination (zone trigger) | 44 | 4.60 | +0.729 |
| 17 | H1 GBPJPY Z_SWH_brk & e200=-1 & loc=none & stz=0 → h4 fade | combination (zone trigger) | 61 | 4.60 | +0.705 |
| 18 | H1 AUDJPY Z_S1_rej & e200=-1 & stz=0 → h12 fade | combination (zone trigger) | 103 | 4.59 | +1.350 |
| 19 | H1 GBPCHF Z_ASH_rej & e200=1 & loc=ASH & rsiz=2 → h4 follow | combination (zone trigger) | 80 | 4.58 | +0.461 |
| 20 | H4 EURUSD C_engulf & dd1=-1 & e200=-1 & stz=0 → br follow | combination (candle trigger) | 30 | 4.54 | +1.592 |

Confirmation on the other 16 pool years (2026-11-04T03:41:33+00:00); running test count = 100

| # | candidate | N | mean pips | mean R | t trades | t daily | gross R | 2x-cost R | blocks + | pairs + | rollover-hour check | verdict | context |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H1 USDCHF Z_ASL_rej & dh4=0 & dd1=1 & stz=0 → h12 follow | 363 | -0.42 | -0.062 | -0.62 | -0.63 | -0.036 | -0.088 | 1/4 | other pairs 8/16 | FAIL: entry-hour top 03h +13R, 20h +7R, 10h +6R; max 16-18h share nan; ex-16-18h N 232 mean -0.004R | **limited** | same rule other 16 pairs pooled -0.006R t-0.2 |
| 2 | H1 EURAUD Z_SWH_at & dh4=1 & e200=-1 & macdh=-1 → h12 follow | 343 | +2.48 | -0.017 | -0.18 | -0.18 | -0.001 | -0.033 | 2/4 | other pairs 5/16 | FAIL: entry-hour top 08h +11R, 09h +8R, 19h +6R; max 16-18h share nan; ex-16-18h N 266 mean -0.004R | **limited** | same rule other 16 pairs pooled -0.048R t-1.8 |
| 3 | H1 USDCHF Z_SWH_at & dd1=0 & loc=SWL & macdh=-1 → h12 follow | 208 | -3.60 | -0.203 | -1.76 | -1.77 | -0.178 | -0.229 | 0/4 | other pairs 8/16 | FAIL: entry-hour top 19h +6R, 22h +4R, 03h +4R; max 16-18h share nan; ex-16-18h N 162 mean -0.216R | **limited** | same rule other 16 pairs pooled +0.004R t0.1 |
| 4 | H4 GBPCHF I_bb_uh → h24 fade | 860 | +6.55 | +0.210 | 1.06 | 1.06 | +0.227 | +0.193 | 3/4 | other pairs 8/16 | ok: entry-hour top 12h +101R, 04h +36R, 20h +33R; max 16-18h share 0.28; ex-16-18h N 678 mean +0.188R | **limited** | same rule other 16 pairs pooled +0.016R t0.3 |
| 5 | H4 AUDNZD Z_SWL_rej & dh4=-1 & e200=1 & macdh=-1 → h4 fade | 191 | +1.20 | +0.032 | 0.22 | 0.23 | +0.059 | +0.006 | 2/3 | other pairs 2/16 | FAIL: entry-hour top 00h +11R, 16h +5R, 20h +1R; max 16-18h share 1.97; ex-16-18h N 133 mean -0.086R | **limited** | same rule other 16 pairs pooled -0.120R t-3.1 |
| 6 | H4 GBPCHF Z_PP_rej & dh4=0 & macdt=1 → h24 fade | 414 | +15.18 | +0.435 | 1.21 | 1.21 | +0.452 | +0.418 | 4/4 | other pairs 8/16 | ok: entry-hour top 12h +76R, 00h +65R, 20h +47R; max 16-18h share 0.37; ex-16-18h N 309 mean +0.332R | **limited** | same rule other 16 pairs pooled -0.028R t-0.4 |
| 7 | H1 AUDJPY Z_ASL_rej & dd1=1 & loc=none & rsi50=-1 → br follow | 412 | -1.00 | -0.051 | -0.93 | -0.94 | -0.028 | -0.074 | 2/4 | other pairs 1/16 | FAIL: entry-hour top 09h +11R, 10h +11R, 19h +6R; max 16-18h share nan; ex-16-18h N 358 mean -0.045R | **limited** | same rule other 16 pairs pooled -0.061R t-5.0 |
| 8 | H4 AUDNZD Z_SWL_rej & dh4=-1 & e200=1 & macdh=-1 → br fade | 183 | -1.36 | -0.119 | -0.81 | -0.81 | -0.092 | -0.146 | 1/3 | other pairs 3/16 | FAIL: entry-hour top 08h -0R, 20h -1R, 00h -1R; max 16-18h share nan; ex-16-18h N 150 mean -0.061R | **limited** | same rule other 16 pairs pooled -0.085R t-2.5 |
| 9 | H4 EURGBP Z_R1_at & loc=PDH & rsiz=2 → h12 fade | 306 | +6.09 | +0.304 | 1.39 | 1.39 | +0.343 | +0.265 | 4/4 | other pairs 12/16 | ok: entry-hour top 04h +61R, 12h +19R, 08h +17R; max 16-18h share 0.21; ex-16-18h N 238 mean +0.329R | **limited** | same rule other 16 pairs pooled +0.097R t1.9 |
| 10 | H1 EURGBP Z_SWH_at & e200=1 & loc=ASL → h4 follow | 330 | -1.14 | -0.057 | -0.86 | -0.87 | -0.021 | -0.094 | 1/4 | other pairs 5/16 | FAIL: entry-hour top 10h +4R, 14h +2R, 15h +2R; max 16-18h share nan; ex-16-18h N 269 mean -0.064R | **limited** | same rule other 16 pairs pooled -0.008R t-0.5 |
| 11 | H4 AUDNZD Z_SWL_rej & dh4=-1 & dd1=1 & macdh=-1 → br fade | 144 | +6.27 | +0.189 | 1.11 | 1.14 | +0.216 | +0.161 | 3/4 | other pairs 5/16 | ok: entry-hour top 08h +12R, 04h +9R, 12h +5R; max 16-18h share 0.31; ex-16-18h N 120 mean +0.117R | **limited** | same rule other 16 pairs pooled -0.060R t-1.7 |
| 12 | H1 EURUSD Z_PDL_at & dh4=-1 & dd1=0 & loc=PDL → h24 fade | 187 | -3.85 | -0.099 | -0.51 | -0.51 | -0.075 | -0.122 | 2/4 | other pairs 7/16 | FAIL: entry-hour top 23h +14R, 09h +12R, 00h +10R; max 16-18h share nan; ex-16-18h N 165 mean -0.136R | **limited** | same rule other 16 pairs pooled -0.025R t-0.6 |
| 13 | H1 EURAUD Z_PDH_at & e200=1 & stz=1 → h4 follow | 831 | +0.42 | +0.012 | 0.30 | 0.31 | +0.029 | -0.004 | 3/4 | other pairs 6/16 | FAIL: entry-hour top 07h +14R, 11h +13R, 23h +11R; max 16-18h share 0.80; ex-16-18h N 642 mean +0.024R | **limited** | same rule other 16 pairs pooled -0.015R t-1.6 |
| 14 | H4 GBPCHF I_rsi_50_70 → h24 fade | 828 | +3.72 | +0.161 | 0.81 | 0.81 | +0.178 | +0.143 | 3/4 | other pairs 4/16 | ok: entry-hour top 12h +82R, 04h +78R, 20h +51R; max 16-18h share 0.32; ex-16-18h N 690 mean +0.138R | **limited** | same rule other 16 pairs pooled -0.061R t-1.3 |
| 15 | H4 NZDUSD I_rsi_gt70 → h24 fade | 241 | -1.00 | -0.193 | -0.61 | -0.61 | -0.166 | -0.220 | 2/4 | other pairs 5/16 | FAIL: entry-hour top 20h +42R, 00h +15R, 16h +0R; max 16-18h share nan; ex-16-18h N 181 mean -0.439R | **limited** | same rule other 16 pairs pooled -0.097R t-1.1 |
| 16 | H1 NZDJPY Z_PDL_brk & dh4=0 & rsiz=1 → h4 follow | 506 | -1.80 | -0.098 | -1.67 | -1.67 | -0.074 | -0.121 | 1/4 | other pairs 6/16 | FAIL: entry-hour top 21h +7R, 16h +4R, 08h +3R; max 16-18h share nan; ex-16-18h N 437 mean -0.082R | **limited** | same rule other 16 pairs pooled -0.020R t-1.5 |
| 17 | H1 GBPJPY Z_SWH_brk & e200=-1 & loc=none & stz=0 → h4 fade | 451 | -3.32 | -0.018 | -0.29 | -0.29 | -0.005 | -0.032 | 2/4 | other pairs 7/16 | FAIL: entry-hour top 18h +8R, 11h +8R, 08h +7R; max 16-18h share nan; ex-16-18h N 385 mean -0.041R | **limited** | same rule other 16 pairs pooled -0.024R t-1.9 |
| 18 | H1 AUDJPY Z_S1_rej & e200=-1 & stz=0 → h12 fade | 712 | -0.12 | +0.003 | 0.03 | 0.03 | +0.026 | -0.020 | 2/4 | other pairs 8/16 | FAIL: entry-hour top 09h +18R, 16h +13R, 01h +12R; max 16-18h share 6.92; ex-16-18h N 534 mean +0.057R | **limited** | same rule other 16 pairs pooled +0.048R t0.9 |
| 19 | H1 GBPCHF Z_ASH_rej & e200=1 & loc=ASH & rsiz=2 → h4 follow | 1249 | -0.01 | +0.015 | 0.51 | 0.52 | +0.032 | -0.002 | 1/4 | other pairs 2/16 | ok: entry-hour top 07h +16R, 06h +16R, 08h +12R; max 16-18h share 0.26; ex-16-18h N 996 mean +0.014R | **limited** | same rule other 16 pairs pooled -0.033R t-4.0 |
| 20 | H4 EURUSD C_engulf & dd1=-1 & e200=-1 & stz=0 → br follow | 353 | -1.73 | -0.149 | -1.54 | -1.52 | -0.125 | -0.173 | 2/4 | other pairs 7/16 | FAIL: entry-hour top 00h -5R, 20h -6R, 12h -8R; max 16-18h share nan; ex-16-18h N 274 mean -0.173R | **limited** | same rule other 16 pairs pooled -0.005R t-0.2 |

Window result: 0 CONFIRMED, 20 limited. Confirmation t of the 20 winners: median -0.24, >0: 9, >2: 0, >=3.4: 0.

## Window 6: 2012  (discovery 2026-11-04T03:42:30+00:00; 13204 candidate rows with >= 30 events and window t > 2.5 [v2] / any t [v1])

| # | candidate | family | events | window t | window mean net R |
|---|---|---|---|---|---|
| 1 | H4 USDCHF Z_SWL_at & dh4=-1 & loc=PP & macdt=1 → h24 follow | combination (zone trigger) | 31 | 5.15 | +4.323 |
| 2 | H1 GBPCHF Z_PP_rej & dh4=1 & e200=-1 & macdh=-1 → br follow | combination (zone trigger) | 36 | 4.81 | +0.702 |
| 3 | H1 EURGBP Z_ASL_rej & dh4=0 & e200=1 & macdt=-1 → h4 follow | combination (zone trigger) | 32 | 4.81 | +0.762 |
| 4 | H4 USDCHF Z_SWL_at & dh4=-1 & loc=PP & rsiz=1 → h24 follow | combination (zone trigger) | 34 | 4.79 | +3.970 |
| 5 | H4 USDCHF Z_SWL_at & dh4=-1 & loc=PP → h24 follow | combination (zone trigger) | 35 | 4.76 | +3.840 |
| 6 | H4 GBPJPY I_rsi_50_70 → h24 follow | indicator | 689 | 4.64 | +1.872 |
| 7 | H1 GBPCHF Z_PDH_at & dh4=-1 & dd1=-1 & loc=PDH → br fade | combination (zone trigger) | 42 | 4.63 | +0.518 |
| 8 | H1 GBPCHF Z_PDH_at & dh4=-1 & dd1=-1 & rsi50=1 → br fade | combination (zone trigger) | 40 | 4.58 | +0.534 |
| 9 | H4 AUDUSD Z_S1_rej & dd1=0 & e200=-1 & rsi50=-1 → br fade | combination (zone trigger) | 31 | 4.57 | +1.266 |
| 10 | H1 USDCAD Z_PDL_at & e200=1 → br follow | combination (zone trigger) | 50 | 4.55 | +0.593 |
| 11 | H4 EURAUD Z_PDL_at & dd1=-1 & stz=-1 → h24 fade | combination (zone trigger) | 30 | 4.52 | +3.842 |
| 12 | H1 USDCAD Z_PDL_rej & loc=PDL & stz=-1 → br follow | combination (zone trigger) | 75 | 4.52 | +0.456 |
| 13 | H1 USDCAD Z_PDL_at & stz=-1 → br follow | combination (zone trigger) | 179 | 4.51 | +0.339 |
| 14 | H1 EURJPY Z_SWL_rej & dd1=-1 & e200=1 & rsi50=-1 → br fade | combination (zone trigger) | 36 | 4.50 | +0.667 |
| 15 | H4 USDCHF Z_SWL_at & loc=PP & macdt=1 → h24 follow | combination (zone trigger) | 47 | 4.49 | +3.171 |
| 16 | H1 AUDUSD Z_S1_rej & dh4=1 & dd1=0 & rsiz=1 → br fade | combination (zone trigger) | 31 | 4.47 | +0.807 |
| 17 | H4 POOL Z_PWL_at & dh4=0 & loc=S1 & macdt=-1 → br follow | combination (zone trigger) | 52 | 4.43 | +1.051 |
| 18 | H1 GBPJPY Z_PP_rej & dh4=0 & loc=PP → h24 fade | combination (zone trigger) | 60 | 4.42 | +1.324 |
| 19 | H1 GBPCHF Z_SWL_rej & dd1=-1 & e200=-1 & macdt=-1 → h12 fade | combination (zone trigger) | 119 | 4.37 | +0.822 |
| 20 | H4 NZDJPY Z_PP_at & dd1=1 & e200=1 & macdt=1 → br fade | combination (zone trigger) | 32 | 4.35 | +1.233 |

Confirmation on the other 16 pool years (2026-11-04T03:42:33+00:00); running test count = 120

| # | candidate | N | mean pips | mean R | t trades | t daily | gross R | 2x-cost R | blocks + | pairs + | rollover-hour check | verdict | context |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H4 USDCHF Z_SWL_at & dh4=-1 & loc=PP & macdt=1 → h24 follow | 152 | +8.70 | +0.233 | 0.50 | 0.50 | +0.258 | +0.208 | 3/4 | other pairs 6/16 | ok: entry-hour top 20h +30R, 00h +25R, 04h +18R; max 16-18h share 0.00; ex-16-18h N 100 mean +0.592R | **limited** | same rule other 16 pairs pooled -0.142R t-1.3 |
| 2 | H1 GBPCHF Z_PP_rej & dh4=1 & e200=-1 & macdh=-1 → br follow | 336 | -2.62 | -0.069 | -1.36 | -1.35 | -0.053 | -0.085 | 2/4 | other pairs 4/16 | FAIL: entry-hour top 02h +5R, 20h +3R, 21h +3R; max 16-18h share nan; ex-16-18h N 290 mean -0.034R | **limited** | same rule other 16 pairs pooled -0.046R t-3.3 |
| 3 | H1 EURGBP Z_ASL_rej & dh4=0 & e200=1 & macdt=-1 → h4 follow | 455 | -2.79 | -0.205 | -3.25 | -3.23 | -0.168 | -0.241 | 0/4 | other pairs 7/16 | FAIL: entry-hour top 05h +2R, 20h +2R, 23h +1R; max 16-18h share nan; ex-16-18h N 397 mean -0.222R | **limited** | same rule other 16 pairs pooled +0.013R t0.9 |
| 4 | H4 USDCHF Z_SWL_at & dh4=-1 & loc=PP & rsiz=1 → h24 follow | 157 | +10.50 | +0.241 | 0.53 | 0.53 | +0.265 | +0.216 | 3/4 | other pairs 7/16 | FAIL: entry-hour top 20h +87R, 04h +16R, 00h +10R; max 16-18h share 1.18; ex-16-18h N 99 mean +0.324R | **limited** | same rule other 16 pairs pooled -0.152R t-1.5 |
| 5 | H4 USDCHF Z_SWL_at & dh4=-1 & loc=PP → h24 follow | 175 | +6.04 | +0.079 | 0.19 | 0.19 | +0.104 | +0.054 | 1/4 | other pairs 5/16 | FAIL: entry-hour top 20h +44R, 04h +22R, 00h +19R; max 16-18h share 1.26; ex-16-18h N 108 mean +0.253R | **limited** | same rule other 16 pairs pooled -0.131R t-1.3 |
| 6 | H4 GBPJPY I_rsi_50_70 → h24 follow | 823 | -1.43 | +0.129 | 0.70 | 0.70 | +0.142 | +0.116 | 3/4 | other pairs 3/16 | ok: entry-hour top 08h +56R, 20h +45R, 16h +30R; max 16-18h share 0.32; ex-16-18h N 670 mean +0.107R | **limited** | same rule other 16 pairs pooled -0.074R t-1.6 |
| 7 | H1 GBPCHF Z_PDH_at & dh4=-1 & dd1=-1 & loc=PDH → br fade | 182 | -4.74 | -0.094 | -1.30 | -1.36 | -0.077 | -0.110 | 1/4 | other pairs 4/16 | FAIL: entry-hour top 07h +5R, 20h +3R, 15h +2R; max 16-18h share nan; ex-16-18h N 164 mean -0.087R | **limited** | same rule other 16 pairs pooled -0.057R t-2.9 |
| 8 | H1 GBPCHF Z_PDH_at & dh4=-1 & dd1=-1 & rsi50=1 → br fade | 177 | -5.05 | -0.096 | -1.32 | -1.36 | -0.079 | -0.112 | 1/4 | other pairs 5/16 | FAIL: entry-hour top 07h +5R, 20h +3R, 15h +2R; max 16-18h share nan; ex-16-18h N 159 mean -0.089R | **limited** | same rule other 16 pairs pooled -0.060R t-3.0 |
| 9 | H4 AUDUSD Z_S1_rej & dd1=0 & e200=-1 & rsi50=-1 → br fade | 266 | -0.43 | -0.003 | -0.03 | -0.03 | +0.023 | -0.029 | 2/4 | other pairs 7/16 | ok: entry-hour top 00h +19R, 16h +11R, 04h +4R; max 16-18h share nan; ex-16-18h N 203 mean +0.018R | **limited** | same rule other 16 pairs pooled -0.017R t-0.6 |
| 10 | H1 USDCAD Z_PDL_at & e200=1 → br follow | 572 | -1.06 | -0.033 | -0.78 | -0.78 | -0.010 | -0.055 | 1/4 | other pairs 6/16 | FAIL: entry-hour top 18h +18R, 05h +15R, 20h +10R; max 16-18h share nan; ex-16-18h N 473 mean -0.102R | **limited** | same rule other 16 pairs pooled -0.016R t-1.5 |
| 11 | H4 EURAUD Z_PDL_at & dd1=-1 & stz=-1 → h24 fade | 147 | +23.68 | +0.445 | 1.08 | 1.08 | +0.460 | +0.430 | 3/4 | other pairs 6/16 | ok: entry-hour top 00h +44R, 16h +7R, 12h +6R; max 16-18h share 0.24; ex-16-18h N 103 mean +0.531R | **limited** | same rule other 16 pairs pooled -0.023R t-0.2 |
| 12 | H1 USDCAD Z_PDL_rej & loc=PDL & stz=-1 → br follow | 606 | -0.62 | -0.031 | -0.85 | -0.85 | -0.008 | -0.054 | 1/4 | other pairs 4/16 | FAIL: entry-hour top 18h +9R, 02h +6R, 20h +4R; max 16-18h share nan; ex-16-18h N 506 mean -0.040R | **limited** | same rule other 16 pairs pooled -0.025R t-2.4 |
| 13 | H1 USDCAD Z_PDL_at & stz=-1 → br follow | 1135 | -0.42 | -0.016 | -0.58 | -0.59 | +0.007 | -0.039 | 2/4 | other pairs 7/16 | FAIL: entry-hour top 18h +24R, 20h +9R, 05h +6R; max 16-18h share nan; ex-16-18h N 914 mean -0.043R | **limited** | same rule other 16 pairs pooled -0.010R t-1.3 |
| 14 | H1 EURJPY Z_SWL_rej & dd1=-1 & e200=1 & rsi50=-1 → br fade | 319 | +2.76 | +0.034 | 0.64 | 0.66 | +0.052 | +0.016 | 3/4 | other pairs 10/16 | ok: entry-hour top 21h +5R, 03h +5R, 10h +4R; max 16-18h share 0.35; ex-16-18h N 270 mean +0.035R | **limited** | same rule other 16 pairs pooled +0.004R t0.3 |
| 15 | H4 USDCHF Z_SWL_at & loc=PP & macdt=1 → h24 follow | 214 | +9.03 | +0.255 | 0.67 | 0.67 | +0.280 | +0.231 | 2/4 | other pairs 8/16 | ok: entry-hour top 20h +50R, 04h +27R, 08h +13R; max 16-18h share 0.00; ex-16-18h N 150 mean +0.659R | **limited** | same rule other 16 pairs pooled +0.002R t0.0 |
| 16 | H1 AUDUSD Z_S1_rej & dh4=1 & dd1=0 & rsiz=1 → br fade | 221 | -2.24 | -0.101 | -1.61 | -1.64 | -0.075 | -0.127 | 0/4 | other pairs 4/16 | FAIL: entry-hour top 00h +4R, 11h +4R, 07h +3R; max 16-18h share nan; ex-16-18h N 204 mean -0.089R | **limited** | same rule other 16 pairs pooled -0.040R t-2.3 |
| 17 | H4 POOL Z_PWL_at & dh4=0 & loc=S1 & macdt=-1 → br follow | 515 | -4.33 | -0.104 | -1.26 | -1.25 | -0.080 | -0.129 | 1/4 | 5/16 | FAIL: entry-hour top 16h +47R, 08h -4R, 20h -12R; max 16-18h share nan; ex-16-18h N 393 mean -0.220R | **limited** | EURCHF +0.796R, NZDJPY +0.334R, AUDUSD +0.310R, EURGBP +0.145R |
| 18 | H1 GBPJPY Z_PP_rej & dh4=0 & loc=PP → h24 fade | 809 | +4.84 | +0.072 | 0.79 | 0.79 | +0.085 | +0.059 | 3/4 | other pairs 7/16 | ok: entry-hour top 14h +26R, 16h +17R, 00h +17R; max 16-18h share 0.29; ex-16-18h N 683 mean +0.042R | **limited** | same rule other 16 pairs pooled +0.027R t0.4 |
| 19 | H1 GBPCHF Z_SWL_rej & dd1=-1 & e200=-1 & macdt=-1 → h12 fade | 677 | -5.58 | -0.156 | -2.05 | -2.03 | -0.140 | -0.172 | 0/4 | other pairs 6/16 | FAIL: entry-hour top 18h +10R, 07h +7R, 12h +6R; max 16-18h share nan; ex-16-18h N 471 mean -0.247R | **limited** | same rule other 16 pairs pooled -0.102R t-1.5 |
| 20 | H4 NZDJPY Z_PP_at & dd1=1 & e200=1 & macdt=1 → br fade | 248 | +2.74 | +0.114 | 0.92 | 0.96 | +0.138 | +0.090 | 4/4 | other pairs 8/16 | ok: entry-hour top 00h +18R, 20h +17R, 16h +8R; max 16-18h share 0.27; ex-16-18h N 198 mean +0.091R | **limited** | same rule other 16 pairs pooled +0.001R t0.0 |

Window result: 0 CONFIRMED, 20 limited. Confirmation t of the 20 winners: median -0.31, >0: 9, >2: 0, >=3.4: 0.

## Window 7: 2015  (discovery 2026-11-04T03:43:23+00:00; 5065 candidate rows with >= 30 events and window t > 2.5 [v2] / any t [v1])

| # | candidate | family | events | window t | window mean net R |
|---|---|---|---|---|---|
| 1 | H4 NZDUSD Z_SWH_rej & loc=SWL → br follow | combination (zone trigger) | 34 | 5.10 | +1.466 |
| 2 | H4 AUDUSD Z_SWL_at & dh4=-1 & e200=-1 & stz=-1 → br follow | combination (zone trigger) | 35 | 4.56 | +1.039 |
| 3 | H1 NZDJPY Z_SWL_at & dh4=1 & dd1=0 & macdt=1 → br fade | combination (zone trigger) | 35 | 4.55 | +0.496 |
| 4 | H1 USDCAD Z_PDH_rej & dh4=0 & macdh=1 → br fade | combination (zone trigger) | 94 | 4.42 | +0.423 |
| 5 | H4 AUDUSD Z_SWL_at & dh4=-1 & macdt=-1 → br follow | combination (zone trigger) | 42 | 4.31 | +1.021 |
| 6 | H1 GBPCHF Z_S1_at & e200=1 & stz=0 → br fade | combination (zone trigger) | 30 | 4.31 | +0.557 |
| 7 | H1 AUDJPY Z_PDL_rej & dd1=1 & e200=1 & macdh=-1 → br follow | combination (zone trigger) | 32 | 4.31 | +0.619 |
| 8 | H4 AUDUSD Z_SWL_rej & dh4=-1 & loc=SWL & macdh=-1 → br follow | combination (zone trigger) | 30 | 4.31 | +1.182 |
| 9 | H1 USDJPY Z_PWL_at & dd1=0 & rsi50=-1 → br follow | combination (zone trigger) | 38 | 4.29 | +0.589 |
| 10 | H1 GBPJPY Z_PDH_rej & e200=-1 & macdt=1 → br follow | combination (zone trigger) | 33 | 4.21 | +0.855 |
| 11 | H1 EURAUD Z_ASH_at & dh4=1 & dd1=-1 & rsi50=1 → br fade | combination (zone trigger) | 37 | 4.19 | +0.534 |
| 12 | H4 EURUSD Z_PDL_at & dd1=1 → br fade | combination (zone trigger) | 37 | 4.18 | +1.242 |
| 13 | H4 POOL Z_PDH_at & dd1=1 & e200=-1 & loc=SWH → br follow | combination (zone trigger) | 66 | 4.16 | +0.902 |
| 14 | H1 EURGBP Z_SWH_at & dh4=1 & loc=PP & macdh=-1 → br follow | combination (zone trigger) | 33 | 4.12 | +0.626 |
| 15 | H1 AUDJPY C_inside & dh4=-1 & dd1=-1 & rsiz=1 → br fade | combination (candle trigger) | 50 | 4.12 | +0.423 |
| 16 | H1 EURJPY Z_PDL_brk & dh4=-1 & e200=-1 & stz=0 → br follow | combination (zone trigger) | 45 | 4.11 | +0.553 |
| 17 | H4 AUDUSD Z_SWL_at & dh4=-1 & e200=-1 & macdt=-1 → br follow | combination (zone trigger) | 41 | 4.11 | +0.996 |
| 18 | H1 AUDUSD Z_ASH_ret & dh4=0 & macdt=-1 → br follow | combination (zone trigger) | 37 | 4.11 | +0.692 |
| 19 | H4 EURUSD Z_PDL_at & dd1=1 & macdh=-1 → br fade | combination (zone trigger) | 32 | 4.10 | +1.342 |
| 20 | H1 GBPJPY Z_SWH_rej & dd1=-1 & rsi50=-1 → br follow | combination (zone trigger) | 75 | 4.10 | +0.461 |

Confirmation on the other 16 pool years (2026-11-04T03:43:25+00:00); running test count = 140

| # | candidate | N | mean pips | mean R | t trades | t daily | gross R | 2x-cost R | blocks + | pairs + | rollover-hour check | verdict | context |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H4 NZDUSD Z_SWH_rej & loc=SWL → br follow | 362 | -0.59 | -0.032 | -0.31 | -0.30 | -0.007 | -0.058 | 1/4 | other pairs 4/16 | FAIL: entry-hour top 20h +17R, 08h +15R, 00h +3R; max 16-18h share nan; ex-16-18h N 282 mean -0.067R | **limited** | same rule other 16 pairs pooled -0.039R t-1.6 |
| 2 | H4 AUDUSD Z_SWL_at & dh4=-1 & e200=-1 & stz=-1 → br follow | 180 | +2.28 | +0.029 | 0.20 | 0.20 | +0.058 | +0.001 | 1/4 | other pairs 5/16 | FAIL: entry-hour top 12h +25R, 08h +3R, 20h +2R; max 16-18h share 1.29; ex-16-18h N 140 mean +0.024R | **limited** | same rule other 16 pairs pooled -0.077R t-2.3 |
| 3 | H1 NZDJPY Z_SWL_at & dh4=1 & dd1=0 & macdt=1 → br fade | 356 | -2.18 | -0.084 | -1.61 | -1.58 | -0.062 | -0.106 | 0/4 | other pairs 4/16 | FAIL: entry-hour top 15h +8R, 02h +7R, 05h +7R; max 16-18h share nan; ex-16-18h N 311 mean -0.079R | **limited** | same rule other 16 pairs pooled -0.048R t-3.7 |
| 4 | H1 USDCAD Z_PDH_rej & dh4=0 & macdh=1 → br fade | 845 | -0.31 | -0.020 | -0.58 | -0.60 | +0.005 | -0.044 | 2/4 | other pairs 6/16 | FAIL: entry-hour top 19h +14R, 12h +9R, 15h +8R; max 16-18h share nan; ex-16-18h N 744 mean -0.018R | **limited** | same rule other 16 pairs pooled -0.014R t-1.5 |
| 5 | H4 AUDUSD Z_SWL_at & dh4=-1 & macdt=-1 → br follow | 367 | -1.65 | -0.094 | -0.92 | -0.92 | -0.066 | -0.122 | 1/4 | other pairs 3/16 | FAIL: entry-hour top 12h +12R, 16h +6R, 20h +3R; max 16-18h share nan; ex-16-18h N 295 mean -0.154R | **limited** | same rule other 16 pairs pooled -0.083R t-3.5 |
| 6 | H1 GBPCHF Z_S1_at & e200=1 & stz=0 → br fade | 324 | -2.68 | -0.044 | -0.76 | -0.76 | -0.026 | -0.061 | 2/4 | other pairs 3/16 | FAIL: entry-hour top 10h +8R, 09h +6R, 06h +5R; max 16-18h share nan; ex-16-18h N 290 mean -0.046R | **limited** | same rule other 16 pairs pooled -0.062R t-4.3 |
| 7 | H1 AUDJPY Z_PDL_rej & dd1=1 & e200=1 & macdh=-1 → br follow | 287 | -2.07 | -0.103 | -1.80 | -1.83 | -0.080 | -0.126 | 0/4 | other pairs 5/16 | FAIL: entry-hour top 04h +5R, 01h +3R, 22h +3R; max 16-18h share nan; ex-16-18h N 262 mean -0.084R | **limited** | same rule other 16 pairs pooled -0.046R t-2.9 |
| 8 | H4 AUDUSD Z_SWL_rej & dh4=-1 & loc=SWL & macdh=-1 → br follow | 318 | -2.24 | -0.050 | -0.46 | -0.46 | -0.023 | -0.078 | 1/4 | other pairs 6/16 | FAIL: entry-hour top 12h +19R, 04h -1R, 20h -5R; max 16-18h share nan; ex-16-18h N 248 mean -0.031R | **limited** | same rule other 16 pairs pooled -0.043R t-1.7 |
| 9 | H1 USDJPY Z_PWL_at & dd1=0 & rsi50=-1 → br follow | 251 | -0.41 | -0.034 | -0.52 | -0.53 | -0.009 | -0.059 | 2/4 | other pairs 3/16 | FAIL: entry-hour top 12h +8R, 09h +4R, 16h +4R; max 16-18h share nan; ex-16-18h N 216 mean -0.041R | **limited** | same rule other 16 pairs pooled -0.028R t-1.8 |
| 10 | H1 GBPJPY Z_PDH_rej & e200=-1 & macdt=1 → br follow | 398 | +1.22 | -0.008 | -0.16 | -0.16 | +0.005 | -0.021 | 2/4 | other pairs 4/16 | FAIL: entry-hour top 14h +6R, 04h +5R, 03h +5R; max 16-18h share nan; ex-16-18h N 360 mean -0.019R | **limited** | same rule other 16 pairs pooled -0.045R t-3.6 |
| 11 | H1 EURAUD Z_ASH_at & dh4=1 & dd1=-1 & rsi50=1 → br fade | 315 | +1.05 | +0.009 | 0.14 | 0.14 | +0.026 | -0.008 | 3/4 | other pairs 4/16 | ok: entry-hour top 04h +8R, 13h +7R, 07h +6R; max 16-18h share 0.12; ex-16-18h N 278 mean +0.032R | **limited** | same rule other 16 pairs pooled -0.031R t-2.4 |
| 12 | H4 EURUSD Z_PDL_at & dd1=1 → br fade | 415 | -3.59 | -0.107 | -1.20 | -1.23 | -0.085 | -0.128 | 1/4 | other pairs 7/16 | FAIL: entry-hour top 00h +12R, 08h +11R, 16h -9R; max 16-18h share nan; ex-16-18h N 335 mean -0.076R | **limited** | same rule other 16 pairs pooled -0.014R t-0.6 |
| 13 | H4 POOL Z_PDH_at & dd1=1 & e200=-1 & loc=SWH → br follow | 430 | -1.05 | -0.032 | -0.35 | -0.34 | -0.006 | -0.057 | 1/4 | 6/15 | FAIL: entry-hour top 20h +20R, 12h +18R, 04h +3R; max 16-18h share nan; ex-16-18h N 338 mean -0.073R | **limited** | EURJPY +0.762R, GBPJPY +0.564R, USDCHF +0.385R, AUDJPY +0.354R |
| 14 | H1 EURGBP Z_SWH_at & dh4=1 & loc=PP & macdh=-1 → br follow | 340 | +0.41 | +0.012 | 0.24 | 0.23 | +0.051 | -0.026 | 2/4 | other pairs 3/16 | FAIL: entry-hour top 18h +7R, 13h +4R, 07h +4R; max 16-18h share 1.54; ex-16-18h N 277 mean -0.014R | **limited** | same rule other 16 pairs pooled -0.042R t-3.2 |
| 15 | H1 AUDJPY C_inside & dh4=-1 & dd1=-1 & rsiz=1 → br fade | 362 | -1.77 | -0.062 | -1.00 | -1.07 | -0.041 | -0.083 | 2/4 | other pairs 4/16 | FAIL: entry-hour top 22h +4R, 06h +3R, 11h +3R; max 16-18h share nan; ex-16-18h N 309 mean -0.062R | **limited** | same rule other 16 pairs pooled -0.037R t-3.0 |
| 16 | H1 EURJPY Z_PDL_brk & dh4=-1 & e200=-1 & stz=0 → br follow | 492 | -0.90 | -0.019 | -0.39 | -0.39 | -0.001 | -0.038 | 1/4 | other pairs 2/16 | FAIL: entry-hour top 04h +19R, 07h +7R, 09h +6R; max 16-18h share nan; ex-16-18h N 435 mean -0.007R | **limited** | same rule other 16 pairs pooled -0.047R t-4.0 |
| 17 | H4 AUDUSD Z_SWL_at & dh4=-1 & e200=-1 & macdt=-1 → br follow | 237 | -2.34 | -0.124 | -0.99 | -0.98 | -0.095 | -0.152 | 1/4 | other pairs 4/16 | FAIL: entry-hour top 12h +12R, 20h +9R, 04h -0R; max 16-18h share nan; ex-16-18h N 188 mean -0.158R | **limited** | same rule other 16 pairs pooled -0.067R t-2.3 |
| 18 | H1 AUDUSD Z_ASH_ret & dh4=0 & macdt=-1 → br follow | 568 | -1.61 | -0.044 | -1.09 | -1.08 | -0.019 | -0.070 | 2/4 | other pairs 2/16 | FAIL: entry-hour top 10h +6R, 02h +2R, 01h +2R; max 16-18h share nan; ex-16-18h N 506 mean -0.026R | **limited** | same rule other 16 pairs pooled -0.052R t-4.6 |
| 19 | H4 EURUSD Z_PDL_at & dd1=1 & macdh=-1 → br fade | 368 | -4.86 | -0.140 | -1.49 | -1.54 | -0.118 | -0.161 | 0/4 | other pairs 7/16 | FAIL: entry-hour top 08h +9R, 00h +8R, 04h -9R; max 16-18h share nan; ex-16-18h N 296 mean -0.113R | **limited** | same rule other 16 pairs pooled -0.009R t-0.4 |
| 20 | H1 GBPJPY Z_SWH_rej & dd1=-1 & rsi50=-1 → br follow | 742 | -0.43 | -0.028 | -0.78 | -0.78 | -0.014 | -0.041 | 1/4 | other pairs 2/16 | FAIL: entry-hour top 21h +7R, 04h +6R, 18h +5R; max 16-18h share nan; ex-16-18h N 656 mean -0.026R | **limited** | same rule other 16 pairs pooled -0.046R t-5.1 |

Window result: 0 CONFIRMED, 20 limited. Confirmation t of the 20 winners: median -0.68, >0: 3, >2: 0, >=3.4: 0.

## Window 8: 2009  (discovery 2026-11-04T03:44:26+00:00; 18712 candidate rows with >= 30 events and window t > 2.5 [v2] / any t [v1])

| # | candidate | family | events | window t | window mean net R |
|---|---|---|---|---|---|
| 1 | H1 AUDNZD Z_SWH_at & dh4=-1 & dd1=1 & rsiz=1 → br follow | combination (zone trigger) | 59 | 5.52 | +0.547 |
| 2 | H4 POOL Z_PDL_rej & dh4=-1 & dd1=-1 & macdh=1 → h12 follow | combination (zone trigger) | 35 | 5.48 | +3.019 |
| 3 | H4 GBPUSD I_adx_gt25 → h24 fade | indicator | 633 | 5.28 | +1.849 |
| 4 | H4 EURAUD Z_SWH_at & dh4=1 & e200=1 & macdt=1 → br follow | combination (zone trigger) | 32 | 5.23 | +1.220 |
| 5 | H1 AUDNZD Z_SWL_rej & dd1=1 & e200=-1 & loc=SWH → h24 fade | combination (zone trigger) | 49 | 5.16 | +1.436 |
| 6 | H4 EURCHF I_cloud → h24 fade | indicator | 1286 | 5.12 | +1.431 |
| 7 | H4 AUDNZD Z_SWL_at & dd1=0 & macdt=1 → h4 follow | combination (zone trigger) | 97 | 5.07 | +0.699 |
| 8 | H1 EURCHF Z_ASL_rej & dd1=0 & loc=SWH → h12 fade | combination (zone trigger) | 67 | 5.06 | +0.859 |
| 9 | H1 NZDUSD Z_SWL_rej & loc=PP & rsi50=-1 → h24 follow | combination (zone trigger) | 45 | 5.06 | +1.561 |
| 10 | H4 AUDNZD Z_SWL_at & dd1=0 & e200=-1 & macdt=1 → h4 follow | combination (zone trigger) | 73 | 5.04 | +0.833 |
| 11 | H4 AUDJPY Z_PP_at & e200=1 & loc=SWH → br follow | combination (zone trigger) | 35 | 5.01 | +1.283 |
| 12 | H1 EURCHF Z_ASL_rej & dd1=0 & loc=SWH & stz=0 → h12 fade | combination (zone trigger) | 60 | 4.96 | +0.874 |
| 13 | H4 EURAUD I_rsi_50_70 → h12 fade | indicator | 607 | 4.93 | +1.033 |
| 14 | H4 USDCHF Z_PP_at & dd1=0 & e200=-1 & stz=0 → h4 fade | combination (zone trigger) | 90 | 4.83 | +0.752 |
| 15 | H1 USDCAD C_pin & dh4=0 & loc=none → h12 fade | combination (candle trigger) | 135 | 4.81 | +0.563 |
| 16 | H4 GBPUSD I_adx_gt25 → h12 fade | indicator | 633 | 4.78 | +1.174 |
| 17 | H1 AUDNZD Z_SWH_at & dh4=-1 & dd1=1 & loc=SWH → br follow | combination (zone trigger) | 160 | 4.77 | +0.443 |
| 18 | H1 USDCAD Z_SWL_at & dd1=0 & loc=ASL & rsiz=1 → h24 fade | combination (zone trigger) | 84 | 4.74 | +0.902 |
| 19 | H1 CADJPY C_engulf & dh4=0 & dd1=0 & macdt=1 → h24 follow | combination (candle trigger) | 48 | 4.71 | +1.812 |
| 20 | H1 EURGBP Z_PP_at & dd1=0 & e200=-1 & loc=PP → h4 fade | combination (zone trigger) | 146 | 4.68 | +0.266 |

Confirmation on the other 16 pool years (2026-11-04T03:44:30+00:00); running test count = 160

| # | candidate | N | mean pips | mean R | t trades | t daily | gross R | 2x-cost R | blocks + | pairs + | rollover-hour check | verdict | context |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H1 AUDNZD Z_SWH_at & dh4=-1 & dd1=1 & rsiz=1 → br follow | 121 | -0.28 | -0.021 | -0.19 | -0.19 | +0.005 | -0.047 | 1/4 | other pairs 6/16 | FAIL: entry-hour top 16h +6R, 14h +6R, 07h +5R; max 16-18h share nan; ex-16-18h N 88 mean -0.024R | **limited** | same rule other 16 pairs pooled -0.020R t-1.0 |
| 2 | H4 POOL Z_PDL_rej & dh4=-1 & dd1=-1 & macdh=1 → h12 follow | 495 | -3.00 | -0.091 | -0.57 | -0.56 | -0.065 | -0.118 | 2/4 | 8/15 | FAIL: entry-hour top 20h +28R, 00h +14R, 12h +5R; max 16-18h share nan; ex-16-18h N 378 mean -0.018R | **limited** | EURUSD +0.978R, EURAUD +0.830R, EURJPY +0.732R, GBPUSD +0.644R |
| 3 | H4 GBPUSD I_adx_gt25 → h24 fade | 722 | -0.77 | -0.112 | -0.56 | -0.56 | -0.094 | -0.129 | 1/4 | other pairs 6/16 | FAIL: entry-hour top 00h +34R, 20h +8R, 08h -5R; max 16-18h share nan; ex-16-18h N 513 mean -0.132R | **limited** | same rule other 16 pairs pooled -0.103R t-1.9 |
| 4 | H4 EURAUD Z_SWH_at & dh4=1 & e200=1 & macdt=1 → br follow | 299 | -7.69 | -0.156 | -1.40 | -1.37 | -0.140 | -0.172 | 1/4 | other pairs 4/16 | FAIL: entry-hour top 20h +6R, 04h +5R, 08h -0R; max 16-18h share nan; ex-16-18h N 225 mean -0.032R | **limited** | same rule other 16 pairs pooled -0.076R t-2.7 |
| 5 | H1 AUDNZD Z_SWL_rej & dd1=1 & e200=-1 & loc=SWH → h24 fade | 91 | -5.61 | -0.038 | -0.13 | -0.13 | -0.010 | -0.066 | 2/4 | other pairs 11/16 | FAIL: entry-hour top 16h +8R, 19h +8R, 00h +7R; max 16-18h share nan; ex-16-18h N 78 mean -0.222R | **limited** | same rule other 16 pairs pooled +0.099R t1.6 |
| 6 | H4 EURCHF I_cloud → h24 fade | 1043 | -1.21 | -0.527 | -0.90 | -0.90 | -0.481 | -0.573 | 2/4 | other pairs 6/16 | FAIL: entry-hour top 08h +115R, 16h +18R, 12h +14R; max 16-18h share nan; ex-16-18h N 740 mean -0.798R | **limited** | same rule other 16 pairs pooled -0.007R t-0.2 |
| 7 | H4 AUDNZD Z_SWL_at & dd1=0 & macdt=1 → h4 follow | 411 | +3.75 | +0.199 | 1.92 | 1.88 | +0.228 | +0.171 | 3/4 | other pairs 9/16 | FAIL: entry-hour top 00h +52R, 16h +17R, 04h +16R; max 16-18h share 0.64; ex-16-18h N 274 mean +0.046R | **limited** | same rule other 16 pairs pooled +0.007R t0.3 |
| 8 | H1 EURCHF Z_ASL_rej & dd1=0 & loc=SWH → h12 fade | 450 | +1.58 | +0.084 | 0.98 | 0.98 | +0.148 | +0.020 | 4/4 | other pairs 11/16 | ok: entry-hour top 05h +11R, 20h +10R, 10h +8R; max 16-18h share 0.26; ex-16-18h N 298 mean +0.100R | **limited** | same rule other 16 pairs pooled +0.010R t0.4 |
| 9 | H1 NZDUSD Z_SWL_rej & loc=PP & rsi50=-1 → h24 follow | 494 | -0.75 | +0.015 | 0.13 | 0.13 | +0.043 | -0.012 | 2/4 | other pairs 7/16 | FAIL: entry-hour top 18h +32R, 19h +19R, 01h +14R; max 16-18h share 4.19; ex-16-18h N 431 mean -0.072R | **limited** | same rule other 16 pairs pooled +0.057R t0.7 |
| 10 | H4 AUDNZD Z_SWL_at & dd1=0 & e200=-1 & macdt=1 → h4 follow | 276 | +2.69 | +0.152 | 1.28 | 1.26 | +0.181 | +0.123 | 3/4 | other pairs 10/16 | FAIL: entry-hour top 00h +35R, 20h +19R, 04h +8R; max 16-18h share 0.87; ex-16-18h N 173 mean +0.019R | **limited** | same rule other 16 pairs pooled +0.003R t0.1 |
| 11 | H4 AUDJPY Z_PP_at & e200=1 & loc=SWH → br follow | 314 | +2.01 | +0.044 | 0.41 | 0.41 | +0.069 | +0.020 | 2/4 | other pairs 8/16 | FAIL: entry-hour top 20h +15R, 12h +3R, 00h +3R; max 16-18h share 0.75; ex-16-18h N 260 mean +0.009R | **limited** | same rule other 16 pairs pooled -0.030R t-1.1 |
| 12 | H1 EURCHF Z_ASL_rej & dd1=0 & loc=SWH & stz=0 → h12 fade | 410 | +2.62 | +0.172 | 2.04 | 2.04 | +0.236 | +0.108 | 4/4 | other pairs 9/16 | ok: entry-hour top 20h +13R, 05h +9R, 09h +7R; max 16-18h share 0.23; ex-16-18h N 270 mean +0.211R | **limited** | same rule other 16 pairs pooled +0.022R t0.7 |
| 13 | H4 EURAUD I_rsi_50_70 → h12 fade | 1379 | -1.15 | -0.092 | -0.87 | -0.87 | -0.076 | -0.108 | 1/4 | other pairs 6/16 | FAIL: entry-hour top 20h +70R, 04h +6R, 00h +3R; max 16-18h share nan; ex-16-18h N 1183 mean -0.108R | **limited** | same rule other 16 pairs pooled -0.030R t-1.2 |
| 14 | H4 USDCHF Z_PP_at & dd1=0 & e200=-1 & stz=0 → h4 fade | 379 | +1.32 | +0.033 | 0.27 | 0.27 | +0.058 | +0.007 | 2/4 | other pairs 7/16 | FAIL: entry-hour top 16h +22R, 00h +6R, 12h +6R; max 16-18h share 1.80; ex-16-18h N 268 mean -0.006R | **limited** | same rule other 16 pairs pooled -0.004R t-0.2 |
| 15 | H1 USDCAD C_pin & dh4=0 & loc=none → h12 fade | 1251 | +0.87 | +0.031 | 0.62 | 0.61 | +0.055 | +0.007 | 2/4 | other pairs 8/16 | FAIL: entry-hour top 21h +29R, 05h +28R, 08h +21R; max 16-18h share 0.69; ex-16-18h N 945 mean +0.024R | **limited** | same rule other 16 pairs pooled -0.003R t-0.2 |
| 16 | H4 GBPUSD I_adx_gt25 → h12 fade | 1255 | -2.30 | -0.086 | -0.81 | -0.81 | -0.069 | -0.103 | 1/4 | other pairs 5/16 | FAIL: entry-hour top 00h +36R, 08h +28R, 20h +24R; max 16-18h share nan; ex-16-18h N 947 mean -0.010R | **limited** | same rule other 16 pairs pooled -0.071R t-2.5 |
| 17 | H1 AUDNZD Z_SWH_at & dh4=-1 & dd1=1 & loc=SWH → br follow | 428 | +2.60 | +0.073 | 1.33 | 1.36 | +0.100 | +0.047 | 3/4 | other pairs 4/16 | ok: entry-hour top 11h +12R, 07h +10R, 16h +10R; max 16-18h share 0.31; ex-16-18h N 357 mean +0.062R | **limited** | same rule other 16 pairs pooled -0.042R t-4.0 |
| 18 | H1 USDCAD Z_SWL_at & dd1=0 & loc=ASL & rsiz=1 → h24 fade | 409 | -1.57 | -0.010 | -0.08 | -0.08 | +0.014 | -0.034 | 1/4 | other pairs 8/16 | ok: entry-hour top 08h +35R, 22h +11R, 12h +11R; max 16-18h share nan; ex-16-18h N 374 mean +0.023R | **limited** | same rule other 16 pairs pooled -0.011R t-0.3 |
| 19 | H1 CADJPY C_engulf & dh4=0 & dd1=0 & macdt=1 → h24 follow | 417 | +2.18 | +0.089 | 0.70 | 0.70 | +0.112 | +0.066 | 2/4 | other pairs 5/16 | ok: entry-hour top 04h +19R, 21h +18R, 08h +13R; max 16-18h share 0.18; ex-16-18h N 364 mean +0.102R | **limited** | same rule other 16 pairs pooled -0.024R t-0.8 |
| 20 | H1 EURGBP Z_PP_at & dd1=0 & e200=-1 & loc=PP → h4 fade | 1006 | -0.71 | -0.056 | -1.79 | -1.81 | -0.018 | -0.095 | 0/4 | other pairs 3/16 | FAIL: entry-hour top 23h +11R, 00h +10R, 01h +6R; max 16-18h share nan; ex-16-18h N 795 mean -0.036R | **limited** | same rule other 16 pairs pooled -0.044R t-5.0 |

Window result: 0 CONFIRMED, 20 limited. Confirmation t of the 20 winners: median 0.02, >0: 10, >2: 1, >=3.4: 0.

## Round 8 loop finished 2026-11-04T03:44:30+00:00: windows tried 8, candidate tests 160, accepted methods []

# Diagnostics (r8_diag.py)

## Confirmation t of the 20 discovery winners per window (t used = min(trade t, daily t))

| round | window | k | n | median | gt0 | gt2 | ge34 | ge35 | confirmed |
|---|---|---|---|---|---|---|---|---|---|
| 8 | 2017 | 1 | 20 | -0.55 | 8 | 0 | 0 | 0 | 0 |
| 8 | 2021 | 2 | 20 | -0.43 | 8 | 2 | 1 | 1 | 0 |
| 8 | 2018 | 3 | 20 | -0.21 | 10 | 0 | 0 | 0 | 0 |
| 8 | 2007 | 4 | 20 | -1.06 | 8 | 0 | 0 | 0 | 0 |
| 8 | 2008 | 5 | 20 | -0.24 | 9 | 0 | 0 | 0 | 0 |
| 8 | 2012 | 6 | 20 | -0.31 | 9 | 0 | 0 | 0 | 0 |
| 8 | 2015 | 7 | 20 | -0.68 | 3 | 0 | 0 | 0 | 0 |
| 8 | 2009 | 8 | 20 | 0.02 | 10 | 1 | 0 | 0 | 0 |
| 7 | 2012-03 | 1 | 20 | -0.83 | 7 | 0 | 0 | 0 | 0 |
| 7 | 2021-07 | 2 | 20 | -0.81 | 7 | 1 | 1 | 1 | 0 |
| 7 | 2017-07 | 3 | 20 | -0.46 | 4 | 0 | 0 | 0 | 0 |
| 7 | 2013-11 | 4 | 20 | -0.65 | 6 | 0 | 0 | 0 | 0 |
| 7 | 2015-08 | 5 | 20 | -0.88 | 1 | 0 | 0 | 0 | 0 |
| 7 | 2019-03 | 6 | 20 | 0.03 | 10 | 0 | 0 | 0 | 0 |
| 7 | 2006-06 | 7 | 20 | -0.32 | 4 | 0 | 0 | 0 | 0 |
| 7 | 2012-02 | 8 | 20 | -0.67 | 5 | 0 | 0 | 0 | 0 |
| 7 | 2006-08 | 9 | 20 | -1.12 | 3 | 0 | 0 | 0 | 0 |
| 7 | 2016-08 | 10 | 20 | -0.75 | 7 | 1 | 0 | 0 | 0 |
| 7 | 2021-08 | 11 | 20 | -0.07 | 10 | 1 | 1 | 1 | 0 |
| 7 | 2008-05 | 12 | 20 | -0.70 | 4 | 0 | 0 | 0 | 0 |

## Aggregate: round 8 (12-month windows) vs round 7 (1-month windows, library v2)

| round | n | median | gt0 | gt2 | ge34 | ge35 | pos_mean_share |
|---|---|---|---|---|---|---|---|
| round 7 (1-month, v2, 12 months, 240 tests) | 240.00 | -0.67 | 68.00 | 3.00 | 2.00 | 2.00 | 0.28 |
| round 8 (12-month, 8 windows max) | 160.00 | -0.46 | 65.00 | 3.00 | 1.00 | 1.00 | 0.41 |

## Family breakdown (round 8 n/confirmed/positive/t>2; round 7 v2 columns with suffix 7)

| family | n | confirmed | pos | t_gt2 | median_t | best_t | n7 | pos7 | t_gt2_7 | median_t7 |
|---|---|---|---|---|---|---|---|---|---|---|
| combination | 136.00 | 0.00 | 56.00 | 1.00 | -0.37 | 2.04 | 188 | 49 | 1 | -0.77 |
| indicator | 18.00 | 0.00 | 5.00 | 0.00 | -0.82 | 1.06 | 48 | 17 | 0 | -0.40 |
| time | 6.00 | 0.00 | 4.00 | 2.00 | 0.81 | 4.70 | 2 | 2 | 2 | 7.69 |
| zone | 0.00 | nan | nan | nan | nan | nan | 2 | 0 | 0 | -1.00 |

## Failed criteria count (round 8, a candidate can fail several)

{'t': 159, 'blocks': 126, 'not_rollover': 119, 'cost2x': 115, 'mean_pos': 104, 'pairs60': 10}

# Round 8 verdict (2026-11-04T03:46:29+00:00)
- 8 calendar-year windows (2017, 2021, 2018, 2007, 2008, 2012, 2015, 2009), 160 confirmation tests, **0 CONFIRMED, 0 promoted, 0 holdout looks in round 8** (r8_holdout_timeline.log not created; 2022-2024 remains as after round 7: looked at twice, only for the two rejected v1 rollover rules).
- Only candidate with confirmation t >= 3.4: GBPCHF long 18:00-19:00 EST (F1_h18, discovered in 2021; also the top v2 survivor in round 7): t 4.70, +0.47 pips, but positive in only 2/4 blocks and 100% of its P&L sits in the rollover-adjacent 18h -> limited (rollover-hour rule and blocks).
- Hit rate vs round 7 (1-month windows): positive in confirmation 65/160 = 41% (r7 68/240 = 28%); median confirmation t -0.46 (r7 -0.67); t > 2: 3/160 (r7 3/240); t >= 3.4: 1 (r7 2, both GBPCHF 18h). Spearman(window t, confirmation t) = 0.05 (p 0.49) (r7 0.16).
- Implementation note: H4 tables keep r7's convention (no rollover mask for H4; the 16:00-20:00 H4 bar's high/low are used for bracket checks and the exit is stamped at the bar close 20:00, so the hour check does not see those exits). Not material here because nothing was confirmed; it would need checking for any confirmed H4 bracket rule.
- Comparison = method 1 only (r8_compare.json / r8_compare.png). No EA written.
