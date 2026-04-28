# AIOS × G-Brain 統合設計 v3 addendum（C案メリット精査 + GBrain 思想の答え + 新案F）

- 作成日: 2026-04-28
- 担当: AIエージェント (BL-0053 mini-tachyon spawn)
- 関連: BL-0053 / BL-0002（GBrain 統合 AICore 検証）
- 前版: `aios_gbrain_integration_design_v2.md`（5 案比較、案E 段階的を推奨）
- 趣旨: 田中さんの 4/28 鋭い問いへの回答 — (1) C案のメリットはスイッチングコスト抜きで本当に成立するのか? (2) GBrain 単独だと AI がフォルダを勝手に増やして後から見にくいのでは? (3) 飯武さんゼロスタート前提だと最適解は何か?

---

## 0. 結論先出し

| 問い | 答え |
|---|---|
| Q1: 案C のメリットはスイッチングコスト以外にあるか？ | **YES、5 つの本質的価値がある**（§1） |
| Q2: GBrain 単独だと AI が勝手に dir 作って人が見にくいのでは？ | **GBrain の思想は「人は dir を探さない、LLM が取り出す」前提**。top-level dir は人間が固定。サブ dir は基本的に AI 自動生成しない。ただし**人間がファイルブラウザで探したい場面では辛い**のは事実（§2） |
| Q3: 飯武さんゼロスタート前提だと？ | **新案F（Brain 一本 + 公開時点で snapshot freeze）が最適解**。案C より単純、GBrain 純度高く、しかも「凍結された成果物」も担保（§3-§4） |

---

## 1. C案のメリット（スイッチングコスト抜きの本質）

田中さんの懸念は正当: **「移行コストが理由なら、ゼロスタートには無関係」**。なので Stock/Flow を Brain と並列に持つことの本質的価値だけ抽出する。

### 1.1 メリット A: バージョンの凍結（Versioning Freeze）

- **Brain の compiled truth は LLM が常に rewrite する**（これが GBrain の哲学）。2026-04-28 時点の `projects/aios.md` と 2026-05-15 時点の同ページは別物
- 一方で **顧客に渡した提案書 v1 は変わってはいけない**。1 ヶ月後に「あの時の提案書見せて」と言われた時に rewrite された版を出すのは事故
- Stock = 凍結された artifact 置き場として独立させると、**Brain がいくら賢くなっても過去の deliverable は変わらない**
- GBrain にも `archive/` ディレクトリはあるが、これは「廃ページ」用で「公開済 artifact」用ではない

→ **「LLM が常に書き換える知識」と「絶対に書き換えてはいけない成果物」の境界**が本質。これは飯武さんゼロスタートでも必要。

### 1.2 メリット B: 外部公開境界（Trust Boundary）

- Brain は内部知識: 顧客や外部に出す前提でなく、推測・未検証の事実が compiled truth に混ざる（GBrain は confidence 表記で対処してるが、それでも LLM 補正が入る）
- Stock = **「外に出した瞬間に内容確定」**の仕組み。バージョン管理付きで証跡が残る
- これは品質保証 / コンプライアンス文脈で重要: 「2026-04-30 にこの版を渡しました」が証明できる

→ **B2B 業務 (飯武さんへの提供も含む) では本質的に必要**。Brain の自由なリライトと両立しない。

### 1.3 メリット C: 引用の構造（Citation Primary Source）

- GBrain の哲学: **すべての fact は `[Source: ...]` で出典付き**。出典を持たないと "broken brain"
- 内部知識ばかりだと出典が「会話・推論」に偏り、citation の根拠が弱くなる
- Stock の deliverable を「**第一次出典**」として持つことで、Brain は `[Source: Stock/AIOS/proposal-v1.md]` のような明確な参照を持てる
- これは GBrain の `sources/` に近い役割だが、**`sources/` は "raw data dump" 用**で「自分が作って外に出した artifact」用ではない

→ **Brain が引用元として参照する固定アーティファクト群 = Stock**。GBrain 思想にむしろ整合する。

