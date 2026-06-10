---
title: rawdata.csv タイムゾーン解釈バグ 調査レポート
date: 2026-06-10
status: 修正方針確定済み・実装未着手
author: investigation agent (claude opus 4.7)
scope: 週報 + 月報 のPython集計パイプライン
fix_owner: TBD
related_findings:
  - BFA W23 売上 ¥496,610 (バグ) → ¥806,830 (正)
  - BFA W23 客単価 ¥5,067 (バグ) → ¥29,883 (正)
---

# 0. エグゼクティブサマリ

`rawdata.csv` の `entry_at` / `exit_at` / `ordered_at` 列は **JSTのナイーブ文字列** (`"2025-11-25 20:16:30"` のような TZ サフィックスなし) で保存されている。

しかし週報・月報のPython集計スクリプト群は以下のパターンで処理している:

```python
sales_df['entry_at']     = pd.to_datetime(sales_df['entry_at'], utc=True)         # ← naive を UTC とみなす
sales_df['entry_at_jst'] = sales_df['entry_at'].dt.tz_convert('Asia/Tokyo')        # ← +9h
```

結果として **すべての時刻が +9時間ずれ**、これに連動する以下が壊れる:
- `business_date` (営業日: JST 0-5時を前日に付け替え)
- `business_hour` / `hour_bucket`
- `weekday` (営業日基準の曜日)
- `year_week` (営業日のISO週)
- → 上記を集計キーとする **すべてのKPI** (売上、客単価、客数、曜日別、時間帯別、週次推移)

影響範囲は **週報5店舗 (BFA / 麻布しき / 麻布しき本店 / BBC / キーポイント) の全週 + 月報全体**。

---

# 1. 原因セクション: TZ情報がどこで落ちているか

## 1.1 データフロー全体図

```
[POSの売上CSV(各社)]
        ↓ bulk-upload-*.mjs
[Postgres DB]
  sales_data.entry_at @db.Timestamptz(6)   ← UTC として内部保存
        ↓ Prisma が JS Date (UTC) で取得
[Dashboard API: /api/data/[month]]
  formatUTCtoJST(sale.entryAt, 'datetime')  ← ★ ここでJST文字列に変換 (TZサフィックスなし)
        ↓ visitDateTime: "YYYY-MM-DD HH:mm:ss" (JST naive string)
[export-rawdata.mjs]
  entry_at: item.visitDateTime           ← そのまま CSV へ
        ↓
[rawdata.csv]
  "2025-11-25 20:16:30"                  ← ★ JSTナイーブ文字列。これが入力
        ↓
[analysis_script.py]
  pd.to_datetime(..., utc=True)          ← ★★ バグ: naive を UTC と誤解釈
   .dt.tz_convert('Asia/Tokyo')          ← +9h されて完全に壊れる
```

## 1.2 確定エビデンス（コード行レベル）

### (a) DBはTimestamptz保存 (UTC内部)
`~/RestaurantAILab/Dashboard/prisma/schema.prisma:97`
```prisma
entryAt        DateTime    @map("entry_at") @db.Timestamptz(6)
exitAt         DateTime    @map("exit_at") @db.Timestamptz(6)
```
`@db.Timestamptz` は PostgreSQL の `timestamp with time zone` で、内部的に常にUTC正規化される。

### (b) API層でJSTに明示変換し、TZサフィックスなしで返す
`~/RestaurantAILab/Dashboard/app/api/data/[month]/route.ts:199-215`
```typescript
// Convert UTC timestamps to JST for display
// Database stores in UTC, but application layer works with JST
const entryDateTimeJST = formatUTCtoJST(sale.entryAt, 'datetime');
const exitDateTimeJST  = formatUTCtoJST(sale.exitAt,  'datetime');
...
salesData.push({
  visitDate:     entryBusinessDate,      // 営業日付 (YYYY-MM-DD)
  visitDateTime: entryDateTimeJST,        // YYYY-MM-DD HH:mm:ss in JST  ← ★コメント明記
  exitDateTime:  exitDateTimeJST,         // YYYY-MM-DD HH:mm:ss in JST
  dayOfWeek:     businessDow,             // 営業日基準の曜日
  ...
});
```

