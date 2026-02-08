---
name: "USENレジ売上CSVダウンロード"
description: "USENレジから店舗の売上データ（電表＋電表明細）をCSV形式でダウンロードします。"
version: "1.0.1"
author: "Restaurant AI Lab"
created: "2026-02-09"
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
  - name: companyCode
    type: string
    required: true
    description: 企業コード
    example: "12345"
  - name: username
    type: string
    required: true
    description: ユーザー名
    example: "user01"
  - name: password
    type: string
    required: true
    description: パスワード
    sensitive: true
  - name: storeName
    type: string
    required: true
    description: 店舗名
    example: "渋谷店"
constants:
  loginUrl: "https://u07.u-regi.com/"
  downloadPath: "/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/週報/0_downloads"
  fileNameFormat: "{startDate}-{endDate}-{storeName}.csv"
---

# USENレジ売上CSVダウンロード

## 概要

このSkillは、Playwright MCPを使用してUSENレジにログインし、指定された店舗・期間の売上データCSVを自動的にダウンロードします。

**機能**:
- 単一店舗の売上データダウンロード
- ダウンロード後のファイルリネーム
- 指定項目の選択によるカスタムCSV出力

**出力先**: /Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/週報/0_downloads
**ファイル名形式**: `{開始日}-{終了日}-{店舗名}.csv`（例: `20260101-20260131-渋谷店.csv`）

---

## 実行前の確認事項

このSkillを実行する前に、以下を確認してください：

- [ ] Playwright MCPが有効になっているか
- [ ] 対象期間（開始日・終了日）が指定されているか
- [ ] 企業コード、ユーザー名、パスワードが正しいか
- [ ] ダウンロード先ディレクトリが存在するか

---

## 必要なパラメータ

| パラメータ | 必須 | 説明 | 例 |
|-----------|-----|------|-----|
| `startDate` | ✅ | 集計開始日（YYYYMMDD形式） | `20260101` |
| `endDate` | ✅ | 集計終了日（YYYYMMDD形式） | `20260131` |
| `companyCode` | ✅ | 企業コード | `12345` |
| `username` | ✅ | ユーザー名 | `user01` |
| `password` | ✅ | パスワード | `********` |
| `storeName` | ✅ | 店舗名 | `渋谷店` |

---

## 実装手順

### 全体フロー

```
1. ログインページへ遷移
2. 企業コード、ユーザー名、パスワードを入力してログイン
3. 店舗選択画面が表示された場合は対象店舗を選択
4. サイドメニューから「帳票管理」→「汎用検索」を選択
5. 新しいタブで検索画面が開く
6. データ種別、店舗、対象期間、項目を設定
7. CSV出力
8. ファイルリネーム
9. 完了レポートを出力
```

---

## 各ステップの処理手順

### Step 1: ブラウザ起動とログインページへ遷移

```
ツール: mcp__playwright__browser_navigate
パラメータ:
  url: "https://u07.u-regi.com/"
```

**期待される結果**: USENレジログインページが表示される

---

### Step 2: ページの状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

**目的**: ログインフォームが表示されていることを確認（企業コード、ユーザー名、パスワードの3つの入力欄）

---

### Step 3: ログイン情報を入力

#### 3-1. 企業コードを入力

```
ツール: mcp__playwright__browser_fill_form
パラメータ:
  fields:
    - name: "企業コード"
      type: "textbox"
      ref: [snapshot から取得した入力欄の ref]
      value: {companyCode}
```

#### 3-2. ユーザー名を入力

```
ツール: mcp__playwright__browser_fill_form
パラメータ:
  fields:
    - name: "ユーザー名"
      type: "textbox"
      ref: [snapshot から取得した入力欄の ref]
      value: {username}
```

#### 3-3. パスワードを入力

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
- 上から順に：企業コード、ユーザー名、パスワードの入力欄
- または `input[type="text"]`, `input[type="password"]`

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
- またはボタン: `button[type="submit"]`

**期待される結果**: ログインが成功し、店舗選択画面またはダッシュボードに遷移

---

### Step 5: ページ読み込みを待機

```
ツール: mcp__playwright__browser_wait_for
パラメータ:
  time: 3
```

---

### Step 6: 店舗選択（必要な場合）

#### 6-1. ページ状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

**目的**: 店舗選択画面が表示されているか、または既にダッシュボードが表示されているかを確認

#### 6-2. 店舗をクリック（店舗選択画面が表示されている場合）

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "{storeName} 店舗選択"
  ref: [snapshot から取得した店舗名の ref]
