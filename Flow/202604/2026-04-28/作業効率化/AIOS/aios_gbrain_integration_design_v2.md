# AIOS × G-Brain 統合設計 v2（Brain の正体を踏まえた 5 案 + 推奨）

- 作成日: 2026-04-28
- 担当: AIエージェント (BL-0053 mini-tachyon spawn)
- 関連: BL-0053 / BL-0002（GBrain 統合 AICore 検証）
- 前版: `Flow/202604/2026-04-27/作業効率化/AIOS/g_brain_aios_integration_options_v1.md`（v1: 5 案比較、推奨案 E ハイブリッド）
- v2 で何が変わるか: 田中さんの 4/28 設計問い（Brain と Stock の二重管理懸念、プロジェクト進捗を Brain に寄せられるか）に応えるため、**「ファイル階層実物 + ユーザ体験ストーリー」レベルまで具体化**

---

## 0. まず最初に：田中さんの理解を訂正したい点

> 「G-Brainは人や関係者、会社などのエンティティの関係を保存しておくものであって、プロジェクトやプロダクト、成果物、ドキュメントなどは保存しておかないという理解であってますでしょうか」

**No、これは誤解です。** GBrain の `docs/GBRAIN_RECOMMENDED_SCHEMA.md` を読むと、Brain の標準ディレクトリは以下のように **エンティティ＋ドキュメント＋プロジェクト全部**を含みます：

```
brain/
├─ people/        — 人物
├─ companies/     — 組織
├─ deals/         — 金融取引・案件
├─ meetings/      — 会議記録（フル本文）
├─ projects/      — 実際にビルドされているもの（repo, spec, team あり）  ← !!
├─ ideas/         — 誰もまだビルドしてない可能性
├─ concepts/      — 教えられるフレームワーク・メンタルモデル
├─ writing/       — 散文成果物（エッセイ・哲学・ドラフト）            ← !!
├─ programs/      — 主要な人生ワークストリーム（森、木ではない）        ← !!
├─ org/           — 自分の組織の戦略・運用
├─ civic/         — 政治・政策
├─ media/         — 公開ナラティブ・コンテンツ運用
├─ personal/      — 私的メモ・健康・内省
├─ household/     — 家事運用
├─ hiring/        — 候補者パイプライン
├─ sources/       — 生データ取り込み
├─ prompts/       — 再利用可能な LLM プロンプト
├─ inbox/         — 未分類クイックキャプチャ
└─ archive/       — 廃ページ
```

つまり **GBrain は「エンティティ wiki」ではなく「LLM 維持型の包括的ナレッジベース」**。Karpathy の LLM wiki パターンの拡張版。GBrain 自身の表現:

> "A personal intelligence system where your AI agent builds and maintains an interlinked wiki of **everything you know about your world — people, companies, deals, projects, meetings, ideas — as structured, cross-referenced markdown files**."

### GBrain の disambiguation ルール（公式）

| 区別 | 判定 |
|---|---|
| **Concept vs Idea** | フレームワークとして"教えられる" → concept、"ビルドできる" → idea |
| **Idea vs Project** | 誰かがビルドしてる？ Yes → project、No → idea |
| **Writing vs Concept** | 発展した散文（議論・ナラティブ） → writing、200 語の蒸留 → concept |
| **Writing vs Media** | 成果物そのもの → writing、生産配信インフラ → media |
| **Person vs Company** | 人としての記述 → people、組織として → companies |

つまり Brain には **「プロジェクト進行状態 (`projects/`)」「ドラフト・エッセイ (`writing/`)」「アイデア段階 (`ideas/`)」** が普通に入る。

→ **田中さんの「Brain にプロジェクトが入ると Stock と二重になる」懸念は正当**。設計上ここをどう棲み分けるかが本質。

---

## 1. AIOS と GBrain の概念マッピング

