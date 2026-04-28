# GbrainOS PoC v3 — 完全反映 + Scope/BL/Published 改善

- 作成日: 2026-04-29
- 担当: AIエージェント (BL-0053 mini-tachyon spawn)
- 関連: BL-0053 / BL-0002
- 配置: `~/GbrainOS/Brain/`（aipm と並列、self-contained）
- v2 からの修正点（田中さん 4/29 指示への対応）:
  1. **published に過去配信物を遡及登録** — 月報/週報 の 2_output 配下 125 件
  2. **BL は GBrain 方式に従う** — projects/ の Open Threads セクションに変換 (mini-tachyon なし前提)
  3. **Scope セクション** を全 projects/ に追加 — STATUS/README から自動抽出、無ければ TBD 明示
  4. **Stock の完全反映を達成** — 数学的検証で 1056 .md = 1002 destinations + 54 embedded

---

## 0. 完全反映の検証（最重要）

| 項目 | 数 |
|---|---|
| Stock 全 .md ファイル | **1056** |
| project-root STATUS.md + README.md (projects/<name>.md に embed) | 54 |
| Brain destinations (writing + published + org) 合計 | **1002** |
| 合計 (Brain でアクセス可能な Stock 内容) | **1056 ✓** |
| Backlog YAMLs (mini-tachyon canonical, projects/ Open Threads に変換) | 35 |

→ **Stock の全コンテンツが Brain のいずれかの場所からアクセス可能**。零落（lost in migration）なし。

---

## 1. Brain 最終構成

```
~/GbrainOS/Brain/
├─ RESOLVER.md / schema.md / index.md
├─ programs/      9 件   (Stock 全カテゴリ)
├─ projects/     43 件   ★ Scope + Open Threads + STATUS/README embed
├─ writing/     871 件   (Stock 全 deliverable + sub-dir README/STATUS)
├─ published/   125 件   ★ 月報/週報 過去配信物を .lock 付きで遡及登録
├─ org/           6 件   (category README + MasterIndex)
├─ people/        3 件   (tanaka / iitake / ohchi seed)
├─ companies/     1 件   (restaurant-ai-lab seed)
├─ sources/       1 件   (MasterIndex.yaml)
└─ 他 12 dir     (各 README.md only — 今後の運用で蓄積)
```

**.md total**: ~1080 / **.lock total**: 125

---

## 2. 田中さん 3 指示への対応詳細

### 2.1 published に過去分を遡及登録

**対象**: `Stock/RestaurantAILab/月報/2_output/<client>/2_output_<period>/*.md` および `週報/2_output/...` の合計 125 件

**手順**:
1. writing/ 配下の `月報--2_output-*` / `週報--2_output-*` を抽出
2. ファイル名から client / period / topic を parse
   - 例: `週報--2_output-麻布しき-2_output_2026w06-週報スライド構成案.md`
   - → client=麻布しき / period=2026w06 / topic=週報スライド構成案
3. published/ に `<period>-<client>-<type>-<topic>-v1.md` で配置
4. 同名 `.lock` ファイル (YAML) を生成（recipient / source / version / hash プレースホルダ）
5. writing/ から削除（MECE 維持: 同じファイルは一箇所のみ）

**サンプル**:
```
published/
├─ 2025w42-BFA-週報-週報作成基礎資料-v1.md          # 2025 W42 BFA 向け週報基礎資料
├─ 2025w42-BFA-週報-週報作成基礎資料-v1.lock         # メタ情報
├─ 2025w52-BBC-週報-別天地銀座_週報スライド構成案_2025W52-v1.md
├─ 2026w06-麻布しき-週報-週報スライド構成案-v1.md
├─ 202601-BFA-月報-月報スライド構成案-v1.md
└─ ...
```

**.lock の中身（例）**:
```yaml
slug: 2026w06-麻布しき-週報-週報スライド構成案-v1
type: published
recipient: companies/麻布しき
source_writing: writing/週報--2_output-麻布しき-2_output_2026w06-週報スライド構成案.md
version: v1
period: 2026w06
published_at: 2026-04-29  # retroactively registered
retroactively_registered: true
notes: Retroactively registered from writing/ during 2026-04-29 案F PoC migration.
```

### 2.2 BL は GBrain 方式に従う

GBrain 標準には専用の BL primitive はなく、`daily-task-manager` skill が **projects ページの Open Threads セクション**でタスクを扱う流儀。これに従い:

**Stock の `<project>/backlog/BL-*.yaml` (35 件) を projects/<name>.md の Open Threads セクションに変換**。

**変換ルール**:
- BL.yaml から `id` / `title` / `state` / `priority` を抽出
- チェックボックス: `state=completed` → `[x]`, `blocked` → `[!]`, それ以外 → `[ ]`
- 1 行形式: `- [ ] **BL-XXXX** [state/priority] title`

**Brain projects/AIOS.md の Open Threads サンプル**:
```markdown
## Open Threads (tasks — GBrain way)

> 元 `Stock/.../backlog/BL-*.yaml` を Open Threads に変換 (案F は mini-tachyon なし前提)。

- [ ] **BL-0053** [planned/high] AIOSアップデート（G-Brain統合 + ルール全体の見直し）
- [ ] **BL-0067** [planned/normal] INBOX 設計の再検討
```

