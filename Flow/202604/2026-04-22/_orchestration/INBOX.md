# 田中さんの未対応事項 — 2026-04-22

最終更新: 2026-04-22 17:55（BL-0065 リライフメディカル予約システムデモ 新規追加）
- ✍️ 回答記入欄の `> ` の行に直接書き込んでください
- 完了したらチェック `[x]` を入れてください
- セクションは **BL ID 順**に並べ、状態を見出し横に明記

---

## BL-0017 マイナンバー再交付  [✅ 完了]

オンライン申請完了（`net.kojinbango-card.go.jp`）。新カード到着待ち（1〜2ヶ月）。
- 副次対応: BL-0014 確定申告は新カード到着まで1〜2ヶ月かかるので **書面提出** に切替を強く推奨
- ✍️ 回答履歴: 文京区 / 通知書なし / 両方期限切れ / 暗証番号両方記憶 / オンライン希望 → 失効後再交付方針へ転換、申請完了

---

## BL-0028 睡眠デバイス比較  [⏸ デバイス確定保留中]

最終推奨: **Garmin Vivoactive 6 ¥39,800**（5年TCO ¥49,800、23g軽量、24h装着OK）

#### Q-final. Vivoactive 6 で確定？ [ブロッカー・保留中] 🔄 2026-04-22 14:30 追加データ反映

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

✅ 過去回答: A(必達)+RPA検討 / Ouraはサブスクで却下 / 24h装着 / コスト>連携>精度 / iPhone所有 / Webhook=Vercel / HAE\$24.99許容

---

## BL-0037 PONチャット履歴ナレッジ化  [✅ 全Phase完了・残りPONさん招待のみ]

### 🎯 完了した作業（2026-04-22 17:00時点）

- ✅ **Phase 1 完了**: Step4 process (25/25) + deploy → `Stock/.../ChatGPT移行/` (478 MD)
- ✅ **Phase 2 再パッケージ完了**: AIOS Program `ChatGPT履歴/` 構築（4カテゴリ × 21 subcategories, 531ファイル）
- ✅ **機械生成完了**: `_overview/00_README.md` / `05_people_directory.md` / `06_artifacts_index.md`
- ✅ **LLM合成完了**: Batch `msgbatch_01Y5wVxibtXrPGQLufPSmUbQ` 11/11成功 → `_overview/` に11ファイル追加
  - 01_PON_persona / 02_business_overview / 03_decisions_log / 04_open_ideas / themes×7
- ✅ **GitHub push完了**: https://github.com/RestaurantAILab/pon-chatgpt-knowledge (private)
- ✅ **田中さん側 Stock log更新**: `Stock/.../AIOS提供/log.md` にBL-0037作業を追記済
- ✅ **AIPM準拠修正 (2026-04-22 17:00-17:15)**: ユーザー指摘を受けて以下を修正・再push
  - 21 サブカテゴリを **AIPM Project 化**（`conversations_index.json` → `ProjectIndex.yaml` 変換、`log.md` 追加）
  - `.cursor/rules/aios/templates/{ProjectIndex,log}.template.*` に準拠したフォーマット
  - カテゴリ folder（美容室/美容専門店/自社ブランド/J-Beauty）の `ProjectIndex.yaml` / `log.md` を **削除**（Projectではなく単なる束ねフォルダのため）
  - artifact ファイル名の `<8文字hex>_` プレフィックスを **439件全て除去**（md 431件＋docx/pdf/txt 8件、衝突回避のsuffix処理込み）
  - `README.md` / `conversations_summary.md` / `ProjectIndex.yaml` / `_overview/06_artifacts_index.md` の artifact参照を新ファイル名に一括更新
  - `MasterIndex_snippet.yaml` を Project=subcategory 単位（全21個）に再編
  - 生成スクリプト `repackage_to_program.py` をAIPM方針に合わせて修正＋実行順序ドキュメント化（`fix_aipm_compliance.py` を新規追加、全拡張子対応）
  - 検証: conversations_index.json=0 / hex prefix残=0 / category-level ProjectIndex.yaml=0 / Project-level ProjectIndex.yaml=21 ✅
  - GitHub に追加commit push（`b68a99a` / `044351b`、合計 **4 commits**、最終 **544 tracked files / 6.5 MB**）