| 概念 | AIOS の場所 | GBrain の場所 | 重複度 | 棲み分けの難しさ |
|---|---|---|---|---|
| 人物の知識 | （なし） | `people/` | なし | 易（Brain 独占） |
| 会社・組織 | （なし） | `companies/` | なし | 易（Brain 独占） |
| 会議録 | （Flow 経由でアドホック） | `meetings/` | 低 | 易（Brain で標準化） |
| アイデア | （なし、INBOX 廃止済） | `ideas/` | なし | 易（Brain 独占） |
| 概念・フレームワーク | （なし、Cursor rules 内） | `concepts/` | 低 | 中（rules 配置と被る） |
| プロジェクトメタ・状態 | `Stock/<cat>/<proj>/STATUS.md` | `projects/<name>.md` | **高** | **難（本論点）** |
| プロジェクト成果物 | `Stock/<cat>/<proj>/*.md` | `projects/<name>.md` 内 or `writing/` | **中** | **難（本論点）** |
| BL（タスク・意思） | `Stock/<cat>/<proj>/backlog/BL-*.yaml` + mini-tachyon | （なし、`daily-task-manager` は別） | 低 | 易（mini-tachyon が canonical） |
| Daily 中間生成物 | `Flow/YYYY-MM-DD/<cat>/<proj>/` | `inbox/` or 都度該当 dir | 中 | 中 |
| 朝晩のループ | `Flow/.../_orchestration/` | `daily-task-prep` / `briefing` skills | 中 | 中（mini-tachyon と機能被り） |
| エッセイ・思考の記録 | （なし） | `writing/` | なし | 易（Brain 独占） |
| 横断的プログラム | （なし） | `programs/` | なし | 易（Brain 独占） |

**重複が深刻なのは 2 箇所**: ①プロジェクトメタ・状態（STATUS.md ⇔ `projects/`）、②プロジェクト成果物（Stock 配下 ⇔ `projects/` 内 or `writing/`）。

---

## 2. 設計思想の整理（AIOS と GBrain の本質）

### AIOS の思想（田中さんの記述から）
- **目的**: 最終成果物を蓄積 → 再利用 → さらなる成果物を作る
- **構造**: Flow（中間生成物）/ Stock（最終成果物）の二層
- **記憶の方法**: Stock を index で辿ることで「擬似長期記憶」を実現
- **特徴**: 成果物中心（artifact-centric）

### GBrain の思想
- **目的**: 「世界について知っていること」全体を生きた wiki として LLM に維持させる
- **構造**: 1 ファイル = 1 エンティティ／概念／プロジェクト／成果物。MECE な primary home + cross-link
- **記憶の方法**: compiled truth（蒸留された結論）+ timeline（生エビデンス）+ typed graph
- **特徴**: 知識中心（knowledge-centric）、subject-as-primary-home

### 両者の違いの本質

|  | AIOS | GBrain |
|---|---|---|
| 1ファイルの単位 | 1 タスクや 1 ドキュメント単位 | **1 エンティティ・概念単位**（People/Project/Concept …） |
| 同じ会議の扱い | Flow に議事録 → 必要なら Stock に | meetings/ にページ（fixed）+ 関係する people/, companies/ も自動更新 |
| 同じ人物への言及 | プロジェクトごとに散在 | people/<name>.md に集約、各 mention から back-link |
| 状態の管理 | STATUS.md frontmatter（手動） | compiled truth（LLM が auto-rewrite） |
| 検索 | Backlog index、grep | hybrid search + graph traversal |
| メンテナンス | 人がやる | LLM が cron で自動 |

→ **GBrain は AIOS の Flow/Stock より一段上の抽象を提供する**（"subject" を一級概念として扱う）。AIOS は時間軸（Flow→Stock）、GBrain は主題軸（people/companies/projects/...）。**直交する分類軸**なので組み合わせ可能。

---

## 3. 統合 5 案の比較

