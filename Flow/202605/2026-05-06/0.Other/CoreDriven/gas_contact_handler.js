/**
 * CoreDriven Contact Form Handler (Google Apps Script Web App)
 *
 * 役割:
 *   - core-driven.com/contact-new/ のフォームから POST 送信を受け取る
 *   - Google Sheets に行追加
 *   - info@core-driven.com にメール通知
 *
 * デプロイ手順:
 *   1. https://script.google.com/ で新規プロジェクト作成
 *   2. プロジェクト名: "CoreDriven Contact Handler"
 *   3. Code.gs にこのファイルの中身を全部貼り付け (デフォルトのコードは削除)
 *   4. 上部の「保存」(Cmd+S) でファイル保存
 *   5. 右上の「デプロイ」→「新しいデプロイ」
 *   6. 種類: ウェブアプリ
 *      - 説明: "CoreDriven Contact v1"
 *      - 次のユーザーとして実行: 自分
 *      - アクセスできるユーザー: ★ 全員 (※ 重要 — 「全員」を選ばないと外部から POST 不可)
 *   7. 「デプロイ」→ 「アクセスを承認」→ Google アカウントで認可 (初回のみ)
 *   8. 表示される「ウェブアプリ URL」 (https://script.google.com/macros/s/AKfyc.../exec) をコピー
 *   9. その URL を AI に伝える → AI が AI HTML フォームの action を更新
 *
 * 設定値: 修正不要 (この値で動きます)
 */

const SHEET_ID = '1ED_UKHB3QatCcRVj0aEyPzAgt6RPJrfdJ7HtbLKRzQs';
const SHEET_GID = 0;
const NOTIFY_EMAIL = 'info@core-driven.com';

// 相談領域コードを日本語に
const AREA_LABEL = {
  'biz': 'Biz Core (人による経営伴走)',
  'ai': 'AI Core (AIによる経営伴走)',
  'unknown': 'どちらか分からない',
};

/**
 * POST: フォーム送信を受け付ける
 */
function doPost(e) {
  try {
    const payload = (e && e.parameter) || {};
    const ts = new Date();
    const tsStr = Utilities.formatDate(ts, 'Asia/Tokyo', 'yyyy-MM-dd HH:mm:ss');

    // 1. Google Sheets に書き込み
    const ss = SpreadsheetApp.openById(SHEET_ID);
    const sheets = ss.getSheets();
    const sheet = sheets.filter(s => s.getSheetId() === SHEET_GID)[0] || sheets[0];

    // 1 行目に何もなければヘッダー行を作成
    if (sheet.getLastRow() === 0) {
      const headers = ['送信日時', '相談領域', '会社名', '役職', '氏名', 'メール', '電話番号', '希望打ち合わせ時間', '現在の課題', '実現したいこと', 'User-Agent'];
      sheet.appendRow(headers);
      sheet.getRange(1, 1, 1, headers.length)
        .setBackground('#0B1530')
        .setFontColor('#FFFFFF')
        .setFontWeight('bold');
      sheet.setFrozenRows(1);
      // 列幅を調整
      sheet.setColumnWidth(1, 150); // 日時
      sheet.setColumnWidth(2, 220); // 相談領域
      sheet.setColumnWidth(3, 180); // 会社名
      sheet.setColumnWidth(4, 120); // 役職
      sheet.setColumnWidth(5, 120); // 氏名
      sheet.setColumnWidth(6, 200); // メール
      sheet.setColumnWidth(7, 130); // 電話
      sheet.setColumnWidth(8, 180); // 希望時間
      sheet.setColumnWidth(9, 400); // 現在の課題
      sheet.setColumnWidth(10, 400); // 実現したいこと
      sheet.setColumnWidth(11, 200); // UA
    }

    sheet.appendRow([
      tsStr,
      AREA_LABEL[payload.area] || payload.area || '',
      payload.company || '',
      payload.position || '',
      payload.name || '',
      payload.email || '',
      payload.tel || '',
      payload.schedule || '',
      payload.issue || '',
      payload.goal || '',
      payload.ua || '',
    ]);

    // 2. メール通知
    const subject = `[CoreDriven Contact] ${payload.company || '(会社名なし)'} ${payload.name || '(氏名なし)'} 様より新規問い合わせ`;
    const body = [
      `Core Driven のお問い合わせフォームに新規送信がありました。`,
      ``,
      `■ 送信日時: ${tsStr} (JST)`,
      ``,
      `■ 相談領域: ${AREA_LABEL[payload.area] || payload.area || '-'}`,
      `■ 会社名: ${payload.company || '-'}`,
      `■ 役職: ${payload.position || '-'}`,
      `■ 氏名: ${payload.name || '-'}`,
      `■ メール: ${payload.email || '-'}`,
      `■ 電話: ${payload.tel || '-'}`,
      `■ 希望打ち合わせ時間: ${payload.schedule || '-'}`,
      ``,
      `■ 現在の課題:`,
      `${payload.issue || '-'}`,
      ``,
      `■ 実現したいこと:`,
      `${payload.goal || '-'}`,
      ``,
      `--`,
      `送信元: https://core-driven.com/contact-new/`,
      `スプレッドシート: https://docs.google.com/spreadsheets/d/${SHEET_ID}/edit#gid=${SHEET_GID}`,
      `User-Agent: ${payload.ua || '-'}`,
    ].join('\n');

    const mailOpts = {
      to: NOTIFY_EMAIL,
      subject: subject,
      body: body,
      name: 'CoreDriven Contact',
    };
    if (payload.email && /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(payload.email)) {
      mailOpts.replyTo = payload.email;
    }
    MailApp.sendEmail(mailOpts);

    return ContentService
      .createTextOutput(JSON.stringify({ ok: true, ts: tsStr }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    console.error(err);
    // エラーでも、Sheets/メール失敗を分かるように管理者に通知
    try {
      MailApp.sendEmail({
        to: NOTIFY_EMAIL,
        subject: '[CoreDriven Contact] ⚠️ ハンドラエラー',
        body: 'GAS スクリプトでエラーが発生しました:\n\n' + String(err) + '\n\n送信内容: ' + JSON.stringify(e && e.parameter, null, 2),
      });
    } catch (e2) {}
    return ContentService
      .createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * GET: 動作確認用
 *   https://script.google.com/macros/s/AKfyc.../exec
 *   をブラウザで開くと {"ok":true,"message":"..."} が出れば OK
 */
function doGet(e) {
  return ContentService
    .createTextOutput(JSON.stringify({
      ok: true,
      message: 'CoreDriven Contact GAS Webhook is alive',
      timestamp: new Date().toISOString(),
    }))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * (開発用) 手動テスト
 *   GAS エディタの「実行」で testHandler() を選んで実行すると
 *   ダミーデータで Sheets / メール送信のテストができる
 */
function testHandler() {
  const fakeEvent = {
    parameter: {
      area: 'biz',
      company: 'テスト株式会社',
      position: '代表取締役',
      name: 'テスト 太郎',
      email: 'test@example.com',
      tel: '090-1234-5678',
      schedule: '平日午前',
      issue: 'これはテストです。本番では送信されません。',
      goal: '動作確認です。',
      ua: 'Manual Test',
    },
  };
  const result = doPost(fakeEvent);
  Logger.log(result.getContent());
}