### 📍 残り作業（田中さん側で実施）

#### 1. PONさんに送付文面を送信 （下記C参照）

#### 2. PONさんのGitHubアカウントが判明したら Collaborator招待 （下記B参照）

---

#### B. PONさん username確定後の Collaborator 招待コマンド

**PONさんのGitHub username/email が判明したら以下を実行してCollaborator招待してください:**

```bash
# username の場合（推奨）
gh api -X PUT \
  "repos/RestaurantAILab/pon-chatgpt-knowledge/collaborators/PONさんのusername" \
  -f permission=push

# email の場合（GitHubアカウント無ければ招待メール送信）
gh api -X POST \
  "repos/RestaurantAILab/pon-chatgpt-knowledge/invitations" \
  -f email=PONさんのemail
```

#### C. PONさんへの送付文面（案内ドキュメント・田中さん送信用）

下記をベースに適宜調整してLINE/メール送信してください:

> Pon社長
>
> ChatGPTで話した会話履歴を、Cursor + AIOS で「過去の話を踏まえて続きができる」形に整理しました。
>
> GitHub private リポジトリ: https://github.com/RestaurantAILab/pon-chatgpt-knowledge
>
> （Collaborator招待はPonさんのGitHubアカウント教えていただいた後に送ります）
>
> **使い方**:
> 1. リポジトリを `git clone` してローカルに配置
> 2. `ChatGPT履歴/` フォルダを PonさんのAIOSリポ `Stock/` 配下にコピー
> 3. `MasterIndex_snippet.yaml` の内容を `Stock/MasterIndex.yaml` にマージ
> 4. Cursorで新しいチャットを開き「Stock/ChatGPT履歴/_overview/01_PON_persona.md を読んで」と最初に指示
>
> リポジトリの `README.md` と `ChatGPT履歴/README.md` にも使い方書いてあります。
> ご不明点あれば聞いてください。

### 📝 成果物の場所

- **GitHub repo** (private): https://github.com/RestaurantAILab/pon-chatgpt-knowledge
- **ローカル出力** (参考): `Flow/202604/2026-04-22/バンコクPonさん案件/output/pon-chatgpt-knowledge/`
- **生成スクリプト**: `Flow/202604/2026-04-22/バンコクPonさん案件/scripts/`
  - `repackage_to_program.py` — Step4出力を AIOS Program 構造へ再パッケージ
  - `generate_mechanical.py` — `_overview/00/05/06` を機械生成
  - `build_overview_batch.py` — `_overview/01-04 + themes` を LLM合成 (Batch API)
  - `fix_aipm_compliance.py` — サブカテゴリを AIPM Project 形式化（必須の後処理）
- **Batch進捗**: `scripts/batch_work/batch_log.json`
- **田中さん側 基盤素材**: `~/RestaurantAILab/Markdowns-1/Stock/バンコクPonさん案件/AIOS提供/ChatGPT移行/`
- **v2計画書**: [implementation_plan.md](../バンコクPonさん案件/implementation_plan.md)
- **背景メモ**: [discovery_notes.md](../バンコクPonさん案件/discovery_notes.md)

### ⚠ 注意事項（田中さんへの引き継ぎ）

- リポジトリは **RestaurantAILab org 所有** で作成。もし TRick111 個人所有にしたい場合は `gh repo transfer RestaurantAILab/pon-chatgpt-knowledge TRick111` で移管可
- リポジトリには**スタッフ氏名・給与額・コミッション率が多数含まれる**（Q3の指示通りマスキングなし）。**絶対にpublic化しないこと**
- 「大地さん」は町田大地さん (Restaurant AI Lab AI担当) を指す

### ✅ 回答受領済み

