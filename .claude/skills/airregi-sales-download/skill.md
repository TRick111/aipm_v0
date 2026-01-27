---
name: "AirRegi日別売上CSVダウンロード"
description: "AirRegiから複数店舗の日別売上データ（会計明細）をCSV形式で一括ダウンロードします。"
version: "1.1.1"
author: "Restaurant AI Lab"
created: "2026-01-03"
updated: "2026-01-03"
dependencies:
  - playwright-mcp
parameters:
  - name: targetYear
    type: string
    required: true
    description: 集計対象の年
    example: "2026"
  - name: targetMonth
    type: string
    required: true
    description: 集計対象の月
    example: "1"
  - name: accountsFilePath
    type: string
    required: false
    description: 店舗アカウントCSVファイルのパス（指定しない場合は単一店舗モード）
    default: "プロンプト/Download/airregi_accounts.csv"
  - name: airIDOrEmail
    type: string
    required: false
    description: AirIDまたはメールアドレス（単一店舗モード時に使用）
    example: "example@email.com"
  - name: password
    type: string
    required: false
    description: パスワード（単一店舗モード時に使用）
    sensitive: true
  - name: storeName
    type: string
    required: false
    description: 店舗名（単一店舗モード時に使用）
    default: "BAR FIVE Arrows"
constants:
  loginUrl: "https://connect.airregi.jp/login?client_id=ARG&redirect_uri=https%3A%2F%2Fconnect.airregi.jp%2Foauth%2Fauthorize%3Fclient_id%3DARG%26redirect_uri%3Dhttps%253A%252F%252Fairregi.jp%252FCLP%252Fview%252FcallbackForPlfLogin%252Fauth%26response_type%3Dcode"
  downloadPath: "C:\\Users\\auk1i\\Downloads"
  fileNameFormat: "{storeName}_{YYYYMM}_POS.csv"
---

# AirRegi日別売上CSVダウンロード

## 概要

このSkillは、Playwright MCPを使用してAirRegiにログインし、指定された店舗・月の会計明細CSVを自動的にダウンロードします。

**機能**:
- ✅ 複数店舗の一括ダウンロード（CSVファイルから店舗リストを読み込み）
- ✅ 単一店舗のダウンロード（パラメータ直接指定）
- ✅ ダウンロード後のファイルリネーム
- ✅ ログアウト処理

**出力先**: C:\Users\auk1i\Downloads
**ファイル名形式**: `{店舗名}_{YYYYMM}_POS.csv`（例: `昼からワイン食堂_202601_POS.csv`）

---

## 実行モード

### モード1: 複数店舗一括ダウンロード

店舗アカウントCSVファイルを読み込み、全店舗を順番に処理します。

**必要なパラメータ**:
- `targetYear`: 集計対象の年
- `targetMonth`: 集計対象の月
- `accountsFilePath`: 店舗アカウントCSVファイルのパス

### モード2: 単一店舗ダウンロード

1店舗のみをダウンロードします。

**必要なパラメータ**:
- `targetYear`: 集計対象の年
- `targetMonth`: 集計対象の月
- `airIDOrEmail`: AirIDまたはメールアドレス
- `password`: パスワード
- `storeName`: 店舗名

---

## 店舗アカウントファイル形式

**ファイルパス**: `プロンプト/Download/airregi_accounts.csv`

```csv
storeCode,storeName,airregiId,password
fd-001,昼からワイン食堂,example1@email.com,password1
fd-002,レイカフェ,example2@email.com,password2
fd-003,せんべろ,example3@email.com,password3
```

| カラム | 説明 |
|--------|------|
| `storeCode` | 自社管理用の店舗ID（ログ出力用） |
| `storeName` | 店舗名（AirRegiでの表示名と一致させる、ファイル名に使用） |
| `airregiId` | AirRegiのログインID（AirIDまたはメールアドレス） |
| `password` | AirRegiのパスワード |

---

## 実行前の確認事項

このSkillを実行する前に、以下を確認してください：

- [ ] Playwright MCPが有効になっているか
- [ ] 対象年月が指定されているか（指定がない場合はユーザーに確認）
- [ ] 店舗アカウントCSVファイルに正しい認証情報が入力されているか
- [ ] ダウンロード先ディレクトリ（C:\Users\auk1i\Downloads）が存在するか

---

## 実装手順（複数店舗モード）

### 全体フロー

