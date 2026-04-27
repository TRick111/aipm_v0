# G-Brain 目的調査 v1

- 作成日: 2026-04-27
- 担当: AIエージェント (BL-0053 4/27 spawn)
- 田中さん新前提 (4/27): 「G-Brain は **GitHub にあるリポジトリ**。おそらく **長期記憶を保持する仕組み**」
- 関連: BL-0053 (本タスク) / BL-0066 (飯武さん導入の前提整備) / BL-0054 (共用リポ設計)
- 4/26 調査ドラフト (要再確認): `Flow/202604/2026-04-26/AIOS/g_brain_research.md` — 大地さん本人作と仮定して探索したが見つからず Phase 0 止まり

---

## エグゼクティブサマリー

**G-Brain は `garrytan/gbrain`（OSS / 11.5k★）でほぼ確定。** 4/26 ドラフトの「大地さん本人作の私的リポ」前提は誤りで、**Garry Tan（Y Combinator 社長兼CEO）が 2026-04-05 に公開した OSS の Personal Knowledge Brain** だった。

- **目的**: AI エージェントに **長期記憶 (Personal Knowledge Brain)** を持たせるための共通基盤。"Your AI agent is smart but forgetful. GBrain gives it a brain."
- **思想**: **Thin Harness, Fat Skills** — markdown を「procedure を記述するコード」と捉え、agent 用の **fat skills** を markdown で 29 本提供 / harness は ~200 行で薄く保つ
- **データ**: **markdown が source of truth** (`brain/people/`, `companies/`, etc.) + **Postgres / PGLite + pgvector** で hybrid search。**MECE ディレクトリ + RESOLVER.md + 自動 entity 抽出 + typed link**
- **実績**: Garry Tan 本人の OpenClaw / Hermes デプロイで **17,888 ページ / 4,383 人 / 723 社 / 21 cron jobs** を 12 日で構築。BrainBench で P@5 49.1% / R@5 97.9%、ripgrep-BM25 + vector-only RAG を **+31.4 pt** 上回る
- **統合形態**: **MCP 30 ツール** で Claude Code / Cursor / Windsurf から直接呼べる
- **田中さん仮説の検証**: 「**長期記憶を保持する仕組み**」**完全に的中**。AIOS の ファイル + index 思想と **設計思想は近接**（MECE / resolver / markdown-first）、ただし AIOS は手動 index、gbrain は **DB-backed 自動索引 + MCP 公開**

> ※ 大地さんが「G-Brain」と呼んでいる対象が **本当にこの `garrytan/gbrain`** かは、最終的に田中さん→大地さんの 1 行確認が必要（INBOX Q1 参照）。ただし「GitHub にある」「長期記憶」という前提に **完全に一致するリポは GitHub 全体で他に該当なし**（4/26 / 4/27 検索結果）。

---

## 1. リポジトリ特定

### 1.1 一次情報

| 項目 | 値 | ソース |
|---|---|---|
| URL | https://github.com/garrytan/gbrain | gh search repos "gbrain" |
| 名称 | **GBrain** (大地さん呼称: G-Brain) | README.md |
| 作者 | **Garry Tan** (President & CEO, Y Combinator) | README / X 投稿 |
| ライセンス | **MIT** | LICENSE |
| 言語 | TypeScript (bun ランタイム) | package.json / bunfig.toml |
| 作成 | 2026-04-05 | gh api repos |
| 直近 push | 2026-04-26 (本日まで活発) | gh api repos |
| 規模 | 15,550 KB / **11,559 ★ / 1,389 fork / 277 issues** | gh api repos |
| バージョン | v0.14.1 系（CHANGELOG 329 KB） | CHANGELOG.md / migrations |
| ドキュメント | README 41 KB / CLAUDE.md 90 KB / TODOS 39 KB / `llms-full.txt` 294 KB / `llms.txt` 4 KB | リポルート |

### 1.2 4/26 調査との差分

| 項目 | 4/26 ドラフトの推定 | 4/27 確認結果 |
|---|---|---|
| 所有者 | 町田大地さん（私的） | **Garry Tan（公開 OSS）** ✘ |
| 公開状態 | private（GitHub 未公開 or 個人 private） | **public、MIT、11.5k★** |
| 既知のホスト | RestaurantAILab org / 個人 private | **garrytan/gbrain (個人 OSS)** |
| 田中さんの動機 | 大地さん独自資産の取り込み | **大地さんが OSS gbrain の採用を勧めている**（推定） |

