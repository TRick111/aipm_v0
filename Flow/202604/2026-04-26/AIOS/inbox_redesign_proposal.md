# INBOX 設計の再検討 — Cockpit 統合 + 対応優先度の可視化

- BL: BL-0067（INBOX設計の再検討 — Cockpit統合＋対応優先度の可視化）
- 作成日: 2026-04-26
- ドラフト Status: unreviewed
- 関連 BL: BL-0046（定期タスク設計見直し）, BL-0053（AIOS+G-Brain 統合）, BL-TBD-005/006/007/009/010（ミニタキオン 進行中シリーズ）
- 背景: 2026-04-22 振り返り — 「エージェントが田中さん回答待ちで止まっているのに意識から外れ、進まない」事象。プロジェクト跨ぎの切替コストが本質要因

---

## 1. 現状 INBOX 分析

### 1.1 「INBOX 機能」が分散している場所

| # | 場所 | 形式 | 主な用途 | 認知単位 | 田中さんから見える？ |
|---|---|---|---|---|:-:|
| 1 | `Flow/<date>/_orchestration/INBOX.md` (legacy) | Markdown 散文 + `## BL-XXXX` 見出し | エージェントから田中さんへの質問・回答待ち | BL 1個 = 1セクション | ❌（廃止スコープ。4/22 が最終生成） |
| 2 | ミニタキオン own BL.yaml の `pending_questions[]` | YAML 配列 | エージェントから田中さんへの質問 (schema v2) | Q 1個 = 1要素 | △（BL 詳細ページで開かないと見えない） |
| 3 | 中央 `Backlog.md` の Notes 列 | Markdown 表 1セル | BL の状況サマリ・回答待ち情報の混在 | BL 1個 = 1行 | ◯（一覧で見える、ただし Q として分離されていない） |
| 4 | `Flow/<date>/_orchestration/今日のタスク案.md` | Markdown Q.0-Q.7 | 朝の整理時の田中さん判断 | 1日分の Q 集合 | ◯（朝のループで触る） |
| 5 | `Flow/<date>/_orchestration/確認事項.md` | Markdown 散文 | 朝の done 承認後に追加発生する確認事項 | 当日のスナップ | ◯（unreviewed でホーム表示） |
| 6 | `Flow/<date>/<Project>/<file>.md` 中の「✍️ 回答記入欄」 | Markdown 散文 | 各プロジェクトのドラフト中で AI が田中さんに尋ねる箇所 | ファイル 1個 = N か所 | ❌（ファイルを開かないと見えない） |
| 7 | ミニタキオン UI の `/bl/[id]` AI フィードバック textarea | UI フォーム | 田中さんからエージェントへの指示 | BL 1個 = 1テキスト | ◯（BL 単位） |

→ **田中さん向けの問いは少なくとも 7 か所に物理分散している**。「自分が答えるべきもの」だけを抜き出す装置は実質 #4・#5（朝/夕の deliverable）と #2（BL 詳細）の 3 か所のみ。

### 1.2 見出しベースのステータス付与の限界（legacy INBOX.md の構造的弱点）

`INBOX.template.md` を見ると 1 BL = 1 セクションで、見出し横に状態タグ（🆕 / ⏸ / ✅ / ❌ など）を付けて運用していた。これには次の限界がある:

1. **粒度が BL**: 1 つの BL に Q が 5 個あっても見出しは 1 つ。「Q1 だけ回答済、Q2-Q5 が回答待ち」が表現しづらい。実際に 4/22 INBOX.md でも BL-0053 の Q1〜Q5 が一括 `[ブロッカー・最優先]` として並ぶ形になり、田中さんが「次に答えるべき1問」を選ぶ判断が常にトップに乗る。
2. **滞留時間（年齢）が見えない**: Q 単位の created_at がないので「いつから止まっているか」が分からない。4/22 振り返りの「意識から外れる」現象の直接原因。
3. **優先度が手動**: BL 自体の Priority (P0-P3) しかない。「Q を答えれば 2 エージェントが解凍される」のような Q-blast-radius が表現できない。
4. **散文ゆえ機械処理しにくい**: 表セル内禁止記号 (`|`) や見出しレベルの揺れで、UI 側で「全 Q 横断ビュー」を組み立てるのが難しい。BL.yaml の `pending_questions[]` (schema v2) を作ったのはこの反省。
5. **日付ファイルに紐づく**: 4/22 の INBOX.md と 4/23 の INBOX.md は別物として運用されていた。プロジェクト跨ぎどころか「日跨ぎ」で内容が分断され、未回答が古い日付に取り残される。

