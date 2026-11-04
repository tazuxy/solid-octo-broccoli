# Round 7 loop log

Created 2026-11-04T02:35:07+00:00. Pool 2005-01..2021-12 (204 months); holdout 2022-01..2024-12 locked in code.
Month draw: numpy default_rng(42).choice(204 pool months, 12, replace=False) = [201203, 202107, 201707, 201311, 201508, 201903, 200606, 201202, 200608, 201608, 202108, 200805]
Confirmation: net mean>0 (0.5 pip; XAU 0.30 USD), t(netR)>=3.2, >=3/4 blocks positive, 2x cost mean>0.

## Month 1: 2012-03  (discovery 2026-11-04T02:35:56+00:00; 2708 instrument x bucket x direction candidates with >=8 events)

| # | inst | feature | dir | units | trades | in-month t | mean net pips/trade | mean net R/trade |
|---|---|---|---|---|---|---|---|---|
| 1 | USDJPY | F2_Wed_04 | L/follow | 16 | 4 | 3.94 | +25.6 | +1.381 |
| 2 | EURGBP | F2_Fri_00 | S/fade | 20 | 5 | 3.88 | +12.5 | +0.959 |
| 3 | NZDJPY | F1_h16 | L/follow | 22 | 22 | 3.62 | +3.6 | +0.154 |
| 4 | EURUSD | F1_h12 | L/follow | 22 | 22 | 3.61 | +5.1 | +0.172 |
| 5 | EURJPY | F2_Mon_08 | L/follow | 16 | 4 | 3.40 | +47.4 | +1.553 |
| 6 | EURAUD | F2_Mon_08 | L/follow | 16 | 4 | 3.36 | +45.1 | +1.678 |
| 7 | GBPJPY | F1_h14 | L/follow | 22 | 22 | 3.34 | +8.0 | +0.224 |
| 8 | AUDNZD | F1_h21 | S/fade | 21 | 21 | 3.16 | +6.8 | +0.364 |
| 9 | CADJPY | F3_d28-31_Asia | S/fade | 21 | 3 | 3.09 | +36.9 | +1.437 |
| 10 | AUDNZD | F1_h07 | S/fade | 22 | 22 | 3.04 | +3.9 | +0.214 |

Confirmation on the other 203 pool months (2026-11-04T02:35:58+00:00); running test count = 10

| # | inst | feature | dir | N | mean pips | mean R | t(R) | gross R | 2x-cost R | blocks + | verdict | other inst + | neighbours t>=2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | USDJPY | F2_Wed_04 | L/follow | 877 | +1.42 | +0.067 | 2.02 | +0.092 | +0.041 | 3/4 | **limited** | 7/17 | AUDJPY +0.075R t2.3, USDCHF +0.077R t2.0 |
| 2 | EURGBP | F2_Fri_00 | S/fade | 872 | -1.31 | -0.124 | -3.60 | -0.087 | -0.162 | 1/4 | **limited** | 8/17 |  |
| 3 | NZDJPY | F1_h16 | L/follow | 3927 | -1.27 | -0.070 | -8.97 | -0.048 | -0.093 | 2/4 | **limited** | 0/17 | h15 -0.017R t-2.0, h17 -0.005R t-0.5 |
| 4 | EURUSD | F1_h12 | L/follow | 4373 | +0.05 | -0.000 | -0.04 | +0.022 | -0.022 | 3/4 | **limited** | 1/17 | h11 -0.001R t-0.1, h13 -0.004R t-0.6 |
| 5 | EURJPY | F2_Mon_08 | L/follow | 871 | -1.84 | -0.030 | -0.74 | -0.012 | -0.048 | 1/4 | **limited** | 6/17 |  |
| 6 | EURAUD | F2_Mon_08 | L/follow | 869 | -0.09 | +0.010 | 0.25 | +0.026 | -0.005 | 2/4 | **limited** | 5/17 |  |
| 7 | GBPJPY | F1_h14 | L/follow | 4365 | +0.55 | +0.004 | 0.57 | +0.017 | -0.009 | 3/4 | **limited** | 2/17 | h13 -0.006R t-0.9, h15 +0.006R t0.9 |
| 8 | AUDNZD | F1_h21 | S/fade | 3645 | -0.65 | -0.036 | -3.02 | -0.009 | -0.062 | 0/4 | **limited** | 2/17 | h20 -0.032R t-2.9, h22 -0.037R t-3.8 |
| 9 | CADJPY | F3_d28-31_Asia | S/fade | 432 | +2.32 | +0.127 | 2.07 | +0.149 | +0.104 | 4/4 | **limited** | 7/17 | EURAUD +0.157R t3.0, USDJPY +0.214R t2.7, EURJPY +0.135R t2.2 |
| 10 | AUDNZD | F1_h07 | S/fade | 3645 | -0.31 | -0.022 | -2.80 | +0.005 | -0.049 | 1/4 | **limited** | 2/17 | h06 -0.037R t-5.0, h08 -0.021R t-2.4 |

Month result: 0 CONFIRMED, 10 limited.

## Month 2: 2021-07  (discovery 2026-11-04T02:35:58+00:00; 2876 instrument x bucket x direction candidates with >=8 events)

| # | inst | feature | dir | units | trades | in-month t | mean net pips/trade | mean net R/trade |
|---|---|---|---|---|---|---|---|---|
| 1 | EURCHF | F1_h16 | S/fade | 22 | 22 | 5.58 | +2.8 | +0.335 |
| 2 | GBPCHF | F1_h18 | L/follow | 21 | 21 | 5.50 | +5.1 | +0.261 |
| 3 | EURAUD | F1_h16 | S/fade | 22 | 22 | 4.86 | +6.5 | +0.282 |
| 4 | AUDNZD | F1_h16 | S/fade | 22 | 22 | 4.59 | +3.6 | +0.341 |
| 5 | CADJPY | F1_h17 | L/follow | 21 | 21 | 4.39 | +3.3 | +0.172 |
| 6 | EURGBP | F1_h16 | S/fade | 22 | 22 | 4.26 | +2.7 | +0.244 |
| 7 | EURAUD | F1_h17 | L/follow | 21 | 21 | 3.63 | +3.4 | +0.140 |
| 8 | AUDJPY | F1_h17 | L/follow | 21 | 21 | 3.53 | +3.7 | +0.211 |
| 9 | EURJPY | F1_h17 | L/follow | 21 | 21 | 3.47 | +2.2 | +0.120 |
| 10 | GBPCHF | F1_h16 | S/fade | 22 | 22 | 3.42 | +3.4 | +0.173 |

Confirmation on the other 203 pool months (2026-11-04T02:36:01+00:00); running test count = 20

| # | inst | feature | dir | N | mean pips | mean R | t(R) | gross R | 2x-cost R | blocks + | verdict | other inst + | neighbours t>=2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | EURCHF | F1_h16 | S/fade | 4374 | +0.74 | +0.069 | 2.32 | +0.115 | +0.024 | 2/4 | **limited** | 11/17 | AUDNZD +0.128R t12.3, GBPCHF +0.072R t10.7, USDCHF +0.050R t8.3, EURAUD +0.045R t8.2, EURGBP +0.027R t5.2, USDCAD +0.026R t4.0, h15 -0.045R t-6.6, h17 -0.072R t-11.6 |
| 2 | GBPCHF | F1_h18 | L/follow | 4350 | +0.79 | +0.039 | 7.75 | +0.055 | +0.022 | 2/4 | **limited** | 10/17 | GBPJPY +0.025R t4.0, CADJPY +0.022R t3.4, EURCHF +0.017R t3.1, AUDNZD +0.030R t2.9, EURJPY +0.018R t2.8, NZDJPY +0.023R t2.6, h17 +0.003R t0.5, h19 -0.016R t-2.9 |
| 3 | EURAUD | F1_h16 | S/fade | 4356 | +1.30 | +0.045 | 8.16 | +0.060 | +0.029 | 2/4 | **limited** | 11/17 | AUDNZD +0.128R t12.3, GBPCHF +0.072R t10.7, USDCHF +0.050R t8.3, EURGBP +0.027R t5.2, USDCAD +0.026R t4.0, NZDUSD +0.027R t3.5, h15 -0.023R t-3.3, h17 -0.118R t-18.7 |
| 4 | AUDNZD | F1_h16 | S/fade | 3638 | +2.14 | +0.128 | 12.31 | +0.155 | +0.102 | 3/4 | **CONFIRMED** | 11/17 | GBPCHF +0.072R t10.7, USDCHF +0.050R t8.3, EURAUD +0.045R t8.2, EURGBP +0.027R t5.2, USDCAD +0.026R t4.0, NZDUSD +0.027R t3.5, h15 -0.007R t-0.8, h17 -0.157R t-14.7 |
| 5 | CADJPY | F1_h17 | L/follow | 3814 | -0.19 | -0.003 | -0.47 | +0.019 | -0.025 | 2/4 | **limited** | 9/17 | EURAUD +0.087R t13.7, AUDNZD +0.104R t9.8, USDCAD +0.023R t4.9, EURGBP +0.018R t3.1, h16 -0.047R t-7.5, h18 +0.022R t3.4 |
| 6 | EURGBP | F1_h16 | S/fade | 4372 | +0.48 | +0.027 | 5.22 | +0.065 | -0.010 | 2/4 | **limited** | 11/17 | AUDNZD +0.128R t12.3, GBPCHF +0.072R t10.7, USDCHF +0.050R t8.3, EURAUD +0.045R t8.2, USDCAD +0.026R t4.0, NZDUSD +0.027R t3.5, h15 -0.025R t-4.9, h17 -0.093R t-15.6 |
| 7 | EURAUD | F1_h17 | L/follow | 4375 | +2.76 | +0.087 | 13.74 | +0.102 | +0.071 | 4/4 | **CONFIRMED** | 8/17 | AUDNZD +0.104R t9.8, USDCAD +0.023R t4.9, EURGBP +0.018R t3.1, h16 -0.076R t-13.9, h18 -0.009R t-1.4 |
| 8 | AUDJPY | F1_h17 | L/follow | 4100 | -1.01 | -0.037 | -4.87 | -0.015 | -0.059 | 1/4 | **limited** | 9/17 | EURAUD +0.087R t13.7, AUDNZD +0.104R t9.8, USDCAD +0.023R t4.9, EURGBP +0.018R t3.1, h16 -0.035R t-6.3, h18 +0.019R t2.5 |
| 9 | EURJPY | F1_h17 | L/follow | 4397 | -0.00 | +0.009 | 1.42 | +0.028 | -0.009 | 2/4 | **limited** | 8/17 | EURAUD +0.087R t13.7, AUDNZD +0.104R t9.8, USDCAD +0.023R t4.9, EURGBP +0.018R t3.1, h16 -0.014R t-2.7, h18 +0.018R t2.8 |
| 10 | GBPCHF | F1_h16 | S/fade | 4356 | +1.91 | +0.072 | 10.67 | +0.088 | +0.055 | 3/4 | **CONFIRMED** | 11/17 | AUDNZD +0.128R t12.3, USDCHF +0.050R t8.3, EURAUD +0.045R t8.2, EURGBP +0.027R t5.2, USDCAD +0.026R t4.0, NZDUSD +0.027R t3.5, h15 -0.025R t-4.7, h17 -0.036R t-5.9 |

Month result: 3 CONFIRMED, 7 limited.
- [2026-11-04T02:36:01+00:00] DEV method2 AUDNZD|F1_h16|S: stop table (2005-2021, netR) None: mean +0.130 t 12.49 ratio 21.02; 2: mean +0.129 t 13.42 ratio 27.68; 3: mean +0.133 t 13.35 ratio 24.34 -> stop = 2
- [2026-11-04T02:36:02+00:00] DEV method2: refinement selected on 2005-2014 = {'cond': 'c_weekday', 'exclude': 'Thu'} (frozen r7_method2_refine.json)
- [2026-11-04T02:36:02+00:00] DEV method2: refinement confirmation 2015-2021: not adopted {'N_val': 1812, 'ratio_base': 94.7850287246857, 'ratio_filtered': 71.75514282470895, 'mean_excl': 0.2219277779861366, 'mean_rest': 0.2532237826264078, 'n_excl': 364}
- [2026-11-04T02:36:02+00:00] DEV method2: daily-return correlation (2005-2021) method1 -0.02
- [2026-11-04T02:36:02+00:00] FROZEN method2 -> r7_method2_frozen.json: short AUDNZD from 16:00 to 17:00 EST every day (H1 bar open->close); stop 2R; refinement None; pool N 3660 mean +0.129R (+2.17 pips) t 13.42 ratio 27.68
- [2026-11-04T02:36:02+00:00] HOLDOUT EVALUATION START method2 (2022-01..2024-12), rules frozen at 2026-11-04T02:36:02+00:00
- [2026-11-04T02:36:04+00:00] HOLDOUT method2: N 718 mean +0.129R (+1.88 pips) t 7.36 | pool mean +0.129R | full 2005-2024 t 15.11 ratio 33.10 | crit {'holdout_mean_gt0': True, 'holdout_ge_25pct': True, 'full_t': True, 'full_ratio': True} -> ACCEPTED
- [2026-11-04T02:36:04+00:00] DEV method3 EURAUD|F1_h17|L: stop table (2005-2021, netR) None: mean +0.087 t 13.84 ratio 26.71; 2: mean +0.085 t 13.44 ratio 26.11; 3: mean +0.087 t 13.74 ratio 24.55 -> stop = None
- [2026-11-04T02:36:05+00:00] DEV method3: refinement selected on 2005-2014 = {'cond': 'c_weekday', 'exclude': 'Sun'} (frozen r7_method3_refine.json)
- [2026-11-04T02:36:05+00:00] DEV method3: refinement confirmation 2015-2021: CONFIRMED {'N_val': 1813, 'ratio_base': 79.76403874590716, 'ratio_filtered': 105.33011640190894, 'mean_excl': 0.1439670418115866, 'mean_rest': 0.16233623324982138, 'n_excl': 361}
- [2026-11-04T02:36:05+00:00] DEV method3: daily-return correlation (2005-2021) method1 +0.02, method2 -0.01
- [2026-11-04T02:36:05+00:00] FROZEN method3 -> r7_method3_frozen.json: long EURAUD from 17:00 to 18:00 EST every day (H1 bar open->close); stop None; refinement {'cond': 'c_weekday', 'exclude': 'Sun'}; pool N 3527 mean +0.094R (+2.97 pips) t 14.03 ratio 31.12
- [2026-11-04T02:36:05+00:00] HOLDOUT EVALUATION START method3 (2022-01..2024-12), rules frozen at 2026-11-04T02:36:05+00:00
- [2026-11-04T02:36:08+00:00] HOLDOUT method3: N 570 mean +0.195R (+5.85 pips) t 16.55 | pool mean +0.094R | full 2005-2024 t 17.95 ratio 41.56 | crit {'holdout_mean_gt0': True, 'holdout_ge_25pct': True, 'full_t': True, 'full_ratio': True} -> ACCEPTED

## Loop finished 2026-11-04T02:36:08+00:00: months tried 2, candidate tests 20, accepted methods [2, 3]

---
# Library v1 — summary and verdict (logged 2026-11-04, before the switch to library v2)

- Library v1 = F1-F9 only, top 10 per month, confirmation t >= 3.2. Months tried with v1: **2012-03** (0 confirmed / 10 limited) and **2021-07** (3 confirmed / 7 limited). Candidate tests under v1: **20**.
- The 3 v1 confirmations were all F1 hour-of-day buckets touching the **17:00 EST daily rollover**: AUDNZD short 16-17 EST, EURAUD long 17-18 EST, GBPCHF short 16-17 EST. The loop promoted the first two (frozen as method2/method3, files now renamed `r7_v1_method2_*`, `r7_v1_method3_*`), looked at the 2022-2024 holdout once each (2 holdout looks, see `r7_holdout_timeline.log`), and both passed the numeric acceptance criteria (holdout +0.129R and +0.195R per trade).
- **Verdict: both REJECTED as a data artifact, not a tradable edge.** Diagnostic on 2005-2021 only (`r7_rollover_diag.log`, `r7_rollover_diag2.log`): the bid-only M5 open drops on average 1.3-3.5 pips exactly at the 17:00 EST bar on crosses (AUDNZD -2.3, EURAUD -2.3, GBPCHF -2.9, EURCHF -1.6, EURGBP -1.3; EURUSD -0.35) and partly recovers by 17:15-17:30, in US summer and winter alike, while the M5 high-low range widens ~1.7x at 16:55-17:05. Selling into 17:00 and buying at 17:00 on bid quotes captures this spread-widening dip; in real trading the trade would be filled at the ask with a rollover spread of several pips, so the 0.5-pip cost assumption does not hold there. The edges (+2.1 and +2.8 pips/trade) are the size of the dip. GBPCHF (3rd confirmed) is the same effect and was not promoted.
- Consequence for library v2: a **rollover validity rule** is added — no entry or exit price may be stamped 16:55-17:30 EST (H1 stamps at 17:00 move to 18:00; F1 hours 16/17, F3 NY session (exit 17:00), F8 Sunday-open (FX), F7 units at 16:00/17:00 and F4/F5/F9 trades entering/exiting at 17:00 are removed; bracket TP/SL checks ignore the 17:00 H1 bar). Method numbering restarts at 2 for library v2.