### 1.4 メリット D: MECE 制約からの解放

- Brain は「1 ファイル = 1 主題」を強制する MECE ルール
- しかし提案書のような **複合成果物**（飯武さん向け提案書 = 飯武さん × J-Beauty × AIOS 思想 × 価格 × スケジュール…）は、Brain で filing しようとすると主題が一つに絞れない
- 答え: **Brain はそういう成果物を直接持たず、Stock の artifact を `writing/<topic>` から `[See: Stock/...]` で参照する**
- 結果として Brain の MECE が壊れず、複合成果物も置き場がある

→ **GBrain MECE × 複合成果物の不整合を、Stock の独立性が解消する**。

### 1.5 メリット E: BL/タスクとの統合

- mini-tachyon は **deliverable** を一級概念として持つ（`mt deliverable update-state` etc.）
- BL → deliverable_refs で紐付ける構造が既にある
- これを Brain ページに紐付けようとすると、新たな概念マッピングが必要（BL = ?, deliverable = ? in Brain terms）
- Stock を維持すれば、**mini-tachyon の既存 BL/deliverable モデルがそのまま使える**

→ これは「飯武さんゼロスタート」でも mini-tachyon を提供する前提なら重要。

### 1.6 まとめ: 案C のメリットはゼロスタートでも成立する

| メリット | スイッチングコスト依存？ | 本質性 |
|---|---|---|
| A バージョン凍結 | × | ◎ 必須 |
| B 外部公開境界 | × | ◎ 必須 |
| C 引用元構造 | × | ○ 重要 |
| D MECE 解放 | × | ○ 重要 |
| E BL/task 統合 | × | ◎ mini-tachyon を提供するなら必須 |

→ **案C は飯武さんゼロスタートでも 5 つすべてのメリットが残る**。ただし「mini-tachyon は提供しない、純粋に GBrain だけ提供」なら E は無関係になる。

---

## 2. GBrain の思想：「AI が勝手にフォルダを作って後から人が見にくい」問題

田中さんのもう一つの懸念に正面から答える。

### 2.1 GBrain の前提: 「人はフォルダを探さない、LLM が取り出す」

GBrain 公式 (`docs/GBRAIN_RECOMMENDED_SCHEMA.md`) の核心思想:

> "knowledge management has failed for 30 years because maintenance falls on humans. LLM agents change the equation"

→ GBrain は **「人が手で整理する knowledge management の失敗」への対案**として設計されている。よって人がフォルダブラウザで探す体験は**意図的に最優先化していない**。

代わりに：
- **hybrid search**（"飯武さんに渡した提案書" で取れる）
- **graph traversal**（飯武さん people page → 関連 deliverable へリンク）
- **briefing skill**（朝に「今日関係する成果物」を要約）
- **query skill**（自然言語で問い合わせ）

で取り出す前提。

### 2.2 ただし「AI が勝手にフォルダを作る」は誤解

実際の GBrain の挙動:

| 項目 | 誰が決めるか |
|---|---|
| top-level dirs (`people/`, `companies/`, `projects/`, `writing/`, ...) | **人間が初期 schema 設計時に決定**。`schema.md` で固定 |
| 新しい top-level dir 追加 | 人間が判断（schema evolution として明示） |
| 個別 .md ファイル（`people/iitake.md` など） | **AI が filing rules に従って自動生成** |
| サブフォルダ（`people/iitake/.raw/`） | 標準化された `.raw/` のみ AI が作る |
| 任意のサブフォルダ（`people/clients/`, `people/internal/`） | **AI は作らない**（MECE rule に違反するため） |

つまり：
- ✅ ファイル数は爆発する（17,888 ページの実例）
- ❌ ディレクトリ構造は爆発しない（top-level + 標準サブだけ）

→ 「AI が勝手にフォルダを作って混沌になる」は実は起こらない。**起こるのは「ファイルが大量に増える」こと**。

### 2.3 でも田中さんの懸念は実は別の側面で正当

正確に言い直すと: **「ファイル数が多すぎて、人がブラウザで開いて探せない」という体験**は GBrain で起こる。