`~/RestaurantAILab/Dashboard/lib/utils/date.ts:213-233`
```typescript
export function formatUTCtoJST(date: Date, format = 'datetime'): string {
  const jstDate = new Date(date.getTime() + 9 * 60 * 60 * 1000);
  ...
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;  // ★ Zサフィックス無し
}
```

### (c) export-rawdata.mjs は素通し
`~/RestaurantAILab/Dashboard/scripts/export-rawdata.mjs:99`
```javascript
entry_at: item.visitDateTime || '',   // JST naive 文字列がそのままCSVへ
exit_at:  item.exitDateTime  || '',
```

### (d) 実CSVサンプル (全店舗で同形式を確認済み)
| 店舗 | サンプル行 |
|------|-----------|
| BFA | `"bfa-001","BAR FIVE Arrows",...,"2024-01-01 00:40:28","2024-01-01 00:40:28","月",...` |
| 麻布しき (旗の台) | `"shiki-001",...,"2025-01-01 11:14:23","2025-01-01 13:54:02","水",...` |
| 麻布しき本店 | `shiki-002,...,2025-03-01 11:39:18,2025-03-01 12:18:33,土,...` |
| BBC | `"bbc-001","別天地　銀座",...,"2025-11-25 20:16:30","2025-11-25 23:08:55","火",...` |
| キーポイント | `"kp-001","かめや駅前店",...,"2026-01-03 18:45:09","2026-01-03 18:45:09","土",...` |

すべて TZ サフィックスなしのJSTナイーブ文字列。

### (e) Python集計でのバグ箇所
`Scripts/analysis_script.py:170-179`
```python
sales_df['entry_at'] = pd.to_datetime(sales_df['entry_at'], utc=True)
sales_df['exit_at']  = pd.to_datetime(sales_df['exit_at'],  utc=True)
if 'ordered_at' in sales_df.columns:
    sales_df['ordered_at'] = pd.to_datetime(sales_df['ordered_at'], utc=True, errors='coerce')

# UTC → JST 変換（+9時間）  ← コメント自体がバグの存在を物語っている
sales_df['entry_at_jst'] = sales_df['entry_at'].dt.tz_convert('Asia/Tokyo')
sales_df['exit_at_jst']  = sales_df['exit_at'].dt.tz_convert('Asia/Tokyo')
```

pandas の `pd.to_datetime(s, utc=True)` は、TZ情報のないナイーブ文字列を **「UTCである」と仮定して** tz-aware に変換する仕様。そのため:
- 入力: `"2024-01-01 00:40:28"` (実態はJST = 1/1 00:40 JST)
- `pd.to_datetime(..., utc=True)` 後: `2024-01-01 00:40:28+00:00` (UTCと誤認識)
- `.tz_convert('Asia/Tokyo')` 後: `2024-01-01 09:40:28+09:00` (JST 09:40 — 実態より9時間ずれ)

## 1.3 ユーザー検証結果との整合

| 検証 | 結果 | 解釈 |
|------|------|------|
| W23 30件で `entry_at` JST直読み vs `day_of_week` の一致率 | JST直読み 30/30、UTC+9h解釈 4/30 | ★ rawdata.csv は JST 確定 |
| BFA W23 報告書値 ¥496,610 vs 実態 ¥806,830 | -38%乖離 | バグで深夜帯売上が翌日にズレ、対象週から脱落 |
| BFA W23 客単価 ¥5,067 vs ¥29,883 | バー業態(¥30k帯)としてあり得ない | KPI が壊れていることを裏付け |

`get_business_date()` (analysis_script.py:185-195) が JST 0-5時を前日に付け替える設計のため、+9時間ずれた時刻が直撃する。具体的には:
- 実態 `JST 22:00` (バー営業中) → +9h で `JST 翌07:00` 扱い → 翌営業日カウント
- 実態 `JST 翌01:00` (深夜営業締め) → +9h で `JST 翌10:00` 扱い → 翌営業日カウント (本来は前日営業日に統合されるべき)

つまり営業日が **+1日 (週末) または +1日 + 営業日カットオフ越え** で壊れ、KPI の集計対象週がそもそもズレる。

---

# 2. 影響範囲セクション

## 2.1 影響を受けるスクリプト一覧

### 週報 (`Stock/RestaurantAILab/週報/`)

