# 田中さんの未対応事項 — 2026-04-22

最終更新: 2026-04-22 16:00（BL-0037 Q1-Q4回答反映・Phase1完了・v2計画でPhase2着手中・Q5/Q6追加）
- ✍️ 回答記入欄の `> ` の行に直接書き込んでください
- 完了したらチェック `[x]` を入れてください

---

## 🔴 緊急（今日中）

### BL-0037 PONチャット履歴: Phase1完了→Phase2実行中・送付時にQ5/Q6必要 🔄 2026-04-22 16:00

📌 **状況サマリ**:
- Q1-Q4 回答反映済み（Q1=Cursor+AIOS / Q2=GitHub private / Q3=マスク無し / Q4=今日中）
- **Phase 1 完了**: Step4 process (25/25成功) → deploy 済み（`Stock/.../ChatGPT移行/` に 478 MD 配置）
- **計画を v2 にピボット**: ChatGPT Projects向け → **AIOS Program「ChatGPT履歴」×4 Projects** 構造へ
- **Phase 2 着手中**（AIOS再パッケージ + LLM合成バッチ送信予定）

📝 関連ファイル:
- v2計画書: [implementation_plan.md](../バンコクPonさん案件/implementation_plan.md)
- 背景メモ: [discovery_notes.md](../バンコクPonさん案件/discovery_notes.md)

以下 Q5/Q6 は **Phase 3（送付）直前**に必要。先行タスク (S3〜S8) は回答待たずに並行で進めます。

#### Q5-repo-name. GitHub private リポジトリ名 [送付時必要] 🆕

AIOS Program「ChatGPT履歴」を丸ごと入れる private repo を作成します。

選択肢:
- (a) `pon-chatgpt-knowledge` （英語・明確）
- (b) `pon-aios-chatgpt-archive` （AIOS標準を強調）
- (c) `rios-innovation-knowledge-base` （会社名・拡張性）
- (d) その他 → 記入

📌 AI推奨: (c) `rios-innovation-knowledge-base`。理由: 今後のAIOS拡張（ChatGPT以外の知識も入る）を考えると会社名ベースが長期的に便利。

✍️ 回答記入欄:
> 

---

#### Q6-gh-invite. PONさんのGitHubアカウント [送付時必要] 🆕

PONさんの GitHub username / email を教えてください（Collaborator招待に使用）。

選択肢:
- (a) username を知っている → 記入
- (b) email を知っている → 記入（GitHub招待メール送信）
- (c) PONさんに直接聞いてから回答
- (d) 田中さん所有 repo にpush、田中さんから PONさんへZIP/リンクで送付（運用を一部変更）

✍️ 回答記入欄:
> 

---

#### 以前の Q1-Q4（✅ 回答済み 2026-04-22 15:45 受領）

| Q | 回答 |
|---|---|
| Q1 投入先 | **Cursor + AIOS** / Stock の Program+Project 形式で保存 |
| Q2 送付 | **(3)** GitHub private repo + 招待 |
| Q3 秘匿 | **(a)** マスキング不要 |
| Q4 スコープ | **(A)** Phase1+2+3 今日中 |

→ v2計画書に反映済み。詳細回答は下部アーカイブ参照。

---

<details>
<summary>Q1-Q4 回答詳細（クリックで展開）</summary>

#### Q1-target-tool. PONさんが使う想定のAIツールは？ [設計に影響] ✅

ファイルの粒度・命名・まとめ方が変わります。

選択肢:
- (a) ChatGPT Plus の **Projects機能** にまとめてアップロード → 新規スレッドから呼び出し
- (b) **Custom GPT** を1つ作って知識ファイルとして登録
- (c) **NotebookLM** にソース登録
- (d) **Claude Projects** に登録
- (e) 複数併用（例: a + d）
- (f) 不明 → 汎用的（どれでも流用可）な粒度で作成

📌 AI推奨: (a) ChatGPT Projects。理由: PONさんは現在ChatGPTユーザー、Projects機能ならzipアップロードで13ファイル全部扱える、最も移行ロスが少ない。

