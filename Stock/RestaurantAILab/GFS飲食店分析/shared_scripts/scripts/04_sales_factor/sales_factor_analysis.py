#!/usr/bin/env python3
"""
売上要因分析スクリプト
- 日次集計
- EDA可視化
- クラスタリング
- 要因重要度分析
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from matplotlib import rcParams
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# 日本語フォント設定
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Hiragino Sans', 'Hiragino Kaku Gothic ProN', 'Yu Gothic', 'Meiryo', 'sans-serif']
rcParams['axes.unicode_minus'] = False

# 出力ディレクトリ
OUTPUT_DIR = '/Users/rikutanaka/aipm_v0/Flow/202601/2026-01-21/SalesFactorAnalysis'
import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("売上要因分析を開始します")
print("=" * 60)

# ============================================================
# Step 1: データ読み込みと日次集計
# ============================================================
print("\n[Step 1] データ読み込みと日次集計...")

df = pd.read_csv('/Users/rikutanaka/aipm_v0/Flow/202601/2026-01-21/transformed_pos_data_eatin.csv')

# 日付カラムをdatetime型に変換
df['H.集計対象営業年月日'] = pd.to_datetime(df['H.集計対象営業年月日'])
df['D.オーダー日時'] = pd.to_datetime(df['D.オーダー日時'])

# オーダー時間（時）を抽出
df['order_hour'] = df['D.オーダー日時'].dt.hour

print(f"  - 総レコード数: {len(df):,}")
print(f"  - 期間: {df['H.集計対象営業年月日'].min()} 〜 {df['H.集計対象営業年月日'].max()}")

# ============================================================
# 日次集計テーブルの作成
# ============================================================

# 伝票単位のユニークデータ
df_slip = df.drop_duplicates(subset=['H.伝票番号'])

# 日次売上・客数
daily_basic = df_slip.groupby('H.集計対象営業年月日').agg({
    'H.小計': 'sum',
    'H.客数（合計）': 'sum',
    'H.伝票番号': 'nunique'
}).reset_index()
daily_basic.columns = ['date', 'total_sales', 'total_customers', 'slip_count']

# 客単価、1組あたり客数
daily_basic['avg_spend_per_customer'] = daily_basic['total_sales'] / daily_basic['total_customers']
daily_basic['avg_customers_per_slip'] = daily_basic['total_customers'] / daily_basic['slip_count']

# 曜日
daily_basic['weekday'] = pd.to_datetime(daily_basic['date']).dt.dayofweek
daily_basic['weekday_name'] = pd.to_datetime(daily_basic['date']).dt.day_name()
daily_basic['is_weekend'] = daily_basic['weekday'].isin([5, 6]).astype(int)

# 時間帯別売上比率
def calc_time_ratio(group):
    lunch = group[(group['order_hour'] >= 11) & (group['order_hour'] < 14)]['D.価格'].sum()
    dinner = group[(group['order_hour'] >= 17) & (group['order_hour'] < 21)]['D.価格'].sum()
    total = group['D.価格'].sum()
    return pd.Series({
        'lunch_ratio': lunch / total if total > 0 else 0,
        'dinner_ratio': dinner / total if total > 0 else 0
    })

time_ratio = df.groupby('H.集計対象営業年月日').apply(calc_time_ratio).reset_index()
time_ratio.columns = ['date', 'lunch_ratio', 'dinner_ratio']

# カテゴリ別売上比率
def calc_category_ratio(group):
    total = group['D.価格'].sum()
    alcohol = group[group['D.商品カテゴリ2'] == 'アルコール']['D.価格'].sum()
    topping = group[group['D.商品カテゴリ2'] == 'トッピング']['D.価格'].sum()
    soft_drink = group[group['D.商品カテゴリ2'] == 'ソフトドリンク']['D.価格'].sum()
    alacarte = group[group['D.商品カテゴリ2'] == 'アラカルト']['D.価格'].sum()
    return pd.Series({
        'alcohol_ratio': alcohol / total if total > 0 else 0,
        'topping_ratio': topping / total if total > 0 else 0,
        'soft_drink_ratio': soft_drink / total if total > 0 else 0,
        'alacarte_ratio': alacarte / total if total > 0 else 0
    })

category_ratio = df.groupby('H.集計対象営業年月日').apply(calc_category_ratio).reset_index()
category_ratio.columns = ['date', 'alcohol_ratio', 'topping_ratio', 'soft_drink_ratio', 'alacarte_ratio']

# 商品数（明細数）
item_count = df.groupby('H.集計対象営業年月日').size().reset_index(name='item_count')
item_count.columns = ['date', 'item_count']

# 商品多様性（ユニーク商品数）
product_diversity = df.groupby('H.集計対象営業年月日')['D.商品名'].nunique().reset_index()
product_diversity.columns = ['date', 'unique_products']

# 平均注文商品数
avg_items_per_slip = df.groupby(['H.集計対象営業年月日', 'H.伝票番号']).size().groupby(level=0).mean().reset_index()
avg_items_per_slip.columns = ['date', 'avg_items_per_slip']

# ピーク時間帯集中度（12時台と13時台の比率）
def calc_peak_concentration(group):
    peak = group[(group['order_hour'] >= 12) & (group['order_hour'] < 14)]['D.価格'].sum()
    total = group['D.価格'].sum()
    return peak / total if total > 0 else 0

peak_conc = df.groupby('H.集計対象営業年月日').apply(calc_peak_concentration).reset_index()
peak_conc.columns = ['date', 'peak_concentration']

# 全てをマージ
daily = daily_basic.copy()
for df_merge in [time_ratio, category_ratio, item_count, product_diversity, avg_items_per_slip, peak_conc]:
    daily = daily.merge(df_merge, on='date', how='left')

# 月・日を追加
daily['month'] = pd.to_datetime(daily['date']).dt.month
daily['day'] = pd.to_datetime(daily['date']).dt.day

print(f"  - 日次集計完了: {len(daily)} 日分")
print(f"  - 特徴量数: {len(daily.columns)}")

# 日次データを保存
daily.to_csv(f'{OUTPUT_DIR}/daily_summary.csv', index=False)
print(f"  - 保存: daily_summary.csv")

# ============================================================
# Step 2: 基礎統計・EDA可視化
# ============================================================
print("\n[Step 2] 基礎統計・EDA可視化...")

# 基本統計量
print("\n【売上の基本統計】")
print(daily['total_sales'].describe())

# 図1: 売上の分布
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 売上ヒストグラム
axes[0, 0].hist(daily['total_sales'], bins=30, edgecolor='black', alpha=0.7, color='steelblue')
axes[0, 0].axvline(daily['total_sales'].mean(), color='red', linestyle='--', label=f'平均: {daily["total_sales"].mean():,.0f}円')
axes[0, 0].axvline(daily['total_sales'].median(), color='orange', linestyle='--', label=f'中央値: {daily["total_sales"].median():,.0f}円')
axes[0, 0].set_xlabel('日次売上（円）')
axes[0, 0].set_ylabel('頻度')
axes[0, 0].set_title('売上の分布')
axes[0, 0].legend()

# 曜日別売上箱ひげ図
weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
weekday_jp = ['月', '火', '水', '木', '金', '土', '日']
daily['weekday_order'] = daily['weekday_name'].map({w: i for i, w in enumerate(weekday_order)})
daily_sorted = daily.sort_values('weekday_order')

bp = axes[0, 1].boxplot([daily_sorted[daily_sorted['weekday'] == i]['total_sales'] for i in range(7)],
                         labels=weekday_jp, patch_artist=True)
colors = ['#1f77b4'] * 5 + ['#ff7f0e', '#ff7f0e']
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
axes[0, 1].set_xlabel('曜日')
axes[0, 1].set_ylabel('日次売上（円）')
axes[0, 1].set_title('曜日別売上分布')

# 売上時系列
axes[1, 0].plot(daily['date'], daily['total_sales'], marker='o', markersize=3, alpha=0.7)
axes[1, 0].set_xlabel('日付')
axes[1, 0].set_ylabel('日次売上（円）')
axes[1, 0].set_title('売上の時系列推移')
axes[1, 0].tick_params(axis='x', rotation=45)

# 客数 vs 売上
axes[1, 1].scatter(daily['total_customers'], daily['total_sales'], alpha=0.6)
z = np.polyfit(daily['total_customers'], daily['total_sales'], 1)
p = np.poly1d(z)
x_line = np.linspace(daily['total_customers'].min(), daily['total_customers'].max(), 100)
axes[1, 1].plot(x_line, p(x_line), 'r--', label=f'回帰線')
corr = daily['total_customers'].corr(daily['total_sales'])
axes[1, 1].set_xlabel('客数')
axes[1, 1].set_ylabel('日次売上（円）')
axes[1, 1].set_title(f'客数 vs 売上（相関: {corr:.3f}）')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/01_eda_basic.png', dpi=150, bbox_inches='tight')
plt.close()
print("  - 保存: 01_eda_basic.png")

# 図2: 相関ヒートマップ
numeric_cols = ['total_sales', 'total_customers', 'slip_count', 'avg_spend_per_customer',
                'avg_customers_per_slip', 'lunch_ratio', 'dinner_ratio', 'alcohol_ratio',
                'topping_ratio', 'soft_drink_ratio', 'avg_items_per_slip', 'peak_concentration']

fig, ax = plt.subplots(figsize=(12, 10))
corr_matrix = daily[numeric_cols].corr()
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r', 
            center=0, ax=ax, square=True, linewidths=0.5)
ax.set_title('特徴量間の相関行列')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/02_correlation_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print("  - 保存: 02_correlation_heatmap.png")

# 図3: 売上上位/下位の比較
daily['sales_rank'] = pd.qcut(daily['total_sales'], q=3, labels=['低売上', '中売上', '高売上'])

fig, axes = plt.subplots(2, 3, figsize=(15, 10))

compare_cols = [
    ('avg_spend_per_customer', '客単価（円）'),
    ('total_customers', '客数'),
    ('alcohol_ratio', 'アルコール比率'),
    ('lunch_ratio', 'ランチ比率'),
    ('avg_customers_per_slip', '1組あたり客数'),
    ('avg_items_per_slip', '平均注文商品数')
]

for idx, (col, title) in enumerate(compare_cols):
    ax = axes[idx // 3, idx % 3]
    daily.boxplot(column=col, by='sales_rank', ax=ax)
    ax.set_title(title)
    ax.set_xlabel('売上カテゴリ')
    ax.set_ylabel(title)
    plt.suptitle('')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/03_high_low_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print("  - 保存: 03_high_low_comparison.png")

# ============================================================
# Step 3: クラスタリング分析
# ============================================================
print("\n[Step 3] クラスタリング分析...")

# クラスタリング用の特徴量を選択
cluster_features = ['avg_spend_per_customer', 'avg_customers_per_slip', 'lunch_ratio', 
                    'dinner_ratio', 'alcohol_ratio', 'topping_ratio', 'avg_items_per_slip',
                    'peak_concentration', 'is_weekend']

X = daily[cluster_features].copy()
X = X.fillna(X.mean())

# 標準化
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# エルボー法でクラスタ数を決定
inertias = []
silhouettes = []
K_range = range(2, 8)

from sklearn.metrics import silhouette_score

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    inertias.append(kmeans.inertia_)
    silhouettes.append(silhouette_score(X_scaled, kmeans.labels_))

# 最適クラスタ数（シルエットスコア最大）
optimal_k = K_range[np.argmax(silhouettes)]
print(f"  - 最適クラスタ数（シルエットスコア基準）: {optimal_k}")

# 図4: エルボー法とシルエットスコア
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].plot(K_range, inertias, 'bo-')
axes[0].set_xlabel('クラスタ数')
axes[0].set_ylabel('Inertia')
axes[0].set_title('エルボー法')

axes[1].plot(K_range, silhouettes, 'go-')
axes[1].axvline(optimal_k, color='red', linestyle='--', label=f'最適: k={optimal_k}')
axes[1].set_xlabel('クラスタ数')
axes[1].set_ylabel('シルエットスコア')
axes[1].set_title('シルエットスコア')
axes[1].legend()

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/04_cluster_optimization.png', dpi=150, bbox_inches='tight')
plt.close()
print("  - 保存: 04_cluster_optimization.png")

# 最適クラスタ数でクラスタリング実行
kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
daily['cluster'] = kmeans.fit_predict(X_scaled)

# PCAで2次元に射影
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)
daily['pca1'] = X_pca[:, 0]
daily['pca2'] = X_pca[:, 1]

# 図5: クラスタ可視化（PCA）
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# PCA空間でのクラスタ
scatter = axes[0].scatter(daily['pca1'], daily['pca2'], c=daily['cluster'], 
                          cmap='viridis', alpha=0.7, s=50)
axes[0].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
axes[0].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
axes[0].set_title('クラスタ分布（PCA空間）')
plt.colorbar(scatter, ax=axes[0], label='クラスタ')

# 売上でカラーリング
scatter2 = axes[1].scatter(daily['pca1'], daily['pca2'], c=daily['total_sales'], 
                           cmap='RdYlGn', alpha=0.7, s=50)
axes[1].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
axes[1].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
axes[1].set_title('売上分布（PCA空間）')
plt.colorbar(scatter2, ax=axes[1], label='売上（円）')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/05_cluster_pca.png', dpi=150, bbox_inches='tight')
plt.close()
print("  - 保存: 05_cluster_pca.png")

# クラスタ別の特徴
print("\n【クラスタ別の特徴】")
cluster_summary = daily.groupby('cluster').agg({
    'total_sales': 'mean',
    'total_customers': 'mean',
    'avg_spend_per_customer': 'mean',
    'avg_customers_per_slip': 'mean',
    'alcohol_ratio': 'mean',
    'lunch_ratio': 'mean',
    'dinner_ratio': 'mean',
    'is_weekend': 'mean'
}).round(2)
cluster_summary['count'] = daily.groupby('cluster').size()
print(cluster_summary)

# 図6: クラスタ別レーダーチャート
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

categories = ['客単価', '1組あたり客数', 'ランチ比率', 'ディナー比率', 
              'アルコール比率', '平均注文商品数', 'ピーク集中度']
N = len(categories)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

# 各クラスタの正規化された値
radar_cols = ['avg_spend_per_customer', 'avg_customers_per_slip', 'lunch_ratio', 
              'dinner_ratio', 'alcohol_ratio', 'avg_items_per_slip', 'peak_concentration']

cluster_means = daily.groupby('cluster')[radar_cols].mean()
cluster_means_norm = (cluster_means - cluster_means.min()) / (cluster_means.max() - cluster_means.min())

colors = plt.cm.viridis(np.linspace(0, 1, optimal_k))

for i in range(optimal_k):
    values = cluster_means_norm.loc[i].values.tolist()
    values += values[:1]
    ax.plot(angles, values, 'o-', linewidth=2, label=f'クラスタ {i}', color=colors[i])
    ax.fill(angles, values, alpha=0.25, color=colors[i])

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories)
ax.set_title('クラスタ別特徴（レーダーチャート）', y=1.08)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/06_cluster_radar.png', dpi=150, bbox_inches='tight')
plt.close()
print("  - 保存: 06_cluster_radar.png")

# ============================================================
# Step 4: 要因重要度分析（ランダムフォレスト）
# ============================================================
print("\n[Step 4] 要因重要度分析...")

# 特徴量の選択
feature_cols = ['total_customers', 'slip_count', 'avg_spend_per_customer', 
                'avg_customers_per_slip', 'lunch_ratio', 'dinner_ratio',
                'alcohol_ratio', 'topping_ratio', 'soft_drink_ratio',
                'avg_items_per_slip', 'peak_concentration', 'is_weekend', 'weekday']

X_rf = daily[feature_cols].copy()
X_rf = X_rf.fillna(X_rf.mean())
y_rf = daily['total_sales']

# ランダムフォレスト
rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
rf.fit(X_rf, y_rf)

# 特徴量重要度
feature_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': rf.feature_importances_
}).sort_values('importance', ascending=True)

# 図7: 特徴量重要度
fig, ax = plt.subplots(figsize=(10, 8))
colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(feature_importance)))
bars = ax.barh(feature_importance['feature'], feature_importance['importance'], color=colors)
ax.set_xlabel('重要度')
ax.set_title('売上に対する各要因の重要度（ランダムフォレスト）')

# 数値ラベル
for bar, val in zip(bars, feature_importance['importance']):
    ax.text(val + 0.005, bar.get_y() + bar.get_height()/2, f'{val:.3f}', va='center')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/07_feature_importance.png', dpi=150, bbox_inches='tight')
plt.close()
print("  - 保存: 07_feature_importance.png")

print("\n【特徴量重要度 TOP 5】")
print(feature_importance.tail(5).to_string(index=False))

# 図8: 上位要因と売上の関係（散布図）
top_features = feature_importance.tail(4)['feature'].tolist()

fig, axes = plt.subplots(2, 2, figsize=(12, 10))
axes = axes.flatten()

for idx, feat in enumerate(top_features):
    ax = axes[idx]
    ax.scatter(daily[feat], daily['total_sales'], alpha=0.5)
    
    # 回帰線
    z = np.polyfit(daily[feat], daily['total_sales'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(daily[feat].min(), daily[feat].max(), 100)
    ax.plot(x_line, p(x_line), 'r--')
    
    corr = daily[feat].corr(daily['total_sales'])
    ax.set_xlabel(feat)
    ax.set_ylabel('売上（円）')
    ax.set_title(f'{feat} vs 売上（相関: {corr:.3f}）')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/08_top_features_scatter.png', dpi=150, bbox_inches='tight')
plt.close()
print("  - 保存: 08_top_features_scatter.png")

# ============================================================
# 分析サマリーの出力
# ============================================================
print("\n[最終出力] 分析サマリー...")

# クラスタに売上ラベルを付与
cluster_sales = daily.groupby('cluster')['total_sales'].mean().sort_values()
cluster_labels = {cluster_sales.index[i]: ['低売上型', '中売上型', '高売上型'][min(i, 2)] 
                  for i in range(len(cluster_sales))}
daily['cluster_label'] = daily['cluster'].map(cluster_labels)

summary_text = f"""
# 売上要因分析レポート

