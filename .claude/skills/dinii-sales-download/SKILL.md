---
name: "Dinii注文一覧CSVダウンロード"
description: "Diniiから店舗の注文一覧データをCSV形式でダウンロードします。"
version: "2.0.0"
author: "Restaurant AI Lab"
created: "2026-01-05"
updated: "2026-02-09"
dependencies:
  - playwright-mcp
parameters:
  - name: startDate
    type: string
    required: true
    description: 集計開始日（YYYYMMDD形式）
    example: "20260101"
  - name: endDate
    type: string
    required: true
    description: 集計終了日（YYYYMMDD形式）
    example: "20260131"
  - name: email
    type: string
    required: true
    description: メールアドレス
    example: "example@email.com"
  - name: password
    type: string
    required: true
    description: パスワード
    sensitive: true
  - name: storeName
    type: string
    required: true
    description: 店舗名
    example: "昼からワイン食堂"
constants:
  loginUrl: "https://dashboard.self.dinii.jp/signIn"
  downloadPath: "/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/週報/0_downloads"
  fileNameFormat: "{startDate}-{endDate}-{storeName}.csv"
---

# Dinii注文一覧CSVダウンロード

## 概要

このSkillは、Playwright MCPを使用してDiniiにログインし、指定された店舗・期間の注文一覧CSVを自動的にダウンロードします。

**機能**:
- 単一店舗の注文データダウンロード
- ダウンロード後のファイルリネーム
- ログアウト処理

**出力先**: /Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/週報/0_downloads
**ファイル名形式**: `{開始日}-{終了日}-{店舗名}.csv`（例: `20260101-20260131-昼からワイン食堂.csv`）

---

## 必要なパラメータ

| パラメータ | 必須 | 説明 | 例 |
|-----------|-----|------|-----|
| `startDate` | ✅ | 集計開始日（YYYYMMDD形式） | `20260101` |
| `endDate` | ✅ | 集計終了日（YYYYMMDD形式） | `20260131` |
| `email` | ✅ | メールアドレス | `example@email.com` |
| `password` | ✅ | パスワード | `********` |
| `storeName` | ✅ | 店舗名 | `昼からワイン食堂` |

---

## 実行前の確認事項

このSkillを実行する前に、以下を確認してください：

- [ ] Playwright MCPが有効になっているか
- [ ] 対象期間（開始日・終了日）が指定されているか
- [ ] 認証情報が正しいか
- [ ] ダウンロード先ディレクトリが存在するか

---

## 実装手順

### 全体フロー

```
1. ログインページへ遷移
2. メールアドレス、パスワードを入力してログイン
3. 分析メニューを開く
4. CSVダウンロードを選択
5. 店舗選択（全選択解除 → 対象店舗を選択）
6. 期間を設定（開始日・終了日）
7. 注文一覧・取引一覧にチェック
8. ダウンロード
9. ファイルリネーム
10. ログアウト
11. 完了レポートを出力
```

---

## 各ステップの処理手順

### Step 1: ブラウザ起動とログインページへ遷移

```
ツール: mcp__playwright__browser_navigate
パラメータ:
  url: "https://dashboard.self.dinii.jp/signIn"
```

**期待される結果**: Diniiログインページが表示される

---

### Step 2: ページの状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

**目的**: ログインフォームが表示されていることを確認

---

### Step 3: ログイン情報を入力

#### 3-1. メールアドレスを入力

```
ツール: mcp__playwright__browser_fill_form
パラメータ:
  fields:
    - name: "メールアドレス"
      type: "textbox"
      ref: [snapshot から取得した入力欄の ref]
      value: {email}
```

#### 3-2. パスワードを入力

```
ツール: mcp__playwright__browser_fill_form
パラメータ:
  fields:
    - name: "パスワード"
      type: "textbox"
      ref: [snapshot から取得したパスワード欄の ref]
      value: {password}
```

**UI要素の特定方法**:
- プレースホルダー: `placeholder="メールアドレス"` または `input[type="email"]`
- プレースホルダー: `placeholder="パスワード"` または `input[type="password"]`

---

### Step 4: ログインボタンをクリック

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "ログインボタン"
  ref: [snapshot から取得したボタンの ref]
```

**UI要素の特定方法**:
- テキスト: `text="ログイン"` または `text="サインイン"` または `text="Sign In"`
- またはボタン: `button[type="submit"]`

**期待される結果**: ログインが成功し、ダッシュボードに遷移

---

### Step 5: ページ読み込みを待機

```
ツール: mcp__playwright__browser_wait_for
パラメータ:
  time: 3
```

---

### Step 6: 分析メニューを開く

#### 6-1. ページ状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

**目的**: 左側メニューの状態を確認

#### 6-2. 「分析」メニューをクリック（デフォルトで閉じているため必須）

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "分析メニュー"
  ref: [snapshot から取得したメニュー項目の ref]
```

**UI要素の特定方法**:
- テキスト: `text="分析"`

**期待される結果**: 分析メニューが展開され、サブメニューが表示される

---

### Step 7: CSVダウンロードを選択

#### 7-1. ページ状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