| スクリプト | 行 | 重要度 | 備考 |
|---|---|---|---|
| `Scripts/analysis_script.py` | 170-179 | **致命** | 週報本体パイプラインのコア。BFA/麻布しき/麻布しき本店/BBC/キーポイント 全店舗共通 |
| `Scripts/bfa_category_product_ranking_html.py` | 119-122 | 高 | BFAのカテゴリ・商品ランキング (HTML) |
| `Scripts/deep_dive_weekday_analysis.py` | 46-47 | 高 | 曜日深堀分析 |
| `category_product_ranking.py` (リポルート) | 45-46 | 中 | カテゴリ・商品ランキング集計 |
| `weekly_sales_analysis_procedure.md` | 49-50 | 低 (ドキュメント) | 手順書にバグ実装例が明記。要修正 |
| `old/deep_dive_wednesday.py` | 13-14 | 旧 | レガシー (要確認: 現運用で使われていなければ放置可) |
| `old/deep_dive_friday.py` | 13-14 | 旧 | 同上 |
| `old/analyze_weekday_deep_dive.py` | 27-28 | 旧 | 同上 |

### 月報 (`Stock/RestaurantAILab/月報/Scripts/`)

| スクリプト | 行 | 重要度 |
|---|---|---|
| `monthly_analysis_script.py` | 82-88 | **致命** (月報本体) |
| `deep_dive_weekly_analysis.py` | 50-51 | 高 |
| `monthly_report_pipeline.py` | 95-96, 233 | 高 |

### 影響なし (正しい実装)
- `Scripts/bfa_renewal_analysis.py:15` — `pd.to_datetime(df['entry_at'])` のみで `utc=True` なし。これが正しい挙動 (ナイーブ→ナイーブ JST のまま扱う)。
- `Scripts/dashboard_data_pipeline.py` — `entry_at` の TZ 変換コード未検出。
- `Scripts/merge_ranking_into_weekly.py` — 同上。

### Dashboard 側 (`~/RestaurantAILab/Dashboard/scripts/`)
- `pd.to_datetime(..., utc=True)` の Python パターンは未検出 (Node.js/TS のため別系統)。
- TS 側は `formatUTCtoJST` / `toBusinessDate` が DB UTC を前提に書かれており、設計上は一貫している。

## 2.2 影響を受ける成果物 (年週単位)

`2_output/` 配下のディレクトリを店舗別に列挙:

| 店舗 | 影響を受ける週 (2026年) | 件数 |
|---|---|---|
| 麻布しき | W06, W07, W08, W09, W10, W11, W12, W13, W14, W15, W16, W17, W18, W19, W20, W21, W22, W23 | 18週 |
| BBC | W02, W3, W04, W05, W07_v2, W52(2025) ほか | 詳細列挙未 |
| BFA / 麻布しき本店 / キーポイント | 同様 (詳細は ls で確認可) | 多数 |

→ **2026年 (および2025年末) の全週報がバグ値で生成されている可能性が極めて高い**。
→ 月報も同様に全期間バグ値。

## 2.3 影響を受ける意思決定リスク

KPI レベルでの誤差は店舗・週で異なるが、BFA W23 のように **売上が38%過少報告** されているケースがある。客単価は約 1/6 に圧縮されており、業態判断 (バー業態としての客単価帯) すら成立しない。

これに基づき:
- 在庫 / 仕入計画 (売上ベース) の見直し可能性
- 人時生産性評価の基準値の見直し
- 過去の「曜日別ピーク」「時間帯別ピーク」の解釈が完全に逆転している可能性 (深夜帯の売上が翌日朝の枠で集計されている)

---

# 3. 修正方針セクション

## 3.1 案比較

### 案A: Python 集計スクリプト側で修正 (推奨)