例:
- AIPM 1 ヶ月運用後の `people/` には 50〜200 ページが並ぶ
- 「飯武さんに渡した提案書、ファイルブラウザで探したい」→ どこにあるか目視で探せない
- GBrain の答え: `gbrain query "飯武さん 提案書"` で出してくれる
- でも田中さんは「LLM 不在で目視で探したい」場面もあるはず（電車の中、緊急時、AI が落ちてる時）

→ ここは GBrain 思想 vs 人間の現実的ニーズの**真のトレードオフ**。

### 2.4 答え: GBrain 単独の場合の対処法

GBrain 公式が用意してる仕組み:

1. **`index.md`** — content catalog with one-line summaries（人間が眺める用、AI が定期更新）
2. **`projects/<name>.md` の compiled truth** — 各プロジェクトのトップページに「関連 deliverable / meeting / people」を See Also で列挙
3. **canonical slug** — ファイル名がそのまま ID なので命名規則が一貫
4. **briefing skill** — 朝の運用で「今日関係する成果物」をリストアップ
5. **gbrain doctor / orphans** — 孤立ページ検出（後追いメンテ）

これらで「ファイル数爆発」をある程度カバーするが、**「ブラウザで開いて探す体験」を完全には代替しない**。

### 2.5 結論: GBrain 単独でも実は破綻しないが、人間の心理的安心感は失われる

- GBrain 思想を信じきれば: query / graph / briefing で十分
- 信じきれない（or 一部しか信じない）なら: Stock のような「人が目視で navigateable な場所」を残す価値あり
- **これが案C を採用する 6 つ目の隠れた理由**: 田中さんが LLM の出力を信用しきれないシーンへの保険

---

## 3. 飯武さんゼロスタート前提での再評価

田中さんの問題提起の核心: **「飯武さんは AIOS ない状態でゼロから提案する。スイッチングコスト ゼロ。なら最適解は？」**

### 3.1 飯武さんの状況を仮定で整理

| 項目 | 状態 |
|---|---|
| 既存の知識管理ツール | 不明（恐らく Notion / Obsidian / Drive 程度） |
| Cursor / Claude Code 環境 | 不明 |
| AI エージェント運用経験 | 不明 |
| 顧客向け提案書の管理 | 必須（B2B 業務） |
| バージョン管理（git）リテラシー | 不明 |
| 「LLM が常に rewrite する」思想への耐性 | 未知 |

→ **多くの不確実性**。「シンプルさ」と「成果物の堅牢性」のバランス重視。

### 3.2 ゼロスタートだからこそ重要な観点

1. **学習コスト**: 概念が少ないほど良い。Brain だけ vs Brain + Stock + Flow の差は大きい
2. **失敗リスク**: 提供して使われなかった時の機会損失
3. **将来の拡張性**: 後から機能を足すのと、削るのと、どちらが容易か
4. **信頼の獲得**: 最初の体験が「賢い」と感じられるか

### 3.3 案C は飯武さんゼロスタートでもまだ最適か？

各メリットの飯武さん文脈での価値:

| メリット | 飯武さんでの価値 |
|---|---|
| A バージョン凍結 | ◎ 顧客提案書を扱うなら必須 |
| B 外部公開境界 | ◎ 同上 |
| C 引用元構造 | ○ Brain の citation を強化（中期で効く） |
| D MECE 解放 | ○ 提案書のような複合成果物を扱うなら効く |
| E BL/task 統合 | △ mini-tachyon を一緒に提供するかで変わる |

**A と B は飯武さんゼロスタートでも完全に必要**。これだけで案C 採用の根拠になる。

ただし **Flow 層は飯武さんに必要か** が別の論点。

### 3.4 Flow 層の役割を再検討

AIOS では Flow = 中間生成物 / 日次作業空間。これは GBrain では何にあたる？