| 案 | Stock の扱い | Brain の役割 | 移行コスト | 二重管理リスク | 既存 mini-tachyon への影響 |
|---|---|---|---|---|---|
| **A. 完全統合** | 廃止 → Brain に吸収 | すべて | 大 | なし | 大（Stock 前提コード総替え） |
| **B. Entity-only Brain**（田中さん仮説） | 維持 | 人・会社・概念・会議のみ | 小 | 低 | 小 |
| **C. 役割分担ハイブリッド** ★推奨★ | 維持・**役割を絞る** | 横断知識＋プロジェクト状態 | 中 | 低（明示棲み分け） | 中 |
| **D. 読取りインデックス層** | 維持 | Stock を `gbrain import` で読み込み・検索のみ | 小 | なし（Stock canonical） | 小 |
| **E. 段階的移行** | 維持 → 縮退 | 段階的に拡大 | 段階別 | 段階別 | 段階別 |

### 案A: 完全統合（Stock 廃止 → 全て Brain）

**思想:** AIOS の Flow/Stock 二層を捨て、Brain のディレクトリ階層を AIOS の knowledge layer にする。Stock の `STATUS.md` は brain `projects/<name>.md` に、Stock の deliverable は brain `writing/` or `projects/<name>/.raw/` に移行。

**ファイル階層イメージ:**
```
~/aipm_v0/
├─ Brain/                          # GBrain 標準
│  ├─ people/
│  ├─ companies/
│  ├─ projects/                    # AIOS 旧 Stock の役割
│  │  ├─ aios.md                   # 旧 STATUS.md, 自動更新
│  │  ├─ aios/                     # フォルダ形式: 同名ディレクトリで子ページ
│  │  │  ├─ design-2026-04.md
│  │  │  └─ .raw/
│  │  └─ jbeauty-signage.md
│  ├─ writing/
│  ├─ meetings/
│  └─ ...
├─ Flow/                           # 維持（中間生成物）
│  └─ 202604/2026-04-28/
└─ （Stock は廃止）
```

**ユーザ体験:**
- 「BL-0053 の最新状態は？」→ `gbrain query "AIOS project status"` → `projects/aios.md` の compiled truth が返る
- 「J-Beauty Signage の design doc 読みたい」→ `gbrain get projects/jbeauty-signage` の See Also に link
- mini-tachyon UI は brain に対して読み取り

**Pros:** 単一 source of truth、自己編成 graph フル活用、cron で自動更新
**Cons:** **mini-tachyon の Stock 前提を全替え**。Backlog.md / per-project YAML / deliverables.yaml の置き場所を再設計。移行作業が極めて大きい。

---

### 案B: Entity-only Brain（田中さんの当初仮説）

**思想:** Brain には人・会社・概念・会議だけ置く。プロジェクト・成果物・状態は Stock に残す。

**ファイル階層イメージ:**
```
~/aipm_v0/
├─ Brain/
│  ├─ people/
│  ├─ companies/
│  ├─ concepts/
│  ├─ meetings/
│  └─ inbox/
├─ Stock/                          # 維持
│  └─ 作業効率化/AIOS/
│     ├─ STATUS.md
│     ├─ design-2026-04.md
│     └─ backlog/BL-0053.yaml
└─ Flow/
```

**ユーザ体験:**
- 「飯武さんって誰だっけ」→ `gbrain query "iitake"` → `people/iitake-*.md` から人物概要
- 「AIOS プロジェクトの状態」→ Stock STATUS.md を mt CLI / mini-tachyon で確認
- Brain の people page から Stock の deliverable へは `[See: /Stock/作業効率化/AIOS/design.md]` で link

**Pros:** 既存 AIOS 構造をほぼ維持。すぐ始められる。
**Cons:** **GBrain の `projects/`/`writing/`/`programs/` を捨てることになる**。Brain 機能の半分（プロジェクト・成果物の auto-enrichment）を諦める。「成果物に LLM が触れてない」状態になり、cron による自動 enrich の恩恵を Stock 側で受けられない。

→ **GBrain の真価を引き出さない案**。お試しには良い。

---

### 案C: 役割分担ハイブリッド ★推奨★