**修正例 (analysis_script.py)**
```python
# Before
sales_df['entry_at'] = pd.to_datetime(sales_df['entry_at'], utc=True)
sales_df['exit_at']  = pd.to_datetime(sales_df['exit_at'],  utc=True)
if 'ordered_at' in sales_df.columns:
    sales_df['ordered_at'] = pd.to_datetime(sales_df['ordered_at'], utc=True, errors='coerce')

sales_df['entry_at_jst'] = sales_df['entry_at'].dt.tz_convert('Asia/Tokyo')
sales_df['exit_at_jst']  = sales_df['exit_at'].dt.tz_convert('Asia/Tokyo')
if 'ordered_at' in sales_df.columns and sales_df['ordered_at'].notna().any():
    sales_df['ordered_at_jst'] = sales_df['ordered_at'].dt.tz_convert('Asia/Tokyo')

# After (rawdata.csv が JST ナイーブであることを明示)
sales_df['entry_at_jst'] = pd.to_datetime(sales_df['entry_at']).dt.tz_localize('Asia/Tokyo')
sales_df['exit_at_jst']  = pd.to_datetime(sales_df['exit_at']).dt.tz_localize('Asia/Tokyo')
if 'ordered_at' in sales_df.columns:
    sales_df['ordered_at_jst'] = pd.to_datetime(sales_df['ordered_at'], errors='coerce').dt.tz_localize('Asia/Tokyo')

# entry_at / exit_at の素の列は以降で参照していないなら削除可
# (現状の analysis_script.py では entry_at_jst のみ使用していることを確認済み)
```

**ポイント**
- `tz_localize` は「ナイーブな日時にTZを後付けで宣言する」操作。+9hシフトはしない。
- `entry_at`, `exit_at` の素の列は `entry_at_jst` 生成後に参照されていない (analysis_script.py 内 grep 確認済み) ので、tz-aware版だけ作れば足りる。
- 影響箇所: `analysis_script.py`, `bfa_category_product_ranking_html.py`, `deep_dive_weekday_analysis.py`, `category_product_ranking.py`, 月報3スクリプト の計7ファイル。同じパターンで機械的に置換可能。

| 観点 | 評価 |
|---|---|
| 影響範囲 | 小 (Python 側のみ) |
| 工数 | 数時間 (7ファイル + 動作確認) |
| 既存 rawdata.csv 再生成 | **不要** |
| 過去週報の再集計 | 必要 (案A・B・Cいずれでも同じ) |
| 長期保守性 | △ (rawdataがJSTなのか UTCなのか、依然として文脈頼み) |
| リスク | 低 (パターンが単純) |

### 案B: export-rawdata.mjs 側で TZ サフィックス付き ISO で出力

**修正例 (export-rawdata.mjs)**
```javascript
// API が "YYYY-MM-DD HH:mm:ss" (JST naive) を返すので、+09:00 を付与
entry_at: item.visitDateTime ? `${item.visitDateTime}+09:00` : '',
exit_at:  item.exitDateTime  ? `${item.exitDateTime}+09:00`  : '',
ordered_at: item.orderedAt   ? `${item.orderedAt}+09:00`     : '',
```
かつ Python 側は:
```python
sales_df['entry_at_jst'] = pd.to_datetime(sales_df['entry_at']).dt.tz_convert('Asia/Tokyo')
```

| 観点 | 評価 |
|---|---|
| 影響範囲 | 中 (Dashboard + Python 両方) |
| 既存 rawdata.csv 再生成 | 必要 (TZ付与のため) |
| 下流 (Python以外: Excel手動確認等) | 影響あり |
| 長期保守性 | ◎ (CSVファイル単体で TZ が自己記述) |
| リスク | 中 (CSVを直接覗く運用箇所が壊れる可能性) |

### 案C: DB UTC統一・export UTC出力・Pythonで UTC→JST 変換

**修正例 (export-rawdata.mjs)**
```javascript
entry_at: sale.entryAt.toISOString(),   // "2025-11-25T11:16:30.000Z" (UTC)
```
かつ Python 側:
```python
sales_df['entry_at_jst'] = pd.to_datetime(sales_df['entry_at'], utc=True).dt.tz_convert('Asia/Tokyo')
```
(現状コードが奇しくも正解になる)

| 観点 | 評価 |
|---|---|
| 影響範囲 | 大 (Dashboard API契約 / Python / 既存 rawdata.csv / 他下流すべて) |
| 既存 rawdata.csv 再生成 | 必要 |
| 長期保守性 | ◎◎ (システム全体で「保存はUTC、表示はJST」の王道) |
| リスク | 高 (Dashboard UI画面が同じAPIを使っているなら表示の整合性確認が必要) |

## 3.2 推奨案

### 推奨: **案A (Python 集計側で修正)**

