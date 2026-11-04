#!/usr/bin/env bash
# Rebuild all bar files from the histdata M1 zips in a fresh session.
# Usage: bash research/rebuild.sh <WORK_DIR>
#   <WORK_DIR>/data       : DAT_ASCII_<PAIR>_M1_<YEAR>.zip, 2012-2024 (18 FX/gold instruments)
#   <WORK_DIR>/data_early : same, 2005-2011
#   <WORK_DIR>/data_idx   : SPXUSD GRXEUR UKXGBP JPXJPY AUXAUD, 2010-2024
# (download them first: see research/data_manifest.md)
set -euo pipefail
W=${1:?work dir}
REPO=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$W"/{bars,bars_early,bars_idx,bars_full,bars_m5,out}
rm -rf "$W/code" && cp -r "$REPO/research/code" "$W/code"
pip install -q pandas numpy pyarrow scipy matplotlib
FX="eurusd gbpusd usdjpy audusd usdcad usdchf nzdusd xauusd eurjpy gbpjpy eurgbp audjpy euraud eurchf cadjpy audnzd nzdjpy gbpchf"
cd "$W"
# 1) 2012-2024 bars (M15/H1/H4/D1)
python3 -I code/prep.py $FX
# 2) 2005-2011 bars
DATA_DIR=data_early BARS_DIR=bars_early python3 -I code/prep.py $FX
# 3) equity-index bars
DATA_DIR=data_idx BARS_DIR=bars_idx python3 -I code/prep.py spxusd grxeur ukxgbp jpxjpy auxaud
# 4) cleaned, continuous 2005-2024 bars (applies the round-2 data-quality fixes)
python3 -I code/r2_prep_full.py
# 5) M5 bars for the 17 FX pairs, 2005-2024 (round 4)
python3 -I code/r4_prep_m5.py
# 6) integrity check: method 1 must reproduce (all Gotobi-eve: N=1514, net +4.77 pips, t 3.89)
python3 -I code/v_gotobi_eve.py "$W"