```
1. 店舗アカウントCSVファイルを読み込む
2. 各店舗に対してループ処理:
   a. ログイン
   b. 店舗選択（複数店舗がある場合）
   c. 売上・分析 → 日別売上 へ移動
   d. 年月選択 → 表示する
   e. CSVダウンロード
   f. ファイルリネーム
   g. ログアウト
3. 完了レポートを出力
```

---

## 各店舗の処理手順

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
      value: {store.airregiId}
```

#### 3-2. パスワードを入力

```
ツール: mcp__playwright__browser_fill_form
パラメータ:
  fields:
    - name: "パスワード"
      type: "textbox"
      ref: [snapshot から取得したパスワード欄の ref]
      value: {store.password}
```

**UI要素の特定方法**:
- プレースホルダー: `placeholder="AirIDまたはメールアドレス"`
- プレースホルダー: `placeholder="パスワード"`
- または `input[type="email"]`, `input[type="password"]`

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
- またはボタン: `button:has-text("ログイン")`

**期待される結果**: ログインが成功し、店舗選択画面またはダッシュボードに遷移

---

### Step 5: ページ読み込みを待機

```
ツール: mcp__playwright__browser_wait_for
パラメータ:
  time: 3
```

**目的**: ページ遷移とデータ読み込みを待つ

---

### Step 6: 店舗を選択

#### 6-1. 現在のページ状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

**目的**: 店舗選択画面が表示されているか、または既に店舗が選択されているかを確認

#### 6-2. 店舗をクリック（必要な場合）

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "{store.storeName} 店舗選択"
  ref: [snapshot から取得した店舗名の ref]
```

**UI要素の特定方法**:
- テキスト: `text="{store.storeName}"`

**エラーハンドリング**:
- 店舗が見つからない場合: スナップショットから表示されている店舗一覧を確認し、エラーを記録して次の店舗へ

---

### Step 7: 売上・分析メニューを開く

#### 7-1. ページ状態を確認

```
ツール: mcp__playwright__browser_snapshot
パラメータ: なし
```

**目的**: 左側メニューの状態を確認し、「日別売上」が既に表示されているかチェック

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

```
ツール: mcp__playwright__browser_select_option
パラメータ:
  element: "年の選択ボックス"
  ref: [snapshot から取得した年選択ボックスの ref]
  values: ["{targetYear}"]
```

#### 9-3. 月を選択

```
ツール: mcp__playwright__browser_select_option
パラメータ:
  element: "月の選択ボックス"
  ref: [snapshot から取得した月選択ボックスの ref]
  values: ["{targetMonth}"]
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
- またはボタン: `button:has-text("表示する")`

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

#### 11-2. 必要に応じてスクロール

**条件**: ボタンが見当たらない場合のみ実行

```
ツール: mcp__playwright__browser_scroll
パラメータ:
  direction: "down"
```

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

### Step 14: ファイルリネーム ⭐ 新機能

ダウンロードされたファイルを以下の形式にリネームします：

**ファイル名形式**: `{store.storeName}_{YYYYMM}_POS.csv`

**例**:
- `昼からワイン食堂_202601_POS.csv`
- `レイカフェ_202601_POS.csv`
- `Bar Five Arrows_202601_POS.csv`

**処理方法**:
1. ダウンロード先ディレクトリ（C:\Users\auk1i\Downloads）で最新のCSVファイルを特定
2. ファイル名を変更

```
# PowerShellでの例
$latestFile = Get-ChildItem "C:\Users\auk1i\Downloads\*.csv" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$newName = "{store.storeName}_{targetYear}{targetMonth.padStart(2,'0')}_POS.csv"
Rename-Item $latestFile.FullName $newName
```

---

### Step 15: ログアウト ⭐ 新機能

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
- **位置**: 画面右上（左上ではない！）
- **要素**: AirIDが表示されているlistitem（例: `bar_five_arrows`）
- **セレクタ例**: `listitem` で `hasText` にAirIDを含むもの
- クリックするとポップアップ/ドロップダウンメニューが表示される

**重要**:
- 画面の**右上**にあるアカウント領域を探すこと
- 通常、3つのlistitemが並んでいる（AirID、店舗名、サービス切り替え）
- 最初のlistitem（AirIDが表示されている要素）をクリックする

#### 15-2. ログアウトボタンをクリック

ドロップダウンメニューが表示されたら、ログアウトボタンをクリックします。

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "ログアウトボタン"
  ref: [snapshot から取得したログアウトボタンの ref]
```

