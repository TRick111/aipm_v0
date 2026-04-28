# G-Brain 目的調査 v2（4/28 更新版）

- 作成日: 2026-04-28
- 担当: AIエージェント (BL-0053 mini-tachyon spawn)
- v1 からの更新趣旨: **田中さん 4/28 質問への回答**「GBrain はスキルの集合体？ スキルはスクリプトで定式化？」を反映
- 関連: BL-0053 / BL-0066 / BL-0002（GBrain 統合 AICore 検証, 新設）
- 前版: `Flow/202604/2026-04-27/作業効率化/AIOS/g_brain_investigation_v1.md`

---

## v2 で追加・更新した点

| セクション | 変更 |
|---|---|
| §3「GBrain の二層構造」 | **新規追加**: 「スキルの集合体？」への正確な回答（TS コア層 + Markdown スキル層の2層） |
| §4「スキルの中身」 | **新規追加**: スキルが実行スクリプトを含まず、プロンプト + コマンド断片で構成されていることを実物コードで提示 |
| §10「バージョン情報」 | v0.14.1 系 → **v0.22.2**（package.json）/ プラグイン v0.19.0 にアップデート |
| §11「最近の動き」 | **新規追加**: v0.22.2（2026-04-26）で minions worker の memory leak / freeze 対策が入った点を記載 |

v1 で確定済みの内容（リポジトリ特定 / ベンチマーク / 設計思想の近接性 / 統合形態の選択肢）は本書で再掲しているが結論は変わっていない。

---

## 1. リポジトリ特定（v1 から変更なし）

| 項目 | 値 |
|---|---|
| URL | https://github.com/garrytan/gbrain |
| 作者 | Garry Tan（Y Combinator 社長兼CEO） |
| ライセンス | MIT |
| 言語 | TypeScript（Bun ランタイム） |
| 作成 | 2026-04-05 |
| 直近 push | 2026-04-26（極めてアクティブ） |
| 規模 | **11,616 ★ / 1,392 fork** / 15.5 MB |
| バージョン | **v0.22.2**（package.json）/ v0.19.0（OpenClaw plugin manifest） |

> 大地さんが「G-Brain」と呼ぶ対象がこの `garrytan/gbrain` であることは、田中さんとの直接確認（4/27 BL-0053 質問 Q3 回答）で確定済。

---

## 2. 一行で言うと（v1 から変更なし）

**Postgres-native personal knowledge brain with hybrid RAG search.** 会話・会議・メール・ツイート・記事・PDF などをエージェントに食わせると、人物／会社／案件／概念ページが Markdown で勝手に育ち、相互リンクされ、ベクトル＋BM25＋グラフのハイブリッド検索で取り出せる仕組み。

ベンチ: 240ページ rich-prose コーパスで P@5 49.1% / R@5 97.9%、graph 無効版より +31.4pt、ripgrep-BM25 + vector-only RAG にも同程度の差で勝利。

---

## 3. GBrain の二層構造（v2 新規・最重要セクション）

> **田中さん質問A への回答**: 「GBrain はスキルの集合体という理解で合ってる？」
> → **半分合っているが正確ではない。** GBrain は **2 層構造**で、スキルはその一方の層に過ぎない。

| 層 | 中身 | 役割 |
|---|---|---|
| **TS コア層** (`src/`) | `engine`, `search/hybrid`, `embedding`, `mcp/server`, `cli`, `commands/*.ts`（38本以上） | プリミティブの実装。Postgres/PGLite 接続、ベクトル検索、グラフ走査、MCP サーバ、CLI コマンド本体 |
| **Markdown スキル層** (`skills/`) | 25〜29 個の `SKILL.md`（YAML frontmatter + プロンプト + フェーズ手順） | エージェントへの「処方箋」。プリミティブをどう組み合わせて目的を達成するかをエージェントに**読ませる**ためのレシピ |

つまり **GBrain = 検索DB/グラフ/MCP サーバを提供する Bun ランタイム ＋ エージェントが読む手順書集**。スキルだけ移植してもコアが無いと動かない。逆に、コアだけでも CLI から `gbrain query` などの操作はできるが、エージェントを動かすにはスキル層が必須。

### 3.1 ディレクトリ実物

