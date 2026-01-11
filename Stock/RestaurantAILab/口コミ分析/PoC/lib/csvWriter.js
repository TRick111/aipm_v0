import fs from 'fs';
import path from 'path';

/**
 * CSV出力ユーティリティ
 */
export class CsvWriter {
  /**
   * レビューデータをCSVファイルに出力
   * @param {Array} reviews - レビューデータの配列
   * @param {string} placeId - 店舗のplace_id
   * @param {string} outputPath - 出力先ファイルパス
   */
  static async writeReviews(reviews, placeId, outputPath) {
    const fetchedAt = new Date().toISOString();

    // CSVヘッダー
    const headers = [
      'place_id',
      'fetched_at',
      'review_time',
      'review_time_unix',
      'language',
      'rating',
      'text',
      'author_name',
      'author_total_reviews',
      'author_local_guide_level',
      'author_photo_url'
    ];

    // CSV行を生成
    const rows = reviews.map(review => {
      const reviewTime = review.time ? new Date(review.time * 1000).toISOString() : '';

      return [
        this.escapeCsvField(placeId),
        this.escapeCsvField(fetchedAt),
        this.escapeCsvField(reviewTime),
        review.time || '',
        this.escapeCsvField(review.language || ''),
        review.rating || '',
        this.escapeCsvField(review.text || ''),
        this.escapeCsvField(review.author_name || ''),
        review.author_total_reviews || '',
        review.author_local_guide_level || '',
        this.escapeCsvField(review.profile_photo_url || '')
      ].join(',');
    });

    // CSV内容を作成
    const csvContent = [
      headers.join(','),
      ...rows
    ].join('\n');

    // ファイルに書き込み
    try {
      // 出力ディレクトリが存在しない場合は作成
      const dir = path.dirname(outputPath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }

      // UTF-8 BOM付きで書き込み（Excelでの文字化け対策）
      const bom = '\uFEFF';
      fs.writeFileSync(outputPath, bom + csvContent, 'utf8');

      console.log(`[CSV] ${reviews.length}件のレビューを出力しました: ${outputPath}`);
    } catch (error) {
      throw new Error(`CSV書き込みエラー: ${error.message}`);
    }
  }

  /**
   * CSVフィールドをエスケープ
   * @param {string} field - フィールド値
   * @returns {string} - エスケープされた値
   */
  static escapeCsvField(field) {
    if (field == null) {
      return '';
    }

    const str = String(field);

    // カンマ、改行、ダブルクォートが含まれる場合はダブルクォートで囲む
    if (str.includes(',') || str.includes('\n') || str.includes('\r') || str.includes('"')) {
      // ダブルクォートは2つ重ねてエスケープ
      return `"${str.replace(/"/g, '""')}"`;
    }

    return str;
  }

  /**
   * デフォルトの出力ファイル名を生成
   * @param {string} placeId - 店舗のplace_id
   * @returns {string} - ファイル名
   */
  static generateDefaultFilename(placeId) {
    const now = new Date();
    const timestamp = now.toISOString()
      .replace(/[-:]/g, '')
      .replace(/\..+/, '')
      .replace('T', '_');

    return `reviews_${placeId}_${timestamp}.csv`;
  }
}
