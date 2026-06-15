# 【マスター】シェフズルーム ダッシュボード AI参照用 仕様マニュアル v1

> **このファイルの使い方**
> - これは LLM（ChatGPT / Claude 等）が参照するための仕様マニュアルの **マスターインデックス** です
> - 詳細仕様は機能別ファイルに分割されています。必要に応じて参照先ファイルを読み込んでください
> - すべて同一ディレクトリ `manuals/` 配下に配置されています
> - 最終更新: 2026-06-15 / Dashboard 本体バージョン: Phase A〜H 後継

---

## 0. リファレンス構成

| ファイル | 内容 |
|---------|------|
| **`AI参照用_仕様マニュアル_v1.md`**（本書） | 全体マスター。共通仕様・用語・ロール・認証・LINE・管理機能・FAQ |
| `ai-reference/POSダッシュボード.md` | 売上ダッシュボード（9タブ）／売上CSVアップロード詳細 |
| `ai-reference/PLダッシュボード.md` | PL管理（日次入力・着地予想・月次目標・売上控除・営業日・日報・カテゴリ管理） |
| `ai-reference/週報.md` | 週報・月報機能（HTMLアップロード／閲覧／印刷／LINE配信との関係） |

> **参照優先順序**: ユーザーの質問が PL/POS/週報 に絞れる場合は該当ファイルを読む。それ以外（ログイン・LINE・管理者・全体設定・エラーコード）は本書を読む。

---

## 1. プロダクト概要

- **名称**: 飲食店売上分析ダッシュボード（シェフズルーム × RestaurantAILab）
- **提供形態**: SaaS（Next.js 14 App Router / Vercel ホスティング / Neon PostgreSQL / Vercel Blob）
- **対象POS**: ぽっくんPa（3形式自動判定）／ Airレジ ／ USENレジ ／ スマレジ ／ Dinii（2ファイル）／ 列マッピング汎用
- **3環境構成**: Development (dev) / Staging (staging) / Production (main)
- **基本URL構造**: `/store/{storeCode}/...` で店舗固有のページに到達

### 1.1 機能カテゴリ（全機能の俯瞰）

| カテゴリ | 主な機能 | 参照ファイル |
|---------|---------|-------------|
| 認証 | ログイン（店舗 / グループ）／ デモログイン／ 日報パスワード認証 | 本書 §3 |
| 売上分析 | 売上CSVアップロード／ 9タブダッシュボード | POSダッシュボード.md |
| 経営管理 | PL日次入力／ 着地予想／ 月次目標／ 月次推移／ 売上控除／ 営業日／ CSVエクスポート | PLダッシュボード.md |
| 日報 | 店員日報（AI深掘り）／ 店長日報＋自動店舗まとめ／ LINE通知 | 本書 §6 + PL管理に隣接 |
| レポート | 週報・月報のHTMLアップロード／ 閲覧／ 印刷／ PDF保存 | 週報.md |
| LINE連携 | グループ参加検知 → ペアリングコード → 店舗紐付け → 日報＋売上速報送信 | 本書 §7 |
| 管理機能 | 店舗 / グループ CRUD／ 全体設定（プロンプト3種）／ フィーチャーフラグ | 本書 §8 |

---

## 2. 用語集

