# PLダッシュボード 詳細仕様（PL管理）

> マスター: `../AI参照用_仕様マニュアル_v1.md`

---

## 1. 機能の役割

飲食店オーナーが **日次で売上と経費を入力** し、月次目標に対する進捗・着地予想を把握する。スマホファースト、レスポンシブ。

- **入口**: `/store/{storeId}` の「PL管理」カード
- **初期遷移**: `/store/{storeId}/pl` → `/pl/dashboard` （`featureFlags.dailyReportOnly=true` の店舗は `/pl/daily-reports` へ）

---

## 2. 画面構成（6タブ）

`components/pl/PlNavigation.tsx` のタブ:

| タブ | パス | 主な役割 |
|------|------|---------|
| ダッシュボード | `/pl/dashboard` | 着地予想・進捗 |
| 月次推移 | `/pl/trends` | 月次の売上/経費/利益/FL率の推移 |
| 日次入力 | `/pl/daily` | 日別の売上・経費入力 |
| 日報 | `/pl/daily-reports` | 日報確認・店舗まとめ |
| 月次目標 | `/pl/monthly` | カテゴリ別目標・予算・FL目標 |
| 設定 | `/pl/settings` | カテゴリ／取引先／営業日／控除ルール／日報設定／フィーチャーフラグ |

`dailyReportOnly=true` ではタブが日報系のみに制限される。

---

## 3. アクセス権限

| 操作 | admin | store | group |
|------|:-----:|:-----:|:-----:|
| PL閲覧・編集 | 全店舗 | 自店舗 | 所属店舗 |
| フィーチャーフラグ変更 | ○ | × | × |
| 売上控除ルール変更 | ○ | △（featureFlag.salesDeduction=true 時のみ画面表示）| △ |

---

## 4. PLダッシュボード（/pl/dashboard）

### 4.1 表示項目

| 項目 | 計算式 |
|------|--------|
| 累計売上 | 当月の `pl_daily_sales.amount` の合計 |
| 累計経費 | 当月の `pl_daily_expenses.amount` の合計 |
| 累計利益 | 累計売上 − 累計経費 |
| 経過営業日 | 当月開始日〜本日（営業日カレンダー適用） |
| 当月営業日数 | 営業日カレンダーから算出 |
| 着地予想売上 | （累計売上 ÷ 経過営業日）× 当月営業日数 |
| 着地予想経費 | 定常経費（RECURRING）は線形補外、例外経費（ONE_TIME）は実額 |
| 着地予想利益 | 着地予想売上 − 着地予想経費 |
| FL率 | （FLコスト対象経費の合計）÷ 売上 |
| FL率目標 | `pl_monthly_targets.fl_target_ratio`（%） |

### 4.2 営業日カレンダー（businessDayCutoffHour ＋定休日／例外休日）

- 営業日付の確定:
  - `businessDayCutoffHour`（既定 5）で「今日」を判定
  - 例: cutoff=5 のとき、深夜0:00〜4:59 のデータは「前日」の営業日付として扱う
- 営業日数 = カレンダー日数 − 定休日（曜日） − 例外休日（個別日付）

### 4.3 「未締めの日」の日報表示

PLダッシュボード内に日報セクション:
- 当日の店舗まとめ日報が未生成（未締め）の場合は **直近の締めまでのまとめ** を表示
- それも無ければ **個人日報を時系列でフォールバック表示**

### 4.4 関連API

```
GET /api/pl/dashboard?storeId=...&month=YYYY-MM
GET /api/today?storeId=...   営業日付（businessDayCutoffHour 適用後）
```

---

## 5. 日次入力（/pl/daily）

### 5.1 売上入力

| フィールド | 型 | バリデーション |
|-----------|---|---------------|
| date | DATE | 営業日付 |
| category_id | UUID | 売上カテゴリのID |
| amount | DECIMAL(12,2) | 税込売上 |

**一意性**: `(store_id, date, category_id)` で UNIQUE

**入力ロック**: 売上控除ルールの **対象売上カテゴリ** は入力ロック（自動算出）

### 5.2 経費入力

