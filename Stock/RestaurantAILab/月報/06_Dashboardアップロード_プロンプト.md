# フェーズ6: Dashboard アップロード（月報）

> HTMLスライド（フェーズ5の成果物）を Dashboard にアップロードし、ブラウザで閲覧可能にする。
> 週報の `06_Dashboardアップロード_プロンプト.md` の対称形（`week` → `month` に置換）。

---

## 入力

| 項目 | 値 |
|------|-----|
| HTMLファイル | `{出力ディレクトリ}/{開始日}_{終了日}_{店名}_月次報告資料.html` |
| 運営会社コード | `{運営会社コード}` |
| 対象月 | `{対象月}` （例: `2026-04`） |

## 運営会社コード → Dashboard ストアコード対応表

| 運営会社コード | 店名 | Dashboard ストアコード |
|--------------|------|----------------------|
| `BFA` | BAR FIVE Arrows | `bfa-001` |
| `BBC` | 別天地　銀座 | `bginza-001` |
| `麻布しき` | 麻布しき 旗の台店 | `shiki-001` |
| `キーポイント` | かめや駅前店 | `kameya-001` |

## 手順

### 1. Dashboard リポジトリに移動

```bash
cd /path/to/RestaurantAILab/Dashboard
```

### 2. アップロードコマンドを実行

```bash
node scripts/upload-monthly-report.mjs \
  --file {HTMLファイルパス} \
  --store {ストアコード} \
  --month {対象月} \
  --title "{店名} 月次営業報告 — {対象月}" \
  --env prod
```

#### 実行例（BFA / 2026-04）

```bash
node scripts/upload-monthly-report.mjs \
  --file ../aipm_v0/Stock/RestaurantAILab/月報/2_output/BFA/2026-04/20260401_20260430_BAR_FIVE_Arrows_月次報告資料.html \
  --store bfa-001 \
  --month 2026-04 \
  --title "BAR FIVE Arrows 月次営業報告 — 2026-04" \
  --env prod
```

### 3. 出力確認

成功時のコンソール出力:

```
✓ Upload successful!
  ID:      <UUID>
  Title:   BAR FIVE Arrows 月次営業報告 — 2026-04
  BlobUrl: https://...
```

### 4. ブラウザで確認

アップロード後、以下のURLで閲覧できることを確認:

```
https://<dashboard-url>/store/{ストアコード}/weekly-reports
```

「週報・月報確認」画面に **`M04` インディゴバッジ** で月報が表示されることを確認する。

直接ビューアにアクセスする場合:

```
https://<dashboard-url>/store/{ストアコード}/monthly-reports/{ID}
```

## オプション

| オプション | 必須 | 説明 | デフォルト |
|-----------|------|------|-----------|
| `--file` | Yes | HTMLファイルパス | — |
| `--store` | Yes | Dashboard ストアコード | — |
| `--month` | Yes | 対象月 (`YYYY-MM`) | — |
| `--title` | Yes | レポートタイトル | — |
| `--env` | No | 環境 (`dev` / `prod`) | `dev` |

- `--month` から月初日・月末日は自動計算される
- 同一店舗・同一月に再アップロードすると既存レポートを上書きする

## エラー時の対応

| エラー | 原因 | 対応 |
|-------|------|------|
| `Login failed` | ADMIN_PASSWORD が未設定 or 不一致 | `.env.production` の `ADMIN_PASSWORD` を確認 |
| `Invalid month format` | `--month` の形式が不正 | `YYYY-MM` 形式で指定（例: `2026-04`） |
| `month は 1-12` | 月の値が範囲外 | 1〜12 で指定 |
| `ENOENT` | HTMLファイルが見つからない | `--file` のパスを確認 |
| `Upload failed` | API側エラー | サーバーログを確認。ストアコードの存在確認 |

## チェックリスト

- [ ] HTMLファイルがフェーズ5で正常に生成されていること
- [ ] ストアコードが対応表と一致していること
- [ ] `--env` が正しい環境を指していること（dev / prod）
- [ ] アップロード成功メッセージが表示されたこと
- [ ] Dashboard の「週報・月報確認」画面に M## バッジで月報が表示されること
