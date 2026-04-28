# GbrainOS（飯武さん配布版・案F）PoC v1 — 初期 Migration レポート

- 作成日: 2026-04-29
- 担当: AIエージェント (BL-0053 mini-tachyon spawn)
- 関連: BL-0053（統合方針）/ BL-0002（GBrain 統合 AICore 検証）
- 配置: `~/aipm_v0/GbrainOS/`（AIOS と並列、aipm_v0 内）

---

## 0. やったこと（一行）

田中さん指示「AIOS と並列で GbrainOS フォルダを作り、GBrain のフォルダ構成 + Stock 内容を Brain に反映」を実行。**配布版のみ検証** = 案F（Brain 一本 + `published/` snapshot freeze、mini-tachyon なし、Flow なし）の PoC として動作可能な初期状態を構築。

---

## 1. 完成した構造

```
~/aipm_v0/GbrainOS/
└─ Brain/
   ├─ RESOLVER.md                 # GBrain 標準 + 案F 拡張の決定木
   ├─ schema.md                   # ページテンプレート（people/projects/published 等）
   ├─ index.md                    # コンテンツカタログ
   ├─ people/        (3 人 + README)   tanaka / iitake / ohchi
   ├─ companies/     (1 + README)      restaurant-ai-lab
   ├─ projects/      (43 + README)     全 Stock プロジェクトを反映
   ├─ programs/      (9 + README)      Stock 8 カテゴリ + 本業
   ├─ published/     (空 + README)     ★ 案F 固有: snapshot freeze 領域
   ├─ deals/         (空 + README)
   ├─ meetings/      (空 + README)
   ├─ ideas/         (空 + README)
   ├─ concepts/      (空 + README)
   ├─ writing/       (空 + README)
   ├─ org/           (空 + README)
   ├─ civic/         (空 + README)
   ├─ media/         (空 + README)
   ├─ personal/      (空 + README)
   ├─ household/     (空 + README)
   ├─ hiring/        (空 + README)
   ├─ sources/       (空 + README)
   ├─ prompts/       (空 + README)
   ├─ inbox/         (空 + README)
   └─ archive/       (空 + README)
```

**Total: 79 Markdown files** (RESOLVER + schema + index + 20 README + 56 entity pages)

---

## 2. Migration の方針（重要）

**「Stock を読み取り専用で残し、Brain に Reflection を作る」** スタイル。Stock の本体ファイルは触らず、Brain `projects/<name>.md` に **メタ情報 + 本体への See Also** を生成。

### マッピング規則

| Stock | → Brain | 備考 |
|---|---|---|
| `Stock/<category>/` | `programs/<category>.md` | 全 8 + 本業 = 9 ファイル |
| `Stock/<cat>/<project>/` | `projects/<project>.md` | 全 43 ファイル |
| `Stock/<cat>/<proj>/STATUS.md` | projects/ frontmatter + State セクション | status / next_action / blocker / current_bl 抽出 |
| `Stock/<cat>/<proj>/backlog/BL-*.yaml` | projects/ "Related BLs" | リスト表示のみ。**mini-tachyon canonical のため Brain には個別ページ作らない** |
| `Stock/<cat>/<proj>/<deliverable>.md` | projects/ "Deliverables" | リスト表示のみ。本体は Stock 側に残す（飯武さん版では原本も Brain に取り込まないシンプル方針） |
| 既知の人物（田中・飯武さん・大地さん） | `people/<slug>.md` | 会話コンテキストから seed |
| RestaurantAILab | `companies/restaurant-ai-lab.md` | seed |

### Brain 標準 vs 案F 固有

- 標準: `people/`, `companies/`, `projects/`, `programs/`, `meetings/`, `concepts/`, `writing/`, `ideas/` 等の GBrain 推奨ディレクトリすべて
- **案F 固有: `published/`** を新設。「外部公開した固定版」の immutable 領域。`<YYYY-MM-DD>-<slug>-<version>.md` 命名規則と `.lock` メタファイルを規定

---

## 3. 重要な設計判断

### 3.1 Stock 原本を残した（destructive migration ではない）

理由：
1. **PoC 段階なので原本破壊リスクを取らない**
2. Stock は AIOS（mini-tachyon 連動、田中さん本人運用）の canonical のまま
3. GbrainOS は飯武さん配布版の検証であり、田中さん本人運用とは別系統

→ Brain `projects/<name>.md` の "Original Source" セクションが Stock を指す形。Brain 単独でも自己完結（メタ情報は揃っている）、深掘りしたいときは Stock を読む。

### 3.2 BL は Brain に出さない

理由：飯武さん配布版（案F）は **mini-tachyon を提供しない**前提。BL はリスト表示のみで、個別ページは Brain には作らない。BL の意思追跡は飯武さん側で別途仕組みが必要（要検討）。

### 3.3 Deliverables 本体も移動しない

理由：飯武さんへの配布物は、田中さんの過去 Stock の本体ではなく **新たに飯武さん向けに作るもの**。Stock の本体を Brain に複製するのは不要かつノイズ。projects/ で「Stock にこういう deliverable がある」とリスト表示に留める。

### 3.4 People / Companies は最小 seed

理由：Stock には `people/` `companies/` 相当のページがそもそも存在しない（AIOS は entity-first ではないため）。会話コンテキストから seed として 3 人 + 1 社のみ作成。今後の運用で `enrich` skill 等で追加していく。

---

## 4. これで何ができるようになったか