| フィールド | 型 | バリデーション |
|-----------|---|---------------|
| date | DATE | 営業日付 |
| category_id | UUID | 経費カテゴリのID |
| vendor_id | UUID? | 取引先（任意）。取引先削除時は SetNull |
| amount | DECIMAL(12,2) | 経費金額 |
| expense_type | string | `RECURRING` または `ONE_TIME` |
| memo | string(500) | 任意メモ |

**重要**: 同一日・同一カテゴリの経費を **複数行入力可能**（取引先別など）。UNIQUEではなくINDEX。

**取引先プルダウン**: `pl_vendor_categories` で経費カテゴリに紐付いた取引先のみ候補に出る

### 5.3 関連API

```
GET / POST /api/pl/daily-sales?storeId=...&date=YYYY-MM-DD
GET / POST /api/pl/daily-expenses?storeId=...&date=YYYY-MM-DD
```

### 5.4 監査ログ

`pl_daily_sales_audit` / `pl_daily_expenses_audit` テーブルに DBトリガで自動記録:

| カラム | 内容 |
|--------|------|
| source_id | 元レコードID |
| amount_old / amount_new | 変更前後の金額 |
| memo_old / memo_new | 変更前後のメモ（expenses のみ） |
| operation | INSERT / UPDATE / DELETE |
| actor | 操作者（記録あれば） |
| at | TIMESTAMPTZ |

**UI なし**。DBクエリで参照する想定。

---

## 6. 月次目標（/pl/monthly）

### 6.1 設定項目

`pl_monthly_targets` テーブル:

| カラム | 型 | 内容 |
|--------|---|------|
| year_month | VARCHAR(7) | "2026-02" |
| sales_target | DECIMAL(15,2) | 月全体の売上目標 |
| sales_breakdown | JSON | カテゴリ別売上目標 `{ categoryId: amount }` |
| expense_budgets | JSON | カテゴリ別経費予算 `{ categoryId: amount }` |
| profit_target | DECIMAL(15,2) | 利益目標 |
| fl_target_ratio | DECIMAL(5,2) | FLコスト目標比率（%） |

**一意性**: `(store_id, year_month)`

### 6.2 ダッシュボードへの反映

- 達成率 = 累計売上 / 売上目標
- 達成見込み% = 着地予想売上 / 売上目標
- カテゴリ別の達成率・達成見込みも個別に算出

### 6.3 関連API

```
GET / POST /api/pl/monthly-targets?storeId=...&yearMonth=YYYY-MM
```

---

## 7. 月次推移（/pl/trends）

### 7.1 表示

- 期間切替: 3 / 6 / 12 / 全期間
- グラフ（Plotly）: 売上 / 経費 / 利益 / FL率
- 経費テーブル: 月ごとに **費目 → 取引先 → 日次明細** の3階層ドリルダウン

### 7.2 関連API

```
GET /api/pl/trends?storeId=...&months=12
GET /api/pl/trends/expense-breakdown?storeId=...&fromYearMonth=...&toYearMonth=...
GET /api/pl/expenses/breakdown?storeId=...&yearMonth=YYYY-MM   費目→取引先→日次の3階層
```

### 7.3 エラー

| コード | 用途 |
|--------|------|
| ERR-PL-TRENDS-BREAKDOWN-001 | 店舗ID未指定 |
| ERR-PL-TRENDS-BREAKDOWN-002 | 月範囲不正 |
| ERR-PL-TRENDS-BREAKDOWN-003 | 経費取引先内訳取得失敗 |
| ERR-PL-EXPENSE-001 | 店舗ID未指定 |
| ERR-PL-EXPENSE-002 | 月指定不正 (YYYY-MM) |
| ERR-PL-EXPENSE-003 | 経費明細取得失敗 |

---

## 8. CSVエクスポート

```
GET /api/pl/export/sales?storeId=...&from=YYYY-MM-DD&to=YYYY-MM-DD
GET /api/pl/export/expenses?storeId=...&from=...&to=...
GET /api/pl/export/monthly?storeId=...&from=YYYY-MM&to=YYYY-MM
```

エラー: ERR-EXPORT-001（期間不正）／002（店舗ID未指定）／003（生成失敗）

---

## 9. PL設定（/pl/settings）

### 9.1 売上カテゴリ管理（pl_sales_categories）

| フィールド | 説明 |
|-----------|------|
| name | カテゴリ名（店舗内ユニーク） |
| display_order | D&Dで並び替え |
| color_code | グラフ色 |
| is_active | 論理削除 |

