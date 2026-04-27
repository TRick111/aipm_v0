# PONさんへの月次請求 — Wise 完全運用手順 v2（25万円/月・LINE請求・遡及3件含む）

- 対象 BL: **BL-0068**
- 作成日: 2026-04-27（v1 の前提を田中さん回答反映 → v2 確定）
- 担当: 田中利空（受取 / 日本）— Pon さん（送金 / バンコク・**個人 Wise** ）
- 月次請求額: **250,000 JPY 固定 / 月**（毎月発生）
- 上位文書: `wise_billing_full_procedure_v1.md`（10章版）／ `payment_switch_comparison.md`（5候補比較）

---

## 0. v1 → v2 の確定差分（田中さん回答 2026-04-27 反映）

| 項目 | v1 想定 | v2 確定 |
|---|---|---|
| 送金者名義 (Q-A) | 法人/個人/併用の3案 | **Pon さん個人 Wise 単一**（Rio's Innovation 法人ルートは不採用） |
| 初回支払い (Q-B) | 5月上旬・中旬・末で選択 | **急ぎではない**。ただし **2月分・3月分の遡及** + 4月分 = 3 件まとめ発行 |
| 月次金額 (Q-C) | (A) THB / (B) JPY / (C) USD で選択 | **(B) JPY 250,000 円固定** |
| 受取口座 (Q-D) | 既存メイン or 新設 or 滞留 | **みずほメインバンク**（事業所得もここに合算） |
| PONさん側決裁 (Q-E) | Pon 一人 / 経理同意要 / 不明 | **Pon さん一人で決済可** |
| SWIFT バックアップ (Q-F) | 即時/後回し/不要 | **不要**（v2 §8 削除） |
| 請求書送付経路 (Q-G) | (a) 個人メール / (b) 経理 CC / (c) 法人代表 | **LINE トークに PDF 添付**（メール非採用） |

---

## 1. 全体ロードマップ（確定版）

```
[Phase A] 田中さん側 Wise 個人開設（当日〜3 営業日 / KYC マイナンバー）
   ↓
[Phase B] Pon さん個人 Wise 開設（タイ・1〜3 日）
   ↓
[Phase C] テスト送金 100〜500 THB で経路確認（任意・推奨）
   ↓
[Phase D] 遡及3件まとめ発行
   - Invoice RAL-2026-02 (2月稼働分: 2026-02-19 〜 2026-03-18)  250,000 JPY
   - Invoice RAL-2026-03 (3月稼働分: 2026-03-19 〜 2026-04-18)  250,000 JPY
   - Invoice RAL-2026-04 (4月稼働分: 2026-04-19 〜 2026-05-18)  250,000 JPY
   → LINE で田中さんから Pon さんへ 3 件送付 → Pon さん Wise から田中さん Wise へ送金
   ↓
[Phase E] 5月以降の月次運用に移行（毎月19日締め・翌月初発行・翌月15日着金目安）
```

> 「急ぎではない」ため Phase A〜D は本日着手でなくて OK。ただし **Phase A は田中さん本人作業で当日〜3 日かかる** ので、開始日を意識的に決めた方が遅延しにくい。

---

## 2. Phase A — 田中さん（受取側）Wise 個人アカウント開設

> **所要日数: 当日〜3 営業日**（多くは 12 時間以内に審査完了）。月25万円ペースは Wise 個人の年間上限内（年300万円程度・国別で多少変動）。

### 2.1 事前準備（5 分・揃えるもの）

- [ ] **本人確認書類**: マイナンバーカード（顔写真付き表面）／運転免許証 顔写真ページ／日本のパスポート 顔写真ページ — どれか 1 つ
- [ ] **マイナンバー通知書類**: マイナンバーカード裏面 or 通知カード or マイナンバー記載住民票
- [ ] **住所確認書類**（過去 3 ヶ月以内発行）: 公共料金領収書／クレジットカード明細／住民票／賃貸契約書 のいずれか
- [ ] **セルフィー**（スマホで撮影。本人確認書類と顔が同フレームの写真）
- [ ] **みずほ メインバンクの口座情報**: 銀行名 `みずほ銀行` ／ 支店名 ／ 口座種別（普通） ／ 口座番号 ／ 名義（カナ）