| AIOS Flow | GBrain での代替 |
|---|---|
| 日次の `_orchestration/` | `daily-task-prep` skill が動的生成、`inbox/` に保存 |
| 中間 deliverable（調査ノート） | `writing/` または `inbox/` に保存 |
| 議事録 raw | `meetings/<date>-<topic>.md` の Timeline section |

→ **GBrain は Flow 層相当を `inbox/` + `daily-task-prep` skill で代替できる**。Flow を独立フォルダで持たなくてもよい。

### 3.5 飯武さんに対する最小構成

**最低限必要な分離:**
- 「公開固定版（Stock 的な何か）」: 顧客提案書のバージョン凍結
- 「内部で使う知識（Brain）」: 人物・会社・プロジェクト・概念

**不要な分離:**
- 中間生成物の Flow フォルダ（GBrain の `inbox/` で十分）
- BL の per-project YAML（mini-tachyon 一本で十分）

→ 案C を簡略化した **「Brain + Stock 二層」** で十分かもしれない。Flow を消す。

---

## 4. 新案F: Brain 一本 + Snapshot Freeze（飯武さんゼロスタート向け新提案）

### 4.1 思想

> **GBrain の標準スキーマをそのまま使う。ただし「外部に渡した瞬間に snapshot を取って immutable にする」レイヤーを 1 つ足す。**

つまり Stock を「**Brain の一部として実装**」する。Brain `archive/` または専用の `published/` ディレクトリに、release-tag 付きで凍結コピーを置く。

### 4.2 ファイル階層

```
~/iitake_aipm/
├─ Brain/                              # GBrain 標準・唯一の知識層
│  ├─ RESOLVER.md
│  ├─ schema.md
│  ├─ people/
│  │  ├─ iitake.md
│  │  └─ <顧客>/                       # 標準: company と連動
│  ├─ companies/
│  │  ├─ <顧客社名>.md
│  │  └─ jbeauty.md
│  ├─ projects/
│  │  └─ <プロジェクト名>.md
│  ├─ writing/                         # ドラフト・思考
│  │  └─ 2026-XX-提案ドラフト.md
│  ├─ published/                       # ★新設: 公開時点で snapshot
│  │  ├─ 2026-04-30-jbeauty-proposal-v1.md   # immutable
│  │  ├─ 2026-04-30-jbeauty-proposal-v1.lock # メタ情報 (公開日, 受領者, 元 writing/ の slug)
│  │  └─ ...
│  ├─ meetings/
│  ├─ concepts/
│  ├─ ideas/
│  ├─ inbox/
│  └─ archive/
│
└─ ~/.gbrain/                          # Postgres + pgvector index
```

### 4.3 公開時の snapshot freeze ワークフロー

```bash
# 1. writing/ でドラフト作成（Brain で通常通り）
# 2. 公開準備ができたら freeze
gbrain publish-snapshot writing/2026-04-jbeauty-proposal-draft.md \
  --to published/2026-04-30-jbeauty-proposal-v1.md \
  --recipient companies/jbeauty.md \
  --version v1

# → published/ にハッシュ付きコピー、.lock ファイルにメタ情報
# → writing/ のドラフトは Brain のリライト対象として継続
# → published/ は immutable（Brain 自動更新の対象外）
```

### 4.4 スキル構成

- 標準 GBrain skill は全部使える
- 新規 skill: `publish-snapshot` (上記ワークフロー実装)
- 新規 skill: `query-published` (公開済み artifact の専用検索)

### 4.5 案F のメリット

| 項目 | 評価 |
|---|---|
| 学習コスト | ◎ Brain 一本、Stock/Flow の二層概念なし |
| バージョン凍結 | ◎ `published/` で実現 |
| 外部公開境界 | ◎ snapshot freeze で実現 |
| GBrain 純度 | ◎ 標準 schema をそのまま使う |
| 自己編成 graph | ◎ フル機能、`published/` も graph に組み込まれる |
| 既存 GBrain ツールとの互換 | ◎ 標準 schema 内の `published/` 追加だけ |
| 飯武さんゼロスタートでの導入 | ◎ シンプルに始められる |

### 4.6 案F のデメリット