| 用語 | 英名 | 意味 |
|------|------|------|
| 店舗コード | storeCode | 各店舗の英数字ID。ログインIDとして使用 |
| グループコード | storeGroupCode | 複数店舗にアクセスできる共通ID（外注コンサル等） |
| ロール | role | `admin` / `store` / `group` の3種 |
| 営業日付 | business day date | businessDayCutoffHour（既定 5:00 JST）を境とした営業上の日付 |
| 営業日切り替え時刻 | businessDayCutoffHour | 0–23 の整数。深夜営業対応。例: 5 → 0:00〜4:59 は前日扱い |
| 会計ID | accountId | 1会計（レシート）を一意に識別するキー |
| 売上カテゴリ | sales category | ランチ／ディナー／コース 等。店舗ごとに自由定義 |
| 経費カテゴリ | expense category | 食材費／人件費／光熱費 等。経費グループに所属 |
| 経費グループ | expense category group | 原価／販管費 等の上位階層 |
| 経費種別 | expense type | RECURRING（定常）／ ONE_TIME（例外） |
| FLコスト | FL cost | 食材費 + 人件費。FL率 = FLコスト / 売上 |
| 着地予想 | landing forecast | 月末予測値。詳細は PLダッシュボード.md §4 |
| 売上控除ルール | sales deduction rule | 売上カテゴリの一部を自動控除（+ 経費へ振替）するルール |
| 客単価除外カテゴリ | exclude-from-avg-spend categories | 売上ダッシュボードで客単価計算から除外するカテゴリ（お土産・物販等） |
| ABC分析 | ABC analysis | 売上構成比でA(0–70%)/B(70–90%)/C(90–100%)に分類 |
| 日報メンバー | daily report member | 日報を書くスタッフ（責任者 or スタッフ） |
| ペアリングコード | pairing code | 6桁・10分有効。LINEグループと店舗を紐付けるコード |
| 店舗まとめ日報 | store summary | 全スタッフの日報をAIで要約したもの |
| 週報／月報 | weekly/monthly report | 管理者がHTMLでアップロード→店舗が閲覧する自己完結型レポート |
| 監査ログ | audit log | 日次売上・日次経費の変更履歴（DBトリガで自動記録） |

---

## 3. 認証・権限

### 3.1 ロール

| ロール | 判定 | アクセス範囲 |
|--------|------|--------------|
| `admin` | `storeCode === 'admin'` でログイン | 全店舗 + `/admin` 管理画面 |
| `store` | 店舗コードでログイン | 自店舗のみ |
| `group` | グループコードでログイン | `accessibleStoreIds` に含まれる店舗 |

### 3.2 ログインフロー

```
POST /api/auth/login { code, password }
  → 店舗認証を試行
  → 失敗時にグループ認証を試行
  → 成功時に session_token Cookie（7日間、HTTPOnly、sameSite=lax）を発行
  → DBに StoreSession / StoreGroupSession を作成
```

### 3.3 デモログイン

```
POST /api/auth/demo
  → storeCode='demo' の店舗にパスワード入力なしでログイン
  → store ロールでセッション発行
```

### 3.4 日報用店舗パスワード認証（セッションを発行しない）

```
POST /api/daily-report/auth { storeCode, password }
  → bcrypt compare で検証
  → 成功時: 店舗名 + ポジション設定を返すのみ（Cookieは発行しない）
```

### 3.5 アクセス制御マトリクス

| リソース | admin | store | group |
|----------|:-----:|:-----:|:-----:|
| `/admin` | ○ | × | × |
| 売上ダッシュボード / PL / 日報 / 週報 閲覧 | 全店舗 | 自店舗 | 所属店舗 |
| 売上CSVアップロード | 任意店舗 | 自店舗のみ | 想定外（API実装上 store ロールのみ） |
| 週報・月報のアップロード / 削除 | ○ | × | × |
| 店舗追加・編集 / グループCRUD / 全体設定 / フィーチャーフラグ | ○ | × | × |
| 日報入力（店舗パスワード認証） | （誰でも、店舗パスワードを知っていれば） | | |

### 3.6 セッション管理

- Cookie名: `session_token`
- 有効期間: 7日（`maxAge` と DB の `expiresAt` の両方で検証）
- 保存先: `StoreSession` / `StoreGroupSession` テーブル
- 期限切れ: `getSession()` 時に自動削除

---

## 4. 共通画面・ナビゲーション

