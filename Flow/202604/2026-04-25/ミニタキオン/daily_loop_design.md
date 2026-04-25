# Daily Loop 設計 — ミニタキオンを 1 日の運用ハブにする

Generated: 2026-04-25 22:30
Status: DRAFT (田中さんレビュー待ち)
BL: BL-TBD-004 (ミニタキオン Phase 3: Daily Loop)

## 何をしたいか

田中さんは毎朝、複数プロジェクトを横断して「今日何をやるか」を整理している。現状は手作業 (頭の中 + AIPM ファイル確認)。

ミニタキオンに **「☀️ 今日を始める / 🌙 今日を締める」** ボタンを置き、朝/夜のタスク整理 自体を AI に投げて、その案を ミニタキオン上のレビュー物として承認するフローにする。

つまり: **ミニタキオンを「1日の運用ハブ」に進化させる**。

---

## 現状のフロー (やや属人化)

```
朝:
  田中さん → 頭の中で整理 → 手で daily_tasks.md 編集 → AIPM 上で各プロジェクト見回り
日中:
  AI 進行 → 田中さんレビュー (PC + iPhone) → AI 続行
夜:
  田中さん → 寝る前に状況確認 → 次の朝の頭で整理
```

問題:
- 朝の整理が固定プロンプト化されておらず再現性がない (日によってブレる)
- 前日からの引き継ぎが田中さんの記憶頼り
- 整理プロセス自体が記録に残らない

---

## 提案フロー (Daily Loop)

```
☀️ 朝
  田中さん [☀️ 今日を始める] → ミニタキオンが
    1. BL-DAILY-{YYYYMMDD} 自動作成
    2. 固定プロンプトで Cockpit task 起動 (朝の整理エージェント)
    3. AI が今日のタスク案 .md を生成
    4. BL-DAILY のレビュー物として ミニタキオンに登場
  ↓
  田中さんが iPhone で BL-DAILY をタップ
    → 「AIからの成果物」=「今日のタスク案」を読む
    → コメント or 修正依頼 → 承認 [✓ done]
  ↓
  AI が承認に基づき各 BL の priority/state を更新
  → 1日が始まる

🟢 日中 (既存通り)
  各 BL を AI が進める / 田中さんレビュー / AI 質問 → 田中さん回答
  ミニタキオンの「レビュー待ち / AIの番」を iPhone で見ながら作業

🌙 夜
  田中さん [🌙 今日を締める] → ミニタキオンが
    1. BL-WRAPUP-{YYYYMMDD} 自動作成
    2. 固定プロンプトで Cockpit task 起動 (振り返りエージェント)
    3. AI が今日の振り返り .md を生成
       - 今日完了したこと
       - 残課題
       - 翌日への申し送り
    4. STATUS.md を Flow → Stock にマージ (既存 Phase 5 設計と統合)
  ↓
  田中さんが BL-WRAPUP を読んで承認 → 1日終了

🔄 翌朝
  朝の整理エージェントが前日の振り返りを読んで、今日のタスク案を作成
  → ループ
```

「☀️ / 🌙」ボタンを忘れた場合のセーフティネット:
- **03:00 cron** が走り、未締めなら自動で 🌙 を実行 (既設計)
- 翌朝のエージェントが「昨日締めずに走り抜けたよね」を検知してリマインド

---

## 朝の整理エージェントの固定プロンプト (案)

