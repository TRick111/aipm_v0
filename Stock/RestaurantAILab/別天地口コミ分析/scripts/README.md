# 分析スクリプト

## regenerate_graphs.py

食べログ口コミデータから数値分析グラフを生成するPythonスクリプト

### 機能
- カテゴリ別平均評価の横棒グラフ
- 総合評価の分布ヒストグラム
- カテゴリ別評価の箱ひげ図
- 月別レビュー数の推移
- 月別平均評価の推移（移動平均含む）
- いいね数分析（分布とスコアとの関係）

### 使用方法

```bash
# データファイル（reviews_output.csv）と同じディレクトリで実行
python regenerate_graphs.py
```

### 出力
- `1_overall_rating.png` - 総合評価の分布
- `2_category_avg.png` - カテゴリ別平均評価
- `3_boxplot.png` - 評価分布の比較
- `4_monthly_trend.png` - 月別レビュー数の推移
- `4_monthly_avg_rating.png` - 月別平均評価の推移
- `5_likes_analysis.png` - いいね数分析

### 必要なライブラリ
```bash
pip install pandas matplotlib seaborn
```

### 日本語フォント対応
- Windowsの場合: Yu Gothic（YuGothM.ttc）を自動検出
- その他: システムにインストールされている日本語フォントを自動選択
- FontPropertiesを使用して全テキスト要素に明示的に適用

### データ形式
CSVファイル（UTF-8 with BOM）に以下のカラムが必要:
- `投稿日`: 投稿日（例: '26/01/14 形式）
- `総合評価`: 1-5の数値
- `料理・味`, `サービス`, `雰囲気`, `CP`, `酒・ドリンク`: カテゴリ別評価
- `いいね数`: 数値

### 注意点
- 日付データは単一引用符付き（'YY/MM/DD）形式に対応
- 欠損値は自動的に除外して処理
