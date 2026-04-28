# Brain Schema — ページ構造とテンプレート

すべての brain ページは **compiled truth + timeline** の二層構造に従う。`---` で区切る。

---

## 共通フォーマット

```markdown
---
slug: my-page-slug
type: people | companies | projects | concepts | writing | meetings | ideas | programs | published | ...
status: active | archived | snapshot
aliases: ["別名", "Alias 2"]
tags: [tag1, tag2]
created_at: YYYY-MM-DD
updated_at: YYYY-MM-DD
---

# ページタイトル

> Executive summary（1 段落）— このページを読まなくてもこの段落だけで現状把握できる

## State
構造化された現在の事実（State fields）。LLM が常時 rewrite する対象。

## Open Threads
未解決の active items（解決したら timeline に移す + 削除）

## See Also
- [関連ページ](path/to/page.md) — 一行説明
- 外部リンク

---

## Timeline

reverse-chronological、append-only（書き換え禁止）

- **YYYY-MM-DD** | source | what happened [Source: ...]
- ...
```

**上半分** = compiled truth（常に最新、LLM rewrite OK）
**下半分** = timeline（生エビデンス、append-only）

---

## 引用ルール（MANDATORY）

すべての fact は以下のいずれかの引用を持つ：

- `[Source: User, <context>, YYYY-MM-DD]` — ユーザの直接発言（最高権威）
- `[Source: <provider>, YYYY-MM-DD]` — API / 外部
- `[Source: <publication>, <URL>]` — 出版物
- `[Source: compiled from <list>]` — 複数ソースの合成

**Source precedence (highest to lowest):**
1. User's direct statements
2. Compiled truth (pre-existing brain synthesis)
3. Timeline entries (raw evidence)
4. External sources (web, API)

矛盾する場合は両方の引用を残し、矛盾を明示する。

---

## ページタイプ別テンプレート

### people/<slug>.md

```markdown
---
slug: <first-last>
type: people
aliases: ["別名", "メアド", "SNS handle"]
---

# 人物名

> 1段落の executive summary — 誰で、何で重要か、関わる時に何を知っておくべきか

## State
- **Role:** 現在の肩書
- **Company:** 所属
- **Relationship to me:** 関係性
- **Key context:** 今重要なこと（2-4 bullets）

## What They Believe
信念・世界観（出典必須）

## What They're Building
現在のプロジェクト・成果

## Communication Style
コミュニケーションの傾向（直接観察由来のみ）

## See Also
- [関連 people/companies/meetings]

---

## Timeline
- YYYY-MM-DD | source | event
```

### companies/<slug>.md

```markdown
---
slug: <company-name>
type: companies
aliases: [...]
---

# 会社名

> Executive summary

## State
- **Industry:**
- **Size:**
- **Stage:**
- **Key context:**

## What They Do
事業内容

## Key People
- [Person Name](../people/slug.md) — 肩書

## See Also

---

## Timeline
```

### projects/<slug>.md

```markdown
---
slug: <project-name>
type: projects
status: active | paused | completed
category: <分野>
owner: <people/slug>
---

# プロジェクト名

> Executive summary — 何を作っていて、なぜ、現在のフェーズ

## State
- **Phase:** discovery | building | shipping | done
- **Next action:** 一文
- **Blocker:** あれば
- **Key stakeholders:** [people/...]

## What's Being Built
具体的な成果物・スコープ

## Decisions Log
- YYYY-MM-DD: 決定内容 [Source: ...]

## See Also
- [関連 people/companies]
- [関連 published/<date>-<slug>] — 公開済成果物

---

## Timeline
```

### writing/<slug>.md

```markdown
---
slug: <topic>
type: writing
status: draft | review | published
---

# タイトル

（散文・ドラフト・エッセイ本文）

## See Also

---

## Timeline
- YYYY-MM-DD: 初稿 / レビュー / publish
```

### published/<YYYY-MM-DD>-<slug>-<version>.md（案F 固有）

```markdown
---
slug: <date>-<topic>-<version>
type: published
status: snapshot
recipient: companies/<slug> | external
source_writing: writing/<slug>     # スナップショット元
version: v1 | v2 | ...
hash: sha256:...                    # コンテンツハッシュ
published_at: YYYY-MM-DD
---

# タイトル — vN

（公開時点の固定版コピー — 編集禁止）

# Original Source
- writing/<slug> から YYYY-MM-DD にスナップショット
- 同一スラグの最新ドラフトは writing/ を参照
```

### meetings/<YYYY-MM-DD>-<topic>.md

```markdown
---
slug: <date>-<topic>
type: meetings
attendees: [people/...]
duration: <minutes>
---

# 会議タイトル — YYYY-MM-DD

## Attendees
- [Person](../people/slug.md)

## Summary
3-5 bullet outcomes

## Key Decisions

## Action Items

## Discussion Notes

---

## Timeline / Raw Transcript
（生文字起こし、append-only）
```

---

## ファイル名規約（Canonical Slug）

- ASCII を優先（`first-last`, `company-name`）
- 日本語名はそのまま使用可（既存 Stock 名の踏襲は OK）
- 全て小文字、空白はハイフン
- ID として stable — 一度決めたら変更しない（リネームは merge protocol に従う）

---

## frontmatter 必須フィールド

| フィールド | 必須 | 用途 |
|---|---|---|
| `slug` | YES | ファイル名と一致、graph の primary key |
| `type` | YES | ディレクトリと一致（people/companies/projects/...） |
| `aliases` | 推奨 | 別名・メアド・SNS handle 等 |
| `created_at` | YES | 作成日 |
| `updated_at` | YES | 最終更新日 |
| `status` | type 依存 | active/archived/snapshot 等 |

その他、type 固有のフィールド（people なら `role`, `company`, projects なら `phase`, `owner` 等）は柔軟に追加可。

---

## .raw/ サイドカー

各エンティティの生データ（API レスポンス・添付・生議事録）は同階層の `.raw/<slug>/` に保存：

```
people/
├─ iitake.md
└─ .raw/
   └─ iitake/
      ├─ linkedin-2026-04-29.json
      └─ meeting-transcript-2026-04-30.txt
```

100MB 超のメディアは外部ストレージ + `.redirect.yaml` ポインタ（GBrain の files upload-raw 規約参照）。