```
gbrain/
├─ src/                          # TS コア層
│  ├─ cli.ts                     # CLI エントリ
│  ├─ commands/                  # 38 本以上の CLI コマンド (TS 実装)
│  │  ├─ import.ts / query.ts / extract.ts / embed.ts
│  │  ├─ graph-query.ts / backlinks.ts / orphans.ts
│  │  ├─ doctor.ts / autopilot.ts / jobs.ts ...
│  ├─ core/                      # engine / search / embedding / operations
│  ├─ mcp/                       # MCP サーバ (server.ts + tool-defs.ts)
│  └─ schema.sql
├─ skills/                       # Markdown スキル層
│  ├─ RESOLVER.md                # ディスパッチャ（トリガー → スキル）
│  ├─ brain-ops/SKILL.md         # 全メッセージで自動発火
│  ├─ query/SKILL.md             # 検索・回答
│  ├─ ingest/ + idea-/media-/meeting-ingestion
│  ├─ enrich/ / maintain/ / signal-detector/ ...
│  └─ _brain-filing-rules.md     # 全スキル共通の規約
├─ recipes/                      # 統合レシピ (email-to-brain.md 等)
├─ docs/                         # 設計・運用ドキュメント
├─ openclaw.plugin.json          # OpenClaw プラグイン manifest
├─ package.json                  # bun ランタイム / 依存
└─ AGENTS.md / CLAUDE.md         # エージェント向け運用書
```

---

## 4. スキルの中身（v2 新規・最重要セクション）

> **田中さん質問A への回答**: 「スキルの中ではスクリプトも使って定式化されている？」
> → **No。スキルは実行可能スクリプトを含まない。すべてプロンプト + コマンド呼び出しの Markdown。**

### 4.1 スキルの実物（meeting-ingestion 抜粋）

```markdown
---
name: meeting-ingestion
version: 1.0.0
description: |
  Ingest meeting transcripts into brain pages with attendee enrichment, entity
  propagation, and timeline merge.
triggers:
  - "meeting transcript"
  - "process this meeting"
tools:
  - search
  - query
  - get_page
  - put_page
  - add_link
  - add_timeline_entry
mutating: true
writes_to:
  - meetings/
  - people/
  - companies/
---

# Meeting Ingestion Skill

## Phases
### Phase 1: Parse the transcript
Extract from the transcript: 出席者・日時・議題・決定・アクション・関連社名

### Phase 3: Attendee enrichment (MANDATORY)
For EACH attendee:
1. `gbrain search "{name}"` — does a people page exist?
2. If NO → create via enrich skill (mandatory, not optional)
3. If YES → update compiled truth with meeting context
4. `gbrain timeline-add <person-slug> <date> "Attended <meeting-title>"`
```

### 4.2 スキルの構成要素

| 要素 | 中身 | 役割 |
|---|---|---|
| **YAML frontmatter** | `name` / `version` / `description` / `triggers` / `tools` / `mutating` / `writes_to` | スキルのメタ情報。RESOLVER.md がトリガー文字列で当該スキルを選定する |
| **Markdown 散文** | `## Contract` / `## Phases` / `## Anti-Patterns` / `## Output Format` / `## Quality Rules` | エージェントが読む判断ロジック。「何を保証するか」「どの順序で何をするか」「やってはいけないこと」 |
| **シェルコマンド断片** | ` ```bash ... ``` ` ブロックに `gbrain search "..."` 等 | エージェントが実行する具体コマンド。実装は TS コア層に存在 |

つまり **スキルは「LLM が読んで実行する手順書」**であり、実行ロジックそのものは TS コア（`src/commands/*.ts`）に集約されている。

### 4.3 これが GBrain の哲学「Thin Harness, Fat Skills」

- **Thin Harness**: ハーネス（コア）は薄く保つ。プリミティブだけ提供
- **Fat Skills**: スキル（判断ロジック）は太く Markdown で外出し
- **理由**: LLM が直接読めて改修できる / プロンプトエンジニアリングがコード変更ではなく Markdown 編集で済む / バージョン管理しやすい

参考: `docs/ethos/THIN_HARNESS_FAT_SKILLS.md` / `docs/ethos/MARKDOWN_SKILLS_AS_RECIPES.md`

---

## 5. アーキテクチャの肝（v1 から変更なし、整理し直し）

1. **Hybrid Search** — vector + BM25 + 自己編成型 knowledge graph の三層
2. **Self-wiring graph** — ページ書き込み時に entity 抽出 → 型付きリンク（`attended` / `works_at` / `invested_in` / `founded` / `advises`）を **LLM コール 0** で生成
3. **Engine 切替** — PGLite（zero-config / 単機）⇄ Postgres+pgvector（Supabase 推奨 / スケール）
4. **Trust boundary** — CLI 経由（trusted）と MCP 経由（untrusted）を `OperationContext.remote` で峻別
5. **Minions worker** — autonomous 実行用ジョブキュー
6. **Cron 21 本** — 夜間に enrich / citation-fixer / maintain / dream / briefing が走り、寝てる間にブレインが賢くなる

---

## 6. スキル一覧（25〜29 個）