**思想:** Brain と Stock を**役割で明確に分ける**：
- **Stock** = 「外に出せる完成物」専用（顧客提案、納品ドキュメント、公開仕様、外部共有可能な成果物）。mini-tachyon の deliverable 管理基盤として継続
- **Brain** = 「組織内部の生きた知識」全般（人物・会社・プロジェクト状態・概念・会議・ドラフト・アイデア）
- **Flow** = 中間生成物（現状維持）
- **mini-tachyon** = タスク・意思の追跡（BL canonical）

**重要な棲み分けルール:**

| 種類 | 例 | 場所 |
|---|---|---|
| 顧客に提出する成果物 | 提案書、技術仕様書（外部公開用） | Stock |
| 公開発表資料 | スライド、ホワイトペーパー | Stock |
| プロジェクトの**現在状態**（要約・次アクション・関係者） | STATUS 相当 | **Brain `projects/<name>.md`** |
| プロジェクトの**構想・思想・調査** | 設計議論、調査レポート、思想文書 | **Brain `writing/`** または `projects/<name>/` |
| 個別の人物・会社の知識 | 飯武さん、大地さん、客先 | **Brain `people/`/`companies/`** |
| 会議録 | 議事録、文字起こし | **Brain `meetings/`** + Flow に raw |
| 内部アイデア（着手前） | 思いつき | **Brain `ideas/`** |
| 既に着手中のプロジェクト | AIOS / J-Beauty Signage | **Brain `projects/`**（メタ）+ Stock（成果物） |
| BL（意思・タスク） | BL-0053 | **mini-tachyon canonical**（Stock YAML） |
| Daily Loop | 朝のタスク案・夜の振り返り | **Flow + mini-tachyon** |

**ファイル階層イメージ:**
```
~/aipm_v0/
├─ Brain/                                       # 新設
│  ├─ RESOLVER.md                               # GBrain 標準
│  ├─ people/
│  │  ├─ iitake.md                              # 飯武さん
│  │  ├─ ohchi.md                               # 大地さん
│  │  ├─ tanaka.md                              # 田中さん本人
│  │  └─ .raw/
│  ├─ companies/
│  │  ├─ restaurant-ai-lab.md
│  │  └─ jbeauty.md
│  ├─ projects/                                 # 状態 + メタ
│  │  ├─ aios.md                                # ★ STATUS.md の役割
│  │  ├─ jbeauty-signage.md
│  │  └─ ai-core-iitake.md
│  ├─ concepts/
│  │  ├─ flow-stock-philosophy.md               # AIOS 思想を概念化
│  │  ├─ thin-harness-fat-skills.md             # GBrain 思想を概念化
│  │  └─ mini-tachyon-protocol.md
│  ├─ meetings/
│  │  ├─ 2026-04-28-iitake-1on1.md
│  │  └─ 2026-04-30-jbeauty-kickoff.md
│  ├─ writing/                                  # 内部考察ドラフト
│  │  └─ 2026-04-28-aios-vs-gbrain-philosophy.md
│  ├─ ideas/                                    # 着手前
│  │  └─ programmatic-bl-from-meetings.md
│  ├─ programs/                                 # 横断ワークストリーム
│  │  └─ aios-platform.md                       # AIOS 全体（projects/ 跨ぎ）
│  └─ inbox/
│
├─ Stock/                                       # 維持・役割を「外部公開可能な成果物」に絞る
│  └─ 作業効率化/
│     └─ AIOS/
│        ├─ README.md                           # 簡略化（詳細は Brain projects/aios.md）
│        ├─ backlog/
│        │  └─ BL-0053.yaml                     # mini-tachyon canonical
│        └─ deliverables/
│           ├─ aios-spec-v1.md                  # 外部公開可能版
│           └─ aios-onboarding-guide.md
│
├─ Flow/                                        # 現状維持
│  └─ 202604/2026-04-28/作業効率化/AIOS/
│     ├─ deliverables.yaml                      # 中間 deliverable
│     ├─ g_brain_investigation_v2.md
│     └─ g_brain_use_cases_v1.md
│
└─ ~/.agi-tools/mini-tachyon/                   # 現状維持
```