✍️ 回答記入欄:
>Cursorです。そのため、私の今やっているAI-PMのシステムをPonさんも使っています。今回作成しているアウトプットは、ストックの中にプロジェクトとプログラムという形で保存するのが最終ゴールです。 

---

#### Q2-delivery. PONさんへの送付方法の希望は？ [送付に影響] 🆕

選択肢:
- (1) **Google Drive 共有フォルダ** → URL送付（gws CLI で自動化可、更新も楽）
- (2) **Zip添付**（LINE/メール）
- (3) **GitHub private repo** → PONさん招待
- (4) **Notion ページ化**
- (5) 田中さん側で都度配布（出力物だけ用意してこちらで留める）

📌 AI推奨: (1) Google Drive。理由: ファイル13個・総量<1MB・今後の更新再共有が楽・PONさん側の受取障壁が最小。

✍️ 回答記入欄:
> 3

---

#### Q3-privacy. 秘匿性のレベル（スタッフ実名・給与額のマスキング）は？ [生成物品質に影響] 🆕

過去会話にはスタッフ氏名（RISA/Kozue/Hiroto COO 等）や具体的な給与額・コミッション率が多数含まれます。

選択肢:
- (a) **マスキング不要**（PONさん本人向けなので原文のまま）
- (b) スタッフ名だけ伏字化（例: PLE → スタッフA）
- (c) 給与・金額も伏字化
- (d) その他 → 要望を記入

📌 AI推奨: (a) マスキング不要。理由: 返却先がPONさん本人、マスクすると活用時の情報欠落が致命的。第三者共有が発生する場合のみ(b)以上を検討。

✍️ 回答記入欄:
> A

---

#### Q4-scope-today. 本日のスコープはどこまで？ [進め方に影響] 🆕

選択肢:
- (A) **Phase1 (Step4 deploy) + Phase2 (ナレッジソース生成) + Phase3 (案内+送付) を全部今日中**
- (B) 今日は **Phase1 + Phase2 まで**、送付は明日以降
- (C) 今日は **Phase1 (Step4 deploy) のみ**、Phase2以降は後日
- (D) 田中さんに任せる（AI側で効率的に進める）

📌 AI推奨: (B)。理由: Phase2のBatch待ちで合計3〜4h見積、Phase3（案内+送付方法確定）は送付前の目視確認含めて明日以降の方が品質が出る。最短なら(A)も可能だが送付判断が夜になる。

✍️ 回答記入欄:
> A

</details>

---

（マイナンバー申請完了 ✅ — `net.kojinbango-card.go.jp` でオンライン申請済み。新カード到着待ち。詳細は ✅ 完了セクション参照。副次対応: BL-0014 確定申告は新カード到着まで1〜2ヶ月かかるので書面提出を強く推奨）

---

## 🟡 確認・判断（時間ある時）

### BL-0028 睡眠デバイス: デバイス確定は保留中

#### Q-final. Vivoactive 6 で確定？ [ブロッカー・保留中] 🔄 2026-04-22 14:30 追加データ反映

最終推奨: **Garmin Vivoactive 6 ¥39,800**（5年TCO ¥49,800、23g軽量、24h装着OK）

選択肢:
- (a) Vivoactive 6 で確定
- (b) Venu 4 にする（体温センサーあり、+¥40k）

📌 AI推奨: (a) Vivoactive 6。Q6優先軸（コスト>連携>精度）に最も整合。

🆕 **新データポイント（2026-04-22 14:30 追加調査結果）**:
- **Garmin → Apple Health の同期項目は steps / workouts / heart rate / sleep が中心**
- **体温（skin / wrist temperature）は Apple Health に同期されない**（Garmin 公式サポートで確認）
- → **Venu 4 を選んでも、AIOS パイプラインに体温は流れない**（Garmin Connect アプリ内でのみ参照可）
- → Venu 4 の体温センサーが活きるのは「Garmin Connect アプリで毎日体温を目で見る」用途のみ
- → 「AIOS にデータを集約したい」が動機の Venu 検討なら、その動機は成立しない
- 📝 詳細: [健康管理/sleep_device_final_comparison.md §7.5](../健康管理/sleep_device_final_comparison.md)

