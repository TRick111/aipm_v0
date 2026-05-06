# BL-0079 — Phase 2 (2/N) フォームハンドラ実装 (GAS Webhook 案 5)

**作業日**: 2026-05-06
**作業者**: AI (mt cockpit-task ab2f1e5a)
**実行根拠**: 田中さん指示 (5/6 案 5 = GAS + メール通知 を採用)
**設定値**:
- 通知先: `info@core-driven.com`
- 反映先: https://docs.google.com/spreadsheets/d/1ED_UKHB3QatCcRVj0aEyPzAgt6RPJrfdJ7HtbLKRzQs/edit?gid=0#gid=0

---

## 0. アーキテクチャ

```
[訪問者ブラウザ]
   │  ① /contact-new/ ページのフォームに入力
   │  ② 送信ボタンクリック
   ↓
[フォーム JavaScript]
   │  ③ FormData を URLSearchParams に変換
   │  ④ fetch(GAS_URL, {method:'POST', body:params})
   ↓
[Google Apps Script Web App]
   │  ⑤ doPost(e) で受け取り
   │  ⑥ Google Sheets (1ED_UKH...) に行追加
   │  ⑦ MailApp.sendEmail で info@core-driven.com に通知
   │  ⑧ {ok:true} を JSON レスポンス
   ↓
[フォーム JavaScript]
   │  ⑨ 「送信完了しました」メッセージ表示
```

---

## 1. 田中さんの作業 (1 回だけ・10 分)

### Step 1.1 GAS プロジェクト作成

1. https://script.google.com/ を開く (Google アカウントでログイン)
2. **「新しいプロジェクト」** をクリック
3. 左上のプロジェクト名 (デフォルト「無題のプロジェクト」) をクリック → **「CoreDriven Contact Handler」** に変更

### Step 1.2 スクリプト貼り付け

1. デフォルトの `Code.gs` を開く
2. 既存のコード (`function myFunction() {}`) を **すべて削除**
3. ローカルの **`gas_contact_handler.js`** (このフォルダにある) の中身を全部コピー
4. Code.gs に貼り付け
5. 上部の **保存ボタン (フロッピーアイコン) または `Cmd+S`** で保存

### Step 1.3 (任意) 動作テスト

1. 上部の関数選択ドロップダウンで **`testHandler`** を選択
2. **「実行」** ボタンをクリック
3. 初回は Google アカウントの認可ダイアログが出る → 「権限を確認」→ 自分のアカウント選択 → 「詳細」→「(プロジェクト名) (安全ではないページ) に移動」→「許可」
4. 実行ログに `{"ok":true,"ts":"2026-05-06 ..."}` が出れば成功
5. Google Sheets を開いて、「テスト株式会社 / テスト 太郎」の行が追加されているか確認
6. info@core-driven.com にテストメールが届いているか確認

→ 確認できたらテスト行を Sheets から削除して OK

### Step 1.4 Web アプリとしてデプロイ

1. 右上の **「デプロイ」 → 「新しいデプロイ」**
2. 歯車アイコン (種類の選択) → **「ウェブアプリ」**
3. 設定:
   - 説明: `CoreDriven Contact v1`
   - 次のユーザーとして実行: **自分** (田中さんのアカウント)
   - アクセスできるユーザー: **★ 全員** (重要 — 「全員」を選ばないと外部ブラウザから POST できません)
4. 「デプロイ」をクリック
5. 「アクセスを承認」→ 認可 (Step 1.3 で済ませている場合は省略)
6. 表示される **「ウェブアプリ URL」** (`https://script.google.com/macros/s/AKfyc.../exec`) を **コピー**
7. **完了** をクリック

### Step 1.5 URL を AI に共有

コピーした `https://script.google.com/macros/s/AKfyc.../exec` をチャットで AI に伝える。

---

## 2. AI の作業 (URL 受領後・5 分)

田中さんから GAS Web App URL を受け取り次第:

### Step 2.1 /contact-new/ ページのフォームに JavaScript 追加

`coredriven_contact-new_paste_ready.html` の `</form>` の直後に以下を挿入:

