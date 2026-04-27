# PONさん向け 月次請求書テンプレ — Wise Invoice Generator 入力用

- 関連 BL: **BL-0068**
- 上位文書: `wise_billing_full_procedure_v1.md` §5
- 月次請求額: **250,000 JPY 固定**（方式 (B) JPY 建て請求）
- 想定運用: 毎月1日に Invoice 複製 → invoice number と item の月名を更新 → PDF メール送付

---

## 1. Wise Invoice Generator 入力フィールド対応表

Wise ダッシュボード → **Invoices → Create new invoice** で以下を入力。

### 1.1 Invoice info（請求書情報）

| Wise の入力欄 | 入力値（4 月分例） | 月次運用での更新箇所 |
|---|---|---|
| Invoice number | `RAL-2026-04` | **毎月更新**（年月部分だけ書換） |
| Invoice date | `2026-05-01` | **毎月更新**（発行日 = 翌月1日） |
| Due date | `2026-05-15` | **毎月更新**（発行日 + 14 日） |
| Currency | `JPY - Japanese Yen` | 固定 |

> Invoice number 体系: `RAL-YYYY-MM` で月次連番。`RAL` = Restaurant AI Lab の略。年で繰り返し可（4桁年で衝突しない）。

### 1.2 Bill from（請求元 = 田中さん）

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
| Tax ID（任意） | 確定申告で個人事業者番号取得済みなら入力 / 未取得なら空欄 |

> ⚠️ 名義は **Wise 登録名 と完全一致** が必須。漢字氏名で Wise 登録した場合は氏名フィールドに漢字、ローマ字併記は Notes に。

### 1.3 Bill to（請求先 = PONさん側）

[Q-A 回答により分岐]

#### A. Q-A = 法人 を選択した場合

| Wise の入力欄 | 入力値 |
|---|---|
| Name / Business name | `Rio's Innovation Co., Ltd.` |
| Contact person | `Mr. Pon Kondo` |
| Address line 1 | （バンコク本社住所 1 行目・英語表記） |
| Address line 2 | （建物名等） |
| City | `Bangkok` |
| Postal code | （郵便番号） |
| Country | `Thailand` |
| Email | （Q-G で確認した請求書受取メール） |
| Tax ID（任意） | タイ法人税登録番号（PONさん側に確認） |

#### B. Q-A = 個人 を選択した場合

| Wise の入力欄 | 入力値 |
|---|---|
| Name | `Mr. Pon Kondo` |
| Address line 1 | （PONさん個人住所） |
| City | `Bangkok` |
| Country | `Thailand` |
| Email | （Q-G で確認した請求書受取メール） |

### 1.4 Items（請求項目）

| Description | Quantity | Unit price | Amount |
|---|---|---|---|
| `AI Strategy & Development Consulting Fee — April 2026` | `1` | `250,000` | `250,000 JPY` |

> **項目テンプレ**: `AI Strategy & Development Consulting Fee — {YYYY年M月}`
> 月次運用での更新箇所: 月名（April 2026 → May 2026 → ...）のみ書換。

### 1.5 合計（自動計算）

| 項目 | 値 |
|---|---|
| Subtotal | `250,000 JPY` |
| Tax | `0`（輸出免税のため非表示でもOK） |
| **Total** | **`250,000 JPY`** |

### 1.6 Notes / Bank details（備考・振込先）

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

> **重要**: Bank details は §2.4 で田中さん Wise 個人アカウントに発行された **JPY 受取専用口座情報** を **そのまま貼る**。みずほ等の田中さん最終受取口座を貼ってはいけない（Wise を経由しないと為替変換されないため）。

---

## 2. 請求書送付メール テンプレ

### 2.1 件名

```
[Invoice RAL-2026-04] AI Consulting Fee — April 2026 (JPY 250,000)
```

> 月次運用: `RAL-YYYY-MM` と `MMMM YYYY`（月名）と `JPY 250,000` の3点を月次更新。

### 2.2 本文（日本語＋英語併記）

```
PONさん

いつもお世話になっております。

2026年4月分のAIアドバイザリー業務料の請求書を添付いたします。

  - 請求番号: RAL-2026-04
  - 金額: 250,000 JPY
  - 支払期日: 2026年5月15日
  - 振込方法: Wise（PDF記載の振込先へ）

ご不明点ありましたらお知らせください。
今後ともよろしくお願いいたします。

----

Hi Pon-san,

Please find attached the invoice for AI advisory services for April 2026.

  - Invoice No.: RAL-2026-04
  - Amount: 250,000 JPY
  - Due date: 15 May 2026
  - Payment: Wise (see PDF for bank account details)

Please let me know if you have any questions.

Best regards,
Rikuu Tanaka
Restaurant AI Lab
setup@restaurantailab.core-driven.com
```

---

## 3. 月次運用での更新箇所チェックリスト（5分）

毎月1日に Wise Invoice ダッシュボードで以下を実行:

- [ ] 前月の Invoice を **Duplicate（複製）**
- [ ] **Invoice number** を `RAL-YYYY-MM` の今月分に書換
- [ ] **Invoice date** を当月1日に書換
- [ ] **Due date** を当月15日に書換
- [ ] **Items の Description** を `AI Strategy & Development Consulting Fee — {当月名} {年}` に書換
- [ ] Unit price `250,000` ／ Quantity `1` ／ Currency `JPY` を確認（変更なしのはず）
- [ ] PDF をダウンロード
- [ ] PONさんへメール送付（§2 のテンプレで件名・本文の月次部分を更新）

> 5回程度繰り返したら、田中さんの手元で Markdown テンプレを `monthly_billing_log.md` 等で管理する運用に格上げ。BL-0046 完了後はミニタキオン定期タスクに乗せる。

---

## 4. 年明け（年次更新）の注意

- Invoice number は `RAL-2027-01` から開始（年で連番リセット OK）
- 確定申告のタイミングで **前年12回分の Wise 取引履歴 CSV** をダウンロードしておく → 売上計上の証跡

---

## 関連

- 完全手順: `wise_billing_full_procedure_v1.md`
- 候補比較: `Flow/202604/2026-04-26/RestaurantAILab/バンコクPonさん案件/payment_switch_comparison.md`
- 確認事項: `Flow/202604/2026-04-27/_orchestration/INBOX.md` § BL-0068
