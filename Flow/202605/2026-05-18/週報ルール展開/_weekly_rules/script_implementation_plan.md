# 週報スクリプト修正 実装プラン（別タスクで実施）

**作成日**: 2026-05-19  
**ステータス**: **未実装・マスター承認済み（K-8）**  
**実施タスク**: 別タスクで実装（このルール展開タスクとは分離）

## マスター判断（K-8）

優先順位:
1. **#2 合計>0 フィルタ追加**（全店舗・高優先）
2. **#3 BFA ボトル除外**（BFA・高優先）
3. **#4 ランキング TOP10→TOP15＋★マーク**（全店舗・中優先）

その他（#5, #6, #7, #8）は後続タスクで対応。
#1（業務日基準）と #9（dashboard_data_pipeline.py）は確認のみで完了。

---

## 実装タスクの推奨スコープ

### タスク名（推奨）
「週報スクリプト 月報ルール反映 第1弾 — 合計>0 フィルタ ／ BFA ボトル除外 ／ TOP15＋★マーク」

### 実行ディレクトリ
`Stock/RestaurantAILab/週報/`

### 作業ブランチ／バックアップ命名
- 各スクリプトを修正前にコピー: `<filename>.bak_20260519_apply_monthly_rules_phase2`
- コミットメッセージ例: `週報スクリプト: 合計>0 フィルタ ／ BFA ボトル除外 ／ ランキング TOP15＋★マーク を追加`

---

## #2 合計>0 フィルタ（最優先 / 全店舗）

### 影響範囲
- `Scripts/analysis_script.py` — 主対象（200行目あたり、business_date 計算の直後）
- `Scripts/deep_dive_weekday_analysis.py` — 同様にデータ読み込み直後にフィルタ追加
- `Scripts/bfa_category_product_ranking_html.py` — 同様

### 提案差分

```python
# analysis_script.py / business_date 計算後
prev_count = len(sales_df)
sales_df = sales_df[sales_df['account_total'] > 0].copy()
filtered_count = prev_count - len(sales_df)
print(f"[INFO] 合計>0 フィルタ後の明細数: {len(sales_df):,} （除外: {filtered_count}件）", file=sys.stderr)
```

### 検証手順
1. 既存の BFA W19 等の週報を再生成
2. 既存出力との数値差分（売上 / 客数 / 組数）を `_weekly_rules/diff_logs/合計0_diff.md` に記録
3. 差分が業務的に妥当（赤伝・無効会計の除外 → 売上微増・組数微減）か確認

### 期待される影響
- 売上: わずかに増加または不変（マイナス会計を除外するため）
- 組数: わずかに減少（カウントから外れる）
- 顧客あたり数値: 微変動

### マスター確認ポイント
- BFA以外（BBC / 麻布しき / キーポイント）にも適用していいか
- データ品質ログ（除外件数）の保存先

---

## #3 BFA ボトル除外（高優先 / BFA限定）

### 影響範囲
- `Scripts/analysis_script.py` — 曜日別 / 時間帯別 / 会計レベル集計の前にフィルタを分岐

### 提案差分

```python
# analysis_script.py 内
EXCLUDE_BOTTLE_CATEGORIES = {'ボトル購入'}

# 全集計用（週次総売上）
sales_df_all = sales_df.copy()

# ボトル除外用（曜日別・時間帯別・会計レベル）
if operating_company == 'BFA':
    sales_df_nobottle = sales_df[~sales_df['category1'].isin(EXCLUDE_BOTTLE_CATEGORIES)].copy()
else:
    sales_df_nobottle = sales_df.copy()  # 他店舗はそのまま

# 週次総売上は sales_df_all、曜日別・時間帯別は sales_df_nobottle を使う
```

### 適用箇所（具体的に変更する処理）
- `by_day_of_week` の売上・客数集計 → `sales_df_nobottle`
- `by_hour` の売上・客数集計 → `sales_df_nobottle`
- 会計レベル分布（中央値・P10・P90 等） → `sales_df_nobottle`
- 客単価（経営判断用）→ `sales_df_nobottle` 由来
- 客単価（エアメイト比較用）→ `sales_df_all` 由来