### 1.3 既に進んでいる是正アクションの棚卸し

INBOX 課題に直接効く実装は実は **4/25 から既に走っている**。BL-0067 はそれらに「方針の言語化と統合の方向付け」を与える位置付けになる。

| 既存実装 | 状態 | INBOX 課題への効き |
|---|---|---|
| BL.yaml schema v2 (`pending_questions[]` 分離) | 完了 (4/25) | Q 単位の構造化を実現。1.2-(1)(4) を解決済み |
| INBOX.md / daily_tasks.md 廃止スコープ採用 | 確定 (4/25) | 散文 INBOX.md を機械処理可能な構造へ寄せる方針 |
| ミニタキオン Phase 3a (☀️ 朝の整理) | 完了・dogfood中 | 朝に当日の Q を一覧化する場を提供 (今日のタスク案.md) |
| ミニタキオン Phase 3b (🌙 夜の振り返り) | 実装完了・確認待ち | 残課題（未回答 Q）を当日中にもう一度可視化 |
| BL-TBD-009 (中央 Backlog.md 読込) | 実装完了・確認待ち | UI に全 active BL を載せた。1.1-#3 を読み込み済み |
| BL-TBD-010 (今日の選択フィルタ + /backlog) | 実装完了・確認待ち | 「今日触る BL のみ」の絞り込みを実現 |
| BL-TBD-006 (Phase 3c 承認後自動更新) | 未着手 | 田中さん回答 → BL 自動更新の自動化 |

→ **本提案は新機能の押し付けではなく、既に動いている実装の上に「Q ファースト」の 1 ビューを足す形で着地させるのが筋**。

---

## 2. 課題の定式化

4/22 振り返りで観察された「エージェントが回答待ちで止まっているのに意識から外れる」事象を 4 つに分解する。

### 課題 P1: 「自分が今、答えるべき Q」が一望できない

- 物理分散 7 か所（§1.1）。横断クエリは現状ゼロ。
- 朝のタスク案 Q.0-Q.7 は当日生成されたものに限る。前日以前の Q は別ファイルに置き残されている。
- ホームに「📥 今、田中さんが回答すべき Q」という単一リストが無い。

### 課題 P2: Q の滞留時間（FIFO）が見えない

- Q ごとの created_at が一部しかない（pending_questions[] には入るが、INBOX.md / Notes 列には無い）。
- 「3 日前に来た Q」と「今朝来た Q」が同列に並ぶ。古いほど目立つ仕掛けが無い。
- 田中さん側の認知負荷: 「今日のもの」しか見ないと古い Q が永遠に放置される。

### 課題 P3: プロジェクト跨ぎで Q がロストする

- BL は所属プロジェクトの BL.yaml に格納される。プロジェクト切替コストが高い (Cursor を別フォルダで開き直すような UX)。
- 「PONさん月曜本番」で頭が一杯のとき、「飯武さん向け資料」の回答待ち Q は完全に脳から消える。
- ミニタキオンが「BL 単位」でなく「Q 単位」を中心に組み直されない限り、UI を見ても切替は強要される。

### 課題 P4: Q の優先度がブロッカー連鎖を反映しない

- Q が 1 つ答えられないと、その Q に依存する複数エージェントが全員凍る（例: BL-0053 Q2-gbrain 未回答 → BL-0066 飯武さん導入も実質ブロック）。
- 現在は BL の Priority しか持たないため、Q 自体の重要度（= 解凍する人数 / 解凍する金額）が表現されない。
- 結果: P0 BL の Q と P3 BL の Q が表示順で同じ重みになる。

### 解くべきもの（要件）

| Req | 内容 | 主に解く課題 |
|---|---|---|
| R1 | 全プロジェクト横断で「今、田中さんが答えるべき Q」を 1 リストに集約 | P1 / P3 |
| R2 | Q ごとの created_at を持ち、滞留時間でソート可能 | P2 |
| R3 | 上から順に答えていけば終わる FIFO 体験（モバイル最優先） | P1 / P2 |
| R4 | Q 単位の blast_radius（解凍する BL/エージェント数） を可視化 | P4 |
| R5 | 田中さんの回答が「BL の decisions[] / pending_questions[].answered_at」に自動反映される | P1 が再発しない |
| R6 | 既存の BL.yaml schema v2、ミニタキオン UI、中央 Backlog.md と整合 | （非機能要件） |