→ 飯武さんは BL-XXXX という ID 体系を意識せずに Open Threads として扱える。完了したら `- [x]` に書き換え、archive すれば良い（GBrain 流）。

### 2.3 Scope セクションの自動付与

**問題**: Stock の STATUS.md / README.md にスコープが定義されていないプロジェクトが多い（「定置されていない」という田中さん指摘）

**対応**: projects/ 全 43 件に **`## Scope` セクション**を追加。優先順位で抽出:

1. STATUS.md の `## 概要` または `## 📋 概要` セクション
2. README.md の `## 概要` または `## Overview` セクション
3. README.md の `## 背景` + `## 目的` + `## ゴール` を結合（多くの project はこの形式）
4. いずれもない場合 → `**TBD — Stock 由来の STATUS.md / README.md にスコープ相当のセクション (概要 / 背景+目的+ゴール / Overview) が見つかりませんでした。**` と明示

**Source 表記**: 抽出元を `*Source: STATUS.md / 📋 概要*` 形式で記録。透明性確保。

**サンプル — 麻布しき (no STATUS, README に背景+目的+ゴール)**:
```markdown
## Scope

*Source: README.md / 背景+目的+ゴール*

### 背景
- 麻布しきは当社プロダクトを利用しているクライアント飲食店
- 旗の台店・本店の2店舗を運営

### 目的
- 麻布しきに対する個別タスク（売上分析、目標設定、ダッシュボード設定等）を管理する

### ゴール
- クライアント対応タスクが漏れなく管理・遂行されている状態
```

→ 関係者・状況などは README.md (imported, full) セクションでも引き続き参照可能。

---

## 3. 完全反映のために行った追加修正（v2 からの差分）

| 修正 | 詳細 |
|---|---|
| **maxdepth 制限の撤廃** | v2 は `-maxdepth 4` で深い階層 (e.g., `month/2_output/client/period/file`) を取りこぼし → 制限なしに変更 |
| **Stock 直下ファイルの取り込み** | `Stock/MasterIndex.md` → `org/aipm-master-index.md` |
| **category-level READMEs** | `Stock/<cat>/README.md` (5 件) → `org/category-<cat>-readme.md` |
| **category-level non-README .md** | `Stock/むしめがね/program_definition.md` 等 3 件 → `writing/_category-<cat>--<stem>.md` |
| **sub-dir README/STATUS** | `Stock/<cat>/<proj>/<sub>/README.md` 等 → `writing/<proj>--<rel-path>-README.md` |

---

## 4. 残課題（v2 から継続）

1. **GBrain CLI 実インストール + `gbrain init ~/GbrainOS/Brain/`** — hybrid search / graph-query の動作確認
2. **`publish-snapshot` skill 実装** — 案F 固有、新規 publish 時の自動化（手動 mv + .lock 生成を skill 化）
3. **People / Companies の充実** — 過去議事録から enrich (`Stock/RestaurantAILab/ChefsRoom会議議事録/` 等から抽出)
4. **配布パッケージ化** — `~/GbrainOS/` を tar / GitHub repo / Cursor workspace template に
5. **田中さん本人の AIPM 案C 移行** — 飯武さん検証完了後

---

## 5. 田中さんへの問い返し（v3 で残るもの）

### 5.1 published/ 範囲の妥当性

現状は **月報/週報 の 2_output 配下のみ** (125 件) を published/ に登録した。他にも遡及登録すべき "外部に渡したもの" はあるか？ 候補:

- `Stock/RestaurantAILab/麻布しき/` 配下のクライアント提出資料
- `Stock/RestaurantAILab/<クライアント案件>/` 配下の提案書・報告書
- `Stock/RestaurantAILab/Famm/`, `BFA/`, `BBC/` 等の納品物
- `Stock/むしめがね/バンコク2025年8月/3_handout/` 等の配布物

→ 必要なら追加判定ルール（例: ディレクトリ名に `output` `納品` `提出` `配布` `final` `v[0-9]` 含む等）を提案できる。

### 5.2 People / Companies の自動 enrich

過去議事録（`Stock/RestaurantAILab/ChefsRoom会議議事録/` 等）から人物名・会社名を抽出して people/ companies/ に自動投入するか？ それとも手動で重要度の高い 5〜10 件のみ充実させるか？

### 5.3 配布パッケージ化のスコープ

第一回（4/30）or 第二回（5月）に向け、どの形で配布するか？
- (a) GitHub private repo として渡す
- (b) tar.gz パッケージ
- (c) Cursor workspace template として
- (d) PoC 段階なので配布せず、田中さんが操作デモのみ

---

## 6. v2 deliverable の扱い

v2 は配置・migration 方法は正しかったが**完全反映と Scope/BL/Published 改善が未済**だった → v3 で superseded 候補。本書 (v3) を canonical として登録、v2 は履歴として残す。