⚖️ **判断軸の整理**:
- **Vivoactive 6 を選ぶ理由**: 5年TCO¥40k安、23g軽量、Q6優先軸に最適、AIOSパイプライン上Venuと差なし
- **Venu 4 を選ぶ理由**: Garminアプリ内で体温トレンドを見たい、AMOLED画面・所有感、+¥40k許容

✍️ 回答記入欄:
> Venuが欲しいけど、一旦考えを寝かせます（決定は明日以降）

📌 エージェントへの指示: デバイス確定を待たず、他3点（iPhone / Vercel / HAE許容）の前提で BL-0030 の事前準備を進める。事前準備設計書: [健康管理/bl0030_integration_prep.md](../健康管理/bl0030_integration_prep.md) で Health Auto Export 設定 / Vercel Webhook 雛形 / DB候補（推奨: GitHub commit）/ 動作確認手順を整備済み。デバイス到着後すぐ連携開始可能。

---

（実装着手GOいただき、別タスク `3b95ee3a` を `~/RestaurantAILab/` で起動済み。実装中に追加質問があればこの🟡セクションに「BL-0061 AI-Core PL 実装」見出しで追加されます）

---

### BL-0062 低速タキオン（会議後ToDo生成）要件詰め ✅ 完了 2026-04-22 16:05（全Q回答済 → 計画 v1.0 確定）

📌 状況: **Q1〜Q9 全回答受領 → `implementation_plan.md` v1.0 確定完了**。次は実装フェーズ起動（前提: Notion Integration + DB作成の準備）。

📝 成果物: [Tachyon/implementation_plan.md](../Tachyon/implementation_plan.md)（Phase1工数 14〜17h）

#### 🗂 確定サマリ（v1.0 要点）

| 項目 | 決定 |
|---|---|
| 実装場所 | 既存Tachyon (`~/tachyon-workspace/tachyon/`) に機能追加 |
| 入力(Phase1) | `live.md` + テキストアップロード(.md/.txt) |
| 入力(Phase2) | Notion AI Meeting Notes 直接取込 |
| トリガー | close時自動 + 手動再実行（5分以内要件） |
| ToDoスキーマ | title / 詳細 / 完了条件 / 関連プロジェクト / AI作業内容 / AI作業の完了条件 |
| レビュー | **案B** Tachyon UI事前レビュー（承認/編集/スキップ/実行） |
| 実行 | **Anthropic SDK直接**（Tachyon内軽量エージェント、単一エンジン） |
| 結果保存 | **Tachyon内 + Notion 両方**（AIPM Flowには保存しない） |
| 失敗時 | UIエラー表示 + 手動再実行（自動リトライなし） |

#### 🔜 次アクション依頼: Notion DB作成

実装着手前に、AI-Core PL と同じ段取りで以下をご準備ください（所要 10〜15分）:

1. **Notion Integration** を作成（名前: `Tachyon Slow Todos`、Capabilities: Read/Update/Insert） → `secret_xxxx...` を控える
2. **Notion DB「Meeting ToDos」** を作成（スキーマは計画書 §6 参照）
3. DBにIntegrationをコネクション追加

✍️ 準備完了後 or 「実装着手 BL-0062」の指示をいただければ、実装タスクを別エージェントで起動します:
> 

---

（質問詳細アーカイブ: 以下 ✅ 回答済み Q1〜Q9 を保存。過去参照用）

#### ✅ Q1〜Q9 回答一覧（アーカイブ）