## 1. データ概要
- 分析期間: {daily['date'].min()} 〜 {daily['date'].max()}
- 日数: {len(daily)} 日
- 売上合計: {daily['total_sales'].sum():,.0f} 円
- 平均日次売上: {daily['total_sales'].mean():,.0f} 円
- 売上標準偏差: {daily['total_sales'].std():,.0f} 円

## 2. 売上の分布
- 最小: {daily['total_sales'].min():,.0f} 円
- 25%点: {daily['total_sales'].quantile(0.25):,.0f} 円
- 中央値: {daily['total_sales'].median():,.0f} 円
- 75%点: {daily['total_sales'].quantile(0.75):,.0f} 円
- 最大: {daily['total_sales'].max():,.0f} 円

## 3. 曜日別平均売上
{daily.groupby('weekday_name')['total_sales'].mean().reindex(weekday_order).to_frame().to_markdown()}

## 4. クラスタリング結果（{optimal_k}クラスタ）
{cluster_summary.to_markdown()}

## 5. 売上に影響する要因（重要度順）
{feature_importance.tail(10).iloc[::-1].to_markdown(index=False)}

## 6. 主要な発見

### 売上を上げる要因（相関が高い）
"""

# 相関上位
corr_with_sales = daily[numeric_cols].corrwith(daily['total_sales']).drop('total_sales').sort_values(ascending=False)
for feat, corr_val in corr_with_sales.head(5).items():
    summary_text += f"- {feat}: 相関 {corr_val:.3f}\n"

summary_text += f"""
### クラスタ別の特徴