```

**UI要素の特定方法**:
- テキスト: `text="{storeName}"`

**エラーハンドリング**:
- 店舗が見つからない場合: スナップショットから表示されている店舗一覧を確認し、エラーを記録

---

### Step 7: サイドメニューを開く（必要な場合）

#### 7-1. ページ状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

**目的**: サイドメニューの状態を確認

#### 7-2. ハンバーガーボタンをクリック（サイドメニューが閉じている場合）

**条件**: サイドメニューが閉じている場合のみ実行

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "ハンバーガーメニューボタン"
  ref: [snapshot から取得した左上のハンバーガーボタンの ref]
```

**UI要素の特定方法**:
- 画面左上にある三本線のアイコン（ハンバーガーメニュー）

---

### Step 8: 帳票管理メニューを選択

#### 8-1. ページ状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

**目的**: サイドメニューの内容を確認

#### 8-2. 「帳票管理」をクリック

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "帳票管理メニュー"
  ref: [snapshot から取得したメニュー項目の ref]
```

**UI要素の特定方法**:
- テキスト: `text="帳票管理"`

**期待される結果**: 帳票管理のサブメニューが表示される

---

### Step 9: 汎用検索を選択

#### 9-1. ページ状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

**目的**: サブメニューの内容を確認

#### 9-2. 「汎用検索」をクリック

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "汎用検索メニュー"
  ref: [snapshot から取得したメニュー項目の ref]
```

**UI要素の特定方法**:
- テキスト: `text="汎用検索"`

**期待される結果**: 新しいタブで検索画面が開かれる

---

### Step 10: 新しいタブに切り替え

```
ツール: mcp__playwright__browser_tabs
パラメータ:
  action: "list"
```

**目的**: 開いているタブを確認

```
ツール: mcp__playwright__browser_tabs
パラメータ:
  action: "select"
  index: [新しいタブのインデックス]
```

**期待される結果**: 検索画面のタブがアクティブになる

---

### Step 11: ページ読み込みを待機

```
ツール: mcp__playwright__browser_wait_for
パラメータ:
  time: 3
```

---

### Step 12: 検索画面の設定

#### 12-1. ページ状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

**目的**: 検索画面の入力項目を確認

#### 12-2. データ種別を選択

```
ツール: mcp__playwright__browser_select_option
パラメータ:
  element: "データ種別ドロップダウン"
  ref: [snapshot から取得したドロップダウンの ref]
  values: ["売上データ（電表＋電表明細）"]
```

**UI要素の特定方法**:
- 「データ」ラベルの隣にあるドロップダウン

---

### Step 13: 店舗を選択

#### 13-1. ページ状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

#### 13-2. 店舗選択

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "店舗選択"
  ref: [snapshot から取得した店舗選択エリアの ref]
```

対象店舗を選択:

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "{storeName}"
  ref: [snapshot から取得した店舗名の ref]
```

---

### Step 14: 対象期間を設定

#### 14-1. ページ状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

#### 14-2. 開始日を入力

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "開始日フィールド"
  ref: [snapshot から取得した開始日フィールドの ref]
```

```
ツール: mcp__playwright__browser_type
パラメータ:
  ref: [snapshot から取得した開始日フィールドの ref]
  text: "{startDate}"
```

**入力形式**: `YYYYMMDD`（例: `20260101`）

#### 14-3. 終了日を入力

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "終了日フィールド"
  ref: [snapshot から取得した終了日フィールドの ref]
```

```
ツール: mcp__playwright__browser_type
パラメータ:
  ref: [snapshot から取得した終了日フィールドの ref]
  text: "{endDate}"
```

**入力形式**: `YYYYMMDD`（例: `20260131`）

---

### Step 15: 項目を選択

#### 15-1. ページ状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

**目的**: 項目選択エリアを確認（スクロール可能なリスト）

#### 15-2. 以下の項目を順番に選択

**選択する項目一覧**:
1. H.年表番号
2. H.集計対象営業年月日
3. H.曜日
4. H.電表発行日
5. H.電表処理日
6. H.客数（合計）
7. H.小計
8. H.総商品数
9. D.カテゴリー
10. D.商品カテゴリー1
11. D.商品カテゴリー2
12. D.商品
13. D.商品名
14. D.サブメニュー
15. D.価格
16. D.オーダー日時
17. D.数量
18. D.オーダーステータス

**注意**: 項目一覧はスクロール可能。すべての項目を選択するために適宜スクロールが必要

各項目について:

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "{項目名}"
  ref: [snapshot から取得した項目の ref]
