---
bl_id: BL-0066
project: AI-Core_飯武さん導入
date: 2026-04-26
author: agent (claude)
review_state: unreviewed
title: 第1回セッション 資料章立てドラフト（2026-04-30 90分想定）
related_files:
  - session1_provision_scope.md
related_bls:
  - BL-0066
  - BL-0053
  - BL-0054
---

# 第1回セッション 資料章立てドラフト

## 0. メタ情報
- 対象: 飯武さん（クライアント）
- 日時: 2026-04-30（木）/ 90分想定
- 形式: 対面 or オンライン（要確認）
- 渡す資産: `session1_provision_scope.md` で確定したパッケージ（推奨: 案②）
- 同席者候補: 町田大地さん（G-Brain担当） — 出席可否は別途確認

---

## 1. 提供スコープ（資料 第1章）

**目的**: 「今日渡すもの／渡さないもの」を最初に明示し、第1回のゴールを共有する。

### 1.1 渡す3点
1. AIOS ルール（cursor rules / `.cursor/rules/aios/` — core + 基礎ops 4本）
2. テンプレート一式（README / STATUS / log / MasterIndex / ProjectIndex / INBOX）
3. Flow / Stock / Meetings の骨格＋ダミーproject 1件

### 1.2 今回渡さないもの（第2回以降）
- 並行タスク運用（cockpit-task / ops 12）
- G-Brain 統合（BL-0053 決定後）
- 共用リポ運用ルール（BL-0054 決定後 / 第2回で詳細）

### 1.3 第1回のゴール（合意したい状態）
- 飯武さんが「自分の業務で何を Flow に書き始めるか」を一つ決められる
- 翌週までに最初の Stock 1 件を確定反映する

> 詳細は `session1_provision_scope.md` 参照

---

## 2. AIOS の構成説明（資料 第2章）

**目的**: 「なぜこの構成で運用すると AI が手を最小化できるのか」を理解してもらう。

### 2.1 AIOS の世界観
- ユーザーは原則 **AIとの対話**で Flow / Stock / Meetings を更新
- AI が「どのプロジェクトを参照するか」を Index（YAML）から判断する
- ユーザーは最小入力（箇条書き・URL・メモ）で済む

### 2.2 3つの場所（Flow / Stock / Meetings）
| 場所 | 役割 | 物理パス |
|---|---|---|
| Flow | 作業（WIP） | `Flow/YYYYMM/YYYY-MM-DD/<Project>/` |
| Stock | 確定成果物（正） | `Stock/<Program>/<Project>/` |
| Meetings | 会議の横串保管 | `Meetings/YYYY-MM-DD_<title>.<ext>` |

### 2.3 重要ルール（強制）
- **Stock は直接編集しない**（必ず Flow → Finalize で反映）
- **作業開始時、必ず「今日の Flow / プロジェクト名」フォルダを作る**

### 2.4 ファイル構造（飯武さん側の最小セット）
```
.cursor/rules/aios/
  ├─ 00_aios_core.mdc          ← 常時参照ルール
  ├─ 10_aios_ops_router.mdc    ← ユーザー意図 → ops 振り分け
  ├─ ops/
  │   ├─ 02_project_init.mdc
  │   ├─ 03_daily_task_planning.mdc
  │   ├─ 05_finalize_to_stock.mdc
  │   └─ 06_meeting_close.mdc
  └─ templates/
      ├─ README.template.md
      ├─ STATUS.template.md
      ├─ log.template.md
      ├─ MasterIndex.template.yaml
      ├─ ProjectIndex.template.yaml
      └─ INBOX.template.md
```

### 2.5 運用フロー（最頻出3パターンをデモ）
1. **朝**: 03_daily_task_planning → 今日のFlowに作業フォルダを切る
2. **作業中**: ドラフトはFlowに作成、編集を続ける
3. **確定**: 05_finalize_to_stock → Stock へコピー＋Index/README/log 更新

---

## 3. 飯武さん側の前提環境（資料 第3章 / 兼 事前ヒアリング項目）

**目的**: 当日の手戻りをなくすため、4-29 までにヒアリング送付。

### 3.1 必須確認項目
| # | 確認内容 | 想定値 | 備考 |
|---|---|---|---|
| Q1 | 利用OS | Mac / Windows | コマンド例（cp/Copy-Item）の出し分けに影響 |
| Q2 | エディタ | Cursor 利用有無 / バージョン | cursor rules 適用可否の前提 |
| Q3 | Git 利用経験 | あり / なし | 共用リポ運用（BL-0054）の進め方に影響 |
| Q4 | GitHub アカウント | 有無 / username | 共用リポ招待先 |
| Q5 | Notion 利用 | 有無 / ワークスペース所属 | 解説ページ共有の媒体 |
| Q6 | Drive / iCloud | 利用状況 | Zip フォールバック時の共有先 |
| Q7 | AI 利用経験 | ChatGPT / Claude / Cursor AI 等 | 説明の粒度調整 |
| Q8 | 期待値 | 第1回で何を持ち帰りたいか | アジェンダ微調整 |

### 3.2 推奨セットアップ（第1回までに準備していただきたいもの）
- Cursor インストール（未導入の場合）
- GitHub アカウント（共用リポ運用予定の場合）
- ローカルで `aios-starter-v0/` を展開できるディレクトリ

---

## 4. 当日アジェンダ（資料 第4章 / 90分タイムテーブル）

| 時間 | パート | 内容 | 担当 |
|---|---|---|---|
| 0:00–0:10 | オープニング | 自己紹介 / 第1回ゴール共有 / 提供スコープ（§1）説明 | 田中 |
| 0:10–0:30 | AIOS の世界観 | §2.1〜2.3 を口頭＋スライド | 田中 |
| 0:30–0:55 | デモ（実演） | §2.5 の3パターンを実機デモ（朝→作業→確定） | 田中 |
| 0:55–1:05 | 4-24 議事録を題材にしたデモ | Meetings 保存→README に要点反映の流れを実演 | 田中 |
| 1:05–1:20 | 質疑応答 | §3 の前提環境を踏まえた具体質問への対応 | 双方 |
| 1:20–1:30 | 次回ToDo / クロージング | 飯武さん側の宿題 / 次回日程仮押え / 第2回スコープ予告 | 田中 |

### 4.1 当日持参 / 共有するもの
- AIOS 提供パッケージ（GitHub URL or Zip）
- 4-24 議事録（Meetings 形式）
- 本資料一式（PDF or Notion）
- AIコア PL の URL（必要に応じて）

### 4.2 次回ToDo（仮）
- 飯武さん: 自分の業務から最初の Project 1 件を切る → 1週間運用してみる
- 田中: BL-0053（G-Brain）/ BL-0054（共用リポ）決定の反映 / 第2回スコープ確定

---

## 5. 4-24 議事録の組み込み方
- `Meetings/2026-04-24_<title>.md` として整形して提供
- 当日 §2.5 デモの「会議反映（06_meeting_close）」題材に流用
- 議事録の中で **AI-Core 関連の決定/宿題** が出ていれば、第1回スコープの根拠として §1 に追記する

> ※ 議事録の中身が未到着のため、到着次第 §1〜§4 へ反映予定（BL-0066 STATUS.md のブロッカー解消後）

---

## 6. オープンクエスチョン（田中さん判断要）
1. アジェンダ §0:55–1:05 を「4-24 議事録デモ」に充てるか、別の現業題材にするか
2. 第2回の予告で G-Brain 統合（BL-0053）にどこまで言及するか
3. 飯武さんに事前に渡す「ヒアリングシート」（§3.1）を Notion / メール どちらで送るか