# Library v2 loop (started 2026-11-04T03:02:55+00:00)

Same seed-42 month sequence; months tried under v1 are re-scanned. Top 20 per month; confirmation min(t on trades, t on daily P&L) of net R >= 3.5, >=3/4 blocks positive, 2x cost > 0, pooled rules also >= 60% of pairs positive. Rollover validity rule: no entry/exit price stamped 16:55-17:30 EST. Test count continues from v1 (20).

## v2 Month 1: 2012-03  (discovery 2026-11-04T03:03:32+00:00; 8601 candidate rows with >=8 events and in-month t>2.5 [v2] or any t [v1])

| # | candidate | family | events | in-month t | in-month mean net R |
|---|---|---|---|---|---|
| 1 | H1 EURGBP Z_SWH_rej & dh4=1 & dd1=0 & loc=SWH → br follow | combination (zone trigger) | 14 | 8.09 | +0.983 |
| 2 | H4 NZDUSD I_adx_gt25 → h4 fade | indicator | 32 | 7.19 | +1.562 |
| 3 | H1 GBPJPY Z_PDL_rej & dh4=0 & e200=1 & macdt=1 → h24 fade | combination (zone trigger) | 9 | 6.27 | +4.608 |
| 4 | H4 GBPCHF I_ema200 → h24 fade | indicator | 131 | 6.25 | +2.400 |
| 5 | H4 NZDUSD I_adx_gt25 → h12 fade | indicator | 32 | 6.21 | +3.435 |
| 6 | H1 EURUSD Z_PP_rej & dh4=-1 & dd1=-1 & loc=PP → h12 follow | combination (zone trigger) | 9 | 5.99 | +2.041 |
| 7 | H4 NZDUSD I_adx_gt25 → br fade | indicator | 32 | 5.99 | +1.738 |
| 8 | H1 EURUSD Z_PP_rej & dd1=-1 & loc=PP & macdh=1 → h12 follow | combination (zone trigger) | 10 | 5.91 | +1.811 |
| 9 | H1 GBPCHF Z_SWL_rej & dh4=1 & dd1=0 & macdt=1 → br follow | combination (zone trigger) | 9 | 5.76 | +1.089 |
| 10 | H1 EURUSD Z_PP_rej & dd1=-1 & loc=PP & stz=0 → h12 follow | combination (zone trigger) | 12 | 5.76 | +2.081 |
| 11 | H1 EURUSD Z_SWH_at & dh4=-1 & dd1=-1 & stz=0 → br fade | combination (zone trigger) | 16 | 5.76 | +0.692 |
| 12 | H1 GBPCHF Z_SWL_at & dh4=1 & dd1=0 & rsi50=-1 → br follow | combination (zone trigger) | 12 | 5.75 | +0.816 |
| 13 | H1 EURUSD Z_SWH_rej & dh4=-1 & dd1=-1 & loc=SWH → br fade | combination (zone trigger) | 11 | 5.75 | +1.005 |
| 14 | H1 AUDUSD Z_ASH_at & e200=-1 & macdh=1 → br fade | combination (zone trigger) | 16 | 5.74 | +0.809 |
| 15 | H1 EURUSD Z_SWH_rej & dh4=-1 & dd1=-1 & stz=0 → br fade | combination (zone trigger) | 11 | 5.61 | +0.982 |
| 16 | H1 EURUSD Z_PP_rej & dd1=-1 & loc=PP & rsiz=2 → h24 follow | combination (zone trigger) | 8 | 5.53 | +3.035 |
| 17 | H1 EURUSD Z_SWH_rej & dh4=-1 & e200=-1 & stz=0 → h12 fade | combination (zone trigger) | 11 | 5.53 | +1.541 |
| 18 | H1 EURUSD C_outside & dd1=-1 & e200=1 & macdh=-1 → h12 fade | combination (candle trigger) | 11 | 5.53 | +1.778 |
| 19 | H1 NZDJPY Z_SWL_rej & dh4=0 & e200=1 & rsi50=-1 → br fade | combination (zone trigger) | 13 | 5.52 | +0.707 |
| 20 | H1 GBPCHF Z_SWL_rej & dh4=1 & dd1=0 & rsiz=1 → br follow | combination (zone trigger) | 10 | 5.44 | +0.925 |

Confirmation on the other 203 pool months (2026-11-04T03:03:36+00:00); running test count (v1+v2) = 40

| # | candidate | N | mean pips | mean R | t trades | t daily | gross R | 2x-cost R | blocks + | pairs + | verdict | context |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H1 EURGBP Z_SWH_rej & dh4=1 & dd1=0 & loc=SWH → br follow | 569 | -0.74 | -0.043 | -1.06 | -1.03 | -0.007 | -0.079 | 1/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.029R t-2.9 |
| 2 | H4 NZDUSD I_adx_gt25 → h4 fade | 3115 | -0.59 | -0.056 | -1.52 | -1.51 | -0.030 | -0.083 | 1/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.042R t-4.2 |
| 3 | H1 GBPJPY Z_PDL_rej & dh4=0 & e200=1 & macdt=1 → h24 fade | 155 | -0.50 | -0.221 | -1.01 | -1.01 | -0.208 | -0.235 | 1/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.092R t-1.7 |
| 4 | H4 GBPCHF I_ema200 → h24 fade | 1120 | +6.19 | +0.213 | 1.26 | 1.26 | +0.230 | +0.197 | 3/4 | other pairs 8/16 | **limited** | same rule other 16 pairs pooled -0.008R t-0.2 |
| 5 | H4 NZDUSD I_adx_gt25 → h12 fade | 1197 | +1.35 | -0.042 | -0.40 | -0.40 | -0.016 | -0.069 | 2/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.049R t-1.8 |
| 6 | H1 EURUSD Z_PP_rej & dh4=-1 & dd1=-1 & loc=PP → h12 follow | 218 | -10.12 | -0.340 | -2.48 | -2.46 | -0.318 | -0.361 | 0/4 | other pairs 7/16 | **limited** | same rule other 16 pairs pooled -0.021R t-0.7 |
| 7 | H4 NZDUSD I_adx_gt25 → br fade | 2927 | -0.53 | -0.058 | -1.56 | -1.51 | -0.032 | -0.085 | 1/4 | other pairs 2/16 | **limited** | same rule other 16 pairs pooled -0.055R t-5.9 |
| 8 | H1 EURUSD Z_PP_rej & dd1=-1 & loc=PP & macdh=1 → h12 follow | 356 | -9.66 | -0.276 | -2.83 | -2.79 | -0.254 | -0.299 | 0/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.121R t-1.2 |
| 9 | H1 GBPCHF Z_SWL_rej & dh4=1 & dd1=0 & macdt=1 → br follow | 487 | +1.38 | +0.045 | 0.99 | 1.01 | +0.062 | +0.028 | 3/4 | other pairs 2/16 | **limited** | same rule other 16 pairs pooled -0.041R t-3.5 |
| 10 | H1 EURUSD Z_PP_rej & dd1=-1 & loc=PP & stz=0 → h12 follow | 580 | -2.96 | -0.113 | -1.47 | -1.47 | -0.092 | -0.135 | 0/4 | other pairs 7/16 | **limited** | same rule other 16 pairs pooled -0.061R t-1.0 |
| 11 | H1 EURUSD Z_SWH_at & dh4=-1 & dd1=-1 & stz=0 → br fade | 428 | +0.14 | +0.015 | 0.34 | 0.33 | +0.037 | -0.007 | 2/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.035R t-3.0 |
| 12 | H1 GBPCHF Z_SWL_at & dh4=1 & dd1=0 & rsi50=-1 → br follow | 699 | -0.76 | -0.030 | -0.81 | -0.84 | -0.013 | -0.048 | 1/4 | other pairs 4/16 | **limited** | same rule other 16 pairs pooled -0.024R t-2.3 |
| 13 | H1 EURUSD Z_SWH_rej & dh4=-1 & dd1=-1 & loc=SWH → br fade | 339 | +0.74 | +0.017 | 0.33 | 0.34 | +0.039 | -0.005 | 2/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.032R t-2.4 |
| 14 | H1 AUDUSD Z_ASH_at & e200=-1 & macdh=1 → br fade | 1261 | -0.49 | -0.039 | -1.35 | -1.36 | -0.014 | -0.064 | 0/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.055R t-8.0 |
| 15 | H1 EURUSD Z_SWH_rej & dh4=-1 & dd1=-1 & stz=0 → br fade | 415 | +0.21 | +0.011 | 0.24 | 0.23 | +0.033 | -0.011 | 2/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.024R t-1.9 |
| 16 | H1 EURUSD Z_PP_rej & dd1=-1 & loc=PP & rsiz=2 → h24 follow | 322 | -1.48 | -0.039 | -0.27 | -0.27 | -0.018 | -0.061 | 1/4 | other pairs 11/16 | **limited** | same rule other 16 pairs pooled +0.076R t2.2 |
| 17 | H1 EURUSD Z_SWH_rej & dh4=-1 & e200=-1 & stz=0 → h12 fade | 642 | +1.47 | +0.052 | 0.69 | 0.69 | +0.074 | +0.029 | 2/4 | other pairs 7/16 | **limited** | same rule other 16 pairs pooled -0.081R t-1.1 |
| 18 | H1 EURUSD C_outside & dd1=-1 & e200=1 & macdh=-1 → h12 fade | 430 | -1.46 | -0.075 | -0.81 | -0.82 | -0.053 | -0.098 | 1/4 | other pairs 7/16 | **limited** | same rule other 16 pairs pooled -0.019R t-0.8 |
| 19 | H1 NZDJPY Z_SWL_rej & dh4=0 & e200=1 & rsi50=-1 → br fade | 729 | -1.78 | -0.079 | -2.19 | -2.22 | -0.055 | -0.102 | 0/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.022R t-2.3 |
| 20 | H1 GBPCHF Z_SWL_rej & dh4=1 & dd1=0 & rsiz=1 → br follow | 620 | +1.06 | +0.021 | 0.52 | 0.54 | +0.038 | +0.004 | 3/4 | other pairs 2/16 | **limited** | same rule other 16 pairs pooled -0.048R t-4.4 |

Month result: 0 CONFIRMED, 20 limited.

## v2 Month 2: 2021-07  (discovery 2026-11-04T03:04:04+00:00; 8973 candidate rows with >=8 events and in-month t>2.5 [v2] or any t [v1])

| # | candidate | family | events | in-month t | in-month mean net R |
|---|---|---|---|---|---|
| 1 | H4 GBPJPY I_rsi_lt30 → h24 fade | indicator | 12 | 10.20 | +6.989 |
| 2 | H1 CADJPY I_rsi_gt70 → br fade | indicator | 31 | 7.26 | +0.610 |
| 3 | H1 EURCHF Z_SWH_at & dd1=0 & e200=-1 & macdh=-1 → br follow | combination (zone trigger) | 14 | 6.58 | +0.928 |
| 4 | H1 USDCHF Z_ASH_at & dh4=1 & macdt=1 → h24 follow | combination (zone trigger) | 12 | 6.56 | +2.659 |
| 5 | H1 POOL T_a_e4 & dh4=0 & dd1=0 & macdh=-1 → h24 follow | combination (trendline trigger) | 8 | 6.19 | +3.822 |
| 6 | H1 POOL T_a_any & dh4=0 & dd1=0 & macdh=-1 → h24 follow | combination (trendline trigger) | 8 | 6.19 | +3.822 |
| 7 | H4 AUDNZD Z_PWL_rej & macdt=1 → br follow | combination (zone trigger) | 13 | 6.17 | +2.347 |
| 8 | H4 USDJPY Z_PP_rej & dd1=1 & stz=0 → br follow | combination (zone trigger) | 9 | 6.14 | +2.211 |
| 9 | H1 USDCHF Z_ASH_at & dh4=1 & macdh=-1 → h24 follow | combination (zone trigger) | 11 | 5.89 | +2.634 |
| 10 | H1 AUDNZD Z_SWH_at & dh4=0 & e200=-1 & macdt=-1 → br follow | combination (zone trigger) | 19 | 5.79 | +0.796 |
| 11 | H4 XAUUSD I_ema200 → h24 fade | indicator | 131 | 5.78 | +1.890 |
| 12 | H1 EURGBP Z_S1_rej & dd1=1 → br follow | combination (zone trigger) | 9 | 5.71 | +1.255 |
| 13 | H1 AUDNZD Z_SWH_rej & dh4=0 & e200=-1 & macdt=-1 → br follow | combination (zone trigger) | 17 | 5.66 | +0.869 |
| 14 | GBPCHF F1_h18 long/follow | time | 21 | 5.50 | +0.261 |
| 15 | H4 POOL Z_PP_brk & dd1=0 & e200=-1 & macdt=-1 → h24 follow | combination (zone trigger) | 21 | 5.49 | +4.347 |
| 16 | H1 AUDNZD Z_SWH_rej & dh4=0 & e200=-1 & rsiz=2 → br follow | combination (zone trigger) | 15 | 5.44 | +0.947 |
| 17 | H4 AUDNZD Z_SWL_rej & macdt=1 → br follow | combination (zone trigger) | 15 | 5.37 | +2.039 |
| 18 | H4 POOL Z_SWH_at & macdt=1 → h24 follow | combination (zone trigger) | 202 | 5.23 | +1.419 |
| 19 | H4 POOL Z_PP_rej & e200=-1 & loc=SWH & macdh=1 → h24 fade | combination (zone trigger) | 35 | 5.22 | +2.852 |
| 20 | H1 POOL Z_S1_at & dd1=1 & e200=1 & rsiz=1 → br fade | combination (zone trigger) | 10 | 5.16 | +1.047 |

Confirmation on the other 203 pool months (2026-11-04T03:04:07+00:00); running test count (v1+v2) = 60