| パス | 画面 | 用途 |
|------|------|------|
| `/login` | ログイン画面 | 全ロール共通 |
| `/group/select` | 店舗選択 | group ロールのログイン直後 |
| `/store/{storeId}` | アプリランチャー | 売上ダッシュボード / PL管理 / 週報・月報 への入口 |
| `/store/{storeId}/sales-dashboard` | 売上ダッシュボード月一覧 | アップロード済み月のカード一覧 + 店舗設定 |
| `/store/{storeId}/dashboard/{YYYY-MM}` | 売上ダッシュボード本体 | 9タブ。POSダッシュボード.md 参照 |
| `/store/{storeId}/upload` | CSVアップロード | POSダッシュボード.md §3 参照 |
| `/store/{storeId}/pl` | PL管理トップ（リダイレクト） | featureFlag.dailyReportOnly=true なら `/pl/daily-reports` へ |
| `/store/{storeId}/pl/dashboard` | PLダッシュボード | PLダッシュボード.md §4 |
| `/store/{storeId}/pl/daily` | PL日次入力 | PLダッシュボード.md §5 |
| `/store/{storeId}/pl/monthly` | 月次目標設定 | PLダッシュボード.md §6 |
| `/store/{storeId}/pl/trends` | PL月次推移 | PLダッシュボード.md §7 |
| `/store/{storeId}/pl/daily-reports` | 日報確認 | 本書 §6 |
| `/store/{storeId}/pl/settings` | PL設定 | PLダッシュボード.md §9 |
| `/store/{storeId}/weekly-reports` | 週報・月報一覧 | 週報.md §3 |
| `/store/{storeId}/weekly-reports/{weekId}` | 週報詳細 | 週報.md §4 |
| `/store/{storeId}/monthly-reports/{monthId}` | 月報詳細 | 週報.md §4 |
| `/daily-report/{storeId}` | 店員日報入力 | スマホ向け。本書 §6 |
| `/admin` | 管理画面（3タブ） | 本書 §8 |

---

## 5. 店舗別機能設定（フィーチャーフラグ / カスタム設定）

### 5.1 featureFlags（管理者のみ操作可）

```typescript
interface FeatureFlags {
  dailyReportPosition?: boolean;  // 日報ポジション選択UI
  lineNotification?: boolean;     // LINE通知の送信
  hideProfit?: boolean;           // 利益情報の非表示
  salesDeduction?: boolean;       // 売上控除・費用振替ルールの設定UI表示
  dailyReportOnly?: boolean;      // PL管理を日報のみに制限（店長は売上を見ない）
}
```

- 操作API: `GET / POST /api/pl/feature-flags?storeId=...`（admin のみ）
- データ: `store_settings.feature_flags` JSON カラム

### 5.2 customSettings（店長＋管理者）

```json
{
  "labor": { "fullTimeHourlyRate": 3000, "partTimeHourlyRate": 1200 },
  "dailyReportPosition": { "options": ["ホール", "キッチン", "ドリンク"] },
  "lineGroupId": "C1234..."
}
```

- 操作API: `GET / POST /api/settings`（店長＋admin）／LINE関連は `/api/line/settings`
- 機能の有効/無効は **featureFlags** 側で管理（customSettings には `enabled` を含めない）

---

## 6. 日報機能

### 6.1 全体フロー

```
店員: /daily-report/{storeId} を開く
  → 店舗パスワード入力 → POST /api/daily-report/auth で検証
  → メンバー選択（GET /api/daily-report/members）
  → 質問取得（GET /api/daily-report/questions?memberId=...）
  → 回答入力 → POST /api/daily-report/stream で SSE 経由のAI深掘り（gpt-4.1、最大2回）
  → POST /api/daily-report/summarize で質問単位の要約
  → POST /api/daily-report/submit で全質問まとめて保存

店長: /store/{storeId}/pl/daily-reports で確認 / 締め
  → POST /api/daily-report/manager-submit
  → 自動: 店舗まとめ日報を生成（gpt-4.1）
  → 自動: LINE通知を送信（featureFlag.lineNotification=true の店舗）
```

### 6.2 スタッフタイプ別質問テンプレート（初期値、現在はDB管理）