**ユーザ体験ストーリー（典型 1 日）:**

```
[朝 8:00] 田中さんが iPhone で「☀️ 今日を始める」
   ↓
mini-tachyon が朝のエージェントを spawn
   ↓
Agent: gbrain query "today's meetings + active projects"
   → meetings/ から今日の予定、projects/ から active なもの、
     people/ から今日会う人の最新コンテキストを取得
   → Flow/<today>/_orchestration/今日のタスク案.md を生成
   → mt deliverable update-state ... unreviewed

[朝 9:00] 田中さん「今日の AIOS 状況」
   ↓
mini-tachyon UI で gbrain の projects/aios.md compiled truth + 
mt projects list の BL 一覧を併記表示

[10:00 飯武さんとの 1on1 開始]
   会議録は Zoom 文字起こしで Flow/.../meetings/ に保存
   ↓
Agent: gbrain meeting-ingestion を発火
   → Brain meetings/2026-04-28-iitake-1on1.md 生成
   → Brain people/iitake.md timeline に「Attended ...」追加
   → Brain projects/ai-core-iitake.md timeline に進捗追記
   → meetings ↔ people ↔ projects に typed link 自動生成

[午後] 田中さんが調査レポート（design-doc-v3.md）を執筆
   → 中間版は Flow に置く
   → 公開可能版は Stock/作業効率化/AIOS/deliverables/ へ移動
   → 内部設計議論ドキュメントは Brain writing/ へ
   → どちらに移すかは内容次第（公開？非公開？）

[夜 22:00] 田中さん「🌙 今日を締める」
   ↓
mini-tachyon の夜のエージェント:
   - mt CLI で BL 状態整理
   - gbrain で projects/aios.md compiled truth 更新
   - 振り返り Flow に保存
   ↓
[就寝中の cron]
   - gbrain enrich: people/iitake.md / companies/jbeauty.md を web 検索で補強
   - gbrain citation-fixer: 全ページの citation を整える
   - gbrain dream: 既存ページから新しい関連性を発見
   ↓
[翌朝] Brain が昨夜より賢くなっている
```

**Pros:**
- 既存 AIOS 構造を**最小変更**で活かしつつ、Brain の自己編成・cron 自動化の恩恵を最大化
- 「外向き／内向き」「成果物／知識」の境界が明確 → 二重管理が起きにくい
- mini-tachyon は BL/Daily Loop に集中、Brain は知識に集中 → 役割が綺麗
- STATUS.md を `projects/<name>.md` に寄せることで「進行度合いを LLM が auto-update」が実現

**Cons:**
- mini-tachyon UI に Brain 連携のフックが必要（projects/ 読取り、meetings/ 表示）
- 棲み分けルールを田中さんが運用上覚えておく必要（最初は迷う）
- BL と Brain projects/ の link を mt CLI で扱える必要

---

### 案D: 読取りインデックス層のみ

**思想:** Stock は一切触らない。Brain は Stock を `gbrain import` で取り込み、検索とグラフ走査だけ提供する。

**ファイル階層イメージ:**
```
~/aipm_v0/
├─ Stock/                      # 完全に現状維持・canonical
├─ Flow/                       # 現状維持
└─ ~/.gbrain/                  # Brain は別管理 (Postgres index のみ)
```

**ユーザ体験:**
- 田中さんは普通に Stock を編集
- 必要に応じて `gbrain import ~/aipm_v0/Stock` でインデックス更新
- 検索だけ `gbrain query "..."` で利用
- people/, companies/ などの auto-enrich は使えない（書き込みなし）

**Pros:** リスクほぼ 0、すぐ試せる。失敗しても Stock は無傷
**Cons:** Brain の自己編成・enrich・cron をほぼ全部諦める。検索エンジンとしてしか使えない（それでも価値はある）

→ **PoC・第一回検証（BL-0002）の最初のステップとしては最適**。本番では C か A に進化させる前提。

---

### 案E: 段階的移行（D → C → A）