| # | candidate | N | mean pips | mean R | t trades | t daily | gross R | 2x-cost R | blocks + | pairs + | verdict | context |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H4 GBPJPY I_rsi_lt30 → h24 fade | 255 | -5.96 | +0.035 | 0.09 | 0.09 | +0.048 | +0.021 | 2/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.184R t-2.0 |
| 2 | H1 CADJPY I_rsi_gt70 → br fade | 2019 | +0.20 | -0.014 | -0.62 | -0.61 | +0.009 | -0.037 | 2/4 | other pairs 1/16 | **limited** | same rule other 16 pairs pooled -0.032R t-5.7 |
| 3 | H1 EURCHF Z_SWH_at & dd1=0 & e200=-1 & macdh=-1 → br follow | 512 | -0.39 | -0.038 | -0.82 | -0.86 | +0.019 | -0.096 | 1/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.014R t-1.1 |
| 4 | H1 USDCHF Z_ASH_at & dh4=1 & macdt=1 → h24 follow | 718 | +0.42 | +0.051 | 0.36 | 0.36 | +0.077 | +0.026 | 3/4 | other pairs 11/16 | **limited** | same rule other 16 pairs pooled +0.055R t0.9 |
| 5 | H1 POOL T_a_e4 & dh4=0 & dd1=0 & macdh=-1 → h24 follow | 1781 | -0.62 | -0.058 | -0.97 | -0.94 | -0.035 | -0.082 | 2/4 | 8/17 | **limited** | USDCHF +0.308R, CADJPY +0.225R, AUDNZD +0.224R, USDCAD +0.220R |
| 6 | H1 POOL T_a_any & dh4=0 & dd1=0 & macdh=-1 → h24 follow | 1781 | -0.62 | -0.058 | -0.97 | -0.94 | -0.035 | -0.082 | 2/4 | 8/17 | **limited** | USDCHF +0.308R, CADJPY +0.225R, AUDNZD +0.224R, USDCAD +0.220R |
| 7 | H4 AUDNZD Z_PWL_rej & macdt=1 → br follow | 417 | -0.66 | -0.086 | -0.86 | -0.84 | -0.058 | -0.113 | 2/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.020R t-0.8 |
| 8 | H4 USDJPY Z_PP_rej & dd1=1 & stz=0 → br follow | 637 | +1.47 | +0.057 | 0.75 | 0.75 | +0.084 | +0.031 | 2/4 | other pairs 9/16 | **limited** | same rule other 16 pairs pooled +0.006R t0.3 |
| 9 | H1 USDCHF Z_ASH_at & dh4=1 & macdh=-1 → h24 follow | 543 | -1.20 | -0.047 | -0.45 | -0.45 | -0.021 | -0.073 | 2/4 | other pairs 7/16 | **limited** | same rule other 16 pairs pooled +0.013R t0.5 |
| 10 | H1 AUDNZD Z_SWH_at & dh4=0 & e200=-1 & macdt=-1 → br follow | 633 | -0.67 | -0.058 | -1.34 | -1.31 | -0.030 | -0.086 | 2/4 | other pairs 8/16 | **limited** | same rule other 16 pairs pooled -0.009R t-1.0 |
| 11 | H4 XAUUSD I_ema200 → h24 fade | 836 | -104.94 | -0.383 | -1.95 | -1.95 | -0.314 | -0.451 | 0/3 | other pairs 9/17 | **limited** | same rule other 16 pairs pooled +0.010R t0.2 |
| 12 | H1 EURGBP Z_S1_rej & dd1=1 → br follow | 773 | -0.43 | +0.001 | 0.01 | 0.01 | +0.038 | -0.037 | 2/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.028R t-3.0 |
| 13 | H1 AUDNZD Z_SWH_rej & dh4=0 & e200=-1 & macdt=-1 → br follow | 730 | -2.17 | -0.104 | -2.61 | -2.49 | -0.077 | -0.131 | 0/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.030R t-3.4 |
| 14 | GBPCHF F1_h18 long/follow | 4350 | +0.79 | +0.039 | 7.75 | 7.75 | +0.055 | +0.022 | 2/4 | 10/17 | **limited** | GBPJPY +0.025R t4.0, CADJPY +0.022R t3.4, EURCHF +0.017R t3.1, h17 nanR tnan, h19 -0.016R t-2.9 |
| 15 | H4 POOL Z_PP_brk & dd1=0 & e200=-1 & macdt=-1 → h24 follow | 2564 | +2.21 | +0.005 | 0.05 | 0.04 | +0.029 | -0.020 | 2/4 | 7/17 | **limited** | GBPUSD +1.103R, NZDJPY +0.759R, GBPJPY +0.679R, EURCHF +0.470R |
| 16 | H1 AUDNZD Z_SWH_rej & dh4=0 & e200=-1 & rsiz=2 → br follow | 677 | -1.79 | -0.078 | -1.91 | -1.79 | -0.050 | -0.105 | 1/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.041R t-4.3 |
| 17 | H4 AUDNZD Z_SWL_rej & macdt=1 → br follow | 1011 | -1.56 | -0.090 | -1.41 | -1.39 | -0.063 | -0.118 | 1/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.023R t-1.5 |
| 18 | H4 POOL Z_SWH_at & macdt=1 → h24 follow | 9731 | +1.55 | +0.004 | 0.08 | 0.07 | +0.028 | -0.020 | 2/4 | 8/17 | **limited** | AUDNZD +0.318R, USDCHF +0.284R, CADJPY +0.277R, EURUSD +0.242R |
| 19 | H4 POOL Z_PP_rej & e200=-1 & loc=SWH & macdh=1 → h24 fade | 1856 | -1.94 | -0.089 | -0.77 | -0.74 | -0.064 | -0.115 | 1/4 | 7/17 | **limited** | AUDUSD +0.940R, GBPCHF +0.563R, NZDUSD +0.521R, AUDNZD +0.451R |
| 20 | H1 POOL Z_S1_at & dd1=1 & e200=1 & rsiz=1 → br fade | 3437 | -1.02 | -0.052 | -3.00 | -2.89 | -0.029 | -0.075 | 0/4 | 4/17 | **limited** | EURAUD +0.113R, GBPCHF +0.047R, AUDUSD +0.035R, AUDJPY +0.004R |

Month result: 0 CONFIRMED, 20 limited.

## v2 Month 3: 2017-07  (discovery 2026-11-04T03:04:35+00:00; 8583 candidate rows with >=8 events and in-month t>2.5 [v2] or any t [v1])

| # | candidate | family | events | in-month t | in-month mean net R |
|---|---|---|---|---|---|
| 1 | H4 EURUSD I_bb_lh → h24 fade | indicator | 43 | 7.35 | +5.275 |
| 2 | H4 EURUSD I_ema200 → h24 follow | indicator | 127 | 7.16 | +4.558 |
| 3 | H4 EURUSD I_cloud → h24 follow | indicator | 125 | 6.82 | +4.508 |
| 4 | H1 EURUSD Z_SWL_rej & dh4=0 & dd1=1 & stz=-1 → h24 follow | combination (zone trigger) | 8 | 6.42 | +3.766 |
| 5 | H4 EURUSD I_rsi_50_70 → h24 follow | indicator | 86 | 5.83 | +5.102 |
| 6 | H1 AUDJPY Z_SWH_at & loc=PDH & macdh=1 → h12 fade | combination (zone trigger) | 10 | 5.76 | +2.605 |
| 7 | H1 EURGBP Z_SWH_at & dh4=1 & dd1=1 & rsi50=1 → br fade | combination (zone trigger) | 11 | 5.65 | +0.860 |
| 8 | H1 NZDJPY Z_ASL_rej & dh4=0 & dd1=1 & macdh=-1 → h4 follow | combination (zone trigger) | 10 | 5.61 | +1.382 |
| 9 | H4 POOL Z_PP_rej & dd1=1 & e200=-1 & macdh=1 → br follow | combination (zone trigger) | 12 | 5.56 | +2.183 |
| 10 | H4 POOL I_bb_uh → h24 follow | indicator | 1033 | 5.53 | +1.484 |
| 11 | H1 GBPUSD Z_PP_rej & dh4=0 & dd1=0 & stz=0 → h12 follow | combination (zone trigger) | 8 | 5.42 | +2.370 |
| 12 | H1 EURCHF Z_PP_at & dh4=1 & macdh=-1 → br follow | combination (zone trigger) | 13 | 5.41 | +1.176 |
| 13 | H1 POOL T_a_any & dd1=-1 & e200=1 & macdt=1 → tt fade | combination (trendline trigger) | 8 | 5.39 | +1.595 |
| 14 | H1 EURCHF Z_PP_at & dh4=1 & macdh=-1 → h24 follow | combination (zone trigger) | 13 | 5.34 | +2.728 |
| 15 | H4 POOL I_ema200 → h24 follow | indicator | 2159 | 5.26 | +1.233 |
| 16 | H1 EURGBP Z_SWH_at & dh4=1 & dd1=1 & loc=SWH → br fade | combination (zone trigger) | 12 | 5.21 | +0.727 |
| 17 | H4 EURUSD I_rsi_30_50 → h24 fade | indicator | 24 | 5.18 | +4.774 |
| 18 | H1 GBPUSD Z_PP_rej & dh4=0 & dd1=0 & rsi50=-1 → h12 follow | combination (zone trigger) | 10 | 5.10 | +2.318 |
| 19 | H1 EURCHF Z_PP_at & dh4=1 & e200=1 & loc=PP → br follow | combination (zone trigger) | 14 | 5.10 | +1.163 |
| 20 | H1 EURUSD T_a_dd1 & stz=0 → h24 follow | combination (trendline trigger) | 9 | 5.07 | +3.222 |

Confirmation on the other 203 pool months (2026-11-04T03:04:40+00:00); running test count (v1+v2) = 80

| # | candidate | N | mean pips | mean R | t trades | t daily | gross R | 2x-cost R | blocks + | pairs + | verdict | context |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H4 EURUSD I_bb_lh → h24 fade | 898 | -2.29 | -0.076 | -0.43 | -0.43 | -0.054 | -0.098 | 2/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.084R t-1.5 |
| 2 | H4 EURUSD I_ema200 → h24 follow | 1121 | +2.25 | +0.061 | 0.39 | 0.39 | +0.083 | +0.039 | 2/4 | other pairs 4/16 | **limited** | same rule other 16 pairs pooled -0.067R t-1.2 |
| 3 | H4 EURUSD I_cloud → h24 follow | 1103 | -1.49 | -0.044 | -0.27 | -0.27 | -0.022 | -0.066 | 3/4 | other pairs 8/16 | **limited** | same rule other 16 pairs pooled -0.021R t-0.4 |
| 4 | H1 EURUSD Z_SWL_rej & dh4=0 & dd1=1 & stz=-1 → h24 follow | 193 | -9.44 | -0.287 | -1.64 | -1.64 | -0.265 | -0.308 | 1/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.105R t-2.0 |
| 5 | H4 EURUSD I_rsi_50_70 → h24 follow | 867 | -2.78 | -0.041 | -0.23 | -0.23 | -0.020 | -0.063 | 2/4 | other pairs 7/16 | **limited** | same rule other 16 pairs pooled -0.035R t-0.8 |
| 6 | H1 AUDJPY Z_SWH_at & loc=PDH & macdh=1 → h12 fade | 920 | -0.62 | +0.005 | 0.09 | 0.09 | +0.028 | -0.017 | 2/4 | other pairs 8/16 | **limited** | same rule other 16 pairs pooled -0.017R t-1.1 |
| 7 | H1 EURGBP Z_SWH_at & dh4=1 & dd1=1 & rsi50=1 → br fade | 494 | -0.92 | -0.050 | -1.11 | -1.07 | -0.014 | -0.087 | 1/4 | other pairs 2/16 | **limited** | same rule other 16 pairs pooled -0.051R t-4.9 |
| 8 | H1 NZDJPY Z_ASL_rej & dh4=0 & dd1=1 & macdh=-1 → h4 follow | 412 | -0.93 | -0.025 | -0.49 | -0.48 | -0.001 | -0.050 | 2/4 | other pairs 4/16 | **limited** | same rule other 16 pairs pooled -0.034R t-2.4 |
| 9 | H4 POOL Z_PP_rej & dd1=1 & e200=-1 & macdh=1 → br follow | 1851 | -1.21 | -0.054 | -1.22 | -1.17 | -0.030 | -0.078 | 0/4 | 6/17 | **limited** | NZDJPY +0.358R, GBPJPY +0.175R, EURGBP +0.141R, GBPUSD +0.056R |
| 10 | H4 POOL I_bb_uh → h24 follow | 15097 | -2.69 | -0.107 | -1.84 | -1.53 | -0.083 | -0.130 | 1/4 | 8/17 | **limited** | USDJPY +0.148R, AUDJPY +0.126R, GBPJPY +0.096R, EURJPY +0.070R |
| 11 | H1 GBPUSD Z_PP_rej & dh4=0 & dd1=0 & stz=0 → h12 follow | 426 | +0.48 | +0.057 | 0.56 | 0.56 | +0.074 | +0.040 | 2/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.037R t-1.8 |
| 12 | H1 EURCHF Z_PP_at & dh4=1 & macdh=-1 → br follow | 1174 | +0.12 | -0.013 | -0.42 | -0.41 | +0.030 | -0.056 | 2/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.017R t-2.4 |
| 13 | H1 POOL T_a_any & dd1=-1 & e200=1 & macdt=1 → tt fade | 2029 | -1.93 | -0.059 | -1.56 | -1.47 | -0.036 | -0.083 | 1/4 | 5/17 | **limited** | EURAUD +0.293R, AUDNZD +0.183R, NZDUSD +0.180R, EURUSD +0.084R |
| 14 | H1 EURCHF Z_PP_at & dh4=1 & macdh=-1 → h24 follow | 793 | -2.72 | -0.752 | -1.04 | -1.04 | -0.708 | -0.795 | 1/4 | other pairs 7/16 | **limited** | same rule other 16 pairs pooled -0.012R t-0.5 |
| 15 | H4 POOL I_ema200 → h24 follow | 18487 | -2.23 | -0.059 | -1.11 | -0.97 | -0.036 | -0.083 | 1/4 | 5/17 | **limited** | EURCHF +0.408R, EURUSD +0.061R, AUDNZD +0.028R, AUDJPY +0.014R |
| 16 | H1 EURGBP Z_SWH_at & dh4=1 & dd1=1 & loc=SWH → br fade | 735 | -1.47 | -0.092 | -2.47 | -2.40 | -0.056 | -0.128 | 0/4 | other pairs 0/16 | **limited** | same rule other 16 pairs pooled -0.051R t-5.9 |
| 17 | H4 EURUSD I_rsi_30_50 → h24 fade | 857 | -4.54 | -0.157 | -0.88 | -0.88 | -0.135 | -0.179 | 1/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.115R t-1.8 |
| 18 | H1 GBPUSD Z_PP_rej & dh4=0 & dd1=0 & rsi50=-1 → h12 follow | 315 | +1.91 | +0.108 | 0.94 | 0.94 | +0.125 | +0.092 | 3/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.050R t-2.1 |
| 19 | H1 EURCHF Z_PP_at & dh4=1 & e200=1 & loc=PP → br follow | 1072 | +0.18 | -0.003 | -0.09 | -0.09 | +0.040 | -0.046 | 2/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.019R t-2.6 |
| 20 | H1 EURUSD T_a_dd1 & stz=0 → h24 follow | 930 | -0.04 | -0.011 | -0.12 | -0.12 | +0.011 | -0.032 | 2/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.051R t-2.1 |

Month result: 0 CONFIRMED, 20 limited.

## v2 Month 4: 2013-11  (discovery 2026-11-04T03:05:07+00:00; 9804 candidate rows with >=8 events and in-month t>2.5 [v2] or any t [v1])

| # | candidate | family | events | in-month t | in-month mean net R |
|---|---|---|---|---|---|
| 1 | H1 GBPJPY Z_ASH_rej & dh4=0 & dd1=1 & rsi50=1 → h24 fade | combination (zone trigger) | 8 | 8.72 | +5.114 |
| 2 | H1 GBPJPY Z_ASH_rej & dh4=0 & dd1=1 & rsi50=1 → h12 fade | combination (zone trigger) | 8 | 7.70 | +3.056 |
| 3 | H1 EURGBP Z_SWL_rej & dd1=1 & macdh=1 → h24 fade | combination (zone trigger) | 9 | 6.64 | +4.315 |
| 4 | H1 GBPCHF C_outside & dh4=-1 & rsi50=-1 → h12 fade | combination (candle trigger) | 8 | 6.46 | +2.666 |
| 5 | H1 POOL Z_ASH_at & dh4=0 & e200=-1 & loc=PP → br fade | combination (zone trigger) | 21 | 6.38 | +0.651 |
| 6 | H4 EURJPY Z_PP_rej & e200=1 & macdh=-1 → h24 fade | combination (zone trigger) | 10 | 5.99 | +7.201 |
| 7 | H1 AUDJPY Z_SWL_at & dd1=1 & macdt=1 → h12 fade | combination (zone trigger) | 16 | 5.85 | +1.161 |
| 8 | H1 EURUSD Z_SWL_rej & dd1=0 & macdh=-1 → h24 fade | combination (zone trigger) | 12 | 5.78 | +2.112 |
| 9 | H1 AUDNZD Z_SWL_at & dh4=1 & macdt=1 → br follow | combination (zone trigger) | 17 | 5.63 | +0.691 |
| 10 | H4 USDJPY I_cloud → h24 follow | indicator | 119 | 5.62 | +3.957 |
| 11 | H4 CADJPY I_rsi_30_50 → br fade | indicator | 16 | 5.53 | +1.786 |
| 12 | H1 EURGBP C_outside & dh4=1 & e200=1 & rsi50=1 → h12 fade | combination (candle trigger) | 8 | 5.52 | +2.582 |
| 13 | H4 AUDJPY I_ema200 → h24 fade | indicator | 125 | 5.51 | +2.741 |
| 14 | H4 GBPJPY I_ema200 → h24 follow | indicator | 125 | 5.51 | +5.870 |
| 15 | H1 GBPJPY Z_ASL_rej & stz=0 → br follow | combination (zone trigger) | 19 | 5.50 | +1.044 |
| 16 | H1 USDCAD Z_ASL_at & e200=-1 & macdt=1 → h24 fade | combination (zone trigger) | 8 | 5.47 | +3.711 |
| 17 | H1 XAUUSD Z_ASH_rej & dd1=-1 & loc=SWH & macdt=1 → br follow | combination (zone trigger) | 13 | 5.45 | +0.691 |
| 18 | H1 AUDJPY Z_SWL_at & dd1=1 & macdt=1 → h24 fade | combination (zone trigger) | 16 | 5.45 | +1.492 |
| 19 | H1 EURCHF Z_SWL_rej & dh4=1 & rsi50=1 → h4 fade | combination (zone trigger) | 15 | 5.41 | +0.700 |
| 20 | H4 EURJPY I_rsi_50_70 → h24 follow | indicator | 55 | 5.38 | +6.190 |

