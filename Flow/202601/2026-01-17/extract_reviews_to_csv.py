"""
食べログの口コミ管理ページHTMLから口コミデータを抽出してCSVファイルに変換するスクリプト

機能:
- HTMLファイルから口コミ情報を抽出
- 口コミタイトル、投稿日、訪問日、レビュアー名、評価、金額、本文などを取得
- CSV形式で出力

使用方法:
    python extract_reviews_to_csv.py
"""

from bs4 import BeautifulSoup
import csv
import re
from pathlib import Path

def extract_text(element):
    """要素からテキストを安全に抽出"""
    return element.get_text(strip=True) if element else ""

def extract_rating(soup_element):
    """評価を抽出"""
    rating_elem = soup_element.find('b', class_='c-rating-v2__val--strong')
    return extract_text(rating_elem) if rating_elem else ""

def extract_detailed_ratings(soup_element):
    """詳細評価を抽出"""
    ratings = {}
    ratings_list = soup_element.find('ul', class_='ratings')
    if ratings_list:
        for li in ratings_list.find_all('li', class_='rate'):
            text = li.get_text(strip=True)
            # "料理・味4.5" のような形式から分割
            match = re.search(r'([^\d]+)([\d.]+)', text)
            if match:
                category = match.group(1).strip('［|]')
                value = match.group(2)
                ratings[category] = value
    return ratings

def extract_prices(soup_element):
    """使用金額を抽出"""
    prices = {}
    prices_list = soup_element.find('ul', class_='prices')
    if prices_list:
        for li in prices_list.find_all('li', class_='rate'):
            text = li.get_text(strip=True)
            if '（夜）' in text:
                prices['夜'] = re.search(r'（夜）\s*(.+)', text).group(1) if re.search(r'（夜）\s*(.+)', text) else ""
            elif '（昼）' in text:
                prices['昼'] = re.search(r'（昼）\s*(.+)', text).group(1) if re.search(r'（昼）\s*(.+)', text) else ""
    return prices

def parse_review_html(html_file):
    """HTMLファイルから口コミを抽出"""
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    reviews = []

    # 各口コミブロックを取得
    review_wraps = soup.find_all('div', class_='review-wrap')

    for review_wrap in review_wraps:
        review_data = {}

        # 口コミタイトル
        title_elem = review_wrap.find('p', class_='title')
        if title_elem:
            title_link = title_elem.find('a')
            review_data['タイトル'] = extract_text(title_link) if title_link else ""
        else:
            review_data['タイトル'] = ""

        # 投稿日と訪問日
        entry_date = review_wrap.find('p', class_='entry-date')
        if entry_date:
            date_span = entry_date.find('span', class_='date')
            review_data['投稿日'] = extract_text(date_span) if date_span else ""

            visit_span = entry_date.find('span', class_='visit')
            if visit_span:
                visit_date = visit_span.find('span', class_='date')
                review_data['訪問日'] = extract_text(visit_date) if visit_date else ""
            else:
                review_data['訪問日'] = ""
        else:
            review_data['投稿日'] = ""
            review_data['訪問日'] = ""

        # レビュアー名
        reviewer_name = review_wrap.find('p', class_='reviewer-name')
        if reviewer_name:
            reviewer_link = reviewer_name.find('a')
            if reviewer_link:
                # レビュアー名と投稿数を分離
                text = extract_text(reviewer_link)
                # "かなぞうグルメ（221）" -> "かなぞうグルメ"
                name_match = re.match(r'(.+?)\s*（\d+）', text)
                review_data['レビュアー名'] = name_match.group(1) if name_match else text
            else:
                review_data['レビュアー名'] = ""
        else:
            review_data['レビュアー名'] = ""

        # 総合評価
        review_data['総合評価'] = extract_rating(review_wrap)

        # 詳細評価
        detailed_ratings = extract_detailed_ratings(review_wrap)
        review_data['料理・味'] = detailed_ratings.get('料理・味', "")
        review_data['サービス'] = detailed_ratings.get('サービス', "")
        review_data['雰囲気'] = detailed_ratings.get('雰囲気', "")
        review_data['CP'] = detailed_ratings.get('CP', "")
        review_data['酒・ドリンク'] = detailed_ratings.get('酒・ドリンク', "")

        # 使用金額
        prices = extract_prices(review_wrap)
        review_data['金額_夜'] = prices.get('夜', "")
        review_data['金額_昼'] = prices.get('昼', "")

        # 口コミ本文
        comment_div = review_wrap.find('div', class_='comment')
        if comment_div:
            comment_p = comment_div.find('p')
            if comment_p:
                # <br>タグを改行に変換
                for br in comment_p.find_all('br'):
                    br.replace_with('\n')
                review_data['口コミ本文'] = comment_p.get_text(strip=True)
            else:
                review_data['口コミ本文'] = ""
        else:
            review_data['口コミ本文'] = ""

        # いいね数
        like_count = review_wrap.find('div', class_='review-footer')
        if like_count:
            count_span = like_count.find('span', class_='js-count')
            review_data['いいね数'] = extract_text(count_span) if count_span else ""
        else:
            review_data['いいね数'] = ""

        reviews.append(review_data)

    return reviews

def save_to_csv(reviews, output_file):
    """口コミデータをCSVファイルに保存"""
    if not reviews:
        print("抽出された口コミがありません。")
        return

    fieldnames = [
        'タイトル', '投稿日', '訪問日', 'レビュアー名', '総合評価',
        '料理・味', 'サービス', '雰囲気', 'CP', '酒・ドリンク',
        '金額_夜', '金額_昼', 'いいね数', '口コミ本文'
    ]

    with open(output_file, 'w', encoding='utf-8-sig', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(reviews)

    print(f"[OK] {len(reviews)}件の口コミを {output_file} に保存しました。")

def main():
    # 入力・出力ファイルのパス
    script_dir = Path(__file__).parent
    input_file = script_dir / 'review1.html'
    output_file = script_dir / 'reviews_output.csv'

    print(f"HTMLファイルを読み込み中: {input_file}")

    if not input_file.exists():
        print(f"エラー: {input_file} が見つかりません。")
        return

    # 口コミを抽出
    reviews = parse_review_html(input_file)

    # CSVに保存
    save_to_csv(reviews, output_file)

    print("\n処理完了！")

if __name__ == "__main__":
    main()
