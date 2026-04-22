# BL-0037 Implementation Plan v2 — PONさんChatGPT履歴整理（AIOS Program化）

最終更新: 2026-04-22 15:30（ユーザー回答 Q1-Q4 反映、AIOS前提にピボット）

## 0. 前提の再確認（Q1-Q4 回答反映）

| # | 項目 | 回答 | 影響 |
|---|---|---|---|
| Q1 | 投入先AIツール | **Cursor + AI-PM (AIOS) システム** / ゴールは Stock の Program+Project 形式 | 出力はChatGPT Project向けファイル群ではなく、**AIOS Program/Project構造** |
| Q2 | 送付方法 | **(3) GitHub private repo + PONさん招待** | 独立リポジトリ or 既存repoへpushが必要 |
| Q3 | 秘匿性 | **(a) マスキング不要** | 原文のまま使える |
| Q4 | 本日スコープ | **(A) Phase1+2+3 全部今日中** | 時間効率優先・Batch APIは並行待機 |

**Phase 1 (Step4 deploy) は完了済み** (2026-04-22 15:30):
- `Stock/バンコクPonさん案件/AIOS提供/ChatGPT移行/` に 478 Markdown + 1 YAML を配置
- これは **田中さん側AIOSに配置された基盤素材**。ここからPONさん向けに再パッケージする

## 1. 改訂方針

### 1.1 出力物の再定義

旧計画（ChatGPT Projects前提）:
- `for_PON/` フォルダに 13 ファイル（persona / themes / decisions_log ほか）

新計画（AIOS Stock前提）:
- **独立した AIOS Program「ChatGPT履歴」**を作り、PONさん側 Stock に drop-in 可能な形で出力
- 横断ナレッジ（persona / themes / decisions_log 等）はProgram直下の「_overview/」配下に配置
- カテゴリは**Project**として構造化（4 Projects）
- サブカテゴリは各Project内のサブディレクトリ

### 1.2 ターゲット構造（AI提案）

```
<PONさんのStock配下に配置する単体Program>
Stock/
└── ChatGPT履歴/                   ← Program (新規)
    ├── README.md                   ← Program README（背景/目的/使い方）
    ├── ProgramIndex.yaml           ← オプション：MasterIndex追加用のスニペット
    │
    ├── _overview/                  ← Program横断ナレッジ（LLM合成）
    │   ├── 00_README.md            ← overview の使い方
    │   ├── 01_PON_persona.md       ← AIに最初に渡すペルソナ
    │   ├── 02_business_overview.md ← 事業全体像
    │   ├── 03_decisions_log.md     ← 決定事項の時系列
    │   ├── 04_open_ideas.md        ← 未実行アイデア集
    │   ├── 05_people_directory.md  ← 登場人物（機械生成）
    │   ├── 06_artifacts_index.md   ← 成果物目次（機械生成）
    │   └── themes/                 ← テーマ別ナレッジ（LLM合成）
    │       ├── 給与制度とスタッフマネジメント.md
    │       ├── プロモーション・マーケティング.md
    │       ├── 商品開発・ブランド戦略.md
    │       ├── 人事評価・採用.md
    │       ├── 競合分析と市場対応.md
    │       ├── 海外展開とJ-Beauty.md
    │       └── 経営指標・財務管理.md
    │
    ├── 美容室/                     ← Project（カテゴリ）
    │   ├── README.md
    │   ├── ProjectIndex.yaml
    │   ├── log.md
    │   ├── 全般/
    │   │   ├── README.md           ← サブカテゴリREADME（Step4生成済み）
    │   │   ├── conversations_summary.md
    │   │   ├── conversations_index.json
    │   │   └── artifacts/          ← 105件
    │   ├── Rapi-rabi/ ...           (以下21サブカテゴリ分)
    ├── 美容専門店/                 ← Project
    ├── 自社ブランド/               ← Project
    └── J-Beauty/                   ← Project
```

- 4 Programs でなく **1 Program × 4 Projects** を推奨: PONさん既存Stockとの名前衝突を避ける（Rapi-rabi 等の Project 名は彼の既存Stockに存在する可能性が高いため、「ChatGPT履歴」配下にネストして隔離）

### 1.3 重要な仕様上のポイント

- **Project の README / ProjectIndex.yaml / log.md は追加で生成が必要**（Step4出力はカテゴリ/サブカテゴリREADMEのみ。AIOS Project レベルのメタファイルは無い）
- `ProgramIndex.yaml` は MasterIndex に統合すべきエントリのスニペット（PONさんが merge）
- PONさんの Stock/ に新規ディレクトリ追加なので、**既存Stockとの衝突なし**で drop-in 可能

## 2. 実行手順

### Phase 1 ✅ (完了)

- Step4 process: 25/25 成功、README生成 OK
- Step4 deploy: `Stock/…/ChatGPT移行/` に 478 MD + 1 YAML 配置

### Phase 2A — AIOS構造への再パッケージング（スクリプト実行、所要30分）