Confirmation on the other 203 pool months (2026-11-04T03:05:12+00:00); running test count (v1+v2) = 100

| # | candidate | N | mean pips | mean R | t trades | t daily | gross R | 2x-cost R | blocks + | pairs + | verdict | context |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H1 GBPJPY Z_ASH_rej & dh4=0 & dd1=1 & rsi50=1 → h24 fade | 337 | +7.29 | +0.136 | 0.97 | 0.97 | +0.150 | +0.122 | 3/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.020R t-0.5 |
| 2 | H1 GBPJPY Z_ASH_rej & dh4=0 & dd1=1 & rsi50=1 → h12 fade | 397 | +8.33 | +0.187 | 1.94 | 1.94 | +0.201 | +0.173 | 4/4 | other pairs 9/16 | **limited** | same rule other 16 pairs pooled +0.003R t0.1 |
| 3 | H1 EURGBP Z_SWL_rej & dd1=1 & macdh=1 → h24 fade | 574 | +2.70 | +0.127 | 1.15 | 1.15 | +0.164 | +0.090 | 3/4 | other pairs 7/16 | **limited** | same rule other 16 pairs pooled -0.031R t-1.0 |
| 4 | H1 GBPCHF C_outside & dh4=-1 & rsi50=-1 → h12 fade | 1252 | -3.70 | -0.072 | -1.33 | -1.30 | -0.055 | -0.088 | 1/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.020R t-1.4 |
| 5 | H1 POOL Z_ASH_at & dh4=0 & e200=-1 & loc=PP → br fade | 1921 | -2.76 | -0.124 | -5.75 | -5.61 | -0.099 | -0.149 | 1/4 | 2/17 | **limited** | GBPJPY +0.102R, USDJPY +0.100R, GBPUSD -0.055R, GBPCHF -0.055R |
| 6 | H4 EURJPY Z_PP_rej & e200=1 & macdh=-1 → h24 fade | 406 | -4.72 | -0.262 | -1.02 | -1.02 | -0.243 | -0.281 | 1/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.091R t-1.3 |
| 7 | H1 AUDJPY Z_SWL_at & dd1=1 & macdt=1 → h12 fade | 897 | -1.23 | -0.061 | -0.81 | -0.82 | -0.038 | -0.084 | 2/4 | other pairs 2/16 | **limited** | same rule other 16 pairs pooled -0.047R t-3.0 |
| 8 | H1 EURUSD Z_SWL_rej & dd1=0 & macdh=-1 → h24 fade | 716 | -1.32 | -0.010 | -0.09 | -0.09 | +0.012 | -0.032 | 2/4 | other pairs 4/16 | **limited** | same rule other 16 pairs pooled -0.029R t-1.3 |
| 9 | H1 AUDNZD Z_SWL_at & dh4=1 & macdt=1 → br follow | 905 | -2.86 | -0.121 | -3.30 | -3.24 | -0.095 | -0.147 | 0/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.008R t-1.0 |
| 10 | H4 USDJPY I_cloud → h24 follow | 1099 | -0.10 | -0.006 | -0.04 | -0.04 | +0.020 | -0.031 | 2/4 | other pairs 7/16 | **limited** | same rule other 16 pairs pooled -0.025R t-0.5 |
| 11 | H4 CADJPY I_rsi_30_50 → br fade | 2653 | -2.53 | -0.102 | -2.67 | -2.61 | -0.080 | -0.125 | 1/4 | other pairs 0/16 | **limited** | same rule other 16 pairs pooled -0.065R t-7.2 |
| 12 | H1 EURGBP C_outside & dh4=1 & e200=1 & rsi50=1 → h12 fade | 1047 | -2.06 | -0.101 | -1.60 | -1.60 | -0.065 | -0.138 | 1/4 | other pairs 10/16 | **limited** | same rule other 16 pairs pooled +0.008R t0.5 |
| 13 | H4 AUDJPY I_ema200 → h24 fade | 1049 | -1.46 | -0.085 | -0.49 | -0.49 | -0.063 | -0.107 | 1/4 | other pairs 11/16 | **limited** | same rule other 16 pairs pooled +0.020R t0.4 |
| 14 | H4 GBPJPY I_ema200 → h24 follow | 1121 | -1.23 | -0.068 | -0.41 | -0.41 | -0.054 | -0.081 | 1/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.061R t-1.1 |
| 15 | H1 GBPJPY Z_ASL_rej & stz=0 → br follow | 3773 | -0.83 | -0.017 | -1.06 | -1.06 | -0.004 | -0.031 | 0/4 | other pairs 0/16 | **limited** | same rule other 16 pairs pooled -0.043R t-10.9 |
| 16 | H1 USDCAD Z_ASL_at & e200=-1 & macdt=1 → h24 fade | 824 | +1.49 | +0.054 | 0.60 | 0.60 | +0.077 | +0.030 | 2/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.027R t-1.1 |
| 17 | H1 XAUUSD Z_ASH_rej & dd1=-1 & loc=SWH & macdt=1 → br follow | 270 | -75.56 | -0.130 | -2.56 | -2.66 | -0.060 | -0.199 | 0/3 | other pairs 1/17 | **limited** | same rule other 16 pairs pooled -0.054R t-4.5 |
| 18 | H1 AUDJPY Z_SWL_at & dd1=1 & macdt=1 → h24 fade | 639 | +0.96 | +0.038 | 0.31 | 0.31 | +0.061 | +0.015 | 1/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.048R t-1.8 |
| 19 | H1 EURCHF Z_SWL_rej & dh4=1 & rsi50=1 → h4 fade | 736 | -0.68 | -0.034 | -0.86 | -0.86 | +0.016 | -0.085 | 1/4 | other pairs 8/16 | **limited** | same rule other 16 pairs pooled +0.002R t0.2 |
| 20 | H4 EURJPY I_rsi_50_70 → h24 follow | 880 | -2.25 | +0.043 | 0.25 | 0.25 | +0.062 | +0.025 | 3/4 | other pairs 7/16 | **limited** | same rule other 16 pairs pooled -0.038R t-0.8 |

Month result: 0 CONFIRMED, 20 limited.

## v2 Month 5: 2015-08  (discovery 2026-11-04T03:05:38+00:00; 8300 candidate rows with >=8 events and in-month t>2.5 [v2] or any t [v1])

| # | candidate | family | events | in-month t | in-month mean net R |
|---|---|---|---|---|---|
| 1 | H1 EURUSD Z_SWL_at & dd1=1 & e200=1 & macdh=1 → h12 follow | combination (zone trigger) | 10 | 7.10 | +2.560 |
| 2 | H1 EURUSD Z_SWL_rej & dd1=1 & e200=1 & loc=SWL → h12 follow | combination (zone trigger) | 9 | 6.89 | +2.758 |
| 3 | H1 GBPJPY Z_SWL_rej & dd1=1 & stz=0 → h12 fade | combination (zone trigger) | 24 | 6.31 | +1.230 |
| 4 | H1 EURCHF Z_SWL_at & loc=PP & macdt=-1 → h12 follow | combination (zone trigger) | 13 | 6.08 | +1.947 |
| 5 | H1 EURCHF Z_SWL_at & e200=1 & loc=PP & macdt=-1 → h12 follow | combination (zone trigger) | 10 | 5.75 | +2.073 |
| 6 | H1 EURUSD Z_SWL_rej & dh4=0 & e200=1 & rsiz=1 → br follow | combination (zone trigger) | 14 | 5.74 | +0.758 |
| 7 | H1 EURUSD Z_SWL_rej & e200=1 & macdt=-1 → br follow | combination (zone trigger) | 9 | 5.73 | +1.174 |
| 8 | H1 EURUSD I_rsi_gt70 → br follow | indicator | 62 | 5.71 | +0.594 |
| 9 | H1 EURUSD Z_SWL_rej & dd1=1 & e200=1 & loc=SWL → br follow | combination (zone trigger) | 9 | 5.66 | +1.161 |
| 10 | H4 POOL Z_PP_rej & dd1=-1 & e200=-1 & loc=none → br fade | combination (zone trigger) | 14 | 5.54 | +2.440 |
| 11 | H4 POOL Z_S1_at & dh4=0 & e200=-1 & loc=SWL → br follow | combination (zone trigger) | 21 | 5.53 | +1.378 |
| 12 | H1 EURAUD C_maru & dd1=1 & e200=1 & macdh=-1 → br follow | combination (candle trigger) | 16 | 5.51 | +1.225 |
| 13 | H1 EURAUD Z_SWL_rej & dd1=1 & loc=SWL & stz=0 → h12 fade | combination (zone trigger) | 12 | 5.49 | +2.327 |
| 14 | H4 POOL Z_S1_rej & e200=-1 & loc=S1 & macdh=-1 → br follow | combination (zone trigger) | 26 | 5.48 | +1.614 |
| 15 | H1 EURUSD Z_SWL_rej & dd1=1 & e200=1 & stz=0 → h24 follow | combination (zone trigger) | 10 | 5.44 | +2.911 |
| 16 | H4 EURGBP Z_PP_at & dd1=1 → br fade | combination (zone trigger) | 10 | 5.30 | +2.403 |
| 17 | H4 EURGBP Z_PP_at & dd1=1 & rsiz=2 → br fade | combination (zone trigger) | 9 | 5.29 | +2.347 |
| 18 | H1 AUDNZD Z_SWH_at & dh4=1 & macdt=1 → br follow | combination (zone trigger) | 14 | 5.24 | +0.691 |
| 19 | H1 POOL Z_ASH_at & dd1=-1 & e200=1 & macdt=-1 → br fade | combination (zone trigger) | 20 | 5.21 | +0.834 |
| 20 | H1 POOL Z_PWH_brk & dd1=1 & loc=none & rsi50=1 → br follow | combination (zone trigger) | 17 | 5.20 | +1.082 |

Confirmation on the other 203 pool months (2026-11-04T03:05:40+00:00); running test count (v1+v2) = 120

| # | candidate | N | mean pips | mean R | t trades | t daily | gross R | 2x-cost R | blocks + | pairs + | verdict | context |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H1 EURUSD Z_SWL_at & dd1=1 & e200=1 & macdh=1 → h12 follow | 354 | -1.31 | -0.002 | -0.02 | -0.02 | +0.020 | -0.023 | 2/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.048R t-2.0 |
| 2 | H1 EURUSD Z_SWL_rej & dd1=1 & e200=1 & loc=SWL → h12 follow | 524 | +0.86 | +0.029 | 0.35 | 0.35 | +0.051 | +0.007 | 3/4 | other pairs 8/16 | **limited** | same rule other 16 pairs pooled -0.038R t-1.8 |
| 3 | H1 GBPJPY Z_SWL_rej & dd1=1 & stz=0 → h12 fade | 1160 | -1.35 | -0.093 | -1.64 | -1.65 | -0.079 | -0.107 | 0/4 | other pairs 7/16 | **limited** | same rule other 16 pairs pooled -0.008R t-0.5 |
| 4 | H1 EURCHF Z_SWL_at & loc=PP & macdt=-1 → h12 follow | 943 | -0.12 | -0.039 | -0.75 | -0.75 | +0.015 | -0.094 | 1/4 | other pairs 7/16 | **limited** | same rule other 16 pairs pooled -0.003R t-0.2 |
| 5 | H1 EURCHF Z_SWL_at & e200=1 & loc=PP & macdt=-1 → h12 follow | 337 | +1.24 | -0.032 | -0.35 | -0.35 | +0.013 | -0.077 | 1/4 | other pairs 13/16 | **limited** | same rule other 16 pairs pooled +0.032R t1.3 |
| 6 | H1 EURUSD Z_SWL_rej & dh4=0 & e200=1 & rsiz=1 → br follow | 658 | -0.61 | -0.027 | -0.74 | -0.74 | -0.005 | -0.049 | 1/4 | other pairs 4/16 | **limited** | same rule other 16 pairs pooled -0.032R t-3.4 |
| 7 | H1 EURUSD Z_SWL_rej & e200=1 & macdt=-1 → br follow | 1630 | -0.65 | -0.022 | -0.95 | -0.94 | -0.000 | -0.043 | 2/4 | other pairs 0/16 | **limited** | same rule other 16 pairs pooled -0.045R t-7.5 |
| 8 | H1 EURUSD I_rsi_gt70 → br follow | 2137 | -0.59 | -0.021 | -0.94 | -0.94 | +0.001 | -0.043 | 1/4 | other pairs 1/16 | **limited** | same rule other 16 pairs pooled -0.043R t-7.2 |
| 9 | H1 EURUSD Z_SWL_rej & dd1=1 & e200=1 & loc=SWL → br follow | 684 | -0.79 | -0.014 | -0.40 | -0.41 | +0.008 | -0.036 | 2/4 | other pairs 4/16 | **limited** | same rule other 16 pairs pooled -0.024R t-2.5 |
| 10 | H4 POOL Z_PP_rej & dd1=-1 & e200=-1 & loc=none → br fade | 3886 | -3.19 | -0.117 | -3.79 | -3.57 | -0.094 | -0.141 | 0/4 | 2/17 | **limited** | EURGBP +0.218R, GBPCHF +0.089R, EURJPY -0.030R, GBPJPY -0.050R |
| 11 | H4 POOL Z_S1_at & dh4=0 & e200=-1 & loc=SWL → br follow | 1844 | -3.09 | -0.121 | -2.77 | -2.69 | -0.095 | -0.147 | 0/4 | 6/17 | **limited** | AUDJPY +0.188R, GBPUSD +0.170R, EURJPY +0.098R, EURCHF +0.095R |
| 12 | H1 EURAUD C_maru & dd1=1 & e200=1 & macdh=-1 → br follow | 620 | -2.51 | -0.079 | -1.77 | -1.63 | -0.063 | -0.095 | 0/4 | other pairs 0/16 | **limited** | same rule other 16 pairs pooled -0.071R t-7.9 |
| 13 | H1 EURAUD Z_SWL_rej & dd1=1 & loc=SWL & stz=0 → h12 fade | 807 | +0.18 | -0.036 | -0.58 | -0.59 | -0.020 | -0.051 | 1/4 | other pairs 7/16 | **limited** | same rule other 16 pairs pooled -0.001R t-0.1 |
| 14 | H4 POOL Z_S1_rej & e200=-1 & loc=S1 & macdh=-1 → br follow | 4655 | -2.07 | -0.038 | -1.33 | -1.25 | -0.014 | -0.062 | 0/4 | 6/17 | **limited** | EURGBP +0.221R, AUDUSD +0.157R, USDJPY +0.084R, USDCHF +0.082R |
| 15 | H1 EURUSD Z_SWL_rej & dd1=1 & e200=1 & stz=0 → h24 follow | 489 | -2.32 | -0.115 | -0.93 | -0.93 | -0.093 | -0.136 | 1/4 | other pairs 7/16 | **limited** | same rule other 16 pairs pooled -0.070R t-2.1 |
| 16 | H4 EURGBP Z_PP_at & dd1=1 → br fade | 753 | -0.77 | -0.052 | -0.76 | -0.77 | -0.015 | -0.089 | 2/4 | other pairs 9/16 | **limited** | same rule other 16 pairs pooled -0.008R t-0.5 |
| 17 | H4 EURGBP Z_PP_at & dd1=1 & rsiz=2 → br fade | 396 | +0.42 | -0.001 | -0.01 | -0.01 | +0.035 | -0.036 | 2/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.029R t-1.2 |
| 18 | H1 AUDNZD Z_SWH_at & dh4=1 & macdt=1 → br follow | 1498 | -0.53 | -0.024 | -0.82 | -0.81 | +0.002 | -0.051 | 1/4 | other pairs 2/16 | **limited** | same rule other 16 pairs pooled -0.029R t-5.0 |
| 19 | H1 POOL Z_ASH_at & dd1=-1 & e200=1 & macdt=-1 → br fade | 4717 | -0.84 | -0.045 | -3.09 | -2.90 | -0.021 | -0.068 | 0/4 | 5/17 | **limited** | NZDJPY +0.037R, GBPUSD +0.030R, USDCAD +0.021R, GBPCHF +0.017R |
| 20 | H1 POOL Z_PWH_brk & dd1=1 & loc=none & rsi50=1 → br follow | 2737 | -0.68 | -0.023 | -1.14 | -1.10 | +0.001 | -0.046 | 0/4 | 7/17 | **limited** | GBPCHF +0.137R, AUDUSD +0.128R, EURGBP +0.103R, GBPJPY +0.076R |

Month result: 0 CONFIRMED, 20 limited.

## v2 Month 6: 2019-03  (discovery 2026-11-04T03:06:07+00:00; 11357 candidate rows with >=8 events and in-month t>2.5 [v2] or any t [v1])

