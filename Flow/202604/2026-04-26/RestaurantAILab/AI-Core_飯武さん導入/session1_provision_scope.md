---
bl_id: BL-0066
project: AI-Core_飯武さん導入
date: 2026-04-26
author: agent (claude)
review_state: unreviewed
title: 第1回セッション 提供スコープ整理（2026-04-30 セッション向け）
related_bls:
  - BL-0066
  - BL-0053
  - BL-0054
---

# 第1回セッション 提供スコープ整理

## 0. 目的
2026-04-30（木）の第1回導入支援セッションで、飯武さんに **何を渡し / 何を渡さないか** を確定させるためのドラフト。
4-29（水）までに本ドキュメントを最終化 → 渡す資産（ファイル / リポURL / Notion）を確定する。

前提: AIOS本体は `/Users/rikutanaka/aipm_v0/` 配下で運用中。BL-0053（G-Brain統合）/ BL-0054（共用リポ設計）の決定を取り込みながら確定する。

---

## 1. AIOS の構成要素 とりうる提供パターン

AIOSは以下の3レイヤー構成で成り立っている。第1回でどこまで開示するかを決める。

| レイヤー | 中身 | ファイル/フォルダ | 第1回提供候補 |
|---|---|---|---|
| **A. ルール（cursor rules）** | 常時参照される運用ルール（00_aios_core.mdc）、運用ルート（10_aios_ops_router.mdc）、各種 ops（01〜12） | `.cursor/rules/aios/` | **A-1** ルール一式（ops 含む） / **A-2** core + ops 抜粋（毎日/会議/Stock化など最小） |
| **B. テンプレート** | README / STATUS / log / MasterIndex / ProjectIndex / INBOX / questions_to_user | `.cursor/rules/aios/templates/` | 原則フル提供（Bだけは独立しても価値あり） |
| **C. Index構造（運用骨格）** | Flow/Stock/Meetings の物理レイアウト、MasterIndex.yaml と ProjectIndex.yaml の運用例 | `Flow/`, `Stock/`, `Meetings/` のサンプル構造 | サンプル骨格（空 or ダミー project 1件）を提供 |

### 想定する3つの提供パッケージ案

| 案 | 内容 | 利点 | 欠点 |
|---|---|---|---|
| **案① フルパッケージ** | A-1 + B + C（実 Stock のサニタイズ版含む） | 田中さんの運用が丸ごと見える / 自走しやすい | 情報量が多く第1回で消化しきれない / 機微情報の除去工数大 |
| **案② コアパッケージ（推奨初期案）** | A-2（core + 基礎ops 4本: 02 project_init / 03 daily_task / 05 finalize / 06 meeting_close）+ B フル + C 骨格 | 90分で説明しきれる / 飯武さんが翌日から触れる粒度 | 並行タスク運用（ops 12）など高度機能は別回 |
| **案③ ミニマムパッケージ** | A の 00 core のみ + B（README / log / ProjectIndex のみ）+ C 骨格 | 説明はラクだが、運用感が伝わりづらい | 「単なるフォルダ規約」に見える可能性 |

**ドラフト推奨: 案② コアパッケージ**
- 第1回の90分で「概要 → デモ → 質疑 → 次回ToDo」までを成立させやすい
- BL-0053（G-Brain統合）の決定が出る前に渡せる範囲
- 第2回以降で ops 04（project_work）/ 07（backlog）/ 12（parallel）を順次追加できる

> 田中さんの判断ポイント: BL-0053 と BL-0054 の決定が 4-29 までに出るなら案①へ拡張も可能。

---

## 2. 渡す媒体

| 候補 | 想定 | 4-29 までに必要な準備 |
|---|---|---|
| **GitHub 共用リポ（BL-0054 決定待ち）** | AIOS 一式を `aios-starter` 的に切り出して push、READMEで使い方を説明 | BL-0054 の構成決定（org / private / 招待方法） |
| **Zip スナップショット** | 4-30 セッション当日に手渡し（USB or Drive） | 機微情報サニタイズ |
| **Notion ページ** | テキスト解説中心、ファイル本体は別途 | Notion ワークスペース有無確認（§3） |

第1回は **GitHub or Zip + Notion 解説ページ併用** が現実的。BL-0054 決定が間に合わない場合は Zip + Drive 共有でフォールバック。

---

## 3. 提供 / 非提供の線引き

### 提供する
- AIOS ルール（案②）
- テンプレート一式
- 空の Stock / Flow / Meetings 骨格（ダミー project 1件入り）
- 4-24 議事録（Meetings 形式での渡し方サンプルも兼ねる）
- AIコア PL（営業フロント） https://ai-core-pl.vercel.app/ の URL 共有

### 提供しない（第1回時点）
- 田中さんの実 Stock 内容（クライアント情報、恋愛、生活管理など機微情報）
- BL-0053 検討中の G-Brain 統合中身（決定後に第2回以降で）
- 並行タスク運用（ops 12）の cockpit-task 連携部分

---

## 4. 4-29 までの完了条件（チェックリスト）

- [ ] 本ドキュメント（提供スコープ）を田中さん承認（案②でいくか判断）
- [ ] BL-0054 の決定を取り込む（GitHub or Zip）
- [ ] 提供パッケージ実体作成（案②なら `aios-starter-v0/` を Flow に組み立て）
- [ ] 4-24 議事録を渡せる形に整形（Meetings/2026-04-24_*.md として）
- [ ] 飯武さんの前提環境ヒアリング項目を事前送付（§ session1_outline.md の §3 参照）
- [ ] 当日アジェンダ確定（session1_outline.md §4）

---

## 5. オープンクエスチョン
1. 案①〜③のどれで行くか（推奨: 案②）
2. 提供媒体: GitHub（BL-0054決定）か Zip フォールバックか
3. 4-24 議事録の渡し方（生 or 要約版）
4. AIコア PL を「飯武さんメニュー選択用」として当日見せるか