| カテゴリ | スキル | 用途 |
|---|---|---|
| 常時発火 | `signal-detector` | 全メッセージで entity 抽出 |
| 常時発火 | `brain-ops` | READ → ENRICH → WRITE ループ（コア） |
| 検索 | `query` | 3層検索 + 引用付き回答 |
| 取り込み | `ingest` / `idea-ingest` / `media-ingest` / `meeting-ingestion` | URL / 動画 / PDF / 議事録 |
| 強化 | `enrich` / `maintain` / `citation-fixer` / `frontmatter-guard` | ページ補強・健全性 |
| 運用 | `briefing` / `daily-task-manager` / `daily-task-prep` | 日々の運用 |
| 自律 | `cron-scheduler` / `minion-orchestrator` / `signal-detector` | 並列・autonomous |
| 拡張 | `skill-creator` / `skillify` / `webhook-transforms` | スキル開発・外部連携 |
| 健全性 | `skillpack-check` / `smoke-test` / `testing` / `soul-audit` | テスト・品質 |
| 雑 | `cross-modal-review` / `data-research` / `repo-architecture` / `reports` / `signal-detector` | その他 |
| セットアップ | `setup` / `migrate` / `publish`（install 時のみ） | 初期セットアップ |

---

## 7. 統合面（AIOS から見たインターフェース）

- **MCP server**（stdio / リモート HTTP 両対応、30+ ツール、operation 自動公開）
- **OpenClaw プラグイン**（`bundle-plugin` family）
- **ライブラリ exports**（`./engine`, `./search/hybrid`, `./embedding`, `./operations` など豊富）
- **CLI**（`gbrain init/import/query/doctor/serve`）
- **GStack 連携**（コード調査エージェント向けの call-graph モード）

---

## 8. ハイブリッド統合 3 案と推奨（v1 から維持）

| 案 | 工数 | 自由度 | リスク | 第一回から可否 |
|---|---|---|---|---|
| **A. MCP として接続**（gbrain serve を AIOS が呼ぶ） | 小 | 中 | 低 | ◎ |
| **B. ライブラリとして取り込み**（`gbrain/engine` 等を import） | 中〜大 | 大 | 中（Bun依存） | △ |
| **C. パターンだけ採用**（思想を真似て自前実装） | 大 | 最大 | 低 | × |

**推奨: A（MCP）から始める**。第一回スコープに収まり、upstream 追随も容易。後から B（ライブラリ統合）に降りる余地を残せる。

> 4/28 の田中さん回答により、第一回（飯武さん向け）の前に **BL-0002（RestaurantAILab で GBrain 統合 AICore を先行検証）** が新設された。検証結果を踏まえて第一回スコープと Phase 1 spawn 判断を行う方針。

---

## 9. 第一回から組み込む上での注意点

1. **ランタイムが Bun**（Node.js ではない）— AIOS 側の前提と擦り合わせ必要
2. **スケール時は Postgres+pgvector 必須** — PGLite は単機限定
3. **API キー** — OpenAI（embeddings）+ Anthropic SDK が同梱
4. **プライバシー規約** — 公開アーティファクトに実名禁止（社内利用なら問題なし）
5. **バージョン乖離** — `package.json` v0.22.2 と OpenClaw 側 v0.19.0 のズレ

---

## 10. バージョン情報（v2 更新点）

- `package.json` version: **v0.22.2**（v1 時点 v0.14.1 系から進行）
- `openclaw.plugin.json` version: v0.19.0
- `skills/manifest.json` conformance_version: 1.0.0
- 直近の更新: 2026-04-26（極めてアクティブ）

---

## 11. 最近の動き（v2 新規）

### v0.22.2（2026-04-26）の主要修正
production で起きていた **minions worker の memory leak / freeze 問題**を解消するパッチ：
- watchdog: RSS が閾値（default 2048 MB）を超えたら worker を self-terminate → supervisor が指数バックオフで respawn
- 60秒周期の RSS チェックタイマー追加（全 concurrency slot が wedged で job 完了が 0 でも検知できる）
- cold-start auth race 対策: `connectEngine()` が transient error を 3 回リトライ（1s/2s/4s）
- autopilot-cycle の `maxWaiting: 1` で queue 暴走を防止

→ **production-ready の段階で安定化が進んでおり、第一回から組み込むのに十分な信頼度**。

---

## 12. 出典 / 参照

- README: https://raw.githubusercontent.com/garrytan/gbrain/master/README.md
- AGENTS.md: https://raw.githubusercontent.com/garrytan/gbrain/master/AGENTS.md
- llms.txt: https://raw.githubusercontent.com/garrytan/gbrain/master/llms.txt
- skills/RESOLVER.md / skills/manifest.json
- src/commands/* / src/mcp/*
- CHANGELOG.md（v0.22.2 セクション）

---

## 13. 次アクション

1. 本 v2 を田中さんレビュー → BL-0002（GBrain 統合 AICore 検証）の準備に活用
2. ユースケースの具体イメージは別成果物 `g_brain_use_cases_v1.md` を参照
3. BL-0002 の検証範囲を decide 後、Phase 1 spawn 判断