| Q | 回答 | 反映 |
|---|---|---|
| Q1 投入先 | Cursor + AIOS | Program/Project構造採用 |
| Q2 送付方法 | (3) GitHub private repo | 実施済み |
| Q3 秘匿性 | (a) マスキング不要 | 原文ママ配置 |
| Q4 本日スコープ | (A) 全Phase今日中 | 進行中（Batch待ち） |
| Q5 repo名 | (a) `pon-chatgpt-knowledge` | 採用 |
| Q6 GHアカウント | (c) PONさんに確認後 | 田中さん側で後続対応（Bに手順） |

---

#### ✅ Q1-Q4 回答済（参考）

| Q | 回答 |
|---|---|
| Q1 投入先AIツール | Cursor + AIOS（Stockに Program/Project 形式で保存） |
| Q2 送付方法 | (3) GitHub private repo + 招待 |
| Q3 秘匿性 | (a) マスキング不要 |
| Q4 本日スコープ | (A) Phase1+2+3 今日中 |

---

## BL-0053 AIOS+G-Brain統合  [⏸ Q1〜Q5 回答待ち]

📌 状況: 「AIOSアップデート（G-Brain統合 + ルール全体見直し）」の **要件詰めフェーズ**。現状AIOSルール（17ファイル）の棚卸しと G-Brain 所在探索を完了。スコープ未定義のため、まず **スコープA/B/C から1つ選んで** ほしい。Q2 が実質ブロッカー。

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

## BL-0060 Claude Code アップデート  [🟢 実行中]

- 📌 現在の状況: Native Installer 切替を実施中（待つだけ）
- 📝 関連ファイル: 環境整備/（作業中）
- ✅ 過去回答: Q1=(1) Native Installer / Q2=(a) 手順書のみ

---

## BL-0061 AI-Core PL  [✅ Phase 1 完全完了]

🎉 **公開URL（本番）**: https://ai-core-pl.vercel.app/  ← クライアント共有可

- ✍️ 回答: `.env` に NOTION_TOKEN / NOTION_DB_CASES / NOTION_DB_REQUESTS を格納済み
- 📌 反映:
  - GitHub: https://github.com/RestaurantAILab/ai-core-pl（private）
  - Vercel: `restaurant-ai-lab/ai-core-pl`（既存ダッシュボードと同 team）
  - `npm run seed` で 50 事例を Notion ServiceCases に create 完了 / `data/case-page-map.json` をコミット
  - Vercel 本番に NOTION_TOKEN（sensitive）/ NOTION_DB_CASES / NOTION_DB_REQUESTS を投入
  - 本番 `/api/submit` → Notion ClientRequests へ Status=未対応 + SelectedCases relation 5件 で Insert を確認（page_id: 34abf91a-5716-81b0-...）
- ⚠️ 知見: Vercel は git commit の `committer` email が GitHub user に紐づかないと auto-deploy をブロックする（`readyStateReason: "GitHub could not associate the committer with a GitHub user"`）。`197918871+RestaurantAILab@users.noreply.github.com` を committer に設定して解決。今後の git push は同じ committer email を使用すること。
- 📝 ログ: `Flow/202604/2026-04-22/AI-Core/implementation_log.md`（全工程記録）
- 🔜 運用: Notion ClientRequests を `Status=未対応` でフィルタしたビューを朝開く運用（Slack 通知なし・v2.1 確定）
- ✅ 過去回答: 計画 v2.0/v2.1 確定（Notion DB化 / Slack 削除 / PONさん案件方式）

### 🔄 追加対応 (2026-04-22 PM3) — モバイルフィルター折りたたみ修正完了 [waiting_confirmation]

- **背景**: モバイル表示で `.filter-box`（役割/ツール/頻度/難易度 チップ）がビューポートの約9割を埋めていた（田中さん指摘）
- **実装**: `components/FilterBar.tsx` + `app/globals.css` のみ変更（フィルターロジック不変）
  - mobile (`<768px`) は default 折りたたみ・タップで展開。トグル行に「絞り込み [適用中バッジ] · N/M 件 · ▼」を表示
  - `aria-expanded` / `aria-controls` を付与（a11y）
  - desktop (`≥768px`) は現状維持（toggle 非表示・常時展開）