| # | candidate | family | events | in-month t | in-month mean net R |
|---|---|---|---|---|---|
| 1 | H1 GBPUSD Z_SWH_at & e200=-1 & macdt=1 → h12 fade | combination (zone trigger) | 9 | 10.41 | +4.128 |
| 2 | H1 GBPUSD Z_SWH_at & e200=-1 → h12 fade | combination (zone trigger) | 11 | 10.36 | +3.363 |
| 3 | H1 GBPUSD Z_SWH_at & e200=-1 & stz=0 → h12 fade | combination (zone trigger) | 10 | 9.01 | +3.217 |
| 4 | H4 POOL I_cloud → h24 fade | indicator | 1743 | 8.07 | +2.220 |
| 5 | H4 POOL I_ema200 → h24 fade | indicator | 2091 | 7.71 | +1.542 |
| 6 | H4 GBPUSD I_cloud → h24 fade | indicator | 90 | 6.91 | +3.869 |
| 7 | H1 POOL Z_R1_at & dd1=1 & e200=-1 & rsiz=1 → h12 fade | combination (zone trigger) | 12 | 6.67 | +2.059 |
| 8 | H1 GBPJPY Z_SWH_at & dh4=1 & e200=1 & macdt=1 → br follow | combination (zone trigger) | 14 | 6.20 | +1.021 |
| 9 | H1 EURGBP Z_PWL_at → br fade | zone | 17 | 6.19 | +0.831 |
| 10 | H1 USDJPY Z_SWL_at & e200=-1 & loc=ASL → h12 fade | combination (zone trigger) | 10 | 6.14 | +2.193 |
| 11 | H1 USDCHF Z_ASH_at & dd1=0 & macdt=-1 → br follow | combination (zone trigger) | 14 | 6.09 | +0.778 |
| 12 | H4 POOL Z_PP_at & dd1=0 & loc=PDH & macdh=-1 → h24 follow | combination (zone trigger) | 15 | 6.03 | +4.561 |
| 13 | H1 GBPJPY Z_PP_rej & dh4=0 & dd1=1 & stz=0 → h24 fade | combination (zone trigger) | 9 | 5.92 | +3.807 |
| 14 | H1 GBPUSD Z_SWH_at & e200=-1 → h4 fade | combination (zone trigger) | 11 | 5.82 | +1.124 |
| 15 | H1 USDCAD Z_S1_rej & e200=1 & stz=0 → br fade | combination (zone trigger) | 14 | 5.80 | +0.759 |
| 16 | H1 GBPUSD Z_SWH_at & e200=-1 & macdt=1 → h4 fade | combination (zone trigger) | 9 | 5.67 | +1.344 |
| 17 | H1 POOL Z_PDH_rej & dh4=-1 & dd1=1 & macdh=1 → br follow | combination (zone trigger) | 22 | 5.65 | +0.839 |
| 18 | H1 USDCHF T_a_any & macdh=-1 → tt fade | combination (trendline trigger) | 8 | 5.61 | +2.143 |
| 19 | H4 EURJPY I_cloud → h24 fade | indicator | 118 | 5.50 | +5.625 |
| 20 | H1 POOL Z_ASL_at & dd1=-1 & loc=SWL & rsi50=1 → h12 fade | combination (zone trigger) | 16 | 5.47 | +1.409 |

Confirmation on the other 203 pool months (2026-11-04T03:06:12+00:00); running test count (v1+v2) = 140

| # | candidate | N | mean pips | mean R | t trades | t daily | gross R | 2x-cost R | blocks + | pairs + | verdict | context |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H1 GBPUSD Z_SWH_at & e200=-1 & macdt=1 → h12 fade | 1325 | +1.95 | +0.063 | 1.23 | 1.23 | +0.079 | +0.046 | 3/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.080R t-2.4 |
| 2 | H1 GBPUSD Z_SWH_at & e200=-1 → h12 fade | 1755 | +1.42 | +0.040 | 0.91 | 0.90 | +0.057 | +0.024 | 4/4 | other pairs 4/16 | **limited** | same rule other 16 pairs pooled -0.058R t-2.2 |
| 3 | H1 GBPUSD Z_SWH_at & e200=-1 & stz=0 → h12 fade | 1493 | +0.93 | +0.021 | 0.42 | 0.42 | +0.037 | +0.004 | 3/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.058R t-2.0 |
| 4 | H4 POOL I_cloud → h24 fade | 18180 | -0.28 | -0.040 | -0.79 | -0.70 | -0.016 | -0.064 | 1/4 | 6/17 | **limited** | USDCHF +0.266R, EURGBP +0.149R, EURJPY +0.090R, USDCAD +0.072R |
| 5 | H4 POOL I_ema200 → h24 fade | 18491 | +1.02 | -0.001 | -0.01 | -0.01 | +0.023 | -0.024 | 1/4 | 8/17 | **limited** | GBPCHF +0.219R, EURGBP +0.216R, USDCHF +0.198R, GBPUSD +0.171R |
| 6 | H4 GBPUSD I_cloud → h24 fade | 1104 | +0.45 | +0.012 | 0.07 | 0.07 | +0.029 | -0.005 | 1/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.043R t-0.8 |
| 7 | H1 POOL Z_R1_at & dd1=1 & e200=-1 & rsiz=1 → h12 fade | 93 | +8.86 | +0.189 | 1.06 | 1.06 | +0.215 | +0.163 | 3/4 | 0/0 | **limited** |  |
| 8 | H1 GBPJPY Z_SWH_at & dh4=1 & e200=1 & macdt=1 → br follow | 1424 | -0.93 | -0.011 | -0.45 | -0.44 | +0.002 | -0.025 | 2/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.030R t-4.4 |
| 9 | H1 EURGBP Z_PWL_at → br fade | 948 | -0.52 | -0.035 | -1.08 | -1.09 | +0.003 | -0.074 | 1/4 | other pairs 1/16 | **limited** | same rule other 16 pairs pooled -0.061R t-7.1 |
| 10 | H1 USDJPY Z_SWL_at & e200=-1 & loc=ASL → h12 fade | 804 | +3.35 | +0.130 | 1.81 | 1.80 | +0.155 | +0.104 | 3/4 | other pairs 7/16 | **limited** | same rule other 16 pairs pooled -0.015R t-1.0 |
| 11 | H1 USDCHF Z_ASH_at & dd1=0 & macdt=-1 → br follow | 623 | -1.44 | -0.059 | -1.63 | -1.61 | -0.035 | -0.084 | 1/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.018R t-1.8 |
| 12 | H4 POOL Z_PP_at & dd1=0 & loc=PDH & macdh=-1 → h24 follow | 83 | +3.40 | -0.192 | -0.32 | -0.30 | -0.170 | -0.213 | 2/4 | 0/0 | **limited** |  |
| 13 | H1 GBPJPY Z_PP_rej & dh4=0 & dd1=1 & stz=0 → h24 fade | 408 | +0.80 | +0.012 | 0.08 | 0.08 | +0.026 | -0.002 | 2/4 | other pairs 9/16 | **limited** | same rule other 16 pairs pooled +0.013R t0.4 |
| 14 | H1 GBPUSD Z_SWH_at & e200=-1 → h4 fade | 3212 | +0.15 | +0.006 | 0.29 | 0.28 | +0.022 | -0.011 | 2/4 | other pairs 1/16 | **limited** | same rule other 16 pairs pooled -0.047R t-3.8 |
| 15 | H1 USDCAD Z_S1_rej & e200=1 & stz=0 → br fade | 390 | -0.63 | -0.066 | -1.28 | -1.31 | -0.043 | -0.090 | 2/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.038R t-3.3 |
| 16 | H1 GBPUSD Z_SWH_at & e200=-1 & macdt=1 → h4 fade | 1987 | +0.59 | +0.021 | 0.89 | 0.89 | +0.038 | +0.005 | 3/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.065R t-3.4 |
| 17 | H1 POOL Z_PDH_rej & dh4=-1 & dd1=1 & macdh=1 → br follow | 3521 | -0.97 | -0.047 | -2.84 | -2.71 | -0.023 | -0.071 | 0/4 | 4/17 | **limited** | GBPUSD +0.116R, AUDJPY +0.051R, GBPCHF +0.040R, CADJPY +0.027R |
| 18 | H1 USDCHF T_a_any & macdh=-1 → tt fade | 1028 | +0.39 | -0.005 | -0.08 | -0.08 | +0.020 | -0.030 | 2/4 | other pairs 9/16 | **limited** | same rule other 16 pairs pooled -0.006R t-0.4 |
| 19 | H4 EURJPY I_cloud → h24 fade | 1098 | +3.57 | +0.090 | 0.56 | 0.56 | +0.108 | +0.072 | 3/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.048R t-0.9 |
| 20 | H1 POOL Z_ASL_at & dd1=-1 & loc=SWL & rsi50=1 → h12 fade | 1357 | -0.45 | -0.021 | -0.40 | -0.38 | +0.005 | -0.047 | 2/4 | 7/17 | **limited** | AUDJPY +0.224R, USDCHF +0.206R, EURGBP +0.137R, AUDUSD +0.109R |

Month result: 0 CONFIRMED, 20 limited.

## v2 Month 7: 2006-06  (discovery 2026-11-04T03:06:39+00:00; 8027 candidate rows with >=8 events and in-month t>2.5 [v2] or any t [v1])

| # | candidate | family | events | in-month t | in-month mean net R |
|---|---|---|---|---|---|
| 1 | H1 EURAUD Z_PDL_rej & e200=-1 → h12 follow | combination (zone trigger) | 11 | 7.78 | +2.816 |
| 2 | H1 EURAUD Z_PDL_rej & e200=-1 → br follow | combination (zone trigger) | 11 | 6.84 | +1.248 |
| 3 | H1 GBPCHF Z_SWH_rej & dd1=0 & e200=1 & macdt=1 → br follow | combination (zone trigger) | 20 | 6.50 | +0.730 |
| 4 | H1 GBPJPY Z_SWL_at & e200=1 & macdh=-1 → br follow | combination (zone trigger) | 31 | 6.39 | +0.621 |
| 5 | H1 EURJPY Z_ASH_rej & dh4=0 & e200=1 & rsiz=2 → br fade | combination (zone trigger) | 15 | 6.21 | +0.840 |
| 6 | H1 GBPCHF Z_PWH_rej & macdh=-1 → br follow | combination (zone trigger) | 15 | 6.19 | +0.917 |
| 7 | H1 USDJPY Z_SWH_at & dd1=0 & loc=PP & macdh=1 → h12 fade | combination (zone trigger) | 9 | 6.12 | +2.010 |
| 8 | H1 USDJPY Z_PP_at & dd1=0 & loc=SWH & macdh=1 → h12 fade | combination (zone trigger) | 9 | 6.12 | +2.010 |
| 9 | H1 EURAUD Z_PDL_rej & dh4=0 & e200=-1 & rsi50=-1 → h12 follow | combination (zone trigger) | 8 | 5.89 | +2.724 |
| 10 | H1 GBPJPY Z_SWL_at & e200=1 → br follow | combination (zone trigger) | 53 | 5.72 | +0.603 |
| 11 | H4 POOL Z_PDH_at & dd1=-1 & e200=-1 & stz=0 → br follow | combination (zone trigger) | 23 | 5.65 | +1.394 |
| 12 | H1 EURJPY Z_ASH_rej & dh4=0 & e200=1 & loc=SWH → br fade | combination (zone trigger) | 11 | 5.61 | +0.897 |
| 13 | H1 EURJPY Z_ASH_rej & dh4=0 & e200=1 & stz=0 → br fade | combination (zone trigger) | 9 | 5.56 | +1.087 |
| 14 | H1 USDCAD Z_SWL_rej & e200=1 & stz=-1 → h24 fade | combination (zone trigger) | 8 | 5.54 | +2.920 |
| 15 | H1 USDCAD Z_SWL_rej & e200=1 & stz=-1 → h12 fade | combination (zone trigger) | 8 | 5.53 | +2.472 |
| 16 | H1 EURAUD Z_PDL_rej & e200=-1 & rsiz=1 → h12 follow | combination (zone trigger) | 8 | 5.51 | +2.805 |
| 17 | H1 EURAUD Z_PDL_rej & e200=-1 & rsiz=1 → br follow | combination (zone trigger) | 8 | 5.48 | +1.262 |
| 18 | H1 EURAUD Z_PDL_rej & dh4=0 & e200=-1 & rsi50=-1 → br follow | combination (zone trigger) | 8 | 5.45 | +1.183 |
| 19 | H1 GBPCHF Z_PP_rej & dd1=0 & loc=PP & macdt=-1 → br follow | combination (zone trigger) | 10 | 5.42 | +1.440 |
| 20 | H1 GBPCHF Z_SWH_at & dd1=0 & e200=-1 & rsi50=1 → br follow | combination (zone trigger) | 21 | 5.42 | +0.785 |

Confirmation on the other 203 pool months (2026-11-04T03:06:42+00:00); running test count (v1+v2) = 160

| # | candidate | N | mean pips | mean R | t trades | t daily | gross R | 2x-cost R | blocks + | pairs + | verdict | context |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H1 EURAUD Z_PDL_rej & e200=-1 → h12 follow | 1794 | -1.33 | -0.007 | -0.18 | -0.18 | +0.008 | -0.023 | 2/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.081R t-2.8 |
| 2 | H1 EURAUD Z_PDL_rej & e200=-1 → br follow | 2549 | -0.74 | -0.029 | -1.50 | -1.48 | -0.013 | -0.045 | 1/4 | other pairs 1/16 | **limited** | same rule other 16 pairs pooled -0.045R t-8.0 |
| 3 | H1 GBPCHF Z_SWH_rej & dd1=0 & e200=1 & macdt=1 → br follow | 1199 | -1.73 | -0.063 | -2.27 | -2.27 | -0.046 | -0.079 | 1/4 | other pairs 1/16 | **limited** | same rule other 16 pairs pooled -0.046R t-6.0 |
| 4 | H1 GBPJPY Z_SWL_at & e200=1 & macdh=-1 → br follow | 1989 | -0.62 | -0.003 | -0.15 | -0.14 | +0.010 | -0.017 | 1/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.023R t-3.9 |
| 5 | H1 EURJPY Z_ASH_rej & dh4=0 & e200=1 & rsiz=2 → br fade | 952 | -1.50 | -0.045 | -1.47 | -1.45 | -0.026 | -0.064 | 1/4 | other pairs 4/16 | **limited** | same rule other 16 pairs pooled -0.024R t-3.0 |
| 6 | H1 GBPCHF Z_PWH_rej & macdh=-1 → br follow | 723 | -0.23 | +0.016 | 0.44 | 0.44 | +0.034 | -0.001 | 2/4 | other pairs 2/16 | **limited** | same rule other 16 pairs pooled -0.059R t-6.0 |
| 7 | H1 USDJPY Z_SWH_at & dd1=0 & loc=PP & macdh=1 → h12 fade | 228 | +0.29 | -0.002 | -0.02 | -0.02 | +0.025 | -0.030 | 3/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.061R t-2.1 |
| 8 | H1 USDJPY Z_PP_at & dd1=0 & loc=SWH & macdh=1 → h12 fade | 228 | +0.30 | -0.021 | -0.18 | -0.18 | +0.007 | -0.048 | 2/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.056R t-1.9 |
| 9 | H1 EURAUD Z_PDL_rej & dh4=0 & e200=-1 & rsi50=-1 → h12 follow | 720 | -1.66 | -0.026 | -0.41 | -0.40 | -0.010 | -0.042 | 1/4 | other pairs 2/16 | **limited** | same rule other 16 pairs pooled -0.080R t-4.0 |
| 10 | H1 GBPJPY Z_SWL_at & e200=1 → br follow | 2880 | -0.63 | -0.005 | -0.30 | -0.30 | +0.008 | -0.019 | 2/4 | other pairs 4/16 | **limited** | same rule other 16 pairs pooled -0.019R t-4.0 |
| 11 | H4 POOL Z_PDH_at & dd1=-1 & e200=-1 & stz=0 → br follow | 3261 | +2.24 | +0.057 | 1.64 | 1.47 | +0.081 | +0.032 | 2/4 | 11/17 | **limited** | USDCHF +0.374R, AUDJPY +0.342R, GBPJPY +0.207R, EURCHF +0.202R |
| 12 | H1 EURJPY Z_ASH_rej & dh4=0 & e200=1 & loc=SWH → br fade | 513 | -0.06 | -0.014 | -0.33 | -0.34 | +0.004 | -0.032 | 2/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.021R t-2.0 |
| 13 | H1 EURJPY Z_ASH_rej & dh4=0 & e200=1 & stz=0 → br fade | 815 | -2.24 | -0.079 | -2.41 | -2.41 | -0.060 | -0.098 | 0/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.019R t-2.2 |
| 14 | H1 USDCAD Z_SWL_rej & e200=1 & stz=-1 → h24 fade | 436 | -0.39 | +0.067 | 0.52 | 0.52 | +0.090 | +0.043 | 3/4 | other pairs 14/16 | **limited** | same rule other 16 pairs pooled +0.069R t2.1 |
| 15 | H1 USDCAD Z_SWL_rej & e200=1 & stz=-1 → h12 fade | 488 | -0.48 | +0.015 | 0.18 | 0.18 | +0.039 | -0.008 | 2/4 | other pairs 13/16 | **limited** | same rule other 16 pairs pooled +0.029R t1.3 |
| 16 | H1 EURAUD Z_PDL_rej & e200=-1 & rsiz=1 → h12 follow | 1630 | -1.37 | -0.004 | -0.09 | -0.09 | +0.012 | -0.020 | 1/4 | other pairs 4/16 | **limited** | same rule other 16 pairs pooled -0.080R t-2.6 |
| 17 | H1 EURAUD Z_PDL_rej & e200=-1 & rsiz=1 → br follow | 2220 | -0.99 | -0.034 | -1.65 | -1.63 | -0.019 | -0.050 | 1/4 | other pairs 1/16 | **limited** | same rule other 16 pairs pooled -0.041R t-6.8 |
| 18 | H1 EURAUD Z_PDL_rej & dh4=0 & e200=-1 & rsi50=-1 → br follow | 973 | -1.23 | -0.027 | -0.88 | -0.87 | -0.011 | -0.043 | 1/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.048R t-5.3 |
| 19 | H1 GBPCHF Z_PP_rej & dd1=0 & loc=PP & macdt=-1 → br follow | 598 | -2.67 | -0.053 | -1.23 | -1.24 | -0.036 | -0.069 | 0/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.030R t-2.9 |
| 20 | H1 GBPCHF Z_SWH_at & dd1=0 & e200=-1 & rsi50=1 → br follow | 612 | -0.83 | -0.030 | -0.73 | -0.72 | -0.013 | -0.046 | 2/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.020R t-2.0 |