| タイプ | 対象 | 質問の狙い | 言語 |
|--------|------|----------|------|
| A: 店舗責任者・幹部 | マネージャー | 売上要因分析・月間目標達成 | 日本語 |
| B: 外国人スタッフ | 一部スタッフ | 自己成長・スキル習得 | 英語 |
| C: 一般スタッフ | 一般 | 接客力・チームワーク向上 | 日本語 |

各タイプは「最大2問」＋「AI深掘りプロンプト（最大2回）」の構成。

### 6.3 プロンプト優先順位

```
店舗個別プロンプト (PL設定で店舗が指定)
  → GlobalSettings（/admin の「全体設定」で admin が指定）
  → lib/daily-report/default-prompts.ts（コード組み込みのデフォルト）
```

### 6.4 LINE通知の内容

「店長日報を送信」または手動の締め操作で配信される:

1. **本日の売上速報**: 累計売上／今月の見込み（着地予想）／達成見込み%
2. **AI一言コメント**（40文字以内、gpt-4o-mini）
3. **日報のまとめ**: 店舗まとめ日報の本文

### 6.5 関連API

| API | 説明 |
|------|------|
| `POST /api/daily-report/auth` | 店舗パスワード検証（セッション発行なし） |
| `GET /api/daily-report/members` | メンバー一覧 |
| `GET /api/daily-report/questions?memberId=...` | メンバーの質問一覧 |
| `POST /api/daily-report/stream` | AI深掘り SSE |
| `POST /api/daily-report/summarize` | 質問単位の要約（gpt-4.1） |
| `POST /api/daily-report/submit` | 日報保存 |
| `POST /api/daily-report/manager-submit` | 店長日報＋自動店舗まとめ＋LINE通知（maxDuration: 30秒） |
| `GET /api/daily-report/reports?mode=...&memberId=...&date=...&limit=...` | 個人日報一覧（mode=date: 指定日のみ / mode=recent: 指定日以前を最大limit件） |
| `GET /api/daily-report/store-summary?storeId=...&date=...&fallback=...` | 日次まとめ日報取得（fallback=true で当日になければ直近を返す） |

---

## 7. LINE連携

### 7.1 紐付けフロー

```
1. 店舗LINEグループに公式アカウントBotを招待
2. Bot参加（join イベント）を /api/line/webhook で受信
3. ペアリングコード（6桁、10分有効）を発行し、グループへ送信
4. ダッシュボード側 PL設定 → LINE設定 にコードを入力
5. POST /api/line/pair でグループIDを StoreSettings.customSettings.lineGroupId に保存
6. 以降、日報送信・締めの際に自動配信
```

### 7.2 設定の取得・変更

```
GET / POST /api/line/settings
  → lineGroupId の取得・設定・解除（クリア）
```

### 7.3 設定 / フラグ

- `customSettings.lineGroupId`: 送信先LINEグループID
- `featureFlags.lineNotification`: ON/OFF（OFF時は送信スキップ）

---

## 8. 管理機能（`/admin`）

admin ロールのみアクセス可能。3タブ構成。

### 8.1 店舗管理タブ

- 店舗一覧。クリックで `/store/{storeId}` へ
- **新規追加**: 店舗ID・店舗名・パスワード（bcrypt rounds=10 でハッシュ化）
  - エラー: ERR-AUTH-009（必須欠落）／ ERR-AUTH-011（ID重複）
- **編集**: 店舗ID変更不可。店舗名必須。パスワード空欄なら据え置き
- **削除**: 機能なし（論理削除も UI 未提供）

| API | 説明 |
|------|------|
| `GET /api/auth/stores` | 店舗一覧 |
| `POST /api/auth/stores` | 新規追加 |
| `PUT /api/auth/stores` | 更新 |

### 8.2 グループ管理タブ

複数店舗にアクセスできるグループアカウント（外注コンサル等向け）。