**UI要素の特定方法**:
- テキスト: `text="ログアウト"`
- ドロップダウン内に表示される

**期待される結果**: ログアウト確認ダイアログが表示される

#### 15-3. ログアウト確認ダイアログで「OK」をクリック

⚠️ **重要**: ログアウトボタンをクリックすると、確認ダイアログが表示されます。

```
ツール: mcp__playwright__browser_click
パラメータ:
  element: "OKボタン"
  ref: [snapshot から取得したOKボタンの ref]
```

**UI要素の特定方法**:
- ダイアログ内のボタン: `text="OK"`
- 確認メッセージ: 「ログアウトしますか？」

**期待される結果**: ログアウトが完了し、ログインページに戻る

#### 15-4. ログアウト完了の確認

```
ツール: mcp__playwright__browser_wait_for
パラメータ:
  time: 2
```

**期待される結果**:
- URLが `https://connect.airregi.jp/login` に変わる
- ログインページが表示される

---

### Step 16: 次の店舗へ（複数店舗モードの場合）

ループの次のイテレーションへ進み、Step 1 から繰り返す。

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
| 要素 | セレクタ | 補足 |
|------|---------|------|
| アカウントドロップダウン | 画面右上のlistitem（AirID表示） | 例: `listitem:has-text("bar_five_arrows")` |
| ログアウトボタン | `text="ログアウト"` | ドロップダウン内に表示 |
| OK確認ボタン | `text="OK"` | 確認ダイアログ内 |

---

## エラーハンドリング

実行中に以下のエラーが発生する可能性があります。適切に対処してください：

| エラーケース | 検出方法 | 対処方法 |
|-------------|---------|---------|
| **ログイン失敗** | ログイン後もログインページが表示される | エラーを記録し、次の店舗へスキップ |
| **店舗が見つからない** | スナップショット内に店舗名が存在しない | エラーを記録し、次の店舗へスキップ |
| **メニューが畳まれている** | 「日別売上」が表示されていない | 「売上・分析」をクリックして展開 |
| **CSVボタンが見つからない** | スナップショット内にボタンが存在しない | スクロールして再検索。見つからなければエラー記録 |
| **ダウンロード失敗** | ファイルが保存されない | 1回リトライ。失敗ならエラー記録 |
| **リネーム失敗** | ファイル名変更エラー | 元ファイル名のまま続行、警告を記録 |
| **ログアウト失敗** | ログアウトボタンがクリックできない | ブラウザを閉じて次の店舗は新規セッションで開始 |

### エラー発生時の基本対応フロー（複数店舗モード）

1. **エラーを記録**: どの店舗で何が起きたかを記録
2. **現在の店舗をスキップ**: エラーが発生したら次の店舗へ
3. **ブラウザをリセット**: ログアウト失敗時はブラウザを閉じる
4. **最後にレポート出力**: 成功/失敗を一覧で報告

---

## 実行結果の報告

### 複数店舗モードの報告形式

```
============================================
AirRegi 売上CSV一括ダウンロード 完了レポート
============================================
対象期間: 2026年1月
実行日時: 2026-01-03 16:30:00

【成功】3店舗
  ✅ fd-001 昼からワイン食堂 → 昼からワイン食堂_202601_POS.csv
  ✅ fd-002 レイカフェ → レイカフェ_202601_POS.csv
  ✅ fd-003 せんべろ → せんべろ_202601_POS.csv

【失敗】2店舗
  ❌ fd-004 二階のフレン家
     原因: ログイン失敗（認証エラー）
  ❌ fd-005 河本式
     原因: CSVダウンロードボタンが見つからない

保存先: C:\Users\auk1i\Downloads
============================================
```

### 単一店舗モードの報告形式

#### ✅ 成功時

```
AirRegi日別売上CSVダウンロード - 成功

対象店舗: BAR FIVE Arrows
対象期間: 2026年1月
ダウンロードファイル: Bar Five Arrows_202601_POS.csv
保存先: C:\Users\auk1i\Downloads

ダウンロードが完了しました。
```

#### ❌ 失敗時