**Phase 1**（BL-0002 で実施 / 1 週間）: 案D 試行
- Stock を `gbrain import` で読み込み
- 検索・graph-query が AIPM の現実データで動くか検証
- mini-tachyon UI からの query 接続を試す

**Phase 2**（飯武さん第一回 or 直後 / 1 ヶ月）: 案C 移行
- Brain の `people/`/`companies/`/`meetings/` を新設
- `projects/<name>.md` に STATUS.md を移行
- Stock を「外部公開成果物」に役割を絞る
- 棲み分けルールを `aios/ops/14_brain_filing_rules.mdc` として明文化

**Phase 3**（数ヶ月後 / 任意）: 案A 検討
- Stock を完全に Brain `projects/<name>/` 配下に吸収できるか再評価
- mini-tachyon が Brain 一本で動くようリファクタ

**Pros:** リスク最小、各 Phase で撤退可能
**Cons:** 移行が長期化、各段階で意思決定が必要

---

## 4. 比較表（最終）

| 観点 | A 完全統合 | B Entity-only | **C 役割分担** | D Index層 | E 段階的 |
|---|---|---|---|---|---|
| Brain 機能を活かす度合 | 100% | 30% | **80%** | 40% | 段階的 |
| 既存 AIOS への侵襲 | 大 | 小 | **中** | 極小 | 段階的 |
| 二重管理リスク | なし | 中 | **低** | なし | 低 |
| mini-tachyon 改修 | 大 | 小 | **中** | 極小 | 段階的 |
| 田中さんの認知負荷 | 中（GBrain 流儀のみ） | 中（既存どおり） | **中（境界ルール覚える）** | 小 | 段階的 |
| 第一回（飯武さん）に間に合うか | × | ○ | △ | ○ | ○（Phase 1 のみ） |
| 検証コスト | 大 | 小 | 中 | **小** | 小（Phase 1） |
| 完成度の上限 | 高 | 中 | **高** | 中 | 高 |
| **総合** | △ | △ | **◎** | ○ | **◎** |

---

## 5. 推奨：**案E（段階的）で Phase 1=D → Phase 2=C へ進む**

### 理由
1. **BL-0002（GBrain 統合 AICore 検証）は案D で始めるのが最も安全**。Stock 無傷、リスク 0。Brain の検索・graph-query が実データで動く確証を得る
2. 検証結果が良ければ案C に進む。**案C は AIOS の思想（Flow/Stock）を壊さず、GBrain の真価（自己編成・cron 自動化・graph）も最大化**
3. 案A への進化は将来オプション。AIPM が組織導入された後に判断

### 第一回（飯武さん 4/30 or 直後）への組込み判断

| シナリオ | 推奨 |
|---|---|
| 第一回までに BL-0002 で案D 検証完了 | 第一回は AIOS のみ（v1 推奨どおり）+ 第二回で案C 開始 |
| BL-0002 検証で案D が衝撃的に良い | 第一回でデモとして案D の検索を見せる（書き込みは AIOS のみ） |
| BL-0002 検証で問題発覚 | 第一回は AIOS のみ、Brain は当面延期 |

---

## 6. 案C の運用ルール詳細（推奨採用時のルールブック）

### 6.1 ファイリング決定木（毎回これを参照）

```
新しい情報を保存したい
  ↓
Q1. 外部の人に渡す可能性ある？
   YES → Stock/<cat>/<proj>/deliverables/ + mt deliverable で登録
   NO  → ↓

Q2. 主題は何か？
   人物 → Brain/people/<slug>.md
   会社 → Brain/companies/<slug>.md
   会議 → Brain/meetings/<date>-<topic>.md
   プロジェクトの「状態」「次アクション」「関係者リスト」→ Brain/projects/<slug>.md
   プロジェクトの「構想・調査・思想」→ Brain/writing/<date>-<topic>.md
   着手前のアイデア → Brain/ideas/<slug>.md
   再利用可能な思考フレームワーク → Brain/concepts/<slug>.md
   横断ワークストリーム（複数 project に跨る） → Brain/programs/<slug>.md
   
Q3. BL（意思・タスク）として追跡する？
   YES → mt bl create で mini-tachyon に登録（Brain には登録しない）
   NO  → 主題ディレクトリに保存
```