```

スクロールが必要な場合:

```
ツール: mcp__playwright__browser_evaluate
パラメータ:
  function: "() => { document.querySelector('[項目リストのセレクタ]').scrollBy(0, 200); }"
```

---

### Step 16: CSV出力

#### 16-1. ページ状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

**目的**: CSV出力ボタンを確認

#### 16-2. CSV出力ボタンをクリック

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "CSV出力ボタン"
  ref: [snapshot から取得したボタンの ref]
```

**UI要素の特定方法**:
- テキスト: `text="CSV出力"`

**期待される結果**: CSVファイルのダウンロードが開始される

---

### Step 17: ダウンロード完了を待機

```
ツール: mcp__playwright__browser_wait_for
パラメータ:
  time: 5
```

---

### Step 18: ファイルリネーム

ダウンロードされたファイルを以下の形式にリネームします：

**ファイル名形式**: `{startDate}-{endDate}-{storeName}.csv`

**例**:
- `20260101-20260131-渋谷店.csv`

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

### Step 19: ブラウザを閉じる

```
ツール: mcp__playwright__browser_close
パラメータ: なし
```

---

## UI要素セレクタ一覧

### ログイン画面
| 要素 | セレクタ |
|------|---------|
| 企業コード入力欄 | 1番目のテキスト入力欄 |
| ユーザー名入力欄 | 2番目のテキスト入力欄 |
| パスワード入力欄 | `input[type="password"]` |
| ログインボタン | `text="ログイン"` |

### メインメニュー
| 要素 | セレクタ |
|------|---------|
| ハンバーガーボタン | 画面左上の三本線アイコン |
| 帳票管理 | `text="帳票管理"` |
| 汎用検索 | `text="汎用検索"` |

### 検索画面
| 要素 | セレクタ |
|------|---------|
| データ種別 | 「データ」ラベル横のドロップダウン |
| 店舗選択 | 店舗選択エリア |
| 開始日 | 対象期間の開始日入力欄 |
| 終了日 | 対象期間の終了日入力欄 |
| 項目リスト | スクロール可能な項目選択エリア |
| CSV出力ボタン | `text="CSV出力"` |

---

## エラーハンドリング

| エラーケース | 検出方法 | 対処方法 |
|-------------|---------|---------|
| **ログイン失敗** | ログイン後もログインページが表示される | エラーを記録し終了 |
| **店舗が見つからない** | スナップショット内に店舗名が存在しない | エラーを記録し終了 |
| **サイドメニューが閉じている** | 「帳票管理」が表示されていない | ハンバーガーボタンをクリックして展開 |
| **新しいタブが開かない** | タブ一覧に検索画面がない | リトライまたはエラー記録 |
| **項目が見つからない** | スクロールしても項目が見つからない | エラーを記録 |
| **CSV出力ボタンが見つからない** | スナップショット内にボタンが存在しない | スクロールして再検索 |
| **ダウンロード失敗** | ファイルが保存されない | 1回リトライ |
| **リネーム失敗** | ファイル名変更エラー | 元ファイル名のまま続行、警告を記録 |

---

## 実行結果の報告

### 成功時

```
USENレジ売上CSVダウンロード - 成功

対象店舗: 渋谷店
対象期間: 20260101 〜 20260131
ダウンロードファイル: 20260101-20260131-渋谷店.csv
保存先: /Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/週報/0_downloads

ダウンロードが完了しました。
```

### 失敗時

```
USENレジ売上CSVダウンロード - 失敗

対象店舗: 渋谷店
失敗ステップ: Step 4 - ログインボタンのクリック
エラー内容: ログインに失敗しました。

推奨対処:
- 企業コードが正しいか確認してください
- ユーザー名が正しいか確認してください
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
   - USENレジのUIが更新された場合、セレクタや手順を見直す

3. **スナップショット活用**
   - 各ステップの前後で `browser_snapshot` を実行し、状態を確認

---

## 更新履歴

| 日付 | バージョン | 更新内容 |
|------|-----------|----------|
| 2026-02-09 | 1.0.0 | 初版作成 - USENレジ売上CSVダウンロード機能を実装 |
| 2026-02-09 | 1.0.1 | D.オーダーステータスを項目一覧に追加 |

---

## ライセンス

このSkillは Restaurant AI Lab プロジェクトの一部です。

---

## 参考リンク

- [Playwright MCP ドキュメント](https://github.com/anthropics/anthropic-quickstarts/tree/main/mcp-server-playwright)
- [USENレジ](https://u07.u-regi.com/)