| # | 質問 | 回答 |
|---|---|---|
| Q1 | 遅延許容 | 会議終了後5分以内 |
| Q2 | 入力ソース | Notion Meeting = Notion AI Meeting Notes、提案希望 → Q2-revへ |
| Q3 | 出力先 | Tachyon UI + 実行ボタン + 結果保存、最終Notion or AIPM → Q8/Q6-revへ |
| Q4 | トリガー | 自動＋アップロード、提案希望 → Q9へ |
| Q5 | 実装場所 | 既存Tachyonに機能追加 |
| Q6 | レビュー | 案比較希望 → Q6-revへ |
| Q7 | メタ情報 | title / 詳細 / 完了条件 / 関連プロジェクト / AI作業内容 / AI作業の完了条件 |
| Q2-rev | Notion AI連携時期 | OK（(a) Phase1はアップロード経由、Phase2でNotion直接連携） |
| Q6-rev | レビューフロー | B（Tachyon UI事前レビュー） |
| Q8-a | 実行エンジン | 2（SDK直接、単一エンジン） |
| Q8-b | 結果保存先 | 3（Tachyon + Notion 両方） |
| Q8-c | 失敗時挙動 | 1（UIエラー + 手動再実行） |
| Q9-a | アップロード形式 | 1（テキストのみ） |
| Q9-b | アップロードUI | 1（新規会議として作成） |
| Q9-c | Notion URL取込 | 1（当面なし、エクスポートMDを通常アップロードで） |

---

#### Q2-rev. Notion AI Meeting Notes の連携タイミング [方針] ✅ (a)=OK

（詳細は上の ✅ Q1〜Q9 回答一覧に集約。元の選択肢は履歴アーカイブとして以下に残置）

選択肢:
- (a) **Phase1 は `live.md`+アップロードのみ → Phase2 で Notion AI Meeting Notes 追加**（段階導入）
- (b) **最初から Notion AI Meeting Notes もサポート**（実装コスト +1〜2h、Notion API の議事録取得実装が必要）
- (c) **Notion AI Meeting Notes をメイン入力にする**（Tachyon録音は補助。既存アーキテクチャと役割が逆転）

📌 AI推奨: **(a)**。理由:
- Q4の回答で「既存ツールの文字起こしアップロード」が要件化されたため、アップロード機能は必須→ Notion AI Meeting Notes の中身（マークダウン）もアップロードで代用可能
- Notion AI Meeting Notes の API 取得は「Notion Meeting ページ」の構造に依存（AIブロックのプロパティ探索が必要）、実装が重め
- まず `live.md` + アップロードで動かし、運用で Notion AI 連携の優先度を見極めるのが効率的

✍️ 回答記入欄:
> OK

---

#### Q6-rev. タスクレビューフロー 3案比較 ✅ B

| 案 | フロー | 長所 | 短所 |
|---|---|---|---|
| **A: Notion投入後レビュー** | LLM生成 → 即Notion投入（Status=未レビュー） → Notionで田中さんが approve / edit / delete → approveで Status=未着手 | チーム共有がシンプル（投入時点で可視化）、Notion運用に馴染む | Notionを開かないとレビューできない、却下タスクがNotionに履歴として残る、実行ボタンをNotion上に作るのは困難 |
| **B: Tachyon UI事前レビュー** | LLM生成 → Tachyon UIにドラフトカード表示 → 田中さんが approve / edit / skip / 実行 → approveでNotion投入、skipは破棄 | 会議直後にTachyon UIで完結、不要タスクはNotionに流れない、**実行ボタンもTachyon UIに統合しやすい（Q3との親和性高）** | Tachyon UIを開く必要、チーム共有は approve後 |
| **C: ハイブリッド（高confidenceのみ自動）** | confidence≥0.8 → Notion自動投入 / <0.8 → Tachyon UIでレビュー必須 | 手間最小、重要タスクは必ず人間チェック | 閾値調整が必要、confidence精度の初期検証が必要（数回運用してから決めるのが現実的） |

📌 AI推奨: **案B で開始 → 精度が安定したら案C へ進化**。理由:
- Q3で「Tachyon UIで実行／しない選択 → 実行 → 結果保存」が要件化されているため、UIに集約する案Bが最も自然
- Notionを「既に人間レビュー済みの確定ToDoリスト」として扱えるので意味付けがシンプル
- 案A は Notion側にワークフロー（Status遷移＋実行ボタン）を組む必要があり、Tachyon UI と Notion の責務分離が曖昧になる