### 4.1 Brain 単独でプロジェクト概観が取れる

```bash
# 全 active プロジェクトを見る
ls ~/aipm_v0/GbrainOS/Brain/projects/

# 特定プロジェクトの状態
cat ~/aipm_v0/GbrainOS/Brain/projects/AIOS.md
# → status / next action / 関連 BL / Stock 原本パスが一目で分かる

# プログラム別の俯瞰
cat ~/aipm_v0/GbrainOS/Brain/programs/RestaurantAILab.md
# → 配下プロジェクト一覧 + 各 projects/ への link
```

### 4.2 GBrain CLI を入れれば即動作する見込み

`~/aipm_v0/GbrainOS/Brain/` を `gbrain init` の brain dir として指定すれば、PGLite + hybrid search + graph traversal が動く想定。RESOLVER.md / schema.md / 各 README.md は GBrain 推奨スキーマに準拠しているので skill との整合も取れるはず（要検証）。

### 4.3 published/ workflow が試せる

例: 飯武さんに 4/30 渡す資料が決まったら、`writing/` で書いて `published/2026-04-30-iitake-onboarding-v1.md` にスナップショット → 以降 immutable。

---

## 5. 残課題・次の検証項目（BL-0002 検証スコープ案）

### Phase 1b の残作業

1. **GBrain CLI の実インストールと動作確認**
   - `bun install` → `gbrain init ~/aipm_v0/GbrainOS/Brain/` で動くか
   - `gbrain query "AIOS"` で hybrid search が hit するか
   - `gbrain graph-query` で typed link が機能するか（現状 entity 数少ないので限定的）

2. **`published/` の publish-snapshot skill を実装**
   - GBrain 標準にはない skill（自前実装）
   - `gbrain publish-snapshot writing/x.md --to published/2026-04-30-x-v1.md --recipient companies/y --version v1`
   - .lock ファイル自動生成

3. **People / Companies の充実**
   - 過去議事録（Meetings/ にある？）から enrich
   - 既存 STATUS.md 内の人名を抽出して seed

4. **Brain 単独 UI の検討**
   - mini-tachyon なし前提なので、CLI + ファイルブラウザ + （簡易 web UI?）
   - 飯武さんに渡せるレベルの onboarding ドキュメントが要る

5. **配布パッケージ化**
   - `~/aipm_v0/GbrainOS/` をそのまま配布できるか（API key 等の secret 除外）
   - Setup script（`gbrain init` + `bun install` + 初期ガイド）

### 飯武さん第一回への組込み判断材料

- BL-0002 で 1〜2 がクリアできれば第一回でデモ可能（ただし限定的）
- 完全な配布パッケージ化（5）は第二回以降

---

## 6. 田中さん本人 (AIOS / 案C) との関係

本 PoC は **飯武さん配布版（案F）の検証専用**。田中さん本人の AIPM (`~/aipm_v0/Stock|Flow|`) は無傷。

- 田中さん運用: AIOS (Stock + Flow + mini-tachyon) を継続
- 検証用: GbrainOS (Brain 一本 + published/) を並列保持
- 学習が進んだら、田中さん本人の AIPM を案C に進化させるかは別判断

---

## 7. ファイル一覧（重要なものだけ）

```
~/aipm_v0/GbrainOS/Brain/
├─ RESOLVER.md             # 決定木
├─ schema.md               # テンプレート集
├─ index.md                # カタログ
├─ people/
│  ├─ tanaka.md           # owner
│  ├─ iitake.md           # 飯武さん（4/29 確定: mini-tachyon NO / LLM auto-rewrite YES / Flow NO）
│  └─ ohchi.md            # 大地さん
├─ companies/
│  └─ restaurant-ai-lab.md
├─ programs/                              # 9 ファイル
│  ├─ RestaurantAILab.md   (16 projects)
│  ├─ 作業効率化.md          (8 projects)
│  ├─ 定型作業.md            (3 projects)
│  ├─ 生活管理.md            (3 projects)
│  ├─ リライフメディカル.md   (2 projects)
│  ├─ むしめがね.md          (5 projects)
│  ├─ ゴール管理.md          (1 project)
│  ├─ 0.Other.md             (3 projects)
│  └─ 本業.md               (1+ project)
├─ projects/                              # 43 ファイル
│  ├─ AIOS.md
│  ├─ AI-Core.md
│  ├─ AI-Core_飯武さん導入.md
│  ├─ ...（全 Stock プロジェクト分）
└─ published/             # 空（PoC 段階）
```

---

## 8. 次アクション

1. 田中さんレビュー → 構造方針（特に Stock 原本維持 vs 取り込みの方針）が OK か確認
2. BL-0002 で Phase 1b 実装に進む（GBrain CLI 動作確認 / publish-snapshot skill / 配布パッケージ化）
3. 田中さん本人の AIPM (案C 移行) は別タスクで時期判断

---

## 9. 田中さんへの問い返し

1. **Stock 原本を Brain に複製しないでメタ反映に留めた**方針で OK か？（深いリンク辿りは Stock を見る前提）
2. **published/ の運用** — 過去に外部に渡した固定版を遡及的に published/ に登録するか、4/29 以降の新規分のみか？
3. **BL を Brain に出さない**判断 — 飯武さん配布版で BL 相当の意思追跡をどうするか別途検討要
4. **People / Companies の充実** — 過去議事録などから enrich を回すか、第一回前にどこまでやるか

これらの決定によって BL-0002 Phase 1b の検証スコープを最終確定。