- グループ名・グループコード・所属店舗・有効/無効
- グループ作成・編集・所属店舗付け替え・削除

| API | 説明 |
|------|------|
| `GET / POST / PUT / DELETE /api/auth/store-groups` | グループCRUD |

ログインは `/login` → グループコード入力 → `/group/select` で店舗選択。

### 8.3 全体設定タブ（GlobalSettings）

全店舗共通のデフォルトプロンプト（店舗個別未設定時のフォールバック）。

| 項目 | 用途 |
|------|------|
| 質問まとめ生成プロンプト | 日報送信時に質問ごとの会話を要約 |
| 日次まとめ生成プロンプト | 店長日報送信時に店舗まとめを生成 |
| LINE一言アドバイスプロンプト | LINE送信時のAI一言（40字以内、gpt-4o-mini） |

| API | 説明 |
|------|------|
| `GET / POST /api/admin/global-settings` | 取得 / 保存（admin のみ） |

### 8.4 フィーチャーフラグ（admin のみ）

| API | 説明 |
|------|------|
| `GET / POST /api/pl/feature-flags?storeId=...` | フラグ取得 / 更新（マージ） |

---

## 9. データベース概要

### 9.1 主要テーブル（33テーブル中、頻出のもの）

| テーブル | 役割 |
|---------|------|
| `stores` | 店舗マスタ（id, storeCode, name, passwordHash） |
| `store_settings` | 店舗設定（regularHolidays, exceptionHolidays, businessDayCutoffHour, featureFlags, customSettings） |
| `store_sessions` / `store_group_sessions` | セッション |
| `store_groups` / `store_group_members` | グループアカウント |
| `sales_data` | 売上明細（POSデータ取込結果） |
| `pl_sales_categories` / `pl_expense_categories` / `pl_expense_category_groups` | カテゴリ |
| `pl_vendors` / `pl_vendor_categories` | 取引先 |
| `pl_daily_sales` / `pl_daily_expenses` | 日次入力 |
| `pl_monthly_targets` | 月次目標 |
| `pl_sales_deduction_rules` | 売上控除・費用振替ルール |
| `pl_daily_sales_audit` / `pl_daily_expenses_audit` | 監査ログ（DBトリガで自動記録） |
| `daily_report_members` / `daily_report_questions` | 日報メンバー・質問 |
| `daily_reports` / `daily_report_summaries` | 日報・店舗まとめ |
| `weekly_reports` / `monthly_reports` | 週報・月報（HTMLメタデータ。本体はBlob） |
| `global_settings` | 全体設定（admin） |

### 9.2 Blob ストレージ

Vercel Blob に以下を保管:

- 売上CSVの原本（再取込用）
- 週報・月報の HTML（自己完結型、CSS/JS inline）

---

## 10. エラーコード辞書（よく出るもの）

### 10.1 共通（config/constants.ts の ERROR_CODES）

| コード | メッセージ |
|--------|-----------|
| ERR-001 | CSVファイルを選択してください |
| ERR-002 | ファイルサイズが10MBを超えています |
| ERR-003 | 必須列が見つかりません |
| ERR-004 | データ形式が不正です |
| ERR-005 | アップロードに失敗しました。再試行してください |
| ERR-404 | 指定月のデータが見つかりません |
| ERR-PL-001 | 同名のカテゴリが既に存在します |
| ERR-PL-DAILY-SALES | 日次売上の操作に失敗しました |
| ERR-PL-DAILY-EXPENSES | 日次経費の操作に失敗しました |
| ERR-PL-MONTHLY | 月次目標の操作に失敗しました |
| ERR-PL-BUSINESS-DAYS | 営業日設定の操作に失敗しました |
| ERR-PL-DASHBOARD | ダッシュボードの取得に失敗しました |
| ERR-EXPORT-001〜003 | CSVエクスポート系（期間不正・店舗ID未指定・生成失敗） |
| ERR-PL-EXPENSE-001〜003 | 経費明細の取得失敗 |

