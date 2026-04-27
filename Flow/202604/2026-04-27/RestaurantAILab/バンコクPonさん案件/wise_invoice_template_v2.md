# PONさん向け 月次請求書テンプレ v2 — Wise Invoice + LINE 送付（25万円固定）

- 関連 BL: **BL-0068**
- 上位文書: `wise_billing_full_procedure_v2.md` §5
- 月次請求額: **250,000 JPY 固定**（方式 (B) JPY 建て請求）
- 送付経路: **LINE トークに PDF 添付**（メール非採用）
- 想定運用: 毎月1日に Wise Invoice を複製 → invoice number / 月名 / 稼働期間 を更新 → PDF を LINE で Pon さんへ送付

---

## 1. 初回バッチ（Phase D）— 遡及 3 件

田中さん 2026-04-27 確定: 2 月稼働分・3 月稼働分の遡及 + 4 月稼働分 = **3 件まとめ発行**。

| Invoice No. | 稼働期間（19 日締め月初発行） | 金額 |
|---|---|---|
| `RAL-2026-02` | **2026-02-19 〜 2026-03-18** | 250,000 JPY |
| `RAL-2026-03` | **2026-03-19 〜 2026-04-18** | 250,000 JPY |
| `RAL-2026-04` | **2026-04-19 〜 2026-05-18** | 250,000 JPY |
| | **合計** | **750,000 JPY** |

---

## 2. Wise Invoice Generator 入力フィールド対応表

Wise ダッシュボード → **Invoices → Create new invoice** で以下を入力。

### 2.1 Invoice info（請求書情報）

| Wise の入力欄 | 入力値（2 月分例） | 月次運用での更新箇所 |
|---|---|---|
| Invoice number | `RAL-2026-02` | 毎月更新（年月部分のみ書換） |
| Invoice date | （発行日。Phase D は 3 件同日発行を推奨） | 毎月更新 |
| Due date | （発行日 + 14 日） | 毎月更新 |
| Currency | `JPY - Japanese Yen` | 固定 |

> **Invoice number 体系**: `RAL-YYYY-MM` で月次連番。`RAL` = Restaurant AI Lab の略。年で繰り返し可（4 桁年で衝突しない）。

### 2.2 Bill from（請求元 = 田中さん・固定値）

| Wise の入力欄 | 入力値 |
|---|---|
| Name / Business name | `Rikuu Tanaka` ／ 屋号運用なら `Restaurant AI Lab` |
| Address line 1 | （田中さん住所 1 行目・英語表記） |
| Address line 2 | （建物名等・英語表記） |
| City | `Tokyo` （or 該当区） |
| Postal code | （郵便番号） |
| Country | `Japan` |
| Email | `setup@restaurantailab.core-driven.com` |
| Phone（任意） | （携帯番号 +81 から始まる国際表記） |
| Tax ID（任意） | 個人事業者番号取得済みなら入力 / 未取得なら空欄 |

> ⚠️ 名義は **Wise 登録名 と完全一致** が必須。漢字氏名で Wise 登録した場合は氏名フィールドに漢字、ローマ字併記は Notes に。

### 2.3 Bill to（請求先 = Pon さん個人）

| Wise の入力欄 | 入力値 |
|---|---|
| Name | `Mr. Pon Kondo` |
| Address line 1 | （Pon さん個人住所・パスポートと一致） |
| City | `Bangkok` |
| Postal code | （タイ郵便番号） |
| Country | `Thailand` |
| Email | （任意・LINE 運用なので空欄でも可） |

### 2.4 Items（請求項目）

#### 2 月分

| Description | Quantity | Unit price | Amount |
|---|---|---|---|
| `AI Strategy & Development Consulting Fee — February 2026 (Work period: 2026-02-19 〜 2026-03-18)` | `1` | `250,000` | `250,000 JPY` |

#### 3 月分

| Description | Quantity | Unit price | Amount |
|---|---|---|---|
| `AI Strategy & Development Consulting Fee — March 2026 (Work period: 2026-03-19 〜 2026-04-18)` | `1` | `250,000` | `250,000 JPY` |

#### 4 月分

| Description | Quantity | Unit price | Amount |
|---|---|---|---|
| `AI Strategy & Development Consulting Fee — April 2026 (Work period: 2026-04-19 〜 2026-05-18)` | `1` | `250,000` | `250,000 JPY` |

> **項目テンプレ**: `AI Strategy & Development Consulting Fee — {Month YYYY} (Work period: YYYY-MM-19 〜 YYYY-MM+1-18)`
> 月次運用での更新箇所: 月名 + 稼働期間 のみ書換。

### 2.5 合計（自動計算）

| 項目 | 値 |
|---|---|
| Subtotal | `250,000 JPY` |
| Tax | `0`（輸出免税のため非表示でも OK） |
| **Total** | **`250,000 JPY`** |

### 2.6 Notes / Bank details（備考・振込先 / 全月共通）

```
Please remit JPY 250,000 to the bank account below via Wise.

Bank name: Wise Payments Japan
Bank code: 0200
Branch: (Wise が割当てた支店名)
Account type: Saving
Account number: (Wise が割当てた口座番号)
Account holder: RIKUU TANAKA (must match exactly)

Note: This service is exempt from Japanese consumption tax
as it qualifies as export of services.

Thank you for your continued partnership.
```

> **重要**: Bank details は §2.4（v2 手順書）で田中さん Wise 個人アカウントに発行された **JPY 受取専用口座情報** を **そのまま貼る**。みずほの口座を直接貼ってはいけない（Wise を経由しないと為替変換されないため）。

---

## 3. LINE 送付テンプレ（Q-G 確定運用）