### 2.2 アカウント作成（PCブラウザ推奨・10 分）

1. https://wise.com/jp/ にアクセス
2. 右上「Sign up」→「**Personal account**」を選択
3. メール + パスワード設定（推奨: `setup@restaurantailab.core-driven.com` か田中さん個人メール）
4. 居住国: **日本**
5. 携帯電話番号で SMS 認証
6. 個人情報入力（本名漢字・カナ・生年月日・住所・職業）
7. **マイナンバー入力**

### 2.3 KYC 本人確認（5〜30 分・審査 12 時間以内）

8. 本人確認書類の表裏を撮影アップロード
9. セルフィー撮影
10. 住所確認書類アップロード
11. 「Submit for verification」
12. メール通知で審査完了を待つ（多くは数時間〜12 時間 / 混雑時 1〜3 営業日）

> 不備で再提出になる最頻ケース: 「住所書類の発行日が 3 ヶ月超」「マイナンバーが不鮮明」。

### 2.4 受取用 JPY 口座情報の発行 + みずほ出金先登録

13. ダッシュボード → **Recipients / 口座情報** → 「**JPY を受け取る**」
14. **田中さん専用の JPY 口座番号** が発行される（銀行コード `0200` / `Wise Payments Japan` / 支店名 / 口座番号 / 口座名義 ローマ字）。**§5 でこの情報を Pon さんへ LINE で共有する**
15. ダッシュボード → **設定 → 出金先銀行口座** → **みずほ銀行** メインバンクを登録
    - 口座名義は Wise 登録氏名（漢字 or カナ）と完全一致が必要。**みずほの届出名義と一致させる**
    - 名義不一致だと組戻しになるため、Wise 登録時の漢字氏名と銀行届出を必ず照合

### 2.5 動作確認（任意・推奨）

16. **テスト送金 1,000 円** を自分のみずほ口座 → Wise の JPY 口座番号 へ振込
17. Wise アプリで「入金あり」通知 → ダッシュボードに残高反映を確認
18. 残高 → みずほ出金 → 着金確認
19. これで **Pon さん経路でも同じ動作** が回ることが事前確認できる

---

## 3. Phase B — Pon さん個人 Wise 開設（タイ・1〜3 日）

> Q-A 確定により **法人 Business 開設は不要**。個人 Wise 単一ルート。

### 3.1 Pon さん側で必要なもの

- パスポート 顔写真ページ
- 住所確認書類（タイ国内、3 ヶ月以内）
- セルフィー
- タイ国内銀行口座（バーツ建て、引落元として）

### 3.2 Pon さん側の手順（田中さんから案内する内容）

1. https://wise.com/ で Personal account 作成
2. 居住国: **Thailand**
3. KYC（書類アップロード + セルフィー）
4. 引落用のタイ国内銀行口座を Wise に登録
5. 審査完了通知を待つ（多くは 12 時間以内）

### 3.3 Pon さんへの依頼メッセージ（LINE 送信用テンプレ）

```
Pon-san,

Please open a personal Wise account so we can switch from PayPal.

Steps (takes ~1 hour total + verification ~1 day):
1. Go to https://wise.com/
2. Click "Sign up" → "Personal account"
3. Country: Thailand
4. Upload passport + selfie + address proof (within 3 months)
5. Link your Thai bank account (THB)

Once verified, please let me know.
I'll send you 3 invoices for Feb / Mar / Apr together.
Each invoice = 250,000 JPY. You'll send via Wise to my JPY account.

Thanks!
```

> 田中さんが本テンプレを LINE に貼って Pon さんへ送る。タイ語が必要なら次回セッション (BL-0073) ついでに口頭で補足。

### 3.4 タイ Wise の 2026-05-19 移行について

Wise はタイ国内ユーザー向けに **2026-05-19 以降、Wise の現地ライセンス済法人** 経由のサービスへ移行中。Pon さん側は移行を **意識せず継続利用可能**（Wise 側で内部切替）。新規開設も移行後に問題なく可能。

---

## 4. 顧客（送金元）情報の登録