**含意**: 4/26 ドラフト §1.4「G の意味」は **Garry の "G"** で確定濃厚（or 単に "Generative" / "Graph"）。命名の謎は解消。

### 1.3 4/26 ドラフトの取り扱い

- §1〜3（「大地さん本人作の私的リポ」前提のセクション）は **要差し替え**。本ファイル §1〜§4 が新版。
- §4〜§5（統合形態の検討、案A〜D）は **構造は流用可能**。ただし「(α)〜(ε) のタクソノミー」は **(ε) 複合 = α + β + γ + δ 全部** が gbrain の実態に近いため、別フレームに置き換え（→ 統合案 v1 ファイル参照）。
- §6 の Q-G1（リポ所在）は **本ファイルで解決**。Q-G2〜G5 も新版で再質問。

---

## 2. 何のための仕組みか（目的・コアコンセプト）

### 2.1 一行で言うと

**「LLM が忘れない。AI エージェントに永続的な脳を与える。」**

> "Your AI agent is smart but forgetful. GBrain gives it a brain." (README 冒頭)

### 2.2 解こうとしている問題

1. **LLM の根本的健忘症**: コンテキスト窓を超えると agent はすべて忘れる。RAG で都度引いても synthesis を毎回やり直す
2. **知識管理は 30 年失敗してきた** — 維持コストが人間に乗るから。「LLM agent はメンテを苦にしない」という前提で **wiki を agent に維持させる** ことで初めて実用化される (Karpathy LLM wiki pattern の拡張)
3. **会議・メール・ツイート・通話・カレンダー・連絡先** の信号は毎日入ってくる。手動で人物 page にまとめるのは破綻する → **enrichment pipeline を自動で走らせる**

### 2.3 三大原則（README / GBRAIN_RECOMMENDED_SCHEMA より）

| # | 原則 | 内容 |
|---|---|---|
| 1 | **Every Piece of Knowledge Has a Primary Home (MECE Directories)** | `people/`, `companies/`, `deals/`, `meetings/`, `projects/`, `concepts/` 等。**1 entity = 1 file**。各 dir に `README.md` リゾルバ。トップに `RESOLVER.md` 決定木。重複を root で禁止 |
| 2 | **Compiled Truth + Timeline (Two-Layer Pages)** | 各 page は `---` で 2 層に分かれる。**上段 = Compiled Truth**（常に最新、書き換え可、要約 + State + Open Threads + See Also）/ **下段 = Timeline**（append-only、reverse-chronological、source 付き event log）。「synthesis を毎回 LLM で再生成しない」 |
| 3 | **Enrichment Fires on Every Signal** | 会議・メール・SNS・コンタクト同期のすべてが entity（人 / 会社）に触れたら **enrich skill が必ず起動**。"discipline ではなく wiring"（ルールでなく配線で強制） |

### 2.4 哲学：Thin Harness, Fat Skills

`docs/ethos/THIN_HARNESS_FAT_SKILLS.md`（Garry Tan 2026 年春の YC 講演ドラフト）に集約:

> The bottleneck is never the model's intelligence. The bottleneck is whether the model understands your schema.

5 つの定義:
1. **Skill File** = markdown で書いた手続き。`/investigate` のように **メソッド呼び出し** として動く（params: TARGET / QUESTION / DATASET）
2. **Harness** = LLM を回すプログラム。~200 行で「読み書き / コンテキスト管理 / 安全性」だけ。**40+ ツール定義の god-tool アンチパターンを避ける**
3. **Resolver** = "task type X が来たら doc Y を先に読む" のルーティング表。`CLAUDE.md` を 20,000 行から 200 行に縮める
4. **Latent vs. Deterministic** = 各ステップを「LLM の判断」か「決定的なコード」に明確に振り分ける（8 人席は LLM、800 人席は SQL）
5. **Diarization** = 50 documents を読み 1 page の **構造化された判断** にする（RAG では出せない）

