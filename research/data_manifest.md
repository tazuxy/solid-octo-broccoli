# Data manifest (for re-downloading in a new session)

Source: histdata.com Generic ASCII 1-minute bars, mirrored on a public Google Drive folder from the GitHub project philipperemy/FX-1-Minute-Data.
Root folder ID: `1IG_5SM3SLsxVeaDJlmL2qskex5EsTwjG`. Inside, one sub-folder per instrument containing `DAT_ASCII_<SYMBOL>_M1_<YEAR>.zip`.

Download method that worked: Google Drive connector `search_files` with `parentId = '<folderId>'`, then `download_file_content(fileId)`. Large results are written by the harness to a JSON file under the session's `tool-results/` directory; decode with `jq -r '.content' <file> | base64 -d > <title>.zip`, then `unzip -t`. When several agents download at once, each must decode only the exact result paths it was given (never glob the shared directory).

| Instrument | Folder ID | Years used | Notes |
|---|---|---|---|
| EURUSD | 1d-UaZD_1fDYy9UxO6C3Gu8keJqLRMQPb | 2005-2024 | |
| GBPUSD | 1WTDjD_VWr0_L0NW4XKb8zRM39KFq60vE | 2005-2024 | |
| USDJPY | 1aNQztqvX8JOQvTdgQnqRLlrIU6qmEHso | 2005-2024 | method 1 instrument |
| AUDUSD | 111jrwJl5FAeXnsWrJJxRyQwvgqWELyHy | 2005-2024 | isolated >10% spikes removed (round 2) |
| USDCAD | 1iUoMlNekZvS_Noh58jAAkPEndI1IWXRe | 2005-2024 | |
| USDCHF | 1-Ngyf-ctR9lx8Afy82SwuMPVSrmpvzo5 | 2005-2024 | spikes removed |
| NZDUSD | 1bEU82yfqqgKuWThpis3LnqTOX-bnIxcK | 2005-08..2024 | 2005 partial; spikes removed |
| XAUUSD | 1gzYT7dDg45EiMONlapMshOQVXDxUbpfx | 2009-03..2024 | folder starts 2009 |
| EURJPY | 1QuIdvTRug1Qe9qgFf5PhcxOEVlfszQCT | 2005-2024 | |
| GBPJPY | 1iBXlaUq-wbu33Y4Am-GRh4CUw9979FjB | 2005-2024 | |
| EURGBP | 1INIeXYa7eaMSjppp-bjQFqyjm6gS9Gfw | 2005-2024 | |
| AUDJPY | 1f8gXbcIgaIXrrB238Yqzzn-Cov-WAmu5 | 2005-2024 | 2005-05-01..15 contaminated (dropped); 2012 mostly missing (Jan-Sep, Nov-Dec) |
| EURAUD | 1lj_p-XoGRXT8gUmF7oBkK_tZ2qHOTR46 | 2005-2024 | |
| EURCHF | 1K3WbcP8QDxOsx2nalt2N3keUL7dICd5S | 2005-2024 | SNB 2015-01-15 outlier |
| CADJPY | 1RgAeVXjWPd_HqdG4ZnELjuB8zeSSmOd_ | 2007-03..2024 | |
| AUDNZD | 1uetSUc0Gj3w-mRTpESiv3DNijLQbAuTa | 2007-09..2024 | |
| NZDJPY | 1v--RttS1z9koHTt4CRjdBvzNGOJBu-7N | 2006-09..2024 | |
| GBPCHF | 1JlXj13vqKYwkQuwMMO0Oacbk0NqpPdOm | 2005-2024 | spikes removed |
| SPXUSD (S&P500) | 1o4kSKtdwxXf7XYxTzeg7RK-kpFejz_i3 | 2010-11..2024 | |
| GRXEUR (DAX) | 15z_anjRGjj-uwBTVK_hBFwn0EXcen24q | 2010-11..2024 | 2020-06-15..2023-12-01 is NOT DAX (looks like Euro Stoxx 50) |
| UKXGBP (FTSE100) | 1Z2mhxrhBtK8h9muLiHs52NCA_TB275BD | 2010-11..2024 | |
| JPXJPY (Nikkei225) | 1drktk9T07ScUYrzsJSWMOniBfYcRM8t5 | 2010-11..2024 | |
| AUXAUD (ASX200) | 1pB3vQ63-OQS4rWUrqUw7mApfX8aBTWls | 2010-11..2024 | |

Put 2012-2024 FX zips in `<WORK>/data`, 2005-2011 FX zips in `<WORK>/data_early`, index zips in `<WORK>/data_idx`, then run `bash research/rebuild.sh <WORK>`.

Data conventions: timestamps are fixed EST (UTC-5, no DST); JST = EST + 14 h; prices are BID only (spread must be modelled; the 16:55-17:30 EST rollover window produces fake bid dips/recoveries and must be excluded from entries/exits).

## Faster method (verified 2026-11-04): direct HTTPS download, no agents needed

`bash research/fetch_data.sh <WORK>` lists each folder via `https://drive.google.com/embeddedfolderview?id=<folderId>` (folder IDs in `research/data_folders.txt`), downloads each zip from `https://drive.usercontent.google.com/download?id=<fileId>&export=download&confirm=t` (6 in parallel, resumable, retries with backoff), checks HTTP 200, Content-Length = bytes received, and `unzip -t`, and puts the files into `data` / `data_early` / `data_idx`. Took about 3 minutes for all files.

Expected result: 426 zips, 1,299,019,707 bytes (data 234 files 813,948,458 B; data_early 117 files 296,017,886 B; data_idx 75 files 189,053,363 B). Per-file sizes are in `research/data_sizes.tsv`; check with
`cd <WORK> && for f in data*/*.zip; do echo -e "$(basename $f)\t$(stat -c %s $f)"; done | sort | diff - <REPO>/research/data_sizes.tsv && echo SIZES_MATCH`
(USDJPY 2005-2024 sizes were also confirmed equal to the Drive API `fileSize`.)