Month result: 0 CONFIRMED, 20 limited.

## v2 Month 8: 2012-02  (discovery 2026-11-04T03:07:10+00:00; 10080 candidate rows with >=8 events and in-month t>2.5 [v2] or any t [v1])

| # | candidate | family | events | in-month t | in-month mean net R |
|---|---|---|---|---|---|
| 1 | H4 CADJPY I_bb_uh → h24 follow | indicator | 90 | 9.58 | +5.520 |
| 2 | H4 CADJPY I_rsi_30_50 → h24 fade | indicator | 17 | 7.90 | +6.675 |
| 3 | H1 GBPJPY I_rsi_30_50 → h12 fade | indicator | 152 | 7.11 | +1.210 |
| 4 | H4 CADJPY I_rsi_50_70 → h24 follow | indicator | 80 | 6.99 | +6.222 |
| 5 | H4 CADJPY I_ema200 → h24 follow | indicator | 126 | 6.93 | +5.545 |
| 6 | H4 NZDJPY I_bb_lh → br fade | indicator | 17 | 6.56 | +2.699 |
| 7 | H4 USDJPY I_bb_lh → h24 fade | indicator | 23 | 6.42 | +6.783 |
| 8 | H1 AUDUSD Z_ASH_rej & dh4=-1 & stz=0 → br follow | combination (zone trigger) | 11 | 6.35 | +1.162 |
| 9 | H4 GBPJPY I_ema200 → h24 follow | indicator | 126 | 6.21 | +5.740 |
| 10 | H4 GBPJPY I_rsi_50_70 → h24 follow | indicator | 92 | 6.09 | +6.483 |
| 11 | H4 GBPJPY I_bb_uh → h24 follow | indicator | 89 | 6.06 | +5.915 |
| 12 | H4 AUDNZD Z_SWH_rej & dd1=1 & loc=SWL → br follow | combination (zone trigger) | 10 | 5.96 | +2.664 |
| 13 | H1 AUDNZD Z_SWL_rej & loc=SWL & macdh=1 → br follow | combination (zone trigger) | 30 | 5.92 | +0.627 |
| 14 | H4 CADJPY I_bb_uh → h12 follow | indicator | 90 | 5.91 | +3.481 |
| 15 | H1 AUDUSD Z_ASH_rej & dh4=-1 & dd1=1 & stz=0 → br follow | combination (zone trigger) | 9 | 5.91 | +1.143 |
| 16 | H4 CADJPY I_bb_lh → br fade | indicator | 16 | 5.88 | +2.175 |
| 17 | H1 POOL Z_PDH_at & dd1=1 & rsiz=3 → br fade | combination (zone trigger) | 10 | 5.81 | +1.010 |
| 18 | H1 POOL Z_PWH_rej & dh4=1 & rsiz=1 → h24 follow | combination (zone trigger) | 20 | 5.78 | +2.393 |
| 19 | H4 CADJPY I_rsi_30_50 → h12 fade | indicator | 17 | 5.77 | +3.850 |
| 20 | H1 NZDJPY Z_SWL_rej & loc=SWL & stz=-1 → h24 follow | combination (zone trigger) | 8 | 5.77 | +5.115 |

Confirmation on the other 203 pool months (2026-11-04T03:07:16+00:00); running test count (v1+v2) = 180

| # | candidate | N | mean pips | mean R | t trades | t daily | gross R | 2x-cost R | blocks + | pairs + | verdict | context |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H4 CADJPY I_bb_uh → h24 follow | 803 | -2.99 | -0.016 | -0.09 | -0.09 | +0.006 | -0.038 | 2/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.114R t-1.9 |
| 2 | H4 CADJPY I_rsi_30_50 → h24 fade | 737 | -8.81 | -0.225 | -1.12 | -1.12 | -0.203 | -0.247 | 0/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.108R t-1.7 |
| 3 | H1 GBPJPY I_rsi_30_50 → h12 fade | 5749 | -1.97 | -0.040 | -1.57 | -1.54 | -0.027 | -0.053 | 0/4 | other pairs 1/16 | **limited** | same rule other 16 pairs pooled -0.028R t-4.4 |
| 4 | H4 CADJPY I_rsi_50_70 → h24 follow | 769 | -3.21 | -0.003 | -0.01 | -0.01 | +0.020 | -0.025 | 2/4 | other pairs 7/16 | **limited** | same rule other 16 pairs pooled -0.038R t-0.8 |
| 5 | H4 CADJPY I_ema200 → h24 follow | 973 | -2.97 | -0.114 | -0.69 | -0.69 | -0.092 | -0.136 | 2/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.052R t-0.9 |
| 6 | H4 NZDJPY I_bb_lh → br fade | 2669 | -0.50 | -0.052 | -1.30 | -1.27 | -0.029 | -0.075 | 1/4 | other pairs 1/16 | **limited** | same rule other 16 pairs pooled -0.060R t-6.7 |
| 7 | H4 USDJPY I_bb_lh → h24 fade | 897 | +1.00 | +0.093 | 0.50 | 0.50 | +0.118 | +0.067 | 2/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.092R t-1.6 |
| 8 | H1 AUDUSD Z_ASH_rej & dh4=-1 & stz=0 → br follow | 1041 | -0.43 | -0.008 | -0.27 | -0.26 | +0.017 | -0.034 | 2/4 | other pairs 1/16 | **limited** | same rule other 16 pairs pooled -0.054R t-7.6 |
| 9 | H4 GBPJPY I_ema200 → h24 follow | 1121 | -1.07 | -0.065 | -0.40 | -0.40 | -0.052 | -0.079 | 1/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.055R t-1.0 |
| 10 | H4 GBPJPY I_rsi_50_70 → h24 follow | 873 | +0.38 | +0.188 | 1.06 | 1.06 | +0.202 | +0.175 | 3/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.051R t-1.1 |
| 11 | H4 GBPJPY I_bb_uh → h24 follow | 925 | -3.78 | +0.058 | 0.33 | 0.33 | +0.072 | +0.045 | 3/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.120R t-2.0 |
| 12 | H4 AUDNZD Z_SWH_rej & dd1=1 & loc=SWL → br follow | 102 | -1.10 | +0.094 | 0.45 | 0.47 | +0.119 | +0.069 | 2/4 | other pairs 8/16 | **limited** | same rule other 16 pairs pooled -0.069R t-1.6 |
| 13 | H1 AUDNZD Z_SWL_rej & loc=SWL & macdh=1 → br follow | 1935 | -1.98 | -0.080 | -3.13 | -3.09 | -0.054 | -0.107 | 0/4 | other pairs 2/16 | **limited** | same rule other 16 pairs pooled -0.028R t-4.9 |
| 14 | H4 CADJPY I_bb_uh → h12 follow | 1392 | +1.46 | +0.081 | 0.85 | 0.85 | +0.103 | +0.059 | 2/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.069R t-1.8 |
| 15 | H1 AUDUSD Z_ASH_rej & dh4=-1 & dd1=1 & stz=0 → br follow | 345 | -1.24 | -0.041 | -0.76 | -0.76 | -0.015 | -0.068 | 0/4 | other pairs 1/16 | **limited** | same rule other 16 pairs pooled -0.069R t-5.5 |
| 16 | H4 CADJPY I_bb_lh → br fade | 2743 | -2.39 | -0.109 | -2.90 | -2.84 | -0.087 | -0.131 | 0/4 | other pairs 1/16 | **limited** | same rule other 16 pairs pooled -0.057R t-6.3 |
| 17 | H1 POOL Z_PDH_at & dd1=1 & rsiz=3 → br fade | 1047 | -0.56 | -0.020 | -0.66 | -0.64 | +0.004 | -0.043 | 2/4 | 8/17 | **limited** | EURGBP +0.204R, USDCAD +0.162R, NZDUSD +0.154R, NZDJPY +0.142R |
| 18 | H1 POOL Z_PWH_rej & dh4=1 & rsiz=1 → h24 follow | 2367 | -2.31 | -0.076 | -1.35 | -1.17 | -0.052 | -0.100 | 1/4 | 6/17 | **limited** | EURAUD +0.532R, EURCHF +0.229R, AUDNZD +0.197R, EURGBP +0.169R |
| 19 | H4 CADJPY I_rsi_30_50 → h12 fade | 1262 | -4.55 | -0.134 | -1.27 | -1.27 | -0.112 | -0.156 | 0/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.082R t-2.5 |
| 20 | H1 NZDJPY Z_SWL_rej & loc=SWL & stz=-1 → h24 follow | 767 | -3.73 | -0.109 | -1.15 | -1.15 | -0.085 | -0.133 | 1/4 | other pairs 1/16 | **limited** | same rule other 16 pairs pooled -0.084R t-3.8 |

Month result: 0 CONFIRMED, 20 limited.

## v2 Month 9: 2006-08  (discovery 2026-11-04T03:07:44+00:00; 8650 candidate rows with >=8 events and in-month t>2.5 [v2] or any t [v1])

| # | candidate | family | events | in-month t | in-month mean net R |
|---|---|---|---|---|---|
| 1 | H1 GBPCHF Z_SWL_at & dd1=0 → br follow | combination (zone trigger) | 21 | 7.15 | +0.683 |
| 2 | H1 EURJPY Z_ASL_rej & dh4=1 & dd1=1 & stz=0 → br fade | combination (zone trigger) | 10 | 6.88 | +1.183 |
| 3 | H4 POOL Z_PWL_rej & e200=1 & macdh=1 → br follow | combination (zone trigger) | 9 | 6.25 | +2.626 |
| 4 | H1 GBPCHF Z_SWL_at & dh4=1 & macdh=-1 → br follow | combination (zone trigger) | 29 | 6.25 | +0.535 |
| 5 | H4 POOL Z_PWL_rej & e200=1 & macdh=1 → h24 follow | combination (zone trigger) | 9 | 6.21 | +6.197 |
| 6 | H1 EURJPY Z_ASL_rej & dh4=1 & dd1=1 & macdh=-1 → br fade | combination (zone trigger) | 9 | 6.13 | +1.171 |
| 7 | H1 GBPCHF Z_SWL_at & dd1=0 & macdh=-1 → br follow | combination (zone trigger) | 15 | 5.96 | +0.690 |
| 8 | H1 GBPCHF Z_SWL_at & dh4=1 → br follow | combination (zone trigger) | 30 | 5.89 | +0.483 |
| 9 | H1 EURAUD Z_SWL_at & e200=-1 & loc=ASL & rsiz=1 → h4 follow | combination (zone trigger) | 12 | 5.77 | +0.927 |
| 10 | H1 GBPJPY Z_SWL_rej & dh4=-1 & rsi50=-1 → h24 fade | combination (zone trigger) | 11 | 5.60 | +2.393 |
| 11 | H1 POOL Z_R1_rej & dh4=1 & dd1=-1 & macdt=-1 → h4 fade | combination (zone trigger) | 12 | 5.58 | +1.259 |
| 12 | H1 GBPUSD Z_ASH_at & macdh=1 → br fade | combination (zone trigger) | 31 | 5.56 | +0.554 |
| 13 | H4 GBPJPY I_bb_below → h24 fade | indicator | 9 | 5.46 | +4.680 |
| 14 | H4 POOL I_rsi_30_50 → h24 fade | indicator | 741 | 5.45 | +1.669 |
| 15 | H1 GBPCHF Z_SWL_at & dd1=0 & rsiz=1 → br follow | combination (zone trigger) | 16 | 5.42 | +0.759 |
| 16 | H4 POOL Z_PP_rej & loc=PWH & stz=0 → h12 fade | combination (zone trigger) | 21 | 5.40 | +3.677 |
| 17 | H1 EURUSD Z_SWL_at & e200=-1 & stz=0 → h12 follow | combination (zone trigger) | 22 | 5.39 | +1.201 |
| 18 | H1 POOL Z_SWL_at & dd1=1 & e200=-1 & rsi50=-1 → h12 follow | combination (zone trigger) | 265 | 5.35 | +0.361 |
| 19 | H1 POOL Z_PDL_rej & e200=-1 & loc=SWH & macdh=1 → br follow | combination (zone trigger) | 9 | 5.33 | +1.190 |
| 20 | H1 GBPCHF Z_PP_rej & dd1=1 & loc=SWL → br follow | combination (zone trigger) | 9 | 5.32 | +1.028 |

Confirmation on the other 203 pool months (2026-11-04T03:07:48+00:00); running test count (v1+v2) = 200

