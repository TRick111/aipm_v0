# ホットペッパーグルメ — クチコミ一覧 ダウンロード SOP

最終更新日: 2026-06-29
店舗: 韓国屋台ポックンパ ネネチキン 東岡崎店
対応 Dashboard reportType: `hpg_reviews`（`lib/marketing/reportTypes.ts`）
パーサ実装の正: `lib/marketing/parsers/hpg.ts` の `parseHpgReviews`
既存スクレイパ: `scripts/scrapers/hotpepper/`（HTML 取得 → CSV 化の自動化済み）

> **位置付け**: D-04 クチコミ画面の HPG 側ソース。HTML 取得→CSV 化の自動化は既存だが、**定期実行・月別整理・過去 12 ヶ月遡及取得の手順は未整備**のため本 SOP で整理。

## 1. ログイン URL と必要認証情報

| 項目 | 内容 |
|---|---|
| ログイン URL | https://www.cms.hotpepper.jp/CLN/login/ |
| 認証ページ（直接） | https://www.cms.hotpepper.jp/CLP/ccm010/showReportListAllForAuth |
| 認証方式 | リクルート ID（HPG クライアント管理画面） |
| 2 要素認証 | **2 要素認証 / ワンタイムパスワード導入済**（SMS or メール OTP） |
| ID / PW の保管 | **要 user 確認**。既存スクレイパ運用上、`scripts/scrapers/hotpepper/login_and_save_state.py` で手動ログイン → storageState を保存する想定（CI/cron 自動化ではなくローカル運用） |
| セッション保持期間 | 短時間タイムアウト。storageState の Cookie が失効したら再ログイン |
| アカウントロック | 連続失敗で発生想定 |

## 2. ダウンロード手順（自動 + 月別整理）

クチコミは公式 CSV 出力なし。**HTML スクレイピング** で取得する。既存スクレイパが整備済み。

### 2-A. 既存スクレイパによる自動取得（推奨）

#### 初回セットアップ（1 回だけ）

```bash
# Python 依存
pip3 install --break-system-packages playwright beautifulsoup4 lxml
python3 -m playwright install chromium

# 認証セッション保存
cd Stock/RestaurantAILab/マーケダッシュボード/scripts/scrapers/hotpepper
python3 login_and_save_state.py
# -> Chromium が開く -> 手動で ID/PW + OTP 入力 -> Enter
# -> state/storageState.json が生成される
```

#### 月次定期実行（毎月初）

```bash
cd Stock/RestaurantAILab/マーケダッシュボード/scripts/scrapers/hotpepper
./run_all.sh
# -> fetch_all.py が /CLP/ccm010/showReportListAllForAuth の HTML を raw_html/reviews.html に保存
# -> parsers/parse_reviews.py が output/reviews.csv を生成（1 ページ 20 件）
```

#### 過去 12 ヶ月分のクチコミを取得する場合（**未実装・要拡張**）

既存 `fetch_all.py` は 1 ページ目（最新 20 件）のみ取得する。**過去 12 ヶ月分を取るにはページング対応の拡張が必要**:

1. 1 ページ目を取得
2. パース後の最古投稿日が「12 ヶ月前」より新しければ次ページ（`?PG=2` 相当 ※要 URL 仕様確認）を取得
3. 投稿日が 12 ヶ月超過した時点で停止
4. 取得した全ページの HTML を結合してから `parse_reviews.py` 実行（または各ページの CSV をマージ）

### 2-B. 完全手動の場合（参考）

1. ブラウザで https://www.cms.hotpepper.jp/CLN/login/ にログイン
2. 「クチコミ管理」または直接 https://www.cms.hotpepper.jp/CLP/ccm010/showReportListAllForAuth へ
3. ページネーション（1 ページ 20 件）で過去のクチコミを順次閲覧
4. **画面に CSV エクスポートボタンはない**。ブラウザの保存（Ctrl+S）で HTML を保存 → `parse_reviews.py` で CSV 化

## 3. 期間指定の限界

| 項目 | 仕様 |
|---|---|
| 過去の遡及範囲 | クチコミ管理画面のページネーションで遡れる範囲（**公式に上限明示なし**。一般的には全期間） |
| 1 ページ件数 | **20 件**固定 |
| 1 リクエストあたり最大期間 | 期間指定 UI なし。**投稿日順での全件ページング** |
| 当月途中ダウンロード | 投稿は随時発生のため当月分は変動 |
| 月確定タイミング | 「来店日」UI はなく `投稿日`／`利用シーン`（ランチ/ディナー）で集計（食べログとは非対称） |

## 4. 出力ファイルの仕様

| 項目 | 仕様 |
|---|---|
| 文字コード | **UTF-8（BOM なし）**（パーサ出力時に `encoding="utf-8", newline=""`） |
| 改行 | LF |
| 区切り | カンマ |
| 拡張子 | `.csv` |
| 行粒度 | 1 行 = 1 クチコミ |

### 必須カラム（`parseHpgReviews` が参照）

パーサが必須トークンとして検出: `投稿日`, `総合評価`

`parse_reviews.py` が出力するカラム = Dashboard 側パーサが読むカラム:

```
投稿日, 総合評価, 投稿者, 利用シーン, 最終審査日, 口コミID, 本文先頭
```