```html
<script>
(function() {
  const GAS_URL = '<<田中さんから受領した URL>>';
  const form = document.getElementById('contactForm');
  if (!form) return;

  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    if (!form.checkValidity()) { form.reportValidity(); return; }

    const submitBtn = form.querySelector('[type="submit"]');
    const originalText = submitBtn ? submitBtn.textContent : '';
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = '送信中...';
    }

    try {
      const formData = new FormData(form);
      formData.append('ua', navigator.userAgent);
      const params = new URLSearchParams(formData);

      const res = await fetch(GAS_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: params,
      });
      const data = await res.json();

      if (data && data.ok) {
        form.outerHTML = '<div class="form-card thank-you" style="text-align:center;padding:80px 32px"><h3 style="font-size:24px;margin-bottom:16px;color:var(--ink-900)">送信完了しました</h3><p style="color:var(--ink-500);font-size:15px;line-height:1.8">担当者より 1〜3 営業日以内にご連絡いたします。<br>お問い合わせありがとうございました。</p></div>';
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        throw new Error(data && data.error || 'unknown error');
      }
    } catch (err) {
      console.error('[Contact] submit failed:', err);
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
      }
      alert('送信に失敗しました。お手数ですが時間をおいて再度お試しいただくか、info@core-driven.com まで直接ご連絡ください。');
    }
  });
})();
</script>
```

### Step 2.2 wp post update で /contact-new/ 反映

```bash
scp -P 10022 coredriven_contact-new_paste_ready_v3.html xserver:/tmp/
ssh xserver 'wp post update 708 --post_content="$(cat /tmp/coredriven_contact-new_paste_ready_v3.html)"'
```

### Step 2.3 Playwright でテスト送信

ブラウザで `/contact-new/` → ダミーデータ入力 → 送信 → 「送信完了しました」確認 → Sheets に行追加されているか確認 → メール届いているか確認。

---

## 3. ハマりポイント / トラブルシュート

| 症状 | 原因 | 対処 |
|---|---|---|
| 送信時に `Failed to fetch` | GAS の deploy で「全員」を選ばなかった | デプロイ設定で「アクセスできるユーザー」を「全員」に修正 |
| 送信時に CORS エラー | `Content-Type: application/json` で送信した (preflight 必要) | `Content-Type: application/x-www-form-urlencoded` で送信 |
| Sheets に書き込まれない | SHEET_ID が間違っている / 権限がない | GAS の SHEET_ID を確認 / 田中さんの GAS と Sheets が同じアカウント |
| メールが届かない | GAS のメール送信枠超過 (無料 100通/日) / NOTIFY_EMAIL 誤り | Apps Script ダッシュボードで割当残数確認 |
| 「権限を確認」が永遠に出る | 認可未完了 | testHandler を一度実行 → 認可フロー完了 |
| 受信メールが英語で文字化け | 通常起きないが、Gmail 側の表示問題 | メーラーの文字コード設定確認 |

---

## 4. セキュリティ / 運用考慮事項

### 4.1 Bot 対策 (今回はあえて未実装)
- 現状: reCAPTCHA / honeypot 等なし → スパム送信される可能性
- 対策案 (将来):
  - **honeypot**: hidden input を 1 個追加 → 値が入っていたら無視 (Bot 排除に効果大)
  - **reCAPTCHA v3**: スコアで判定、UI 不要
  - **rate limit**: GAS 内で IP/メール単位の制限
  - **Cloudflare Turnstile**: 無料、UX 良し

### 4.2 機密情報
- GAS Web App URL は誰でも叩ける → URL 自体は機密性が低いものとして扱う (URL を知っていれば誰でも送信可)
- ただし 1 件の送信で 1 行追加 + 1 メール送信なので大量に来ても影響は限定的
- 心配なら honeypot / Turnstile を追加 (Phase 2 後半で検討)

### 4.3 GAS の制限
- メール送信: 100通/日 (Gmail 無料アカウント)、1500通/日 (Workspace アカウント)
- 実行時間: 6 分/回 (今回の処理は 1 秒以内)
- データ保管: Sheets の制限 (1000万セルまで) → 実用上気にしなくて OK

### 4.4 監査
- Sheets に履歴が残るので「いつ誰から来たか」全件追跡可能
- GAS の実行ログ (Apps Script ダッシュボード → 実行) で過去の動作確認

---

## 5. 完了基準

- [ ] GAS スクリプト作成 + 「全員」公開デプロイ済 (田中さんの作業)
- [ ] AI に Web App URL 共有済 (田中さんの作業)
- [ ] /contact-new/ の form に JS 注入済 (AI の作業)
- [ ] Playwright でテスト送信成功 (AI の作業)
- [ ] Sheets に行追加確認 (Playwright + 田中さん視覚確認)
- [ ] info@core-driven.com にメール受信確認 (田中さん)

---

## 6. 関連ファイル

- `gas_contact_handler.js` ← Code.gs に貼るスクリプト本体
- `coredriven_contact-new_paste_ready.html` ← 現状の /contact-new/ ページ HTML (今後 v3 に更新予定)
- 既存 `/contact/` (id=55, draft) は当面残置 (Phase 2 後半で削除判断)

---

**END OF SETUP GUIDE.** 田中さんが Step 1 (GAS デプロイ) → URL 共有 → AI が Step 2 を 5 分で完了。