**重要なのは "skill 1 つ = メソッド呼び出し"**。同じ `/investigate` skill に「Sarah Chen + 210 万 discovery email」と「Pacific Corp + FEC filings」を渡すと別ドメインの調査になる。markdown を **再利用可能なコード** として扱う発想。

---

## 3. 主要機能

### 3.1 ストレージ層（pluggable engine）

```
BrainEngine (interface, src/core/engine.ts)
  ├─ PostgresEngine (v0)        — Supabase + pgvector + tsvector + pg_trgm + 再帰CTE
  └─ PGLiteEngine (v0.7+, デフォルト) — WASM 上の Postgres 17.5、サーバ不要、`gbrain init` 2秒
  -- 将来: DuckDBEngine / TursoEngine 拡張可能
```

- **インターフェース**: `getPage / putPage / searchKeyword / searchVector / addLink / getBacklinks / traverseGraph / addTag / addTimelineEntry / putRawData / createVersion / runMigration` 等
- **slug が ID**: `first-last.md` / `company-name.md`、衝突時は `david-liu-crustdata.md` で disambiguate
- **Embedding は engine の外**（OpenAI 等の外部呼出し、`src/core/embedding.ts`）
- **Hybrid search**: keyword (tsvector + ts_rank) + vector (pgvector HNSW cosine) を **RRF fusion + 4-layer dedup**（hybrid.ts は engine-agnostic）

### 3.2 Index 層（DB プリミティブ4種 + Markdown）

| プリミティブ | 役割 |
|---|---|
| **Entity Registry** | canonical ID + alias + 外部 ID（LinkedIn / X / email）。merge は DB op（page merge ではない） |
| **Event Ledger** | 全 signal が immutable event。timeline section はここから生成 |
| **Fact Store** | claim + provenance（source, confidence, observed_at）。LinkedIn と公式サイトが矛盾したら **2 つの fact が並ぶ**（contradictions become data） |
| **Relationship Graph** | typed edge: `Person→Company (role)`, `Person→Person (co-founded)`, `Company→Deal`。"who do I know who's invested in AI infra?" がグラフ traversal で答えられる |

**markdown の慣習が DB に直接 map**:
- frontmatter → fact store
- `.raw/` (sidecar JSON) → provenance records
- below-the-line timeline → event ledger
- `[[wikilink]]` → relationship graph
- canonical slug → entity ID

### 3.3 クエリ層（30 MCP ツール）

`docs/mcp/DEPLOY.md`。Claude Code / Cursor / Windsurf から直接呼べる:
- `gbrain.search` (hybrid)
- `gbrain.get_page` / `put_page`
- `gbrain.add_timeline_entry`
- `gbrain.get_backlinks` / `traverse_graph`
- `gbrain.enrich_entity`
- ... 計 30 ツール

CLI: `gbrain doctor / orphans / repair-jsonb / upgrade / init / migrate / apply-migrations / build:llms`

### 3.4 自動運用層（"Dream Cycle"）

- **cron-scheduler skill** + **Minions（job worker）**: crontab + watchdog、systemd / Procfile / fly.toml で動く
- **enrich skill**: page write のたびに entity 抽出 → typed link 自動生成（**zero LLM call**）
- **citation-fixer skill**: overnight に引用整合性を直す
- **soul-audit skill**: 整合性監査
- **signal-detector**: 外部信号（メール・会議・X）を取り込む

29 個の skill が `skills/` 配下に markdown で配置（agent 向け recipe）。

### 3.5 セキュリティ境界

`OperationContext.remote = true`（MCP 経由 = 信頼境界外）/ `false`（CLI 直接 = ローカル信頼）の二段。`file_upload` 等の sensitive op は remote 時に filesystem confinement を強化。**プライバシールール**: 公開アーティファクトに本物の人名・社名・ファンド名を含めない（`alice-example`, `acme-example` を使う）。

---

## 4. AIOS との設計思想の対比

### 4.1 共通している設計DNA