---

## 3. 設計案

3 つの案を出す。それぞれ「Q を 1 ビューに集約する場所」をどこに置くかが軸。

### 案 A: Cockpit に統合（pending_questions[] を 1 リストで集約 UI）

- **場所**: ミニタキオン UI のホーム上部（または専用ページ `/inbox`）に「📥 田中さんへの問い (N)」セクションを新設。
- **データソース**: 全 BL.yaml の `pending_questions[]` をスキャン → 1 リスト化。
- **データ構造（追加）**:
  ```yaml
  pending_questions:
    - id: q-20260422-bl0053-gbrain-scope    # 一意 ID
      created_at: 2026-04-22T10:30:00+09:00
      created_by: master-agent
      bl_id: BL-0053
      project: 作業効率化/AIOS
      title: G-Brain の実体・所在の確認
      body: |
        田中さんのローカルを探索したが G-Brain 本体は見当たらなかった ...
      blocker_for: [BL-0053, BL-0066]   # 解凍される BL 群
      priority: blocker                  # blocker / planning / nice_to_have
      answered_at: null
      answer: null
  ```
- **UI**:
  - リストは created_at 昇順（古いものが上）
  - 各行に「BL-XXXX / プロジェクト名 / 滞留 X 日 / blocker_for: 2BL」のメタ
  - タップで Q 詳細 + 回答 textarea。送信で `answered_at` セット → ミニタキオンが Cockpit task spawn して decisions[] へ反映
- **スコープ**:
  - ミニタキオン側: `/inbox` ページ + lib/pending-questions.ts + index-store 拡張
  - スキーマ: BL.yaml v2 → v2.1 に minor bump（pending_questions[].id, blocker_for, priority を追加）
  - 既存散文 INBOX.md / 「✍️ 回答記入欄」は段階的に pending_questions[] へ寄せる

### 案 B: 上から順に積み上がる FIFO 構造

- **場所**: 単一の `Stock/作業効率化/AIOS/inbox.md`（または `Flow/<date>/_orchestration/inbox.md`）に append-only で Q を追記。
- **形式**:
  ```markdown
  ## 2026-04-22 10:30 — BL-0053 G-Brain の所在 [BLOCKER for BL-0053, BL-0066]
  田中さんのローカルを探索したが G-Brain 本体は見当たらなかった...
  ✍️ 回答:
  >

  ## 2026-04-22 11:00 — BL-0067 INBOX 設計の方針 [PLANNING]
  ...
  ```
- 田中さんが上から順に回答記入欄に書き込めば自然に FIFO 消化。
- ファイルウォッチで「✍️ 回答:」の下に文字が入った Q を検出 → エージェントへルーティング。
- **スコープ**:
  - 単一ファイルなので実装最小（ファイルパースのみ）
  - スキーマ変更不要。ただし、機械処理は依然として「散文の見出しレベル一致」に依存

### 案 C: ハイブリッド（Cockpit 統合 + Markdown FIFO ビュー）

- **データの正本**: 案 A（pending_questions[] を BL.yaml 配下で構造化）
- **読みやすい view**: 案 B（生成された FIFO Markdown）を「ミニタキオン UI」と「Markdown ファイル」の両方で提供
- **書き込み**: ミニタキオン UI の textarea 経由（PC でも iPhone でも可）。Markdown ファイルへの直接編集も検出して同期（fallback）
- **構造（同じ）**: 案 A のスキーマを採用。FIFO Markdown は generator 出力なので削除しても再生成可能
- **UI**:
  - ホームに「📥 今、田中さんが答えるべき (N)」（案 A の 1 リスト）
  - サブビューとして「📜 INBOX 履歴」（過去回答済も含めた append-only ストリーム、案 B 風）
  - 個別 Q ページ（深掘りリンクや関連 BL/エージェント表示）
- 実質 BL-TBD-005/009/010 の延長線で実装可能

---

## 4. 各案のメリ / デメ + 実装コスト