### 6.2 BL と Brain の link

- BL.yaml の `deliverable_refs` は引き続き mini-tachyon canonical
- Brain `projects/<name>.md` の See Also に `mt bl list --project <name>` で得られる BL 一覧を記載
- BL 完了時に Brain projects/ timeline に追記（mt CLI から hook できると理想だが当面手動 or AI agent 経由）

### 6.3 mini-tachyon UI 拡張案

- `BL-0053 詳細画面` に「関連 Brain ページ」セクション追加（projects/aios.md, people/iitake.md など）
- `projects` 一覧画面: Brain projects/ を読み込んで compiled truth を表示
- `query` ボックス: gbrain query を直接呼べる（hybrid search 結果表示）
- 既存の deliverables.yaml ベースの「AI からの成果物」セクションは継続

### 6.4 STATUS.md の扱い

**段階的に廃止 → Brain `projects/<name>.md` に移行**：
- Phase 1: STATUS.md と `projects/<name>.md` を併存（同期は人手 or AI）
- Phase 2: `projects/<name>.md` を canonical、STATUS.md は generated view（read-only）
- Phase 3: STATUS.md 廃止、mini-tachyon UI も `projects/` から表示

### 6.5 Daily Loop と Brain の連携

- 朝のエージェント: `gbrain query "today's context"` を呼んで `projects/`、`meetings/`（直近）、`people/`（今日会う人）を集約 → Flow にタスク案
- 夜のエージェント: 当日の作業を `projects/<name>.md` の timeline に追記、`meetings/` 整理

---

## 7. ファイル階層 — 案C 採用時の Before/After 実物

### Before（現状）
```
~/aipm_v0/
├─ Stock/作業効率化/AIOS/
│  ├─ STATUS.md                    # プロジェクト状態（手動更新）
│  ├─ README.md
│  ├─ backlog/BL-0053.yaml          # mini-tachyon canonical
│  ├─ design-philosophy.md          # 思想ドキュメント
│  ├─ onboarding-guide.md           # 飯武さん向け
│  └─ research-notes-2026-04.md     # 調査メモ
├─ Flow/202604/2026-04-28/作業効率化/AIOS/
│  ├─ deliverables.yaml
│  ├─ g_brain_investigation_v2.md
│  └─ g_brain_use_cases_v1.md
└─ .cursor/rules/aios/ops/13_mini_tachyon_protocol.mdc
```

### After（案C 採用後）
```
~/aipm_v0/
├─ Brain/                                           # ★新設
│  ├─ RESOLVER.md
│  ├─ schema.md
│  ├─ people/
│  │  ├─ tanaka.md                                  # 田中さん
│  │  ├─ iitake.md                                  # 飯武さん
│  │  └─ ohchi.md                                   # 大地さん
│  ├─ companies/
│  │  ├─ restaurant-ai-lab.md
│  │  └─ jbeauty.md
│  ├─ projects/
│  │  ├─ aios.md                                    # ★旧 STATUS.md（compiled truth + timeline）
│  │  ├─ jbeauty-signage.md
│  │  └─ ai-core-iitake.md
│  ├─ writing/
│  │  ├─ 2026-04-28-aios-philosophy.md              # ★旧 design-philosophy.md
│  │  └─ 2026-04-28-research-notes.md               # ★旧 research-notes
│  ├─ concepts/
│  │  ├─ flow-stock-philosophy.md
│  │  ├─ thin-harness-fat-skills.md
│  │  └─ mini-tachyon-protocol.md
│  ├─ meetings/
│  │  └─ 2026-04-30-iitake-1on1.md
│  └─ ideas/
│     └─ programmatic-bl-from-meetings.md
│
├─ Stock/                                           # 役割を絞る
│  └─ 作業効率化/AIOS/
│     ├─ README.md                                  # 短く（詳細は Brain projects/aios.md）
│     ├─ backlog/BL-0053.yaml                       # mini-tachyon canonical（変更なし）
│     └─ deliverables/
│        └─ aios-onboarding-guide-v1.md             # ★公開版のみ（飯武さんに渡す版）
│
├─ Flow/                                            # 変更なし
│  └─ 202604/2026-04-28/作業効率化/AIOS/
│     ├─ deliverables.yaml
│     ├─ g_brain_investigation_v2.md
│     ├─ g_brain_use_cases_v1.md
│     └─ aios_gbrain_integration_design_v2.md       # ★本書
│
└─ .cursor/rules/aios/ops/
   ├─ 13_mini_tachyon_protocol.mdc                  # 変更なし
   └─ 14_brain_filing_rules.mdc                     # ★新設（案C 採用時）
```