```
あなたは ミニタキオン の「朝の整理」担当エージェントです。

# やること (順番)

1. 全 Stock プロジェクトの STATUS.md を読む
   ~/aipm_v0/Stock/*/*/STATUS.md

2. 各プロジェクトの active な BL を確認
   - state, priority, pending_questions, decisions
   - 当日 Flow に deliverables.yaml があれば読む

3. 前日の Daily Wrap-up を読む (もしあれば)
   ~/aipm_v0/Flow/<前日>/_orchestration/今日の振り返り.md

4. 以下を含む「今日のタスク案」を Markdown で出力

   # 今日のタスク案 — {YYYY-MM-DD}

   ## 🎯 今日のフォーカス
   <3-5 行で 今日のテーマを集約>

   ## ⏸ レビュー待ち (田中さんの番)
   <pending_questions / 未レビュー成果物 / awaiting_user 状態の BL を 優先順位順>
   - **BL-XXX (project)**: <概要> [推奨アクション]

   ## 🟢 AI 進行リスト
   <今日 AI が進める BL、目安時間付き>
   - **BL-XXX (project)**: <今日やる予定の作業>

   ## 💡 提案
   <新規 BL 案 / scope 変更 / 中止すべき BL>

   ## ❓ 田中さんへの質問
   <タスク整理時点で確認したいこと、なければ「なし」>

5. 出力先: ~/aipm_v0/Flow/<today>/_orchestration/今日のタスク案.md

6. ミニタキオン に成果物として登録:
   - deliverables.yaml に entry 追加
   - BL-DAILY-{YYYYMMDD} の deliverable_refs に append

7. BL-DAILY の state を awaiting_user に
```

---

## 夜の振り返りエージェントの固定プロンプト (案)

```
あなたは ミニタキオン の「夜の振り返り」担当エージェントです。

# やること

1. 当日の Flow から:
   ~/aipm_v0/Flow/<today>/<project>/deliverables.yaml
   - 今日 review_state が done に変わったもの
   - 今日 created_at の新規 deliverable

2. 各プロジェクトの BL.yaml decisions[] から:
   - 今日 (created_at が today) の decisions

3. 残課題の集計:
   - state が awaiting_user / blocked のままの BL
   - pending_questions[] が空でない BL

4. Markdown で出力:

   # 今日の振り返り — {YYYY-MM-DD}

   ## ✅ 今日完了したこと
   - **BL-XXX**: <変化のサマリー>
   - 成果物 N 件レビュー (done X / needs_revision Y)

   ## 🚧 残課題
   - <未完 BL とブロック理由>
   - <未回答の AI 質問>

   ## 📌 翌日への申し送り
   - <翌朝の整理エージェントが読む情報>
   - <優先的にレビューすべき BL>
   - <新規発見した課題>

   ## 📊 メトリクス (オプション)
   - 動かした BL: N 件
   - レビュー件数: M 件
   - AI 回答件数: K 件

5. 出力先: ~/aipm_v0/Flow/<today>/_orchestration/今日の振り返り.md

6. STATUS.md を Flow から Stock にマージ
   - 各プロジェクトの Flow/<today>/<project>/STATUS.md を Stock の永続版にマージ
   - 履歴 append、完了済 union、次アクション 上書き

7. ミニタキオンに登録、BL-WRAPUP-{YYYYMMDD} の deliverable_refs に append、awaiting_user に
```

---

## 必要な実装 (Phase 3 スコープ)

### A. UI 変更
- ホーム画面の上部に **「☀️ 今日を始める」「🌙 今日を締める」** ボタン
  - 時間帯で強調を切り替え (朝は ☀️ 大、夜は 🌙 大)
  - 既に当日の BL-DAILY / BL-WRAPUP があれば、ボタンは「📅 今日の運用へ」リンクに変わる
- ホーム上部に「📅 今日の運用」セクション (BL-DAILY / BL-WRAPUP 専用、既存プロジェクト一覧の上)

### B. Server Actions
```typescript
// app/actions.ts に追加
async function startDailyLoop(): Promise<Result<{ blId: string }, ...>> {
  // 1. BL-DAILY-{YYYYMMDD}.yaml を Stock に作成
  // 2. Cockpit task を起動 (固定プロンプト + bl_id 渡す)
  // 3. cockpit_task_ids[] に append
  // 4. revalidatePath
}

async function endDailyLoop(): Promise<Result<{ blId: string }, ...>> {
  // 似たフロー、BL-WRAPUP 作成
}
```