| 観点 | 案 A: Cockpit 統合 | 案 B: FIFO Markdown | 案 C: ハイブリッド |
|---|---|---|---|
| **横断 1 リスト (R1)** | ◎ pending_questions[] を全 BL から集約 | ◎ 単一ファイルなので構造的に 1 リスト | ◎ |
| **滞留時間ソート (R2)** | ◎ created_at が構造化 | ◯ 見出しの YYYY-MM-DD HH:MM をパース | ◎ |
| **FIFO 体験 (R3)** | ◯ UI で sort 順制御 | ◎ ファイルそのものが FIFO | ◎ |
| **blast_radius / 優先度 (R4)** | ◎ blocker_for[] フィールド | △ 見出し横の `[BLOCKER for ...]` 散文 | ◎ |
| **回答自動反映 (R5)** | ◎ answered_at フィールド + Cockpit task | △ ファイル変更検出 → 各 BL 反映が複雑 | ◎ |
| **既存整合 (R6)** | ◎ schema v2 の minor bump で済む | △ 別経路を持つことになり二重管理リスク | ◎ |
| **モバイル UX** | ◎ ミニタキオン UI と一体 | △ Markdown は iPhone でも開けるが回答 UX が劣る | ◎ |
| **学習コスト** | △ 構造を意識する必要 | ◎ 「ファイルに書くだけ」 | △ 同左 |
| **エージェント側の書きやすさ** | ◯ YAML 編集（schema 厳守ルール既存） | △ 散文の見出し規約に依存 | ◯ |
| **実装工数** | M（中。ミニタキオン に1ページ + lib + schema bump） | S（小。1ファイル + watcher） | M-L（A をベースに view を1枚足す） |
| **長期メンテ** | ◎ 構造化されているので拡張しやすい | △ 散文は割れ窓化しやすい | ◎ |

### 実装コスト概算

| 案 | 工数 | 主な作業 |
|---|---|---|
| A | 1〜1.5 日 | スキーマ minor bump、`/inbox` ページ、index-store 拡張、Q 単位の write-back、vitest |
| B | 0.5 日 | inbox.md 仕様、watcher、回答検出ロジック |
| C | 1.5〜2 日 | A の作業 + 履歴ストリームページ + Markdown export generator |

---

## 5. 推奨案 + 段階導入計画

### 推奨: **案 C（ハイブリッド）**を 3 段階で。

理由:

1. **データは案 A の構造で持つ**のが正解。BL.yaml schema v2 で既に `pending_questions[]` を導入済みで、進化方向と整合する。散文 INBOX.md の限界（§1.2）は構造化でしか解けない。
2. **見せ方は案 B の FIFO 体験**を取り入れる。田中さんの「上から順に答えれば終わる」感覚は P2/P3 を解く心理的レバー。
3. ハイブリッドが嫌うのは「実装が増える」点だけだが、view layer は generator なので捨てやすい。**正本データを案 A で固めた瞬間にロールバック可能性が確保される**。

### Phase 0（先行：今日中〜明日）— 田中さん意思決定の準備

- [ ] 本提案 (`inbox_redesign_proposal.md`) を unreviewed として deliverable 化（**本タスクで実施**）
- [ ] 田中さんレビュー → 案 A/B/C のどれで行くか確定
- [ ] 確定後、BL-0067 を `doing` のまま keep（実装は Phase 1〜）

### Phase 1（小: 0.5〜1 日）— Q 単位の構造化を確立 (案 A の最小コア)

- [ ] BL.yaml schema v2 → v2.1: `pending_questions[]` に `id`, `blocker_for[]`, `priority` を additive 追加（既存データの後方互換性は維持）
- [ ] 既存 4/22 INBOX.md の Q を pending_questions[] へ手動移行 (BL-0053 の Q1〜Q5 / BL-0028 Q-final / BL-0065 Q1-4 など)
- [ ] ミニタキオン `lib/pending-questions.ts` 新規（全 BL.yaml をスキャンして Q[] を返す）
- [ ] vitest（パース 5+ ケース）

### Phase 2（中: 1 日）— ホーム統合 (案 A の UI)

- [ ] ミニタキオン ホームに「📥 今、田中さんへの問い (N)」セクション追加
- [ ] BL-TBD-010 の「今日の選択」と並ぶ第 2 セクションに（情報過多にしないため、デフォルト最大 5 件 + 「もっと見る」）
- [ ] 各 Q 詳細ページ `/inbox/[qid]`（または BL 詳細内の Q ピン留め）で回答 textarea
- [ ] 回答送信 → Cockpit task spawn → 該当 BL の `pending_questions[].answered_at` & `decisions[]` に append
- [ ] iPhone 動作確認（Tailscale 越し）
- [ ] 既存「✍️ 回答記入欄」フォーマットは併存させ、徐々に Q 化

