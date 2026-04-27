# Pon さんへの Wise 切替 事前確認 — 前提条件・影響・LINE 送付テンプレ

- 対象 BL: **BL-0068**
- 作成日: 2026-04-27
- 目的: 田中さん側で Wise 個人開設に着手する前に、**Pon さんに Wise 切替で問題ないか確認** する。同時に Pon さん側に発生する作業・前提・影響を一括提示し、判断材料を渡す。
- 上位文書: `wise_billing_full_procedure_v2.md`（v2 確定版・本書は §3 Phase B の前段確認）

---

## 0. 一行サマリ（田中さん向け）

> **Pon さん側で Wise 個人アカウントの開設は必須**（送金者本人名義の Wise 口座が必要なため）。本書は「Wise でいいか + 開設に同意してもらえるか」を Pon さんに確認するためのもの。同意取得後に v2 手順書 Phase A → B → D の順で実行する。

---

## 1. Pon さん側で Wise アカウントは必要か？

### 結論: **必要（必須）**

| 観点 | 結論 |
|---|---|
| Wise アカウントなしで送金できるか | ❌ 不可。Wise の「送金」は送金者が Wise アカウントを持っている前提 |
| 田中さんの口座番号 (Wise JPY 口座) に銀行から直接振込んだら届くか | △ 一応届くが、その場合は Wise を経由する利点（為替実勢・低コスト）が消える。**Wise の意義はゼロ** |
| 法人 Wise Business の代わりに個人 Wise でも問題ないか | ✅ 問題なし。田中さん回答で「Pon さん個人で送金」確定済 |
| Pon さんに開設の手間がかかる | はい。**KYC 含めて 1〜3 日 + 1 時間程度の操作** |

> Wise の本質は「送金者・受取者の両方が Wise を経由することでミッドマーケット為替＋低手数料を実現」する仕組み。送金者側に Wise アカウントが無いと意味がない。

---

## 2. Pon さん側の前提条件（揃えるもの）

### 2.1 必要書類（KYC 用）

- [ ] **パスポート 顔写真ページ**（タイ ID カードでも可だが、外貨送金は通常パスポート推奨）
- [ ] **住所確認書類**（過去 3 ヶ月以内発行）
  - タイの公共料金領収書（電気 / 水道 / インターネット）
  - 銀行明細書（オンライン明細 PDF も可）
  - 賃貸契約書 等
- [ ] **セルフィー**（スマホで撮影。本人確認書類と顔が同じフレームに収まる写真）
- [ ] **タイ国内の銀行口座**（バーツ建て、引落元として Wise に紐付け）
- [ ] **メールアドレス + 携帯電話番号**（SMS 認証用）

### 2.2 環境

- スマホ or PC（Wise アプリ or wise.com）
- インターネット環境
- タイ国内銀行のオンラインバンキング or アプリ（送金時の引落確認用）

### 2.3 開設時間の見積もり

| 工程 | 所要 |
|---|---|
| アカウント情報入力 | 10 分 |
| 書類撮影 + アップロード | 10 分 |
| KYC 審査（Wise 側） | 数時間 〜 12 時間（混雑時 1〜3 営業日） |
| 銀行口座紐付け | 5 分 |
| **合計** | **当日〜3 営業日** |

---

## 3. Pon さん側への影響（メリット・デメリット）

### 3.1 メリット

- ✅ **PayPal 不可問題が解消**（タイで PayPal 送金機能が事実上使えない問題を回避）
- ✅ **送金手数料が安い**（為替実勢に近く、隠れコストなし）
- ✅ **着金が早い**（数時間〜1 営業日。SWIFT の 2〜5 日と比べて高速）
- ✅ **送金履歴がアプリで一元管理**（過去送金の確認・領収書 PDF 出力が楽）
- ✅ **将来的にタイ国内 PromptPay 統合**（2026-05-19 以降、Wise からタイ国内決済も可能に）

### 3.2 デメリット / 注意点

- ⚠️ **送金手数料は Pon さん側負担**
  - 250,000 JPY = 約 58,000 THB（2026-04 為替）相当の送金で、Wise 手数料は **約 250〜500 THB（約 1,000〜2,000 円相当）**
  - PayPal の 2〜4% 手数料と比べて格段に安い
- ⚠️ **為替変動リスクは Pon さん側**
  - 田中さん側は **250,000 JPY 固定** で受取。THB→JPY のレートが Pon さん側に円高で動くと、引落 THB が増える
  - 過去 1 年の THB/JPY 変動レンジは ±5% 程度なので、月次での誤差は ±3,000 THB（±10,000 円）程度に収まる