| 共通項 | AIOS | gbrain |
|---|---|---|
| **markdown が source of truth** | `Stock/<Program>/<Project>/*.md` | `brain/people/*.md`, `brain/companies/*.md` etc. |
| **MECE ディレクトリ + resolver** | `Stock/MasterIndex.yaml` (Program → Project) + `ProjectIndex.yaml` (Project → file) | `RESOLVER.md` (master decision tree) + `<dir>/README.md` (local resolver) |
| **README が人間向け入口** | `Stock/<Program>/<Project>/README.md` | 各 entity page の Compiled Truth section（上段） |
| **append-only な log** | `log.md` | Timeline section（下段、event ledger backed） |
| **AI 用 index と 人間用 README の分離** | `ProjectIndex.yaml` (AI) ⇔ `README.md` (人) | `RESOLVER.md` (agent) ⇔ Compiled Truth (人) |
| **ops を skill / mdc で外出し** | `.cursor/rules/aios/ops/*.mdc` (12 本) | `skills/*` (29 本 markdown) |
| **作業 = Flow / 確定 = Stock** の二層 | Flow (WIP) / Stock (canonical) | inbox/ (unsorted) / 各 MECE dir (canonical) |

→ **設計思想は驚くほど近い**。AIOS が「人間 + 軽量手動 index」で、gbrain が「人間 + DB 自動 index + agent skill 大群」という **進化スペクトル** の関係。

### 4.2 違うところ（gbrain 強み / AIOS 強み）

| 軸 | AIOS | gbrain |
|---|---|---|
| Index 作成 | **手動**（YAML を AI が編集、田中さんレビュー） | **自動**（page write trigger で entity 抽出、zero LLM call の typed link） |
| Search | **ファイル grep / AI コンテキスト読み込み** | **Hybrid（pgvector + tsvector + RRF fusion + dedup）** |
| 矛盾の取り扱い | README の人間レビューで吸収 | **fact store に複数並列 fact**（contradictions become data） |
| Entity merge | 手動 rename + grep 修正 | DB op（点 ID を統合するだけ） |
| 自動運用 | 無し（ユーザー操作 trigger） | **cron Dream Cycle**（夜間に enrich / citation 修復 / consolidate） |
| Agent との接続 | Cursor rules + CLAUDE.md 参照 | **MCP 30 ツール**（Claude Code / Cursor / Windsurf 直結） |
| 依存スタック | Markdown のみ（git で十分） | TypeScript / bun / Postgres or PGLite / pgvector / OpenAI API key |
| セットアップ時間 | ゼロ（既存ファイル） | **30 分**（init 2 秒 + API キー設定） |
| 言語 | **日本語 native**（運用ルール / README / log） | 英語 native（プライバシー規約まで英語） |
| 規模実績 | aipm_v0（数百〜千ファイル規模） | OpenClaw / Hermes で **17,888 ページ / 4,383 人 / 723 社** |
| ライセンス / 公開状態 | 田中さんの私的リポ | **OSS / MIT / 11.5k ★** |
| 既存利用者の習熟度 | 田中さん本人で完結 | 全世界の OSS コミュニティ + Garry Tan 本人がドッグフード |

### 4.3 田中さん仮説の検証

> 田中さん仮説（4/27）: 「おそらく **長期的な記憶を保持するための仕組み**」

**結論: 仮説は完全に的中。** gbrain は明確に "personal knowledge brain = AI エージェント用長期記憶" を標榜している。さらに踏み込んだ含意:

- 「長期記憶」の **粒度** は **エンティティ単位の wiki page** + **Timeline event ledger** + **Fact store with provenance** + **Relationship graph** の 4 プリミティブ。単なる「会話履歴の保存」ではない
- AIOS が想定してきた長期記憶の範囲（**プロジェクト跨ぎの永続知識** + 会議反映 + Project README）は **gbrain の concept / project / meeting / org page** がほぼ 1:1 で受け持つ
- **足りないのは: 人物 / 会社 / deals の "営業ナレッジ的" 層** — AIOS にはこれが弱い（README の関係者欄止まり）。gbrain はこれを 1 級市民として扱う

---

## 5. AIOS 統合への含意（5 点）

> 詳細は `g_brain_aios_integration_options_v1.md` 参照。本ファイルでは **目的調査の含意** だけ記す。