- **commit**: `e73bf41 feat(filter): collapsible filter bar on mobile`（committer: `197918871+RestaurantAILab@users.noreply.github.com`）
- **確認**: ローカル（390×844 / 1280×800 双方）と本番 https://ai-core-pl.vercel.app/ で default 折りたたみ・展開・バッジ表示・desktop 変化なし・console errors 0 を目視確認
- 📝 詳細: `Flow/202604/2026-04-22/AI-Core/implementation_log.md` §PM3

---

## BL-0062 低速タキオン（会議後ToDo生成）  [✅ Phase 1 完了 (2026-04-22)]

📌 状況: **Phase 1 完了**（2026-04-22 実装エージェントによる、計画通りP1〜P10達成）。全8コミット (`7e1f284`〜`c548019`) を `~/tachyon-workspace/tachyon/` main ブランチに積み、`next build` pass、実会議3件 + 破壊的ToDoテスト1件でE2E動作確認済。Notion DB `Tachyon ToDos` との投入・実行結果同期も動作確認。DoD 9項目すべて ✅。

📝 詳細: `Flow/202604/2026-04-22/Tachyon/implementation_log.md`（commit SHA一覧 / DoDチェック / Phase2候補 含む）

🆔 Notion 動作確認ページ:
- ChatGPTエクスポートデータ整形（approve）: pageId `34abf91a-5716-8196-a3cd-fe09ee3caca3`
- メールドラフト作成（execute→completed）: pageId `34abf91a-5716-8156-b97b-f0f596906dde`

⏭ 次アクション（Phase 2 候補・別BL起票推奨）:
- Notion AI Meeting Notes 直接取込（Q2-rev=(a) Phase2）
- confidence ベース自動承認（Q6-rev=C への進化）
- MCP 拡張（Figma / Canva / Playwright / Vercel）
- 30日TTL の作業ディレクトリ自動cleanup cron

📝 進捗ログ: `Flow/202604/2026-04-22/Tachyon/implementation_log.md`（実装エージェントが各Phase完了時に追記）

📝 成果物: [Tachyon/implementation_plan.md](../Tachyon/implementation_plan.md)（v1.1、Phase1工数 17〜20h）

#### 🗂 確定サマリ（v1.1 要点）

| 項目 | 決定 |
|---|---|
| 実装場所 | 既存Tachyon (`~/tachyon-workspace/tachyon/`) に機能追加 |
| 入力(Phase1) | `live.md` + テキストアップロード(.md/.txt) |
| 入力(Phase2) | Notion AI Meeting Notes 直接取込 |
| トリガー | close時自動 + 手動再実行（5分以内要件） |
| ToDoスキーマ | title / 詳細 / 完了条件 / 関連プロジェクト / AI作業内容 / AI作業の完了条件 |
| レビュー | **案B** Tachyon UI事前レビュー（承認/編集/スキップ/実行） |
| **実行（v1.1変更）** | **生成=SDK直接 / 実行=Claude Code CLI相当**（`@anthropic-ai/claude-agent-sdk` + bypassPermissions + allowedTools） |
| 結果保存 | **Tachyon内 + Notion 両方**（AIPM Flowには保存しない） |
| 失敗時 | UIエラー表示 + 実行ログ参照 + 手動再実行（自動リトライなし） |
| **作業ディレクトリ（v1.1追加）** | `~/tachyon-workspace/projects/slow-exec-{todoId}/`（隔離、30日TTL） |
| **タイムアウト（v1.1追加）** | 実行既定15分、超過で kill |

#### Q10. 実行時の allowedTools 範囲は？ ✅ B（中）