田中さん側 Wise の **Contacts**（連絡先）に Pon さん個人を登録しておくと、§5 で請求書発行が早い。

1. ダッシュボード → **Contacts** → **Add a contact**
2. 入力:
   - Name: `Mr. Pon Kondo`（パスポート表記に合わせる。漢字「近藤」表記は可）
   - Email: 任意（**LINE 運用なので空欄でも可**）
   - Country: **Thailand**
   - Currency: **JPY**

> Q-G 回答でメール送付は採用されないため、Email 欄は空でも運用上問題なし。Wise 上での識別用にだけ使う。

---

## 5. 月次請求書発行（25万円 × 3 件 まとめ発行 / その後は月次）

### 5.1 Wise Invoice Generator の利用

ダッシュボード → **Invoices** → **Create new invoice**。PDF 出力 → ダウンロードして **LINE で送付**（Wise の送信機能は使わない）。

### 5.2 Phase D — 遡及 3 件の発行（初回バッチ）

田中さん回答の「2 月稼働分・3 月稼働分の請求が必要」に対応。**4 月稼働分も同タイミングで発行** すれば、4 件ではなく 3 件で 5 月以降の月次運用に乗れる。

| Invoice No. | 稼働期間 | Invoice date | Due date | 金額 | 摘要 |
|---|---|---|---|---|---|
| `RAL-2026-02` | 2026-02-19 〜 2026-03-18 | 発行日（任意・推奨 Phase A 完了直後） | 発行日 + 14 日 | **250,000 JPY** | February 2026 工数分 |
| `RAL-2026-03` | 2026-03-19 〜 2026-04-18 | 同上 | 同上 | **250,000 JPY** | March 2026 工数分 |
| `RAL-2026-04` | 2026-04-19 〜 2026-05-18 | 同上 | 同上 | **250,000 JPY** | April 2026 工数分 |

> **発行タイミング**: Phase A 完了直後の 1 日（任意の同日）に 3 件まとめ発行が最もシンプル。Pon さん側の支払いも 3 件まとめて送金してもらう（Wise なら 3 件分でも手数料は通常通り）。

### 5.3 Invoice Generator 入力フィールド（1 件あたり）

| Wise の入力欄 | 入力値（2 月分例） |
|---|---|
| Invoice number | `RAL-2026-02` |
| Invoice date | （発行日。例: 2026-04-30） |
| Due date | （発行日 + 14 日。例: 2026-05-14） |
| Currency | `JPY` |
| Bill from | `Rikuu Tanaka` ／ `Restaurant AI Lab` ／ 住所 ／ Email ／ 電話 |
| Bill to | `Mr. Pon Kondo` ／ Bangkok ／ Thailand |
| Item | `AI Strategy & Development Consulting Fee — February 2026 (Work period: 2026-02-19 〜 2026-03-18)` |
| Quantity | `1` |
| Unit price | `250,000` |
| Subtotal | `250,000 JPY` |
| Tax | `0`（輸出免税） |
| Total | **`250,000 JPY`** |
| Notes / Bank details | Wise JPY 口座情報（§2.4 で発行された 銀行コード 0200 ／ Wise Payments Japan ／ 支店名 ／ 口座番号 ／ 口座名義 ローマ字） |

3 月分・4 月分は **Duplicate（複製）** → Invoice number と稼働期間と Item の月名のみ書き換え。所要 5 分。

### 5.4 LINE 送付（Q-G 確定運用）

請求書 PDF 3 件をダウンロードして、田中さんから Pon さんへ LINE トークで送付。

#### 5.4.1 送付メッセージ テンプレ（LINE 1 通目: 説明）

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

#### 5.4.2 PDF 添付

1 通目のテキスト送信後、**3 つの PDF を続けて送信**（LINE は 1 通あたり PDF 1 ファイルが扱いやすい）。

#### 5.4.3 既読確認

LINE の既読マークを目視確認。返信がない場合は §7 のリマインドルールで対応。

### 5.5 消費税の扱い（v1 §5.5 と同一）

田中さんがフリーランスとして国外個人 Pon さん（バンコク在住）に役務提供する場合、消費税法上の **輸出免税（不課税）** に該当。

