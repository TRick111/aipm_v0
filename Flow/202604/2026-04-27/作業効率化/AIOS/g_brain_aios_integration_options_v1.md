# AIOS × G-Brain (garrytan/gbrain) 統合方針 v1

- 作成日: 2026-04-27
- 担当: AIエージェント (BL-0053 4/27 spawn)
- 前提: G-Brain = `garrytan/gbrain`（OSS / MIT / 11.5k ★）で確定濃厚（`g_brain_investigation_v1.md` 参照）
- 関連: BL-0053 (本タスク) / BL-0066 (飯武さん 4/30 第1回) / BL-0054 (共用リポ設計)
- 4/26 ドラフト `g_brain_research.md` §5 案A〜D は **gbrain 実体特定後の構造に置き換え**

---

## 0. エグゼクティブサマリー

**推奨: 案 (E) ハイブリッド = AIOS 維持 + gbrain MCP 並走 + AIOS 取り込み（一部）**

- gbrain は AIOS の **対立軸ではなく自然な発展系**。乗り換えは不要。
- AIOS の弱点（手動 index / 検索貧弱 / entity 構造なし）を gbrain で **補完**。AIOS の強み（日本語ネイティブ / Flow-Stock 二層 / 軽量・依存ゼロ）は **維持**。
- 飯武さん 4/30 第 1 回には **gbrain は含めず AIOS のみ提供**、第 2 回以降で gbrain を「AIOS の発展系」として段階導入が安全。
- 4/30 までに田中さん側で実施するのは **(1) Q1 で確定 / (2) 自分の AIPM ローカルに gbrain init して 30 分体験 / (3) AIOS の RESOLVER 化（軽い）** の 3 点で十分。

---

## 1. 5 つの統合案

### 案 (A) gbrain そのまま採用、AIOS 廃止 — **全乗り換え**

- aipm_v0 の `.cursor/rules/aios/` を捨て、`brain/` を gbrain で初期化
- AIOS の運用ルール（ops 12 本 / 03_daily_task_planning / 12_parallel_orchestration 等）は gbrain skill 形式に書き直す
- Stock/Flow の二層は inbox/ + MECE dir に再配置
- README / Index / log は entity page の Compiled Truth + Timeline に翻訳

### 案 (B) gbrain を MCP サーバで並走、AIOS 維持 — **並列共存**

- aipm_v0 内に `gbrain/` を独立フォルダで設置（`gbrain init`）
- Cursor / Claude Code から **MCP 30 ツール**で gbrain を呼べるようにする
- AIOS の運用ルール / Stock / Flow は **そのまま維持**
- 田中さんが必要に応じて「gbrain で人物検索」「gbrain で関係グラフ traverse」を行う
- AIOS と gbrain は **データを共有しない**（独立 source）

### 案 (C) gbrain のコア概念だけ AIOS に取り込む — **思想輸入**

- gbrain そのものは導入しない
- AIOS のテンプレート / ops に **3 概念だけ** 反映:
  1. **RESOLVER.md**（master decision tree）を `Stock/RESOLVER.md` として追加 → MasterIndex.yaml と併存
  2. **Compiled Truth + Timeline 二層構造**を README / log に明示（`---` 区切り）
  3. **MECE ディレクトリ + 各 dir の README リゾルバ**を Stock 配下で正式化
- 軽量、依存追加なし

### 案 (D) AIOS を gbrain skill 化 して contribute — **upstream 還元**

- AIOS の運用ルール（特に並行タスク運用 / Flow-Stock / 日次・週次・月次レビュー）を **gbrain skill** に翻訳
- garrytan/gbrain に PR を出す or fork として `aipm-tanaka/gbrain` を維持
- 国際 OSS への貢献 → 田中さんの個人ブランディング材料

### 案 (E) ハイブリッド (B + C)  ★推奨★

- **検索 / 自動 enrichment / 関係グラフ** は gbrain MCP に任せる（案 B）
- **運用フレーム（Flow-Stock 二層 / 日次レビュー / parallel orchestration / 日本語語彙）** は AIOS に残す
- AIOS の Stock 配下に **RESOLVER.md / Compiled Truth + Timeline / MECE README** を追加（案 C）
- gbrain は **読み取り専用の "augment"** として扱い、確定書き込みは AIOS Stock 経由
- gbrain の `brain/people/` `brain/companies/` は AIPM の **新規ディレクトリ**として段階導入（既存 Stock を破壊しない）

---

## 2. 比較表