### Phase 3（小: 0.5 日）— FIFO 履歴ビュー (案 B 風)

- [ ] `/inbox/history` で append-only の Q ストリーム（回答済含む）を時系列降順で表示
- [ ] エクスポート: `Flow/<date>/_orchestration/inbox_history.md`（generator 出力、人間が Markdown で読める）
- [ ] 「📚 過去の運用」(BL-TBD-007) と統合可能なら統合

### Phase 4（中: BL-TBD-006 と統合）— 自動化

- [ ] 朝のタスク案 done 承認時の自動更新ロジック（BL-TBD-006 既存）に「pending_questions[].answered_at セット」も含める
- [ ] Q ごとに `blocker_for[]` を自動算出するヒューリスティクス（pending_questions[] への参照を関連 BL から逆引き）
- [ ] 1 週間 dogfood して「意識から外れて止まる」事象がゼロになるか観測

### 各 Phase の ROI（4/22 振り返り事象が消えるか）

| Phase | 「自分が答えるべき Q がパッと見えない」 | 「FIFO で消化できない」 | 「プロジェクト跨ぎでロスト」 |
|---|:-:|:-:|:-:|
| 0 | — | — | — |
| 1 | △（データ構造のみ） | — | △ |
| 2 | ◎（ホームに 1 リスト） | ◯（古い順ソート） | ◎ |
| 3 | ◎ | ◎（履歴ビュー） | ◎ |
| 4 | ◎ | ◎ | ◎ + 再発防止 |

→ **Phase 2 完了時点で 4/22 振り返りで挙がった核心課題は実用的に解消される**。

### 本提案を採用しない場合のリスク

- 飯武さん導入 (BL-0066, 4/30 セッション) で AI が「田中さんに確認」を多発する。回答経路が分散していると新規メンバー（飯武さん）にも見せにくい。
- BL-0046（定期タスク設計見直し）が完了してもタスクは増える方向。Q も増える。今、構造化しないと数か月後に「散文 INBOX 群島」が固定化する。

---

## 6. ミニタキオンとの関係（BL-TBD-* シリーズとの整合性）

### 既に走っている / これから走る BL-TBD と本提案の対応

| BL-TBD | 内容 | 状態 | 本提案との関係 |
|---|---|---|---|
| BL-TBD-005 (Phase 3b 🌙 夜の振り返り) | 完了・確認待ち | 既存 | 「今日の Q が消化されたか」をラップアップで点検する出口になる。本提案の Phase 3 履歴ビューと相互補完 |
| BL-TBD-006 (Phase 3c cron + 承認後自動更新) | 未着手 | 既存 | 本提案 Phase 4 を内包する。BL-TBD-006 のスコープに「pending_questions[].answered_at 更新」を追加する形で統合 |
| BL-TBD-007 (Phase 3d 「📅 今日の運用」+「📚 過去の運用」) | 未着手 | 既存 | 本提案 Phase 3 の `/inbox/history` を「📚 過去の運用」配下にネストさせる方が UI が散らばらない |
| BL-TBD-009 (中央 Backlog.md 読込) | 完了・確認待ち | 既存 | 本提案 Phase 1 で「全 BL.yaml + 中央 Backlog.md Notes 列の両方から Q を吸い上げる」仕様の前提として活きる |
| BL-TBD-010 (今日の選択 + /backlog) | 完了・確認待ち | 既存 | ホームの「📥 田中さんへの問い」は BL-TBD-010 の「🔥 今日の選択」と並列配置（情報量バランス考慮） |
| BL-TBD-008 (Phase 3a v3) | 完了・確認待ち | 既存 | 朝のタスク案の Q.0-Q.7 を、本提案 Phase 1 の pending_questions[] に「当日 Q として登録」する経路を追加 |

### 整合性のポイント

1. **データの正本は BL.yaml 配下**: 中央 Backlog.md は別経路だが Notes 列は人間 view、pending_questions[] が機械処理の正本。BL-TBD-009 の方向（Backlog.md は read-only ソースとして mini-tachyon が読む）と整合。
2. **新 BL の起票は不要（推奨）**: BL-0067 を本タスク・本提案で進め、Phase 2/3/4 の実装段階で BL-TBD-011 (INBOX 統合 ホーム) のような子タスクを起こすのが筋。BL-TBD-006/007 のスコープは拡張で吸収できる。
3. **schema 衝突回避**: pending_questions[] の minor bump は BL-TBD-009 のパースを壊さない（追加フィールド only）。BL-TBD-006 の自動更新パスに「answered_at セット」を追加するだけで済む。
4. **モバイル前提**: ミニタキオン UI は iPhone (Tailscale) 体験が主役。回答 textarea は iPhone でも快適に書ける粒度（1 Q = 1 textarea）に保つ。