**理由**:
1. **影響範囲が最小** — Python 7ファイルの単純置換で済む。Dashboard 側は契約上問題なく動作している (UI画面は `visitDateTime` を JST ナイーブ文字列として正しく扱っている)。
2. **既存 rawdata.csv の再生成が不要** — `1_input/` 配下の現rawdataをそのまま使って再集計できる。
3. **緊急性に対応** — W23 の BFA / 麻布しき / 麻布しき本店 を最短で正値に作り直せる。
4. **将来的に案Cへ段階的に移行可能** — 案Aで緊急修正後、別チケットで「rawdata.csv は ISO+TZ にする」「DB と表示層の分離を厳密化する」を進めればよい。今すぐ全層を触る必要はない。

**条件 (採用するなら必須)**:
- 修正パッチを当てる7ファイル全てで **同一の修正パターン** を適用すること (差分レビューしやすくするため)。
- `analysis_script.py` の冒頭コメント `# UTC → JST 変換（+9時間）` を `# rawdata.csv は JST ナイーブ。tz_localize で TZ 情報のみ付与` に更新。
- `weekly_sales_analysis_procedure.md` (手順書) と同期させ、後発の派生スクリプトで再発しないようにする。

## 3.3 修正 diff ドラフト (案A、analysis_script.py)

```diff
--- a/Scripts/analysis_script.py
+++ b/Scripts/analysis_script.py
@@ -166,18 +166,17 @@
 # ==========================================
-# UTC → JST 変換と営業日定義
+# JST 解釈と営業日定義
 # ==========================================
-# 日付型への変換（UTC）
-sales_df['entry_at'] = pd.to_datetime(sales_df['entry_at'], utc=True)
-sales_df['exit_at'] = pd.to_datetime(sales_df['exit_at'], utc=True)
-if 'ordered_at' in sales_df.columns:
-    sales_df['ordered_at'] = pd.to_datetime(sales_df['ordered_at'], utc=True, errors='coerce')
-
-# UTC → JST 変換（+9時間）
-sales_df['entry_at_jst'] = sales_df['entry_at'].dt.tz_convert('Asia/Tokyo')
-sales_df['exit_at_jst'] = sales_df['exit_at'].dt.tz_convert('Asia/Tokyo')
-if 'ordered_at' in sales_df.columns and sales_df['ordered_at'].notna().any():
-    sales_df['ordered_at_jst'] = sales_df['ordered_at'].dt.tz_convert('Asia/Tokyo')
+# rawdata.csv の entry_at / exit_at / ordered_at は
+# Dashboard API が formatUTCtoJST で生成した JST ナイーブ文字列。
+# tz_localize で TZ 情報のみ付与する (+9h シフトはしない)。
+sales_df['entry_at_jst'] = pd.to_datetime(sales_df['entry_at']).dt.tz_localize('Asia/Tokyo')
+sales_df['exit_at_jst']  = pd.to_datetime(sales_df['exit_at']).dt.tz_localize('Asia/Tokyo')
+if 'ordered_at' in sales_df.columns:
+    sales_df['ordered_at_jst'] = pd.to_datetime(sales_df['ordered_at'], errors='coerce').dt.tz_localize('Asia/Tokyo')
```

他 6 ファイルにも同じパターンで適用。詳細は別タスクで実装する。

---

# 4. 再計算プラン

## 4.1 即時対応 (W23 — 既に生成済みの3店舗)

対象: BFA / 麻布しき / 麻布しき本店 の W23 出力

**推奨: 再生成 (バグ補正注記での温存はしない)**

理由:
- 売上が **-38% (BFA実測)** ずれており、配布物として温存する妥当性に欠ける。
- 客単価が業態の典型値から大きく外れる (BFA: ¥5,067 vs 実勢 ¥29,883) ため、報告書を見た人が誤った経営判断を導くリスクが高い。
- 注記運用は「正値はどこ」の追跡コストを永久に背負う。

**作り直しの手順 (別タスクで実施)**:
1. `Scripts/analysis_script.py` ほか 7 ファイルに案Aパッチを適用。
2. `git diff` でレビューしフィクスをコミット。
3. 既存 `1_input/{BFA,麻布しき,麻布しき本店}/rawdata.csv` を **再ダウンロードせず** そのまま入力に使う (rawdataはJSTで正しい)。
4. `analysis_script.py` を `--start-date 2026-06-01 --end-date 2026-06-07` で 3 店舗実行。
5. 出力先は `2_output/{店舗}/2_output_2026w23/` を一度退避 (`*_bugged_20260610/`) してから新規生成。
6. 新KPIをマスター提示のW23正値 (BFA 売上 ¥806,830 / 客単価 ¥29,883) と突合し、誤差±0.1%以内であることを確認。