### 10.2 認証系（ERR-AUTH-*）

| コード | 用途 | HTTP |
|--------|------|------|
| ERR-AUTH-001 | 未認証／必須欠落 | 401/400 |
| ERR-AUTH-002 | セッション無効／パスワード不一致 | 401 |
| ERR-AUTH-003 | 他店舗アクセス禁止 / ログイン処理失敗 | 403/500 |
| ERR-AUTH-007 | 権限不足（最頻出） | 403 |
| ERR-AUTH-008 | 店舗一覧取得失敗 | 500 |
| ERR-AUTH-009 | 店舗追加: 必須欠落 | 400 |
| ERR-AUTH-011 | 店舗追加: ID重複 | 400 |
| ERR-AUTH-013 | 店舗更新: 店舗ID・店舗名必須 | 400 |
| ERR-AUTH-014 | 店舗更新: 店舗が見つからない | 404 |

### 10.3 売上控除（ERR-DEDUCT-*）

| コード | 用途 |
|--------|------|
| ERR-DEDUCT-001〜005 | バリデーション・操作失敗 |

### 10.4 LINE（ERR-LINE-*）

| コード | 用途 |
|--------|------|
| ERR-LINE-001 / 002 | LINE設定取得・更新失敗 |
| ERR-LINE-010 | 接続コード形式・照合エラー |

### 10.5 日報（ERR-DR-*）

| コード | 用途 |
|--------|------|
| ERR-DR-001 | 汎用日報操作失敗 |
| ERR-DR-MEMBER | メンバー操作失敗 |
| ERR-DR-QUESTION | 質問操作失敗 |
| ERR-DR-PROMPTS | プロンプト操作失敗 |
| ERR-DR-POSITION | ポジション設定操作失敗 |

---

## 11. APIエンドポイント全一覧

統一形式: `{ success: true, data: ... }` または `{ success: false, error: { code, message } }`

### 11.1 認証

```
POST /api/auth/login         店舗→グループの順で認証
POST /api/auth/logout        セッション削除
GET  /api/auth/session       現在のセッション情報
POST /api/auth/demo          デモログイン
GET / POST / PUT /api/auth/stores             店舗CRUD（admin）
GET / POST / PUT / DELETE /api/auth/store-groups   グループCRUD（admin）
```

### 11.2 売上・ダッシュボード

```
POST /api/upload             売上CSVアップロード
POST /api/upload/preview     CSVプレビュー（列マッピングUI用）
GET  /api/data/[month]       月次ダッシュボード集計データ
GET  /api/months             アップロード済み月一覧
GET  /api/trends/monthly     月次推移
GET  /api/today              営業日付（businessDayCutoffHour 適用後）
GET / POST /api/settings     店舗設定（時給・最大収容数等）
```

### 11.3 PL

```
GET  /api/pl/dashboard                       ダッシュボード集計
GET / POST /api/pl/daily-sales              日次売上
GET / POST /api/pl/daily-expenses           日次経費
GET / POST /api/pl/categories               カテゴリ（?type=sales|expense）
GET / POST /api/pl/expense-groups           経費グループ
GET / POST /api/pl/vendors                  取引先
GET / POST /api/pl/monthly-targets          月次目標
GET / POST /api/pl/business-days            営業日設定
GET  /api/pl/trends                          月次推移
GET  /api/pl/trends/expense-breakdown        費目×取引先×月の経費ドリルダウン
GET  /api/pl/expenses/breakdown              月単位の費目→取引先→日次の3階層集計
GET  /api/pl/export/[type]                   CSVエクスポート（sales/expenses/monthly）
GET / POST /api/pl/sales-deduction          売上控除設定
GET / POST /api/pl/sales-deduction/rules    控除ルール一覧/作成
GET / PUT / DELETE /api/pl/sales-deduction/rules/[ruleId]   控除ルール個別
GET / POST /api/pl/feature-flags             フィーチャーフラグ（admin）
GET / POST /api/pl/daily-report-members      日報メンバー
GET / POST /api/pl/daily-report-questions    質問
GET / POST /api/pl/daily-report-prompts      プロンプト
GET / POST /api/pl/daily-report-position     ポジション設定
```