- 請求書には消費税 0 表記
- 確定申告では「輸出取引等の対価の額」欄に計上
- インボイス制度対応は、国外取引なのでインボイス番号未取得でも輸出免税の取扱は維持
- ⚠️ 詳細は税理士確認推奨（BL-0014 確定申告タスクと連携）

---

## 6. 入金確認・記帳

### 6.1 着金検知

Wise から「**You've received 250,000 JPY**」のメール / アプリ通知（Pon さん送金から数時間以内が目安）。3 件分まとめて Pon さんが送る場合は 3 通の通知が来る。

### 6.2 みずほへ出金

1. Wise ダッシュボード → 残高 → **Send to bank account**
2. 出金先: §2.4 で登録した **みずほ メインバンク**
3. JPY → JPY の同通貨出金は **手数料無料**（営業日内に着金）
4. 着金通知（みずほアプリ / 通帳）を受けて記帳

### 6.3 記帳（事業所得 / 確定申告用）

- 日付: **みずほ着金日**
- 勘定科目: `売上高（コンサルティング料）`
- 摘要: `Pon Kondo (Bangkok) / Invoice RAL-2026-MM`
- 金額: `250,000 円`
- 区分: **輸出免税**

会計ソフト（freee / マネーフォワード / 弥生等）を使う場合は Wise 取引履歴 CSV を月次インポート。

### 6.4 領収書発行（Pon さん要請時のみ）

要求があれば Wise Invoice テンプレを Duplicate → タイトル `Receipt`、Receipt date を着金日に書換 → PDF → LINE で送付。

---

## 7. 月次運用カレンダー（Phase E ＝ 5 月以降のルーチン）

| 日付 | アクション | 担当 | 所要 | チェック |
|---|---|---|---|---|
| 毎月18日 | 当月稼働分の確定（19日〜翌18日の 1 ヶ月分。25万円固定なので額確認のみ） | 田中さん | 2 分 | [ ] |
| 翌月1日 | Wise Invoice 複製 → invoice number と稼働期間と月名を更新 | 田中さん | 5 分 | [ ] |
| 翌月1〜3日 | PDF をダウンロード → **LINE で Pon さんへ送付**（§5.4 テンプレ） | 田中さん | 3 分 | [ ] |
| 翌月15日（Due） | 入金確認（Wise アプリ通知） | 田中さん | 1 分 | [ ] |
| 翌月15日以降未着 | LINE で Pon さんへリマインド | 田中さん | 3 分 | [ ] |
| 翌月20日まで | Wise → みずほへ出金 | 田中さん | 3 分 | [ ] |
| 月次 | 会計ソフトに記帳 | 田中さん | 10 分 | [ ] |

### 7.1 リマインダ設定

- **iCloud カレンダー定期予定**:
  - 「毎月1日 09:00 — Wise 請求書を Pon さんへ LINE 送付」
  - 「毎月15日 09:00 — Wise 入金確認 + 未着ならリマインド」
- **AIOS / ミニタキオン**: BL-0046（定期タスク設計）完了後にルーチン BL として登録

> 5 件程度ルーチンが回ったら、本書 §7 を `Stock/RestaurantAILab/バンコクPonさん案件/recurring_billing.md` に昇格 → BL-0046 経由で月次タスク自動投入。

---

## 8. リスク・既知の落とし穴（v1 §9 から SWIFT 関連を削除）

| リスク | 対処 |
|---|---|
| Wise 送金者名義不一致 → 組戻し | §2.5 のテスト送金で名義整合性を確認。Pon さん本人名義 Wise → 田中さん本人名義 Wise なら問題なし |
| タイ BOT 規制 2026-05-19 移行で送金一時不可 | Phase A〜D を 5 月までに動作確認完了させれば回避可。5 月以降は Wise Thailand local entity が継続提供 |
| 田中さん側 KYC で住所書類が古い → 再提出 | §2.1 で発行 3 ヶ月以内を確認 |
| Pon さん側 KYC が落ちた | パスポート再撮影 + タイ国内住所書類の鮮明版で再提出。田中さんが LINE で Pon さんに連絡 |
| 確定申告での輸出免税の処理ミス | §5.5 を税理士確認。BL-0014 確定申告タスクで併せて対応 |
| LINE で PDF を Pon さんが見落とし | §7.1 でリマインダ設定。15 日 Due で未着なら即 LINE で再送 |
| 月次 25 万円が為替変動で Pon さん側で重く感じる | 方式 (B) JPY 建てなので Pon さん側コストが為替次第で増減。THB 建て要望が出たら方式 (A) に切替検討（ただし田中さん手取り変動するため非推奨） |