### 検証手順
1. BFA の最新週で再生成し、既存出力と比較
2. 「金曜の異常値（ボトル単発高額）」が消えていることを確認
3. 月報側の値（同月）と曜日別売上が整合することを確認

### 期待される影響
- BFA の曜日別・時間帯別売上が変動（特に大口ボトル購入があった曜日）
- 客単価（ボトル除く）が表示される
- 週次総売上は不変

### マスター確認ポイント
- BFA 以外でボトル相当（高額単発商品）の除外が必要かは保留
- 「BFAだけ特例で2系統客単価を表示する」運用が UX 的に許容されるか

---

## #4 ランキング TOP10 → TOP15 ＋ ★マーク（中優先 / 全店舗）

### 影響範囲
- `Scripts/analysis_script.py` — フード/ドリンクランキング生成箇所
- `03_スライド構成案作成_プロンプト.md` — 表構成更新
- `05_HTMLスライド作成_プロンプト.md` — 表レイアウト調整（15行収容）

### 提案差分

```python
# analysis_script.py
TOP_N = 15  # 旧 10 → 15

# 列構成: 出数 / 入客数 / 売上 / 平均販売価格 / 構成比 / ★
ranking_df['avg_price'] = ranking_df['subtotal'] / ranking_df['quantity']
ranking_df['price_dev_pct'] = ((ranking_df['avg_price'] - ranking_df['registered_price']) / ranking_df['registered_price'] * 100)
ranking_df['star'] = ranking_df['price_dev_pct'].abs() >= 5.0  # ±5%以上で★
```

### 検証手順
1. BFA 最新週で再生成
2. ★マーク付きメニューが期待通りか（実際のダブル販売や特別価格商品）を確認
3. スライド表に15行が収まることを HTML プレビューで確認

### マスター確認ポイント
- `registered_price` カラムが rawdata.csv に存在するか要確認
  - 不在の場合は「メニュー名ごとの最頻値価格」を簡易の登録価格として使う代替案
- 15行表示で他のスライド要素が崩れないか

---

## 後続タスク（K-8 で「後で」と分類されたもの）

### #5 客単価2系統（BFA）
- `analysis_results.json` に `spend_per_head_excl_bottle` / `spend_per_head_incl_bottle` を追加
- 03 / 05 プロンプトの KPI カードを BFA だけ2行化

### #6 インバウンド自動非表示
- → K-5 で週報にインバウンドスライドを **追加しない** ことが確定したため、本項目は **不要**

### #7 出典表記統一
- 05 プロンプトのフッターテンプレを以下に統一
  - BFA / キーポイント: 「出典: エアレジ会計明細」
  - BBC: 「出典: Dinii 注文データ」
  - 麻布しき: 「出典: USENレジ 売上データ」

### #8 カテゴリ分類マスタ整合確認
- `Scripts/analysis_script.py` のランキング生成で `カテゴリ分類マスタ.md` の food/drink 分類を介していることを確認
- 新規カテゴリ発生時の追記ルールを再確認

---

## タスク完了条件

各 #2 / #3 / #4 で:

- [ ] 修正前にバックアップ（`.bak_20260519_apply_monthly_rules_phase2`）取得
- [ ] BFA / BBC / 麻布しき の最新週で再生成
- [ ] 差分ログ（`_weekly_rules/diff_logs/`）を保存
- [ ] 月報の同月数値と整合確認（特に #2 / #3）
- [ ] プロンプト側（03 / 05）と整合 — 表構成・KPI表示
- [ ] STATUS.md / log.md を更新

---

## 推奨実装順

1. **準備**: `Flow/.../週報スクリプト適用_第1弾/` ディレクトリを作成、最新の BFA W19 等の出力を待避してベースライン化
2. **#2 実装** → 全店舗で再生成・差分確認
3. **#3 実装** → BFA で再生成・月報整合確認
4. **#4 実装** → プロンプト側の表構成更新と並行
5. **コミット**（バックアップ確認後）
6. **STATUS.md / log.md 更新**
7. **マスター報告**

---

## 関連ファイル

- `_weekly_rules/script_changes.md` — 当初の修正提案9件（K-8 で #2/#3/#4 を高優先と確定）
- `_weekly_rules/questions_to_user.md` — マスター回答（回答済み）
- `_weekly_rules/classification.md` — 月報→週報 ルール分類（確定版）