選択肢:
- (a) **最小** — `Read` / `Write` / `Edit` / `Glob` / `Grep`（作業dir内fs操作） + `WebFetch` / `WebSearch` のみ。Bash/MCP無し
- (b) **中（推奨）** — (a) + `Bash`（`gws` CLI / `gh` CLI 等を許可）+ Notion MCP + Google Drive MCP
- (c) **フル** — (b) + 田中さん環境のMCP全部（Figma / Canva / Playwright / Vercel 等）+ Bash全権限
- (d) **カスタム** — 欲しいツール/MCPを個別指定

📌 AI推奨: **(b) 中**。理由:
- スプレッドシート連携（gws sheets）・GitHub起票（gh）・Notion拡張操作・Drive参照が揃えば、会議ToDoの大半（調査・記録・連絡・リンク収集）は実行可能
- Figma/Canva/Playwright は会議ToDoで使うケースが稀、Phase2 で個別追加が素直
- `Bash` は破壊的コマンドをプロンプト + pre-tool-use hook でブロック

✍️ 回答記入欄:
> B

#### Q11. 実行の承認モードは？ ✅ A（bypassPermissions 全自動）

選択肢:
- (a) **bypassPermissions 全自動** — 承認ボタン押下後はツール使用も自動（Q6-rev=B の UI事前レビューで人間ゲート済と見なす）
- (b) **書込系のみ承認プロンプト** — `Bash`、ファイル `Write`、Notion書込、Sheets書込など副作用のあるツールだけ Tachyon UI で承認ステップ
- (c) **全ツール承認プロンプト** — 安全最優先、体験は重い

📌 AI推奨: **(a)**。理由:
- Q6-rev=B で承認時点にすでに人間が「このAI作業内容・完了条件で実行してよい」と判断している
- 実行後のツール呼び出しまで逐一承認すると会議後ToDoの意義（自動化）が薄れる
- 安全は allowedTools 範囲 (Q10) + プロンプト + pre-tool-use hook で担保する設計

✍️ 回答記入欄:
> A

#### ✅ 実装起動ブロッカー状況（全解消）

- [x] Notion Integration + DB 準備（.envに NOTION_TOKEN / NOTION_DB_ToDos 登録済）
- [x] v1.1 計画書 確定（Q10=B / Q11=A 反映済）
- [x] Q10 回答（B 中）
- [x] Q11 回答（A bypassPermissions 全自動）
- [x] **「実装着手 BL-0062」指示 → 別エージェント起動** (2026-04-22 完了)

✍️ 起動指示いただければ `~/tachyon-workspace/tachyon/` で実装フェーズを開始します:
> 

#### ✅ Q1〜Q9 回答済（アーカイブ）

| # | 質問 | 回答 |
|---|---|---|
| Q1 | 遅延許容 | 会議終了後5分以内 |
| Q2 | 入力ソース | Notion Meeting = Notion AI Meeting Notes |
| Q3 | 出力先 | Tachyon UI + 実行ボタン + 結果保存、最終Notion or AIPM |
| Q4 | トリガー | 自動＋アップロード |
| Q5 | 実装場所 | 既存Tachyonに機能追加 |
| Q6 | レビュー | 案B（Tachyon UI事前レビュー） |
| Q7 | メタ情報 | title / 詳細 / 完了条件 / 関連プロジェクト / AI作業内容 / AI作業の完了条件 |
| Q2-rev | Notion AI連携時期 | (a) Phase2でNotion直接連携 |
| Q6-rev | レビューフロー | B（Tachyon UI事前レビュー） |
| Q8-a | 実行エンジン | 2（SDK直接、単一エンジン） |
| Q8-b | 結果保存先 | 3（Tachyon + Notion 両方） |
| Q8-c | 失敗時挙動 | 1（UIエラー + 手動再実行） |
| Q9-a | アップロード形式 | 1（テキストのみ） |
| Q9-b | アップロードUI | 1（新規会議として作成） |
| Q9-c | Notion URL取込 | 1（当面なし、エクスポートMDを通常アップロードで） |

---