**API**: `GET / POST /api/pl/categories?type=sales&storeId=...`
**エラー**: ERR-PL-001（重複）／ERR-PL-CATEGORY（汎用失敗）

### 9.2 経費グループ（pl_expense_category_groups）

「原価」「販管費」など経費カテゴリの上位階層。

**API**: `GET / POST /api/pl/expense-groups?storeId=...`
**エラー**: ERR-PL-GROUP

### 9.3 経費カテゴリ（pl_expense_categories）

| フィールド | 説明 |
|-----------|------|
| name | カテゴリ名 |
| default_expense_type | RECURRING / ONE_TIME |
| group_id | 所属グループ（SetNull on delete） |
| is_fl_cost | FL率の分子に含めるか |
| display_order | 並び替え |

**API**: `GET / POST /api/pl/categories?type=expense&storeId=...`

### 9.4 取引先（pl_vendors / pl_vendor_categories）

- 取引先名・並び順
- 取引先 × 経費カテゴリの紐付け（複数カテゴリ可）
- 日次経費入力で、選択中の経費カテゴリに紐付いた取引先のみプルダウンに出る

**API**: `GET / POST /api/pl/vendors?storeId=...`
**エラー**: ERR-PL-VENDOR

### 9.5 営業日設定

`store_settings` の以下のJSON列を編集:

```json
{
  "regularHolidays": [1, 2],        // 月曜・火曜が定休
  "exceptionHolidays": ["2026-07-15", "2026-08-13"],
  "businessDayCutoffHour": 5         // 既定 5（AM5時）
}
```

**API**: `GET / POST /api/pl/business-days?storeId=...`
**エラー**: ERR-PL-BUSINESS-DAYS

### 9.6 売上控除・費用振替ルール（pl_sales_deduction_rules）

| フィールド | 型 | 内容 |
|-----------|---|------|
| name | string? | ルール名（任意） |
| sales_category_id | UUID | 控除対象の売上カテゴリ |
| ratio | DECIMAL(5,2) | 0 < ratio ≦ 100（税込売上に対する%） |
| expense_category_id | UUID? | 振替先費用カテゴリ。null = 単純控除 |
| start_date | DATE | 有効期間開始（inclusive） |
| end_date | DATE? | 終了（inclusive、null = 無期限） |
| is_active | boolean | |

**仕様**:
- ルールが効いている期間中、対象売上カテゴリは **日次入力UIで入力ロック**
- 売上は自動算出（外部入力データ × ratio% の控除）
- 振替先経費カテゴリが設定されていれば、控除額を経費として自動計上

**API**:
```
GET / POST /api/pl/sales-deduction?storeId=...           ルール全体ON/OFF
GET / POST /api/pl/sales-deduction/rules?storeId=...     一覧 / 作成
GET / PUT / DELETE /api/pl/sales-deduction/rules/[ruleId]
```

**エラー**: ERR-DEDUCT-001〜005

**UI表示制御**: `featureFlags.salesDeduction=true` の店舗でのみ設定UI表示

### 9.7 日報設定（メンバー / 質問 / プロンプト / ポジション）

各種テーブル:
- `daily_report_members`: 日報を書くスタッフ（責任者・スタッフ）
- `daily_report_questions`: メンバー別の質問テンプレ + `systemPrompt`
- `daily_report_prompts`: 店舗別のサマリープロンプト

**API**:
```
GET / POST /api/pl/daily-report-members?storeId=...
GET / POST /api/pl/daily-report-questions?storeId=...&memberId=...
GET / POST /api/pl/daily-report-prompts?storeId=...
GET / POST /api/pl/daily-report-position?storeId=...   featureFlags + customSettings
```

**エラー**: ERR-DR-MEMBER / ERR-DR-QUESTION / ERR-DR-PROMPTS / ERR-DR-POSITION

### 9.8 フィーチャーフラグ管理（admin のみ）

`store_settings.feature_flags` JSON カラム:

```typescript
interface FeatureFlags {
  dailyReportPosition?: boolean;  // 日報ポジション選択UI
  lineNotification?: boolean;     // LINE通知の送信
  hideProfit?: boolean;           // 利益情報の非表示
  salesDeduction?: boolean;       // 売上控除設定UIの表示
  dailyReportOnly?: boolean;      // 日報のみのナビ制限
}
```

