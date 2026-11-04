# EA開発解説サイトの調査と分析

作成日: 2026-11-04

## 調査方法と制約

- 予定: EA開発を解説するサイト20件を全文で読む。
- 実際: このクラウド環境のネットワーク設定で、ページ本文の取得（WebFetch）がすべての対象ドメインで拒否された。拒否されたドメインは oanda.jp, www.oanda.jp, crexgroup.com, gentosha-go.com, www.ebc.com, www.soico.jp, www.mql5.com, newyorkcityservers.com, www.forex.in.rs, algoadvantage.substack.com, getpineforge.com, www.dailyfx.com, forextester.com。
- 代替: Web検索（12回）が返す本文の抜粋と要約から、約30の情報源の主張を集めた。**全文を読んだわけではない**ので、各サイトの細部（具体的なpips数や設定値）は拾えていない。
- 全文で読み直すには、環境設定の Network access で上記ドメインを許可する必要がある（手順: https://code.claude.com/docs/en/cloud-environments#network-access ）。

## 情報源の内訳

| 種類 | 主な情報源 | 偏り |
|---|---|---|
| 国内ブローカーの教育記事 | OANDA証券 Lab（朝スキャEA、最適化、評価値の見方、停止判断、失敗対策、曜日制限、ナンピン、仲値アノマリー） | 口座開設が目的。手法は入門的で、成績の裏付けは示さない |
| EA販売・ツール業者 | MQL5マーケットの製品ページ（Night Scalper、Tokyo Range Breakout 等）、forex-ea-builder、newyorkcityservers | 強い。成績は自己申告のみ |
| 実務家 | Kevin Davey（書籍・ポッドキャスト要約）、Build Alpha（David Bergstrom）、Robot Wealth（Kris Longmore） | 講座販売はあるが、方法論は具体的 |
| 学術 | 神戸大学 卒業論文（ゴトー日）、早稲田大学 MBA論文（仲値前後の時間帯パターン）、Lopez de Prado (2015) | 査読なしの学生論文が中心 |
| メディア・その他 | DailyFX、Benzinga、幻冬舎GOLD ONLINE、ダイヤモンドZAi | 一般論 |

## サイト間で共通していた主張

### 1. 開発の進め方
- **目標を先に決める**: 目標リターンと許容ドローダウンをコードを書く前に決める（Davey）。
- **仮説から始める**: 「なぜその値動きが起きるか」の理由を先に置き、エントリー・ストップ・時間決済・利確をバックテスト前に固定する（Build Alpha、Robot Wealth）。
- **エントリーと決済を別々に検証する**: 決済のほうが成績への影響が大きいことが多い（Davey）。
- **段階的に運用する**: バックテスト → デモ（インキュベーション）→ 最小ロット → 増額 → 定期点検（OANDA、Davey）。

### 2. 検証方法
- **過剰最適化を避ける**: パラメータと指標を減らす。成績の山が尖った1点より、なだらかな台地を選ぶ（OANDA、MQL5、forex-ea-builder）。
- **アウトオブサンプル・ウォークフォワード**: 時系列で分割し、未使用期間で確かめる。目安は 60%/40% など（Build Alpha）。
- **モンテカルロ**: トレード順を入れ替えて、ドローダウンの分布を見る（Davey、Build Alpha）。
- **長期テスト**: 10年以上。景気の一巡をカバーするため（OANDA）。
- **評価指標**: リカバリーファクター（総損益÷最大DD）は10年で10以上が目安。勝率単体では判断しない（OANDA）。
- **停止基準**: バックテストの最大ドローダウンを実運用で超えたら停止（OANDA）。

### 3. コストと執行
- **個人のEAが負ける主因はシグナルよりコスト**（PineForge の例: 1,000回×0.3pipで年間利益の6割が消える）。
- **スプレッドフィルター**: 最大スプレッドを超えたら発注しない（夜間スキャル系EAのほぼすべて）。
- **ロールオーバー時間（NY 17時前後）を避ける**: スプレッドが3〜5倍になる（MQL5ブログ）。
- **ブローカーのサーバー時間に合わせて時刻設定を調整する**。

### 4. 具体的な売買ロジック
| ロジック | 出典 | 内容 |
|---|---|---|
| 早朝（朝スキャ）・夜間スキャルピング | OANDA、MQL5の多数の製品 | 出来高の少ない早朝はレンジになりやすい → RSIやBBで逆張り、小さな利確・大きめの損切り、1ポジション、スプレッドで制限 |
| 仲値・ゴトー日 | OANDAコラム、神戸大・早稲田の論文 | 実需のドル買いで、ドル円は仲値（9:55）に向けて上がり、発表後に下がる。ドル円だけの現象 |
| 東京レンジ・ブレイクアウト | MQL5の製品 | 東京時間の高安を欧州時間に抜けたら順張り |
| トレンドフォロー／平均回帰の切り替え | DailyFX、各種ブログ | ADXなどで相場の状態を判定して使い分け |
| ナンピン | OANDA | 「多くの有名EAに搭載」と紹介しつつ、強制ロスカットの危険も明記 |
| 曜日・アノマリー | OANDA、ダイヤモンドZAi | 曜日ごとの癖を使って取引日を制限 |

## これまでの検証結果との照合