### 11.4 日報

```
POST /api/daily-report/auth              店舗パスワード認証
GET  /api/daily-report/members           メンバー一覧
GET  /api/daily-report/questions          質問取得
POST /api/daily-report/stream            AI深掘り SSE
POST /api/daily-report/summarize         要約
POST /api/daily-report/submit            送信
POST /api/daily-report/manager-submit    店長締め＋AI店舗まとめ＋LINE
GET  /api/daily-report/reports           個人日報一覧
GET  /api/daily-report/store-summary     店舗まとめ取得
```

### 11.5 週報・月報

```
GET  /api/weekly-reports                       一覧
POST /api/weekly-reports/upload                アップロード（admin）
GET / DELETE /api/weekly-reports/[id]          詳細 / 削除
GET  /api/weekly-reports/[id]/html             iframe表示用 HTML 配信
GET  /api/weekly-reports/[id]/printable        印刷用CSS注入版
GET  /api/monthly-reports                      月報一覧
POST /api/monthly-reports/upload               月報アップロード（admin）
GET / DELETE /api/monthly-reports/[id]         詳細 / 削除
GET  /api/monthly-reports/[id]/html            iframe HTML
GET  /api/monthly-reports/[id]/printable       印刷用
GET  /api/store-reports                        週報+月報を endDate 降順マージ
```

### 11.6 LINE

```
POST /api/line/webhook       LINE Platform からの Webhook
POST /api/line/pair          ペアリングコードで紐付け
GET / POST /api/line/settings  LINE設定取得 / 更新
```

### 11.7 管理・デバッグ

```
GET / POST /api/admin/global-settings  全体設定
GET  /api/debug/blobs                  Blob一覧（debug）
POST /api/test-parse                   CSVパーステスト（debug）
```

---

## 12. FAQ（よくある運用現場の質問）

### Q1. ログインできない／パスワードを忘れた

A. 管理者（admin）が `/admin` → 店舗管理 → 該当店舗を編集 → 新パスワードを入力して保存。bcrypt でハッシュ化されてDB保存される。

### Q2. アップロードした売上が表示されない

A. チェック順:
1. 月一覧（`/store/{storeId}/sales-dashboard`）に該当月のカードが出ているか
2. Dinii の場合は orders と transactions の **両方** をアップロードしたか
3. CSV にヘッダー行が含まれているか
4. アップロード時のレスポンスが `success: true` だったか（コンソールエラーがないか）

### Q3. 客単価が想定と違う

A. ダッシュボード設定タブで「客単価除外カテゴリ」を確認。お土産・物販・デリバリーなどを除外することで店内体験の客単価が見えるようになる。除外設定は全期間・全タブに自動反映される。

### Q4. PL着地予想がブレる

A. チェック順:
1. 営業日設定（定休日・例外休日）が今月の実態と合っているか
2. 経費の「定常／例外」種別が正しく区別されているか（一時的なスポット支出は **例外**）
3. businessDayCutoffHour が深夜営業の実態に合っているか

### Q5. LINE通知が来ない

A. チェック順:
1. PL設定 → フィーチャーフラグの `lineNotification` がON か（admin のみ操作可）
2. customSettings の `lineGroupId` が設定されているか（ペアリングコード経由で紐付け）
3. LINE グループから Bot が退出していないか

### Q6. 客単価除外カテゴリは月別に変えられるか

A. **店舗単位の設定で全期間に反映される**。月別の切り替えは不可。

### Q7. CSV取込でERR-003（必須列が見つかりません）が出る

