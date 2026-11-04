"""r9c benchmarks: multiple-testing thresholds (Bonferroni, Sidak, BH under global null, expected max for the
deflated Sharpe ratio), and what our t / ratio thresholds mean in Sharpe / Calmar terms. Pure arithmetic, no market data.
Output: out/r9c_bench.log  Run: python3 -I r9c_bench.py"""
import os, numpy as np
from statistics import NormalDist
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, 'out')
Z = NormalDist().inv_cdf; F = NormalDist().cdf
L = open(os.path.join(OUT, 'r9c_bench.log'), 'w')
def P(s=''): print(s); L.write(s + '\n')
g = 0.5772156649
P('m tests | Bonferroni one-sided 5% t | Bonferroni 10% | E[max of m null t] (DSR SR0) | DSR 95% bar = E[max]+1.645 | expected #t>2 under null')
for m in (1, 8, 14, 20, 160, 260, 400, 420, 5000, 19000):
    em = (1 - g) * Z(1 - 1 / m) + g * Z(1 - 1 / (m * np.e)) if m > 1 else 0.0
    P(f'{m} | {Z(1 - 0.05 / m):.2f} | {Z(1 - 0.10 / m):.2f} | {em:.2f} | {em + 1.645:.2f} | {m * (1 - F(2)):.1f}')
P()
P('t threshold -> annualised Sharpe (iid, t = SR_ann * sqrt(years))')
for t in (2.0, 2.5, 3.0, 3.2, 3.4, 3.5):
    P(f't {t}: 13y {t / np.sqrt(13):.2f} | 16y {t / np.sqrt(16):.2f} | 17y {t / np.sqrt(17):.2f} | 20y {t / np.sqrt(20):.2f} | '
      f'12y(2005-16) {t / np.sqrt(12):.2f}')
P()
P('t threshold -> per-trade Sharpe (mean/sd) = t/sqrt(N)')
for t in (2.0, 2.5, 3.0, 3.5):
    P(f't {t}: N300 {t / np.sqrt(300):.3f} | N1000 {t / np.sqrt(1000):.3f} | N5000 {t / np.sqrt(5000):.3f}')
P()
P('Edge needed for 50% / 80% power, Gaussian approximation: edge/sd = (t* + z_power)/sqrt(N)')
for t in (2.0, 2.5, 3.0, 3.5):
    P(f't* {t}: ' + ' | '.join(f'N{n}: 50% {t / np.sqrt(n):.3f}sd 80% {(t + 0.8416) / np.sqrt(n):.3f}sd' for n in (300, 1000, 5000)))
P()
P('ratio = sum/|maxDD| for a drifting random walk (Magdon-Ismail approx.): E[maxDD] ~ (sd^2/mu)(0.6352 + 0.5 ln(t^2)) -> ratio ~ t^2/(0.6352+ln t)')
for t in (1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0):
    P(f't {t}: ratio ~ {t * t / (0.6352 + np.log(t)):.2f}  | per year over 20y (Calmar-like, in R) ~ {t * t / (0.6352 + np.log(t)) / 20:.2f}')
L.close()