| 項目 | 評価 |
|---|---|
| Flow 層がないのでドラフト中の整理が難しい | △ `inbox/` + `writing/` で代替できるが体験は別 |
| AIPM の mini-tachyon との統合 | △ mini-tachyon の deliverable 概念とずれる（`published/` は別概念） |
| MECE rule との整合 | △ `published/` が新カテゴリで、既存 `writing/` `archive/` と境界整理が必要 |
| 「snapshot freeze」自体が GBrain にない概念 | △ upstream に未存在、自前実装が必要（PR 候補にはなる） |
| AIPM 既存運用の田中さんが採用するなら案C のほうが整合 | ○ 田中さん本人 vs 飯武さん配布版で異なる |

### 4.7 案F の射程

**飯武さん向けの新しい配布パッケージとしては最適**。ただし田中さん自身の AIPM (mini-tachyon との統合済) には案C の方が整合する。

→ **田中さん本人 = 案C / 飯武さん配布版 = 案F** という二系統運用もあり得る（GBrain は同じ、上層の整理が違う）。

---

## 5. 推奨修正

v2 では案E（D→C 段階的）を推奨したが、本 v3 で **2 系統運用に修正**:

### 5.1 田中さん本人の AIPM (RestaurantAILab)

→ **案E（D→C）継続**。理由:
- mini-tachyon が既に動いており BL/deliverable 概念が canonical
- 既存 Stock を活かせる
- 移行リスクを段階的に管理できる

### 5.2 飯武さん向け配布版

→ **案F（Brain 一本 + snapshot freeze）を新規検討**。理由:
- ゼロスタート、概念は最小に
- バージョン凍結 / 外部公開境界は `published/` で担保
- 学習コスト最小、Brain の真価フル発揮
- mini-tachyon は提供せず GBrain 単独で動かす（or 簡易 GUI）

### 5.3 BL-0002 の検証スコープ

BL-0002（GBrain 統合 AICore 検証）では **両方を試す**:

1. **Phase 1a (案D)**: 田中さん AIPM の Stock を `gbrain import` で読み込み・検索
2. **Phase 1b (案F PoC)**: 飯武さん想定で「Brain 一本 + `published/`」の最小プロトタイプ

→ 検証結果から、田中さん運用 (案C) と飯武さん配布 (案F) の決定を行う。

---

## 6. 田中さんへの問い返し

ここまでで決まらないこと:

1. **飯武さんに mini-tachyon も提供するか？**
   - YES → 案C 路線（田中さんと同じ運用）
   - NO → 案F 路線（GBrain 単独、シンプル）
   - ※ mini-tachyon 提供は別の議論：iPhone UI / launchd / Tailscale が要るので飯武さん環境次第

2. **「LLM が常に rewrite する」思想を飯武さんが受け入れるか？**
   - YES → 案F が刺さる
   - NO → 案C のほうが安心感

3. **Flow 層は本当に必要か？**
   - 田中さん本人は Yes（mini-tachyon と連動）
   - 飯武さんは No でも回る（`inbox/` で代替）

これらに答えが出れば、案C / 案F のどちらか確定できる。

---

## 7. 次アクション

1. 本 v3 を田中さんレビュー → 上記 §6 の 3 つの問いに回答もらう
2. 回答に応じて BL-0002 の検証スコープを確定
3. BL-0002 で Phase 1a (案D) + Phase 1b (案F PoC) を並行実施
4. 検証結果を踏まえて飯武さん第一回（4/30 or 5月）への組込み度合を最終判断

---

## 8. 出典・参照

- v2 設計書: `Flow/202604/2026-04-28/作業効率化/AIOS/aios_gbrain_integration_design_v2.md`
- GBrain schema: `docs/GBRAIN_RECOMMENDED_SCHEMA.md`
- GBrain filing rules: `skills/_brain-filing-rules.md`
- Karpathy LLM wiki pattern (GBrain README より参照)
- mini-tachyon protocol: `~/aipm_v0/.cursor/rules/aios/ops/13_mini_tachyon_protocol.mdc`
