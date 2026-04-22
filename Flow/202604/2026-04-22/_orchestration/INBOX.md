# 田中さんの未対応事項 — 2026-04-22

最終更新: 2026-04-22 15:30（BL-0053 AIOS+G-Brain統合 要件詰め：スコープ案+質問を🟡に追加）
- ✍️ 回答記入欄の `> ` の行に直接書き込んでください
- 完了したらチェック `[x]` を入れてください

---

## 🔴 緊急（今日中）

### BL-0037 PONチャット履歴: 計画完了 → 実装前に4点確認 🆕 2026-04-22 15:15

📌 状況: 計画ドキュメント完成（`Flow/202604/2026-04-22/バンコクPonさん案件/implementation_plan.md`）。Step4バッチは ended / 25 succeeded 待機中。ユーザー承認 + 下記4点回答で即着手できます。

📝 関連ファイル:
- 計画書: [implementation_plan.md](../バンコクPonさん案件/implementation_plan.md)
- 背景メモ: [discovery_notes.md](../バンコクPonさん案件/discovery_notes.md)

#### Q1-target-tool. PONさんが使う想定のAIツールは？ [設計に影響] 🆕

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
> 

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
> 

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
> 

---

#### Q4-scope-today. 本日のスコープはどこまで？ [進め方に影響] 🆕

選択肢:
- (A) **Phase1 (Step4 deploy) + Phase2 (ナレッジソース生成) + Phase3 (案内+送付) を全部今日中**
- (B) 今日は **Phase1 + Phase2 まで**、送付は明日以降
- (C) 今日は **Phase1 (Step4 deploy) のみ**、Phase2以降は後日
- (D) 田中さんに任せる（AI側で効率的に進める）

📌 AI推奨: (B)。理由: Phase2のBatch待ちで合計3〜4h見積、Phase3（案内+送付方法確定）は送付前の目視確認含めて明日以降の方が品質が出る。最短なら(A)も可能だが送付判断が夜になる。

✍️ 回答記入欄:
> 

---

### マイナンバー: 発見したオンライン申請URLの正体確認（申請実行の前段） 🆕 2026-04-22 14:00

- 📌 状況: 以前発行のURLにアクセス済。ただし「失効後再交付」に使えるかはURL種別・発行時期で決まる。以下3問で判定可能
- 📌 回答後: URLで申請OKと確認できれば、スマホ約20分で申請完了（写真撮影5分 + 入力10分 + 完了）

#### Q-url-domain. URLのドメインは何ですか？ [ブロッカー] 🆕

URLの先頭部分（例: `https://net.kojinbango-card.go.jp/...`）だけでOK

選択肢:
- (a) `net.kojinbango-card.go.jp` → J-LIS公式申請サイト（本命）
- (b) `mynumbercard.point.soumu.go.jp` → マイナポイント用（**申請には使えない**）
- (c) `myna.go.jp` → マイナポータル（**申請には使えない**）
- (d) その他 → URLを貼ってください

✍️ 回答記入欄:
>オンライン申請完了しました net.kojinbango-card.go.jp

---

#### Q-url-screen. URLにアクセスして、最初に表示された画面は？ [ブロッカー] 🆕

選択肢:
- (a) メールアドレス入力画面（申請開始できる画面）→ ✅ そのまま申請実行OK
- (b) 申請書ID入力画面
- (c) 「すでに申請済」「受付終了」などのエラー画面 → 別ルート必要
- (d) その他 → スクショ or 画面の文言を教えてください

✍️ 回答記入欄:
>完了済みです

---

#### Q-url-date. URLはいつ発行されたものですか？ [参考] 🆕

前回のカード作成時のURL/QRコードか、最近マイナポータル等で発行したものか

✍️ 回答記入欄:
>ー

---

- 📝 関連ファイル: [雑事/mynumber_renewal_action.md](../雑事/mynumber_renewal_action.md)
- 📌 副次: BL-0014 確定申告は新カード到着まで1〜2ヶ月かかるので**書面提出**に切替を強く推奨

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

### BL-0061 AI-Core PL 実装: Notion DB 2つ作成 + Integration 接続 依頼 🔄 2026-04-22 15:30（UI デプロイ完了・Notion 接続待ち）