| # | candidate | N | mean pips | mean R | t trades | t daily | gross R | 2x-cost R | blocks + | pairs + | verdict | context |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H1 GBPCHF Z_SWL_at & dd1=0 → br follow | 2649 | +0.31 | +0.010 | 0.52 | 0.52 | +0.027 | -0.007 | 2/4 | other pairs 4/16 | **limited** | same rule other 16 pairs pooled -0.015R t-3.1 |
| 2 | H1 EURJPY Z_ASL_rej & dh4=1 & dd1=1 & stz=0 → br fade | 368 | -0.23 | -0.018 | -0.32 | -0.32 | +0.001 | -0.037 | 1/4 | other pairs 7/16 | **limited** | same rule other 16 pairs pooled -0.014R t-1.1 |
| 3 | H4 POOL Z_PWL_rej & e200=1 & macdh=1 → br follow | 663 | -2.46 | -0.108 | -1.41 | -1.33 | -0.084 | -0.131 | 1/4 | 7/17 | **limited** | AUDUSD +0.417R, USDCAD +0.377R, EURJPY +0.214R, NZDUSD +0.183R |
| 4 | H1 GBPCHF Z_SWL_at & dh4=1 & macdh=-1 → br follow | 1836 | -0.78 | -0.020 | -0.86 | -0.85 | -0.003 | -0.037 | 1/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.027R t-4.3 |
| 5 | H4 POOL Z_PWL_rej & e200=1 & macdh=1 → h24 follow | 518 | -7.53 | -0.368 | -1.70 | -1.62 | -0.345 | -0.392 | 1/4 | 4/17 | **limited** | EURAUD +0.673R, USDCAD +0.538R, USDJPY +0.460R, EURGBP +0.401R |
| 6 | H1 EURJPY Z_ASL_rej & dh4=1 & dd1=1 & macdh=-1 → br fade | 420 | -0.12 | +0.010 | 0.20 | 0.20 | +0.029 | -0.009 | 2/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.015R t-1.3 |
| 7 | H1 GBPCHF Z_SWL_at & dd1=0 & macdh=-1 → br follow | 1805 | -0.82 | -0.020 | -0.87 | -0.86 | -0.003 | -0.037 | 1/4 | other pairs 4/16 | **limited** | same rule other 16 pairs pooled -0.022R t-3.5 |
| 8 | H1 GBPCHF Z_SWL_at & dh4=1 → br follow | 2136 | -1.02 | -0.024 | -1.12 | -1.13 | -0.007 | -0.041 | 1/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.025R t-4.4 |
| 9 | H1 EURAUD Z_SWL_at & e200=-1 & loc=ASL & rsiz=1 → h4 follow | 1643 | -0.44 | -0.035 | -1.42 | -1.42 | -0.019 | -0.051 | 2/4 | other pairs 1/16 | **limited** | same rule other 16 pairs pooled -0.053R t-6.5 |
| 10 | H1 GBPJPY Z_SWL_rej & dh4=-1 & rsi50=-1 → h24 fade | 844 | -3.30 | -0.059 | -0.61 | -0.61 | -0.046 | -0.073 | 1/4 | other pairs 8/16 | **limited** | same rule other 16 pairs pooled -0.014R t-0.6 |
| 11 | H1 POOL Z_R1_rej & dh4=1 & dd1=-1 & macdt=-1 → h4 fade | 2398 | +0.74 | +0.020 | 0.84 | 0.79 | +0.044 | -0.005 | 2/4 | 10/17 | **limited** | USDCAD +0.218R, GBPJPY +0.151R, NZDUSD +0.066R, USDCHF +0.055R |
| 12 | H1 GBPUSD Z_ASH_at & macdh=1 → br fade | 2614 | -0.18 | -0.005 | -0.30 | -0.29 | +0.011 | -0.022 | 2/4 | other pairs 0/16 | **limited** | same rule other 16 pairs pooled -0.047R t-9.9 |
| 13 | H4 GBPJPY I_bb_below → h24 fade | 489 | -12.59 | -0.109 | -0.40 | -0.40 | -0.096 | -0.123 | 2/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.149R t-2.4 |
| 14 | H4 POOL I_rsi_30_50 → h24 fade | 14271 | -2.42 | -0.113 | -1.87 | -1.55 | -0.089 | -0.137 | 0/4 | 5/17 | **limited** | EURGBP +0.094R, EURJPY +0.091R, USDCAD +0.087R, GBPJPY +0.033R |
| 15 | H1 GBPCHF Z_SWL_at & dd1=0 & rsiz=1 → br follow | 1948 | -0.60 | -0.025 | -1.10 | -1.11 | -0.008 | -0.042 | 1/4 | other pairs 2/16 | **limited** | same rule other 16 pairs pooled -0.014R t-2.3 |
| 16 | H4 POOL Z_PP_rej & loc=PWH & stz=0 → h12 fade | 1721 | -4.28 | -0.130 | -1.27 | -1.25 | -0.105 | -0.154 | 1/4 | 4/17 | **limited** | USDCHF +0.955R, NZDUSD +0.892R, USDJPY +0.418R, EURAUD +0.076R |
| 17 | H1 EURUSD Z_SWL_at & e200=-1 & stz=0 → h12 follow | 2112 | -1.17 | -0.056 | -1.29 | -1.29 | -0.034 | -0.078 | 0/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.018R t-0.8 |
| 18 | H1 POOL Z_SWL_at & dd1=1 & e200=-1 & rsi50=-1 → h12 follow | 10065 | -1.31 | -0.049 | -2.57 | -2.38 | -0.024 | -0.073 | 0/4 | 6/17 | **limited** | AUDNZD +0.059R, NZDJPY +0.041R, EURJPY +0.035R, AUDUSD +0.023R |
| 19 | H1 POOL Z_PDL_rej & e200=-1 & loc=SWH & macdh=1 → br follow | 1021 | -2.10 | -0.089 | -2.68 | -2.65 | -0.064 | -0.114 | 0/4 | 6/17 | **limited** | NZDJPY +0.137R, AUDUSD +0.115R, GBPUSD +0.080R, EURUSD +0.039R |
| 20 | H1 GBPCHF Z_PP_rej & dd1=1 & loc=SWL → br follow | 557 | -3.62 | -0.117 | -2.91 | -2.78 | -0.099 | -0.134 | 0/4 | other pairs 2/16 | **limited** | same rule other 16 pairs pooled -0.047R t-4.3 |

Month result: 0 CONFIRMED, 20 limited.

## v2 Month 10: 2016-08  (discovery 2026-11-04T03:08:15+00:00; 9445 candidate rows with >=8 events and in-month t>2.5 [v2] or any t [v1])

| # | candidate | family | events | in-month t | in-month mean net R |
|---|---|---|---|---|---|
| 1 | H1 AUDUSD I_rsi_gt70 → h12 fade | indicator | 15 | 7.26 | +1.920 |
| 2 | H1 EURGBP Z_PDL_at & dd1=0 & e200=-1 & macdt=1 → h12 fade | combination (zone trigger) | 8 | 7.06 | +2.270 |
| 3 | H1 USDCHF Z_PP_rej & dd1=-1 & e200=1 & macdh=-1 → br fade | combination (zone trigger) | 12 | 6.91 | +0.942 |
| 4 | H1 AUDUSD I_rsi_gt70 → h24 fade | indicator | 15 | 6.76 | +2.481 |
| 5 | M15 EURAUD T_a_e4 & dd1=0 & e200=1 & macdt=-1 → tb fade | combination (trendline trigger) | 9 | 6.36 | +1.164 |
| 6 | H1 USDCHF Z_PP_rej & e200=1 & macdh=-1 → br fade | combination (zone trigger) | 14 | 6.35 | +0.919 |
| 7 | H1 EURAUD Z_SWL_at & dh4=-1 & dd1=-1 & loc=SWL → br fade | combination (zone trigger) | 12 | 6.35 | +0.912 |
| 8 | H1 EURGBP Z_PDL_at & dd1=0 & e200=-1 & macdt=1 → h24 fade | combination (zone trigger) | 8 | 5.86 | +2.533 |
| 9 | H1 EURCHF C_maru & macdt=-1 → br fade | combination (candle trigger) | 20 | 5.51 | +1.015 |
| 10 | H1 NZDUSD Z_SWH_rej & dh4=-1 & dd1=0 & macdt=-1 → h12 follow | combination (zone trigger) | 11 | 5.49 | +1.283 |
| 11 | H1 NZDJPY Z_SWL_at & dd1=-1 & rsi50=-1 → br follow | combination (zone trigger) | 19 | 5.40 | +0.620 |
| 12 | H1 AUDJPY Z_PDH_rej & dh4=1 & e200=-1 & macdt=-1 → h24 fade | combination (zone trigger) | 11 | 5.39 | +1.956 |
| 13 | H4 POOL Z_PP_rej & dd1=1 & macdh=1 → h24 follow | combination (zone trigger) | 28 | 5.38 | +3.514 |
| 14 | H1 USDCAD Z_SWH_at & dh4=0 & stz=0 → br follow | combination (zone trigger) | 20 | 5.38 | +0.473 |
| 15 | H1 EURAUD Z_SWL_at & dd1=-1 & stz=1 → br fade | combination (zone trigger) | 9 | 5.37 | +0.945 |
| 16 | H1 USDJPY Z_SWH_at & dh4=1 & e200=1 & rsiz=2 → h24 fade | combination (zone trigger) | 10 | 5.31 | +1.835 |
| 17 | H4 EURGBP Z_SWL_rej & macdh=-1 → h24 follow | combination (zone trigger) | 12 | 5.26 | +4.373 |
| 18 | H4 USDJPY I_rsi_gt70 → h12 follow | indicator | 18 | 5.21 | +2.829 |
| 19 | H1 EURAUD C_pin & dd1=-1 & loc=SWL → br follow | combination (candle trigger) | 8 | 5.18 | +1.018 |
| 20 | H4 POOL Z_PWL_rej & loc=SWL & macdh=-1 → br follow | combination (zone trigger) | 24 | 5.18 | +1.416 |

Confirmation on the other 203 pool months (2026-11-04T03:08:18+00:00); running test count (v1+v2) = 220

| # | candidate | N | mean pips | mean R | t trades | t daily | gross R | 2x-cost R | blocks + | pairs + | verdict | context |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H1 AUDUSD I_rsi_gt70 → h12 fade | 1186 | +1.23 | +0.043 | 0.85 | 0.87 | +0.069 | +0.017 | 1/4 | other pairs 8/16 | **limited** | same rule other 16 pairs pooled -0.023R t-1.6 |
| 2 | H1 EURGBP Z_PDL_at & dd1=0 & e200=-1 & macdt=1 → h12 fade | 312 | -0.76 | -0.075 | -0.82 | -0.82 | -0.037 | -0.112 | 1/4 | other pairs 4/16 | **limited** | same rule other 16 pairs pooled -0.058R t-2.1 |
| 3 | H1 USDCHF Z_PP_rej & dd1=-1 & e200=1 & macdh=-1 → br fade | 416 | -1.09 | -0.046 | -1.05 | -1.05 | -0.021 | -0.071 | 1/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.026R t-2.2 |
| 4 | H1 AUDUSD I_rsi_gt70 → h24 fade | 896 | +0.98 | +0.061 | 0.73 | 0.73 | +0.087 | +0.035 | 1/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.032R t-1.4 |
| 5 | M15 EURAUD T_a_e4 & dd1=0 & e200=1 & macdt=-1 → tb fade | 492 | -1.53 | -0.034 | -0.67 | -0.65 | -0.019 | -0.050 | 2/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.022R t-1.9 |
| 6 | H1 USDCHF Z_PP_rej & e200=1 & macdh=-1 → br fade | 1740 | -1.17 | -0.069 | -3.16 | -3.12 | -0.044 | -0.094 | 0/4 | other pairs 2/16 | **limited** | same rule other 16 pairs pooled -0.019R t-3.2 |
| 7 | H1 EURAUD Z_SWL_at & dh4=-1 & dd1=-1 & loc=SWL → br fade | 790 | -2.76 | -0.061 | -1.73 | -1.68 | -0.045 | -0.077 | 2/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.045R t-4.9 |
| 8 | H1 EURGBP Z_PDL_at & dd1=0 & e200=-1 & macdt=1 → h24 fade | 276 | -0.56 | +0.041 | 0.30 | 0.30 | +0.079 | +0.003 | 3/4 | other pairs 4/16 | **limited** | same rule other 16 pairs pooled -0.059R t-1.4 |
| 9 | H1 EURCHF C_maru & macdt=-1 → br fade | 3982 | +1.01 | +0.044 | 2.50 | 2.49 | +0.086 | +0.003 | 4/4 | other pairs 9/16 | **limited** | same rule other 16 pairs pooled +0.002R t0.4 |
| 10 | H1 NZDUSD Z_SWH_rej & dh4=-1 & dd1=0 & macdt=-1 → h12 follow | 290 | -2.85 | -0.206 | -1.83 | -1.83 | -0.180 | -0.232 | 0/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.091R t-3.4 |
| 11 | H1 NZDJPY Z_SWL_at & dd1=-1 & rsi50=-1 → br follow | 1297 | -0.66 | -0.036 | -1.23 | -1.20 | -0.013 | -0.059 | 1/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.027R t-4.2 |
| 12 | H1 AUDJPY Z_PDH_rej & dh4=1 & e200=-1 & macdt=-1 → h24 fade | 55 | +4.33 | +0.126 | 0.39 | 0.39 | +0.146 | +0.105 | 2/4 | other pairs 7/16 | **limited** | same rule other 16 pairs pooled -0.026R t-0.3 |
| 13 | H4 POOL Z_PP_rej & dd1=1 & macdh=1 → h24 follow | 3780 | +1.24 | -0.010 | -0.12 | -0.11 | +0.014 | -0.033 | 2/4 | 7/17 | **limited** | GBPJPY +0.621R, AUDNZD +0.456R, NZDUSD +0.379R, USDJPY +0.202R |
| 14 | H1 USDCAD Z_SWH_at & dh4=0 & stz=0 → br follow | 2552 | +0.09 | -0.004 | -0.20 | -0.20 | +0.020 | -0.028 | 1/4 | other pairs 2/16 | **limited** | same rule other 16 pairs pooled -0.025R t-4.9 |
| 15 | H1 EURAUD Z_SWL_at & dd1=-1 & stz=1 → br fade | 225 | -2.95 | -0.077 | -1.17 | -1.26 | -0.061 | -0.094 | 0/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.064R t-3.9 |
| 16 | H1 USDJPY Z_SWH_at & dh4=1 & e200=1 & rsiz=2 → h24 fade | 712 | +1.53 | +0.142 | 1.48 | 1.48 | +0.168 | +0.116 | 4/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.056R t-2.3 |
| 17 | H4 EURGBP Z_SWL_rej & macdh=-1 → h24 follow | 514 | -8.73 | -0.449 | -2.00 | -2.00 | -0.411 | -0.488 | 1/4 | other pairs 4/16 | **limited** | same rule other 16 pairs pooled -0.060R t-1.0 |
| 18 | H4 USDJPY I_rsi_gt70 → h12 follow | 355 | +5.37 | +0.352 | 1.76 | 1.76 | +0.379 | +0.325 | 3/4 | other pairs 8/16 | **limited** | same rule other 16 pairs pooled -0.025R t-0.4 |
| 19 | H1 EURAUD C_pin & dd1=-1 & loc=SWL → br follow | 552 | -1.07 | -0.055 | -1.32 | -1.29 | -0.040 | -0.071 | 1/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.056R t-5.1 |
| 20 | H4 POOL Z_PWL_rej & loc=SWL & macdh=-1 → br follow | 3650 | -1.18 | -0.048 | -1.48 | -1.43 | -0.022 | -0.073 | 0/4 | 7/17 | **limited** | EURJPY +0.221R, GBPCHF +0.098R, GBPJPY +0.079R, NZDUSD +0.063R |

Month result: 0 CONFIRMED, 20 limited.

## v2 Month 11: 2021-08  (discovery 2026-11-04T03:08:46+00:00; 8937 candidate rows with >=8 events and in-month t>2.5 [v2] or any t [v1])

| # | candidate | family | events | in-month t | in-month mean net R |
|---|---|---|---|---|---|
| 1 | H4 XAUUSD Z_SWL_rej & dd1=1 & loc=SWH → h24 fade | combination (zone trigger) | 10 | 9.91 | +13.735 |
| 2 | H4 XAUUSD Z_SWL_rej & dh4=0 & dd1=1 & stz=0 → h24 fade | combination (zone trigger) | 8 | 9.36 | +17.076 |
| 3 | H4 XAUUSD Z_SWL_rej & dd1=1 & stz=0 → h24 fade | combination (zone trigger) | 9 | 9.35 | +13.962 |
| 4 | H4 GBPCHF I_bbsq → h12 follow | indicator | 13 | 9.05 | +5.694 |
| 5 | H1 NZDUSD Z_ASH_at & dd1=0 & macdt=1 → h24 fade | combination (zone trigger) | 14 | 8.00 | +2.931 |
| 6 | GBPCHF F1_h18 long/follow | time | 23 | 7.12 | +0.349 |
| 7 | H1 NZDUSD Z_ASH_at & dd1=0 → h24 fade | combination (zone trigger) | 18 | 6.76 | +2.278 |
| 8 | H1 NZDUSD Z_ASH_at & dd1=0 & rsiz=2 → h24 fade | combination (zone trigger) | 15 | 6.72 | +2.297 |
| 9 | H1 EURAUD Z_SWL_rej & dd1=0 & stz=0 → h24 follow | combination (zone trigger) | 24 | 6.48 | +1.384 |
| 10 | H4 XAUUSD Z_SWL_at & dh4=0 & dd1=1 & loc=SWL → h24 fade | combination (zone trigger) | 11 | 6.40 | +10.500 |
| 11 | H1 EURAUD Z_SWL_rej & dd1=0 → h24 follow | combination (zone trigger) | 27 | 6.34 | +1.442 |
| 12 | H4 XAUUSD Z_SWL_at & dh4=0 & dd1=1 & stz=0 → h24 fade | combination (zone trigger) | 9 | 6.26 | +12.752 |
| 13 | H1 GBPCHF Z_SWL_rej & loc=SWH & macdh=-1 → br fade | combination (zone trigger) | 14 | 6.23 | +0.937 |
| 14 | H1 POOL T_a_any & e200=-1 & loc=SWL & macdt=1 → tt follow | combination (trendline trigger) | 8 | 6.15 | +1.818 |
| 15 | H1 NZDUSD Z_ASH_at & dd1=0 & macdh=1 → h24 fade | combination (zone trigger) | 17 | 6.10 | +2.297 |
| 16 | H1 POOL Z_SWH_rej & dh4=1 & loc=R1 & macdt=1 → h12 fade | combination (zone trigger) | 12 | 5.95 | +2.217 |
| 17 | H1 POOL Z_S1_at & dh4=1 & loc=SWL & macdt=-1 → br follow | combination (zone trigger) | 21 | 5.87 | +0.790 |
| 18 | H4 GBPCHF I_bbsq → h24 follow | indicator | 13 | 5.65 | +8.638 |
| 19 | H4 GBPCHF I_bbsq → br follow | indicator | 13 | 5.61 | +1.981 |
| 20 | H4 XAUUSD Z_SWL_rej & dd1=1 & macdh=-1 → h24 fade | combination (zone trigger) | 13 | 5.57 | +11.189 |