**API**: `GET / POST /api/pl/feature-flags?storeId=...`（admin only）

---

## 10. DBテーブル一覧（PL系）

| Prisma モデル | テーブル名 | 役割 |
|--------------|-----------|------|
| PlSalesCategory | pl_sales_categories | 売上カテゴリ |
| PlExpenseCategoryGroup | pl_expense_category_groups | 経費グループ |
| PlExpenseCategory | pl_expense_categories | 経費カテゴリ |
| PlDailySales | pl_daily_sales | 日次売上 |
| PlDailyExpense | pl_daily_expenses | 日次経費 |
| PlMonthlyTarget | pl_monthly_targets | 月次目標 |
| PlSalesDeductionRule | pl_sales_deduction_rules | 売上控除・費用振替ルール |
| PlVendor | pl_vendors | 取引先 |
| PlVendorCategory | pl_vendor_categories | 取引先×経費カテゴリ |
| PlDailySalesAudit | pl_daily_sales_audit | 監査ログ（DBトリガ） |
| PlDailyExpensesAudit | pl_daily_expenses_audit | 監査ログ（DBトリガ） |

---

## 11. 主要なロジックの完全フォーミュラ

### 11.1 着地予想売上

```
着地予想売上 = (累計売上 / 経過営業日) * 当月営業日数
```

- 経過営業日: 営業日カレンダーで今日までに経過した営業日数
- 当月営業日数: 営業日カレンダーで当月の営業日総数

### 11.2 着地予想経費

```
定常経費の合計 = SUM(pl_daily_expenses.amount WHERE expense_type='RECURRING')
例外経費の合計 = SUM(pl_daily_expenses.amount WHERE expense_type='ONE_TIME')
着地予想経費 = (定常経費の合計 / 経過営業日) * 当月営業日数 + 例外経費の合計
```

### 11.3 FL率

```
FLコスト = SUM(pl_daily_expenses.amount WHERE category.is_fl_cost=true)
FL率 = FLコスト / 累計売上 * 100
```

### 11.4 売上控除ルール適用後の売上

```
控除対象売上 = 元の売上 * ratio / 100
表示売上 = 元の売上 - 控除対象売上

if (rule.expense_category_id) {
  // 振替: 経費カテゴリに控除額を自動計上
  insert pl_daily_expenses (category_id=rule.expense_category_id, amount=控除対象売上)
}
```

---

## 12. よくある質問

### Q. 売上控除ルールを途中で変えたら過去のデータは？

A. ルールは `start_date` / `end_date` の有効期間でのみ適用される。過去日のデータには遡及適用されない。

### Q. 営業日カレンダーを変えたら過去の着地予想は？

A. 着地予想はリクエストごとに算出されるため、最新の営業日カレンダーで再計算される。

### Q. 経費を間違えて入力した場合の修正手段は？

A. 同じ画面で行を編集して保存。監査ログ（DBトリガ）に旧値・新値・operation=UPDATE が自動記録される。

### Q. 取引先を削除したら過去の経費明細はどうなる？

A. `vendor_id` が SetNull になる（明細自体は残る）。

### Q. 同じ日・同じカテゴリに2回入力したい

A. **可能**。UNIQUE ではなく INDEX なので複数行入力可能（取引先別など）。

### Q. FLコスト対象フラグを途中でONにしたらFL率は？

A. 過去日のデータも含めて即時反映される（履歴ベースではなく現在のフラグで計算）。

### Q. 月次目標を月の途中で変えたら？

A. 月次目標は当月の最新値が常に使われる。途中変更は履歴に残らない。

---

## 13. 制約・注意点

1. **売上控除ルール対象カテゴリは日次入力ロック**。手動で上書きできない
2. **同月の同カテゴリ売上は1行のみ**（UNIQUE）
3. **同月の同カテゴリ経費は複数行可**（取引先別等）
4. **FL率対象フラグ変更は即時反映**（履歴ベースではない）
5. **businessDayCutoffHour は店舗ごとに1つ**。曜日別の切替はできない
6. **監査ログUIなし**。DB直接参照が必要