📌 **現在の状況**: Phase 1 の コード＋UI デプロイまで完了。🎉
- **公開URL（UIプレビュー）**: https://ai-core-pl.vercel.app/
- GitHub: https://github.com/RestaurantAILab/ai-core-pl
- Vercel: `restaurant-ai-lab/ai-core-pl` （既存ダッシュボードと同 team）
- 動作確認済:
  - ✅ トップページ / 50事例カタログ表示 / フィルタ / チェック選択 / 送信バー
  - ✅ `/api/cases` → 50件の JSON を返す
  - ⚠️ `/api/submit` → `NOTION_TOKEN is not set` で 500（期待動作・下記 Notion 接続で解消）

📌 **次にお願いしたいこと**: Notion 側の DB 2 つを作成 → 発行された token / DB ID を下に貼り付け → 受領後エージェントが seed + env 投入 + 本番再デプロイ（残 1h 程度）。

#### Q-notion-db. Notion 側の DB 作成 + Integration Connect [ブロッカー] 🆕

以下 3 ステップで所要 15〜20 分程度です（計画書 §4 にスキーマあり）。

**ステップ 1. Internal Integration を作成**
1. https://www.notion.so/my-integrations を開く
2. 「新しいインテグレーション」→ 名前: `AI-Core PL`、関連付けるワークスペースを選択
3. Capabilities: Read / Update / Insert content にチェック
4. 発行される `secret_xxxx...` を控える（これが `NOTION_TOKEN`）

**ステップ 2. 2つの DB を作成（計画書 §4.1 / §4.2 のスキーマで）**

- **事例一覧 (ServiceCases)**: Title / ID(Number) / Category(Select) / Status(Select) / Difficulty(Number) / Roles(Multi-select) / Tools(Multi-select) / Frequency(Multi-select) / Pain(Rich text) / WhatAIDoes(Rich text) / DataFlow(Rich text) / FrequencyLabel(Rich text) / Effect(Rich text) / ToolsLabel(Rich text) / PriceJpy(Number)
- **クライアント依頼 (ClientRequests)**: Title / SubmittedAt(Date) / ClientName(Rich text) / Contact(Rich text) / Segment(Select: restaurant/b2b_saas/other) / Notes(Rich text) / SelectedCases(Relation → 事例一覧) / Status(Select: 未対応/対応中/提案済み/完了/クローズ) / InternalNote(Rich text)

※ Select の選択肢は空でOK（値投入時に自動追加される。ただし Status の「未対応」だけ先に作っておくと安全）。

**ステップ 3. 両 DB に Integration を接続**
各 DB のページを開き、右上「・・・」→「コネクション」→「AI-Core PL」を追加。

**ステップ 4. 以下 3 点を回答記入欄に貼り付け**（`database_id` は DB フルページを開いた URL の `https://www.notion.so/<workspace>/XXXXXXXXXXXXXXXX?v=...` の `XXXXXXXXXXXXXXXX` 32桁）

✍️ 回答記入欄:
> NOTION_TOKEN=（secret_... を貼り付け）
> NOTION_DB_CASES=（事例一覧 DB の ID を貼り付け）
> NOTION_DB_REQUESTS=（クライアント依頼 DB の ID を貼り付け）

📌 受領後のエージェント側作業: `npm run seed`（50事例を Notion に upsert）→ Vercel に env 投入 → `vercel deploy --prod` で本番再デプロイ → 送信ボタンが Notion に Insert することを確認してお渡し（残 1h 想定）

📝 参考ファイル:
- 計画書: `Flow/202604/2026-04-22/AI-Core/implementation_plan.md` §4, §6
- 実装コード: `~/RestaurantAILab/ai-core-pl/scripts/seed-notion.mjs`
- 進捗ログ: `Flow/202604/2026-04-22/AI-Core/implementation_log.md`

---

### BL-0062 低速タキオン（会議後ToDo生成）要件詰め 🆕 2026-04-22 15:00

📌 状況: 既存Tachyon資産の棚卸し完了（discovery_notes.md）。要件確定のため以下7問にご回答ください。実装計画は回答受領後に確定版を出します。

📝 関連ファイル: [Tachyon/discovery_notes.md](../Tachyon/discovery_notes.md)

#### Q1. 「低速」の遅延許容度は？ [設計前提] 🆕

選択肢:
- (a) 会議close直後に自動起動（数分以内に出る）
- (b) 時間単位でOK（当日中に出れば良い）
- (c) 翌営業日でOK（夜間バッチでも可）

📌 AI推奨: **(a)**。close時自動起動の方がユーザー体験が連続的で忘れにくい。バッチ化は後からいつでもできる。

✍️ 回答記入欄:
> 

---

#### Q2. 入力ソースは？ [ブロッカー] 🆕

「Notion Meeting連携が理想」のメモがあったため、「Notion Meeting」が何を指すかも併せて教えてください。