1. **gbrain は AIOS の "対立" でなく "発展系"**: 思想が近いので、AIOS を捨てて gbrain に乗り換えなくても、**核概念（Compiled Truth + Timeline / RESOLVER / typed link）の取り込み** が低コストで可能
2. **MCP サーバとして並走** が技術的に最も自然（gbrain を install → AIOS は薄く維持 → Claude / Cursor から両方見える）。`gbrain doctor` 系 CLI は AIPM の他プロジェクトでも有用
3. **飯武さん導入（4/30）に gbrain を含めるか**は要判断。"30 分で動く" + "Claude Code 直結" は強いが、**TypeScript / Postgres / pgvector / OpenAI key** を理解してもらう必要があり、**第1回には重い** 可能性が高い
4. **大地さんの役回りが変わる**: 「自分が作ったライブラリを共有」ではなく「**OSS の選定と運用ノウハウを共有**」になる。これは大地さん側の負荷が **下がる** 方向（メンテが Garry Tan）
5. **公開リポなので fork / contribute も可能**: AIPM 固有のニーズ（日本語、Notion 連携、AIOS 流の Flow/Stock）を skill として加える形で **community 還元** もありうる

---

## 6. 田中さんへの確認事項

> INBOX `## BL-0053 G-Brain調査+AIOS統合検討` セクションに同内容を起票（最優先 = Q1）。

### Q1. 【最優先・確定確認】"G-Brain" は `garrytan/gbrain` で合っているか

> 4/27 田中さん前提（GitHub にある / 長期記憶）+ 4/26 / 4/27 検索結果から、`garrytan/gbrain` で確定濃厚。ただし大地さんが別物を「G-Brain」と呼んでいる可能性は残る。

**選択肢**:
- (a) **そう、これで合っている** → 統合案 v1 ファイル §推奨案 を進める
- (b) **違う、別のリポ** → 大地さんから URL 取得してもらう（4/26 ドラフトの Q-G1 に戻る）
- (c) **大地さんに確認するまで分からない** → 大地さんへ 1 行確認（"gbrain って `github.com/garrytan/gbrain` のこと？"）

📌 AI推奨: (a)。理由は (1) 田中さんの「GitHub にある」「長期記憶」の 2 条件を完全充足するリポはこれ以外に該当なし、(2) 11.5k ★ で 4 月時点の "話題の OSS"、(3) Claude Code / Cursor / MCP 連携が AIPM 環境と相性最良。

### Q2. 【方針確定】統合形態の希望（→ 統合案 v1 で詳細）

**選択肢の概要**（詳細は `g_brain_aios_integration_options_v1.md`）:
- (A) **gbrain そのまま採用、AIOS 廃止** — 全乗り換え
- (B) **gbrain を MCP サーバで並走、AIOS 維持** — 検索 / enrichment は gbrain、運用ルールは AIOS
- (C) **gbrain のコア概念だけ AIOS に取り込む** — Compiled Truth + Timeline / RESOLVER 化を AIOS ファイルへ翻訳
- (D) **AIOS を gbrain skill 化 して contribute** — AIPM の運用ルールを gbrain skill として upstream
- (E) **ハイブリッド (B + C)**: 重い検索層は gbrain MCP、運用フレームと日本語語彙は AIOS で正規化

📌 AI推奨: **(E) ハイブリッド**。理由は §5 + 統合案 v1 §推奨案 参照。

### Q3. 【方針確定】飯武さん導入（BL-0066, 4/30）への組込み度合

**選択肢**:
- (a) **第1回から gbrain を含める** — AIOS + gbrain を一緒に提供
- (b) **第1回は AIOS のみ、第2回以降で gbrain 追加**
- (c) **大地さんが直接飯武さんに gbrain を提供** — 田中さんは AIOS のみ担当

📌 AI推奨: **(b)**。理由は (1) gbrain は 30 分セットアップだが OpenAI API key / pgvector の理解が要る、(2) 飯武さん側の Cursor 環境準備状況が不明、(3) 第 1 回は AIOS の Flow/Stock 思想を伝えるだけで満載、(4) 第 2 回以降に gbrain を「AIOS の発展系」として追加する流れが自然。

### Q4. 【任意】大地さんの関与スコープ

- (a) 大地さんが gbrain の社内 expert として **AIPM 内 deploy / メンテ / skill 拡張** を担当
- (b) 大地さんは「採用を勧めた」立場のみで、田中さん中心に運用
- (c) 大地さんに 15 分ヒアリングして方針確定