| 軸 | (A) 全乗り換え | (B) MCP 並走 | (C) 思想輸入のみ | (D) skill 化 contribute | **(E) ハイブリッド ★** |
|---|---|---|---|---|---|
| **AIOS 既存資産の保護** | ❌ ほぼ廃棄 | ✅ 完全維持 | ✅ 完全維持 | ✅ 維持 + skill 化 | ✅ 維持 + 強化 |
| **gbrain の機能を活かせるか** | ✅ 100% | ✅ 100% | ❌ 概念のみ | ✅ ただし自分用 fork メンテ | ✅ 95%（書込みは AIOS） |
| **依存スタック増加** | 大（Postgres / bun / OpenAI） | 中（gbrain 単体、独立） | ゼロ | 大 + fork メンテ | 中（独立フォルダ） |
| **学習コスト** | 高 — 全員 gbrain 流に再教育 | 中 — 田中さん + Cursor MCP | 低 — AIOS 既知の延長 | 高 — TS / bun / skill 規約 | **中 — 段階的** |
| **移行コスト** | **大**（Stock 全変換） | **小**（並走） | **小**（README に追記） | **大**（skill 翻訳）| **小→中**（段階） |
| **日本語ネイティブ運用** | ❌（gbrain は英語想定） | ✅ AIOS 側で確保 | ✅ | ❌ skill は英語 | ✅ AIOS 側で確保 |
| **検索能力** | ✅ Hybrid + graph | ✅ Hybrid + graph | ❌ grep | ✅ | ✅ Hybrid + graph |
| **Entity merge / dedupe** | ✅ DB op | ✅ DB op | ❌ 手動 | ✅ | ✅ DB op |
| **会議・メール ingest 自動化** | ✅ skill 完備 | ✅ skill 完備 | ❌ 手動 | ✅ | ✅ |
| **Cron Dream Cycle** | ✅ | ✅ | ❌ | ✅ | ✅ |
| **MCP 30 ツール** | ✅ | ✅ | ❌ | ✅ | ✅ |
| **田中さんの "次の一手" 即実装可** | ❌ 数週間〜 | ✅ 当日 30 分 | ✅ 当日数時間 | ❌ 数日〜 | ✅ 数日 |
| **飯武さん導入 (BL-0066) への影響** | 🔴 致命的（4/30 まで間に合わない） | 🟡 第 2 回以降に | 🟢 第 1 回に間に合う | 🟡 中期計画 | 🟢 **第 1 回 = AIOS のみ / 第 2 回 = gbrain 追加** で段階提供できる |
| **大地さんの関与 (BL-0066)** | 大（実装責任） | 小（採用推薦のみ） | 小 | 大（contribute 推進） | 中（第 2 回以降 Mentor 役） |
| **失敗時のロールバック** | 困難 | 容易（gbrain 削除） | 容易（README 戻し） | 中 | 容易 |
| **Y-Combinator OSS の進化に追随** | ✅ そのまま | ✅ そのまま | ❌ 都度移植が要る | ✅ ただし fork 同期コスト | ✅ そのまま |

---

## 3. 推奨：案 (E) ハイブリッド

### 3.1 なぜ (E) か（4 つの理由）

1. **AIOS が積み上げた半年分の運用知（Flow-Stock / 並行タスク / Cockpit / Tachyon / 日本語語彙）を捨てない**: これらは gbrain の英語 OSS には無い、田中さん固有資産
2. **gbrain の "DB-backed 自動 index + MCP" の力は本物**: ベンチマーク P@5 49.1%, R@5 97.9% は AIOS の grep ベースでは到底届かない。"使える検索" が手に入る
3. **段階導入が安全**: 案 (A) は 4/30 飯武さん導入に間に合わない。案 (B) や (C) 単体では片手落ち。**(E) は最初に (C) → 次に (B)** という 2 段ロケットで進められる
4. **思想が近い OSS なので低摩擦**: gbrain は AIOS と同じ「markdown-first / MECE / resolver / append-only timeline」を採用しているため、aipm_v0 の Stock を **そのまま gbrain に ingest** できる（案 D に発展する余地もある）

### 3.2 段階ロードマップ（提案）

| Phase | 期間（提案） | 内容 | 成果物 |
|---|---|---|---|
| **Phase 0** | 4/27〜4/29 | Q1 確定 / 田中さんが gbrain init で 30 分体験 / Q2 (E) を選定確定 | INBOX 回答 + AIOS implementation_plan.md |
| **Phase 1（軽い、案 C 部分）** | 4/28〜5/3 | AIOS Stock 配下に **`Stock/RESOLVER.md` 追加** / 主要 README に **Compiled Truth + Timeline 二層**を明記 / 各 Program README に **MECE 局所 resolver** を追記 | Stock 直接更新（テンプレも `aios/templates/` に追加） |
| **Phase 2（中、案 B 部分）** | 5/4〜5/15 | aipm_v0 内に `gbrain/` 独立フォルダ。`gbrain init` (PGLite)。既存 Stock の **MasterIndex 配下 README 全件を gbrain ingest**。Cursor / Claude Code に MCP 接続 | `gbrain/` ディレクトリ + MCP 設定 + ingest log |
| **Phase 3（任意、案 D 部分）** | 5/16〜5/31 | AIOS の並行タスク運用 / Flow-Stock を gbrain skill 化（fork or PR）。upstream に検討 | `skills/aipm-flow-stock/` 等の skill |

