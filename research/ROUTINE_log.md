# Research loop (user instruction 2026-11-03)
Goal: a profitable, low-drawdown EA. Indicator choice is free.
Pending round 0: (a) divergence rule C hold-out on 10 crosses -> out/holdout_report.md ; (b) strategy-family screening -> out/fam_report.md
When BOTH finish: report both together to the user.
Pre-registered pass criteria (unchanged across rounds): 4 cells (design8/cross10 x IS2012-18/OOS2019-24) all avgR>0 net; t>=2 pooled 18;
 sumR/|maxDD_R|>=3; N>=100; >=12/18 instruments positive.
If neither passes: diagnose failure -> design 2-3 alternatives (record dropped/changed/added) -> verify with Opus high agent, same data/costs/criteria -> judge.
Max 3 iterations (multiple-testing control). Log every tested variant incl. failures. If none after 3: say so honestly + closest candidate.
Deliverables to repo (push currently blocked by GitHub App access; commit locally).

## Round 0 result (a) divergence hold-out: FAIL
Rule C cross10: N=156 avgR -0.168 t -1.50 IS -0.16 OOS -0.18, 4/10 pairs+. Cluster (2nd signal) effect reverses on cross. Costs not the cause (gross -0.116).
30 filters tested; only 2 consistent in 4 cells (~chance). Best rule E: design +0.555 (N80), cross -0.049 (N69). Verdict: divergence does not generalise -> DROP.
Report: out/holdout_report.md
Waiting for (b) fam_report.md

## Round 0 result (b) family screening: FAIL (27/27 rows fail; only N criterion met). Closest Donchian H4 N50 + filters: t1.64, ratio 2.5; portfolio maxDD -41%.
Both round-0 results reported to user. Committed 00efb58 (local; push blocked).
## Round 1 started (iteration 1 of 3): H1 cross-sectional currency momentum/reversal; H2 vol-targeted diversified TSMOM portfolio (+ex-JPY/XAU); H3 intraday "home currency depreciates in home hours".
 Portfolio-form criteria (4 cells D/C x IS/OOS, t>=2 weekly, ret/DD>=3 at 8% vol, >=100 rebalances, >=60% contributors). Output out/r1_report.md

## Round 1 result: FAIL (6/6). H1a 12w xs-momentum negative (t-2.0); H1b 1w reversal t0.43; H2 TSMOM = SNB week only; H3 intraday t-7.
 Post-hoc: H1a flipped (12w xs REVERSAL) 4 cells + but t1.53, ret/DD 3.8 -> not a candidate (snooped).
## Round 2 plan (iteration 2 of 3): fresh untouched data 2005-2011 from Drive (earlier years exist). Pre-registered one-shot tests on 2005-11 of:
 12w xs reversal, 1w xs reversal, their 50/50 combo, plus round-0 closest (Donchian H4 N50+filters, divergence rule C). Execution Monday 08:00 EST (fix Sunday-open spread issue).

## Round 2 launched: 2005-2011 bars in bars_early (18 pairs). One-shot fixed candidates P1 12w xs reversal, P2 1w reversal, P3 combo, P4 Donchian H4, P5 div C/E. Exec Mon 08:00 EST. Output out/r2_report.md (+ r2_EA.mq5 if pass)
## Round 2 result: FAIL (6/6, one-shot on untouched 2005-07..2011-12, Mon 08:00 exec). P1 12w reversal (post-hoc flip) negative out of sample (D -4.0%, C -4.5% @8%vol, t -1.24; 2008 -24%).
 P2 1w reversal closest: 2005-11 D +5.5% C +3.3%, pooled t 1.34 (<1.5); 13/15 ccy+; but 2012-24 with Mon exec t -0.61; full 2005-24 t 0.59, ret/DD 0.61.
 P3 t 0.21; P4 Donchian 2005-11 avgR -0.080 (t -1.68); P5 C -0.044, E -0.136. 2012-24 round-0/1 numbers reproduced exactly. No EA written. Report out/r2_report.md
 Committed d919654. Reported to user.
