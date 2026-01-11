import { google } from 'googleapis';

/**
 * Google Business Profile (旧GMB) API クライアント
 */
export class GmbClient {
  constructor(authClient) {
    this.authClient = authClient;
    this.mybusinessbusinessinformation = google.mybusinessbusinessinformation({
      version: 'v1',
      auth: authClient,
    });
    this.mybusinessaccountmanagement = google.mybusinessaccountmanagement({
      version: 'v1',
      auth: authClient,
    });
  }

  /**
   * アカウント一覧を取得
   */
  async listAccounts() {
    try {
      console.log('[GMB API] アカウント一覧を取得中...');
      const response = await this.mybusinessaccountmanagement.accounts.list();
      return response.data.accounts || [];
    } catch (error) {
      throw new Error(`アカウント一覧の取得に失敗: ${error.message}`);
    }
  }

  /**
   * ロケーション（店舗）一覧を取得
   */
  async listLocations(accountName) {
    try {
      console.log(`[GMB API] ロケーション一覧を取得中... (account: ${accountName})`);
      const response = await this.mybusinessbusinessinformation.accounts.locations.list({
        parent: accountName,
        readMask: 'name,title,storefrontAddress',
      });
      return response.data.locations || [];
    } catch (error) {
      throw new Error(`ロケーション一覧の取得に失敗: ${error.message}`);
    }
  }

  /**
   * レビュー一覧を取得（Business Profile APIの新しいエンドポイント使用）
   */
  async listReviews(locationName, pageSize = 50) {
    try {
      console.log(`[GMB API] レビュー一覧を取得中... (location: ${locationName})`);

      const allReviews = [];
      let pageToken = null;

      // ページネーション対応
      do {
        const params = {
          parent: locationName,
          pageSize: pageSize,
        };

        if (pageToken) {
          params.pageToken = pageToken;
        }

        // My Business API v4 のレビューエンドポイントを使用
        const url = `https://mybusiness.googleapis.com/v4/${locationName}/reviews`;
        const response = await this.authClient.request({
          url: url,
          params: {
            pageSize: pageSize,
            pageToken: pageToken,
          },
        });

        const reviews = response.data.reviews || [];
        allReviews.push(...reviews);

        pageToken = response.data.nextPageToken;

        console.log(`[GMB API] ${reviews.length}件のレビューを取得しました (累計: ${allReviews.length}件)`);

        // 次のページがあればループ継続
      } while (pageToken);

      return allReviews;
    } catch (error) {
      // エラーの詳細を表示
      if (error.response) {
        console.error('[GMB API] APIエラーレスポンス:', error.response.data);
        throw new Error(
          `レビューの取得に失敗: ${error.response.status} - ${JSON.stringify(error.response.data)}`
        );
      }
      throw new Error(`レビューの取得に失敗: ${error.message}`);
    }
  }

  /**
   * アカウント名からロケーション名を検索
   */
  async findLocationByName(accountName, locationTitle) {
    const locations = await this.listLocations(accountName);

    const found = locations.find(loc =>
      loc.title && loc.title.toLowerCase().includes(locationTitle.toLowerCase())
    );

    if (!found) {
      console.log('\n利用可能なロケーション:');
      locations.forEach(loc => {
        console.log(`  - ${loc.title || '(タイトルなし)'} (${loc.name})`);
      });
      throw new Error(`ロケーション "${locationTitle}" が見つかりません`);
    }

    return found;
  }

  /**
   * レビューデータを標準フォーマットに変換
   */
  static normalizeReview(review) {
    return {
      review_id: review.reviewId || review.name || '',
      time: review.createTime ? Math.floor(new Date(review.createTime).getTime() / 1000) : null,
      rating: review.starRating === 'STAR_RATING_UNSPECIFIED' ? null : this.convertStarRating(review.starRating),
      text: review.comment || '',
      language: '', // GMB APIでは言語コードが直接提供されない
      author_name: review.reviewer?.displayName || '',
      author_total_reviews: null, // GMB APIでは提供されない
      author_local_guide_level: null, // GMB APIでは提供されない
      author_photo_url: review.reviewer?.profilePhotoUrl || '',
      reply_text: review.reviewReply?.comment || '',
      reply_time: review.reviewReply?.updateTime || '',
    };
  }

  /**
   * StarRating enumを数値に変換
   */
  static convertStarRating(starRating) {
    const mapping = {
      'ONE': 1,
      'TWO': 2,
      'THREE': 3,
      'FOUR': 4,
      'FIVE': 5,
    };
    return mapping[starRating] || null;
  }
}