1. `Flow/202604/2026-04-22/バンコクPonさん案件/scripts/repackage_to_program.py` を作成
   - 入力: `Stock/…/ChatGPT移行/` 全件
   - 出力: `Flow/202604/2026-04-22/バンコクPonさん案件/output/ChatGPT履歴/` (ワーク領域)
   - 動作:
     - ルートに `ChatGPT履歴/README.md`（Program README, 新規作成）
     - カテゴリ4つを Project として整形（`README.md`を流用 + `ProjectIndex.yaml`・`log.md`を新規生成）
     - サブカテゴリ以下は既存ファイルをコピー
2. 人物表・成果物目次の機械生成（`06_artifacts_index.md`, `05_people_directory.md`）
   - Step3 の `conversations_index.json` をパースして自動生成

### Phase 2B — LLM合成（Batch API、所要3〜60分＋待機）

3. `scripts/build_overview_batch.py` を作成
   - 11リクエスト（persona/business_overview/decisions_log/open_ideas + themes×7）
   - Sonnet 中心、一部 Opus（persona / business_overview）
4. Batch API に submit、待機
5. 結果を process → `_overview/` 配下に配置

**Phase 2A と 2B は並行実行**（2A は即着手、2B は submit後バッチ待ち）

### Phase 3 — 案内ドキュメント + 送付（所要45〜60分）

6. `ChatGPT履歴/README.md`（Program README）を最終化
   - 使い方（Cursor + AIOS前提の具体シナリオ）
   - MasterIndex への追加方法
   - ディレクトリマップ
7. GitHub private repo 作成（`gh repo create` を使用）
   - repo名候補: `pon-chatgpt-knowledge` / `pon-aios-chatgpt-archive`
   - 初期化は Flow の output/ をそのままコピー
   - PONさんを Collaborator として招待
8. 送付メッセージ文面を作成（田中さんが PON さんへ送る想定）

### Phase 4 — Stock反映（田中さん側 AIOS）

9. MasterIndex/ProjectIndex/log の更新
   - 今回作業のログを `Stock/バンコクPonさん案件/AIOS提供/log.md` に追記
   - ChatGPT移行 プロジェクトを MasterIndex に追加（既存なら files 追記のみ）

## 3. タスク分解

| ID | サブタスク | 状態 | 依存 | ブロッカー |
|---|---|---|---|---|
| S1 | Step4 --process 実行 | ✅ 完了 | - | - |
| S2 | Step4 --deploy 実行 | ✅ 完了 | S1 | - |
| S3 | repackage_to_program.py 作成＋実行 | 未着手 | S2 | - |
| S4 | 人物表・artifacts目次の機械生成 | 未着手 | S3 | - |
| S5 | build_overview_batch.py 作成＋prepare | 未着手 | S3 | - |
| S6 | Batch API submit | 未着手 | S5 | - |
| S7 | Batch 結果 process → _overview/ 配置 | 未着手 | S6 | Batch待機 |
| S8 | Program README 最終化 | 未着手 | S4, S7 | - |
| S9 | GitHub private repo 作成＋push | 未着手 | S8 | **Q5確認**: repo名 |
| S10 | PONさんを Collaborator 招待 | 未着手 | S9 | **Q6確認**: PONさんのGitHubアカウント |
| S11 | 送付メッセージ文面作成 | 未着手 | S10 | - |
| S12 | Stock (田中さん側) log/MasterIndex更新 | 未着手 | S2 | - |

## 4. 確認事項（追加）

Q1-Q4 への回答で大枠固まりましたが、Phase 3 の送付実行時に以下2点が必要:

- **Q5**: GitHub リポジトリ名（推奨: `pon-chatgpt-knowledge` private）
- **Q6**: PONさんのGitHubアカウント（username or email で招待可能）

どちらも最後の送付直前に確認すれば十分なので、先行する S3〜S8 は並行で進められる。

## 5. タイムライン（本日完了想定）

| 時刻目安 | 作業 |
|---|---|
| 15:30 ✅ | Phase 1 完了 |
| 15:30-16:00 | S3 repackage + S4 機械生成 |
| 16:00-16:15 | S5 Batch prepare + S6 submit（非同期で submit 完了） |
| 16:15-17:30 | S6 のバッチ待ち時間に S8 (Program README 骨組み) 並行執筆 |
| 17:30-18:00 | S7 Batch結果受領 + _overview/ 配置 |
| 18:00-18:30 | S8 最終化 + S9 repo作成 + S10 招待 + S11 送付文面 |
| 18:30-19:00 | S12 Stock反映 + 完了報告 |

合計 約3.5時間。Batch待ちが長引けば翌日への持ち越しの可能性あり。

## 6. ゲート

- **ゲート1**: 本 v2 計画書承認 → S3着手（現在のゲート）
- **ゲート2**: S7まで完了 + 生成物の目視確認 → S9 (GitHub push) 着手
- **ゲート3**: S11 送付文面確認 → 送付実行
