import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import matplotlib.font_manager as fm
from matplotlib.font_manager import FontProperties
import sys
import warnings
warnings.filterwarnings('ignore')

sys.stdout.reconfigure(encoding='utf-8')

# フォントキャッシュをクリア
try:
    fm._rebuild()
except:
    pass

# 日本語フォントの検索と設定
print('日本語フォント設定中...')
available_fonts = {f.name: f.fname for f in fm.fontManager.ttflist}

font_candidates = [
    'Yu Gothic', 'MS Gothic', 'Meiryo', 'BIZ UDGothic',
    'Noto Sans CJK JP', 'Noto Sans JP'
]

selected_font = None
font_path = None

for font_name in font_candidates:
    if font_name in available_fonts:
        selected_font = font_name
        font_path = available_fonts[font_name]
        print(f'使用フォント: {selected_font}')
        print(f'パス: {font_path}')
        break

if not selected_font:
    print('エラー: 日本語フォントが見つかりません')
    sys.exit(1)

# FontPropertiesオブジェクトを作成（これが重要！）
font_prop = FontProperties(fname=font_path)

# rcParamsで全体設定
plt.rcParams['axes.unicode_minus'] = False

# データ読み込み
df = pd.read_csv('reviews_output.csv', encoding='utf-8-sig')
# 日付の単一引用符を削除してから正しいフォーマットで解釈
df['投稿日_cleaned'] = df['投稿日'].str.replace("'", "", regex=False)
df['投稿日_parsed'] = pd.to_datetime(df['投稿日_cleaned'], format='%y/%m/%d', errors='coerce')
df['year_month'] = df['投稿日_parsed'].dt.to_period('M')

cats = ['料理・味', 'サービス', '雰囲気', 'CP', '酒・ドリンク']
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']

print('\nグラフ生成開始...')

# 1. カテゴリ別平均評価
print('1/6 カテゴリ別平均評価')
means = [df[c].mean() for c in cats]
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(range(len(cats)), means, color=colors, edgecolor='black', alpha=0.8, linewidth=1.5)
ax.set_yticks(range(len(cats)))
ax.set_yticklabels(cats, fontproperties=font_prop, fontsize=11)
ax.set_xlabel('平均評価スコア', fontproperties=font_prop, fontsize=12)
ax.set_title('カテゴリ別平均評価', fontproperties=font_prop, fontsize=16, fontweight='bold', pad=20)
ax.set_xlim([0, 5])
ax.grid(axis='x', alpha=0.3, linestyle='--')
for i, (bar, mean) in enumerate(zip(bars, means)):
    ax.text(mean + 0.15, i, f'{mean:.2f}', va='center', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('2_category_avg.png', dpi=300, bbox_inches='tight')
plt.close()

# 2. 総合評価の分布
print('2/6 総合評価の分布')
fig, ax = plt.subplots(figsize=(10, 6))
rating_counts = df['総合評価'].value_counts().sort_index()
bars = ax.bar(range(len(rating_counts)), rating_counts.values, color='steelblue', edgecolor='black', alpha=0.8)
ax.set_xticks(range(len(rating_counts)))
ax.set_xticklabels([f'{x:.1f}' for x in rating_counts.index], rotation=45)
ax.set_title('総合評価の分布', fontproperties=font_prop, fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('評価スコア', fontproperties=font_prop, fontsize=12)
ax.set_ylabel('レビュー数', fontproperties=font_prop, fontsize=12)
ax.grid(axis='y', alpha=0.3)
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}', ha='center', va='bottom', fontsize=9)
plt.tight_layout()
plt.savefig('1_overall_rating.png', dpi=300, bbox_inches='tight')
plt.close()

# 3. 箱ひげ図
print('3/6 カテゴリ別評価分布（箱ひげ図）')
fig, ax = plt.subplots(figsize=(12, 6))
bp = df[cats].boxplot(ax=ax, patch_artist=True, return_type='dict')
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.6)
ax.set_title('カテゴリ別評価分布', fontproperties=font_prop, fontsize=16, fontweight='bold', pad=20)
ax.set_ylabel('評価スコア', fontproperties=font_prop, fontsize=12)
ax.set_xticklabels(cats, fontproperties=font_prop, rotation=45, ha='right')
ax.set_ylim([0, 5.5])
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('3_boxplot.png', dpi=300, bbox_inches='tight')
plt.close()