✍️ 回答記入欄:
> Bでいきます。

---

#### Q8. タスク実行フロー詳細設計 ✅ (a=2 / b=3 / c=1)

Q3で新要件として「実行ボタン → AIがタスク実行 → 結果保存」が追加された。既存Tachyonのリアルタイム版は `projects/` 配下にNext.jsアプリを作る方式だが、低速タキオンのタスクは会議後のToDoなので**性質が異なる**（調査・ドキュメント作成・メール文面など非開発系も多い）。

##### Q8-a. タスクを実行するのは誰（どのエージェント）？

選択肢:
- (1) **既存 Claude Code CLI モード**（現在のTachyonの実行エージェントと同じ、CockPit経由）
- (2) **Tachyon内の新しい軽量エージェント（Anthropic SDK直接呼び出し）** — 短時間・単発タスク向け
- (3) **AGI Cockpit経由で別タスク起動**（`./task create`）— 大規模・多段階タスク向け
- (4) **(2)+(3) ハイブリッド**（短時間系はSDK直接、大規模系はCockpit）

📌 AI推奨: **(4)**。ToDoの `category`（text/document/code/app/research）で自動振り分け。Q7のスキーマに `executionMode` フィールドを追加。短時間調査はSDKで即結果、アプリ開発はCockpitへ。

✍️ 回答記入欄:
> ２

##### Q8-b. 実行結果の保存先

選択肢:
- (1) **Tachyon内のみ**（`data/meetings/{id}/todos.json` に result 追記、タスク結果ページで表示）
- (2) **Notionの元ToDoレコードに紐付け**（Notionページ本体に結果を書き込み、またはrelation）
- (3) **(1) と (2) の両方**（Tachyonが一次保存、Notionに同期）
- (4) **AIPMのFlow配下に成果物として保存**（`Flow/YYYYMM/YYYY-MM-DD/MeetingTodos/{todoId}/`）

📌 AI推奨: **(3) + (4) 条件付き**。短時間テキスト結果は (3)（TachyonとNotionに同期）、AIPMに関わる成果物（設計ドキュメント等）は (4) にも保存してFlowに入れる。

✍️ 回答記入欄:
> ３

##### Q8-c. 実行失敗時の挙動

選択肢:
- (1) UIにエラー表示、手動で再実行
- (2) 自動リトライ3回 → 失敗で (1)
- (3) エラーをNotionに別レコードとして起票（人間に知らせる）

📌 AI推奨: **(1)**。最初はシンプルに。運用で再実行率が高ければ (2) を追加。

✍️ 回答記入欄:
> １

---

#### Q9. 文字起こしアップロード機能 仕様提案 ✅ (a=1 / b=1 / c=1)

Q4で「外部の文字起こしツールの結果もアップロードで実行できるようにしたい」との要望。以下の仕様を提案します。

##### Q9-a. 受付ファイル形式

選択肢:
- (1) **テキスト（.md/.txt）のみ**（外部ツールで既に文字起こし済みのものを投入）
- (2) **音声ファイル（.m4a/.mp3/.wav）も受付**→Tachyon内部で OpenAI STT にかけてテキスト化
- (3) **両対応**（テキストが最優先、音声はバックアップ）

📌 AI推奨: **(3)**。テキストなら即処理（5分要件に余裕）、音声もSTTパイプラインが既にあるので追加コスト低。ただし音声は長時間だとSTT時間が5分を超える可能性あり → 音声アップロードは「ToDo生成完了までの時間保証なし」と注記。

✍️ 回答記入欄:
> １

##### Q9-b. UIとデータモデル