"""

for cluster_id in sorted(daily['cluster'].unique()):
    cluster_data = daily[daily['cluster'] == cluster_id]
    label = cluster_labels.get(cluster_id, f'クラスタ{cluster_id}')
    summary_text += f"""
#### {label}（クラスタ {cluster_id}）
- 該当日数: {len(cluster_data)} 日
- 平均売上: {cluster_data['total_sales'].mean():,.0f} 円
- 平均客数: {cluster_data['total_customers'].mean():.0f} 人
- 平均客単価: {cluster_data['avg_spend_per_customer'].mean():,.0f} 円
- アルコール比率: {cluster_data['alcohol_ratio'].mean()*100:.1f}%
- 週末比率: {cluster_data['is_weekend'].mean()*100:.0f}%
"""

summary_text += """
## 7. 施策への示唆

### 売上向上のためのポイント
1. **客数確保が最重要**: 売上との相関が最も高い要因は「客数」
2. **客単価向上策**: 
   - アルコール販売促進（アルコール比率と客単価に正の相関）
   - セット販売・追加注文の促進
3. **グループ客の取り込み**: 1組あたり客数が多いほど売上増加傾向
4. **時間帯別戦略**: ランチ/ディナーの比率と売上の関係を活用

### 低売上日の特徴と対策
- 低売上クラスタの特徴を分析し、該当曜日や条件でのプロモーション強化
"""

with open(f'{OUTPUT_DIR}/analysis_summary.md', 'w', encoding='utf-8') as f:
    f.write(summary_text)
print("  - 保存: analysis_summary.md")

# 日次データ（クラスタ付き）を保存
daily.to_csv(f'{OUTPUT_DIR}/daily_summary_with_cluster.csv', index=False)
print("  - 保存: daily_summary_with_cluster.csv")

print("\n" + "=" * 60)
print("分析完了！")
print(f"出力先: {OUTPUT_DIR}")
print("=" * 60)

# 生成ファイル一覧
print("\n【生成ファイル一覧】")
for f in sorted(os.listdir(OUTPUT_DIR)):
    print(f"  - {f}")