```
AirRegi日別売上CSVダウンロード - 失敗

対象店舗: BAR FIVE Arrows
失敗ステップ: Step 4 - ログインボタンのクリック
エラー内容: ログインに失敗しました。「メールアドレスまたはパスワードが正しくありません」というエラーが表示されています。

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
   - `airregi_accounts.csv` を `.gitignore` に追加すること

2. **アカウントファイルの管理**
   - CSVファイルにはパスワードが含まれるため、適切なアクセス制限を設定
   - Gitリポジトリにコミットしない

3. **スクリーンショット**
   - エラー時にスクリーンショットを取得する場合、個人情報が含まれないよう注意
   - パスワード入力画面のスクリーンショットは取らない

### ベストプラクティス

1. **待機時間の調整**
   - ネットワーク状況に応じて `browser_wait_for` の時間を調整
   - ページの読み込みが遅い場合は待機時間を延長

2. **UI変更への対応**
   - AirRegiのUIが更新された場合、セレクタや手順を見直す必要がある
   - 定期的に動作確認を行い、変更があれば Skill を更新

3. **スナップショット活用**
   - 各ステップの前後で `browser_snapshot` を実行し、状態を確認
   - エラー時のデバッグに役立つ

---

## 補足情報

### ダウンロードされるCSVファイルについて

- **ファイル形式**: UTF-8 または Shift-JIS エンコーディングのCSV
- **元ファイル名**: 通常 `会計明細_YYYYMMDD.csv` の形式
- **リネーム後**: `{店舗名}_{YYYYMM}_POS.csv`
- **内容**: 指定した月の全ての会計明細（来店日時、商品、金額、人数など）

### RestaurantAILab Dashboard との連携

ダウンロードしたCSVファイルは、このプロジェクトの Dashboard にアップロードして分析できます：

1. Dashboard の `/store/store-001/upload` にアクセス
2. ダウンロードしたCSVファイルをアップロード
3. 自動的に解析され、ダッシュボードで可視化される

詳細は `docs/運用ガイド/バルクアップロード.md` を参照してください。

---

## トラブルシューティング

### Q1. Playwright MCPが利用できない

**症状**: ツールが実行できない、エラーが発生する

**対処**:
- Playwright MCPが正しくインストールされているか確認
- ブラウザドライバが正しくインストールされているか確認
- 必要に応じて `mcp__playwright__browser_install` を実行

### Q2. ブラウザが起動しない

**症状**: `browser_navigate` でエラーが発生する

**対処**:
- システムにブラウザ（Chrome, Firefox等）がインストールされているか確認
- Playwrightの設定でブラウザが正しく指定されているか確認

### Q3. ダウンロード先が見つからない

**症状**: ファイルがダウンロードされない

**対処**:
- `C:\Users\auk1i\Downloads` ディレクトリが存在するか確認
- ブラウザのダウンロード設定を確認
- 必要に応じてダウンロード先を変更

### Q4. ログアウトボタンが見つからない

**症状**: Step 15 でログアウトできない

**対処**:
- スナップショットで**画面右上**のアカウント領域を確認（左上ではない！）
- AirIDが表示されているlistitemを探す（例: `bar_five_arrows`）
- ドロップダウンが開かない場合は、正しいlistitemをクリックしているか確認
- ログアウトボタンをクリック後、確認ダイアログの「OK」ボタンを忘れずにクリック
- 見つからない場合はブラウザを閉じて次の店舗へ

### Q5. ファイルリネームが失敗する

**症状**: Step 14 でリネームエラー

**対処**:
- ダウンロード先に同名ファイルが既に存在していないか確認
- ファイル名に使用できない文字が店舗名に含まれていないか確認
- リネーム失敗時は元のファイル名で続行

---

## 更新履歴

| 日付 | バージョン | 更新内容 |
|------|-----------|----------|
| 2026-01-03 | 1.0.0 | 初版作成 - AirRegi日別売上CSVダウンロード機能を実装 |
| 2026-01-03 | 1.1.0 | 機能追加 - 複数店舗一括ダウンロード、ログアウト処理、ファイルリネーム |
| 2026-01-03 | 1.1.1 | ログアウト処理の改善 - 画面位置の修正（左上→右上）、確認ダイアログ手順の追加 |

---

## ライセンス

このSkillは Restaurant AI Lab プロジェクトの一部です。

---

## 参考リンク

- [Playwright MCP ドキュメント](https://github.com/anthropics/anthropic-quickstarts/tree/main/mcp-server-playwright)
- [AirRegi 公式サイト](https://airregi.jp/)
- [RestaurantAILab Dashboard - 開発ルール](../../docs/設計書/開発ルール.md)
