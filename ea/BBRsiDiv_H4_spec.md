> **非推奨（2026-11-03）:** 後続の検証（他通貨・未使用期間）でこのルールは再現しませんでした。`FINAL_SUMMARY.md` を参照。

# EA 仕様: BB(20,2σ) 終値外 × RSI ダイバージェンス（2回目）H4

REPORT.md の 3 章を MQL5 に落とすための骨子。**未コンパイル・未検証**（本環境に MT5 がない）。
実装後は必ずストラテジーテスターで 2012〜2024 を走らせ、`research/out/trades_final_h4_ruleC.csv` と
トレード数・平均R が同程度になることを確認すること（H4 の足の区切りがブローカーで異なるため、完全一致はしない）。

## 入力パラメータ

| 名前 | 既定値 | 意味 |
|---|---|---|
| BB_Period / BB_Dev | 20 / 2.0 | ボリンジャーバンド（終値） |
| RSI_Period | 14 | RSI |
| ATR_Period | 14 | ATR |
| Lookback | 100 | 安値・高値の参照範囲（3本前〜100本前） |
| RsiMargin | 5.0 | RSI 乖離の最小値（pt） |
| ClusterBars | 12 | 「2回目」と見なす範囲（本） |
| SL_ATR | 1.0 | シグナル足の極値からの ATR 倍率 |
| MaxRiskATR | 1.5 | ストップ幅の上限（ATR 倍）。超えたら見送り |
| MaxBars | 32 | 時間切れ（本） |
| RiskPct | 0.5 | 1トレードの口座リスク（%） |
| MaxPositions | 4 | 口座全体の同時ポジション上限（複数チャートで共有するならグローバル変数で管理） |
| MaxSpreadMult | 2.0 | 現在スプレッドが通常の何倍を超えたら発注しないか |
| NewsBlockMin | 0 | 指標前後の新規停止（分）。0 で無効。カレンダー連携は別途 |
| Magic | 240401 | マジックナンバー |

## 判定ロジック（確定足 shift=1 で判定、新しい足が開いたときに 1 回だけ実行）

```mql5
// ハンドル: iBands(_Symbol, PERIOD_H4, BB_Period, 0, BB_Dev, PRICE_CLOSE)
//           iRSI(_Symbol, PERIOD_H4, RSI_Period, PRICE_CLOSE)
//           iATR(_Symbol, PERIOD_H4, ATR_Period)

bool IsNewBar() { static datetime last=0; datetime t=iTime(_Symbol,PERIOD_H4,0); if(t==last) return false; last=t; return true; }

// 直近 Lookback 本（3 本前〜Lookback 本前）の最安値のインデックスを返す
int ArgMinLow(int from=3, int to=100) {
   int best=from; double v=iLow(_Symbol,PERIOD_H4,from);
   for(int s=from+1; s<=to; s++){ double l=iLow(_Symbol,PERIOD_H4,s); if(l<v){v=l;best=s;} }
   return best;
}
int ArgMaxHigh(int from=3, int to=100) { /* 鏡像 */ }

// シグナル判定（1 = 買い, -1 = 売り, 0 = なし）。すべて shift=1 の確定足で評価
int Signal() {
   double upper[1], lower[1], mid[1], rsi[2], atr[1];
   CopyBuffer(hBB,1,1,1,upper); CopyBuffer(hBB,2,1,1,lower); CopyBuffer(hBB,0,1,1,mid);
   CopyBuffer(hATR,0,1,1,atr);
   double c=iClose(_Symbol,PERIOD_H4,1), l=iLow(_Symbol,PERIOD_H4,1), h=iHigh(_Symbol,PERIOD_H4,1);
   double rsiNow; { double b[1]; CopyBuffer(hRSI,0,1,1,b); rsiNow=b[0]; }

   if(c<=lower[0]) {
      int j=ArgMinLow(3,Lookback);                       // 1 本前基準なので実際の shift は j+1
      double refLow=iLow(_Symbol,PERIOD_H4,j+1);
      double refRsi; { double b[1]; CopyBuffer(hRSI,0,j+1,1,b); refRsi=b[0]; }
      if(l<refLow && rsiNow>refRsi+RsiMargin) return 1;
   }
   if(c>=upper[0]) {
      int j=ArgMaxHigh(3,Lookback);
      double refHigh=iHigh(_Symbol,PERIOD_H4,j+1);
      double refRsi; { double b[1]; CopyBuffer(hRSI,0,j+1,1,b); refRsi=b[0]; }
      if(h>refHigh && rsiNow<refRsi-RsiMargin) return -1;
   }
   return 0;
}
```

### 「2回目」ルールの状態管理

```mql5
datetime lastBuySig=0, lastSellSig=0;   // 直近の同方向シグナル足の時刻（EA 再起動に備えて GlobalVariable に保存推奨）

void OnTick() {
   if(!IsNewBar()) return;
   ManageOpenPosition();                  // 時間切れ決済
   int sig=Signal(); if(sig==0) return;
   datetime t1=iTime(_Symbol,PERIOD_H4,1);
   datetime &last = (sig==1)? lastBuySig : lastSellSig;
   bool second = (last!=0 && (t1-last) <= ClusterBars*PeriodSeconds(PERIOD_H4));
   last = t1;                             // 今回を記録（1回目でも記録する）
   if(!second) return;                    // ★ 1回目は取引しない
   TryEnter(sig);
}
```

### エントリー時の見送り条件（TryEnter 内、順にチェック）

```
1. 同銘柄に自分のポジションがある              → 見送り
2. 口座全体のポジション数 >= MaxPositions        → 見送り
3. 現在スプレッド > 通常スプレッド × MaxSpreadMult → 見送り（通常値は直近 N ティックの中央値などで推定）
4. NewsBlockMin > 0 かつ指標の前後 NewsBlockMin 分 → 見送り
5. stop = (買い) low[1] - SL_ATR*ATR[1] / (売り) high[1] + SL_ATR*ATR[1]
   risk = |entry - stop|（entry は現在の Ask/Bid）
   risk > MaxRiskATR*ATR[1]                   → 見送り（★ 大きな足のシグナルは取らない）
6. tp = BB 中心線[1]（固定）
   |tp - entry| <= スプレッド                  → 見送り（目標が近すぎる）
7. ロット = AccountBalance * RiskPct/100 / (risk / TickSize * TickValue)、最小・最大・ステップで丸める
8. 成行で発注、SL/TP を同時に設定、コメントにシグナル足の時刻を入れる
```

### 時間切れ決済

```
保有ポジションのオープン時刻から MaxBars 本（MaxBars * PeriodSeconds）経過したら成行でクローズ。
```

### 非常停止

```
口座のピーク残高を GlobalVariable に保持し、現在の残高がピーク比 −10% を下回ったら新規停止。
再開は手動（GlobalVariable のリセット）。
```

## 検証で採用しなかったもの（入れない）

- 上位足トレンド方向への限定（検証では逆効果）
- RSI 30/70 の閾値（ダイバージェンスの代替にならない）
- 曜日フィルター（IS/OOS で不一致）
- ナンピン・分割決済・トレーリング（未検証）

## フォワードで比較したいスイッチ

- バンド幅フィルター（直近200本の百分位 < 0.6 のときだけ取引）: バックテストでは DD がやや改善、トレード数は 35% 減
- 20:00 EST 相当の足（アジア早朝）の除外: OOS でのみ効果、N が小さい
- 指標フィルター（NewsBlockMin）: 未検証