- ⚠️ **個人立替の経理処理が必要**
  - Pon さん **個人** から田中さんへ送金 → Rio's Innovation の経費として **Pon さんが個人立替 → 法人精算** する必要あり
  - 法人 Wise Business に切替えれば不要になるが、現時点では個人運用で確定（田中さん 4/27 回答）
- ⚠️ **KYC 書類提出**
  - パスポート + 住所書類 + セルフィー が必要
  - Wise 側でデータ管理されるが、合理的な KYC 範囲（タイ国内の他の金融サービスと同等）
- ⚠️ **タイ BOT 規制**
  - 月額 25 万円 = 年間 300 万円ペースは個人 Wise の年間上限内（タイ個人 Wise は年間 5,000,000〜10,000,000 THB ≒ 2,000〜4,000 万円相当）
  - 規制抵触の心配なし

### 3.3 Pon さん側で発生する月次運用

| タイミング | アクション | 所要 |
|---|---|---|
| 毎月初 | 田中さんから LINE で請求書 PDF 受領 | — |
| 任意（〜15 日） | Wise アプリで田中さん JPY 口座へ 250,000 JPY 送金 | 5 分 |
| | THB 引落確認 | 1 分 |
| | 法人経費精算（領収書ダウンロード → Rio's Innovation 経理へ提出） | 5 分 |

> 月次合計約 **10〜15 分** が Pon さん側の運用負荷。

---

## 4. 田中さんが Pon さんに確認すべき項目（チェックリスト）

LINE で確認するか、次回セッション（2026-04-27 月 第6回）で口頭確認:

- [ ] **Q-1**. Wise への切替自体に同意してもらえるか？
- [ ] **Q-2**. Pon さん個人での Wise アカウント開設に同意してもらえるか？
  - 法人ではなく個人での送金になることへの了解
  - Rio's Innovation 経費として個人立替→法人精算を回せるか
- [ ] **Q-3**. KYC 書類（パスポート / 住所書類 / セルフィー）の準備は問題ないか？
- [ ] **Q-4**. 送金手数料 Pon さん負担（毎月 1,000〜2,000 円相当）に問題ないか？
- [ ] **Q-5**. 為替変動が Pon さん側に来ること（月 ±10,000 円程度の THB 変動）に問題ないか？
- [ ] **Q-6**. 開設に 1〜3 日かかるが、いつ頃から着手可能か？
- [ ] **Q-7**. Wise 以外の選択肢（Payoneer / SWIFT 銀行送金）を試したいか？
- [ ] **Q-8**. **2 月分・3 月分・4 月分の遡及 3 件まとめ請求**（合計 750,000 JPY ≒ 174,000 THB 相当）の支払いタイミングは Pon さん側で問題ないか？

> Q-7 で代替を希望されない限り、Wise で進める前提。

---

## 5. 代替案（Pon さんが Wise を望まない場合）

万一 Pon さんが Wise 開設を渋る場合の選択肢:

| 代替 | 手数料 (5,000 USD / 月) | 着金 | Pon さん側手間 | 推奨度 |
|---|---|---|---|---|
| **Wise 個人**（本命） | 25〜45 USD | 数時間〜1 日 | 開設 1〜3 日 | ⭐️⭐️⭐️ |
| Payoneer | 50〜150 USD + 為替差 | 1〜3 日 | 開設 1〜3 日 | ⭐️ |
| SWIFT 銀行送金 | 約 8,000 円 + 為替差 | 2〜5 日 | 既存銀行口座のみ・即可 | ⭐️⭐️（手間最小、ただしコスト最大） |

> Pon さんが「銀行から振り込ませて」と言ったら → **SWIFT** に切替（v1 で比較済）。コストは増えるが Pon さん側の手間は最小。

---

## 6. Pon さんへの LINE 送付テンプレ（日英併記）

田中さんがこのまま LINE にコピペできるように整形。

### 6.1 1 通目（全体説明 + 同意確認）