**目的**: CSVダウンロードメニューが表示されていることを確認

#### 7-2. 「CSVダウンロード」をクリック

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "CSVダウンロードメニュー"
  ref: [snapshot から取得したメニュー項目の ref]
```

**UI要素の特定方法**:
- テキスト: `text="CSVダウンロード"`

**期待される結果**: CSVダウンロードページが表示される

---

### Step 8: ページ読み込みを待機

```
ツール: mcp__playwright__browser_wait_for
パラメータ:
  time: 2
```

---

### Step 9: 店舗選択（全選択解除）

#### 9-1. ページ状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

**目的**: 店舗選択エリアが表示されていることを確認

#### 9-2. 「全選択」チェックボックスを外す

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "全選択チェックボックス"
  ref: [snapshot から取得したチェックボックスの ref]
```

**UI要素の特定方法**:
- テキスト: `text="全選択"` または `text="すべて選択"`

**期待される結果**: 全店舗の選択が解除される

---

### Step 10: 対象店舗を選択

#### 10-1. 店舗選択テキストボックスをクリック

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "店舗選択テキストボックス"
  ref: [snapshot から取得したテキストボックスの ref]
```

**期待される結果**: 店舗選択のドロップダウンが表示される

#### 10-2. ページ状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

**目的**: 店舗一覧のドロップダウンが表示されていることを確認

#### 10-3. 対象店舗をクリック

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "{storeName}"
  ref: [snapshot から取得した店舗名の ref]
```

**UI要素の特定方法**:
- テキスト: `text="{storeName}"`

**期待される結果**: 対象店舗が選択される

---

### Step 11: 期間を設定

#### 11-1. ページ状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

**目的**: 店舗別集計エリアと期間選択フィールドを確認

#### 11-2. 開始日フィールドをクリック

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "開始日フィールド"
  ref: [snapshot から取得した開始日フィールドの ref]
```

#### 11-3. 開始日を入力

YYYYMMDD形式をYYYY-MM-DD形式に変換して入力（例: 20260101 → 2026-01-01）

```
ツール: mcp__playwright__browser_fill_form
パラメータ:
  fields:
    - name: "開始日"
      type: "textbox"
      ref: [snapshot から取得した開始日フィールドの ref]
      value: "{startDate formatted as YYYY-MM-DD}"
```

#### 11-4. 終了日フィールドをクリック

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "終了日フィールド"
  ref: [snapshot から取得した終了日フィールドの ref]
```

#### 11-5. 終了日を入力

YYYYMMDD形式をYYYY-MM-DD形式に変換して入力（例: 20260131 → 2026-01-31）

```
ツール: mcp__playwright__browser_fill_form
パラメータ:
  fields:
    - name: "終了日"
      type: "textbox"
      ref: [snapshot から取得した終了日フィールドの ref]
      value: "{endDate formatted as YYYY-MM-DD}"
```

#### 11-6. エリア外をクリック（カレンダーを閉じる）

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "ページの他の部分"
  ref: [snapshot から取得したカレンダー外のエリアの ref]
```

**期待される結果**: カレンダー表記が閉じる

---

### Step 12: 注文一覧・取引一覧にチェックを入れる

#### 12-1. ページ状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

**目的**: チェックボックスの状態を確認

#### 12-2. 「注文一覧」チェックボックスをクリック

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "注文一覧チェックボックス"
  ref: [snapshot から取得したチェックボックスの ref]
```

**UI要素の特定方法**:
- テキスト: `text="注文一覧"`

#### 12-3. 「取引一覧」チェックボックスをクリック

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "取引一覧チェックボックス"
  ref: [snapshot から取得したチェックボックスの ref]
```

**UI要素の特定方法**:
- テキスト: `text="取引一覧"`

**注意**: 「注文一覧」と「取引一覧」の両方にチェックが入っている状態にする

---

### Step 13: ダウンロードボタンを探す

#### 13-1. 下にスクロール

```
ツール: mcp__playwright__browser_press_key
パラメータ:
  key: "PageDown"
```

#### 13-2. ページ状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

**目的**: ダウンロードボタンが表示されていることを確認

---

### Step 14: ダウンロード実行

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "ダウンロードボタン"
  ref: [snapshot から取得したボタンの ref]
```

**UI要素の特定方法**:
- テキスト: `text="ダウンロード"` または `text="Download"`
- ボタン: `button:has-text("ダウンロード")`

**期待される結果**: CSVファイルのダウンロードが開始される

---

### Step 15: ダウンロード完了を待機

```
ツール: mcp__playwright__browser_wait_for
パラメータ:
  time: 5
```

---

### Step 16: ファイルリネーム

ダウンロードされたファイルを以下の形式にリネームします：

**ファイル名形式**: `{startDate}-{endDate}-{storeName}.csv`

**例**:
- `20260101-20260131-昼からワイン食堂.csv`

**処理方法**:
1. ダウンロード先ディレクトリで最新のCSVファイルを特定
2. ファイル名を変更
3. 指定のダウンロードフォルダに移動

