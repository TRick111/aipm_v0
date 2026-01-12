"""
食べログ口コミHTMLをCSVに変換するスクリプト
"""
from bs4 import BeautifulSoup
import csv
import re
from pathlib import Path

def clean_text(text):
    """テキストをクリーンアップ"""
    if text is None:
        return ""
    # 改行をスペースに変換し、余分な空白を削除
    text = re.sub(r'\s+', ' ', text.strip())
    return text

def extract_reviewer_name(review):
    """投稿者名を抽出"""
    reviewer_name_elem = review.select_one('p.reviewer-name a span')
    if reviewer_name_elem:
        # 口コミ数のspanを除外
        name = reviewer_name_elem.get_text(strip=True)
        # 口コミ数（例: （395））を除去
        name = re.sub(r'\s*（\d+）$', '', name)
        return name
    return ""

def extract_date(review):
    """投稿日を抽出"""
    entry_date = review.select_one('p.entry-date > span.date')
    if entry_date:
        return entry_date.get_text(strip=True)
    return ""

def extract_visit_date(review):
    """訪問日を抽出"""
    visit = review.select_one('span.visit span.date')
    if visit:
        return visit.get_text(strip=True)
    return ""

def extract_total_score(review):
    """総合点数を抽出"""
    score_elem = review.select_one('b.c-rating-v2__val--strong')
    if score_elem:
        return score_elem.get_text(strip=True)
    return ""

def extract_detail_ratings(review):
    """詳細評価を抽出（料理・味、サービス、雰囲気、CP、酒・ドリンク）"""
    ratings = {}
    ratings_list = review.select('ul.ratings li.rate')
    
    for li in ratings_list:
        item_elem = li.select_one('span.item')
        score_elem = li.select_one('strong')
        if item_elem and score_elem:
            item_name = item_elem.get_text(strip=True)
            score = score_elem.get_text(strip=True)
            # "－"や"-"は空文字に変換
            if score in ['－', '-']:
                score = ''
            ratings[item_name] = score
    
    return ratings

def extract_prices(review):
    """使った金額を抽出"""
    prices = {
        '夜': '',
        '昼': '',
        'テイクアウト': '',
        'デリバリー': '',
        'その他': ''
    }
    
    prices_list = review.select('ul.prices li.rate')
    for li in prices_list:
        text = li.get_text()
        strong_elem = li.select_one('strong')
        if strong_elem:
            price = strong_elem.get_text(strip=True)
            # "－"は空文字に変換
            if price == '－':
                price = ''
            
            if '（夜）' in text:
                prices['夜'] = price
            elif '（昼）' in text:
                prices['昼'] = price
            elif '（テイクアウト）' in text:
                prices['テイクアウト'] = price
            elif '（デリバリー）' in text:
                prices['デリバリー'] = price
            elif '（その他）' in text:
                prices['その他'] = price
    
    return prices

def extract_comment(review):
    """口コミ内容を抽出"""
    comment_div = review.select_one('div.comment p')
    if comment_div:
        # <br>タグを改行に変換してからテキスト取得
        for br in comment_div.find_all('br'):
            br.replace_with('\n')
        text = comment_div.get_text()
        # 改行は残しつつ、前後の空白を削除
        return text.strip()
    return ""

def extract_review_title(review):
    """口コミタイトルを抽出"""
    title_elem = review.select_one('p.title a')
    if title_elem:
        return title_elem.get_text(strip=True)
    return ""

def extract_review_type(review):
    """口コミタイプ（夜/昼）を抽出"""
    type_img = review.select_one('span.type img')
    if type_img:
        alt = type_img.get('alt', '')
        if '夜' in alt:
            return '夜'
        elif '昼' in alt:
            return '昼'
    return ""

def extract_likes(review):
    """いいね数を抽出"""
    footer_likes = review.select_one('div.review-footer .like-count__count')
    if footer_likes:
        return footer_likes.get_text(strip=True)
    return "0"

def parse_reviews_html(html_path, output_path):
    """HTMLファイルをパースしてCSVに出力"""
    
    # HTMLファイル読み込み
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 全ての口コミを取得
    reviews = soup.select('div.review-wrap')
    print(f"口コミ数: {len(reviews)}件")
    
    # CSVヘッダー
    headers = [
        '投稿者',
        '口コミタイトル',
        '口コミ内容',
        '総合点数',
        '投稿日',
        '訪問日',
        '口コミタイプ',
        '使った金額_夜',
        '使った金額_昼',
        '使った金額_テイクアウト',
        '使った金額_デリバリー',
        '使った金額_その他',
        '料理・味',
        'サービス',
        '雰囲気',
        'CP',
        '酒・ドリンク',
        'いいね数'
    ]
    
    # CSVに書き出し
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for i, review in enumerate(reviews, 1):
            try:
                reviewer_name = extract_reviewer_name(review)
                title = extract_review_title(review)
                comment = extract_comment(review)
                total_score = extract_total_score(review)
                post_date = extract_date(review)
                visit_date = extract_visit_date(review)
                review_type = extract_review_type(review)
                prices = extract_prices(review)
                detail_ratings = extract_detail_ratings(review)
                likes = extract_likes(review)
                
                row = [
                    reviewer_name,
                    title,
                    comment,
                    total_score,
                    post_date,
                    visit_date,
                    review_type,
                    prices['夜'],
                    prices['昼'],
                    prices['テイクアウト'],
                    prices['デリバリー'],
                    prices['その他'],
                    detail_ratings.get('料理・味', ''),
                    detail_ratings.get('サービス', ''),
                    detail_ratings.get('雰囲気', ''),
                    detail_ratings.get('CP', ''),
                    detail_ratings.get('酒・ドリンク', ''),
                    likes
                ]
                
                writer.writerow(row)
                
            except Exception as e:
                print(f"Error processing review {i}: {e}")
                continue
    
    print(f"CSVファイルを出力しました: {output_path}")

if __name__ == '__main__':
    # パス設定
    script_dir = Path(__file__).parent
    html_path = script_dir / 'reviews.html'
    output_path = script_dir / 'reviews.csv'
    
    parse_reviews_html(html_path, output_path)


