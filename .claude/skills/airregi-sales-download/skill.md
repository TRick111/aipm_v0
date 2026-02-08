---
name: "AirRegi日別売上CSVダウンロード"
description: "AirRegiから店舗の日別売上データ（会計明細）をCSV形式でダウンロードします。"
version: "2.0.0"
author: "Restaurant AI Lab"
created: "2026-01-03"
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
  - name: airIDOrEmail
    type: string
    required: true
    description: AirIDまたはメールアドレス
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
    example: "BAR FIVE Arrows"
constants:
  loginUrl: "https://connect.airregi.jp/login?client_id=ARG&redirect_uri=https%3A%2F%2Fconnect.airregi.jp%2Foauth%2Fauthorize%3Fclient_id%3DARG%26redirect_uri%3Dhttps%253A%252F%252Fairregi.jp%252FCLP%252Fview%252FcallbackForPlfLogin%252Fauth%26response_type%3Dcode"
  downloadPath: "/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/週報/0_downloads"
  fileNameFormat: "{startDate}-{endDate}-{storeName}.csv"
---

# AirRegi日別売上CSVダウンロード

## 概要

このSkillは、Playwright MCPを使用してAirRegiにログインし、指定された店舗・期間の会計明細CSVを自動的にダウンロードします。

**機能**:
- 単一店舗の売上データダウンロード
- ダウンロード後のファイルリネーム
- ログアウト処理

**出力先**: /Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/週報/0_downloads
**ファイル名形式**: `{開始日}-{終了日}-{店舗名}.csv`（例: `20260101-20260131-BAR FIVE Arrows.csv`）

---

## 必要なパラメータ

| パラメータ | 必須 | 説明 | 例 |
|-----------|-----|------|-----|
| `startDate` | ✅ | 集計開始日（YYYYMMDD形式） | `20260101` |
| `endDate` | ✅ | 集計終了日（YYYYMMDD形式） | `20260131` |
| `airIDOrEmail` | ✅ | AirIDまたはメールアドレス | `example@email.com` |
| `password` | ✅ | パスワード | `********` |
| `storeName` | ✅ | 店舗名 | `BAR FIVE Arrows` |

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
2. AirID/メールアドレス、パスワードを入力してログイン
3. 店舗選択（複数店舗がある場合）
4. 売上・分析 → 日別売上 へ移動
5. 年月選択 → 表示する
6. CSVダウンロード（会計明細）
7. ファイルリネーム
8. ログアウト
9. 完了レポートを出力
```

---

## 各ステップの処理手順

### Step 1: ブラウザ起動とログインページへ遷移

```
ツール: mcp__playwright__browser_navigate
パラメータ:
  url: "https://connect.airregi.jp/login?client_id=ARG&redirect_uri=https%3A%2F%2Fconnect.airregi.jp%2Foauth%2Fauthorize%3Fclient_id%3DARG%26redirect_uri%3Dhttps%253A%252F%252Fairregi.jp%252FCLP%252Fview%252FcallbackForPlfLogin%252Fauth%26response_type%3Dcode"
```

**期待される結果**: AirRegiログインページが表示される

---

### Step 2: ページの状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

**目的**: ログインフォームが表示されていることを確認

---

### Step 3: ログイン情報を入力

#### 3-1. メールアドレス/AirIDを入力

```
ツール: mcp__playwright__browser_fill_form
パラメータ:
  fields:
    - name: "AirIDまたはメールアドレス"
      type: "textbox"
      ref: [snapshot から取得した入力欄の ref]
      value: {airIDOrEmail}
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
- プレースホルダー: `placeholder="AirIDまたはメールアドレス"`
- プレースホルダー: `placeholder="パスワード"`

---

### Step 4: ログインボタンをクリック

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "ログインボタン"
  ref: [snapshot から取得したボタンの ref]
```

**UI要素の特定方法**:
- テキスト: `text="ログイン"`

**期待される結果**: ログインが成功し、店舗選択画面またはダッシュボードに遷移

---

### Step 5: ページ読み込みを待機

```
ツール: mcp__playwright__browser_wait_for
パラメータ:
  time: 3