## Round 3 (FINAL, iteration 3 of 3) design: price-only signals exhausted -> add NEW information (cross-asset equity indices from histdata: SPX, DAX, FTSE, Nikkei, ASX; SPX from 2010).
 R3-A risk-regime JPY carry: long AUDJPY NZDJPY CADJPY (group A) / EURJPY GBPJPY AUDUSD NZDUSD (group B) only when SPX>200d SMA (a) [+ SPX 20d vol < 1y median (b)]; flat otherwise; vs buy&hold benchmark. Swap excluded (conservative for these longs).
 R3-B month-end hedge-rebalancing (Melvin&Prins 2015): last business day, MTD SPX vs foreign index; US outperform -> long foreign ccy vs USD from 08:00 EST to London 16:00 fix (DST aware). EURUSD/DAX GBPUSD/FTSE USDJPY/Nikkei AUDUSD/ASX. variant b: enter 2 bdays before.
 Period 2011-2024 (IS 2011-17 / OOS 2018-24). Data downloading to data_idx/.
## Round 3 result (FINAL): FAIL 4/4. Data: GRXEUR 2020-06-15..2023-12-01 is Euro Stoxx 50 (excluded for EURUSD in H-B); AUDJPY 2012 gap handled (pair unavailable).
 H-A a: cells A +1.2/+0.8 B -0.4/-0.2 %, t 0.16, ret/DD 0.02, worse than B&H (SR A 0.12 vs 0.31). b negative. Risk-off days were the BEST days for JPY carry.
 H-B a: avgR -0.039 t -1.27 (gross -0.010R); b: -0.004 t -0.05; 1/4 pairs +. No EA. Report out/r3_report.md. 3-iteration limit reached.

## Loop finished after round 3 (max). Final verdict: no candidate. FINAL_SUMMARY.md committed.

## Round 4 (extra round requested after loop end; site-review hypotheses): FAIL 8/8. Report out/r4_report.md (JP).
 S1 night M5 scalping 17:30-18:45 EST, RSI/BB x mid/ATR exits, 17 pairs, baseline cost x2: gross +1.1..+2.2 pips/trade (t 18-41) but net <0 already at x1
  (break-even 0.49-0.88x cost); x2 avgR -0.23..-0.38, 0/6 cells, <=1/17 pairs. Gross edge concentrated 17:30-17:55 (rollover; bid-only artifact likely). Placebo 08-11 EST ~0 gross.
 S2 Tokyo fix USDJPY (cost x1=1.0pip): a -0.004R; b goto-bi +0.039R t2.40, 3 periods +, ratio 2.47 (<3), x2 -0.010 -> FAIL (closest; passes 1-3 only if cost<=0.7pip);
  c -0.020; c2 +0.006. Gross effect also in EURJPY/AUDJPY. No filters/portfolio/EA (nothing passed).

## 2026-11-04 user instructions
- Spread assumption = 0.5 pip (user). Re-evaluate r4 S1/S2 at 0.5 pip -> out/r4b_report.md (agent running).
- New Gotobi variants: buy on the business day BEFORE Gotobi (E1 15:00 JST D->09:55 G, E2 22:00 JST D->09:55 G, E3 09:55 D->09:55 G, E4 control 08:00->09:55 on D).
- Source research: JP 50 (25 EA / 25 method), EN 150 (75 EA / 75 method); individuals preferred, brokers <=20%. WebFetch blocked -> search-excerpt based.
  Outputs sites2/catalog_jp.md, catalog_en_ea.md, catalog_en_method.md. Then synthesize -> round 5 hypotheses.

## Round 5 launched (200-source ideas): H1 weekend gap fade, H2 round numbers (Osler), H3 daily fix flows (Tokyo/ECB/London pre-long USD / post-short), H4 gold Asia long, H5 JPY afternoon & month-end. Cost 0.5 pip (gold 0.30). t>=3, 6 cells, robustness. -> out/r5_report.md

## Round 5 result: FAIL (14/14). Agent interrupted by container restart after evaluation; report written from saved r5_summary.csv / r5_eval.txt. Closest H1b weekend-gap fade (t 2.42, Bonferroni p 0.11). Gotobi-eve E2 (r4b) remains the only pass.

## Round 6 (user 2026-11-04): refine E2 with (1) HTF environment, (2) day-of-week/calendar, (3) extra indicators. Selection 2005-2014, validation 2015-2024 (frozen choice in out/r6_frozen.json before validation). Max 2 filters. Output out/r6_report.md, r6_EA.mq5.

## Round 6 result: one filter frozen on 2005-14 (skip month-end Gotobi), CONFIRMED on 2015-24 (sum/DD 2.02->3.78). Final rule N~1260, +6.2 pips, t 4.6. Caveats: drop top5% -> +0.6 pips t 0.5 (fat-tail dependent); month-end weakness seen earlier (partial contamination). EA updated InpSkipMonthEndG=true.
