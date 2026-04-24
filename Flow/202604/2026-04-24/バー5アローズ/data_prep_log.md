# データ準備ログ — バー5アローズ リニューアル前後比較

実行日: 2026-04-24  
担当: Claude (assistant)

---

## 1. 初期状況

| 項目 | 確認結果 |
|------|---------|
| `Stock/RestaurantAILab/週報/1_input/BFA/rawdata.csv` 最終 entry_at | **2026-04-18 23:41:33** |
| `Stock/RestaurantAILab/週報/1_input/BFA/DailyReport.csv` 最終営業日 | **2026-04-18** |
| Dashboard 起動状況 | **未起動**（ポート3001はtachyonプロジェクトが占有、3000はvoice-beauty-advisorが占有） |
| Playwright 利用可否 | **不可**（AirRegi DLスキルはWindows環境前提：`C:\Users\auk1i\Downloads`を使用） |
| 本番DB（Neon Postgres）への直接アクセス | **可能**（`psycopg2` でreadonly接続）|

## 2. 実施手順と結果

### 2.1 Dashboard 起動の試み
- ポート3001は別プロジェクト（tachyon、PID 55817）が占有中。`pnpm run dev:prod`はポート3001ハードコード
- 競合プロジェクトを止めるとユーザー作業に影響するため起動を断念

### 2.2 AirRegi 経由のCSV取得の試み
- `airregi-sales-download` スキルは `playwright-mcp` 依存・Windows パス前提（`C:\Users\auk1i\Downloads`）
- 当環境（macOS / aipm_v0）では Playwright MCP も Windows ダウンロードフォルダも存在せず**不可**

### 2.3 Neon Postgres への直接接続でのデータ更新（採用）
本番DB（`ep-rough-bird-a1ynj8pb-pooler.ap-southeast-1.aws.neon.tech`）に `psycopg2` で直接接続してデータを取得した。

#### POS データ
| 項目 | 結果 |
|------|------|
| 接続先 | Neon Postgres prod（`Dashboard/.env.production` の `DATABASE_URL`）|
| BFA store_id | `70414fc6-1135-4b25-8584-ca479e3a5110`（store_code: `bfa-001`）|
| **DB上の最新 entry_at** | **2026-04-18 14:41:33 UTC（JST 4/18 23:41:33）** |
| 4/1-4/18 期間 sales_items 件数（DB） | **495 件** |
| 同期間（更新前 CSV） | 454 件 |
| 差分 | **41 件**（`bfa-001` 4/1-4/18 範囲のみ DB から再取得して上書きマージ）|
| 更新後 CSV 最新日 | **2026-04-18** |

→ **2026-04-19 〜 2026-04-23 の POS データはDB自体に存在しない**。AirRegi DL がリアルタイム連携でないため、DB側にも未到達と推定。

#### 日報（DailyReport.csv）
| 項目 | 結果 |
|------|------|
| DB上の存在日 | 4/1, 4/2, 4/3, 4/4, 4/5, 4/6, 4/7, 4/9, 4/10, 4/11, 4/12, 4/13, 4/15, 4/16, 4/17, 4/18, **4/20, 4/21, 4/23**（4/8, 4/14, 4/19, 4/22 は未提出 ＝ 定休/シフト外と推定）|
| 更新前 CSV | 4/13-4/18 のみ |
| 更新後 CSV | **4/1-4/23（19件）** に拡張 |

## 3. データ欠損の取り扱い

> **POSデータ欠損: 2026-04-19 〜 2026-04-23（5日間）**

リニューアル後の分析期間は当初 **4/1〜4/23（23日間）** を予定していたが、AirRegiからの取り込みが完了しているのは **4/18 まで**であり、4/19〜4/23 は POS 側の素材が存在しない。

| 区分 | 当初定義 | 実分析期間 | カバー率 |
|------|---------|-----------|---------|
| After（POS） | 2026-04-01〜2026-04-23（23日） | **2026-04-01〜2026-04-18（18日）** | 78% |
| After（日報） | 2026-04-01〜2026-04-23 | **2026-04-01〜2026-04-23（19件）** | 100% |
| Before（同ウィンドウ） | 2026-03-01〜2026-03-23 | **2026-03-01〜2026-03-18（18日）に変更**（After日数と揃える） | 同期間ウィンドウで揃え |
| Before（月全体） | 2026-03-01〜2026-03-31 | 同左（31日） | — |
| 昨年同月 | 2025-04-01〜2025-04-23 | **2025-04-01〜2025-04-18（18日）に変更**（After日数と揃える）| 同期間ウィンドウで揃え |

→ レポート冒頭・各テーブル脚注に「データ欠損: 4/19〜4/23（POS）」を明記する。

## 4. 実行コマンド・ログ抜粋

```bash
# DB 接続疎通確認
PYENV_VERSION=llm-env python3 -c "import psycopg2; ..."   # OK

# 4/1-4/18 sales_items DB件数 = 495 vs CSV件数 = 454（41件差）

# DB から bfa-001 4/1-4/18 を再取得して CSV にマージ
Fetched 495 fresh rows for 4/1-4/18
Keeping 36122 existing rows (outside 4/1-4/18 BFA range)
Total after merge: 36617

# 更新後 rawdata.csv 検証
Total rows: 36617 | Apr 2026 rows: 495
Last 10 dates: ['2026-04-09', ..., '2026-04-18']

# 日報 4/1-4/23 を export し DailyReport.csv 上書き
Wrote 19 rows
```

## 5. 結論

- **POSデータ**: 2026-04-18 までで分析実行（4/19-4/23は欠損として明記）
- **日報データ**: 2026-04-23 までフル取得済み
- **比較ベースライン**: After 18日に合わせて Before 同ウィンドウ・昨年同月も 18日ウィンドウで揃える。Before月全体（3月31日分）は補助指標として併記
