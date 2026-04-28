# Brain Resolver — どこに何を置くかの決定木

すべての新規ページは作成前に**この決定木を辿り、primary home を一意に決定**する。これは MECE 制約。迷ったら inbox/ に置き、後で正規化する（schema を進化させるシグナル）。

---

## 決定木

```
新しい情報を保存したい
  ↓
Q1. 主題は何か（一つに絞る — 「人 AND 会社」ではなく primary な subject）

  人物（個人）            → people/<slug>.md
  組織・会社             → companies/<slug>.md
  金融取引・案件          → deals/<slug>.md
  特定日時のイベント記録    → meetings/<YYYY-MM-DD>-<topic>.md
  実際にビルド中のもの      → projects/<slug>.md     [repo / spec / team あり]
  着手前のアイデア          → ideas/<slug>.md
  教えられるフレームワーク   → concepts/<slug>.md     [200 語の蒸留]
  発展した散文・エッセイ     → writing/<slug>.md      [議論・物語・ドラフト]
  横断ワークストリーム      → programs/<slug>.md     [複数 project を束ねる]
  自組織の戦略・運用        → org/<slug>.md
  政治・政策              → civic/<slug>.md
  公開ナラティブ・コンテンツ運用 → media/<slug>.md
  私的メモ・健康・内省       → personal/<slug>.md
  家事運用                → household/<slug>.md
  候補者パイプライン        → hiring/<slug>.md
  生データ・bulk import    → sources/<slug>.md
  再利用 LLM プロンプト    → prompts/<slug>.md
  ★公開・配布した固定版     → published/<YYYY-MM-DD>-<slug>.md  [案F: snapshot freeze]
  分類できない・暫定         → inbox/<slug>.md     [後で再分類]
```

---

## 主要な分岐ルール（GBrain 標準 + 案F 拡張）

### Concept vs Idea
- **教えられる・知的フレームワーク** → concepts/
- **誰か実装すれば形になる** → ideas/

### Idea vs Project
- **誰も着手していない** → ideas/
- **現に着手中（repo / spec / team あり）** → projects/

### Writing vs Concept
- **発展した散文（議論・物語・ナラティブ）** → writing/
- **200 語の蒸留・要点メモ** → concepts/

### Writing vs Published（案F 固有）
- **自分が編集中・rewrite される可能性あり** → writing/
- **外部に渡した・公開した・凍結したい** → **published/**（immutable・rewrite 対象外）

### Person vs Company
- **人物として記述** → people/
- **組織として記述** → companies/
- 両方関連する場合は両方にページを作り、相互リンク（cross-reference）

### Project vs Program
- **単一のビルド対象** → projects/
- **複数の projects を束ねる人生・事業ワークストリーム** → programs/

---

## published/ の特別な扱い（案F）

- **immutable** — 一度書いたら rewrite しない（Brain の auto-update 対象外）
- ファイル名: `<YYYY-MM-DD>-<slug>-<version>.md`
- 各ファイルに `<filename>.lock` メタ情報（公開日 / 受領者 / ハッシュ）
- 内部編集中のドラフトは writing/ に置く
- writing/<slug> → published/<date>-<slug>-v1 のスナップショット時、writing/ 側は継続編集可

詳細: `published/README.md` 参照。

---

## Iron Law

1. **一つのエンティティ = 一つの primary home**（MECE）
2. **mention あれば必ず back-link を作る**（unlinked mention は broken brain）
3. **すべての fact に `[Source: ...]` 引用**
4. **新規ページ作成前に既存ページ検索**（重複防止）
5. **published/ は immutable**（案F 固有）

---

## 迷った時

inbox/ に置いて `# TODO: 再分類` と先頭にメモ。週次で見直して移す。inbox/ が増えてきたら schema 進化のサイン（例: 新カテゴリを top-level に追加）。