A. POS の自動判定後、フォーマットごとの必須列を満たしていないと出る。
- Dinii orders: `会計ID` / `メニュー名称` / `主副区別` / `売価(税込)` 等の8列
- Dinii transactions: `会計ID` / `人数` / `合計` / `修正履歴` 等の6列
- スマレジ: `取引ID` / `取引日時` / `販売単価` / `部門名` 等の11列
- Airレジ: `取引No` / `会計日` / `会計時間` / `ID` 等の10列
詳細は POSダッシュボード.md §3 参照。

### Q8. 売上控除ルールを設定したら日次入力ができなくなった

A. 仕様。控除ルールの対象売上カテゴリは **日次入力画面で入力ロック** され、自動算出される。控除を解除すれば再び入力可能。

### Q9. 日報送信ボタンが押せない

A. すべての質問に回答していないと送信不可。途中まで進めて全質問が「✓」になっているかを確認。

### Q10. 店長と店員で見える画面が違う

A. `featureFlags.dailyReportOnly=true` の店舗では、店長以外（店員）は PL/売上ダッシュボードが見えず、日報系のみに制限される。

### Q11. 監査ログを画面から見たい

A. **画面UIなし**。DBの `pl_daily_sales_audit` / `pl_daily_expenses_audit` テーブルを直接参照（DBトリガで INSERT/UPDATE/DELETE が自動記録される）。

### Q12. 週報・月報を店舗側でアップロードしたい

A. 不可。アップロードは **admin のみ**。店舗は閲覧と印刷/PDF保存のみ可能。

### Q13. 売上CSVを誤って取り込んだ

A. 同じ月で再アップロードすると **上書き**（同月の既存データを削除→新規取込）。

### Q14. 営業日切り替え時刻（businessDayCutoffHour）が分からない

A. 既定値は **5（AM5時）**。深夜営業しないお店は触らなくてOK。深夜0:00〜4:59 の売上を「前日」扱いにするための設定。

### Q15. グループアカウントとは何か

A. 外注コンサル等向け。1つのIDで複数店舗にアクセスできる。ログイン直後に `/group/select` で店舗を選んで操作。管理は `/admin` → グループ管理。

### Q16. AIによる日報深掘りが止まらない

A. プロンプトに「最大2回まで」と明示してある。それでも止まらない場合は店舗個別のプロンプトが上書きされている可能性。PL設定 → 日報サマリープロンプトを確認、または admin の全体設定にフォールバック。

### Q17. CSVエクスポートは何が出せるか

A. `/api/pl/export/[type]` で:
- `sales`: 売上明細
- `expenses`: 経費明細
- `monthly`: 月次集計

### Q18. 「店舗が見つかりません」（ERR-STORE-001）が出る

A. URLに含まれる店舗コードに typo がないか確認。ロールが store/group の場合、自分のアクセス権限外の店舗にアクセスしようとしている可能性。

### Q19. PLダッシュボードに利益が表示されない

A. `featureFlags.hideProfit=true` が設定されている可能性。admin に設定見直しを依頼。

### Q20. 「ログインに失敗しました」が連発する

A. パスワードのコピペ時の空白混入が頻出。手入力で試す。それでもダメなら admin にパスワード再設定を依頼。

---

## 13. クライアント側の前提・制約

- ブラウザ: Chrome / Safari の最新版を推奨
- ファイルサイズ上限: 売上CSV 10MB / 週報・月報 HTML 制限なし（実用上は数MB）
- セッション: 7日。複数端末からの同時ログイン可
- AI機能: OpenAI gpt-4.1（深掘り・要約）／ gpt-4o-mini（LINE一言）
- LINE: Messaging API（Bot招待→ペアリング方式）

---

## 14. 開発・運用情報（参考）

- 設計ドキュメント: `docs/01_design/`
- 運用ドキュメント: `docs/02_operations/`
- 環境: dev / staging / production（CLAUDE.md 参照）
- リリースフロー: `feature/* → dev → staging → main`

---

**マスター末尾**
詳細仕様は機能別ファイル（POSダッシュボード.md / PLダッシュボード.md / 週報.md）を参照してください。