選択肢:
- (1) **新規「会議」として作成**（status=closed即設定、live.mdにtranscript投入、meta.jsonに `source: "upload"` を記録）→ 通常の会議と同じ「close後ToDo生成」フローに合流
- (2) **既存会議に追加**（transcript差し替え / 追記）
- (3) **専用の「外部取り込み」タブを分離**（UIを別にし、会議とは別の一覧で管理）

📌 AI推奨: **(1)**。既存フローと合流できるので実装最小、履歴もダッシュボードで一覧できる。`meta.json.source` で区別すれば運用上困らない。

✍️ 回答記入欄:
> １

##### Q9-c. Notion AI Meeting Notes からのインポート機能は？（Q2-revと連動）

選択肢:
- (1) **当面なし**（Notion側でエクスポートしたMarkdownをQ9の通常アップロードで投入）
- (2) **Notion URL 貼り付けで自動取得**（Notion API でページ取得→transcript化）

📌 AI推奨: **(1)**。Q2-rev Phase1 と整合。(2) は Phase2 で追加。

✍️ 回答記入欄:
> １

---

（4件（Q2-rev / Q6-rev / Q8a/b/c / Q9a/b/c）回答後、`implementation_plan.md` を v1.0 に書き換えます）

---

### BL-0053 AIOS+G-Brain統合: スコープ案選定 + 前提確認 🆕 2026-04-22 15:30

📌 状況: 「AIOSアップデート（G-Brain統合 + ルール全体見直し）」の **要件詰めフェーズ**。現状AIOSルールの棚卸し（`.cursor/rules/aios/` 配下 17ファイル）と G-Brain 所在探索を完了。スコープが未定義のため、まず **スコープA/B/C から1つ選んで** ほしい。関連前提は Q2〜Q5 に分けて置いてある（Q2は実質ブロッカー）。

📝 関連ファイル:
- 探索メモ: [AIOS/discovery_notes.md](../AIOS/discovery_notes.md)
- スコープ3案比較: [AIOS/scope_proposal.md](../AIOS/scope_proposal.md)

#### Q1-scope. スコープA/B/Cのどれを採用しますか？ [ブロッカー・最優先] 🆕

（詳細・メリデメは `scope_proposal.md` 参照）

選択肢:
- (A) **最小** — G-Brain統合の "型" だけ定義（新ルール1本追加、既存は触らない）。**半日〜1日**。BL-0054 を早く動かしたい場合向け
- (B) **中間** — G-Brain統合 + 03/12 の責務重複解消 + 05/06統合 + テンプレ整理 + マルチリポ運用の正式ルール化。**2〜3日**。現状のモヤモヤも解消
- (C) **最大** — AIOS再設計（メタリポ+実体リポの多層モデル、Index v2、Migration含む）。**1〜1.5週間**。OMI/Tachyon/G-Brain を同時期に全部乗せる想定

📌 AI推奨: **(B) 中間**。理由:
1. `12_parallel_task_orchestration` が直近追加で `03_daily_task_planning` と責務重複（`questions_to_user.md` 仕様・INBOX一次受け）が発生。放置するとエージェント挙動のブレが出る
2. BL-0054（共用リポ設計・doing）が AIOS 側のマルチリポ運用の型を待って止まっている。案Aでは設計制約が不十分
3. 案Cは "今後AIOSを1年以上使う" 前提のコミットメントが重い。(B) で整えて1〜2ヶ月運用してから (C) 判断が安全

✍️ 回答記入欄:
> （A / B / C のどれか、または独自スコープの希望）

---

#### Q2-gbrain. G-Brain の実体・所在を教えてもらえますか？ [ブロッカー] 🆕

田中さんのローカル（`aipm_v0` / `~/RestaurantAILab/` / `~/RestaurantAILab/Markdowns-1/`）を探索したが **G-Brain 本体は見当たらなかった**。大地さん（町田大地さん）側のはずなので、以下どれに該当しますか？

**タクソノミー**（複合可）:
- (α) **AI向けルール/プロンプト集**（Cursor rules / Claude Code instructions 等）
- (β) **コード共有ライブラリ**（npm / pip パッケージ）
- (γ) **ナレッジ/ドキュメント集**（Markdown、事例・ノウハウ・テンプレ）
- (δ) **ツール/スクリプト集**（CLI / automation）
- (ε) 複合 / 不明 / 大地さんに聞かないと分からない