- `投稿日`: `YYYY-MM-DD` 形式に正規化済（`parse_reviews.py` の `normalize_date`）
- `総合評価`: float（5.0 / 4.5 等）
- `利用シーン`: `ランチ` / `ディナー`
- `本文先頭`: 100 文字まで（パーサ既定値）

## 5. 12 ヶ月遡及取得の作業見積もり

| 項目 | 見積もり |
|---|---|
| 1 ページ（20 件）の取得 | **約 30 秒**（fetch + parse） |
| 投稿頻度の前提 | ポックンパが月 5〜20 件のクチコミ投稿と仮定すると、12 ヶ月で 60〜240 件 = **3〜12 ページ** |
| 12 ヶ月分の総工数（自動・ページング実装後） | **約 10〜30 分**（OTP 含む初回認証込み。スクレイパ走らせるだけ） |
| 12 ヶ月分の総工数（手動・ページング未実装） | **約 30〜60 分**（各ページ HTML 保存 → 月別 CSV 化のマニュアル繰り返し） |
| 一括取得の可否 | **件数次第で全期間 1 ファイルが現実的**。投稿数が少なければ 12 ヶ月分が 1 〜数ページで完結 |
| 取得方針 | **既存スクレイパでまず 1 ページ取得 → 投稿日範囲を見て必要ページ数を判定 → ページング拡張実装後に全期間取得 → Dashboard 側で投稿月別に集計** |

## 6. ファイル配置先

| 項目 | パス／命名 |
|---|---|
| 配置ディレクトリ（生 CSV） | `Stock/RestaurantAILab/マーケダッシュボード/sample_data/hotpepper/` |
| ファイル命名規則（全期間 1 ファイル） | `ホットペッパー_クチコミ一覧.csv`（既存サンプルと同じ命名） |
| ファイル命名規則（月別アーカイブ） | `ホットペッパー_クチコミ_{YYYY-MM}.csv`（必要なら投稿月で分割） |
| Phase 1 取り込みの推奨 | **全期間 1 ファイル**でアップロードし、Dashboard パーサ側で投稿月別にグループ化（パーサが `byMonth` map を返す実装になっている） |

> **既存スクレイパの出力配置との関係**: `scripts/scrapers/hotpepper/output/reviews.csv` に生成されたものを、sample_data 側にコピーしてリネームする運用。Phase 1.0 では手動コピー、Phase 1.1 で自動化。

## 7. 既知の落とし穴

| # | 内容 | 対処 |
|---|---|---|
| 1 | 「来店日」UI が存在せず、`投稿日` + `利用シーン` のみ | 食べログ（来店月ベース）と非対称な集計になることを UI で明記 |
| 2 | 1 ページ 20 件固定。過去遡及はページングが必要 | ページング対応の拡張が未実装。`PG` 相当のクエリパラメータを実機で確認後、`fetch_all.py` を拡張 |
| 3 | OTP で毎回コード要求の可能性 | `login_and_save_state.py` の手動ログインで OTP 入力 → storageState 保存運用 |
| 4 | セッション短時間タイムアウト | `fetch_all.py` が `noLoginError` / `login` URL を検出したら自動でエラー終了 → 再認証 |
| 5 | 2026/01/29 以降「おすすめレポート」→「口コミ」へ仕様変更 | 過去 12 ヶ月分には旧名称が含まれる可能性。`investigation` 時に注意 |
| 6 | 評価詳細（料理／接客／雰囲気）は一覧画面にない | 総合評価のみで集計 |
| 7 | 投稿の審査タイムラグ（`最終審査日`） | 「直近で審査済みのクチコミ件数」と「投稿日ベースの月次件数」がズレる可能性 |
| 8 | HPG クチコミは食べログクチコミと別ドメインで storageState 別管理 | `scripts/scrapers/hotpepper/state/` を専用 |

## 8. 自動化の見通し

| 項目 | 見通し |
|---|---|
| Playwright 自動化の所要工数 | **追加実装は半日**（既存 1 ページ取得 → N ページ取得に拡張、停止条件「最古投稿日が N ヶ月前を超過」を実装） |
| Selector の安定性 | `<span id="contributionDateN">` / `<input id="reportTextN">` の DOM 構造に依存。**N=0..19 の繰り返しパターンは安定**だが、HPG UI 更新で破綻リスク |
| ログイン状態保持 | `state/storageState.json`。OTP 込みの手動ログイン → storageState 保存運用が既存パターン |
| Phase 1.0 運用 | 既存スクレイパを **月初に 1 回手動実行 → CSV を sample_data に手動コピー**。完全な自動化は Phase 1.1 |
| Phase 1.1 移植 | Cron / GitHub Actions 化 + 失敗時 Slack 通知 + DOM スナップショットテスト |

### 既存スクレイパでの過去 12 ヶ月遡及可否（脚注）

- **現状の制約**: `fetch_all.py` は 1 ページ目（最新 20 件）のみ取得。
- **遡及には拡張必須**: ページングクエリ（`?PG=2` 等の URL 仕様）を実機確認し、`fetch_all.py` にループを追加する必要あり。
- **HPG 側の保持期間**: 公式に明示なし。投稿は通常全期間保持されると推定。
- **代替策**: 過去 12 ヶ月遡及が困難な場合、Phase 1.0 は「現時点で見られるクチコミのみ取得 → 月次運用で差分を蓄積」する設計に倒すのも現実的。