# 4. 月別レビュー数の推移
print('4/6 月別レビュー数の推移')
monthly_counts = df['year_month'].value_counts().sort_index()
fig, ax = plt.subplots(figsize=(14, 6))
x_pos = range(len(monthly_counts))
ax.plot(x_pos, monthly_counts.values, marker='o', linewidth=2.5, markersize=8,
        color='steelblue', markerfacecolor='lightblue', markeredgewidth=2, markeredgecolor='steelblue')
ax.fill_between(x_pos, monthly_counts.values, alpha=0.3, color='steelblue')
ax.set_xticks(x_pos[::3])
ax.set_xticklabels([str(monthly_counts.index[i]) for i in range(0, len(monthly_counts), 3)], rotation=45, ha='right')
ax.set_title('月別レビュー数の推移', fontproperties=font_prop, fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('年月', fontproperties=font_prop, fontsize=12)
ax.set_ylabel('レビュー数', fontproperties=font_prop, fontsize=12)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('4_monthly_trend.png', dpi=300, bbox_inches='tight')
plt.close()

# 5. 月別平均評価の推移
print('5/6 月別平均評価の推移')
monthly_avg = df.groupby('year_month')['総合評価'].mean()
monthly_std = df.groupby('year_month')['総合評価'].std().fillna(0)
fig, ax = plt.subplots(figsize=(14, 6))
x_pos = range(len(monthly_avg))
ax.errorbar(x_pos, monthly_avg.values, yerr=monthly_std.values,
            marker='s', linewidth=2.5, markersize=8, capsize=5, capthick=2,
            color='green', markerfacecolor='lightgreen', markeredgewidth=2,
            markeredgecolor='green', ecolor='gray', alpha=0.7)
avg_line = monthly_avg.mean()
ax.axhline(y=avg_line, color='red', linestyle='--', linewidth=2, alpha=0.7, label=f'全期間平均: {avg_line:.2f}')
if len(monthly_avg) >= 3:
    from pandas import Series
    ma = Series(monthly_avg.values).rolling(window=3, center=True).mean()
    ax.plot(x_pos, ma, color='orange', linestyle=':', linewidth=2.5, alpha=0.8, label='3ヶ月移動平均')
ax.set_xticks(x_pos[::3])
ax.set_xticklabels([str(monthly_avg.index[i]) for i in range(0, len(monthly_avg), 3)], rotation=45, ha='right')
ax.set_title('月別平均評価の推移（エラーバー: 標準偏差）', fontproperties=font_prop, fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('年月', fontproperties=font_prop, fontsize=12)
ax.set_ylabel('平均評価スコア', fontproperties=font_prop, fontsize=12)
ax.set_ylim([2.5, 5.5])
ax.grid(True, alpha=0.3)
ax.legend(loc='best', fontsize=10, prop=font_prop)
plt.tight_layout()
plt.savefig('4_monthly_avg_rating.png', dpi=300, bbox_inches='tight')
plt.close()

# 6. いいね数分析
print('6/6 いいね数分析')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
ax1.hist(df['いいね数'], bins=15, edgecolor='black', color='lightgreen', alpha=0.7)
ax1.axvline(df['いいね数'].mean(), color='red', linestyle='--', linewidth=2, label=f'平均: {df["いいね数"].mean():.1f}')
ax1.axvline(df['いいね数'].median(), color='blue', linestyle='--', linewidth=2, label=f'中央値: {df["いいね数"].median():.0f}')
ax1.set_title('いいね数の分布', fontproperties=font_prop, fontsize=14, fontweight='bold')
ax1.set_xlabel('いいね数', fontproperties=font_prop, fontsize=11)
ax1.set_ylabel('レビュー数', fontproperties=font_prop, fontsize=11)
ax1.legend(prop=font_prop)
ax1.grid(axis='y', alpha=0.3)
scatter = ax2.scatter(df['総合評価'], df['いいね数'], alpha=0.6, s=100,
                      c=df['総合評価'], cmap='RdYlGn', edgecolors='black', linewidths=1.5)
ax2.set_title('総合評価 vs いいね数', fontproperties=font_prop, fontsize=14, fontweight='bold')
ax2.set_xlabel('総合評価', fontproperties=font_prop, fontsize=11)
ax2.set_ylabel('いいね数', fontproperties=font_prop, fontsize=11)
ax2.grid(True, alpha=0.3)
cbar = plt.colorbar(scatter, ax=ax2)
cbar.set_label('評価スコア', fontproperties=font_prop)
plt.tight_layout()
plt.savefig('5_likes_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

print('\n完了！全てのグラフをFontProperties対応で再生成しました')
print(f'使用フォント: {selected_font} ({font_path})')
