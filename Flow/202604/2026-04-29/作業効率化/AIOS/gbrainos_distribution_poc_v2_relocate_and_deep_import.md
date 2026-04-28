# GbrainOS（飯武さん配布版・案F）PoC v2 — 配置修正 + Deep Import

- 作成日: 2026-04-29
- 担当: AIエージェント (BL-0053 mini-tachyon spawn)
- 関連: BL-0053 / BL-0002（GBrain 統合 AICore 検証）
- 配置: **`~/GbrainOS/`**（aipm_v0 と並列、~/ 直下、self-contained）
- v1 からの修正点:
  1. 配置を `~/aipm_v0/GbrainOS/` から **`~/GbrainOS/`** に変更（aipm と並列）
  2. Migration を **「Stock 参照型 reflection」から「実コピー型 deep import」に変更**（Brain は self-contained）
- v1 の `~/aipm_v0/GbrainOS/` は削除済（rm -rf）

---

## 0. 完成形

```
~/aipm_v0/                    # 既存 AIOS（無傷、本番運用）
└─ Stock / Flow / .cursor/rules/aios/ ...

~/GbrainOS/                   # ★新規（飯武さん配布版 PoC、self-contained）
└─ Brain/
   ├─ RESOLVER.md / schema.md / index.md
   ├─ programs/    9 件
   ├─ projects/   43 件   (STATUS + README を embed)
   ├─ writing/   427 件   (Stock の deliverable .md を実コピー)
   ├─ people/      3 件   (tanaka / iitake / ohchi seed)
   ├─ companies/   1 件   (restaurant-ai-lab seed)
   ├─ published/   0 件   (案F 固有・空)
   └─ 他 14 dir   各 README.md のみ
```

**Total: 508 .md ファイル**（v1 の 79 件から大幅増加 = deliverable 本体取り込みのため）

---

## 1. v1 → v2 で何が変わったか

| 項目 | v1 | v2 |
|---|---|---|
| 配置 | `~/aipm_v0/GbrainOS/` | **`~/GbrainOS/`**（aipm と並列） |
| Stock の扱い | 参照（See Also に Stock パス、本体は読まない） | **実コピー**（writing/ に取り込み、Brain self-contained） |
| projects/ | メタ情報 + Stock パス link | メタ情報 + STATUS.md + README.md embed + writing/ への内部リンク |
| writing/ | 0 件 | **427 件**（Stock 全 deliverable を `<project>--<rel-path>.md` として import） |
| 配布性 | Stock を要する（独立しない） | self-contained（GbrainOS だけで完結） |

---

## 2. インポート規則

### 2.1 ディレクトリ対応

| Stock | → Brain |
|---|---|
| `Stock/<category>/` | `programs/<category>.md` |
| `Stock/<cat>/<project>/` | `projects/<project>.md` |
| `Stock/<cat>/<proj>/STATUS.md` | projects/ frontmatter + `## STATUS (imported)` セクションに body embed |
| `Stock/<cat>/<proj>/README.md` | projects/ `## README (imported)` セクションに embed |
| `Stock/<cat>/<proj>/<deliverable>.md` | **`writing/<project>--<deliverable-stem>.md`** に実コピー |
| `Stock/<cat>/<proj>/<sub>/<file>.md` | `writing/<project>--<sub>-<file>.md`（パス区切りはハイフン） |
| `Stock/<cat>/<proj>/backlog/*.yaml` | **import しない**（mini-tachyon canonical、案F は mini-tachyon なし）。projects/ に名前のみリスト |
| `Stock/<cat>/<proj>/.raw/`, `Stock/<cat>/<proj>/.git/` | 除外（ドット始まり） |

### 2.2 命名規約

writing/ の各ファイル：`<project>--<rel-path>.md`
例：
- `Stock/作業効率化/AIOS/discovery_notes.md` → `writing/AIOS--discovery_notes.md`
- `Stock/RestaurantAILab/麻布しき/2026-04-15-定例.md` → `writing/麻布しき--2026-04-15-定例.md`
- `Stock/RestaurantAILab/AI-Core/sub/file.md` → `writing/AI-Core--sub-file.md`

`--`（ダブルハイフン）でプロジェクト名と元相対パスを区切ることで、後で機械的に元 Stock パスに戻せる。

---

## 3. 重要な設計判断

### 3.1 Self-contained にした理由

