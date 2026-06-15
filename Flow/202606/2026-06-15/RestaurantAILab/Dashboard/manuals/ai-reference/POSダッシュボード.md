# POSダッシュボード 詳細仕様（売上分析 + CSVアップロード）

> マスター: `../AI参照用_仕様マニュアル_v1.md`

---

## 1. 機能の役割

POSレジから出力されたCSVを取り込み、月単位で売上・客数・客単価・メニュー構成を分析する機能。

- **入口画面**: `/store/{storeId}/sales-dashboard` （月一覧）
- **本体画面**: `/store/{storeId}/dashboard/{YYYY-MM}` （9タブ）
- **アップロード画面**: `/store/{storeId}/upload`

---

## 2. アクセス権限

| ロール | 閲覧 | アップロード |
|--------|------|------------|
| admin | 全店舗 | 任意店舗 |
| store | 自店舗のみ | 自店舗のみ |
| group | 所属店舗のみ | （API実装上 store ロールのみ自店舗チェック→運用想定外）|

---

## 3. CSVアップロード詳細

### 3.1 対応フォーマット（6種）

`lib/csv/validator.ts` の `detectCSVFormat(headers)` がヘッダー列から自動判定する。判定順序は **以下の順** で先に一致したものを採用:

1. **Dinii orders**: `メニューID` / `メニュー名称` / `主副区別` / `売価(税込)` を全て含む → `dinii`（orders）
2. **Dinii transactions**: `会計ID` / `人数` / `合計` / `修正履歴` を全て含む → `dinii`（transactions）
3. **スマレジ**: `取引ID` / `取引日時` / `販売単価` / `部門名` → `smaregi`
4. **Airレジ**: `取引No` / `会計日` / `会計時間` / `ID` → `airregi`
5. **完全版（ぽっくんPa）**: `H.` で始まる列 AND `D.` で始まる列の両方あり → `full`
6. **ヘッダーのみ（ぽっくんPa）**: `H.` で始まる列のみ → `header-only`
7. **デフォルト（旧 麻布しき）**: 上記いずれにも該当しない → `denormalized`

USENレジは `airregi` フォーマットに準じる（必須列に `D.オーダーステータス` が追加）。

### 3.2 各フォーマットの必須列

| フォーマット | 必須列 | 必須列数 |
|------------|------|---------|
| denormalized | 来店日 / 来店時間 / 合計 / 人数 / 商品点数 / 会計ID / カテゴリー名 / メニュー名 / 価格 / 注文数量 / 曜日 / 売上明細ID | 12 |
| header-only | 来店日 / H.伝票番号 / H.会計時間 / H.伝票金額 / H.人数 | 5 |
| full | H.伝票番号 + D.明細列 + （H.伝票金額 or H.小計のいずれか1つ） | 10+ |
| smaregi | 取引ID / 取引日時 / 取消区分 / 取引明細区分 / 合計 / 客数 / 部門名 / 商品名 / 販売単価 / 数量 / 明細金額 | 11 |
| airregi | 取引No / 会計日 / 会計時間 / ID / 部門 / 単価 / 数量 / 金額 / 客数 / オーダーステータス | 10 |
| dinii (orders) | 会計ID / 営業日 / オーダー日時 / 分類名称 / メニュー名称 / 主副区別 / 売価(税込) / 販売数 | 8 |
| dinii (transactions) | 会計ID / 営業日 / 会計日時 / 人数 / 合計 / 修正履歴 | 6 |

不足時のエラー: `ERR-003`（必須列が見つかりません）

### 3.3 取込時の正規化ルール（特殊な除外条件）

| フォーマット | 除外条件 |
|------------|---------|
| Dinii | `修正履歴` に「会計取り消し」を含む transactions 行を除外 |
| Dinii | `主副区別 = 1`（副商品）の orders 行を除外 |
| Dinii | transactions に対応する会計ID がない orders 行をスキップ |
| スマレジ | `取消区分 = 1` の行を除外 |
| スマレジ | `取引明細区分 = 2`（返品明細）を除外 |
| Airレジ | `D.オーダーステータス` が「取消」「未会計」等の行を除外 |

### 3.4 複数月の自動分割