選択肢:
- (a) 既存Tachyonの `live.md` を使う（STTで生成済みトランスクリプト）
- (b) Notion Meeting から取得する（→ Notion Meeting の正体を以下で補足）
- (c) (a)(b) の両対応（抽象レイヤーを作る）

📌 AI推奨: **(a) をまず実装 → 動作確認後に (b) を追加**。既存資産を最大活用できる最短ルート。

**「Notion Meeting」の正体（該当するものにチェック）:**
- [ ] Notion AI Meeting Notes（Notion公式AIの議事録機能）
- [ ] 手動で運用しているNotion DBのページ（自分で書く議事録）
- [ ] BL-0063 OMI連携で将来Notionに入ってくるもの
- [ ] その他（欄に記入）

✍️ 回答記入欄（Q2選択 + Notion Meeting正体）:
> 選択: 
> Notion Meetingの正体: 

---

#### Q3. ToDoの出力先は？ [ブロッカー] 🆕

選択肢:
- (a) Notion DB のみ（チーム共有はNotionで）
- (b) AIPM Backlog.md のみ（AIOSで一元管理）
- (c) Notion DB + AIPM Backlog 両方（マスターはどちらか決める必要あり）
- (d) Notion DB + 既存Tachyonの `todos.json` にも（UI表示用）

📌 AI推奨: **(c) Notion DB をマスター、AIPM Backlog にミラー（日次で同期）**。チーム視認性（Notion）とAIOS運用（Backlog）を両立。ただし同期設計がやや重い。シンプルにいくなら (a)。

✍️ 回答記入欄:
> 

---

#### Q4. 起動トリガーは？ [設計前提] 🆕

選択肢:
- (a) 会議close時に自動起動（Tachyonの `/api/close` がフックする）
- (b) 手動キック（UIにボタン or CLIコマンド）
- (c) cron定期実行（1日1回、closed未処理会議をまとめて）
- (d) (a)+(b) 併用（通常は自動、失敗時に手動再実行）

📌 AI推奨: **(d)**。自動で走りつつ、落ちたら手動で再走できる安全網。実装量は (a) 単独とほぼ変わらず。

✍️ 回答記入欄:
> 

---

#### Q5. 実装場所は？ [ブロッカー] 🆕

選択肢:
- (a) 既存Tachyonリポ内の新モジュール（`~/tachyon-workspace/tachyon/lib/slow-agent.ts` + 新API）
- (b) `~/tachyon-workspace/projects/slow-tachyon/` として独立Next.jsアプリ
- (c) AIPMリポ内のCLI/スクリプト（Next.js不要、Node.jsバッチ）

📌 AI推奨: **(a)**。データ所在が同一で実装最短。既存UIに自然統合できる。Notion連携も既存設定（`settings.json`）を拡張する形で入れやすい。

✍️ 回答記入欄:
> 

---

#### Q6. ToDo投入前の人間レビューは？ [運用設計] 🆕

選択肢:
- (a) LLMが生成したら即Notionに投入（自動運用、誤抽出は人間が後から削除）
- (b) ドラフト状態でUIに表示 → ユーザーが承認したものだけNotionへ（リアルタイム版と同じフロー）
- (c) 一次レビューは田中さん、その後Notionに入って町田・吉田共有

📌 AI推奨: **(b) → 数回回して精度を見たら (a) に緩める**。最初は既存Tachyonのapprove/skipフローを再利用、安定したら自動投入に。

✍️ 回答記入欄:
> 

---

#### Q7. ToDoのメタ情報はどこまで抽出する？ [スコープ] 🆕

既存ToDoスキーマ: title / description / priority / category / assignee? / recommendedAction / sourceText

選択肢:
- (a) 最小限（title / description / sourceText / priority のみ）
- (b) 担当者 (assignee) + 期限 (dueDate) も抽出（会議発言から推定）
- (c) (b) + プロジェクト分類（AIPM MasterIndex.yamlと照合して Program/Project を付与）
- (d) (c) + AIPM Backlogのフォーマット（BL-ID / Program / Project / keywords）に整形

📌 AI推奨: **(c)**。担当者・期限は会議発言から十分に抽出可能で価値が高い。MasterIndex照合はAIPMナレッジ参照モードが既にあるため実装コスト低。BL-ID発番 (d) は BL-0049（タスク管理システム接続）のスコープとして後送りが整理しやすい。

✍️ 回答記入欄:
> 

---

（回答後、`implementation_plan.md` を確定版にします。追加の前提質問が出たら同じセクションに🆕で追記します）

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