Confirmation on the other 203 pool months (2026-11-04T03:08:48+00:00); running test count (v1+v2) = 240

| # | candidate | N | mean pips | mean R | t trades | t daily | gross R | 2x-cost R | blocks + | pairs + | verdict | context |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H4 XAUUSD Z_SWL_rej & dd1=1 & loc=SWH → h24 fade | 75 | -795.86 | -1.926 | -3.02 | -3.02 | -1.857 | -1.995 | 0/3 | other pairs 8/17 | **limited** | same rule other 16 pairs pooled -0.070R t-0.5 |
| 2 | H4 XAUUSD Z_SWL_rej & dh4=0 & dd1=1 & stz=0 → h24 fade | 91 | -456.28 | -1.144 | -2.23 | -2.23 | -1.079 | -1.209 | 0/3 | other pairs 8/17 | **limited** | same rule other 16 pairs pooled +0.008R t0.1 |
| 3 | H4 XAUUSD Z_SWL_rej & dd1=1 & stz=0 → h24 fade | 158 | -231.94 | -0.793 | -1.84 | -1.84 | -0.726 | -0.861 | 0/3 | other pairs 9/17 | **limited** | same rule other 16 pairs pooled -0.010R t-0.1 |
| 4 | H4 GBPCHF I_bbsq → h12 follow | 500 | +6.61 | +0.120 | 0.75 | 0.75 | +0.137 | +0.103 | 3/4 | other pairs 9/16 | **limited** | same rule other 16 pairs pooled +0.060R t0.6 |
| 5 | H1 NZDUSD Z_ASH_at & dd1=0 & macdt=1 → h24 fade | 648 | -0.43 | +0.008 | 0.08 | 0.08 | +0.034 | -0.018 | 2/4 | other pairs 11/16 | **limited** | same rule other 16 pairs pooled +0.027R t1.1 |
| 6 | GBPCHF F1_h18 long/follow | 4348 | +0.78 | +0.038 | 7.64 | 7.64 | +0.055 | +0.021 | 2/4 | 10/17 | **limited** | GBPJPY +0.025R t4.0, CADJPY +0.021R t3.3, AUDNZD +0.029R t2.8, h17 nanR tnan, h19 -0.015R t-2.8 |
| 7 | H1 NZDUSD Z_ASH_at & dd1=0 → h24 fade | 780 | +1.31 | +0.051 | 0.58 | 0.58 | +0.077 | +0.025 | 3/4 | other pairs 11/16 | **limited** | same rule other 16 pairs pooled +0.027R t1.2 |
| 8 | H1 NZDUSD Z_ASH_at & dd1=0 & rsiz=2 → h24 fade | 696 | +1.29 | +0.067 | 0.72 | 0.72 | +0.092 | +0.041 | 3/4 | other pairs 10/16 | **limited** | same rule other 16 pairs pooled +0.021R t0.9 |
| 9 | H1 EURAUD Z_SWL_rej & dd1=0 & stz=0 → h24 follow | 1032 | +4.31 | +0.081 | 1.02 | 1.02 | +0.096 | +0.065 | 2/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.047R t-2.2 |
| 10 | H4 XAUUSD Z_SWL_at & dh4=0 & dd1=1 & loc=SWL → h24 fade | 104 | -52.77 | -0.108 | -0.21 | -0.21 | -0.046 | -0.170 | 1/3 | other pairs 7/17 | **limited** | same rule other 16 pairs pooled -0.024R t-0.2 |
| 11 | H1 EURAUD Z_SWL_rej & dd1=0 → h24 follow | 1164 | +1.71 | +0.039 | 0.54 | 0.54 | +0.055 | +0.024 | 3/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.041R t-2.0 |
| 12 | H4 XAUUSD Z_SWL_at & dh4=0 & dd1=1 & stz=0 → h24 fade | 91 | -177.69 | -0.324 | -0.56 | -0.56 | -0.261 | -0.387 | 1/3 | other pairs 9/17 | **limited** | same rule other 16 pairs pooled +0.007R t0.1 |
| 13 | H1 GBPCHF Z_SWL_rej & loc=SWH & macdh=-1 → br fade | 1012 | -1.96 | -0.064 | -2.07 | -2.04 | -0.047 | -0.081 | 0/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.032R t-3.6 |
| 14 | H1 POOL T_a_any & e200=-1 & loc=SWL & macdt=1 → tt follow | 1899 | -0.57 | -0.043 | -0.90 | -0.85 | -0.018 | -0.067 | 2/4 | 6/17 | **limited** | AUDUSD +0.217R, NZDJPY +0.198R, AUDNZD +0.187R, GBPJPY +0.158R |
| 15 | H1 NZDUSD Z_ASH_at & dd1=0 & macdh=1 → h24 fade | 622 | -1.44 | -0.042 | -0.42 | -0.42 | -0.016 | -0.067 | 1/4 | other pairs 11/16 | **limited** | same rule other 16 pairs pooled +0.020R t0.8 |
| 16 | H1 POOL Z_SWH_rej & dh4=1 & loc=R1 & macdt=1 → h12 fade | 1851 | +0.98 | +0.057 | 1.35 | 1.33 | +0.081 | +0.032 | 3/4 | 11/17 | **limited** | USDJPY +0.372R, EURCHF +0.311R, NZDUSD +0.170R, AUDNZD +0.168R |
| 17 | H1 POOL Z_S1_at & dh4=1 & loc=SWL & macdt=-1 → br follow | 2589 | -0.15 | -0.027 | -1.36 | -1.36 | -0.003 | -0.051 | 1/4 | 6/17 | **limited** | GBPJPY +0.127R, EURJPY +0.099R, NZDJPY +0.053R, NZDUSD +0.047R |
| 18 | H4 GBPCHF I_bbsq → h24 follow | 384 | +0.13 | +0.042 | 0.12 | 0.12 | +0.059 | +0.026 | 2/4 | other pairs 4/16 | **limited** | same rule other 16 pairs pooled -0.018R t-0.1 |
| 19 | H4 GBPCHF I_bbsq → br follow | 934 | +1.82 | +0.049 | 0.86 | 0.86 | +0.066 | +0.032 | 2/4 | other pairs 11/16 | **limited** | same rule other 16 pairs pooled +0.021R t1.4 |
| 20 | H4 XAUUSD Z_SWL_rej & dd1=1 & macdh=-1 → h24 fade | 149 | -279.99 | -0.741 | -1.80 | -1.80 | -0.675 | -0.806 | 0/3 | other pairs 12/17 | **limited** | same rule other 16 pairs pooled +0.064R t0.7 |

Month result: 0 CONFIRMED, 20 limited.

## v2 Month 12: 2008-05  (discovery 2026-11-04T03:09:16+00:00; 9206 candidate rows with >=8 events and in-month t>2.5 [v2] or any t [v1])

| # | candidate | family | events | in-month t | in-month mean net R |
|---|---|---|---|---|---|
| 1 | H4 NZDUSD Z_SWL_rej & dd1=0 & rsi50=1 → h12 fade | combination (zone trigger) | 10 | 6.59 | +4.335 |
| 2 | H1 EURJPY Z_ASH_rej & e200=1 & macdh=-1 → br follow | combination (zone trigger) | 19 | 6.25 | +0.854 |
| 3 | H4 NZDUSD Z_SWL_rej & dd1=0 → h12 fade | combination (zone trigger) | 11 | 6.06 | +3.459 |
| 4 | H1 AUDUSD Z_SWH_at & dh4=0 & e200=-1 & loc=SWH → br follow | combination (zone trigger) | 13 | 6.02 | +0.736 |
| 5 | H1 AUDUSD Z_SWL_at & dd1=1 & macdt=1 → br fade | combination (zone trigger) | 13 | 5.90 | +0.722 |
| 6 | H1 USDJPY Z_PDL_rej & e200=-1 & macdh=1 → h12 follow | combination (zone trigger) | 9 | 5.87 | +1.749 |
| 7 | H1 AUDNZD Z_SWL_rej & dh4=1 & dd1=1 & macdh=-1 → br follow | combination (zone trigger) | 14 | 5.86 | +0.770 |
| 8 | H4 GBPCHF I_ema200 → h24 fade | indicator | 131 | 5.79 | +2.607 |
| 9 | H1 AUDNZD Z_SWL_rej & loc=SWH & rsiz=1 → h24 fade | combination (zone trigger) | 9 | 5.76 | +2.471 |
| 10 | H1 NZDJPY Z_SWH_rej & e200=-1 & rsi50=-1 → h4 fade | combination (zone trigger) | 10 | 5.67 | +0.933 |
| 11 | H1 GBPCHF Z_SWL_rej & dd1=-1 & macdh=-1 → h12 follow | combination (zone trigger) | 20 | 5.66 | +1.754 |
| 12 | H1 GBPCHF Z_SWL_rej & dd1=-1 & loc=none & stz=0 → h24 follow | combination (zone trigger) | 8 | 5.61 | +3.123 |
| 13 | H1 GBPCHF Z_SWL_rej & dd1=-1 & stz=-1 → h12 follow | combination (zone trigger) | 8 | 5.56 | +1.862 |
| 14 | H4 POOL I_cloud → h24 fade | indicator | 1892 | 5.48 | +1.096 |
| 15 | H1 GBPCHF Z_SWH_at & dd1=0 → br follow | combination (zone trigger) | 39 | 5.45 | +0.292 |
| 16 | H4 USDCAD Z_SWL_at & dh4=-1 → h4 follow | combination (zone trigger) | 29 | 5.41 | +0.994 |
| 17 | H1 EURJPY Z_SWL_rej & e200=1 & rsiz=1 → br follow | combination (zone trigger) | 28 | 5.41 | +0.434 |
| 18 | H4 CADJPY Z_PDL_rej → br follow | zone | 10 | 5.38 | +2.066 |
| 19 | H1 AUDNZD Z_PDH_rej & dh4=1 & dd1=1 & stz=0 → h12 fade | combination (zone trigger) | 12 | 5.34 | +1.193 |
| 20 | H4 POOL I_adx_gt25 → h24 fade | indicator | 901 | 5.29 | +1.587 |

Confirmation on the other 203 pool months (2026-11-04T03:09:20+00:00); running test count (v1+v2) = 260

| # | candidate | N | mean pips | mean R | t trades | t daily | gross R | 2x-cost R | blocks + | pairs + | verdict | context |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H4 NZDUSD Z_SWL_rej & dd1=0 & rsi50=1 → h12 fade | 192 | -2.89 | -0.176 | -0.71 | -0.71 | -0.152 | -0.201 | 1/4 | other pairs 9/16 | **limited** | same rule other 16 pairs pooled -0.070R t-1.0 |
| 2 | H1 EURJPY Z_ASH_rej & e200=1 & macdh=-1 → br follow | 1239 | -0.45 | -0.028 | -1.07 | -1.08 | -0.010 | -0.047 | 1/4 | other pairs 1/16 | **limited** | same rule other 16 pairs pooled -0.039R t-5.8 |
| 3 | H4 NZDUSD Z_SWL_rej & dd1=0 → h12 fade | 384 | -0.55 | -0.053 | -0.29 | -0.29 | -0.028 | -0.078 | 2/4 | other pairs 12/16 | **limited** | same rule other 16 pairs pooled +0.077R t1.8 |
| 4 | H1 AUDUSD Z_SWH_at & dh4=0 & e200=-1 & loc=SWH → br follow | 1158 | -0.39 | -0.018 | -0.60 | -0.62 | +0.008 | -0.044 | 2/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.020R t-2.8 |
| 5 | H1 AUDUSD Z_SWL_at & dd1=1 & macdt=1 → br fade | 1271 | -0.68 | -0.040 | -1.42 | -1.44 | -0.014 | -0.067 | 0/4 | other pairs 0/16 | **limited** | same rule other 16 pairs pooled -0.052R t-7.1 |
| 6 | H1 USDJPY Z_PDL_rej & e200=-1 & macdh=1 → h12 follow | 485 | -2.36 | -0.110 | -1.16 | -1.17 | -0.085 | -0.134 | 1/4 | other pairs 4/16 | **limited** | same rule other 16 pairs pooled -0.036R t-1.8 |
| 7 | H1 AUDNZD Z_SWL_rej & dh4=1 & dd1=1 & macdh=-1 → br follow | 395 | -2.15 | -0.135 | -2.46 | -2.52 | -0.110 | -0.160 | 0/4 | other pairs 1/16 | **limited** | same rule other 16 pairs pooled -0.044R t-4.0 |
| 8 | H4 GBPCHF I_ema200 → h24 fade | 1120 | +5.25 | +0.205 | 1.21 | 1.21 | +0.222 | +0.188 | 3/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.013R t-0.2 |
| 9 | H1 AUDNZD Z_SWL_rej & loc=SWH & rsiz=1 → h24 fade | 565 | -3.13 | -0.131 | -1.17 | -1.17 | -0.106 | -0.157 | 2/4 | other pairs 9/16 | **limited** | same rule other 16 pairs pooled +0.067R t2.3 |
| 10 | H1 NZDJPY Z_SWH_rej & e200=-1 & rsi50=-1 → h4 fade | 1318 | -1.10 | -0.049 | -1.66 | -1.67 | -0.026 | -0.071 | 1/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.021R t-2.7 |
| 11 | H1 GBPCHF Z_SWL_rej & dd1=-1 & macdh=-1 → h12 follow | 902 | +0.29 | +0.051 | 0.80 | 0.80 | +0.068 | +0.034 | 2/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.048R t-2.9 |
| 12 | H1 GBPCHF Z_SWL_rej & dd1=-1 & loc=none & stz=0 → h24 follow | 353 | +5.51 | +0.174 | 1.17 | 1.17 | +0.191 | +0.157 | 3/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.049R t-1.4 |
| 13 | H1 GBPCHF Z_SWL_rej & dd1=-1 & stz=-1 → h12 follow | 434 | -0.36 | -0.026 | -0.31 | -0.31 | -0.010 | -0.043 | 3/4 | other pairs 7/16 | **limited** | same rule other 16 pairs pooled -0.020R t-0.9 |
| 14 | H4 POOL I_cloud → h24 fade | 18172 | -0.25 | -0.036 | -0.70 | -0.62 | -0.012 | -0.060 | 1/4 | 6/17 | **limited** | USDCHF +0.262R, EURGBP +0.149R, EURJPY +0.122R, USDCAD +0.089R |
| 15 | H1 GBPCHF Z_SWH_at & dd1=0 → br follow | 2722 | +0.07 | -0.007 | -0.35 | -0.34 | +0.010 | -0.023 | 2/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.020R t-4.0 |
| 16 | H4 USDCAD Z_SWL_at & dh4=-1 → h4 follow | 858 | -1.44 | -0.047 | -0.66 | -0.66 | -0.023 | -0.070 | 1/4 | other pairs 6/16 | **limited** | same rule other 16 pairs pooled -0.025R t-1.4 |
| 17 | H1 EURJPY Z_SWL_rej & e200=1 & rsiz=1 → br follow | 1641 | -1.39 | -0.023 | -0.98 | -1.03 | -0.005 | -0.042 | 1/4 | other pairs 1/16 | **limited** | same rule other 16 pairs pooled -0.038R t-6.1 |
| 18 | H4 CADJPY Z_PDL_rej → br follow | 1413 | -0.61 | -0.046 | -0.90 | -0.91 | -0.024 | -0.069 | 2/4 | other pairs 3/16 | **limited** | same rule other 16 pairs pooled -0.060R t-4.9 |
| 19 | H1 AUDNZD Z_PDH_rej & dh4=1 & dd1=1 & stz=0 → h12 fade | 171 | +2.17 | +0.108 | 0.86 | 0.86 | +0.132 | +0.084 | 3/4 | other pairs 5/16 | **limited** | same rule other 16 pairs pooled -0.028R t-0.8 |
| 20 | H4 POOL I_adx_gt25 → h24 fade | 12023 | -0.02 | -0.071 | -1.43 | -1.10 | -0.047 | -0.095 | 1/4 | 6/17 | **limited** | EURJPY +0.274R, GBPCHF +0.260R, AUDNZD +0.241R, EURGBP +0.210R |

Month result: 0 CONFIRMED, 20 limited.

## v2 loop finished 2026-11-04T03:09:20+00:00: months tried 12, candidate tests v1+v2 260, accepted methods []