## 4.2 過去週報の扱い

### 提案: 「過去の週報出力は再生成せず、生データから直再集計するクエリのみ用意する」

**理由**:
- 2026年全週 × 5店舗 = 約 90週分 + 月報多数 を再生成するコストは現実的でない。
- 一方、誤値で意思決定が積み上がっているリスクは無視できない。
- 折衷案として、**過去週分の KPI 比較表を CSV で一括出力する補助スクリプト** を1本作り、「報告書 W## の客単価X円は、実は Y円 (+ZZ%)」の対照表を提供する。

**実行プラン**:
1. (上記 4.1 で案A適用済みのスクリプトを使用)
2. 補助スクリプト `Scripts/recompute_history.py` (新規) を作成: `1_input/{店舗}/rawdata.csv` 全期間を読み、店舗×ISO週単位で `売上 / 客数 / 客単価 / 客組数` を計算 → 単一CSV出力。
3. 出力 CSV を `_investigations/2026-06-10_history_kpi_corrected.csv` として保存。
4. マスターと相談し、業務判断の見直しが必要な週 (ズレ閾値 ±10%) を優先的にレビュー。

**完全再生成しない判断の合理性**:
- 報告書本文 (グラフ・所見・施策提案) はバグ値前提で書かれているため、KPIだけ差し替えても整合しない。再生成するなら所見も書き直しになる。
- 「対照表 + 必要に応じた個別週の作り直し」が最小コストで意思決定品質を回復する道筋。

## 4.3 ガードレール (再発防止)

修正実装と合わせて以下を別タスクで実施推奨:
1. **analysis_script.py に assert を追加**: rawdata の `entry_at` 列がJSTと矛盾しないか、`day_of_week` カラムとの整合チェックを `--strict` モードで実行 (今回の検証1と同じロジック)。
2. **export-rawdata.mjs のヘッダコメント追記**: 「entry_at / exit_at は JST ナイーブ文字列。下流で UTC とみなさないこと」。
3. **CLAUDE.md (週報配下)** に方針を追記: 「rawdata.csv の時刻列は JST。Python側では `tz_localize('Asia/Tokyo')` を使う」。

---

# 5. 本タスクの完了条件

- [x] 原因の特定 (DB / API / export / Python 各層)
- [x] 影響範囲の洗い出し (週報7ファイル + 月報3ファイル + 出力多数)
- [x] 修正方針3案の比較と推奨選定 (案A推奨)
- [x] 修正 diff ドラフト (analysis_script.py)
- [x] 再計算プラン (即時 / 過去 / ガードレール)
- [ ] **コード修正コミット**: 別タスク
- [ ] **W23 3店舗の再生成**: 別タスク
- [ ] **過去週対照表の生成**: 別タスク

---

## 付録A: バグの定量シミュレーション (参考)

BFA W23 (2026-06-01〜06-07) のバー業態 (営業時間 18:00-01:00) の典型的な売上発生時刻を想定:

| 実態 (JST) | バグ後の解釈 (+9h) | バグ後の `business_date` (cutoff 5時) | 正しい `business_date` |
|---|---|---|---|
| 6/1 (月) 19:30 | 6/2 (火) 04:30 | 6/1 (月) (深夜帯前日付替) | 6/1 (月) |
| 6/1 (月) 22:00 | 6/2 (火) 07:00 | 6/2 (火) | 6/1 (月) |
| 6/2 (火) 00:30 (= 6/1営業日) | 6/2 (火) 09:30 | 6/2 (火) | 6/1 (月) |

→ 月曜営業の売上が **火曜・水曜の業務日に分散**。一方、6/7 (日) 深夜の売上は 6/8 (月、W24) に転出 → W23の対象期間 (`date >= 2026-06-01 & date <= 2026-06-07`) から脱落。

これにより:
- W23 集計対象件数が減少 (深夜売上の取りこぼし) → 売上 -38%
- 客数は会計単位なのでさらにズレ方が異なる (客組数だけ残り客数が乖離) → 客単価が異常値化 (¥5,067)