## BL-0065 リライフメディカル予約システム デモ作成  [🆕 新規・要件詰め待ち]

📌 **状況サマリ**: 田中さんから新規追加（17:55）。**リライフメディカル**の予約システムを新規構築するにあたり、まずはデモ（動くプロトタイプ）を作る。LPデザインは**仮**でOKだが、**カレンダー / 予約システム / スタッフ運用**の機能は実際に動く状態にする。

📝 関連:
- 既存プロジェクト: `Stock/リライフメディカル/` (Phase 1 PoC あり、Instagram投稿・台本生成アプリ系が中心)
- 今回は **新規プロジェクト**（予約システム）として扱う想定

---

#### Q1-scope. このタスクは今日着手しますか？ [ブロッカー] 🆕 2026-04-22 17:55

- (a) 今日中に要件詰め + 実装着手（エージェント起動）
- (b) 今日は要件詰めだけ、実装は別日
- (c) 明日以降に回す（追加のみ）

📌 AI推奨: (b)。既に他タスクが多く、要件詳細化（対象ユーザー・必要機能・技術スタック・デプロイ先）を整理してから実装の方が手戻りが少ない。

✍️ 回答記入欄:
> A

---

#### Q2-requirements. 必要機能・利用者像を整理するにあたり、以下の粒度でOKですか？ [方針確定] 🆕 2026-04-22 17:55

デモに必要と想定される機能:
1. **LP（仮デザインでOK）**: サービス紹介 + 予約への導線
2. **予約カレンダー**: 利用者が空き時間を見て予約枠を選択
3. **予約フォーム**: 利用者情報入力（氏名・連絡先・症状・希望日時）
4. **スタッフ運用画面**: 予約一覧閲覧 / 承認・キャンセル / シフト管理
5. **通知**: 予約確定時に利用者とスタッフへ（メール or LINE）

上記の過不足を教えてください。

✍️ 回答記入欄:
> ５は不要

---

#### Q3-stack. 技術スタックとデプロイ先の希望 [方針確定] 🆕 2026-04-22 17:55

- (a) 既存の Dashboard / AI-Core PL と揃える: Next.js + Prisma + Neon + Vercel（RestaurantAILab team）
- (b) リライフメディカル用の新規 Vercel team に置く（医療案件なので分離）
- (c) 別スタック希望（Supabase / Firebase 等）

DBの候補:
- 予約データは関係データが多い（予約↔スタッフ↔シフト↔顧客）ので **Postgres (Neon) 推奨**
- Notion運用は向かない（集計・重複チェックが必要なため）

✍️ 回答記入欄:
> デプロイ先は合わせたいです

---

#### Q4-pms. 関連する既存資産・参考にしたいもの [任意] 🆕 2026-04-22 17:55

- リライフメディカルの業務委託契約書やPoC文書が `Stock/リライフメディカル/` にあるが、予約システムに直接関連する資料はなさそう
- 参考にしたい既存の予約サービス（例: reserva / tol / coubic / airreserve 等）はありますか？
- 医療系ならではの要件（診察券番号 / カルテ連携 / 保険証 等）は今回のスコープに含めますか？

✍️ 回答記入欄:
> 今はありません

---



### セクション見出し横の状態タグ
- 🆕 新規 / 🟢 実行中 / ⏸ 回答待ち / 🔄 ループ中（ユーザー対応・エージェント作業を交互） / 🔵 計画完了（実装待ち） / ✅ 完了 / ❌ ブロック

### 情報種別アイコン
- 📌 推奨 / ❓ 確認 / ☎ 電話 / 📝 関連ファイル / 📄 追加参照 / 🔗 外部リンク / ✍️ 回答記入欄

### 質問の状態マーカー
- 🆕 新規 / ⏸ 既出・待ち / ✅ 回答済み / 🔄 再質問

## 関連
- 全体ダッシュボード: [`STATUS.md`](STATUS.md)
- 本日のタスク表: [`../0422_daily_tasks.md`](../0422_daily_tasks.md)