**所在**:
- [ ] GitHub（URL: ___）
- [ ] 大地さんのローカルのみ
- [ ] 田中さんのローカルのどこか（パス: ___）
- [ ] その他

📌 AI推奨: (ε) になりそうなら **本タスクのスコープ確定前に大地さんに15分だけヒアリング**。観点のたたき台は discovery_notes.md §2.3 のタクソノミー表。

✍️ 回答記入欄:
> （分類＋所在。「大地さんに要ヒアリング」でも可）

---

#### Q3-daichi. 大地さんの稼働はいつ取れますか？ [方針確定] 🆕

G-Brain の実体特定／統合方針すり合わせに大地さんの時間が必要。特に案B/C で重要。

選択肢:
- (a) 今日〜明日中に30分取れる
- (b) 今週中に取れる
- (c) 来週以降
- (d) すぐには取れない → AIOSは **田中さん単独で済む範囲（案A相当）まで先に着地** させる

📌 AI推奨: (d) の場合は **案A先行 → 大地さん合流時に案B着手** の段階運用が無難。

✍️ 回答記入欄:
> 

---

#### Q4-compat. 既存ルール (`.cursor/rules/aios/`) の後方互換性はどう扱いますか？ [方針確定] 🆕

ルール本文や命名規則を変えると過去分 Flow/Stock が新ルールに違反する状態になりうる。

選択肢:
- (a) **過去分は現状維持**、新規分だけ新ルール適用（軽い）
- (b) 過去分も一括マイグレーション（重い・案C寄り）
- (c) ルール変更は最小限にとどめ、互換性問題を発生させない（案A寄り）

📌 AI推奨: **(a)**。過去の Flow/Stock は履歴として固定、ルール変更の効果は新規分から。

✍️ 回答記入欄:
> 

---

#### Q5-multirepo. マルチリポ運用（PONさん案件方式）を AIOS 正式ルールに昇格しますか？ [方針確定] 🆕

BL-0061（AI-Core PL）で発生した「aipm_v0 はメタ（Stock/README/ProjectIndex/log）、実体は別リポ（`~/RestaurantAILab/ai-core-pl/`）」パターン。同じ構造が BL-0054 / BL-0063 でも発生見込み。

選択肢:
- (a) **昇格する**（案Bの標準オプション。ops/14 として新設）
- (b) 当面は非公式のまま、3例以上発生してから検討
- (c) 別方式に倒す（例: 全リポを aipm_v0 サブモジュール化）

📌 AI推奨: **(a)**。既に BL-0061 で動いており、BL-0054 の設計制約にも直結。早めに正式化が安全。

✍️ 回答記入欄:
> 

---

（Q1〜Q5 回答後 → `implementation_plan.md` 確定版を起票し `waiting_confirmation` で承認依頼します）

---

## 🟢 待機中（自分側のアクション不要）

### BL-0060 Claude Code アップデート
- 📌 現在の状況: Native Installer 切替を実施中（待つだけ）
- 📝 関連ファイル: 環境整備/（作業中）

---

## ✅ 本日完了（参考）

### BL-0061 AI-Core PL: ✅ Phase 1 完全完了（Notion 接続 + 本番デプロイ + E2E 動作確認）🎉
- ✍️ 回答: `.env` に NOTION_TOKEN / NOTION_DB_CASES / NOTION_DB_REQUESTS を格納済み
- 📌 反映:
  - **公開URL（本番）**: https://ai-core-pl.vercel.app/  ← クライアント共有可
  - GitHub: https://github.com/RestaurantAILab/ai-core-pl（private）
  - Vercel: `restaurant-ai-lab/ai-core-pl`（既存ダッシュボードと同 team）
  - `npm run seed` で 50 事例を Notion ServiceCases に create 完了 / `data/case-page-map.json` をコミット
  - Vercel 本番に NOTION_TOKEN（sensitive）/ NOTION_DB_CASES / NOTION_DB_REQUESTS を投入
  - 本番 `/api/submit` → Notion ClientRequests へ Status=未対応 + SelectedCases relation 5件 で Insert を確認（page_id: 34abf91a-5716-81b0-...）
