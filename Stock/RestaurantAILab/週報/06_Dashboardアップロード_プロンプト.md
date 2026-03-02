# フェーズ6: Dashboard アップロード

> HTMLスライド（フェーズ5の成果物）を Dashboard にアップロードし、ブラウザで閲覧可能にする。

---

## 入力

| 項目 | 値 |
|------|-----|
| HTMLファイル | `{出力ディレクトリ}/{開始日}_{終了日}_{店名}_週次報告資料.html` |
| 運営会社コード | `{運営会社コード}` |
| 対象週 | `{対象週}` （例: `2026-W07`） |

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
node scripts/upload-weekly-report.mjs \
  --file {HTMLファイルパス} \
  --store {ストアコード} \
  --week {対象週} \
  --title "{店名} 週次営業報告 — {対象週}" \
  --env prod
```

#### 実行例（BBC / 2026-W07）

```bash
node scripts/upload-weekly-report.mjs \
  --file ../aipm_v0/Stock/RestaurantAILab/週報/2_output/BBC/2_output_2026w07/20260209_20260215_別天地_銀座_週次報告資料.html \
  --store bginza-001 \
  --week 2026-W07 \
  --title "別天地　銀座 週次営業報告 — 2026-W07" \
  --env prod
```

### 3. 出力確認

成功時のコンソール出力:

```
✓ Upload successful!
  ID:      <UUID>
  Title:   別天地　銀座 週次営業報告 — 2026-W07
  BlobUrl: https://...
```

### 4. ブラウザで確認

アップロード後、以下のURLで閲覧できることを確認:

```
https://<dashboard-url>/store/{ストアコード}/weekly-reports
```

## オプション

| オプション | 必須 | 説明 | デフォルト |
|-----------|------|------|-----------|
| `--file` | Yes | HTMLファイルパス | — |
| `--store` | Yes | Dashboard ストアコード | — |
| `--week` | Yes | ISO週 (`YYYY-Wnn`) | — |
| `--title` | Yes | レポートタイトル | — |
| `--env` | No | 環境 (`dev` / `prod`) | `dev` |

- `--week` から開始日（月曜）・終了日（日曜）は自動計算される
- 同一店舗・同一週に再アップロードすると既存レポートを上書きする

## エラー時の対応

| エラー | 原因 | 対応 |
|-------|------|------|
| `Login failed` | ADMIN_PASSWORD が未設定 or 不一致 | `.env.production` の `ADMIN_PASSWORD` を確認 |
| `Invalid week format` | `--week` の形式が不正 | `YYYY-Wnn` 形式で指定（例: `2026-W07`） |
| `ENOENT` | HTMLファイルが見つからない | `--file` のパスを確認 |
| `Upload failed` | API側エラー | サーバーログを確認。ストアコードの存在確認 |

## チェックリスト

- [ ] HTMLファイルがフェーズ5で正常に生成されていること
- [ ] ストアコードが対応表と一致していること
- [ ] `--env` が正しい環境を指していること（dev / prod）
- [ ] アップロード成功メッセージが表示されたこと
- [ ] Dashboard のブラウザ画面で週報が閲覧できること