---

## 8. 残課題・今後の意思決定ポイント

1. **Brain のディレクトリ構造を AIOS ローカライズすべきか？**
   - GBrain 標準の英語ディレクトリ名（people/companies/projects/）をそのまま使うか
   - `人物/` `組織/` `プロジェクト/` のような日本語ディレクトリにするか
   - → GBrain 標準推奨（upstream の skill / 自動化を流用しやすい）

2. **`projects/` と `programs/` の使い分けをどうローカルルール化するか**
   - GBrain 公式: `projects/` = 1 件のビルド対象、`programs/` = 複数 project を束ねる人生ワークストリーム
   - AIOS 用: `projects/` = AIOS / J-Beauty Signage 等個別、`programs/` = 「AIPM 全体」「クライアント業務全体」など？
   - → 第一回後の整理で OK、最初は `projects/` だけで始める

3. **mini-tachyon UI の Brain 連携実装範囲**
   - 最小: BL 詳細に Brain ページへの link
   - 中: projects 一覧画面で compiled truth 表示
   - 最大: query ボックスで gbrain query を呼ぶ
   - → 段階的、Phase 2 で順次

4. **BL の Brain への露出**
   - BL は本当に Brain に出さなくて良いか（mt 専管で良いか）
   - GBrain の `daily-task-manager` skill との衝突回避策
   - → mt canonical を維持、Brain は read-only mirror（必要なら）

5. **Cursor rules の Brain 化**
   - `.cursor/rules/aios/ops/*.mdc` を Brain `concepts/` に link するか
   - → 13_mini_tachyon_protocol.mdc は AIOS 固有なので rules に残す。普遍的概念だけ concepts/ に

---

## 9. 次アクション

1. **本書を田中さんがレビュー** → 案C/Eで合意できるか判断
2. 合意できたら **BL-0002（GBrain 統合 AICore 検証）** を Phase 1=案D で着手
   - 既存 AIPM の Stock/Flow を `gbrain import` で取り込み
   - hybrid search / graph-query が実データで動くか検証
   - mini-tachyon UI から `gbrain query` を呼ぶプロトタイプ
3. 検証結果次第で案C へ進む（Phase 2）
4. 飯武さん第一回への組込みは BL-0002 結果を見て最終判断

---

## 10. 出典

- `docs/GBRAIN_RECOMMENDED_SCHEMA.md`（Brain ディレクトリ構造・disambiguation ルール・compiled truth + timeline）
- `skills/_brain-filing-rules.md`（filing rules、Iron Law back-linking）
- `skills/RESOLVER.md`（dispatch ロジック）
- `skills/manifest.json` / `skills/*/SKILL.md`（運用 skill）
- `~/aipm_v0/Flow/202604/2026-04-28/作業効率化/AIOS/g_brain_investigation_v2.md`（GBrain 二層構造）
- `~/aipm_v0/Flow/202604/2026-04-28/作業効率化/AIOS/g_brain_use_cases_v1.md`（ユースケース）
- `~/aipm_v0/.cursor/rules/aios/ops/13_mini_tachyon_protocol.mdc`（mini-tachyon protocol）