```
Pon-san、お疲れさまです。
ご相談です。

【背景】
PayPal で支払いをお願いしてきましたが、タイでは PayPal の送金機能が使えないことが判明しました。
代替案を検討した結果、Wise（旧 TransferWise）が手数料・着金スピードの面で最適でした。
切替えてもよろしいでしょうか？

【Wise でやることのサマリ】
- Pon さん側で個人 Wise アカウント開設（無料、1〜3 日）
- 月次 250,000 JPY を Wise 経由で田中さん口座へ送金
- 送金手数料: 約 1,000〜2,000 円 / 回（Pon さん側負担）
- 為替は月によって ±10,000 円程度動きます（Pon さん側引落 THB が変動）

【Pon さん側で必要なこと】
1. https://wise.com/ で Personal account を作成
2. パスポート + 住所確認書類（3 ヶ月以内）+ セルフィー で本人確認
3. タイの銀行口座を Wise に登録
4. 月次で田中さんから請求書 PDF を LINE で受領 → Wise アプリで送金

【確認事項】
Q1. Wise への切替に同意していただけますか？
Q2. Pon さん個人名義で送金（→ Rio's Innovation で個人立替→精算）で問題ないですか？
Q3. アカウント開設の着手はいつ頃から可能ですか？
Q4. （補足）2 月稼働分・3 月稼働分・4 月稼働分の合計 750,000 JPY を遡及でまとめて請求させてください。Wise 開設後に 3 件まとめて支払い、で大丈夫でしょうか？

もし Wise 以外がよければ、Payoneer や銀行 SWIFT 送金も検討できます。
ご都合教えてください。

----

Hi Pon-san,

I'd like to discuss our payment method.

[Background]
I asked you to pay via PayPal before, but it turns out PayPal's send-money function isn't usable in Thailand.
After comparing alternatives, Wise (formerly TransferWise) is the best option for fees and speed.
Would you be OK switching to Wise?

[What this means]
- You'd open a personal Wise account (free, 1〜3 days for verification)
- Monthly transfer of 250,000 JPY via Wise to my account
- Sending fee: ~1,000〜2,000 JPY equivalent per transfer, on your side
- Exchange rate fluctuates ±10,000 JPY/month roughly (your THB cost varies)

[What you'd need to do]
1. Create a Personal account at https://wise.com/
2. Upload passport + proof of address (within 3 months) + selfie for KYC
3. Link your Thai bank account to Wise
4. Receive my monthly invoice PDF via LINE → send via Wise app

[Questions]
Q1. Are you OK switching to Wise?
Q2. Is it OK to send from your personal Wise account (Rio's Innovation reimburses you internally)?
Q3. When can you start setting up the account?
Q4. (Bonus) I'd like to invoice February + March + April together = 750,000 JPY total in retrospect. OK to settle them in one batch after your Wise is ready?

If you'd prefer something else, we can also use Payoneer or SWIFT bank transfer.
Let me know!
```

### 6.2 補足: 質問への想定回答パターン

#### パターン A: Pon さん同意（最もシンプル）

田中さんは即座に Phase A（個人 Wise 開設）に着手 → Pon さん側にも v2 §3.3 の依頼テンプレを送付 → Phase B 並走。

#### パターン B: Pon さん「個人ではなく法人で送りたい」

→ Wise Business（タイ法人）開設になり 1〜2 週かかる。田中さん側は Phase A 個人開設で問題なし、Pon さん側だけ Business 開設に変更。手順書 v1 §3.1 を再活用。

#### パターン C: Pon さん「Wise 開設は手間なので銀行から直接送りたい」

→ SWIFT 銀行送金に切替。田中さん側は Wise 開設不要、みずほの SWIFT 受取情報を Pon さんに共有。手数料増 + 着金遅延を許容する代わりに Pon さん側の手間ゼロ。

#### パターン D: Pon さん「Wise でいいけど書類提出の時間がない」

→ Phase B のスタート時期を調整（5 月中旬以降など）。田中さん側は Phase A だけ先に進める。遡及 3 件は Phase B 完了後に発行。

---

## 7. 田中さんネクストアクション

1. **本日 4/27 第6回セッション（BL-0073）で口頭確認** または **LINE で 6.1 のテンプレ送付**
2. Pon さん回答パターン（A/B/C/D）に応じて進路選択:
   - パターン A → v2 手順書通り Phase A〜D 進行
   - パターン B → 手順書 v1 §3.1 を再活用 + v2 を一部修正
   - パターン C → SWIFT 切替で別 BL or BL-0068 のスコープ拡張
   - パターン D → Phase A 先行 / Phase B 後追い
3. Pon さん同意取得後、`mt bl add-decision BL-0068 --type answer --by user --content "Pon さん同意済み・パターン X で進行"` を記録 → 田中さん本人 Phase A 着手

---

## 関連ファイル

- 完全手順 v2: `wise_billing_full_procedure_v2.md`
- 請求書テンプレ v2: `wise_invoice_template_v2.md`
- 候補比較 v1: `Flow/202604/2026-04-26/RestaurantAILab/バンコクPonさん案件/payment_switch_comparison.md`
- BL-0068（ミニタキオン）: `mt bl get BL-0068 --human`