```bash
# macOSでの例
latestFile=$(ls -t ~/Downloads/*.csv | head -1)
newName="{startDate}-{endDate}-{storeName}.csv"
mv "$latestFile" "/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/週報/0_downloads/$newName"
```

---

### Step 17: ログアウト

#### 17-1. ユーザーアイコンをクリック

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "ユーザーアイコン"
  ref: [snapshot から取得した画面右上のユーザーアイコンの ref]
```

**UI要素の特定方法**:
- 画面右上にあるユーザーアイコン（アバター、プロフィール画像など）

#### 17-2. ページ状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

**目的**: ログアウトボタンの位置を確認

#### 17-3. ログアウトボタンをクリック

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "ログアウトボタン"
  ref: [snapshot から取得したログアウトボタンの ref]
```

**UI要素の特定方法**:
- テキスト: `text="ログアウト"` または `text="Sign Out"` または `text="Logout"`

#### 17-4. ログアウト完了を待機

```
ツール: mcp__playwright__browser_wait_for
パラメータ:
  time: 2
```

**期待される結果**: ログアウトが完了し、ログインページに戻る

---

## UI要素セレクタ一覧

### ログイン画面
| 要素 | セレクタ |
|------|---------|
| メールアドレス入力欄 | `input[type="email"]` または `placeholder="メールアドレス"` |
| パスワード入力欄 | `input[type="password"]` または `placeholder="パスワード"` |
| ログインボタン | `text="ログイン"` または `button[type="submit"]` |

### メインメニュー
| 要素 | セレクタ |
|------|---------|
| 分析メニュー | `text="分析"` |
| CSVダウンロード | `text="CSVダウンロード"` |

### CSVダウンロードページ
| 要素 | セレクタ |
|------|---------|
| 全選択チェックボックス | `text="全選択"` |
| 店舗選択テキストボックス | 店舗選択エリア内のテキストボックス |
| 開始日フィールド | 期間選択の開始日入力欄 |
| 終了日フィールド | 期間選択の終了日入力欄 |
| 注文一覧チェックボックス | `text="注文一覧"` |
| 取引一覧チェックボックス | `text="取引一覧"` |
| ダウンロードボタン | `text="ダウンロード"` |

### ログアウト
| 要素 | セレクタ |
|------|---------|
| ユーザーアイコン | 画面右上（要スナップショットで確認） |
| ログアウトボタン | `text="ログアウト"` |

---

## エラーハンドリング

| エラーケース | 検出方法 | 対処方法 |
|-------------|---------|---------|
| **ログイン失敗** | ログイン後もログインページが表示される | エラーを記録し終了 |
| **分析メニューが見つからない** | スナップショット内にメニューが存在しない | エラーを記録し終了 |
| **店舗が見つからない** | ドロップダウン内に店舗名が存在しない | エラーを記録し終了 |
| **期間入力エラー** | 日付形式が正しくない | 形式を確認し、再入力 |
| **ダウンロードボタンが見つからない** | スナップショット内にボタンが存在しない | スクロールして再検索 |
| **ダウンロード失敗** | ファイルが保存されない | 1回リトライ |
| **リネーム失敗** | ファイル名変更エラー | 元ファイル名のまま続行 |

---

## 実行結果の報告

### 成功時

```
Dinii注文一覧CSVダウンロード - 成功

対象店舗: 昼からワイン食堂
対象期間: 20260101 〜 20260131
ダウンロードファイル: 20260101-20260131-昼からワイン食堂.csv
保存先: /Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/週報/0_downloads

ダウンロードが完了しました。
```

### 失敗時

```
Dinii注文一覧CSVダウンロード - 失敗

対象店舗: 昼からワイン食堂
失敗ステップ: Step 4 - ログインボタンのクリック
エラー内容: ログインに失敗しました。

推奨対処:
- メールアドレスが正しいか確認してください
- パスワードが正しいか確認してください
```

---

## セキュリティとベストプラクティス

### セキュリティ

1. **パスワードの取り扱い**
   - パスワードはログやコンソール出力に表示しないこと

2. **認証情報の管理**
   - 認証情報は安全な場所に保管

### ベストプラクティス

1. **待機時間の調整**
   - ネットワーク状況に応じて `browser_wait_for` の時間を調整

2. **UI変更への対応**
   - DiniiのUIが更新された場合、セレクタや手順を見直す

3. **スナップショット活用**
   - 各ステップの前後で `browser_snapshot` を実行し、状態を確認

---

## 更新履歴

| 日付 | バージョン | 更新内容 |
|------|-----------|----------|
| 2026-01-05 | 1.0.0 | 初版作成 |
| 2026-02-02 | 1.1.0 | 取引一覧のチェックボックスも同時に選択するよう追加 |
| 2026-02-09 | 2.0.0 | 単一店舗モードに簡素化、ダウンロード先・ファイル名形式を変更 |

---

## ライセンス

このSkillは Restaurant AI Lab プロジェクトの一部です。

---

## 参考リンク

- [Playwright MCP ドキュメント](https://github.com/anthropics/anthropic-quickstarts/tree/main/mcp-server-playwright)
- [Dinii ダッシュボード](https://dashboard.self.dinii.jp/)