---

## 9. 田中さんネクストアクション（本書完了直後）

1. **Phase A 着手**: §2.1 の必要書類を揃えて https://wise.com/jp/ で個人 Wise 開設（当日〜3 日）
2. **Phase B 起動**: §3.3 の依頼メッセージを LINE で Pon さんへ送付（タイミングは Phase A 申請直後でも、Phase A 完了後でも可）
3. **テスト送金**（任意）: §2.5 でみずほ→Wise→みずほ の往復確認
4. **Phase D 発行**: 両者 Wise 完了後、§5.2 の 3 件まとめ発行 → §5.4 LINE 送付
5. **入金確認**: §6 で着金 → みずほ出金 → 記帳
6. **5 月以降は §7 の月次ルーチン** で運用継続。BL-0046 完了後にミニタキオン定期タスクへ昇格

---

## 付録: 想定 Q&A

**Q. PayPal の既存契約は解約していい？**
→ Phase D で初回 3 件分が無事着金確認できたら停止 OK。停止前に Pon さんに「以後は Wise でお願いします」と LINE で一報。

**Q. 2 月分・3 月分の請求が遅れたことを Pon さんに説明する必要は？**
→ §5.4.1 の LINE テンプレで「PayPal から Wise への切替に伴い、まとめて」と説明済。追加説明不要。

**Q. 25 万円から金額変更があったら？**
→ Wise Invoice 複製時に Unit price だけ書き換える。月次運用は維持。

**Q. 為替が大きく動いた月、田中さんの手取りが減らない？**
→ 方式 (B) JPY 固定なので **田中さん側は常に 250,000 円固定**。減るのは Pon さん側（送金側）。為替不利月は Pon さん側コストが増える。

**Q. Pon さんが Wise 開設に時間がかかったら 2 月分の請求が更に遅れる？**
→ 「急ぎではない」と田中さん回答済。Phase B が 1〜2 週遅れる程度なら全体スケジュールに影響なし。

**Q. LINE で PDF を送るのは安全？**
→ LINE トーク内は E2E 暗号化。Wise 口座情報自体は **PDF 受領者が支払うために必要な情報** なので、Pon さん 1 名のトークで送る限り問題なし。グループトークには絶対送らない。

---

## 関連ファイル

- v1 完全手順（前提仮置き版）: `wise_billing_full_procedure_v1.md`
- 候補比較: `Flow/202604/2026-04-26/RestaurantAILab/バンコクPonさん案件/payment_switch_comparison.md`
- 請求書テンプレ v2（LINE 送付対応）: `wise_invoice_template_v2.md`
- バックログ: `Stock/定型作業/バックログ/Backlog.md` BL-0068
- 案件 STATUS: `Stock/RestaurantAILab/バンコクPonさん案件/STATUS.md`

---

## 参考リンク（実画面で再確認）

- Wise 個人開設: https://wise.com/jp/
- Wise 日本本人確認ガイド: https://wise.com/help/articles/2968293/getting-verified-in-japan
- Wise Invoice 機能: https://wise.com/help/articles/3PBeSfyBJ22iAsQD49HEbE/getting-paid-to-your-wise-business-by-invoice
- Wise JPY 口座情報（銀行コード 0200）: https://wise.com/ja/help/articles/4aS54s32KbEkl1KMonAjJV
- タイ Wise 移行（2026-05-19〜）: https://huahintoday.com/thailand-news/wise-rolls-out-overseas-transfers-and-promptpay-access-in-thailand/

> **本書は v2（確定版）**。5 月以降の月次ルーチンが安定したら `Stock/RestaurantAILab/バンコクPonさん案件/` 配下へ Finalize（移送）する。
