# 再現手順

## データ

histdata.com の Generic ASCII 1分足を使用。GitHub プロジェクト `philipperemy/FX-1-Minute-Data` の README にある
Google Drive フォルダ（「All instruments - 1Minute - 2000 / 2024」）から、各銘柄の
`DAT_ASCII_<PAIR>_M1_<YEAR>.zip`（2012〜2024）を `data/` に置く。

銘柄: EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, NZDUSD, XAUUSD

## 環境

Python 3.13, pandas 3, numpy, pyarrow, scipy, matplotlib

```
pip install pandas numpy pyarrow scipy matplotlib
```

## 実行順

`code/` の 1 つ上のディレクトリに `data/`, `bars/`, `out/` を作ってから実行する。

```
python -I code/prep.py eurusd gbpusd usdjpy audusd usdcad usdchf nzdusd xauusd   # M1 -> M15/H1/H4/D1 parquet
python -I code/eval1.py M15 H1        # 段階1: シグナル後の先行リターン（ATR単位）
python -I code/run_bt1.py M15 H1      # 段階2: トレードシミュレーション + 特徴量保存
python -I code/filt1.py H1 mid_sl1.0_32   # フィルター候補の条件付き集計
python -I code/grid.py H1 H4          # シグナル定義 x 決済ルールの総当たり
python -I code/h4.py                  # H4 の安定性・ダイバージェンス有無比較・特徴量
Q=3 python -I code/filt1.py H4 mid_sl1.0_32 trades_h4.parquet
python -I code/port.py                # フィルター組み合わせ + ポートフォリオ
python -I code/cluster.py             # 何回目のシグナルかによる差、保有期間
python -I code/final_h4.py            # 最終ルール案の成績と資産曲線 (out/equity_h4.png)
python -I code/h1_cluster.py          # 2回目ルールを H1/M15 に適用した場合
```

## 主要ファイル

- `code/sig.py`: 指標（BB, RSI, ATR）とシグナル定義（`signals()`）
- `code/bt.py`: トレードシミュレーター（`simulate()`）、特徴量（`build()`）、コスト設定（`COST_PIPS`）
- `out/eval1.csv`, `out/grid.csv`, `out/h4_grid.csv`: 集計結果
- `out/trades_final_h4_ruleC.csv`: 最終ルール案の全トレード（141件）
- `out/equity_h4.png`: 資産曲線