📌 AI推奨: (c)。「G-Brain」呼称や採用経緯（OpenClaw / Hermes 由来）の大地さん側の意図を 1 度確認した方が後々の運用が滑らか。

### Q5. 【任意】aipm_v0 の Stock/Flow を gbrain に投入するか

- aipm_v0 の既存 markdown（README / log / discovery_notes 等）を **gbrain の people / projects / concepts / programs に ingest** すれば、即時に hybrid search が利く
- 一方、Flow（WIP）は gbrain の inbox/ に当たるため、**確定後 Stock に動く流れ** を gbrain の MECE に翻訳する設計判断が要る

📌 AI推奨: 統合案 (E) を選ぶなら、**まず Stock の MasterIndex 全 Project README を gbrain に ingest** → AIOS の Index と gbrain の自動 index を **平行運用** で慣らす。1 週間後に有用性を判定。

---

## 7. 完了条件 / 次アクション

### 本タスクの完了条件

- [x] G-Brain の **正体（リポ URL / 公開状態 / 作者）** を 1 ページにまとめた
- [x] **目的・コアコンセプト・主要機能・公開状態** を抽出した
- [x] 田中さん仮説「長期記憶の仕組み」を **検証**（一致と判断）
- [x] AIOS との設計思想を **対比表**（共通点 / 差異）にまとめた
- [x] 統合への **含意 5 点** を抽出した
- [x] 確認事項を **Q1〜Q5** として INBOX 起票用に整備した

### 次アクション（推奨）

1. **田中さん→Q1 確認**（"これで合っているか"）→ INBOX で 1 行回答
2. Q1 が (a) で確定したら **統合案 v1（別ファイル）** をレビュー → Q2 で方針 (A〜E) 選定
3. Q3 で飯武さん導入への組込み度合を判定 → BL-0066 implementation_plan.md を起票
4. 必要なら BL-0053 を 2 段階に分割: **Phase 1（AIOS ルール棚卸し + Q2 案 (E) の RESOLVER / Compiled Truth 取り込み）** / **Phase 2（gbrain MCP サーバ install + 既存 Stock の ingest 試行）**

---

## 8. 参照ファイル一覧

### 本日 (2026-04-27) 取得した一次情報

- `gh api repos/garrytan/gbrain` (リポ概要 + 統計)
- https://raw.githubusercontent.com/garrytan/gbrain/master/README.md (41 KB)
- https://raw.githubusercontent.com/garrytan/gbrain/master/AGENTS.md
- https://raw.githubusercontent.com/garrytan/gbrain/master/llms.txt
- https://raw.githubusercontent.com/garrytan/gbrain/master/docs/GBRAIN_RECOMMENDED_SCHEMA.md
- https://raw.githubusercontent.com/garrytan/gbrain/master/docs/ethos/THIN_HARNESS_FAT_SKILLS.md
- https://raw.githubusercontent.com/garrytan/gbrain/master/docs/ENGINES.md
- `gh api repos/garrytan/gbrain/contents/skills` (29 skill フォルダ一覧)
- WebSearch: "G-Brain GitHub repository long-term memory agent" (Agent Wars 記事 / mem0 / MemGPT 周辺確認)

### 4/26 ドラフト（要差し替え対象）

- `Flow/202604/2026-04-26/AIOS/g_brain_research.md`（§1〜§3 を本ファイルに置換）

### AIOS 側

- `.cursor/rules/aios/00_aios_core.mdc`
- `.cursor/rules/aios/ops/12_parallel_task_orchestration.mdc`
- `Stock/作業効率化/AIOS/{README,STATUS,discovery_notes,scope_proposal,ProjectIndex.yaml}`
- `Stock/定型作業/バックログ/Backlog.md`（BL-0053 / BL-0054 / BL-0066）

### 関連 OSS（比較対象として確認）

- mem0ai/mem0（universal memory layer for AI agents）
- letta-ai/letta（旧 MemGPT）
- LangMem（LangChain SDK）
- Flowers-of-Romance/ghost（hippocampus + neocortex inspired）

→ いずれも記憶レイヤーだが、gbrain ほど **markdown-first + MECE + agent skill 大群 + Postgres-native** にコミットしているのは見当たらず、**AIOS 思想との接続が桁違いに容易** な選択肢。