### C. 固定プロンプトファイル
```
~/.agi-tools/mini-tachyon/lib/prompts/
├── daily-start.md     # 朝の整理プロンプト (上記)
└── daily-wrapup.md    # 夜の振り返りプロンプト
```

### D. BL-DAILY / BL-WRAPUP の置き場所
**提案: 専用プロジェクト「朝の整理」を Stock に作る**
```
~/aipm_v0/Stock/作業効率化/朝の整理/
├── STATUS.md
└── backlog/
    ├── BL-DAILY-20260426.yaml
    ├── BL-DAILY-20260427.yaml
    ├── BL-WRAPUP-20260426.yaml
    └── ...
```

UI:
- ホームの「📅 今日の運用」セクションは「朝の整理」プロジェクトの BL のうち今日のものだけを抽出して見せる
- 過去のは「朝の整理」プロジェクトページで日付順に並べる
- 30 日以前は collapsed (古いものから)

### E. 03:00 cron との統合
既設計の Phase 5 cron に「未締めなら 🌙 endDailyLoop を実行」を追加。

### F. テスト
- Server Actions のテスト (BL-DAILY 作成、Cockpit fallback 各分岐、revalidatePath)

### 工数見積
- Phase 3a: ☀️ ボタン + 朝の整理 + BL-DAILY 作成 (1-2 日)
- Phase 3b: 🌙 ボタン + 夜の振り返り + Stock マージ (1 日)
- Phase 3c: 03:00 cron との統合 (半日)
- Phase 3d: 「📅 今日の運用」専用 UI、past archive (半日)

**合計 3-4 日 (1-2 週末)**

---

## 田中さんに確認したいこと (Open Questions)

### Q1: BL-DAILY / BL-WRAPUP の置き場所
- (a) 推奨: 専用プロジェクト「朝の整理」を Stock に作る (例: `Stock/作業効率化/朝の整理/`)
- (b) `_orchestration/` 直下に置く (各 Flow フォルダ直下)
- (c) 各プロジェクトに分散 (各 STATUS.md にメタとして記録)

### Q2: 1日 1 BL or 2 BL?
- (a) 推奨: BL-DAILY (朝) + BL-WRAPUP (夜) = 2 個 / 日 → 月 60 BL
- (b) 1 BL に統合 (`BL-DAILY-{date}` に朝の案 + 夜の振り返りを両方ぶら下げる) = 月 30 BL

### Q3: タスク案の粒度
- (a) 推奨: BL 一覧の優先順位 + 各 BL で「今日 AI が進める」内容を1-2行
- (b) 各 BL で具体タスクを細かく出す (時間配分まで)
- (c) 一言の概要だけ (シンプル運用)

### Q4: 承認後の AI の権限
- (a) 推奨: 田中さんが done で承認したら、AI が各 BL の priority/state を自動更新
- (b) 案は出すだけ、実際の更新は田中さんが ミニタキオン UI で手動

### Q5: アーカイブ
- (a) 推奨: 30 日前から collapsed、90 日前から非表示 (検索のみ)
- (b) 全期間表示 (どんどん増える)
- (c) 7 日で削除 (履歴は git で十分)

### Q6: 「今日を始める」を何時までに押す想定?
- 朝のうち (起きてすぐ) に押す前提でいいか?
- 押し忘れたら 朝の整理は走らないが、田中さんは普通に作業を進めて OK?

### Q7: 「タスク整理」スキップ機能
- 旅行や会議の日など、Daily Loop をスキップしたい時用に「今日はスキップ」ボタンも欲しい?
- それとも単に 🌙 を押さなければ自動的に skip 扱いになる?

---

## 副次的: 既存運用との整合

- AIPM の 3 ファイル同期 (STATUS / INBOX / daily_tasks) は **既に廃止** 決定 (Phase 4 で実施予定)
- 「daily_tasks.md」を作る役割は **「今日のタスク案.md」が引き継ぐ**
- INBOX は ミニタキオン 自体が引き継ぎ済 (pending_questions[])
- だから Phase 3 完了で AIPM 散文 3ファイルから完全離脱できる