### 本提案を進めることでミニタキオン スコープが膨らみすぎないか？

- 膨らまない理由: ミニタキオン は 4/25 設計確定時点で **「INBOX.md / daily_tasks.md を廃止し、ミニタキオンが代替する」** スコープを採っている（STATUS.md L33）。本提案はそのスコープに対する具体実装で、新規スコープ拡張ではない。
- リスク: ミニタキオン own BL (BL-TBD-*) の数が今後 + 1〜2 増える。許容範囲（既に 10 BL 進行中）。

### BL-0046（定期タスク設計見直し）との関係

- BL-0046 は「毎月の請求書発行のような繰り返しタスクをどう Backlog 化するか」がスコープ。
- 本提案は「単発の Q をどう構造化するか」がスコープ。
- 接点: 定期タスクが生成する Q（例: 「今月分の請求書送付しましたか？」）も pending_questions[] に乗る形にすれば、BL-0046 完了後の自動 Q 生成と本提案の集約 UI が直結する。
- 実装順序: 本提案 Phase 1〜2 を先に → BL-0046 が定期タスク仕様を固める時に「Q を pending_questions[] にどう吐くか」が前提として既に存在する状態になる（順序メリット大）。

---

## 付録 A: BL.yaml schema v2.1（提案差分）

```yaml
# 既存 (v2)
pending_questions:
  - title: <string>
    body: <string>
    created_at: <ISO8601>
    created_by: <agent name>

# 提案 (v2.1) — 追加フィールドのみ。既存読み込みはすべて後方互換
pending_questions:
  - id: q-<yyyymmdd>-<bl-slug>-<topic-slug>   # 追加: 一意 ID
    title: <string>                            # 既存
    body: <string>                             # 既存
    created_at: <ISO8601>                      # 既存
    created_by: <agent name>                   # 既存
    blocker_for: [BL-XXXX, ...]                # 追加: 解凍する BL 群（任意）
    priority: blocker | planning | nice_to_have  # 追加: Q 単位優先度（デフォルト planning）
    answered_at: <ISO8601 | null>              # 追加: 回答済の場合 set
    answer: <string | null>                    # 追加: 田中さんの回答本文
    answered_via: ui | markdown | cli          # 追加: 回答経路
```

## 付録 B: 4/22 振り返り発生事象を再現させない for ループ

```
[朝 8:30] ☀️ 起動 → 当日 Q.0-Q.7 が pending_questions[] に登録される
   ↓
[ホーム表示] 📥 今、田中さんへの問い (5)
   - 3 日前から: BL-0053 G-Brain 所在 [BLOCKER for BL-0053, BL-0066]  ← 滞留 3 日
   - 今朝: Q.5 BL-0014 確定申告書類リスト [PLANNING]
   ...
   ↓
[田中さん] 上から 1 件タップ → 回答送信
   ↓
[自動] BL.yaml に answered_at + answer + decisions[] が append
   ↓
[凍ってたエージェント] watcher 検出 → 解凍、作業再開
   ↓
[夜 22:00] 🌙 夜の振り返り → 「今日 N 件解凍した / 残 M 件」 を表示
```

→ ホームを開いた瞬間に「答えるべきものがある」が一目で分かる。プロジェクト跨ぎの切替コストはゼロ。

---

## 付録 C: 田中さんレビュー観点

本ドラフトを確認後、ミニタキオン上で needs_revision / done のいずれかで返してください。観点:

1. 案 A/B/C のうち推奨 (案 C) でよいか、または別案希望
2. Phase 1〜4 の段階導入順は妥当か（Phase 2 まで急ぐ必要があるか / Phase 4 までやり切るか）
3. BL-TBD-006/007 にスコープを内包する vs. 新 BL-TBD-011 を立てる、どちらの実装単位を好むか
4. schema v2.1 の追加フィールドで懸念があるか（特に `priority: blocker | planning | nice_to_have` の語彙）
5. 4/22 振り返りで観察された事象以外で、INBOX に求める要件が漏れていないか