- CSV内の `来店日` / `会計日` / `営業日` を見て月ごとに自動分割
- 各月ごとに `bulkInsertSalesData` で PostgreSQL へ一括投入
- 同月の既存データは **削除 → 再投入**（実質上書き）

### 3.5 関連API

```
POST /api/upload            multipart/form-data（file, storeId, optionally fileExtra for Dinii）
POST /api/upload/preview    ヘッダー + サンプル数行を返す（列マッピングUI用）
```

### 3.6 列マッピング（汎用フォーマット）

`denormalized` で判定された場合に列マッピングUIが起動。CSVのヘッダーをアプリの内部フィールド（`visitDate`, `accountId`, `totalAmount` 等）へ手動で対応付けられる。

### 3.7 元ファイルの保管

アップロード元のCSVは Vercel Blob に保管され、後から再取込可能（`debug/blobs` で確認可）。

### 3.8 エラーコード

| コード | 用途 |
|--------|------|
| ERR-001 | CSVファイル形式不正 |
| ERR-002 | ファイルサイズ超過（>10MB） |
| ERR-003 | 必須列欠落 |
| ERR-004 | データ形式不正 |
| ERR-005 | 取込失敗 |
| ERR-PREVIEW-001〜003 | プレビュー解析エラー |
| ERR-MAPPING-001 | 列マッピング処理エラー |
| ERR-USEN-STATUS-001 | USENレジ形式で `D.オーダーステータス` 列が無い |

---

## 4. ダッシュボード9タブ

タブ切替: クエリパラメータ `?sheet=home|weekly|menu|product|trends|summary|customer|unitprice|settings`

### 4.1 ホーム（home）

#### 表示

- サマリーカード4種:
  - 総売上 = 会計IDで重複除外した totalAmount の合計
  - 総来店数 = ユニークな会計ID 数
  - 平均客単価 = 総売上 ÷ 総来店数
  - 総客数 = 会計IDで重複除外した customerCount の合計
- 日別推移グラフ（Plotly 折れ線）
- 日別テーブル（日付 / 曜日 / 売上 / 来店数 / 客単価 / 客数）

#### ロジック（lodash使用）

```typescript
const dailyData = _.chain(standardData)
  .groupBy('visitDate')
  .map((rows, date) => {
    const accounts = _.uniqBy(rows, 'accountId');
    return {
      date,
      dayOfWeek: rows[0].dayOfWeek,
      sales: _.sumBy(accounts, 'totalAmount'),
      visits: accounts.length,
      customers: _.sumBy(accounts, 'customerCount'),
      avgSpend: _.sumBy(accounts, 'totalAmount') / accounts.length
    };
  })
  .sortBy('date')
  .value();
```

#### 重複除外

- 売上・客数: `accountId` でグループ化し、最初の行のみ採用
- 来店数: ユニークな accountId 数

### 4.2 曜日・時間帯分析（weekly）

#### 軸・指標

- X軸: 曜日（月〜日）
- Y軸: 時間帯（0〜23時）
- セル値: 売上 / 来店数 / 客単価（指標切替）
- 空白セル: データなし

#### 週フィルター

- 月全体 / 第1〜第6週
- 週の定義: **月曜開始、日曜終了**
- 第1週: データ最初の日を含む週
- 最大6週

#### 週区切りロジック

```typescript
let weekStart = startOfWeek(firstDate, { weekStartsOn: 1 });
for (const date of allDates) {
  if (date >= addDays(weekStart, 7)) {
    weeks.push(currentWeek);
    currentWeek = [];
    weekStart = addDays(weekStart, 7);
  }
  currentWeek.push(date);
}
```

#### カラースケール

- 全週のデータから **15–85パーセンタイル** で正規化（外れ値除外）
- カラーマップ: Blues（青系グラデーション）
- 週選択時も「月全体の正規化値」でカラー → 週間比較可能

```typescript
const allValues = weeks.flatMap(w => w.heatmapData.flatMap(row => row.values));
const sorted = allValues.filter(v => v > 0).sort((a, b) => a - b);
const p15 = sorted[Math.floor(sorted.length * 0.15)];
const p85 = sorted[Math.floor(sorted.length * 0.85)];
```

#### 勤怠データオーバーレイ

勤怠データがアップロードされている場合、各セル右上にスタッフ数（社員・アルバイト内訳）を重ね表示:

```typescript
const staffCount = attendanceData.filter(att => {
  const startHour = parseInt(att.startTime.split(':')[0]);
  const endHour = parseInt(att.endTime.split(':')[0]);
  return startHour <= hour && hour < endHour;
}).length;
```

### 4.3 メニュー分析（menu）／ABC分析

#### 分類ルール

メニュー（商品）を売上累積構成比でランク付け:

- **A**: 0–70%（看板）
- **B**: 70–90%（準主力）
- **C**: 90–100%（裾野）

#### 表示

- カテゴリ別 構成比（円グラフ）
- メニュー別 ABC ランク一覧（テーブル）
- 売上 / 数量 / 構成比 / 累積構成比

### 4.4 商品詳細（product）／クロスセル分析

#### 表示

- **カテゴリ × カテゴリ ヒートマップ**: 同時購入率
- **商品ペア Top 20**: ペア出現率

#### 計算式

```
ペア出現率 = （AとBの両方を含む会計の数）/（Aを含む会計の数）
```

### 4.5 月次推移（trends）

複数月の集計を並べる:
- 売上 / 客数 / 客単価 / 来店数
- 人件費（勤怠データがあれば）

API: `GET /api/trends/monthly?storeId=...`

### 4.6 全体サマリー（summary）

コース・アラカルトを含めた総合サマリー。1ページに各種指標を集約。

### 4.7 客数分析（customer）

客数の詳細分析（人数別、曜日別、時間帯別など）。

### 4.8 客単価分析（unitprice）

客単価の分布、時期ごとの変動。

### 4.9 設定（settings）／客単価除外カテゴリ

- 客単価計算から除外するカテゴリの選択
- 設定は **店舗単位・全期間・全タブに自動反映**
- データ保存: `customSettings.avgSpendExcludeCategories` 等（店舗設定）

---

## 5. 売上ダッシュボード月一覧（`/store/{storeId}/sales-dashboard`）

### 5.1 表示要素

- アップロード済み月のカード一覧（クリックでダッシュボードへ）
- 「売上データをアップロード」ボタン → `/upload`
- 分析機能の説明（ホーム/曜日・時間帯分析/メニュー分析/商品詳細）
- CSVフォーマット説明（denormalized 必須列） + サンプルCSVダウンロードリンク
- 店舗設定パネル:
  - 上限人数（席数）— 席稼働率の計算に使用
  - 人件費設定（社員時給 / アルバイト時給）— 労働コスト分析に使用

### 5.2 関連API

```
GET /api/months?storeId=...     アップロード済み月の一覧
GET /api/data/[month]?storeId=  指定月のダッシュボードデータ
GET / POST /api/settings        店舗設定（席数・時給）
```

---

## 6. 入力データ仕様（StandardSalesData）

CSVから変換された後の内部統一形式:

| フィールド | 型 | 説明 |
|----------|---|------|
| accountId | string | 会計ID |
| visitDate | string (YYYY-MM-DD) | 来店日 |
| visitDateTime | string ISO | 来店日時 |
| exitDateTime | string ISO | 退店/会計日時 |
| dayOfWeek | string | 曜日（月/火/.../日） |
| totalAmount | number | 会計合計（税込） |
| customerCount | number | 来客数 |
| category1 | string | カテゴリ名 |
| menuName | string | メニュー名 |
| price | number | 単価 |
| quantity | number | 数量 |
| itemCount | number | 商品点数 |

---

## 7. パフォーマンス・制約

- ファイルサイズ上限: 10MB（ERR-002）
- 1会計内の明細件数: 制限なし（ただし極端に多い場合は処理時間に影響）
- 月またぎCSV: 内部で月ごとに自動分割
- 文字コード: Shift-JIS / UTF-8 を自動判定（`lib/csv/detectEncoding`）

---

## 8. 既知の注意点

1. **Dinii は必ず2ファイル必須**。片方だけだと取込失敗
2. **取消・返品行は自動除外**。取り込み件数が CSV 行数より少なくなる
3. **同月の再アップロードは上書き**（既存データ削除→新規取込）。誤ってアップしてもやり直し可能
4. **客単価除外カテゴリは全タブに自動反映**。タブごとに切り替え不可
5. **第1週は「データ最初の日を含む週」** という独自定義。月初が週途中の場合に注意