### 3.3 BL-0066（飯武さん 4/30 第 1 回）への影響

| 観点 | 案 (E) で 4/30 までにすべきこと |
|---|---|
| 第 1 回提供物 | **AIOS のみ**（Phase 1 完了版）。gbrain は触れない or 「次回紹介します」予告だけ |
| 大地さんの役 | 第 1 回：オンザサイドでサポート、第 2 回以降：gbrain 紹介・運用ガイド |
| 飯武さん側準備 | 第 1 回までは Cursor + AIOS（既存）/ 第 2 回前に Node.js + bun + OpenAI API キー準備依頼 |
| リスク | 第 1 回までに **Phase 1 が間に合わない** 場合、AIOS 現状版 + 「将来 gbrain 統合予定」アナウンスで OK（実害なし） |

→ **(E) は BL-0066 を阻害しない**。むしろ第 2 回以降の "厚み" を構造的に確保できる。

### 3.4 リスクとカウンター

| リスク | カウンター |
|---|---|
| gbrain v0.x で破壊的変更が頻発（migrations が v0.5〜v0.14.1 ある） | `skills/migrations/` で agent-executable マイグレが整備されている。**マイナーバージョンを月 1 で追う** 運用 |
| Postgres / pgvector / OpenAI API キーの運用負荷 | PGLite デフォルトでサーバ不要。OpenAI key は田中さんが既に他所で運用 |
| 大地さんの想定する「G-Brain」が gbrain と別物だった | Q1 で確認。違ったら案を組み直す（リスクは Phase 0 で解消） |
| AIOS と gbrain の **二重 source of truth 化** | 「AIOS Stock = canonical / gbrain = augment（読み取り中心、書き込みは Stock 経由）」の **方向性ルール**を Phase 1 で `aios/ops/13_gbrain_integration.mdc` として明文化 |
| 日本語 entity の slug 化（"田中利空" → ?）| canonical slug を日本語ローマ字 + alias として漢字保存（gbrain は alias 機能あり）/ alternative: ASCII slug + アクセス時に表示名解決 |
| 飯武さん側で gbrain 学習負荷 | 第 1 回は AIOS 限定 / 第 2 回以降に段階導入。導入時は `INSTALL_FOR_AGENTS.md` (9 step) を日本語化したオンボーディングを別途作る |

---

## 4. 採用しないが残しておく代替案の評価

### 案 (A) 全乗り換え — **却下**

- **致命傷**: 4/30 飯武さん導入に間に合わない（数週間規模の移行）
- **失う資産**: AIOS の Flow-Stock / 並行タスク運用 / 日本語語彙 / Cockpit Tachyon の連携
- **採用条件**: 田中さんが「もう AIOS は捨てて新規に作り直したい」と明言し、かつ 飯武さん導入を 1 ヶ月延期できる場合のみ

### 案 (B) MCP 並走のみ — **(E) に包含**

- (E) の Phase 2 がこれ。単独で選ぶ理由は無い。**(C) の Phase 1 を先にやる方が即時 ROI が高い**

### 案 (C) 思想輸入のみ — **(E) に包含**

- (E) の Phase 1 がこれ。単独で選んでも軽量で価値はあるが、**gbrain の検索能力を捨てる**のは勿体ない

### 案 (D) skill 化 contribute — **(E) Phase 3 として保留**

- 個人ブランディング材料として優れるが、4/30 飯武さん導入には貢献しない。**Phase 2 完了後の自然な発展**として位置づける

---

## 5. Phase 1（案 C 部分、即着手可能）の具体タスク

> Phase 0 (Q1 確定) が終わり次第、これだけは 4/30 までに完了できる軽量改修。