```

---

### Step 6: 店舗を選択

#### 6-1. 現在のページ状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

**目的**: 店舗選択画面が表示されているか確認

#### 6-2. 店舗をクリック（必要な場合）

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "{storeName} 店舗選択"
  ref: [snapshot から取得した店舗名の ref]
```

**UI要素の特定方法**:
- テキスト: `text="{storeName}"`

---

### Step 7: 売上・分析メニューを開く

#### 7-1. ページ状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

**目的**: 左側メニューの状態を確認

#### 7-2. 「売上・分析」メニューを展開（必要な場合）

**条件**: 「日別売上」が表示されていない場合のみ実行

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "売上・分析メニュー"
  ref: [snapshot から取得したメニュー項目の ref]
```

**UI要素の特定方法**:
- テキスト: `text="売上・分析"`

#### 7-3. 「日別売上」をクリック

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "日別売上メニュー"
  ref: [snapshot から取得したメニュー項目の ref]
```

**UI要素の特定方法**:
- テキスト: `text="日別売上"`

**期待される結果**: 日別売上ページが表示される

---

### Step 8: ページ読み込みを待機

```
ツール: mcp__playwright__browser_wait_for
パラメータ:
  time: 2
```

---

### Step 9: 集計対象の年月を選択

#### 9-1. ページ状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

**目的**: 年月選択フォームが表示されていることを確認

#### 9-2. 年を選択

startDateから年を抽出（例: 20260101 → 2026）

```
ツール: mcp__playwright__browser_select_option
パラメータ:
  element: "年の選択ボックス"
  ref: [snapshot から取得した年選択ボックスの ref]
  values: ["{year}"]
```

#### 9-3. 月を選択

startDateから月を抽出（例: 20260101 → 1）

```
ツール: mcp__playwright__browser_select_option
パラメータ:
  element: "月の選択ボックス"
  ref: [snapshot から取得した月選択ボックスの ref]
  values: ["{month}"]
```

#### 9-4. 「表示する」ボタンをクリック

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "表示するボタン"
  ref: [snapshot から取得したボタンの ref]
```

**UI要素の特定方法**:
- テキスト: `text="表示する"`

**期待される結果**: 指定した年月の日別売上データが表示される

---

### Step 10: ページ読み込みを待機

```
ツール: mcp__playwright__browser_wait_for
パラメータ:
  time: 3
```

---

### Step 11: CSVダウンロードボタンを探す

#### 11-1. ページ状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

**目的**: 「CSVデータをダウンロードする」ボタンが表示されているかを確認

---

### Step 12: CSVをダウンロード

#### 12-1. 「CSVデータをダウンロードする」ボタンをクリック

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "CSVデータをダウンロードするボタン"
  ref: [snapshot から取得したボタンの ref]
```

**UI要素の特定方法**:
- テキスト: `text="CSVデータをダウンロードする"`

#### 12-2. 「会計明細」を選択

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "会計明細リンク/ボタン"
  ref: [snapshot から取得した会計明細の ref]
```

**UI要素の特定方法**:
- テキスト: `text="会計明細"`

**期待される結果**: CSVファイルのダウンロードが開始される

---

### Step 13: ダウンロード完了を待機

```
ツール: mcp__playwright__browser_wait_for
パラメータ:
  time: 5
```

---

### Step 14: ファイルリネーム

ダウンロードされたファイルを以下の形式にリネームします：

**ファイル名形式**: `{startDate}-{endDate}-{storeName}.csv`

**例**:
- `20260101-20260131-BAR FIVE Arrows.csv`

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

### Step 15: ログアウト

#### 15-1. アカウントドロップダウンをクリック

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

**目的**: 画面右上のアカウント領域を確認

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "アカウントドロップダウン（AirID表示領域）"
  ref: [snapshot から取得したアカウント領域の ref]
```

**UI要素の特定方法**:
- **位置**: 画面右上
- **要素**: AirIDが表示されているlistitem

#### 15-2. ログアウトボタンをクリック

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "ログアウトボタン"
  ref: [snapshot から取得したログアウトボタンの ref]