v1 では Stock を参照（See Also link）していたが、配布版なら **GbrainOS フォルダだけで完結すべき**。`~/GbrainOS/` を tar で固めて飯武さん環境に展開すれば動く状態を目指した。Stock 依存を断つために実コピー方式に変更。

### 3.2 BL を入れない判断（v1 から継続）

案F は mini-tachyon なし前提。BL は田中さん本人の AIPM (`~/aipm_v0/`) で canonical 管理。Brain の projects/ 内に名前のみリスト掲載（飯武さんは BL が「あった」ことを認識できる）。飯武さん側の意思追跡仕組みは別途検討。

### 3.3 People / Companies は最小 seed

Stock に entity ページがないため、会話コンテキストから 3 人 + 1 社のみ作成。今後の運用で `enrich` skill 等で増やす（GBrain CLI を入れた後）。

### 3.4 `published/` は空でスタート

過去に外部に渡した版を遡及的に登録するか、4/29 以降の新規分のみかは田中さん判断待ち。snapshot freeze ワークフローは README で規定済。

---

## 4. 動作確認サンプル

```bash
# 全 program 一覧
ls ~/GbrainOS/Brain/programs/

# AIOS プロジェクトの状態（STATUS.md 内容含む）
cat ~/GbrainOS/Brain/projects/AIOS.md
# → frontmatter + STATUS body + README body + writing への links

# AIOS の deliverable
ls ~/GbrainOS/Brain/writing/ | grep '^AIOS--'
# → AIOS--discovery_notes.md / AIOS--scope_proposal.md / AIOS--log.md
cat ~/GbrainOS/Brain/writing/AIOS--discovery_notes.md
# → Stock の元ファイル本文がそのまま import されている

# 全 writing 数
ls ~/GbrainOS/Brain/writing/*.md | grep -v README | wc -l
# → 427
```

---

## 5. Stats（最終）

| Type | Count | 内訳 |
|---|---|---|
| Programs | 9 | Stock の 9 カテゴリ全反映 |
| Projects | 43 | Stock の全プロジェクト |
| Writing | 427 | Stock 全 deliverable を実コピー |
| People | 3 | tanaka / iitake / ohchi |
| Companies | 1 | restaurant-ai-lab |
| Published | 0 | （4/29 以降の運用で蓄積） |
| Meetings | 0 | （後の enrichment で増やす） |
| **Total .md** | **508** | (上記 + RESOLVER + schema + index + 20 README) |

---

## 6. 残課題・次の検証項目

### Phase 1b（BL-0002）の残作業

1. **GBrain CLI 実インストール + `gbrain init ~/GbrainOS/Brain/`**
   - PGLite で hybrid search が動くか
   - 508 .md を index して `gbrain query` 実行
   - `gbrain graph-query` で typed link が機能するか

2. **`publish-snapshot` skill 自前実装**
   - GBrain 標準にない（案F 固有）
   - `gbrain publish-snapshot writing/X.md --to published/<date>-X-v1.md --recipient companies/Y --version v1`
   - .lock ファイル自動生成

3. **People / Companies の充実**
   - 過去議事録（`Stock/Meetings/` がある？要確認）から enrich
   - STATUS.md 内の人名抽出 → people/ seed

4. **配布パッケージ化**
   - `~/GbrainOS/` を tar で配布できる状態に
   - secret 除外（API key 等）
   - Setup script（`bun install` + `gbrain init` + onboarding）

5. **田中さん本人の AIPM 案C 移行**
   - これは BL-0053 後続タスク（飯武さん検証完了後）

---

## 7. 田中さんへの問い返し（v1 から継続）

1. **`published/` の遡及登録** — 過去に外部提出した固定版も登録する？ それとも 4/29 以降の新規分のみ？
2. **BL の代替手段** — 飯武さん配布版で BL 相当の意思追跡をどうするか
3. **People / Companies 充実のタイミング** — 第一回前にどこまで enrich するか（過去議事録から自動抽出する？）
4. **配布パッケージ化のスコープ** — 飯武さんに渡す形は GitHub repo / tarball / Cursor workspace template どれが良いか

---

## 8. 補足：v1 deliverable の扱い

`d-bl0053-20260429-gbrainos-poc-v1-migration` は配置と方法の両方が変わったため superseded。本 v2 を canonical とする。v1 の Markdown ファイル（`Flow/202604/2026-04-29/作業効率化/AIOS/gbrainos_distribution_poc_v1_migration_report.md`）は履歴として残す。