| # | タスク | 影響範囲 | 工数目安 |
|---|---|---|---|
| 1 | `Stock/RESOLVER.md` 新設（MasterIndex.yaml の人間可読版 + 局所 resolver の決定木） | 新規 1 ファイル | 0.5h |
| 2 | `aios/templates/README.template.md` に **Compiled Truth + Timeline 二層** 構造を追加（`---` 区切り + 上下セクション） | テンプレ 1 ファイル | 0.5h |
| 3 | 既存 Project README（数十件）に二層構造を **段階適用**（変更頻度の高いものから） | Stock 配下 README | 1〜2h（一括スクリプト or AI バッチ） |
| 4 | 各 Program 直下に `<Program>/README.md` の **MECE 局所 resolver** セクション（"このプログラムに含まれる / 含まれない")を追記 | Program README 数件 | 1h |
| 5 | `aios/00_aios_core.mdc` に「**RESOLVER.md を MasterIndex.yaml の前に読む**」という参照導線の追記（任意） | 1 ファイル | 0.3h |
| 6 | `aios/ops/13_gbrain_integration.mdc` 起票（Phase 2 への前提整理 / 二重 source 化禁止ルール） | 新規 1 ファイル | 0.7h |

**合計**: 約 4〜5 時間（AI 並列で実施すれば半日で完了）。Phase 2 (gbrain init) は別工数で 30 分〜数時間。

---

## 6. Phase 2（案 B 部分、5 月以降）の具体タスク

| # | タスク | 工数 |
|---|---|---|
| 1 | aipm_v0 内に `gbrain/` 独立フォルダで `git clone https://github.com/garrytan/gbrain.git gbrain && cd gbrain && bun install && gbrain init`（PGLite） | 30 min |
| 2 | OpenAI API キー設定 + `gbrain doctor --fix` でヘルス確認 | 15 min |
| 3 | `Stock/MasterIndex.yaml` 配下の主要 Project README を `gbrain ingest` でロード（人物 / 会社 / プロジェクト / 概念に分類） | 1〜3 h |
| 4 | Cursor / Claude Code MCP に gbrain サーバ追加（`docs/mcp/DEPLOY.md` 参照） | 30 min |
| 5 | 1 週間試用 → P@5 や使い勝手を判定 | 試用期間 |
| 6 | 良ければ `aios/ops/13_gbrain_integration.mdc` を Phase 2 知見で更新 / 悪ければ撤退 | 1 h |

---

## 7. 判断スケジュール（提案）

| 日付 | アクション |
|---|---|
| 2026-04-27 | INBOX で Q1 確定 / 田中さん本ファイル + 調査 v1 ファイルをレビュー |
| 2026-04-28 | Q2 で (E) 選定確定 / Phase 1 実施 |
| 2026-04-29 | Phase 1 完了 / 飯武さん 4/30 第 1 回提供物（AIOS 版）最終化 / 第 2 回予告メモ作成 |
| 2026-04-30 | 飯武さん第 1 回（AIOS のみ提供） |
| 2026-05-01 以降 | Phase 2 (gbrain init) 着手 |
| 2026-05-中旬 | 飯武さん第 2 回で gbrain 紹介 / 大地さんメンター登場 |
| 2026-05-下旬 | Phase 3 (skill 化 contribute) を判定 |

---

## 8. 田中さんに必要な意思決定（INBOX で確定する 3 点）

1. **Q1**: G-Brain = `garrytan/gbrain` で確定か？（`g_brain_investigation_v1.md` Q1 と同一）
2. **Q2**: 統合方針 案 (E) ハイブリッドで進めるか？
3. **Q3**: 飯武さん第 1 回 (4/30) の提供物は **AIOS のみ** で良いか？

→ INBOX `## BL-0053 G-Brain調査+AIOS統合検討` セクションに 3 件として起票。

---

## 9. 補遺：技術スタック早見表（飯武さん向け説明用素案）

```
[gbrain (Phase 2 以降)]
  ├── ランタイム: bun (Node.js 互換、高速)
  ├── 言語: TypeScript
  ├── DB (デフォルト): PGLite (WASM 上の Postgres、サーバ不要)
  ├── DB (スケール時): Supabase (Managed Postgres + pgvector)
  ├── 検索: tsvector (keyword) + pgvector HNSW (semantic) → RRF fusion
  ├── Embedding: OpenAI Embeddings API (text-embedding-3-small 等)
  ├── Agent 接続: MCP 30 ツール (Claude Code / Cursor / Windsurf)
  └── 自動運用: cron + Minions worker (systemd / Procfile / fly.toml)

[AIOS (継続)]
  ├── ストア: markdown + YAML (git のみ)
  ├── 運用ルール: .cursor/rules/aios/ (mdc)
  ├── 階層: Flow (WIP) / Stock (canonical) / Meetings
  ├── インデックス: MasterIndex.yaml + ProjectIndex.yaml + README
  ├── 言語: 日本語 native
  └── Phase 1 で追加: RESOLVER.md / Compiled Truth + Timeline / MECE README
```

→ 飯武さんへの第 1 回は下段（AIOS）のみ。第 2 回で上段（gbrain）を追加。