```

**UI要素の特定方法**:
- テキスト: `text="ログアウト"`

#### 15-3. ログアウト確認ダイアログで「OK」をクリック

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "OKボタン"
  ref: [snapshot から取得したOKボタンの ref]
```

**期待される結果**: ログアウトが完了し、ログインページに戻る

---

## UI要素セレクタ一覧

### ログイン画面
| 要素 | セレクタ |
|------|---------|
| ID入力欄 | `placeholder="AirIDまたはメールアドレス"` |
| パスワード入力欄 | `placeholder="パスワード"` |
| ログインボタン | `text="ログイン"` |

### メインメニュー
| 要素 | セレクタ |
|------|---------|
| 売上・分析 | `text="売上・分析"` |
| 日別売上 | `text="日別売上"` |

### 日別売上ページ
| 要素 | セレクタ |
|------|---------|
| 表示ボタン | `text="表示する"` |
| CSVダウンロードボタン | `text="CSVデータをダウンロードする"` |
| 会計明細 | `text="会計明細"` |

### ログアウト
| 要素 | セレクタ |
|------|---------|
| アカウントドロップダウン | 画面右上のlistitem |
| ログアウトボタン | `text="ログアウト"` |
| OK確認ボタン | `text="OK"` |

---

## エラーハンドリング

| エラーケース | 検出方法 | 対処方法 |
|-------------|---------|---------|
| **ログイン失敗** | ログイン後もログインページが表示される | エラーを記録し終了 |
| **店舗が見つからない** | スナップショット内に店舗名が存在しない | エラーを記録し終了 |
| **メニューが畳まれている** | 「日別売上」が表示されていない | 「売上・分析」をクリックして展開 |
| **CSVボタンが見つからない** | スナップショット内にボタンが存在しない | スクロールして再検索 |
| **ダウンロード失敗** | ファイルが保存されない | 1回リトライ |
| **リネーム失敗** | ファイル名変更エラー | 元ファイル名のまま続行 |

---

## 実行結果の報告

### 成功時

```
AirRegi日別売上CSVダウンロード - 成功

対象店舗: BAR FIVE Arrows
対象期間: 20260101 〜 20260131
ダウンロードファイル: 20260101-20260131-BAR FIVE Arrows.csv
保存先: /Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/週報/0_downloads

ダウンロードが完了しました。
```

### 失敗時

```
AirRegi日別売上CSVダウンロード - 失敗

対象店舗: BAR FIVE Arrows
失敗ステップ: Step 4 - ログインボタンのクリック
エラー内容: ログインに失敗しました。

推奨対処:
- AirIDまたはメールアドレスが正しいか確認してください
- パスワードが正しいか確認してください
```

---

## セキュリティとベストプラクティス

### セキュリティ

1. **パスワードの取り扱い**
   - パスワードはログやコンソール出力に表示しないこと
   - 実行ログには `password: "****"` のようにマスクして記録

2. **認証情報の管理**
   - 認証情報は安全な場所に保管

### ベストプラクティス

1. **待機時間の調整**
   - ネットワーク状況に応じて `browser_wait_for` の時間を調整

2. **UI変更への対応**
   - AirRegiのUIが更新された場合、セレクタや手順を見直す

3. **スナップショット活用**
   - 各ステップの前後で `browser_snapshot` を実行し、状態を確認

---

## 更新履歴

| 日付 | バージョン | 更新内容 |
|------|-----------|----------|
| 2026-01-03 | 1.0.0 | 初版作成 |
| 2026-01-03 | 1.1.0 | 複数店舗一括ダウンロード、ログアウト処理、ファイルリネーム追加 |
| 2026-01-03 | 1.1.1 | ログアウト処理の改善 |
| 2026-02-09 | 2.0.0 | 単一店舗モードに簡素化、ダウンロード先・ファイル名形式を変更 |

---

## ライセンス

このSkillは Restaurant AI Lab プロジェクトの一部です。

---

## 参考リンク

- [Playwright MCP ドキュメント](https://github.com/anthropics/anthropic-quickstarts/tree/main/mcp-server-playwright)
- [AirRegi 公式サイト](https://airregi.jp/)
