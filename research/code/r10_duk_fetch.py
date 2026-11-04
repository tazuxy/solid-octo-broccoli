"""Round 10: resumable downloader for Dukascopy M1 BID/ASK candle files (one file per UTC day).
Usage: python3 -I r10_duk_fetch.py <OUT_DIR> <job>   job = h6 (7 majors, Mon-Thu UTC days 2005-2024) | xs (AUDCAD NZDCAD AUDNZD, Wednesdays 2008-2024)
Files: <OUT_DIR>/<PAIR>/<YYYY-MM-DD>_<BID|ASK>.bi5 (0-byte file = no data that day). Rate limit ~4 files/s -> 4 threads, backoff on 429."""
import os, sys, time, subprocess, datetime as dt
from concurrent.futures import ThreadPoolExecutor
OUT, JOB = sys.argv[1], sys.argv[2]
if JOB == 'h6':
    PAIRS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF', 'NZDUSD']; d0, d1, dows = dt.date(2005, 1, 1), dt.date(2024, 12, 31), {0, 1, 2, 3}
else:
    PAIRS = ['AUDCAD', 'NZDCAD', 'AUDNZD']; d0, d1, dows = dt.date(2008, 1, 1), dt.date(2024, 12, 31), {2}
jobs = []
d = d0
while d <= d1:
    if d.weekday() in dows:
        for p in PAIRS:
            for side in ('BID', 'ASK'):
                f = os.path.join(OUT, p, f'{d}_{side}.bi5')
                if not os.path.exists(f): jobs.append((p, d, side, f))
    d += dt.timedelta(days=1)
print('todo', len(jobs), flush=True)
def get(job):
    p, d, side, f = job
    url = f'https://datafeed.dukascopy.com/datafeed/{p}/{d.year}/{d.month-1:02d}/{d.day:02d}/{side}_candles_min_1.bi5'
    os.makedirs(os.path.dirname(f), exist_ok=True)
    for k in range(8):
        r = subprocess.run(['curl', '-sS', '-o', f + '.part', '-w', '%{http_code}', url], capture_output=True, text=True)
        code = r.stdout.strip()
        if code == '200': os.replace(f + '.part', f); return 0
        if code == '404': open(f, 'wb').close(); return 0
        time.sleep(min(60, 1.5 * 2 ** k))
    return 1
fails = 0; n = 0
with ThreadPoolExecutor(4) as ex:
    for r in ex.map(get, jobs):
        fails += r; n += 1
        if n % 2000 == 0: print(n, 'done', fails, 'failed', time.strftime('%H:%M:%S'), flush=True)
print('finished', n, 'failed', fails, flush=True)