- ⚠️ 知見: Vercel は git commit の `committer` email が GitHub user に紐づかないと auto-deploy をブロックする（`readyStateReason: "GitHub could not associate the committer with a GitHub user"`）。`197918871+RestaurantAILab@users.noreply.github.com` を committer に設定して解決。今後の git push は同じ committer email を使用すること。
- 📝 ログ: `Flow/202604/2026-04-22/AI-Core/implementation_log.md`（全工程記録）
- 🔜 運用: Notion ClientRequests を `Status=未対応` でフィルタしたビューを朝開く運用（Slack 通知なし・v2.1 確定）

### BL-0017 マイナンバー: ✅ オンライン申請完了
- ✍️ 回答: net.kojinbango-card.go.jp で申請済み
- 📌 反映: Backlog ステータス done 化、新カード到着待ち（1〜2ヶ月）、BL-0014 確定申告は書面提出推奨を別途追記

### BL-0061 AI-Core PL: ✅ 実装着手GO + 計画フェーズ完了
- ✍️ 回答: 「実装にうつってください。Restaurant AI Labのフォルダ以下に作成して」
- 📌 反映: 計画タスク `86ab7e6d` 完了、実装タスク `3b95ee3a` を `~/RestaurantAILab/` で起動

### BL-0028 睡眠デバイス: iPhone/Webhook/HAE 3点確定
- ✍️ 回答: iPhone所有 / Webhook=Vercel / HAE\$24.99許容 / デバイスは保留
- 📌 反映: 3点の前提で BL-0030 事前準備を前倒し（13:50送信）

### BL-0061 AI-Core PL: Slack通知削除
- ✍️ 回答: Slack通知は不要
- 📌 反映: 実装計画 v2.1 で Slack 関連を削除、Notion運用に統一（13:50送信）
- ⏸ 残: 実装着手GOサインは再確認予定

### BL-0017 マイナンバー: Q1〜Q6 回答済み（過去）
- ✍️ 回答: 文京区 / 通知書なし / 両方期限切れ / 暗証番号両方記憶 / オンライン希望
- 📌 反映: エージェントが「失効後の再交付」方針に転換

### BL-0028 睡眠デバイス: Q1〜Q6 回答済み（過去）
- ✍️ 回答: A(必達)+RPA検討 / Ouraはサブスクで却下 / 24h装着 / コスト>連携>精度
- 📌 反映: Oura → Garmin に推奨変更

### BL-0060 Claude Code: Q1, Q2 回答済み（過去）
- ✍️ 回答: Q1=(1) Native Installer / Q2=(a) 手順書のみ
- 📌 反映: 切替実施中

### BL-0061 AI-Core PL: Q-A, Q-B, Q-C 回答済み（過去）
- ✍️ 回答: Q-A=(a) null / Q-B=Notion DB化 / Q-C=(b-1) PONさん案件方式
- 📌 反映: 実装計画 v2.0 確定

---

## 凡例

### 優先度
- 🔴 緊急（今日中に対応必要）/ 🟡 確認・判断（時間ある時）/ 🟢 待機中（アクション不要）/ ✅ 完了

### 情報種別アイコン
- 📌 推奨 / ❓ 確認 / ☎ 電話 / 📝 関連ファイル / 📄 追加参照 / 🔗 外部リンク / ✍️ 回答記入欄

### 質問の状態マーカー
- 🆕 新規 / ⏸ 既出・待ち / ✅ 回答済み / 🔄 再質問

## 関連
- 全体ダッシュボード: [`STATUS.md`](STATUS.md)
- 本日のタスク表: [`../0422_daily_tasks.md`](../0422_daily_tasks.md)
