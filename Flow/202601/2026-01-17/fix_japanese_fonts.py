import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import matplotlib.font_manager as fm
from matplotlib.font_manager import FontProperties
import sys
import os
import warnings
warnings.filterwarnings('ignore')

sys.stdout.reconfigure(encoding='utf-8')

print('=' * 80)
print('日本語フォント問題の修正')
print('=' * 80)

# Step 1: フォントキャッシュを強制的にクリア
print('\nStep 1: フォントキャッシュのクリア...')
try:
    cache_dir = matplotlib.get_cachedir()
    cache_file = os.path.join(cache_dir, 'fontlist-v330.json')
    if os.path.exists(cache_file):
        os.remove(cache_file)
        print(f'  キャッシュファイルを削除: {cache_file}')
    fm._load_fontmanager(try_read_cache=False)
    print('  フォントマネージャーを再読み込み')
except Exception as e:
    print(f'  警告: {e}')

# Step 2: 利用可能なフォントを詳細に調査
print('\nStep 2: 日本語フォントの検索...')
jp_fonts = []
for font in fm.fontManager.ttflist:
    font_name = font.name
    font_fname = font.fname
    
    # 日本語フォントの候補をチェック
    if any(keyword in font_name for keyword in ['Gothic', 'Mincho', 'Meiryo', 'Yu', 'MS', 'BIZ', 'Noto']):
        jp_fonts.append((font_name, font_fname))
        print(f'  見つかったフォント: {font_name}')
        if len(jp_fonts) >= 5:
            break

if not jp_fonts:
    print('  エラー: 日本語フォントが見つかりません')
    sys.exit(1)

# 最初に見つかったフォントを使用
font_name, font_path = jp_fonts[0]
print(f'\n使用するフォント: {font_name}')
print(f'フォントパス: {font_path}')

# Step 3: FontPropertiesオブジェクトを作成
font_prop = FontProperties(fname=font_path)
print(f'FontPropertiesを作成: {font_prop.get_name()}')

# Step 4: matplotlib設定
plt.rcParams['axes.unicode_minus'] = False

# データ読み込み
print('\nデータ読み込み中...')
df = pd.read_csv('reviews_output.csv', encoding='utf-8-sig')
df['投稿日_parsed'] = pd.to_datetime(df['投稿日'], errors='coerce')
df['year_month'] = df['投稿日_parsed'].dt.to_period('M')

cats = ['料理・味', 'サービス', '雰囲気', 'CP', '酒・ドリンク']
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']

print('\nグラフ生成開始（FontPropertiesを明示的に使用）...')

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
    ax.text(mean + 0.15, i, f'{mean:.2f}', va='center', fontsize=11, fontweight='bold', fontproperties=font_prop)
plt.tight_layout()
plt.savefig('category_avg.png', dpi=300, bbox_inches='tight')
plt.close()

# 2. 総合評価の分布
print('2/6 総合評価の分布')
fig, ax = plt.subplots(figsize=(10, 6))
rating_counts = df['総合評価'].value_counts().sort_index()
bars = ax.bar(range(len(rating_counts)), rating_counts.values, color='steelblue', edgecolor='black', alpha=0.8)
ax.set_xticks(range(len(rating_counts)))
ax.set_xticklabels([f'{x:.1f}' for x in rating_counts.index], rotation=45, fontproperties=font_prop)
ax.set_title('総合評価の分布', fontproperties=font_prop, fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('評価スコア', fontproperties=font_prop, fontsize=12)
ax.set_ylabel('レビュー数', fontproperties=font_prop, fontsize=12)
ax.grid(axis='y', alpha=0.3)
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}', ha='center', va='bottom', fontsize=9)
plt.tight_layout()
plt.savefig('overall_rating.png', dpi=300, bbox_inches='tight')
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
plt.savefig('boxplot.png', dpi=300, bbox_inches='tight')
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
plt.savefig('monthly_trend.png', dpi=300, bbox_inches='tight')
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
leg = ax.legend(loc='best', fontsize=10, prop=font_prop)
plt.tight_layout()
plt.savefig('monthly_avg_rating.png', dpi=300, bbox_inches='tight')
plt.close()

# 6. いいね数分析
print('6/6 いいね数分析')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
ax1.hist(df['いいね数'], bins=15, edgecolor='black', color='lightgreen', alpha=0.7)
ax1.axvline(df['いいね数'].mean(), color='red', linestyle='--', linewidth=2, label=f'平均: {df["いいね数"].mean():.1f}')
ax1.axvline(df[