| サイトの主張 | 私たちの検証 | 判定 |
|---|---|---|
| 過剰最適化を避け、未使用データで確かめる | すべてのラウンドで実施。設計時に良い結果も、他通貨・未使用期間で消えた | 主張どおり。最大の落とし穴だった |
| コストが優位性を消す | M15・H1ではコスト前にわずかな偏りがあっても、コスト後はすべてマイナス | 主張どおり |
| 東京レンジ・ブレイクアウト | 第0ラウンドで検証済み。t値 −14 の大きなマイナス | 不成立 |
| ADXでのレジーム切り替え | 第0ラウンドでフィルターとして検証。4区分で一貫せず | 不成立 |
| 曜日フィルター | 前半と後半で符号が一致せず | 不成立 |
| トレンドフォロー全般 | 第0・第1ラウンドで27案以上。利益は数回の大勝ちに依存 | 不成立 |
| ナンピン | 未検証。損失を先送りして勝率を上げる仕組みで、ドローダウンを最小にする要件と正面から矛盾するため対象外とした | 対象外 |
| 早朝・夜間スキャルピング | **未検証**（時間帯を限定した平均回帰はまだ試していない） | 第4ラウンドで検証 |
| 仲値・ゴトー日 | **未検証** | 第4ラウンドで検証 |

## 第4ラウンドに持ち込んだ仮説

サイトの主張のうち、まだ試しておらず、理由（なぜ起きるか）が説明でき、手元のデータで検証できるものは2つだった。

1. **早朝の逆張りスキャルピング**: 理由は「NYクローズ後の流動性低下で値動きがレンジ化する」。ロールオーバーを避け、日本時間7:30〜8:45に入り、9:00の東京オープン前に必ず決済する。コストは夜間のスプレッド拡大を見込み、通常の2倍を基準にした。
2. **仲値アノマリー**: 理由は「輸入企業の実需のドル買いが仲値に集中する」。日本時間8:00に買って9:55に決済する案と、ゴトー日に限る案、仲値後の下落を狙う案。

判定基準は、これまでと同じく事前に固定した（詳細は `r4_report.md`）。

## 主な情報源

- [OANDA Lab: 朝スキャEAの作成方法](https://oanda.jp/lab-education/ea_trading/beginner/morning_scalping_ea)
- [OANDA Lab: EAの最適化](https://www.oanda.jp/lab-education/ea_trading/beginner/ea-optimization/)
- [OANDA Lab: EAの評価値の見方](https://www.oanda.jp/lab-education/ea_trading/beginner/ea-evaluation-value-view/)
- [OANDA Lab: EAの停止判断](https://www.oanda.jp/lab-education/ea_trading/beginner/ea-stop-judgment/)
- [OANDA Lab: EAの失敗と対策](https://www.oanda.jp/lab-education/ea_trading/beginner/ea-failure-countermeasures/)
- [OANDA Lab: 曜日を制限して検証](https://www.oanda.jp/lab-education/?p=46519)
- [OANDA Lab: 朝スキャEAにナンピンを実装](https://www.oanda.jp/lab-education/ea_trading/beginner/morning_scan_ea_nanpin/)
- [OANDA Lab: アノマリーを利用するトレード手法](https://www.oanda.jp/lab-education/blog_column/oanda_local_time)
- [神戸大学 卒業論文（ゴトー日アノマリー）](https://www.econ.kobe-u.ac.jp/wp-content/uploads/2023/05/R2_shirakisho2.pdf)
- [早稲田大学 MBA論文（仲値前後の時間帯パターン）](https://waseda.repo.nii.ac.jp/record/65405/files/WasedaBusinessSchool_mba_2020_1003_57195015.pdf)
- [MQL5: Robustness Testing on Expert Advisors](https://mql5.com/en/articles/16957)
- [MQL5: Walk-Forward Efficiency Ratio](https://www.mql5.com/en/articles/23250)
- [MQL5 blog: The "Holy Grail" Illusion](https://www.mql5.com/en/blogs/post/768222)
- [MQL5 blog: Night Scalper EA – Trading Low Volatility Market Hours](https://www.mql5.com/en/blogs/post/768712)
- [MQL5 blog: Why the Same Strategy Wins in London and Dies in Tokyo](https://www.mql5.com/en/blogs/post/774527)
- [MQL5 Market: Tokyo Range Breakout USDJPY](https://www.mql5.com/ja/market/product/173783)
- [forex-ea-builder: Avoid overfitting](https://forex-ea-builder.vercel.app/blog/avoid-overfitting-expert-advisor)
- [NYC Servers: Walk-forward and Monte Carlo testing](https://newyorkcityservers.com/blog/walk-forward-monte-carlo-testing-eas)
- [Build Alpha (David Bergstrom) interview summary](https://www.forex.in.rs/quant-tested-edge)
- [Kevin Davey: How a champion system builder finds edges](https://www.forex.in.rs/algorithmic-rules-blueprint)
- [Algo Advantage 036: Kevin Davey Part I](https://algoadvantage.substack.com/p/036-kevin-davey-part-i-its-all-about)
- [PineForge: Algorithmic Trading Guide](https://getpineforge.com/guides/algorithmic-trading-master-guide)
- [DailyFX: Methods of Algorithmic Trading](https://www.dailyfx.com/forex/education/algorithmic-trading/2015/08/31/methods-of-algorithmic-trading.html)
- [Forex Tester: Algorithmic Trading Strategies](https://forextester.com/blog/algorithmic-trading-strategies/)
- [Robot Wealth: About](https://robotwealth.com/about/)
- [幻冬舎GOLD ONLINE: EAで勝てない理由](https://gentosha-go.com/articles/-/77353)