### 3.1 Phase D — 遡及 3 件 まとめ送付（初回）

LINE で 1 通目（テキスト）→ 2〜4 通目（PDF 各 1 枚）の順で送る。

#### 1 通目（テキスト）

```
Pon-san、ご無沙汰しております。
Wise アカウントの準備ありがとうございます。

PayPal から Wise への切替に伴い、2 月稼働分以降の請求書をまとめてお送りします。
各 250,000 JPY、合計 750,000 JPY のお支払いをお願いします。

【請求 3 件】
① 2026年2月稼働分 (Feb 19 – Mar 18)  250,000 JPY  Invoice RAL-2026-02
② 2026年3月稼働分 (Mar 19 – Apr 18)  250,000 JPY  Invoice RAL-2026-03
③ 2026年4月稼働分 (Apr 19 – May 18)  250,000 JPY  Invoice RAL-2026-04

支払期日: 5月15日まで（急ぎではないので無理のない範囲で OK）
振込先: Wise（PDF 記載の JPY 口座へ送金）

Wise の使い方は別添 PDF か、必要なら次回セッションで一緒に確認します。

----

Hi Pon-san,
Following our switch from PayPal to Wise, please find attached three invoices:

① Invoice RAL-2026-02 — Feb 2026 work  250,000 JPY
② Invoice RAL-2026-03 — Mar 2026 work  250,000 JPY
③ Invoice RAL-2026-04 — Apr 2026 work  250,000 JPY
   Total: 750,000 JPY  Due: 15 May 2026

Please send via your Wise account to the JPY account shown in the PDFs.
Let me know if you have any questions.

Best,
Rikuu
```

#### 2〜4 通目（PDF 添付・1 ファイルずつ）

LINE は 1 通あたり PDF 1 ファイルが見やすい。順番:
1. `RAL-2026-02.pdf`（2 月分）
2. `RAL-2026-03.pdf`（3 月分）
3. `RAL-2026-04.pdf`（4 月分）

### 3.2 Phase E — 月次運用（5 月以降のルーチン送付）

#### 1 通目（テキスト）

```
Pon-san、お疲れさまです。
{YYYY 年 M 月} 稼働分の請求書を送ります。

  - 請求番号: RAL-YYYY-MM
  - 金額: 250,000 JPY
  - 稼働期間: YYYY-MM-19 〜 YYYY-MM+1-18
  - 支払期日: {翌月15日}
  - 振込: Wise（PDF 記載の JPY 口座へ）

ご不明点あればお知らせください。

----

Hi Pon-san,
Invoice for {Month YYYY} work attached.

  - No: RAL-YYYY-MM   Amount: 250,000 JPY
  - Period: YYYY-MM-19 to YYYY-MM+1-18
  - Due: {15 of next month}
  - Pay via Wise (see PDF)

Best,
Rikuu
```

#### 2 通目（PDF 添付）

`RAL-YYYY-MM.pdf` を添付。

---

## 4. 月次運用での更新箇所チェックリスト（5 分 / 月）

毎月 1 日に Wise Invoice ダッシュボードで:

- [ ] 前月の Invoice を **Duplicate（複製）**
- [ ] **Invoice number** を `RAL-YYYY-MM` の今月分に書換
- [ ] **Invoice date** を当月 1 日に書換
- [ ] **Due date** を当月 15 日に書換
- [ ] **Items の Description** を `... — {当月名} {年} (Work period: YYYY-MM-19 〜 YYYY-MM+1-18)` に書換
- [ ] Unit price `250,000` ／ Quantity `1` ／ Currency `JPY` を確認（変更なしのはず）
- [ ] PDF をダウンロード
- [ ] LINE トーク（Pon さん 1:1）を開く
- [ ] §3.2 のテキストテンプレを送信
- [ ] PDF を続けて添付送信
- [ ] 既読確認

> 5 ヶ月程度ルーチンが回ったら、田中さんの手元で Markdown テンプレを `monthly_billing_log.md` 等で管理する運用に格上げ。BL-0046 完了後はミニタキオン定期タスクに乗せる。

---

## 5. 年明け（年次更新）の注意

- Invoice number は `RAL-2027-01` から開始（年で連番リセック OK）
- 確定申告のタイミングで **前年 12 回分の Wise 取引履歴 CSV** をダウンロードしておく → 売上計上の証跡
- 2027 年 2 月以降の月次運用は §3.2 のテンプレで継続（特例なし）

---

## 6. LINE 送付運用の注意点

| 項目 | 対応 |
|---|---|
| 送り間違い防止 | **Pon さん 1:1 トーク** にしか送らない。グループトーク禁止 |
| 既読が付かない | 24 時間後にリマインド「先ほどの請求書、確認お願いします」 |
| PDF が開けない | LINE 上で「ファイルを開く」が動かないケースあり → Pon さん側で「保存」してから別アプリで開く案内 |
| 履歴が流れる | LINE トーク内で `RAL-2026-MM` で検索可能。田中さん側でも `monthly_billing_log.md` に送信記録（送信日 / 既読日 / 入金日） |
| Pon さん側 LINE 通知 OFF | 重要送付時は LINE 通話か別途連絡で「LINE 確認お願いします」と一報 |

---

## 関連

- 完全手順 v2: `wise_billing_full_procedure_v2.md`
- 完全手順 v1（参考）: `wise_billing_full_procedure_v1.md`
- 候補比較: `Flow/202604/2026-04-26/RestaurantAILab/バンコクPonさん案件/payment_switch_comparison.md`
- BL-0068: ミニタキオン UI から `mt bl get BL-0068` で確認
