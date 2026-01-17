import os

# ファイル名の変更マッピング
renames = {
    'overall_rating.png': '1_overall_rating.png',
    'category_avg.png': '2_category_avg.png',
    'boxplot.png': '3_boxplot.png',
    'monthly_trend.png': '4_monthly_trend.png',
    'monthly_avg_rating.png': '4_monthly_avg_rating.png',
    'likes_analysis.png': '5_likes_analysis.png'
}

for old_name, new_name in renames.items():
    if os.path.exists(old_name):
        os.rename(old_name, new_name)
        print(f'{old_name} -> {new_name}')
    else:
        print(f'{old_name} が見つかりません')

print('\n完了！')
